import difflib

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPlainTextEdit
from PySide6.QtGui import QTextCharFormat, QColor, QFont, QSyntaxHighlighter
from PySide6.QtCore import Qt

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK, accent_rgba
from ..widgets_qt import HOTSDialog, HOTSButton, HOTSContextMenu
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
        self.discarded = False

        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        self._diff_lines = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=T("diff_file_current"), tofile=T("diff_file_new"), lineterm=""
        ))

        self._build()
        self.center_on_parent()

    def _card_style(self) -> str:
        return (f"background: {DARK['panel_bg']}; "
                f"border: 1px solid {DARK['border_faint']}; border-radius: 6px;")

    def _build(self):
        cl = self.body_layout
        cl.setContentsMargins(12, 10, 12, 10)
        cl.setSpacing(6)

        # --- karta nagłówka: statystyki + przyciski Zapisz/Pomiń/Anuluj ---
        hdr = QWidget()
        hdr.setStyleSheet(self._card_style())
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(16, 14, 16, 14)

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

        skip_btn = HOTSButton(FIF.RETURN, DARK["fg2"], T("diff_skip"))
        skip_btn.clicked.connect(self._skip)
        hdr_lay.addWidget(skip_btn)

        cancel_btn = HOTSButton(FIF.CLOSE, DARK["red"], T("diff_cancel"))
        cancel_btn.clicked.connect(self.reject)
        hdr_lay.addWidget(cancel_btn)

        common_w = max(
            save_btn.layout().sizeHint().width(),
            skip_btn.layout().sizeHint().width(),
            cancel_btn.layout().sizeHint().width(),
        ) + 8
        save_btn.setFixedWidth(common_w)
        skip_btn.setFixedWidth(common_w)
        cancel_btn.setFixedWidth(common_w)

        cl.addWidget(hdr)

        if self._diff_lines:
            legend_w = QWidget()
            legend_w.setStyleSheet(self._card_style())
            legend_lay = QHBoxLayout(legend_w)
            legend_lay.setContentsMargins(16, 9, 16, 9)
            legend = QLabel(T("diff_legend"))
            legend.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent; border: none;")
            legend_lay.addWidget(legend)
            legend_lay.addStretch()
            cl.addWidget(legend_w)

        text_card = QWidget()
        text_card.setStyleSheet(self._card_style())
        text_card_lay = QVBoxLayout(text_card)
        text_card_lay.setContentsMargins(6, 6, 6, 6)
        text_card_lay.setSpacing(0)

        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setFont(QFont("Cascadia Code", 9))
        self._text.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._text.setStyleSheet(
            f"QPlainTextEdit {{ background-color: {DARK['table_bg']}; color: {DARK['fg']}; "
            f"border: none; border-radius: 4px; padding: 10px; }}"
            # QPlainTextEdit jest QAbstractScrollArea, więc jak tylko dostaje
            # własny setStyleSheet(), przestaje niezawodnie dziedziczyć
            # globalny styl QScrollBar z widgets_qt.py (patrz identyczny
            # komentarz/fix przy tabeli w diagnostics_page.py) — dublujemy
            # te same reguły lokalnie, żeby suwak wyglądał i zachowywał się
            # identycznie jak na pozostałych kartach.
            "QScrollBar:vertical {"
            "    background: transparent;"
            "    width: 14px;"
            "    border: none;"
            "    margin: 2px 2px 2px 0;"
            "}"
            "QScrollBar:horizontal {"
            "    background: transparent;"
            "    height: 14px;"
            "    border: none;"
            "    margin: 0 2px 2px 2px;"
            "}"
            f"QScrollBar::handle:vertical {{"
            f"    background: {DARK['scrollbar_handle']};"
            f"    border-radius: 3px;"
            f"    min-height: 32px;"
            f"    margin: 0 5px;"
            f"}}"
            f"QScrollBar::handle:horizontal {{"
            f"    background: {DARK['scrollbar_handle']};"
            f"    border-radius: 3px;"
            f"    min-width: 32px;"
            f"    margin: 5px 0;"
            f"}}"
            f"QScrollBar::handle:vertical:hover {{"
            f"    background: {accent_rgba(0.70)};"
            f"    border-radius: 4px;"
            f"    margin: 0 2px;"
            f"}}"
            f"QScrollBar::handle:horizontal:hover {{"
            f"    background: {accent_rgba(0.70)};"
            f"    border-radius: 4px;"
            f"    margin: 2px 0;"
            f"}}"
            f"QScrollBar::handle:vertical:pressed,"
            f"QScrollBar::handle:horizontal:pressed {{"
            f"    background: {accent_rgba(0.95)};"
            f"}}"
            f"QScrollBar:vertical:hover,"
            f"QScrollBar:horizontal:hover {{"
            f"    background: {DARK['scrollbar_track_hover']};"
            f"}}"
            "QScrollBar::add-line, QScrollBar::sub-line {"
            "    width: 0; height: 0; background: none; border: none;"
            "}"
            "QScrollBar::add-page, QScrollBar::sub-page {"
            "    background: none;"
            "}"
        )
        self._hl = _DiffHighlighter(self._text.document(), has_diff=bool(self._diff_lines))

        if not self._diff_lines:
            self._text.setPlainText(T("diff_no_changes_body"))
        else:
            self._text.setPlainText("\n".join(self._diff_lines))

        self._text.setContextMenuPolicy(Qt.CustomContextMenu)
        self._text.customContextMenuRequested.connect(self._show_context_menu)

        text_card_lay.addWidget(self._text)
        cl.addWidget(text_card, 1)

    def _show_context_menu(self, pos):
        gpos = self._text.mapToGlobal(pos)
        items = [
            ("⧉", DARK['accent'], T("ctx_copy"),        self._text.copy),
            ("▤", DARK['accent'], T("ctx_select_all"), self._text.selectAll),
        ]
        menu = HOTSContextMenu(self._text, items)
        self._text._hots_ctx_menu = menu
        menu.popup(gpos)

    def _confirm(self):
        self.confirmed = True
        self.accept()

    def _skip(self):
        self.discarded = True
        self.reject()
