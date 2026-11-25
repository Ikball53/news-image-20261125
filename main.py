"""News image for Wednesday 25 November 2026.

Draws a one-page newspaper front page with PIL: a dark header naming
the day, a title line with the three headline stories, 21 illustrated
scene panels, a dense list of the remaining 29 stories, a UTC timeline
strip and a six-story ticker. Every story comes from the verified list
for 25 November 2026; only two clock times appear (00:18 and 03:56 GMT).

Writes entry.png into /output when that directory exists, otherwise
into the current directory. Deterministic: same bytes every run.
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
CREAM = (247, 242, 231)
PAPER = (255, 253, 247)
INK = (24, 28, 38)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
RED_SOFT = (214, 90, 70)
GREY = (96, 100, 110)
RULE = (196, 188, 172)
GOLD = (176, 132, 32)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_REG = FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"

HEADER_TEXT = "WEDNESDAY, 25 NOVEMBER 2026 \u00b7 50 STORIES \u00b7 10 REGIONS"
TITLE_A = "US tariffs on 14 economies  \u00b7  Pakistan's first astronaut boards Tiangong"
TITLE_B = "KOSPI -6.2% as Asian chip rout deepens"

# Region accent colours.
ME = (179, 64, 42)
EU = (46, 94, 140)
AF = (122, 90, 31)
AS = (47, 125, 79)
AM = (106, 63, 160)
UK = (140, 47, 94)
SC = (15, 118, 110)

# (icon kind, region colour, caption) — 21 illustrated scenes.
PANELS = [
    ("ship", ME, "Hormuz: two oil tankers hit by mines, on fire"),
    ("flame", ME, "Houthis hit Saudi Ras Tanura refinery; fires"),
    ("blast", EU, "Russian strike on Odesa kills 2, injures 3"),
    ("drone", EU, "Ukraine drones hit two Rosneft refineries"),
    ("shield", AF, "Sudan RSF drone strikes kill 19 civilians"),
    ("stadium", AF, "Senegal reinstated as AFCON champions"),
    ("rocket", AS, "Pakistan's first astronaut boards Tiangong"),
    ("chart", AS, "KOSPI -6.2%; Samsung -9.9%, SK Hynix -11.1%"),
    ("hockey", AS, "India women beat Japan 4-0 in hockey"),
    ("cricket", AS, "Sooryavanshi 204 off 53 balls, 28 sixes"),
    ("chess", AS, "Gukesh holds Sindarov to draw, Game 1"),
    ("tariff", AM, "US proposes tariffs on 14 economies"),
    ("market", AM, "Wall Street: S&P -2.2%, Nasdaq -3.2%"),
    ("chip", AM, "Dell record Q3: revenue $54.9bn, AI $22bn"),
    ("court", AM, "Huawei convicted on 10 of 12 counts"),
    ("siege", AM, "Colombia: hostages freed after 17-hour siege"),
    ("shop", UK, "Poundland collapses; 11,000 jobs at risk"),
    ("soccer", UK, "Champions League: Real Madrid 5-1 PSV"),
    ("asteroid", SC, "ESA Hera: first images of Dimorphos crater"),
    ("orbit", SC, "BepiColombo settles into Mercury orbit"),
    ("climate", SC, "Pope Leo XIV: COP31 talks failed to agree"),
]

# The remaining 29 stories, as a dense headline list.
MORE_STORIES = [
    "Houthi drone strike on Riyadh tower injures 11",
    "Israel kills Hamas colonel Abuelouf, wife + 2 children",
    "Knesset advances October 7 inquiry",
    "Putin: Ukraine keeps hitting Russian oil refineries",
    "Poland pushes permanent US military presence",
    "Poland to create no-fly zone after drone incursion",
    "Merz warns Russia wants more than Ukraine",
    "Spain heads to snap election",
    "Ramaphosa wins court battle over impeachment threat",
    "DR Congo Ebola outbreak in Beni",
    "China investigates Shanghai party chief Chen Jining",
    "North Korea expels Swiss diplomat",
    "Solomon Islands and Australia sign security treaty",
    "Australia inflation rises to 4.9%",
    "India women's hockey reaches career-best world No. 5",
    "Ben Stokes registers for IPL 2027 mini-auction",
    "East Bengal 1-0 Al Hussein, ACL Two (Jeakson 87')",
    "Pakistan names Fatima Sana captain for West Indies tour",
    "Sri Lanka Women beat Ireland, win Emerging Trophy",
    "Nvidia -5.9% Tue, -7% Wed; Huang back as CEO Monday",
    "US Oct PCE inflation 3.8% YoY, core 3.3%",
    "Anthropic shares fall below IPO price",
    "US Army destroys lead azide stockpile in Iowa",
    "Argentina enters technical recession",
    "Jayson Tatum 41 pts, Celtics beat Wizards 131-116",
    "Bitcoin ~$58,400; gold -3.2%; Brent $89.73 +1.1%",
    "UK energy price cap to rise 26% in January",
    "NASA Europa Clipper Earth flyby Dec 3 previewed",
    "UN warns HIV gains could unravel",
]

# (label, sublabel) — only the two verified GMT times carry numbers.
TIMELINE = [
    ("00:18 GMT", "Shenzhou-24 launch"),
    ("03:56 GMT", "Tiangong docking"),
    ("MORNING", "Europe: Odesa"),
    ("MIDDAY", "Asia: markets rout"),
    ("AFTERNOON", "Americas: Wall St falls"),
    ("EVENING", "Worldwide: UCL night"),
]

TICKER = [
    "US tariffs on 14 economies",
    "Pakistan's first astronaut boards Tiangong",
    "KOSPI -6.2% in Asian chip rout",
    "Hormuz: two tankers hit by mines",
    "UCL: Real Madrid 5-1 PSV",
    "Wall Street: S&P -2.2%, Nasdaq -3.2%",
]


def load_font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REG
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def wrap_text(text, font, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if font.getlength(trial) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_center(draw, cx, y, text, font, fill):
    width = font.getlength(text)
    draw.text((cx - width / 2, y), text, font=font, fill=fill)


def draw_icon(draw, kind, x0, y0, x1, y1):
    """Simple flat vector pictogram for one scene panel."""
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    s = min(x1 - x0, y1 - y0)
    u = s / 10.0
    dark = (38, 44, 58)
    accent = RED
    blue = (46, 94, 140)
    green = (47, 125, 79)
    gold = GOLD
    if kind == "ship":
        draw.polygon([(cx - 4 * u, cy + u), (cx + 4 * u, cy + u),
                      (cx + 3 * u, cy + 3 * u), (cx - 3 * u, cy + 3 * u)],
                     fill=dark)
        draw.rectangle([cx - 2 * u, cy - 2 * u, cx + 2 * u, cy + u], fill=blue)
        draw.polygon([(cx - 1 * u, cy - 2 * u), (cx - 1 * u, cy - 4 * u),
                      (cx + 2 * u, cy - 2 * u)], fill=accent)
        draw.ellipse([cx + 2 * u, cy - 4 * u, cx + 4 * u, cy - 2 * u],
                     fill=(232, 120, 40))
        draw.line([x0 + u, cy + 4 * u, x1 - u, cy + 4 * u], fill=blue, width=2)
    elif kind == "flame":
        draw.polygon([(cx - 3 * u, cy + 3 * u), (cx - 2 * u, cy - u),
                      (cx - u, cy + u), (cx, cy - 3 * u), (cx + u, cy),
                      (cx + 2 * u, cy - 2 * u), (cx + 3 * u, cy + 3 * u)],
                     fill=(232, 120, 40))
        draw.polygon([(cx - 1.5 * u, cy + 3 * u), (cx, cy), (cx + 1.5 * u, cy + 3 * u)],
                     fill=gold)
        draw.rectangle([x0 + u, cy + 3.5 * u, x1 - u, cy + 4 * u], fill=dark)
    elif kind == "blast":
        for dx, dy, r in [(-2, -1, 1.6), (2, -2, 1.3), (0, 1, 1.8), (-3, 2, 1.1), (3, 1, 1.2)]:
            draw.ellipse([cx + dx * u - r * u, cy + dy * u - r * u,
                          cx + dx * u + r * u, cy + dy * u + r * u],
                         fill=(120, 120, 128))
        draw.polygon([(cx, cy - 4 * u), (cx + u, cy - u), (cx + 3.5 * u, cy - 2 * u),
                      (cx + 1.5 * u, cy + u), (cx + 2.5 * u, cy + 3.5 * u),
                      (cx, cy + 1.5 * u), (cx - 2.5 * u, cy + 3.5 * u),
                      (cx - 1.5 * u, cy + u), (cx - 3.5 * u, cy - 2 * u),
                      (cx - u, cy - u)], fill=gold)
    elif kind == "drone":
        draw.rectangle([cx - 2.5 * u, cy - u, cx + 2.5 * u, cy + u], fill=dark)
        draw.ellipse([cx - 1 * u, cy - 1 * u, cx + 1 * u, cy + 1 * u], fill=accent)
        for sx in (-1, 1):
            draw.line([cx + sx * 2.5 * u, cy, cx + sx * 4 * u, cy - u],
                      fill=dark, width=2)
            draw.ellipse([cx + sx * 4 * u - 1.2 * u, cy - 1.6 * u,
                          cx + sx * 4 * u + 1.2 * u, cy - 0.4 * u], fill=GREY)
    elif kind == "shield":
        draw.polygon([(cx, cy - 3.5 * u), (cx + 3 * u, cy - 2.5 * u),
                      (cx + 3 * u, cy), (cx, cy + 3.5 * u), (cx - 3 * u, cy),
                      (cx - 3 * u, cy - 2.5 * u)], fill=blue)
        draw.line([cx - 1.5 * u, cy, cx - 0.3 * u, cy + 1.5 * u], fill=(255, 255, 255), width=2)
        draw.line([cx - 0.3 * u, cy + 1.5 * u, cx + 1.8 * u, cy - 1.5 * u],
                  fill=(255, 255, 255), width=2)
    elif kind == "stadium":
        draw.ellipse([cx - 4 * u, cy - 2 * u, cx + 4 * u, cy + 3 * u],
                     outline=green, width=3)
        draw.ellipse([cx - 2.5 * u, cy - 1 * u, cx + 2.5 * u, cy + 2 * u],
                     outline=green, width=2)
        draw.line([cx - 4 * u, cy + 1 * u, cx + 4 * u, cy + 1 * u], fill=green, width=2)
        draw.polygon([(cx - 1 * u, cy - 4 * u), (cx + 1 * u, cy - 4 * u),
                      (cx, cy - 2 * u)], fill=gold)
    elif kind == "rocket":
        draw.polygon([(cx, cy - 4 * u), (cx + 1.8 * u, cy - u), (cx + 1.8 * u, cy + 2 * u),
                      (cx - 1.8 * u, cy + 2 * u), (cx - 1.8 * u, cy - u)],
                     fill=dark)
        draw.ellipse([cx - 0.9 * u, cy - 1 * u, cx + 0.9 * u, cy + 1 * u], fill=(180, 220, 240))
        draw.polygon([(cx - 1.8 * u, cy + 2 * u), (cx - 3 * u, cy + 4 * u),
                      (cx - 1 * u, cy + 3 * u)], fill=accent)
        draw.polygon([(cx + 1.8 * u, cy + 2 * u), (cx + 3 * u, cy + 4 * u),
                      (cx + 1 * u, cy + 3 * u)], fill=accent)
        draw.polygon([(cx - 0.8 * u, cy + 2 * u), (cx + 0.8 * u, cy + 2 * u),
                      (cx, cy + 4.5 * u)], fill=(232, 120, 40))
    elif kind == "chart":
        draw.line([x0 + u, cy + 3 * u, x1 - u, cy + 3 * u], fill=dark, width=2)
        draw.line([cx - 4 * u, cy - 2 * u, cx - 2 * u, cy - 1 * u, cx, cy - 3 * u,
                   cx + 2 * u, cy + 1 * u, cx + 4 * u, cy + 3.5 * u],
                  fill=accent, width=3)
        draw.polygon([(cx + 2.8 * u, cy + 3.5 * u), (cx + 4 * u, cy + 3.5 * u),
                      (cx + 4 * u, cy + 2 * u)], fill=accent)
    elif kind == "hockey":
        draw.ellipse([cx - 1.6 * u, cy - 1.6 * u, cx + 1.6 * u, cy + 1.6 * u], fill=(255, 255, 255),
                     outline=dark, width=2)
        draw.line([cx - 4 * u, cy + 2.5 * u, cx + 4 * u, cy - 2.5 * u], fill=(150, 90, 40), width=3)
        draw.line([cx + 2.5 * u, cy - 1.5 * u, cx + 4 * u, cy + 1 * u], fill=(150, 90, 40), width=3)
    elif kind == "cricket":
        draw.ellipse([cx - 1.4 * u, cy - 1.4 * u, cx + 1.4 * u, cy + 1.4 * u], fill=accent,
                     outline=(255, 255, 255), width=1)
        draw.line([cx - 4 * u, cy + 3 * u, cx - 1 * u, cy - 3 * u], fill=(150, 90, 40), width=3)
        draw.rectangle([cx - 1 * u, cy - 4 * u, cx + 4 * u, cy - 3 * u], fill=(150, 90, 40))
    elif kind == "chess":
        draw.rectangle([cx - 3 * u, cy - 3 * u, cx, cy], fill=dark)
        draw.rectangle([cx, cy, cx + 3 * u, cy + 3 * u], fill=dark)
        draw.rectangle([cx, cy - 3 * u, cx + 3 * u, cy], outline=dark, width=2)
        draw.rectangle([cx - 3 * u, cy, cx, cy + 3 * u], outline=dark, width=2)
        draw.ellipse([cx - 1.2 * u, cy - 4.5 * u, cx + 1.2 * u, cy - 2.2 * u], fill=gold)
    elif kind == "tariff":
        draw.rectangle([cx - 3.5 * u, cy - 3 * u, cx + 3.5 * u, cy + 2.5 * u],
                       outline=dark, width=2)
        draw.line([cx - 2.5 * u, cy - 1 * u, cx + 2.5 * u, cy - 1 * u], fill=dark, width=2)
        draw.line([cx - 2.5 * u, cy + 0.5 * u, cx + 1 * u, cy + 0.5 * u], fill=GREY, width=2)
        draw.text((cx + 1 * u, cy + 1 * u), "%", font=load_font(16, True), fill=accent)
    elif kind == "market":
        for i, hgt in enumerate([2, 3.5, 1.5, 4, 2.5]):
            bx = cx - 4 * u + i * 1.7 * u
            draw.rectangle([bx, cy + 3 * u - hgt * u, bx + 1.2 * u, cy + 3 * u],
                           fill=blue if i % 2 == 0 else accent)
        draw.line([cx - 4 * u, cy - 2.5 * u, cx + 4 * u, cy - 3.5 * u], fill=accent, width=2)
    elif kind == "chip":
        draw.rectangle([cx - 2.5 * u, cy - 2.5 * u, cx + 2.5 * u, cy + 2.5 * u],
                       fill=dark)
        draw.rectangle([cx - 1.2 * u, cy - 1.2 * u, cx + 1.2 * u, cy + 1.2 * u],
                       fill=green)
        for k in range(3):
            yy = cy - 1.5 * u + k * 1.5 * u
            draw.line([cx - 4 * u, yy, cx - 2.5 * u, yy], fill=dark, width=2)
            draw.line([cx + 2.5 * u, yy, cx + 4 * u, yy], fill=dark, width=2)
    elif kind == "court":
        draw.rectangle([cx - 3 * u, cy - 3.5 * u, cx + 3 * u, cy + 3.5 * u],
                       outline=dark, width=2)
        draw.line([cx, cy - 3.5 * u, cx, cy + 3.5 * u], fill=dark, width=2)
        draw.ellipse([cx - 1.5 * u, cy - 1.5 * u, cx + 1.5 * u, cy + 1.5 * u],
                     outline=accent, width=2)
        draw.line([cx - 3 * u, cy, cx + 3 * u, cy], fill=GREY, width=1)
    elif kind == "siege":
        draw.rectangle([cx - 3.5 * u, cy - 2 * u, cx + 3.5 * u, cy + 3 * u], fill=blue)
        draw.rectangle([cx - 2.5 * u, cy, cx - 0.5 * u, cy + 3 * u], fill=(180, 220, 240))
        draw.rectangle([cx + 0.5 * u, cy, cx + 2.5 * u, cy + 3 * u], fill=(180, 220, 240))
        draw.polygon([(cx - 3.5 * u, cy - 2 * u), (cx, cy - 4 * u), (cx + 3.5 * u, cy - 2 * u)],
                     fill=accent)
    elif kind == "shop":
        draw.rectangle([cx - 3.5 * u, cy - 1 * u, cx + 3.5 * u, cy + 3.5 * u],
                       outline=dark, width=2)
        draw.polygon([(cx - 4 * u, cy - 1 * u), (cx + 4 * u, cy - 1 * u),
                      (cx + 3 * u, cy - 3 * u), (cx - 3 * u, cy - 3 * u)], fill=accent)
        draw.line([cx, cy - 1 * u, cx, cy + 3.5 * u], fill=dark, width=2)
    elif kind == "soccer":
        draw.ellipse([cx - 3.5 * u, cy - 3.5 * u, cx + 3.5 * u, cy + 3.5 * u],
                     fill=(255, 255, 255), outline=dark, width=2)
        draw.polygon([(cx, cy - 1.4 * u), (cx + 1.3 * u, cy - 0.4 * u),
                      (cx + 0.8 * u, cy + 1.1 * u), (cx - 0.8 * u, cy + 1.1 * u),
                      (cx - 1.3 * u, cy - 0.4 * u)], fill=dark)
        draw.line([cx, cy - 1.4 * u, cx, cy - 3.5 * u], fill=dark, width=2)
    elif kind == "asteroid":
        draw.ellipse([cx - 3.5 * u, cy - 2.5 * u, cx + 3.5 * u, cy + 2.5 * u],
                     fill=(150, 140, 130))
        draw.ellipse([cx - 1.5 * u, cy - 1 * u, cx + 0.5 * u, cy + 1 * u],
                     fill=(110, 100, 90))
        draw.ellipse([cx + 1.5 * u, cy - 1.5 * u, cx + 2.8 * u, cy - 0.2 * u],
                     fill=(110, 100, 90))
        for dx, dy in [(-4, 3), (4, 3), (0, -3.5)]:
            draw.ellipse([cx + dx * u - 0.5 * u, cy + dy * u - 0.5 * u,
                          cx + dx * u + 0.5 * u, cy + dy * u + 0.5 * u], fill=GREY)
    elif kind == "orbit":
        draw.ellipse([cx - 4 * u, cy - 2 * u, cx + 4 * u, cy + 2 * u],
                     outline=blue, width=2)
        draw.ellipse([cx - 1.6 * u, cy - 1.6 * u, cx + 1.6 * u, cy + 1.6 * u], fill=gold)
        draw.ellipse([cx + 3 * u, cy - 2.5 * u, cx + 4 * u, cy - 1.5 * u], fill=dark)
    else:  # climate
        draw.ellipse([cx - 3 * u, cy - 3 * u, cx + 3 * u, cy + 3 * u],
                     outline=green, width=2)
        draw.arc([cx - 3 * u, cy - 3 * u, cx + 3 * u, cy + 3 * u], 200, 340, fill=green, width=2)
        draw.line([cx - 3 * u, cy + 1 * u, cx + 3 * u, cy + 1 * u], fill=green, width=2)
        draw.polygon([(cx - 1 * u, cy - 3 * u), (cx + 1 * u, cy - 3 * u),
                      (cx, cy - 0.5 * u)], fill=green)


def draw_panel(draw, x, y, w, h, kind, colour, caption):
    draw.rectangle([x, y, x + w, y + h], fill=PAPER, outline=RULE, width=1)
    draw.rectangle([x, y, x + w, y + 5], fill=colour)
    draw_icon(draw, kind, x + 8, y + 12, x + w - 8, y + 72)
    font = load_font(11, True)
    lines = wrap_text(caption, font, w - 12)[:4]
    ty = y + 76
    for line in lines:
        draw.text((x + 6, ty), line, font=font, fill=INK)
        ty += 13


def draw_timeline(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 216), outline=RULE, width=1)
    label_font = load_font(11, True)
    sub_font = load_font(10)
    draw.text((x + 10, y + 5), "UTC TIMELINE  \u2014  25 NOVEMBER 2026", font=label_font, fill=NAVY)
    line_y = y + h - 10
    draw.line([x + 16, line_y, x + w - 16, line_y], fill=NAVY, width=2)
    n = len(TIMELINE)
    for i, (stamp, note) in enumerate(TIMELINE):
        cx = x + 40 + i * (w - 80) // (n - 1)
        draw.ellipse([cx - 4, line_y - 4, cx + 4, line_y + 4], fill=RED)
        stamp_font = load_font(11, True)
        half = max(stamp_font.getlength(stamp),
                   sub_font.getlength(note)) / 2
        tcx = min(max(cx, x + half + 4), x + w - half - 4)
        draw_center(draw, tcx, y + 20, stamp, stamp_font,
                    RED if "GMT" in stamp else NAVY)
        draw_center(draw, tcx, y + 34, note, sub_font, INK)


def draw_ticker(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY, outline=NAVY)
    label_font = load_font(11, True)
    item_font = load_font(11, True)
    draw.text((x + 10, y + 6), "TICKER", font=label_font, fill=(255, 214, 90))
    cols = 3
    cell_w = (w - 20) // cols
    for idx, item in enumerate(TICKER):
        col = idx % cols
        row = idx // cols
        cx0 = x + 10 + col * cell_w
        cy0 = y + 24 + row * 32
        draw.ellipse([cx0, cy0 + 3, cx0 + 8, cy0 + 11], fill=RED_SOFT)
        lines = wrap_text(item, item_font, cell_w - 18)[:2]
        ty = cy0
        for line in lines:
            draw.text((cx0 + 13, ty), line, font=item_font, fill=(255, 255, 255))
            ty += 13


def build_image():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W - 1, H - 1], outline=NAVY, width=3)

    # Header band.
    draw.rectangle([0, 0, W, 62], fill=NAVY)
    draw_center(draw, W // 2, 10, "THE WORLD IN ONE DAY", load_font(12, True),
                (255, 214, 90))
    draw_center(draw, W // 2, 28, HEADER_TEXT, load_font(20, True), (255, 255, 255))
    draw.rectangle([0, 62, W, 66], fill=RED)

    # Title line naming the three headline stories.
    draw_center(draw, W // 2, 74, TITLE_A, load_font(19, True), INK)
    draw_center(draw, W // 2, 98, TITLE_B, load_font(19, True), RED)
    draw.line([300, 122, 724, 122], fill=RULE, width=1)

    # 21 illustrated scenes: 7 columns x 3 rows.
    draw.text((10, 128), "21 SCENES FROM THE DAY", font=load_font(11, True), fill=NAVY)
    cols, rows = 7, 3
    pw, ph, gap = 140, 132, 6
    gx, gy = 10, 146
    for idx, (kind, colour, caption) in enumerate(PANELS):
        col = idx % cols
        row = idx // cols
        draw_panel(draw, gx + col * (pw + gap), gy + row * (ph + gap),
                   pw, ph, kind, colour, caption)

    # Dense list of the remaining 29 stories in 3 columns.
    list_y = 566
    draw.text((10, list_y), "THE REST OF THE DAY \u2014 29 MORE STORIES",
              font=load_font(11, True), fill=NAVY)
    draw.line([10, list_y + 18, W - 10, list_y + 18], fill=RED, width=2)
    col_w = 330
    col_x = [10, 348, 686]
    per_col = 10
    list_font = load_font(10)
    for idx, story in enumerate(MORE_STORIES):
        col = idx // per_col
        row = idx % per_col
        x = col_x[col]
        y = list_y + 24 + row * 22
        draw.ellipse([x, y + 4, x + 6, y + 10], fill=RED)
        lines = wrap_text(story, list_font, col_w - 12)[:2]
        ty = y
        for line in lines:
            draw.text((x + 10, ty), line, font=list_font, fill=INK)
            ty += 11

    # UTC timeline strip.
    draw_timeline(draw, 10, 812, W - 20, 58)

    # Six-story ticker strip.
    draw_ticker(draw, 10, 878, W - 20, 92)

    # Footer.
    draw_center(draw, W // 2, 982,
                "50 stories \u00b7 10 regions \u00b7 Wednesday 25 November 2026",
                load_font(12), GREY)
    return img


def output_path():
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        target = Path(env_dir)
        if target.is_dir():
            return target / "entry.png"
    out_dir = Path("/output")
    if out_dir.is_dir():
        return out_dir / "entry.png"
    return Path("entry.png")


def main():
    image = build_image()
    target = output_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="PNG")
    return target


if __name__ == "__main__":
    main()
