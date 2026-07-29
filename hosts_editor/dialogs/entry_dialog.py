import re
import socket

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QCheckBox, QWidget,
)
from PySide6.QtCore import Qt

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK
from ..core import is_valid_ip
from ..widgets_qt import HOTSDialog, HOTSButton, h_separator, attach_line_edit_context_menu
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
        is_ip = False
        for fam in (socket.AF_INET, socket.AF_INET6):
            try:
                socket.inet_pton(fam, candidate)
                is_ip = True
                break
            except Exception:
                pass
        if is_ip and len(parts) >= 2:
            results.append({"enabled": True, "ip": parts[0], "hostname": parts[1],
                            "comment": comment, "raw": ""})
        elif not is_ip and len(parts) == 1:
            results.append({"enabled": True, "ip": "0.0.0.0", "hostname": parts[0],
                            "comment": comment, "raw": ""})
        else:
            return []
    return results


def _dark_line_edit(placeholder="") -> QLineEdit:
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setStyleSheet(
        f"QLineEdit {{ background-color: {DARK['bg3']}; color: {DARK['fg']}; "
        f"border: 1px solid {DARK['border']}; border-radius: 4px; padding: 4px 8px; }}"
        f"QLineEdit:focus {{ border: 1px solid {DARK['accent']}; }}"
    )
    attach_line_edit_context_menu(e)
    return e


class EntryDialog(HOTSDialog):
    def __init__(self, parent=None, entry=None, existing_hostnames=None):
        title = T("entry_title_add") if entry is None else T("entry_title_edit")
        super().__init__(parent, title=title, min_width=420, min_height=320)

        self.result      = None
        self.result_list = None
        self._existing   = {h.lower() for h in (existing_hostnames or set())}
        self._is_edit    = entry is not None
        self._ip_valid   = True

        content = QWidget()
        content.setStyleSheet("background: transparent; border: none;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(20, 16, 20, 12)
        cl.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignRight)

        self._ip_edit = _dark_line_edit("0.0.0.0")
        self._ip_edit.setText(entry["ip"] if entry else "0.0.0.0")
        self._ip_hint = QLabel("")
        self._ip_hint.setStyleSheet(f"color: {DARK['red']}; font-size: 8pt; background: transparent;")
        form.addRow(_lbl(T("entry_lbl_ip")), self._ip_edit)
        form.addRow("", self._ip_hint)

        self._host_edit = _dark_line_edit()
        self._host_edit.setText(entry["hostname"] if entry else "")
        self._host_hint = QLabel("")
        self._host_hint.setStyleSheet(f"color: #f0c040; font-size: 8pt; background: transparent;")
        self._host_hint.setWordWrap(True)
        form.addRow(_lbl(T("entry_lbl_host")), self._host_edit)
        form.addRow("", self._host_hint)

        self._com_edit = _dark_line_edit()
        self._com_edit.setText(entry.get("comment", "") if entry else "")
        form.addRow(_lbl(T("entry_lbl_comment")), self._com_edit)

        self._enabled_cb = QCheckBox(T("entry_lbl_active"))
        self._enabled_cb.setChecked(entry["enabled"] if entry else True)
        self._enabled_cb.setStyleSheet(
            f"QCheckBox {{ color: {DARK['fg']}; background: transparent; spacing: 8px; }}"
            f"QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {DARK['border']}; "
            f"border-radius: 3px; background: {DARK['bg3']}; }}"
            f"QCheckBox::indicator:checked {{ background: {DARK['accent']}; border: 1px solid {DARK['accent']}; }}"
        )
        form.addRow("", self._enabled_cb)

        cl.addLayout(form)
        cl.addWidget(h_separator())

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = HOTSButton(FIF.SAVE, "#ffffff", T("entry_btn_save"), accent=True)
        save_btn.fit_to_content()
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        cancel_btn = HOTSButton(FIF.CLOSE, DARK["red"], T("entry_btn_cancel"))
        cancel_btn.fit_to_content()
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)

        self.body_layout.addWidget(content)

        self._ip_edit.textChanged.connect(self._validate_ip)
        self._host_edit.textChanged.connect(self._on_host_change)
        self._validate_ip()

        self.adjustSize()
        self.center_on_parent()

    def _validate_ip(self):
        ip = self._ip_edit.text().strip()
        if not ip:
            self._ip_hint.setText("")
            self._ip_valid = True
            return
        valid = is_valid_ip(ip)
        self._ip_valid = valid
        if valid:
            self._ip_hint.setText("")
            self._ip_edit.setStyleSheet(
                f"QLineEdit {{ background-color: {DARK['bg3']}; color: {DARK['fg']}; "
                f"border: 1px solid {DARK['border']}; border-radius: 4px; padding: 4px 8px; }}"
                f"QLineEdit:focus {{ border: 1px solid {DARK['accent']}; }}"
            )
        else:
            self._ip_hint.setText(T("entry_hint_bad_ip"))
            self._ip_edit.setStyleSheet(
                f"QLineEdit {{ background-color: {DARK['bg3']}; color: {DARK['fg']}; "
                f"border: 1px solid {DARK['red']}; border-radius: 4px; padding: 4px 8px; }}"
            )

    def _on_host_change(self):
        raw = self._host_edit.text()
        if "\n" in raw:
            self._host_hint.setText(T("entry_hint_bulk"))
            return
        needs = (raw.startswith("http://") or raw.startswith("https://")
                 or raw.endswith("/") or raw.endswith("\\"))
        if needs:
            self._host_hint.setText(T("entry_hint_sanitize"))
            return
        if not self._is_edit:
            h = self._sanitize_hostname(raw)
            if h and h.lower() in self._existing:
                self._host_hint.setStyleSheet(f"color: {DARK['red']}; font-size: 8pt; background: transparent;")
                self._host_hint.setText(T("entry_hint_dup"))
                return
        self._host_hint.setText("")

    @staticmethod
    def _sanitize_hostname(raw: str) -> str:
        h = raw.strip()
        h = re.sub(r"^https?://", "", h)
        h = h.split("/")[0]
        h = h.split(":")[0] if not h.startswith("[") else h
        if "@" in h:
            h = h.split("@")[-1]
        return h.strip().lower()

    def _save(self):
        ip       = self._ip_edit.text().strip()
        raw_host = self._host_edit.text()

        if "\n" in raw_host:
            bulk = _parse_bulk(raw_host)
            if not bulk:
                HOTSDialog.error(self, T("entry_err_title"), T("entry_err_bulk_fmt"))
                return
            new_entries = []
            skipped     = []
            for e in bulk:
                if e["hostname"].lower() in self._existing:
                    skipped.append(e["hostname"])
                else:
                    new_entries.append(e)
                    self._existing.add(e["hostname"].lower())
            if skipped and not new_entries:
                HOTSDialog.info(self, T("entry_skip_title"),
                                T("entry_skip_msg", n=len(skipped), list="\n".join(skipped[:10])))
                return
            self.result_list = new_entries
            self.accept()
            return

        host = self._sanitize_hostname(raw_host)
        if not ip or not host:
            HOTSDialog.error(self, T("entry_err_title"), T("entry_err_required"))
            return
        if not self._ip_valid:
            if not HOTSDialog.ask(self, T("entry_bad_ip_title"), T("entry_bad_ip_ask", ip=ip)):
                return
        if not self._is_edit and host.lower() in self._existing:
            if not HOTSDialog.ask(self, T("entry_dup_title"), T("entry_dup_ask", host=host)):
                return

        self.result = {
            "enabled":  self._enabled_cb.isChecked(),
            "ip":       ip,
            "hostname": host,
            "comment":  self._com_edit.text().strip(),
            "raw":      "",
        }
        self.accept()


def _lbl(text: str) -> QLabel:
    l = QLabel(text + ":")
    l.setStyleSheet(f"color: {DARK['fg2']}; background: transparent;")
    return l
