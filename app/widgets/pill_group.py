"""Pill buttons para seleção de modo"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup
from PySide6.QtCore import Qt, Signal
from app.style import COLORS as C, FONTS as F


class PillGroup(QWidget):
    """Grupo de botões pill (ASCII/HEX/Dec/Bin)"""
    
    selection_changed = Signal(str)
    
    def __init__(self, options, parent=None):
        super().__init__(parent)
        self._options = options
        
        self.setStyleSheet(
            f"background-color: {C['bg_surface']}; "
            f"border: 1px solid {C['border_bright']}; "
            f"border-radius: 6px;"
        )
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        
        for i, opt in enumerate(options):
            btn = QPushButton(opt)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(26)
            
            # Estilo pill
            if i == 0:
                btn.setChecked(True)
            
            btn.setStyleSheet(self._pill_style(i == 0))
            
            self._group.addButton(btn, i)
            layout.addWidget(btn)
        
        self._group.idClicked.connect(self._on_clicked)
    
    def _pill_style(self, active):
        if active:
            return f"""
                QPushButton {{
                    background-color: {C['accent']};
                    color: {C['bg_deep']};
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: {F['small']}px;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {C['text_secondary']};
                    border: none;
                    border-radius: 5px;
                    font-size: {F['small']}px;
                }}
                QPushButton:hover {{
                    background-color: {C['bg_raised']};
                    color: {C['text_primary']};
                }}
            """
    
    def _on_clicked(self, idx):
        # Atualiza estilos
        for i in range(len(self._options)):
            btn = self._group.button(i)
            btn.setStyleSheet(self._pill_style(i == idx))
        
        self.selection_changed.emit(self._options[idx])
    
    def current(self):
        btn = self._group.checkedButton()
        return btn.text() if btn else self._options[0]
