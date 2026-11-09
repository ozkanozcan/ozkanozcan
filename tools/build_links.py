"""profile.json'daki 'links' listesinden piksel-art bağlantı butonları üretir.

Her bağlantı için link_<n>_dark.svg ve link_<n>_light.svg yazar (n = 1, 2, 3...).
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "profile.json").read_text())

PX = 3  # bir "piksel"in boyutu
W, H = 330, 60

THEMES = {
    "dark": {"bg": "#161b22", "border": "#30363d", "text": "#c9d1d9"},
    "light": {"bg": "#f6f8fa", "border": "#d0d7de", "text": "#24292f"},
}

# 11x9 piksel ikonlar ('#' = dolu)
ICONS = {
    "globe": [
        "...#####...",
        "..#..#..#..",
        ".#..#.#..#.",
        "###########",
        "#...#.#...#",
        "###########",
        ".#..#.#..#.",
        "..#..#..#..",
        "...#####...",
    ],
    "x": [
        "##.......##",
        ".##.....##.",
        "..##...##..",
        "...##.##...",
        "....###....",
        "...##.##...",
        "..##...##..",
        ".##.....##.",
        "##.......##",
    ],
    "mail": [
        "###########",
        "##.......##",
        "#.#.....#.#",
        "#..#...#..#",
        "#...#.#...#",
        "#....#....#",
        "#.........#",
        "#.........#",
        "###########",
    ],
    "linkedin": [
        "###########",
        "#.##......#",
        "#.........#",
        "#.##.#.##.#",
        "#.##.##..##",
        "#.##.#...##",
        "#.##.#...##",
        "#.##.#...##",
        "###########",
    ],
}


def pixel_box(x, y, w, h, fill):
    """Köşeleri bir piksel kırpılmış kutu."""
    return (
        f'<path d="M{x + PX} {y}h{w - 2 * PX}v{PX}h{PX}v{h - 2 * PX}h-{PX}v{PX}'
        f'h-{w - 2 * PX}v-{PX}h-{PX}v-{h - 2 * PX}h{PX}z" fill="{fill}"/>'
    )


def icon_paths(name):
    rows = ICONS[name]
    d = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                d.append(f"M{x * PX} {y * PX}h{PX}v{PX}h-{PX}z")
    return "".join(d), len(rows[0]) * PX, len(rows) * PX


def build(link, theme_name, accent):
    t = THEMES[theme_name]
    label = escape(link["label"])
    text_w = len(link["label"]) * 18 * 0.6
    d, iw, ih = icon_paths(link["icon"])
    gap = 14
    total = iw + gap + text_w
    ix = (W - total) / 2
    iy = (H - ih) / 2
    tx = ix + iw + gap
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}px" height="{H}px" viewBox="0 0 {W} {H}" font-family="ConsolasFallback,Consolas,Menlo,monospace">
<style>
@font-face {{ src: local('Consolas'); font-family: 'ConsolasFallback'; font-display: swap; size-adjust: 109%; }}
text {{white-space: pre;}}
.px {{shape-rendering: crispEdges;}}
@keyframes hop {{ 0%, 80%, 100% {{ transform: translateY(0); }} 88% {{ transform: translateY(-{PX}px); }} }}
.ico {{ animation: hop 2.6s steps(1) infinite; }}
</style>
<g class="px">
{pixel_box(6, 0, W - 12, H, t["border"])}
{pixel_box(6 + PX, PX, W - 12 - 2 * PX, H - 2 * PX, t["bg"])}
<rect x="{6 + 2 * PX}" y="{H - 2 * PX}" width="{W - 12 - 4 * PX}" height="{PX}" fill="{accent}"/>
<g transform="translate({ix:.2f},{iy:.2f})"><g class="ico"><path d="{d}" fill="{accent}"/></g></g>
</g>
<text x="{tx:.2f}" y="{H / 2 + 6.3:.2f}" font-size="18px" fill="{t["text"]}">{label}</text>
</svg>
"""


def main():
    for i, link in enumerate(CONFIG["links"], 1):
        for theme in THEMES:
            (ROOT / f"link_{i}_{theme}.svg").write_text(build(link, theme, CONFIG["accent"][theme]))
    print(f"{len(CONFIG['links'])} buton yazıldı")


if __name__ == "__main__":
    main()
