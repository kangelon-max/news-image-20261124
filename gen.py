#!/usr/bin/env python3
"""gen.py — draws the news-image-20261124 poster, "THE WORLD IN ONE DAY".

Build-time generator (runs locally, where PIL lives): it renders the poster
at 2048x2048 and downscales to the 1024x1024 entry.png the competition gate
accepts (at most 1024x1024 px, at most 1 MiB). Fully deterministic: every
position, star and wave comes from fixed constants or a fixed-seed RNG, and
the PNG is saved with no time metadata. main.ts ships entry.png to /output.

Rank-1 defense revision: a far richer hero (detailed corvette with bridge,
mast, radar, funnel and portholes; layered explosion with flame tongues,
sparks and a drifting smoke column; four naval drones with spray wakes;
lighthouse and container port; moon glitter and fire reflections on the
water), more detailed motifs in every major panel, a wireframe-globe
masthead, and the complete markets ticker from the day's verified closes.
"""

import random

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants

S = 2048                      # render size; final image is S//2 = 1024
W = H = S
FINAL = 1024

PAPER = (245, 239, 226)
CARD = (252, 249, 241)
NAVY = (13, 27, 46)
NAVY2 = (21, 42, 68)
INK = (26, 26, 30)
RED = (192, 57, 43)
RED_L = (231, 96, 76)
GOLD = (201, 162, 39)
DARK = (8, 14, 24)
SHIP = (44, 62, 82)
SHIP2 = (56, 78, 100)
MOON = (240, 230, 190)
FIRE0 = (178, 44, 26)
FIRE1 = (232, 110, 40)
FIRE2 = (245, 180, 60)
FIRE3 = (252, 226, 160)
SMOKE = (120, 124, 130)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FONT_DIR + "DejaVuSerif-Bold.ttf"
SERIF = FONT_DIR + "DejaVuSerif.ttf"
SANS_B = FONT_DIR + "DejaVuSans-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, fnt):
    box = draw.textbbox((0, 0), s, font=fnt)
    return box[2] - box[0]


def fit_font(draw, s, path, start, max_w, min_size=18):
    """Largest font (<= start) whose rendered width fits max_w."""
    size = start
    while size > min_size:
        fnt = font(path, size)
        if text_w(draw, s, fnt) <= max_w:
            return fnt
        size -= 2
    return font(path, min_size)


def wrap(draw, s, fnt, max_w):
    """Greedy word wrap measured with textbbox."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def vgrad(draw, x0, y0, x1, y1, top, bot):
    """Vertical gradient fill, one line per step of 4 px."""
    steps = max(1, (y1 - y0) // 4)
    for i in range(steps + 1):
        t = i / steps
        col = tuple(round(top[c] + (bot[c] - top[c]) * t) for c in range(3))
        yy = y0 + (y1 - y0) * i // steps
        draw.rectangle([x0, yy, x1, min(y1, yy + 4)], fill=col)


# ------------------------------------------------------------------- canvas

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img, "RGBA")
rng = random.Random(20261124)  # fixed seed: the poster never changes

MX = 48                       # outer margin
RIGHT = W - MX

# --------------------------------------------------------------- masthead

vgrad(d, MX, 40, RIGHT, 272, NAVY2, NAVY)
d.rectangle([MX, 40, RIGHT, 272], outline=GOLD, width=4)
d.rectangle([MX + 12, 52, RIGHT - 12, 260], outline=GOLD + (150,), width=1)


def globe(cx, cy, r):
    """Wireframe globe emblem: rim, two meridians, two parallels."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=4)
    for mw in (r * 2 // 5, r * 4 // 5):
        d.ellipse([cx - mw // 2, cy - r, cx + mw // 2, cy + r], outline=GOLD + (200,), width=2)
    d.line([cx - r, cy, cx + r, cy], fill=GOLD + (200,), width=2)
    for dy in (-r // 2, r // 2):
        half = int((r * r - dy * dy) ** 0.5)
        d.line([cx - half, cy + dy, cx + half, cy + dy], fill=GOLD + (170,), width=2)
    d.line([cx, cy - r, cx, cy + r], fill=GOLD + (200,), width=2)


globe(MX + 104, 156, 50)
globe(RIGHT - 104, 156, 50)
title_f = fit_font(d, "THE WORLD IN ONE DAY", SERIF_B, 124, RIGHT - MX - 340)
tw = text_w(d, "THE WORLD IN ONE DAY", title_f)
d.text(((W - tw) / 2, 58), "THE WORLD IN ONE DAY", font=title_f, fill=PAPER)
date_f = font(SANS_B, 44)
d.text((MX + 190, 216), "TUESDAY · 24 NOVEMBER 2026", font=date_f, fill=GOLD)
tag_f = font(SERIF, 36)
tag_s = "One image, the whole planet"
gw = text_w(d, tag_s, tag_f)
d.text((RIGHT - 190 - gw, 220), tag_s, font=tag_f, fill=(214, 205, 180))

# ------------------------------------------------------------------- hero
# Night sea off Benghazi: drones skim the waves, a corvette burns at port.

HX0, HY0, HX1, HY1 = MX, 296, RIGHT, 956
SEA_Y = 648
vgrad(d, HX0, HY0, HX1, SEA_Y, (8, 18, 36), (22, 48, 76))
vgrad(d, HX0, SEA_Y, HX1, HY1, (26, 80, 118), (9, 32, 56))

# stars: many faint, a few bright with sparkle crosses
for _ in range(170):
    sx = rng.randint(HX0 + 14, HX1 - 14)
    sy = rng.randint(HY0 + 14, SEA_Y - 130)
    r = rng.choice([1, 2, 2, 3])
    a = rng.randint(60, 220)
    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255, a))
for _ in range(6):
    sx = rng.randint(HX0 + 90, HX1 - 90)
    sy = rng.randint(HY0 + 50, SEA_Y - 220)
    d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 255, 255, 235))
    d.line([sx - 13, sy, sx + 13, sy], fill=(255, 255, 255, 120), width=2)
    d.line([sx, sy - 13, sx, sy + 13], fill=(255, 255, 255, 120), width=2)

# drifting cloud bands (kept inside the hero panel)
for (cx0, cy0, cx1, cy1), col in [
        ((HX0 + 30, 330, 760, 376), (10, 16, 28, 74)),
        ((880, 314, 1780, 354), (10, 16, 28, 64)),
        ((1240, 462, HX1 - 30, 508), (10, 16, 28, 58)),
        ((180, 516, 1080, 546), (190, 200, 215, 15))]:
    d.ellipse([cx0, cy0, cx1, cy1], fill=col)

# moon and its glow, above the port
for gr, ga in [(124, 26), (94, 42)]:
    d.ellipse([452 - gr, 402 - gr, 452 + gr, 402 + gr], fill=(240, 230, 190, ga))
d.ellipse([452 - 58, 402 - 58, 452 + 58, 402 + 58], fill=MOON)
d.ellipse([432 - 12, 384 - 12, 432 + 12, 384 + 12], fill=(222, 210, 168))
d.ellipse([478 - 8, 424 - 8, 478 + 8, 424 + 8], fill=(222, 210, 168))
d.ellipse([458 - 6, 442 - 6, 458 + 6, 442 + 6], fill=(226, 215, 175))

# port silhouette, left: lighthouse, container stacks, two gantry cranes
d.polygon([(78, SEA_Y), (86, 486), (98, 486), (106, SEA_Y)], fill=DARK)      # lighthouse
d.rectangle([80, 470, 104, 488], fill=DARK)
d.ellipse([84, 452, 100, 468], fill=(255, 214, 120))
d.polygon([(100, 462), (528, 542), (506, 578)], fill=(255, 240, 190, 22))    # beam
for bx, bw, bh, tone in [(120, 118, 74, DARK), (244, 96, 52, (11, 22, 34)),
                         (346, 128, 92, DARK), (480, 84, 60, (12, 26, 38))]:
    d.rectangle([bx, SEA_Y - bh, bx + bw, SEA_Y], fill=tone)
    for gy in range(SEA_Y - bh + 12, SEA_Y - 8, 16):
        d.line([bx + 6, gy, bx + bw - 6, gy], fill=(30, 48, 66), width=2)
for cx in (176, 492):
    d.line([cx, SEA_Y - 214, cx, SEA_Y], fill=DARK, width=14)
    d.line([cx + 128, SEA_Y - 214, cx + 128, SEA_Y], fill=DARK, width=10)
    d.line([cx - 44, SEA_Y - 214, cx + 176, SEA_Y - 214], fill=DARK, width=12)
    d.line([cx, SEA_Y - 214, cx + 128, SEA_Y], fill=DARK, width=5)
    d.line([cx + 96, SEA_Y - 214, cx + 96, SEA_Y - 160], fill=DARK, width=6)
    d.rectangle([cx + 76, SEA_Y - 160, cx + 116, SEA_Y - 134], fill=DARK)
    d.rectangle([cx + 88, SEA_Y - 196, cx + 104, SEA_Y - 182], fill=DARK)

# distant headland on the horizon, right
d.polygon([(1470, SEA_Y), (1730, 620), (2000, 632), (2000, SEA_Y)], fill=(7, 12, 20))

# ------------------------------------------------------------- the corvette
# Bow to the left, stern burning to the right; waterline at SEA_Y.

HULL = [(872, SEA_Y), (972, SEA_Y - 54), (1702, SEA_Y - 54), (1796, SEA_Y)]
d.polygon(HULL, fill=SHIP)
d.line([972, SEA_Y - 54, 1702, SEA_Y - 54], fill=(168, 188, 208), width=5)    # sheer line
d.line([900, SEA_Y - 6, 1770, SEA_Y - 6], fill=(96, 40, 30), width=4)         # boot-top
for i, px in enumerate(range(1012, 1660, 46)):                                # portholes
    lit = (i % 4 == 1)
    d.ellipse([px, SEA_Y - 32, px + 11, SEA_Y - 21],
              fill=(255, 190, 90) if lit else (22, 34, 48))
d.rectangle([972, SEA_Y - 66, 1702, SEA_Y - 54], fill=SHIP2)                  # deck strip
for rx in range(992, 1690, 38):                                               # railing
    d.line([rx, SEA_Y - 78, rx, SEA_Y - 66], fill=(96, 116, 138), width=3)
d.line([972, SEA_Y - 78, 1702, SEA_Y - 78], fill=(96, 116, 138), width=3)

# fore gun turret with twin barrels
d.polygon([(1006, SEA_Y - 66), (1080, SEA_Y - 66), (1068, SEA_Y - 90),
           (1018, SEA_Y - 90)], fill=SHIP)
d.line([1026, SEA_Y - 84, 958, SEA_Y - 102], fill=SHIP, width=10)
d.line([1030, SEA_Y - 74, 970, SEA_Y - 90], fill=SHIP, width=8)

# bridge superstructure: two tiers, window rows, mast and radar
d.rectangle([1150, SEA_Y - 108, 1420, SEA_Y - 66], fill=SHIP)
d.rectangle([1196, SEA_Y - 150, 1372, SEA_Y - 108], fill=SHIP2)
d.line([1150, SEA_Y - 108, 1420, SEA_Y - 108], fill=(150, 170, 192), width=3)  # rim light
d.line([1196, SEA_Y - 150, 1372, SEA_Y - 150], fill=(150, 170, 192), width=3)
for i, wx in enumerate(range(1168, 1396, 36)):
    d.rectangle([wx, SEA_Y - 94, wx + 18, SEA_Y - 80],
                fill=(255, 190, 90) if i % 3 == 0 else (140, 175, 205))
for wx in range(1212, 1352, 28):
    d.rectangle([wx, SEA_Y - 138, wx + 16, SEA_Y - 122], fill=(170, 205, 235))
d.rectangle([1276, SEA_Y - 228, 1290, SEA_Y - 150], fill=SHIP)                # mast
d.line([1236, SEA_Y - 200, 1330, SEA_Y - 200], fill=SHIP, width=6)            # yardarm
d.rectangle([1240, SEA_Y - 244, 1326, SEA_Y - 230], fill=(72, 94, 116),
            outline=(128, 148, 168), width=2)                                 # radar bar
d.line([1283, SEA_Y - 244, 1283, SEA_Y - 262], fill=SHIP, width=4)
d.ellipse([1278, SEA_Y - 270, 1288, SEA_Y - 260], fill=RED_L)                 # masthead light

# funnel with cap and a faint smoke trail of its own
d.polygon([(1466, SEA_Y - 66), (1526, SEA_Y - 66), (1518, SEA_Y - 132),
           (1474, SEA_Y - 132)], fill=SHIP)
d.rectangle([1472, SEA_Y - 140, 1520, SEA_Y - 130], fill=(44, 60, 80))
for sx, sy, sr, sa in [(1560, SEA_Y - 168, 17, 60), (1612, SEA_Y - 188, 23, 44),
                       (1672, SEA_Y - 204, 29, 30)]:
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(150, 154, 160, sa))

# aft block, windows, and a missile launcher
d.rectangle([1560, SEA_Y - 100, 1668, SEA_Y - 66], fill=SHIP)
for wx in range(1576, 1640, 32):
    d.rectangle([wx, SEA_Y - 88, wx + 14, SEA_Y - 74], fill=(255, 190, 90))
d.rectangle([1532, SEA_Y - 92, 1558, SEA_Y - 66], fill=SHIP2)
d.line([1540, SEA_Y - 88, 1518, SEA_Y - 106], fill=SHIP2, width=7)
d.line([1552, SEA_Y - 88, 1532, SEA_Y - 108], fill=SHIP2, width=7)

# hull reflection on the water
d.polygon([(900, SEA_Y + 4), (980, SEA_Y + 44), (1690, SEA_Y + 44),
           (1770, SEA_Y + 4)], fill=(6, 10, 18, 90))

# ------------------------------------------------- explosion at the stern
EX, EY = 1706, SEA_Y - 36
d.ellipse([EX - 215, EY - 135, EX + 215, EY + 135], fill=(255, 120, 40, 46))  # glow
for (rx, ry), col in [((150, 96), FIRE0), ((118, 76), FIRE1), ((84, 52), FIRE2),
                      ((50, 31), FIRE3), ((25, 17), (255, 246, 214))]:
    d.ellipse([EX - rx, EY - ry, EX + rx, EY + ry], fill=col)
for fx, fw, fh, col in [(-118, 30, 96, FIRE1), (-76, 36, 138, FIRE2),
                        (-30, 40, 168, FIRE3), (22, 36, 142, FIRE2),
                        (70, 32, 112, FIRE1), (112, 24, 80, FIRE0),
                        (-4, 26, 118, FIRE2), (48, 22, 88, FIRE3)]:
    d.polygon([(EX + fx, EY - 24), (EX + fx + fw, EY - 24),
               (EX + fx + fw // 2, EY - 24 - fh)], fill=col)
for _ in range(46):                                                           # sparks
    ang = rng.uniform(-2.6, -0.4)
    dist = rng.randint(60, 200)
    sx = int(EX + dist * 0.9 * (1 if rng.random() > 0.3 else -0.4))
    sy = int(EY - abs(dist * 0.62 * rng.uniform(0.4, 1.0)))
    r = rng.choice([2, 3, 3, 4])
    d.ellipse([sx - r, sy - r, sx + r, sy + r],
              fill=rng.choice([FIRE2, FIRE3, (255, 200, 110)]))
# smoke plume hugging the blast, drifting up and to the left
for sx, sy, sr, sa in [(1706, SEA_Y - 152, 34, 120), (1666, SEA_Y - 196, 44, 100),
                       (1616, SEA_Y - 232, 54, 82), (1558, SEA_Y - 260, 64, 64)]:
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(92, 96, 103, sa))
d.ellipse([1730 - 28, SEA_Y - 70 - 28, 1730 + 28, SEA_Y - 70 + 28],
          fill=(56, 58, 64, 150))

# firelight shimmering on the sea under the blast
for _ in range(30):
    fx = rng.randint(1560, 1870)
    fy = rng.randint(SEA_Y + 10, SEA_Y + 128)
    fl = rng.randint(12, 34)
    fa = max(36, 130 - (fy - SEA_Y))
    d.line([fx, fy, fx, fy + fl], fill=(255, 150, 60, fa), width=5)
# moon glitter path
for _ in range(20):
    gx = rng.randint(392, 512)
    gy = rng.randint(SEA_Y + 10, SEA_Y + 112)
    gl = rng.randint(14, 40)
    d.line([gx, gy, gx + gl, gy], fill=(230, 225, 190, 88), width=4)

# ------------------------------------------- four naval drones closing in
# They skim the waterline itself, spray fanning behind each hull.
for dx, dy, sc in [(238, 600, 1.45), (460, 624, 1.8), (700, 604, 1.2), (824, 632, 1.05)]:
    ln = int(128 * sc)
    body = (126, 146, 164)
    d.polygon([(dx, dy), (dx + ln, dy + int(9 * sc)), (dx + ln - int(24 * sc), dy + int(21 * sc)),
               (dx + int(16 * sc), dy + int(19 * sc))], fill=body)
    d.polygon([(dx + int(10 * sc), dy), (dx + int(36 * sc), dy - int(17 * sc)),
               (dx + int(56 * sc), dy)], fill=body)                            # fin
    d.polygon([(dx + int(52 * sc), dy + int(14 * sc)), (dx + int(84 * sc), dy + int(24 * sc)),
               (dx + int(58 * sc), dy + int(22 * sc))], fill=(100, 120, 138))  # wing
    d.ellipse([dx + ln - int(34 * sc), dy + int(3 * sc), dx + ln - int(18 * sc),
               dy + int(15 * sc)], fill=(255, 190, 90))                       # sensor eye
    d.ellipse([dx + int(30 * sc), dy - int(19 * sc), dx + int(36 * sc),
               dy - int(13 * sc)], fill=RED_L)                                # signal light
    for k in range(4):                                                        # spray fan
        wy = dy + int(22 * sc) + k * 7
        d.line([dx - int((26 + k * 30) * sc), wy, dx - int(4 * sc), wy - 4],
               fill=(220, 236, 244, 175 - k * 24), width=5)
    for k in range(3):                                                        # foam at its own waterline
        fy = dy + int(27 * sc) + k * 9
        d.line([dx - int(120 * sc) + k * 24, fy, dx - int(36 * sc) + k * 18, fy],
               fill=(214, 230, 240, 120), width=5)

# bow foam where the hull meets the water
for k in range(5):
    d.line([876 + k * 20, SEA_Y + 8 + k * 5, 940 + k * 24, SEA_Y + 8 + k * 5],
           fill=(215, 232, 242, 120), width=5)

# wave strokes across the sea
for _ in range(58):
    wx = rng.randint(HX0 + 20, HX1 - 190)
    wy = rng.randint(SEA_Y + 26, HY1 - 200)
    wl = rng.randint(60, 170)
    col = (150, 190, 220, 90) if rng.random() > 0.4 else (96, 146, 184, 70)
    d.line([wx, wy, wx + wl, wy], fill=col, width=4)

# hero headline strip
d.rectangle([HX0, 756, HX1, HY1], fill=(9, 18, 33, 224))
d.rectangle([HX0, 756, HX1, 759], fill=GOLD)
d.rectangle([HX0 + 36, 784, HX0 + 52, 800], fill=RED)
kick_f = font(SANS_B, 36)
d.text((HX0 + 68, 776), "TOP STORY · BENGHAZI, LIBYA", font=kick_f, fill=RED_L)
hero_f = fit_font(d, "UKRAINE SINKS RUSSIAN CORVETTE", SERIF_B, 80, HX1 - HX0 - 72)
d.text((HX0 + 36, 810), "UKRAINE SINKS RUSSIAN CORVETTE", font=hero_f, fill=PAPER)
sub_f = font(SANS, 37)
d.text((HX0 + 36, 884),
       "Seven naval drones strike the warship Merkury in port — the UN seeks a probe",
       font=sub_f, fill=(226, 220, 202))
sub2_f = font(SANS, 30)
d.text((HX0 + 36, 922),
       "President Zelensky confirms the strike · Tripoli demands explanations from Kyiv",
       font=sub2_f, fill=GOLD)


# ------------------------------------------------------------ major panels

def motif_tanker(x, y):
    """Tanker in a mined strait: headlands, dashed route, spiked mines."""
    d.polygon([(x + 218, y - 6), (x + 306, y - 6), (x + 306, y + 34),
               (x + 252, y + 30)], fill=NAVY2)                                # headland
    d.polygon([(x + 236, y + 104), (x + 306, y + 104), (x + 306, y + 66),
               (x + 262, y + 70)], fill=NAVY2)
    for gx in range(x + 6, x + 210, 26):                                      # dashed route
        d.line([gx, y + 88, gx + 13, y + 88], fill=GOLD, width=4)
    d.polygon([(x, y + 62), (x + 18, y + 44), (x + 196, y + 44), (x + 214, y + 62)],
              fill=NAVY)                                                      # hull
    d.line([x + 4, y + 50, x + 200, y + 50], fill=(96, 116, 138), width=3)
    for tx in (x + 34, x + 82, x + 130):                                      # cargo tanks
        d.rectangle([tx, y + 26, tx + 38, y + 44], fill=NAVY2)
        d.ellipse([tx, y + 19, tx + 38, y + 33], fill=NAVY2)
    d.rectangle([x + 168, y + 10, x + 194, y + 44], fill=NAVY)                # bridge castle
    for wx in range(x + 173, x + 190, 8):
        d.rectangle([wx, y + 17, wx + 4, y + 23], fill=(255, 190, 90))
    d.rectangle([x + 176, y - 2, x + 186, y + 10], fill=NAVY)                 # funnel
    d.rectangle([x + 176, y - 2, x + 186, y + 3], fill=RED)
    d.line([x + 20, y + 44, x + 20, y + 14], fill=NAVY, width=4)              # mast
    for mx, my in [(x + 248, y + 52), (x + 282, y + 26), (x + 292, y + 82)]:  # mines
        d.ellipse([mx - 11, my - 11, mx + 11, my + 11], outline=RED, width=5)
        for ddx, ddy in [(0, -18), (0, 18), (-18, 0), (18, 0),
                         (-13, -13), (13, -13), (-13, 13), (13, 13)]:
            d.line([mx, my, mx + ddx, my + ddy], fill=RED, width=4)


def motif_chart(x, y):
    """Rising market chart: grid, filled area, data points, arrow head."""
    for gy in range(y + 8, y + 92, 21):
        d.line([x, gy, x + 272, gy], fill=NAVY2 + (70,), width=2)
    d.line([x, y + 96, x + 272, y + 96], fill=NAVY2, width=3)
    d.line([x, y + 2, x, y + 96], fill=NAVY2, width=3)
    pts = [(x + 4, y + 78), (x + 62, y + 62), (x + 118, y + 68),
           (x + 178, y + 36), (x + 246, y + 10)]
    d.polygon(pts + [(x + 246, y + 96), (x + 4, y + 96)], fill=GOLD + (52,))
    d.line(pts, fill=(160, 125, 25), width=13, joint="curve")
    d.line(pts, fill=GOLD, width=7, joint="curve")
    for px, py in pts[:-1]:
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=NAVY)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=PAPER)
    d.polygon([(x + 246, y + 10), (x + 216, y + 12), (x + 240, y + 36)], fill=GOLD)
    d.text((x + 8, y - 4), "+31%", font=font(SANS_B, 34), fill=NAVY)


def motif_skyline(x, y):
    """City skyline: varied towers, lit windows, minaret, strike smoke."""
    base = y + 96
    for bx, bw, bh in [(0, 42, 54), (48, 32, 38), (86, 50, 66), (142, 34, 46),
                       (182, 44, 58), (232, 38, 42)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=NAVY)
        for wy in range(base - bh + 8, base - 10, 13):
            for wx in range(x + bx + 6, x + bx + bw - 8, 12):
                if (wx + wy) % 3 != 0:
                    d.rectangle([wx, wy, wx + 6, wy + 7], fill=GOLD)
    d.rectangle([x + 282, base - 84, x + 290, base], fill=NAVY)               # minaret
    d.ellipse([x + 276, base - 96, x + 296, base - 82], fill=NAVY)
    d.rectangle([x + 274, base - 74, x + 298, base - 68], fill=NAVY)
    for sx, sy, sr in [(x + 104, base - 84, 13), (x + 122, base - 94, 17),
                       (x + 146, base - 100, 21)]:                            # smoke
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SMOKE + (120,))
    d.line([x, base, x + 300, base], fill=NAVY, width=4)


def motif_building(x, y):
    """Apartment block: window grid, blast hole with glow, debris."""
    d.rectangle([x + 158, y + 6, x + 268, y + 100], fill=NAVY2)               # rear block
    for r in range(4):
        for c in range(3):
            d.rectangle([x + 172 + c * 30, y + 16 + r * 22, x + 186 + c * 30,
                         y + 28 + r * 22], fill=(52, 76, 102))
    d.rectangle([x, y - 14, x + 148, y + 100], fill=NAVY)                     # main block
    for r in range(5):
        for c in range(4):
            lit = (r * 4 + c) % 3 != 0
            d.rectangle([x + 13 + c * 34, y - 4 + r * 22, x + 29 + c * 34,
                         y + 9 + r * 22], fill=GOLD if lit else NAVY2)
    hole = [(x + 96, y + 8), (x + 122, y + 30), (x + 108, y + 44),
            (x + 128, y + 68), (x + 100, y + 62), (x + 90, y + 34)]
    d.polygon(hole, fill=FIRE1)                                               # blast hole
    d.polygon([(x + 102, y + 26), (x + 116, y + 40), (x + 106, y + 54),
               (x + 100, y + 38)], fill=FIRE2)
    d.line([x + 96, y + 8, x + 78, y - 10], fill=NAVY, width=4)               # cracks
    d.line([x + 108, y + 44, x + 88, y + 58], fill=NAVY, width=3)
    for dx, dw in [(x + 8, 26), (x + 44, 18), (x + 118, 30)]:                 # debris
        d.polygon([(dx, y + 100), (dx + dw, y + 100), (dx + dw // 2, y + 88)], fill=NAVY)
    d.line([x - 4, y + 100, x + 280, y + 100], fill=NAVY, width=4)


def panel(x0, y0, x1, y1, kicker, headline, body, motif):
    d.rectangle([x0, y0, x1, y1], fill=CARD)
    d.rectangle([x0, y0, x1, y1], outline=NAVY, width=4)
    d.rectangle([x0, y0, x1, y0 + 10], fill=RED)
    motif(x1 - 336, y0 + 34)
    d.rectangle([x0 + 30, y0 + 34, x0 + 46, y0 + 50], fill=RED)
    d.text((x0 + 58, y0 + 26), kicker, font=font(SANS_B, 35), fill=RED)
    head_f = fit_font(d, headline, SERIF_B, 54, x1 - x0 - 396)
    d.text((x0 + 30, y0 + 74), headline, font=head_f, fill=NAVY)
    d.line([x0 + 30, y0 + 142, x1 - 30, y0 + 142], fill=GOLD, width=2)
    body_f = font(SANS, 41)
    ly = y0 + 158
    for line in wrap(d, body, body_f, x1 - x0 - 60):
        d.text((x0 + 30, ly), line, font=body_f, fill=INK)
        ly += 52


PW = (RIGHT - MX - 24) // 2          # panel width; two per row
R1Y, R2Y, PH = 980, 1330, 326
panel(MX, R1Y, MX + PW, R1Y + PH, "STRAIT OF HORMUZ", "ON A KNIFE-EDGE",
      "Iran says three tankers hit mines and refuses talks until Washington "
      "meets its seven conditions.", motif_tanker)
panel(MX + PW + 24, R1Y, RIGHT, R1Y + PH, "MARKETS", "THE HUANG EFFECT",
      "Nvidia's board reinstates founder Jensen Huang as CEO. Shares +31% in "
      "a day; S&P +4.73%, Nasdaq +6.51%.", motif_chart)
panel(MX, R2Y, MX + PW, R2Y + PH, "GAZA", "STRIKES KILL HAMAS CHIEF",
      "Israeli strikes kill internal-security chief Naeem Abu Nahel and six "
      "others, incl. two police officers and an UNRWA worker.", motif_skyline)
panel(MX + PW + 24, R2Y, RIGHT, R2Y + PH, "ZAPORIZHZHIA", "APARTMENT BLOCK HIT",
      "A Russian strike on homes kills 2 and wounds 40 — four of them "
      "children — in an overnight attack.", motif_building)

# ------------------------------------------------------------------ briefs

BY = 1680
d.rectangle([MX + 6, BY + 8, MX + 22, BY + 24], fill=RED)
d.text((MX + 34, BY), "AROUND THE WORLD IN BRIEF", font=font(SANS_B, 36), fill=RED)
sign_f = font(SERIF, 36)
sign_s = "57 stories · 854 headlines · one image"
sw = text_w(d, sign_s, sign_f)
d.text((RIGHT - 6 - sw, BY), sign_s, font=sign_f, fill=INK)
d.line([MX, BY + 52, RIGHT, BY + 52], fill=NAVY, width=3)
d.line([MX, BY + 52, MX + 320, BY + 52], fill=GOLD, width=3)

BRIEFS = [
    ("INDONESIA", "Banten factory fire kills 26; dozens still missing"),
    ("NEPAL", "5.6 quake strikes Koshi province, near China border"),
    ("SPACE", "Zeeshan Ali, first foreigner on Tiangong — Shenzhou-24"),
    ("THE HAGUE", "14 nations back ICJ Rohingya genocide ruling; 6,500 return"),
    ("DR CONGO", "Ituri fighting traps Ebola teams at a hospital"),
    ("COLOMBIA", "Car bomb wrecks Villavicencio governor's office"),
    ("AI", "Guterres seeks a global AI-risk framework in a year"),
    ("POLAND", "Russian drone enters airspace; NATO responds"),
]
COLX = [MX + 6, 1036]
COLW = 950


def brief_size(lead, rest, start=32, min_size=23):
    """Largest size at which bold lead + regular rest fit the column."""
    size = start
    while size > min_size:
        lf, rf = font(SANS_B, size), font(SANS, size)
        if text_w(d, lead, lf) + text_w(d, rest, rf) <= COLW - 24:
            return size
        size -= 1
    return min_size


for i, (lead, txt) in enumerate(BRIEFS):
    cx = COLX[i % 2]
    cy = BY + 76 + (i // 2) * 50
    rest = " — " + txt
    size = brief_size(lead, rest)
    lf, rf = font(SANS_B, size), font(SANS, size)
    ty = cy + (38 - size) // 2
    d.rectangle([cx, cy + 13, cx + 12, cy + 25], fill=GOLD)
    d.text((cx + 24, ty), lead, font=lf, fill=NAVY)
    d.text((cx + 24 + text_w(d, lead, lf), ty), rest, font=rf, fill=INK)

# ------------------------------------------------------------------ ticker

TY = 1952
d.rectangle([MX, TY, RIGHT, 2008], fill=NAVY)
d.rectangle([MX, TY, RIGHT, TY + 4], fill=GOLD)
tick = ("S&P 500 7,237 ▲4.73% · NASDAQ 24,090 ▲6.51% · NIKKEI 58,645 ▲3.91% · "
        "FTSE 100 10,481 ▲1.30% · BRENT $86.7 · GOLD $3,620 · EUR/USD 1.09")
tick_f = fit_font(d, tick, SANS_B, 34, RIGHT - MX - 48, min_size=18)
tw2 = text_w(d, tick, tick_f)
d.text(((W - tw2) / 2, TY + 15), tick, font=tick_f, fill=GOLD)

# -------------------------------------------------------------------- save

final = img.resize((FINAL, FINAL), Image.LANCZOS)
final.save("entry.png", optimize=True)
print("wrote entry.png", final.size)
