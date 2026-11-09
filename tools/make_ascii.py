"""Bir fotoğrafı karttaki ASCII portreye çevirir (tek seferlik; çıktı assets/ altına yazılır).

Kullanım: python tools/make_ascii.py foto.jpg [--crop x0,y0,x1,y1] [--cols 58]
Pillow gerekir: pip install pillow
"""
import argparse
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
# Koyudan açığa: koyu temada parlak pikseller yoğun karakter olur.
RAMP = " .:-=+*#%@"


def convert(img, cols, invert, gamma=1.8):
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img, cutoff=2)
    img = img.filter(ImageFilter.SHARPEN)
    # Monospace karakterler yaklaşık 2 kat uzun; satır sayısını yarıya indir.
    rows = round(img.height / img.width * cols * 0.5)
    img = img.resize((cols, rows), Image.LANCZOS)
    lines = []
    for y in range(rows):
        row = ""
        for x in range(cols):
            v = (img.getpixel((x, y)) / 255) ** gamma
            if invert:
                v = 1 - v
            row += RAMP[min(int(v * len(RAMP)), len(RAMP) - 1)]
        lines.append(row.rstrip())
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument("--crop", help="x0,y0,x1,y1")
    p.add_argument("--cols", type=int, default=58)
    a = p.parse_args()
    img = Image.open(a.image).convert("RGB")
    if a.crop:
        img = img.crop(tuple(int(v) for v in a.crop.split(",")))
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets/ascii-art.txt").write_text(convert(img, a.cols, False))
    print((ROOT / "assets/ascii-art.txt").read_text())


if __name__ == "__main__":
    main()
