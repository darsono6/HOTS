"""
Business logic for the Windows AntiSpy module in the HOTS project.
Remembers the original computer state before applying changes.
The creationflags flag is set to suppress console (cmd) window popups.
"""

import os
import json
import platform
import subprocess

if platform.system() == "Windows":
    import winreg

TELEMETRY_SERVICES = ["DiagTrack", "dmwappushservice"]

FIREWALL_APPS = {
    "HOTS_AntiSpy_CompatTel": "%systemroot%\\System32\\CompatTelRunner.exe",
    "HOTS_AntiSpy_DeviceCensus": "%systemroot%\\System32\\devicecensus.exe",
    "HOTS_AntiSpy_WerFault": "%systemroot%\\System32\\WerFault.exe"
}

REG_DATA_COLLECTION = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
HOTS_APPDATA_DIR = os.path.join(os.environ.get("APPDATA", "C:\\"), "HOTS")
BACKUP_FILE = os.path.join(HOTS_APPDATA_DIR, "HOTS_antispy_state.json")

# Windows system flag preventing creation of a new console window
CREATE_NO_WINDOW = 0x08000000


class AntiSpyManager:
    @staticmethod
    def is_active() -> bool:
        """
        Real status check — used by the UI instead of looking at the hosts
        file, which AntiSpy never actually writes to (it has no domain
        blocklist; its mechanism is services/registry/firewall).

        BACKUP_FILE is created by enable_antispy() (before it changes
        anything, so it can remember the original values) and removed by
        disable_antispy() once everything has been restored — so its mere
        presence already tracks "have we applied changes that haven't
        been reverted yet", and it survives app restarts since it lives
        in %APPDATA%.

        The registry check on top guards against the backup file being
        orphaned — e.g. if telemetry settings were restored to factory
        values by something other than this app (manual registry edit,
        System Restore, Windows reset) without going through
        disable_antispy(), the leftover backup file alone would still
        say "active" even though the real protection is gone.
        """
        if not os.path.exists(BACKUP_FILE):
            return False
        return AntiSpyManager._get_registry_telemetry_value() == 0

    @staticmethod
    def _get_service_start_type(service_name: str) -> str:
        """
        Returns 'auto', 'demand', or 'disabled'.

        Uses PowerShell's Get-CimInstance (WMI) instead of parsing the
        descriptive text from `sc qc`, because the StartMode property
        values ("Auto", "Manual", "Disabled") come from the CIM schema
        and stay the same regardless of the Windows display language —
        unlike sc.exe's human-readable output, which is not guaranteed
        to use the same English labels on every language edition.
        """
        try:
            ps_command = (
                f"(Get-CimInstance -ClassName Win32_Service "
                f"-Filter \"Name='{service_name}'\").StartMode"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, check=False,
                creationflags=CREATE_NO_WINDOW
            )
            value = result.stdout.strip()
            if value == "Auto":
                return "auto"
            if value == "Manual":
                return "demand"
            if value == "Disabled":
                return "disabled"
        except Exception:
            pass
        return "auto"

    @staticmethod
    def _get_registry_telemetry_value():
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_DATA_COLLECTION, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "AllowTelemetry")
            winreg.CloseKey(key)
            return int(value)
        except Exception:
            return "NOT_FOUND"

    @staticmethod
    def enable_antispy() -> bool:
        try:
            if not os.path.exists(BACKUP_FILE):
                system_backup = {
                    "services": {},
                    "registry_telemetry": AntiSpyManager._get_registry_telemetry_value()
                }
                for service in TELEMETRY_SERVICES:
                    system_backup["services"][service] = AntiSpyManager._get_service_start_type(service)
                os.makedirs(HOTS_APPDATA_DIR, exist_ok=True)
                with open(BACKUP_FILE, "w", encoding="utf-8") as f:
                    json.dump(system_backup, f, indent=4)

            for service in TELEMETRY_SERVICES:
                subprocess.run(["sc", "config", service, "start=", "disabled"], capture_output=True, check=False, creationflags=CREATE_NO_WINDOW)
                subprocess.run(["net", "stop", service], capture_output=True, check=False, creationflags=CREATE_NO_WINDOW)

            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, REG_DATA_COLLECTION, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)

            AntiSpyManager._remove_firewall_rules()
            for rule_name, app_path in FIREWALL_APPS.items():
                cmd = ["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=out", "action=block", f"program={app_path}", "enable=yes"]
                subprocess.run(cmd, capture_output=True, check=False, creationflags=CREATE_NO_WINDOW)
            return True
        except Exception as e:
            print(f"Error enabling AntiSpy: {e}")
            return False

    @staticmethod
    def disable_antispy() -> bool:
        try:
            backup_data = None
            if os.path.exists(BACKUP_FILE):
                try:
                    with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                        backup_data = json.load(f)
                except Exception:
                    pass

            for service in TELEMETRY_SERVICES:
                start_type = "auto"
                if backup_data and "services" in backup_data and service in backup_data["services"]:
                    start_type = backup_data["services"][service]
                subprocess.run(["sc", "config", service, "start=", start_type], capture_output=True, check=False, creationflags=CREATE_NO_WINDOW)
                if start_type != "disabled":
                    subprocess.run(["net", "start", service], capture_output=True, check=False, creationflags=CREATE_NO_WINDOW)

            if backup_data and "registry_telemetry" in backup_data:
                orig_reg = backup_data["registry_telemetry"]
                if orig_reg == "NOT_FOUND":
                    # Key did not exist before AntiSpy was enabled — remove the
                    # value we set; if the key or value is already gone, that's fine.
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_DATA_COLLECTION, 0, winreg.KEY_SET_VALUE)
                        try: winreg.DeleteValue(key, "AllowTelemetry")
                        except FileNotFoundError: pass
                        winreg.CloseKey(key)
                    except FileNotFoundError:
                        pass
                else:
                    key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, REG_DATA_COLLECTION, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, orig_reg)
                    winreg.CloseKey(key)

            AntiSpyManager._remove_firewall_rules()
            if os.path.exists(BACKUP_FILE):
                os.remove(BACKUP_FILE)
            return True
        except Exception as e:
            print(f"Error disabling AntiSpy: {e}")
            return False

    @staticmethod
    def _remove_firewall_rules():
        for rule_name in FIREWALL_APPS.keys():
            cmd = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"]
            subprocess.run(cmd, capture_output=True, check=False, creationflags=CREATE_NO_WINDOW)