import difflib

from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget, QPlainTextEdit
from PySide6.QtGui import QTextCharFormat, QColor, QFont, QSyntaxHighlighter

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK
from ..widgets_qt import HOTSDialog, HOTSButton, h_separator
from ..i18n import T


class _DiffHighlighter(QSyntaxHighlighter):
    def __init__(self, doc, has_diff: bool = True):
        super().__init__(doc)
        self._has_diff = has_diff
        self._add = QTextCharFormat()
        self._add.setForeground(QColor(DARK["diff_add_fg"]))
        self._add.setBackground(QColor(DARK["diff_add"]))

        self._del = QTextCharFormat()
        self._del.setForeground(QColor(DARK["diff_del_fg"]))
        self._del.setBackground(QColor(DARK["diff_del"]))

        self._hdr = QTextCharFormat()
        self._hdr.setForeground(QColor(DARK["fg2"]))
        self._hdr.setBackground(QColor(DARK["bg3"]))

        self._ctx = QTextCharFormat()
        self._ctx.setForeground(QColor(DARK["fg2"]))

    def highlightBlock(self, text: str):
        block_no = self.currentBlock().blockNumber()
        if (self._has_diff and block_no < 2) or text.startswith("@@"):
            self.setFormat(0, len(text), self._hdr)
        elif text.startswith("+"):
            self.setFormat(0, len(text), self._add)
        elif text.startswith("-"):
            self.setFormat(0, len(text), self._del)
        elif text.startswith(" "):
            self.setFormat(0, len(text), self._ctx)


class DiffDialog(HOTSDialog):
    def __init__(self, parent, old_text: str, new_text: str):
        super().__init__(parent, title=T("diff_title"), min_width=720, min_height=480)
        self.confirmed = False

        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        self._diff_lines = list(difflib.unified_diff(
            old_lines, new_lines, fromfile="current_hosts", tofile="new_hosts", lineterm=""
        ))

        self._build()
        self.center_on_parent()

    def _build(self):
        cl = self.body_layout
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        hdr = QWidget()
        hdr.setStyleSheet(f"background: {DARK['panel_bg']};")
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(16, 10, 16, 10)

        content_lines = self._diff_lines[2:] if self._diff_lines else []
        adds = sum(1 for l in content_lines if l.startswith("+"))
        dels = sum(1 for l in content_lines if l.startswith("-"))
        stat_txt = T("diff_stat", adds=adds, dels=dels)

        stat = QLabel(stat_txt)
        stat.setStyleSheet(f"color: {DARK['fg2']}; background: transparent; margin-right: 8px;")
        hdr_lay.addWidget(stat)

        save_label = T("diff_save_anyway") if adds + dels == 0 else T("diff_save")
        save_btn = HOTSButton(FIF.SAVE, "#ffffff", save_label, accent=True)
        save_btn.clicked.connect(self._confirm)
        hdr_lay.addWidget(save_btn)

        cancel_btn = HOTSButton(FIF.CLOSE, DARK["red"], T("diff_cancel"))
        cancel_btn.clicked.connect(self.reject)
        hdr_lay.addWidget(cancel_btn)

        common_w = max(
            save_btn.layout().sizeHint().width(),
            cancel_btn.layout().sizeHint().width(),
        ) + 8
        save_btn.setFixedWidth(common_w)
        cancel_btn.setFixedWidth(common_w)

        cl.addWidget(hdr)
        cl.addWidget(h_separator())

        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setFont(QFont("Cascadia Code", 9))
        self._text.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._text.setStyleSheet(
            f"QPlainTextEdit {{ background-color: {DARK['table_bg']}; color: {DARK['fg']}; "
            f"border: none; padding: 10px; }}"
        )
        self._hl = _DiffHighlighter(self._text.document(), has_diff=bool(self._diff_lines))

        if not self._diff_lines:
            self._text.setPlainText(T("diff_no_changes_body"))
        else:
            self._text.setPlainText("\n".join(self._diff_lines))

        cl.addWidget(self._text, 1)

    def _confirm(self):
        self.confirmed = True
        self.accept()
