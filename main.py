#!/usr/bin/env python3
"""news-image-20261125 v4 — 'Tariffs, Tiangong & the Chip Rout'.

Draws one 1024x1024 PNG summing up Wednesday 25 November 2026:
50 verified stories, 10 regions, 21 drawn scenes, a world map with red
dots only, a UTC timeline strip and a 6-story ticker.

Everything on the image comes from the verified story list. Only two
clock times are verified and appear: Shenzhou-24 launch 00:18 GMT and
docking 03:56 GMT. No other clock time with numbers appears anywhere.

Deterministic: fixed palette, fixed geometry, no randomness, no time.
Writes to os.environ.get("MAKEFUN_OUTPUT_DIR", "/output") + "/entry.png".
Standard library + Pillow only.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (18, 24, 38)
NAVY = (16, 28, 54)
NAVY2 = (24, 42, 78)
AMBER = (245, 176, 65)
RED = (206, 32, 32)
RED_DK = (150, 18, 18)
TEAL = (14, 116, 110)
GREY = (90, 96, 110)
LINE = (200, 192, 176)
PANEL_BG = (255, 255, 255)
SKY = (214, 231, 245)

# ---------------------------------------------------------------- fonts
def _font(name, size, bold=False):
    cands = []
    if bold:
        cands = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:
        cands = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    if name == "serif":
        cands = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        ]
    for path in cands:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


F_TITLE = _font("serif", 40, bold=True)
F_SUB = _font("sans", 16, bold=True)
F_SECT = _font("sans", 13, bold=True)
F_CAP = _font("sans", 12, bold=True)
F_CAP2 = _font("sans", 11)
F_LIST = _font("sans", 12)
F_LIST_B = _font("sans", 12, bold=True)
F_SMALL = _font("sans", 10, bold=True)
F_TICK = _font("sans", 11, bold=True)
F_NUM = _font("sans", 13, bold=True)


def wrap(draw, text, font, width):
    """Greedy word wrap to pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
def flame(d, cx, cy, s, col=(232, 90, 20)):
    d.polygon([(cx, cy - s), (cx + s * 0.55, cy - s * 0.1),
               (cx + s * 0.35, cy + s * 0.55), (cx, cy + s * 0.3),
               (cx - s * 0.35, cy + s * 0.55), (cx - s * 0.55, cy - s * 0.1)],
              fill=col)
    d.polygon([(cx, cy - s * 0.3), (cx + s * 0.25, cy + s * 0.1),
               (cx, cy + s * 0.4), (cx - s * 0.25, cy + s * 0.1)],
              fill=(245, 200, 60))


def explosion(d, cx, cy, r):
    pts = []
    import math
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=(245, 176, 65), outline=(206, 32, 32))


def ship(d, x, y, w, h):
    d.polygon([(x, y + h * 0.45), (x + w, y + h * 0.45),
               (x + w * 0.88, y + h), (x + w * 0.12, y + h)],
              fill=(40, 60, 90))
    d.rectangle([x + w * 0.18, y, x + w * 0.55, y + h * 0.45], fill=(120, 130, 145))
    d.line([x + w * 0.7, y, x + w * 0.7, y + h * 0.45], fill=INK, width=3)
    d.rectangle([x, y + h * 0.95, x + w, y + h * 1.15], fill=(40, 110, 160))


def tower(d, x, y, w, h):
    d.rectangle([x + w * 0.3, y, x + w * 0.7, y + h], fill=(70, 90, 120))
    for i in range(5):
        yy = y + 4 + i * (h - 8) / 5
        d.rectangle([x + w * 0.36, yy, x + w * 0.64, yy + 3], fill=(245, 200, 60))


def refinery(d, x, y, w, h):
    d.rectangle([x, y + h * 0.5, x + w, y + h], fill=(110, 110, 115))
    for i, fx in enumerate((0.12, 0.38, 0.64, 0.86)):
        d.polygon([(x + w * fx, y + h), (x + w * fx + 4, y + h * 0.15),
                   (x + w * fx + 12, y + h * 0.15), (x + w * fx + 16, y + h)],
                  fill=(80, 80, 88))
    flame(d, x + w * 0.5, y + h * 0.28, 10)


def building(d, x, y, w, h, col=(90, 110, 140)):
    d.rectangle([x, y, x + w, y + h], fill=col)
    for r in range(4):
        for c in range(3):
            d.rectangle([x + 4 + c * (w - 8) / 3, y + 4 + r * (h - 8) / 4,
                         x + 4 + c * (w - 8) / 3 + 6, y + 4 + r * (h - 8) / 4 + 6],
                        fill=(245, 200, 60))


def jet(d, x, y, w, h):
    d.polygon([(x, y + h * 0.5), (x + w * 0.55, y + h * 0.3),
               (x + w, y + h * 0.5), (x + w * 0.55, y + h * 0.7)],
              fill=(60, 80, 110))
    d.polygon([(x + w * 0.45, y + h * 0.5), (x + w * 0.3, y + h * 0.05),
               (x + w * 0.5, y + h * 0.5)], fill=(60, 80, 110))
    d.polygon([(x + w * 0.45, y + h * 0.5), (x + w * 0.3, y + h * 0.95),
               (x + w * 0.5, y + h * 0.5)], fill=(60, 80, 110))


def ballot(d, x, y, w, h):
    d.rectangle([x, y + h * 0.3, x + w, y + h], fill=(150, 60, 60))
    d.rectangle([x + w * 0.2, y + h * 0.3, x + w * 0.8, y + h * 0.45], fill=(40, 40, 40))
    d.rectangle([x + w * 0.35, y, x + w * 0.65, y + h * 0.32], fill=(255, 255, 255),
                outline=INK)
    d.line([x + w * 0.4, y + h * 0.16, x + w * 0.5, y + h * 0.26,
            x + w * 0.62, y + h * 0.06], fill=TEAL, width=3)


def gavel(d, x, y, w, h):
    d.line([x + w * 0.2, y + h * 0.75, x + w * 0.8, y + h * 0.25],
           fill=(120, 80, 40), width=6)
    d.rectangle([x + w * 0.55, y + h * 0.05, x + w * 0.95, y + h * 0.35],
                fill=(90, 60, 30))
    d.rectangle([x + w * 0.05, y + h * 0.8, x + w * 0.95, y + h * 0.95],
                fill=(90, 60, 30))


def trophy(d, x, y, w, h):
    d.pieslice([x + w * 0.2, y, x + w * 0.8, y + h * 0.6], 0, 180, fill=(245, 200, 60))
    d.rectangle([x + w * 0.42, y + h * 0.55, x + w * 0.58, y + h * 0.8],
                fill=(245, 200, 60))
    d.rectangle([x + w * 0.25, y + h * 0.8, x + w * 0.75, y + h * 0.9],
                fill=(245, 200, 60))
    d.arc([x, y + h * 0.05, x + w * 0.3, y + h * 0.4], 90, 270, fill=(245, 200, 60), width=4)
    d.arc([x + w * 0.7, y + h * 0.05, x + w, y + h * 0.4], 270, 90, fill=(245, 200, 60), width=4)


def rocket(d, x, y, w, h):
    d.ellipse([x + w * 0.35, y, x + w * 0.65, y + h * 0.7], fill=(230, 235, 240),
              outline=RED)
    d.polygon([(x + w * 0.35, y + h * 0.55), (x + w * 0.15, y + h * 0.8),
               (x + w * 0.35, y + h * 0.7)], fill=RED)
    d.polygon([(x + w * 0.65, y + h * 0.55), (x + w * 0.85, y + h * 0.8),
               (x + w * 0.65, y + h * 0.7)], fill=RED)
    flame(d, x + w * 0.5, y + h * 0.88, 10)
    d.ellipse([x + w * 0.42, y + h * 0.12, x + w * 0.58, y + h * 0.28],
              fill=(40, 110, 180))


def chart_down(d, x, y, w, h, col=RED):
    pts = [(x, y + h * 0.15), (x + w * 0.25, y + h * 0.3),
           (x + w * 0.45, y + h * 0.25), (x + w * 0.65, y + h * 0.6),
           (x + w * 0.85, y + h * 0.75), (x + w, y + h * 0.95)]
    d.line(pts, fill=col, width=4, joint="curve")
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=col)


def chip(d, x, y, w, h):
    d.rectangle([x + w * 0.2, y + h * 0.2, x + w * 0.8, y + h * 0.8],
                fill=(30, 40, 60))
    d.rectangle([x + w * 0.35, y + h * 0.35, x + w * 0.65, y + h * 0.65],
                fill=(245, 200, 60))
    for i in range(4):
        xx = x + w * (0.3 + i * 0.13)
        d.line([xx, y, xx, y + h * 0.2], fill=(30, 40, 60), width=3)
        d.line([xx, y + h * 0.8, xx, y + h], fill=(30, 40, 60), width=3)


def magnifier(d, x, y, w, h):
    d.ellipse([x, y, x + w * 0.65, y + h * 0.65], outline=INK, width=4)
    d.line([x + w * 0.55, y + h * 0.55, x + w, y + h], fill=INK, width=5)
    d.text((x + w * 0.18, y + h * 0.1), "?", font=F_NUM, fill=RED)


def gate(d, x, y, w, h):
    d.rectangle([x, y + h * 0.2, x + w, y + h * 0.25], fill=INK)
    for i in range(6):
        xx = x + w * i / 5
        d.line([xx, y + h * 0.2, xx, y + h], fill=INK, width=3)
    d.rectangle([x + w * 0.4, y + h * 0.45, x + w * 0.6, y + h * 0.7],
                fill=(220, 220, 220), outline=RED)


def hockey(d, x, y, w, h):
    d.line([x + w * 0.2, y + h * 0.1, x + w * 0.35, y + h * 0.8],
           fill=(120, 80, 40), width=5)
    d.line([x + w * 0.35, y + h * 0.8, x + w * 0.65, y + h * 0.85],
           fill=(120, 80, 40), width=5)
    d.ellipse([x + w * 0.7, y + h * 0.7, x + w * 0.85, y + h * 0.85],
              fill=(255, 255, 255), outline=INK)


def cricket(d, x, y, w, h):
    d.polygon([(x + w * 0.3, y), (x + w * 0.55, y), (x + w * 0.6, y + h * 0.6),
               (x + w * 0.35, y + h * 0.6)], fill=(200, 170, 120))
    d.rectangle([x + w * 0.38, y + h * 0.6, x + w * 0.52, y + h], fill=(120, 80, 40))
    d.ellipse([x + w * 0.7, y + h * 0.15, x + w * 0.9, y + h * 0.35],
              fill=RED)


def chessboard(d, x, y, w, h):
    s = min(w, h) / 4
    for r in range(4):
        for c in range(4):
            if (r + c) % 2 == 0:
                d.rectangle([x + c * s, y + r * s, x + (c + 1) * s, y + (r + 1) * s],
                            fill=INK)
    d.ellipse([x + s * 0.4, y + s * 0.4, x + s * 1.1, y + s * 1.1], fill=RED)
    d.ellipse([x + s * 2.9, y + s * 2.9, x + s * 3.6, y + s * 3.6], fill=(255, 255, 255),
              outline=INK)


def containers(d, x, y, w, h):
    cols = [(206, 32, 32), (40, 110, 180), (245, 176, 65)]
    for r in range(2):
        for c in range(3):
            d.rectangle([x + c * w / 3 + 1, y + r * h / 2 + 1,
                         x + (c + 1) * w / 3 - 1, y + (r + 1) * h / 2 - 1],
                        fill=cols[(r + c) % 3], outline=(255, 255, 255))


def football(d, x, y, w, h):
    d.ellipse([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK, width=2)
    d.polygon([(x + w * 0.5, y + h * 0.3), (x + w * 0.68, y + h * 0.45),
               (x + w * 0.6, y + h * 0.68), (x + w * 0.4, y + h * 0.68),
               (x + w * 0.32, y + h * 0.45)], fill=INK)


def asteroid(d, x, y, w, h):
    d.ellipse([x, y, x + w, y + h], fill=(140, 130, 120))
    for cx, cy, r in ((0.3, 0.35, 0.12), (0.6, 0.55, 0.18), (0.45, 0.7, 0.1)):
        d.ellipse([x + w * cx - r * w, y + h * cy - r * h,
                   x + w * cx + r * w, y + h * cy + r * h], fill=(100, 92, 84))


ICONS = {
    "ship": ship, "tower": tower, "refinery": refinery, "building": building,
    "jet": jet, "ballot": ballot, "gavel": gavel, "trophy": trophy,
    "rocket": rocket, "chart": chart_down, "chip": chip,
    "magnifier": magnifier, "gate": gate, "hockey": hockey,
    "cricket": cricket, "chess": chessboard, "containers": containers,
    "football": football, "asteroid": asteroid,
}


def flag_stripes(d, x, y, w, h, colors):
    n = len(colors)
    for i, col in enumerate(colors):
        d.rectangle([x, y + i * h / n, x + w, y + (i + 1) * h / n], fill=col)


# ---------------------------------------------------------------- data
# 21 drawn scenes: (number, region tag, icon, headline, caption)
SCENES = [
    ("01", "MIDDLE EAST", "ship",
     "HORMUZ ON FIRE",
     "Two oil tankers hit naval mines in the Strait of Hormuz and catch fire."),
    ("02", "MIDDLE EAST", "refinery",
     "RAS TANURA HIT",
     "Houthis attack the Saudi Ras Tanura refinery; fires break out."),
    ("03", "MIDDLE EAST", "tower",
     "RIYADH DRONE STRIKE",
     "Houthi drone strike on a Riyadh tower injures 11 people."),
    ("04", "MIDDLE EAST", "explosion",
     "GAZA STRIKE",
     "Israel kills Hamas colonel Mohammad Abuelouf, his wife and 2 children."),
    ("05", "EUROPE", "explosion",
     "ODESA UNDER FIRE",
     "Russian strike on the Odesa region kills 2, injures 3, incl. a child."),
    ("06", "EUROPE", "refinery",
     "REFINERIES BURNING",
     "Ukraine drones hit Syzran and Kuibyshev Rosneft refineries; 1 killed."),
    ("07", "EUROPE", "jet",
     "POLAND: NO-FLY ZONE",
     "Poland to create a no-fly zone after a drone incursion."),
    ("08", "EUROPE", "building",
     "MERZ WARNS BERLIN",
     "Merz warns Russia wants more than Ukraine."),
    ("09", "EUROPE", "ballot",
     "SPAIN TO THE POLLS",
     "Spain heads to a snap election."),
    ("10", "AFRICA", "explosion",
     "SUDAN: 19 KILLED",
     "RSF drone strikes kill 19 civilians and wound 20 in Blue Nile."),
    ("11", "AFRICA", "gavel",
     "RAMAPHOSA WINS",
     "Ramaphosa wins his court battle over an impeachment threat in Pretoria."),
    ("12", "AFRICA", "trophy",
     "SENEGAL CHAMPIONS",
     "Senegal reinstated as AFCON champions by CAS."),
    ("13", "ASIA-PACIFIC", "rocket",
     "SHENZHOU-24 LIFTS OFF",
     "Pakistan's first astronaut, Muhammad Zeeshan Ali, boards Tiangong."),
    ("14", "ASIA-PACIFIC", "chart",
     "THE CHIP ROUT",
     "KOSPI falls 6.2% as AI doubts hit Samsung and SK Hynix."),
    ("15", "ASIA-PACIFIC", "magnifier",
     "SHANGHAI CHIEF PROBED",
     "China investigates Shanghai party chief Chen Jining."),
    ("16", "ASIA-PACIFIC", "gate",
     "PYONGYANG EXPULSION",
     "North Korea expels a Swiss diplomat."),
    ("17", "ASIA-PACIFIC", "hockey",
     "INDIA 4-0 JAPAN",
     "India women sweep the Women's Asian Champions Trophy league stage."),
    ("18", "ASIA-PACIFIC", "cricket",
     "204 OFF 53 BALLS",
     "Vaibhav Sooryavanshi hits 28 sixes, the fastest List A double century."),
    ("19", "ASIA-PACIFIC", "chess",
     "GUKESH HOLDS DRAW",
     "Gukesh holds Sindarov to a draw in Game 1 of the World Chess Championship."),
    ("20", "AMERICAS", "containers",
     "TARIFFS ON 14 ECONOMIES",
     "US proposes tariffs: China 20%, India 25%, Vietnam 35%."),
    ("21", "AMERICAS", "chip",
     "NVIDIA SLIDES",
     "Nvidia falls again as Jensen Huang is reinstated as CEO."),
]

# The other 29 stories, one dense line each (each fits one line at 11 px).
REST = [
    ("Knesset advances October 7 inquiry", "ISRAEL"),
    ("Putin: Ukraine keeps hitting Russian refineries", "RUSSIA"),
    ("Poland pushes permanent US military presence", "POLAND"),
    ("DR Congo Ebola outbreak in Beni", "DR CONGO"),
    ("Solomon Islands and Australia sign security treaty", "PACIFIC"),
    ("Australia inflation rises to 4.9%", "AUSTRALIA"),
    ("India women's hockey reaches career-best world No. 5", "INDIA"),
    ("Ben Stokes registers for IPL 2027 auction, Goa", "CRICKET"),
    ("East Bengal 1-0 Al Hussein, ACL Two", "FOOTBALL"),
    ("Pakistan names Fatima Sana captain for WI tour", "CRICKET"),
    ("Sri Lanka Women win Emerging Nations Trophy", "CRICKET"),
    ("Wall St: S&P -2.2%, Nasdaq -3.2%; Dow past 50,000", "MARKETS"),
    ("Dell record Q3: revenue $54.9bn, AI servers $22bn", "TECH"),
    ("US Oct PCE inflation 3.8%, core 3.3%", "US ECONOMY"),
    ("Huawei convicted, 10 of 12 counts, Brooklyn jury", "US COURTS"),
    ("Anthropic shares fall below IPO price", "TECH"),
    ("US Army destroys lead azide stockpile in Iowa", "USA"),
    ("Colombia: hostages freed after 17-hour siege", "COLOMBIA"),
    ("Argentina enters technical recession", "ARGENTINA"),
    ("Tatum 41 pts, Celtics beat Wizards 131-116", "NBA"),
    ("Bitcoin about $58,400; gold -3.2%; Brent $89.73", "MARKETS"),
    ("Poundland collapses, 11,000 jobs at risk", "UK"),
    ("UK energy price cap to rise 26% in January", "UK"),
    ("UCL: Real Madrid 5-1 PSV; Barcelona 4-1 Sabah", "FOOTBALL"),
    ("ESA Hera: first images of Dimorphos crater", "SPACE"),
    ("NASA Europa Clipper Earth flyby on Dec 3", "SPACE"),
    ("BepiColombo settles into Mercury orbit", "SPACE"),
    ("Pope Leo XIV: COP31 climate talks failed", "CLIMATE"),
    ("UN warns HIV gains could unravel, Geneva", "HEALTH"),
]

TICKER = [
    "TARIFFS ON 14 ECONOMIES",
    "KOSPI -6.2% IN CHIP ROUT",
    "SHENZHOU-24 DOCKS",
    "HORMUZ TANKERS ON FIRE",
    "POUNDLAND COLLAPSES",
    "REAL MADRID 5-1 PSV",
]

# World map: rough continent polygons in (lon, lat).
CONTINENTS = [
    [(-168, 65), (-150, 70), (-130, 71), (-120, 69), (-105, 68), (-95, 80),
     (-85, 69), (-75, 72), (-65, 60), (-55, 52), (-60, 46), (-70, 42),
     (-75, 35), (-80, 26), (-85, 30), (-90, 21), (-95, 16), (-100, 18),
     (-105, 23), (-115, 30), (-125, 40), (-125, 49), (-140, 60), (-158, 58)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -55), (-73, -50),
     (-75, -35), (-80, -20), (-80, -10)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 53), (5, 58), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (30, 70),
     (20, 70), (15, 68), (10, 64), (5, 60), (2, 55), (-2, 50), (-5, 43)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (46, 0), (40, -10), (35, -20), (32, -28),
     (25, -34), (18, -35), (12, -18), (9, -1), (9, 4), (-8, 5)],
    [(30, 70), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 66), (178, 65), (170, 60), (160, 55), (155, 50),
     (140, 45), (135, 35), (130, 33), (127, 35), (120, 30), (110, 20),
     (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 8), (75, 12),
     (70, 20), (60, 25), (55, 26), (50, 28), (45, 30), (40, 35), (35, 36)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (147, -39), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -11), (137, -12), (132, -12), (126, -14), (122, -17)],
]

# Red dots only: (lon, lat) of story locations.
DOTS = [
    (56, 26), (50, 26.6), (46.7, 24.6), (34.5, 31.5), (30.7, 46.5),
    (30.5, 50.5), (48.5, 53.2), (50, 53.2), (21, 52.2), (13.4, 52.5),
    (-3.7, 40.4), (33, 11), (28.2, -25.7), (29.5, 0.5), (100.3, 40.9),
    (127, 37.5), (139.7, 35.7), (121.5, 31.2), (125.8, 39), (160, -9.4),
    (149.1, -35.3), (77.4, 23.3), (6.1, 46.2), (88.4, 22.6),
    (-77, 38.9), (-74, 40.7), (-93.1, 41.9), (-75.5, 10.4),
    (-58.4, -34.6), (-71, 42.4), (-0.1, 51.5),
]

REGION_COUNTS = [
    ("MIDDLE EAST", "5"), ("EUROPE", "4"), ("RUSSIA-UKRAINE", "3"),
    ("AFRICA", "4"), ("ASIA-PACIFIC", "14"), ("N. AMERICA", "10"),
    ("LATIN AMERICA", "2"), ("UK", "2"), ("EURO FOOTBALL", "1"),
    ("SCIENCE & CLIMATE", "5"),
]


# ---------------------------------------------------------------- drawing
def draw_map(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(226, 236, 244), outline=LINE)
    def proj(lon, lat):
        px = x0 + 8 + (lon + 180) / 360.0 * (x1 - x0 - 16)
        py = y0 + 8 + (80 - lat) / 165.0 * (y1 - y0 - 16)
        return (px, py)
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=(176, 196, 168),
                  outline=(120, 140, 120))
    for lon, lat in DOTS:
        px, py = proj(lon, lat)
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED,
                  outline=(255, 255, 255), width=1)


def draw_scene(d, box, num, region, icon, headline, caption):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=PANEL_BG, outline=LINE)
    # number badge + region tag
    d.rectangle([x0, y0, x0 + 30, y0 + 16], fill=NAVY)
    d.text((x0 + 4, y0 + 2), num, font=F_SMALL, fill=(255, 255, 255))
    d.text((x0 + 34, y0 + 2), region, font=F_SMALL, fill=GREY)
    # icon area
    ix0, iy0 = x0 + 6, y0 + 20
    iw, ih = 52, 44
    d.rectangle([ix0, iy0, ix0 + iw, iy0 + ih], fill=SKY)
    if icon == "explosion":
        explosion(d, ix0 + iw / 2, iy0 + ih / 2, 18)
    else:
        ICONS[icon](d, ix0 + 6, iy0 + 5, iw - 12, ih - 10)
    # small flags where apt
    if num == "17":
        flag_stripes(d, ix0 + iw - 16, iy0 + 2, 14, 9,
                     [(255, 153, 51), (255, 255, 255), (19, 136, 8)])
    if num == "09":
        flag_stripes(d, ix0 + iw - 16, iy0 + 2, 14, 9,
                     [(198, 12, 48), (255, 196, 0), (198, 12, 48)])
    if num == "07":
        flag_stripes(d, ix0 + iw - 16, iy0 + 2, 14, 9,
                     [(255, 255, 255), (220, 20, 60)])
    # headline + caption to the right of the icon, then below
    tx = ix0 + iw + 8
    tw = x1 - tx - 6
    hl = wrap(d, headline, F_CAP, tw)
    yy = iy0 + 1
    for line in hl[:2]:
        d.text((tx, yy), line, font=F_CAP, fill=INK)
        yy += 13
    cap = wrap(d, caption, F_CAP2, x1 - x0 - 12)
    yy = y0 + 68
    for line in cap[:3]:
        d.text((x0 + 6, yy), line, font=F_CAP2, fill=(40, 44, 56))
        yy += 12


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- header
    d.rectangle([0, 0, W, 92], fill=NAVY)
    d.rectangle([0, 92, W, 96], fill=AMBER)
    d.text((16, 8), "TARIFFS, TIANGONG & THE CHIP ROUT",
           font=F_TITLE, fill=(255, 255, 255))
    d.text((16, 62),
           "WEDNESDAY, 25 NOVEMBER 2026  ·  50 STORIES  ·  10 REGIONS  ·  21 FIELDS",
           font=F_SUB, fill=AMBER)

    # ---- 21 drawn scenes: 3 columns x 7 rows, left side
    for i, (num, region, icon, headline, caption) in enumerate(SCENES):
        col, row = i % 3, i // 3
        x0 = 12 + col * 216
        y0 = 104 + row * 108
        draw_scene(d, (x0, y0, x0 + 208, y0 + 102),
                   num, region, icon, headline, caption)

    # ---- right column: map + region counts + the rest of the day
    rx0, rx1 = 668, 1012
    d.text((rx0, 104), "WHERE IT HAPPENED", font=F_SECT, fill=INK)
    d.text((rx0, 122), "Red dots mark the places in today's stories.",
           font=F_CAP2, fill=GREY)
    draw_map(d, (rx0, 140, rx1, 336))
    # region counts: 2 columns x 5 rows, count right-aligned in column
    yy = 344
    d.text((rx0, yy), "10 REGIONS", font=F_SECT, fill=INK)
    yy += 18
    for i, (name, cnt) in enumerate(REGION_COUNTS):
        cx = rx0 + (i % 2) * 176
        cy = yy + (i // 2) * 15
        d.text((cx, cy), name, font=F_SMALL, fill=GREY)
        cw = d.textlength(cnt, font=F_SMALL)
        d.text((cx + 168 - cw, cy), cnt, font=F_SMALL, fill=RED)
    yy += 5 * 15 + 6
    d.text((rx0, yy), "THE REST OF THE DAY — 29 MORE STORIES",
           font=F_SECT, fill=INK)
    yy += 19
    F_REST = _font("sans", 11)
    F_REST_S = _font("sans", 10)
    for text, tag in REST:
        line = tag + " — " + text
        font = F_REST
        if d.textlength(line, font=font) > rx1 - rx0:
            font = F_REST_S
        while d.textlength(line, font=font) > rx1 - rx0 and len(line) > 4:
            line = line[:-2] + "…"
        d.text((rx0, yy), line, font=font, fill=(30, 34, 48))
        yy += 14

    # ---- UTC timeline strip (only two verified clock times carry numbers)
    ty0, ty1 = 886, 946
    d.rectangle([0, ty0, W, ty1], fill=NAVY2)
    d.text((16, ty0 + 5), "THE DAY IN UTC", font=F_SECT, fill=AMBER)
    line_y = ty0 + 34
    d.line([16, line_y, W - 16, line_y], fill=(255, 255, 255), width=2)
    stops = [
        # (fraction along strip, day-part label, clock label or None)
        (0.10, "ASIA MORNING", None),
        (0.22, "LAUNCH", "00:18 GMT"),
        (0.36, "DOCKING", "03:56 GMT"),
        (0.58, "EUROPE MIDDAY", None),
        (0.80, "AMERICAS AFTERNOON", None),
        (0.95, "DAY ENDS", None),
    ]
    for frac, label, clock in stops:
        cx = 16 + frac * (W - 32)
        d.ellipse([cx - 5, line_y - 5, cx + 5, line_y + 5], fill=RED,
                  outline=(255, 255, 255))
        if clock:
            cw = d.textlength(clock, font=F_SMALL)
            d.text((max(16, min(W - 16 - cw, cx - cw / 2)), ty0 + 19),
                   clock, font=F_SMALL, fill=AMBER)
        lw = d.textlength(label, font=F_SMALL)
        lx = max(16, min(W - 16 - lw, cx - lw / 2))
        d.text((lx, line_y + 8), label, font=F_SMALL, fill=(255, 255, 255))

    # ---- ticker strip (auto-fit so the last item is never cut off)
    d.rectangle([0, 952, W, 990], fill=RED)
    ticker = "  •  ".join(TICKER)
    tick_font = F_TICK
    for size in (11, 10, 9):
        tick_font = _font("sans", size, bold=True)
        if d.textlength(ticker, font=tick_font) <= W - 32:
            break
    d.text((16, 963), ticker, font=tick_font, fill=(255, 255, 255))
    d.text((16, 996), "All 50 stories were reported on Wednesday, 25 November 2026.",
           font=F_CAP2, fill=GREY)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"), format="PNG",
             compress_level=9)


if __name__ == "__main__":
    main()
