import os
import stat
from pathlib import Path

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal, QObject
import shiboken6

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK, accent_rgba
from ..core import list_backups, restore_from_backup, HostsBusyError
from ..core_antispy import HostsLockError
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton, h_separator
from ..i18n import T
from ..bg_tasks import start_bg_thread, is_shutting_down


class _RestoreSignals(QObject):
    done = Signal(bool, object)


class BackupManagerPage(HOTSPage):
    def __init__(self, parent, hosts_path, on_restore, on_backup_count_changed=None, on_restore_default=None):
        super().__init__("backupInterface", FIF.SAVE, T("bak_title"), parent)
        self.hosts_path = hosts_path
        self.on_restore = on_restore
        self.on_backup_count_changed = on_backup_count_changed
        self.on_restore_default = on_restore_default
        self._build()
        self._refresh()

    def _card_style(self) -> str:
        return (f"background: {DARK['panel_bg']}; "
                f"border: 1px solid {DARK['border_faint']}; border-radius: 6px;")

    def _build(self):
        cl = self.content_layout

        sub = QLabel(T("bak_subheader"))
        sub.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        cl.addWidget(sub)
        cl.addSpacing(10)
        cl.addWidget(h_separator())

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        cl_body = QVBoxLayout(body)
        cl_body.setContentsMargins(12, 10, 12, 10)
        cl_body.setSpacing(6)
        cl.addWidget(body, 1)
        cl = cl_body

        table_card = QWidget()
        table_card.setStyleSheet(self._card_style())
        table_card_lay = QVBoxLayout(table_card)
        table_card_lay.setContentsMargins(6, 6, 6, 6)
        table_card_lay.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            T("bak_col_date"), T("bak_col_size"), T("bak_col_file")
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 160)
        self.table.setColumnWidth(1, 80)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.table.setStyleSheet(
            f"QTableWidget {{ background-color: transparent; color: {DARK['fg']}; "
            f"border: none; border-radius: 6px; gridline-color: {DARK['grid_line']}; }}"
            f"QTableWidget::item {{ background-color: transparent; }}"
            f"QTableWidget::item:selected {{ background-color: {accent_rgba(0.16)}; color: {DARK['fg']}; }}"
            f"QHeaderView::section {{ background-color: {DARK['panel_bg_alt']}; color: {DARK['fg2']}; "
            f"border: none; border-bottom: 1px solid {DARK['border_soft2']}; padding: 6px; }}"
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
        table_card_lay.addWidget(self.table)
        cl.addWidget(table_card, 1)

        act = QWidget()
        act.setStyleSheet(self._card_style())
        act_lay = QHBoxLayout(act)
        act_lay.setContentsMargins(14, 10, 14, 10)
        act_lay.addStretch()

        restore_btn = HOTSButton(FIF.SYNC, "#ffffff", T("bak_btn_restore"), accent=True)
        restore_btn.fit_to_content()
        restore_btn.clicked.connect(self._restore)
        act_lay.addWidget(restore_btn)
        self._restore_btn = restore_btn

        del_btn = HOTSButton(FIF.DELETE, "#e05050", T("bak_btn_delete"))
        del_btn.fit_to_content()
        del_btn.clicked.connect(self._delete_bak)
        act_lay.addWidget(del_btn)
        self._del_btn = del_btn

        default_btn = HOTSButton(FIF.BROOM, DARK["fg2"], T("btn_default"), accent=False)
        default_btn.fit_to_content()
        default_btn.clicked.connect(self._restore_default_clicked)
        act_lay.addWidget(default_btn)
        self._default_btn = default_btn

        act_lay.addStretch()
        cl.addWidget(act)

        self._status = QLabel("")
        self._status.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        cl.addWidget(self._status)

    def refresh_content(self):
        self._refresh()

    def _refresh(self):
        self.table.setRowCount(0)
        self._baks = list_backups(self.hosts_path)
        if not self._baks:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(T("bak_empty")))
        else:
            self.table.setRowCount(len(self._baks))
            for row, (p, dt) in enumerate(self._baks):
                size = p.stat().st_size
                size_str = f"{size/1024:.1f} KB" if size >= 1024 else f"{size} B"
                self.table.setItem(row, 0, QTableWidgetItem(dt.strftime("%Y-%m-%d  %H:%M:%S")))
                self.table.setItem(row, 1, QTableWidgetItem(size_str))
                item = QTableWidgetItem(str(p))
                item.setData(Qt.UserRole, str(p))
                self.table.setItem(row, 2, item)
        self._status.setText(T("bak_status_count", n=len(self._baks)))

    def _selected_paths(self) -> list:
        rows = set(item.row() for item in self.table.selectedItems())
        if not rows:
            HOTSDialog.info(self, T("no_sel_title"), T("bak_no_sel_msg"))
            return []
        result = []
        for row in sorted(rows):
            item = self.table.item(row, 2)
            if item and item.data(Qt.UserRole):
                result.append(Path(item.data(Qt.UserRole)))
        return result

    def _restore(self):
        paths = self._selected_paths()
        if not paths:
            return
        if len(paths) > 1:
            HOTSDialog.info(self, T("bak_too_many_title"), T("bak_too_many_msg"))
            return
        p = paths[0]
        if not HOTSDialog.ask(self, T("bak_restore_ask_title"),
                              T("bak_restore_ask_msg", name=p.name)):
            return

        self._restore_btn.setEnabled(False)
        self._del_btn.setEnabled(False)
        self.table.setEnabled(False)
        self.begin_busy()

        signals = _RestoreSignals(self)
        if not hasattr(self, "_restore_signal_refs"):
            self._restore_signal_refs = []
        self._restore_signal_refs.append(signals)

        def _cleanup_and_handle(ok, err):
            if signals in self._restore_signal_refs:
                self._restore_signal_refs.remove(signals)
            if not shiboken6.isValid(self):
                return
            self._finish_restore(p, ok, err)

        signals.done.connect(_cleanup_and_handle)

        def worker():
            ok = True
            err = None
            try:
                restore_from_backup(self.hosts_path, p)
            except (HostsBusyError, HostsLockError) as ex:
                err = str(ex)
                ok = False
            except Exception as ex:
                err = str(ex)
                ok = False
            signals.done.emit(ok, err)

        start_bg_thread(worker)

    def _finish_restore(self, p, ok: bool, err):
        if not shiboken6.isValid(self):
            return
        if is_shutting_down():
            return
        self.end_busy()
        if shiboken6.isValid(self._restore_btn):
            self._restore_btn.setEnabled(True)
        if shiboken6.isValid(self._del_btn):
            self._del_btn.setEnabled(True)
        if shiboken6.isValid(self.table):
            self.table.setEnabled(True)

        if not ok:
            HOTSDialog.error(self, T("bak_restore_ask_title"), err or T("par_err_hosts_msg"))
            return

        HOTSDialog.info(self, T("save_success_title"), T("bak_restore_ok"))
        self._refresh()
        self._status.setText(T("bak_status_restored", name=p.name))
        self.on_restore()

    def _restore_default_clicked(self):
        if self.on_restore_default:
            self.on_restore_default()

    def _delete_bak(self):
        paths = self._selected_paths()
        if not paths:
            return
        names = "\n".join(p.name for p in paths)
        q = (T("bak_del_ask_many", n=len(paths), names=names)
             if len(paths) > 1
             else T("bak_del_ask_one", name=paths[0].name))
        if not HOTSDialog.ask(self, T("bak_del_ask_title"), q):
            return
        deleted = 0
        errors = []
        for p in paths:
            try:
                try:
                    os.chmod(str(p), stat.S_IWRITE)
                except OSError:
                    pass
                p.unlink(missing_ok=True)
                deleted += 1
            except OSError as e:
                errors.append(f"{p.name}: {e}")
        self._refresh()
        if errors:
            HOTSDialog.info(self, T("bak_del_err_title"), "\n".join(errors))
        self._status.setText(T("bak_status_deleted", n=deleted))
        if deleted and self.on_backup_count_changed:
            self.on_backup_count_changed()
