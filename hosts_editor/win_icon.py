import ctypes
import os
import sys
from ctypes import wintypes as wt

from .resource_utils import resource_path

_WM_SETICON, _WM_GETICON = 0x0080, 0x007F
_ICON_SMALL, _ICON_BIG = 0, 1
_IMAGE_ICON, _LR_LOADFROMFILE = 1, 0x0010
_GCLP_HICONSM, _GCLP_HICON = -34, -14
_SM_CXICON, _SM_CYICON, _SM_CXSMICON, _SM_CYSMICON = 11, 12, 49, 50

_user32 = None
_cache = {}


def _api():
    global _user32
    if _user32 is None:
        u = ctypes.WinDLL("user32", use_last_error=True)
        u.LoadImageW.argtypes = [wt.HINSTANCE, wt.LPCWSTR, wt.UINT, ctypes.c_int, ctypes.c_int, wt.UINT]
        u.LoadImageW.restype = ctypes.c_void_p
        u.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
        u.SendMessageW.restype = ctypes.c_ssize_t
        u.SetClassLongPtrW.argtypes = [wt.HWND, ctypes.c_int, ctypes.c_void_p]
        u.SetClassLongPtrW.restype = ctypes.c_void_p
        u.GetSystemMetrics.argtypes = [ctypes.c_int]
        u.GetSystemMetrics.restype = ctypes.c_int
        _user32 = u
    return _user32


def _metric(u, hwnd, index):
    try:
        dpi = int(u.GetDpiForWindow(wt.HWND(hwnd)))
        if dpi > 0:
            return int(u.GetSystemMetricsForDpi(index, dpi))
    except Exception:
        pass
    return u.GetSystemMetrics(index)


def _load(u, path, w, h):
    key = (path, w, h)
    if key not in _cache:
        _cache[key] = u.LoadImageW(None, path, _IMAGE_ICON, w, h, _LR_LOADFROMFILE)
    return _cache[key]


def apply(hwnd: int) -> None:
    if sys.platform != "win32" or not hwnd:
        return
    try:
        path = resource_path("graphic/logo.ico")
        if not os.path.isfile(path):
            return
        u = _api()
        big = _load(u, path, _metric(u, hwnd, _SM_CXICON), _metric(u, hwnd, _SM_CYICON))
        small = _load(u, path, _metric(u, hwnd, _SM_CXSMICON), _metric(u, hwnd, _SM_CYSMICON))
        if big and u.SendMessageW(hwnd, _WM_GETICON, _ICON_BIG, 0) != big:
            u.SendMessageW(hwnd, _WM_SETICON, _ICON_BIG, big)
            u.SetClassLongPtrW(hwnd, _GCLP_HICON, big)
        if small and u.SendMessageW(hwnd, _WM_GETICON, _ICON_SMALL, 0) != small:
            u.SendMessageW(hwnd, _WM_SETICON, _ICON_SMALL, small)
            u.SetClassLongPtrW(hwnd, _GCLP_HICONSM, small)
    except Exception:
        pass
