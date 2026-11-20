#!/usr/bin/env python3
"""Build the entry image for make.fun's news-image-20261120 bounty.

Draws a one-page newspaper, "The World in One Day", summing up the
world news of Friday 20 November 2026 in a single 1024x1024 PNG.

Stories (all reported on 20 November 2026):
  * Shenzhen: Trump, Xi and Putin hold the first US-China-Russia
    three-way summit at APEC; a symbolic peace declaration reaffirming
    that nuclear war must never be fought, but no arms-control plan
    and no progress on Ukraine, Iran or Taiwan (Reuters, 20 Nov).
  * Kyiv: a Russian barrage damages the Austrian and Dutch embassies
    and a cathedral; the EU summons Moscow's envoy and the UK pledges
    1,000+ drones in a GBP 260m package (SCMP / press reports, 20 Nov).
  * The Hague: the World Court rules Myanmar committed genocide
    against the Rohingya; the UN chief urges Myanmar to bring the
    Rohingya home (Bangkok Post / UN reports, 20 Nov).
  * Riyadh: a Houthi missile hits Riyadh's tallest skyscraper; oil
    prices edge higher on supply concerns (SCMP / Reuters, 20 Nov).
  * Antalya: COP31 enters its final day with fossil fuels stripped
    from the draft deal (Reuters / Dawn, 20 Nov).
  * Space: NASA's Voyager 1 phones home from one light-day away,
    about 26 billion km, 49 years after launch (AP / Reuters, 20 Nov).
  * Markets: Anthropic's record $81bn IPO at a $1.5tn valuation,
    shares up 17% on debut (Reuters / Jiji, 20 Nov).
  * Ticker: Seoul court upholds Kakao founder's acquittal; Taiwan
    flags 2,700 China-linked accounts before local elections.

The drawing is done at 2x and downscaled for clean edges.
Only the Python standard library and Pillow (build-time tool) are
used; the submitted program (main.py) simply copies the result.
"""

from PIL import Image, ImageDraw, ImageFont

S = 2  # supersampling factor
W = 1024 * S

PAPER = (247, 243, 233)
INK = (18, 30, 43)
NAVY = (22, 50, 79)
RED = (178, 44, 32)
GOLD = (176, 132, 40)
GREY = (84, 92, 102)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/noto/"
SERIF_BLACK = FONT_DIR + "NotoSerif-Black.ttf"
SANS_BLACK = FONT_DIR + "NotoSans-Black.ttf"
SANS_XBOLD = FONT_DIR + "NotoSans-ExtraBold.ttf"
SANS_BOLD = FONT_DIR + "NotoSans-Bold.ttf"
SANS_SEMI = FONT_DIR + "NotoSans-SemiBold.ttf"
SANS_REG = FONT_DIR + "NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size * S)


def xy(box):
    return tuple(int(v * S) for v in box)


class Canvas:
    def __init__(self):
        self.img = Image.new("RGB", (W, W), PAPER)
        self.d = ImageDraw.Draw(self.img)

    def rect(self, box, fill=None, outline=None, width=1):
        self.d.rectangle(xy(box), fill=fill, outline=outline,
                         width=int(width * S))

    def rrect(self, box, radius, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(xy(box), radius=radius * S, fill=fill,
                                 outline=outline, width=int(width * S))

    def line(self, pts, fill=INK, width=2):
        self.d.line([(int(x * S), int(y * S)) for x, y in pts],
                    fill=fill, width=int(width * S))

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.d.ellipse(xy(box), fill=fill, outline=outline,
                       width=int(width * S))

    def poly(self, pts, fill=None, outline=None):
        self.d.polygon([(int(x * S), int(y * S)) for x, y in pts],
                       fill=fill, outline=outline)

    def text(self, pos, s, fnt, fill=INK, anchor="la", spacing=4):
        self.d.text((pos[0] * S, pos[1] * S), s, font=fnt, fill=fill,
                    anchor=anchor, spacing=spacing * S)

    def textw(self, s, fnt):
        return self.d.textlength(s, font=fnt) / S


def wrap(c, s, fnt, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if c.textw(trial, fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def block(c, pos, s, fnt, maxw, leading, fill=INK):
    x, y = pos
    for ln in wrap(c, s, fnt, maxw):
        c.text((x, y), ln, fnt, fill=fill, anchor="la")
        y += leading
    return y


def spaced(c, pos, s, fnt, fill, gap=6, anchor_center_x=None):
    """Draw letter-spaced small caps text."""
    widths = [c.textw(ch, fnt) for ch in s]
    total = sum(widths) + gap * (len(s) - 1)
    x = pos[0] if anchor_center_x is None else anchor_center_x - total / 2
    for ch, w_ in zip(s, widths):
        c.text((x, pos[1]), ch, fnt, fill=fill, anchor="la")
        x += w_ + gap
    return total


# ---------------------------------------------------------------- flags
def flag_us(c, x, y, w, h):
    stripe = h / 7
    for i in range(7):
        col = (178, 44, 32) if i % 2 == 0 else WHITE
        c.rect((x, y + i * stripe, x + w, y + (i + 1) * stripe), fill=col)
    c.rect((x, y, x + w * 0.44, y + stripe * 4), fill=NAVY)
    r = w * 0.028
    for row in range(4):
        for col_i in range(5):
            cx = x + w * 0.05 + col_i * w * 0.085
            cy = y + stripe * 0.55 + row * stripe * 0.95
            c.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE)
    c.rect((x, y, x + w, y + h), outline=INK, width=1)


def flag_cn(c, x, y, w, h):
    c.rect((x, y, x + w, y + h), fill=(222, 41, 16))
    r = w * 0.09
    cx, cy = x + w * 0.16, y + h * 0.28
    c.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 222, 0))
    r2 = w * 0.04
    for dx, dy in ((0.30, 0.10), (0.34, 0.30), (0.34, 0.52), (0.28, 0.70)):
        px, py = x + w * dx, y + h * dy
        c.ellipse((px - r2, py - r2, px + r2, py + r2), fill=(255, 222, 0))
    c.rect((x, y, x + w, y + h), outline=INK, width=1)


def flag_ru(c, x, y, w, h):
    third = h / 3
    c.rect((x, y, x + w, y + third), fill=WHITE)
    c.rect((x, y + third, x + w, y + 2 * third), fill=(0, 57, 166))
    c.rect((x, y + 2 * third, x + w, y + h), fill=(213, 43, 30))
    c.rect((x, y, x + w, y + h), outline=INK, width=1)


def figure(c, cx, base, suit, shirt, skin, hair):
    """A simple seated leader figure, seen from the front."""
    c.ellipse((cx - 13, base - 74, cx + 13, base - 48), fill=skin)  # head
    c.poly([(cx - 14, base - 72), (cx + 14, base - 72),
            (cx + 13, base - 80), (cx - 13, base - 80)], fill=hair)
    c.poly([(cx - 30, base), (cx - 22, base - 44), (cx - 8, base - 50),
            (cx, base - 40), (cx + 8, base - 50), (cx + 22, base - 44),
            (cx + 30, base)], fill=suit)  # shoulders / suit
    c.poly([(cx - 8, base - 50), (cx + 8, base - 50),
            (cx, base - 38)], fill=shirt)  # shirt V
    c.poly([(cx - 3, base - 48), (cx + 3, base - 48),
            (cx + 2, base - 34), (cx - 2, base - 34)], fill=RED)  # tie


def hero_art(c, x, y, w, h):
    """Shenzhen skyline, three flags and three leaders at a round table."""
    c.rrect((x, y, x + w, y + h), 10, fill=(214, 228, 240))
    # skyline silhouette
    towers = [(0.02, 0.42, 0.10, 0.46), (0.13, 0.30, 0.09, 0.58),
              (0.24, 0.38, 0.08, 0.50), (0.72, 0.34, 0.09, 0.54),
              (0.83, 0.44, 0.08, 0.44), (0.92, 0.36, 0.07, 0.52)]
    for tx, ty, tw, th in towers:
        c.rect((x + w * tx, y + h * ty, x + w * (tx + tw),
                y + h * (ty + th)), fill=(120, 148, 175))
    c.rect((x, y + h * 0.88, x + w, y + h), fill=(96, 122, 148))
    # flags on poles
    fw, fh = w * 0.24, h * 0.17
    positions = [(x + w * 0.07, y + h * 0.07), (x + w * 0.38, y + h * 0.04),
                 (x + w * 0.69, y + h * 0.07)]
    for (fx, fy), fn in zip(positions, (flag_us, flag_cn, flag_ru)):
        c.line([(fx, fy + fh), (fx, fy + fh + 26)], fill=INK, width=3)
        fn(c, fx, fy, fw, fh)
    # round table
    tx0, ty0 = x + w * 0.16, y + h * 0.70
    tx1, ty1 = x + w * 0.84, y + h * 0.97
    c.ellipse((tx0, ty0, tx1, ty1), fill=(240, 235, 220), outline=INK,
              width=2)
    c.ellipse((tx0 + 14, ty0 + 6, tx1 - 14, ty1 - 6),
              outline=(190, 180, 150), width=1)
    # three leaders behind the table
    base = y + h * 0.78
    figure(c, x + w * 0.28, base, (38, 48, 66), WHITE,
           (232, 190, 160), (90, 70, 50))
    figure(c, x + w * 0.50, base, (30, 34, 44), WHITE,
           (238, 200, 165), (25, 25, 25))
    figure(c, x + w * 0.72, base, (52, 54, 60), WHITE,
           (240, 205, 175), (150, 145, 140))
    c.rrect((x, y, x + w, y + h), 10, outline=INK, width=2)


def masthead(c):
    c.line([(28, 30), (996, 30)], fill=INK, width=3)
    c.line([(28, 38), (996, 38)], fill=INK, width=1)
    f_small = font(SANS_BOLD, 21)
    spaced(c, (0, 46), "THE WORLD IN ONE DAY", f_small, RED, gap=8,
           anchor_center_x=512)
    f_date = font(SERIF_BLACK, 80)
    c.text((512, 72), "20 NOVEMBER 2026", f_date, fill=NAVY, anchor="ma")
    f_strap = font(SANS_SEMI, 23)
    c.text((512, 160),
           "Friday's world news in one picture — diplomacy, war, "
           "climate, space and markets",
           f_strap, fill=GREY, anchor="ma")
    c.line([(28, 192), (996, 192)], fill=INK, width=1)
    c.line([(28, 197), (996, 197)], fill=INK, width=3)


# ---------------------------------------------------------------- panels
def panel(c, box, tint, kicker, kcol, headline, sub, icon):
    x, y, w, h = box
    c.rrect((x, y, x + w, y + h), 10, fill=tint)
    icon(c, x + 16, y + 16, 104, 104)
    f_kick = font(SANS_XBOLD, 20)
    c.text((x + 136, y + 14), kicker, f_kick, fill=kcol, anchor="la")
    f_head = font(SANS_BLACK, 28)
    block(c, (x + 136, y + 38), headline, f_head, w - 152, 32)
    f_sub = font(SANS_SEMI, 19)
    block(c, (x + 16, y + 136), sub, f_sub, w - 32, 22,
          fill=(62, 70, 80))
    c.rrect((x, y, x + w, y + h), 10, outline=INK, width=2)


def icon_kyiv(c, x, y, w, h):
    c.rrect((x, y, x + w, y + h), 8, fill=(250, 226, 196))
    # cathedral with golden dome
    c.rect((x + 8, y + 58, x + 40, y + 96), fill=(238, 238, 232),
           outline=INK, width=2)
    c.poly([(x + 24, y + 22), (x + 38, y + 58), (x + 10, y + 58)],
           fill=GOLD, outline=INK)
    c.line([(x + 24, y + 10), (x + 24, y + 22)], fill=INK, width=3)
    # embassy block with cracked windows
    c.rect((x + 52, y + 34, x + 98, y + 96), fill=(196, 205, 216),
           outline=INK, width=2)
    for r_ in range(3):
        for col in range(2):
            wx, wy = x + 60 + col * 20, y + 42 + r_ * 18
            c.rect((wx, wy, wx + 12, wy + 11), fill=(90, 110, 135))
    c.line([(x + 60, y + 42), (x + 72, y + 53), (x + 66, y + 60)],
           fill=WHITE, width=2)  # crack
    # smoke
    c.ellipse((x + 56, y + 4, x + 84, y + 24), fill=(150, 150, 150))
    c.ellipse((x + 70, y + 0, x + 100, y + 20), fill=(170, 170, 170))


def icon_icj(c, x, y, w, h):
    c.rrect((x, y, x + w, y + h), 8, fill=(226, 236, 214))
    # courthouse roof and columns
    c.poly([(x + 52, y + 8), (x + 96, y + 32), (x + 8, y + 32)],
           fill=NAVY, outline=INK)
    c.ellipse((x + 46, y + 16, x + 58, y + 28), fill=WHITE)
    for i in range(4):
        cx = x + 16 + i * 22
        c.rect((cx, y + 38, cx + 10, y + 82), fill=WHITE, outline=INK,
               width=1)
    c.rect((x + 8, y + 84, x + 96, y + 94), fill=NAVY)
    # scales of justice in front
    cx = x + 52
    c.line([(cx, y + 44), (cx, y + 74)], fill=GOLD, width=4)
    c.line([(cx - 18, y + 50), (cx + 18, y + 50)], fill=GOLD, width=3)
    c.poly([(cx - 26, y + 62), (cx - 10, y + 62), (cx - 18, y + 72)],
           fill=GOLD, outline=INK)
    c.poly([(cx + 10, y + 62), (cx + 26, y + 62), (cx + 18, y + 72)],
           fill=GOLD, outline=INK)


def icon_riyadh(c, x, y, w, h):
    c.rrect((x, y, x + w, y + h), 8, fill=(252, 222, 214))
    # tallest tower
    c.poly([(x + 40, y + 96), (x + 44, y + 18), (x + 52, y + 6),
            (x + 60, y + 18), (x + 64, y + 96)], fill=(110, 130, 155),
           outline=INK)
    for i in range(5):
        wy = y + 26 + i * 13
        c.line([(x + 46, wy), (x + 58, wy)], fill=(210, 228, 244),
               width=3)
    # damaged band of windows
    c.poly([(x + 43, y + 52), (x + 61, y + 52), (x + 62, y + 64),
            (x + 42, y + 64)], fill=(60, 60, 66))
    c.line([(x + 46, y + 54), (x + 52, y + 60), (x + 58, y + 55)],
           fill=WHITE, width=2)
    # second building
    c.rect((x + 72, y + 56, x + 98, y + 96), fill=(150, 165, 185),
           outline=INK, width=2)
    # missile trail arcing in
    c.line([(x + 4, y + 8), (x + 22, y + 22), (x + 38, y + 40)],
           fill=RED, width=4)
    c.poly([(x + 34, y + 34), (x + 46, y + 44), (x + 32, y + 46)],
           fill=RED)
    c.ellipse((x + 0, y + 0, x + 12, y + 12), fill=GOLD)


def icon_cop(c, x, y, w, h):
    c.rrect((x, y, x + w, y + h), 8, fill=(208, 236, 226))
    # globe
    c.ellipse((x + 22, y + 16, x + 82, y + 76), fill=(86, 150, 200),
              outline=INK, width=2)
    c.poly([(x + 34, y + 30), (x + 48, y + 26), (x + 46, y + 40),
            (x + 34, y + 40)], fill=(92, 170, 110))
    c.poly([(x + 56, y + 46), (x + 72, y + 44), (x + 70, y + 60),
            (x + 58, y + 58)], fill=(92, 170, 110))
    # thermometer of a warming world
    c.rect((x + 88, y + 14, x + 96, y + 62), fill=WHITE, outline=INK,
           width=2)
    c.rect((x + 90, y + 26, x + 94, y + 62), fill=RED)
    c.ellipse((x + 84, y + 58, x + 100, y + 76), fill=RED, outline=INK,
              width=2)
    # factory with crossed-out smoke (fossil fuels struck from text)
    c.rect((x + 12, y + 80, x + 62, y + 98), fill=(120, 124, 130),
           outline=INK, width=2)
    c.rect((x + 18, y + 66, x + 26, y + 80), fill=(120, 124, 130),
           outline=INK, width=2)
    c.line([(x + 8, y + 62), (x + 44, y + 92)], fill=RED, width=5)
    c.line([(x + 44, y + 62), (x + 8, y + 92)], fill=RED, width=5)


# ---------------------------------------------------------------- minis
def icon_voyager(c, x, y, w, h):
    c.rrect((x, y, x + w, y + h), 8, fill=(24, 28, 58))
    # Earth, far away at lower left
    c.ellipse((x + 4, y + h - 18, x + 18, y + h - 4), fill=(86, 150, 200))
    # signal dashes from Earth to the probe
    for i in range(3):
        sx = x + 20 + i * 13
        sy = y + h - 16 - i * 11
        c.line([(sx, sy), (sx + 7, sy - 5)], fill=(255, 214, 90), width=3)
    # Voyager: big dish, bus and long boom
    cx, cy = x + w * 0.58, y + h * 0.38
    c.ellipse((cx - 17, cy - 17, cx + 17, cy + 17), fill=(238, 238, 238),
              outline=GOLD, width=3)
    c.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=GOLD)
    c.line([(cx + 10, cy + 12), (cx + 30, cy + 30)], fill=(200, 200, 200),
           width=4)  # boom
    c.line([(cx + 30, cy + 30), (cx + 44, cy + 22)], fill=(200, 200, 200),
           width=3)
    c.rect((cx + 26, cy + 26, cx + 36, cy + 36), fill=GOLD)  # bus
    # stars
    for sx, sy in ((8, 8), (30, 4), (64, 8), (58, 58), (12, 34)):
        c.ellipse((x + sx, y + sy, x + sx + 4, y + sy + 4),
                  fill=(255, 255, 255))


def icon_ipo(c, x, y, w, h):
    c.rrect((x, y, x + w, y + h), 8, fill=(255, 244, 205))
    base = y + h - 10
    c.line([(x + 8, base), (x + w - 6, base)], fill=INK, width=3)
    bars = [(14, 16, (110, 170, 110)), (32, 28, (84, 150, 96)),
            (50, 40, (52, 128, 74))]
    for bx, bh, col in bars:
        c.rect((x + bx, base - bh, x + bx + 13, base), fill=col,
               outline=INK, width=1)
    # rising arrow, kept inside the icon box
    c.line([(x + 12, base - 20), (x + 34, base - 34),
            (x + 52, base - 44), (x + 68, base - 56)], fill=RED, width=4)
    c.poly([(x + 56, base - 58), (x + 72, base - 58), (x + 66, base - 44)],
           fill=RED)


def mini(c, box, tint, kicker, kcol, headline, sub, icon):
    x, y, w, h = box
    c.rrect((x, y, x + w, y + h), 10, fill=tint)
    icon(c, x + 12, y + 12, 78, 78)
    f_kick = font(SANS_XBOLD, 16)
    c.text((x + 104, y + 8), kicker, f_kick, fill=kcol, anchor="la")
    f_head = font(SANS_BLACK, 24)
    block(c, (x + 104, y + 27), headline, f_head, w - 118, 26)
    f_sub = font(SANS_SEMI, 16)
    c.text((x + 104, y + 80), sub, f_sub, fill=(62, 70, 80), anchor="la")
    c.rrect((x, y, x + w, y + h), 10, outline=INK, width=2)


# ---------------------------------------------------------------- build
def build():
    c = Canvas()
    masthead(c)

    # HERO — Shenzhen three-way summit
    hx, hy, hw, hh = 28, 208, 968, 218
    c.rrect((hx, hy, hx + hw, hy + hh), 10, fill=(234, 240, 247))
    hero_art(c, hx + 14, hy + 14, 340, hh - 28)
    tx = hx + 378
    f_kick = font(SANS_XBOLD, 22)
    c.text((tx, hy + 14), "SHENZHEN • APEC — THE DAY'S TOP STORY",
           f_kick, fill=RED, anchor="la")
    f_head = font(SANS_BLACK, 39)
    block(c, (tx, hy + 44), "TRUMP, XI & PUTIN: FIRST THREE-WAY SUMMIT",
          f_head, hw - 402, 45)
    f_sub = font(SANS_SEMI, 20)
    block(c, (tx, hy + 140),
          "“Nuclear war must never be fought,” the three leaders agree "
          "in Shenzhen — but no deal on arms control, Ukraine, Iran or "
          "Taiwan. Trump rates it “12 out of 10.”",
          f_sub, hw - 402, 24, fill=(62, 70, 80))
    c.rrect((hx, hy, hx + hw, hy + hh), 10, outline=INK, width=2)

    pw = (968 - 16) / 2
    # ROW A
    panel(c, (28, 438, pw, 202), (253, 243, 228), "KYIV • UKRAINE", RED,
          "RUSSIAN BARRAGE HITS KYIV EMBASSIES",
          "Daytime strike damages the Austrian & Dutch missions and a "
          "cathedral. EU summons Moscow's envoy; UK pledges 1,000+ drones.",
          icon_kyiv)
    panel(c, (28 + pw + 16, 438, pw, 202), (240, 246, 232),
          "THE HAGUE • WORLD COURT", (46, 110, 60),
          "WORLD COURT: MYANMAR GENOCIDE",
          "ICJ rules Myanmar committed genocide against the Rohingya. "
          "UN: “Bring them home.” Malaysia resettles 10,000 Rohingya.",
          icon_icj)
    # ROW B
    panel(c, (28, 652, pw, 202), (253, 238, 234), "RIYADH • SAUDI ARABIA",
          RED, "HOUTHI MISSILE HITS RIYADH TOWER",
          "Windows blown out across eight floors of the capital's tallest "
          "tower, a second attack this month. Oil prices edge higher.",
          icon_riyadh)
    panel(c, (28 + pw + 16, 652, pw, 202), (232, 245, 240),
          "ANTALYA • COP31 CLIMATE TALKS", (16, 110, 96),
          "COP31 DRAFT ERASES FOSSIL FUELS",
          "Final-day draft drops every mention of fossil fuels and the "
          "$120bn adaptation fund; “35 by 35” electrification stays.",
          icon_cop)
    # MINI ROW
    mini(c, (28, 866, pw, 104), (233, 231, 247), "SPACE • NASA", NAVY,
         "VOYAGER 1 PHONES HOME FROM ONE LIGHT-DAY AWAY",
         "26 billion km out • launched 1977", icon_voyager)
    mini(c, (28 + pw + 16, 866, pw, 104), (255, 248, 224),
         "MARKETS • AI", (150, 100, 10),
         "ANTHROPIC IPO: RECORD $81BN RAISE",
         "Shares +17% on debut • $1.5 trillion valuation", icon_ipo)
    # TICKER
    c.rrect((28, 980, 996, 1016), 8, fill=NAVY)
    f_tick = font(SANS_BOLD, 18)
    c.text((512, 989),
           "ALSO: SEOUL UPHOLDS KAKAO FOUNDER'S ACQUITTAL • "
           "TAIWAN FLAGS 2,700 CHINA-LINKED ACCOUNTS",
           f_tick, fill=WHITE, anchor="ma")

    out = c.img.resize((1024, 1024), Image.LANCZOS)
    out.save("entry.png", optimize=True)
    print("wrote entry.png", out.size)


if __name__ == "__main__":
    build()
