"""Indicador de linha de controle serial (LED estilo Docklight)"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QRectF, QSize
from PySide6.QtGui import QPainter, QColor, QFont
from app.style import COLORS as C, FONTS as F


class LineIndicator(QWidget):
    """LED com label: saídas (RTS/DTR) são clicáveis, entradas são só leitura"""

    clicked = Signal()

    def __init__(self, label, output=False, parent=None):
        super().__init__(parent)
        self.label = label
        self.output = output
        self._on = False
        self._line_enabled = False
        self.setFixedSize(38, 42)
        if output:
            self.setToolTip(f"{label}: clique para alternar a linha")
        else:
            self.setToolTip(f"{label}: estado sinalizado pelo dispositivo")

    def setOn(self, on):
        if self._on != bool(on):
            self._on = bool(on)
            self.update()

    def isOn(self):
        return self._on

    def setLineEnabled(self, enabled):
        self._line_enabled = bool(enabled)
        if self.output:
            self.setCursor(Qt.PointingHandCursor if self._line_enabled else Qt.ArrowCursor)
        self.update()

    def mousePressEvent(self, event):
        if self.output and self._line_enabled and event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()

        font = QFont(self.font())
        font.setPixelSize(F['label'])
        font.setBold(self.output)
        painter.setFont(font)
        painter.setPen(QColor(C['text_secondary'] if self._line_enabled else C['text_muted']))
        painter.drawText(QRectF(0, 2, w, 14), Qt.AlignHCenter | Qt.AlignVCenter, self.label)

        d = 12
        x = (w - d) / 2
        y = 22

        if not self._line_enabled:
            fill = QColor(C['bg_raised'])
            border = QColor(C['border'])
        elif self._on:
            fill = QColor(C['green'])
            border = QColor(C['green'])
        else:
            fill = QColor(C['bg_raised'])
            border = QColor(C['border_bright'])

        if self._line_enabled and self._on:
            glow = QColor(C['green'])
            glow.setAlpha(50)
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(QRectF(x - 3, y - 3, d + 6, d + 6))

        painter.setPen(border)
        painter.setBrush(fill)
        painter.drawEllipse(QRectF(x, y, d, d))

    def sizeHint(self):
        return QSize(38, 42)
