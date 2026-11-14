import json
import logging
import os
import subprocess
import threading
import winreg
from typing import Optional

from .core_antispy import _is_admin, _console_encoding, CREATE_NO_WINDOW
from .i18n import T
from .secure_storage import PROGRAMDATA_DIR, atomic_write_json

logger = logging.getLogger("HOTS.netblock")

STATE_FILE = os.path.join(PROGRAMDATA_DIR, "netblock_state.json")
NETSH_EXE = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "netsh.exe")

_RULES = (
    ("HOTS Internet Block v4",
     "1.0.0.0-9.255.255.255,11.0.0.0-126.255.255.255,128.0.0.0-169.253.255.255,"
     "169.255.0.0-172.15.255.255,172.32.0.0-192.167.255.255,192.169.0.0-223.255.255.255"),
    ("HOTS Internet Block v6", "2000::/3"),
)

_FIREWALL_POLICY_KEY = r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy"


def _run_netsh(args: list) -> Optional[subprocess.CompletedProcess]:
    try:
        return subprocess.run(
            [NETSH_EXE, *args],
            capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
            creationflags=CREATE_NO_WINDOW, timeout=30,
        )
    except Exception as e:
        logger.warning("_run_netsh: exception running %s: %s", args, e)
        return None


def _rule_exists(name: str) -> bool:
    r = _run_netsh(["advfirewall", "firewall", "show", "rule", f"name={name}"])
    return r is not None and r.returncode == 0


def _remove_rules() -> None:
    for name, _remote in _RULES:
        _run_netsh(["advfirewall", "firewall", "delete", "rule", f"name={name}"])


def _firewall_profiles_on() -> bool:
    for profile in ("DomainProfile", "StandardProfile", "PublicProfile"):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{_FIREWALL_POLICY_KEY}\\{profile}") as key:
                if winreg.QueryValueEx(key, "EnableFirewall")[0] == 0:
                    return False
        except OSError:
            continue
    return True


class NetBlockManager:

    last_error: str = ""
    _op_lock = threading.RLock()

    @staticmethod
    def is_active() -> bool:
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return False
        return isinstance(data, dict) and data.get("active") is True

    @staticmethod
    def rules_present() -> bool:
        return all(_rule_exists(name) for name, _remote in _RULES)

    @staticmethod
    def enable() -> bool:
        with NetBlockManager._op_lock:
            NetBlockManager.last_error = ""
            if not _is_admin():
                NetBlockManager.last_error = T("antispy_err_no_admin")
                return False
            r = _run_netsh(["advfirewall", "set", "allprofiles", "state", "on"])
            if r is None or r.returncode != 0:
                NetBlockManager.last_error = T("netblock_err_firewall")
                return False
            try:
                for name, remote in _RULES:
                    _run_netsh(["advfirewall", "firewall", "delete", "rule", f"name={name}"])
                    r = _run_netsh([
                        "advfirewall", "firewall", "add", "rule",
                        f"name={name}", "dir=out", "action=block", f"remoteip={remote}",
                        "profile=any", "interfacetype=any", "enable=yes",
                    ])
                    if r is None or r.returncode != 0:
                        NetBlockManager.last_error = (
                            (r.stderr or r.stdout).strip() if r is not None else ""
                        ) or T("netblock_err_rule")
                        _remove_rules()
                        return False
                if not NetBlockManager.rules_present():
                    NetBlockManager.last_error = T("netblock_err_rule")
                    _remove_rules()
                    return False
                atomic_write_json(STATE_FILE, {"active": True})
            except Exception as e:
                NetBlockManager.last_error = str(e)
                logger.exception("NetBlockManager.enable: unexpected error")
                _remove_rules()
                return False
            logger.info("NetBlockManager.enable: OK")
            return True

    @staticmethod
    def disable() -> bool:
        with NetBlockManager._op_lock:
            NetBlockManager.last_error = ""
            if not _is_admin():
                NetBlockManager.last_error = T("antispy_err_no_admin")
                return False
            _remove_rules()
            if any(_rule_exists(name) for name, _remote in _RULES):
                NetBlockManager.last_error = T("netblock_err_rule")
                return False
            try:
                atomic_write_json(STATE_FILE, {"active": False})
            except Exception as e:
                NetBlockManager.last_error = str(e)
                logger.exception("NetBlockManager.disable: cannot save state")
                return False
            logger.info("NetBlockManager.disable: OK")
            return True

    @staticmethod
    def check_drift() -> Optional[str]:
        if not NetBlockManager.is_active():
            return None
        if NetBlockManager.rules_present() and _firewall_profiles_on():
            return None
        return "restored" if NetBlockManager.enable() else "regressed"
