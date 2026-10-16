from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget
from PySide6.QtCore import Qt, QTimer, Signal

from ..icons import FIF
from ..constants import DARK
from ..widgets_qt import HOTSDialog, HOTSButton, HOTSSwitch, h_separator
from ..i18n import T


_CHEVRON_CLOSED = FIF.CHEVRON_RIGHT_MED
_CHEVRON_OPEN = FIF.CHEVRON_DOWN_MED


class _OptionCard(QFrame):
    expanded_changed = Signal()

    def __init__(self, title: str, desc: str, default: bool, enabled: bool, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame {{ background-color: {DARK['btn_bg']}; border: 1px solid {DARK['border']}; "
            f"border-radius: 8px; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 8, 14, 8)
        lay.setSpacing(3)

        head = QHBoxLayout()
        head.setSpacing(6)
        self.switch = HOTSSwitch(title, font_pt=9.5, spacing=10)
        self.switch.setChecked(bool(default and enabled))
        self.switch.setEnabled(enabled)
        head.addWidget(self.switch, 1)

        self._toggle_btn = HOTSButton(
            _CHEVRON_CLOSED, DARK["fg2"], "", accent=False, glyph_color=DARK["accent"],
        )
        self._toggle_btn.setFixedSize(38, 28)
        self._toggle_btn.clicked.connect(self._toggle_desc)
        head.addWidget(self._toggle_btn)
        lay.addLayout(head)

        self._desc_lbl = QLabel(desc)
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setStyleSheet(
            f"color: {DARK['fg2']}; font-size: 8.3pt; background: transparent; "
            f"border: none; padding-left: 44px;"
        )
        self._desc_lbl.setVisible(False)
        lay.addWidget(self._desc_lbl)

    def _toggle_desc(self):
        show = not self._desc_lbl.isVisible()
        self._desc_lbl.setVisible(show)
        self._toggle_btn.set_icon(
            _CHEVRON_OPEN if show else _CHEVRON_CLOSED,
            color=DARK["fg2"], glyph_color=DARK["accent"],
        )
        self.expanded_changed.emit()

    def is_checked(self) -> bool:
        return self.switch.isChecked()


class UninstallWizardDialog(HOTSDialog):
    def __init__(self, parent=None, counts: dict | None = None):
        super().__init__(parent, T("uninst_wizard_title"), min_width=460, min_height=200)
        self._counts = counts or {}
        self.choices = None
        self._build()
        for card in (self._card_hosts, self._card_privacy, self._card_data,
                     self._card_domains, self._card_backups):
            card.expanded_changed.connect(lambda: QTimer.singleShot(0, self._refit))
        self.adjustSize()
        self.center_on_parent()

    def _build(self):
        cl = self.body_layout
        cl.setContentsMargins(28, 22, 28, 20)
        cl.setSpacing(10)

        heading = QLabel(T("uninst_wizard_heading"))
        heading.setStyleSheet(
            f"color: {DARK['fg']}; font-size: 11pt; font-weight: 600; "
            f"background: transparent; border: none;"
        )
        cl.addWidget(heading)

        intro = QLabel(T("uninst_wizard_intro"))
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent; border: none;")
        cl.addWidget(intro)

        cl.addSpacing(6)
        cl.addWidget(h_separator())
        cl.addSpacing(6)

        n_antispy = self._counts.get("antispy", 0)
        n_backups = self._counts.get("backups", 0)

        self._card_hosts = _OptionCard(
            T("uninst_opt_hosts_title"), T("uninst_opt_hosts_desc"),
            default=True, enabled=True,
        )
        cl.addWidget(self._card_hosts)

        self._card_privacy = _OptionCard(
            T("uninst_opt_antispy_title"),
            T("uninst_opt_antispy_desc_n", n=n_antispy) if n_antispy else T("uninst_opt_antispy_desc_none"),
            default=False, enabled=n_antispy > 0,
        )
        cl.addWidget(self._card_privacy)

        self._card_data = _OptionCard(
            T("uninst_opt_data_title"), T("uninst_opt_data_desc"),
            default=True, enabled=True,
        )
        cl.addWidget(self._card_data)

        has_domains = bool(self._counts.get("custom_domains"))
        self._card_domains = _OptionCard(
            T("uninst_opt_domains_title"),
            T("uninst_opt_domains_desc") if has_domains else T("uninst_opt_domains_desc_none"),
            default=False, enabled=has_domains,
        )
        cl.addWidget(self._card_domains)

        self._card_backups = _OptionCard(
            T("uninst_opt_backups_title"),
            T("uninst_opt_backups_desc_n", n=n_backups) if n_backups else T("uninst_opt_backups_desc_none"),
            default=n_backups > 0, enabled=n_backups > 0,
        )
        cl.addWidget(self._card_backups)

        cl.addSpacing(2)
        footer = QLabel(T("uninst_wizard_footer"))
        footer.setWordWrap(True)
        footer.setStyleSheet(f"color: {DARK['muted_fg']}; font-size: 8pt; background: transparent; border: none;")
        cl.addWidget(footer)

        cl.addStretch()
        cl.addWidget(h_separator())

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 12, 0, 0)
        btn_row.addStretch()

        confirm_btn = HOTSButton(FIF.DELETE, DARK['red'], T("uninst_btn_confirm"))
        confirm_btn.fit_to_content()
        confirm_btn.clicked.connect(self._confirm)
        btn_row.addWidget(confirm_btn)

        cancel_btn = HOTSButton(FIF.CLOSE, DARK['fg'], T("uninst_btn_cancel"))
        cancel_btn.fit_to_content()
        cancel_btn.clicked.connect(self.reject)
        btn_row.addSpacing(10)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch()

        cl.addLayout(btn_row)

    def _refit(self):
        lay = self.layout()
        for ch in self.findChildren(QWidget):
            ch.updateGeometry()
        lay.invalidate()
        lay.activate()
        self.resize(self.width(), max(lay.totalHeightForWidth(self.width()), self.minimumHeight()))
        scr = self.screen()
        if scr is not None:
            avail = scr.availableGeometry()
            self.move(self.x(), max(avail.top(), min(self.y(), avail.bottom() - self.height())))

    def _confirm(self):
        self.choices = {
            "remove_hosts_entries": self._card_hosts.is_checked(),
            "restore_privacy": self._card_privacy.is_checked(),
            "delete_data": self._card_data.is_checked(),
            "delete_custom_domains": self._card_domains.is_checked(),
            "delete_hosts_backups": self._card_backups.is_checked(),
        }
        self.accept()
