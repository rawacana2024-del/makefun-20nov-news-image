#!/usr/bin/env python3
"""make.fun bounty entry - "Sum up 20 November's world news in one image".

Renders a newspaper front page (11 verified stories from the 20 Nov 2026
brief) to entry.png, 1024x1024 RGB, under 1 MiB.

PURE PYTHON STANDARD LIBRARY ONLY. No Pillow, no third-party packages,
no system font files, no network. Text is drawn with a small 5x7 bitmap
font defined in this file; the PNG is written by hand with zlib. The
grader runs "Python 3.13 main.py" in a fresh container where nothing is
installed, so this file must (and does) work with the stdlib alone.

Deterministic: two runs write byte-identical output.
Prepared for Irpan, 20 Nov 2026. Not submitted anywhere by this script.
"""
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024
M = 32  # margin
PAPER = (251, 247, 238)
INK = (18, 18, 18)
RED = (178, 34, 34)
GREY = (110, 110, 105)
RULE = (60, 60, 60)
GRIDLINE = (200, 196, 186)
SEPLINE = (190, 186, 176)
SUMMARY = (40, 40, 40)
WHITE = (255, 255, 255)


class Canvas:
    """A plain RGB pixel buffer with a few drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x0, y0, x1, y1, color):
        """Filled rectangle, inclusive corners, clipped to the canvas."""
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        if x1 < x0 or y1 < y0:
            return
        row = bytes(color) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x0, x1, y, color, width=1):
        for dy in range(width):
            self.rect(x0, y + dy, x1, y + dy, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        """Bresenham line, with a square brush of the given width."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = width // 2
        while True:
            self.rect(x0 - half, y0 - half, x0 + half, y0 + half, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        """Filled circle, drawn as horizontal scanlines."""
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.rect(cx - dx, cy + dy, cx + dx, cy + dy, color)

    def save_png(self, path):
        """Write the buffer as an 8-bit RGB PNG (signature, IHDR, IDAT, IEND)."""
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)  # filter type 0: none
            raw += self.px[y * stride:(y + 1) * stride]
        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        png = b"\x89PNG\r\n\x1a\n"
        png += _chunk(b"IHDR", ihdr)
        png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        png += _chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(png)


def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out

# ---------------------------------------------------------------------------
# 5x7 bitmap font, defined in this file. Each glyph is 7 rows of 5 bits,
# "1" is ink, "0" is blank. One character cell is 6 px wide (5 + 1 gap),
# so text width is len(text) * 6 * scale. Glyphs are hand-drawn for
# legibility at small sizes; bold is faked by thickening each stroke 1 px.
# ---------------------------------------------------------------------------
FONT = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ":": ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    ";": ("00000", "00100", "00000", "00000", "00100", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "\\": ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "`": ("00100", "00100", "00010", "00000", "00000", "00000", "00000"),
}

FONT.update({
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "{": ("00010", "00100", "00100", "01100", "00100", "00100", "00010"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "}": ("01000", "00100", "00100", "00110", "00100", "00100", "01000"),
    "~": ("00000", "00000", "01101", "10110", "00000", "00000", "00000"),
    # Specials used by the page copy (bullet, em/en dash).
    "•": ("00000", "00000", "00000", "01110", "01110", "00000", "00000"),
    "—": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "–": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
})

# Characters the font has no glyph for: fold them to a plain equivalent.
# Curly quotes become straight ones; the ellipsis becomes three periods.
NORMALIZE = {
    "’": "'", "‘": "'", "“": '"', "”": '"', "…": "...",
    "â": "a", "à": "a", "á": "a", "ä": "a", "ã": "a",
    "ê": "e", "è": "e", "é": "e", "ë": "e",
    "î": "i", "ì": "i", "í": "i", "ï": "i",
    "ô": "o", "ò": "o", "ó": "o", "ö": "o", "õ": "o",
    "û": "u", "ù": "u", "ú": "u", "ü": "u",
    "ç": "c", "ñ": "n", "ÿ": "y",
}


def normalize(text):
    return "".join(NORMALIZE.get(ch, ch) for ch in text)


def text_width(text, scale):
    """Pixel width of text at the given scale (monospace: 6 px per char)."""
    return len(normalize(text)) * 6 * scale


def draw_text(cv, x, y, text, scale, color, bold=False):
    """Draw one line of text; returns the x just past the last character."""
    cx = x
    for ch in normalize(text):
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            col = 0
            while col < 5:
                if bits[col] == "1":
                    start = col
                    while col < 5 and bits[col] == "1":
                        col += 1
                    x0 = cx + start * scale
                    x1 = cx + col * scale - 1
                    if bold:
                        x1 += 1  # thicken every stroke by one pixel
                    cv.rect(x0, y + row * scale,
                            x1, y + (row + 1) * scale - 1, color)
                else:
                    col += 1
        cx += 6 * scale
    return cx


def wrap(text, scale, width):
    """Wrap text to fit pixel width; returns a list of lines."""
    max_chars = max(1, width // (6 * scale))
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = (cur + " " + w) if cur else w
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                while len(w) > max_chars:  # one very long word: hard-split
                    lines.append(w[:max_chars])
                    w = w[max_chars:]
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_wrapped(cv, xy, text, scale, width, color=INK, leading=None,
                 max_lines=None, bold=False):
    """Draw wrapped text; with max_lines, truncate the tail with '...'."""
    x, y = xy
    lh = leading or int(7 * scale * 1.25)
    lines = wrap(text, scale, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        # Truncate at a word boundary where possible, then add "...".
        last = lines[-1]
        while len(last + "...") > width // (6 * scale) and " " in last:
            last = last.rsplit(" ", 1)[0]
        while len(last + "...") > width // (6 * scale) and last:
            last = last[:-1]
        lines[-1] = last + "..."
    for line in lines:
        draw_text(cv, x, y, line, scale, color, bold=bold)
        y += lh
    return y

# (number, title, summary, lon, lat)
STORIES = [
    (1, "Houthi missiles strike Riyadh's finance tower",
     "Missiles hit the financial district, damaging the Public Investment "
     "Fund tower and other buildings as attacks on the Saudi capital escalate.",
     46.7, 24.7),
    (2, "Cyclone Akvan makes landfall in Odisha",
     "Crosses the coast near Gopalpur at 70-80 kmph; over 300,000 evacuated, "
     "no major damage yet.",
     84.8, 19.1),
    (3, "Trump, Xi and Putin issue peace declaration",
     "First three-way meeting in Shenzhen ends with a four-point joint "
     "declaration.",
     114.06, 22.55),
    (4, "ICJ: Myanmar committed genocide",
     "World court finds Myanmar guilty over the Rohingya, a first against a "
     "state.",
     4.3, 52.07),
    (5, "Stocks slide as AI doubts grow",
     "Nikkei falls 4.8%, S&P 500 down a fifth straight day after "
     "Anthropic's debut.",
     -74.0, 40.7),
    (6, "COP31 draft drops fossil-fuel phase-out",
     "Negotiators strip any reference to ending fossil fuel use from the "
     "draft deal.",
     30.7, 36.9),
    (7, "Israeli troops cross Gaza's Yellow Line",
     "First incursion across the ceasefire boundary since the truce.",
     34.45, 31.5),
    (8, "Hormuz tanker attacks intensify",
     "Iran war enters its ninth month; a tanker catches fire after hitting "
     "a mine.",
     56.0, 27.0),
    (9, "Three Kyiv bridges hit in missile attack",
     "Major Russian strike hits Kyiv as Europe says it is ready for talks "
     "on ending the war.",
     30.5, 50.45),
    (10, "Kenya discharges its last Ebola patient",
     "Outbreak ends 37 days after the first case.",
     36.8, -1.3),
    (11, "US and Venezuela sign military deal",
     "Hegseth signs pact in Caracas: joint training, intelligence sharing, "
     "defence equipment.",
     -66.9, 10.5),
]

LEAD = STORIES[0]
REST = STORIES[1:]


def main():
    if len(sys.argv) > 1:
        out = sys.argv[1]
    else:
        out = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"),
                           "entry.png")
    cv = Canvas(W, H, PAPER)

    # ---- Masthead ----
    title = "THE WORLD"
    tw = text_width(title, 8)
    draw_text(cv, (W - tw) // 2, 14, title, 8, INK, bold=True)
    cv.hline(M, W - M, 92, INK, width=3)
    cv.hline(M, W - M, 98, INK, width=1)
    dateline = ("Friday, 20 November 2026  \u2022  11 stories  \u2022  "
                "5 continents")
    tw = text_width(dateline, 2)
    draw_text(cv, (W - tw) // 2, 106, dateline, 2, INK, bold=True)
    cv.hline(M, W - M, 134, INK, width=1)

    # ---- Lead story ----
    y = 144
    draw_text(cv, M, y, "LEAD  \u2022  RIYADH, SAUDI ARABIA", 2, RED,
              bold=True)
    y += 26
    y = draw_wrapped(cv, (M, y),
                     "Houthi missiles strike\nRiyadh's finance tower",
                     5, W - 2 * M, leading=44, bold=True)
    y += 6
    y = draw_wrapped(cv, (M, y),
                     "Missiles hit the financial district, damaging the "
                     "Public Investment Fund tower and other buildings as "
                     "Houthi attacks on the Saudi capital escalate.",
                     2, W - 2 * M, leading=25)
    y += 10
    cv.hline(M, W - M, y, RULE, width=1)
    y += 12

    # ---- Map panel: numbered dots on a graticule ----
    map_top = y
    map_h = 130  # shorter than the original's 150: the freed rows below
    # give the story grid room for three-line summaries.
    map_left, map_right = M, W - M
    cv.rect(map_left, map_top, map_right, map_top, INK)
    cv.rect(map_left, map_top + map_h, map_right, map_top + map_h, INK)
    cv.rect(map_left, map_top, map_left + 1, map_top + map_h, INK)
    cv.rect(map_right - 1, map_top, map_right, map_top + map_h, INK)
    draw_text(cv, map_left + 12, map_top + 8, "WHERE IT HAPPENED", 2, INK,
              bold=True)
    grid_top = map_top + 30
    grid_bot = map_top + map_h - 8
    for lon in range(-150, 181, 30):
        x = map_left + (lon + 180) / 360 * (map_right - map_left)
        cv.line(int(x), grid_top, int(x), grid_bot, GRIDLINE)
    for lat in (-60, -30, 0, 30, 60):
        yy = grid_top + (90 - lat) / 180 * (grid_bot - grid_top)
        cv.line(map_left, int(yy), map_right, int(yy), GRIDLINE)
    # Small manual offsets so near-identical locations stay readable.
    offsets = {1: (0, -13), 6: (16, -16), 7: (24, 14), 8: (0, 13),
               9: (-26, -20), 10: (-16, 10), 11: (0, 8)}
    for num, _t, _s, lon, lat in STORIES:
        dx, dy = offsets.get(num, (0, 0))
        x = map_left + (lon + 180) / 360 * (map_right - map_left) + dx
        yy = grid_top + (90 - lat) / 180 * (grid_bot - grid_top) + dy
        x, yy = int(x), int(yy)
        cv.circle(x, yy, 14, WHITE)  # white ring around the red dot
        cv.circle(x, yy, 12, RED)
        label = str(num)
        lw = text_width(label, 2)
        draw_text(cv, x - lw // 2, yy - 7, label, 2, WHITE, bold=True)
    y = map_top + map_h + 12
    cv.hline(M, W - M, y, RULE, width=1)
    y += 12

    # ---- Story grid: 2 columns x 5 rows ----
    # Rows stretch to the footer rule, so a two-line title still leaves
    # room for a three-line summary without crossing the separator.
    col_w = (W - 2 * M - 24) // 2
    row_h = (H - 44 - y) // 5
    for i, (num, title, summ, _lon, _lat) in enumerate(REST):
        col, row = i % 2, i // 2
        x0 = M + col * (col_w + 24)
        y0 = y + row * row_h
        draw_text(cv, x0, y0, "%d." % num, 3, RED, bold=True)
        num_w = text_width("%d." % num, 3)
        tx = x0 + num_w + 10
        text_w = col_w - (tx - x0)
        ty = draw_wrapped(cv, (tx, y0 + 2), title, 2,
                          text_w, leading=18, max_lines=2, bold=True)
        draw_wrapped(cv, (tx, ty + 2), summ, 2, text_w,
                     color=SUMMARY, leading=16, max_lines=3)
        if row < 4:
            cv.line(x0, y0 + row_h - 10, x0 + col_w, y0 + row_h - 10,
                    SEPLINE)

    # ---- Footer ----
    cv.hline(M, W - M, H - 44, INK, width=2)
    foot = ("Sources: OneTurn \u2022 The Hindu BusinessLine \u2022 Wikipedia "
            "\u2022 BBC \u2022 AppiSToS  \u2014  20 Nov 2026")
    draw_text(cv, M, H - 32, foot, 1, GREY, bold=True)

    outdir = os.path.dirname(os.path.abspath(out))
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    cv.save_png(out)
    print("wrote %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    main()
