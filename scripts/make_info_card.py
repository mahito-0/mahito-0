#!/usr/bin/env python3
"""
Generate a neofetch-style info card SVG that sits beside mahito-ascii.svg.

The canvas is 840 x 880 to match the ASCII portrait so both panels line up
cleanly when displayed in a table.
Each line fades and slides in on a short stagger so the panel looks like it's
printing next to the portrait.
Setting STATIC=1 emits a frozen frame without animations.

Usage:
    python scripts/make_info_card.py [output.svg]
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

W, H = 840, 880
PAD = 28
TITLEBAR_H = 30

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
MUTED = "#8b949e"
KEY_COLOR = "#58a6ff"
ACCENT_GREEN = "#3fb950"
ACCENT_CYAN = "#38bdf8"
ACCENT_YELLOW = "#f2cc60"
ACCENT_PURPLE = "#bc8cff"
ACCENT_RED = "#ff7b72"
TEXT_WHITE = "#f0f6fc"

ASCII_ART = [
    r"     .---.     ",
    r"    /     \    ",
    r"   | () () |   ",
    r"    \  ^  /    ",
    r"   .-'` `-'.   ",
    r"  / /     \ \  ",
    r" / / |   | \ \ ",
    r"/_/  |   |  \_" + "\\",
    r"     |   |     ",
    r"    /     \    ",
    r"   |  / \  |   ",
    r"   '-'   '-'   ",
    r"  [BUG HUNTER] ",
]

INFO_ROWS = [
    ("OS", "Windows 11 x86_64 / Ubuntu Linux", ACCENT_CYAN),
    ("Host", "American Intl University-Bangladesh (AIUB)", TEXT_WHITE),
    ("Kernel", "B.Sc in Computer Science & Engineering", TEXT_WHITE),
    ("Role", "SQA Engineer & Quality Specialist", ACCENT_GREEN),
    ("Now", "Rigorous Manual Testing & Bug Hunting", ACCENT_YELLOW),
    ("Collaborate", "Functional, UI/UX & Manual API QA", TEXT_WHITE),
    ("Tech Stack", "Postman · Jira · Git · Python · C# · Java · SQL", ACCENT_CYAN),
    ("Frameworks", "HTML5 · CSS3 · .NET · MySQL · Apache", TEXT_WHITE),
    ("Focus", "Test Plans · Defect Tracking · Edge Cases", ACCENT_PURPLE),
    ("Learning", "API Automation Testing & Agile QA", ACCENT_GREEN),
    ("Portfolio", "mahito-0.github.io/Portfolio", KEY_COLOR),
    ("Email", "syedmahmud10270@gmail.com", KEY_COLOR),
    ("Location", "Dhaka, Bangladesh", MUTED),
    ("Fun Fact", "Catching that sneaky bug before production!", ACCENT_YELLOW),
]

COLOR_BLOCKS = [
    "#484f58", "#ff7b72", "#3fb950", "#d29922",
    "#58a6ff", "#bc8cff", "#39c5cf", "#f0f6fc",
]
COLOR_BLOCKS_BRIGHT = [
    "#6e7681", "#ffa198", "#56d364", "#e3b341",
    "#79c0ff", "#d2a8ff", "#56d4dd", "#ffffff",
]

parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
)

parts.append("""
<style>
@keyframes fadeSlide {
  0%   { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}
.term-line {
  opacity: 0;
  animation: fadeSlide 0.38s cubic-bezier(0.16, 1, 0.3, 1) both;
}
@media (prefers-reduced-motion: reduce) {
  .term-line {
    opacity: 1 !important;
    transform: none !important;
    animation: none !important;
  }
}
</style>
""")

parts.append('<defs>'
             f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
             f'</linearGradient></defs>')

parts.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" '
             f'fill="none" stroke="{FRAME}" stroke-width="1"/>')

parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">mahito@github: ~$ neofetch</text>')

start_delay = 0.1
delay_step = 0.08
cur_delay = start_delay

# Header: mahito@aiub-workstation
header_y = TITLEBAR_H + 42
def anim_attr(d):
    return "" if STATIC else f' class="term-line" style="animation-delay:{d:.3f}s"'

parts.append(
    f'<g{anim_attr(cur_delay)}>'
    f'<text x="{PAD}" y="{header_y}" font-size="19" font-weight="700">'
    f'<tspan fill="{ACCENT_CYAN}">mahito</tspan>'
    f'<tspan fill="{MUTED}">@</tspan>'
    f'<tspan fill="{ACCENT_GREEN}">aiub-workstation</tspan>'
    f'</text></g>'
)
cur_delay += delay_step

# Divider dashes
div_y = header_y + 18
parts.append(
    f'<g{anim_attr(cur_delay)}>'
    f'<text x="{PAD}" y="{div_y}" fill="{FRAME}" font-size="16">'
    f'----------------------------------------------------------------</text></g>'
)
cur_delay += delay_step

# Layout: Left side ASCII badge, Right side Neofetch key-values
LEFT_X = PAD
LEFT_COL_W = 160
RIGHT_X = PAD + LEFT_COL_W + 15
LINE_H = 34
content_y = div_y + 36

# Left ASCII Bug Hunter Art
for idx, line in enumerate(ASCII_ART):
    y = content_y + idx * 24
    color = ACCENT_GREEN if "BUG" in line else ACCENT_CYAN
    safe_line = html.escape(line)
    parts.append(
        f'<g{anim_attr(cur_delay)}>'
        f'<text xml:space="preserve" x="{LEFT_X}" y="{y}" fill="{color}" font-size="14" font-weight="700">{safe_line}</text>'
        f'</g>'
    )
    cur_delay += 0.03

# Right Neofetch Rows
row_y = content_y
for key, val, val_col in INFO_ROWS:
    safe_key = html.escape(key)
    safe_val = html.escape(val)
    parts.append(
        f'<g{anim_attr(cur_delay)}>'
        f'<text x="{RIGHT_X}" y="{row_y}" font-size="14.5">'
        f'<tspan fill="{KEY_COLOR}" font-weight="700">{safe_key}</tspan>'
        f'<tspan fill="{MUTED}">: </tspan>'
        f'<tspan fill="{val_col}">{safe_val}</tspan>'
        f'</text>'
        f'</g>'
    )
    row_y += LINE_H
    cur_delay += delay_step

# Neofetch Color Palette Blocks at bottom
palette_y = H - PAD - 48
block_w = 42
block_h = 16
gap = 6
palette_x = PAD

parts.append(f'<g{anim_attr(cur_delay)}>')
# Row 1: normal colors
for i, col in enumerate(COLOR_BLOCKS):
    bx = palette_x + i * (block_w + gap)
    parts.append(f'<rect x="{bx}" y="{palette_y}" width="{block_w}" height="{block_h}" rx="3" fill="{col}"/>')
# Row 2: bright colors
for i, col in enumerate(COLOR_BLOCKS_BRIGHT):
    bx = palette_x + i * (block_w + gap)
    parts.append(f'<rect x="{bx}" y="{palette_y + block_h + 5}" width="{block_w}" height="{block_h}" rx="3" fill="{col}"/>')
parts.append('</g>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT}: {W} x {H}, {len(svg)} bytes")
