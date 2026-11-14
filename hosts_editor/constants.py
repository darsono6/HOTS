import os
import re
import sys
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
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}

def updates_on_startup(settings: dict) -> bool:
    return str(settings.get("check_updates_on_startup", "1")).strip().lower() in ("1", "true", "yes")


def save_settings(data: dict):
    tmp = None
    try:
        payload = json.dumps(data, indent=2).encode("utf-8")
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = SETTINGS_PATH.with_name(f".settings_{os.getpid()}_{os.urandom(6).hex()}.tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, SETTINGS_PATH)
    except Exception as e:
        print(f"save_settings warning: {e!r}", flush=True)
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
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

    "panel_bg":        "rgba(255, 255, 255, 0.45)",
    "panel_bg_alt":    "rgba(0, 0, 0, 0.055)",
    "panel_bg_strong": "rgba(0, 0, 0, 0.08)",
    "table_bg":        "rgba(255, 255, 255, 0.30)",
    "table_alt_bg":    "rgba(255, 255, 255, 0.50)",
    "header_bg":       "rgba(255, 255, 255, 0.60)",
    "toolbar_bg":      "rgba(255, 255, 255, 0.35)",
    "searchbar_bg":    "rgba(255, 255, 255, 0.50)",
    "statusbar_bg":    "rgba(235, 235, 235, 0.92)",
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
    "teal":  {"accent": "#2aa5a0", "accent_fg": "#ffffff", "sel_bg": "#123a38", "sel_fg": "#b0f0ea"},
    "graphite": {"accent": "#b0b0b0", "accent_fg": "#1a1a1a", "sel_bg": "#2e2e2e", "sel_fg": "#e0e0e0"},
}
ACCENT_PRESETS_LIGHT = {
    "gold":  {"accent": "#a87b0e", "accent_fg": "#ffffff", "sel_bg": "#fbf0d4", "sel_fg": "#5c4409"},
    "red":   {"accent": "#b23434", "accent_fg": "#ffffff", "sel_bg": "#fbe1e1", "sel_fg": "#6b1f1f"},
    "green": {"accent": "#2e8f2e", "accent_fg": "#ffffff", "sel_bg": "#e1f5e1", "sel_fg": "#1c561c"},
    "blue":  {"accent": "#2f77ab", "accent_fg": "#ffffff", "sel_bg": "#e1eef7", "sel_fg": "#1c4a68"},
    "teal":  {"accent": "#1f827d", "accent_fg": "#ffffff", "sel_bg": "#dff3f1", "sel_fg": "#14504d"},
    "graphite": {"accent": "#5a5a5a", "accent_fg": "#ffffff", "sel_bg": "#e4e4e4", "sel_fg": "#2b2b2b"},
}
DEFAULT_ACCENT = "teal"
DEFAULT_THEME = "dark"
DEFAULT_TRANSPARENCY = 40
DEFAULT_GLOW = DEFAULT_TRANSPARENCY
DEFAULT_MATERIAL = "mica"
DEFAULT_EFFECTS = True
ACRYLIC_SUPPORTED = bool(sys.platform == "win32" and sys.getwindowsversion().build >= 22621)

_GLASS_KEYS = (
    "panel_bg", "panel_bg_alt", "panel_bg_strong", "table_bg", "table_alt_bg",
    "header_bg", "toolbar_bg", "searchbar_bg", "statusbar_bg",
    "dialog_body_bg",
)

_RGBA_RE = re.compile(
    r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)")


def valid_theme(value) -> str:
    return value if value in ("dark", "light") else DEFAULT_THEME


def valid_accent(value) -> str:
    return value if isinstance(value, str) and value in ACCENT_PRESETS_DARK else DEFAULT_ACCENT


def valid_material(value) -> str:
    return "acrylic" if value == "acrylic" else DEFAULT_MATERIAL


def clamp_transparency(value) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return DEFAULT_TRANSPARENCY
    try:
        return max(0, min(100, int(value)))
    except (ValueError, OverflowError):
        return DEFAULT_TRANSPARENCY


clamp_glow = clamp_transparency


def saved_glow(settings: dict) -> int:
    return clamp_glow(settings.get("glow", settings.get("transparency", DEFAULT_GLOW)))


DARK = dict(BASE_DARK)

IS_LIGHT_THEME = False
TRANSPARENCY = DEFAULT_TRANSPARENCY
GLOW = DEFAULT_GLOW
MATERIAL = DEFAULT_MATERIAL
EFFECTS = DEFAULT_EFFECTS
ACRYLIC_BASE_ALPHA = 0.0
_PANEL_ALPHA0 = 1.0


def _acrylic_end_factor() -> float:
    return 0.45 if IS_LIGHT_THEME else 1.125


def _acrylic_alpha(end_alpha: float, transparency: int) -> float:
    return 1.0 - (1.0 - end_alpha) * transparency / 100


_ACRYLIC_END_CAP = {"statusbar_bg": 0.5}


def _acrylic_color(value: str, transparency: int, cap: float = 1.0) -> str:
    m = _RGBA_RE.match(value.strip())
    if not m:
        return value
    a = float(m.group(4)) if m.group(4) is not None else 1.0
    a = _acrylic_alpha(min(cap, a * _acrylic_end_factor()), transparency)
    return f"rgba({m.group(1)}, {m.group(2)}, {m.group(3)}, {a:.3f})"


def _acrylic_base_alpha(transparency: int) -> float:
    return _acrylic_alpha(0.85 * min(1.0, _PANEL_ALPHA0 * _acrylic_end_factor()), transparency)


def _apply_saved_theme():
    global IS_LIGHT_THEME, TRANSPARENCY, GLOW, MATERIAL, EFFECTS, ACRYLIC_BASE_ALPHA, _PANEL_ALPHA0
    try:
        settings = load_settings()
    except Exception:
        settings = {}

    IS_LIGHT_THEME = (valid_theme(settings.get("theme")) == "light")
    base = BASE_LIGHT if IS_LIGHT_THEME else BASE_DARK
    accent_presets = ACCENT_PRESETS_LIGHT if IS_LIGHT_THEME else ACCENT_PRESETS_DARK
    accent_preset = accent_presets[valid_accent(settings.get("accent_color"))]

    TRANSPARENCY = clamp_transparency(settings.get("transparency", DEFAULT_TRANSPARENCY))
    GLOW = saved_glow(settings)
    EFFECTS = settings.get("effects") is not False
    wants_acrylic = valid_material(settings.get("material")) == "acrylic"
    MATERIAL = "acrylic" if (EFFECTS and wants_acrylic and ACRYLIC_SUPPORTED) else DEFAULT_MATERIAL
    m0 = _RGBA_RE.match(base["panel_bg"].strip())
    _PANEL_ALPHA0 = float(m0.group(4)) if m0 and m0.group(4) is not None else 1.0

    DARK.clear()
    DARK.update(base)
    DARK.update(accent_preset)
    if MATERIAL == "acrylic":
        for key in _GLASS_KEYS:
            if IS_LIGHT_THEME and key in ("panel_bg_alt", "panel_bg_strong"):
                continue
            DARK[key] = _acrylic_color(DARK[key], TRANSPARENCY, _ACRYLIC_END_CAP.get(key, 1.0))
    ACRYLIC_BASE_ALPHA = _acrylic_base_alpha(TRANSPARENCY) if MATERIAL == "acrylic" else 0.0


_apply_saved_theme()


def set_live_glow(value) -> None:
    global GLOW
    GLOW = clamp_glow(value)


def set_live_transparency(value) -> None:
    global TRANSPARENCY, ACRYLIC_BASE_ALPHA
    TRANSPARENCY = clamp_transparency(value)
    if MATERIAL == "acrylic":
        ACRYLIC_BASE_ALPHA = _acrylic_base_alpha(TRANSPARENCY)


def hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (255, 255, 255)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def accent_rgba(alpha: float) -> str:
    r, g, b = hex_to_rgb(DARK["accent"])
    return f"rgba({r},{g},{b},{alpha})"
