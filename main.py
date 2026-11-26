#!/usr/bin/env python3
"""One-day world news image: Wednesday, 25 November 2026.

Draws a dense newspaper-style infographic of 36 verified stories from
that day (18 drawn panels + 18 listed in "The Rest of the Day"), a
simplified world map with red dots, region counts, a day-part timeline
and a footer. Standard library + Pillow only, no network, fully
deterministic: the same run always writes the same PNG bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT_NAME = "entry.png"

# ---- palette ---------------------------------------------------------
PAPER = (247, 243, 234)
INK = (24, 28, 38)
NAVY = (26, 42, 74)
RED = (178, 34, 34)
MUTED = (96, 100, 110)
PANEL = (255, 255, 255)
BORDER = (200, 196, 186)
MAP_BG = (215, 227, 234)
LAND = (154, 168, 143)
DOT = (192, 39, 39)

REGION_COLORS = {
    "MIDDLE EAST": (176, 58, 46),
    "EUROPE": (46, 95, 163),
    "ASIA-PACIFIC": (30, 122, 76),
    "MARKETS": (138, 109, 0),
    "TECH": (91, 45, 142),
    "SPORT": (194, 94, 0),
    "AFRICA": (14, 124, 123),
    "AMERICAS": (120, 60, 120),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


F_TITLE = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)
F_REG = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Word-wrap text to the given pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, width, max_lines):
    """Wrap and clip to max_lines, adding an ellipsis if clipped."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " ...", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + " ..."
    return lines


# ---- the 18 drawn panels ---------------------------------------------
PANELS = [
    ("MIDDLE EAST", "CAIRO TANKER FIRE",
     "Fuel tanker overturns on Ring Road, Giza; 31 killed, 21 injured, 27 vehicles burned",
     "fire"),
    ("MIDDLE EAST", "RIYADH DRONE STRIKE",
     "Houthi drone hits tower in Riyadh financial district; 11 injured, incl. 2 Indians; India condemns",
     "drone"),
    ("MIDDLE EAST", "HORMUZ CLAIM DISPUTED",
     "Iran claims mines hit tankers in Strait of Hormuz; US military disputes it; reports differ",
     "mine"),
    ("EUROPE", "UKRAINE STRIKES NEAR BENGHAZI",
     "Ukraine strikes Russian ships near Benghazi, Libya; 2 Libyan soldiers killed",
     "ship"),
    ("ASIA-PACIFIC", "SHENZHOU-24 LIFTS OFF",
     "China launches Shenzhou-24; Pakistan's first astronaut, Muhammad Zeeshan Ali, aboard",
     "rocket"),
    ("EUROPE", "SPAIN TO THE POLLS",
     "Snap general election on Sunday; PSOE promises housing reform, trails PP-led bloc",
     "ballot"),
    ("EUROPE", "30+ NATIONS TO RUSSIA",
     "Over 30 countries urge Russia to stop using chemical agents in Ukraine",
     "flask"),
    ("MARKETS", "KOSPI -5.9%",
     "Chip rout deepens; SK Hynix -9.8%, Samsung -9.1%; Nikkei -2.9%, Taiex -6.0%",
     "chart"),
    ("TECH", "NVIDIA -5.9%",
     "AI selloff resumes; Anthropic -6.5%, below its IPO price",
     "chip"),
    ("MARKETS", "TARIFFS LOOM",
     "White House plans tariff rises on China and 15 partners; USTR probe findings expected",
     "tag"),
    ("MARKETS", "US INFLATION IN LINE",
     "October PCE +3.8% year on year, +0.3% on month, as expected",
     "gauge"),
    ("TECH", "DELL FALLS DESPITE RECORD",
     "Shares fall despite record $132.3B AI backlog and lifted outlook",
     "laptop"),
    ("EUROPE", "UK ENERGY CAP +26%",
     "UK energy price cap to rise 26% to \u00a32,166 in January",
     "bolt"),
    ("ASIA-PACIFIC", "JAVA MINE FLOOD",
     "Flooded West Java gold mine leaves 9 dead, 17 trapped",
     "tunnel"),
    ("ASIA-PACIFIC", "BANGLADESH WAGE +36%",
     "Garment workers win 36% minimum-wage rise, to 17,000 taka a month",
     "coins"),
    ("SPORT", "204 OFF 53 BALLS",
     "Sooryavanshi smashes 204 off 53 balls, 28 sixes \u2014 List A records",
     "cricket"),
    ("SPORT", "SENEGAL CHAMPIONS AGAIN",
     "CAS restores Senegal as AFCON champions, overturning CAF award to Morocco",
     "trophy"),
    ("AFRICA", "EBOLA TEAMS EVACUATED",
     "DR Congo Ebola health workers evacuated amid heavy fighting in Ituri",
     "cross"),
]

# ---- the other 18 stories, one line each ------------------------------
REST = [
    ("19", "AMERICAS", "Trump: Iran war funding secured to Jan"),
    ("20", "MIDDLE EAST", "Iran claims US MQ-9 drone downed"),
    ("21", "AMERICAS", "Coast Guard: 6 dead in Cessna crash"),
    ("22", "AMERICAS", "DOJ charges 800+ in anti-scam sweep"),
    ("23", "ASIA-PACIFIC", "Australia\u2013Solomon Islands treaty"),
    ("24", "MIDDLE EAST", "Iraq takes control of Kurdish oil"),
    ("25", "AFRICA", "Congo to halt cobalt exports Nov 30"),
    ("26", "AFRICA", "HIV funding fell 18% in a year: UNAIDS"),
    ("27", "EUROPE", "Ukraine faces \u20ac70B gap for 2027"),
    ("28", "EUROPE", "Court: Poland, Latvia pushbacks inhumane"),
    ("29", "AMERICAS", "Judge bars Trump punishing ICC groups"),
    ("30", "TECH", "Huawei convicted in US court"),
    ("31", "ASIA-PACIFIC", "China\u2013Cambodia Golden Dragon drills"),
    ("32", "ASIA-PACIFIC", "Hasina sets Dec 16 return from exile"),
    ("33", "SPORT", "Ben Stokes registers for IPL 2027 auction"),
    ("34", "SPORT", "East Bengal 1-0 Al Hussein; Jeakson 87th"),
    ("35", "MARKETS", "Bitcoin near $59,300; Brent near $90"),
    ("36", "MIDDLE EAST", "UN fears Gaza attacks; Yemen aid"),
]

REGION_COUNTS = [
    ("MIDDLE EAST", 6), ("EUROPE", 6), ("ASIA-PACIFIC", 6),
    ("AMERICAS", 4), ("MARKETS", 4), ("SPORT", 4),
    ("TECH", 3), ("AFRICA", 3),
]

DAY_PARTS = [
    ("ASIA MORNING", "first reports"),
    ("EUROPE MIDDAY", "midday"),
    ("AMERICAS AFTERNOON", "afternoon"),
    ("DAY ENDS", "the day closes"),
]


# ---- icons (simple drawn glyphs, 40x40 box centred on cx, cy) --------
def draw_icon(d, kind, cx, cy):
    s = 20  # half-size
    if kind == "fire":
        d.polygon([(cx, cy - s), (cx + 12, cy - 2), (cx + 8, cy + 12),
                   (cx - 6, cy + 14), (cx - 12, cy + 2)], fill=(226, 88, 34))
        d.polygon([(cx, cy - 2), (cx + 6, cy + 6), (cx, cy + 12),
                   (cx - 6, cy + 6)], fill=(255, 196, 0))
    elif kind == "drone":
        d.rectangle([cx - 8, cy - 4, cx + 8, cy + 4], fill=INK)
        d.ellipse([cx - 16, cy - 12, cx - 6, cy - 2], outline=INK, width=2)
        d.ellipse([cx + 6, cy - 12, cx + 16, cy - 2], outline=INK, width=2)
        d.ellipse([cx - 16, cy + 2, cx - 6, cy + 12], outline=INK, width=2)
        d.ellipse([cx + 6, cy + 2, cx + 16, cy + 12], outline=INK, width=2)
        d.line([cx - 11, cy - 7, cx - 16, cy - 12], fill=INK, width=2)
        d.line([cx + 11, cy - 7, cx + 16, cy - 12], fill=INK, width=2)
        d.line([cx - 11, cy + 7, cx - 16, cy + 12], fill=INK, width=2)
        d.line([cx + 11, cy + 7, cx + 16, cy + 12], fill=INK, width=2)
    elif kind == "mine":
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=INK)
        for dx, dy in [(-14, 0), (14, 0), (0, -14), (0, 14),
                       (-10, -10), (10, -10), (-10, 10), (10, 10)]:
            d.line([cx + dx * 0.6, cy + dy * 0.6, cx + dx, cy + dy],
                   fill=INK, width=2)
        d.arc([cx - 16, cy + 12, cx - 4, cy + 20], 0, 180, fill=(46, 95, 163), width=2)
        d.arc([cx + 4, cy + 12, cx + 16, cy + 20], 0, 180, fill=(46, 95, 163), width=2)
    elif kind == "ship":
        d.polygon([(cx - 16, cy + 4), (cx + 16, cy + 4), (cx + 10, cy + 14),
                   (cx - 10, cy + 14)], fill=(46, 95, 163))
        d.line([cx, cy + 4, cx, cy - 14], fill=INK, width=2)
        d.polygon([(cx, cy - 14), (cx + 10, cy - 8), (cx, cy - 6)], fill=RED)
        d.line([cx - 16, cy - 12, cx - 10, cy - 16], fill=(226, 88, 34), width=2)
        d.line([cx - 16, cy - 12, cx - 12, cy - 18], fill=(226, 88, 34), width=2)
    elif kind == "rocket":
        d.polygon([(cx, cy - 18), (cx + 8, cy - 4), (cx + 6, cy + 10),
                   (cx - 6, cy + 10), (cx - 8, cy - 4)], fill=(200, 200, 205))
        d.ellipse([cx - 4, cy - 6, cx + 4, cy + 2], fill=(46, 95, 163))
        d.polygon([(cx - 6, cy + 10), (cx - 12, cy + 16), (cx - 4, cy + 12)],
                  fill=RED)
        d.polygon([(cx + 6, cy + 10), (cx + 12, cy + 16), (cx + 4, cy + 12)],
                  fill=RED)
        d.polygon([(cx - 4, cy + 12), (cx + 4, cy + 12), (cx, cy + 20)],
                  fill=(255, 196, 0))
    elif kind == "ballot":
        d.rectangle([cx - 14, cy - 4, cx + 14, cy + 14], outline=INK, width=2)
        d.line([cx - 8, cy - 4, cx + 8, cy - 4], fill=INK, width=2)
        d.polygon([(cx - 6, cy - 16), (cx + 6, cy - 16), (cx + 4, cy - 4),
                   (cx - 4, cy - 4)], fill=(46, 95, 163))
    elif kind == "flask":
        d.polygon([(cx - 4, cy - 16), (cx + 4, cy - 16), (cx + 4, cy - 4),
                   (cx + 14, cy + 14), (cx - 14, cy + 14), (cx - 4, cy - 4)],
                  outline=INK, width=2)
        d.polygon([(cx - 10, cy + 4), (cx + 10, cy + 4), (cx + 12, cy + 12),
                   (cx - 12, cy + 12)], fill=(30, 122, 76))
    elif kind == "chart":
        d.line([cx - 16, cy + 14, cx + 16, cy + 14], fill=INK, width=2)
        d.line([cx - 16, cy + 14, cx - 16, cy - 16], fill=INK, width=2)
        d.line([cx - 14, cy - 10, cx - 4, cy - 2, cx + 4, cy - 6,
                cx + 14, cy + 10], fill=RED, width=3)
        d.polygon([(cx + 8, cy + 4), (cx + 16, cy + 4), (cx + 14, cy + 12)],
                  fill=RED)
    elif kind == "chip":
        d.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], fill=INK)
        d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], outline=(255, 255, 255), width=2)
        for i in (-8, 0, 8):
            d.line([cx + i, cy - 16, cx + i, cy - 10], fill=INK, width=2)
            d.line([cx + i, cy + 10, cx + i, cy + 16], fill=INK, width=2)
            d.line([cx - 16, cy + i, cx - 10, cy + i], fill=INK, width=2)
            d.line([cx + 10, cy + i, cx + 16, cy + i], fill=INK, width=2)
    elif kind == "tag":
        d.polygon([(cx - 14, cy - 8), (cx + 4, cy - 16), (cx + 16, cy - 4),
                   (cx + 16, cy + 8), (cx - 2, cy + 16), (cx - 14, cy + 4)],
                  outline=(138, 109, 0), width=2)
        d.ellipse([cx + 8, cy - 6, cx + 12, cy - 2], outline=(138, 109, 0), width=2)
    elif kind == "gauge":
        d.arc([cx - 14, cy - 12, cx + 14, cy + 16], 180, 360, fill=INK, width=2)
        d.line([cx, cy + 2, cx + 8, cy - 10], fill=RED, width=3)
        d.ellipse([cx - 3, cy - 1, cx + 3, cy + 5], fill=INK)
        d.line([cx - 14, cy + 2, cx + 14, cy + 2], fill=INK, width=2)
    elif kind == "laptop":
        d.rectangle([cx - 14, cy - 12, cx + 14, cy + 6], outline=INK, width=2)
        d.line([cx - 18, cy + 10, cx + 18, cy + 10], fill=INK, width=3)
        d.line([cx - 14, cy + 6, cx - 18, cy + 10], fill=INK, width=2)
        d.line([cx + 14, cy + 6, cx + 18, cy + 10], fill=INK, width=2)
        d.line([cx - 8, cy - 6, cx - 2, cy - 6], fill=(178, 34, 34), width=2)
        d.line([cx - 8, cy - 2, cx + 4, cy - 2], fill=(178, 34, 34), width=2)
    elif kind == "bolt":
        d.polygon([(cx + 4, cy - 18), (cx - 8, cy + 2), (cx - 1, cy + 2),
                   (cx - 4, cy + 18), (cx + 8, cy - 2), (cx + 1, cy - 2)],
                  fill=(255, 196, 0), outline=(138, 109, 0))
    elif kind == "tunnel":
        d.arc([cx - 14, cy - 12, cx + 14, cy + 16], 180, 360, fill=INK, width=3)
        d.line([cx - 14, cy + 2, cx - 14, cy + 14], fill=INK, width=3)
        d.line([cx + 14, cy + 2, cx + 14, cy + 14], fill=INK, width=3)
        d.arc([cx - 12, cy + 10, cx - 2, cy + 18], 0, 180, fill=(46, 95, 163), width=2)
        d.arc([cx + 2, cy + 10, cx + 12, cy + 18], 0, 180, fill=(46, 95, 163), width=2)
    elif kind == "coins":
        d.ellipse([cx - 12, cy - 14, cx + 2, cy + 0], outline=(138, 109, 0), width=2)
        d.ellipse([cx - 4, cy - 6, cx + 10, cy + 8], outline=(138, 109, 0), width=2)
        d.ellipse([cx - 12, cy + 2, cx + 2, cy + 16], outline=(138, 109, 0), width=2)
        d.line([cx - 5, cy - 7, cx - 5, cy - 13], fill=(138, 109, 0), width=2)
    elif kind == "cricket":
        d.line([cx - 12, cy + 14, cx + 8, cy - 12], fill=(140, 100, 40), width=5)
        d.ellipse([cx + 8, cy + 6, cx + 18, cy + 16], fill=RED)
    elif kind == "trophy":
        d.polygon([(cx - 8, cy - 14), (cx + 8, cy - 14), (cx + 6, cy + 2),
                   (cx - 6, cy + 2)], fill=(212, 160, 23))
        d.arc([cx - 16, cy - 14, cx - 6, cy - 2], 90, 270, fill=(212, 160, 23), width=3)
        d.arc([cx + 6, cy - 14, cx + 16, cy - 2], 270, 90, fill=(212, 160, 23), width=3)
        d.line([cx, cy + 2, cx, cy + 10], fill=(212, 160, 23), width=3)
        d.line([cx - 8, cy + 12, cx + 8, cy + 12], fill=(212, 160, 23), width=3)
    elif kind == "cross":
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=RED, width=2)
        d.rectangle([cx - 3, cy - 10, cx + 3, cy + 10], fill=RED)
        d.rectangle([cx - 10, cy - 3, cx + 10, cy + 3], fill=RED)


# ---- simplified world map --------------------------------------------
CONTINENTS = [
    [(18, 42), (52, 28), (96, 30), (112, 44), (104, 66), (84, 84),
     (58, 86), (34, 72), (16, 58)],
    [(88, 108), (112, 104), (128, 120), (124, 150), (110, 178),
     (96, 160), (86, 132)],
    [(142, 34), (168, 26), (182, 38), (176, 58), (158, 62), (144, 50)],
    [(146, 72), (180, 70), (196, 88), (188, 118), (172, 146),
     (156, 128), (144, 100)],
    [(184, 30), (286, 26), (294, 50), (282, 78), (250, 92), (224, 84),
     (206, 66), (188, 52)],
    [(238, 150), (272, 146), (282, 162), (268, 178), (242, 174)],
]
# (x, y) in map-box coordinates, roughly where the stories happened.
DOTS = [(168, 92), (190, 86), (200, 80), (162, 76), (146, 52), (150, 36),
        (252, 58), (258, 128), (238, 72), (228, 80), (138, 96), (166, 124),
        (70, 58), (78, 72)]


def draw_map(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=MAP_BG, outline=BORDER)
    d.text((x0 + 10, y0 + 8), "WHERE IT HAPPENED",
           font=F_BOLD(11), fill=INK)
    ox, oy = x0, y0 + 26
    for poly in CONTINENTS:
        pts = [(ox + round(px * 0.96), oy + round(py * 0.85))
               for px, py in poly]
        d.polygon(pts, fill=LAND)
    for dx, dy in DOTS:
        mx, my = ox + round(dx * 0.96), oy + round(dy * 0.85)
        d.ellipse([mx - 4, my - 4, mx + 4, my + 4],
                  fill=DOT, outline=(255, 255, 255), width=1)
    d.text((x0 + 10, y0 + h - 18),
           "Red dots mark where the day's stories happened.",
           font=F_REG(9), fill=MUTED)


def draw_panel(d, x, y, w, h, num, region, headline, caption, icon):
    color = REGION_COLORS[region]
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=BORDER)
    d.rectangle([x, y, x + w, y + 3], fill=color)
    # icon box, top-left, with number badge
    ix, iy = x + 8, y + 10
    d.rectangle([ix, iy, ix + 44, iy + 44], fill=(242, 238, 228),
                outline=BORDER)
    draw_icon(d, icon, ix + 22, iy + 22)
    d.ellipse([ix - 6, iy - 6, ix + 18, iy + 18], fill=NAVY)
    d.text((ix + 6, iy + 7), str(num), font=F_BOLD(10),
           fill=(255, 255, 255), anchor="mm")
    # region tag
    d.text((x + 60, y + 10), region, font=F_BOLD(9), fill=color)
    # headline, up to 2 lines
    hl = fit_lines(d, headline, F_BOLD(13), w - 68, 2)
    hy = y + 26
    for line in hl:
        d.text((x + 60, hy), line, font=F_BOLD(13), fill=INK)
        hy += 15
    # caption, up to 3 lines
    cap = fit_lines(d, caption, F_REG(11), w - 16, 3)
    cy = y + 62
    for line in cap:
        d.text((x + 8, cy), line, font=F_REG(11), fill=(48, 52, 62))
        cy += 14


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- header ------------------------------------------------------
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.text((W // 2, 10), "THE WORLD IN ONE PAGE",
           font=F_BOLD(11), fill=(200, 205, 220), anchor="ma")
    d.text((W // 2, 28), "TARIFFS, TANKERS & THE CHIP ROUT",
           font=F_TITLE(33), fill=(255, 255, 255), anchor="ma")
    d.text((W // 2, 70),
           "WEDNESDAY, 25 NOVEMBER 2026  \u2022  36 STORIES  \u2022  8 REGIONS",
           font=F_BOLD(14), fill=(255, 196, 0), anchor="ma")
    d.rectangle([0, 96, W, 99], fill=RED)

    # ---- 18 panels: 3 cols x 6 rows ----------------------------------
    px, py = 10, 108
    pw, ph, gx, gy = 224, 128, 8, 8
    for i, (region, headline, caption, icon) in enumerate(PANELS):
        col, row = i % 3, i // 3
        draw_panel(d, px + col * (pw + gx), py + row * (ph + gy),
                   pw, ph, i + 1, region, headline, caption, icon)

    # ---- right column -------------------------------------------------
    rx, rw = 712, 302
    draw_map(d, rx, 108, rw, 210)
    # region counts
    cy0 = 326
    d.rectangle([rx, cy0, rx + rw, cy0 + 152], fill=PANEL, outline=BORDER)
    d.text((rx + 10, cy0 + 8), "BY REGION \u2014 36 STORIES",
           font=F_BOLD(11), fill=INK)
    for j, (name, count) in enumerate(REGION_COUNTS):
        ry = cy0 + 30 + j * 15
        d.rectangle([rx + 10, ry + 2, rx + 20, ry + 12],
                    fill=REGION_COLORS[name])
        d.text((rx + 26, ry), name, font=F_REG(10), fill=INK)
        d.text((rx + rw - 10, ry), str(count), font=F_BOLD(10),
               fill=INK, anchor="ra")
    # the rest of the day
    ly0 = 486
    d.rectangle([rx, ly0, rx + rw, ly0 + 374], fill=PANEL, outline=BORDER)
    d.text((rx + 10, ly0 + 8), "THE REST OF THE DAY \u2014 18 MORE STORIES",
           font=F_BOLD(11), fill=INK)
    d.line([rx + 10, ly0 + 26, rx + rw - 10, ly0 + 26], fill=BORDER, width=1)
    for j, (num, region, text) in enumerate(REST):
        ry = ly0 + 34 + j * 18
        d.text((rx + 10, ry), num + ".", font=F_BOLD(10), fill=RED)
        d.text((rx + 32, ry), region + " \u2014 " + text,
               font=F_REG(9), fill=(48, 52, 62))

    # ---- timeline strip: day parts only, no clock times ---------------
    ty = 920
    d.text((10, ty), "HOW THE DAY UNFOLDED", font=F_BOLD(11), fill=INK)
    seg_w = 244
    for j, (label, sub) in enumerate(DAY_PARTS):
        sx = 10 + j * (seg_w + 8)
        d.rounded_rectangle([sx, ty + 18, sx + seg_w, ty + 46],
                            radius=6, fill=NAVY)
        d.text((sx + seg_w // 2, ty + 22), label, font=F_BOLD(11),
               fill=(255, 255, 255), anchor="ma")
        d.text((sx + seg_w // 2, ty + 34), sub, font=F_REG(9),
               fill=(200, 205, 220), anchor="ma")
        if j < 3:
            ax = sx + seg_w + 1
            d.text((ax, ty + 26), "\u2192", font=F_BOLD(14), fill=RED)

    # ---- footer -------------------------------------------------------
    d.line([10, 982, W - 10, 982], fill=BORDER, width=1)
    d.text((W // 2, 990),
           "All 36 stories were reported on Wednesday, 25 November 2026.",
           font=F_REG(12), fill=MUTED, anchor="ma")
    return img


def main():
    img = build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "."
    here = os.path.dirname(os.path.abspath(__file__))
    for path in {os.path.join(out_dir, OUT_NAME),
                 os.path.join(here, OUT_NAME)}:
        img.save(path, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
