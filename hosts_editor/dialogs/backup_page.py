import os
import shutil
import stat
from pathlib import Path

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PySide6.QtCore import Qt

from qfluentwidgets import FluentIcon as FIF

from ..constants import DARK, accent_rgba
from ..core import list_backups, flush_dns_cache, create_backup
from ..widgets_qt import HOTSPage, HOTSDialog, HOTSButton
from ..i18n import T


class BackupManagerPage(HOTSPage):
    def __init__(self, parent, hosts_path, on_restore, on_backup_count_changed=None):
        super().__init__("backupInterface", FIF.SAVE, T("bak_title"), parent)
        self.hosts_path = hosts_path
        self.on_restore = on_restore
        self.on_backup_count_changed = on_backup_count_changed
        self._build()
        self._refresh()

    def _build(self):
        cl = self.content_layout

        sub = QLabel(T("bak_subheader"))
        sub.setStyleSheet(f"color: {DARK['fg2']}; font-size: 9pt; background: transparent;")
        cl.addWidget(sub)
        cl.addSpacing(8)

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

        self.table.setStyleSheet(
            f"QTableWidget {{ background-color: {DARK['table_bg']}; color: {DARK['fg']}; "
            f"border: 1px solid {DARK['border_soft']}; gridline-color: {DARK['grid_line']}; }}"
            f"QTableWidget::item {{ background-color: transparent; }}"
            f"QTableWidget::item:selected {{ background-color: {accent_rgba(0.16)}; color: {DARK['fg']}; }}"
            f"QHeaderView::section {{ background-color: {DARK['panel_bg_alt']}; color: {DARK['fg2']}; "
            f"border: none; border-bottom: 1px solid {DARK['border_soft2']}; padding: 6px; }}"
        )
        cl.addWidget(self.table, 1)
        cl.addSpacing(8)

        act = QWidget()
        act_lay = QHBoxLayout(act)
        act_lay.setContentsMargins(0, 0, 0, 0)
        act_lay.addStretch()

        restore_btn = HOTSButton(FIF.SYNC, "#ffffff", T("bak_btn_restore"), accent=True)
        restore_btn.fit_to_content()
        restore_btn.clicked.connect(self._restore)
        act_lay.addWidget(restore_btn)

        del_btn = HOTSButton(FIF.DELETE, "#e05050", T("bak_btn_delete"))
        del_btn.fit_to_content()
        del_btn.clicked.connect(self._delete_bak)
        act_lay.addWidget(del_btn)
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
        create_backup(self.hosts_path)
        shutil.copy2(str(p), self.hosts_path)
        try:
            os.chmod(self.hosts_path, stat.S_IWRITE)
        except OSError:
            pass
        flush_dns_cache()
        HOTSDialog.info(self, T("save_success_title"), T("bak_restore_ok"))
        self._refresh()
        self._status.setText(T("bak_status_restored", name=p.name))
        self.on_restore()

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
