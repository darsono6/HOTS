import os
import re
import sys
import copy
import time
import ctypes
import threading
import difflib

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QScrollArea, QSizePolicy,
    QTextEdit, QMenu, QApplication, QFileDialog, QStyledItemDelegate,
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QPoint, QSize, QRect, QObject, QProcess,
)
from PySide6.QtGui import (
    QColor, QFont, QIcon, QPixmap, QAction, QSyntaxHighlighter, QTextCharFormat, QPalette,
    QCursor, QGuiApplication,
)

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon,
    PushButton, ToolButton, SearchLineEdit, BodyLabel, TitleLabel,
    SubtitleLabel, CaptionLabel, CardWidget, ScrollArea,
    ToggleButton, SwitchButton, InfoBar, InfoBarIcon, InfoBarPosition,
    MessageBox, Dialog, StateToolTip, ProgressBar, Flyout,
    FlyoutViewBase, setTheme, Theme, setThemeColor,
    TransparentPushButton,
)
from qfluentwidgets import FluentIcon as FIF
try:
    from qfluentwidgets import IndeterminateProgressRing
except ImportError:
    IndeterminateProgressRing = None

from .constants import DARK, HOSTS_PATH, IS_LIGHT_THEME, accent_rgba, load_settings, save_settings
from .i18n import T, set_lang, current_lang, LANGUAGES
from .core import (
    parse_hosts, save_hosts, entries_to_text, list_backups,
    import_from_path, export_to_path, is_valid_ip, MAX_ACTIVE_ENTRIES,
)
from .widgets_qt import (
    HOTSButton, HOTSDialog, apply_global_style, h_separator,
    v_separator, enable_acrylic, enable_rounded_corners,
    HOTSContextMenu, attach_line_edit_context_menu, attach_text_edit_context_menu,
)


_ACCENT_GOLD = QColor(DARK["accent"])

_EXTERNAL_ACTIVATE_EVENT_NAME = "Global\\HOTS_HostsEditor_ActivateEvent"


def _low_integrity_security_attributes():
    try:
        class SECURITY_ATTRIBUTES(ctypes.Structure):
            _fields_ = [
                ("nLength", ctypes.c_ulong),
                ("lpSecurityDescriptor", ctypes.c_void_p),
                ("bInheritHandle", ctypes.c_int),
            ]

        sddl = "D:(A;;GA;;;WD)S:(ML;;NW;;;LW)"
        p_sd = ctypes.c_void_p()
        ok = ctypes.windll.advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
            ctypes.c_wchar_p(sddl), 1, ctypes.byref(p_sd), None
        )
        if not ok or not p_sd:
            return None

        sa = SECURITY_ATTRIBUTES()
        sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
        sa.lpSecurityDescriptor = p_sd
        sa.bInheritHandle = False
        return sa
    except Exception:
        return None


def _parse_saved_geometry(geo_str: str):
    m = re.match(r"^(\d+)x(\d+)(?:\+(-?\d+)\+(-?\d+))?$", geo_str or "")
    if not m:
        return 900, 580, None, None
    w, h = int(m.group(1)), int(m.group(2))
    if m.group(3) is None:
        return w, h, None, None
    return w, h, int(m.group(3)), int(m.group(4))


def _geometry_fits_on_screen(x: int, y: int, w: int, h: int) -> bool:
    win_rect = QRect(x, y, w, h)
    return any(win_rect.intersects(screen.availableGeometry())
               for screen in QApplication.screens())


def _centered_position(w: int, h: int):
    screen = QGuiApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
    if screen is None:
        return None, None
    geo = screen.availableGeometry()
    x = geo.x() + (geo.width() - w) // 2
    y = geo.y() + (geo.height() - h) // 2
    return x, y


class ClickableLabel(QLabel):
    clicked = Signal()
    def mousePressEvent(self, event):
        from PySide6.QtCore import Qt
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class SaveWorker(QThread):
    finished  = Signal(bool)
    error_msg = Signal(str)

    def __init__(self, hosts_path, entries):
        super().__init__()
        self._path    = hosts_path
        self._entries = entries

    def run(self):
        try:
            save_hosts(self._path, self._entries)
            self.finished.emit(True)
        except PermissionError:
            self.error_msg.emit(T("save_perm_msg"))
        except Exception as ex:
            self.error_msg.emit(str(ex))


class _HostsHighlighter(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        self._fmt_comment = QTextCharFormat()
        self._fmt_comment.setForeground(QColor(DARK["fg2"]))
        self._fmt_active  = QTextCharFormat()
        self._fmt_active.setForeground(QColor(DARK["green"]))

    def highlightBlock(self, text: str):
        stripped = text.strip()
        if not stripped:
            return
        if stripped.startswith("#"):
            self.setFormat(0, len(text), self._fmt_comment)
        else:
            self.setFormat(0, len(text), self._fmt_active)


class _SortHeaderItem(QTableWidgetItem):
    def __init__(self, text: str, active: bool = False):
        super().__init__(text)
        if active:
            self.setForeground(QColor(DARK["accent"]))
        else:
            self.setForeground(QColor(DARK["fg2"]))


def _sort_px(up: bool) -> QPixmap:
    from PySide6.QtGui import QPainter, QPainterPath
    sz = 9
    px = QPixmap(sz, sz)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(DARK["accent"]))
    p.setPen(Qt.NoPen)
    path = QPainterPath()
    if up:
        path.moveTo(sz / 2, 1)
        path.lineTo(sz - 1, sz - 1)
        path.lineTo(1,      sz - 1)
    else:
        path.moveTo(1,      1)
        path.lineTo(sz - 1, 1)
        path.lineTo(sz / 2, sz - 1)
    path.closeSubpath()
    p.drawPath(path)
    p.end()
    return px


class _NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        from PySide6.QtWidgets import QStyle
        option.state &= ~QStyle.State_HasFocus
        super().paint(painter, option, index)


class _AntiSpyReapplySignals(QObject):
    done = Signal(dict)


class _AntiSpyWatchdogSignals(QObject):
    done = Signal(list, list)


class _ExternalActivateSignals(QObject):
    activate = Signal()


class HostsEditor(FluentWindow):
    def __init__(self, on_before_show=None):
        super().__init__()

        self._settings = load_settings()
        set_lang(self._settings.get("language", "en"))
        self.entries: list = []
        self._dirty  = False
        self._raw_mode = False
        self._bg_signal_objs: list = []


        self._page_route_map: dict = {}

        self._options_nav_widgets: set = set()
        self._options_click_guard_ts = 0.0
        self._options_click_guard_ms = 350

        setTheme(Theme.LIGHT if IS_LIGHT_THEME else Theme.DARK)
        setThemeColor(_ACCENT_GOLD)

        self.setWindowTitle("HOTS Hosts")
        w, h, x, y = _parse_saved_geometry(self._settings.get("geometry", ""))
        self.resize(w, h)
        if x is not None and y is not None and _geometry_fits_on_screen(x, y, w, h):
            self.move(x, y)
        else:
            cx, cy = _centered_position(w, h)
            if cx is not None and cy is not None:
                self.move(cx, cy)
        self.setMinimumSize(900, 640)

        _ico = self._find_asset("logo.ico")
        if _ico:
            self.setWindowIcon(QIcon(_ico))

        _logo_top = self._find_asset("logoS.png")

        self._build_navigation()
        self.navigationInterface.setExpandWidth(200)
        self._build_main_view()
        self._build_backup_page()

        self._load()

        try:
            tb = self.titleBar
            tb.titleLabel.setStyleSheet(
                f"color: {DARK['accent']}; font-size: 13pt; font-weight: bold; background: transparent;"
            )
            if _logo_top:
                self._setup_top_logo(_logo_top)
            try:
                self.navigationInterface.setReturnButtonVisible(True)
            except Exception:
                pass
        except Exception as e:
            print(f"Titlebar customization warning: {e}")

        self.closeEvent = self._on_close_event

        if on_before_show is not None:
            try:
                on_before_show()
            except Exception as e:
                print(f"on_before_show hook warning: {e}")

        self.show()
        self._start_external_activation_listener()
        QTimer.singleShot(1500, self._check_antispy_watchdog)

        try:
            hwnd = int(self.winId())
            apply_global_style(QApplication.instance())
            enable_rounded_corners(hwnd)
            enable_acrylic(hwnd, dark=not IS_LIGHT_THEME)
        except Exception as e:
            print(f"Windows visual effects warning: {e}")

    def _start_external_activation_listener(self):
        self._ext_activate_signals = _ExternalActivateSignals()
        self._ext_activate_signals.activate.connect(self._restore_and_activate)

        def _listen():
            try:
                sa = _low_integrity_security_attributes()
                sa_arg = ctypes.byref(sa) if sa is not None else None
                handle = ctypes.windll.kernel32.CreateEventW(
                    sa_arg, False, False, _EXTERNAL_ACTIVATE_EVENT_NAME
                )
                if not handle:
                    return
                INFINITE = 0xFFFFFFFF
                WAIT_OBJECT_0 = 0x0
                while True:
                    result = ctypes.windll.kernel32.WaitForSingleObject(handle, INFINITE)
                    if result != WAIT_OBJECT_0:
                        break
                    self._ext_activate_signals.activate.emit()
            except Exception as e:
                print(f"External activation listener warning: {e}")

        self._ext_activate_thread = threading.Thread(target=_listen, daemon=True)
        self._ext_activate_thread.start()

    def _restore_and_activate(self):
        try:
            state = self.windowState()
            if state & Qt.WindowMinimized:
                self.setWindowState((state & ~Qt.WindowMinimized) | Qt.WindowActive)
            self.showNormal()
            self.raise_()
            self.activateWindow()
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
        except Exception as e:
            print(f"Restore/activate warning: {e}")

    def _setup_deselect_on_outside_click(self):
        from PySide6.QtCore import Qt as _Qt
        self.table.setFocusPolicy(_Qt.ClickFocus)

        targets = [
            getattr(self, "_toolbar_frame", None),
            getattr(self, "_status_bar_frame", None),
            getattr(self, "status_bar", None),
            getattr(self, "titleBar", None),
        ]
        for w in targets:
            if w is not None:
                w.installEventFilter(self)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent

        if event.type() == QEvent.Type.MouseButtonPress and obj in self._options_nav_widgets:
            now = time.monotonic()
            if (now - self._options_click_guard_ts) * 1000 < self._options_click_guard_ms:
                return True
            self._options_click_guard_ts = now

        if event.type() == QEvent.Type.MouseButtonPress and obj in (
            getattr(self, "_toolbar_frame", None),
            getattr(self, "_status_bar_frame", None),
            getattr(self, "status_bar", None),
            getattr(self, "titleBar", None),
        ):
            QTimer.singleShot(0, self._safe_clear_table_selection)
        return super().eventFilter(obj, event)

    def _safe_clear_table_selection(self):
        try:
            if hasattr(self, 'table') and self.table is not None:
                self.table.clearSelection()
                self.table.setCurrentCell(-1, -1)
        except Exception:
            pass

    def _check_antispy_watchdog(self):
        try:
            self._privacy_page.set_watchdog_running(True)
        except Exception as e:
            print(f"AntiSpy watchdog warning: {e}")

        signals = _AntiSpyWatchdogSignals()
        signals.done.connect(self._on_antispy_watchdog_checked)
        self._antispy_watchdog_signals = signals
        self._bg_signal_objs.append(signals)

        def worker():
            try:
                from .core_antispy import AntiSpyManager, run_startup_seed
                run_startup_seed()
                drifted, restored = AntiSpyManager.get_drifted_items()
            except Exception as e:
                print(f"AntiSpy watchdog warning: {e}")
                drifted, restored = [], []
            signals.done.emit(drifted, restored)

        threading.Thread(target=worker, daemon=True).start()

    def _on_antispy_watchdog_checked(self, drifted_items: list, restored_items: list):
        restored_items = restored_items or []
        self._antispy_drifted_ids = set(drifted_items)
        try:
            self._privacy_page.set_drifted(self._antispy_drifted_ids)
        except Exception as e:
            print(f"AntiSpy watchdog warning: {e}")

        if restored_items:
            try:
                self._show_antispy_restored_notice(restored_items)
            except Exception as e:
                print(f"AntiSpy watchdog warning: {e}")

        if not drifted_items:
            return
        try:
            from .core_antispy import ITEMS
            names_map = {
                "basic": T("par_antispy_basic_btn"),
                "medium": T("par_antispy_medium_btn"),
                "advanced": T("par_antispy_advanced_btn"),
            }
            item_levels = {it["id"]: it["level"] for it in ITEMS}
            levels_drifted = sorted({item_levels[i] for i in drifted_items if i in item_levels},
                                     key=("basic", "medium", "advanced").index)
            modules_txt = ", ".join(names_map[lvl] for lvl in levels_drifted)

            bar = InfoBar(
                icon=InfoBarIcon.WARNING,
                title=T("antispy_watchdog_title"),
                content=T("antispy_watchdog_msg", modules=modules_txt),
                orient=Qt.Vertical,
                isClosable=True,
                duration=-1,
                position=InfoBarPosition.TOP,
                parent=self,
            )
            reapply_btn = HOTSButton(FIF.SYNC, DARK["accent"], T("antispy_watchdog_reapply_btn"))
            reapply_btn.fit_to_content()

            action_row = QWidget()
            action_lay = QHBoxLayout(action_row)
            action_lay.setContentsMargins(0, 0, 0, 0)
            action_lay.setSpacing(6)

            busy_spinner = None
            if IndeterminateProgressRing is not None:
                busy_spinner = IndeterminateProgressRing()
                busy_spinner.setFixedSize(14, 14)
                busy_spinner.setStrokeWidth(2)
                busy_spinner.setVisible(False)
                action_lay.addWidget(busy_spinner, 0, Qt.AlignVCenter)

            busy_lbl = QLabel(T("priv_op_working"))
            busy_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 8pt; background: transparent;")
            busy_lbl.setVisible(False)
            action_lay.addWidget(busy_lbl, 0, Qt.AlignVCenter)

            action_lay.addWidget(reapply_btn, 0, Qt.AlignVCenter)

            def _on_reapply_clicked(_c=False, d=list(drifted_items), b=bar,
                                     btn=reapply_btn, spin=busy_spinner, lbl=busy_lbl):
                btn.setEnabled(False)
                btn.setVisible(False)
                if spin is not None:
                    spin.setVisible(True)
                lbl.setVisible(True)
                self._reapply_antispy_drift(d, b)

            reapply_btn.clicked.connect(_on_reapply_clicked)
            bar.addWidget(action_row)
            bar.show()
        except Exception as e:
            print(f"AntiSpy watchdog warning: {e}")

    def _show_antispy_restored_notice(self, restored_items: list):
        from .core_antispy import ITEMS
        names_map = {
            "basic": T("par_antispy_basic_btn"),
            "medium": T("par_antispy_medium_btn"),
            "advanced": T("par_antispy_advanced_btn"),
        }
        item_levels = {it["id"]: it["level"] for it in ITEMS}
        levels_restored = sorted({item_levels[i] for i in restored_items if i in item_levels},
                                  key=("basic", "medium", "advanced").index)
        modules_txt = ", ".join(names_map[lvl] for lvl in levels_restored)

        InfoBar.info(
            title=T("antispy_watchdog_restored_title"),
            content=T("antispy_watchdog_restored_msg", modules=modules_txt),
            orient=Qt.Horizontal,
            isClosable=True,
            duration=5000,
            position=InfoBarPosition.TOP,
            parent=self,
        )

    def _reapply_antispy_drift(self, drifted_items: list, bar):
        from .core_antispy import AntiSpyManager

        signals = _AntiSpyReapplySignals()
        signals.done.connect(lambda results: self._on_antispy_reapply_done(results, bar))
        self._antispy_reapply_signals = signals
        self._bg_signal_objs.append(signals)

        def worker(ids=list(drifted_items)):
            results = {i: AntiSpyManager.enable_item(i) for i in ids}
            signals.done.emit(results)

        threading.Thread(target=worker, daemon=True).start()

    def _on_antispy_reapply_done(self, results: dict, bar):
        try:
            bar.close()
        except Exception:
            pass

        fixed_ids = {i for i, ok in results.items() if ok}
        self._antispy_drifted_ids -= fixed_ids
        try:
            self._privacy_page.set_drifted(self._antispy_drifted_ids)
        except Exception as e:
            print(f"AntiSpy watchdog warning: {e}")

        if all(results.values()):
            InfoBar.success(
                title=T("save_success_title"),
                content=T("antispy_watchdog_reapply_success"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )
        else:
            from .core_antispy import ITEMS
            label_by_id = {it["id"]: T(it["label_key"]) for it in ITEMS}
            failed = [label_by_id.get(i, i) for i, ok in results.items() if not ok]
            HOTSDialog.error(self, T("par_antispy_err_title"),
                             T("par_antispy_err_msg") + "\n\n" + ", ".join(failed))

    def _setup_top_logo(self, path: str):
        try:
            tb = self.titleBar
            if hasattr(tb, "iconLabel"):
                tb.iconLabel.hide()
            tb.titleLabel.hide()

            pix = QPixmap(path)
            if pix.isNull():
                return

            margin = 6
            scale_factor = 0.50
            target_h = max(int((tb.height() - margin) * scale_factor), 12)
            scaled = pix.scaledToHeight(target_h, Qt.SmoothTransformation)

            self._logo_lbl = QLabel(tb)
            self._logo_lbl.setPixmap(scaled)
            self._logo_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
            self._logo_lbl.setStyleSheet("background: transparent;")
            self._logo_lbl.adjustSize()

            start_x = tb.iconLabel.x() if hasattr(tb, "iconLabel") else 10
            y = (tb.height() - self._logo_lbl.height()) // 2
            self._logo_lbl.move(start_x, y)
            self._logo_lbl.show()
            self._logo_lbl.raise_()
        except Exception as e:
            print(f"Top logo setup warning: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._adjust_columns_on_resize)

    def _find_asset(self, name: str) -> str:
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        p = os.path.join(base, name)
        return p if os.path.exists(p) else ""

    def _nav(self, fn, route_key=None):
        def _wrapper():
            indices = self._selected_indices()

            def _deferred():
                fn()
                if route_key:
                    current = self.stackedWidget.currentWidget()
                    if current is not None and current is not self._main_widget:
                        self._page_route_map[current.objectName()] = route_key
                    self.navigationInterface.setCurrentItem(route_key)
                if indices and hasattr(self, "table"):
                    for row in range(self.table.rowCount()):
                        item = self.table.item(row, 0)
                        if item and item.data(Qt.UserRole) in indices:
                            self.table.selectRow(row)

            QTimer.singleShot(0, _deferred)

        return _wrapper

    def _build_navigation(self):
        nav = self.navigationInterface

        nav.addItem(routeKey="repair",    icon=FIF.CODE,      text=T("btn_repair"),      onClick=self._nav(self._repair, "repair"),    position=NavigationItemPosition.TOP)
        nav.addItem(routeKey="default",   icon=FIF.BROOM,     text=T("btn_default"),     onClick=self._nav(self._restore_default, "default"), position=NavigationItemPosition.TOP)
        nav.addItem(routeKey="check_dom", icon=FIF.SEARCH,    text=T("btn_check_dom"),   onClick=self._nav(self._diag_existence, "check_dom"), position=NavigationItemPosition.TOP)
        nav.addItem(routeKey="malware",   icon=FIF.VPN,       text=T("btn_malware"),     onClick=self._nav(self._diag_malware, "malware"), position=NavigationItemPosition.TOP)
        nav.addItem(routeKey="parental",  icon=FIF.PEOPLE,    text=T("btn_parental"),    onClick=self._nav(self._open_parental_control, "parental"), position=NavigationItemPosition.TOP)
        nav.addItem(routeKey="privacy",   icon=FIF.HIDE,      text=T("btn_privacy"),     onClick=self._nav(self._open_privacy, "privacy"), position=NavigationItemPosition.TOP)

        nav.addItem(routeKey="options",   icon=FIF.SETTING,   text=T("btn_options"),     selectable=False,        position=NavigationItemPosition.BOTTOM)
        nav.addItem(routeKey="about",     icon=FIF.INFO,      text=T("opt_about"),       onClick=self._nav(self._about, "about"),     position=NavigationItemPosition.BOTTOM, parentRouteKey="options")
        nav.addItem(routeKey="support",   icon=FIF.HEART,     text=T("opt_support"),     onClick=self._nav(self._support, "support"),   position=NavigationItemPosition.BOTTOM, parentRouteKey="options")
        nav.addItem(routeKey="rawview",   icon=FIF.DOCUMENT,  text=T("opt_show_raw"),    onClick=self._nav(self._show_raw_view, "rawview"), position=NavigationItemPosition.BOTTOM, parentRouteKey="options")
        nav.addItem(routeKey="password",  icon=FIF.HIDE,      text=T("opt_pass_off"),    onClick=self._nav(self._manage_password), position=NavigationItemPosition.BOTTOM, parentRouteKey="options")
        nav.addItem(routeKey="language",  icon=FIF.GLOBE,     text=T("opt_language"),    onClick=self._nav(self._change_language), position=NavigationItemPosition.BOTTOM, parentRouteKey="options")
        nav.addItem(routeKey="theme",     icon=FIF.PALETTE,   text=T("opt_appearance"),      onClick=self._nav(self._change_accent_color), position=NavigationItemPosition.BOTTOM, parentRouteKey="options")

        for _rk in ("options", "about", "support", "rawview", "password", "language", "theme"):
            _w = nav.widget(_rk)
            if _w is not None:
                self._options_nav_widgets.add(_w)
                _w.installEventFilter(self)

    def _build_main_view(self):
        self._main_widget = QWidget()
        self._main_widget.setObjectName("mainWidget")
        self._main_widget.setStyleSheet("#mainWidget { background: transparent; border: none; }")

        root = QVBoxLayout(self._main_widget)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        gold_line = QFrame()
        gold_line.setFixedHeight(2)
        gold_line.setStyleSheet(f"background-color: {DARK['accent']}; border: none;")
        root.addWidget(gold_line)

        root.addWidget(self._build_toolbar())

        self._table_widget = self._build_table()
        self._raw_widget   = self._build_raw_view()
        self._raw_widget.hide()

        root.addWidget(self._table_widget, 1)
        root.addWidget(self._raw_widget,   1)

        root.addWidget(self._build_status_bar())

        self._setup_deselect_on_outside_click()

        self.addSubInterface(interface=self._main_widget, icon=FIF.HOME, text="HOTS Hosts")
        self.navigationInterface.widget("mainWidget").clicked.connect(self._show_table_view)

    def _build_backup_page(self):
        from .dialogs import BackupManagerPage
        self._backup_page = BackupManagerPage(self, HOSTS_PATH, on_restore=self._load,
                                              on_backup_count_changed=self._update_status)
        self.addSubInterface(interface=self._backup_page, icon=FIF.SAVE, text=T("bak_title"))
        self.navigationInterface.widget("backupInterface").hide()

        from .dialogs import DiagnosticsPage
        self._diagnostics_page = DiagnosticsPage(self)
        self.addSubInterface(interface=self._diagnostics_page, icon=FIF.SEARCH, text=T("diag_title_existence"))
        self.navigationInterface.widget("diagnosticsInterface").hide()

        from .dialogs import ParentalPage
        self._parental_page = ParentalPage(self)
        self.addSubInterface(interface=self._parental_page, icon=FIF.PEOPLE, text=self._parental_page._title_text)
        self.navigationInterface.widget("parentalInterface").hide()

        from .dialogs import PrivacyPage
        self._privacy_page = PrivacyPage(self)
        self.addSubInterface(interface=self._privacy_page, icon=FIF.HIDE, text=self._privacy_page._title_text)
        self.navigationInterface.widget("privacyInterface").hide()
        self._antispy_drifted_ids = set()
        self._privacy_page.busy_changed.connect(self._set_navigation_locked)

        from .dialogs import SupportPage
        self._support_page = SupportPage(self)
        self.addSubInterface(interface=self._support_page, icon=FIF.HEART, text=T("sup_title"))
        self.navigationInterface.widget("supportInterface").hide()

        from .dialogs import AboutPage
        self._about_page = AboutPage(self)
        self.addSubInterface(interface=self._about_page, icon=FIF.INFO, text=self._about_page._title_text)
        self.navigationInterface.widget("aboutInterface").hide()

        self.stackedWidget.currentChanged.connect(self._on_stack_changed)

    def _set_navigation_locked(self, locked: bool):
        self.navigationInterface.setEnabled(not locked)
        tip = T("priv_nav_locked_tooltip") if locked else ""
        self.navigationInterface.setToolTip(tip)

    def _on_stack_changed(self, index):
        if self._raw_mode and self.stackedWidget.currentWidget() is not self._main_widget:
            self._show_table_view()

        widget = self.stackedWidget.currentWidget()
        if widget is not None:
            visible_key = self._page_route_map.get(widget.objectName(), widget.objectName())
            self.navigationInterface.setCurrentItem(visible_key)

        if widget is not self._main_widget and hasattr(self, "_search_edit") and self._search_edit.text():
            self._search_edit.clear()

    def _build_toolbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("toolbar")
        self._toolbar_frame = bar
        bar.setFixedHeight(68)
        bar.setStyleSheet(f"#toolbar {{ background-color: {DARK['toolbar_bg']}; border-bottom: 1px solid {DARK['border_faint']}; }}")

        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(8)

        hov_frame = QFrame()
        hov_frame.setObjectName("hovInfo")
        hov_frame.setFixedWidth(165)
        hov_frame.setStyleSheet(
            "QFrame#hovInfo {"
            f"  background: {DARK['border_faint']};"
            f"  border: 1px solid {DARK['border_soft']};"
            "  border-radius: 8px;"
            "}"
        )
        hov_lay = QHBoxLayout(hov_frame)
        hov_lay.setContentsMargins(10, 0, 10, 0)
        hov_lay.setSpacing(8)
        hov_lay.setAlignment(Qt.AlignCenter)

        hov_icon_lbl = QLabel()
        hov_icon_lbl.setFixedSize(18, 18)
        hov_icon_lbl.setAlignment(Qt.AlignCenter)
        hov_icon_lbl.setStyleSheet("background: transparent; border: none;")
        hov_lay.addWidget(hov_icon_lbl)

        hov_text_lbl = QLabel("")
        hov_text_lbl.setStyleSheet(
            f"color: {DARK['fg2']}; font-size: 10pt; background: transparent; border: none;"
        )
        hov_lay.addWidget(hov_text_lbl)

        def _set_hov(icon, label, color=None):
            if color is None:
                color = DARK['accent']
            try:
                px = icon.icon(color=QColor(color)).pixmap(QSize(16, 16))
                hov_icon_lbl.setPixmap(px)
            except Exception:
                hov_icon_lbl.clear()
            hov_text_lbl.setText(label)
            hov_text_lbl.setStyleSheet(
                f"color: {color}; font-size: 10pt; font-weight: 600;"
                f" background: transparent; border: none;"
            )

        def _clear_hov():
            hov_icon_lbl.clear()
            hov_text_lbl.setText("")
            hov_text_lbl.setStyleSheet(
                f"color: {DARK['fg2']}; font-size: 10pt;"
                f" background: transparent; border: none;"
            )

        self._hov_filters: list = []

        def _hook(btn, icon, label):
            class _F(QObject):
                def eventFilter(self_, obj, event):
                    from PySide6.QtCore import QEvent
                    t = event.type()
                    if t == QEvent.Type.Enter:
                        _set_hov(icon, label)
                    elif t == QEvent.Type.Leave:
                        _clear_hov()
                    return False
            f = _F(btn)
            btn.installEventFilter(f)
            self._hov_filters.append(f)

        def _tb(icon, color, label_key, slot):
            b = HOTSButton(icon, color, "")
            b.setFixedWidth(44)
            b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            b.clicked.connect(slot)
            _hook(b, icon, T(label_key))
            return b

        btn_add     = _tb(FIF.ADD,     DARK['accent'], "btn_add",     self._add)
        btn_edit    = _tb(FIF.EDIT,    DARK['accent'], "btn_edit",    self._edit)
        btn_toggle  = _tb(FIF.SYNC,    DARK['accent'], "btn_toggle",  self._toggle)
        btn_delete  = _tb(FIF.DELETE,  DARK['accent'], "btn_delete",  self._delete)
        btn_backups = _tb(FIF.HISTORY, DARK['accent'], "btn_backups", self._backups)

        self._save_btn = HOTSButton(FIF.SAVE, DARK['accent'], "")
        self._save_btn.setFixedWidth(44)
        self._save_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._save_btn.clicked.connect(self._save)
        _hook(self._save_btn, FIF.SAVE, T("btn_save"))

        btn_import = _tb(FIF.DOWNLOAD, DARK['accent'], "btn_import", self._import)
        btn_export = _tb(FIF.SHARE,    DARK['accent'], "btn_export", self._export)

        lay.addWidget(btn_add)
        lay.addWidget(btn_edit)
        lay.addWidget(btn_toggle)
        lay.addWidget(btn_delete)

        lay.addStretch(1)
        lay.addWidget(hov_frame)
        lay.addStretch(1)

        lay.addWidget(self._save_btn)
        lay.addWidget(btn_backups)
        lay.addWidget(btn_import)
        lay.addWidget(btn_export)

        return bar

    def _load_table_col_widths(self) -> list[int]:
        defaults = [110, 160, 280]
        raw = self._settings.get("table_col_widths", "")
        try:
            parts = [int(x) for x in raw.split(",")]
            if len(parts) == 3 and all(p > 0 for p in parts):
                return parts
        except Exception:
            pass
        return defaults

    def _load_table_sort_state(self) -> tuple[int, bool]:
        try:
            col = int(self._settings.get("table_sort_col", -1))
        except Exception:
            col = -1
        rev = str(self._settings.get("table_sort_reverse", "")).strip().lower() in ("1", "true", "yes")
        return col, rev

    def _build_table(self) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent; border: none;")
        lay = QVBoxLayout(wrapper)
        lay.setContentsMargins(8, 6, 8, 0)
        lay.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setFixedHeight(40)
        
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().sectionResized.connect(self._prevent_slider_escape)
        
        _saved_widths = self._load_table_col_widths()
        self.table.setColumnWidth(0, _saved_widths[0])
        self.table.setColumnWidth(1, _saved_widths[1])
        self.table.setColumnWidth(2, _saved_widths[2])
        self.table.verticalHeader().setDefaultSectionSize(40)

        self.table.setStyleSheet(
            f"QTableWidget {{ background-color: {DARK['table_bg']}; alternate-background-color: {DARK['table_alt_bg']}; "
            f"color: {DARK['fg']}; gridline-color: {DARK['grid_line']}; border: 1px solid {DARK['border_soft']}; "
            f"selection-background-color: transparent; selection-color: {DARK['fg']}; "
            f"font-family: 'Segoe UI'; font-size: 11pt; }}"
            f"QTableWidget::item {{ border-left: none; border-right: none; border-top: none; "
            f"border-bottom: 1px solid {DARK['border_faint']}; padding: 0px 8px; outline: 0; }}"
            f"QTableWidget::item:selected {{ background-color: {accent_rgba(0.10)}; "
            f"border-bottom: 1px solid {accent_rgba(0.12)}; color: {DARK['fg']}; }}"
            f"QTableWidget::item:selected:active {{ background-color: {accent_rgba(0.10)}; }}"
            f"QTableWidget::item:selected:!active {{ background-color: {accent_rgba(0.07)}; }}"
            f"QTableWidget::item:focus {{ outline: 0; border: none; background-color: {accent_rgba(0.10)}; }}"
            f"QHeaderView::section {{ background-color: {DARK['header_bg']}; color: {DARK['fg2']}; "
            f"border: none; border-right: 1px solid {DARK['border_strong']}; border-bottom: 1px solid {DARK['border_soft']}; padding: 4px 8px; "
            f"font-family: 'Segoe UI'; font-size: 11pt; font-weight: normal; }}"
            f"QHeaderView::section:last {{ border-right: none; }}"
            f"QHeaderView::section:hover {{ color: {DARK['fg']}; }}"
        )

        self.table.setItemDelegate(_NoFocusDelegate(self.table))
        self.table.horizontalHeader().sectionClicked.connect(self._sort_col)
        self._sort_col_active, self._sort_col_reverse = self._load_table_sort_state()
        self._update_sort_headers()

        self.table.doubleClicked.connect(lambda _: self._edit())
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        lay.addWidget(self.table)

        return wrapper

    def _prevent_slider_escape(self, logicalIndex, oldSize, newSize):
        if logicalIndex >= 3:
            return
            
        viewport_width = self.table.viewport().width()
        min_comment_col_width = 50 
        
        other_widths = 0
        for i in range(3):
            if i != logicalIndex:
                other_widths += self.table.columnWidth(i)
                
        max_allowed_width = viewport_width - other_widths - min_comment_col_width
        
        min_safe_width = 40
        max_allowed_width = max(min_safe_width, max_allowed_width)
        
        if newSize > max_allowed_width:
            self.table.horizontalHeader().blockSignals(True)
            self.table.setColumnWidth(logicalIndex, max_allowed_width)
            self.table.horizontalHeader().blockSignals(False)

    def _adjust_columns_on_resize(self):
        if not hasattr(self, 'table') or self.table is None:
            return
            
        viewport_width = self.table.viewport().width()
        
        w0 = self.table.columnWidth(0)
        w1 = self.table.columnWidth(1)
        w2 = self.table.columnWidth(2)
        
        total_interactive = w0 + w1 + w2
        min_comment_col_width = 50
        min_safe_width = 40
        
        max_allowed = viewport_width - min_comment_col_width
        
        if total_interactive > max_allowed and max_allowed > 0:
            scale = max_allowed / total_interactive
            
            new_w0 = max(min_safe_width, int(w0 * scale))
            new_w1 = max(min_safe_width, int(w1 * scale))
            new_w2 = max(min_safe_width, max_allowed - new_w0 - new_w1)
            
            self.table.horizontalHeader().blockSignals(True)
            self.table.setColumnWidth(0, new_w0)
            self.table.setColumnWidth(1, new_w1)
            self.table.setColumnWidth(2, new_w2)
            self.table.horizontalHeader().blockSignals(False)

    def _build_raw_view(self) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet(f"background: transparent; border: none;")
        lay = QVBoxLayout(wrapper)
        lay.setContentsMargins(8, 4, 8, 0)
        lay.setSpacing(4)

        from qfluentwidgets import IconWidget as _IconWidget

        hdr_row = QHBoxLayout()
        hdr_row.setSpacing(10)
        hdr_ico = _IconWidget(FIF.DOCUMENT)
        hdr_ico.setFixedSize(22, 22)
        hdr_ico.setIcon(FIF.DOCUMENT.icon(color=QColor(DARK["accent"])))
        hdr_row.addWidget(hdr_ico)
        title = QLabel(T("raw_view_title"))
        title.setStyleSheet(f"color: {DARK['accent']}; font-size: 14pt; font-weight: 600; background: transparent;")
        hdr_row.addWidget(title)
        hdr_row.addStretch()
        lay.addLayout(hdr_row)

        hint = QLabel(T("raw_view_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {DARK['fg2']}; font-size: 10pt; background: transparent;")
        lay.addWidget(hint)

        self._raw_editor = QTextEdit()
        self._raw_editor.setFont(QFont("Consolas", 11))
        self._raw_editor.setStyleSheet(
            f"QTextEdit {{ background-color: {DARK['table_bg']}; color: {DARK['fg']}; "
            f"border: 1px solid {DARK['border_soft']}; font-size: 11pt; }}"
        )
        self._raw_editor.setCursorWidth(2)
        self._raw_editor.setLineWrapMode(QTextEdit.NoWrap)
        self._raw_editor.textChanged.connect(self._raw_on_modified)
        self._raw_editor.cursorPositionChanged.connect(self._raw_highlight_current_line)
        self._raw_highlighter = _HostsHighlighter(self._raw_editor.document())
        attach_text_edit_context_menu(self._raw_editor)
        lay.addWidget(self._raw_editor, 1)
        self._raw_highlight_current_line()
        return wrapper

    def _raw_highlight_current_line(self):
        line_color = QColor(DARK["accent"])
        line_color.setAlpha(35)
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(line_color)
        selection.format.setProperty(selection.format.Property.FullWidthSelection, True)
        selection.cursor = self._raw_editor.textCursor()
        selection.cursor.clearSelection()
        self._raw_editor.setExtraSelections([selection])

    def _populate_raw_view(self):
        text = entries_to_text(self.entries).rstrip("\n")
        self._raw_editor.blockSignals(True)
        self._raw_editor.setPlainText(text)
        self._raw_editor.blockSignals(False)
        self._raw_highlight_current_line()

    def _raw_on_modified(self):
        self._mark_dirty()

    def _build_status_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("statusBar")
        self._status_bar_frame = bar
        bar.setFixedHeight(54)
        bar.setStyleSheet(
            f"#statusBar {{"
            f"  background-color: {DARK['statusbar_bg']};"
            f"  border-top: 1px solid {DARK['border_faint']};"
            f"}}"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 0, 10, 0)
        lay.setSpacing(10)

        from qfluentwidgets import TransparentToolButton as _TransparentToolButton
        self._folder_btn = _TransparentToolButton(FIF.FOLDER)
        self._folder_btn.setFixedSize(28, 28)
        self._folder_btn.setIconSize(QSize(15, 15))
        self._folder_btn.setIcon(FIF.FOLDER.icon(color=QColor(DARK["accent"])))
        self._folder_btn.setCursor(Qt.PointingHandCursor)
        self._folder_btn.setToolTip(HOSTS_PATH)
        self._folder_btn.clicked.connect(self._open_hosts_folder)
        lay.addWidget(self._folder_btn)

        self.status_bar = QLabel("")
        self.status_bar.setStyleSheet(
            f"color: {DARK['fg2']}; font-size: 10pt; background: transparent;"
        )
        lay.addWidget(self.status_bar, 1)

        search_frame = QFrame()
        search_frame.setObjectName("statusSearch")
        search_frame.setFixedHeight(34)
        search_frame.setMinimumWidth(220)
        search_frame.setMaximumWidth(340)
        search_frame.setStyleSheet(
            f"#statusSearch {{"
            f"  background-color: {DARK['search_frame_bg']};"
            f"  border: 1px solid {DARK['border_soft2']};"
            f"  border-radius: 17px;"
            f"}}"
        )
        sf_lay = QHBoxLayout(search_frame)
        sf_lay.setContentsMargins(10, 0, 8, 0)
        sf_lay.setSpacing(6)

        from qfluentwidgets import IconWidget as _IconWidget
        lupa = _IconWidget(FIF.SEARCH)
        lupa.setFixedSize(16, 16)
        lupa.setAttribute(Qt.WA_TransparentForMouseEvents)
        sf_lay.addWidget(lupa)

        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText(T("search_placeholder"))
        self._search_edit.setStyleSheet(
            f"QLineEdit {{"
            f"  background: transparent;"
            f"  color: {DARK['fg']};"
            f"  border: none;"
            f"  font-size: 10pt;"
            f"  font-weight: bold;"
            f"  padding: 0;"
            f"}}"
        )
        attach_line_edit_context_menu(self._search_edit)
        self._search_edit.textChanged.connect(self._on_search)
        sf_lay.addWidget(self._search_edit, 1)

        self._search_count = QLabel("")
        self._search_count.setStyleSheet(
            f"color: {accent_rgba(0.70)}; font-size: 9pt; font-weight: bold; background: transparent;"
        )
        sf_lay.addWidget(self._search_count)

        clr = ClickableLabel("✕")
        clr.setStyleSheet(
            f"color: {DARK['muted_fg']}; font-size: 11px; background: transparent;"
        )
        clr.setCursor(Qt.PointingHandCursor)
        clr.clicked.connect(self._search_edit.clear)
        sf_lay.addWidget(clr)

        lay.addWidget(search_frame)
        return bar

    def _open_hosts_folder(self):
        import subprocess
        folder = os.path.dirname(HOSTS_PATH)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", HOSTS_PATH])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def _load(self):
        self.entries = parse_hosts(HOSTS_PATH)
        self._refresh_table()
        self._update_status()
        self._mark_clean()

    def _refresh_table(self):
        query = self._search_edit.text().lower().strip() if hasattr(self, "_search_edit") else ""

        visible = [
            (i, e) for i, e in enumerate(self.entries)
            if e["enabled"] is not None
            and (not query or any(
                query in str(e.get(f, "")).lower()
                for f in ("ip", "hostname", "comment")
            ))
        ]

        COL_KEYS = ["status", "ip", "hostname", "comment"]
        if 0 <= self._sort_col_active < len(COL_KEYS):
            col = COL_KEYS[self._sort_col_active]
            rev = self._sort_col_reverse
            if col == "ip":
                visible.sort(
                    key=lambda p: tuple(int(x) if x.isdigit() else x
                                       for x in re.split(r"(\d+)", p[1]["ip"])),
                    reverse=rev
                )
            elif col == "status":
                visible.sort(key=lambda p: 0 if p[1]["enabled"] else 1, reverse=rev)
            else:
                visible.sort(key=lambda p: str(p[1].get(col, "")).lower(), reverse=rev)

        self.table.setRowCount(0)
        self.table.setRowCount(len(visible))

        for row, (orig_idx, e) in enumerate(visible):
            status_text = T("status_active") if e["enabled"] else T("status_disabled")
            fg = QColor(DARK["green"]) if e["enabled"] else QColor(DARK["gray"])

            items = [
                status_text,
                e["ip"],
                e["hostname"],
                e.get("comment", ""),
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                if col == 3 and text:
                    item.setForeground(QColor("#d4800a"))
                else:
                    item.setForeground(fg)
                item.setData(Qt.UserRole, orig_idx)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

        total_real = sum(1 for e in self.entries if e["enabled"] is not None)
        if query:
            self._search_count.setText(f"{len(visible)} / {total_real}")
        else:
            self._search_count.setText("")

    def _update_status(self):
        real = [e for e in self.entries if e["enabled"] is not None]
        on   = sum(1 for e in real if e["enabled"])
        off  = len(real) - on
        baks = len(list_backups(HOSTS_PATH))
        self.status_bar.setText(
            f"{T('status_entries', total=len(real), active=on, disabled=off)}"
            f"   |   {T('status_backups', n=baks)}"
        )

    def _on_search(self):
        if self._raw_mode:
            self._search_raw_text()
        else:
            self._refresh_table()

    def _search_raw_text(self):
        from PySide6.QtGui import QTextCursor, QTextDocument
        query = self._search_edit.text().strip()

        if not query:
            self._search_count.setText("")
            cursor = self._raw_editor.textCursor()
            cursor.clearSelection()
            self._raw_editor.setTextCursor(cursor)
            return

        text = self._raw_editor.toPlainText()
        lines = [l for l in text.split("\n") if l.strip()]
        matches = sum(1 for l in lines if query.lower() in l.lower())
        self._search_count.setText(f"{matches} / {len(lines)}")

        cursor = self._raw_editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self._raw_editor.setTextCursor(cursor)
        found = self._raw_editor.find(query, QTextDocument.FindFlags())
        if not found:
            cursor = self._raw_editor.textCursor()
            cursor.clearSelection()
            self._raw_editor.setTextCursor(cursor)

    def _sort_col(self, logical_index: int):
        if self._sort_col_active == logical_index:
            self._sort_col_reverse = not self._sort_col_reverse
        else:
            self._sort_col_active  = logical_index
            self._sort_col_reverse = False
        self._update_sort_headers()
        self._refresh_table()

    def _update_sort_headers(self):
        col_keys = [T("col_status"), T("col_ip"), T("col_hostname"), T("col_comment")]
        for i, label in enumerate(col_keys):
            if i == self._sort_col_active:
                item = QTableWidgetItem(label)
                item.setData(Qt.DecorationRole, _sort_px(not self._sort_col_reverse))
            else:
                item = QTableWidgetItem(label + "  ⇅")
            self.table.setHorizontalHeaderItem(i, item)

    def _selected_indices(self) -> list[int]:
        seen = set()
        result = []
        for item in self.table.selectedItems():
            idx = item.data(Qt.UserRole)
            if idx is not None and idx not in seen:
                seen.add(idx)
                if self.entries[idx]["enabled"] is not None:
                    result.append(idx)
        return result

    def _selected_idx(self) -> int | None:
        indices = self._selected_indices()
        return indices[0] if indices else None

    def _mark_dirty(self):
        if not self._dirty:
            self._dirty = True
            self._save_btn.set_accent(True)

    def _mark_clean(self):
        if self._dirty:
            self._dirty = False
            self._save_btn.set_accent(False)

    def _add(self):
        from .dialogs import EntryDialog
        existing = {e["hostname"].lower() for e in self.entries if e["enabled"] is not None}
        dlg = EntryDialog(self, existing_hostnames=existing)
        dlg.exec()

        if dlg.result_list is not None:
            added, candidate = len(dlg.result_list), self.entries + dlg.result_list
        elif dlg.result:
            added, candidate = 1, self.entries + [dlg.result]
        else:
            return

        active_after = sum(1 for e in candidate if e.get("enabled") is True)
        if active_after > MAX_ACTIVE_ENTRIES:
            if not HOTSDialog.ask(self, T("add_limit_ask_title"),
                                  T("add_limit_ask_msg", n=added,
                                    total=active_after, max=MAX_ACTIVE_ENTRIES)):
                return

        self.entries = candidate
        self._refresh_table(); self._update_status(); self._mark_dirty()

    def _edit(self):
        idx = self._selected_idx()
        if idx is None:
            HOTSDialog.info(self, T("no_sel_title"), T("no_sel_edit"))
            return
        from .dialogs import EntryDialog
        dlg = EntryDialog(self, self.entries[idx])
        dlg.exec()
        if dlg.result:
            self.entries[idx] = dlg.result
            self._refresh_table(); self._update_status(); self._mark_dirty()

    def _toggle(self):
        indices = self._selected_indices()
        if not indices:
            HOTSDialog.info(self, T("no_sel_title"), T("no_sel_toggle"))
            return
        any_off = any(not self.entries[i]["enabled"] for i in indices)
        for i in indices:
            self.entries[i]["enabled"] = any_off
        self._refresh_table(); self._update_status(); self._mark_dirty()

    def _delete(self):
        if self._raw_mode:
            cursor = self._raw_editor.textCursor()
            if cursor.hasSelection():
                cursor.removeSelectedText()
            self._mark_dirty()
            return

        indices = self._selected_indices()
        if not indices:
            HOTSDialog.info(self, T("no_sel_title"), T("no_sel_delete"))
            return

        if len(indices) == 1:
            e = self.entries[indices[0]]
            q = T("del_confirm_one", ip=e["ip"], hostname=e["hostname"])
        else:
            preview = "\n".join(
                f"{self.entries[i]['ip']}  {self.entries[i]['hostname']}"
                for i in indices[:10]
            )
            suffix = T("del_more", n=len(indices)-10) if len(indices) > 10 else ""
            q = T("del_confirm_many", n=len(indices), preview=preview, suffix=suffix)

        if not HOTSDialog.ask(self, T("del_confirm_title"), q):
            return
        for i in sorted(indices, reverse=True):
            self.entries.pop(i)
        self._refresh_table(); self._update_status(); self._mark_dirty()

    def _set_zero_ip(self):
        indices = self._selected_indices()
        if not indices:
            return
        changed = False
        for i in indices:
            entry = self.entries[i]
            if entry["enabled"] is not None and entry["ip"] != "0.0.0.0":
                entry["ip"] = "0.0.0.0"
                changed = True
        if not changed:
            return
        self._refresh_table(); self._update_status(); self._mark_dirty()

    def _save(self):
        if self._raw_mode:
            if not self._commit_raw_text():
                return

        active_count = sum(1 for e in self.entries if e.get("enabled") is True)
        if active_count > MAX_ACTIVE_ENTRIES:
            HOTSDialog.error(self, T("save_limit_title"),
                             T("save_limit_msg", n=active_count, max=MAX_ACTIVE_ENTRIES))
            return

        try:
            with open(HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
                old_text = f.read()
        except Exception:
            old_text = ""
        new_text = entries_to_text(self.entries)

        from .dialogs import DiffDialog
        dlg = DiffDialog(self, old_text, new_text)
        dlg.exec()
        if not dlg.confirmed:
            return

        self.status_bar.setText(T("status_saving"))
        self._worker = SaveWorker(HOSTS_PATH, self.entries)
        self._worker.finished.connect(self._on_save_finished)
        self._worker.error_msg.connect(self._on_save_error)
        self._worker.start()

    def _on_save_finished(self, _ok: bool):
        self._mark_clean()
        self._update_status()
        InfoBar.success(
            title=T("save_success_title"),
            content=T("save_success_msg"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self,
        )

    def _on_save_error(self, msg: str):
        self._update_status()
        HOTSDialog.error(self, T("save_err_title"), msg)

    def _import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, T("import_dialog_title"), "",
            f"{T('import_filetypes_hosts')} (*.txt *.hosts *);;{T('import_filetypes_all')} (*.*)"
        )
        if not path:
            return
        try:
            new_entries, count = import_from_path(path, self.entries)
        except ValueError as ex:
            HOTSDialog.info(self, T("import_empty_title"), str(ex))
            return

        active_after = sum(1 for e in new_entries if e.get("enabled") is True)
        if active_after > MAX_ACTIVE_ENTRIES:
            if not HOTSDialog.ask(self, T("import_limit_ask_title"),
                                  T("import_limit_ask_msg", n=count,
                                    total=active_after, max=MAX_ACTIVE_ENTRIES)):
                return
        else:
            if not HOTSDialog.ask(self, T("import_confirm_title"),
                                  T("import_confirm_msg", n=count)):
                return

        self.entries = new_entries
        self._refresh_table(); self._update_status(); self._mark_dirty()

    def _export(self):
        from .dialogs import ExportOptionsDialog
        dlg = ExportOptionsDialog(
            self,
            total_count  = sum(1 for e in self.entries if e["enabled"] is not None),
            sel_indices  = self._selected_indices(),
        )
        dlg.exec()
        if not dlg.confirmed:
            return

        entries_to_exp = (
            [self.entries[i] for i in dlg.sel_indices]
            if dlg.use_selection and dlg.sel_indices
            else self.entries
        )

        path, _ = QFileDialog.getSaveFileName(
            self, T("export_dialog_title"), "",
            f"{T('export_filetypes_txt')} (*.txt);;"
            f"{T('export_filetypes_csv')} (*.csv);;"
            f"{T('export_filetypes_all')} (*.*)"
        )
        if not path:
            return

        try:
            n = export_to_path(path, entries_to_exp, include_comments=dlg.include_comments)
            if path.endswith(".csv"):
                HOTSDialog.info(self, T("export_ok_csv_title"), T("export_ok_csv_msg", path=path))
            else:
                HOTSDialog.info(self, T("export_ok_txt_title"), T("export_ok_txt_msg", n=n, path=path))
        except Exception as ex:
            HOTSDialog.error(self, T("export_err_title"), str(ex))

    def _backups(self):
        self.switchTo(self._backup_page)

    def _show_context_menu(self, pos: QPoint):
        item = self.table.itemAt(pos)
        if not item:
            return
        if not self.table.selectedItems():
            self.table.selectRow(item.row())

        if hasattr(self, "_ctx_menu") and self._ctx_menu is not None:
            try:
                QApplication.instance().removeEventFilter(self._ctx_menu)
                self._ctx_menu.hide()
                self._ctx_menu.deleteLater()
            except Exception:
                pass
            self._ctx_menu = None

        global_pos = self.table.viewport().mapToGlobal(pos)
        self._ctx_menu = HOTSContextMenu(self, [
            ("☑", "#50c878", T("ctx_select_all"), self._select_all),
            None,
            ("✎", DARK['accent'], T("ctx_edit"),    self._edit),
            ("◑", "#a0a0ff", T("ctx_toggle"),  self._toggle),
            ("✖", "#e05050", T("ctx_delete"),  self._delete),
            None,
            ("⊘", "#ff9050", T("ctx_zero_ip"), self._set_zero_ip),
        ])
        self._ctx_menu.popup(global_pos)

    def _select_all(self):
        self.table.selectAll()

    @staticmethod
    def _entries_semantically_equal(a: list, b: list) -> bool:
        if len(a) != len(b):
            return False
        for ea, eb in zip(a, b):
            if ea.get("enabled") is None or eb.get("enabled") is None:
                if ea.get("enabled") != eb.get("enabled"):
                    return False
                if ea.get("raw", "") != eb.get("raw", ""):
                    return False
            else:
                if (ea.get("enabled") != eb.get("enabled")
                        or ea.get("ip", "") != eb.get("ip", "")
                        or ea.get("hostname", "") != eb.get("hostname", "")
                        or ea.get("comment", "") != eb.get("comment", "")):
                    return False
        return True

    def _commit_raw_text(self) -> bool:
        from .core import parse_hosts as _ph
        import tempfile
        raw_text = self._raw_editor.toPlainText()
        fd, tmp = tempfile.mkstemp(suffix=".hosts")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(raw_text)
            new_entries = _ph(tmp)
            if not self._entries_semantically_equal(new_entries, self.entries):
                self.entries = new_entries
                self._mark_dirty()
            else:
                self.entries = new_entries
            return True
        except Exception as ex:
            HOTSDialog.error(self, T("parse_err_title"), T("raw_commit_err_msg", error=str(ex)))
            return False
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    def _raw_view_active(self) -> bool:
        return self._raw_widget.isVisible()

    def _show_table_view(self):
        if self._raw_mode:
            self._commit_raw_text()
            self._raw_mode = False
            self._raw_widget.hide()
            self._table_widget.show()
            self._toolbar_frame.show()
            self._refresh_table()
            self._update_status()

    def _show_raw_view(self):
        self._table_widget.hide()
        self._toolbar_frame.hide()
        self._raw_widget.show()
        self._raw_mode = True
        self._populate_raw_view()
        if self.stackedWidget.currentWidget() is not self._main_widget:
            self.switchTo(self._main_widget)
        if self._search_edit.text().strip():
            self._search_raw_text()

    def _repair(self):
        self._show_table_view()

        original_state = [
            (e.get("ip", ""), e.get("hostname", ""), e.get("comment", ""), e.get("enabled"))
            for e in self.entries
        ]
        fixed_entries = []
        seen_pairs = set()
        wildcards_fixed = dups_removed = invalid_removed = normalized = 0

        for e in self.entries:
            if e["enabled"] is None:
                fixed_entries.append(e)
                continue
            ip   = e["ip"].strip()
            host = e["hostname"].strip()
            comment = e["comment"].strip()
            if not ip or not host or not is_valid_ip(ip):
                invalid_removed += 1
                continue
            original_host = host
            while True:
                stripped_host = re.sub(r"^\*\.?", "", host).lstrip(".")
                if stripped_host == host:
                    break
                host = stripped_host
            if host != original_host:
                wildcards_fixed += 1
            if not host:
                invalid_removed += 1
                continue
            host_clean = host.lower().strip()
            if host_clean != host:
                normalized += 1
            pair_key = (ip.strip(), host_clean, bool(e["enabled"]))
            if pair_key in seen_pairs:
                dups_removed += 1
                if comment:
                    for prev in reversed(fixed_entries):
                        if (prev["enabled"] is not None
                                and bool(prev["enabled"]) == bool(e["enabled"])
                                and prev["ip"].strip() == ip.strip()
                                and prev["hostname"].lower() == host_clean):
                            if prev["comment"]:
                                if comment not in prev["comment"]:
                                    prev["comment"] += f" | {comment}"
                            else:
                                prev["comment"] = comment
                            break
                continue
            seen_pairs.add(pair_key)
            fixed_entries.append({
                "enabled": e["enabled"], "ip": ip,
                "hostname": host_clean, "comment": comment,
                "raw": e.get("raw", ""),
            })

        new_state = [
            (e.get("ip", ""), e.get("hostname", ""), e.get("comment", ""), e.get("enabled"))
            for e in fixed_entries
        ]
        if new_state == original_state:
            HOTSDialog.info(self, T("repair_no_changes_title"), T("repair_no_changes_msg"))
            return

        self.entries = fixed_entries
        self._refresh_table(); self._update_status(); self._mark_dirty()

        report = [T("repair_done_header")]
        if wildcards_fixed: report.append(T("repair_wildcards",  n=wildcards_fixed))
        if dups_removed:    report.append(T("repair_dups",       n=dups_removed))
        if invalid_removed: report.append(T("repair_invalid",    n=invalid_removed))
        if normalized:      report.append(T("repair_normalized", n=normalized))
        HOTSDialog.info(self, T("repair_done_title"), "\n".join(report))

    def _restore_default(self):
        if not HOTSDialog.ask(self, T("restore_ask_title"), T("restore_ask_msg")):
            return
        default_entries = [
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# Copyright (c) 1993-2009 Microsoft Corp."},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "#"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# This is a sample HOSTS file used by Microsoft TCP/IP for Windows."},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "#"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# This file contains the mappings of IP addresses to host names. Each"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# entry should be kept on an individual line. The IP address should"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# be placed in the first column followed by the corresponding host name."},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# The IP address and the host name should be separated by at least one"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# space."},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "#"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# Additionally, comments (such as these) may be inserted on individual"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# lines or following the machine name denoted by a '#' symbol."},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "#"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# For example:"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "#"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "#      102.54.94.97     rhino.acme.com          # source server"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "#       38.25.63.10     x.acme.com              # x client host"},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": ""},
            {"enabled": None, "ip": "", "hostname": "", "comment": "",
             "raw": "# localhost name resolution is handled within DNS itself."},
            {"enabled": False, "ip": "127.0.0.1", "hostname": "localhost", "comment": "", "raw": ""},
            {"enabled": False, "ip": "::1",        "hostname": "localhost", "comment": "", "raw": ""},
        ]
        try:
            save_hosts(HOSTS_PATH, default_entries)
        except Exception as ex:
            HOTSDialog.error(self, T("save_err_title"), str(ex))
            return
        self._load()
        self.switchTo(self._main_widget)
        self._show_table_view()
        HOTSDialog.info(self, T("restore_done_title"), T("restore_done_msg"))

    def _diag_existence(self):
        selected = self._selected_indices()
        if not selected:
            HOTSDialog.info(self, T("no_sel_title"), T("no_sel_check"))
            self.switchTo(self._main_widget)
            return
        self._diagnostics_page.set_context(
            [self.entries[i] for i in selected], mode="existence",
            on_remove=self._remove_by_hostnames)
        self.switchTo(self._diagnostics_page)

    def _diag_malware(self):
        selected = self._selected_indices()
        to_check = [self.entries[i] for i in selected] if selected else self.entries
        self._diagnostics_page.set_context(
            to_check, mode="malware", on_remove=self._remove_by_hostnames)
        self.switchTo(self._diagnostics_page)

    def _remove_by_hostnames(self, hostnames: set):
        self.entries = [e for e in self.entries if e["hostname"].lower() not in hostnames]
        self._refresh_table(); self._update_status(); self._mark_dirty()

    def _open_parental_control(self):
        self.switchTo(self._parental_page)

    def _open_privacy(self):
        self.switchTo(self._privacy_page)

    def _support(self):
        self.switchTo(self._support_page)

    def _about(self):
        self.switchTo(self._about_page)

    def _change_language(self):
        from .dialogs import LanguageDialog
        dlg = LanguageDialog(self)
        dlg.exec()
        if dlg.chosen and dlg.chosen != current_lang():
            set_lang(dlg.chosen)
            self._save_settings_merged(language=dlg.chosen)
            HOTSDialog.info(self, T("lang_title"), T("lang_restart_msg"))

    def _change_accent_color(self):
        from .dialogs import AccentColorDialog
        current_accent = self._settings.get("accent_color", "gold")
        current_theme = self._settings.get("theme", "dark")
        dlg = AccentColorDialog(self, current_accent=current_accent, current_theme=current_theme)
        dlg.exec()
        if dlg.chosen_accent is None and dlg.chosen_theme is None:
            return
        changed = (
            (dlg.chosen_accent and dlg.chosen_accent != current_accent) or
            (dlg.chosen_theme and dlg.chosen_theme != current_theme)
        )
        if changed:
            self._save_settings_merged(
                accent_color=dlg.chosen_accent or current_accent,
                theme=dlg.chosen_theme or current_theme,
            )
            if HOTSDialog.restart_prompt(self, T("app_title"), T("app_restart_msg")):
                self._restart_app()

    def _restart_app(self):
        self._disconnect_bg_signals()
        if not self.close():
            return

        os.environ.pop("_MEIPASS2", None)

        try:
            main_mod = sys.modules.get("__main__")
            release_fn = getattr(main_mod, "release_single_instance_lock", None)
            if callable(release_fn):
                release_fn()
        except Exception:
            pass

        python = sys.executable
        args = sys.argv[1:]
        if getattr(sys, "frozen", False):
            ok = QProcess.startDetached(python, args)
        else:
            pkg = (__package__ or "").split(".")[0]
            if pkg:
                ok = QProcess.startDetached(python, ["-m", pkg] + args)
            else:
                ok = QProcess.startDetached(python, sys.argv)
        if not ok:
            HOTSDialog.error(self, T("app_title"), T("app_restart_fail_msg"))
            return
        QApplication.quit()

    def _manage_password(self):
        from .__main__ import _reg_get_password, _reg_set_password
        from .dialogs import SetPasswordDialog
        current_hash = _reg_get_password()

        def on_save(new_hash: str):
            _reg_set_password(new_hash)
            self._refresh_pass_nav()

        dlg = SetPasswordDialog(self, current_hash, on_save)
        dlg.exec()

    def _refresh_pass_nav(self):
        from .__main__ import _reg_get_password
        has = bool(_reg_get_password())
        try:
            item = self.navigationInterface.widget("password")
            if item:
                item.setToolTip(T("opt_pass_on") if has else T("opt_pass_off"))
        except Exception:
            pass

    def _disconnect_bg_signals(self):
        for sig in self._bg_signal_objs:
            try:
                sig.done.disconnect()
            except Exception:
                pass
        self._bg_signal_objs.clear()

        try:
            self._privacy_page.disconnect_bg_signals()
        except Exception as e:
            print(f"disconnect_bg_signals (privacy_page) warning: {e}")

    def _save_settings_merged(self, **updates):
        fresh = load_settings()
        fresh.update(updates)
        self._settings = fresh
        save_settings(fresh)

    def _on_close_event(self, event):
        if self._dirty:
            if not HOTSDialog.ask(self, T("dlg_unsaved_title"), T("dlg_unsaved_msg")):
                event.ignore()
                return
        self._disconnect_bg_signals()
        geo = self.geometry()
        col_widths = ",".join(str(self.table.columnWidth(i)) for i in range(3))
        self._save_settings_merged(
            geometry=f"{geo.width()}x{geo.height()}+{geo.x()}+{geo.y()}",
            language=current_lang(),
            table_col_widths=col_widths,
            table_sort_col=self._sort_col_active,
            table_sort_reverse="1" if self._sort_col_reverse else "0",
        )
        event.accept()