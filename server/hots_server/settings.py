"""Runtime settings, read from environment variables (see deploy/hots-server.env)."""

import os


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


DATA_DIR = _env("HOTS_DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
DB_PATH = os.path.join(DATA_DIR, "hots.db")

# "auto": Secure cookie when the request arrived over HTTPS (Caddy sets X-Forwarded-Proto).
COOKIE_SECURE = _env("HOTS_COOKIE_SECURE", "auto").lower()

# Iterations of PBKDF2-SHA256 for console passwords (lower only for tests).
PBKDF2_ITERATIONS = int(_env("HOTS_PBKDF2_ITERATIONS", "600000"))

# How long the server holds an agent poll open, and when a PC is shown as offline.
POLL_HOLD_SECONDS = float(_env("HOTS_POLL_HOLD", "25"))
ONLINE_GRACE_SECONDS = float(_env("HOTS_ONLINE_GRACE", "75"))

SESSION_DAYS = int(_env("HOTS_SESSION_DAYS", "14"))
DEFAULT_AGENT_LANG = _env("HOTS_AGENT_LANG", "fr") or "fr"
