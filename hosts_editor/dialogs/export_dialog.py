from PySide6.QtWidgets import QHBoxLayout, QLabel, QButtonGroup

from ..icons import FIF
from ..constants import DARK
from ..widgets_qt import HOTSDialog, HOTSButton, HOTSSwitch, HOTSRadio, h_separator
from ..i18n import T


class ExportOptionsDialog(HOTSDialog):
    def __init__(self, parent, total_count: int, sel_indices: list):
        super().__init__(parent, T("btn_export"), min_width=360, min_height=260)
        self.confirmed         = False
        self.use_selection     = False
        self.include_comments  = True
        self.sel_indices       = sel_indices
        self._total            = total_count
        self._has_sel          = bool(sel_indices)
        self._build()
        self.adjustSize()
        self.center_on_parent()

    def _build(self):
        cl = self.body_layout
        cl.setContentsMargins(28, 24, 28, 16)
        cl.setSpacing(12)

        scope_lbl = QLabel(T("export_scope_label"))
        scope_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 10pt; font-weight: bold; background: transparent;")
        cl.addWidget(scope_lbl)


        self._rb_group = QButtonGroup(self)

        self._rb_all = HOTSRadio(T("export_scope_all", n=self._total))
        self._rb_all.setChecked(not self._has_sel)
        self._rb_group.addButton(self._rb_all)
        cl.addWidget(self._rb_all)

        sel_text = T("export_scope_sel", n=len(self.sel_indices)) if self._has_sel else T("export_scope_sel_none")
        self._rb_sel = HOTSRadio(sel_text)
        self._rb_sel.setEnabled(self._has_sel)
        self._rb_sel.setChecked(self._has_sel)
        self._rb_group.addButton(self._rb_sel)
        cl.addWidget(self._rb_sel)

        cl.addSpacing(4)

        comm_lbl = QLabel(T("export_comments_label"))
        comm_lbl.setStyleSheet(f"color: {DARK['fg2']}; font-size: 10pt; font-weight: bold; background: transparent;")
        cl.addWidget(comm_lbl)

        self._cb_comments = HOTSSwitch(T("export_comments_include"))
        self._cb_comments.setChecked(True)
        cl.addWidget(self._cb_comments)
        
        cl.addStretch()
        cl.addWidget(h_separator())

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()
        
        exp_btn = HOTSButton(FIF.SHARE, "#ffffff", T("btn_export"), accent=True)
        exp_btn.fit_to_content(min_width=100)
        exp_btn.clicked.connect(self._do_export)
        btn_row.addWidget(exp_btn)

        cancel_btn = HOTSButton(FIF.CLOSE, DARK["red"], T("btn_cancel"))
        cancel_btn.fit_to_content(min_width=100)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch()
        cl.addLayout(btn_row)

    def _do_export(self):
        self.confirmed        = True
        self.use_selection    = self._rb_sel.isChecked()
        self.include_comments = self._cb_comments.isChecked()
        self.accept()