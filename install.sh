#!/usr/bin/env bash
# Instalador do SerialForge
#
#   sudo ./install.sh              instala para todos os usuários (/usr/local)
#   ./install.sh --user            instala só para você (~/.local, sem sudo)
#   sudo ./install.sh --uninstall  remove a instalação de sistema
#   ./install.sh --user --uninstall
#
# Requer o binário já compilado em dist/serialforge:
#   ./venv/bin/python -m PyInstaller serialforge.spec
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
MODE="system"
ACTION="install"

for arg in "$@"; do
    case "$arg" in
        --user) MODE="user" ;;
        --uninstall) ACTION="uninstall" ;;
        *) echo "Opção desconhecida: $arg"; exit 1 ;;
    esac
done

if [ "$MODE" = "user" ]; then
    PREFIX="${DESTDIR:-$HOME/.local}"
else
    PREFIX="${DESTDIR:-/usr/local}"
    if [ "$ACTION" = "install" ] && [ -z "${DESTDIR:-}" ] && [ "$(id -u)" -ne 0 ]; then
        echo "Instalação de sistema requer sudo (ou use --user)."; exit 1
    fi
fi

BIN_DIR="$PREFIX/bin"
APPS_DIR="$PREFIX/share/applications"
ICON_BASE="$PREFIX/share/icons/hicolor"
ICON_SIZES="16 24 32 48 64 128 256 512"

if [ "$ACTION" = "uninstall" ]; then
    rm -f "$BIN_DIR/serialforge" "$APPS_DIR/serialforge.desktop"
    for s in $ICON_SIZES; do
        rm -f "$ICON_BASE/${s}x${s}/apps/serialforge.png"
    done
    echo "SerialForge removido de $PREFIX"
else
    if [ ! -f "$HERE/dist/serialforge" ]; then
        echo "Binário não encontrado. Gere-o antes com:"
        echo "  ./venv/bin/python -m PyInstaller serialforge.spec"
        exit 1
    fi
    install -Dm755 "$HERE/dist/serialforge" "$BIN_DIR/serialforge"
    install -Dm644 "$HERE/packaging/serialforge.desktop" "$APPS_DIR/serialforge.desktop"
    for s in $ICON_SIZES; do
        install -Dm644 "$HERE/app/assets/icons/serialforge_${s}.png" \
            "$ICON_BASE/${s}x${s}/apps/serialforge.png"
    done
    echo "SerialForge instalado em $BIN_DIR/serialforge"
    echo "Atalho no menu: $APPS_DIR/serialforge.desktop"
fi

# Atualiza caches do menu/ícones (melhor esforço; alguns ambientes nem precisam)
command -v update-desktop-database >/dev/null && update-desktop-database "$APPS_DIR" 2>/dev/null || true
command -v gtk-update-icon-cache >/dev/null && gtk-update-icon-cache -q "$ICON_BASE" 2>/dev/null || true

if [ "$ACTION" = "install" ]; then
    if ! id -nG | grep -qwE 'uucp|dialout'; then
        echo ""
        echo "AVISO: seu usuário não está no grupo da porta serial."
        echo "  Arch/Manjaro:  sudo usermod -aG uucp \$USER"
        echo "  Debian/Ubuntu: sudo usermod -aG dialout \$USER"
        echo "  (faça logout/login depois)"
    fi
fi
