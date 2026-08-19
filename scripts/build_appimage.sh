#!/usr/bin/env bash
# Monta o dist/SerialForge-x86_64.AppImage.
#
# Requer o appimagetool (https://github.com/AppImage/appimagetool/releases);
# aponte a variável APPIMAGETOOL para ele ou deixe-o no PATH.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-./venv/bin/python}"
APPIMAGETOOL="${APPIMAGETOOL:-$(command -v appimagetool || true)}"
if [ -z "$APPIMAGETOOL" ]; then
    echo "appimagetool não encontrado. Baixe-o e exporte APPIMAGETOOL=/caminho/appimagetool"
    exit 1
fi

echo "==> PyInstaller (onedir)"
"$PYTHON" -m PyInstaller --noconfirm --onedir --windowed \
    --name serialforge-app \
    --add-data "$ROOT/app/assets/icons:app/assets/icons" \
    --distpath build/appimage --workpath build/pyi-appimage --specpath build \
    main.py

echo "==> AppDir"
rm -rf build/AppDir
mkdir -p build/AppDir/usr/share/applications \
         build/AppDir/usr/share/icons/hicolor/256x256/apps
cp -r build/appimage/serialforge-app build/AppDir/usr/bin
mv build/AppDir/usr/bin/serialforge-app build/AppDir/usr/bin/serialforge
cp packaging/serialforge.desktop build/AppDir/serialforge.desktop
cp packaging/serialforge.desktop build/AppDir/usr/share/applications/
cp app/assets/icons/serialforge_256.png build/AppDir/serialforge.png
cp app/assets/icons/serialforge_256.png \
   build/AppDir/usr/share/icons/hicolor/256x256/apps/serialforge.png
ln -sf usr/bin/serialforge build/AppDir/AppRun

echo "==> appimagetool"
ARCH=x86_64 "$APPIMAGETOOL" build/AppDir dist/SerialForge-x86_64.AppImage
echo "Pronto: dist/SerialForge-x86_64.AppImage"
