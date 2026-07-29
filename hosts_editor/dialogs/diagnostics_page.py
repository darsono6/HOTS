import math
import re
import difflib
import ipaddress
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QApplication,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from qfluentwidgets import FluentIcon as FIF, IconWidget

from ..constants import DARK, accent_rgba
from ..core import dns_lookup_external, has_internet_connection
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton, HOTSContextMenu, h_separator
from ..i18n import T

from ._diagnostics_shared import (
    _Emitter,
    _SYSTEM_DOMAINS, _UPDATE_DOMAINS, _HOMOGLYPH_CHARS, _KNOWN_SAFE_DOMAINS,
    _SUSPICIOUS_TLDS, _SUSPICIOUS_PATTERNS, _KNOWN_CDN_DOMAINS,
    load_ignored_hosts, save_ignored_hosts,
)


class DiagnosticsPage(HOTSPage):
    SYSTEM_DOMAINS   = _SYSTEM_DOMAINS
    UPDATE_DOMAINS   = _UPDATE_DOMAINS
    HOMOGLYPH_CHARS  = _HOMOGLYPH_CHARS
    KNOWN_SAFE       = _KNOWN_SAFE_DOMAINS
    SUSPICIOUS_TLDS  = _SUSPICIOUS_TLDS
    SUSPICIOUS_PATS  = _SUSPICIOUS_PATTERNS
    KNOWN_CDN        = _KNOWN_CDN_DOMAINS

    ENTROPY_THRESHOLD    = 3.8
    ENTROPY_MIN_LEN      = 8
    TYPOSQUAT_RATIO_LOW  = 0.75
    TYPOSQUAT_RATIO_HIGH = 1.0
    MULTI_DOMAIN_LIMIT   = 3
    SUBDOMAIN_DEPTH_MAX  = 5

    ZERO_WIDTH_CHARS = frozenset(
        "\u200b\u200c\u200d\u200e\u200f\ufeff\u2060"
    )

    EXISTENCE_MAX_WORKERS = 24

    def __init__(self, parent):
        super().__init__("diagnosticsInterface", FIF.SEARCH, T("diag_title_existence"), parent)
        self.mode       = "existence"
        self.entries    = []
        self._on_remove = None
        self._run_id    = 0
        self._stop_event = threading.Event()
        self._ignored_hosts = load_ignored_hosts()
        self._ctx_menu  = None
        self._emitter   = _Emitter()
        self._emitter.row_ready.connect(self._add_row)
        self._emitter.progress.connect(self._update_progress)
        self._emitter.done.connect(self._scan_done)

    def set_context(self, entries, mode, on_remove=None):
        self._stop_event.set()
        self._run_id += 1
        self.mode       = mode
        self.entries    = entries
        self._on_remove = on_remove
        title_key = "diag_title_existence" if mode == "existence" else "diag_title_malware"
        self.set_title(T(title_key))
        self._rebuild()

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _rebuild(self):
        self._clear_content()
        self._build()

    def _build(self):
        cl = self.content_layout

        hdr = QWidget()
        hdr.setStyleSheet(f"background: {DARK['panel_bg']}; border-bottom: 1px solid {DARK['border_faint']};")
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(12, 8, 8, 8)

        icon_fif = FIF.SEARCH if self.mode == "existence" else FIF.CERTIFICATE
        ico_lbl = IconWidget(icon_fif)
        ico_lbl.setFixedSize(20, 20)
        ico_lbl.setIcon(icon_fif.icon(color=QColor(DARK["accent"])))
        hdr_lay.addWidget(ico_lbl, 0, Qt.AlignVCenter)

        n = len([e for e in self.entries if e.get("enabled") is True])
        desc_key = "diag_desc_existence" if self.mode == "existence" else "diag_desc_malware"
        desc = QLabel(T(desc_key))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        hdr_lay.addWidget(desc, 1)

        self._run_btn = HOTSButton(FIF.PLAY, "#ffffff", T("diag_btn_run"), accent=True)
        self._run_btn.fit_to_content()
        self._run_btn.clicked.connect(self._run)
        hdr_lay.addWidget(self._run_btn, 0, Qt.AlignVCenter)

        self._stop_btn = HOTSButton(FIF.CLOSE, DARK["red"], T("diag_btn_stop"))
        self._stop_btn.fit_to_content()
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop)
        hdr_lay.addWidget(self._stop_btn, 0, Qt.AlignVCenter)
        cl.addWidget(hdr)

        prog_w = QWidget()
        prog_w.setStyleSheet("background: transparent;")
        prog_lay = QHBoxLayout(prog_w)
        prog_lay.setContentsMargins(12, 6, 12, 6)
        self._prog_lbl = QLabel(T("diag_click_to_start"))
        self._prog_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        prog_lay.addWidget(self._prog_lbl)
        prog_lay.addStretch()
        self._prog_count = QLabel(T("diag_scan_count", n=n))
        self._prog_count.setStyleSheet(f"color: {DARK['accent']}; font-size: 9pt; font-weight: 600; background: transparent;")
        prog_lay.addWidget(self._prog_count)
        cl.addWidget(prog_w)

        if self.mode == "existence":
            headers = [T("diag_col_result"), T("diag_col_hostname"), T("diag_col_ip"), T("diag_col_info")]
            widths  = [100, 270, 140, 190]
        else:
            headers = [T("diag_col_risk"), T("diag_col_hostname"), T("diag_col_ip"), T("diag_col_reason")]
            widths  = [100, 240, 140, 220]

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        if self.mode == "malware":
            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        _hdr = self.table.horizontalHeader()
        _hdr.setSectionResizeMode(QHeaderView.Interactive)
        _hdr.setStretchLastSection(True)
        _hdr.setMinimumSectionSize(50)
        for i, w in enumerate(widths[:-1]):
            self.table.setColumnWidth(i, w)

        self.table.setStyleSheet(
            f"QTableWidget {{ background-color: transparent; color: {DARK['fg']}; "
            f"border: none; gridline-color: {DARK['grid_line']}; }}"
            f"QTableWidget::item {{ background-color: transparent; }}"
            f"QTableWidget::item:selected {{ background-color: {accent_rgba(0.16)}; color: {DARK['fg']}; }}"
            f"QHeaderView::section {{ background-color: {DARK['panel_bg_alt']}; color: {DARK['fg2']}; "
            f"border: none; border-bottom: 1px solid {DARK['border_soft2']}; padding: 6px; }}"
        )
        cl.addWidget(self.table, 1)

        act = QWidget()
        act.setStyleSheet(f"background: {DARK['panel_bg']};")
        act_lay = QHBoxLayout(act)
        act_lay.setContentsMargins(8, 6, 8, 6)

        if self.mode == "existence":
            del_inactive_btn = HOTSButton(FIF.DELETE, "#f0c040", T("diag_btn_del_inactive"))
            del_inactive_btn.fit_to_content()
            del_inactive_btn.clicked.connect(self._remove_nonexistent)
            act_lay.addWidget(del_inactive_btn)

        del_sel_btn = HOTSButton(FIF.DELETE, DARK["red"],
                                 T("diag_btn_del_sel") if self.mode == "existence"
                                 else T("diag_btn_del_sel_hosts"))
        del_sel_btn.fit_to_content()
        del_sel_btn.clicked.connect(self._remove_selected)
        act_lay.addWidget(del_sel_btn)
        act_lay.addStretch()

        cl.addWidget(h_separator())
        cl.addWidget(act)

        self._status = QLabel("")
        self._status.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        cl.addWidget(self._status)

    def _run(self):
        if self.mode == "existence" and not has_internet_connection():
            HOTSDialog.error(self, T("diag_no_internet_title"), T("diag_no_internet_msg"))
            return

        self._stop_event.clear()
        self._run_btn.setEnabled(False)
        self._run_btn.set_accent(False)
        self._stop_btn.setEnabled(True)
        self.table.setRowCount(0)
        real = [dict(e) for e in self.entries if e["enabled"] is True]
        run_id = self._run_id
        threading.Thread(target=self._scan, args=(real, run_id), daemon=True).start()

    def _stop(self):
        self._stop_event.set()
        self._stop_btn.setEnabled(False)
        self._prog_lbl.setText(T("diag_stopping"))

    def _scan(self, entries, run_id):
        try:
            if self.mode == "existence":
                self._scan_existence(entries, run_id)
            else:
                self._scan_malware(entries, run_id)
        except Exception as exc:
            import traceback
            err = traceback.format_exc()
            if run_id == self._run_id:
                self._emitter.row_ready.emit("ERROR", str(exc), "", err[:120], "error")
                self._emitter.done.emit(f"Scan error: {exc}")

    @staticmethod
    def _shannon_entropy(host: str) -> float:
        label = host.split(".")[0]
        if not label:
            return 0.0
        label_no_hyphens = label.replace("-", "")
        if not label_no_hyphens:
            return 0.0
        freq = Counter(label_no_hyphens)
        n = len(label_no_hyphens)
        return -sum((c / n) * math.log2(c / n) for c in freq.values())

    @staticmethod
    def _typosquat_match(host: str, known: tuple) -> "str | None":
        host_base = host.rsplit(".", 1)[0] if "." in host else host

        for safe in known:
            if host == safe:
                continue
            if host.endswith("." + safe):
                continue

            safe_base = safe.rsplit(".", 1)[0]
            if host_base == safe_base:
                continue

            ratio_full = difflib.SequenceMatcher(None, host, safe).ratio()
            if DiagnosticsPage.TYPOSQUAT_RATIO_LOW < ratio_full < DiagnosticsPage.TYPOSQUAT_RATIO_HIGH:
                return safe

            ratio_base = difflib.SequenceMatcher(None, host_base, safe_base).ratio()
            if DiagnosticsPage.TYPOSQUAT_RATIO_LOW < ratio_base < DiagnosticsPage.TYPOSQUAT_RATIO_HIGH:
                return safe

        return None

    def _is_trusted_subdomain(self, host):
        for d in self.SYSTEM_DOMAINS:
            if host == d or host.endswith("." + d):
                return True
        for d in self.KNOWN_SAFE:
            if host.endswith("." + d):
                return True
        for d in self.KNOWN_CDN:
            if host == d or host.endswith("." + d):
                return True
        return False

    def _scan_existence(self, entries, run_id):
        total = len(entries)
        if total == 0:
            self._emitter.done.emit(T("diag_summary_exist", found=0, missing=0, errors=0))
            return

        found = missing = errors = 0
        done_count = 0
        stopped = False

        def _lookup_one(entry):
            return entry, dns_lookup_external(entry["hostname"])

        workers = min(self.EXISTENCE_MAX_WORKERS, total)
        executor = ThreadPoolExecutor(max_workers=workers)
        try:
            futures = [executor.submit(_lookup_one, e) for e in entries]
            for future in as_completed(futures):
                if self._stop_event.is_set():
                    stopped = True
                    break
                if run_id != self._run_id:
                    continue

                e, result = future.result()
                done_count += 1
                host = e["hostname"]
                self._emitter.progress.emit(done_count, total, host)

                if result is True:
                    found += 1
                    self._emitter.row_ready.emit(T("diag_exist_ok"), host, e["ip"], T("diag_exist_ok_info"), "ok")
                elif result is False:
                    missing += 1
                    self._emitter.row_ready.emit(T("diag_exist_miss"), host, e["ip"], T("diag_exist_miss_info"), "warn")
                else:
                    errors += 1
                    self._emitter.row_ready.emit(T("diag_exist_err"), host, e["ip"], T("diag_exist_err_info"), "error")
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        if run_id != self._run_id:
            return
        if stopped:
            self._emitter.done.emit(T("diag_summary_stopped", done=done_count, total=total))
        else:
            self._emitter.done.emit(T("diag_summary_exist", found=found, missing=missing, errors=errors))

    def _scan_malware(self, entries, run_id):
        total  = len(entries)
        issues = 0

        public_ip_count = Counter()
        for e in entries:
            try:
                addr = ipaddress.ip_address(e["ip"].strip())
                if not addr.is_loopback and not addr.is_private and str(addr) not in ("0.0.0.0", "::"):
                    public_ip_count[e["ip"].strip()] += 1
            except ValueError:
                pass

        for i, e in enumerate(entries):
            if run_id != self._run_id:
                return
            if self._stop_event.is_set():
                self._emitter.done.emit(T("diag_summary_stopped", done=i, total=total))
                return
            host     = e["hostname"].lower().strip()
            raw_host = e["hostname"].strip()
            ip       = e["ip"].strip()
            self._emitter.progress.emit(i + 1, total, host)

            if host in self._ignored_hosts:
                continue

            _trusted = self._is_trusted_subdomain(host)

            try:
                _addr_chk = ipaddress.ip_address(ip)
                _is_block = _addr_chk.is_loopback or str(_addr_chk) in ("0.0.0.0", "::")
            except ValueError:
                _is_block = False

            reasons = []
            risk    = None

            if host in self.SYSTEM_DOMAINS:
                try:
                    addr = ipaddress.ip_address(ip)
                    if not addr.is_loopback and str(addr) not in ("0.0.0.0", "::"):
                        reasons.append(T("diag_reason_sys_dom", ip=ip))
                        risk = "high"
                except ValueError:
                    pass

            if host in self.UPDATE_DOMAINS:
                try:
                    addr = ipaddress.ip_address(ip)
                    if addr.is_loopback or str(addr) in ("0.0.0.0", "::"):
                        reasons.append(T("diag_reason_update", host=host))
                        risk = "high"
                except ValueError:
                    pass

            try:
                addr = ipaddress.ip_address(ip)
                if not addr.is_loopback and not addr.is_private and str(addr) not in ("0.0.0.0", "::"):
                    reasons.append(T("diag_reason_public_ip", ip=ip))
                    risk = risk or "medium"
            except ValueError:
                pass

            if public_ip_count.get(ip, 0) > self.MULTI_DOMAIN_LIMIT:
                reasons.append(T("diag_reason_many_dom", n=public_ip_count[ip]))
                risk = risk or "medium"

            try:
                ipaddress.ip_address(host)
                reasons.append(T("diag_reason_ip_host"))
                risk = risk or "medium"
            except ValueError:
                pass

            if not _is_block:
                hg = [c for c in raw_host if c in self.HOMOGLYPH_CHARS]
                if hg:
                    chars_str = ", ".join("U+" + format(ord(c), "04X") for c in set(hg))
                    reasons.append(T("diag_reason_homoglyph", chars=chars_str))
                    risk = "high"

                zw = [c for c in raw_host if c in self.ZERO_WIDTH_CHARS]
                if zw:
                    chars_str = ", ".join("U+" + format(ord(c), "04X") for c in set(zw))
                    reasons.append(T("diag_reason_zero_width", chars=chars_str))
                    risk = "high"

                if not _trusted:
                    entropy = self._shannon_entropy(host)
                    label_len = len(host.split(".")[0])
                    if entropy > self.ENTROPY_THRESHOLD and label_len >= self.ENTROPY_MIN_LEN:
                        reasons.append(T("diag_reason_dga", entropy=f"{entropy:.2f}"))
                        risk = risk or "medium"

                if host not in self.SYSTEM_DOMAINS:
                    matched = self._typosquat_match(host, self.KNOWN_SAFE)
                    if matched:
                        reasons.append(T("diag_reason_typosquat", similar_to=matched))
                        risk = "high"

                parts = host.rsplit(".", 1)
                if len(parts) == 2 and parts[1] in self.SUSPICIOUS_TLDS:
                    reasons.append(T("diag_reason_bad_tld", tld=parts[1]))
                    risk = risk or "medium"

                if host.startswith("xn--") or any(
                    seg.startswith("xn--") for seg in host.split(".")
                ):
                    reasons.append(T("diag_reason_punycode"))
                    risk = "high"

                depth = len(host.split("."))
                if not _trusted and depth > self.SUBDOMAIN_DEPTH_MAX:
                    reasons.append(T("diag_reason_deep_sub", n=depth))
                    risk = risk or "medium"

                if not _trusted:
                    for pattern, sig_label in self.SUSPICIOUS_PATS:
                        m = re.search(pattern, host)
                        if not m:
                            continue
                        if sig_label == "brand_phish":
                            gd = m.groupdict()
                            brand = gd.get("brand1") or gd.get("brand2") or host
                            reasons.append(T("diag_reason_suspicious_phish", brand=brand))
                            risk = "high"
                        elif sig_label == "long_digits":
                            reasons.append(T("diag_reason_suspicious_digits"))
                            risk = risk or "medium"
                        elif sig_label == "long_label":
                            reasons.append(T("diag_reason_suspicious_label"))
                            risk = risk or "medium"
                        elif sig_label == "ip_like":
                            reasons.append(T("diag_reason_suspicious_iplike"))
                            risk = risk or "medium"
                        else:
                            reasons.append(T("diag_reason_suspicious"))
                            risk = risk or "medium"
                        break

            if reasons:
                issues += 1
                tag   = risk or "medium"
                label = T("diag_risk_high") if risk == "high" else T("diag_risk_medium")
                self._emitter.row_ready.emit(label, host, ip, "; ".join(reasons), tag)

        if run_id != self._run_id:
            return
        if issues == 0:
            self._emitter.row_ready.emit(T("diag_clean"), T("diag_clean_msg"), "", "", "ok")
        self._emitter.done.emit(T("diag_summary_malware", issues=issues, total=total))

    def _add_row(self, col0: str, host: str, ip: str, info: str, tag: str):
        _TAG_COLORS = {
            "ok":     DARK["green"],
            "warn":   "#f0c040",
            "error":  DARK["red"],
            "high":   DARK["red"],
            "medium": "#f0c040",
        }
        fg = QColor(_TAG_COLORS.get(tag, DARK["fg"]))
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, text in enumerate([col0, host, ip, info]):
            item = QTableWidgetItem(text)
            item.setForeground(fg)
            item.setData(Qt.UserRole, host)
            item.setToolTip(text)
            self.table.setItem(row, col, item)

    def _update_progress(self, done: int, total: int, current: str):
        self._prog_lbl.setText(T("diag_scanning") + current)
        self._prog_count.setText(f"{done} / {total}")

    def _scan_done(self, summary: str):
        self._prog_lbl.setText(T("diag_scan_done"))
        self._status.setText(summary)
        self._run_btn.set_accent(True)
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def _selected_hostnames(self) -> set:
        seen = set()
        for item in self.table.selectedItems():
            h = item.data(Qt.UserRole)
            if h:
                seen.add(h)
        return seen

    def _warn_hostnames(self) -> set:
        result = set()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.foreground().color() == QColor("#f0c040"):
                h = self.table.item(row, 1)
                if h:
                    result.add(h.text())
        return result

    def _remove_nonexistent(self):
        hostnames = self._warn_hostnames()
        if not hostnames:
            HOTSDialog.info(self, T("diag_no_inactive_title"), T("diag_no_inactive_msg"))
            return
        preview = "\n".join(list(hostnames)[:10])
        suffix  = T("diag_more", n=len(hostnames) - 10) if len(hostnames) > 10 else ""
        if not HOTSDialog.ask(self, T("diag_del_confirm_title"),
                              T("diag_del_inactive_msg", n=len(hostnames), preview=preview, suffix=suffix)):
            return
        if self._on_remove:
            self._on_remove(hostnames)
        self._status.setText(T("diag_status_deleted_inactive", n=len(hostnames)))
        rows_to_del = [
            row for row in range(self.table.rowCount())
            if (item := self.table.item(row, 0)) and item.foreground().color() == QColor("#f0c040")
        ]
        for row in sorted(rows_to_del, reverse=True):
            self.table.removeRow(row)

    def _remove_selected(self):
        hostnames = self._selected_hostnames()
        if not hostnames:
            HOTSDialog.info(self, T("no_sel_title"), T("diag_no_sel_msg"))
            return
        preview = "\n".join(list(hostnames)[:10])
        suffix  = T("diag_more", n=len(hostnames) - 10) if len(hostnames) > 10 else ""
        if not HOTSDialog.ask(self, T("diag_del_confirm_title"),
                              T("diag_del_sel_msg", n=len(hostnames), preview=preview, suffix=suffix)):
            return
        if self._on_remove:
            self._on_remove(hostnames)
        self._status.setText(T("diag_status_deleted_sel", n=len(hostnames)))
        rows_to_del = sorted(
            {self.table.row(item) for item in self.table.selectedItems()},
            reverse=True
        )
        for row in rows_to_del:
            self.table.removeRow(row)

    def _show_table_context_menu(self, pos):
        if self.mode != "malware":
            return
        item = self.table.itemAt(pos)
        if not item:
            return
        if not self.table.selectedItems():
            self.table.selectRow(item.row())

        if self._ctx_menu is not None:
            try:
                QApplication.instance().removeEventFilter(self._ctx_menu)
                self._ctx_menu.hide()
                self._ctx_menu.deleteLater()
            except Exception:
                pass
            self._ctx_menu = None

        rows = {self.table.row(it) for it in self.table.selectedItems()}
        n = len(rows)
        label = T("diag_ctx_ignore_one") if n <= 1 else T("diag_ctx_ignore_many", n=n)

        global_pos = self.table.viewport().mapToGlobal(pos)
        self._ctx_menu = HOTSContextMenu(self, [
            ("⊗", DARK["fg2"], label, self._ignore_selected_rows),
        ])
        self._ctx_menu.popup(global_pos)

    def _ignore_selected_rows(self):
        rows = sorted(
            {self.table.row(it) for it in self.table.selectedItems()},
            reverse=True
        )
        if not rows:
            return
        newly_ignored = set()
        for row in rows:
            risk_item = self.table.item(row, 0)
            host_item = self.table.item(row, 1)
            if not host_item:
                continue
            if risk_item and risk_item.text() == T("diag_clean"):
                continue
            host = host_item.text().strip().lower()
            if host:
                newly_ignored.add(host)

        if not newly_ignored:
            return

        self._ignored_hosts |= newly_ignored
        save_ignored_hosts(self._ignored_hosts)

        for row in rows:
            risk_item = self.table.item(row, 0)
            if risk_item and risk_item.text() == T("diag_clean"):
                continue
            self.table.removeRow(row)

        self._status.setText(T("diag_status_ignored", n=len(newly_ignored)))
