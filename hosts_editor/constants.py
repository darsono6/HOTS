"""
Application-wide constants: paths, color palette, settings.
No other module should define its own colors or paths —
import them from here instead.
"""

import os
import platform
import json
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
HOSTS_PATH = (
    r"C:\Windows\System32\drivers\etc\hosts"
    if platform.system() == "Windows"
    else "/etc/hosts"
)

# All per-user data lives under a single HOTS\ subdirectory so that
# settings, DNS backup and AntiSpy backup are cleaned up together.
if platform.system() == "Windows":
    _cfg_dir = Path(os.environ.get("APPDATA", Path.home())) / "HOTS"
else:
    _cfg_dir = Path.home() / ".hots"
SETTINGS_PATH = _cfg_dir / "settings.json"

# ── Color palette ──────────────────────────────────────────────────────────
DARK = {
    "bg":          "#1e1e1e", "bg2": "#2b2b2b", "bg3": "#3a3a3a",
    "fg":          "#f0f0f0", "fg2": "#9e9e9e",
    "border":      "#4a4a4a",
    "accent":      "#d4a017", "accent_fg": "#ffffff",
    "green":       "#4ec94e", "gray": "#686868",
    "sel_bg":      "#0078d4", "sel_fg": "#ffffff",
    "btn_bg":      "#2e2e2e", "btn_fg": "#f0f0f0", "btn_hover": "#3e3e3e",
    "red":         "#c84040", "red_bg": "#3a2020",
    "search_bg":   "#252525",
    "diff_add":    "#1a3a1a",   # added line background
    "diff_del":    "#3a1a1a",   # deleted line background
    "diff_add_fg": "#6fe06f",
    "diff_del_fg": "#e06f6f",
}

# ── User settings ──────────────────────────────────────────────────────────
def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_settings(data: dict):
    try:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass
