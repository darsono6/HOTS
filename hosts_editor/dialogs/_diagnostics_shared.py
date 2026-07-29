import json
import os

from PySide6.QtCore import Signal, QObject

_SYSTEM_DOMAINS: frozenset = frozenset({
    "localhost", "localhost.localdomain", "local", "broadcasthost",
    "ip6-localhost", "ip6-loopback", "ip6-localnet", "ip6-mcastprefix",
    "ip6-allnodes", "ip6-allrouters", "ip6-allhosts", "wpad", "wpad.home",
    "google.com", "www.google.com", "bing.com", "www.bing.com",
    "microsoft.com", "www.microsoft.com", "apple.com", "www.apple.com",
    "amazon.com", "www.amazon.com", "facebook.com", "www.facebook.com",
    "twitter.com", "www.twitter.com", "paypal.com", "www.paypal.com",
    "bankofamerica.com", "chase.com", "wellsfargo.com",
    "login.microsoftonline.com", "account.microsoft.com",
    "windowsupdate.microsoft.com", "update.microsoft.com",
})

_UPDATE_DOMAINS: frozenset = frozenset({
    "windowsupdate.com", "windowsupdate.microsoft.com",
    "update.microsoft.com", "download.windowsupdate.com",
    "ntservicepack.microsoft.com", "wustat.windows.com",
    "mu.microsoft.com", "wu.microsoft.com",
    "definitionupdates.microsoft.com",
    "update.avast.com", "update.avg.com",
    "update.kaspersky.com", "kaspersky.com",
    "update.norton.com", "liveupdate.symantec.com",
    "update.eset.com", "update.bitdefender.com",
    "update.malwarebytes.com", "downloads.malwarebytes.com",
    "update.avira.com", "update.drweb.com",
})

_HOMOGLYPH_CHARS: frozenset = frozenset(
    "аеорсхіАЕОРСХІ"
    "вгдзклмнптуфыэАВГДЗКЛМНПТУФЫЭЮЯ"
    "αβγδεζηθιλμνξοπρστυφχψω"
    "ΑΒΓΔΕΖΗΘΙΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
    "ıɑɡℓ"
)

_KNOWN_SAFE_DOMAINS: tuple = (
    "google.com", "microsoft.com", "apple.com", "paypal.com",
    "amazon.com", "facebook.com", "github.com", "windows.com",
    "office.com", "live.com", "outlook.com", "yahoo.com",
    "netflix.com", "twitter.com", "instagram.com", "linkedin.com",
    "bankofamerica.com", "chase.com", "wellsfargo.com", "citibank.com",
    "pinterest.com", "reddit.com", "tumblr.com", "wordpress.com",
    "dropbox.com", "spotify.com", "twitch.tv", "adobe.com",
    "dhl.com", "fedex.com", "ups.com",
    "binance.com", "coinbase.com",
    "gmail.com", "steampowered.com", "epicgames.com",
)

_SUSPICIOUS_TLDS: frozenset = frozenset({
    "tk", "ml", "ga", "cf", "gq",
    "pw", "top", "xyz", "buzz", "click",
    "download", "loan", "win", "stream",
    "accountant", "date", "faith", "party",
    "review", "science", "trade", "webcam",
    "work", "zip", "mov",
})

_SUSPICIOUS_PATTERNS: tuple = (
    (r"\d{5,}",                 "long_digits"),
    (r"[a-z0-9]{25,}",         "long_label"),
    (r"(?:(?:login|secure|security|signin|verify|verification|update|confirm|"
     r"account|banking|support|billing|alert|suspended)"
     r".*?(?P<brand1>paypal|microsoft|google|apple|amazon|facebook|bank))"
     r"|"
     r"(?:(?P<brand2>paypal|microsoft|google|apple|amazon|facebook|bank)"
     r".*?(?:login|secure|security|signin|verify|verification|update|confirm|"
     r"account|banking|support|billing|alert|suspended))",
     "brand_phish"),
    (r"^\d{1,3}\.\d{1,3}",     "ip_like"),
)

_KNOWN_CDN_DOMAINS: frozenset = frozenset({
    "cdninstagram.com", "fbcdn.net", "fbsbx.com", "facebook.net",
    "gstatic.com", "googlevideo.com", "ytimg.com", "ggpht.com",
    "googleusercontent.com", "googleapis.com",
    "akamaized.net", "akamai.net", "akamaihd.net", "akamaitechnologies.com",
    "cloudfront.net", "amazonvideo.com", "aiv-cdn.net",
    "fastly.net", "fastlylb.net", "cloudflare.net",
    "azureedge.net", "azurefd.net", "msecnd.net", "vo.msecnd.net",
    "nflxvideo.net", "nflximg.net", "nflxext.com",
    "twimg.com",
    "pinimg.com",
    "reddstatic.com", "redditmedia.com",
    "steamcontent.com", "steamstatic.com",
    "tiktokcdn.com", "tiktokv.com", "tiktokcdn-us.com", "tiktokcdn-eu.com",
    "snapchatcdn.com", "sc-cdn.net",
    "discordapp.net",
    "jtvnw.net", "twitchsvc.net",
    "llnwd.net", "hwcdn.net", "edgecastcdn.net",
    "jsdelivr.net", "unpkg.com", "bootstrapcdn.com",
    "wp.com", "giphy.com", "imgur.com",
})


class _Emitter(QObject):
    row_ready = Signal(str, str, str, str, str)
    progress  = Signal(int, int, str)
    done      = Signal(str)


_HOTS_APPDATA_DIR   = os.path.join(os.environ.get("APPDATA", "C:\\"), "HOTS Hosts")
_IGNORED_HOSTS_FILE = os.path.join(_HOTS_APPDATA_DIR, "HOTS_diag_ignored.json")


def load_ignored_hosts() -> set:
    try:
        with open(_IGNORED_HOSTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return {str(h).strip().lower() for h in data if str(h).strip()}
    except Exception:
        pass
    return set()


def save_ignored_hosts(hosts: set):
    try:
        os.makedirs(_HOTS_APPDATA_DIR, exist_ok=True)
        with open(_IGNORED_HOSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(hosts), f, ensure_ascii=False, indent=2)
    except Exception:
        pass
