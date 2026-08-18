"""Linha de comando no painel de comandos"""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, QTimer
from app.style import COLORS as C, FONTS as F, MONO

_BTN = (
    f"QPushButton {{ background: transparent; border: 1px solid {C['border_bright']}; "
    f"border-radius: 4px; color: {C['text_muted']}; font-size: {F['base']}px; "
    f"padding: 0 0 1px 0; }}"
    f"QPushButton:hover {{ color: {C['text_primary']}; border-color: {C['accent']}; "
    f"background: {C['bg_raised']}; }}"
)
_BTN_REPEAT = (
    f"QPushButton {{ background: transparent; border: 1px solid {C['border_bright']}; "
    f"border-radius: 4px; color: {C['text_muted']}; font-size: {F['small']}px; padding: 0 6px; }}"
    f"QPushButton:checked {{ background-color: {C['accent_dim']}; color: {C['accent']}; "
    f"border-color: {C['accent']}; }}"
    f"QPushButton:hover {{ border-color: {C['accent']}; }}"
)


class CommandEntry(QFrame):
    send_requested = Signal(dict)
    edit_requested = Signal()
    delete_requested = Signal()

    def __init__(self, command: dict, parent=None):
        super().__init__(parent)
        self._command = command
        self._timer = QTimer(self)
        self._timer.timeout.connect(lambda: self.send_requested.emit(self._command))
        self.setFixedHeight(40)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(
            f"CommandEntry {{ background-color: {C['bg_surface']}; "
            f"border: 1px solid {C['border']}; border-radius: 6px; }}"
        )
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 6, 0)
        layout.setSpacing(6)

        lbl_name = QLabel(self._command.get("name", ""))
        lbl_name.setFixedWidth(80)
        lbl_name.setStyleSheet(f"color: {C['text_primary']}; font-size: {F['base']}px;")

        payload = self._command.get("payload", "")
        preview = payload if len(payload) <= 18 else payload[:18] + "…"
        lbl_frame = QLabel(preview)
        lbl_frame.setStyleSheet(
            f"color: {C['text_muted']}; font-size: {F['small']}px; font-family: {MONO};"
        )

        layout.addWidget(lbl_name)
        layout.addWidget(lbl_frame, stretch=1)

        interval = self._command.get("repeat_interval")
        if interval:
            self.btn_repeat = QPushButton(f"⟳ {interval}s")
            self.btn_repeat.setCheckable(True)
            self.btn_repeat.setFixedHeight(26)
            self.btn_repeat.setStyleSheet(_BTN_REPEAT)
            self.btn_repeat.toggled.connect(self._on_repeat_toggled)
            layout.addWidget(self.btn_repeat)

        btn_send = QPushButton("▶")
        btn_send.setFixedSize(28, 28)
        btn_send.setStyleSheet(_BTN)
        btn_send.clicked.connect(lambda: self.send_requested.emit(self._command))

        btn_edit = QPushButton("⚙")
        btn_edit.setFixedSize(28, 28)
        btn_edit.setStyleSheet(_BTN)
        btn_edit.clicked.connect(self.edit_requested.emit)

        btn_delete = QPushButton("×")
        btn_delete.setFixedSize(28, 28)
        btn_delete.setStyleSheet(_BTN)
        btn_delete.clicked.connect(self.delete_requested.emit)

        layout.addWidget(btn_send)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)

    def _on_repeat_toggled(self, checked):
        interval = self._command.get("repeat_interval", 1.0)
        if checked:
            self._timer.start(int(interval * 1000))
        else:
            self._timer.stop()

    def get_command(self):
        return self._command

    def cleanup(self):
        self._timer.stop()
