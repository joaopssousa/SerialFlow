"""Toggle row - label + switch"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from app.widgets.toggle_switch import ToggleSwitch
from app.style import COLORS as C


class ToggleRow(QWidget):
    """Linha com label e toggle switch"""
    
    toggled = Signal(bool)
    
    def __init__(self, label, checked=False, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(
            f"background-color: {C['bg_surface']}; "
            f"border: 1px solid {C['border']}; "
            f"border-radius: 6px;"
        )
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {C['text_secondary']}; font-size: 11px; border: none; background: transparent;")
        
        self.toggle = ToggleSwitch(checked)
        self.toggle.toggled.connect(self.toggled)
        
        layout.addWidget(lbl)
        layout.addStretch()
        layout.addWidget(self.toggle)
    
    def mousePressEvent(self, event):
        self.toggle.setChecked(not self.toggle.isChecked())
        super().mousePressEvent(event)
    
    def isChecked(self):
        return self.toggle.isChecked()
