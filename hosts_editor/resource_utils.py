import os
import sys

_IS_NUITKA = "__compiled__" in globals()


def get_base_dir() -> str:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return meipass

    if _IS_NUITKA or getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))

    return os.path.dirname(os.path.abspath(__file__))


def resource_path(name: str) -> str:
    return os.path.join(get_base_dir(), name)


def blocklists_dir() -> str:
    return os.path.join(get_base_dir(), "blocklists")


def certifi_bundled_path() -> str:
    return os.path.join(get_base_dir(), "certifi", "cacert.pem")
