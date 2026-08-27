import os
import json
from pathlib import Path

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"

_cfg_dir = Path(os.environ.get("APPDATA", Path.home())) / "HOTS Hosts"
SETTINGS_PATH = _cfg_dir / "settings.json"

CUSTOM_DOMAINS_PATH = Path(HOSTS_PATH).parent / "custom_domains.txt"


def custom_domains_path() -> str:
    return str(CUSTOM_DOMAINS_PATH)


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


BASE_DARK = {
    "bg": "#1e1e1e", "bg2": "#2b2b2b", "bg3": "#3a3a3a",
    "fg": "#f0f0f0", "fg2": "#9e9e9e",
    "border": "#4a4a4a",
    "green": "#4ec94e", "gray": "#686868",
    "btn_bg": "#2e2e2e", "btn_fg": "#f0f0f0", "btn_hover": "#3e3e3e",
    "red": "#c84040", "red_bg": "#3a2020",
    "search_bg": "#252525",
    "diff_add": "#1a3a1a", "diff_del": "#3a1a1a",
    "diff_add_fg": "#6fe06f", "diff_del_fg": "#e06f6f",

    "panel_bg":        "rgba(30, 30, 30, 0.4)",
    "panel_bg_alt":    "rgba(40, 40, 40, 0.6)",
    "panel_bg_strong": "rgba(20, 20, 20, 0.5)",
    "table_bg":        "rgba(15, 15, 15, 0.30)",
    "table_alt_bg":    "rgba(30, 30, 30, 0.25)",
    "header_bg":       "rgba(20, 20, 20, 0.35)",
    "toolbar_bg":      "rgba(20, 20, 20, 0.28)",
    "searchbar_bg":    "rgba(20, 20, 20, 0.22)",
    "statusbar_bg":    "rgba(32, 32, 32, 0.92)",
    "titlebar_bg":     "rgba(22, 22, 22, 0.97)",
    "dialog_body_bg":  "rgba(18, 18, 18, 0.14)",
    "popup_bg":        "rgba(22, 22, 22, 0.97)",
    "indicator_bg":    "rgba(30, 30, 30, 0.5)",
    "search_frame_bg": "rgba(255, 255, 255, 0.06)",

    "border_soft":     "rgba(255, 255, 255, 0.07)",
    "border_soft2":    "rgba(255, 255, 255, 0.10)",
    "border_faint":    "rgba(255, 255, 255, 0.05)",
    "border_strong":   "rgba(255, 255, 255, 0.14)",
    "grid_line":       "rgba(255, 255, 255, 0.05)",
    "hover_border":    "rgba(255, 255, 255, 0.4)",
    "muted_fg":        "rgba(255, 255, 255, 0.30)",

    "scrollbar_handle":      "rgba(255, 255, 255, 0.18)",
    "scrollbar_track_hover": "rgba(255, 255, 255, 0.04)",
}

BASE_LIGHT = {
    "bg": "#f5f5f5", "bg2": "#ffffff", "bg3": "#e8e8e8",
    "fg": "#1a1a1a", "fg2": "#5a5a5a",
    "border": "#c8c8c8",
    "green": "#2e9e2e", "gray": "#8a8a8a",
    "btn_bg": "#e8e8e8", "btn_fg": "#1a1a1a", "btn_hover": "#dcdcdc",
    "red": "#c0392b", "red_bg": "#fbe4e1",
    "search_bg": "#eeeeee",
    "diff_add": "#dff5df", "diff_del": "#f9dede",
    "diff_add_fg": "#1d7a1d", "diff_del_fg": "#a83030",

    "panel_bg":        "rgba(0, 0, 0, 0.035)",
    "panel_bg_alt":    "rgba(0, 0, 0, 0.055)",
    "panel_bg_strong": "rgba(0, 0, 0, 0.08)",
    "table_bg":        "rgba(0, 0, 0, 0.02)",
    "table_alt_bg":    "rgba(0, 0, 0, 0.035)",
    "header_bg":       "rgba(0, 0, 0, 0.05)",
    "toolbar_bg":      "rgba(0, 0, 0, 0.03)",
    "searchbar_bg":    "rgba(0, 0, 0, 0.025)",
    "statusbar_bg":    "rgba(235, 235, 235, 0.92)",
    "titlebar_bg":     "rgba(250, 250, 250, 0.97)",
    "dialog_body_bg":  "rgba(255, 255, 255, 0.55)",
    "popup_bg":        "rgba(250, 250, 250, 0.97)",
    "indicator_bg":    "rgba(0, 0, 0, 0.04)",
    "search_frame_bg": "rgba(0, 0, 0, 0.04)",

    "border_soft":     "rgba(0, 0, 0, 0.10)",
    "border_soft2":    "rgba(0, 0, 0, 0.13)",
    "border_faint":    "rgba(0, 0, 0, 0.06)",
    "border_strong":   "rgba(0, 0, 0, 0.16)",
    "grid_line":       "rgba(0, 0, 0, 0.07)",
    "hover_border":    "rgba(0, 0, 0, 0.30)",
    "muted_fg":        "rgba(0, 0, 0, 0.35)",

    "scrollbar_handle":      "rgba(0, 0, 0, 0.18)",
    "scrollbar_track_hover": "rgba(0, 0, 0, 0.04)",
}

ACCENT_PRESETS_DARK = {
    "gold":  {"accent": "#d4a017", "accent_fg": "#ffffff", "sel_bg": "#3d2e08", "sel_fg": "#f0e0b0"},
    "red":   {"accent": "#c84040", "accent_fg": "#ffffff", "sel_bg": "#3d1616", "sel_fg": "#f0b0b0"},
    "green": {"accent": "#4ec94e", "accent_fg": "#ffffff", "sel_bg": "#163d16", "sel_fg": "#b0f0b0"},
    "blue":  {"accent": "#4098d4", "accent_fg": "#ffffff", "sel_bg": "#16283d", "sel_fg": "#b0d0f0"},
}
ACCENT_PRESETS_LIGHT = {
    "gold":  {"accent": "#a87b0e", "accent_fg": "#ffffff", "sel_bg": "#fbf0d4", "sel_fg": "#5c4409"},
    "red":   {"accent": "#b23434", "accent_fg": "#ffffff", "sel_bg": "#fbe1e1", "sel_fg": "#6b1f1f"},
    "green": {"accent": "#2e8f2e", "accent_fg": "#ffffff", "sel_bg": "#e1f5e1", "sel_fg": "#1c561c"},
    "blue":  {"accent": "#2f77ab", "accent_fg": "#ffffff", "sel_bg": "#e1eef7", "sel_fg": "#1c4a68"},
}
DEFAULT_ACCENT = "gold"
DEFAULT_THEME = "dark"

DARK = dict(BASE_DARK)

IS_LIGHT_THEME = False


def _apply_saved_theme():
    global IS_LIGHT_THEME
    try:
        settings = load_settings()
    except Exception:
        settings = {}

    theme = settings.get("theme", DEFAULT_THEME)
    accent_key = settings.get("accent_color", DEFAULT_ACCENT)

    IS_LIGHT_THEME = (theme == "light")
    base = BASE_LIGHT if IS_LIGHT_THEME else BASE_DARK
    accent_presets = ACCENT_PRESETS_LIGHT if IS_LIGHT_THEME else ACCENT_PRESETS_DARK
    accent_preset = accent_presets.get(accent_key, accent_presets[DEFAULT_ACCENT])

    DARK.clear()
    DARK.update(base)
    DARK.update(accent_preset)


_apply_saved_theme()

QSS_VARS = {k: v for k, v in DARK.items()}


def hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (255, 255, 255)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def accent_rgba(alpha: float) -> str:
    r, g, b = hex_to_rgb(DARK["accent"])
    return f"rgba({r},{g},{b},{alpha})"
