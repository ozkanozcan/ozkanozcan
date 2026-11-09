"""profile.json + assets/ascii-art*.txt + cache/stats.json -> dark_mode.svg / light_mode.svg

Neofetch tarzı terminal kartı: solda ASCII portre, sağda nokta dolgulu anahtar/değer satırları.
"""
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "profile.json").read_text())

THEMES = {
    "dark": {
        "bg": "#161b22", "border": "#30363d", "text": "#c9d1d9", "value": "#a5d6ff",
        "dots": "#616e7f", "add": "#3fb950", "art": "assets/ascii-art.txt",
    },
    "light": {
        "bg": "#f6f8fa", "border": "#d0d7de", "text": "#24292f", "value": "#0a3069",
        "dots": "#8c959f", "add": "#1a7f37", "art": "assets/ascii-art.txt",
    },
}

WIDTH = 1000
COLS = 56              # sağ sütunun karakter genişliği
FONT = 16
LINE = 20
RIGHT_X = 430
TOP = 36
ART_FONT = 11.5
ART_LINE = 12.8


def uptime(created_at):
    start = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    months = (now.year - start.year) * 12 + now.month - start.month
    days = now.day - start.day
    if days < 0:
        months -= 1
        days += 30
    y, m = divmod(months, 12)
    return f"{y} yıl, {m} ay, {days} gün"


def fmt(n):
    return f"{n:,}".replace(",", ".")


def kv(key, value):
    """'. Key: ........ value' satırını tspan'lere böler."""
    head = f". {key}:"
    dots = COLS - len(head) - len(value) - 2
    dots = "." * max(dots, 1)
    return (
        f'<tspan class="cc">. </tspan><tspan class="key">{escape(key)}</tspan>:'
        f'<tspan class="cc"> {dots} </tspan><tspan class="value">{escape(value)}</tspan>'
    )


def kv_pair(k1, v1, k2, v2):
    """İki istatistiği tek satırda gösterir: '. Repos: .. 99 | Stars: ..... 10'"""
    half = COLS // 2 - 2
    left_dots = "." * max(half - len(k1) - len(v1) - 5, 1)
    right_dots = "." * max(COLS - half - 3 - len(k2) - len(v2) - 3, 1)
    return (
        f'<tspan class="cc">. </tspan><tspan class="key">{k1}</tspan>:'
        f'<tspan class="cc"> {left_dots} </tspan><tspan class="value">{v1}</tspan>'
        f' | <tspan class="key">{k2}</tspan>:'
        f'<tspan class="cc"> {right_dots} </tspan><tspan class="value">{v2}</tspan>'
    )


def header(title):
    if title is None:
        return f'<tspan class="cc">{"—" * COLS}</tspan>'
    rest = COLS - len(title) - 3
    return f'- <tspan class="title">{escape(title)}</tspan> <tspan class="cc">{"—" * rest}</tspan>'


def right_lines(stats):
    prompt = CONFIG["prompt"]
    lines = [f'<tspan class="title">{escape(prompt)}</tspan> <tspan class="cc">{"—" * (COLS - len(prompt) - 1)}</tspan>']
    for i, section in enumerate(CONFIG["sections"]):
        if i > 0 or section["title"]:
            lines.append(header(section["title"]) if section["title"] or i > 0 else "")
        if section["rows"] == "stats":
            year = datetime.now(timezone.utc).year
            lines += [
                kv_pair("Repos", fmt(stats["repos"]), "Stars", fmt(stats["stars"])),
                kv_pair("Commits", fmt(stats["commits"]), "Followers", fmt(stats["followers"])),
                kv_pair("Katkı", fmt(stats["contributions"]), str(year), fmt(stats["contributions_this_year"])),
            ]
            continue
        for key, value in section["rows"]:
            lines.append(kv(key, value.replace("{uptime}", uptime(stats["created_at"]))))
    return lines


def build(theme_name, stats):
    t = THEMES[theme_name]
    accent = CONFIG["accent"][theme_name]
    art = (ROOT / t["art"]).read_text().rstrip("\n").split("\n")
    lines = right_lines(stats)

    right_h = len(lines) * LINE
    art_h = len(art) * ART_LINE
    height = int(max(right_h, art_h) + TOP * 2)
    art_top = (height - art_h) / 2 + ART_LINE * 0.75

    out = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}px" height="{height}px" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="ConsolasFallback,Consolas,Menlo,monospace">',
        "<style>",
        "@font-face { src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback'; "
        "font-display: swap; size-adjust: 109%; }",
        f".key {{fill: {accent};}}",
        f".value {{fill: {t['value']};}}",
        f".title {{fill: {accent}; font-weight: bold;}}",
        f".cc {{fill: {t['dots']};}}",
        "text, tspan {white-space: pre;}",
        "@keyframes blink { 50% { opacity: 0; } }",
        ".cursor { animation: blink 1.1s step-end infinite; }",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" fill="{t["bg"]}" '
        f'stroke="{t["border"]}" rx="15"/>',
        f'<text fill="{t["text"]}" font-size="{ART_FONT}px">',
    ]
    for i, row in enumerate(art):
        out.append(f'<tspan x="20" y="{art_top + i * ART_LINE:.2f}">{escape(row)}</tspan>')
    out.append("</text>")
    out.append(f'<text fill="{t["text"]}" font-size="{FONT}px">')
    for i, row in enumerate(lines):
        out.append(f'<tspan x="{RIGHT_X}" y="{TOP + 14 + i * LINE}">{row}</tspan>')
    # Terminal hissi: son satırın altında yanıp sönen imleç.
    y = TOP + 14 + len(lines) * LINE
    out.append(f'<tspan x="{RIGHT_X}" y="{y}" class="key">❯ </tspan><tspan class="cursor" fill="{t["text"]}">█</tspan>')
    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    stats = json.loads((ROOT / "cache/stats.json").read_text())
    for name in THEMES:
        (ROOT / f"{name}_mode.svg").write_text(build(name, stats))
    print("dark_mode.svg, light_mode.svg yazıldı")


if __name__ == "__main__":
    main()
