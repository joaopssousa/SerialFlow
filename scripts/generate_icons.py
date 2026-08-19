#!/usr/bin/env python3
"""Gera o conjunto de ícones do SerialForge em app/assets/icons/.

- 64px+: arte completa (app/assets/artwork/serialforge_icon.png).
- 16-48px: pixel art da bigorna (app/assets/artwork/serialforge_pixel.png),
  feita para tamanhos pequenos — taskbar e barra de título.

Uso: QT_QPA_PLATFORM=offscreen python scripts/generate_icons.py
"""
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QImage, QPainter, Qt

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "app" / "assets" / "artwork"
OUT_DIR = ROOT / "app" / "assets" / "icons"

LARGE_SIZES = (64, 128, 256, 512)   # arte completa
SMALL_SIZES = (16, 24, 32, 48)      # pixel art


def save_square(img, s, path):
    scaled = img.scaled(s, s, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    canvas = QImage(s, s, QImage.Format_ARGB32)
    canvas.fill(Qt.transparent)
    p = QPainter(canvas)
    p.drawImage((s - scaled.width()) // 2, (s - scaled.height()) // 2, scaled)
    p.end()
    canvas.save(str(path))


def main():
    QGuiApplication(sys.argv)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full = QImage(str(ART / "serialforge_icon.png"))
    pixel = QImage(str(ART / "serialforge_pixel.png"))
    for s in LARGE_SIZES:
        save_square(full, s, OUT_DIR / f"serialforge_{s}.png")
    for s in SMALL_SIZES:
        save_square(pixel, s, OUT_DIR / f"serialforge_{s}.png")
    print(f"Ícones gerados em {OUT_DIR}")


if __name__ == "__main__":
    main()
