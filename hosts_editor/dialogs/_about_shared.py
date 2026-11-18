import hashlib
import json
import os
import re
import socket
import ssl
import urllib.request
import urllib.error
from pathlib import Path

from PySide6.QtCore import QThread, QStandardPaths, Signal

from ..bg_tasks import is_shutting_down
from ..i18n import T


def _build_ssl_context():
    try:
        import certifi
        cafile = certifi.where()
    except Exception:
        cafile = None

    from ..resource_utils import certifi_bundled_path
    bundled = certifi_bundled_path()
    if os.path.exists(bundled):
        cafile = bundled

    try:
        if cafile:
            return ssl.create_default_context(cafile=cafile)
        return ssl.create_default_context()
    except Exception:
        return ssl.create_default_context()

from ..version import APP_VERSION  # noqa: E402  (re-exported for the dialogs)

# Fork with remote administration: updates must come from this repository, otherwise the
# upstream installer would replace the program without the remote agent.
GITHUB_REPO = "jrsmrtn/HOTS-Web-Administrated"
GITHUB_API_LATEST_RELEASE = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases"
# The upstream site advertises upstream versions only: no fallback for this fork.
SITE_VERSION_URL = ""
SITE_PAGE_URL = "https://hotstools.com/hosts/"
_SITE_VERSION_RE = re.compile(r"\d{1,5}(\.\d{1,5}){0,3}")
_MAX_RESPONSE_BYTES = 1_000_000
_TAG_RE = re.compile(r"[\w.+\-]{1,32}")
_DOWNLOAD_PREFIX = f"https://github.com/{GITHUB_REPO}/releases/download/"
_ASSET_NAME_RE = re.compile(r"\w[\w.\- ]{0,99}\.exe", re.IGNORECASE)
_DIGEST_RE = re.compile(r"sha256:([0-9a-fA-F]{64})")
_MAX_DOWNLOAD_BYTES = 500 * 1024 * 1024
_DOWNLOAD_CHUNK = 64 * 1024


def _parse_version(text: str):
    cleaned = text.strip().lstrip("vV")
    parts = re.findall(r"\d+", cleaned)
    return tuple(int(p) for p in parts) if parts else (0,)


def _pick_installer_asset(data: dict):
    assets = data.get("assets")
    if not isinstance(assets, list):
        return None
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = asset.get("name")
        url = asset.get("browser_download_url")
        size = asset.get("size")
        digest = asset.get("digest")
        if not (isinstance(name, str) and isinstance(url, str) and isinstance(digest, str)):
            continue
        if isinstance(size, bool) or not isinstance(size, int) or not 0 < size <= _MAX_DOWNLOAD_BYTES:
            continue
        match = _DIGEST_RE.fullmatch(digest)
        if not match or not _ASSET_NAME_RE.fullmatch(name) or not url.startswith(_DOWNLOAD_PREFIX):
            continue
        return {"name": name, "url": url, "size": size, "sha256": match.group(1).lower()}
    return None


def _read_site_version():
    if not SITE_VERSION_URL:
        return None
    try:
        request = urllib.request.Request(SITE_VERSION_URL, headers={"User-Agent": "HOTS-UpdateChecker"})
        opener = urllib.request.build_opener(
            _HttpsOnlyRedirect, urllib.request.HTTPSHandler(context=_build_ssl_context()))
        with opener.open(request, timeout=8) as resp:
            text = resp.read(64).decode("ascii").strip()
    except Exception:
        return None
    return text if _SITE_VERSION_RE.fullmatch(text) else None


class _UpdateCheckWorker(QThread):
    finished_ok = Signal(str, str, object)
    failed      = Signal(str)

    def run(self):
        try:
            req = urllib.request.Request(
                GITHUB_API_LATEST_RELEASE,
                headers={
                    "User-Agent": "HOTS-UpdateChecker",
                    "Accept": "application/vnd.github+json",
                },
            )
            with urllib.request.urlopen(req, timeout=8, context=_build_ssl_context()) as resp:
                data = json.loads(resp.read(_MAX_RESPONSE_BYTES).decode("utf-8"))
            tag = str(data.get("tag_name") or data.get("name") or "").strip()
            url = data.get("html_url")
            if not isinstance(url, str) or not url.startswith(f"https://github.com/{GITHUB_REPO}/"):
                url = GITHUB_RELEASES_URL
            if _TAG_RE.fullmatch(tag):
                self.finished_ok.emit(tag, url, _pick_installer_asset(data))
                return
            error = _safe_t("about_update_err_empty")
        except Exception as e:
            error = _classify_update_error(e)

        version = _read_site_version()
        if version:
            self.finished_ok.emit(version, SITE_PAGE_URL, None)
        else:
            self.failed.emit(error)


class _HttpsOnlyRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not newurl.lower().startswith("https://"):
            raise urllib.error.URLError("redirect to a non-HTTPS address")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _DownloadError(Exception):
    pass


def _downloads_dir() -> Path:
    location = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
    return Path(location) if location else Path.home() / "Downloads"


def _move_to_unique_name(tmp: Path, directory: Path, name: str) -> Path:
    stem, ext = os.path.splitext(name)
    for i in range(100):
        candidate = directory / (name if i == 0 else f"{stem} ({i}){ext}")
        if os.path.lexists(candidate):
            continue
        try:
            os.rename(tmp, candidate)
            return candidate
        except FileExistsError:
            continue
    raise _DownloadError(_safe_t("about_dl_err_write"))


def _mark_as_downloaded(path: Path):
    try:
        with open(f"{path}:Zone.Identifier", "w", encoding="ascii") as f:
            f.write("[ZoneTransfer]\r\nZoneId=3\r\n")
    except OSError:
        pass


class _DownloadWorker(QThread):
    progress = Signal(int)
    finished_ok = Signal(str)
    failed = Signal(str)

    def __init__(self, asset: dict, parent=None):
        super().__init__(parent)
        self._asset = asset

    def run(self):
        tmp = None
        try:
            directory = _downloads_dir()
            directory.mkdir(parents=True, exist_ok=True)
            tmp = directory / f".hots_{os.getpid()}_{os.urandom(6).hex()}.part"
            expected = self._asset["size"]
            digest = hashlib.sha256()
            received = 0
            last_pct = -1

            opener = urllib.request.build_opener(
                _HttpsOnlyRedirect, urllib.request.HTTPSHandler(context=_build_ssl_context()))
            request = urllib.request.Request(self._asset["url"], headers={"User-Agent": "HOTS-UpdateChecker"})

            try:
                fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
            except OSError:
                raise _DownloadError(_safe_t("about_dl_err_write"))

            with os.fdopen(fd, "wb") as out, opener.open(request, timeout=15) as resp:
                while True:
                    if is_shutting_down():
                        return
                    chunk = resp.read(_DOWNLOAD_CHUNK)
                    if not chunk:
                        break
                    received += len(chunk)
                    if received > expected:
                        raise _DownloadError(_safe_t("about_dl_err_hash"))
                    digest.update(chunk)
                    out.write(chunk)
                    pct = received * 100 // expected
                    if pct != last_pct:
                        last_pct = pct
                        self.progress.emit(pct)

            if received != expected or digest.hexdigest() != self._asset["sha256"]:
                raise _DownloadError(_safe_t("about_dl_err_hash"))

            final = _move_to_unique_name(tmp, directory, self._asset["name"])
            tmp = None
            _mark_as_downloaded(final)
            self.finished_ok.emit(str(final))
        except _DownloadError as e:
            self.failed.emit(str(e))
        except OSError as e:
            if isinstance(e, (urllib.error.URLError, ConnectionError, TimeoutError, ssl.SSLError)):
                self.failed.emit(_classify_update_error(e))
            else:
                self.failed.emit(_safe_t("about_dl_err_write"))
        except Exception as e:
            self.failed.emit(_classify_update_error(e))
        finally:
            if tmp is not None:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass


def _classify_update_error(exc: Exception) -> str:
    reason = exc
    if isinstance(exc, urllib.error.URLError) and not isinstance(exc, urllib.error.HTTPError):
        reason = exc.reason if exc.reason is not None else exc

    errno_val = getattr(reason, "errno", None)
    winerror_val = getattr(reason, "winerror", None)
    msg = str(reason)
    msg_low = msg.lower()

    if errno_val == 11001 or winerror_val == 11001 or "getaddrinfo failed" in msg_low:
        return _safe_t("about_update_err_no_internet")

    if errno_val == 10013 or winerror_val == 10013:
        return _safe_t("about_update_err_firewall")

    if isinstance(exc, urllib.error.HTTPError):
        if exc.code == 403:
            return _safe_t("about_update_err_rate_limit")
        if exc.code == 404:
            return _safe_t("about_update_err_not_found")

    if isinstance(reason, (socket.timeout, TimeoutError)) or "timed out" in msg_low:
        return _safe_t("about_update_err_timeout")

    if isinstance(reason, ssl.SSLError) or "ssl" in msg_low or "certificate" in msg_low:
        return _safe_t("about_update_err_ssl")

    return _safe_t("about_update_err_generic", has_detail=True).format(detail=msg)


_FALLBACK_TEXT = "An unexpected error occurred. Please try again later."
_FALLBACK_TEXT_DETAIL = "An unexpected error occurred: {detail}"


def _safe_t(key: str, has_detail: bool = False) -> str:
    fallback = _FALLBACK_TEXT_DETAIL if has_detail else _FALLBACK_TEXT
    try:
        val = T(key)
        if not val or val == key:
            return fallback
        return val
    except Exception:
        return fallback
