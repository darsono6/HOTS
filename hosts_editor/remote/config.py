"""Agent configuration, kept in the ProgramData folder (admins + SYSTEM only).

``remote_agent.json`` holds the server URL and the device credentials; a standard
(child) account can neither read the token nor point the agent at another server.
"""

import json
import os
import time
from urllib.parse import urlsplit, urlunsplit

CONFIG_NAME = "remote_agent.json"
STATUS_NAME = "remote_agent_status.json"
LOG_NAME = "remote_agent.log"


def data_dir() -> str:
    override = os.environ.get("HOTS_AGENT_DIR")
    if override:
        return override
    from ..secure_storage import PROGRAMDATA_DIR
    return PROGRAMDATA_DIR


def config_path() -> str:
    return os.path.join(data_dir(), CONFIG_NAME)


def status_path() -> str:
    return os.path.join(data_dir(), STATUS_NAME)


def log_path() -> str:
    return os.path.join(data_dir(), LOG_NAME)


def _write_json(path: str, data) -> None:
    if os.environ.get("HOTS_AGENT_DIR"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = f"{path}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
        return
    from ..secure_storage import atomic_write_json
    atomic_write_json(path, data)


def _read_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def normalize_server_url(url: str) -> str:
    """'console.example.com' -> 'https://console.example.com' (no trailing slash)."""
    url = (url or "").strip()
    if not url:
        raise ValueError("empty server address")
    if "://" not in url:
        url = "https://" + url
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError(f"invalid server address: {url!r}")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError(f"invalid server address: {url!r}")
    if parts.scheme == "http" and not _plain_http_allowed(parts.hostname):
        # The device token would travel in clear: HTTPS only (deploy.sh always sets it up).
        raise ValueError("the console address must start with https://")
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme, parts.netloc.lower(), path, "", ""))


def _plain_http_allowed(host: str) -> bool:
    if os.environ.get("HOTS_AGENT_ALLOW_HTTP") == "1":
        return True
    return host in ("localhost", "127.0.0.1", "::1")


def load():
    data = _read_json(config_path())
    if not isinstance(data, dict):
        return None
    if not all(isinstance(data.get(k), str) and data.get(k) for k in ("server_url", "device_id", "token")):
        return None
    return data


def save(cfg: dict) -> None:
    _write_json(config_path(), cfg)


def clear() -> None:
    for path in (config_path(), status_path()):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


def is_enrolled() -> bool:
    return load() is not None


def netblock_exclusions() -> list:
    """IPs of the console server: the Internet block must never cut the agent off."""
    cfg = load()
    if not cfg:
        return []
    ips = cfg.get("server_ips")
    return [ip for ip in ips if isinstance(ip, str)] if isinstance(ips, list) else []


def update_server_ips(ips) -> bool:
    cfg = load()
    if not cfg:
        return False
    new = sorted({str(ip) for ip in ips or ()})
    if not new or new == sorted(cfg.get("server_ips") or []):
        return False
    cfg["server_ips"] = new
    save(cfg)
    return True


def write_status(**fields) -> None:
    """Small status file read by the desktop app (Options page) to show the connection state."""
    current = read_status()
    current.update(fields)
    current["updated_at"] = time.time()
    try:
        _write_json(status_path(), current)
    except Exception:
        pass


def read_status() -> dict:
    data = _read_json(status_path())
    return data if isinstance(data, dict) else {}
