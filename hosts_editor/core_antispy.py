import ctypes
import functools
import json
import logging
import os
import shutil
import subprocess
import tempfile
import threading
from typing import Dict, List, Optional, Tuple

from .constants import HOSTS_PATH
from .i18n import T

import winreg

logger = logging.getLogger("HOTS.antispy")

REG_DATA_COLLECTION = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
REG_CLOUD_CONTENT = r"SOFTWARE\Policies\Microsoft\Windows\CloudContent"
REG_DELIVERY_OPT = r"SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization"
REG_WINDOWS_AI = r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI"
REG_SQM_CLIENT = r"SOFTWARE\Policies\Microsoft\SQMClient\Windows"
REG_ACTIVITY_FEED = r"SOFTWARE\Policies\Microsoft\Windows\System"
REG_LOCATION = r"SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors"
REG_FIND_MY_DEVICE = r"SOFTWARE\Policies\Microsoft\FindMyDevice"

ITEMS: List[dict] = [
    {"id": "basic_reg_telemetry", "desc_key": "priv_desc_basic_reg_telemetry", "level": "basic", "kind": "hklm_reg",
     "label_key": "priv_item_basic_reg",
     "path": REG_DATA_COLLECTION, "name": "AllowTelemetry", "protect_value": 0},
    {"id": "basic_svc_diagtrack", "desc_key": "priv_desc_basic_svc_diagtrack", "level": "basic", "kind": "service",
     "label_key": "priv_item_basic_diagtrack", "service": "DiagTrack"},
    {"id": "basic_svc_dmwap", "desc_key": "priv_desc_basic_svc_dmwap", "level": "basic", "kind": "service",
     "label_key": "priv_item_basic_dmwap", "service": "dmwappushservice"},
    {"id": "basic_reg_experimentation", "desc_key": "priv_desc_basic_reg_experimentation", "level": "basic", "kind": "hklm_reg",
     "label_key": "priv_item_basic_experimentation",
     "path": REG_DATA_COLLECTION, "name": "AllowExperimentation", "protect_value": 0},
    {"id": "basic_reg_consumerfeatures", "desc_key": "priv_desc_basic_reg_consumerfeatures", "level": "basic", "kind": "hklm_reg",
     "label_key": "priv_item_basic_consumerfeatures",
     "path": REG_CLOUD_CONTENT, "name": "DisableWindowsConsumerFeatures", "protect_value": 1},
    {"id": "basic_reg_tailored", "desc_key": "priv_desc_basic_reg_tailored", "level": "basic", "kind": "hklm_reg",
     "label_key": "priv_item_basic_tailored",
     "path": REG_CLOUD_CONTENT, "name": "DisableTailoredExperiencesWithDiagnosticData", "protect_value": 1},
    {"id": "basic_reg_deliveryopt", "desc_key": "priv_desc_basic_reg_deliveryopt", "level": "basic", "kind": "hklm_reg",
     "label_key": "priv_item_basic_deliveryopt",
     "path": REG_DELIVERY_OPT, "name": "DODownloadMode", "protect_value": 0},
    {"id": "basic_reg_recall", "desc_key": "priv_desc_basic_reg_recall", "level": "basic", "kind": "hklm_reg",
     "label_key": "priv_item_basic_recall",
     "path": REG_WINDOWS_AI, "name": "DisableAIDataAnalysis", "protect_value": 1},
    {"id": "basic_reg_feedback", "desc_key": "priv_desc_basic_reg_feedback", "level": "basic", "kind": "hklm_reg",
     "label_key": "priv_item_basic_feedback",
     "path": REG_DATA_COLLECTION, "name": "DoNotShowFeedbackNotifications", "protect_value": 1},
    {"id": "basic_reg_ceip", "desc_key": "priv_desc_basic_reg_ceip", "level": "basic", "kind": "hklm_reg",
     "label_key": "priv_item_basic_ceip",
     "path": REG_SQM_CLIENT, "name": "CEIPEnable", "protect_value": 0},
    {"id": "advertising_id", "desc_key": "priv_desc_advertising_id", "level": "basic", "kind": "hkcu_reg",
     "label_key": "priv_tweak_advertising_id",
     "path": r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
     "name": "Enabled", "protect_value": 0},
    {"id": "bing_search", "desc_key": "priv_desc_bing_search", "level": "basic", "kind": "hkcu_reg",
     "label_key": "priv_tweak_bing_search",
     "path": r"Software\Microsoft\Windows\CurrentVersion\Search",
     "name": "BingSearchEnabled", "protect_value": 0},
    {"id": "search_suggestions", "desc_key": "priv_desc_search_suggestions", "level": "basic", "kind": "hkcu_reg",
     "label_key": "priv_tweak_search_suggestions",
     "path": r"Software\Policies\Microsoft\Windows\Explorer",
     "name": "DisableSearchBoxSuggestions", "protect_value": 1},

    {"id": "medium_fw_compattel", "desc_key": "priv_desc_medium_fw_compattel", "level": "medium", "kind": "firewall",
     "label_key": "priv_item_medium_compattel",
     "rule_name": "HOTS_AntiSpy_CompatTel", "exe": r"%systemroot%\System32\CompatTelRunner.exe"},
    {"id": "medium_fw_devicecensus", "desc_key": "priv_desc_medium_fw_devicecensus", "level": "medium", "kind": "firewall",
     "label_key": "priv_item_medium_devicecensus",
     "rule_name": "HOTS_AntiSpy_DeviceCensus", "exe": r"%systemroot%\System32\devicecensus.exe"},
    {"id": "medium_fw_werfault", "desc_key": "priv_desc_medium_fw_werfault", "level": "medium", "kind": "firewall",
     "label_key": "priv_item_medium_werfault",
     "rule_name": "HOTS_AntiSpy_WerFault", "exe": r"%systemroot%\System32\WerFault.exe"},
    {"id": "medium_task_appraiser", "desc_key": "priv_desc_medium_task_appraiser", "level": "medium", "kind": "task",
     "label_key": "priv_item_medium_appraiser",
     "task_path": r"\Microsoft\Windows\Application Experience", "task_name": "Microsoft Compatibility Appraiser"},
    {"id": "medium_task_programdata", "desc_key": "priv_desc_medium_task_programdata", "level": "medium", "kind": "task",
     "label_key": "priv_item_medium_programdata",
     "task_path": r"\Microsoft\Windows\Application Experience", "task_name": "ProgramDataUpdater"},
    {"id": "medium_task_consolidator", "desc_key": "priv_desc_medium_task_consolidator", "level": "medium", "kind": "task",
     "label_key": "priv_item_medium_consolidator",
     "task_path": r"\Microsoft\Windows\Customer Experience Improvement Program", "task_name": "Consolidator"},
    {"id": "medium_task_usbceip", "desc_key": "priv_desc_medium_task_usbceip", "level": "medium", "kind": "task",
     "label_key": "priv_item_medium_usbceip",
     "task_path": r"\Microsoft\Windows\Customer Experience Improvement Program", "task_name": "UsbCeip"},
    {"id": "medium_task_queuereporting", "desc_key": "priv_desc_medium_task_queuereporting", "level": "medium", "kind": "task",
     "label_key": "priv_item_medium_queuereporting",
     "task_path": r"\Microsoft\Windows\Windows Error Reporting", "task_name": "QueueReporting"},
    {"id": "medium_task_kernelceip", "desc_key": "priv_desc_medium_task_kernelceip", "level": "medium", "kind": "task",
     "label_key": "priv_item_medium_kernelceip",
     "task_path": r"\Microsoft\Windows\Customer Experience Improvement Program", "task_name": "KernelCeipTask"},
    {"id": "medium_task_diskdiagnostic", "desc_key": "priv_desc_medium_task_diskdiagnostic", "level": "medium", "kind": "task",
     "label_key": "priv_item_medium_diskdiagnostic",
     "task_path": r"\Microsoft\Windows\DiskDiagnostic", "task_name": "Microsoft-Windows-DiskDiagnosticDataCollector"},
    {"id": "medium_task_siuf_dmclient", "desc_key": "priv_desc_medium_task_siuf_dmclient", "level": "medium", "kind": "task",
     "label_key": "priv_item_medium_siuf_dmclient",
     "task_path": r"\Microsoft\Windows\Feedback\Siuf", "task_name": "DmClient"},
    {"id": "medium_task_siuf_dmclientonscenario", "desc_key": "priv_desc_medium_task_siuf_dmclientonscenario", "level": "medium", "kind": "task",
     "label_key": "priv_item_medium_siuf_dmclientonscenario",
     "task_path": r"\Microsoft\Windows\Feedback\Siuf", "task_name": "DmClientOnScenarioDownload"},

    {"id": "advanced_svc_wersvc", "desc_key": "priv_desc_advanced_svc_wersvc", "level": "advanced", "kind": "service",
     "label_key": "priv_item_advanced_wersvc", "service": "WerSvc"},
    {"id": "advanced_svc_pcasvc", "desc_key": "priv_desc_advanced_svc_pcasvc", "level": "advanced", "kind": "service",
     "label_key": "priv_item_advanced_pcasvc", "service": "PcaSvc"},
    {"id": "advanced_reg_activityfeed", "desc_key": "priv_desc_advanced_reg_activityfeed", "level": "advanced", "kind": "hklm_reg",
     "label_key": "priv_item_advanced_activityfeed",
     "path": REG_ACTIVITY_FEED, "name": "EnableActivityFeed", "protect_value": 0},
    {"id": "advanced_reg_publishactivities", "desc_key": "priv_desc_advanced_reg_publishactivities", "level": "advanced", "kind": "hklm_reg",
     "label_key": "priv_item_advanced_publishactivities",
     "path": REG_ACTIVITY_FEED, "name": "PublishUserActivities", "protect_value": 0},
    {"id": "advanced_reg_uploadactivities", "desc_key": "priv_desc_advanced_reg_uploadactivities", "level": "advanced", "kind": "hklm_reg",
     "label_key": "priv_item_advanced_uploadactivities",
     "path": REG_ACTIVITY_FEED, "name": "UploadUserActivities", "protect_value": 0},

    {"id": "extra_svc_lfsvc", "desc_key": "priv_desc_extra_svc_lfsvc", "level": "extra", "kind": "service",
     "label_key": "priv_item_extra_lfsvc", "service": "lfsvc"},
    {"id": "extra_reg_disablelocation", "desc_key": "priv_desc_extra_reg_disablelocation", "level": "extra", "kind": "hklm_reg",
     "label_key": "priv_item_extra_disablelocation",
     "path": REG_LOCATION, "name": "DisableLocation", "protect_value": 1},
    {"id": "extra_reg_text_collection", "desc_key": "priv_desc_extra_reg_text_collection", "level": "extra", "kind": "hkcu_reg",
     "label_key": "priv_item_extra_text_collection",
     "path": r"Software\Microsoft\InputPersonalization", "name": "RestrictImplicitTextCollection", "protect_value": 1},
    {"id": "extra_reg_ink_collection", "desc_key": "priv_desc_extra_reg_ink_collection", "level": "extra", "kind": "hkcu_reg",
     "label_key": "priv_item_extra_ink_collection",
     "path": r"Software\Microsoft\InputPersonalization", "name": "RestrictImplicitInkCollection", "protect_value": 1},
    {"id": "extra_reg_personalization_policy", "desc_key": "priv_desc_extra_reg_personalization_policy", "level": "extra", "kind": "hkcu_reg",
     "label_key": "priv_item_extra_personalization_policy",
     "path": r"Software\Microsoft\Personalization\Settings", "name": "AcceptedPrivacyPolicy", "protect_value": 0},
    {"id": "extra_reg_cross_device_clipboard", "desc_key": "priv_desc_extra_reg_cross_device_clipboard", "level": "extra", "kind": "hklm_reg",
     "label_key": "priv_item_extra_cross_device_clipboard",
     "path": REG_ACTIVITY_FEED, "name": "AllowCrossDeviceClipboard", "protect_value": 0},
    {"id": "extra_reg_findmydevice", "desc_key": "priv_desc_extra_reg_findmydevice", "level": "extra", "kind": "hklm_reg",
     "label_key": "priv_item_extra_findmydevice",
     "path": REG_FIND_MY_DEVICE, "name": "AllowFindMyDevice", "protect_value": 0},
]

LEVELS = ("basic", "medium", "advanced", "extra")

def _find_item(item_id: str) -> Optional[dict]:
    for it in ITEMS:
        if it["id"] == item_id:
            return it
    return None

def _items_for_level(level: str) -> List[dict]:
    return [it for it in ITEMS if it["level"] == level]

def _reg_key(item: dict) -> str:
    return f"{item['path']}::{item['name']}"

def _normalize_privacy_active(priv: dict) -> Dict[str, bool]:
    active = priv.get("active", {})
    if isinstance(active, bool):
        values = priv.get("values", {})
        return {k: True for k in values} if active else {}
    return dict(active or {})

HOTS_PROGRAMDATA_DIR = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "HOTS Hosts")
BACKUP_FILE = os.path.join(HOTS_PROGRAMDATA_DIR, "HOTS_antispy_state.json")

HOTS_APPDATA_DIR = os.path.join(os.environ.get("APPDATA", "C:\\"), "HOTS Hosts")
USER_BACKUP_FILE = os.path.join(HOTS_APPDATA_DIR, "HOTS_antispy_user_state.json")

_LEGACY_BACKUP_FILE = os.path.join(os.environ.get("APPDATA", "C:\\"), "HOTS Hosts", "HOTS_antispy_state.json")

CREATE_NO_WINDOW = 0x08000000

_SYSTEM32 = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")
SC_EXE = os.path.join(_SYSTEM32, "sc.exe")
NET_EXE = os.path.join(_SYSTEM32, "net.exe")
NETSH_EXE = os.path.join(_SYSTEM32, "netsh.exe")
POWERSHELL_EXE = os.path.join(_SYSTEM32, "WindowsPowerShell", "v1.0", "powershell.exe")
ICACLS_EXE = os.path.join(_SYSTEM32, "icacls.exe")

HOSTS_LOCK_STATE_FILE = os.path.join(HOTS_PROGRAMDATA_DIR, "HOTS_hosts_lock_state.json")
HOSTS_LOCK_SID = "S-1-5-32-545"

_PS_MISSING = "__ps_missing__"

_ps_exe_cache: Optional[str] = None
_ps_exe_resolved = False

def _resolve_powershell_exe() -> Optional[str]:
    global _ps_exe_cache, _ps_exe_resolved
    if _ps_exe_resolved:
        return _ps_exe_cache

    _ps_exe_resolved = True

    if os.path.isfile(POWERSHELL_EXE):
        _ps_exe_cache = POWERSHELL_EXE
        return _ps_exe_cache

    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    pwsh_root = os.path.join(program_files, "PowerShell")
    candidate = None
    try:
        if os.path.isdir(pwsh_root):
            for entry in sorted(os.listdir(pwsh_root), reverse=True):
                exe = os.path.join(pwsh_root, entry, "pwsh.exe")
                if os.path.isfile(exe):
                    candidate = exe
                    break
    except Exception:
        candidate = None

    if candidate:
        logger.warning("powershell.exe unavailable — using pwsh.exe: %s", candidate)
        _ps_exe_cache = candidate
        return _ps_exe_cache

    which_candidate = shutil.which("powershell") or shutil.which("pwsh")
    if which_candidate:
        logger.warning("powershell.exe/pwsh.exe not at default paths — found via PATH: %s", which_candidate)
        _ps_exe_cache = which_candidate
        return _ps_exe_cache

    logger.error("No PowerShell interpreter found (neither powershell.exe nor pwsh.exe).")
    _ps_exe_cache = None
    return _ps_exe_cache

def _migrate_legacy_backup() -> None:
    try:
        if not os.path.exists(_LEGACY_BACKUP_FILE) or os.path.exists(BACKUP_FILE):
            return
        with open(_LEGACY_BACKUP_FILE, "r", encoding="utf-8") as f:
            legacy = json.load(f)
        if "services" not in legacy:
            return
        new_data = {
            "basic": {
                "active": True,
                "services": legacy.get("services", {}),
                "registry_telemetry": legacy.get("registry_telemetry"),
            }
        }
        _atomic_write_json(BACKUP_FILE, new_data)
        os.remove(_LEGACY_BACKUP_FILE)
        logger.info("Migrated old (flat) AntiSpy backup to the modular format.")
    except Exception as e:
        logger.warning("Migration of the old AntiSpy backup file failed: %s", e)

def _is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def _console_encoding() -> str:
    try:
        return f"cp{ctypes.windll.kernel32.GetOEMCP()}"
    except Exception:
        return "utf-8"

def _atomic_write_json(path: str, data: dict) -> None:
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".antispy_", suffix=".tmp")
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

def _load_json(path: str) -> Optional[dict]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Failed to read %s: %s", path, e)
        return None

_MEDIUM_TASK_ID_BY_KEY = {
    f"{path}\\{name}": item["id"]
    for item in ITEMS if item["kind"] == "task"
    for path, name in [(item["task_path"], item["task_name"])]
}

def _normalize_machine_data(raw: Optional[dict]) -> Dict[str, dict]:
    if not raw:
        return {}
    if "items" in raw:
        return dict(raw["items"])

    items: Dict[str, dict] = {}

    basic = raw.get("basic", {})
    if basic.get("active"):
        services = basic.get("services", {})
        items["basic_reg_telemetry"] = {"active": True, "original": basic.get("registry_telemetry")}
        items["basic_svc_diagtrack"] = {"active": True, "original": services.get("DiagTrack", "auto")}
        items["basic_svc_dmwap"] = {"active": True, "original": services.get("dmwappushservice", "auto")}

    medium = raw.get("medium", {})
    if medium.get("active"):
        for item_id in ("medium_fw_compattel", "medium_fw_devicecensus", "medium_fw_werfault"):
            items[item_id] = {"active": True}
        for key, state in medium.get("scheduled_tasks", {}).items():
            item_id = _MEDIUM_TASK_ID_BY_KEY.get(key)
            if item_id:
                items[item_id] = {"active": True, "original": state}

    adv_svc = raw.get("advanced_services", {})
    if adv_svc.get("active"):
        services = adv_svc.get("services", {})
        items["advanced_svc_wersvc"] = {"active": True, "original": services.get("WerSvc", "demand")}
        items["advanced_svc_pcasvc"] = {"active": True, "original": services.get("PcaSvc", "demand")}

    return items

def _normalize_user_data(raw: Optional[dict]) -> Dict[str, dict]:
    if not raw:
        return {}
    if "items" in raw:
        return dict(raw["items"])

    items: Dict[str, dict] = {}
    priv = raw.get("advanced_privacy", {})
    values = priv.get("values", {})
    active = _normalize_privacy_active(priv)
    for item in ITEMS:
        if item["kind"] != "hkcu_reg":
            continue
        key = _reg_key(item)
        if key in values:
            items[item["id"]] = {"active": bool(active.get(key)), "original": values[key]}
    return items

_machine_items_cache: Optional[Dict[str, dict]] = None
_user_items_cache: Optional[Dict[str, dict]] = None
_items_cache_lock = threading.Lock()

def _load_machine_items() -> Dict[str, dict]:
    global _machine_items_cache
    with _items_cache_lock:
        if _machine_items_cache is None:
            _machine_items_cache = _normalize_machine_data(_load_json(BACKUP_FILE))
        return _machine_items_cache

def _load_user_items() -> Dict[str, dict]:
    global _user_items_cache
    with _items_cache_lock:
        if _user_items_cache is None:
            _user_items_cache = _normalize_user_data(_load_json(USER_BACKUP_FILE))
        return _user_items_cache

def _save_machine_items(items: Dict[str, dict]) -> None:
    global _machine_items_cache
    _atomic_write_json(BACKUP_FILE, {"items": items})
    with _items_cache_lock:
        _machine_items_cache = items

def _save_user_items(items: Dict[str, dict]) -> None:
    global _user_items_cache
    _atomic_write_json(USER_BACKUP_FILE, {"items": items})
    with _items_cache_lock:
        _user_items_cache = items

def _item_store(item: dict):
    if item["kind"] == "hkcu_reg":
        return _load_user_items, _save_user_items
    return _load_machine_items, _save_machine_items

def _ensure_seeded() -> None:
    machine_needed = not os.path.exists(BACKUP_FILE)
    user_needed = not os.path.exists(USER_BACKUP_FILE)
    if not machine_needed and not user_needed:
        return
    try:
        real, missing = AntiSpyManager._get_real_status_all()
    except Exception as e:
        logger.warning("Initial AntiSpy state scan failed, assuming everything is disabled: %s", e)
        real, missing = {}, {}
    if machine_needed:
        machine_items = {it["id"]: {"active": real.get(it["id"], False) and not missing.get(it["id"], False),
                                     "missing": missing.get(it["id"], False)}
                          for it in ITEMS if it["kind"] != "hkcu_reg"}
        _save_machine_items(machine_items)
        logger.info("Created initial AntiSpy cache (machine) — %d items", len(machine_items))
    if user_needed:
        user_items = {it["id"]: {"active": real.get(it["id"], False) and not missing.get(it["id"], False),
                                  "missing": missing.get(it["id"], False)}
                       for it in ITEMS if it["kind"] == "hkcu_reg"}
        _save_user_items(user_items)
        logger.info("Created initial AntiSpy cache (user) — %d items", len(user_items))

_migrate_legacy_backup()

def _serialized(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with AntiSpyManager._op_lock:
            return fn(*args, **kwargs)
    return wrapper

class AntiSpyManager:
    last_error: str = ""
    last_warnings: List[str] = []

    _op_lock = threading.RLock()

    @staticmethod
    def is_item_flag_active(item_id: str) -> bool:
        item = _find_item(item_id)
        if not item:
            return False
        loader, _ = _item_store(item)
        return bool(loader().get(item_id, {}).get("active"))

    @staticmethod
    def is_item_active(item_id: str) -> bool:
        item = _find_item(item_id)
        if not item:
            return False
        protected, _missing = AntiSpyManager._item_is_protected(item)
        return protected

    @staticmethod
    def get_items_status(level: str) -> Dict[str, bool]:
        items = _items_for_level(level)
        machine_cache = _load_machine_items()
        user_cache = _load_user_items()
        result = {}
        for it in items:
            cache = user_cache if it["kind"] == "hkcu_reg" else machine_cache
            result[it["id"]] = bool(cache.get(it["id"], {}).get("active"))
        return result

    @staticmethod
    def is_item_missing(item_id: str) -> bool:
        item = _find_item(item_id)
        if not item:
            return False
        loader, _ = _item_store(item)
        return bool(loader().get(item_id, {}).get("missing"))

    @staticmethod
    def _get_real_status_all() -> Tuple[Dict[str, bool], Dict[str, bool]]:
        task_cache, svc_cache = AntiSpyManager._prefetch_level_caches(ITEMS)
        status: Dict[str, bool] = {}
        missing: Dict[str, bool] = {}
        for it in ITEMS:
            protected, is_missing = AntiSpyManager._item_is_protected(it, task_cache, svc_cache)
            status[it["id"]] = protected
            missing[it["id"]] = is_missing
        return status, missing

    @staticmethod
    def is_basic_active() -> bool:
        return all(AntiSpyManager.get_items_status("basic").values())

    @staticmethod
    def is_medium_active() -> bool:
        return all(AntiSpyManager.get_items_status("medium").values())

    @staticmethod
    def is_advanced_active() -> bool:
        return all(AntiSpyManager.get_items_status("advanced").values())

    @staticmethod
    def is_extra_active() -> bool:
        return all(AntiSpyManager.get_items_status("extra").values())

    @staticmethod
    def get_status() -> Dict[str, bool]:
        return {lvl: all(AntiSpyManager.get_items_status(lvl).values()) for lvl in LEVELS}

    @staticmethod
    @_serialized
    def get_drifted_items() -> Tuple[List[str], List[str]]:
        try:
            real, missing = AntiSpyManager._get_real_status_all()
        except Exception as e:
            logger.warning("Watchdog: checking real state failed: %s", e)
            return [], []

        machine_cache = _load_machine_items()
        user_cache = _load_user_items()
        regressed: List[str] = []
        restored: List[str] = []
        machine_dirty = False
        user_dirty = False

        for it in ITEMS:
            item_id = it["id"]
            is_user = it["kind"] == "hkcu_reg"
            cache = user_cache if is_user else machine_cache
            entry = cache.get(item_id, {})
            cached_active = bool(entry.get("active"))
            is_missing = missing.get(item_id, False)
            real_active = real.get(item_id, False) and not is_missing

            if bool(entry.get("missing")) != is_missing:
                cache[item_id] = {**entry, "missing": is_missing}
                if is_user:
                    user_dirty = True
                else:
                    machine_dirty = True

            if cached_active and not real_active:
                regressed.append(item_id)
            elif not cached_active and real_active:
                cache[item_id] = {**cache.get(item_id, entry), "active": True}
                restored.append(item_id)
                if is_user:
                    user_dirty = True
                else:
                    machine_dirty = True

        if machine_dirty:
            _save_machine_items(machine_cache)
        if user_dirty:
            _save_user_items(user_cache)

        return regressed, restored

    @staticmethod
    def is_active() -> bool:
        return AntiSpyManager.is_basic_active()

    @staticmethod
    @_serialized
    def enable_item(item_id: str, _reset: bool = True,
                     _task_state_cache: Optional[Dict[tuple, Optional[str]]] = None,
                     _svc_info_cache: Optional[Dict[str, Tuple[bool, str]]] = None) -> bool:
        if _reset:
            AntiSpyManager.last_error = ""
            AntiSpyManager.last_warnings = []

        item = _find_item(item_id)
        if not item:
            AntiSpyManager.last_error = T("antispy_err_unknown_item", id=item_id)
            return False
        if not _is_admin():
            AntiSpyManager.last_error = T("antispy_err_no_admin")
            logger.error("enable_item(%s): missing administrator privileges", item_id)
            return False

        loader, saver = _item_store(item)
        if bool(loader().get(item_id, {}).get("missing")):
            AntiSpyManager._set_flag(loader, saver, item_id, False, missing=True)
            logger.info("enable_item(%s): marked in cache as unavailable, skipped", item_id)
            return True
        try:
            kind = item["kind"]
            service_original: Optional[str] = None

            if kind == "hklm_reg":
                AntiSpyManager._set_hklm_dword(item["path"], item["name"], item["protect_value"])

            elif kind == "hkcu_reg":
                AntiSpyManager._set_hkcu_dword(item["path"], item["name"], item["protect_value"])

            elif kind == "service":
                if _svc_info_cache is not None and item["service"] in _svc_info_cache:
                    svc_exists, svc_start_type = _svc_info_cache[item["service"]]
                else:
                    svc_exists = AntiSpyManager._service_exists(item["service"])
                    svc_start_type = AntiSpyManager._get_service_start_type(item["service"]) if svc_exists else "auto"
                if not svc_exists:
                    AntiSpyManager._warn(T("antispy_warn_service_missing", service=item['service']))
                    AntiSpyManager._set_flag(loader, saver, item_id, False, missing=True)
                    logger.info("enable_item(%s): service does not exist, skipped (not an error)", item_id)
                    return True

                if svc_start_type != "disabled":
                    service_original = svc_start_type
                if not AntiSpyManager._disable_service(item["service"]):
                    AntiSpyManager._warn(T("antispy_warn_service_disable_failed", service=item['service']))

            elif kind == "firewall":
                if not AntiSpyManager._exe_exists(item["exe"]):
                    AntiSpyManager._warn(T("antispy_warn_exe_missing", exe=item['exe']))
                    AntiSpyManager._set_flag(loader, saver, item_id, False, missing=True)
                    logger.info("enable_item(%s): target file does not exist, skipped (not an error)", item_id)
                    return True
                if not AntiSpyManager._add_firewall_rule(item["rule_name"], item["exe"]):
                    AntiSpyManager.last_error = T("antispy_err_firewall_add_failed", rule=item['rule_name'])
                    logger.error("enable_item(%s): adding the firewall rule failed", item_id)
                    return False

            elif kind == "task":
                cache_key = (item["task_path"], item["task_name"])
                if _task_state_cache is not None and cache_key in _task_state_cache:
                    state = _task_state_cache[cache_key]
                else:
                    state = AntiSpyManager._get_task_state(item["task_path"], item["task_name"])
                if state == _PS_MISSING:
                    if not AntiSpyManager.last_error:
                        AntiSpyManager.last_error = T("antispy_err_ps_missing_task", task=item['task_name'])
                    logger.error("enable_item(%s): brak interpretera PowerShell", item_id)
                    return False
                if state is None:
                    AntiSpyManager._warn(T("antispy_warn_task_missing", task=item['task_name']))
                    AntiSpyManager._set_flag(loader, saver, item_id, False, missing=True)
                    logger.info("enable_item(%s): task does not exist, skipped (not an error)", item_id)
                    return True
                if state == "enabled":
                    if not AntiSpyManager._set_task_state(item["task_path"], item["task_name"], enable=False):
                        AntiSpyManager._warn(T("antispy_warn_task_disable_failed", task=item['task_name']))

            AntiSpyManager._set_flag(loader, saver, item_id, True, missing=False, original=service_original)
            logger.info("enable_item(%s) OK", item_id)
            return True
        except Exception as e:
            AntiSpyManager.last_error = str(e)
            logger.exception("enable_item(%s): unexpected error", item_id)
            return False

    @staticmethod
    @_serialized
    def disable_item(item_id: str, _reset: bool = True,
                      _svc_info_cache: Optional[Dict[str, Tuple[bool, str]]] = None,
                      _task_state_cache: Optional[Dict[tuple, Optional[str]]] = None) -> bool:
        if _reset:
            AntiSpyManager.last_error = ""
            AntiSpyManager.last_warnings = []

        item = _find_item(item_id)
        if not item:
            AntiSpyManager.last_error = T("antispy_err_unknown_item", id=item_id)
            return False
        if not _is_admin():
            AntiSpyManager.last_error = T("antispy_err_no_admin")
            logger.error("disable_item(%s): missing administrator privileges", item_id)
            return False

        loader, saver = _item_store(item)
        if bool(loader().get(item_id, {}).get("missing")):
            AntiSpyManager._set_flag(loader, saver, item_id, False, missing=True)
            logger.info("disable_item(%s): marked in cache as unavailable, skipped", item_id)
            return True
        try:
            kind = item["kind"]

            if kind == "hklm_reg":
                AntiSpyManager._delete_hklm_value(item["path"], item["name"])

            elif kind == "hkcu_reg":
                AntiSpyManager._delete_hkcu_value(item["path"], item["name"])

            elif kind == "service":
                if _svc_info_cache is not None and item["service"] in _svc_info_cache:
                    svc_exists = _svc_info_cache[item["service"]][0]
                else:
                    svc_exists = AntiSpyManager._service_exists(item["service"])
                if svc_exists:
                    restore_type = loader().get(item_id, {}).get("original") or "auto"
                    if not AntiSpyManager._restore_service(item["service"], restore_type):
                        AntiSpyManager._warn(T("antispy_warn_service_restore_failed", service=item['service']))
                else:
                    AntiSpyManager._set_flag(loader, saver, item_id, False, missing=True)

            elif kind == "firewall":
                if AntiSpyManager._exe_exists(item["exe"]):
                    AntiSpyManager._remove_firewall_rule(item["rule_name"])
                else:
                    AntiSpyManager._set_flag(loader, saver, item_id, False, missing=True)

            elif kind == "task":
                cache_key = (item["task_path"], item["task_name"])
                if _task_state_cache is not None and cache_key in _task_state_cache:
                    state = _task_state_cache[cache_key]
                else:
                    state = AntiSpyManager._get_task_state(item["task_path"], item["task_name"])
                if state is None:
                    AntiSpyManager._set_flag(loader, saver, item_id, False, missing=True)
                    logger.info("disable_item(%s): task does not exist, skipped (not an error)", item_id)
                    return True
                if state != _PS_MISSING:
                    if not AntiSpyManager._set_task_state(item["task_path"], item["task_name"], enable=True):
                        AntiSpyManager._warn(T("antispy_warn_task_restore_failed", task=item['task_name']))

            AntiSpyManager._set_flag(loader, saver, item_id, False, missing=False)
            logger.info("disable_item(%s) OK", item_id)
            return True
        except Exception as e:
            AntiSpyManager.last_error = str(e)
            logger.exception("disable_item(%s): unexpected error", item_id)
            return False

    @staticmethod
    @_serialized
    def apply_selected(level: str, selected_ids: List[str]) -> bool:
        AntiSpyManager.last_error = ""
        AntiSpyManager.last_warnings = []
        selected = set(selected_ids)
        level_items = _items_for_level(level)
        task_cache, svc_cache = AntiSpyManager._prefetch_level_caches(level_items)
        ok = True
        for item in level_items:
            if item["id"] in selected:
                if not AntiSpyManager.enable_item(item["id"], _reset=False,
                                                    _task_state_cache=task_cache,
                                                    _svc_info_cache=svc_cache):
                    ok = False
            else:
                if not AntiSpyManager.disable_item(item["id"], _reset=False,
                                                     _svc_info_cache=svc_cache,
                                                     _task_state_cache=task_cache):
                    ok = False
        return ok

    @staticmethod
    @_serialized
    def _enable_level(level: str) -> bool:
        AntiSpyManager.last_error = ""
        AntiSpyManager.last_warnings = []
        level_items = _items_for_level(level)
        task_cache, svc_cache = AntiSpyManager._prefetch_level_caches(level_items)
        ok = True
        for item in level_items:
            if not AntiSpyManager.enable_item(item["id"], _reset=False,
                                                _task_state_cache=task_cache,
                                                _svc_info_cache=svc_cache):
                ok = False
        return ok

    @staticmethod
    @_serialized
    def _disable_level(level: str) -> bool:
        AntiSpyManager.last_error = ""
        AntiSpyManager.last_warnings = []
        level_items = _items_for_level(level)
        task_cache, svc_cache = AntiSpyManager._prefetch_level_caches(level_items)
        ok = True
        for item in level_items:
            if not AntiSpyManager.disable_item(item["id"], _reset=False,
                                                 _svc_info_cache=svc_cache,
                                                 _task_state_cache=task_cache):
                ok = False
        return ok

    @staticmethod
    def _get_task_states_batch(tasks: List[Tuple[str, str]]) -> Dict[Tuple[str, str], Optional[str]]:
        if not tasks:
            return {}
        exe = _resolve_powershell_exe()
        if exe is None:
            AntiSpyManager._warn(T("antispy_err_ps_missing_tasks_batch"))
            return {key: _PS_MISSING for key in tasks}

        lines = []
        for path, name in tasks:
            safe_path = path.replace("'", "''")
            safe_name = name.replace("'", "''")
            lines.append(
                "try { "
                f"(Get-ScheduledTask -TaskPath '{safe_path}\\' -TaskName '{safe_name}' "
                "-ErrorAction Stop).State.ToString() "
                "} catch { 'MISSING' }"
            )
        ps_command = "\n".join(lines)
        try:
            result = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False, creationflags=CREATE_NO_WINDOW, timeout=60,
            )
            out_lines = result.stdout.splitlines()
        except Exception as e:
            logger.warning("_get_task_states_batch: exception: %s", e)
            AntiSpyManager._warn(T("antispy_err_ps_spawn_failed_tasks"))
            return {key: _PS_MISSING for key in tasks}

        states: Dict[Tuple[str, str], Optional[str]] = {}
        for i, key in enumerate(tasks):
            value = out_lines[i].strip() if i < len(out_lines) else ""
            if value == "Disabled":
                states[key] = "disabled"
            elif value and value != "MISSING":
                states[key] = "enabled"
            else:
                states[key] = None
        return states

    @staticmethod
    def _get_service_batch_info(names: List[str]) -> Dict[str, Tuple[bool, str]]:
        if not names:
            return {}
        exe = _resolve_powershell_exe()
        if exe is None:
            logger.warning("_get_service_batch_info: no PowerShell interpreter, assuming services exist ('auto').")
            return {n: (True, "auto") for n in names}

        filter_expr = " or ".join(f"Name='{n}'" for n in names)
        ps_command = (
            f'Get-CimInstance -ClassName Win32_Service -Filter "{filter_expr}" '
            "| Select-Object Name, StartMode | ConvertTo-Json -Compress"
        )
        parsed = None
        try:
            result = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False, creationflags=CREATE_NO_WINDOW, timeout=60,
            )
            raw = result.stdout.strip()
            if raw:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    parsed = [parsed]
        except Exception as e:
            logger.warning("_get_service_batch_info: exception: %s", e)
            parsed = None

        if parsed is None:
            return {n: (True, "auto") for n in names}

        start_types: Dict[str, str] = {}
        for entry in parsed:
            name = entry.get("Name")
            if not name:
                continue
            mode = entry.get("StartMode")
            if mode == "Manual":
                start_types[name] = "demand"
            elif mode == "Disabled":
                start_types[name] = "disabled"
            else:
                start_types[name] = "auto"

        return {n: (n in start_types, start_types.get(n, "auto")) for n in names}

    @staticmethod
    def _prefetch_level_caches(items: List[dict], need_tasks: bool = True,
                                need_services: bool = True) -> Tuple[dict, dict]:
        task_cache: dict = {}
        svc_cache: dict = {}
        if need_tasks:
            tasks = [(it["task_path"], it["task_name"]) for it in items if it["kind"] == "task"]
            if tasks:
                task_cache = AntiSpyManager._get_task_states_batch(tasks)
        if need_services:
            names = [it["service"] for it in items if it["kind"] == "service"]
            if names:
                svc_cache = AntiSpyManager._get_service_batch_info(names)
        return task_cache, svc_cache

    @staticmethod
    def enable_basic() -> bool:
        return AntiSpyManager._enable_level("basic")

    @staticmethod
    def disable_basic() -> bool:
        return AntiSpyManager._disable_level("basic")

    @staticmethod
    def enable_medium() -> bool:
        return AntiSpyManager._enable_level("medium")

    @staticmethod
    def disable_medium() -> bool:
        return AntiSpyManager._disable_level("medium")

    @staticmethod
    def enable_advanced() -> bool:
        return AntiSpyManager._enable_level("advanced")

    @staticmethod
    def disable_advanced() -> bool:
        return AntiSpyManager._disable_level("advanced")

    @staticmethod
    def enable_extra() -> bool:
        return AntiSpyManager._enable_level("extra")

    @staticmethod
    def disable_extra() -> bool:
        return AntiSpyManager._disable_level("extra")

    @staticmethod
    def _item_is_protected(item: dict,
                            _task_state_cache: Optional[Dict[tuple, Optional[str]]] = None,
                            _svc_info_cache: Optional[Dict[str, Tuple[bool, str]]] = None) -> Tuple[bool, bool]:
        kind = item["kind"]
        if kind == "hklm_reg":
            return (AntiSpyManager._get_hklm_dword(item["path"], item["name"]) == item["protect_value"], False)
        if kind == "hkcu_reg":
            return (AntiSpyManager._get_hkcu_dword(item["path"], item["name"]) == item["protect_value"], False)
        if kind == "service":
            if _svc_info_cache is not None and item["service"] in _svc_info_cache:
                exists, start_type = _svc_info_cache[item["service"]]
            else:
                exists = AntiSpyManager._service_exists(item["service"])
                start_type = AntiSpyManager._get_service_start_type(item["service"]) if exists else "auto"
            if not exists:
                return (True, True)
            return (start_type == "disabled", False)
        if kind == "firewall":
            if not AntiSpyManager._exe_exists(item["exe"]):
                return (True, True)
            return (AntiSpyManager._firewall_rule_exists(item["rule_name"]), False)
        if kind == "task":
            cache_key = (item["task_path"], item["task_name"])
            if _task_state_cache is not None and cache_key in _task_state_cache:
                state = _task_state_cache[cache_key]
            else:
                state = AntiSpyManager._get_task_state(item["task_path"], item["task_name"])
            if state == _PS_MISSING:
                return (True, False)
            if state is None:
                return (True, True)
            return (state == "disabled", False)
        return (False, False)

    @staticmethod
    def _set_flag(loader, saver, item_id: str, active: bool, missing: Optional[bool] = None,
                   original: Optional[str] = None) -> None:
        items = loader()
        entry = dict(items.get(item_id, {}))
        entry["active"] = active
        if missing is not None:
            entry["missing"] = missing
        if original is not None:
            entry["original"] = original
        items[item_id] = entry
        saver(items)

    @staticmethod
    def _get_service_start_type(service_name: str) -> str:
        exe = _resolve_powershell_exe()
        if exe is None:
            logger.warning("_get_service_start_type('%s'): no PowerShell interpreter, assuming 'auto'.", service_name)
            return "auto"
        try:
            ps_command = (
                f"(Get-CimInstance -ClassName Win32_Service "
                f"-Filter \"Name='{service_name}'\").StartMode"
            )
            result = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
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
    def _service_exists(service_name: str) -> bool:
        exe = _resolve_powershell_exe()
        if exe is None:
            logger.warning("_service_exists('%s'): no PowerShell interpreter, assuming it exists.", service_name)
            return True
        try:
            ps_command = (
                f"(Get-CimInstance -ClassName Win32_Service "
                f"-Filter \"Name='{service_name}'\") -ne $null"
            )
            result = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
            )
            return result.stdout.strip().lower() == "true"
        except Exception:
            return True

    @staticmethod
    def _disable_service(service_name: str) -> bool:
        ok = True
        r1 = subprocess.run([SC_EXE, "config", service_name, "start=", "disabled"],
                             capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                             creationflags=CREATE_NO_WINDOW, timeout=30)
        if r1.returncode != 0:
            AntiSpyManager._warn(T("antispy_warn_sc_config_failed", service=service_name, code=r1.returncode, stderr=r1.stderr.strip()))
            ok = False
        r2 = subprocess.run([NET_EXE, "stop", service_name],
                             capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                             creationflags=CREATE_NO_WINDOW, timeout=30)
        if r2.returncode not in (0, 2):
            AntiSpyManager._warn(T("antispy_warn_net_stop_failed", service=service_name, code=r2.returncode, stderr=r2.stderr.strip()))
        return ok

    @staticmethod
    def _restore_service(service_name: str, start_type: str) -> bool:
        ok = True
        r1 = subprocess.run([SC_EXE, "config", service_name, "start=", start_type],
                             capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                             creationflags=CREATE_NO_WINDOW, timeout=30)
        if r1.returncode != 0:
            AntiSpyManager._warn(T("antispy_warn_sc_config_failed", service=service_name, code=r1.returncode, stderr=r1.stderr.strip()))
            ok = False
        if start_type != "disabled":
            r2 = subprocess.run([NET_EXE, "start", service_name],
                                 capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                                 creationflags=CREATE_NO_WINDOW, timeout=30)
            if r2.returncode not in (0, 2):
                AntiSpyManager._warn(T("antispy_warn_net_start_failed", service=service_name, code=r2.returncode, stderr=r2.stderr.strip()))
        return ok

    @staticmethod
    def _add_firewall_rule(rule_name: str, exe_path: str) -> bool:
        cmd = [NETSH_EXE, "advfirewall", "firewall", "add", "rule",
               f"name={rule_name}", "dir=out", "action=block",
               f"program={exe_path}", "enable=yes"]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                           creationflags=CREATE_NO_WINDOW, timeout=30)
        if r.returncode != 0:
            AntiSpyManager._warn(T("antispy_warn_firewall_rule_failed", rule=rule_name, code=r.returncode, stderr=r.stderr.strip()))
            return False
        return True

    @staticmethod
    def _remove_firewall_rule(rule_name: str) -> None:
        cmd = [NETSH_EXE, "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                           creationflags=CREATE_NO_WINDOW, timeout=30)
        if r.returncode != 0:
            logger.debug("netsh delete rule %s: kod %s (%s)", rule_name, r.returncode, r.stderr.strip())

    @staticmethod
    def _firewall_rule_exists(rule_name: str) -> bool:
        try:
            r = subprocess.run(
                [NETSH_EXE, "advfirewall", "firewall", "show", "rule", f"name={rule_name}"],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
            )
            return r.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _exe_exists(exe_path: str) -> bool:
        try:
            return os.path.isfile(os.path.expandvars(exe_path))
        except Exception:
            return True

    @staticmethod
    def _get_task_state(task_path: str, task_name: str) -> Optional[str]:
        exe = _resolve_powershell_exe()
        if exe is None:
            AntiSpyManager._warn(T("antispy_err_ps_missing_task_check", task=task_name))
            return _PS_MISSING
        try:
            ps_command = (
                f"(Get-ScheduledTask -TaskPath '{task_path}\\' -TaskName '{task_name}' "
                f"-ErrorAction Stop).State.ToString()"
            )
            result = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
            )
            value = result.stdout.strip()
            if value == "Disabled":
                return "disabled"
            if value:
                return "enabled"
            logger.warning(
                "_get_task_state('%s', '%s'): puste stdout, kod %s, stderr: %s",
                task_path, task_name, result.returncode, result.stderr.strip()
            )
        except Exception as e:
            logger.warning("_get_task_state('%s', '%s'): exception: %s", task_path, task_name, e)
        return None

    @staticmethod
    def _set_task_state(task_path: str, task_name: str, enable: bool) -> bool:
        exe = _resolve_powershell_exe()
        if exe is None:
            AntiSpyManager._warn(T("antispy_err_ps_missing_task_set", task=task_name))
            return False
        verb = "Enable-ScheduledTask" if enable else "Disable-ScheduledTask"
        ps_command = f"{verb} -TaskPath '{task_path}\\' -TaskName '{task_name}' -ErrorAction Stop"
        try:
            result = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
            )
            return result.returncode == 0
        except Exception as e:
            AntiSpyManager._warn(T("antispy_warn_task_set_exception", verb=verb, task=task_name, error=e))
            return False

    @staticmethod
    def _get_hklm_dword(subkey: str, name: str) -> Optional[int]:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return int(value)
        except Exception:
            return None

    @staticmethod
    def _set_hklm_dword(subkey: str, name: str, value: int) -> None:
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
        winreg.CloseKey(key)

    @staticmethod
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

    @staticmethod
    def _get_hkcu_dword(subkey: str, name: str) -> Optional[int]:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return int(value)
        except Exception:
            return None

    @staticmethod
    def _set_hkcu_dword(subkey: str, name: str, value: int) -> None:
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
        winreg.CloseKey(key)

    @staticmethod
    def _delete_hkcu_value(subkey: str, name: str) -> None:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, name)
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass

    @staticmethod
    def _warn(msg: str) -> None:
        AntiSpyManager.last_warnings.append(msg)
        logger.warning(msg)

class HostsLockError(Exception):
    pass

class HostsLockManager:

    last_error: str = ""
    _op_lock = threading.RLock()

    @staticmethod
    def _load_state() -> dict:
        return _load_json(HOSTS_LOCK_STATE_FILE) or {"active": False}

    @staticmethod
    def _save_state(active: bool) -> None:
        _atomic_write_json(HOSTS_LOCK_STATE_FILE, {"active": active})

    @staticmethod
    def is_active() -> bool:
        return bool(HostsLockManager._load_state().get("active"))

    @staticmethod
    def _real_locked(hosts_path: str = HOSTS_PATH) -> Optional[bool]:
        exe = _resolve_powershell_exe()
        if exe is None:
            logger.warning("HostsLockManager._real_locked: no PowerShell interpreter available")
            return None
        safe_path = hosts_path.replace("'", "''")
        ps_command = (
            f"$sid = New-Object System.Security.Principal.SecurityIdentifier('{HOSTS_LOCK_SID}'); "
            f"$acl = Get-Acl -LiteralPath '{safe_path}'; "
            "$found = $acl.Access | Where-Object { "
            "$_.AccessControlType -eq 'Deny' -and "
            "$_.FileSystemRights.ToString() -match 'Write' -and "
            "($_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value -eq $sid.Value) "
            "}; "
            "if ($found) { 'LOCKED' } else { 'UNLOCKED' }"
        )
        try:
            result = subprocess.run(
                [exe, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True, text=True, encoding=_console_encoding(), errors="replace", check=False,
                creationflags=CREATE_NO_WINDOW, timeout=30,
            )
            out = result.stdout.strip()
            if out == "LOCKED":
                return True
            if out == "UNLOCKED":
                return False
            logger.warning("HostsLockManager._real_locked: unexpected output %r (stderr: %s)",
                            out, result.stderr.strip())
            return None
        except Exception as e:
            logger.warning("HostsLockManager._real_locked: exception: %s", e)
            return None

    @staticmethod
    def enable(hosts_path: str = HOSTS_PATH) -> bool:
        with HostsLockManager._op_lock:
            HostsLockManager.last_error = ""
            if not _is_admin():
                HostsLockManager.last_error = T("antispy_err_no_admin")
                return False
            if not os.path.exists(hosts_path):
                HostsLockManager.last_error = T("hosts_lock_err_no_file")
                return False
            exe = _resolve_powershell_exe()
            if exe is None:
                HostsLockManager.last_error = T("antispy_err_no_admin")
                logger.error("HostsLockManager.enable: brak interpretera PowerShell")
                return False
            safe_path = hosts_path.replace("'", "''")

            ps_command = (
                f"$acl = Get-Acl -LiteralPath '{safe_path}'; "
                f"$sid = New-Object System.Security.Principal.SecurityIdentifier('{HOSTS_LOCK_SID}'); "
                "$rights = [System.Security.AccessControl.FileSystemRights]::Write -bor "
                "[System.Security.AccessControl.FileSystemRights]::Delete; "
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
                    HostsLockManager.last_error = r.stderr.strip() or r.stdout.strip()
                    logger.error("HostsLockManager.enable: PowerShell failed (code %s): %s",
                                 r.returncode, HostsLockManager.last_error)
                    return False
                HostsLockManager._save_state(True)
                logger.info("HostsLockManager.enable: OK")
                return True
            except Exception as e:
                HostsLockManager.last_error = str(e)
                logger.exception("HostsLockManager.enable: unexpected error")
                return False

    @staticmethod
    def disable(hosts_path: str = HOSTS_PATH) -> bool:
        with HostsLockManager._op_lock:
            HostsLockManager.last_error = ""
            if not _is_admin():
                HostsLockManager.last_error = T("antispy_err_no_admin")
                return False
            exe = _resolve_powershell_exe()
            if exe is None:
                HostsLockManager.last_error = T("antispy_err_no_admin")
                logger.error("HostsLockManager.disable: brak interpretera PowerShell")
                return False
            safe_path = hosts_path.replace("'", "''")
            ps_command = (
                f"$acl = Get-Acl -LiteralPath '{safe_path}'; "
                f"$sid = New-Object System.Security.Principal.SecurityIdentifier('{HOSTS_LOCK_SID}'); "
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
                    HostsLockManager.last_error = r.stderr.strip() or r.stdout.strip()
                    logger.error("HostsLockManager.disable: PowerShell failed (code %s): %s",
                                 r.returncode, HostsLockManager.last_error)
                    return False
                HostsLockManager._save_state(False)
                logger.info("HostsLockManager.disable: OK")
                return True
            except Exception as e:
                HostsLockManager.last_error = str(e)
                logger.exception("HostsLockManager.disable: unexpected error")
                return False

    @staticmethod
    def check_drift(hosts_path: str = HOSTS_PATH) -> Optional[str]:
        cached = HostsLockManager.is_active()
        real = HostsLockManager._real_locked(hosts_path)
        if real is None:
            return None
        if cached and not real:
            HostsLockManager._save_state(False)
            return "regressed"
        if not cached and real:
            HostsLockManager._save_state(True)
            return "restored"
        return None

def run_startup_seed() -> None:
    _ensure_seeded()
