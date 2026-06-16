"""
Add/edit dialog for a single hosts entry.
To change the entry form, edit this file.
"""

import re
import tkinter as tk

from ..constants import DARK
from ..core import is_valid_ip
from ..widgets import make_btn, dark_entry, field_lbl, DarkDialog, center_on_parent
from ..i18n import T


def _parse_bulk(text: str) -> list:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 2:
        return []
    results = []
    for line in lines:
        if line.startswith("#"):
            continue
        comment = ""
        if "#" in line:
            idx = line.index("#")
            comment = line[idx + 1:].strip()
            line = line[:idx].strip()
        parts = line.split()
        if not parts:
            continue
        candidate = parts[0].split("%")[0]
        import socket as _sock
        is_ip = False
        for fam in (_sock.AF_INET, _sock.AF_INET6):
            try:
                _sock.inet_pton(fam, candidate)
                is_ip = True
                break
            except Exception:
                pass
        if is_ip and len(parts) >= 2:
            results.append({
                "enabled": True, "ip": parts[0], "hostname": parts[1],
                "comment": comment, "raw": "",
            })
        elif not is_ip and len(parts) == 1:
            results.append({
                "enabled": True, "ip": "0.0.0.0", "hostname": parts[0],
                "comment": comment, "raw": "",
            })
        else:
            return []
    return results


class EntryDialog(tk.Toplevel):
    def __init__(self, parent, entry=None, existing_hostnames=None):
        super().__init__(parent)
        self.title(T("entry_title_add") if entry is None else T("entry_title_edit"))
        self.configure(bg=DARK["bg2"])
        self.resizable(False, False)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.result = None
        self.result_list = None
        self._existing = {h.lower() for h in (existing_hostnames or set())}
        self._is_edit = entry is not None

        # Row 0: IP
        field_lbl(self, T("entry_lbl_ip"), 0)
        self.ip_var = tk.StringVar(value=entry["ip"] if entry else "0.0.0.0")
        self.ip_entry = dark_entry(self, self.ip_var, width=22)
        self.ip_entry.grid(row=0, column=1, sticky="w", padx=12, pady=(7, 2))

        # Row 1: IP hint
        self._ip_hint = tk.Label(self, text="", bg=DARK["bg2"],
                                 fg=DARK["red"], font=("Segoe UI", 8))
        self._ip_hint.grid(row=1, column=1, sticky="w", padx=12, pady=(0, 4))

        self._ip_valid = True
        self.ip_var.trace_add("write", self._validate_ip)
        self.after(10, self._validate_ip)

        # Row 2: Hostname
        field_lbl(self, T("entry_lbl_host"), 2)
        self.host_var = tk.StringVar(value=entry["hostname"] if entry else "")
        self._host_entry = dark_entry(self, self.host_var, width=34)
        self._host_entry.grid(row=2, column=1, sticky="w", padx=12, pady=(7, 2))

        # Row 3: Hostname hint
        self._host_hint = tk.Label(self, text="", bg=DARK["bg2"],
                                   fg="#f0c040", font=("Segoe UI", 8),
                                   wraplength=260, justify="left")
        self._host_hint.grid(row=3, column=1, sticky="w", padx=12, pady=(0, 4))
        self.host_var.trace_add("write", self._on_host_change)

        # Row 4: Comment
        field_lbl(self, T("entry_lbl_comment"), 4)
        self.com_var = tk.StringVar(value=entry["comment"] if entry else "")
        dark_entry(self, self.com_var, width=34).grid(row=4, column=1, sticky="w",
                                                      padx=12, pady=7)

        # Row 5: Status
        self.enabled_var = tk.BooleanVar(value=entry["enabled"] if entry else True)
        tk.Checkbutton(self, text=T("entry_lbl_active"), variable=self.enabled_var,
                       bg=DARK["bg2"], fg=DARK["fg"],
                       activebackground=DARK["bg2"], activeforeground=DARK["fg"],
                       selectcolor=DARK["bg3"],
                       font=("Segoe UI", 9)).grid(row=5, column=1, sticky="w",
                                                   padx=12, pady=4)

        # Row 6: Buttons
        bf = tk.Frame(self, bg=DARK["bg2"])
        bf.grid(row=6, column=0, columnspan=2, pady=14)
        make_btn(bf, "💾", "#60c8ff", T("entry_btn_save"), self._save, accent=True).pack(side="left", padx=6)
        make_btn(bf, "✖",  "#e05050", T("entry_btn_cancel"), self.destroy).pack(side="left", padx=6)

        self.transient(parent)
        self.grab_set()
        center_on_parent(self, parent, min_w=420, min_h=280)
        self._parent = parent
        self.wait_window()

    def _refit(self):
        """Resizes the window to fit current content (after a hint changes)."""
        self.update_idletasks()
        req_w = max(420, self.winfo_reqwidth())
        req_h = max(280, self.winfo_reqheight())
        # Keep current position (X, Y), only change the size
        try:
            import re as _re
            m = _re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", self.geometry())
            if m:
                _, _, x, y = m.groups()
                sw = self.winfo_screenwidth()
                sh = self.winfo_screenheight()
                # Make sure the window doesn't go off-screen
                x = min(int(x), sw - req_w - 10)
                y = min(int(y), sh - req_h - 10)
                self.geometry(f"{req_w}x{req_h}+{x}+{y}")
        except Exception:
            pass

    def _on_host_change(self, *_):
        raw = self.host_var.get()

        if "\n" in raw:
            self._host_hint.configure(text=T("entry_hint_bulk"))
            self._refit()
            return

        needs = (raw.startswith("http://") or raw.startswith("https://")
                 or raw.endswith("/") or raw.endswith("\\"))
        if needs:
            self._host_hint.configure(text=T("entry_hint_sanitize"))
            self._refit()
            return

        if not self._is_edit:
            h = self._sanitize_hostname(raw)
            if h and h.lower() in self._existing:
                self._host_hint.configure(fg=DARK["red"], text=T("entry_hint_dup"))
                self._refit()
                return

        self._host_hint.configure(fg="#f0c040", text="")
        self._refit()

    @staticmethod
    def _sanitize_hostname(raw):
        h = raw.strip()
        h = re.sub(r"^https?://", "", h)
        h = h.split("/")[0]
        h = h.split(":")[0] if not h.startswith("[") else h
        if "@" in h:
            h = h.split("@")[-1]
        return h.strip().lower()

    def _validate_ip(self, *_):
        ip = self.ip_var.get().strip()
        if not ip:
            self.ip_entry.configure(highlightbackground=DARK["border"],
                                    highlightcolor=DARK["accent"])
            self._ip_hint.configure(text="")
            self._ip_valid = True
            return
        valid = is_valid_ip(ip)
        self._ip_valid = valid
        if valid:
            self.ip_entry.configure(highlightbackground=DARK["border"],
                                    highlightcolor=DARK["accent"])
            self._ip_hint.configure(text="")
        else:
            self.ip_entry.configure(highlightbackground=DARK["red"],
                                    highlightcolor=DARK["red"])
            self._ip_hint.configure(text=T("entry_hint_bad_ip"))
        self._refit()

    def _save(self):
        ip       = self.ip_var.get().strip()
        raw_host = self.host_var.get()

        if "\n" in raw_host:
            bulk = _parse_bulk(raw_host)
            if not bulk:
                DarkDialog.error(self, T("entry_err_title"), T("entry_err_bulk_fmt"))
                return
            new_entries = []
            skipped = []
            for e in bulk:
                if e["hostname"].lower() in self._existing:
                    skipped.append(e["hostname"])
                else:
                    new_entries.append(e)
                    self._existing.add(e["hostname"].lower())
            if skipped:
                info = T("entry_skip_msg", n=len(skipped), list="\n".join(skipped[:10]))
                if not new_entries:
                    DarkDialog.info(self, T("entry_skip_title"), info)
                    return
                DarkDialog.info(self, T("entry_skip_some"), info)
            self.result_list = new_entries
            self.destroy()
            return

        host = self._sanitize_hostname(raw_host)
        if host != raw_host.strip():
            self.host_var.set(host)
        if not ip or not host:
            DarkDialog.error(self, T("entry_err_title"), T("entry_err_required"))
            return
        if not self._ip_valid:
            if not DarkDialog.ask(self, T("entry_bad_ip_title"),
                                  T("entry_bad_ip_ask", ip=ip)):
                return
        if not self._is_edit and host.lower() in self._existing:
            if not DarkDialog.ask(self, T("entry_dup_title"),
                                  T("entry_dup_ask", host=host)):
                return
        self.result = {
            "enabled":  self.enabled_var.get(),
            "ip":       ip,
            "hostname": host,
            "comment":  self.com_var.get().strip(),
            "raw":      "",
        }
        self.destroy()
