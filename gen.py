#!/usr/bin/env python3
"""gen.py — draws the news-image-20261124 poster, "THE WORLD IN ONE DAY".

Build-time generator (runs locally, where PIL lives): it renders the poster
at 2048x2048 and downscales to the 1024x1024 entry.png the competition gate
accepts (at most 1024x1024 px, at most 1 MiB). Fully deterministic: every
position, star and wave comes from fixed constants or a fixed-seed RNG, and
the PNG is saved with no time metadata. main.ts ships entry.png to /output.

Final-round hero redraw: the round-3 "more detail" pass hurt — its big
concentric explosion read as a rising sun and the ship and drones were
too small to read at thumbnail size. This version simplifies hard: one
large corvette filling most of the panel, a fireball bursting out of the
ship's own hull with a glowing breach at the waterline, and four big
drones with bright wakes converging on it; moon and port kept small and
quiet. Major panels keep their detailed motifs, the wireframe-globe
masthead, and the complete markets ticker from the day's verified closes.

Round-4 strengthening (on top of the redraw, same composition): hull
plating lines and a whip antenna, radar dome and funnel light on the
ship; a dock crane at the port; a tighter bright core for the blast
with embers rising above the flames; brighter spray fans, bow waves and
waterline shadows on the drones; a layered horizon band of wave strokes
and a thin horizon glow; wavelets under the tanker motif; the hero
sub-line fitted to its width instead of a fixed size.
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
SHIP = (74, 98, 122)
SHIP2 = (96, 124, 148)
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
# Night sea off Benghazi: a corvette burns at port, drones closing in.
# Final-round redraw: the round-3 "more detail" pass hurt — its big
# concentric explosion read as a rising sun and the ship and drones were
# too small to read at thumbnail size. This version simplifies hard: one
# large warship, a fireball bursting out of its own hull, big drones with
# bright wakes converging on it; moon and port kept small and quiet.

HX0, HY0, HX1, HY1 = MX, 296, RIGHT, 956
SEA_Y = 600
vgrad(d, HX0, HY0, HX1, SEA_Y, (8, 18, 36), (22, 48, 76))
vgrad(d, HX0, SEA_Y, HX1, 756, (26, 80, 118), (9, 32, 56))
d.line([HX0, SEA_Y, HX1, SEA_Y], fill=(140, 180, 215, 70), width=3)         # horizon glow

# stars: many faint, a few bright with sparkle crosses
for _ in range(140):
    sx = rng.randint(HX0 + 14, HX1 - 14)
    sy = rng.randint(HY0 + 14, SEA_Y - 140)
    r = rng.choice([1, 2, 2, 3])
    a = rng.randint(60, 220)
    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255, a))
for _ in range(6):
    sx = rng.randint(HX0 + 90, HX1 - 90)
    sy = rng.randint(HY0 + 50, SEA_Y - 230)
    d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 255, 255, 235))
    d.line([sx - 13, sy, sx + 13, sy], fill=(255, 255, 255, 120), width=2)
    d.line([sx, sy - 13, sx, sy + 13], fill=(255, 255, 255, 120), width=2)

# drifting cloud bands (kept inside the hero panel)
for (cx0, cy0, cx1, cy1), col in [
        ((HX0 + 30, 330, 700, 372), (10, 16, 28, 74)),
        ((900, 314, 1700, 352), (10, 16, 28, 64)),
        ((1300, 470, HX1 - 30, 506), (10, 16, 28, 58)),
        ((1400, 316, 1980, 340), (10, 16, 28, 40)),
        ((560, 330, 1080, 358), (190, 200, 215, 15))]:
    d.ellipse([cx0, cy0, cx1, cy1], fill=col)

# moon and its glow, upper left, clear of the ship and the blast
for gr, ga in [(118, 26), (88, 42)]:
    d.ellipse([330 - gr, 402 - gr, 330 + gr, 402 + gr], fill=(240, 230, 190, ga))
d.ellipse([330 - 54, 402 - 54, 330 + 54, 402 + 54], fill=MOON)
d.ellipse([312 - 11, 386 - 11, 312 + 11, 386 + 11], fill=(222, 210, 168))
d.ellipse([354 - 7, 420 - 7, 354 + 7, 420 + 7], fill=(222, 210, 168))

# port silhouette, left and low: lighthouse and two container stacks only,
# so nothing competes with the ship
d.polygon([(78, SEA_Y), (86, 486), (98, 486), (106, SEA_Y)], fill=DARK)      # lighthouse
d.rectangle([80, 470, 104, 488], fill=DARK)
d.ellipse([84, 452, 100, 468], fill=(255, 214, 120))
d.polygon([(100, 462), (420, 540), (400, 574)], fill=(255, 240, 190, 22))    # beam
for bx, bw, bh, tone in [(120, 118, 74, DARK), (244, 96, 52, (11, 22, 34)),
                         (346, 128, 92, DARK)]:
    d.rectangle([bx, SEA_Y - bh, bx + bw, SEA_Y], fill=tone)
    for gy in range(SEA_Y - bh + 12, SEA_Y - 8, 16):
        d.line([bx + 6, gy, bx + bw - 6, gy], fill=(30, 48, 66), width=2)

# dock crane, just left of the bow: legs, top beam, jib and hook line
d.line([492, SEA_Y, 496, SEA_Y - 96], fill=DARK, width=6)
d.line([544, SEA_Y, 540, SEA_Y - 96], fill=DARK, width=6)
d.line([488, SEA_Y - 96, 548, SEA_Y - 96], fill=DARK, width=6)
d.line([520, SEA_Y - 96, 600, SEA_Y - 150], fill=DARK, width=5)
d.line([590, SEA_Y - 148, 590, SEA_Y - 118], fill=DARK, width=3)
d.rectangle([582, SEA_Y - 118, 598, SEA_Y - 106], fill=DARK)

# distant headland on the horizon, right, kept low and dark
d.polygon([(1830, SEA_Y), (1930, 580), (2000, 586), (2000, SEA_Y)], fill=(7, 12, 20))

# ------------------------------------------------------------- the corvette
# Bow to the left, stern burning to the right; waterline at SEA_Y.
# The ship is drawn BIG — it fills most of the panel — so at thumbnail
# size it still reads as a warship, not a dark bar.

HULL = [(560, SEA_Y), (700, SEA_Y - 104), (1860, SEA_Y - 104), (1920, SEA_Y)]
d.polygon(HULL, fill=SHIP)
d.line([700, SEA_Y - 104, 1860, SEA_Y - 104], fill=(168, 188, 208), width=5)  # sheer line
d.line([590, SEA_Y - 6, 1900, SEA_Y - 6], fill=(96, 40, 30), width=4)        # boot-top
d.line([720, SEA_Y - 72, 1840, SEA_Y - 72], fill=(96, 120, 144), width=2)   # hull plating
d.line([730, SEA_Y - 54, 1830, SEA_Y - 54], fill=(88, 112, 136), width=2)
for i, px in enumerate(range(760, 1830, 46)):                                 # portholes
    lit = (i % 4 == 1)
    d.ellipse([px, SEA_Y - 40, px + 11, SEA_Y - 29],
              fill=(255, 190, 90) if lit else (22, 34, 48))
d.rectangle([700, SEA_Y - 116, 1860, SEA_Y - 104], fill=SHIP2)                # deck strip
for rx in range(720, 1850, 38):                                               # railing
    d.line([rx, SEA_Y - 128, rx, SEA_Y - 116], fill=(96, 116, 138), width=3)
d.line([700, SEA_Y - 128, 1860, SEA_Y - 128], fill=(96, 116, 138), width=3)

# fore gun turret with twin barrels
d.polygon([(740, SEA_Y - 116), (820, SEA_Y - 116), (806, SEA_Y - 140),
           (754, SEA_Y - 140)], fill=SHIP)
d.line([766, SEA_Y - 134, 694, SEA_Y - 152], fill=SHIP, width=10)
d.line([770, SEA_Y - 124, 706, SEA_Y - 140], fill=SHIP, width=8)

# bridge superstructure: two tiers, window rows, mast and radar
d.rectangle([920, SEA_Y - 180, 1320, SEA_Y - 116], fill=SHIP)
d.rectangle([980, SEA_Y - 240, 1260, SEA_Y - 180], fill=SHIP2)
d.line([920, SEA_Y - 180, 1320, SEA_Y - 180], fill=(150, 170, 192), width=3)  # rim light
d.line([980, SEA_Y - 240, 1260, SEA_Y - 240], fill=(150, 170, 192), width=3)
for i, wx in enumerate(range(940, 1300, 36)):
    d.rectangle([wx, SEA_Y - 166, wx + 18, SEA_Y - 152],
                fill=(255, 190, 90) if i % 3 == 0 else (140, 175, 205))
for wx in range(996, 1240, 28):
    d.rectangle([wx, SEA_Y - 226, wx + 16, SEA_Y - 210], fill=(170, 205, 235))
d.rectangle([1114, SEA_Y - 282, 1132, SEA_Y - 240], fill=SHIP)                # mast
d.line([1072, SEA_Y - 264, 1174, SEA_Y - 264], fill=SHIP, width=6)            # yardarm
d.rectangle([1070, SEA_Y - 296, 1170, SEA_Y - 282], fill=SHIP2,
            outline=(150, 170, 192), width=2)                                 # radar bar
d.ellipse([1118, SEA_Y - 298, 1130, SEA_Y - 286], fill=RED_L)                 # masthead light
d.line([1000, SEA_Y - 240, 998, SEA_Y - 272], fill=SHIP2, width=3)            # whip antenna
d.ellipse([995, SEA_Y - 276, 1001, SEA_Y - 270], fill=RED_L)

# funnel with cap and a faint smoke trail of its own
d.polygon([(1400, SEA_Y - 104), (1460, SEA_Y - 104), (1452, SEA_Y - 188),
           (1408, SEA_Y - 188)], fill=SHIP)
d.rectangle([1406, SEA_Y - 196, 1454, SEA_Y - 186], fill=(60, 80, 104))
d.ellipse([1426, SEA_Y - 202, 1434, SEA_Y - 194], fill=RED_L)                 # funnel light

# aft block, windows, and a missile launcher
d.rectangle([1560, SEA_Y - 172, 1700, SEA_Y - 104], fill=SHIP)
for wx in range(1576, 1640, 32):
    d.rectangle([wx, SEA_Y - 152, wx + 14, SEA_Y - 136], fill=(255, 190, 90))
d.rectangle([1520, SEA_Y - 130, 1550, SEA_Y - 104], fill=SHIP2)
d.line([1530, SEA_Y - 126, 1508, SEA_Y - 144], fill=SHIP2, width=7)
d.line([1542, SEA_Y - 126, 1522, SEA_Y - 148], fill=SHIP2, width=7)
d.ellipse([1617, SEA_Y - 199, 1643, SEA_Y - 173], fill=SHIP2,
          outline=(150, 170, 192), width=2)                                   # radar dome

# hull reflection on the water
d.polygon([(590, SEA_Y + 4), (700, SEA_Y + 44), (1800, SEA_Y + 44),
           (1900, SEA_Y + 4)], fill=(6, 10, 18, 90))

# ------------------------------------------------- explosion at the stern
# The blast bursts OUT of the ship's own hull — a jagged cluster of flame
# tongues rising from the aft deck, a small bright core at its base, a
# jagged breach glowing at the waterline, and a smoke column leaning up
# and away. No large round fireball, no symmetric rings: a blast is
# ragged, never a sun. Every flame starts at the ship.
EX, EY = 1700, SEA_Y - 60
# low, wide glow hugging the deck — the only halo, and it stays flat
d.ellipse([EX - 190, EY - 50, EX + 210, EY + 70], fill=(255, 120, 40, 38))
# jagged breach in the hull side, glowing where the drone struck
d.polygon([(1600, SEA_Y), (1620, SEA_Y - 60), (1660, SEA_Y - 40),
           (1700, SEA_Y - 70), (1740, SEA_Y - 40), (1730, SEA_Y)], fill=(10, 8, 8))
d.polygon([(1640, SEA_Y), (1660, SEA_Y - 45), (1690, SEA_Y - 30),
           (1710, SEA_Y - 55), (1720, SEA_Y)], fill=FIRE1)
# flame tongues in three rows: dark red behind, orange mid, bright front.
# Uneven heights and widths give a jagged silhouette, never a circle.
for fx, fw, fh, col in [(-160, 60, 110, FIRE0), (-90, 66, 140, FIRE0),
                        (-10, 60, 120, FIRE0), (70, 56, 150, FIRE0),
                        (140, 50, 100, FIRE0)]:
    d.polygon([(EX + fx, EY + 5), (EX + fx + fw, EY + 5),
               (EX + fx + fw // 2, EY + 5 - fh)], fill=col)
for fx, fw, fh, col in [(-190, 44, 170, FIRE1), (-130, 48, 210, FIRE2),
                        (-60, 50, 180, FIRE1), (10, 46, 220, FIRE2),
                        (80, 44, 170, FIRE1), (130, 40, 130, FIRE2)]:
    d.polygon([(EX + fx, EY + 5), (EX + fx + fw, EY + 5),
               (EX + fx + fw // 2, EY + 5 - fh)], fill=col)
for fx, fw, fh, col in [(-150, 30, 150, FIRE3), (-80, 34, 190, FIRE3),
                        (-10, 32, 170, FIRE2), (50, 30, 200, FIRE3),
                        (110, 26, 140, FIRE3)]:
    d.polygon([(EX + fx, EY + 5), (EX + fx + fw, EY + 5),
               (EX + fx + fw // 2, EY + 5 - fh)], fill=col)
# small bright heart at the base, where the fire is hottest — kept tight
# so it reads as the core of the blast, not a pale shape on the deck
d.ellipse([EX - 52, EY - 8, EX + 52, EY + 34], fill=FIRE3)
d.ellipse([EX - 30, EY - 12, EX + 30, EY + 18], fill=(255, 246, 214))
for _ in range(46):                                                           # sparks
    ang = rng.uniform(-2.6, -0.4)
    dist = rng.randint(60, 200)
    sx = int(EX + dist * 0.9 * (1 if rng.random() > 0.3 else -0.4))
    sy = int(EY - abs(dist * 0.62 * rng.uniform(0.4, 1.0)))
    r = rng.choice([2, 3, 3, 4])
    d.ellipse([sx - r, sy - r, sx + r, sy + r],
              fill=rng.choice([FIRE2, FIRE3, (255, 200, 110)]))
for _ in range(14):                                                           # embers rising above the flames
    ex = EX + rng.randint(-170, 180)
    ey = EY - rng.randint(180, 300)
    r = rng.choice([2, 3, 4])
    d.ellipse([ex - r, ey - r, ex + r, ey + r],
              fill=rng.choice([FIRE1, FIRE2, (255, 200, 110)]))
# smoke plume hugging the blast, drifting up and to the left
for sx, sy, sr, sa in [(1630, SEA_Y - 190, 34, 120), (1560, SEA_Y - 225, 42, 100),
                       (1480, SEA_Y - 250, 48, 80)]:
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(92, 96, 103, sa))

# wave strokes across the sea
for _ in range(58):
    wx = rng.randint(HX0 + 20, HX1 - 190)
    wy = rng.randint(SEA_Y + 26, 748)
    wl = rng.randint(60, 170)
    col = (150, 190, 220, 90) if rng.random() > 0.4 else (96, 146, 184, 70)
    d.line([wx, wy, wx + wl, wy], fill=col, width=4)

# brighter, shorter wave strokes near the horizon to layer the sea
for _ in range(26):
    wx = rng.randint(HX0 + 20, HX1 - 190)
    wy = rng.randint(SEA_Y + 8, SEA_Y + 42)
    wl = rng.randint(30, 90)
    d.line([wx, wy, wx + wl, wy], fill=(170, 205, 232, 110), width=3)

# firelight shimmering on the sea under the blast
for _ in range(30):
    fx = rng.randint(1500, 1920)
    fy = rng.randint(SEA_Y + 10, SEA_Y + 128)
    fl = rng.randint(12, 34)
    fa = max(36, 130 - (fy - SEA_Y))
    d.line([fx, fy, fx, fy + fl], fill=(255, 150, 60, fa), width=5)
# moon glitter path
for _ in range(20):
    gx = rng.randint(270, 390)
    gy = rng.randint(SEA_Y + 10, SEA_Y + 112)
    gl = rng.randint(14, 40)
    d.line([gx, gy, gx + gl, gy], fill=(230, 225, 190, 88), width=4)

# ------------------------------------------- four naval drones closing in
# Big and close to the viewer, each with a bright spray fan and a long
# foam wake trailing behind it, converging on the burning ship.
for dx, dy, sc in [(170, 660, 2.2), (470, 684, 2.4), (800, 664, 2.0), (1100, 690, 1.7)]:
    ln = int(128 * sc)
    body = (150, 170, 188)
    d.ellipse([dx - int(6 * sc), dy + int(6 * sc), dx + ln + int(6 * sc),
               dy + int(26 * sc)], fill=(8, 14, 24, 70))                     # waterline shadow
    d.polygon([(dx, dy), (dx + ln, dy + int(9 * sc)), (dx + ln - int(24 * sc), dy + int(21 * sc)),
               (dx + int(16 * sc), dy + int(19 * sc))], fill=body)
    d.line([dx - int(10 * sc), dy + int(10 * sc), dx, dy + int(12 * sc)],
           fill=(235, 244, 250, 200), width=4)                                # bow wave
    d.polygon([(dx + int(10 * sc), dy), (dx + int(36 * sc), dy - int(17 * sc)),
               (dx + int(56 * sc), dy)], fill=body)                            # fin
    d.polygon([(dx + int(52 * sc), dy + int(14 * sc)), (dx + int(84 * sc), dy + int(24 * sc)),
               (dx + int(58 * sc), dy + int(22 * sc))], fill=(100, 120, 138))  # wing
    d.ellipse([dx + ln - int(38 * sc), dy + int(2 * sc), dx + ln - int(16 * sc),
               dy + int(16 * sc)], fill=(255, 190, 90))                       # sensor eye
    d.ellipse([dx + int(30 * sc), dy - int(19 * sc), dx + int(36 * sc),
               dy - int(13 * sc)], fill=RED_L)                                # signal light
    for k in range(4):                                                        # spray fan
        wy = dy + int(20 * sc) + k * 6
        sx0 = max(HX0 + 8, dx - int((30 + k * 44) * sc))
        d.line([sx0, wy, dx - int(4 * sc), wy - 4],
               fill=(225, 240, 248, 235 - k * 30), width=6)
    for k in range(2):                                                        # foam at its own waterline
        fy = dy + int(24 * sc) + k * 8
        fx0 = max(HX0 + 8, dx - int(150 * sc) + k * 24)
        d.line([fx0, fy, dx - int(40 * sc) + k * 18, fy],
               fill=(214, 230, 240, 120), width=5)

# bow foam where the hull meets the water
for k in range(5):
    d.line([536 + k * 20, SEA_Y + 8 + k * 5, 600 + k * 24, SEA_Y + 8 + k * 5],
           fill=(215, 232, 242, 120), width=5)

# hero headline strip
d.rectangle([HX0, 756, HX1, HY1], fill=(9, 18, 33, 224))
d.rectangle([HX0, 756, HX1, 759], fill=GOLD)
d.rectangle([HX0 + 36, 784, HX0 + 52, 800], fill=RED)
kick_f = font(SANS_B, 36)
d.text((HX0 + 68, 772), "TOP STORY · BENGHAZI, LIBYA", font=kick_f, fill=RED_L)
hero_f = fit_font(d, "UKRAINE SINKS RUSSIAN CORVETTE", SERIF_B, 76, HX1 - HX0 - 72)
d.text((HX0 + 36, 801), "UKRAINE SINKS RUSSIAN CORVETTE", font=hero_f, fill=PAPER)
sub_f = fit_font(d, "Seven naval drones strike the warship Merkury in port — the UN seeks a probe",
                 SANS, 40, HX1 - HX0 - 72, min_size=30)
d.text((HX0 + 36, 872),
       "Seven naval drones strike the warship Merkury in port — the UN seeks a probe",
       font=sub_f, fill=(226, 220, 202))
sub2_f = fit_font(d, "President Zelensky confirms the strike · Tripoli demands explanations from Kyiv",
                  SANS, 32, HX1 - HX0 - 72, min_size=26)
d.text((HX0 + 36, 919),
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
    for wx in (x + 8, x + 78, x + 148):                                        # wavelets under the hull
        d.line([wx, y + 78, wx + 34, y + 78], fill=NAVY2, width=3)
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
