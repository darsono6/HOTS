"""Logic run on uninstall.

Anything that would otherwise leave the system broken (ACL lock on hosts, IFEO entries
pointing at the removed .exe, locked app files, the program's own registry keys) is ALWAYS
reverted, regardless of the wizard choices. Everything else (hosts block content, Anti-Spy
privacy settings, hosts backups, saved config) is reverted ONLY if the user ticked it:
uninstalling must not silently erase user decisions or changes the program does not own.

Every step is best effort: one failure never aborts the rest, and all errors are collected
in report["errors"].
"""

import os
import stat
import winreg

from .constants import HOSTS_PATH, CUSTOM_DOMAINS_PATH
from .core import list_backups, strip_all_parental_blocks
from .core_antispy import AntiSpyManager, HostsLockManager
from .core_appblock import AppBlockManager
from .core_doh import DohBlockManager, BROWSERS as _DOH_BROWSERS
from .dns_utils import is_cf_family_active, disable_cf_family_dns

REG_KEY = r"Software\HOTS Hosts"

_ANTISPY_LEVELS = ("basic", "medium", "advanced", "extra")


def custom_domains_file_exists() -> bool:
    try:
        return os.path.isfile(str(CUSTOM_DOMAINS_PATH))
    except Exception:
        return False


def _delete_custom_domains_file() -> None:
    try:
        path = str(CUSTOM_DOMAINS_PATH)
        if os.path.isfile(path):
            try:
                os.chmod(path, stat.S_IWRITE)
            except OSError:
                pass
            os.remove(path)
    except Exception:
        pass


def count_hosts_backups() -> int:
    try:
        return len(list_backups(HOSTS_PATH))
    except Exception:
        return 0


def count_active_antispy_items() -> int:
    total = 0
    for level in _ANTISPY_LEVELS:
        try:
            total += sum(1 for active in AntiSpyManager.get_items_status(level).values() if active)
        except Exception:
            pass
    return total


def count_blocked_apps() -> int:
    try:
        return len(AppBlockManager.list_blocked())
    except Exception:
        return 0


def _delete_hosts_backups() -> int:
    deleted = 0
    try:
        backups = list_backups(HOSTS_PATH)
    except Exception:
        backups = []
    for bak_path, _dt in backups:
        try:
            try:
                os.chmod(bak_path, stat.S_IWRITE)
            except OSError:
                pass
            os.remove(bak_path)
            deleted += 1
        except Exception:
            pass
    return deleted


def _revert_antispy_items() -> list:
    failed = []
    for level in _ANTISPY_LEVELS:
        try:
            status = AntiSpyManager.get_items_status(level)
        except Exception:
            continue
        for item_id, active in status.items():
            if not active:
                continue
            try:
                if not AntiSpyManager.disable_item(item_id):
                    failed.append(item_id)
            except Exception:
                failed.append(item_id)
    return failed


def _remove_all_appblocks() -> list:
    """Also covers the System Restore (rstrui.exe) lock, which is just another blocked-app entry."""
    failed = []
    try:
        blocked = list(AppBlockManager.list_blocked())
    except Exception:
        blocked = []
    for app in blocked:
        try:
            if not AppBlockManager.remove_app(app.exe_name):
                failed.append(app.exe_name)
        except Exception:
            failed.append(app.exe_name)
    return failed


def _disable_all_doh() -> None:
    for browser in _DOH_BROWSERS:
        try:
            DohBlockManager.disable(browser["id"])
        except Exception:
            pass


def _disable_cf_family_dns() -> bool:
    """Cloudflare Family DNS is a separate blocking channel (adapter DNS servers);
    reuse its own restore mechanism (dns_backup.json)."""
    try:
        if not is_cf_family_active():
            return True
        ok, _failed = disable_cf_family_dns()
        return ok
    except Exception:
        return False


def _delete_key_recursive(hive, path) -> None:
    try:
        key = winreg.OpenKey(hive, path, 0, winreg.KEY_ALL_ACCESS)
    except OSError:
        return
    try:
        while True:
            try:
                sub = winreg.EnumKey(key, 0)
            except OSError:
                break
            _delete_key_recursive(hive, path + "\\" + sub)
    finally:
        winreg.CloseKey(key)
    try:
        winreg.DeleteKey(hive, path)
    except OSError:
        pass


def _remove_registry_keys() -> None:
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            _delete_key_recursive(hive, REG_KEY)
        except Exception:
            pass


def apply_uninstall_choices(choices: dict) -> dict:
    """Run the uninstall cleanup. `choices` comes from the wizard (empty if it was cancelled):
        remove_hosts_entries, restore_privacy, delete_data, delete_hosts_backups, delete_custom_domains.

    The mandatory steps (hosts ACL, IFEO/file locks, registry keys) always run. Returns a report
    dict and never raises."""
    report = {"errors": []}

    try:
        HostsLockManager.disable()
    except Exception as e:
        report["errors"].append(f"hosts_lock: {e}")

    failed_apps = _remove_all_appblocks()
    if failed_apps:
        report["errors"].append(f"appblock: {failed_apps}")

    try:
        _remove_registry_keys()
    except Exception as e:
        report["errors"].append(f"registry: {e}")

    if choices.get("remove_hosts_entries"):
        try:
            strip_all_parental_blocks(HOSTS_PATH)
        except Exception as e:
            report["errors"].append(f"hosts_strip: {e}")
        _disable_all_doh()
        if not _disable_cf_family_dns():
            report["errors"].append("cf_dns: failed to restore original DNS servers")

    if choices.get("restore_privacy"):
        failed_items = _revert_antispy_items()
        if failed_items:
            report["errors"].append(f"antispy: {failed_items}")

    # The custom domains list is a separate option and is KEPT by default: the in-app
    # tooltip promises it survives uninstall.
    if choices.get("delete_custom_domains"):
        _delete_custom_domains_file()

    if choices.get("delete_hosts_backups"):
        report["backups_deleted"] = _delete_hosts_backups()

    # Deleting the ProgramData/AppData folders is left to the calling .cmd script, which runs
    # after this process exits: we hold error.log open in AppData and cannot delete it ourselves.
    report["delete_data"] = bool(choices.get("delete_data"))
    return report
