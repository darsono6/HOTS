import threading
import shiboken6

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QScrollArea, QCheckBox, QPushButton, QFrame,
)
from PySide6.QtCore import Qt, QSize, QObject, Signal, QTimer
from PySide6.QtGui import QColor

from qfluentwidgets import FluentIcon as FIF, IconWidget, TransparentToolButton

from ..constants import DARK
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton, h_separator, attach_fluent_tip, colored_svg_icon
from ..i18n import T
from ..bg_tasks import start_bg_thread, is_shutting_down
from ..core_antispy import AntiSpyManager, ITEMS
from ..core_restore import SystemRestoreManager
from ..core_appblock import AppBlockManager

from ._parental_shared import (
    _blocklists_dir, _AntiSpySignals, _ParentalCardMixin, CUSTOM_CATEGORY, _InfoButton,
    any_info_popup_open, info_popup_bus,
)

_RSTRUI_EXE = "rstrui.exe"

def _refresh_power_toggle_icon(btn: TransparentToolButton):
    """Koloruje ikonę-włącznik (FIF.POWER_BUTTON) zależnie od stanu — ten sam
    wygląd/logika co przy zablokowanych programach/VPN w zakładce Ochrona.

    Stan ON/OFF różni się nie tylko kolorem ikony: wyłączone dostaje dodatkowo
    cienką, kwadratową obwódkę (tę samą, która i tak pojawia się przy hover),
    włączone zostaje "czyste" - sam kolorowy symbol bez obwódki. Dzięki temu
    różnica jest czytelna nawet gdy kolor danego poziomu (np. fiolet
    "Prywatność+") ma zbliżoną jasność do koloru stanu wyłączonego - zwłaszcza
    na jasnym motywie, gdzie samo poleganie na odcieniu bywa zbyt subtelne.

    Ustawiamy tu własny setStyleSheet(), co nadpisuje CAŁY domyślny styl
    TransparentToolButton (łącznie z jego :hover) — dlatego dopisujemy
    własne reguły :hover/:pressed, żeby nie zgubić tego efektu. Neutralny
    szary naświetlacz (zamiast czarnego/białego jak w oryginale) wygląda
    dobrze niezależnie od motywu, bez potrzeby śledzenia który jest aktywny.

    Aktualizuje też tooltip (Blokada aktywna/nieaktywna) — ale nie nadpisuje
    go dla pozycji z dryfem, bo te mają własny, bardziej szczegółowy opis."""
    hover_rules = (
        "QToolButton:hover { background: rgba(128, 128, 128, 30); }"
        "QToolButton:pressed { background: rgba(128, 128, 128, 45); }"
    )

    if getattr(btn, "_is_missing_item", False):
        btn.setIcon(colored_svg_icon(FIF.POWER_BUTTON, QColor(DARK["border_faint"]), sizes=(20,)))
        btn.setStyleSheet(
            "QToolButton { background: transparent; border: none; border-radius: 5px; }"
        )
        return

    on_color = getattr(btn, "_on_color", DARK["accent"])
    checked = btn.isChecked()
    if checked:
        btn.setIcon(colored_svg_icon(FIF.POWER_BUTTON, QColor(on_color), sizes=(20,)))
        btn.setStyleSheet(
            "QToolButton { background: transparent; border: none; border-radius: 5px; }"
            + hover_rules
        )
    else:
        btn.setIcon(colored_svg_icon(FIF.POWER_BUTTON, QColor(DARK["fg2"]), sizes=(20,)))
        btn.setStyleSheet(
            f"QToolButton {{ background: transparent; border: 1px solid {DARK['border']}; "
            f"border-radius: 5px; }}"
            + hover_rules
        )

    if not getattr(btn, "_is_drifted_item", False):
        attach_fluent_tip(
            btn,
            T("priv_toggle_active_tooltip") if checked else T("priv_toggle_inactive_tooltip"),
        )


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

def _items_for_level(level: str) -> list:
    return [it for it in ITEMS if it["level"] == level]

_LABEL_KEY_BY_ID = {it["id"]: it["label_key"] for it in ITEMS}

# Pozycje, których wyłączenie ma zauważalny wpływ na funkcjonalność systemu
# (np. przestaje działać pogoda/mapy albo zabezpieczenie antykradzieżowe).
# Na życzenie usera trójkąt ostrzegawczy przy ich nazwie został wyłączony -
# zbiór celowo pusty (a nie usunięty), żeby zachować miejsce na ponowne
# włączenie w przyszłości bez przywracania całego mechanizmu od zera.
_WARNING_ITEM_IDS = set()

def _with_warning_suffix(item_id: str, text: str) -> str:
    return text + " ⚠" if item_id in _WARNING_ITEM_IDS else text

def _level_any_active(level: str) -> bool:
    return any(AntiSpyManager.get_items_status(level).values())

def _level_counts(level: str) -> tuple:
    items_status = AntiSpyManager.get_items_status(level)
    available_ids = [iid for iid in items_status if not AntiSpyManager.is_item_missing(iid)]
    items_total = len(available_ids)
    items_active = sum(1 for iid in available_ids if items_status[iid])
    return items_active, items_total

class _ChecklistSignals(QObject):
    done = Signal(bool, list, str)

class _RestorePointSignals(QObject):
    done = Signal(str, str)

class _RemoveLimitSignals(QObject):
    done = Signal(bool, str)

class _RstruiLockToggleSignals(QObject):
    done = Signal(bool)


class PrivacyPage(_ParentalCardMixin, HOTSPage):
    busy_changed = Signal(bool)

    def __init__(self, parent=None):
        import re as _re_title
        clean_title = _re_title.sub(r"[^\w\s/.:,!?()-]", "", T("priv_title")).strip()
        super().__init__("privacyInterface", FIF.HIDE, clean_title, parent)
        self._bdir = _blocklists_dir()
        self._states = {}
        self._toggle_signal_refs = []
        self._antispy_states = {}
        self._antispy_busy = set()
        self._antispy_signals = {}
        self._checklist_states = {}
        self._drifted_ids = set()
        self._bg_signal_objs: list = []
        self._manual_ops_active = 0
        self._pending_refresh = False
        self._parent_win = parent
        # Patrz _InfoPopupBus w _parental_shared.py: gdy watchdog konczy
        # prace w tle w momencie, gdy user ma otwarty dymek "?" (np. przy
        # "Zablokuj narzedzie Przywracanie systemu"), refresh_content() nie
        # moze wtedy w calosci przebudowac strony (patrz nizej) - trzeba
        # poczekac, az user zamknie dymek, i dopiero wtedy sprobowac znowu.
        info_popup_bus.popup_closed.connect(self._retry_pending_refresh)
        self._build()

    def _retry_pending_refresh(self):
        if self._pending_refresh:
            self.refresh_content()

    def refresh_content(self):
        if self._manual_ops_active > 0 or any_info_popup_open():
            self._pending_refresh = True
            return
        self._pending_refresh = False
        self._states = {}
        self._antispy_states = {}
        self._antispy_busy = set()
        self._antispy_signals = {}
        self._checklist_states = {}
        _clear_layout(self.content_layout)
        self._build()

    def _mark_op_start(self):
        was_idle = self._manual_ops_active == 0
        self._manual_ops_active += 1
        if was_idle:
            self.busy_changed.emit(True)
        self.begin_busy()

    def _mark_op_end(self):
        self._manual_ops_active = max(0, self._manual_ops_active - 1)
        self.end_busy()
        if self._manual_ops_active == 0:
            self.busy_changed.emit(False)
            self._retry_pending_refresh()

    def _set_categories_busy(self, busy: bool):
        """Nadpisuje wersję z _ParentalCardMixin (_parental_shared.py). Tutaj
        (karty 'Blokada domen telemetrycznych' i 'Blokada własnych domen')
        podpinamy się pod już gotowy wskaźnik zajętości strony (spinner +
        tekst w rogu nagłówka + licznik _manual_ops_active), zamiast
        dokładać drugi, osobny spinner."""
        if busy:
            self._mark_op_start()
        else:
            self._mark_op_end()

    def disconnect_bg_signals(self):
        for sig in self._bg_signal_objs:
            try:
                sig.done.disconnect()
            except Exception:
                pass
        self._bg_signal_objs.clear()

    def _track_bg_signal(self, signals):
        """Rejestruje obiekt sygnałów tła (worker -> UI) tak, żeby usuwał się
        z self._bg_signal_objs sam, zaraz po tym jak 'done' zostanie
        wyemitowane. Bez tego lista rosła bez ograniczeń przy każdej operacji
        (przełączenie modułu, zastosowanie checklisty, punkt przywracania,
        zdjęcie limitu) i była czyszczona dopiero przy zamknięciu aplikacji —
        realny, powolny wyciek pamięci przy dłuższej sesji.

        WAŻNE: obiekty przekazywane tutaj MUSZĄ być tworzone z Qt-rodzicem
        (np. _RestorePointSignals(self)), a nie jako "gołe" QObject. _cleanup
        poniżej usuwa jedyną PYTHONOWĄ referencję do obiektu w trakcie
        wykonywania jednego z jego własnych slotów (podłączonego do 'done').
        Bez Qt-rodzica refcount spada do zera i CPython natychmiast niszczy
        obiekt C++ w trakcie, gdy Qt wciąż iteruje po jego liście połączeń
        (emit() jest jeszcze na stosie wywołań) — use-after-free, które
        objawia się jako uszkodzona sterta (0xc0000374) przy zamykaniu/GC.
        Qt-rodzic sprawia, że obiekt żyje dopóki żyje rodzic, więc usunięcie
        go z tej listy jest tylko księgowością, a nie utratą ostatniej
        referencji."""
        self._bg_signal_objs.append(signals)

        def _cleanup(*_args, s=signals):
            if s in self._bg_signal_objs:
                self._bg_signal_objs.remove(s)

        signals.done.connect(_cleanup)

    def set_drifted(self, drifted_ids):
        self._drifted_ids = set(drifted_ids)
        if not shiboken6.isValid(self) or is_shutting_down():
            return
        if self._manual_ops_active > 0:
            self._pending_refresh = True
            return
        self.refresh_content()

    def _level_effective_active(self, level: str) -> bool:
        return _level_any_active(level)

    def _build(self):
        rl = self.content_layout

        sub_row = QHBoxLayout()
        sub = QLabel(T("priv_subheader"))
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        sub_row.addWidget(sub, 1)

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

        restore_banner = self._make_restore_banner()
        self._restore_banner_widget = restore_banner
        inner_lay.addWidget(restore_banner)
        inner_lay.addSpacing(6)
        rstrui_lock_card = self._make_rstrui_lock_card()
        self._rstrui_lock_card = rstrui_lock_card
        inner_lay.addWidget(rstrui_lock_card)
        inner_lay.addSpacing(6)
        inner_lay.addWidget(self._make_antispy_section())
        inner_lay.addSpacing(6)
        telemetry_module = self._make_telemetry_domains_module()
        self._telemetry_domains_card = telemetry_module
        inner_lay.addWidget(telemetry_module)
        inner_lay.addSpacing(6)
        custom_domains_module = self._make_custom_domains_module()
        self._custom_domains_card = custom_domains_module
        inner_lay.addWidget(custom_domains_module)
        inner_lay.addSpacing(6)
        inner_lay.addStretch()
        scroll.setWidget(inner)
        rl.addWidget(scroll, 1)

        # Ta sama sztuczka co na stronie ochrony rodzicielskiej
        # (parental_page.py, _sync_card_heights): baner punktu przywracania
        # ma naturalnie inną wysokość niż pozostałe moduły (inna liczba
        # linijek tekstu), więc żeby wszystkie 3 moduły na stronie
        # Prywatność wyglądały tak samo jak 5 modułów na stronie Ochrona
        # rodzicielska (ten sam rozmiar), trzeba poczekać, aż Qt policzy
        # realny layout, i dociągnąć resztę do wysokości banera.
        QTimer.singleShot(0, self._sync_privacy_module_heights)

    def _sync_privacy_module_heights(self):
        # Prostsze i bezpieczniejsze niż wcześniejsza wersja: referencja to
        # znowu WŁASNY baner tej strony (bez sięgania do ParentalPage przez
        # self._parent_win). Wysokość i tak wychodzi taka sama jak karty
        # "hosts_lock_card" na stronie Ochrona rodzicielska, bo
        # _make_restore_banner() ma teraz te same marginesy (16,14,16,14)
        # i tę samą liczbę linii tekstu (3) co tamta karta - dopasowanie
        # wynika z samej struktury layoutu, bez kruchej zależności
        # między stronami w czasie działania programu.
        if not shiboken6.isValid(self):
            return
        ref_widget = getattr(self, "_restore_banner_widget", None)
        if ref_widget is None or not shiboken6.isValid(ref_widget):
            return
        ref = ref_widget.height()
        if ref <= 0:
            return
        for widget in (
            getattr(self, "_rstrui_lock_card", None),
            getattr(self, "_antispy_levels_header", None),
            getattr(self, "_telemetry_domains_card", None),
            getattr(self, "_custom_domains_card", None),
        ):
            if widget is not None and shiboken6.isValid(widget):
                widget.setFixedHeight(ref)

    def _make_restore_banner(self) -> QWidget:
        outer = QWidget()
        outer.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        h = QHBoxLayout(outer)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(10)

        icon = IconWidget(FIF.HISTORY)
        icon.setFixedSize(20, 20)
        icon.setIcon(colored_svg_icon(FIF.HISTORY, QColor(DARK["accent"]), sizes=(20,)))
        h.addWidget(icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        title = QLabel(T("priv_restore_banner_title"))
        title.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent; border: none;")
        text_col.addWidget(title)
        desc = QLabel(T("priv_restore_banner_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        text_col.addWidget(desc)

        # Trzecia linijka - domyślnie pusta (samo puste miejsce daje
        # baneru tę samą wysokość co karta hosts_lock_card na stronie
        # Ochrona rodzicielska, patrz _sync_privacy_module_heights niżej),
        # a po utworzeniu punktu / usunięciu limitu wyświetla się w niej
        # komunikat wyniku. Zawsze widoczna (nie chowana) - dzięki temu
        # zajmuje stałe miejsce i komunikat nie dokłada nowej, czwartej
        # linijki rozciągającej kartę w dół, tylko podmienia treść tej
        # zarezerwowanej.
        result_lbl = QLabel("")
        result_lbl.setWordWrap(True)
        result_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8.5pt; background: transparent; border: none;")
        text_col.addWidget(result_lbl)

        accent = DARK["accent"]

        remove_row = QHBoxLayout()
        remove_row.setContentsMargins(0, 0, 0, 0)
        remove_row.setSpacing(4)
        remove_hint_lbl = QLabel(T("priv_restore_remove_limit_hint"))
        remove_hint_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        remove_row.addWidget(remove_hint_lbl)
        remove_link_lbl = QLabel(T("priv_restore_remove_limit_link"))
        remove_link_lbl.setStyleSheet(
            f"color: {accent}; font-size: 8pt; font-weight: 600; text-decoration: underline; "
            "background: transparent; border: none;"
        )
        remove_link_lbl.setCursor(Qt.PointingHandCursor)
        attach_fluent_tip(remove_link_lbl, T("priv_restore_remove_limit_tooltip"), width=260)
        remove_row.addWidget(remove_link_lbl)
        remove_row.addStretch(1)
        remove_widget = QWidget()
        remove_widget.setStyleSheet("background: transparent; border: none;")
        remove_widget.setLayout(remove_row)
        remove_widget.setVisible(False)
        text_col.addWidget(remove_widget)

        h.addLayout(text_col, 1)

        create_btn = HOTSButton(FIF.SAVE, accent, "")
        create_btn.setFixedWidth(44)
        attach_fluent_tip(create_btn, T("priv_restore_btn_create"))
        h.addWidget(create_btn, 0, Qt.AlignVCenter)

        state = {
            "btn": create_btn, "result_lbl": result_lbl, "busy": False,
            "remove_widget": remove_widget, "remove_hint_lbl": remove_hint_lbl,
            "remove_link_lbl": remove_link_lbl, "remove_busy": False,
        }
        create_btn.clicked.connect(lambda _c=False, s=state: self._create_restore_point(s))
        remove_link_lbl.mousePressEvent = lambda _e, s=state: self._remove_restore_limit(s)
        return outer

    def _create_restore_point(self, state: dict):
        if state["busy"]:
            return
        state["busy"] = True
        self._mark_op_start()
        btn = state["btn"]
        btn.setEnabled(False)
        attach_fluent_tip(btn, T("priv_restore_btn_working"))
        state["result_lbl"].setText("")
        state["remove_widget"].setVisible(False)

        signals = _RestorePointSignals(self)
        signals.done.connect(lambda status, details, s=state: self._on_restore_point_done(s, status, details))
        self._restore_signals = signals
        self._track_bg_signal(signals)

        import threading

        def worker():
            try:
                status, details = SystemRestoreManager.create_restore_point(T("priv_restore_point_description"))
            except Exception as e:
                status, details = "error", str(e)
            signals.done.emit(status, details)

        start_bg_thread(worker)

    def _on_restore_point_done(self, state: dict, status: str, details: str):
        if not shiboken6.isValid(self):
            return
        state["busy"] = False
        btn = state["btn"]
        btn.setEnabled(True)
        attach_fluent_tip(btn, T("priv_restore_btn_create"))

        lbl = state["result_lbl"]
        if status == "created":
            lbl.setText(T("priv_restore_msg_created"))
            lbl.setStyleSheet(f"color: {DARK['green']}; font-size: 8.5pt; background: transparent; border: none;")
        elif status == "throttled":
            lbl.setText(T("priv_restore_msg_throttled"))
            lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8.5pt; background: transparent; border: none;")
            state["remove_widget"].setVisible(True)
        elif status == "no_admin":
            lbl.setText(T("priv_restore_msg_no_admin"))
            lbl.setStyleSheet(f"color: {DARK['red']}; font-size: 8.5pt; background: transparent; border: none;")
        else:
            lbl.setText(T("priv_restore_msg_error", details=details or "?"))
            lbl.setStyleSheet(f"color: {DARK['red']}; font-size: 8.5pt; background: transparent; border: none;")
        self._mark_op_end()

    def _remove_restore_limit(self, state: dict):
        if state["busy"] or state["remove_busy"]:
            return
        state["remove_busy"] = True
        self._mark_op_start()

        link_lbl = state["remove_link_lbl"]
        link_lbl.setText(T("priv_restore_remove_limit_working"))
        link_lbl.setCursor(Qt.ArrowCursor)

        signals = _RemoveLimitSignals(self)
        signals.done.connect(lambda ok, details, s=state: self._on_remove_limit_done(s, ok, details))
        self._remove_limit_signals = signals
        self._track_bg_signal(signals)

        def worker():
            try:
                ok, details = SystemRestoreManager.remove_frequency_limit()
            except Exception as e:
                ok, details = False, str(e)
            signals.done.emit(ok, details)

        start_bg_thread(worker)

    def _on_remove_limit_done(self, state: dict, ok: bool, details: str):
        if not shiboken6.isValid(self):
            return
        state["remove_busy"] = False

        link_lbl = state["remove_link_lbl"]
        lbl = state["result_lbl"]
        if ok:
            state["remove_widget"].setVisible(False)
            lbl.setText(T("priv_restore_limit_removed"))
            lbl.setStyleSheet(f"color: {DARK['green']}; font-size: 8.5pt; background: transparent; border: none;")
        else:
            link_lbl.setText(T("priv_restore_remove_limit_link"))
            link_lbl.setCursor(Qt.PointingHandCursor)
            lbl.setText(T("priv_restore_limit_remove_error", details=details or "?"))
            lbl.setStyleSheet(f"color: {DARK['red']}; font-size: 8.5pt; background: transparent; border: none;")
        self._mark_op_end()

    def _make_rstrui_lock_card(self) -> QWidget:
        active = bool(AppBlockManager.is_ifeo_blocked(_RSTRUI_EXE))
        outer = QWidget()
        outer.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        h = QHBoxLayout(outer)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(10)

        icon = IconWidget(FIF.APPLICATION)
        icon.setFixedSize(20, 20)
        icon.setIcon(colored_svg_icon(FIF.APPLICATION, QColor(DARK["accent"]), sizes=(20,)))
        h.addWidget(icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        title = QLabel(T("priv_rstrui_lock_title"))
        title.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent; border: none;")
        title_row.addWidget(title)
        title_row.addWidget(_InfoButton(T("priv_rstrui_lock_tooltip")))
        title_row.addStretch()
        text_col.addLayout(title_row)

        desc = QLabel(T("priv_rstrui_lock_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        text_col.addWidget(desc)

        status_lbl = QLabel(
            T("priv_rstrui_lock_status_locked") if active else T("priv_rstrui_lock_status_unlocked")
        )
        status_lbl.setStyleSheet(
            f"color: {DARK['green'] if active else DARK['fg2']}; font-size: 8.5pt; background: transparent; border: none;"
        )
        text_col.addWidget(status_lbl)
        h.addLayout(text_col, 1)

        side_col = QVBoxLayout()
        side_col.setSpacing(4)
        side_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        btn_color = DARK["green"] if active else DARK["gray"]
        btn_label = T("priv_rstrui_lock_btn_disable") if active else T("priv_rstrui_lock_btn_enable")
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
        self._rstrui_lock_state = state
        btn.clicked.connect(lambda _c=False, s=state: self._toggle_rstrui_lock(s))

        return outer

    def _toggle_rstrui_lock(self, state: dict):
        if state["busy"]:
            return
        target = not state["active"]
        state["busy"] = True
        self._mark_op_start()

        btn = state["btn"]
        btn.setEnabled(False)
        btn.setVisible(False)

        signals = _RstruiLockToggleSignals(self)
        # Ta sama kolejność sprzątania co w _toggle_antispy_module wyżej -
        # patrz komentarz tam (tu tylko bez osobnego słownika per-klucz,
        # bo ta karta jest jedna).
        self._rstrui_lock_signals = signals
        self._bg_signal_objs.append(signals)

        def _cleanup_and_handle(ok, s=state, t=target, sig=signals):
            if sig in self._bg_signal_objs:
                self._bg_signal_objs.remove(sig)
            if self._rstrui_lock_signals is sig:
                self._rstrui_lock_signals = None
            self._on_rstrui_lock_toggle_done(s, t, ok)

        signals.done.connect(_cleanup_and_handle)

        def worker(t=target):
            try:
                if t:
                    ok = AppBlockManager.add_app(_RSTRUI_EXE, T("priv_rstrui_lock_title"), category="custom")
                else:
                    ok = AppBlockManager.remove_app(_RSTRUI_EXE)
            except Exception as e:
                ok = False
                AppBlockManager.last_error = str(e)
            signals.done.emit(ok)

        start_bg_thread(worker)

    def _on_rstrui_lock_toggle_done(self, state: dict, target: bool, ok: bool):
        if not shiboken6.isValid(self):
            return
        # Patrz identyczny komentarz w _on_antispy_module_done wyżej -
        # ten handler też pokazuje modal (HOTSDialog.info/error) i może
        # pośrednio wywołać refresh_content() przez _mark_op_end(), więc
        # nie powinien nic robić, jeśli okno jest już w trakcie zamykania.
        if is_shutting_down():
            return
        state["busy"] = False
        btn = state["btn"]
        btn.setEnabled(True)
        btn.setVisible(True)
        self._mark_op_end()

        if ok:
            state["active"] = target
            self._refresh_rstrui_lock_card(state)
            msg_key = "priv_rstrui_lock_on_ok" if target else "priv_rstrui_lock_off_ok"
            HOTSDialog.info(self, T("priv_rstrui_lock_title"), T(msg_key))
        else:
            self._refresh_rstrui_lock_card(state)
            err_msg = T("priv_rstrui_lock_on_fail") if target else T("priv_rstrui_lock_off_fail")
            if AppBlockManager.last_error == "no_admin":
                err_msg += f"\n\n{T('priv_rstrui_lock_err_no_admin')}"
            elif AppBlockManager.last_error:
                err_msg += f"\n\n{AppBlockManager.last_error}"
            HOTSDialog.error(self, T("priv_rstrui_lock_title"), err_msg)

    def _refresh_rstrui_lock_card(self, state: dict):
        active = state["active"]
        btn = state["btn"]
        attach_fluent_tip(btn, T("priv_rstrui_lock_btn_disable") if active else T("priv_rstrui_lock_btn_enable"))
        btn.set_icon(FIF.ACCEPT if active else FIF.CLOSE, DARK["green"] if active else DARK["gray"])
        btn.set_accent(False)

        status_lbl = state["status_lbl"]
        status_lbl.setText(
            T("priv_rstrui_lock_status_locked") if active else T("priv_rstrui_lock_status_unlocked")
        )
        status_lbl.setStyleSheet(
            f"color: {DARK['green'] if active else DARK['fg2']}; font-size: 8.5pt; background: transparent; border: none;"
        )

    def _make_antispy_section(self) -> QWidget:
        level_configs = [
            {"level": "basic", "icon": FIF.HIDE, "label_key": "par_antispy_basic_btn",
             "success_label_key": "par_antispy_basic_label",
             "enable_fn": AntiSpyManager.enable_basic, "disable_fn": AntiSpyManager.disable_basic,
             "badge_color": "#0078D4"},
            {"level": "medium", "icon": FIF.GLOBE, "label_key": "par_antispy_medium_btn",
             "success_label_key": "par_antispy_medium_label",
             "enable_fn": AntiSpyManager.enable_medium, "disable_fn": AntiSpyManager.disable_medium,
             "badge_color": "#C19C00"},
            {"level": "advanced", "icon": FIF.SETTING, "label_key": "par_antispy_advanced_btn",
             "success_label_key": "par_antispy_advanced_label",
             "enable_fn": AntiSpyManager.enable_advanced, "disable_fn": AntiSpyManager.disable_advanced,
             "badge_color": "#CA5010"},
            {"level": "extra", "icon": FIF.CERTIFICATE, "label_key": "par_antispy_extra_btn",
             "success_label_key": "par_antispy_extra_label",
             "enable_fn": AntiSpyManager.enable_extra, "disable_fn": AntiSpyManager.disable_extra,
             "badge_color": "#8764B8"},
        ]

        return self._make_antispy_levels_group(level_configs)

    def _make_telemetry_domains_module(self) -> QWidget:
        domains_cat = {
            "label_key": "par_cat_antispy_domains", "icon": "📡", "fif_icon": FIF.HIDE,
            "color": "#0078D4", "file": "telemetry.txt",
            "tooltip_key": "priv_telemetry_domains_tooltip",
        }
        return self._make_card(domains_cat)

    def _make_custom_domains_module(self) -> QWidget:
        """4. moduł na stronie Prywatność - dawniej '16. kategoria' w
        akordeonie 'popularne serwisy' na stronie Ochrona rodzicielska,
        przeniesiona tutaj (CUSTOM_CATEGORY w _parental_shared.py), bo to
        blokada zdefiniowana przez samego użytkownika, koncepcyjnie bliższa
        Prywatności niż gotowym kategoriom treści. Cała logika (edycja,
        licznik domen, toggle) zostaje bez zmian w _ParentalCardMixin -
        tutaj tylko renderujemy tę samą kartę co osobny, pełnowymiarowy
        moduł zamiast pozycji w akordeonie."""
        return self._make_card(CUSTOM_CATEGORY)

    def _make_antispy_levels_group(self, level_configs: list) -> QWidget:
        """Cztery poziomy ochrony (podstawowa/średnia/zaawansowana/prywatność+)
        zamknięte w jeden zwijany moduł z przyciskiem Rozwiń/Zwiń -
        dokładnie ten sam wzorzec co karta 'Blokada aplikacji'
        (dialogs/_appblock_card.py, _make_appblock_card) i akordeon
        'popularne serwisy' (dialogs/_parental_shared.py,
        _make_categories_section)."""
        outer = QWidget()
        outer.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        outer_lay = QVBoxLayout(outer)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        outer_lay.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet("background: transparent; border: none;")
        h = QHBoxLayout(header)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(10)

        icon = IconWidget(FIF.FINGERPRINT)
        icon.setFixedSize(20, 20)
        icon.setIcon(colored_svg_icon(FIF.FINGERPRINT, QColor(DARK["accent"]), sizes=(20,)))
        h.addWidget(icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        title = QLabel(T("priv_levels_group_title"))
        title.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent; border: none;")
        title_row.addWidget(title)
        title_row.addWidget(_InfoButton(T("priv_levels_group_tooltip")))
        title_row.addStretch()
        text_col.addLayout(title_row)

        desc = QLabel(T("priv_levels_group_desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        text_col.addWidget(desc)

        h.addLayout(text_col, 1)

        chevron_closed = FIF.CHEVRON_RIGHT_MED if hasattr(FIF, "CHEVRON_RIGHT_MED") else FIF.RIGHT_ARROW
        chevron_open = FIF.CHEVRON_DOWN_MED if hasattr(FIF, "CHEVRON_DOWN_MED") else FIF.DOWN

        toggle_btn = HOTSButton(chevron_closed, DARK["fg2"], "", accent=False, glyph_color=DARK["accent"])
        toggle_btn.setFixedWidth(44)
        attach_fluent_tip(toggle_btn, T("par_categories_expand"))
        h.addWidget(toggle_btn, 0, Qt.AlignVCenter)

        outer_lay.addWidget(header)
        self._antispy_levels_header = header

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {DARK['border_faint']}; border: none;")
        outer_lay.addWidget(sep)

        body = QWidget()
        body.setStyleSheet("background: transparent; border: none;")
        bv = QVBoxLayout(body)
        bv.setContentsMargins(16, 10, 16, 14)
        bv.setSpacing(10)

        for cfg in level_configs:
            bv.addWidget(self._make_level_card(cfg))
            bv.addSpacing(2)

        outer_lay.addWidget(body)

        section_state = {"expanded": getattr(self, "_antispy_levels_expanded", False)}

        def _apply_section_state(expanded: bool):
            body.setVisible(expanded)
            sep.setVisible(expanded)
            attach_fluent_tip(toggle_btn, T("par_categories_collapse") if expanded else T("par_categories_expand"))
            toggle_btn.set_icon(chevron_open if expanded else chevron_closed, DARK["fg2"], glyph_color=DARK["accent"])
            toggle_btn.set_accent(False)

        def _toggle_section():
            expanded = not section_state["expanded"]
            section_state["expanded"] = expanded
            self._antispy_levels_expanded = expanded  # przeżywa refresh_content()/rebuild karty
            _apply_section_state(expanded)

        toggle_btn.clicked.connect(_toggle_section)
        _apply_section_state(section_state["expanded"])

        return outer

    def _make_level_card(self, cfg: dict) -> QWidget:
        level = cfg["level"]
        accent = cfg["badge_color"]

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent; border: none;")
        wrap_lay = QVBoxLayout(wrapper)
        wrap_lay.setContentsMargins(0, 0, 0, 0)
        wrap_lay.setSpacing(4)

        card = self._card_frame(accent)
        info_lay = card.property("info_lay")
        btn_lay = card.property("btn_lay")

        title_row = QHBoxLayout()
        ico = IconWidget(cfg["icon"])
        ico.setFixedSize(16, 16)
        ico.setIcon(colored_svg_icon(cfg["icon"], QColor(accent), sizes=(16,)))
        title_row.addWidget(ico)
        t = QLabel(T(cfg["label_key"]))
        t.setStyleSheet(f"color: {DARK['fg']}; font-size: 12pt; background: transparent;")
        title_row.addWidget(t)
        title_row.addStretch()
        info_lay.addLayout(title_row)

        items_status = AntiSpyManager.get_items_status(level)
        active = any(items_status.values())
        items_active, items_total = _level_counts(level)
        level_ids = {it["id"] for it in _items_for_level(level)}
        drifted_here = self._drifted_ids & level_ids
        if drifted_here:
            status_txt = T("priv_level_status_drift", n=len(drifted_here))
            status_fg = DARK["red"]
        else:
            status_txt = T("priv_level_status", active=items_active, total=items_total)
            status_fg = DARK["green"] if items_active == items_total else DARK["fg2"]
        st_lbl = QLabel(status_txt)
        st_lbl.setStyleSheet(f"color: {status_fg}; font-size: 9pt; background: transparent;")
        info_lay.addWidget(st_lbl)

        gear_btn = QPushButton()
        gear_btn.setIcon(colored_svg_icon(FIF.SETTING, QColor(DARK["fg2"]), sizes=(13,)))
        gear_btn.setIconSize(QSize(13, 13))
        gear_btn.setFixedSize(24, 24)
        gear_btn.setFlat(True)
        gear_btn.setCursor(Qt.PointingHandCursor)
        attach_fluent_tip(gear_btn, T("priv_gear_tooltip"))
        gear_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid transparent; border-radius: 4px; }"
            f"QPushButton:hover {{ background: {DARK['btn_hover']}; border: 1px solid {DARK['border']}; }}"
        )
        btn_lay.addWidget(gear_btn)

        btn_color = DARK["green"] if active else DARK["gray"]
        btn_label = T("par_btn_disable") if active else T("par_btn_enable")
        btn_icon = FIF.ACCEPT if active else FIF.CLOSE

        btn = HOTSButton(btn_icon, btn_color, "", accent=False)
        btn.setFixedWidth(44)
        attach_fluent_tip(btn, btn_label)
        btn_lay.addWidget(btn)

        state = dict(cfg)
        state["btn"] = btn
        state["active"] = active
        state["key"] = level
        state["status_lbl"] = st_lbl
        self._antispy_states[level] = state
        btn.clicked.connect(lambda _checked=False, s=state: self._toggle_antispy_module(s))

        wrap_lay.addWidget(card)

        checklist = self._make_checklist(level, state, accent, items_status=items_status)
        gear_btn.clicked.connect(lambda _c=False, w=checklist: w.setVisible(not w.isVisible()))
        wrap_lay.addWidget(checklist)

        return wrapper

    def _make_checklist(self, level: str, module_state: dict, accent: str = None,
                         items_status: dict = None) -> QWidget:
        accent = accent or DARK["accent"]
        checklist = QWidget()
        checklist.setVisible(False)
        checklist.setStyleSheet(
            f"background: {DARK['panel_bg']}; border: 1px solid {DARK['border_faint']}; border-radius: 6px;"
        )
        cl_lay = QVBoxLayout(checklist)
        cl_lay.setContentsMargins(8, 8, 8, 8)
        cl_lay.setSpacing(6)

        hint = QLabel(T("priv_checklist_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent; border: none;")
        cl_lay.addWidget(hint)

        if items_status is None:
            items_status = AntiSpyManager.get_items_status(level)
        checkboxes = {}
        labels = {}
        for item in _items_for_level(level):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(12)

            is_drifted = item["id"] in self._drifted_ids
            is_missing = AntiSpyManager.is_item_missing(item["id"])
            cb_color = DARK["red"] if is_drifted else accent

            cb = TransparentToolButton(FIF.POWER_BUTTON)
            cb.setFixedSize(20, 20)
            cb.setFocusPolicy(Qt.NoFocus)
            if is_missing:
                cb.setCheckable(False)
                cb.setChecked(False)
                cb.setEnabled(False)
                cb.setCursor(Qt.ArrowCursor)
                cb._is_missing_item = True
                _refresh_power_toggle_icon(cb)
                attach_fluent_tip(cb, T("priv_item_missing_tooltip"))
            else:
                cb.setCheckable(True)
                cb.setChecked(items_status.get(item["id"], False))
                cb.setEnabled(True)
                cb.setCursor(Qt.PointingHandCursor)
                cb._on_color = cb_color
                cb._is_drifted_item = is_drifted
                cb.toggled.connect(lambda _checked, b=cb: _refresh_power_toggle_icon(b))
                _refresh_power_toggle_icon(cb)
                if is_drifted:
                    attach_fluent_tip(cb, T("priv_item_drift_tooltip"))
            row.addWidget(cb, 0, Qt.AlignTop)

            lbl_text = _with_warning_suffix(item["id"], T(item["label_key"]))
            if is_missing:
                lbl_text = lbl_text + "  " + T("priv_item_missing_suffix")
            elif is_drifted:
                lbl_text = "⚠ " + lbl_text
            text_col = QVBoxLayout()
            text_col.setContentsMargins(0, 0, 0, 0)
            text_col.setSpacing(1)

            lbl = QLabel(lbl_text)
            lbl.setWordWrap(True)
            lbl.setMinimumWidth(0)
            lbl_color = DARK["fg2"] if is_missing else (DARK["red"] if is_drifted else DARK["fg"])
            lbl.setStyleSheet(f"color: {lbl_color}; background: transparent; font-size: 10pt; border: none; padding-left: 2px;")
            if is_missing:
                lbl.setCursor(Qt.ArrowCursor)
                attach_fluent_tip(lbl, T("priv_item_missing_tooltip"))
            else:
                lbl.setCursor(Qt.PointingHandCursor)
                if is_drifted:
                    attach_fluent_tip(lbl, T("priv_item_drift_tooltip"))
                lbl.mousePressEvent = lambda _e, c=cb: c.setChecked(not c.isChecked())
            text_col.addWidget(lbl)

            desc_key = item.get("desc_key")
            if desc_key:
                desc_lbl = QLabel(T(desc_key))
                desc_lbl.setWordWrap(True)
                desc_lbl.setMinimumWidth(0)
                desc_fg = DARK["border"] if is_missing else DARK["fg2"]
                desc_lbl.setStyleSheet(f"color: {desc_fg}; background: transparent; font-size: 8.5pt; border: none; padding-left: 2px;")
                if is_missing:
                    desc_lbl.setCursor(Qt.ArrowCursor)
                    attach_fluent_tip(desc_lbl, T("priv_item_missing_tooltip"))
                else:
                    desc_lbl.setCursor(Qt.PointingHandCursor)
                    desc_lbl.mousePressEvent = lambda _e, c=cb: c.setChecked(not c.isChecked())
                text_col.addWidget(desc_lbl)

            row.addLayout(text_col, 1)

            cl_lay.addLayout(row)
            checkboxes[item["id"]] = cb
            labels[item["id"]] = lbl

        apply_btn = HOTSButton(FIF.SYNC, accent, T("priv_checklist_apply_btn"), accent=True)
        apply_btn.fit_to_content()
        apply_row = QHBoxLayout()
        apply_row.addStretch()
        apply_row.addWidget(apply_btn)
        apply_row.addStretch()
        cl_lay.addLayout(apply_row)

        checklist_state = {
            "level": level,
            "checkboxes": checkboxes,
            "labels": labels,
            "apply_btn": apply_btn,
            "module_state": module_state,
            "accent": accent,
        }
        self._checklist_states[level] = checklist_state
        apply_btn.clicked.connect(lambda _c=False, s=checklist_state: self._apply_checklist(s))

        return checklist

    def _apply_checklist(self, state: dict):
        level = state["level"]
        busy_key = f"checklist_{level}"
        if busy_key in self._antispy_busy:
            return
        self._antispy_busy.add(busy_key)
        self._mark_op_start()

        apply_btn = state["apply_btn"]
        apply_btn.setEnabled(False)
        apply_btn.set_label(T("par_btn_working"))
        apply_btn.fit_to_content()
        for cb in state["checkboxes"].values():
            cb.setEnabled(False)

        selected_ids = [iid for iid, cb in state["checkboxes"].items() if cb.isChecked()]

        signals = _ChecklistSignals(self)
        # Ta sama kolejność sprzątania co w _toggle_antispy_module wyżej -
        # patrz komentarz tam.
        self._antispy_signals[busy_key] = signals
        self._bg_signal_objs.append(signals)

        def _cleanup_and_handle(ok, warnings, err, s=state, sig=signals, k=busy_key):
            if sig in self._bg_signal_objs:
                self._bg_signal_objs.remove(sig)
            if self._antispy_signals.get(k) is sig:
                del self._antispy_signals[k]
            self._on_checklist_applied(s, ok, warnings, err)

        signals.done.connect(_cleanup_and_handle)

        import threading

        def worker(lvl=level, ids=selected_ids):
            # last_error/last_warnings w AntiSpyManager to dzielony stan
            # klasowy — jeśli dwie operacje (np. dwa różne poziomy) trwają
            # równocześnie, wątek A może nadpisać go zanim wątek B zdąży go
            # odczytać. Dlatego migawkę bierzemy TU, natychmiast po wywołaniu,
            # w tym samym wątku, i przekazujemy ją przez sygnał — zamiast
            # czytać AntiSpyManager.last_error dopiero w UI, gdy inna operacja
            # mogła już go nadpisać.
            err = ""
            try:
                ok = AntiSpyManager.apply_selected(lvl, ids)
                warnings = list(AntiSpyManager.last_warnings)
                if not ok:
                    err = AntiSpyManager.last_error
            except Exception as e:
                ok = False
                err = str(e)
                warnings = []
            signals.done.emit(ok, warnings, err)

        start_bg_thread(worker)

    def _on_checklist_applied(self, state: dict, ok: bool, warnings: list, err: str = ""):
        if not shiboken6.isValid(self):
            return
        # Patrz identyczny komentarz w _on_antispy_module_done wyżej -
        # ten handler pokazuje modal i może wywołać refresh_content(),
        # więc nie powinien nic robić, jeśli okno jest już w trakcie
        # zamykania.
        if is_shutting_down():
            return
        level = state["level"]
        self._antispy_busy.discard(f"checklist_{level}")

        apply_btn = state["apply_btn"]
        apply_btn.setEnabled(True)
        apply_btn.set_label(T("priv_checklist_apply_btn"))
        apply_btn.set_icon(FIF.SYNC, state.get("accent", DARK["accent"]))
        apply_btn.set_accent(True)
        apply_btn.fit_to_content()

        self._sync_checklist_checkboxes(level)
        for iid, cb in state["checkboxes"].items():
            if not AntiSpyManager.is_item_missing(iid):
                cb.setEnabled(True)

        if ok:
            level_ids = {it["id"] for it in _items_for_level(level)}
            self._drifted_ids -= level_ids
            accent = state.get("accent", DARK["accent"])
            for iid, lbl in state.get("labels", {}).items():
                if AntiSpyManager.is_item_missing(iid):
                    continue
                lbl.setText(_with_warning_suffix(iid, T(_LABEL_KEY_BY_ID[iid])))
                lbl.setStyleSheet(f"color: {DARK['fg']}; background: transparent; font-size: 10pt; border: none; padding-left: 2px;")
                attach_fluent_tip(lbl, "")
            for iid, cb in state["checkboxes"].items():
                if AntiSpyManager.is_item_missing(iid):
                    continue
                cb._on_color = accent
                cb._is_drifted_item = False
                _refresh_power_toggle_icon(cb)

        module_state = state["module_state"]
        module_state["active"] = self._level_effective_active(level)
        self._refresh_antispy_btn(module_state)
        self._mark_op_end()

        if not ok:
            err_msg = T("par_antispy_err_msg")
            if err:
                err_msg += f"\n\n{err}"
            HOTSDialog.error(self, T("par_antispy_err_title"), err_msg)
        elif warnings:
            HOTSDialog.info(self, T("par_success_title"),
                            T(module_state["success_label_key"]) + "\n\n" + "\n".join(warnings))
        else:
            HOTSDialog.info(self, T("par_success_title"), T(module_state["success_label_key"]))

    def _sync_checklist_checkboxes(self, level: str):
        cl_state = self._checklist_states.get(level)
        if not cl_state:
            return
        items_status = AntiSpyManager.get_items_status(level)
        for iid, cb in cl_state["checkboxes"].items():
            cb.blockSignals(True)
            cb.setChecked(items_status.get(iid, False))
            cb.blockSignals(False)
            _refresh_power_toggle_icon(cb)

    def _toggle_antispy_module(self, state: dict):
        key = state["key"]
        if key in self._antispy_busy:
            return
        target = not state["active"]

        self._antispy_busy.add(key)
        self._mark_op_start()
        btn = state["btn"]
        btn.setEnabled(False)
        attach_fluent_tip(btn, T("par_btn_working"))

        signals = _AntiSpySignals(self)
        # Kolejność sprzątania: rejestrujemy "signals" w obu miejscach
        # (_antispy_signals[key] i _bg_signal_objs) PRZED podłączeniem
        # slotu, a w samym slocie NAJPIERW wypisujemy się z obu tych
        # rejestrów i dopiero POTEM wołamy właściwą obsługę wyniku
        # (_on_antispy_module_done) - ten sam wzorzec co _cleanup_and_handle
        # w _run_toggle (_parental_shared.py), zamiast osobnego drugiego
        # slotu doczepianego przez _track_bg_signal. Efekt uboczny na plus:
        # _antispy_signals[key] wcześniej nigdy się nie czyścił (tylko
        # nadpisywał przy kolejnym przełączeniu tego samego trybu) - drobny,
        # ograniczony wyciek referencji, teraz też posprzątany.
        self._antispy_signals[key] = signals
        self._bg_signal_objs.append(signals)

        def _cleanup_and_handle(ok, err, s=state, t=target, sig=signals, k=key):
            if sig in self._bg_signal_objs:
                self._bg_signal_objs.remove(sig)
            if self._antispy_signals.get(k) is sig:
                del self._antispy_signals[k]
            self._on_antispy_module_done(s, t, ok, err)

        signals.done.connect(_cleanup_and_handle)

        import threading

        def worker(s=state, t=target):
            # Migawkę last_error/last_warnings bierzemy natychmiast, w tym
            # samym wątku co operacja — inaczej, jeśli równolegle trwa druga
            # operacja (np. inny poziom), do czasu przetworzenia sygnału w UI
            # AntiSpyManager.last_error mógłby już należeć do TEJ drugiej
            # operacji i użytkownik zobaczyłby błędny komunikat.
            err = ""
            try:
                fn = s["enable_fn"] if t else s["disable_fn"]
                ok = fn()
                s["_last_warnings"] = list(AntiSpyManager.last_warnings)
                if not ok:
                    err = AntiSpyManager.last_error
            except Exception as e:
                ok = False
                err = str(e)
                s["_last_warnings"] = []
            signals.done.emit(ok, err)

        start_bg_thread(worker)

    def _on_antispy_module_done(self, state: dict, target: bool, ok: bool, err: str = ""):
        if not shiboken6.isValid(self):
            return
        # Ten handler dociera tu też wtedy, gdy operacja w tle skończyła się
        # dosłownie w trakcie zamykania okna (patrz processEvents() w
        # _on_close_event() w app.py - celowo "domyka" kolejkę sygnałów
        # Qt.QueuedConnection z wątków roboczych, ZANIM Qt zacznie niszczyć
        # widgety). Bez tej strażniczki modal HOTSDialog.info/error() poniżej
        # (zagnieżdżona pętla zdarzeń) albo self._mark_op_end() ->
        # refresh_content() (pełne przebudowanie strony) mogłyby odpalić się
        # w środku sekwencji zamykania - to dokładnie ten sam rodzaj wyścigu
        # co 0xc0000374, tylko na etapie UI zamiast wątku/GC. Okno i tak się
        # zaraz zamknie, więc pokazywanie wyniku nie ma odbiorcy.
        if is_shutting_down():
            return
        key = state["key"]
        self._antispy_busy.discard(key)
        btn = state["btn"]
        btn.setEnabled(True)

        if not ok:
            self._refresh_antispy_btn(state)
            self._mark_op_end()
            err_msg = T("par_antispy_err_msg")
            if err:
                err_msg += f"\n\n{err}"
            HOTSDialog.error(self, T("par_antispy_err_title"), err_msg)
            return

        state["active"] = target
        self._refresh_antispy_btn(state)
        self._sync_checklist_checkboxes(key)
        self._mark_op_end()
        msg_key = "par_success_on" if target else "par_success_off"
        base_msg = T(msg_key, label=T(state["success_label_key"]))
        warnings = state.get("_last_warnings") or []
        if warnings:
            HOTSDialog.info(self, T("par_success_title"), base_msg + "\n\n" + "\n".join(warnings))
        else:
            HOTSDialog.info(self, T("par_success_title"), base_msg)

    def _refresh_antispy_btn(self, state: dict):
        btn    = state["btn"]
        active = state["active"]
        color  = DARK["green"] if active else DARK["gray"]
        label  = T("par_btn_disable") if active else T("par_btn_enable")
        icon   = FIF.ACCEPT if active else FIF.CLOSE

        attach_fluent_tip(btn, label)
        btn.set_icon(icon, color)
        btn.set_accent(False)

        st_lbl = state.get("status_lbl")
        if st_lbl is not None:
            level = state["key"]
            items_active, items_total = _level_counts(level)
            level_ids = {it["id"] for it in _items_for_level(level)}
            drifted_here = self._drifted_ids & level_ids
            if drifted_here:
                st_lbl.setText(T("priv_level_status_drift", n=len(drifted_here)))
                st_lbl.setStyleSheet(f"color: {DARK['red']}; font-size: 9pt; background: transparent;")
            else:
                st_lbl.setText(T("priv_level_status", active=items_active, total=items_total))
                st_lbl.setStyleSheet(
                    f"color: {DARK['green'] if items_active == items_total else DARK['fg2']}; "
                    f"font-size: 9pt; background: transparent;"
                )
