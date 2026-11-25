#!/usr/bin/env python3
"""news-image-20261125: draw the one-page front page for Wed 25 Nov 2026.

Code-drawn flat 2D vector front page (PIL). Run: python3 draw.py -> entry.png
All story text is written here in its exact render case (no case transforms).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---- colours ----
NAVY = (27, 42, 74)
NAVY2 = (35, 56, 99)
CREAM = (251, 243, 228)
CREAM2 = (245, 234, 210)
INK = (28, 28, 28)
MUSTARD = (232, 163, 23)
CORAL = (228, 87, 46)
TEAL = (42, 127, 111)
SKY = (191, 217, 232)
SEA = (168, 205, 226)
LAND = (107, 124, 63)
LAND2 = (125, 143, 78)
WHITE = (255, 255, 255)
GREY = (90, 90, 90)
LIGHTGREY = (220, 214, 200)
RED = (178, 34, 34)
GREEN = (46, 125, 50)
BLUE = (30, 90, 160)
AMBER = (176, 124, 0)
PURPLE = (106, 76, 147)

FONTDIR = "/usr/share/fonts/truetype/dejavu/"


def font(size, bold=False, serif=False):
    name = "DejaVuSerif-Bold.ttf" if (serif and bold) else \
        "DejaVuSerif.ttf" if serif else \
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(FONTDIR + name, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, fnt, color, max_w, leading=None, align="left"):
    """Draw wrapped text; returns y just below the last line."""
    lh = leading if leading is not None else int(fnt.size * 1.18)
    for line in wrap(d, text, fnt, max_w):
        if align == "center":
            d.text((x + (max_w - d.textlength(line, font=fnt)) / 2, y), line,
                   font=fnt, fill=color)
        else:
            d.text((x, y), line, font=fnt, fill=color)
        y += lh
    return y


def fit_size(d, text, max_w, start, minimum, bold=False, serif=False, max_lines=2):
    """Largest font size >= minimum whose wrap fits in max_lines lines."""
    size = start
    while size > minimum:
        fnt = font(size, bold=bold, serif=serif)
        if len(wrap(d, text, fnt, max_w)) <= max_lines:
            return fnt
        size -= 1
    return font(minimum, bold=bold, serif=serif)


CHIP_COLORS = {"CONFIRMED": GREEN, "OFFICIALS": BLUE, "REPORTED": AMBER,
               "FORECAST": PURPLE}


def chip(d, x, y, label):
    fnt = font(8, bold=True)
    w = int(d.textlength(label, font=fnt)) + 10
    d.rounded_rectangle([x, y, x + w, y + 13], radius=6,
                        fill=CHIP_COLORS[label])
    d.text((x + 5, y + 2), label, font=fnt, fill=WHITE)
    return w


# ---- story data (all verified 25 Nov 2026 in at least one time zone) ----
HEROES = [
    dict(num=1, kicker="01  •  WASHINGTON  •  TRADE",
         headline="TRUMP SET TO UNVEIL SECTION 301 TARIFFS ON 16 ECONOMIES",
         deck="USTR to propose new duties on China, the EU, Japan and others; rates still unknown.",
         source="AP  •  BBC", chip="REPORTED", art="tariffs"),
    dict(num=2, kicker="02  •  JIUQUAN  •  SPACE",
         headline="SHENZHOU-24 LIFTS OFF WITH PAKISTAN'S FIRST ASTRONAUT",
         deck="Muhammad Zeeshan Ali, 40, joins Tang Hongbo and Wu Yi aboard Tiangong station.",
         source="AP  •  XINHUA", chip="CONFIRMED", art="rocket"),
    dict(num=3, kicker="03  •  TEHRAN  •  MIDDLE EAST",
         headline="IRAN: NO TALKS UNTIL US MEETS SEVEN CONDITIONS",
         deck="Parliament speaker Ghalibaf sets terms as Qatar mediates; tanker war at sea widens.",
         source="WORLDWATCH  •  ET ENERGYWORLD", chip="OFFICIALS", art="tehran"),
]

SMALLS = [
    dict(num=4, kicker="04  •  SEOUL  •  MARKETS",
         headline="ASIAN STOCKS TUMBLE AS AI FADES",
         deck="KOSPI plunges 5.3%, Nikkei falls 2.9% as the tech rally fizzles.",
         source="REUTERS", chip="CONFIRMED", art="stocks"),
    dict(num=5, kicker="05  •  HONIARA  •  SECURITY",
         headline="SOLOMONS NAME AUSTRALIA PARTNER",
         deck="New pact names Canberra first; the treaty excludes China.",
         source="AP", chip="CONFIRMED", art="island"),
    dict(num=6, kicker="06  •  ADEN  •  YEMEN",
         headline="HOUTHIS CLOSE IN ON ADEN",
         deck="Houthis 60 km out; forces dig in, coalition hits Hodeidah port.",
         source="REUTERS  •  AL JAZEERA", chip="OFFICIALS", art="aden"),
    dict(num=7, kicker="07  •  TAIPEI  •  TECH",
         headline="HUANG APOLOGISES, IS IN THERAPY",
         deck="Nvidia chief admits 'terrible mistakes'; denies Trump role.",
         source="NYT  •  REUTERS", chip="CONFIRMED", art="chip"),
    dict(num=8, kicker="08  •  MIDDLETOWN  •  USA",
         headline="ARMY TO BLAST 10,000 LB IN IOWA",
         deck="68 drums go up at 09:00 CST; lead dust may drift 100 miles.",
         source="AP  •  US ARMY", chip="FORECAST", art="blast"),
    dict(num=9, kicker="09  •  SAN JUAN  •  CULTURE",
         headline="75TH MISS UNIVERSE CROWNED",
         deck="Jennifer Barreto of Puerto Rico wins; first mother to win.",
         source="USA TODAY  •  AP", chip="CONFIRMED", art="crown"),
    dict(num=10, kicker="10  •  SUVA  •  CLIMATE",
         headline="FIJI DECLARES DROUGHT DISASTER",
         deck="Prolonged drought scorches forests and farmland.",
         source="THE DIPLOMAT", chip="CONFIRMED", art="drought"),
    dict(num=11, kicker="11  •  QUEENSLAND  •  CLIMATE",
         headline="BARRIER REEF BLEACHING ALERT",
         deck="Scientists warn of unprecedented ocean heat as El Nino builds.",
         source="ABC AUSTRALIA", chip="FORECAST", art="reef"),
    dict(num=12, kicker="12  •  SAN FRANCISCO  •  WEATHER",
         headline="SAN FRANCISCO BRACES FOR FLOODS",
         deck="King tides and El Nino surf threaten the bay and the coast.",
         source="INSIDE CLIMATE NEWS", chip="FORECAST", art="waves"),
    dict(num=13, kicker="13  •  HONG KONG  •  RIGHTS",
         headline="HONG KONG FIRE: WARNING A YEAR ON",
         deck="Rights group marks a year on, urges free expression.",
         source="HRW", chip="OFFICIALS", art="hongkong"),
]

ALSO_ON = [
    (14, "Ethiopia offers to host inclusive Sudan peace talks; PM Abiy Ahmed invites all sides.", "Anadolu", "Africa"),
    (15, "Abrego Garcia, symbol of Trump's immigration crackdown, to leave the US voluntarily for Spain.", "AP", "Americas"),
    (16, "UN chief Guterres calls for AI guardrails at the Security Council as AI outpaces institutions.", "Xinhua", "Global"),
    (17, "A narrow majority of Germans now oppose military aid to Ukraine, 53% to 46%, a survey finds.", "Reuters", "Europe"),
    (18, "Eisenkot clinches the first coalition pact in Israel, with Lieberman's Israel Our Home.", "Reuters", "Middle East"),
    (19, "US envoy Huckabee is 'not certain' the $3.8bn annual military aid to Israel will end this year.", "Reuters", "Middle East"),
    (20, "Fort Hood shooter Hasan seeks a stay of execution ahead of a possible firing squad.", "Reuters", "Americas"),
    (21, "Senegal are reinstated as Africa Cup of Nations champions after CAS upholds their appeal.", "Straits Times", "Africa"),
    (22, "Russian warplanes trigger alarm among US partners in Asia, the WSJ reports.", "WSJ", "Asia-Pacific"),
    (23, "Kashiwa beat Newcastle in the AFC Champions League Elite.", "AFC", "Asia-Pacific"),
    (24, "Real Madrid hit PSV for five in the Champions League; Man City and Arsenal are held.", "myKhel", "Europe"),
    (25, "Balloons for Macy's 100th Thanksgiving parade inflate in New York on Wednesday.", "AFAR", "Americas"),
    (26, "Huang heads to Capitol Hill after his Trump-backed return to Nvidia.", "Around Prague", "Americas"),
    (27, "Liverpool visit Club Brugge and Bayern travel to Lille as the Champions League continues.", "BBC", "Europe"),
    (28, "A fourth oil tanker hits a mine in the Strait of Hormuz and catches fire.", "ET EnergyWorld", "Middle East"),
    (29, "Oil prices fall as supply glut fears offset Middle East disruption worries; Brent $90.97.", "Reuters", "Global"),
    (30, "Senegal face Tajikistan with the Group F summit in sight at the Under-17 World Cup.", "AfricaSoccer", "Africa"),
    (31, "Morocco's Ayyoub Bouaddi becomes his country's youngest Champions League scorer.", "AfricaSoccer", "Africa"),
    (32, "The US attorney general sidesteps questions on the Nvidia investigation.", "OzArab Media", "Americas"),
    (33, "Canada's foreign minister Anita Anand talks to the BBC about shaping a new world order.", "BBC", "Americas"),
    (34, "The BBC asks whether Indonesia faces a social reckoning.", "BBC", "Asia-Pacific"),
]

REGIONS = [("AMERICAS", 10), ("ASIA-PACIFIC", 6), ("MIDDLE EAST", 5),
           ("AFRICA", 4), ("EUROPE", 3), ("OCEANIA", 3), ("GLOBAL", 3)]

NUMBERS = [
    ("34", "STORIES"),
    ("7", "REGIONS"),
    ("16", "ECONOMIES IN TARIFF PROBE"),
    ("5.3%", "KOSPI FALL"),
    ("60 KM", "HOUTHIS FROM ADEN"),
    ("9,500 LB", "LEAD AZIDE TO DETONATE"),
]

TIMELINE = [
    ("00:07", "FIJI DISASTER DECLARED"),
    ("00:18", "SHENZHOU-24 LIFTS OFF"),
    ("00:52", "AP: TARIFF PLAN REPORTED"),
    ("02:31", "HORMUZ TANKER HIT"),
    ("04:20", "MISS UNIVERSE CROWNED"),
    ("15:00", "IOWA BLAST DUE"),
]

DATE_CHECK = ("DATE CHECK  •  Wires read up to 05:30 UTC, Wed 25 Nov 2026. "
    "Every story was reported, or still developing, on 25 Nov in at least one "
    "time zone. Left out: Huawei guilty verdict (Tue 24 Nov); China probes "
    "Shanghai party boss Chen Jining (Tue 24 Nov); Houthi drone strike on "
    "Riyadh tower, 11 hurt (Tue 24 Nov); Ukraine sinks Russian corvette "
    "Merkury off Libya (struck Sun 22 Nov, confirmed Mon 23 Nov); COP31 ends "
    "without a deal (Sun 22 Nov). Not yet: Section 301 tariff rates "
    "(pending); Iowa blast outcome (due 15:00 UTC); Sweden PM vote "
    "(not yet held).")

FOOTER = ("Every story here was reported on Wed 25 Nov 2026 in at least one "
    "time zone. Sources: AP, BBC, Reuters, Xinhua, NYT, USA Today, WSJ, HRW, "
    "ABC, The Diplomat, AFC, myKhel, AFAR, Straits Times, Anadolu, "
    "ET EnergyWorld. Original drawings.")


# ---- flat-vector art scenes (each draws inside box x,y,w,h) ----
def art_tariffs(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(233, 196, 106))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(120, 72, 20))
    for i, c in enumerate([(228, 87, 46), (42, 127, 111), (27, 42, 74)]):
        bx = x + 12 + i * 62
        d.rectangle([bx, y + h - 52, bx + 56, y + h - 12], fill=c,
                    outline=WHITE, width=2)
        for k in range(3):
            d.line([bx + 8, y + h - 42 + k * 10, bx + 48, y + h - 42 + k * 10],
                   fill=WHITE, width=2)
    d.ellipse([x + w - 62, y + 8, x + w - 8, y + 62], fill=NAVY)
    d.text((x + w - 48, y + 16), "%", font=font(28, bold=True), fill=MUSTARD)


def art_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(27, 42, 74))
    for sx, sy in [(14, 12), (40, 26), (70, 8), (w - 30, 16),
                   (w - 52, 34), (24, 48), (w - 18, 52)]:
        d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=WHITE)
    cx = x + w // 2
    bw = max(10, w // 12)
    nose = int(h * 0.30)
    body0 = int(h * 0.28)
    body1 = int(h * 0.72)
    d.polygon([(cx, y + 2), (cx - bw, y + nose), (cx + bw, y + nose)],
              fill=CORAL)
    d.rectangle([cx - bw, y + body0, cx + bw, y + body1], fill=WHITE)
    d.ellipse([cx - bw, y + int(h * 0.62), cx + bw, y + int(h * 0.78)],
              fill=MUSTARD)
    d.rectangle([cx - bw - 8, y + int(h * 0.45), cx - bw, y + body1],
                fill=MUSTARD)
    d.rectangle([cx + bw, y + int(h * 0.45), cx + bw + 8, y + body1],
                fill=MUSTARD)
    d.polygon([(cx - 4, y + h - 2), (cx + 4, y + h - 2), (cx, y + body1)],
              fill=(255, 200, 60))


def art_tehran(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 163, 23))
    d.rectangle([x, y + h - 30, x + w, y + h], fill=(120, 72, 20))
    for i in range(5):
        bx = x + 14 + i * 40
        bh = 34 + (i % 2) * 14
        d.rectangle([bx, y + h - 30 - bh, bx + 30, y + h - 30],
                    fill=NAVY2, outline=WHITE, width=1)
        d.rectangle([bx + 10, y + h - 30 - bh + 8, bx + 20,
                     y + h - 30 - bh + 18], fill=MUSTARD)
    d.ellipse([x + w - 66, y + 6, x + w - 14, y + 58], fill=WHITE)
    d.text((x + w - 52, y + 14), "7", font=font(30, bold=True), fill=RED)


def art_stocks(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 34, 34))
    d.line([(x + 8, y + 10), (x + w // 3, y + 16), (x + 2 * w // 3, y + 30),
            (x + w - 10, y + h - 8)], fill=WHITE, width=4)
    for px, py in [(x + 8, y + 10), (x + w // 3, y + 16),
                   (x + 2 * w // 3, y + 30), (x + w - 10, y + h - 8)]:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=MUSTARD)
    d.text((x + 10, y + h - 18), "-5.3%", font=font(13, bold=True), fill=WHITE)


def art_island(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.polygon([(x + 6, y + h), (x + int(w * 0.25), y + int(h * 0.45)),
               (x + w // 2, y + int(h * 0.35)),
               (x + int(w * 0.75), y + int(h * 0.45)), (x + w - 6, y + h)],
              fill=(42, 127, 111))
    d.polygon([(x + w // 2 - 3, y + int(h * 0.15)), (x + w // 2 + 3, y + int(h * 0.15)),
               (x + w // 2, y + int(h * 0.45))], fill=(107, 124, 63))
    d.polygon([(x + w // 2, y + int(h * 0.18)), (x + w // 2 + 18, y + int(h * 0.28)),
               (x + w // 2, y + int(h * 0.36))], fill=MUSTARD)


def art_aden(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 163, 23))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(42, 90, 120))
    d.rectangle([x + w - 82, y + h - 26, x + w - 42, y + h - 14], fill=NAVY)
    d.rectangle([x + w - 64, y + h - 36, x + w - 58, y + h - 26], fill=NAVY)
    d.polygon([(x + w - 46, y + 4), (x + w - 16, y + 4), (x + w - 31, y + 24)],
              fill=RED)
    d.text((x + 8, y + 4), "60 KM", font=font(11, bold=True), fill=RED)


def art_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(27, 42, 74))
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 22, cy - 18, cx + 22, cy + 18], fill=TEAL,
                outline=MUSTARD, width=3)
    for k in range(3):
        d.line([cx - 34, cy - 10 + k * 10, cx - 22, cy - 10 + k * 10],
               fill=MUSTARD, width=3)
        d.line([cx + 22, cy - 10 + k * 10, cx + 34, cy - 10 + k * 10],
               fill=MUSTARD, width=3)
    d.text((cx - 9, cy - 9), "AI", font=font(13, bold=True), fill=WHITE)


def art_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(245, 234, 210))
    d.ellipse([x + w // 2 - 26, y + 2, x + w // 2 + 26, y + 34], fill=(120, 72, 20))
    d.ellipse([x + w // 2 - 16, y + 16, x + w // 2 + 16, y + 44], fill=CORAL)
    for i in range(4):
        bx = x + 12 + i * 18
        d.rectangle([bx, y + h - 16, bx + 14, y + h - 4], fill=NAVY)
    d.text((x + 8, y + h - 30), "9,500 LB", font=font(10, bold=True), fill=RED)


def art_crown(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 87, 46))
    cx = x + w // 2
    d.polygon([(cx - 26, y + h - 10), (cx - 26, y + 14), (cx - 10, y + 26),
               (cx, y + 6), (cx + 10, y + 26), (cx + 26, y + 14),
               (cx + 26, y + h - 10)], fill=MUSTARD, outline=WHITE)
    for px in (cx - 26, cx, cx + 26):
        d.ellipse([px - 3, y + 8, px + 3, y + 14], fill=WHITE)


def art_drought(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(233, 196, 106))
    d.ellipse([x + w - 34, y + 4, x + w - 6, y + 32], fill=(255, 120, 40))
    d.line([(x + 8, y + h - 8), (x + w // 3, y + h - 20),
            (x + 2 * w // 3, y + h - 12), (x + w - 8, y + h - 24)],
           fill=(120, 72, 20), width=2)
    d.line([(x + w // 2, y + h - 6), (x + w // 2 + 6, y + h - 22)],
           fill=(120, 72, 20), width=2)


def art_reef(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(42, 127, 111))
    for i, c in enumerate([(255, 255, 255), (232, 163, 23), (255, 255, 255)]):
        bx = x + 14 + i * 24
        d.polygon([(bx, y + h - 6), (bx + 6, y + 12), (bx + 12, y + 6),
                   (bx + 18, y + 18), (bx + 22, y + h - 6)], fill=c)
    d.ellipse([x + w - 30, y + 6, x + w - 8, y + 28], fill=MUSTARD)


def art_waves(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    for i in range(3):
        yy = y + int(h * (0.12 + i * 0.28))
        d.arc([x + 6, yy, x + w - 6, yy + int(h * 0.28)], 180, 360,
              fill=NAVY, width=3)
    d.rectangle([x + 12, y + h - 14, x + 26, y + h - 4], fill=NAVY2)
    d.rectangle([x + 30, y + h - 18, x + 42, y + h - 4], fill=NAVY2)
    d.rectangle([x + 46, y + h - 12, x + 58, y + h - 4], fill=NAVY2)


def art_hongkong(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(35, 56, 99))
    for i, bh in enumerate([22, 34, 26, 40, 30]):
        bx = x + 10 + i * 15
        d.rectangle([bx, y + h - 8 - bh, bx + 11, y + h - 8], fill=(200, 200, 200))
        d.rectangle([bx + 3, y + h - 8 - bh + 5, bx + 8, y + h - 8 - bh + 10],
                    fill=MUSTARD)
    d.polygon([(x + w - 22, y + 8), (x + w - 14, y + 8), (x + w - 18, y + 22)],
              fill=(255, 200, 60))
    d.ellipse([x + w - 24, y + 22, x + w - 12, y + 30], fill=(255, 200, 60))


ART = {"tariffs": art_tariffs, "rocket": art_rocket, "tehran": art_tehran,
       "stocks": art_stocks, "island": art_island, "aden": art_aden,
       "chip": art_chip, "blast": art_blast, "crown": art_crown,
       "drought": art_drought, "reef": art_reef, "waves": art_waves,
       "hongkong": art_hongkong}


def draw_hero(d, s, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=NAVY, width=2)
    d.rectangle([x, y, x + w, y + 18], fill=NAVY)
    d.text((x + 8, y + 3), s["kicker"], font=font(9, bold=True), fill=MUSTARD)
    hy = y + 22
    hf = fit_size(d, s["headline"], w - 16, 20, 20, bold=True, max_lines=3)
    hy = text_block(d, x + 8, hy, s["headline"], hf, INK, w - 16, leading=23)
    ay = hy + 4
    ah = y + h - 52 - ay
    ART[s["art"]](d, x + 8, ay, w - 16, max(ah, 30))
    dy = y + h - 48
    text_block(d, x + 8, dy, s["deck"], font(11), INK, w - 16, leading=13)
    d.text((x + 8, y + h - 15), s["source"], font=font(8, bold=True), fill=GREY)
    fnt = font(8, bold=True)
    cw = int(d.textlength(s["chip"], font=fnt)) + 10
    chip(d, x + w - 8 - cw, y + h - 16, s["chip"])


def draw_small(d, s, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=NAVY, width=1)
    d.rectangle([x, y, x + w, y + 14], fill=NAVY)
    d.text((x + 6, y + 2), s["kicker"], font=font(7, bold=True), fill=MUSTARD)
    hy = y + 17
    hf = fit_size(d, s["headline"], w - 12, 15, 15, bold=True, max_lines=2)
    hy = text_block(d, x + 6, hy, s["headline"], hf, INK, w - 12, leading=17)
    deck_y = y + h - 38
    ay = hy + 3
    ah = deck_y - 4 - ay
    ART[s["art"]](d, x + 6, ay, w - 12, max(ah, 20))
    text_block(d, x + 6, deck_y, s["deck"], font(10), INK, w - 12, leading=12)
    d.text((x + 6, y + h - 13), s["source"], font=font(7, bold=True), fill=GREY)
    fnt = font(8, bold=True)
    cw = int(d.textlength(s["chip"], font=fnt)) + 10
    chip(d, x + w - 6 - cw, y + h - 14, s["chip"])


# ---- world map (rough equirectangular land, lon -170..190, lat 75..-55) ----
CONTINENTS = [
    [(-168, 66), (-158, 58), (-152, 60), (-140, 60), (-135, 57), (-130, 54),
     (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20),
     (-97, 16), (-92, 15), (-86, 12), (-83, 9), (-79, 9), (-81, 13),
     (-84, 16), (-87, 21), (-90, 21), (-97, 26), (-93, 30), (-89, 30),
     (-84, 30), (-81, 26), (-80, 32), (-76, 35), (-74, 40), (-70, 42),
     (-68, 45), (-65, 44), (-60, 47), (-55, 47), (-60, 52), (-64, 58),
     (-68, 58), (-72, 62), (-78, 62), (-85, 66), (-92, 66), (-95, 69),
     (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68), (-168, 66)],
    [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
     (-20, 74), (-25, 76), (-35, 77), (-50, 76), (-58, 74), (-60, 70),
     (-58, 64)],
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-70, -50),
     (-68, -55), (-65, -55), (-68, -50), (-65, -45), (-62, -41),
     (-58, -35), (-52, -32), (-48, -28), (-41, -23), (-39, -17),
     (-35, -9), (-35, -6), (-41, -3), (-44, -2), (-50, 0), (-53, 4),
     (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-76, 10), (-79, 9)],
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-6, 34), (0, 36),
     (10, 37), (11, 34), (20, 32), (30, 31), (32, 31), (34, 28), (37, 22),
     (39, 18), (43, 12), (48, 11), (51, 12), (46, 5), (42, 0), (40, -5),
     (40, -10), (36, -18), (33, -26), (28, -33), (20, -35), (17, -32),
     (15, -27), (13, -18), (12, -10), (13, -5), (9, 0), (9, 4), (4, 6),
     (-3, 5), (-8, 5), (-13, 8), (-17, 12), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 50), (2, 51),
     (5, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62), (12, 64),
     (18, 69), (25, 71), (32, 70), (40, 68), (50, 69), (60, 70), (68, 72),
     (75, 72), (80, 73), (90, 75), (100, 76), (110, 74), (120, 73),
     (130, 72), (140, 72), (150, 70), (158, 69), (162, 66), (170, 66),
     (178, 65), (178, 62), (170, 60), (162, 60), (158, 52), (150, 59),
     (142, 59), (142, 53), (140, 45), (135, 43), (130, 42), (127, 40),
     (126, 38), (122, 37), (120, 32), (121, 28), (118, 25), (114, 22),
     (110, 20), (108, 18), (105, 10), (103, 7), (100, 7), (98, 10),
     (95, 16), (92, 21), (89, 22), (86, 20), (83, 18), (80, 15), (77, 8),
     (75, 11), (73, 16), (70, 20), (67, 24), (62, 25), (58, 26), (56, 27),
     (54, 27), (52, 26), (50, 29), (48, 30), (50, 26), (54, 24), (56, 26),
     (58, 23), (59, 22), (57, 18), (55, 17), (52, 15), (48, 14), (44, 13),
     (43, 12), (40, 15), (39, 20), (38, 24), (37, 28), (35, 29), (34, 31),
     (33, 35), (30, 36), (27, 37), (26, 38), (23, 36), (22, 37), (19, 40),
     (18, 40), (15, 38), (12, 38), (10, 37), (8, 37), (10, 39), (12, 42),
     (14, 44), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36),
     (-9, 37), (-10, 36)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-3, 50)],
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
     (141, 39), (141, 42), (143, 44), (145, 44), (142, 42), (140, 38)],
    [(95, 5), (98, 3), (100, 0), (103, -2), (106, -6), (110, -7),
     (114, -8), (119, -9), (122, -10), (125, -9), (128, -8), (130, -4),
     (131, -1), (128, 0), (124, 1), (120, 1), (117, 0), (114, 1), (110, 2),
     (106, 3), (102, 4), (98, 5)],
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (113, -4),
     (109, -1)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -8), (147, -9),
     (143, -8), (138, -7), (134, -4), (131, -1)],
    [(114, -22), (114, -30), (115, -34), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
     (146, -19), (142, -15), (142, -11), (140, -17), (136, -15),
     (135, -12), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (114, -22)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
     (174, -41), (172, -43), (168, -46)],
]

# pins: (story, lon, lat, dx, dy) — dx/dy nudge the drawn pin off the true spot
PINS = [
    (1, -77.0, 39.0, 6, 8),
    (2, 98.5, 39.8, -6, -4),
    (3, 51.4, 35.7, 0, 0),
    (4, 127.0, 37.5, 0, 0),
    (5, 160.0, -9.4, 0, 0),
    (6, 45.0, 12.8, 0, 0),
    (7, 121.6, 25.0, 0, 0),
    (8, -91.3, 40.8, -8, -6),
    (9, -66.1, 18.5, 0, 0),
    (10, 178.4, -17.7, 0, 0),
    (11, 146.5, -19.0, 0, 0),
    (12, -122.4, 37.8, 0, 0),
    (13, 114.2, 22.3, -12, 6),
]

# small islands drawn exaggerated (a few px) so their pins sit on land:
# (lon, lat, rx, ry) in map px
ISLANDS = [
    (121.0, 23.7, 5, 8),    # Taiwan
    (160.0, -9.4, 6, 4),    # Solomon Islands
    (178.4, -17.7, 5, 4),   # Fiji
    (-66.1, 18.5, 6, 3),    # Puerto Rico
]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=NAVY, width=1)
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 75.0, -55.0

    def px(lon, lat):
        return (x + (lon - lon0) / (lon1 - lon0) * w,
                y + (lat0 - lat) / (lat0 - lat1) * h)

    for poly in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND)
    for lon, lat, rx, ry in ISLANDS:
        cx, cy = px(lon, lat)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=LAND)
    for num, lon, lat, dx, dy in PINS:
        tx, ty = px(lon, lat)
        cx, cy = tx + dx, ty + dy
        if dx or dy:
            d.line([tx, ty, cx, cy], fill=NAVY, width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=NAVY)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                  outline=WHITE, width=2)
        fnt = font(8, bold=True)
        tw = d.textlength(str(num), font=fnt)
        d.text((cx - tw / 2, cy - 6), str(num), font=fnt, fill=WHITE)


# ---- compose ----
def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # masthead
    d.rectangle([0, 0, W, 108], fill=NAVY)
    d.text((W // 2 - d.textlength("THE DAY IN WORLD NEWS", font=font(13, bold=True)) / 2,
            7), "THE DAY IN WORLD NEWS", font=font(13, bold=True), fill=MUSTARD)
    mf = font(46, bold=True, serif=True)
    title = "Wednesday 25 November 2026"
    d.text((W // 2 - d.textlength(title, font=mf) / 2, 24), title,
           font=mf, fill=WHITE)
    sub = "34 STORIES  •  7 REGIONS  •  ONE DAY"
    d.text((W // 2 - d.textlength(sub, font=font(13, bold=True)) / 2, 86),
           sub, font=font(13, bold=True), fill=WHITE)
    # ticker
    tick = ("TARIFFS LOOM  •  SHENZHOU-24 LIFTS OFF  •  "
            "IRAN SETS SEVEN CONDITIONS")
    d.text((W // 2 - d.textlength(tick, font=font(11, bold=True)) / 2, 110),
           tick, font=font(11, bold=True), fill=NAVY)
    # multicolour stripe
    stripe = [CORAL, MUSTARD, TEAL, NAVY2, (200, 60, 120)]
    for i, c in enumerate(stripe):
        d.rectangle([i * W // 5, 126, (i + 1) * W // 5, 131], fill=c)

    # UTC timeline strip: one line per event in chronological columns,
    # 00-24 axis below with a dot at each event's true UTC position.
    tx0, tx1, ty = 12, 1012, 152
    d.line([tx0, ty, tx1, ty], fill=NAVY, width=2)
    for hh in range(0, 25, 4):
        xx = tx0 + hh / 24 * (tx1 - tx0)
        d.line([xx, ty - 4, xx, ty + 4], fill=NAVY, width=2)
        lab = "%02d" % hh
        d.text((xx - 6, ty + 6), lab, font=font(7), fill=GREY)
    colw = (W - 24) // 6
    for i, (tm, lab) in enumerate(TIMELINE):
        cx = 12 + i * colw
        hour = int(tm.split(":")[0]) + int(tm.split(":")[1]) / 60.0
        xx = tx0 + hour / 24 * (tx1 - tx0)
        d.ellipse([xx - 3, ty - 3, xx + 3, ty + 3], fill=CORAL)
        tf = font(9, bold=True)
        d.text((cx + 4, 134), tm, font=tf, fill=CORAL)
        tw = d.textlength(tm, font=tf)
        d.text((cx + 4 + tw + 5, 134), lab, font=font(8, bold=True), fill=INK)

    # 6 big numbers
    bw = (W - 24 - 5 * 6) // 6
    for i, (num, lab) in enumerate(NUMBERS):
        bx = 12 + i * (bw + 6)
        d.rectangle([bx, 165, bx + bw, 199], fill=WHITE, outline=NAVY, width=1)
        nf = fit_size(d, num, bw - 10, 22, 16, bold=True, max_lines=1)
        d.text((bx + bw // 2 - d.textlength(num, font=nf) / 2, 167), num,
               font=nf, fill=NAVY)
        text_block(d, bx + 4, 188, lab, font(7, bold=True), GREY, bw - 8,
                   leading=8, align="center")

    # region bar
    rb = "  •  ".join("%s %d" % (name, n) for name, n in REGIONS)
    d.text((W // 2 - d.textlength(rb, font=font(10, bold=True)) / 2, 203),
           rb, font=font(10, bold=True), fill=NAVY)

    # heroes
    hw = (W - 24 - 12) // 3
    for i, s in enumerate(HEROES):
        draw_hero(d, s, 12 + i * (hw + 6), 219, hw, 200)

    # small panels, 2 rows of 5
    sw = (W - 24 - 4 * 6) // 5
    for i, s in enumerate(SMALLS):
        row, col = divmod(i, 5)
        draw_small(d, s, 12 + col * (sw + 6), 423 + row * 142, sw, 138)

    # map + ALSO ON
    d.text((12, 707), "WHERE IT HAPPENED", font=font(11, bold=True), fill=NAVY)
    d.text((348, 707), "ALSO ON", font=font(11, bold=True), fill=NAVY)
    draw_map(d, 12, 723, 330, 210)
    d.text((12, 937), "Pins 1–13 mark the panel stories.",
           font=font(8), fill=GREY)
    colw2 = (1012 - 348 - 12) // 2
    for i, (num, text, src, _reg) in enumerate(ALSO_ON):
        col, row = divmod(i, 11)
        ax = 348 + col * (colw2 + 12)
        ay = 723 + row * 21
        full = "%d. %s — %s" % (num, text, src)
        text_block(d, ax, ay, full, font(9), INK, colw2, leading=10)

    # DATE CHECK
    d.rectangle([12, 957, 1012, 1001], fill=(255, 235, 235), outline=RED, width=1)
    text_block(d, 18, 960, DATE_CHECK, font(8), INK, 988, leading=10)

    # footer
    text_block(d, 12, 1004, FOOTER, font(8), GREY, 1000, leading=10)

    img.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
