import os
import threading

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea,
)
from PySide6.QtCore import Qt, QSize, QObject, Signal
from PySide6.QtGui import QColor

from qfluentwidgets import FluentIcon as FIF, IconWidget
try:
    from qfluentwidgets import IndeterminateProgressRing
except ImportError:
    IndeterminateProgressRing = None

from ..constants import DARK
from ..core import toggle_parental_control, get_parental_active_map
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton, h_separator
from ..i18n import T
from ..dns_utils import is_cf_family_active, enable_cf_family_dns, disable_cf_family_dns

from ._parental_shared import (
    CATEGORIES, _CATEGORY_COMMENT, _CF_ACCENT, _blocklists_dir,
    _InfoButton, _ParentalCardMixin,
)


class _CfDnsToggleSignals(QObject):
    done = Signal(bool, bool, list)


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w:
            w.deleteLater()
        else:
            child_layout = item.layout()
            if child_layout:
                _clear_layout(child_layout)


class ParentalPage(_ParentalCardMixin, HOTSPage):
    def __init__(self, parent=None):
        import re as _re_title
        clean_title = _re_title.sub(r"[^\w\s/.:,!?()-]", "", T("par_title")).strip()
        super().__init__("parentalInterface", FIF.PEOPLE, clean_title, parent)
        self._bdir = _blocklists_dir()
        self._states = {}
        self._parent_win = parent
        self._build()

    def refresh_content(self):
        self._states = {}
        _clear_layout(self.content_layout)
        self._build()

    def _open_blocklists_folder(self):
        try:
            path = os.path.normpath(self._bdir)
            if os.path.exists(path):
                os.startfile(path)
        except Exception:
            pass

    def _build(self):
        rl = self.content_layout

        sub_row = QHBoxLayout()
        sub = QLabel(T("par_subheader"))
        sub.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        sub_row.addWidget(sub)
        sub_row.addStretch()

        from qfluentwidgets import TransparentToolButton as _TransparentToolButton
        self._folder_btn = _TransparentToolButton(FIF.FOLDER)
        self._folder_btn.setFixedSize(28, 28)
        self._folder_btn.setIconSize(QSize(15, 15))
        self._folder_btn.setIcon(FIF.FOLDER.icon(color=QColor(DARK["accent"])))
        self._folder_btn.setCursor(Qt.PointingHandCursor)
        self._folder_btn.setToolTip(os.path.normpath(self._bdir))
        self._folder_btn.clicked.connect(self._open_blocklists_folder)
        sub_row.addWidget(self._folder_btn)
        sub_row.addSpacing(6)

        warn_ico = _InfoButton(T("par_limitations_tooltip"))
        sub_row.addWidget(warn_ico)
        rl.addLayout(sub_row)
        rl.addSpacing(10)
        rl.addWidget(h_separator())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(12, 10, 12, 10)
        inner_lay.setSpacing(6)

        active_map = get_parental_active_map([cat["file"] for cat in CATEGORIES])

        for cat in CATEGORIES:
            if cat["file"] == "adult.txt":
                inner_lay.addWidget(self._make_cf_card())
            inner_lay.addWidget(self._make_card(cat, active=active_map.get(cat["file"])))

        inner_lay.addStretch()
        scroll.setWidget(inner)
        rl.addWidget(scroll, 1)

    def _make_cf_card(self) -> QWidget:
        active = is_cf_family_active()
        card = self._card_frame(_CF_ACCENT)
        info_lay = card.property("info_lay")

        title_row = QHBoxLayout()
        ico = IconWidget(FIF.GLOBE)
        ico.setFixedSize(20, 20)
        ico.setIcon(FIF.GLOBE.icon(color=QColor(_CF_ACCENT)))
        title_row.addWidget(ico)
        t = QLabel(T("par_cf_title"))
        t.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent;")
        title_row.addWidget(t)
        title_row.addStretch()
        info_lay.addLayout(title_row)

        desc = QLabel(T("par_cf_desc"))
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        info_lay.addWidget(desc)

        btn_color = DARK["red"] if active else DARK["green"]
        btn_label = T("par_cf_btn_disable") if active else T("par_cf_btn_enable")
        btn_icon  = FIF.CLOSE if active else FIF.CONNECT

        self._cf_btn = HOTSButton(btn_icon, btn_color, btn_label, accent=False)
        self._cf_btn.fit_to_content()
        self._cf_btn.clicked.connect(self._toggle_cf_dns)
        self._cf_active = active

        btn_row = card.property("btn_lay")
        warn_ico = _InfoButton(T("par_cf_tooltip"))
        btn_row.addWidget(warn_ico)

        self._cf_spinner = None
        if IndeterminateProgressRing is not None:
            self._cf_spinner = IndeterminateProgressRing()
            self._cf_spinner.setFixedSize(16, 16)
            self._cf_spinner.setStrokeWidth(2)
            self._cf_spinner.setVisible(False)
            btn_row.addWidget(self._cf_spinner, 0, Qt.AlignVCenter)

        self._cf_busy_lbl = QLabel(T("priv_op_working"))
        self._cf_busy_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        self._cf_busy_lbl.setVisible(False)
        btn_row.addWidget(self._cf_busy_lbl, 0, Qt.AlignVCenter)

        btn_row.addWidget(self._cf_btn)

        return card

    def _toggle_cf_dns(self):
        if not self._cf_active:
            adult_state = self._states.get("adult.txt")
            if adult_state and adult_state["active"]:
                if not self._confirm_overwrite_unsaved():
                    return
                path = adult_state["path"]
                ok = toggle_parental_control(False, path, tag_suffix="adult.txt",
                                             comment=_CATEGORY_COMMENT.get("adult.txt", "Secure"))
                if ok:
                    adult_state["active"] = False
                    self._refresh_btn(adult_state)
                    if self._parent_win and hasattr(self._parent_win, "_load"):
                        self._parent_win._load()
                else:
                    HOTSDialog.error(self, T("par_cf_title"), T("par_err_hosts_msg"))
                    return

            self._run_cf_dns_toggle(enable=True)
        else:
            self._run_cf_dns_toggle(enable=False)

    def _run_cf_dns_toggle(self, enable: bool):
        self._cf_btn.setEnabled(False)
        self._cf_btn.setVisible(False)
        if self._cf_spinner is not None:
            self._cf_spinner.setVisible(True)
        self._cf_busy_lbl.setVisible(True)

        signals = _CfDnsToggleSignals()
        signals.done.connect(lambda ok, active, failed: self._on_cf_dns_toggle_done(enable, ok, active, failed))
        self._cf_toggle_signals = signals

        def worker():
            ok, failed, active = False, [], self._cf_active
            try:
                if enable:
                    ok, failed = enable_cf_family_dns()
                else:
                    ok, failed = disable_cf_family_dns()
            except Exception:
                ok, failed = False, []
            try:
                active = is_cf_family_active()
            except Exception:
                pass
            signals.done.emit(ok, active, failed)

        threading.Thread(target=worker, daemon=True).start()

    def _on_cf_dns_toggle_done(self, enable: bool, ok: bool, active: bool, failed: list):
        if self._cf_spinner is not None:
            self._cf_spinner.setVisible(False)
        self._cf_busy_lbl.setVisible(False)
        self._cf_btn.setEnabled(True)
        self._cf_btn.setVisible(True)

        self._cf_active = active
        self._update_cf_btn()

        if enable:
            if ok:
                msg = T("par_cf_on_ok")
                if failed:
                    msg += "\n" + T("par_cf_partial_fail", ifaces=", ".join(failed))
                HOTSDialog.info(self, T("par_cf_title"), msg)
            else:
                HOTSDialog.error(self, T("par_cf_title"), T("par_cf_on_fail"))
        else:
            if ok:
                msg = T("par_cf_off_ok")
                if failed:
                    msg += "\n" + T("par_cf_partial_fail", ifaces=", ".join(failed))
                HOTSDialog.info(self, T("par_cf_title"), msg)
            else:
                err_msg = T("par_cf_off_fail")
                if failed:
                    err_msg += "\n" + T("par_cf_partial_fail", ifaces=", ".join(failed))
                HOTSDialog.error(self, T("par_cf_title"), err_msg)

    def _update_cf_btn(self):
        color = DARK["red"] if self._cf_active else DARK["green"]
        label = T("par_cf_btn_disable") if self._cf_active else T("par_cf_btn_enable")
        icon  = FIF.CLOSE if self._cf_active else FIF.CONNECT

        self._cf_btn.set_label(label)
        self._cf_btn.set_icon(icon, color)
        self._cf_btn.set_accent(False)
        self._cf_btn.fit_to_content()
