"""
Utilities for managing DNS servers on active network interfaces.
Used by the Parental Control module to enable Cloudflare Family DNS.

Cloudflare Family: 1.1.1.3 / 1.0.0.3  (blocks adult content at DNS level)
"""

import json
import os
import re
import subprocess

# ── Constants ─────────────────────────────────────────────────────────────────

CF_FAMILY_PRIMARY   = "1.1.1.3"
CF_FAMILY_SECONDARY = "1.0.0.3"

# File for storing original DNS settings before switching
_BACKUP_PATH = os.path.join(os.environ.get("APPDATA", ""), "HOTS", "dns_backup.json")

# Flags to suppress the console window on Windows
_NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0x08000000


# ── Interfaces ────────────────────────────────────────────────────────────────

def get_active_interfaces() -> list[str]:
    """Returns a list of active (Connected) network interface names."""
    try:
        out = subprocess.check_output(
            ["netsh", "interface", "show", "interface"],
            text=True, encoding="cp852", errors="replace",
            creationflags=_NO_WINDOW
        )
    except Exception:
        return []

    interfaces = []
    for line in out.splitlines():
        # Match lines with "Connected" (EN) or Polish equivalents (PL)
        if "Connected" in line or "Połączony" in line or "Podłączony" in line:
            # Format: "Enabled    Connected    ...    Interface Name"
            # Name is the last field (may contain spaces)
            parts = line.split()
            if len(parts) >= 4:
                # Interface name = everything after the 3rd column
                name = " ".join(parts[3:])
                interfaces.append(name)
    return interfaces


def get_dns_for_interface(iface: str) -> list[str]:
    """
    Returns the list of DNS servers for the given interface.
    Empty list means DHCP / no static DNS configured.
    """
    try:
        out = subprocess.check_output(
            ["netsh", "interface", "ip", "show", "dns", f"name={iface}"],
            text=True, encoding="cp852", errors="replace",
            creationflags=_NO_WINDOW
        )
    except Exception:
        return []

    servers = []
    for line in out.splitlines():
        m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", line)
        if m:
            ip = m.group(1)
            if not ip.startswith("127."):  # skip loopback addresses
                servers.append(ip)
    return servers


def set_dns_for_interface(iface: str, servers: list[str]) -> bool:
    """
    Sets static DNS servers for the given interface.
    If servers is empty — restores DHCP.
    Returns True on success.
    """
    try:
        if not servers:
            # Restore DHCP
            subprocess.check_call(
                ["netsh", "interface", "ip", "set", "dns",
                 f"name={iface}", "source=dhcp"],
                creationflags=_NO_WINDOW
            )
        else:
            # Set primary
            subprocess.check_call(
                ["netsh", "interface", "ip", "set", "dns",
                 f"name={iface}", "static", servers[0], "primary"],
                creationflags=_NO_WINDOW
            )
            # Add secondary (and any further servers)
            for idx, srv in enumerate(servers[1:], start=2):
                subprocess.check_call(
                    ["netsh", "interface", "ip", "add", "dns",
                     f"name={iface}", srv, f"index={idx}"],
                    creationflags=_NO_WINDOW
                )
        return True
    except Exception:
        return False


# ── DNS backup ────────────────────────────────────────────────────────────────

def _save_dns_backup(backup: dict) -> None:
    """Saves a {iface: [dns, ...]} dict to a JSON file."""
    os.makedirs(os.path.dirname(_BACKUP_PATH), exist_ok=True)
    with open(_BACKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)


def _load_dns_backup() -> dict | None:
    """Loads the DNS backup. Returns None if the file does not exist."""
    if not os.path.exists(_BACKUP_PATH):
        return None
    try:
        with open(_BACKUP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _delete_dns_backup() -> None:
    """Deletes the backup file after DNS has been restored."""
    try:
        if os.path.exists(_BACKUP_PATH):
            os.remove(_BACKUP_PATH)
    except Exception:
        pass


# ── Public API ────────────────────────────────────────────────────────────────

def is_cf_family_active() -> bool:
    """
    Returns True if the backup file exists (= Cloudflare Family DNS is enabled).
    State persists across HOTS sessions.
    """
    return os.path.exists(_BACKUP_PATH)


def enable_cf_family_dns() -> tuple[bool, list[str]]:
    """
    Enables Cloudflare Family DNS on all active interfaces.
    Saves original DNS servers to backup before switching.

    Returns (success: bool, failed_interfaces: list[str]).
    """
    interfaces = get_active_interfaces()
    if not interfaces:
        return False, []

    # Save original DNS settings
    backup = {}
    for iface in interfaces:
        backup[iface] = get_dns_for_interface(iface)
    _save_dns_backup(backup)

    # Switch to Cloudflare Family
    failed = []
    for iface in interfaces:
        ok = set_dns_for_interface(iface, [CF_FAMILY_PRIMARY, CF_FAMILY_SECONDARY])
        if not ok:
            failed.append(iface)

    return len(failed) < len(interfaces), failed


def disable_cf_family_dns() -> tuple[bool, list[str]]:
    """
    Restores original DNS servers from backup.
    If no backup exists — restores DHCP on all active interfaces.

    Returns (success: bool, failed_interfaces: list[str]).
    """
    backup = _load_dns_backup()

    if backup is None:
        # No backup — restore DHCP on active interfaces
        interfaces = get_active_interfaces()
        failed = []
        for iface in interfaces:
            ok = set_dns_for_interface(iface, [])
            if not ok:
                failed.append(iface)
        return len(failed) < len(interfaces), failed

    failed = []
    for iface, servers in backup.items():
        ok = set_dns_for_interface(iface, servers)
        if not ok:
            failed.append(iface)

    if not failed:
        _delete_dns_backup()

    return len(failed) == 0, failed
