"""HTTPS JSON client for the agent (standard library only)."""

import json
import os
import socket
import ssl
import threading
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from . import AGENT_VERSION

MAX_RESPONSE_BYTES = 16 * 1024 * 1024


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class Unauthorized(ApiError):
    """The server no longer knows this device (deleted from the console, or token revoked)."""


def build_ssl_context() -> ssl.SSLContext:
    cafile = None
    try:
        from ..resource_utils import certifi_bundled_path
        bundled = certifi_bundled_path()
        if os.path.exists(bundled):
            cafile = bundled
    except Exception:
        pass
    if cafile is None:
        try:
            import certifi
            cafile = certifi.where()
        except Exception:
            cafile = None
    extra = os.environ.get("HOTS_AGENT_CAFILE")
    ctx = ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()
    if extra and os.path.exists(extra):
        ctx.load_verify_locations(cafile=extra)
    return ctx


# --- DNS fallback --------------------------------------------------------------------------
# When the Internet block is on, public DNS resolvers may be unreachable. The server's IPs
# are excluded from the firewall rules, so we remember them and reuse them if resolution fails.

_cache_lock = threading.Lock()
_ip_cache: dict = {}
_orig_getaddrinfo = socket.getaddrinfo
_patched = False


def remember_ips(host: str, ips) -> None:
    with _cache_lock:
        if ips:
            _ip_cache[host.lower()] = list(ips)


def _getaddrinfo_with_fallback(host, port, *args, **kwargs):
    try:
        return _orig_getaddrinfo(host, port, *args, **kwargs)
    except socket.gaierror:
        key = host.lower() if isinstance(host, str) else host
        with _cache_lock:
            cached = list(_ip_cache.get(key, ()))
        if not cached:
            raise
        out = []
        for ip in cached:
            try:
                out.extend(_orig_getaddrinfo(ip, port, *args, **kwargs))
            except socket.gaierror:
                continue
        if not out:
            raise
        return out


def install_dns_fallback() -> None:
    global _patched
    if not _patched:
        socket.getaddrinfo = _getaddrinfo_with_fallback
        _patched = True


class Transport:
    def __init__(self, server_url: str, auth: str = "", timeout: float = 30):
        self.server_url = server_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout
        self._ctx = build_ssl_context() if self.server_url.startswith("https://") else None

    @property
    def host(self) -> str:
        return urlsplit(self.server_url).hostname or ""

    @property
    def port(self) -> int:
        parts = urlsplit(self.server_url)
        return parts.port or (443 if parts.scheme == "https" else 80)

    def resolve_server_ips(self) -> list:
        host = self.host
        try:
            infos = _orig_getaddrinfo(host, self.port, proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            with _cache_lock:
                return list(_ip_cache.get(host.lower(), ()))
        ips = sorted({info[4][0] for info in infos})
        remember_ips(host, ips)
        return ips

    def request(self, method: str, path: str, payload=None, timeout: float = None) -> dict:
        url = self.server_url + path
        data = None
        headers = {
            "User-Agent": f"HOTS-Remote-Agent/{AGENT_VERSION}",
            "Accept": "application/json",
        }
        if payload is not None:
            data = json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.auth:
            headers["Authorization"] = f"Bearer {self.auth}"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout, context=self._ctx) as resp:
                body = resp.read(MAX_RESPONSE_BYTES + 1)
        except urllib.error.HTTPError as e:
            message = f"HTTP {e.code}"
            try:
                detail = json.loads(e.read(65536).decode("utf-8", "replace")).get("detail")
                if isinstance(detail, str) and detail:
                    message = detail
            except Exception:
                pass
            if e.code in (401, 403, 410):
                raise Unauthorized(e.code, message) from None
            raise ApiError(e.code, message) from None
        except (urllib.error.URLError, OSError, ssl.SSLError, ValueError) as e:
            reason = getattr(e, "reason", e)
            raise ApiError(0, str(reason)) from None
        if len(body) > MAX_RESPONSE_BYTES:
            raise ApiError(0, "response too large")
        if not body:
            return {}
        try:
            data = json.loads(body.decode("utf-8"))
        except ValueError:
            raise ApiError(0, "invalid JSON from server") from None
        return data if isinstance(data, dict) else {}
