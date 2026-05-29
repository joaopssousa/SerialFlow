"""Dialog de criação/edição de comando"""
import re
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QDoubleSpinBox
)
from app.style import get_stylesheet, COLORS as C
from app.widgets.pill_group import PillGroup


class CommandDialog(QDialog):
    def __init__(self, command=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Comando" if command else "Novo Comando")
        self.setMinimumWidth(420)
        self.setModal(True)
        self.setStyleSheet(get_stylesheet())
        self._build_ui()
        if command:
            self._populate(command)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self._section_label("Nome"))
        self.input_name = QLineEdit()
        self.input_name.setFixedHeight(34)
        self.input_name.setPlaceholderText("ex: Ping, Reset, ACK")
        layout.addWidget(self.input_name)

        layout.addWidget(self._section_label("Formato"))
        self.pill_format = PillGroup(["ASCII", "HEX"])
        self.pill_format.setFixedHeight(34)
        self.pill_format.selection_changed.connect(self._update_preview)
        layout.addWidget(self.pill_format)

        layout.addWidget(self._section_label("Frame"))
        self.input_frame = QLineEdit()
        self.input_frame.setFixedHeight(34)
        self.input_frame.setPlaceholderText("ASCII: PING\\r\\n   |   HEX: FF 00 01")
        self.input_frame.textChanged.connect(self._update_preview)
        layout.addWidget(self.input_frame)

        self.lbl_preview = QLabel("Preview: —")
        self.lbl_preview.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 11px; font-family: 'Courier New'; "
            f"background: transparent;"
        )
        layout.addWidget(self.lbl_preview)

        # Repeat interval
        repeat_row = QHBoxLayout()
        lbl_repeat = QLabel("Repetir a cada")
        lbl_repeat.setStyleSheet(f"color: {C['text_secondary']}; font-size: 12px;")

        self.spin_interval = QDoubleSpinBox()
        self.spin_interval.setRange(0.0, 3600.0)
        self.spin_interval.setValue(0.0)
        self.spin_interval.setSingleStep(0.5)
        self.spin_interval.setDecimals(1)
        self.spin_interval.setFixedWidth(75)
        self.spin_interval.setFixedHeight(34)
        self.spin_interval.setSpecialValueText("—")
        self.spin_interval.setStyleSheet(
            f"QDoubleSpinBox {{ background-color: {C['bg_surface']}; border: 1px solid {C['border_bright']}; "
            f"border-radius: 6px; padding: 0 8px; color: {C['text_primary']}; }}"
        )

        lbl_s = QLabel("s   (0 = desativado)")
        lbl_s.setStyleSheet(f"color: {C['text_muted']}; font-size: 11px;")

        repeat_row.addWidget(lbl_repeat)
        repeat_row.addWidget(self.spin_interval)
        repeat_row.addWidget(lbl_s)
        repeat_row.addStretch()
        layout.addLayout(repeat_row)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(34)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Salvar")
        btn_save.setFixedHeight(34)
        btn_save.setStyleSheet(
            f"QPushButton {{ background-color: {C['accent_dim']}; color: {C['accent']}; "
            f"border: 1px solid {C['accent']}44; border-radius: 6px; padding: 0 20px; font-weight: bold; }}"
            f"QPushButton:hover {{ background-color: {C['accent']}33; }}"
        )
        btn_save.clicked.connect(self.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _section_label(self, text):
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(
            f"color: {C['text_muted']}; font-size: 9px; letter-spacing: 1px; background: transparent;"
        )
        return lbl

    def _populate(self, command):
        self.input_name.setText(command.get("name", ""))
        if command.get("format", "ASCII") == "HEX":
            self.pill_format._group.button(1).setChecked(True)
            self.pill_format._on_clicked(1)
        self.input_frame.setText(command.get("payload", ""))
        self.spin_interval.setValue(command.get("repeat_interval") or 0.0)

    def _update_preview(self):
        text = self.input_frame.text()
        fmt = self.pill_format.current()
        try:
            if fmt == "ASCII":
                parsed = text.replace("\\n", "\n").replace("\\r", "\r")
                parsed = re.sub(
                    r'\\x([0-9a-fA-F]{2})',
                    lambda m: chr(int(m.group(1), 16)),
                    parsed,
                )
                data = parsed.encode("latin-1", errors="replace")
                self.lbl_preview.setText("HEX: " + " ".join(f"{b:02X}" for b in data))
            else:
                data = bytes.fromhex(text.replace(" ", ""))
                ascii_str = "".join(
                    chr(b) if 32 <= b < 127 else f"\\x{b:02X}" for b in data
                )
                self.lbl_preview.setText(f"ASCII: {ascii_str}")
        except Exception:
            self.lbl_preview.setText("Preview: —")

    def get_result(self):
        interval = self.spin_interval.value()
        return {
            "name": self.input_name.text().strip() or "Sem nome",
            "payload": self.input_frame.text(),
            "format": self.pill_format.current(),
            "repeat_interval": interval if interval > 0 else None,
        }
