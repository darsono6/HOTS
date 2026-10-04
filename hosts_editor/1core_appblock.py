
import ctypes
import json
import os
import subprocess
import time
import winreg
from dataclasses import dataclass, field, asdict
from typing import Optional

from .core_antispy import (
    _resolve_powershell_exe, _console_encoding, CREATE_NO_WINDOW,
)

IFEO_ROOT = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options"

BLOCK_DEBUGGER_CMD = r"C:\Windows\System32\__hots_blocked__.exe"

_FILE_LOCK_SID = "S-1-5-32-545"

STATE_FILE = os.path.join(
    os.environ.get("APPDATA", ""), "HOTS Hosts", "appblock_state.json"
)

_UNINSTALL_ROOTS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]

KNOWN_VPN_EXES = [
    "nordvpn.exe", "expressvpn.exe", "protonvpn.exe", "openvpn-gui.exe",
    "tunnelbear.exe", "windscribe.exe", "surfshark.exe", "hotspotshield.exe",
    "cyberghost8.exe", "pia_manager.exe",
]

OWN_EXE_NAME = "hots hosts.exe"

PROTECTED_SYSTEM_EXES = {
    "notepad.exe", "cmd.exe", "sethc.exe", "utilman.exe", "taskmgr.exe",
    "explorer.exe", "regedit.exe", "mspaint.exe", "calc.exe", "osk.exe",
    "magnify.exe", "narrator.exe", "powershell.exe", "pwsh.exe",

    "dwm.exe", "winlogon.exe", "csrss.exe", "services.exe", "smss.exe",
    "wininit.exe", "lsass.exe",

    "svchost.exe", "userinit.exe", "sihost.exe", "logonui.exe",

    "dllhost.exe", "fontdrvhost.exe",
}

def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

@dataclass
class BlockedApp:
    exe_name: str
    display_name: str = ""
    category: str = "custom"
    locked_path: str = ""
    enabled: bool = True
    added_at: float = field(default_factory=time.time)

class AppBlockManager:

    last_error: str = ""

    @classmethod
    def list_installed_programs(cls) -> list:
        results = {}
        for hive, subkey in _UNINSTALL_ROOTS:
            try:
                root = winreg.OpenKey(hive, subkey)
            except OSError:
                continue
            try:
                i = 0
                while True:
                    try:
                        name = winreg.EnumKey(root, i)
                    except OSError:
                        break
                    i += 1
                    try:
                        with winreg.OpenKey(root, name) as k:
                            try:
                                display_name = winreg.QueryValueEx(k, "DisplayName")[0]
                            except FileNotFoundError:
                                continue
                            if not display_name:
                                continue
                            try:
                                if winreg.QueryValueEx(k, "SystemComponent")[0] == 1:
                                    continue
                            except FileNotFoundError:
                                pass

                            exe_path = ""
                            try:
                                icon = winreg.QueryValueEx(k, "DisplayIcon")[0]
                                icon = icon.split(",")[0].strip('"').strip()
                                if icon.lower().endswith(".exe") and os.path.isfile(icon):
                                    exe_path = icon
                            except FileNotFoundError:
                                pass

                            if not exe_path:
                                try:
                                    install_loc = winreg.QueryValueEx(k, "InstallLocation")[0]
                                    if install_loc and os.path.isdir(install_loc):
                                        for fn in os.listdir(install_loc):
                                            if fn.lower().endswith(".exe"):
                                                exe_path = os.path.join(install_loc, fn)
                                                break
                                except (FileNotFoundError, OSError):
                                    pass

                            if exe_path and os.path.isfile(exe_path):
                                results[display_name] = os.path.normpath(exe_path)
                    except OSError:
                        continue
            finally:
                root.Close()

        return sorted(results.items(), key=lambda t: t[0].lower())

    @staticmethod
    def _ifeo_key_path(exe_name: str) -> str:
        return f"{IFEO_ROOT}\\{exe_name}"

    @classmethod
    def _set_ifeo_block(cls, exe_name: str) -> bool:
        try:
            key = winreg.CreateKeyEx(
                winreg.HKEY_LOCAL_MACHINE,
                cls._ifeo_key_path(exe_name),
                0,
                winreg.KEY_SET_VALUE,
            )
            with key:
                winreg.SetValueEx(key, "Debugger", 0, winreg.REG_SZ, BLOCK_DEBUGGER_CMD)
            return True
        except OSError as e:
            cls.last_error = str(e)
            return False

    @classmethod
    def _clear_ifeo_block(cls, exe_name: str) -> bool:
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, IFEO_ROOT, 0, winreg.KEY_ALL_ACCESS
            ) as root:
                winreg.DeleteKey(root, exe_name)
            return True
        except FileNotFoundError:
            return True
        except OSError as e:
            cls.last_error = str(e)
            return False

    @classmethod
    def is_ifeo_blocked(cls, exe_name: str) -> Optional[bool]:
        exe_name = exe_name.strip().lower()
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                cls._ifeo_key_path(exe_name),
                0,
                winreg.KEY_READ,
            ) as key:
                val, _ = winreg.QueryValueEx(key, "Debugger")
                return bool(val)
        except FileNotFoundError:
            return False
        except OSError:
            return None

    @classmethod
    def _lock_file(cls, path: str) -> bool:
        exe = _resolve_powershell_exe()
        if exe is None:
            cls.last_error = "no_powershell"
            return False
        safe_path = path.replace("'", "''")
        ps_command = (
            f"$acl = Get-Acl -LiteralPath '{safe_path}'; "
            f"$sid = New-Object System.Security.Principal.SecurityIdentifier('{_FILE_LOCK_SID}'); "
            "$rights = [System.Security.AccessControl.FileSystemRights]::Write -bor "
            "[System.Security.AccessControl.FileSystemRights]::Delete -bor "
            "[System.Security.AccessControl.FileSystemRights]::ExecuteFile; "
            "$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($sid, $rights, 'Deny'); "
            "$acl.AddAccessRule($rule); "
            f"Set-Acl -LiteralPath '{safe_path}' -AclObject $acl"
        )
        try:
            r = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
            )
            if r.returncode != 0:
                cls.last_error = r.stderr.strip() or r.stdout.strip()
                return False
            return True
        except Exception as e:
            cls.last_error = str(e)
            return False

    @classmethod
    def _scan_and_unlock_folder(cls, folder: str) -> bool:
        exe = _resolve_powershell_exe()
        if exe is None:
            cls.last_error = "no_powershell"
            return False
        safe_folder = folder.replace("'", "''")
        ps_command = (
            f"$sid = New-Object System.Security.Principal.SecurityIdentifier('{_FILE_LOCK_SID}'); "
            f"Get-ChildItem -LiteralPath '{safe_folder}' -File -ErrorAction SilentlyContinue | ForEach-Object { '{' } "
            "$acl = Get-Acl -LiteralPath $_.FullName; "
            "$mine = @($acl.Access | Where-Object { $_.AccessControlType -eq 'Deny' -and "
            "($_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value -eq $sid.Value) }); "
            "if ($mine.Count -gt 0) { "
            "foreach ($r in $mine) { $acl.RemoveAccessRule($r) | Out-Null }; "
            "Set-Acl -LiteralPath $_.FullName -AclObject $acl "
            "} "
            + "}"
        )
        try:
            r = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
            )
            if r.returncode != 0:
                cls.last_error = r.stderr.strip() or r.stdout.strip()
                return False
            return True
        except Exception as e:
            cls.last_error = str(e)
            return False

    @classmethod
    def _unlock_file(cls, path: str) -> bool:
        exe = _resolve_powershell_exe()
        if exe is None:
            cls.last_error = "no_powershell"
            return False
        safe_path = path.replace("'", "''")
        ps_command = (
            f"$acl = Get-Acl -LiteralPath '{safe_path}'; "
            f"$sid = New-Object System.Security.Principal.SecurityIdentifier('{_FILE_LOCK_SID}'); "
            "$toRemove = @($acl.Access | Where-Object { $_.AccessControlType -eq 'Deny' -and "
            "($_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value -eq $sid.Value) }); "
            "foreach ($rule in $toRemove) { $acl.RemoveAccessRule($rule) | Out-Null }; "
            f"Set-Acl -LiteralPath '{safe_path}' -AclObject $acl"
        )
        try:
            r = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
            )
            if r.returncode != 0:
                cls.last_error = r.stderr.strip() or r.stdout.strip()
                return False
            return True
        except Exception as e:
            cls.last_error = str(e)
            return False

    @classmethod
    def is_file_locked(cls, path: str) -> Optional[bool]:
        exe = _resolve_powershell_exe()
        if exe is None:
            return None
        safe_path = path.replace("'", "''")
        ps_command = (
            f"$sid = New-Object System.Security.Principal.SecurityIdentifier('{_FILE_LOCK_SID}'); "
            f"$acl = Get-Acl -LiteralPath '{safe_path}'; "
            "$found = $acl.Access | Where-Object { "
            "$_.AccessControlType -eq 'Deny' -and "
            "$_.FileSystemRights.ToString() -match 'Write' -and "
            "$_.FileSystemRights.ToString() -match 'ExecuteFile' -and "
            "($_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value -eq $sid.Value) "
            "}; "
            "if ($found) { 'LOCKED' } else { 'UNLOCKED' }"
        )
        try:
            r = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
            )
            out = r.stdout.strip()
            if out == "LOCKED":
                return True
            if out == "UNLOCKED":
                return False
            return None
        except FileNotFoundError:
            return False
        except Exception:
            return None

    @staticmethod
    def _load_state() -> list:
        if not os.path.exists(STATE_FILE):
            return []
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [BlockedApp(**item) for item in raw]
        except Exception:
            return []

    @staticmethod
    def _save_state(apps: list) -> None:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([asdict(a) for a in apps], f, indent=2, ensure_ascii=False)
        os.replace(tmp, STATE_FILE)

    @classmethod
    def list_blocked(cls) -> list:
        return cls._load_state()

    @classmethod
    def add_app(cls, exe_name: str, display_name: str = "", category: str = "custom",
                file_path: str = "") -> bool:
        cls.last_error = ""
        exe_name = exe_name.strip().lower()

        if not exe_name:
            return False
        if not exe_name.endswith(".exe"):
            exe_name += ".exe"
        if exe_name in PROTECTED_SYSTEM_EXES:
            cls.last_error = "protected_system_app"
            return False
        if exe_name == OWN_EXE_NAME:
            cls.last_error = "self_block"
            return False
        if not _is_admin():
            cls.last_error = "no_admin"
            return False

        apps = cls._load_state()
        existing = next((a for a in apps if a.exe_name == exe_name), None)
        if existing is not None and existing.enabled:

            return True

        if not cls._set_ifeo_block(exe_name):
            return False

        locked_path = existing.locked_path if existing else ""
        if file_path and os.path.isfile(file_path):
            if cls._lock_file(file_path):
                locked_path = file_path

        if existing is None:
            apps.append(BlockedApp(exe_name, display_name or exe_name, category, locked_path))
        else:

            existing.enabled = True
            if locked_path:
                existing.locked_path = locked_path
        cls._save_state(apps)
        return True

    @classmethod
    def set_enabled(cls, exe_name: str, enabled: bool) -> bool:
        cls.last_error = ""
        exe_name = exe_name.strip().lower()

        if not _is_admin():
            cls.last_error = "no_admin"
            return False

        apps = cls._load_state()
        existing = next((a for a in apps if a.exe_name == exe_name), None)
        if existing is None:
            cls.last_error = "not_found"
            return False

        if enabled:
            if not cls._set_ifeo_block(exe_name):
                return False
            if existing.locked_path and os.path.isfile(existing.locked_path):
                cls._lock_file(existing.locked_path)
        else:
            cleared = cls._clear_ifeo_block(exe_name)
            if not cleared and exe_name in PROTECTED_SYSTEM_EXES:
                cls.last_error = ""
                cleared = True
            if not cleared:
                return False
            if existing.locked_path and os.path.exists(existing.locked_path):
                cls._unlock_file(existing.locked_path)

        existing.enabled = enabled
        cls._save_state(apps)
        return True

    @classmethod
    def add_vpn_bundle(cls) -> tuple:
        ok_count = 0
        failed = []
        for exe in KNOWN_VPN_EXES:
            if cls.add_app(exe, exe.replace(".exe", "").title(), category="vpn"):
                ok_count += 1
            else:
                failed.append(exe)
        return ok_count, failed

    @classmethod
    def is_vpn_bundle_blocked(cls) -> bool:
        blocked_names = {a.exe_name for a in cls._load_state() if a.enabled}
        return all(exe in blocked_names for exe in KNOWN_VPN_EXES)

    @classmethod
    def remove_vpn_bundle(cls) -> tuple:
        blocked_names = {a.exe_name for a in cls._load_state()}
        ok_count = 0
        failed = []
        for exe in KNOWN_VPN_EXES:
            if exe not in blocked_names:
                continue
            if cls.remove_app(exe):
                ok_count += 1
            else:
                failed.append(exe)
        return ok_count, failed

    @classmethod
    def remove_app(cls, exe_name: str) -> bool:
        cls.last_error = ""
        exe_name = exe_name.strip().lower()

        if not _is_admin():
            cls.last_error = "no_admin"
            return False

        apps = cls._load_state()
        existing = next((a for a in apps if a.exe_name == exe_name), None)
        if existing and existing.locked_path:
            if os.path.exists(existing.locked_path):
                if not cls._unlock_file(existing.locked_path):

                    cls.last_error = ""
            else:

                folder = os.path.dirname(existing.locked_path)
                if os.path.isdir(folder):
                    if not cls._scan_and_unlock_folder(folder):
                        cls.last_error = ""

        cleared = cls._clear_ifeo_block(exe_name)
        if not cleared and exe_name in PROTECTED_SYSTEM_EXES:

            cls.last_error = ""
            cleared = True
        if not cleared:
            return False

        apps = [a for a in apps if a.exe_name != exe_name]
        cls._save_state(apps)
        return True

    @classmethod
    def force_unlock(cls, path: str) -> bool:
        cls.last_error = ""
        path = os.path.normpath(path)
        exe_name = os.path.basename(path).strip().lower()

        if not exe_name:
            cls.last_error = "invalid_path"
            return False
        if not _is_admin():
            cls.last_error = "no_admin"
            return False

        ifeo_cleared = cls._clear_ifeo_block(exe_name)
        if not ifeo_cleared and exe_name in PROTECTED_SYSTEM_EXES:
            cls.last_error = ""
            ifeo_cleared = True
        if not ifeo_cleared:
            return False

        file_unlocked = True
        if os.path.isfile(path):
            file_unlocked = cls._unlock_file(path)

        folder = os.path.dirname(path)
        if os.path.isdir(folder):

            cls._scan_and_unlock_folder(folder)

        if not file_unlocked:
            return False

        apps = cls._load_state()
        remaining = [a for a in apps if a.exe_name != exe_name]
        if len(remaining) != len(apps):
            cls._save_state(remaining)

        cls.last_error = ""
        return True

    @classmethod
    def check_drift(cls) -> Optional[dict]:
        apps = cls._load_state()
        if not apps:
            return {"regressed": [], "ok": True}

        regressed = []
        for a in apps:
            if not a.enabled:

                continue
            state = cls.is_ifeo_blocked(a.exe_name)
            if state is None:
                return None
            if not state:
                regressed.append(a.exe_name)
                continue
            if a.locked_path and os.path.exists(a.locked_path):
                file_state = cls.is_file_locked(a.locked_path)
                if file_state is None:
                    return None
                if not file_state:
                    regressed.append(a.exe_name)

        if regressed:
            regressed_set = set(regressed)
            for a in apps:
                if a.exe_name in regressed_set:
                    a.enabled = False
            cls._save_state(apps)

        return {"regressed": regressed, "ok": not regressed}
