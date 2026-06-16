"""
Data logic: hosts file parsing and writing, import/export, DNS.
This module does NOT import tkinter — no UI code.
"""

import os
import re
import csv
import shutil
import socket
import fnmatch
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

from .constants import HOSTS_PATH
from .i18n import T


# ── IP validation ───────────────────────────────────────────────────────────
def is_valid_ip(ip: str) -> bool:
    """
    Returns True if the given string is a valid IPv4 or IPv6 address.
    Also handles IPv6 loopback (::1).
    """
    ip = ip.strip()
    if not ip:
        return False
    # Strip IPv6 zone-id if present (e.g. fe80::1%lo0)
    ip_clean = ip.split('%')[0]
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(family, ip_clean)
            return True
        except (socket.error, OSError):
            pass
    return False


# ── Parsing ─────────────────────────────────────────────────────────────────
def _looks_like_entry(text: str) -> bool:
    """
    Returns True if the text (already stripped of leading '#' and whitespace)
    looks like a hosts entry — starts with an IPv4 or IPv6 address.
    """
    parts = text.split()
    if len(parts) < 2:
        return False
    candidate = parts[0].split('%')[0]   # strip IPv6 zone-id
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(family, candidate)
            return True
        except (OSError, socket.error):
            pass
    return False


def parse_hosts(path) -> list:
    """
    Parses the hosts file preserving the COMPLETE structure and line order.
    Returns a list of dicts. Pure comment lines have enabled=None.
    """
    entries = []
    if not os.path.exists(path):
        return entries

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return entries

    for line in lines:
        raw_line = line.rstrip("\r\n")
        stripped = raw_line.strip()

        if not stripped:
            entries.append({"enabled": None, "ip": "", "hostname": "", "comment": "", "raw": raw_line})
            continue

        if stripped.startswith("#"):
            content = stripped[1:].strip()
            if _looks_like_entry(content):
                # Disabled entry (starts with #, but followed by IP and hostname)
                parts = content.split(None, 1)
                ip = parts[0]
                rest = parts[1]
                
                # Extract inline comment from the disabled line
                comment = ""
                if "#" in rest:
                    host_part, comment_part = rest.split("#", 1)
                    hostname = host_part.strip()
                    comment = comment_part.strip()
                else:
                    hostname = rest.strip()

                entries.append({
                    "enabled": False,
                    "ip": ip,
                    "hostname": hostname,
                    "comment": comment,
                    "raw": raw_line
                })
            else:
                # Plain text comment or section header
                entries.append({"enabled": None, "ip": "", "hostname": "", "comment": "", "raw": raw_line})
        else:
            # Active entry
            parts = stripped.split(None, 1)
            ip = parts[0]
            rest = parts[1]

            comment = ""
            if "#" in rest:
                host_part, comment_part = rest.split("#", 1)
                hostname = host_part.strip()
                comment = comment_part.strip()
            else:
                hostname = rest.strip()

            entries.append({
                "enabled": True,
                "ip": ip,
                "hostname": hostname,
                "comment": comment,
                "raw": raw_line
            })

    return entries


def entries_to_text(entries: list, include_comments: bool = True) -> str:
    """Converts the list of entry dicts back to raw hosts file text."""
    lines = []
    for e in entries:
        if e["enabled"] is None:
            lines.append(e.get("raw", ""))
        else:
            prefix = "" if e["enabled"] else "# "
            line = f"{prefix}{e['ip']}\t{e['hostname']}"
            if include_comments and e.get("comment"):
                line += f" # {e['comment']}"
            lines.append(line)
    return "\n".join(lines) + "\n"


# ── Write & flush ───────────────────────────────────────────────────────────
def save_hosts(path, entries: list) -> bool:
    """
    Writes the given list of entries to the hosts file.
    Creates an automatic .bak backup before writing.
    Returns True if the DNS flush succeeded.
    """
    if os.path.exists(path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_path = f"{path}.bak_{ts}"
        try:
            shutil.copy2(path, bak_path)
        except Exception as ex:
            raise RuntimeError(T("save_backup_err", ex=ex))

    text_content = entries_to_text(entries)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text_content)
    except PermissionError:
        raise PermissionError(T("save_perm_err"))
    except Exception as ex:
        raise RuntimeError(T("save_write_err", ex=ex))

    # Backup rotation — keep at most 10 most recent backups
    try:
        existing = list_backups(path)
        for old_bak, _ in existing[10:]:
            try:
                old_bak.unlink()
            except Exception:
                pass
    except Exception:
        pass

    # Flush DNS cache on Windows
    import subprocess
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0  # SW_HIDE
        res = subprocess.run(["ipconfig", "/flushdns"], startupinfo=si, capture_output=True, text=True)
        return res.returncode == 0
    except Exception:
        return False


# ── Backup management ───────────────────────────────────────────────────────
def list_backups(hosts_path) -> list:
    """
    Returns a list of existing automatic backups for the given hosts file.
    Format: list of (Path, datetime) tuples sorted newest-first.
    """
    if not hosts_path:
        return []

    parent_dir = Path(hosts_path).parent
    base_name = Path(hosts_path).name

    if not parent_dir.exists():
        return []

    # Strict pattern: hosts.bak_YYYYMMDD_HHMMSS — only backups created by this app
    bak_re = re.compile(
        r"^" + re.escape(base_name) + r"\.bak_(\d{8})_(\d{6})$"
    )

    backups = []
    try:
        for p in parent_dir.glob(f"{base_name}.bak_*"):
            if not p.is_file():
                continue
            m = bak_re.match(p.name)
            if not m:
                # Not our format (e.g. .bak_old, .bak_v1, manually copied) — skip
                continue
            d_str, t_str = m.groups()
            try:
                dt = datetime.strptime(f"{d_str}_{t_str}", "%Y%m%d_%H%M%S")
            except ValueError:
                continue   # invalid date — not our backup
            backups.append((p, dt))
    except Exception:
        return []

    # Sort newest to oldest
    backups.sort(key=lambda x: x[1], reverse=True)
    return backups


# ── Import / export ─────────────────────────────────────────────────────────
def import_hosts_file(parent_widget, current_entries):
    """
    Opens a file picker and imports raw entries one-to-one.
    Does not modify IPs or remove duplicates on the fly.
    """
    from .widgets import DarkDialog  # local import to avoid circular dependency

    path = filedialog.askopenfilename(
        parent=parent_widget,
        title=T("import_dialog_title"),
        filetypes=[(T("import_filetypes_hosts"), "*.txt *.hosts *"),
                   (T("import_filetypes_all"),   "*.*")],
    )
    if not path:
        return None

    imported = parse_hosts(path)
    new_entries = [e for e in imported if e["enabled"] is not None]

    if not new_entries:
        DarkDialog.info(parent_widget, T("import_empty_title"), T("import_empty_msg"))
        return None

    if not DarkDialog.ask(parent_widget, T("import_confirm_title"),
                          T("import_confirm_msg", n=len(new_entries))):
        return None

    fname = Path(path).name
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M")

    result = list(current_entries)
    result.append({"enabled": None, "ip": "", "hostname": "", "comment": "",
                   "raw": f"\n{T('import_header_comment', path=fname, ts=ts)}"})
    result.extend(new_entries)
    return result


def export_hosts(parent_widget, entries: list, include_comments: bool = True):
    """Exports the current table entries to an external file as CSV or TXT."""
    from .widgets import DarkDialog
    path = filedialog.asksaveasfilename(
        parent=parent_widget,
        title=T("export_dialog_title"),
        defaultextension=".txt",
        filetypes=[(T("export_filetypes_txt"), "*.txt"),
                   (T("export_filetypes_csv"), "*.csv"),
                   (T("export_filetypes_all"), "*.*")]
    )
    if not path:
        return

    real = [e for e in entries if e["enabled"] is not None]
    if path.endswith(".csv"):
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                headers = T("export_csv_headers").split(",")
                if not include_comments:
                    headers = [h for h in headers if h.lower() not in ("comment", "komentarz", "commentaire")]
                writer.writerow(headers)
                for e in real:
                    status = "active" if e["enabled"] else "disabled"
                    if include_comments:
                        writer.writerow([status, e["ip"], e["hostname"], e["comment"]])
                    else:
                        writer.writerow([status, e["ip"], e["hostname"]])
            DarkDialog.info(parent_widget, T("export_ok_csv_title"), T("export_ok_csv_msg", path=path))
        except Exception as ex:
            DarkDialog.error(parent_widget, T("export_err_title"), str(ex))
    else:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(entries_to_text(entries, include_comments=include_comments))
            DarkDialog.info(parent_widget, T("export_ok_txt_title"), T("export_ok_txt_msg", n=len(real), path=path))
        except Exception as ex:
            DarkDialog.error(parent_widget, T("export_err_title"), str(ex))


# ── External DNS resolver (bypasses hosts file) ─────────────────────────────
def dns_lookup_external(hostname, dns_ip="8.8.8.8", port=53, timeout=4):
    """
    Sends a raw UDP DNS A-query directly to an external server (default 8.8.8.8),
    bypassing the hosts file and the system resolver.
    """
    import struct as _st
    import random as _r
    try:
        tid = _r.randint(0, 65535)
        flags = 0x0100
        q = _st.pack(">HHHHHH", tid, flags, 1, 0, 0, 0)
        for label in hostname.rstrip(".").split("."):
            lb = label.encode()
            q += bytes([len(lb)]) + lb
        q += b"\x00"
        q += _st.pack(">HH", 1, 1)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        sock.sendto(q, (dns_ip, port))
        resp, _ = sock.recvfrom(512)
        
        if len(resp) < 12:
            return None
        r_flags = _st.unpack(">H", resp[2:4])[0]
        rcode = r_flags & 0x000F
        if rcode == 3:  # NXDOMAIN
            return False
        if rcode == 0:  # NOERROR
            ancount = _st.unpack(">H", resp[6:8])[0]
            return ancount > 0
        return False
    except Exception:
        return None


# ── Parental Control module ──────────────────────────────────────────────────

def _parental_tags(tag_suffix: str):
    """Returns a unique START/END tag pair for the given block category."""
    key = tag_suffix.replace(".txt", "").upper()
    return (
        f"# === HOSTS_EDITOR_PARENTAL_{key}_START ===",
        f"# === HOSTS_EDITOR_PARENTAL_{key}_END ===",
    )


def is_parental_active(tag_suffix: str = "xxx.txt") -> bool:
    """
    Checks whether the hosts file contains an active section for the given category.
    State is always read from disk — correct after application restart.
    """
    if not os.path.exists(HOSTS_PATH):
        return False
    start_tag, end_tag = _parental_tags(tag_suffix)
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return start_tag in content and end_tag in content
    except Exception:
        return False


def toggle_parental_control(enable: bool, list_path: str = None,
                             tag_suffix: str = "xxx.txt") -> bool:
    """
    Enables or disables the block for a given category in the hosts file.
    Each category has its own unique tag — categories never overwrite each other.
    """
    if not os.path.exists(HOSTS_PATH):
        return False

    start_tag, end_tag = _parental_tags(tag_suffix)

    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        # 1. Remove existing section for this category
        new_lines = []
        inside = False
        for line in lines:
            if start_tag in line:
                inside = True
                continue
            if end_tag in line:
                inside = False
                continue
            if not inside:
                new_lines.append(line)

        # 2. If enabling — append new section at the end
        if enable and list_path and os.path.exists(list_path):
            blocked = set()
            with open(list_path, "r", encoding="utf-8", errors="replace") as lf:
                for line in lf:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    domain = parts[-1].lower()
                    if "." in domain:
                        blocked.add(domain)

            if blocked:
                if new_lines and not new_lines[-1].endswith("\n"):
                    new_lines.append("\n")
                new_lines.append(f"{start_tag}\n")
                for domain in sorted(blocked):
                    new_lines.append(f"0.0.0.0\t\t{domain} # Secure\n")
                new_lines.append(f"{end_tag}\n")

        # 3. Write file and flush DNS
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        import subprocess
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        subprocess.run(["ipconfig", "/flushdns"], startupinfo=si,
                       capture_output=True, text=True)
        return True

    except Exception as e:
        print(T("parental_err", ex=e))
        return False