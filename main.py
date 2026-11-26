#!/usr/bin/env python3
"""News image for make.fun competition news-image-20261125 (entry v7).

Defensive rewrite: the v6 build crashed in the grader sandbox (exit code 1),
so every risky Pillow call is guarded. Standard library + Pillow only, no
network, no timestamps, no randomness - the same run always writes the same
PNG bytes.

Content: only the 36 verified real stories reported on Wednesday,
25 November 2026 (18 drawn panels + 18 listed). No invented stories,
numbers, or clock times; the timeline uses day-part labels only.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024

TITLE = "TARIFFS, TANKERS & THE CHIP ROUT"
SUBTITLE = "WEDNESDAY, 25 NOVEMBER 2026  |  36 STORIES  |  8 REGIONS"
FOOTER = "All 36 stories were reported on Wednesday, 25 November 2026."
SOURCES = ("SOURCES: Standard Topic, Reuters, Investopedia, UN News, "
           "Wikipedia, Mykhel, Day Lila")

NAVY = (15, 42, 68)
RED = (192, 57, 43)
INK = (20, 20, 20)
GREY = (90, 90, 90)
LIGHT = (247, 245, 239)
PANEL_BG = (255, 255, 255)
PANEL_LINE = (205, 205, 200)
MAP_BG = (214, 228, 235)
LAND = (120, 160, 110)

REGION_COLORS = {
    "MIDDLE EAST": (176, 58, 46),
    "EUROPE": (31, 97, 141),
    "ASIA-PACIFIC": (20, 143, 119),
    "MARKETS": (125, 60, 152),
    "TECH": (46, 134, 193),
    "SPORT": (34, 153, 84),
    "AFRICA": (183, 149, 11),
    "AMERICAS": (202, 111, 30),
}

# (region, headline, one-line caption, icon kind)
PANELS = [
    ("MIDDLE EAST", "CAIRO TANKER FIRE",
     "Fuel tanker overturns on Giza Ring Road; 31 killed", "flame"),
    ("MIDDLE EAST", "RIYADH DRONE STRIKE",
     "Houthi drone hits tower; 11 injured, incl. 2 Indians", "drone"),
    ("MIDDLE EAST", "HORMUZ CLAIM DISPUTED",
     "Iran claims mines hit tankers; US disputes it", "ship"),
    ("EUROPE", "UKRAINE STRIKES NEAR BENGHAZI",
     "Russian ships hit near Libya; 2 soldiers killed", "strike"),
    ("ASIA-PACIFIC", "SHENZHOU-24 LIFTS OFF",
     "Pakistan's first astronaut aboard, Zeeshan Ali", "rocket"),
    ("EUROPE", "SPAIN TO THE POLLS",
     "Snap election Sunday; PSOE trails PP-led bloc", "vote"),
    ("EUROPE", "30+ NATIONS TO RUSSIA",
     "Urge halt to chemical agents in Ukraine", "globe"),
    ("MARKETS", "KOSPI -5.9%",
     "Chip rout: SK Hynix -9.8%, Samsung -9.1%", "chart"),
    ("TECH", "NVIDIA -5.9%",
     "AI selloff resumes; Anthropic -6.5%", "chip"),
    ("MARKETS", "TARIFFS LOOM",
     "US plans rises on China and 15 partners", "tariff"),
    ("MARKETS", "US INFLATION IN LINE",
     "Oct PCE +3.8% y/y, +0.3% m/m, as expected", "gauge"),
    ("TECH", "DELL FALLS DESPITE RECORD",
     "Shares fall despite $132.3B AI backlog", "laptop"),
    ("EUROPE", "UK ENERGY CAP +26%",
     "Cap rises to 2,166 pounds in January", "bolt"),
    ("ASIA-PACIFIC", "JAVA MINE FLOOD",
     "Flooded gold mine: 9 dead, 17 trapped", "mine"),
    ("ASIA-PACIFIC", "BANGLADESH WAGE +36%",
     "Garment minimum wage up to 17,000 taka", "wage"),
    ("SPORT", "204 OFF 53 BALLS",
     "Sooryavanshi smashes 204, 28 sixes - records", "bat"),
    ("SPORT", "SENEGAL CHAMPIONS AGAIN",
     "CAS restores Senegal as AFCON champions", "trophy"),
    ("AFRICA", "EBOLA TEAMS EVACUATED",
     "DR Congo health workers evacuated in Ituri", "cross"),
]

# (region, one-line headline) for "THE REST OF THE DAY"
LISTED = [
    ("AMERICAS", "Trump: Iran war funding secured through January"),
    ("MIDDLE EAST", "Iran claims downing of US MQ-9 drone over Hormuz"),
    ("AMERICAS", "US Coast Guard recovers 6 dead from Cessna crash off Mississippi"),
    ("AMERICAS", "US DOJ charges 800+ in global anti-scam crackdown"),
    ("ASIA-PACIFIC", "Australia and Solomon Islands sign security treaty"),
    ("MIDDLE EAST", "Iraq PM takes federal control of Kurdistan oil exports"),
    ("AFRICA", "Congo to halt cobalt exports from 30 November"),
    ("AFRICA", "HIV funding fell 18% in a year, UNAIDS says"),
    ("EUROPE", "Ukraine faces 70B euro funding gap for 2027"),
    ("EUROPE", "Rights court: Poland, Latvia pushbacks inhumane"),
    ("AMERICAS", "US judge bars Trump from punishing ICC-linked groups"),
    ("TECH", "Huawei convicted in US court"),
    ("ASIA-PACIFIC", "China and Cambodia begin Golden Dragon drills"),
    ("ASIA-PACIFIC", "Sheikh Hasina sets Dec 16 return from exile"),
    ("SPORT", "Ben Stokes registers for IPL 2027 auction"),
    ("SPORT", "East Bengal beat Al Hussein 1-0, Jeakson Singh 87th minute"),
    ("MARKETS", "Bitcoin near $59,300; Brent near $90"),
    ("MIDDLE EAST", "UN fears new Israeli attacks in Gaza; Yemen aid chief warns"),
]

DAY_PARTS = ["ASIA MORNING", "EUROPE MIDDAY", "AMERICAS AFTERNOON", "DAY ENDS"]

REGION_ORDER = ["MIDDLE EAST", "EUROPE", "ASIA-PACIFIC", "MARKETS",
                "TECH", "SPORT", "AFRICA", "AMERICAS"]


# ---------------------------------------------------------------- fonts
def load_font(size, bold=False):
    """Font loading that never raises: DejaVu paths, common locations,
    then the built-in default font as the last resort."""
    names = []
    if bold:
        names.append("DejaVuSans-Bold.ttf")
    names.append("DejaVuSans.ttf")
    candidates = []
    for name in names:
        candidates.append(os.path.join("/usr/share/fonts/truetype/dejavu", name))
        candidates.append(os.path.join("/usr/share/fonts", name))
        candidates.append(name)
    candidates.append("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
    candidates.append("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


# ---------------------------------------------------------------- text
def text_width(draw, text, font):
    """Width of text in pixels. Tries textlength, then getlength, then
    getsize, then a character-count estimate - never raises."""
    try:
        return int(draw.textlength(text, font=font))
    except Exception:
        pass
    try:
        return int(font.getlength(text))
    except Exception:
        pass
    try:
        size = font.getsize(text)
        return int(size[0])
    except Exception:
        pass
    return int(len(text) * 6)


def draw_centered(draw, cx, y, text, font, fill):
    """Draw text centred on cx without using anchor= (unsupported in some
    Pillow builds / environments)."""
    w = text_width(draw, text, font)
    draw.text((cx - w // 2, y), text, font=font, fill=fill)


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap into lines that fit max_width. Never raises."""
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = current + " " + word
        if text_width(draw, trial, font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


# ---------------------------------------------------------------- icons
def draw_icon(draw, x, y, kind, color):
    """Simple drawn icon inside a 30x30 box at (x, y). Primitives only."""
    s = 30
    if kind == "flame":
        draw.polygon([(x + 15, y + 2), (x + 24, y + 16), (x + 20, y + 26),
                      (x + 10, y + 26), (x + 6, y + 16)], fill=color)
        draw.ellipse([x + 11, y + 16, x + 19, y + 24], fill=(255, 200, 60))
    elif kind == "drone":
        draw.rectangle([x + 10, y + 12, x + 20, y + 18], fill=color)
        draw.ellipse([x + 2, y + 6, x + 10, y + 12], outline=color, width=2)
        draw.ellipse([x + 20, y + 6, x + 28, y + 12], outline=color, width=2)
        draw.ellipse([x + 2, y + 18, x + 10, y + 24], outline=color, width=2)
        draw.ellipse([x + 20, y + 18, x + 28, y + 24], outline=color, width=2)
    elif kind == "ship":
        draw.polygon([(x + 3, y + 18), (x + 27, y + 18), (x + 22, y + 26),
                      (x + 8, y + 26)], fill=color)
        draw.rectangle([x + 13, y + 6, x + 17, y + 18], fill=color)
        draw.polygon([(x + 17, y + 7), (x + 25, y + 14), (x + 17, y + 14)],
                     fill=(200, 200, 200))
    elif kind == "strike":
        draw.polygon([(x + 15, y + 2), (x + 20, y + 12), (x + 27, y + 13),
                      (x + 21, y + 18), (x + 23, y + 26), (x + 15, y + 21),
                      (x + 7, y + 26), (x + 9, y + 18), (x + 3, y + 13),
                      (x + 10, y + 12)], fill=color)
    elif kind == "rocket":
        draw.polygon([(x + 15, y + 2), (x + 21, y + 12), (x + 19, y + 24),
                      (x + 11, y + 24), (x + 9, y + 12)], fill=color)
        draw.ellipse([x + 12, y + 10, x + 18, y + 16], fill=(255, 255, 255))
        draw.polygon([(x + 15, y + 24), (x + 19, y + 29), (x + 11, y + 29)],
                     fill=(255, 160, 40))
    elif kind == "vote":
        draw.rectangle([x + 5, y + 5, x + 25, y + 25], outline=color, width=2)
        draw.line([x + 9, y + 15, x + 13, y + 20, x + 22, y + 9],
                  fill=color, width=3)
    elif kind == "globe":
        draw.ellipse([x + 3, y + 3, x + 27, y + 27], outline=color, width=2)
        draw.line([x + 15, y + 3, x + 15, y + 27], fill=color, width=1)
        draw.line([x + 3, y + 15, x + 27, y + 15], fill=color, width=1)
    elif kind == "chart":
        draw.line([x + 4, y + 26, x + 26, y + 26], fill=color, width=2)
        draw.line([x + 6, y + 20, x + 12, y + 14, x + 18, y + 17, x + 25, y + 6],
                  fill=color, width=3)
    elif kind == "chip":
        draw.rectangle([x + 8, y + 8, x + 22, y + 22], fill=color)
        for px in (12, 18):
            draw.line([x + px, y + 2, x + px, y + 8], fill=color, width=2)
            draw.line([x + px, y + 22, x + px, y + 28], fill=color, width=2)
        for py in (12, 18):
            draw.line([x + 2, y + py, x + 8, y + py], fill=color, width=2)
            draw.line([x + 22, y + py, x + 28, y + py], fill=color, width=2)
    elif kind == "tariff":
        draw.rectangle([x + 4, y + 8, x + 26, y + 24], outline=color, width=2)
        draw.line([x + 4, y + 13, x + 26, y + 13], fill=color, width=1)
        draw.text((x + 9, y + 15), "%", font=load_font(11, bold=True), fill=color)
    elif kind == "gauge":
        draw.ellipse([x + 3, y + 6, x + 27, y + 26], outline=color, width=2)
        draw.line([x + 15, y + 16, x + 21, y + 9], fill=color, width=2)
        draw.ellipse([x + 13, y + 14, x + 17, y + 18], fill=color)
    elif kind == "laptop":
        draw.rectangle([x + 6, y + 7, x + 24, y + 20], outline=color, width=2)
        draw.rectangle([x + 3, y + 20, x + 27, y + 24], fill=color)
    elif kind == "bolt":
        draw.polygon([(x + 17, y + 3), (x + 10, y + 16), (x + 15, y + 16),
                      (x + 12, y + 27), (x + 20, y + 13), (x + 15, y + 13)],
                     fill=color)
    elif kind == "mine":
        draw.polygon([(x + 4, y + 12), (x + 15, y + 4), (x + 26, y + 12),
                      (x + 22, y + 26), (x + 8, y + 26)], fill=color)
        draw.ellipse([x + 12, y + 13, x + 18, y + 19], fill=(255, 255, 255))
    elif kind == "wage":
        draw.ellipse([x + 4, y + 4, x + 26, y + 26], outline=color, width=2)
        draw.text((x + 11, y + 8), "$", font=load_font(13, bold=True), fill=color)
    elif kind == "bat":
        draw.rectangle([x + 6, y + 20, x + 24, y + 26], fill=color)
        draw.line([x + 15, y + 20, x + 15, y + 4], fill=color, width=4)
        draw.ellipse([x + 11, y + 3, x + 19, y + 11], fill=color)
    elif kind == "trophy":
        draw.polygon([(x + 10, y + 4), (x + 20, y + 4), (x + 18, y + 18),
                      (x + 12, y + 18)], fill=color)
        draw.rectangle([x + 8, y + 20, x + 22, y + 24], fill=color)
        draw.rectangle([x + 6, y + 24, x + 24, y + 27], fill=color)
    elif kind == "cross":
        draw.rectangle([x + 12, y + 4, x + 18, y + 26], fill=color)
        draw.rectangle([x + 4, y + 11, x + 26, y + 17], fill=color)
    else:
        draw.ellipse([x + 6, y + 6, x + 24, y + 24], outline=color, width=2)


# ---------------------------------------------------------------- map
def draw_map(draw, x, y, w, h):
    """Simplified world map: plain rectangles/ellipses as landmasses,
    red dots at story locations. No external data."""
    draw.rectangle([x, y, x + w, y + h], fill=MAP_BG)
    # North America
    draw.ellipse([x + 8, y + 18, x + 78, y + 62], fill=LAND)
    # South America
    draw.ellipse([x + 62, y + 78, x + 100, y + 128], fill=LAND)
    # Europe
    draw.ellipse([x + 138, y + 22, x + 178, y + 58], fill=LAND)
    # Africa
    draw.ellipse([x + 140, y + 62, x + 182, y + 112], fill=LAND)
    # Middle East / Asia
    draw.ellipse([x + 180, y + 24, x + 268, y + 70], fill=LAND)
    # SE Asia / Australia
    draw.ellipse([x + 246, y + 96, x + 292, y + 126], fill=LAND)
    dots = [
        (x + 168, y + 52),   # Cairo / Riyadh / Hormuz
        (x + 160, y + 40),   # Europe
        (x + 235, y + 48),   # China / Shenzhou
        (x + 255, y + 78),   # Java / Bangladesh
        (x + 162, y + 88),   # DR Congo
        (x + 45, y + 45),    # Americas
        (x + 80, y + 100),   # South America
        (x + 275, y + 105),  # Australia / Solomon Islands
    ]
    for (dx, dy) in dots:
        draw.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=RED,
                     outline=(255, 255, 255), width=1)


# ---------------------------------------------------------------- full build
def build_full():
    img = Image.new("RGB", (W, H), LIGHT)
    draw = ImageDraw.Draw(img)

    f_title = load_font(33, bold=True)
    f_sub = load_font(15, bold=True)
    f_section = load_font(14, bold=True)
    f_tag = load_font(10, bold=True)
    f_head = load_font(13, bold=True)
    f_cap = load_font(11, bold=False)
    f_list = load_font(11, bold=False)
    f_list10 = load_font(10, bold=False)
    f_small = load_font(10, bold=False)
    f_num = load_font(12, bold=True)

    # Header band
    draw.rectangle([0, 0, W, 78], fill=NAVY)
    draw_centered(draw, W // 2, 10, TITLE, f_title, (255, 255, 255))
    draw_centered(draw, W // 2, 50, SUBTITLE, f_sub, (255, 210, 90))

    # ---- 18 drawn panels: 3 cols x 6 rows
    gx, gy = 10, 86
    pw, ph, gap = 222, 124, 8
    for i, (region, headline, caption, kind) in enumerate(PANELS):
        col = i % 3
        row = i // 3
        px = gx + col * (pw + gap)
        py = gy + row * (ph + gap)
        color = REGION_COLORS.get(region, NAVY)
        draw.rectangle([px, py, px + pw, py + ph], fill=PANEL_BG,
                       outline=PANEL_LINE, width=1)
        draw.rectangle([px, py, px + pw, py + 5], fill=color)
        # number badge
        cx, cy = px + 16, py + 22
        draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=color)
        num = str(i + 1)
        nw = text_width(draw, num, f_num)
        draw.text((cx - nw // 2, cy - 8), num, font=f_num,
                  fill=(255, 255, 255))
        # region tag
        draw.text((px + 32, py + 14), region, font=f_tag, fill=color)
        # headline (up to 2 lines)
        lines = wrap_text(draw, headline, f_head, pw - 16)
        hy = py + 40
        for line in lines[:2]:
            draw.text((px + 8, hy), line, font=f_head, fill=INK)
            hy += 16
        # caption (up to 2 lines)
        clines = wrap_text(draw, caption, f_cap, pw - 46)
        cy2 = py + 76
        for line in clines[:2]:
            draw.text((px + 8, cy2), line, font=f_cap, fill=GREY)
            cy2 += 14
        # icon, bottom right
        draw_icon(draw, px + pw - 38, py + ph - 36, kind, color)

    # ---- right column
    rx = 700
    rw = 314
    # Where it happened
    draw.text((rx, 86), "WHERE IT HAPPENED", font=f_section, fill=NAVY)
    draw_map(draw, rx, 108, rw, 130)
    # By region (two columns of four, to leave room for the 18-item list)
    by_y = 250
    draw.text((rx, by_y), "BY REGION", font=f_section, fill=NAVY)
    counts = {}
    for region, _h, _c, _k in PANELS:
        counts[region] = counts.get(region, 0) + 1
    for region, _h in LISTED:
        counts[region] = counts.get(region, 0) + 1
    for idx, region in enumerate(REGION_ORDER):
        col_x = rx + (idx // 4) * 160
        ry = by_y + 24 + (idx % 4) * 20
        n = counts.get(region, 0)
        color = REGION_COLORS.get(region, NAVY)
        draw.rectangle([col_x, ry + 2, col_x + 10, ry + 12], fill=color)
        draw.text((col_x + 16, ry), region, font=f_list, fill=INK)
        cnt = str(n)
        cw = text_width(draw, cnt, f_list)
        draw.text((col_x + 150 - cw, ry), cnt, font=f_list, fill=INK)
    # The rest of the day (one line each, 10pt so all 18 fit above the strip)
    ly = by_y + 116
    draw.text((rx, ly), "THE REST OF THE DAY", font=f_section, fill=NAVY)
    draw.text((rx + 178, ly + 2), "18 MORE STORIES", font=f_tag, fill=RED)
    ly += 26
    for j, (region, headline) in enumerate(LISTED):
        num = str(19 + j)
        color = REGION_COLORS.get(region, NAVY)
        draw.text((rx, ly), num + ".", font=f_list10, fill=color)
        text = region + " - " + headline
        lines = wrap_text(draw, text, f_list10, rw - 28)
        for line in lines[:2]:
            draw.text((rx + 28, ly), line, font=f_list10, fill=INK)
            ly += 12
        ly += 2

    # ---- bottom timeline strip (day-part labels only, no clock times)
    ty = 872
    draw.rectangle([10, ty, W - 10, ty + 52], fill=NAVY)
    seg_w = (W - 20) // 4
    for k, part in enumerate(DAY_PARTS):
        cx = 10 + seg_w * k + seg_w // 2
        draw_centered(draw, cx, ty + 18, part, f_section, (255, 255, 255))
        if k > 0:
            draw.line([10 + seg_w * k, ty + 10, 10 + seg_w * k, ty + 42],
                      fill=(255, 255, 255), width=1)

    # ---- footer
    draw_centered(draw, W // 2, 938, FOOTER, f_cap, INK)
    draw_centered(draw, W // 2, 956, SOURCES, f_small, GREY)
    draw_centered(draw, W // 2, 978, "TARIFFS, TANKERS & THE CHIP ROUT  |  "
                  "25 NOVEMBER 2026", f_small, GREY)
    return img


# ---------------------------------------------------------------- fallback
def build_fallback():
    """Minimal plain layout, default font only, no fancy calls.
    Used if anything in the full build raises."""
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    draw.rectangle([0, 0, W, 60], fill=NAVY)
    draw.text((10, 10), TITLE, font=font, fill=(255, 255, 255))
    draw.text((10, 30), SUBTITLE, font=font, fill=(255, 210, 90))
    y = 75
    n = 0
    for region, headline, _caption, _kind in PANELS:
        n += 1
        draw.text((10, y), str(n) + ". " + region + " - " + headline,
                  font=font, fill=INK)
        y += 16
    for region, headline in LISTED:
        n += 1
        draw.text((10, y), str(n) + ". " + region + " - " + headline,
                  font=font, fill=INK)
        y += 16
    draw.text((10, 990), FOOTER, font=font, fill=INK)
    return img


# ---------------------------------------------------------------- main
def main():
    try:
        img = build_full()
    except Exception as exc:
        print("full build failed (%s); using fallback layout" % (exc,))
        try:
            img = build_fallback()
        except Exception as exc2:
            print("fallback build failed: %s" % (exc2,))
            return 1

    targets = [os.path.join(os.getcwd(), "entry.png")]
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    if out_dir:
        targets.append(os.path.join(out_dir, "entry.png"))

    saved = 0
    for path in targets:
        try:
            img.save(path, format="PNG")
            saved += 1
            print("saved " + path)
        except Exception as exc:
            print("save failed for %s: %s" % (path, exc))

    if saved > 0:
        return 0
    print("no image could be saved")
    return 1


if __name__ == "__main__":
    sys.exit(main())
