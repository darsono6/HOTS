import subprocess
import winreg
from typing import Tuple

from .core_antispy import CREATE_NO_WINDOW, _is_admin, _resolve_powershell_exe, _console_encoding
from .i18n import T

_RESTORE_KEY_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore"
_RESTORE_VALUE_NAME = "SystemRestorePointCreationFrequency"


class SystemRestoreManager:
    last_error = ""

    @staticmethod
    def remove_frequency_limit() -> Tuple[bool, str]:
        if not _is_admin():
            return False, T("priv_restore_msg_no_admin")

        try:
            key = winreg.CreateKeyEx(
                winreg.HKEY_LOCAL_MACHINE, _RESTORE_KEY_PATH,
                0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY,
            )
            try:
                winreg.SetValueEx(key, _RESTORE_VALUE_NAME, 0, winreg.REG_DWORD, 0)
            finally:
                winreg.CloseKey(key)
        except OSError as e:
            return False, str(e)

        return True, ""

    @staticmethod
    def create_restore_point(description: str, drive: str = "C:\\") -> Tuple[str, str]:
        SystemRestoreManager.last_error = ""

        if not _is_admin():
            SystemRestoreManager.last_error = T("priv_restore_msg_no_admin")
            return "no_admin", SystemRestoreManager.last_error

        ps_exe = _resolve_powershell_exe()
        if ps_exe is None:
            SystemRestoreManager.last_error = T("priv_restore_detail_no_powershell")
            return "error", SystemRestoreManager.last_error

        safe_desc = description.replace('"', "'").replace("`", "'")
        safe_drive = drive.replace('"', "").replace("`", "")

        ps_command = (
            "$ErrorActionPreference = 'Stop'\n"
            "$WarningPreference = 'SilentlyContinue'\n"
            "try {\n"
            f'    try {{ Enable-ComputerRestore -Drive "{safe_drive}" }} catch {{}}\n'
            "    $before = Get-ComputerRestorePoint | Sort-Object SequenceNumber | Select-Object -Last 1\n"
            "    $beforeSeq = if ($before) { $before.SequenceNumber } else { -1 }\n"
            f'    Checkpoint-Computer -Description "{safe_desc}" -RestorePointType "MODIFY_SETTINGS"\n'
            "    Start-Sleep -Milliseconds 800\n"
            "    $after = Get-ComputerRestorePoint | Sort-Object SequenceNumber | Select-Object -Last 1\n"
            "    $afterSeq = if ($after) { $after.SequenceNumber } else { -1 }\n"
            "    if ($afterSeq -gt $beforeSeq) { Write-Output 'CREATED' } else { Write-Output 'THROTTLED' }\n"
            "} catch {\n"
            '    Write-Output "ERROR:$($_.Exception.Message)"\n'
            "}"
        )

        try:
            result = subprocess.run(
                [ps_exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, check=False,
                encoding=_console_encoding(), errors="replace",
                creationflags=CREATE_NO_WINDOW, timeout=120,
            )
        except subprocess.TimeoutExpired:
            SystemRestoreManager.last_error = T("priv_restore_detail_timeout")
            return "error", SystemRestoreManager.last_error
        except Exception as e:
            SystemRestoreManager.last_error = str(e)
            return "error", SystemRestoreManager.last_error

        out = (result.stdout or "").strip()
        last_line = out.splitlines()[-1].strip() if out else ""
        if last_line == "CREATED":
            return "created", ""
        if last_line == "THROTTLED":
            return "throttled", ""
        if last_line.startswith("ERROR:"):
            msg = last_line[len("ERROR:"):].strip()
            SystemRestoreManager.last_error = msg
            return "error", msg

        err = (result.stderr or out or T("priv_restore_detail_unknown_error")).strip()
        SystemRestoreManager.last_error = err
        return "error", err
