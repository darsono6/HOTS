import ctypes
import json
import logging
import os
import subprocess
import sys
import tempfile

logger = logging.getLogger("HOTS.storage")

PROGRAMDATA_DIR = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "HOTS Hosts")

_SYSTEM32 = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")
_CREATE_NO_WINDOW = 0x08000000
_secured = False


def _secure_machine_dir(path: str) -> None:
    # State files in here drive actions performed by the elevated app, so the folder must not be
    # controllable by a standard user: refuse junctions, take ownership, drop inherited ACEs.
    global _secured
    if _secured or sys.platform != "win32":
        return
    attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
    if attrs == 0xFFFFFFFF or attrs & 0x400:
        raise OSError(f"refusing to use {path}: not a plain directory")
    icacls = os.path.join(_SYSTEM32, "icacls.exe")
    for args in (["/setowner", "*S-1-5-32-544"],
                 ["/inheritance:r", "/grant:r", "*S-1-5-18:(OI)(CI)F", "*S-1-5-32-544:(OI)(CI)F"]):
        r = subprocess.run([icacls, path, *args], capture_output=True, check=False,
                           creationflags=_CREATE_NO_WINDOW, timeout=20)
        if r.returncode != 0:
            logger.warning("secure_storage: icacls %s failed (code %s)", args[0], r.returncode)
    _secured = True


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    if os.path.normcase(os.path.abspath(path)) == os.path.normcase(os.path.abspath(PROGRAMDATA_DIR)):
        _secure_machine_dir(path)


def atomic_write_json(path: str, data) -> None:
    directory = os.path.dirname(path)
    ensure_dir(directory)
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".state_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise
