#!/usr/bin/env python3
"""news-image-20261125 v5: COPY-#1 format - 50 stories, 10 regions, 21 fields.

Code-drawn flat 2D vector front page (PIL). Run: python3 draw.py -> entry.png
All story text is written here in its exact render case (no case transforms).
Region and field bars are computed from STORIES, never hand-counted.
"""
import math
import os
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---- colours ----
NAVY = (27, 42, 74)
NAVY2 = (35, 56, 99)
CREAM = (251, 243, 228)
INK = (28, 28, 28)
MUSTARD = (232, 163, 23)
CORAL = (228, 87, 46)
TEAL = (42, 127, 111)
SKY = (191, 217, 232)
SEA = (168, 205, 226)
LAND = (107, 124, 63)
WHITE = (255, 255, 255)
GREY = (90, 90, 90)
RED = (178, 34, 34)
GREEN = (46, 125, 50)
BLUE = (30, 90, 160)
AMBER = (176, 124, 0)
PURPLE = (106, 76, 147)
PINK = (200, 60, 120)
BROWN = (120, 72, 20)

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


def fit_size(d, text, max_w, start, minimum, bold=False, serif=False,
             max_lines=2):
    """Largest font size >= minimum whose wrap fits in max_lines lines."""
    size = start
    while size > minimum:
        fnt = font(size, bold=bold, serif=serif)
        if len(wrap(d, text, fnt, max_w)) <= max_lines:
            return fnt
        size -= 1
    return font(minimum, bold=bold, serif=serif)


# ---- regions (10) and fields (21) in display order ----
REGION_ORDER = ["N. AMERICA", "LATIN AMERICA", "EUROPE", "MIDDLE EAST",
                "N. AFRICA", "SUB-SAHARAN AFRICA", "SOUTH ASIA",
                "EAST & SE ASIA", "OCEANIA", "GLOBAL"]
REGION_COLORS = {"N. AMERICA": NAVY, "LATIN AMERICA": TEAL,
                 "EUROPE": BLUE, "MIDDLE EAST": RED,
                 "N. AFRICA": MUSTARD, "SUB-SAHARAN AFRICA": PURPLE,
                 "SOUTH ASIA": CORAL, "EAST & SE ASIA": GREEN,
                 "OCEANIA": PINK, "GLOBAL": GREY}
REGION_TEXT = {"N. AFRICA": INK}  # dark text on the mustard chip only

FIELD_ORDER = ["War", "Disaster", "Justice", "Security", "Diplomacy", "Tech",
               "Crime", "Economy", "Labour", "Markets", "Rights", "Sport",
               "Trade", "Business", "Climate", "Energy", "Environment",
               "Humanitarian", "Politics", "Culture", "Space"]

VER_COLORS = {"OFFICIAL": GREEN, "REPORTED": AMBER, "CLAIM": RED}
VER_LABELS = {"O": "OFFICIAL", "R": "REPORTED", "CL": "CLAIM"}


def ver_chip(d, x, y, label):
    fnt = font(8, bold=True)
    w = int(d.textlength(label, font=fnt)) + 10
    d.rounded_rectangle([x, y, x + w, y + 13], radius=6,
                        fill=VER_COLORS[label])
    d.text((x + 5, y + 2), label, font=fnt, fill=WHITE)
    return w


# ---- story data: all verified 25 Nov 2026 (first reported Wed 25 Nov) ----
# keys: num, region, field, kicker, headline, deck, source, ver (O/R/CL),
#       stat (small panels), why (heroes), art (panels)
STORIES = [
    # --- 3 heroes ---
    dict(num=1, region="N. AMERICA", field="Trade",
         kicker="01  •  WASHINGTON  •  TRADE",
         headline="US proposes tariffs of up to 20% on EU, China and 12 more",
         deck="China: 20% new (total ~45%). Vietnam: 35% ceiling, or 20% with a "
              "deal. EU, Japan, Korea, Taiwan: 15%.",
         why="Two top US trade partners face duties.",
         source="REUTERS  •  AP", ver="O", art="tariffs"),
    dict(num=2, region="EAST & SE ASIA", field="Markets",
         kicker="02  •  SEOUL  •  TOKYO  •  TAIPEI  •  MARKETS",
         headline="AI doubts sink Asian chip stocks: Kospi closes −6.2%",
         deck="Kospi 4,697.51; SK hynix −11.1%, Samsung −9.9%; "
              "Taiex −4.8%, Nikkei −2.8%.",
         why="Investors doubt the AI boom pays off.",
         source="WSJ  •  AP", ver="R", art="chart"),
    dict(num=3, region="EAST & SE ASIA", field="Space",
         kicker="03  •  JIUQUAN, CHINA  •  SPACE",
         headline="Pakistan's first astronaut docks at China's space station",
         deck="Muhammad Zeeshan Ali, 40, first foreigner on Tiangong, flew on "
              "Shenzhou-24; stays 5 to 10 days.",
         why="Tiangong takes its first foreign astronaut.",
         source="AP  •  XINHUA", ver="O", art="rocket"),
    # --- 10 small panels ---
    dict(num=4, region="EUROPE", field="War",
         kicker="04  •  KYIV  •  WAR",
         headline="Russian strikes kill 5, cut power in 5 regions",
         deck="Five regions lose power; Zaporizhzhia plant on diesel.",
         stat="5 REGIONS", art="strikes"),
    dict(num=5, region="MIDDLE EAST", field="War",
         kicker="05  •  RAS TANURA  •  WAR",
         headline="Saudis down Houthi drones",
         deck="Four down over Ras Tanura after Hodeidah strike.",
         stat="4 DRONES", art="drone"),
    dict(num=6, region="EUROPE", field="Energy",
         kicker="06  •  LONDON  •  ENERGY",
         headline="UK energy price cap to rise 26% in January",
         deck="Typical bill £1,723 → £2,166 (+£443), Ofgem says.",
         stat="£2,166", art="energy"),
    dict(num=7, region="OCEANIA", field="Diplomacy",
         kicker="07  •  CANBERRA  •  DIPLOMACY",
         headline="Solomons signs security pact with Australia",
         deck="A$740m over 10 years; names Canberra first, excludes China.",
         stat="CANBERRA FIRST", art="island"),
    dict(num=8, region="SOUTH ASIA", field="Labour",
         kicker="08  •  DHAKA  •  LABOUR",
         headline="Garment workers offered higher minimum wage",
         deck="Board lifts the minimum 36%, 12,500 → 17,000 taka a month.",
         stat="17,000 TAKA", art="wage"),
    dict(num=9, region="EAST & SE ASIA", field="Disaster",
         kicker="09  •  BOGOR  •  DISASTER",
         headline="9 dead, 17 still trapped in flooded gold mine",
         deck="Rain floods an illegal 100-metre shaft; 11 miners escape.",
         stat="9 DEAD", art="mine"),
    dict(num=10, region="MIDDLE EAST", field="War",
         kicker="10  •  GAZA CITY  •  WAR",
         headline="Israeli strike kills Hamas security chief",
         deck="Mohammad Abuelouf dies with his wife and two daughters.",
         stat="2ND IN 24H", art="gaza"),
    dict(num=11, region="SUB-SAHARAN AFRICA", field="Justice",
         kicker="11  •  CAPE TOWN  •  JUSTICE",
         headline="Court lifts 'Farmgate' charges",
         deck="High Court voids report; Ramaphosa impeachment ends.",
         stat="RULING", art="scales"),
    dict(num=12, region="MIDDLE EAST", field="Justice",
         kicker="12  •  JERUSALEM  •  JUSTICE",
         headline="Judges urge rethink of Netanyahu graft charges",
         deck="Judges say drop Case 4000; rethink Case 2000.",
         stat="3 CASES", art="court"),
    dict(num=13, region="N. AFRICA", field="Disaster",
         kicker="13  •  GIZA  •  DISASTER",
         headline="Fuel tanker fire kills at least 30 near Cairo",
         deck="Tanker overturns on the Ring Road; fire engulfs cars.",
         stat="30 DEAD", art="tanker"),
    # --- ALSO ON 14-50: one line each, source + veracity letter ---
    dict(num=14, region="SUB-SAHARAN AFRICA", field="Diplomacy",
         text="Ethiopia offers to host inclusive Sudan peace talks.",
         source="Anadolu", ver="R"),
    dict(num=15, region="N. AMERICA", field="Rights",
         text="Abrego Garcia to leave the US voluntarily for Spain.",
         source="AP", ver="R"),
    dict(num=16, region="GLOBAL", field="Tech",
         text="Guterres calls for AI guardrails at Security Council.",
         source="Xinhua", ver="O"),
    dict(num=17, region="EUROPE", field="Politics",
         text="Most Germans oppose military aid to Ukraine, poll finds.",
         source="Reuters", ver="R"),
    dict(num=18, region="MIDDLE EAST", field="Politics",
         text="Eisenkot clinches first coalition pact in Israel.",
         source="Reuters", ver="R"),
    dict(num=19, region="MIDDLE EAST", field="Diplomacy",
         text="Huckabee 'not certain' $3.8bn Israel aid ends this year.",
         source="Reuters", ver="R"),
    dict(num=20, region="N. AMERICA", field="Crime",
         text="Fort Hood shooter Hasan seeks stay ahead of execution.",
         source="Reuters", ver="R"),
    dict(num=21, region="LATIN AMERICA", field="Disaster",
         text="Heavy rains kill at least 8 in southern Brazil.",
         source="Xinhua", ver="R"),
    dict(num=22, region="EAST & SE ASIA", field="Security",
         text="Russian warplanes trigger alarm among US partners in Asia.",
         source="WSJ", ver="R"),
    dict(num=23, region="EAST & SE ASIA", field="Sport",
         text="Kashiwa beat Newcastle in the AFC Champions League Elite.",
         source="AFC", ver="O"),
    dict(num=24, region="EUROPE", field="Diplomacy",
         text="EU leaders meet Western Balkan counterparts.",
         source="EU Council", ver="O"),
    dict(num=25, region="N. AMERICA", field="Culture",
         text="Balloons for Macy's 100th Thanksgiving parade inflate.",
         source="AFAR", ver="R"),
    dict(num=26, region="EUROPE", field="Politics",
         text="Puigdemont to return to Spain on Dec 12, ending exile.",
         source="France 24", ver="R"),
    dict(num=27, region="EUROPE", field="Sport",
         text="Liverpool win 3–0 at Brugge; Lille stun Bayern 2–1.",
         source="UEFA", ver="O"),
    dict(num=28, region="MIDDLE EAST", field="Security",
         text="A fourth tanker hits a mine in the Strait of Hormuz.",
         source="ET EnergyWorld", ver="R"),
    dict(num=29, region="MIDDLE EAST", field="Economy",
         text="Brent jumps 2.4% to $93.60 after Ras Tanura claim.",
         source="OilPrice", ver="R"),
    dict(num=30, region="SUB-SAHARAN AFRICA", field="Sport",
         text="Senegal face Tajikistan at the Under-17 World Cup.",
         source="AfricaSoccer", ver="O"),
    dict(num=31, region="SUB-SAHARAN AFRICA", field="Sport",
         text="Bouaddi is Morocco's youngest UCL scorer.",
         source="AfricaSoccer", ver="O"),
    dict(num=32, region="N. AMERICA", field="Business",
         text="DOJ opened no probe into Huang before return, sources say.",
         source="Reuters", ver="R"),
    dict(num=33, region="N. AMERICA", field="Diplomacy",
         text="Canada's Anita Anand talks to the BBC on a new world order.",
         source="BBC", ver="R"),
    dict(num=34, region="SUB-SAHARAN AFRICA", field="Culture",
         text="Pete Edochie dies Wed 25 Nov, aged 79, after cancer battle.",
         source="BBC", ver="R"),
    dict(num=35, region="MIDDLE EAST", field="Diplomacy",
         text="Iran sets seven conditions before any talks with US.",
         source="ET EnergyWorld", ver="O"),
    dict(num=36, region="EUROPE", field="Business",
         text="Poundland falls into administration; 12,000 jobs at risk.",
         source="Reuters", ver="R"),
    dict(num=37, region="LATIN AMERICA", field="Markets",
         text="Argentina's peso hits record low past 1,600; country risk "
              "tops 1,100.",
         source="Bloomberg", ver="R"),
    dict(num=38, region="N. AMERICA", field="Disaster",
         text="Iowa blast destroys 9,500 lb; EPA finds zero airborne lead.",
         source="AP", ver="O"),
    dict(num=39, region="OCEANIA", field="Disaster",
         text="Fiji declares drought disaster as forests scorch.",
         source="The Diplomat", ver="O"),
    dict(num=40, region="OCEANIA", field="Environment",
         text="Scientists warn of unprecedented ocean heat at Barrier Reef.",
         source="ABC", ver="R"),
    dict(num=41, region="N. AMERICA", field="Climate",
         text="San Francisco braces for floods; king tides threaten bay.",
         source="Inside Climate News", ver="R"),
    dict(num=42, region="EAST & SE ASIA", field="Rights",
         text="HRW urges free expression ahead of Tai Po anniversary.",
         source="HRW", ver="O"),
    dict(num=43, region="LATIN AMERICA", field="Trade",
         text="US proposes 10% duty on Brazilian aircraft, hits Embraer.",
         source="Reuters", ver="R"),
    dict(num=44, region="SOUTH ASIA", field="Markets",
         text="India's Nifty jumps 1.85%, the only Asian riser.",
         source="Reuters", ver="R"),
    dict(num=45, region="N. AMERICA", field="Markets",
         text="Nvidia falls 5.9% in New York; Micron drops 11%.",
         source="WSJ", ver="R"),
    dict(num=46, region="EAST & SE ASIA", field="Markets",
         text="Shanghai falls 2.0% and Hong Kong 1.1% as tariffs loom.",
         source="Reuters", ver="R"),
    dict(num=47, region="MIDDLE EAST", field="Security",
         text="Houthi projectile hits Jazan port; minor damage, no injuries.",
         source="Reuters", ver="R"),
    dict(num=48, region="SUB-SAHARAN AFRICA", field="Humanitarian",
         text="RSF drone strikes kill 19 civilians in Sudan's Blue Nile.",
         source="Reuters", ver="R"),
    dict(num=49, region="EUROPE", field="Politics",
         text="Merz: Russia wants more than Ukraine, defends Kyiv aid.",
         source="Reuters", ver="R"),
    dict(num=50, region="EUROPE", field="Security",
         text="Poland to set up no-fly zone along Ukraine border.",
         source="Reuters", ver="R"),
]

HEROES = STORIES[0:3]
SMALLS = STORIES[3:13]
ALSO_ON = STORIES[13:50]

NUMBERS = [
    ("20%", "TOP US TARIFF: EU, CHINA + 12 MORE"),
    ("−6.2%", "KOSPI CLOSE, WORST IN AI SELL-OFF"),
    ("+26%", "UK ENERGY PRICE CAP FROM 1 JANUARY"),
    ("30+", "KILLED IN CAIRO TANKER FIRE"),
    ("9", "DEAD, 17 TRAPPED IN JAVA GOLD PIT"),
]

DATE_CHECK = ("DATE CHECK  •  Wires read up to 23:00 UTC, Wed 25 Nov 2026. "
    "Every story above happened or was first reported on Wednesday "
    "25 November 2026. Left out: Senegal AFCON reinstatement; Huang "
    "hearings Dec 1–3 and Huang apology (all Tue 24 Nov); Houthis near "
    "Aden (Tue 24 Nov); Huawei guilty verdict (Tue 24 Nov); China "
    "probes Shanghai party boss Chen Jining (Tue 24 Nov); Houthi drone "
    "strike on Riyadh tower, 11 hurt (Tue 24 Nov); Ukraine sinks Russian "
    "corvette Merkury off Libya (struck Sun 22 Nov, confirmed Mon 23 Nov); "
    "COP31 ends without a deal (Sun 22 Nov); Real Madrid 5–1 PSV "
    "(Tue 24 Nov); Miss Universe crowned (Tue 24 Nov). Not yet: US "
    "Thanksgiving (Thu 26 Nov); Sweden PM vote; Section 301 tariffs in "
    "force (comment + hearing first, may slip to January). OFFICIAL an "
    "authority's own figure or act • REPORTED press report • CLAIM one "
    "side's account.")

FOOTER = ("Sources: Reuters, AP, BBC, Xinhua, NYT, WSJ, HRW, ABC, "
    "The Diplomat, AFC, AFAR, Straits Times, Anadolu, ET EnergyWorld, "
    "EU Council, AfricaSoccer, France 24, Bloomberg Línea, UEFA, OilPrice, "
    "Inside Climate News. Every drawing original.")


# ---- flat-vector art scenes (each draws inside box x,y,w,h) ----
def art_tariffs(d, x, y, w, h):
    # Port + tariff-rate containers: reads instantly at 300px.
    # v7: every rate bar carries its country (China 20%, EU 15%,
    # Vietnam 35%, hanging Japan 15%) - deck: EU/Japan/Korea/Taiwan 15%.
    d.rectangle([x, y, x + w, y + h], fill=(233, 196, 106))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=BROWN)
    # big % stamp, top left
    d.ellipse([x + 8, y + 2, x + 40, y + 34], fill=NAVY)
    d.text((x + 14, y + 8), "%", font=font(20, bold=True), fill=MUSTARD)
    # country-labelled containers along the quay
    rates = [("20%", "CHINA", CORAL), ("15%", "EU", TEAL),
             ("35%", "VIETNAM", NAVY)]
    for i, (lab, country, col) in enumerate(rates):
        bx = x + 46 + i * 58
        by = y + h - 42
        d.rectangle([bx, by, bx + 52, by + 34], fill=col,
                    outline=WHITE, width=2)
        fnt = font(11, bold=True)
        d.text((bx + 26 - d.textlength(lab, font=fnt) / 2, by + 4), lab,
               font=fnt, fill=WHITE)
        cfnt = font(7, bold=True)
        d.text((bx + 26 - d.textlength(country, font=cfnt) / 2, by + 20),
               country, font=cfnt, fill=WHITE)
    # v8: stacked container on the EU box + red up-arrow over China
    d.rectangle([x + 104, y + h - 54, x + 156, y + h - 42], fill=MUSTARD,
                outline=WHITE, width=2)
    sfnt = font(7, bold=True)
    d.text((x + 130 - d.textlength("15%", font=sfnt) / 2, y + h - 52),
           "15%", font=sfnt, fill=NAVY)
    ax = x + 72
    d.polygon([(ax - 6, y + h - 47), (ax + 6, y + h - 47), (ax, y + h - 54)],
              fill=RED)
    d.rectangle([ax - 2, y + h - 47, ax + 2, y + h - 42], fill=RED)
    # gantry crane, right: mast, jib, cable, hanging container (Japan 15%)
    d.rectangle([x + w - 52, y + 4, x + w - 46, y + h - 8], fill=NAVY)
    d.rectangle([x + w - 108, y + 4, x + w - 40, y + 10], fill=NAVY)
    d.line([x + w - 84, y + 10, x + w - 84, y + h - 37], fill=NAVY, width=2)
    hx = x + w - 102
    hy = y + h - 37
    d.rectangle([hx, hy, hx + 36, hy + 22], fill=CORAL,
                outline=WHITE, width=2)
    hfnt = font(8, bold=True)
    d.text((hx + 18 - d.textlength("15%", font=hfnt) / 2, hy + 2), "15%",
           font=hfnt, fill=WHITE)
    hcfnt = font(6, bold=True)
    d.text((hx + 18 - d.textlength("JAPAN", font=hcfnt) / 2, hy + 12),
           "JAPAN", font=hcfnt, fill=WHITE)


def art_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=RED)
    # v8: faint gridlines + KOSPI label + big down-arrow at the drop
    for gy in (y + h // 3, y + 2 * h // 3):
        d.line([x + 4, gy, x + w - 4, gy], fill=(255, 150, 150), width=1)
    kfnt = font(9, bold=True)
    lab = "KOSPI 4,697.51"
    d.text((x + w - 8 - d.textlength(lab, font=kfnt), y + 3), lab,
           font=kfnt, fill=WHITE)
    d.line([(x + 8, y + 10), (x + w // 3, y + 16), (x + 2 * w // 3, y + 30),
            (x + w - 10, y + h - 8)], fill=WHITE, width=4)
    for px, py in [(x + 8, y + 10), (x + w // 3, y + 16),
                   (x + 2 * w // 3, y + 30), (x + w - 10, y + h - 8)]:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=MUSTARD)
    d.text((x + 10, y + h - 20), "−6.2%", font=font(15, bold=True),
           fill=WHITE)
    ex, ey = x + w - 10, y + h - 8
    d.rectangle([ex - 20, ey - 26, ex - 16, ey - 14], fill=MUSTARD)
    d.polygon([(ex - 24, ey - 14), (ex - 12, ey - 14), (ex - 18, ey - 4)],
              fill=MUSTARD)


def art_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    for sx, sy in [(14, 12), (40, 26), (70, 8), (w - 30, 16),
                   (w - 52, 34), (24, 18), (w - 18, 52)]:
        d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=WHITE)
    # v8: station module, top right (capsule + solar wing + windows) and
    # a floating astronaut, mid-left - the docking reads at a glance
    d.rectangle([x + w - 128, y + 11, x + w - 102, y + 15], fill=BLUE,
                outline=WHITE, width=1)
    d.rounded_rectangle([x + w - 100, y + 8, x + w - 8, y + 18], radius=5,
                        fill=(210, 210, 210), outline=WHITE, width=1)
    for wx in (x + w - 88, x + w - 64, x + w - 40):
        d.ellipse([wx - 2, y + 11, wx + 2, y + 15], fill=NAVY)
    d.ellipse([x + 42, y + 20, x + 54, y + 32], fill=WHITE,
              outline=NAVY, width=1)
    d.ellipse([x + 45, y + 23, x + 51, y + 29], fill=NAVY)
    d.rectangle([x + 41, y + 32, x + 55, y + 40], fill=WHITE,
                outline=NAVY, width=1)
    d.rectangle([x + 56, y + 34, x + 60, y + 40], fill=CORAL)
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
    # v7: font 8 - font 9 ran the "K" of DOCK into the rocket flame
    # (145.7px vs 129.5px); the real v6 defect was the star at (24,48)
    # overlapping "00", already moved to (24,18) above.
    d.text((x + 6, y + h - 13), "00:18 LAUNCH  •  03:56 DOCK",
           font=font(8, bold=True), fill=MUSTARD)


def art_island(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # v9: TWO flags on the hilltop (a pact, not one flag) + gold coin;
    # hill lowered so the flags have sky above them and read at 300px.
    d.polygon([(x + 6, y + h), (x + int(w * 0.25), y + int(h * 0.62)),
               (x + w // 2, y + int(h * 0.52)),
               (x + int(w * 0.75), y + int(h * 0.62)), (x + w - 6, y + h)],
              fill=TEAL)
    # flagpoles + flags: mustard (Solomons) left, navy + star (Australia)
    for px, col in [(x + w // 2 - 22, MUSTARD), (x + w // 2 + 4, NAVY)]:
        d.line([px, y + 2, px, y + int(h * 0.55)], fill=NAVY, width=2)
        d.rectangle([px, y + 2, px + 18, y + 11], fill=col, outline=WHITE,
                    width=1)
    # white star on each flag
    for sx in (x + w // 2 - 13, x + w // 2 + 13):
        d.ellipse([sx - 2, y + 4, sx + 2, y + 8], fill=WHITE)
    # v8: gold coin for the A$740m + birds in the sky
    d.ellipse([x + w - 30, y + 3, x + w - 12, y + 21], fill=MUSTARD,
              outline=NAVY, width=1)
    d.text((x + w - 24, y + 6), "$", font=font(11, bold=True), fill=NAVY)
    for bx, by in [(x + 12, y + 8), (x + 26, y + 14)]:
        d.arc([bx, by, bx + 8, by + 5], 180, 360, fill=NAVY, width=1)


def art_strikes(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # v9: starburst blasts + brighter smoke + a heavier lightning bolt,
    # so the strike reads at 300px; KYIV stays clear at bottom left.
    for sx, sy, r in [(x + 26, y + 6, 5), (x + w - 30, y + 7, 5)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(205, 205, 205))
    # lightning bolt, right - wider and taller than v8
    d.polygon([(x + w - 18, y + 2), (x + w - 8, y + 2), (x + w - 14, y + 12),
               (x + w - 9, y + 12), (x + w - 19, y + 26),
               (x + w - 14, y + 26), (x + w - 11, y + 15),
               (x + w - 16, y + 15)], fill=MUSTARD)
    for cx, cy, r in [(x + w // 4, y + h // 3 + 2, 10),
                      (x + w // 2, y + h // 2 + 1, 13),
                      (x + 3 * w // 4, y + h // 3 + 2, 9)]:
        pts = []
        for i in range(16):
            ang = math.pi * i / 8
            rr = r if i % 2 == 0 else r * 0.55
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.polygon(pts, fill=CORAL)
        d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2],
                  fill=MUSTARD)
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(20, 30, 55))
    d.text((x + 6, y + h - 22), "KYIV", font=font(9, bold=True), fill=WHITE)


def art_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    cx, cy = x + w // 2, y + h // 2 - 2
    d.line([cx - 22, cy - 8, cx + 22, cy - 8], fill=NAVY, width=2)
    d.line([cx - 22, cy + 6, cx + 22, cy + 6], fill=NAVY, width=2)
    for px, py in [(cx - 24, cy - 8), (cx + 24, cy - 8),
                   (cx - 24, cy + 6), (cx + 24, cy + 6)]:
        d.ellipse([px - 5, py - 2, px + 5, py + 2], fill=GREY)
    d.rectangle([cx - 12, cy - 7, cx + 12, cy + 7], fill=NAVY)
    d.ellipse([cx - 4, cy - 3, cx + 4, cy + 3], fill=RED)
    d.line([cx + 16, cy + 10, cx + 30, cy + 14], fill=RED, width=2)
    d.line([cx + 30, cy + 14, cx + 22, cy + 16], fill=RED, width=2)
    # v8: intercept burst where the drone is hit
    bx, by = cx + 28, cy + 4
    d.polygon([(bx, by - 7), (bx + 2, by - 2), (bx + 7, by - 2),
               (bx + 3, by + 2), (bx + 5, by + 7), (bx, by + 4),
               (bx - 5, by + 7), (bx - 3, by + 2), (bx - 7, by - 2),
               (bx - 2, by - 2)], fill=MUSTARD, outline=RED)


def art_energy(d, x, y, w, h):
    # v8: the bill itself - old figure struck through, new figure bold
    d.rectangle([x, y, x + w, y + h], fill=MUSTARD)
    d.rounded_rectangle([x + 6, y + 4, x + 122, y + h - 4], radius=4,
                        fill=WHITE, outline=NAVY, width=1)
    ofnt = font(10)
    d.text((x + 12, y + h // 2 - 6), "£1,723", font=ofnt, fill=GREY)
    ow = d.textlength("£1,723", font=ofnt)
    d.line([x + 12, y + h // 2 - 1, x + 12 + ow, y + h // 2 - 1],
           fill=RED, width=2)
    d.text((x + 14 + ow, y + h // 2 - 6), "→", font=ofnt, fill=NAVY)
    d.text((x + 30 + ow, y + h // 2 - 7), "£2,166",
           font=font(11, bold=True), fill=NAVY)
    d.text((x + w - 52, y + h - 16), "+26%", font=font(11, bold=True),
           fill=RED)


def art_wage(d, x, y, w, h):
    # v8: shirt + the verified range 12,500 -> 17,000 taka ($100 -> $136)
    d.rectangle([x, y, x + w, y + h], fill=GREEN)
    d.rectangle([x + 8, y + 3, x + w - 8, y + h - 3], fill=CREAM,
                outline=NAVY, width=2)
    sx, sy = x + 12, y + 6
    d.polygon([(sx + 8, sy), (sx + 16, sy), (sx + 22, sy + 3),
               (sx + 28, sy + 8), (sx + 22, sy + 12), (sx + 22, sy + 18),
               (sx + 2, sy + 18), (sx + 2, sy + 12), (sx - 4, sy + 8),
               (sx + 2, sy + 3)], fill=WHITE, outline=NAVY)
    d.text((x + 52, y + 7), "12,500 → 17,000", font=font(10, bold=True),
           fill=NAVY)
    d.text((x + 52, y + 18), "($100 → $136)", font=font(7), fill=NAVY)


def art_mine(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=BROWN)
    d.rectangle([x + w // 2 - 12, y + 4, x + w // 2 + 12, y + h - 6],
                fill=(40, 26, 10))
    for i in range(3):
        yy = y + int(h * (0.30 + i * 0.22))
        d.arc([x + 6, yy, x + w - 6, yy + 10], 180, 360, fill=SKY, width=2)
    d.ellipse([x + 8, y + 6, x + 18, y + 16], fill=MUSTARD)
    # v8: flood water zigzag at the shaft base + a miner's helmet, top right
    cx = x + w // 2
    d.line([(cx - 12, y + h - 12), (cx - 6, y + h - 15), (cx, y + h - 12),
            (cx + 6, y + h - 15), (cx + 12, y + h - 12)], fill=SKY, width=2)
    d.pieslice([x + w - 26, y + 4, x + w - 12, y + 16], 180, 360,
               fill=MUSTARD, outline=NAVY)
    d.rectangle([x + w - 26, y + 15, x + w - 12, y + 17], fill=MUSTARD,
                outline=NAVY)


def art_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(120, 120, 120))
    # v9: the strike reads - spiked blasts over the rooftops + smoke
    # drifting in the open sky right of the buildings (v8 puffs were
    # hidden behind the buildings / clipped at the box top).
    for i, bh in enumerate([20, 30, 24]):
        bx = x + 10 + i * 22
        d.rectangle([bx, y + h - 6 - bh, bx + 18, y + h - 6], fill=NAVY2)
        d.rectangle([bx + 5, y + h - 6 - bh + 5, bx + 13,
                     y + h - 6 - bh + 11], fill=MUSTARD)
    # smoke as one overlapping cloud, not three separate dots (v9 rev:
    # separate dots read as pebbles in the grey sky)
    for sx, sy, r in [(x + 116, y + 9, 6), (x + 126, y + 6, 6),
                      (x + 137, y + 9, 5)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(70, 70, 70))
    # starburst blast, right, bursting over the rooftops
    cx, cy, r = x + w - 18, y + 14, 11
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.55
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=CORAL)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=MUSTARD)
    # second smaller burst, centred on the third building's roof
    # (v9 rev: was straddling the building's edge and read as a blob)
    cx2, cy2, r2 = x + 63, y + 11, 7
    pts2 = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r2 if i % 2 == 0 else r2 * 0.55
        pts2.append((cx2 + rr * math.cos(ang), cy2 + rr * math.sin(ang)))
    d.polygon(pts2, fill=(255, 140, 0))
    d.ellipse([cx2 - 3, cy2 - 3, cx2 + 3, cy2 + 3], fill=MUSTARD)


def art_scales(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    cx = x + w // 2
    d.line([cx, y + 6, cx, y + h - 8], fill=MUSTARD, width=2)
    d.line([cx - 20, y + 10, cx + 20, y + 10], fill=MUSTARD, width=2)
    for px in (cx - 20, cx + 20):
        d.line([px, y + 10, px, y + 18], fill=MUSTARD, width=1)
        d.polygon([(px - 8, y + 18), (px + 8, y + 18), (px, y + 26)],
                  fill=MUSTARD)
    d.rectangle([cx - 12, y + h - 8, cx + 12, y + h - 4], fill=MUSTARD)
    # v8: gavel at the base, right
    d.line([x + w - 36, y + h - 10, x + w - 16, y + h - 20], fill=BROWN,
           width=3)
    d.rectangle([x + w - 20, y + h - 26, x + w - 10, y + h - 18],
                fill=BROWN)


def art_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY2)
    d.polygon([(x + 6, y + 10), (x + w - 6, y + 10), (x + w // 2, y + 2)],
              fill=WHITE)
    for i in range(4):
        bx = x + 10 + i * 18
        d.rectangle([bx, y + 12, bx + 8, y + h - 6], fill=WHITE)
    d.rectangle([x + 6, y + h - 6, x + w - 6, y + h - 2], fill=WHITE)
    # v8: gold star on the pediment + gavel on the steps, right
    cx = x + w // 2
    d.polygon([(cx, y + 3), (cx + 2, y + 7), (cx + 6, y + 7), (cx + 3, y + 10),
               (cx + 4, y + 14), (cx, y + 11), (cx - 4, y + 14),
               (cx - 3, y + 10), (cx - 6, y + 7), (cx - 2, y + 7)],
              fill=MUSTARD)
    d.line([x + w - 30, y + h - 10, x + w - 14, y + h - 18], fill=MUSTARD,
           width=3)
    d.rectangle([x + w - 18, y + h - 22, x + w - 10, y + h - 16],
                fill=MUSTARD)


def art_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 40, 40))
    # v9: the fire reads - two tall flame tongues over the cab/tank +
    # smoke drifting left (v8 flames were one flat blob at the edge).
    for sx, sy, r in [(x + w - 78, y + 6, 5), (x + w - 62, y + 5, 4)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(95, 95, 95))
    # main flame: wide orange tongues ABOVE the cab roofline (v9 rev:
    # coral flames vanished against the coral cab - orange + mustard
    # core now contrasts, and the flame is wider than the cab).
    fx = x + w - 22
    d.polygon([(fx - 16, y + h - 10), (fx - 12, y + 6), (fx - 7, y + 1),
               (fx - 2, y + 6), (fx + 3, y + 1), (fx + 8, y + 6),
               (fx + 14, y + 2), (fx + 16, y + h - 10)],
              fill=(255, 140, 0))
    d.polygon([(fx - 9, y + h - 10), (fx - 5, y + 8), (fx - 1, y + 3),
               (fx + 4, y + 8), (fx + 9, y + h - 10)], fill=MUSTARD)
    # second tongue, left of the main flame, over the tank
    fx2 = x + w - 48
    d.polygon([(fx2 - 8, y + h - 10), (fx2 - 5, y + 8), (fx2, y + 2),
               (fx2 + 5, y + 8), (fx2 + 8, y + h - 10)], fill=(255, 140, 0))
    d.ellipse([fx2 - 3, y + h - 18, fx2 + 3, y + h - 10], fill=MUSTARD)
    d.rectangle([x + 8, y + h - 22, x + w - 36, y + h - 10], fill=(200, 200, 200))
    d.rectangle([x + 8, y + h - 16, x + w - 36, y + h - 13], fill=RED)
    d.rectangle([x + w - 34, y + h - 20, x + w - 10, y + h - 10], fill=CORAL)
    for wx in (x + 16, x + w - 44, x + w - 20):
        d.ellipse([wx - 4, y + h - 10, wx + 4, y + h - 2], fill=INK)


ART = {"tariffs": art_tariffs, "chart": art_chart, "rocket": art_rocket,
       "island": art_island, "strikes": art_strikes, "drone": art_drone,
       "energy": art_energy, "wage": art_wage, "mine": art_mine,
       "gaza": art_gaza, "scales": art_scales, "court": art_court,
       "tanker": art_tanker}


def draw_hero(d, s, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=NAVY, width=2)
    d.rectangle([x, y, x + w, y + 17], fill=NAVY)
    d.text((x + 8, y + 3), s["kicker"], font=font(8, bold=True), fill=MUSTARD)
    hy = y + 21
    hf = fit_size(d, s["headline"], w - 16, 18, 15, bold=True, max_lines=2)
    hy = text_block(d, x + 8, hy, s["headline"], hf, INK, w - 16, leading=20)
    deck_y = y + h - 56
    why_y = y + h - 30
    ART[s["art"]](d, x + 8, hy + 3, w - 16, max(deck_y - 5 - (hy + 3), 20))
    text_block(d, x + 8, deck_y, s["deck"], font(11), INK, w - 16,
               leading=12)
    why = "WHY IT MATTERS: " + s["why"]
    wfnt = font(9)
    if d.textlength(why, font=wfnt) > w - 16:
        wfnt = font(8)
    d.text((x + 8, why_y), why, font=wfnt, fill=RED)
    d.text((x + 8, y + h - 14), s["source"], font=font(8, bold=True),
           fill=GREY)
    label = VER_LABELS[s["ver"]]
    fnt = font(8, bold=True)
    cw = int(d.textlength(label, font=fnt)) + 10
    ver_chip(d, x + w - 8 - cw, y + h - 15, label)


def draw_small(d, s, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=NAVY, width=1)
    # number badge, top left
    d.ellipse([x + 4, y + 4, x + 22, y + 22], fill=RED, outline=WHITE,
              width=1)
    fnt = font(9, bold=True)
    num = str(s["num"])
    d.text((x + 13 - d.textlength(num, font=fnt) / 2, y + 7), num,
           font=fnt, fill=WHITE)
    # stat chip, top right
    fnt = font(7, bold=True)
    cw = int(d.textlength(s["stat"], font=fnt)) + 10
    d.rounded_rectangle([x + w - 4 - cw, y + 5, x + w - 4, y + 18], radius=6,
                        fill=NAVY)
    d.text((x + w - 4 - cw + 5, y + 7), s["stat"], font=fnt, fill=WHITE)
    # kicker
    d.text((x + 6, y + 25), s["kicker"], font=font(7, bold=True), fill=NAVY)
    hy = y + 36
    hf = fit_size(d, s["headline"], w - 12, 14, 12, bold=True, max_lines=2)
    hy = text_block(d, x + 6, hy, s["headline"], hf, INK, w - 12,
                    leading=15)
    deck_y = y + h - 25
    ART[s["art"]](d, x + 6, hy + 3, w - 12, max(deck_y - 3 - (hy + 3), 18))
    text_block(d, x + 6, deck_y, s["deck"], font(10), INK, w - 12,
               leading=11)


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
    # Solomon Islands (v7: pin 7 sits on this blob, NE of Australia)
    [(153, -6), (156, -4), (160, -5), (164, -7), (165, -10), (162, -13),
     (157, -13), (153, -10)],
    # Java strip, thickened (v9): the v8 strip read as a sliver at 300px
    # and pin 9 looked attached to New Guinea; this bar makes Java read
    # as its own long island under the pin.
    [(104, -5.0), (108, -5.5), (112, -6.0), (116, -6.5),
     (120, -7.0), (122, -7.5), (122, -10.5), (118, -10.0),
     (114, -9.5), (110, -9.0), (106, -8.5), (104, -8.0)],
    [(114, -22), (114, -30), (115, -34), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
     (146, -19), (142, -15), (142, -11), (140, -17), (136, -15),
     (135, -12), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (114, -22)],
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
     (174, -41), (172, -43), (168, -46)],
]

# pins: (story, lon, lat, dx, dy) - dx/dy nudge the drawn pin off the true
# spot so the Gaza / Jerusalem / Giza cluster does not collide. Every nudged
# centre still sits on drawn land (v7: verified from RENDER pixels - centre
# + r=3 ring on green land for all 13 pins; v6 lon/lat-only check was wrong).
PINS = [
    (1, -77.0, 39.0, 0, 0),      # Washington
    (2, 127.0, 37.5, -8, -2),    # Seoul: nudged onto mainland China (v7)
    (3, 98.5, 39.8, 0, 0),       # Jiuquan
    (4, 30.5, 50.4, 0, 4),       # Kyiv: nudged down 4 (v9, was on the
                                 # map's top land edge)
    (5, 50.1, 26.6, 8, 0),       # Ras Tanura
    (6, -0.1, 51.5, 5, 5),       # London: nudged onto mainland Europe (v7),
                                 # down 4 more (v9, was on the top edge)
    (7, 159.0, -8.5, 0, 0),      # Solomon Islands (v7: was Canberra, pin sat
                                 # in the sea SE of Australia; story is the
                                 # Solomons pact, pinned on the Solomons blob)
    (8, 90.4, 23.8, 0, 0),       # Dhaka
    (9, 106.8, -6.6, 0, -4),     # Bogor: nudged to mid-Java strip (v7);
                                 # v9: dy -7 -> -4, sits mid thickened strip
    (10, 34.5, 31.5, -18, 20),   # Gaza City
    (11, 18.4, -33.9, 4, -6),    # Cape Town: nudged inland off the tip (v7)
    (12, 35.2, 31.8, 12, -12),   # Jerusalem
    (13, 31.2, 30.0, 2, 20),     # Giza
]

PIN_R = 7


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=NAVY, width=1)
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 75.0, -55.0

    def px(lon, lat):
        return (x + (lon - lon0) / (lon1 - lon0) * w,
                y + (lat0 - lat) / (lat0 - lat1) * h)

    for poly in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND)
    for num, lon, lat, dx, dy in PINS:
        story = STORIES[num - 1]
        tx, ty = px(lon, lat)
        cx, cy = tx + dx, ty + dy
        if dx or dy:
            d.line([tx, ty, cx, cy], fill=NAVY, width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=NAVY)
        d.ellipse([cx - PIN_R, cy - PIN_R, cx + PIN_R, cy + PIN_R],
                  fill=REGION_COLORS[story["region"]], outline=WHITE,
                  width=2)
        fnt = font(7, bold=True)
        tw = d.textlength(str(num), font=fnt)
        d.text((cx - tw / 2, cy - 5), str(num), font=fnt, fill=WHITE)
    d.rectangle([x, y, x + w, y + h], outline=NAVY, width=1)


def draw_legend(d, x, y):
    # 10 regions, 2 columns x 5 rows
    fnt = font(7, bold=True)
    for i, name in enumerate(REGION_ORDER):
        col, row = divmod(i, 5)
        lx = x + col * 170
        ly = y + row * 12
        d.ellipse([lx, ly, lx + 8, ly + 8], fill=REGION_COLORS[name],
                  outline=NAVY, width=1)
        d.text((lx + 11, ly), name, font=fnt, fill=INK)


# ---- compose ----
def build():
    n = len(STORIES)
    regions = Counter(s["region"] for s in STORIES)
    fields = Counter(s["field"] for s in STORIES)
    assert n == 50, n
    assert sum(regions.values()) == 50, regions
    assert sum(fields.values()) == 50, fields
    assert set(regions) == set(REGION_ORDER), set(regions) ^ set(REGION_ORDER)
    assert set(fields) == set(FIELD_ORDER), set(fields) ^ set(FIELD_ORDER)
    assert sorted(s["num"] for s in STORIES) == list(range(1, 51))
    print("stories:", n, "| regions:", dict(regions), "| fields:",
          dict(fields))

    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # navy top strip
    d.rectangle([0, 0, W, 24], fill=NAVY)
    d.text((12, 6), "THE WORLD IN ONE DAY", font=font(9, bold=True),
           fill=WHITE)
    strip = ("%d STORIES  •  %d REGIONS  •  %d FIELDS  •  ALL FIRST REPORTED "
             "ON WEDNESDAY 25 NOVEMBER 2026"
             % (n, len(REGION_ORDER), len(FIELD_ORDER)))
    d.text((W - 12 - d.textlength(strip, font=font(9, bold=True)), 6), strip,
           font=font(9, bold=True), fill=MUSTARD)

    # giant serif masthead
    mf = font(38, bold=True, serif=True)
    title = "Wednesday 25 November 2026"
    d.text((W // 2 - d.textlength(title, font=mf) / 2, 28), title,
           font=mf, fill=NAVY)

    # red subhead: the 3 top stories
    sub = ("US tariffs up to 20%  •  Kospi closes −6.2%  •  "
           "Pakistan's first astronaut docks at Tiangong")
    sf = font(12, serif=True)
    d.text((W // 2 - d.textlength(sub, font=sf) / 2, 72), sub, font=sf,
           fill=RED)

    # region bar: coloured chips, counts from STORIES
    chips = []
    fnt = font(8, bold=True)
    total = 0
    for name in REGION_ORDER:
        label = "%s %d" % (name, regions[name])
        chips.append((label, int(d.textlength(label, font=fnt)) + 12))
        total += chips[-1][1] + 6
    total -= 6
    cx = (W - total) // 2
    for (label, cw), name in zip(chips, REGION_ORDER):
        d.rounded_rectangle([cx, 90, cx + cw, 108], radius=8,
                            fill=REGION_COLORS[name])
        d.text((cx + 6, 94), label, font=fnt,
               fill=REGION_TEXT.get(name, WHITE))
        cx += cw + 6

    # 21 fields row (2 lines, centred)
    # non-breaking space keeps each "Field N" pair on one line
    field_text = "21 FIELDS — " + "  •  ".join(
        "%s %d" % (f, fields[f]) for f in FIELD_ORDER)
    text_block(d, 12, 112, field_text, font(8), INK, 1000, leading=11,
               align="center")

    # 5 big numbers
    bw = (W - 24 - 4 * 6) // 5
    for i, (num, lab) in enumerate(NUMBERS):
        bx = 12 + i * (bw + 6)
        d.rectangle([bx, 138, bx + bw, 172], fill=WHITE, outline=NAVY,
                    width=1)
        nf = fit_size(d, num, bw - 10, 22, 16, bold=True, max_lines=1)
        d.text((bx + bw // 2 - d.textlength(num, font=nf) / 2, 140), num,
               font=nf, fill=NAVY)
        text_block(d, bx + 4, 162, lab, font(7, bold=True), GREY, bw - 8,
                   leading=8, align="center")

    # heroes
    hw = (W - 24 - 12) // 3
    for i, s in enumerate(HEROES):
        draw_hero(d, s, 12 + i * (hw + 6), 176, hw, 180)

    # small panels, 2 rows of 5
    sw = (W - 24 - 4 * 6) // 5
    for i, s in enumerate(SMALLS):
        row, col = divmod(i, 5)
        draw_small(d, s, 12 + col * (sw + 6), 360 + row * 132, sw, 128)

    # map + ALSO ON
    d.text((12, 626), "WHERE IT HAPPENED", font=font(11, bold=True),
           fill=NAVY)
    d.text((348, 626), "ALSO ON 14–50", font=font(11, bold=True), fill=NAVY)
    draw_map(d, 12, 644, 330, 180)
    draw_legend(d, 12, 830)
    colw2 = (1012 - 348 - 12) // 2
    for i, s in enumerate(ALSO_ON):
        col, row = divmod(i, 19)
        ax = 348 + col * (colw2 + 12)
        ay = 644 + row * 13
        full = "%d. %s — %s %s" % (s["num"], s["text"], s["source"],
                                   s["ver"])
        size = 9
        while size > 7:
            fnt = font(size)
            if d.textlength(full, font=fnt) <= colw2:
                break
            size -= 1
        d.text((ax, ay), full, font=font(size), fill=INK)

    # DATE CHECK
    d.rectangle([12, 892, 1012, 976], fill=(255, 235, 235), outline=RED,
                width=1)
    text_block(d, 18, 895, DATE_CHECK, font(8), INK, 988, leading=10)

    # footer
    text_block(d, 12, 980, FOOTER, font(8), GREY, 1000, leading=10)

    img.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
