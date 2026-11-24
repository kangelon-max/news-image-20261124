#!/usr/bin/env python3
"""gen.py — draws the news-image-20261124 poster, "THE WORLD IN ONE DAY".

Build-time generator (runs locally, where PIL lives): it renders the poster
at 2048x2048 and downscales to the 1024x1024 entry.png the competition gate
accepts (at most 1024x1024 px, at most 1 MiB). Fully deterministic: every
position, star and wave comes from fixed constants or a fixed-seed RNG, and
the PNG is saved with no time metadata. main.ts ships entry.png to /output.
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
GOLD = (201, 162, 39)
DARK = (8, 14, 24)
MOON = (240, 230, 190)
FIRE1 = (232, 110, 40)
FIRE2 = (245, 180, 60)
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


def fit_font(draw, s, path, start, max_w, min_size=20):
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

d.rectangle([MX, 40, RIGHT, 272], fill=NAVY)
d.rectangle([MX, 40, RIGHT, 272], outline=GOLD, width=4)
title_f = fit_font(d, "THE WORLD IN ONE DAY", SERIF_B, 124, RIGHT - MX - 120)
tw = text_w(d, "THE WORLD IN ONE DAY", title_f)
d.text(((W - tw) / 2, 62), "THE WORLD IN ONE DAY", font=title_f, fill=PAPER)
date_f = font(SANS_B, 46)
date_s = "TUESDAY · 24 NOVEMBER 2026"
d.text((MX + 36, 200), date_s, font=date_f, fill=GOLD)
tag_f = font(SERIF, 36)
tag_s = "One image, the whole planet"
gw = text_w(d, tag_s, tag_f)
d.text((RIGHT - 36 - gw, 208), tag_s, font=tag_f, fill=(214, 205, 180))

# ------------------------------------------------------------------- hero
# Night sea off Benghazi: drones skim the waves, a corvette burns at port.

HX0, HY0, HX1, HY1 = MX, 296, RIGHT, 956
SEA_Y = 648
vgrad(d, HX0, HY0, HX1, SEA_Y, (9, 20, 38), (20, 44, 72))
vgrad(d, HX0, SEA_Y, HX1, HY1, (23, 74, 110), (10, 34, 58))

# stars
for _ in range(110):
    sx = rng.randint(HX0 + 14, HX1 - 14)
    sy = rng.randint(HY0 + 14, SEA_Y - 150)
    r = rng.choice([2, 2, 3])
    a = rng.randint(90, 210)
    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255, a))

# moon and its glow
for gr, ga in [(120, 26), (92, 40)]:
    d.ellipse([1708 - gr, 428 - gr, 1708 + gr, 428 + gr], fill=(240, 230, 190, ga))
d.ellipse([1708 - 62, 428 - 62, 1708 + 62, 428 + 62], fill=MOON)
d.ellipse([1688 - 13, 408 - 13, 1688 + 13, 408 + 13], fill=(222, 210, 168))
d.ellipse([1736 - 9, 452 - 9, 1736 + 9, 452 + 9], fill=(222, 210, 168))

# port silhouette, left: container stacks and two cranes
for bx, bw, bh in [(70, 120, 74), (196, 96, 52), (298, 130, 92), (434, 84, 60)]:
    d.rectangle([bx, SEA_Y - bh, bx + bw, SEA_Y], fill=DARK)
for cx in (150, 470):
    d.line([cx, SEA_Y - 210, cx, SEA_Y], fill=DARK, width=14)
    d.line([cx, SEA_Y - 210, cx + 150, SEA_Y - 210], fill=DARK, width=12)
    d.line([cx + 138, SEA_Y - 210, cx + 138, SEA_Y - 158], fill=DARK, width=7)
    d.rectangle([cx + 118, SEA_Y - 158, cx + 158, SEA_Y - 132], fill=DARK)

# corvette silhouette, centre-right on the waterline, big enough to read
HULL = [(930, SEA_Y), (1015, SEA_Y - 42), (1610, SEA_Y - 42), (1700, SEA_Y)]
d.polygon(HULL, fill=DARK)
d.rectangle([1090, SEA_Y - 108, 1300, SEA_Y - 42], fill=DARK)         # bridge block
d.rectangle([1180, SEA_Y - 162, 1202, SEA_Y - 108], fill=DARK)        # mast
d.line([1191, SEA_Y - 162, 1270, SEA_Y - 118], fill=DARK, width=6)
d.rectangle([1360, SEA_Y - 84, 1490, SEA_Y - 42], fill=DARK)          # aft block
d.rectangle([990, SEA_Y - 66, 1046, SEA_Y - 42], fill=DARK)           # fore gun
for wx in range(1112, 1280, 34):                                     # lit windows
    d.rectangle([wx, SEA_Y - 92, wx + 14, SEA_Y - 78], fill=GOLD)
for wx in range(1384, 1468, 32):
    d.rectangle([wx, SEA_Y - 68, wx + 12, SEA_Y - 55], fill=GOLD)

# explosion bloom eating the stern, flames up, smoke above
EX, EY = 1630, SEA_Y - 18
for (rx, ry), col in [((126, 78), FIRE1), ((88, 54), FIRE2), ((48, 30), (252, 226, 160))]:
    d.ellipse([EX - rx, EY - ry, EX + rx, EY + ry], fill=col)
for fx, fw, fh in [(-70, 26, 92), (-24, 32, 128), (28, 28, 104), (74, 22, 76)]:
    d.polygon([(EX + fx, EY - 30), (EX + fx + fw, EY - 30), (EX + fx + fw // 2, EY - 30 - fh)],
              fill=FIRE2)
for i, (sx, sy, sr) in enumerate([(1700, 452, 42), (1776, 404, 56), (1852, 372, 66)]):
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SMOKE + (110 - i * 20,))

# three naval drones skimming in from the left, wakes behind them
for dx, dy, sc in [(360, 540, 1.5), (610, 592, 1.85), (905, 528, 1.3)]:
    ln = int(120 * sc)
    d.polygon([(dx, dy), (dx + ln, dy + int(10 * sc)), (dx + ln - int(26 * sc), dy + int(22 * sc)),
               (dx + int(18 * sc), dy + int(20 * sc))], fill=(96, 116, 136))
    d.polygon([(dx + int(8 * sc), dy), (dx + int(34 * sc), dy - int(16 * sc)),
               (dx + int(52 * sc), dy)], fill=(96, 116, 136))
    d.ellipse([dx + ln - int(30 * sc), dy + int(4 * sc), dx + ln - int(16 * sc),
               dy + int(16 * sc)], fill=GOLD)
    for k in range(4):  # wake foam
        wy = SEA_Y + 16 + k * 12
        d.line([dx - 130 + k * 22, wy, dx - 30 + k * 16, wy],
               fill=(210, 228, 240, 130), width=5)

# wave strokes across the sea
for _ in range(46):
    wx = rng.randint(HX0 + 20, HX1 - 190)
    wy = rng.randint(SEA_Y + 26, HY1 - 190)
    wl = rng.randint(60, 170)
    d.line([wx, wy, wx + wl, wy], fill=(150, 190, 220, 90), width=4)

# hero headline strip
d.rectangle([HX0, 762, HX1, HY1], fill=(10, 20, 36, 216))
kick_f = font(SANS_B, 36)
d.text((HX0 + 36, 778), "TOP STORY · BENGHAZI, LIBYA", font=kick_f, fill=RED)
hero_f = fit_font(d, "UKRAINE SINKS RUSSIAN CORVETTE", SERIF_B, 84, HX1 - HX0 - 72)
d.text((HX0 + 36, 818), "UKRAINE SINKS RUSSIAN CORVETTE", font=hero_f, fill=PAPER)
sub_f = font(SANS, 38)
sub = "Seven naval drones strike the warship Merkury in port — the UN seeks a probe"
d.text((HX0 + 36, 902), sub, font=sub_f, fill=(222, 216, 198))


# ------------------------------------------------------------ major panels

def motif_tanker(x, y):
    d.polygon([(x, y + 44), (x + 16, y + 26), (x + 190, y + 26), (x + 206, y + 44)], fill=NAVY)
    d.rectangle([x + 30, y + 8, x + 150, y + 26], fill=NAVY2)
    d.rectangle([x + 158, y - 12, x + 182, y + 26], fill=NAVY)
    for mx, my in [(x + 236, y + 52), (x + 268, y + 30), (x + 300, y + 52)]:
        d.ellipse([mx - 11, my - 11, mx + 11, my + 11], outline=RED, width=5)
        for dx, dy in [(0, -17), (0, 17), (-17, 0), (17, 0)]:
            d.line([mx, my, mx + dx, my + dy], fill=RED, width=4)


def motif_chart(x, y):
    pts = [(x, y + 66), (x + 62, y + 50), (x + 118, y + 56), (x + 178, y + 26), (x + 246, y + 2)]
    d.line(pts, fill=GOLD, width=9, joint="curve")
    d.polygon([(x + 246, y + 2), (x + 218, y + 4), (x + 240, y + 26)], fill=GOLD)
    d.line([x, y + 78, x + 262, y + 78], fill=NAVY2, width=3)


def motif_skyline(x, y):
    for bx, bw, bh in [(0, 44, 52), (52, 34, 38), (94, 52, 58), (154, 36, 44), (198, 46, 56)]:
        d.rectangle([x + bx, y + 78 - bh, x + bx + bw, y + 78], fill=NAVY)
    for wx, wy in [(106, 40), (126, 52), (208, 44)]:
        d.rectangle([x + wx, y + wy, x + wx + 9, y + wy + 11], fill=GOLD)


def motif_building(x, y):
    d.rectangle([x, y - 20, x + 120, y + 78], fill=NAVY)
    for r in range(4):
        for c in range(3):
            lit = (r * 3 + c) % 3 != 0
            d.rectangle([x + 14 + c * 36, y - 8 + r * 22, x + 32 + c * 36, y + 6 + r * 22],
                        fill=GOLD if lit else NAVY2)
    d.polygon([(x + 84, y + 6), (x + 104, y + 34), (x + 92, y + 40), (x + 108, y + 66)],
              fill=RED)


def panel(x0, y0, x1, y1, kicker, headline, body, motif):
    d.rectangle([x0, y0, x1, y1], fill=CARD)
    d.rectangle([x0, y0, x1, y1], outline=NAVY, width=4)
    d.rectangle([x0, y0, x1, y0 + 10], fill=RED)
    motif(x1 - 330, y0 + 40)
    d.text((x0 + 30, y0 + 28), kicker, font=font(SANS_B, 36), fill=RED)
    head_f = fit_font(d, headline, SERIF_B, 54, x1 - x0 - 396)
    d.text((x0 + 30, y0 + 76), headline, font=head_f, fill=NAVY)
    body_f = font(SANS, 42)
    ly = y0 + 148
    for line in wrap(d, body, body_f, x1 - x0 - 60):
        d.text((x0 + 30, ly), line, font=body_f, fill=INK)
        ly += 54


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
d.text((MX + 6, BY), "AROUND THE WORLD IN BRIEF", font=font(SANS_B, 36), fill=RED)
sign_f = font(SERIF, 36)
sign_s = "57 stories · 854 headlines · one image"
sw = text_w(d, sign_s, sign_f)
d.text((RIGHT - 6 - sw, BY), sign_s, font=sign_f, fill=INK)
d.line([MX, BY + 52, RIGHT, BY + 52], fill=NAVY, width=3)

BRIEFS = [
    ("INDONESIA", "Banten factory fire kills 26, dozens missing"),
    ("NEPAL", "5.6 quake strikes Koshi, near China border"),
    ("SPACE", "Zeeshan Ali, first foreigner aboard Tiangong"),
    ("THE HAGUE", "14 nations back ICJ Rohingya genocide ruling"),
    ("DR CONGO", "Ituri fighting traps Ebola teams at hospital"),
    ("COLOMBIA", "Car bomb wrecks Villavicencio governor's office"),
    ("AI", "Guterres seeks a global AI-risk framework"),
    ("POLAND", "Russian drone enters airspace, NATO responds"),
]
COLX = [MX + 6, 1052]
COLW = 922
lead_f = font(SANS_B, 38)
body_f2 = font(SANS, 38)
for i, (lead, txt) in enumerate(BRIEFS):
    cx = COLX[i % 2]
    cy = BY + 76 + (i // 2) * 50
    d.text((cx, cy), lead, font=lead_f, fill=NAVY)
    lw = text_w(d, lead, lead_f)
    rest = " — " + txt
    rf = fit_font(d, rest, SANS, 38, COLW - lw, min_size=28)
    d.text((cx + lw, cy + (38 - rf.size)), rest, font=rf, fill=INK)

# ------------------------------------------------------------------ ticker

TY = 1952
d.rectangle([MX, TY, RIGHT, 2008], fill=NAVY)
tick = ("S&P 500 7,237 ▲4.73% · NASDAQ 24,090 ▲6.51% · NIKKEI 58,645 ▲3.91% · "
        "FTSE ▲1.30% · BRENT $86.7 · GOLD $3,620")
tick_f = fit_font(d, tick, SANS_B, 34, RIGHT - MX - 48)
tw2 = text_w(d, tick, tick_f)
d.text(((W - tw2) / 2, TY + 11), tick, font=tick_f, fill=GOLD)

# -------------------------------------------------------------------- save

final = img.resize((FINAL, FINAL), Image.LANCZOS)
final.save("entry.png", optimize=True)
print("wrote entry.png", final.size)
