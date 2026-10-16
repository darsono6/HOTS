import ctypes
import ctypes.wintypes as wintypes
import ipaddress
import json
import os
import re
import subprocess
try:
    import winreg
except ImportError:
    winreg = None
from concurrent.futures import ThreadPoolExecutor

from .core_antispy import CREATE_NO_WINDOW, _console_encoding, NETSH_EXE
from .secure_storage import PROGRAMDATA_DIR, atomic_write_json

CF_FAMILY_PRIMARY   = "1.1.1.3"
CF_FAMILY_SECONDARY = "1.0.0.3"

_BACKUP_PATH = os.path.join(PROGRAMDATA_DIR, "dns_backup.json")
_LEGACY_BACKUP_PATH = os.path.join(os.environ.get("APPDATA", ""), "HOTS Hosts", "dns_backup.json")

_AF_UNSPEC = 0
_GAA_FLAG_SKIP_ANYCAST      = 0x0002
_GAA_FLAG_SKIP_MULTICAST    = 0x0004
_GAA_FLAG_SKIP_DNS_SERVER   = 0x0008
_ERROR_BUFFER_OVERFLOW = 111
_ERROR_SUCCESS = 0
_IF_OPER_STATUS_UP = 1
_IF_TYPE_LOOPBACK = 24
_IF_TYPE_TUNNEL = 131
_SKIP_IF_TYPES = (_IF_TYPE_LOOPBACK, _IF_TYPE_TUNNEL)

_iface_guid: dict[str, str] = {}
_TCPIP_IFACES_KEY = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"


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
            if (adapter.OperStatus == _IF_OPER_STATUS_UP and adapter.FriendlyName
                    and adapter.IfType not in _SKIP_IF_TYPES):
                interfaces.append(adapter.FriendlyName)
                if adapter.AdapterName:
                    try:
                        _iface_guid[adapter.FriendlyName] = adapter.AdapterName.decode("ascii")
                    except Exception:
                        pass
            p = adapter.Next
        return interfaces
    except Exception:
        return []


def _is_dhcp_dns(iface: str) -> bool:
    guid = _iface_guid.get(iface)
    if winreg is None or not guid:
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            _TCPIP_IFACES_KEY + "\\" + guid)
    except OSError:
        return False
    try:
        with key:
            try:
                value, _ = winreg.QueryValueEx(key, "NameServer")
            except FileNotFoundError:
                return True
            return not str(value).strip()
    except OSError:
        return False


def _read_dns_servers(iface: str) -> list[str]:
    try:
        out = subprocess.check_output(
            [NETSH_EXE, "interface", "ip", "show", "dns", f"name={iface}"],
            text=True, encoding=_console_encoding(), errors="replace",
            creationflags=CREATE_NO_WINDOW, stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
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


def get_dns_for_interface(iface: str) -> list[str]:
    """Statically configured servers only (for backup); an empty list means DHCP."""
    if _is_dhcp_dns(iface):
        return []
    return _read_dns_servers(iface)


def get_dns_info(iface: str) -> tuple[bool, list[str]]:
    return _is_dhcp_dns(iface), _read_dns_servers(iface)


def set_dns_for_interface(iface: str, servers: list[str]) -> bool:
    try:
        if not servers:
            subprocess.check_call(
                [NETSH_EXE, "interface", "ip", "set", "dns",
                 f"name={iface}", "source=dhcp"],
                creationflags=CREATE_NO_WINDOW, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        else:
            subprocess.check_call(
                [NETSH_EXE, "interface", "ip", "set", "dns",
                 f"name={iface}", "static", servers[0], "primary"],
                creationflags=CREATE_NO_WINDOW, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            for idx, srv in enumerate(servers[1:], start=2):
                subprocess.check_call(
                    [NETSH_EXE, "interface", "ip", "add", "dns",
                     f"name={iface}", srv, f"index={idx}"],
                    creationflags=CREATE_NO_WINDOW, stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
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
    atomic_write_json(_BACKUP_PATH, backup)


def _clean_dns_backup(raw) -> dict | None:
    # The backup is replayed as administrator, so only well-formed {interface: [IP addresses]} is accepted.
    if not isinstance(raw, dict):
        return None
    out = {}
    for iface, servers in raw.items():
        if (not isinstance(iface, str) or not iface or len(iface) > 256
                or any(ord(c) < 32 for c in iface) or not isinstance(servers, list)):
            continue
        try:
            out[iface] = [str(ipaddress.ip_address(s)) for s in servers]
        except (ValueError, TypeError):
            continue
    return out or None


def _load_dns_backup() -> dict | None:
    # Older versions kept the backup in the user's profile; it is validated and moved once.
    if os.path.exists(_BACKUP_PATH):
        try:
            with open(_BACKUP_PATH, "r", encoding="utf-8") as f:
                return _clean_dns_backup(json.load(f))
        except Exception:
            return None
    if not os.path.exists(_LEGACY_BACKUP_PATH):
        return None
    try:
        with open(_LEGACY_BACKUP_PATH, "r", encoding="utf-8") as f:
            data = _clean_dns_backup(json.load(f))
    except Exception:
        return None
    if data:
        try:
            _save_dns_backup(data)
            os.remove(_LEGACY_BACKUP_PATH)
        except Exception:
            pass
    return data


def _delete_dns_backup() -> None:
    for path in (_BACKUP_PATH, _LEGACY_BACKUP_PATH):
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


def _parallel_dns_info(interfaces: list[str]) -> dict[str, tuple[bool, list[str]]]:
    result: dict[str, tuple[bool, list[str]]] = {}
    if not interfaces:
        return result
    with ThreadPoolExecutor(max_workers=len(interfaces)) as executor:
        futures = {iface: executor.submit(get_dns_info, iface) for iface in interfaces}
        for iface, future in futures.items():
            try:
                result[iface] = future.result()
            except Exception:
                result[iface] = (False, [])
    return result


def get_cf_status() -> tuple[bool, dict[str, tuple[bool, list[str]]]]:
    """Single read pass: (filter active, {adapter: (from_dhcp, servers)})."""
    interfaces = get_active_interfaces()
    if not interfaces:
        return os.path.exists(_BACKUP_PATH) or os.path.exists(_LEGACY_BACKUP_PATH), {}
    info = _parallel_dns_info(interfaces)
    active = any(CF_FAMILY_PRIMARY in servers or CF_FAMILY_SECONDARY in servers
                 for _dhcp, servers in info.values())
    return active, info


def is_cf_family_active() -> bool:
    return get_cf_status()[0]


def format_dns_status(info: dict[str, tuple[bool, list[str]]]) -> str:
    if not info:
        return "\u2014"
    parts = []
    for iface, (dhcp, servers) in info.items():
        addrs = ", ".join(servers)
        if dhcp:
            text = f"DHCP ({addrs})" if addrs else "DHCP"
        else:
            text = addrs or "\u2014"
        parts.append(f"{iface}: {text}")
    return " \u00b7 ".join(parts)


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
    else:
        _save_dns_backup({iface: backup[iface] for iface in failed if iface in backup})

    return len(failed) < len(backup), failed
