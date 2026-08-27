import json
import os
import re
import socket
import ssl
import urllib.request
import urllib.error

from PySide6.QtCore import QThread, Signal

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

APP_VERSION = "2.1"

GITHUB_REPO = "darsono6/HOTS"
GITHUB_API_LATEST_RELEASE = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases"


def _parse_version(text: str):
    cleaned = text.strip().lstrip("vV")
    parts = re.findall(r"\d+", cleaned)
    return tuple(int(p) for p in parts) if parts else (0,)


class _UpdateCheckWorker(QThread):
    finished_ok = Signal(str, str)
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
                data = json.loads(resp.read().decode("utf-8"))
            tag = (data.get("tag_name") or data.get("name") or "").strip()
            url = data.get("html_url") or GITHUB_RELEASES_URL
            if not tag:
                self.failed.emit(_safe_t("about_update_err_empty"))
                return
            self.finished_ok.emit(tag, url)
        except Exception as e:
            self.failed.emit(_classify_update_error(e))


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
