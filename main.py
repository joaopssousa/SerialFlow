#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SerialForge")
    
    font = QFont("Courier New", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
