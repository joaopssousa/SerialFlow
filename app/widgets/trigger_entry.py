"""Linha de trigger no painel de triggers"""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal
from app.style import COLORS as C, FONTS as F, MONO, rgba

_ACTION_BADGES = {
    "stop":         ("#ff4566", "Parar"),
    "newline":      ("#5a7899", "Nova linha"),
    "highlight":    ("#ffaa00", "Destacar"),
    "send_command": ("#00ff88", "Enviar cmd"),
}

_BTN = (
    f"QPushButton {{ background: transparent; border: 1px solid {C['border_bright']}; "
    f"border-radius: 4px; color: {C['text_muted']}; font-size: {F['base']}px; "
    f"padding: 0 0 1px 0; }}"
    f"QPushButton:hover {{ color: {C['text_primary']}; border-color: {C['accent']}; "
    f"background: {C['bg_raised']}; }}"
)

_BTN_ACTIVE = (
    f"QPushButton {{ background: transparent; border: 1px solid {C['border_bright']}; "
    f"border-radius: 4px; color: {C['text_muted']}; font-size: {F['small']}px; padding: 0 5px; }}"
    f"QPushButton:checked {{ background-color: {C['accent_dim']}; color: {C['accent']}; "
    f"border-color: {C['accent']}; }}"
    f"QPushButton:hover {{ border-color: {C['accent']}; }}"
)


class TriggerEntry(QFrame):
    edit_requested = Signal()
    delete_requested = Signal()

    def __init__(self, trigger: dict, parent=None):
        super().__init__(parent)
        self._trigger = trigger
        self.setFixedHeight(40)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(
            f"TriggerEntry {{ background-color: {C['bg_surface']}; "
            f"border: 1px solid {C['border']}; border-radius: 6px; }}"
        )
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 6, 0)
        layout.setSpacing(6)

        self.btn_active = QPushButton("●")
        self.btn_active.setCheckable(True)
        self.btn_active.setChecked(self._trigger.get("enabled", True))
        self.btn_active.setFixedSize(26, 26)
        self.btn_active.setStyleSheet(_BTN_ACTIVE)
        self.btn_active.toggled.connect(lambda v: self._trigger.update({"enabled": v}))

        lbl_name = QLabel(self._trigger.get("name", ""))
        lbl_name.setFixedWidth(66)
        lbl_name.setStyleSheet(f"color: {C['text_primary']}; font-size: {F['base']}px;")

        pattern = self._trigger.get("pattern", "")
        preview = pattern if len(pattern) <= 14 else pattern[:14] + "…"
        lbl_pattern = QLabel(preview)
        lbl_pattern.setStyleSheet(
            f"color: {C['text_muted']}; font-size: {F['small']}px; font-family: {MONO};"
        )

        action = self._trigger.get("action", "highlight")
        color, label = _ACTION_BADGES.get(action, ("#5a7899", action))
        lbl_action = QLabel(label)
        lbl_action.setFixedWidth(74)
        lbl_action.setStyleSheet(
            f"color: {color}; font-size: {F['label']}px; background: {rgba(color, 0.13)}; "
            f"border: 1px solid {rgba(color, 0.27)}; border-radius: 4px; padding: 1px 6px;"
        )

        layout.addWidget(self.btn_active)
        layout.addWidget(lbl_name)
        layout.addWidget(lbl_pattern, stretch=1)
        layout.addWidget(lbl_action)

        btn_edit = QPushButton("⚙")
        btn_edit.setFixedSize(28, 28)
        btn_edit.setStyleSheet(_BTN)
        btn_edit.clicked.connect(self.edit_requested.emit)

        btn_delete = QPushButton("×")
        btn_delete.setFixedSize(28, 28)
        btn_delete.setStyleSheet(_BTN)
        btn_delete.clicked.connect(self.delete_requested.emit)

        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)

    def get_trigger(self):
        return self._trigger
