#!/usr/bin/env bash
# Gera os artefatos de release em dist/:
#   - serialforge                      executável único
#   - SerialForge-linux-x86_64.tar.gz  pacote com install.sh (menu + /usr/local/bin)
#   - SerialForge-x86_64.AppImage      se APPIMAGETOOL estiver disponível
#
# Uso local:  ./scripts/build_release.sh
# No CI:      PYTHON=python APPIMAGETOOL=/caminho/appimagetool ./scripts/build_release.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-./venv/bin/python}"
PKG="SerialForge-linux-x86_64"

echo "==> Executável (PyInstaller onefile)"
"$PYTHON" -m PyInstaller --noconfirm --onefile --windowed \
    --name serialforge \
    --add-data "$ROOT/app/assets/icons:app/assets/icons" \
    main.py

echo "==> Pacote com instalador"
rm -rf "build/$PKG"
mkdir -p "build/$PKG/dist" "build/$PKG/packaging" "build/$PKG/app/assets/icons"
cp install.sh "build/$PKG/"
cp dist/serialforge "build/$PKG/dist/"
cp packaging/serialforge.desktop "build/$PKG/packaging/"
cp app/assets/icons/serialforge_*.png "build/$PKG/app/assets/icons/"
tar czf "dist/$PKG.tar.gz" -C build "$PKG"

APPIMAGETOOL="${APPIMAGETOOL:-$(command -v appimagetool || true)}"
if [ -n "$APPIMAGETOOL" ]; then
    echo "==> AppImage"
    APPIMAGETOOL="$APPIMAGETOOL" PYTHON="$PYTHON" ./scripts/build_appimage.sh
else
    echo "==> AppImage: pulado (appimagetool não encontrado)"
fi

echo ""
echo "Artefatos em dist/:"
ls -lh dist/ | tail -n +2
