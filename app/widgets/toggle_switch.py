"""Toggle switch animado customizado"""
from PySide6.QtWidgets import QAbstractButton
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRectF, QSize
from PySide6.QtGui import QPainter, QColor


class ToggleSwitch(QAbstractButton):
    """Toggle switch com animação"""
    
    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedSize(34, 20)
        self.setCursor(Qt.PointingHandCursor)
        
        self._handle_pos = 1.0 if checked else 0.0
        
        self._animation = QPropertyAnimation(self, b"handle_pos", self)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._animation.setDuration(180)
        
        self.toggled.connect(self._animate)
    
    def _get_handle_pos(self):
        return self._handle_pos
    
    def _set_handle_pos(self, pos):
        self._handle_pos = pos
        self.update()
    
    handle_pos = Property(float, _get_handle_pos, _set_handle_pos)
    
    def _animate(self, checked):
        self._animation.stop()
        self._animation.setStartValue(self._handle_pos)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        checked = self.isChecked()
        t = self._handle_pos
        
        # Background
        bg = QColor("#00d4ff") if checked else QColor("#1d2436")
        border = QColor("#00d4ff") if checked else QColor("#2a3f55")
        
        painter.setPen(border)
        painter.setBrush(bg)
        painter.drawRoundedRect(0, 0, w, h, h/2, h/2)
        
        # Handle
        handle_size = h - 6
        handle_x = 3 + t * (w - handle_size - 6)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(QRectF(handle_x, 3, handle_size, handle_size))
    
    def sizeHint(self):
        return QSize(34, 20)
