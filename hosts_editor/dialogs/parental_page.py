import os
import threading
import shiboken6

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea,
)
from PySide6.QtCore import Qt, QSize, QObject, Signal, QTimer
from PySide6.QtGui import QColor

from qfluentwidgets import FluentIcon as FIF, IconWidget

from ..constants import DARK
from ..core import toggle_parental_control, get_parental_active_map, HostsBusyError
from ..core_antispy import HostsLockError, HostsLockManager
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton, h_separator, attach_fluent_tip, make_folder_button, colored_svg_icon
from ..i18n import T
from ..bg_tasks import start_bg_thread, is_shutting_down
from ..dns_utils import is_cf_family_active, enable_cf_family_dns, disable_cf_family_dns

from ._parental_shared import (
    CATEGORIES, _CATEGORY_COMMENT, _CF_ACCENT, _blocklists_dir,
    _InfoButton, _ParentalCardMixin,
)
from ._appblock_card import _AppBlockCardMixin
from ._doh_card import _DohBlockCardMixin


class _CfDnsToggleSignals(QObject):
    done = Signal(dict)

class _HostsLockToggleSignals(QObject):
    done = Signal(bool)

class _HostsLockDriftSignals(QObject):
    done = Signal(object)

class _CfDnsStatusSignals(QObject):
    done = Signal(bool)


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


class ParentalPage(_ParentalCardMixin, _AppBlockCardMixin, _DohBlockCardMixin, HOTSPage):
    def __init__(self, parent=None):
        import re as _re_title
        clean_title = _re_title.sub(r"[^\w\s/.:,!?()-]", "", T("par_title")).strip()
        super().__init__("parentalInterface", FIF.PEOPLE, clean_title, parent)
        self._bdir = _blocklists_dir()
        self._states = {}
        self._toggle_signal_refs = []
        self._parent_win = parent
        self._build()
        QTimer.singleShot(800, self._check_hosts_lock_drift)

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
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(12, 10, 12, 10)
        inner_lay.setSpacing(6)

        hosts_lock_card = self._make_hosts_lock_card()
        self._hosts_lock_card = hosts_lock_card
        inner_lay.addWidget(hosts_lock_card)
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

        # Wysokość karty "blokada pliku hosts" nie jest wymuszona (ma o jedną
        # linijkę tekstu więcej niż pozostałe pola, więc dopasowuje się do
        # treści). Żeby dociągnąć do niej pozostałe 3 pola, trzeba poczekać,
        # aż Qt faktycznie policzy layout i przyzna kartom realną szerokość —
        # mierzenie od razu po addWidget() dawałoby zawyżony wynik (etykieta
        # z zawijaniem tekstu liczyłaby się tak, jakby miała szerokość 0).
        QTimer.singleShot(0, self._sync_card_heights)

    def _sync_card_heights(self):
        if not shiboken6.isValid(self):
            return
        hosts_card = getattr(self, "_hosts_lock_card", None)
        if hosts_card is None or not shiboken6.isValid(hosts_card):
            return
        ref = hosts_card.height()
        if ref <= 0:
            return
        for widget in (
            getattr(self, "_cf_card_widget", None),
            getattr(self, "_appblock_header", None),
            getattr(self, "_doh_header", None),
            getattr(self, "_categories_header", None),
        ):
            if widget is not None and shiboken6.isValid(widget):
                widget.setFixedHeight(ref)

    def _make_hosts_lock_card(self) -> QWidget:
        active = HostsLockManager.is_active()
        outer = QWidget()
        outer.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        h = QHBoxLayout(outer)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(10)

        icon = IconWidget(FIF.CERTIFICATE)
        icon.setFixedSize(20, 20)
        icon.setIcon(colored_svg_icon(FIF.CERTIFICATE, QColor(DARK["accent"]), sizes=(20,)))
        h.addWidget(icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        title = QLabel(T("hosts_lock_title"))
        title.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent; border: none;")
        title_row.addWidget(title)
        title_row.addWidget(_InfoButton(T("hosts_lock_tooltip")))
        title_row.addStretch()
        text_col.addLayout(title_row)

        desc = QLabel(T("hosts_lock_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        text_col.addWidget(desc)

        status_lbl = QLabel(T("hosts_lock_status_locked") if active else T("hosts_lock_status_unlocked"))
        status_lbl.setStyleSheet(
            f"color: {DARK['green'] if active else DARK['fg2']}; font-size: 8.5pt; background: transparent; border: none;"
        )
        text_col.addWidget(status_lbl)
        h.addLayout(text_col, 1)

        side_col = QVBoxLayout()
        side_col.setSpacing(4)
        side_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        btn_color = DARK["green"] if active else DARK["gray"]
        btn_label = T("hosts_lock_btn_disable") if active else T("hosts_lock_btn_enable")
        btn_icon = FIF.ACCEPT if active else FIF.CLOSE
        btn = HOTSButton(btn_icon, btn_color, "", accent=False)
        btn.setFixedWidth(44)
        attach_fluent_tip(btn, btn_label)
        side_col.addWidget(btn, 0, Qt.AlignRight)

        h.addLayout(side_col)

        state = {
            "active": active, "btn": btn, "status_lbl": status_lbl,
            "busy": False,
        }
        self._hosts_lock_state = state
        btn.clicked.connect(lambda _c=False, s=state: self._toggle_hosts_lock(s))

        return outer

    def _toggle_hosts_lock(self, state: dict):
        if state["busy"]:
            return
        target = not state["active"]
        state["busy"] = True

        btn = state["btn"]
        btn.setEnabled(False)
        self.begin_busy()

        signals = _HostsLockToggleSignals(self)
        signals.done.connect(lambda ok, s=state, t=target: self._on_hosts_lock_toggle_done(s, t, ok))
        self._hosts_lock_signals = signals

        def worker(t=target):
            try:
                ok = HostsLockManager.enable() if t else HostsLockManager.disable()
            except Exception as e:
                ok = False
                HostsLockManager.last_error = str(e)
            signals.done.emit(ok)

        start_bg_thread(worker)

    def _on_hosts_lock_toggle_done(self, state: dict, target: bool, ok: bool):
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        state["busy"] = False
        btn = state["btn"]
        btn.setEnabled(True)
        self.end_busy()

        if ok:
            state["active"] = target
            self._refresh_hosts_lock_card(state)
            if self._parent_win and hasattr(self._parent_win, "_refresh_toolbar_status_ui"):
                self._parent_win._refresh_toolbar_status_ui()
            msg_key = "hosts_lock_on_ok" if target else "hosts_lock_off_ok"
            HOTSDialog.info(self, T("hosts_lock_title"), T(msg_key))
        else:
            self._refresh_hosts_lock_card(state)
            err_msg = T("hosts_lock_on_fail") if target else T("hosts_lock_off_fail")
            if HostsLockManager.last_error:
                err_msg += f"\n\n{HostsLockManager.last_error}"
            HOTSDialog.error(self, T("hosts_lock_title"), err_msg)

    def _refresh_hosts_lock_card(self, state: dict):
        active = state["active"]
        btn = state["btn"]
        attach_fluent_tip(btn, T("hosts_lock_btn_disable") if active else T("hosts_lock_btn_enable"))
        btn.set_icon(FIF.ACCEPT if active else FIF.CLOSE, DARK["green"] if active else DARK["gray"])
        btn.set_accent(False)

        status_lbl = state["status_lbl"]
        status_lbl.setText(T("hosts_lock_status_locked") if active else T("hosts_lock_status_unlocked"))
        status_lbl.setStyleSheet(
            f"color: {DARK['green'] if active else DARK['fg2']}; font-size: 8.5pt; background: transparent; border: none;"
        )

    def _check_hosts_lock_drift(self):
        signals = _HostsLockDriftSignals(self)
        signals.done.connect(self._on_hosts_lock_drift_checked)
        self._hosts_lock_drift_signals = signals

        def worker():
            try:
                result = HostsLockManager.check_drift()
            except Exception as e:
                print(f"Hosts lock watchdog warning: {e}")
                result = None
            signals.done.emit(result)

        start_bg_thread(worker)

    def _on_hosts_lock_drift_checked(self, result):
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        state = getattr(self, "_hosts_lock_state", None)
        if not state or result is None:
            return
        state["active"] = HostsLockManager.is_active()
        self._refresh_hosts_lock_card(state)
        if self._parent_win and hasattr(self._parent_win, "_refresh_toolbar_status_ui"):
            self._parent_win._refresh_toolbar_status_ui()

        if result == "regressed":
            status_lbl = state["status_lbl"]
            status_lbl.setText(T("hosts_lock_drift_regressed"))
            status_lbl.setStyleSheet(f"color: {DARK['red']}; font-size: 8.5pt; background: transparent; border: none;")
        elif result == "restored":
            status_lbl = state["status_lbl"]
            status_lbl.setText(T("hosts_lock_drift_restored"))
            status_lbl.setStyleSheet(f"color: {DARK['green']}; font-size: 8.5pt; background: transparent; border: none;")

    def _make_cf_card(self, height: int = 64) -> QWidget:
        # is_cf_family_active() odpytuje system o karty sieciowe i dla
        # kazdej z nich odpala proces "netsh" (patrz dns_utils.py) - na
        # Windows to zwykle dziesiatki-setki ms NA INTERFEJS. Wywolane tu
        # synchronicznie, na watku UI, spowalnialoby WIDOCZNIE kazde
        # przelaczenie na te strone (_build() leci przy kazdym showEvent -
        # patrz HOTSPage.showEvent w widgets_qt.py). Zamiast tego karta od
        # razu rysuje sie z ostatnio znanym stanem (self._cf_active,
        # domyslnie False przy pierwszym uruchomieniu), a realny stan jest
        # sprawdzany w tle i podmieniany po cichu, gdy wynik nadejdzie -
        # ten sam wzorzec co _check_hosts_lock_drift() nizej.
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

        desc = QLabel(T("par_cf_desc"))
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
        text_col.addWidget(desc)

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

    def _refresh_cf_status_async(self):
        """Sprawdza realny stan Cloudflare Family DNS w tle (netsh, patrz
        wyzej przy _make_cf_card) i po cichu odswieza przycisk/etykiete,
        jesli stan sie zmienil - bez blokowania watku UI."""
        if getattr(self, "_toggle_op_active", False):
            return

        signals = _CfDnsStatusSignals(self)
        signals.done.connect(self._on_cf_status_checked)
        self._cf_status_signals = signals

        def worker():
            try:
                active = is_cf_family_active()
            except Exception:
                active = False
            signals.done.emit(active)

        start_bg_thread(worker)

    def _on_cf_status_checked(self, active: bool):
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        if getattr(self, "_toggle_op_active", False):
            return
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
        # Ta sama blokada co przy kategoriach ("_toggle_op_active" z
        # _ParentalCardMixin) — jeśli trwa już jakikolwiek zapis do hosts
        # (kategoria ALBO CF DNS), nie pozwalamy odpalić drugiego, żeby
        # znowu nie dostać nakładających się zapisów zapychających DNS
        # Client.
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

            # Wyłączenie kategorii "Dorośli" musi się zdarzyć w TYM SAMYM
            # wątku w tle co reszta — to wywołanie toggle_parental_control()
            # potrafi teraz (przy zajętym pliku hosts) trwać kilkanaście-
            # -kilkadziesiąt sekund retry'ów, więc zrobione na głównym
            # wątku UI zamroziłoby całe okno appki na ten czas.
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
                    res["ok"], res["failed"] = disable_cf_family_dns()
            except Exception:
                res["ok"], res["failed"] = False, []
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
        color = DARK["green"] if self._cf_active else DARK["gray"]
        label = T("par_cf_btn_disable") if self._cf_active else T("par_cf_btn_enable")
        icon  = FIF.CONNECT if self._cf_active else FIF.CLOSE

        attach_fluent_tip(self._cf_btn, label)
        self._cf_btn.set_icon(icon, color)
        self._cf_btn.set_accent(False)
