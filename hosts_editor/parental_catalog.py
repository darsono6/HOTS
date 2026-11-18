"""Parental-control categories, shared by the GUI and the remote agent (no Qt imports here)."""

from .i18n import T

CATEGORIES = [
    {"label_key": "par_cat_twitter",     "icon": "🐦", "color": "#1DA1F2", "file": "twitter.txt"},
    {"label_key": "par_cat_instagram",   "icon": "📸", "color": "#E1306C", "file": "instagram.txt"},
    {"label_key": "par_cat_youtube",     "icon": "▶",  "color": "#FF0000", "file": "youtube.txt"},
    {"label_key": "par_cat_facebook",    "icon": "👤", "color": "#1877F2", "file": "facebook.txt"},
    {"label_key": "par_cat_whatsapp",    "icon": "💬", "color": "#25D366", "file": "whatsapp.txt"},
    {"label_key": "par_cat_tiktok",      "icon": "🎵", "color": "#ff2d55", "file": "tiktok.txt"},
    {"label_key": "par_cat_twitch",      "icon": "🎮", "color": "#9146FF", "file": "twitch.txt"},
    {"label_key": "par_cat_snapchat",    "icon": "👻", "color": "#FFFC00", "file": "snapchat.txt"},
    {"label_key": "par_cat_pinterest",   "icon": "📌", "color": "#E60023", "file": "pinterest.txt"},
    {"label_key": "par_cat_reddit",      "icon": "🤖", "color": "#FF4500", "file": "reddit.txt"},
    {"label_key": "par_cat_adult",       "icon": "🔞", "color": "#cc2222", "file": "adult.txt"},
    {"label_key": "par_cat_games",       "icon": "🕹️", "color": "#7b2d8b", "file": "games.txt"},
    {"label_key": "par_cat_torrent",     "icon": "⛔", "color": "#aaaaaa", "file": "torrent.txt"},
    {"label_key": "par_cat_dating",      "icon": "💘", "color": "#ff5864", "file": "dating.txt"},
    {"label_key": "par_cat_random_chat", "icon": "🎥", "color": "#00bcd4", "file": "random_chat.txt"},
]

TELEMETRY_CATEGORY = {"label_key": "par_cat_antispy_domains", "icon": "📡", "color": "#0078D4",
                      "file": "telemetry.txt"}

CUSTOM_FILE = "custom_domains.txt"


def comment_for_category(cat: dict) -> str:
    suffix = cat["file"][:-4] if cat["file"].endswith(".txt") else cat["file"]
    name_key = f"par_comment_name_{suffix}"
    name = T(name_key)
    if name == name_key:
        name = T(cat["label_key"])
    return name
