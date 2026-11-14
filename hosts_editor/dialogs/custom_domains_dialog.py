import ipaddress
import os
import re
import tempfile

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTextEdit
from PySide6.QtGui import QTextBlockFormat, QTextCursor

from ..icons import FIF
from ..constants import DARK
from ..widgets_qt import HOTSDialog, HOTSButton, h_separator, attach_text_edit_context_menu, SmoothWheel
from ..i18n import T

_DOMAIN_RE = re.compile(
    r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))+$"
)


def _is_ip(token: str) -> bool:
    try:
        ipaddress.ip_address(token)
    except ValueError:
        return False
    return True


def _split_hosts_line(line: str):
    parts = line.split()
    if len(parts) > 1 and _is_ip(parts[0]):
        return parts[1:]
    return [line]


def _clean_candidate(item: str) -> str:
    candidate = re.sub(r"^https?://", "", item, flags=re.IGNORECASE)
    return candidate.split("/")[0].split(":")[0].strip().lower()


def _is_valid_host(candidate: str) -> bool:
    return (
        len(candidate) <= 253
        and bool(_DOMAIN_RE.match(candidate))
        and not candidate.rsplit(".", 1)[-1].isdigit()
    )


def _normalize_and_validate(raw_text: str):
    valid = []
    invalid = []
    seen = set()
    for line in raw_text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        found = [_clean_candidate(item) for item in _split_hosts_line(line)]
        if not all(_is_valid_host(c) for c in found):
            invalid.append(line)
            continue
        for candidate in found:
            if candidate not in seen:
                seen.add(candidate)
                valid.append(candidate)
    return valid, invalid


class CustomDomainsDialog(HOTSDialog):

    def __init__(self, parent, list_path: str):
        super().__init__(parent, title=T("par_custom_dialog_title"), min_width=460, min_height=420)
        self._path = list_path

        content = QWidget()
        content.setStyleSheet("background: transparent; border: none;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(20, 16, 20, 12)
        cl.setSpacing(10)

        hint = QLabel(T("par_custom_dialog_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        cl.addWidget(hint)

        self._edit = QTextEdit()
        SmoothWheel(self._edit)
        self._edit.setPlaceholderText(T("par_custom_placeholder"))
        self._edit.setAcceptRichText(False)
        self._edit.setStyleSheet(
            f"QTextEdit {{ background-color: {DARK['bg3']}; color: {DARK['fg']}; "
            f"border: 1px solid {DARK['border']}; border-radius: 4px; padding: 6px 8px; }}"
            f"QTextEdit:focus {{ border: 1px solid {DARK['accent']}; }}"
        )
        self._edit.setText(self._load_existing())
        self._apply_line_spacing()
        attach_text_edit_context_menu(self._edit)
        cl.addWidget(self._edit, 1)

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        cl.addWidget(self._count_lbl)
        self._edit.textChanged.connect(self._refresh_count)
        self._refresh_count()

        cl.addWidget(h_separator())

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = HOTSButton(FIF.SAVE, "#ffffff", T("entry_btn_save"), accent=True)
        save_btn.fit_to_content(min_width=100)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        cancel_btn = HOTSButton(FIF.CLOSE, DARK["red"], T("entry_btn_cancel"))
        cancel_btn.fit_to_content(min_width=100)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        cl.addLayout(btn_row)

        self.body_layout.addWidget(content)

        self.adjustSize()
        self.center_on_parent()

    def _load_existing(self) -> str:
        if not self._path or not os.path.exists(self._path):
            return ""
        try:
            with open(self._path, "r", encoding="utf-8", errors="replace") as f:
                lines = [
                    ln.strip() for ln in f
                    if ln.strip() and not ln.strip().startswith("#")
                ]
            return "\n".join(sorted(lines))
        except Exception:
            return ""

    def _apply_line_spacing(self):
        fmt = QTextBlockFormat()
        fmt.setLineHeight(150, 1)
        cursor = self._edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(fmt)

    def _refresh_count(self):
        valid, _invalid = _normalize_and_validate(self._edit.toPlainText())
        self._count_lbl.setText(T("par_custom_count", n=len(valid)))

    def _save(self):
        valid, invalid = _normalize_and_validate(self._edit.toPlainText())

        if invalid:
            HOTSDialog.error(
                self, T("par_custom_err_title"),
                T("par_custom_err_msg", list="\n".join(invalid[:15])),
            )
            return

        try:
            if self._path:
                os.makedirs(os.path.dirname(self._path), exist_ok=True)
                target_dir = os.path.dirname(self._path)
                fd, tmp_path = tempfile.mkstemp(dir=target_dir, prefix=".custom_domains_", suffix=".tmp")
                try:
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        for domain in sorted(valid):
                            f.write(domain + "\n")
                        f.flush()
                        os.fsync(f.fileno())
                    os.replace(tmp_path, self._path)
                except Exception:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                    raise
        except OSError as exc:
            HOTSDialog.error(self, T("par_custom_err_title"), str(exc))
            return

        HOTSDialog.info(self, T("par_custom_saved_title"), T("par_custom_saved_msg", n=len(valid)))
        self.accept()
