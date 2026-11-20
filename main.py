#!/usr/bin/env python3
"""make.fun bounty entry — "Sum up 20 November's world news in one image".

Renders a newspaper front page (11 verified stories from the 20 Nov 2026
brief) to /output/entry.png (or a local path given as argv[1]).
Pure Pillow, no network, no fonts bundled — uses system DejaVu/Liberation.
Deterministic: two runs write identical bytes.

Canvas is exactly 1024x1024 and the PNG stays under 1 MiB, per the
competition's requirements (image at most 1 MiB and 1024 by 1024 pixels).
Prepared for Irpan, 20 Nov 2026. Not submitted anywhere by this script.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 32  # margin
PAPER = (251, 247, 238)
INK = (18, 18, 18)
RED = (178, 34, 34)
GREY = (110, 110, 105)
RULE = (60, 60, 60)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Wrap text to fit pixel width; returns list of lines."""
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, fnt, width, fill=INK, leading=None,
                 max_lines=None):
    """Draw wrapped text; when max_lines is set, truncate with an ellipsis."""
    x, y = xy
    lh = leading or int(fnt.size * 1.25)
    lines = wrap(draw, text, fnt, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " …", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + " …"
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
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
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    f_mast = font(SERIF_B, 62)
    title = "THE WORLD"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 14), title, font=f_mast, fill=INK)
    d.line([(M, 92), (W - M, 92)], fill=INK, width=3)
    d.line([(M, 98), (W - M, 98)], fill=INK, width=1)
    f_date = font(SANS_B, 19)
    dateline = "Friday, 20 November 2026  \u2022  11 stories  \u2022  5 continents"
    tw = d.textlength(dateline, font=f_date)
    d.text(((W - tw) / 2, 106), dateline, font=f_date, fill=INK)
    d.line([(M, 134), (W - M, 134)], fill=INK, width=1)

    # ---- Lead story ----
    y = 144
    f_kicker = font(SANS_B, 16)
    d.text((M, y), "LEAD  \u2022  RIYADH, SAUDI ARABIA", font=f_kicker, fill=RED)
    y += 26
    f_head = font(SERIF_B, 36)
    y = draw_wrapped(d, (M, y),
                     "Houthi missiles strike\nRiyadh's finance tower",
                     f_head, W - 2 * M, leading=44)
    y += 6
    f_deck = font(SERIF, 19)
    y = draw_wrapped(d, (M, y),
                     "Missiles hit the financial district, damaging the "
                     "Public Investment Fund tower and other buildings as "
                     "Houthi attacks on the Saudi capital escalate.",
                     f_deck, W - 2 * M, leading=25)
    y += 10
    d.line([(M, y), (W - M, y)], fill=RULE, width=1)
    y += 12

    # ---- Map panel: numbered dots on a graticule ----
    map_top = y
    map_h = 150
    map_left, map_right = M, W - M
    d.rectangle([map_left, map_top, map_right, map_top + map_h],
                outline=INK, width=2)
    f_map_t = font(SANS_B, 15)
    d.text((map_left + 12, map_top + 8), "WHERE IT HAPPENED",
           font=f_map_t, fill=INK)
    grid_top = map_top + 30
    grid_bot = map_top + map_h - 8
    for lon in range(-150, 181, 30):
        x = map_left + (lon + 180) / 360 * (map_right - map_left)
        d.line([(x, grid_top), (x, grid_bot)], fill=(200, 196, 186), width=1)
    for lat in (-60, -30, 0, 30, 60):
        yy = grid_top + (90 - lat) / 180 * (grid_bot - grid_top)
        d.line([(map_left, yy), (map_right, yy)], fill=(200, 196, 186), width=1)
    f_dot = font(SANS_B, 17)
    # Small manual offsets so near-identical locations stay readable.
    offsets = {1: (0, -13), 6: (20, -16), 7: (24, 14), 8: (0, 13),
               9: (-26, -20), 10: (-16, 10), 11: (0, 8)}
    for num, _t, _s, lon, lat in STORIES:
        dx, dy = offsets.get(num, (0, 0))
        x = map_left + (lon + 180) / 360 * (map_right - map_left) + dx
        yy = grid_top + (90 - lat) / 180 * (grid_bot - grid_top) + dy
        r = 12
        d.ellipse([x - r, yy - r, x + r, yy + r], fill=RED, outline="white",
                  width=2)
        label = str(num)
        lw = d.textlength(label, font=f_dot)
        d.text((x - lw / 2, yy - 10), label, font=f_dot, fill="white")
    y = map_top + map_h + 12
    d.line([(M, y), (W - M, y)], fill=RULE, width=1)
    y += 12

    # ---- Story grid: 2 columns x 5 rows ----
    col_w = (W - 2 * M - 24) // 2
    row_h = 88
    f_num = font(SERIF_B, 26)
    f_t = font(SERIF_B, 19)
    f_s = font(SERIF, 15)
    for i, (num, title, summ, _lon, _lat) in enumerate(REST):
        col, row = i % 2, i // 2
        x0 = M + col * (col_w + 24)
        y0 = y + row * row_h
        d.text((x0, y0), f"{num}.", font=f_num, fill=RED)
        num_w = d.textlength(f"{num}.", font=f_num)
        tx = x0 + num_w + 10
        ty = draw_wrapped(d, (tx, y0 + 2), title, f_t, col_w - (tx - x0),
                          leading=23, max_lines=2)
        draw_wrapped(d, (tx, ty + 2), summ, f_s, col_w - (tx - x0),
                     fill=(40, 40, 40), leading=19, max_lines=2)
        if row < 4:
            d.line([(x0, y0 + row_h - 10), (x0 + col_w, y0 + row_h - 10)],
                   fill=(190, 186, 176), width=1)
    y = y + 5 * row_h - 6

    # ---- Footer ----
    d.line([(M, H - 44), (W - M, H - 44)], fill=INK, width=2)
    f_f = font(SANS, 13)
    foot = ("Sources: OneTurn \u2022 The Hindu BusinessLine \u2022 Wikipedia "
            "\u2022 BBC \u2022 AppiSToS  \u2014  20 Nov 2026")
    d.text((M, H - 32), foot, font=f_f, fill=GREY)

    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    img.save(out)
    print(f"wrote {out} ({W}x{H})")


if __name__ == "__main__":
    main()
