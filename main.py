#!/usr/bin/env python3
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon
from app.main_window import MainWindow
from app import appimage_integration

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
    # associa a janela ao serialforge.desktop (icone/agrupamento no Wayland)
    app.setDesktopFileName("serialforge")
    app.setWindowIcon(load_app_icon())

    window = MainWindow()
    window.show()

    _offer_menu_integration(window)

    sys.exit(app.exec())


def _offer_menu_integration(parent):
    """Rodando como AppImage e ainda sem atalho: oferece instalar no menu"""
    if not appimage_integration.running_as_appimage():
        return
    settings = QSettings("SerialForge", "SerialForge")
    if appimage_integration.is_integrated():
        return
    if settings.value("integration_declined", False, type=bool):
        return
    resp = QMessageBox.question(
        parent,
        "Instalar no menu?",
        "Deseja adicionar o SerialForge ao menu de aplicativos?\n\n"
        "O arquivo será copiado para ~/Applications e um atalho será\n"
        "criado — sem precisar de senha de administrador.",
        QMessageBox.Yes | QMessageBox.No,
    )
    if resp == QMessageBox.Yes:
        try:
            target = appimage_integration.integrate(ICON_DIR)
            QMessageBox.information(
                parent, "Instalado",
                f"Pronto! O SerialForge está no menu de aplicativos.\n\n"
                f"Executável: {target}",
            )
        except Exception as e:
            QMessageBox.warning(parent, "Erro", f"Não foi possível instalar:\n{e}")
    else:
        settings.setValue("integration_declined", True)


if __name__ == "__main__":
    main()
