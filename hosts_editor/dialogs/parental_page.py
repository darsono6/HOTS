import os
import shiboken6

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea,
)
from PySide6.QtCore import Qt, QObject, Signal, QSize
from PySide6.QtGui import QColor

from ..icons import FIF
from ..ui_parts import IconWidget, TransparentToolButton
from ..constants import DARK
from ..core import toggle_parental_control, get_parental_active_map, HostsBusyError
from ..core_antispy import HostsLockError
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton, h_separator, attach_fluent_tip, make_folder_button, colored_svg_icon, SmoothWheel, EqualHeight
from ..i18n import T
from ..bg_tasks import start_bg_thread, is_shutting_down
from ..dns_utils import is_cf_family_active, get_cf_status, format_dns_status, enable_cf_family_dns, disable_cf_family_dns, has_dns_backup

from ._parental_shared import (
    CATEGORIES, _CATEGORY_COMMENT, _CF_ACCENT, _blocklists_dir,
    _InfoButton, _ParentalCardMixin, any_info_popup_open,
)
from ._appblock_card import _AppBlockCardMixin
from ._doh_card import _DohBlockCardMixin
from ._netblock_card import _NetBlockCardMixin


class _CfDnsToggleSignals(QObject):
    done = Signal(dict)

class _CfDnsStatusSignals(QObject):
    done = Signal(bool, str)


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w:
            w.hide()
            w.deleteLater()
        else:
            child_layout = item.layout()
            if child_layout:
                _clear_layout(child_layout)


class ParentalPage(_ParentalCardMixin, _AppBlockCardMixin, _DohBlockCardMixin, _NetBlockCardMixin, HOTSPage):
    _refresh_on_show = False

    def __init__(self, parent=None):
        import re as _re_title
        clean_title = _re_title.sub(r"[^\w\s/.:,!?()-]", "", T("par_title")).strip()
        super().__init__("parentalInterface", FIF.PEOPLE, clean_title, parent)
        self._bdir = _blocklists_dir()
        self._states = {}
        self._toggle_signal_refs = []
        self._parent_win = parent
        self._built = False

    def refresh_content(self):
        if self._built and (self._busy_count > 0 or any_info_popup_open()):
            return
        self._states = {}
        _clear_layout(self.content_layout)
        self._build()
        self._built = True

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

        self._folder_btn = make_folder_button(
            os.path.normpath(self._bdir), self._open_blocklists_folder, size=20, icon_size=14
        )
        sub_row.addWidget(self._folder_btn, 0, Qt.AlignVCenter)
        sub_row.addSpacing(6)

        warn_ico = _InfoButton(T("par_limitations_tooltip"))
        sub_row.addWidget(warn_ico)
        rl.addLayout(sub_row)
        rl.addSpacing(10)
        rl.addWidget(h_separator())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        SmoothWheel(scroll)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(12, 10, 12, 10)
        inner_lay.setSpacing(6)

        inner_lay.addWidget(self._make_netblock_card())
        inner_lay.addSpacing(6)
        inner_lay.addWidget(self._make_cf_card())
        inner_lay.addSpacing(6)
        inner_lay.addWidget(self._make_appblock_card())
        inner_lay.addSpacing(6)
        inner_lay.addWidget(self._make_doh_card())
        inner_lay.addSpacing(6)

        active_map = get_parental_active_map([cat["file"] for cat in CATEGORIES])

        inner_lay.addWidget(self._make_categories_section(CATEGORIES, active_map))

        inner_lay.addStretch()
        scroll.setWidget(inner)
        rl.addWidget(scroll, 1)

        self._height_sync = EqualHeight(self._netblock_card_widget, [
            w for w in (
                getattr(self, "_cf_card_widget", None),
                getattr(self, "_appblock_header", None),
                getattr(self, "_doh_header", None),
                getattr(self, "_categories_header", None),
            ) if w is not None and shiboken6.isValid(w)
        ])

    def _make_cf_card(self, height: int = 64) -> QWidget:
        active = getattr(self, "_cf_active", False)
        card = self._card_frame(_CF_ACCENT, height)
        info_lay = card.property("info_lay")

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        ico = IconWidget(FIF.GLOBE)
        ico.setFixedSize(20, 20)
        ico.setIcon(colored_svg_icon(FIF.GLOBE, QColor(_CF_ACCENT), sizes=(20,)))
        top_row.addWidget(ico, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        t = QLabel(T("par_cf_title"))
        t.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent;")
        title_row.addWidget(t)
        title_row.addWidget(_InfoButton(T("par_cf_tooltip")))
        title_row.addStretch()
        text_col.addLayout(title_row)

        dns_row = QHBoxLayout()
        dns_row.setSpacing(4)
        self._cf_dns_lbl = QLabel()
        self._cf_dns_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        dns_row.addWidget(self._cf_dns_lbl)

        self._cf_refresh_btn = TransparentToolButton(FIF.SYNC)
        self._cf_refresh_btn.setFixedSize(18, 18)
        self._cf_refresh_btn.setIconSize(QSize(12, 12))
        self._cf_refresh_btn.setIcon(colored_svg_icon(FIF.SYNC, QColor(DARK["accent"]), sizes=(12,)))
        self._cf_refresh_btn.setCursor(Qt.PointingHandCursor)
        attach_fluent_tip(self._cf_refresh_btn, T("par_cf_refresh"))
        self._cf_refresh_btn.clicked.connect(self._on_cf_refresh_clicked)
        dns_row.addWidget(self._cf_refresh_btn, 0, Qt.AlignVCenter)
        dns_row.addStretch()
        text_col.addLayout(dns_row)
        self._set_cf_dns_text(getattr(self, "_cf_dns_text", ""))

        top_row.addLayout(text_col, 1)
        info_lay.addLayout(top_row)

        btn_color = DARK["green"] if active else DARK["gray"]
        btn_label = T("par_cf_btn_disable") if active else T("par_cf_btn_enable")
        btn_icon  = FIF.CONNECT if active else FIF.CLOSE

        self._cf_btn = HOTSButton(btn_icon, btn_color, "", accent=False)
        self._cf_btn.setFixedWidth(44)
        attach_fluent_tip(self._cf_btn, btn_label)
        self._cf_btn.clicked.connect(self._toggle_cf_dns)
        self._cf_active = active

        btn_row = card.property("btn_lay")
        btn_row.addWidget(self._cf_btn)

        self._cf_card_widget = card
        self._refresh_cf_status_async()
        return card

    def _set_cf_dns_text(self, text: str):
        self._cf_dns_text = text
        lbl = getattr(self, "_cf_dns_lbl", None)
        if lbl is None or not shiboken6.isValid(lbl):
            return
        shown = text or "\u2026"
        full = f"DNS: {shown}"
        lbl.setText(full if len(full) <= 90 else full[:89] + "\u2026")
        attach_fluent_tip(lbl, full, width=360)

    def _on_cf_refresh_clicked(self):
        if getattr(self, "_toggle_op_active", False):
            return
        self._refresh_cf_status_async()

    def _refresh_cf_status_async(self):
        if getattr(self, "_toggle_op_active", False):
            return

        rb = getattr(self, "_cf_refresh_btn", None)
        if rb is not None and shiboken6.isValid(rb):
            rb.setEnabled(False)

        signals = _CfDnsStatusSignals(self)
        signals.done.connect(self._on_cf_status_checked)
        self._cf_status_signals = signals

        def worker():
            try:
                active, dns_map = get_cf_status()
                text = format_dns_status(dns_map)
            except Exception:
                active, text = False, "\u2014"
            signals.done.emit(active, text)

        start_bg_thread(worker)

    def _on_cf_status_checked(self, active: bool, dns_text: str):
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        rb = getattr(self, "_cf_refresh_btn", None)
        if rb is not None and shiboken6.isValid(rb):
            rb.setEnabled(True)
        if getattr(self, "_toggle_op_active", False):
            return
        self._set_cf_dns_text(dns_text)
        btn = getattr(self, "_cf_btn", None)
        if btn is None or not shiboken6.isValid(btn):
            return
        if active == getattr(self, "_cf_active", False):
            return

        self._cf_active = active
        btn_color = DARK["green"] if active else DARK["gray"]
        btn_icon = FIF.CONNECT if active else FIF.CLOSE
        btn.set_icon(btn_icon, btn_color)
        btn.set_accent(False)
        attach_fluent_tip(btn, T("par_cf_btn_disable") if active else T("par_cf_btn_enable"))

    def _toggle_cf_dns(self):
        if getattr(self, "_toggle_op_active", False):
            return

        if not self._cf_active:
            adult_state = self._states.get("adult.txt")
            if adult_state and adult_state["active"]:
                if not self._confirm_overwrite_unsaved():
                    return
                self._run_cf_dns_toggle(enable=True, adult_state=adult_state)
                return
            self._run_cf_dns_toggle(enable=True)
        else:
            self._run_cf_dns_toggle(enable=False)

    def _run_cf_dns_toggle(self, enable: bool, adult_state: dict = None):
        self._toggle_op_active = True
        self._set_all_category_buttons_enabled(False)

        self._cf_btn.setEnabled(False)
        self.begin_busy()

        signals = _CfDnsToggleSignals(self)
        signals.done.connect(lambda res: self._on_cf_dns_toggle_done(enable, adult_state, res))
        self._cf_toggle_signals = signals

        def worker():
            res = {"ok": False, "active": self._cf_active, "failed": [],
                   "adult_ok": None, "adult_err": None}

            if adult_state is not None:
                try:
                    ok = toggle_parental_control(
                        False, adult_state["path"], tag_suffix="adult.txt",
                        comment=_CATEGORY_COMMENT.get("adult.txt", "Secure"))
                    res["adult_ok"] = ok
                    if not ok:
                        res["adult_err"] = T("par_err_hosts_msg")
                except HostsLockError as exc:
                    res["adult_ok"] = False
                    res["adult_err"] = str(exc)
                except HostsBusyError as exc:
                    res["adult_ok"] = False
                    res["adult_err"] = str(exc)
                except Exception:
                    res["adult_ok"] = False
                    res["adult_err"] = T("par_err_hosts_msg")

                if not res["adult_ok"]:
                    res["active"] = self._cf_active
                    signals.done.emit(res)
                    return

            try:
                if enable:
                    res["ok"], res["failed"] = enable_cf_family_dns()
                else:
                    res["no_backup"] = not has_dns_backup()
                    res["ok"], res["failed"] = disable_cf_family_dns()
            except Exception:
                res["ok"], res["failed"] = False, []

            if res["ok"]:
                res["active"] = enable
            else:
                try:
                    res["active"] = is_cf_family_active()
                except Exception:
                    pass
            signals.done.emit(res)

        start_bg_thread(worker)

    def _on_cf_dns_toggle_done(self, enable: bool, adult_state: dict, res: dict):
        self._finish_cf_dns_toggle(enable, adult_state, res)

    def _finish_cf_dns_toggle(self, enable: bool, adult_state: dict, res: dict):
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        self._toggle_op_active = False
        self._set_all_category_buttons_enabled(True)

        self._cf_btn.setEnabled(True)
        self.end_busy()

        self._cf_active = res["active"]
        self._update_cf_btn()
        self._refresh_cf_status_async()

        if adult_state is not None and res["adult_ok"]:
            adult_state["active"] = False
            self._refresh_btn(adult_state)
            if self._parent_win and hasattr(self._parent_win, "_load"):
                self._parent_win._load()

        if adult_state is not None and not res["adult_ok"]:
            HOTSDialog.error(self, T("par_cf_title"),
                             res["adult_err"] or T("par_err_hosts_msg"))
            return

        ok, failed = res["ok"], res["failed"]
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
                msg = T("par_cf_off_ok_no_backup" if res.get("no_backup") else "par_cf_off_ok")
                if failed:
                    msg += "\n" + T("par_cf_partial_fail", ifaces=", ".join(failed))
                HOTSDialog.info(self, T("par_cf_title"), msg)
            else:
                err_msg = T("par_cf_off_fail")
                if failed:
                    err_msg += "\n" + T("par_cf_partial_fail", ifaces=", ".join(failed))
                HOTSDialog.error(self, T("par_cf_title"), err_msg)

    def _update_cf_btn(self):
        color = DARK["green"] if self._cf_active else DARK["gray"]
        label = T("par_cf_btn_disable") if self._cf_active else T("par_cf_btn_enable")
        icon  = FIF.CONNECT if self._cf_active else FIF.CLOSE

        attach_fluent_tip(self._cf_btn, label)
        self._cf_btn.set_icon(icon, color)
        self._cf_btn.set_accent(False)
