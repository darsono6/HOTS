import os
import re
import csv
import shutil
import socket
import stat
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

from .constants import HOSTS_PATH
from .core_antispy import HostsLockManager, HostsLockError, CREATE_NO_WINDOW
from .i18n import T
from .bg_tasks import start_bg_timer

MAX_ACTIVE_ENTRIES = 20000

_HOSTS_FILE_LOCK = threading.Lock()

_MIN_WRITE_GAP = 0.35
_last_write_ts = 0.0

_SIZE_SCALE_MB = 2.0

def _hosts_size_headroom(base: float, cap: float) -> float:
    try:
        size_mb = os.path.getsize(HOSTS_PATH) / (1024 * 1024)
    except OSError:
        return base
    return min(base + size_mb / _SIZE_SCALE_MB, cap)

def _wait_for_write_gap():
    gap = _hosts_size_headroom(_MIN_WRITE_GAP, cap=2.5)
    elapsed = time.monotonic() - _last_write_ts
    if elapsed < gap:
        time.sleep(gap - elapsed)

def _mark_write_done():
    global _last_write_ts
    _last_write_ts = time.monotonic()

class HostsLimitExceeded(Exception):
    def __init__(self, would_be_count: int):
        self.would_be_count = would_be_count
        super().__init__(f"would result in {would_be_count} active entries")

class HostsBusyError(Exception):
    pass

def is_valid_ip(ip: str) -> bool:
    ip = ip.strip()
    if not ip:
        return False
    ip_clean = ip.split('%')[0]
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(family, ip_clean)
            return True
        except (socket.error, OSError):
            pass
    return False

def _looks_like_entry(text: str) -> bool:
    parts = text.split()
    if len(parts) < 2:
        return False
    candidate = parts[0].split('%')[0]
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            socket.inet_pton(family, candidate)
            return True
        except (OSError, socket.error):
            pass
    return False

def _looks_like_ip_attempt(candidate: str) -> bool:
    candidate = candidate.split('%')[0]
    if not candidate:
        return False
    core = candidate.lstrip("/\\.,;:'\"`|~")
    if not core:
        return False
    if core[0].isdigit() or core[0] == ":":
        return True

    if ":" in core and re.fullmatch(r"[0-9a-fA-F:]+", core):
        return True
    return False

def _looks_like_malformed_entry(raw_line: str) -> bool:
    stripped = raw_line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    parts = stripped.split(None, 1)
    candidate = parts[0].split('%')[0]
    if not _looks_like_ip_attempt(candidate):
        return False
    if len(parts) < 2:

        return True
    return not is_valid_ip(candidate)

def _parse_line(raw_line: str) -> dict:
    stripped = raw_line.strip()

    if not stripped:
        return {"enabled": None, "ip": "", "hostname": "", "comment": "", "raw": raw_line}

    if stripped.startswith("#"):
        content = stripped[1:].strip()
        if _looks_like_entry(content):
            parts = content.split(None, 1)
            ip = parts[0]
            rest = parts[1]
            comment = ""
            if "#" in rest:
                host_part, comment_part = rest.split("#", 1)
                hostname = host_part.strip()
                comment = comment_part.strip()
            else:
                hostname = rest.strip()
            return {"enabled": False, "ip": ip, "hostname": hostname,
                    "comment": comment, "raw": raw_line}
        return {"enabled": None, "ip": "", "hostname": "", "comment": "", "raw": raw_line}

    parts = stripped.split(None, 1)
    if len(parts) < 2:

        return {"enabled": None, "ip": "", "hostname": "", "comment": "", "raw": raw_line}
    if not _looks_like_entry(stripped):

        return {"enabled": None, "ip": "", "hostname": "", "comment": "", "raw": raw_line}
    ip = parts[0]
    rest = parts[1]
    comment = ""
    if "#" in rest:
        host_part, comment_part = rest.split("#", 1)
        hostname = host_part.strip()
        comment = comment_part.strip()
    else:
        hostname = rest.strip()
    return {"enabled": True, "ip": ip, "hostname": hostname,
            "comment": comment, "raw": raw_line}

def _read_text_smart(path) -> list:
    with open(path, "rb") as f:
        raw = f.read()

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text = raw.decode("utf-16", errors="replace")
    elif raw.startswith(b"\xef\xbb\xbf"):
        text = raw.decode("utf-8-sig", errors="replace")
    else:

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = raw.decode("cp1250")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", errors="replace")

    return text.splitlines()

def parse_hosts(path) -> list:
    entries = []
    if not os.path.exists(path):
        return entries

    try:
        lines = _read_text_smart(path)
    except Exception:
        return entries

    for line in lines:
        raw_line = line.rstrip("\r\n")
        entries.append(_parse_line(raw_line))

    return entries

def _entry_matches_raw(e: dict) -> bool:
    raw = e.get("raw")
    if not raw:
        return False
    parsed = _parse_line(raw)
    return (
        parsed["enabled"] == e["enabled"]
        and parsed["ip"] == e.get("ip", "")
        and parsed["hostname"] == e.get("hostname", "")
        and parsed["comment"] == e.get("comment", "")
    )

def _format_entry_line(ip: str, hostname: str, comment: str = "",
                        enabled: bool = True, include_comments: bool = True) -> str:
    prefix = "" if enabled else "# "
    line = f"{prefix}{ip} {hostname}"
    if include_comments and comment:
        line += f" # {comment}"
    return line

def entries_to_text(entries: list, include_comments: bool = True) -> str:
    lines = []
    for e in entries:
        if e["enabled"] is None:
            lines.append(e.get("raw", ""))
            continue

        if include_comments and _entry_matches_raw(e):
            lines.append(e["raw"])
            continue

        line = _format_entry_line(e["ip"], e["hostname"], e.get("comment", ""),
                                   e["enabled"], include_comments)
        lines.append(line)
    return "\n".join(lines) + "\n"

MAX_BACKUPS = 15

def _rotate_backups(path, keep: int = MAX_BACKUPS):
    try:
        existing = list_backups(path)
        for old_bak, _ in existing[keep:]:
            try:
                try:
                    os.chmod(old_bak, stat.S_IWRITE)
                except OSError:
                    pass
                old_bak.unlink()
            except Exception:
                pass
    except Exception:
        pass

def create_backup(path) -> str | None:
    if not os.path.exists(path):
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_path = f"{path}.bak_{ts}"

    last_err = None
    for attempt in range(10):
        try:
            shutil.copy2(path, bak_path)
            last_err = None
            break
        except PermissionError as ex:
            last_err = ex
            time.sleep(min(0.3 * (attempt + 1), 1.0))
    if last_err is not None:
        raise last_err

    try:
        os.chmod(bak_path, stat.S_IWRITE)
    except OSError:
        pass
    _rotate_backups(path)
    return bak_path

def restore_from_backup(path, backup_path) -> None:
    if HostsLockManager.is_active():
        raise HostsLockError(T("hosts_lock_blocks_write"))
    with _HOSTS_FILE_LOCK:
        _wait_for_write_gap()
        try:
            create_backup(path)
        except Exception:
            pass

        last_err = None
        for attempt in range(10):
            try:
                if os.path.exists(path):
                    try:
                        os.chmod(path, stat.S_IWRITE)
                    except OSError:
                        pass
                shutil.copy2(str(backup_path), path)
                last_err = None
                break
            except PermissionError as ex:
                last_err = ex
                time.sleep(min(0.3 * (attempt + 1), 1.0))
        if last_err is not None:
            raise HostsBusyError(T("hosts_busy_msg"))
        _mark_write_done()
        try:
            os.chmod(path, stat.S_IWRITE)
        except OSError:
            pass
    flush_dns_cache_debounced()

def save_hosts(path, entries: list) -> bool:
    if HostsLockManager.is_active():
        raise HostsLockError(T("hosts_lock_blocks_write"))

    text_content = entries_to_text(entries)
    try:
        with _HOSTS_FILE_LOCK:
            _wait_for_write_gap()

            if os.path.exists(path):
                try:
                    create_backup(path)
                except Exception as ex:
                    raise RuntimeError(T("save_backup_err", ex=ex))

            dir_path = os.path.dirname(os.path.abspath(path))
            fd, tmp_path = tempfile.mkstemp(dir=dir_path, prefix=".hosts_tmp_")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(text_content)

                last_err = None
                for attempt in range(10):
                    try:
                        if os.path.exists(path):
                            try:
                                os.chmod(path, stat.S_IWRITE)
                            except OSError:
                                pass
                        os.replace(tmp_path, path)
                        last_err = None
                        break
                    except PermissionError as ex:
                        last_err = ex
                        time.sleep(min(0.15 * (attempt + 1), 0.6))
                if last_err is not None:
                    raise last_err
                _mark_write_done()
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
    except PermissionError:
        raise HostsBusyError(T("hosts_busy_msg"))
    except HostsLockError:
        raise
    except Exception as ex:
        raise RuntimeError(T("save_write_err", ex=ex))

    flush_dns_cache_debounced()
    return True

def flush_dns_cache() -> bool:
    import subprocess
    try:

        res = subprocess.run(["ipconfig", "/flushdns"],
                             capture_output=True, text=True,
                             creationflags=CREATE_NO_WINDOW)
        return res.returncode == 0
    except Exception:
        return False

_DNS_FLUSH_DEBOUNCE = 1.0
_dns_flush_timer = None
_dns_flush_lock = threading.Lock()

def flush_dns_cache_debounced():
    global _dns_flush_timer
    debounce = _hosts_size_headroom(_DNS_FLUSH_DEBOUNCE, cap=4.0)
    with _dns_flush_lock:
        if _dns_flush_timer is not None:
            _dns_flush_timer.cancel()
        _dns_flush_timer = start_bg_timer(debounce, flush_dns_cache)

def list_backups(hosts_path) -> list:
    if not hosts_path:
        return []

    parent_dir = Path(hosts_path).parent
    base_name = Path(hosts_path).name

    if not parent_dir.exists():
        return []

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
                continue
            d_str, t_str = m.groups()
            try:
                dt = datetime.strptime(f"{d_str}_{t_str}", "%Y%m%d_%H%M%S")
            except ValueError:
                continue
            backups.append((p, dt))
    except Exception:
        return []

    backups.sort(key=lambda x: x[1], reverse=True)
    return backups

def import_from_path(path: str, current_entries: list):
    imported = parse_hosts(path)
    new_entries = [e for e in imported if e["enabled"] is not None]

    if not new_entries:
        raise ValueError(T("import_empty_msg"))

    fname = Path(path).name
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M")

    result = list(current_entries)

    result.append({"enabled": None, "ip": "", "hostname": "", "comment": "", "raw": ""})
    result.append({"enabled": None, "ip": "", "hostname": "", "comment": "",
                   "raw": T('import_header_comment', path=fname, ts=ts)})
    result.extend(new_entries)
    return result, len(new_entries)

def export_to_path(path: str, entries: list, include_comments: bool = True):
    real = [e for e in entries if e["enabled"] is not None]
    if path.endswith(".csv"):
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            headers = T("export_csv_headers").split(",")
            if not include_comments:
                headers = headers[:3]
            writer.writerow(headers)
            for e in real:
                status = "active" if e["enabled"] else "disabled"
                if include_comments:
                    writer.writerow([status, e["ip"], e["hostname"], e["comment"]])
                else:
                    writer.writerow([status, e["ip"], e["hostname"]])
        return len(real)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(entries_to_text(entries, include_comments=include_comments))
        return len(real)

def has_internet_connection(timeout: float = 2.5) -> bool:
    targets = [
        ("1.1.1.1", 53),
        ("8.8.8.8", 53),
        ("1.0.0.1", 53),
    ]
    for host, port in targets:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            continue
    return False

def dns_lookup_external(hostname, dns_ip="8.8.8.8", port=53, timeout=4):
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

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.sendto(q, (dns_ip, port))
            resp, _ = sock.recvfrom(512)

        if len(resp) < 12:
            return None
        r_flags = _st.unpack(">H", resp[2:4])[0]
        rcode = r_flags & 0x000F
        if rcode == 3:
            return False
        if rcode == 0:
            ancount = _st.unpack(">H", resp[6:8])[0]
            return ancount > 0
        return False
    except Exception:
        return None

def _parental_tags(tag_suffix: str):
    key = tag_suffix.replace(".txt", "").upper()
    return (
        f"# === HOSTS_EDITOR_PARENTAL_{key}_START ===",
        f"# === HOSTS_EDITOR_PARENTAL_{key}_END ===",
    )

def is_parental_active(tag_suffix: str = "xxx.txt") -> bool:
    if not os.path.exists(HOSTS_PATH):
        return False
    start_tag, end_tag = _parental_tags(tag_suffix)
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return start_tag in content and end_tag in content
    except Exception:
        return False

def get_parental_active_map(tag_suffixes) -> dict:
    tag_suffixes = list(tag_suffixes)
    result = {suffix: False for suffix in tag_suffixes}
    if not os.path.exists(HOSTS_PATH):
        return result
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return result
    for suffix in tag_suffixes:
        start_tag, end_tag = _parental_tags(suffix)
        result[suffix] = start_tag in content and end_tag in content
    return result

def toggle_parental_control(enable: bool, list_path: str = None,
                             tag_suffix: str = "xxx.txt",
                             comment: str = "Secure") -> bool:
    if not os.path.exists(HOSTS_PATH):
        return False
    if HostsLockManager.is_active():
        raise HostsLockError(T("hosts_lock_blocks_write"))

    start_tag, end_tag = _parental_tags(tag_suffix)

    try:
        with _HOSTS_FILE_LOCK:
            _wait_for_write_gap()
            lines = None
            read_err = None
            for attempt in range(15):
                try:
                    with open(HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                    read_err = None
                    break
                except PermissionError as ex:
                    read_err = ex
                    time.sleep(min(0.3 * (attempt + 1), 1.0))
            if read_err is not None:
                raise HostsBusyError(T("hosts_busy_msg"))

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
                    block_lines = [f"{start_tag}\n"]
                    for domain in sorted(blocked):
                        block_lines.append(_format_entry_line("0.0.0.0", domain, comment) + "\n")
                    block_lines.append(f"{end_tag}\n")

                    active_total = sum(
                        1 for ln in (new_lines + block_lines)
                        if _parse_line(ln.rstrip("\r\n"))["enabled"] is True
                    )
                    if active_total > MAX_ACTIVE_ENTRIES:
                        raise HostsLimitExceeded(active_total)

                    if new_lines and not new_lines[-1].endswith("\n"):
                        new_lines.append("\n")
                    new_lines.extend(block_lines)

            try:
                create_backup(HOSTS_PATH)
            except Exception:
                pass

            text_content = "".join(new_lines)
            dir_path = os.path.dirname(os.path.abspath(HOSTS_PATH))
            fd, tmp_path = tempfile.mkstemp(dir=dir_path, prefix=".hosts_tmp_")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(text_content)

                last_err = None
                for attempt in range(25):
                    try:
                        if os.path.exists(HOSTS_PATH):
                            try:
                                os.chmod(HOSTS_PATH, stat.S_IWRITE)
                            except OSError:
                                pass
                        os.replace(tmp_path, HOSTS_PATH)
                        last_err = None
                        break
                    except PermissionError as ex:
                        last_err = ex
                        time.sleep(min(0.3 * (attempt + 1), 1.0))
                if last_err is not None:

                    try:
                        if os.path.exists(HOSTS_PATH):
                            try:
                                os.chmod(HOSTS_PATH, stat.S_IWRITE)
                            except OSError:
                                pass
                        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
                            f.write(text_content)
                        last_err = None
                    except PermissionError:
                        raise HostsBusyError(T("hosts_busy_msg"))
                if last_err is not None:
                    raise HostsBusyError(T("hosts_busy_msg"))
                _mark_write_done()
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise

        flush_dns_cache_debounced()
        return True

    except HostsLimitExceeded:
        raise
    except HostsLockError:
        raise
    except HostsBusyError:
        raise
    except Exception as e:
        print(T("parental_err", ex=e))
        return False
