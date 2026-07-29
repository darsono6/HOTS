import json
import os
import re
import ssl
import sys
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

    base = getattr(sys, "_MEIPASS", None)
    if base:
        bundled = os.path.join(base, "certifi", "cacert.pem")
        if os.path.exists(bundled):
            cafile = bundled

    try:
        if cafile:
            return ssl.create_default_context(cafile=cafile)
        return ssl.create_default_context()
    except Exception:
        return ssl.create_default_context()

APP_VERSION = "2.0"

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
                self.failed.emit("Empty response from GitHub.")
                return
            self.finished_ok.emit(tag, url)
        except urllib.error.HTTPError as e:
            self.failed.emit(f"HTTP {e.code}")
        except urllib.error.URLError as e:
            self.failed.emit(str(e.reason))
        except Exception as e:
            self.failed.emit(str(e))


def _safe_t(key: str, fallback: str) -> str:
    try:
        val = T(key)
        if not val or val == key:
            return fallback
        return val
    except Exception:
        return fallback
