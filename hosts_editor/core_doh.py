import ctypes
import json
import logging
import os
import tempfile
from typing import List, Optional

import winreg

logger = logging.getLogger("HOTS.doh")

HOTS_PROGRAMDATA_DIR = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "HOTS Hosts")
DOH_STATE_FILE = os.path.join(HOTS_PROGRAMDATA_DIR, "HOTS_doh_state.json")

BROWSERS: List[dict] = [
    {
        "id": "chrome",
        "name": "Google Chrome",
        "exe_paths": [
            r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
            r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
            r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
        ],
        "reg_path": r"SOFTWARE\Policies\Google\Chrome",
        "kind": "sz_mode",
        "value_name": "DnsOverHttpsMode",
        "off_value": "off",
    },
    {
        "id": "edge",
        "name": "Microsoft Edge",
        "exe_paths": [
            r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
            r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
        ],
        "reg_path": r"SOFTWARE\Policies\Microsoft\Edge",
        "kind": "sz_mode",
        "value_name": "DnsOverHttpsMode",
        "off_value": "off",
    },
    {
        "id": "brave",
        "name": "Brave",
        "exe_paths": [
            r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],

        "reg_path": r"SOFTWARE\Policies\BraveSoftware\Brave",
        "kind": "sz_mode",
        "value_name": "DnsOverHttpsMode",
        "off_value": "off",
    },
    {
        "id": "firefox",
        "name": "Mozilla Firefox",
        "exe_paths": [
            r"%ProgramFiles%\Mozilla Firefox\firefox.exe",
            r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe",
        ],
        "reg_path": r"SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS",
        "kind": "firefox_nested",
    },
]

def _find(browser_id: str) -> Optional[dict]:
    for b in BROWSERS:
        if b["id"] == browser_id:
            return b
    return None

def _expand(path: str) -> str:
    return os.path.expandvars(path)

def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def _delete_hklm_value(subkey: str, name: str) -> None:
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, name)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass

def _atomic_write_json(path: str, data: dict) -> None:
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".doh_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise

def _load_state() -> dict:
    if not os.path.exists(DOH_STATE_FILE):
        return {}
    try:
        with open(DOH_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("DohBlockManager: failed to read state file: %s", e)
        return {}

def _save_state(state: dict) -> None:
    try:
        _atomic_write_json(DOH_STATE_FILE, state)
    except Exception as e:
        logger.warning("DohBlockManager: failed to save state file: %s", e)

class DohBlockManager:

    last_error: str = ""

    @staticmethod
    def is_browser_installed(browser_id: str) -> bool:
        b = _find(browser_id)
        if b is None:
            return False
        return any(os.path.exists(_expand(p)) for p in b["exe_paths"])

    @staticmethod
    def is_blocked(browser_id: str) -> bool:
        b = _find(browser_id)
        if b is None:
            return False
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, b["reg_path"], 0, winreg.KEY_READ)
        except FileNotFoundError:
            return False
        try:
            if b["kind"] == "sz_mode":
                value, _ = winreg.QueryValueEx(key, b["value_name"])
                return str(value).strip().lower() == b["off_value"]
            else:
                value, _ = winreg.QueryValueEx(key, "Enabled")
                return int(value) == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False
        finally:
            winreg.CloseKey(key)

    @staticmethod
    def enable(browser_id: str) -> bool:
        DohBlockManager.last_error = ""
        if not _is_admin():
            DohBlockManager.last_error = "no_admin"
            return False
        b = _find(browser_id)
        if b is None:
            DohBlockManager.last_error = "unknown_browser"
            return False
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, b["reg_path"], 0, winreg.KEY_SET_VALUE)
            try:
                if b["kind"] == "sz_mode":
                    winreg.SetValueEx(key, b["value_name"], 0, winreg.REG_SZ, b["off_value"])
                else:
                    winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "Locked", 0, winreg.REG_DWORD, 1)
            finally:
                winreg.CloseKey(key)
            state = _load_state()
            state[browser_id] = True
            _save_state(state)
            logger.info("DohBlockManager.enable(%s): OK", browser_id)
            return True
        except Exception as e:
            DohBlockManager.last_error = str(e)
            logger.exception("DohBlockManager.enable(%s) failed", browser_id)
            return False

    @staticmethod
    def disable(browser_id: str) -> bool:
        DohBlockManager.last_error = ""
        if not _is_admin():
            DohBlockManager.last_error = "no_admin"
            return False
        b = _find(browser_id)
        if b is None:
            DohBlockManager.last_error = "unknown_browser"
            return False
        try:
            if b["kind"] == "sz_mode":
                _delete_hklm_value(b["reg_path"], b["value_name"])
            else:
                _delete_hklm_value(b["reg_path"], "Enabled")
                _delete_hklm_value(b["reg_path"], "Locked")
            state = _load_state()
            state[browser_id] = False
            _save_state(state)
            logger.info("DohBlockManager.disable(%s): OK", browser_id)
            return True
        except Exception as e:
            DohBlockManager.last_error = str(e)
            logger.exception("DohBlockManager.disable(%s) failed", browser_id)
            return False

    @staticmethod
    def check_drift() -> Optional[dict]:
        state = _load_state()
        if not state:
            return None
        regressed = []
        changed = False
        for browser_id, expected_blocked in state.items():
            if not expected_blocked:
                continue
            b = _find(browser_id)
            if b is None:
                continue
            if not DohBlockManager.is_browser_installed(browser_id):

                continue
            if not DohBlockManager.is_blocked(browser_id):
                regressed.append(b["name"])
                state[browser_id] = False
                changed = True
        if changed:
            _save_state(state)
        if regressed:
            return {"regressed": regressed}
        return None
