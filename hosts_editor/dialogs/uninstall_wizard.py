from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from ..icons import FIF
from ..constants import DARK
from ..widgets_qt import HOTSDialog, HOTSButton, HOTSSwitch, h_separator
from ..i18n import T


class _OptionCard(QFrame):
    def __init__(self, title: str, desc: str, default: bool, enabled: bool, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame {{ background-color: {DARK['btn_bg']}; border: 1px solid {DARK['border']}; "
            f"border-radius: 8px; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(3)

        self.switch = HOTSSwitch(title, font_pt=9.5, spacing=10)
        self.switch.setChecked(bool(default and enabled))
        self.switch.setEnabled(enabled)
        lay.addWidget(self.switch)

        desc_lbl = QLabel(desc)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(
            f"color: {DARK['fg2']}; font-size: 8.3pt; background: transparent; "
            f"border: none; padding-left: 44px;"
        )
        lay.addWidget(desc_lbl)

    def is_checked(self) -> bool:
        return self.switch.isChecked()


class UninstallWizardDialog(HOTSDialog):
    def __init__(self, parent=None, counts: dict | None = None):
        super().__init__(parent, T("uninst_wizard_title"), min_width=460, min_height=200)
        self._counts = counts or {}
        self.choices = None
        self._build()
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

        btn_row.addStretch()

        cl.addLayout(btn_row)

    def reject(self):
        # No Cancel button: uninstall proceeds regardless. The title-bar close
        # button calls reject(), so route it to _confirm() to keep the user's
        # current choices instead of silently discarding them.
        self._confirm()

    def _confirm(self):
        self.choices = {
            "remove_hosts_entries": self._card_hosts.is_checked(),
            "restore_privacy": self._card_privacy.is_checked(),
            "delete_data": self._card_data.is_checked(),
            "delete_custom_domains": self._card_domains.is_checked(),
            "delete_hosts_backups": self._card_backups.is_checked(),
        }
        self.accept()
