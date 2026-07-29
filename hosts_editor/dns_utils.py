import ctypes
import ctypes.wintypes as wintypes
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

from .core_antispy import CREATE_NO_WINDOW, _console_encoding

CF_FAMILY_PRIMARY   = "1.1.1.3"
CF_FAMILY_SECONDARY = "1.0.0.3"

_BACKUP_PATH = os.path.join(os.environ.get("APPDATA", ""), "HOTS Hosts", "dns_backup.json")

_AF_UNSPEC = 0
_GAA_FLAG_SKIP_ANYCAST      = 0x0002
_GAA_FLAG_SKIP_MULTICAST    = 0x0004
_GAA_FLAG_SKIP_DNS_SERVER   = 0x0008
_ERROR_BUFFER_OVERFLOW = 111
_ERROR_SUCCESS = 0
_IF_OPER_STATUS_UP = 1


class _IP_ADAPTER_ADDRESSES(ctypes.Structure):
    pass


_IP_ADAPTER_ADDRESSES._fields_ = [
    ("Length", wintypes.ULONG),
    ("IfIndex", wintypes.DWORD),
    ("Next", ctypes.POINTER(_IP_ADAPTER_ADDRESSES)),
    ("AdapterName", ctypes.c_char_p),
    ("FirstUnicastAddress", ctypes.c_void_p),
    ("FirstAnycastAddress", ctypes.c_void_p),
    ("FirstMulticastAddress", ctypes.c_void_p),
    ("FirstDnsServerAddress", ctypes.c_void_p),
    ("DnsSuffix", ctypes.c_wchar_p),
    ("Description", ctypes.c_wchar_p),
    ("FriendlyName", ctypes.c_wchar_p),
    ("PhysicalAddress", ctypes.c_ubyte * 8),
    ("PhysicalAddressLength", wintypes.DWORD),
    ("Flags", wintypes.DWORD),
    ("Mtu", wintypes.DWORD),
    ("IfType", wintypes.DWORD),
    ("OperStatus", ctypes.c_uint),
]

try:
    _GetAdaptersAddresses = ctypes.windll.iphlpapi.GetAdaptersAddresses
    _GetAdaptersAddresses.argtypes = [
        wintypes.ULONG, wintypes.ULONG, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.POINTER(wintypes.ULONG),
    ]
    _GetAdaptersAddresses.restype = wintypes.ULONG
except (AttributeError, OSError):
    _GetAdaptersAddresses = None

def get_active_interfaces() -> list[str]:
    if _GetAdaptersAddresses is None:
        return []

    try:
        size = wintypes.ULONG(15000)
        buf = ctypes.create_string_buffer(size.value)
        flags = _GAA_FLAG_SKIP_ANYCAST | _GAA_FLAG_SKIP_MULTICAST | _GAA_FLAG_SKIP_DNS_SERVER

        ret = _GetAdaptersAddresses(_AF_UNSPEC, flags, None,
                                     ctypes.cast(buf, ctypes.c_void_p),
                                     ctypes.byref(size))
        if ret == _ERROR_BUFFER_OVERFLOW:
            buf = ctypes.create_string_buffer(size.value)
            ret = _GetAdaptersAddresses(_AF_UNSPEC, flags, None,
                                         ctypes.cast(buf, ctypes.c_void_p),
                                         ctypes.byref(size))
        if ret != _ERROR_SUCCESS:
            return []

        interfaces = []
        p = ctypes.cast(buf, ctypes.POINTER(_IP_ADAPTER_ADDRESSES))
        while p:
            adapter = p[0]
            if adapter.OperStatus == _IF_OPER_STATUS_UP and adapter.FriendlyName:
                interfaces.append(adapter.FriendlyName)
            p = adapter.Next
        return interfaces
    except Exception:
        return []


def get_dns_for_interface(iface: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["netsh", "interface", "ip", "show", "dns", f"name={iface}"],
            text=True, encoding=_console_encoding(), errors="replace",
            creationflags=CREATE_NO_WINDOW
        )
    except Exception:
        return []

    servers = []
    for line in out.splitlines():
        m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", line)
        if m:
            ip = m.group(1)
            if not ip.startswith("127."):
                servers.append(ip)
    return servers


def set_dns_for_interface(iface: str, servers: list[str]) -> bool:
    try:
        if not servers:
            subprocess.check_call(
                ["netsh", "interface", "ip", "set", "dns",
                 f"name={iface}", "source=dhcp"],
                creationflags=CREATE_NO_WINDOW
            )
        else:
            subprocess.check_call(
                ["netsh", "interface", "ip", "set", "dns",
                 f"name={iface}", "static", servers[0], "primary"],
                creationflags=CREATE_NO_WINDOW
            )
            for idx, srv in enumerate(servers[1:], start=2):
                subprocess.check_call(
                    ["netsh", "interface", "ip", "add", "dns",
                     f"name={iface}", srv, f"index={idx}"],
                    creationflags=CREATE_NO_WINDOW
                )
        return True
    except Exception:
        return False


def _parallel_get_dns(interfaces: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    if not interfaces:
        return result
    with ThreadPoolExecutor(max_workers=len(interfaces)) as executor:
        future_to_iface = {
            executor.submit(get_dns_for_interface, iface): iface for iface in interfaces
        }
        for future, iface in future_to_iface.items():
            try:
                result[iface] = future.result()
            except Exception:
                result[iface] = []
    return result


def _parallel_set_dns(iface_servers: dict[str, list[str]]) -> list[str]:
    failed: list[str] = []
    if not iface_servers:
        return failed
    with ThreadPoolExecutor(max_workers=len(iface_servers)) as executor:
        future_to_iface = {
            executor.submit(set_dns_for_interface, iface, servers): iface
            for iface, servers in iface_servers.items()
        }
        for future, iface in future_to_iface.items():
            try:
                ok = future.result()
            except Exception:
                ok = False
            if not ok:
                failed.append(iface)
    return failed


def _save_dns_backup(backup: dict) -> None:
    os.makedirs(os.path.dirname(_BACKUP_PATH), exist_ok=True)
    with open(_BACKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)


def _load_dns_backup() -> dict | None:
    if not os.path.exists(_BACKUP_PATH):
        return None
    try:
        with open(_BACKUP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _delete_dns_backup() -> None:
    try:
        if os.path.exists(_BACKUP_PATH):
            os.remove(_BACKUP_PATH)
    except Exception:
        pass


def is_cf_family_active() -> bool:
    interfaces = get_active_interfaces()
    if not interfaces:
        return os.path.exists(_BACKUP_PATH)
    dns_map = _parallel_get_dns(interfaces)
    for dns in dns_map.values():
        if CF_FAMILY_PRIMARY in dns or CF_FAMILY_SECONDARY in dns:
            return True
    return False


def enable_cf_family_dns() -> tuple[bool, list[str]]:
    interfaces = get_active_interfaces()
    if not interfaces:
        return False, []

    current_dns = _parallel_get_dns(interfaces)
    old_backup = _load_dns_backup()

    backup = {}
    for iface in interfaces:
        current = current_dns.get(iface, [])
        if CF_FAMILY_PRIMARY in current or CF_FAMILY_SECONDARY in current:
            backup[iface] = old_backup.get(iface, []) if old_backup else []
        else:
            backup[iface] = current
    _save_dns_backup(backup)

    iface_servers = {iface: [CF_FAMILY_PRIMARY, CF_FAMILY_SECONDARY] for iface in interfaces}
    failed = _parallel_set_dns(iface_servers)

    return len(failed) < len(interfaces), failed


def disable_cf_family_dns() -> tuple[bool, list[str]]:
    backup = _load_dns_backup()

    if backup is None:
        interfaces = get_active_interfaces()
        iface_servers = {iface: [] for iface in interfaces}
        failed = _parallel_set_dns(iface_servers)
        return len(failed) < len(interfaces), failed

    failed = _parallel_set_dns(backup)

    if not failed:
        _delete_dns_backup()

    return len(failed) < len(backup), failed
