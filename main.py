#!/usr/bin/env python3
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.main_window import MainWindow

ICON_DIR = Path(__file__).resolve().parent / "app" / "assets" / "icons"


def load_app_icon():
    # Tamanhos 16-32 usam um recorte mais fechado da arte para manter
    # a legibilidade; o Qt escolhe o arquivo certo para cada contexto
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256, 512):
        icon.addFile(str(ICON_DIR / f"serialforge_{size}.png"))
    return icon


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SerialForge")
    app.setWindowIcon(load_app_icon())

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
