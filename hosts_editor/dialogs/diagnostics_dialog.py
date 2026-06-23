"""
Diagnostics dialog: domain existence check and malware detection.
To add a new scanning rule, edit this file.
"""

import tkinter as tk
from tkinter import ttk

from ..constants import DARK
from ..core import dns_lookup_external
from ..widgets import make_btn, DarkDialog, DarkToplevel
from ..i18n import T


_SYSTEM_DOMAINS: frozenset = frozenset({
    "localhost", "localhost.localdomain", "local", "broadcasthost",
    "ip6-localhost", "ip6-loopback", "ip6-localnet", "ip6-mcastprefix",
    "ip6-allnodes", "ip6-allrouters", "ip6-allhosts", "wpad", "wpad.home",
    "google.com", "www.google.com", "bing.com", "www.bing.com",
    "microsoft.com", "www.microsoft.com", "apple.com", "www.apple.com",
    "amazon.com", "www.amazon.com", "facebook.com", "www.facebook.com",
    "twitter.com", "www.twitter.com", "paypal.com", "www.paypal.com",
    "bankofamerica.com", "chase.com", "wellsfargo.com",
    "login.microsoftonline.com", "account.microsoft.com",
    "windowsupdate.microsoft.com", "update.microsoft.com",
})
_UPDATE_DOMAINS: frozenset = frozenset({
    "windowsupdate.com", "windowsupdate.microsoft.com",
    "update.microsoft.com", "download.windowsupdate.com",
    "ntservicepack.microsoft.com", "wustat.windows.com",
    "mu.microsoft.com", "wu.microsoft.com",
    "definitionupdates.microsoft.com",
    "update.avast.com", "update.avg.com",
    "update.kaspersky.com", "kaspersky.com",
    "update.norton.com", "liveupdate.symantec.com",
    "update.eset.com", "update.bitdefender.com",
    "update.malwarebytes.com", "downloads.malwarebytes.com",
    "update.avira.com", "update.drweb.com",
})
_HOMOGLYPH_CHARS: frozenset = frozenset("\u0430\u0435\u043e\u0440\u0441\u0445\u0456")


class DiagnosticsDialog(DarkToplevel):
    SYSTEM_DOMAINS  = _SYSTEM_DOMAINS
    UPDATE_DOMAINS  = _UPDATE_DOMAINS
    HOMOGLYPH_CHARS = _HOMOGLYPH_CHARS

    def __init__(self, parent, entries, mode="existence", on_remove=None):
        title_key = "diag_title_existence" if mode == "existence" else "diag_title_malware"
        super().__init__(parent, title=T(title_key), body_bg=DARK["bg"],
                          resizable=True, min_width=780, min_height=520)
        self.mode       = mode
        self.entries    = entries
        self._on_remove = on_remove

        hdr = tk.Frame(self.body, bg=DARK["bg2"],
                       highlightthickness=1, highlightbackground=DARK["border"])
        hdr.pack(fill="x")
        icon = "\U0001f50d" if mode == "existence" else "\U0001f6e1"
        tk.Label(hdr, text=icon, bg=DARK["bg2"], fg=DARK["fg"],
                 font=("Segoe UI Emoji", 18)).pack(side="left", padx=(12, 6), pady=8)

        n = len([e for e in entries if e.get("enabled") is True])
        desc_key = "diag_desc_existence" if mode == "existence" else "diag_desc_malware"
        tk.Label(hdr, text=T(desc_key, n=n), bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 9), justify="left").pack(side="left", padx=4, pady=8)

        self._start_btn = make_btn(hdr, "\u25b6", "#4ec94e", T("diag_btn_run"),
                                   self._run, accent=True)
        self._start_btn.pack(side="right", padx=10, pady=6)

        pf = tk.Frame(self.body, bg=DARK["bg"])
        pf.pack(fill="x", padx=8, pady=(6, 0))
        self._prog_lbl = tk.Label(pf, text=T("diag_click_to_start"),
                                  bg=DARK["bg"], fg=DARK["fg2"], font=("Segoe UI", 9))
        self._prog_lbl.pack(side="left")
        self._prog_count = tk.Label(pf, text="", bg=DARK["bg"], fg=DARK["fg2"],
                                    font=("Segoe UI", 9))
        self._prog_count.pack(side="right")

        tbl = tk.Frame(self.body, bg=DARK["bg"])
        tbl.pack(fill="both", expand=True, padx=8, pady=6)

        if mode == "existence":
            cols   = ("result", "hostname", "ip", "info")
            widths = [100, 270, 140, 190]
            heads  = [T("diag_col_result"), T("diag_col_hostname"), T("diag_col_ip"), T("diag_col_info")]
        else:
            cols   = ("risk", "hostname", "ip", "reason")
            widths = [100, 240, 140, 220]
            heads  = [T("diag_col_risk"), T("diag_col_hostname"), T("diag_col_ip"), T("diag_col_reason")]

        self.tree = ttk.Treeview(tbl, columns=cols, show="headings",
                                 selectmode="extended", style="Diag.Treeview")
        for col, w, h in zip(cols, widths, heads):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, stretch=(col == cols[-1]))
        self.tree.tag_configure("ok",     foreground=DARK["green"])
        self.tree.tag_configure("warn",   foreground="#f0c040")
        self.tree.tag_configure("error",  foreground=DARK["red"])
        self.tree.tag_configure("high",   foreground=DARK["red"])
        self.tree.tag_configure("medium", foreground="#f0c040")
        vsb = ttk.Scrollbar(tbl, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="left", fill="y")

        self._status = tk.Label(self.body, text="", anchor="w", padx=10, pady=3,
                                bg=DARK["bg2"], fg=DARK["fg2"], font=("Segoe UI", 9),
                                highlightthickness=1, highlightbackground=DARK["border"])
        self._status.pack(fill="x", side="bottom")

        act_bar = tk.Frame(self.body, bg=DARK["bg2"],
                           highlightthickness=1, highlightbackground=DARK["border"])
        act_bar.pack(fill="x", side="bottom")
        if mode == "existence":
            make_btn(act_bar, "\U0001f5d1", "#f0c040", T("diag_btn_del_inactive"),
                     self._remove_nonexistent).pack(side="left", padx=6, pady=4)
            make_btn(act_bar, "\U0001f5d1", "#e05050", T("diag_btn_del_sel"),
                     self._remove_selected).pack(side="left", padx=3, pady=4)
        else:
            make_btn(act_bar, "\U0001f5d1", "#e05050", T("diag_btn_del_sel_hosts"),
                     self._remove_selected).pack(side="left", padx=6, pady=4)
        tk.Label(act_bar, text=T("diag_hint_multi"),
                 bg=DARK["bg2"], fg=DARK["fg2"],
                 font=("Segoe UI", 8)).pack(side="right", padx=10)

        self.center_on_parent(min_w=780, min_h=520)

    def _run(self):
        import threading
        for w in [self._start_btn] + self._start_btn.winfo_children():
            w.configure(bg=DARK["bg3"])
        self.tree.delete(*self.tree.get_children())
        real = [dict(e) for e in self.entries if e["enabled"] is True]
        threading.Thread(target=self._scan, args=(real,), daemon=True).start()

    def _scan(self, entries):
        if self.mode == "existence":
            self._scan_existence(entries)
        else:
            self._scan_malware(entries)
        self.after(0, lambda: [
            w.configure(bg=DARK["accent"])
            for w in [self._start_btn] + self._start_btn.winfo_children()])

    def _remove_nonexistent(self):
        iids = [iid for iid in self.tree.get_children()
                if "warn" in self.tree.item(iid, "tags")]
        if not iids:
            DarkDialog.info(self, T("diag_no_inactive_title"), T("diag_no_inactive_msg"))
            return
        preview = "\n".join(iids[:10])
        suffix  = T("diag_more", n=len(iids) - 10) if len(iids) > 10 else ""
        msg = T("diag_del_inactive_msg", n=len(iids), preview=preview, suffix=suffix)
        if not DarkDialog.ask(self, T("diag_del_confirm_title"), msg):
            return
        self._on_remove(set(iids))
        for iid in iids:
            self.tree.delete(iid)
        self._status.configure(text=T("diag_status_deleted_inactive", n=len(iids)))

    def _remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            DarkDialog.info(self, T("no_sel_title"), T("diag_no_sel_msg"))
            return
        hostnames = set(sel)
        preview = "\n".join(list(hostnames)[:10])
        suffix  = T("diag_more", n=len(hostnames) - 10) if len(hostnames) > 10 else ""
        msg = T("diag_del_sel_msg", n=len(hostnames), preview=preview, suffix=suffix)
        if not DarkDialog.ask(self, T("diag_del_confirm_title"), msg):
            return
        self._on_remove(hostnames)
        for iid in sel:
            self.tree.delete(iid)
        self._status.configure(text=T("diag_status_deleted_sel", n=len(hostnames)))

    def _scan_existence(self, entries):
        total = len(entries)
        found = missing = errors = 0
        for i, e in enumerate(entries):
            host = e["hostname"]
            self.after(0, lambda i=i, h=host: (
                self._prog_lbl.configure(text=T("diag_scanning") + h),
                self._prog_count.configure(text=f"{i + 1} / {total}")))
            result = dns_lookup_external(host)
            if result is True:
                found += 1
                self.after(0, lambda h=host, ip=e["ip"]: self.tree.insert(
                    "", "end", iid=h,
                    values=(T("diag_exist_ok"), h, ip, T("diag_exist_ok_info")),
                    tags=("ok",)))
            elif result is False:
                missing += 1
                self.after(0, lambda h=host, ip=e["ip"]: self.tree.insert(
                    "", "end", iid=h,
                    values=(T("diag_exist_miss"), h, ip, T("diag_exist_miss_info")),
                    tags=("warn",)))
            else:
                errors += 1
                self.after(0, lambda h=host, ip=e["ip"]: self.tree.insert(
                    "", "end", iid=h,
                    values=(T("diag_exist_err"), h, ip, T("diag_exist_err_info")),
                    tags=("error",)))
        summary = T("diag_summary_exist", found=found, missing=missing, errors=errors)
        self.after(0, lambda: (
            self._prog_lbl.configure(text=T("diag_scan_done")),
            self._prog_count.configure(text=f"{total} / {total}"),
            self._status.configure(text=summary)))

    def _scan_malware(self, entries):
        import ipaddress as _ip
        from collections import Counter
        total  = len(entries)
        issues = 0

        public_ip_count = Counter()
        for e in entries:
            if e.get("enabled") is not True:
                continue
            try:
                addr = _ip.ip_address(e["ip"].strip())
                if not addr.is_loopback and not addr.is_private and str(addr) not in ("0.0.0.0", "::"):
                    public_ip_count[e["ip"].strip()] += 1
            except ValueError:
                pass

        for i, e in enumerate(entries):
            if e.get("enabled") is not True:
                continue
            host = e["hostname"].lower().strip()
            ip   = e["ip"].strip()
            self.after(0, lambda i=i, h=host: (
                self._prog_lbl.configure(text=T("diag_analyzing") + h),
                self._prog_count.configure(text=f"{i + 1} / {total}")))
            reasons = []
            risk    = None

            if host in self.SYSTEM_DOMAINS:
                try:
                    addr = _ip.ip_address(ip)
                    if not addr.is_loopback and str(addr) not in ("0.0.0.0", "::"):
                        reasons.append(T("diag_reason_sys_dom", ip=ip))
                        risk = "high"
                except ValueError:
                    pass

            if host in self.UPDATE_DOMAINS:
                try:
                    addr = _ip.ip_address(ip)
                    if addr.is_loopback or str(addr) in ("0.0.0.0", "::"):
                        reasons.append(T("diag_reason_update", host=host))
                        risk = "high"
                except ValueError:
                    pass

            try:
                addr = _ip.ip_address(ip)
                if not addr.is_loopback and not addr.is_private and str(addr) not in ("0.0.0.0", "::"):
                    reasons.append(T("diag_reason_public_ip", ip=ip))
                    risk = risk or "medium"
            except ValueError:
                pass

            if public_ip_count.get(ip, 0) > 5:
                reasons.append(T("diag_reason_many_dom", n=public_ip_count[ip]))
                risk = risk or "medium"

            raw_host = e["hostname"].strip()
            hg = [c for c in raw_host if c in self.HOMOGLYPH_CHARS]
            if hg:
                chars_str = ", ".join("U+" + format(ord(c), "04X") for c in set(hg))
                reasons.append(T("diag_reason_homoglyph", chars=chars_str))
                risk = "high"

            try:
                _ip.ip_address(host)
                reasons.append(T("diag_reason_ip_host"))
                risk = risk or "medium"
            except ValueError:
                pass

            if reasons:
                issues += 1
                tag   = risk or "medium"
                label = T("diag_risk_high") if risk == "high" else T("diag_risk_medium")
                reason_str = "; ".join(reasons)
                self.after(0, lambda h=host, ip=ip, label=label, reason_str=reason_str, tag=tag:
                    self.tree.insert("", "end", iid=h,
                                     values=(label, h, ip, reason_str), tags=(tag,)))

        if issues == 0:
            self.after(0, lambda: self.tree.insert(
                "", "end",
                values=(T("diag_clean"), T("diag_clean_msg"), "", ""),
                tags=("ok",)))
        summary = T("diag_summary_malware", issues=issues, total=total)
        self.after(0, lambda: (
            self._prog_lbl.configure(text=T("diag_scan_done")),
            self._prog_count.configure(text=f"{total} / {total}"),
            self._status.configure(text=summary)))
