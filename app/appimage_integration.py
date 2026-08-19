"""Auto-integração do AppImage com o menu de aplicativos.

Tudo em ~/.local e ~/Applications — sem sudo. O runtime do AppImage exporta
a variável APPIMAGE com o caminho do arquivo em execução; é ela que indica
que estamos rodando empacotados.
"""
import os
import shutil
import subprocess
from pathlib import Path

APPS_DIR = Path.home() / ".local" / "share" / "applications"
BIN_DIR = Path.home() / ".local" / "bin"
ICONS_BASE = Path.home() / ".local" / "share" / "icons" / "hicolor"
TARGET_DIR = Path.home() / "Applications"
DESKTOP_FILE = APPS_DIR / "serialforge.desktop"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256, 512)

_DESKTOP_TEMPLATE = """[Desktop Entry]
Type=Application
Name=SerialForge
Comment=Terminal serial com triggers, comandos e monitoramento de linhas
Exec="{exec_path}"
Icon=serialforge
Terminal=false
Categories=Development;Electronics;Utility;
Keywords=serial;uart;rs232;terminal;baudrate;tty;
StartupWMClass=serialforge
"""


def running_as_appimage():
    return bool(os.environ.get("APPIMAGE"))


def is_integrated():
    """Já existe atalho apontando para um AppImage que ainda existe?"""
    if not DESKTOP_FILE.exists():
        return False
    for line in DESKTOP_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("Exec="):
            path = line[5:].strip().strip('"')
            return Path(path).exists()
    return False


def integrate(icon_dir):
    """Copia o AppImage para ~/Applications e registra atalho + ícones."""
    src = Path(os.environ["APPIMAGE"])
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    target = TARGET_DIR / "SerialForge.AppImage"
    if src.resolve() != target.resolve():
        shutil.copy2(src, target)
    target.chmod(0o755)

    APPS_DIR.mkdir(parents=True, exist_ok=True)
    DESKTOP_FILE.write_text(
        _DESKTOP_TEMPLATE.format(exec_path=target), encoding="utf-8"
    )

    icon_dir = Path(icon_dir)
    for s in ICON_SIZES:
        icon = icon_dir / f"serialforge_{s}.png"
        if icon.exists():
            dest = ICONS_BASE / f"{s}x{s}" / "apps"
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(icon, dest / "serialforge.png")

    # comando `serialforge` no terminal (~/.local/bin costuma estar no PATH)
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    link = BIN_DIR / "serialforge"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(target)

    for cmd in (["update-desktop-database", str(APPS_DIR)],
                ["gtk-update-icon-cache", "-q", str(ICONS_BASE)]):
        try:
            subprocess.run(cmd, check=False, capture_output=True)
        except FileNotFoundError:
            pass
    return target
