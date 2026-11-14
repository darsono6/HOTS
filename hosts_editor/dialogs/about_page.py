import ctypes
import os
import platform
import re
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout, QSizePolicy, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPixmap

from ..icons import FIF
from ..ui_parts import IconWidget
from ..constants import DARK
from ..widgets_qt import HOTSPage, HOTSButton, colored_svg_icon
from ..i18n import T, current_lang

from ._about_shared import APP_VERSION, _safe_t


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
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 8px;"
        )
        top.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        top_outer_lay = QVBoxLayout(top)
        top_outer_lay.setContentsMargins(20, 17, 20, 14)
        top_outer_lay.setSpacing(8)

        top_lay = QHBoxLayout()
        top_lay.setSpacing(16)
        top_outer_lay.addLayout(top_lay)

        logo_lbl = QLabel()
        logo_lbl.setStyleSheet("background: transparent; border: none;")
        logo_path = self._find_asset("graphic/logo.png")
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

        ver = QLabel(T("about_version", v=APP_VERSION))
        ver.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent; border: none;")
        col_lay.addWidget(ver)

        top_lay.addWidget(col, 1, Qt.AlignBottom)

        self._website_btn = HOTSButton(FIF.GLOBE, "#60c8ff", T("about_website_btn"))
        self._website_btn.fit_to_content()
        self._website_btn.clicked.connect(lambda: webbrowser.open("https://hotstools.com"))

        self._diag_btn = HOTSButton(FIF.COPY if hasattr(FIF, "COPY") else FIF.DOCUMENT, "#60c8ff", T("about_diag_btn"))
        self._diag_btn.fit_to_content()
        self._diag_btn.clicked.connect(self._copy_diagnostics)
        self._website_btn.set_label(T("about_diag_copied"))
        self._website_btn.fit_to_content()
        copied_w = self._website_btn.width()
        self._website_btn.set_label(T("about_website_btn"))
        self._website_btn.fit_to_content()
        btn_w = max(self._website_btn.width(), self._diag_btn.width(), copied_w)
        self._website_btn.setFixedWidth(btn_w)
        self._diag_btn.setFixedWidth(btn_w)
        self._website_btn.layout().insertStretch(0)
        self._diag_btn.layout().insertStretch(0)

        btn_col = QVBoxLayout()
        btn_col.setContentsMargins(0, 0, 0, 0)
        btn_col.setSpacing(6)
        btn_col.addWidget(self._website_btn)
        btn_col.addWidget(self._diag_btn)
        top_lay.addLayout(btn_col, 0)

        cl.addWidget(top)
        cl.addSpacing(6)

        desc_w = QWidget()
        desc_w.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 8px;"
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
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 8px;"
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
            (FIF.CONNECT,       T("about_feat_netblock")),
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
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 8px;"
        )
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(16, 10, 12, 10)

        author = QLabel(T("about_footer"))
        author.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        footer_lay.addWidget(author)
        footer_lay.addStretch()

        license_btn = HOTSButton(FIF.DOCUMENT, "#60c8ff", T("about_license_btn"))
        license_btn.fit_to_content()
        license_btn.clicked.connect(lambda: self._open_notice(
            "LICENSE.txt", "https://www.gnu.org/licenses/gpl-3.0.html"))
        footer_lay.addWidget(license_btn)

        notices_btn = HOTSButton(FIF.DOCUMENT, "#60c8ff", T("about_notices_btn"))
        notices_btn.fit_to_content()
        notices_btn.clicked.connect(lambda: self._open_notice(
            "THIRD-PARTY-NOTICES.txt", "https://hotstools.com/licenses/"))
        footer_lay.addWidget(notices_btn)
        cl.addWidget(footer)

    @staticmethod
    def _anonymize(text: str) -> str:
        home = str(Path.home())
        if len(home) > 3:
            text = re.sub(re.escape(home), "%USERPROFILE%", text, flags=re.IGNORECASE)
        for value in (os.environ.get("USERNAME", ""), os.environ.get("COMPUTERNAME", "")):
            if len(value) >= 3:
                text = re.sub(re.escape(value), "<user>" if value == os.environ.get("USERNAME") else "<pc>",
                              text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _log_tail(max_lines: int = 80, max_bytes: int = 20 * 1024) -> str:
        path = Path(os.environ.get("APPDATA", Path.home())) / "HOTS Hosts" / "error.log"
        try:
            if path.is_symlink() or not path.is_file():
                return "(no entries)"
            with open(path, "rb") as f:
                f.seek(0, os.SEEK_END)
                f.seek(max(0, f.tell() - max_bytes))
                data = f.read(max_bytes)
            lines = data.decode("utf-8", errors="replace").splitlines()[-max_lines:]
            return "\n".join(lines) if lines else "(no entries)"
        except OSError:
            return "(no entries)"

    def _copy_diagnostics(self):
        try:
            import PySide6
            qt_ver = PySide6.__version__
        except Exception:
            qt_ver = "?"
        try:
            admin = "administrator" if ctypes.windll.shell32.IsUserAnAdmin() else "standard user"
        except Exception:
            admin = "unknown"
        try:
            build = sys.getwindowsversion().build
        except Exception:
            build = "?"
        header = (
            f"HOTS Hosts {APP_VERSION}\n"
            f"Windows: {platform.release()}, build {build} ({platform.machine()})\n"
            f"Program language: {current_lang().upper()}\n"
            f"Privileges: {admin}\n"
            f"Python {platform.python_version()} | PySide6 {qt_ver}\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"--- error.log (last 80 lines) ---\n"
        )
        QApplication.clipboard().setText(self._anonymize(header + self._log_tail()))
        self._diag_btn.set_label(T("about_diag_copied"))
        QTimer.singleShot(2000, lambda: self._diag_btn.set_label(T("about_diag_btn")))

    def _open_notice(self, filename: str, url: str):
        try:
            if webbrowser.open(url):
                return
        except Exception:
            pass
        path = self._find_asset(filename)
        if path:
            try:
                os.startfile(path)
            except OSError:
                pass
