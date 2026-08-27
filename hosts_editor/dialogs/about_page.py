import os
import webbrowser

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap

from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import IconWidget

from ..constants import DARK
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton, colored_svg_icon
from ..i18n import T
from ..bg_tasks import register_qthread, is_shutting_down

from ._about_shared import APP_VERSION, _UpdateCheckWorker, _parse_version, _safe_t


class AboutPage(HOTSPage):
    def __init__(self, parent=None):
        super().__init__("aboutInterface", FIF.INFO,
                          _safe_t("about_title", "About"), parent)
        self._build()

    def _find_asset(self, name: str) -> str:
        from ..resource_utils import resource_path
        p = resource_path(name)
        return p if os.path.exists(p) else ""

    def _build(self):
        cl = self.content_layout

        top = QWidget()
        top.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        top_lay = QHBoxLayout(top)
        top_lay.setContentsMargins(20, 18, 20, 18)
        top_lay.setSpacing(16)

        logo_lbl = QLabel()
        logo_lbl.setStyleSheet("background: transparent; border: none;")
        logo_path = self._find_asset("logo.png")
        if logo_path:
            pix = QPixmap(logo_path)
            if not pix.isNull():
                scaled = pix.scaledToHeight(126, Qt.SmoothTransformation)
                logo_lbl.setPixmap(scaled)
                logo_lbl.setFixedSize(scaled.size())
        top_lay.addWidget(logo_lbl, 0, Qt.AlignBottom)

        col = QWidget()
        col.setStyleSheet("background: transparent; border: none;")
        col_lay = QVBoxLayout(col)
        col_lay.setContentsMargins(0, 0, 0, 0)
        col_lay.setSpacing(4)

        sub = QLabel(T("about_subtitle"))
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {DARK['fg2']}; font-size: 11pt; background: transparent; border: none;")
        col_lay.addWidget(sub)

        ver = QLabel(T("about_version"))
        ver.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent; border: none;")
        col_lay.addWidget(ver)

        top_lay.addWidget(col, 1, Qt.AlignBottom)

        self._website_btn = HOTSButton(FIF.GLOBE, "#60c8ff", T("about_website_btn"))
        self._website_btn.fit_to_content()
        self._website_btn.clicked.connect(lambda: webbrowser.open("https://hotstools.com"))
        top_lay.addWidget(self._website_btn, 0, Qt.AlignVCenter)

        self._update_btn = HOTSButton(FIF.SYNC, "#60c8ff", T("about_check_update"))
        self._update_btn.fit_to_content()
        self._update_btn.clicked.connect(self._check_for_updates)
        top_lay.addWidget(self._update_btn, 0, Qt.AlignVCenter)

        cl.addWidget(top)
        cl.addSpacing(6)

        desc_w = QWidget()
        desc_w.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        desc_lay = QVBoxLayout(desc_w)
        desc_lay.setContentsMargins(20, 14, 20, 14)

        desc = QLabel(T("about_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg']}; font-size: 9pt; background: transparent; border: none;")
        desc_lay.addWidget(desc)
        cl.addWidget(desc_w)
        cl.addSpacing(6)

        feat_w = QWidget()
        feat_w.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        feat_lay = QGridLayout(feat_w)
        feat_lay.setContentsMargins(20, 14, 20, 14)
        feat_lay.setSpacing(4)

        features = [
            (FIF.PEOPLE,        T("about_feat_parental")),
            (FIF.HIDE,          T("about_feat_antispy")),
            (FIF.WIFI,          T("about_feat_diag")),
            (FIF.GLOBE,         T("about_feat_dns")),
            (FIF.CODE,          T("about_feat_raw")),
            (FIF.HISTORY,       T("about_feat_backup")),
            (FIF.CLOUD_DOWNLOAD, T("about_feat_export")),
            (FIF.FINGERPRINT,   T("about_feat_password")),
            (FIF.PALETTE,       T("about_feat_theme")),
            (FIF.LANGUAGE,      T("about_feat_lang")),
            (FIF.CERTIFICATE,   T("about_feat_hostslock")),
            (FIF.APPLICATION,   T("about_feat_appblock")),
            (FIF.CLOUD if hasattr(FIF, "CLOUD") else FIF.GLOBE, T("about_feat_doh")),
            (FIF.VPN if hasattr(FIF, "VPN") else FIF.GLOBE,     T("about_feat_vpn")),
            (FIF.EDIT,          T("about_feat_customdomains")),
            (FIF.SYNC if hasattr(FIF, "SYNC") else FIF.APPLICATION, T("about_feat_rstruilock")),
        ]
        for i, (icon, label) in enumerate(features):
            row, col = divmod(i, 2)
            cell = QWidget()
            cell.setStyleSheet("background: transparent; border: none;")
            cell_lay = QHBoxLayout(cell)
            cell_lay.setContentsMargins(0, 2, 0, 2)
            cell_lay.setSpacing(6)

            ico = IconWidget(icon)
            ico.setFixedSize(15, 15)
            ico.setIcon(colored_svg_icon(icon, QColor(DARK["accent"]), sizes=(15,)))
            ico.setAttribute(Qt.WA_TransparentForMouseEvents)
            cell_lay.addWidget(ico, 0, Qt.AlignVCenter)

            txt = QLabel(label)
            txt.setStyleSheet(f"color: {DARK['fg']}; font-size: 9pt; background: transparent; border: none;")
            cell_lay.addWidget(txt)
            cell_lay.addStretch()
            feat_lay.addWidget(cell, row, col)

        cl.addWidget(feat_w)
        cl.addSpacing(6)

        footer = QWidget()
        footer.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(16, 10, 12, 10)

        author = QLabel(T("about_footer"))
        author.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        footer_lay.addWidget(author)
        footer_lay.addStretch()
        cl.addWidget(footer)

    def _check_for_updates(self):
        if getattr(self, "_update_worker", None) is not None and self._update_worker.isRunning():
            return

        self._update_btn.setEnabled(False)
        self._update_btn.set_label(T("about_checking_update"))
        self._update_btn.fit_to_content()

        self._update_worker = _UpdateCheckWorker(self)
        self._update_worker.finished_ok.connect(self._on_update_check_ok)
        self._update_worker.failed.connect(self._on_update_check_failed)
        self._update_worker.finished.connect(self._reset_update_button)
        self._update_worker.finished.connect(self._update_worker.deleteLater)
        register_qthread(self._update_worker)
        self._update_worker.start()

    def _reset_update_button(self):
        if is_shutting_down():
            return
        self._update_worker = None
        self._update_btn.setEnabled(True)
        self._update_btn.set_label(T("about_check_update"))
        self._update_btn.fit_to_content()

    def _on_update_check_ok(self, latest_tag: str, release_url: str):
        latest_v = _parse_version(latest_tag)
        current_v = _parse_version(APP_VERSION)

        if latest_v > current_v:
            open_it = HOTSDialog.ask(
                self,
                T("about_update_available_title"),
                T("about_update_available_msg").format(version=latest_tag, current=APP_VERSION),
            )
            if open_it:
                webbrowser.open(release_url)
        else:
            HOTSDialog.info(
                self,
                T("about_update_uptodate_title"),
                T("about_update_uptodate_msg").format(current=APP_VERSION),
            )

    def _on_update_check_failed(self, error: str):
        HOTSDialog.error(
            self,
            T("about_update_error_title"),
            T("about_update_error_msg").format(error=error),
        )
