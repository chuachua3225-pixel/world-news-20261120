#!/usr/bin/env python3
"""Version 2 of the front page for make.fun's "Sum up 20 November's
world news in one image" bounty (news-image-20261120).

Same reporting and words as build_entry.py, but the panels carry
rich painterly illustrations (the art-*.webp files in this repo,
drawn for this entry) instead of flat pictograms, so the page reads like an
illustrated newspaper front page. All type is still rendered in
code, so the date and headlines stay perfectly legible.

Drawn at 2x and downscaled to 1024x1024. If the PNG would exceed
the bounty's 1 MiB cap it is palette-quantised until it fits.
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

S = 2
SIZE = 1024 * S
PAPER = (243, 238, 226)
INK = (18, 30, 43)
NAVY = (22, 50, 79)
RED = (178, 44, 32)
GREEN = (46, 106, 72)
GREY = (84, 92, 102)
WHITE = (255, 255, 255)
LINE = (190, 182, 160)

FONT_DIR = "/usr/share/fonts/truetype/noto/"
SERIF_BLACK = FONT_DIR + "NotoSerif-Black.ttf"
SANS_BLACK = FONT_DIR + "NotoSans-Black.ttf"
SANS_XBOLD = FONT_DIR + "NotoSans-ExtraBold.ttf"
SANS_BOLD = FONT_DIR + "NotoSans-Bold.ttf"
SANS_SEMI = FONT_DIR + "NotoSans-SemiBold.ttf"
SANS_REG = FONT_DIR + "NotoSans-Regular.ttf"

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = HERE


def font(path, size):
    return ImageFont.truetype(path, int(size * S))


def sc(box):
    return tuple(int(v * S) for v in box)


class Canvas:
    def __init__(self):
        self.img = Image.new("RGB", (SIZE, SIZE), PAPER)
        self.d = ImageDraw.Draw(self.img)

    def rrect(self, box, radius, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(sc(box), radius=int(radius * S),
                                 fill=fill, outline=outline,
                                 width=int(width * S))

    def line(self, pts, fill=INK, width=2):
        self.d.line([(int(x * S), int(y * S)) for x, y in pts],
                    fill=fill, width=int(width * S))

    def text(self, pos, s, fnt, fill=INK, anchor="la"):
        self.d.text((pos[0] * S, pos[1] * S), s, font=fnt, fill=fill,
                    anchor=anchor)

    def textw(self, s, fnt):
        return self.d.textlength(s, font=fnt) / S


def wrap(c, s, fnt, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.textw(trial, fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(c, pos, s, fnt, maxw, leading, fill=INK):
    y = pos[1]
    for ln in wrap(c, s, fnt, maxw):
        c.text((pos[0], y), ln, fnt, fill)
        y += leading
    return y


def spaced(c, cx, y, s, fnt, fill, gap=5):
    widths = [c.textw(ch, fnt) for ch in s]
    total = sum(widths) + gap * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        c.text((x, y), ch, fnt, fill)
        x += w + gap


def shadow(c, box, radius=10):
    layer = Image.new("L", (SIZE, SIZE), 0)
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle(sc((box[0], box[1] + 3, box[2], box[3] + 3)),
                         radius=int(radius * S), fill=52)
    layer = layer.filter(ImageFilter.GaussianBlur(5 * S))
    c.img.paste((40, 48, 66), (0, 0), layer)
    c.d = ImageDraw.Draw(c.img)


def paste_art(c, name, box, centering=(0.5, 0.5), radius=8):
    art = Image.open(os.path.join(ASSETS, name)).convert("RGB")
    w, h = int((box[2] - box[0]) * S), int((box[3] - box[1]) * S)
    art = ImageOps.fit(art, (w, h), Image.LANCZOS, centering=centering)
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, w, h), radius=int(radius * S), fill=255)
    c.img.paste(art, (int(box[0] * S), int(box[1] * S)), mask)
    c.d = ImageDraw.Draw(c.img)


def masthead(c):
    spaced(c, 512, 20, "THE WORLD IN ONE DAY", font(SANS_BOLD, 15), RED)
    c.text((512, 42), "20 NOVEMBER 2026", font(SERIF_BLACK, 92),
           NAVY, anchor="ma")
    c.text((512, 146), "Friday's world news in one picture — diplomacy, "
           "war, climate, space and markets", font(SANS_SEMI, 17.5),
           GREY, anchor="ma")
    c.line([(18, 172), (1006, 172)], INK, 3)
    c.line([(18, 178), (1006, 178)], INK, 1)


def hero(c):
    box = (18, 190, 1006, 490)
    shadow(c, box)
    c.rrect(box, 10, fill=(237, 241, 246), outline=LINE, width=1)
    paste_art(c, "art-hero.webp", (26, 198, 998, 318), centering=(0.5, 0.62))
    c.text((26, 328), "SHENZHEN • APEC — THE DAY'S TOP STORY",
           font(SANS_XBOLD, 15), RED)
    c.text((26, 350), "TRUMP, XI & PUTIN: FIRST THREE-WAY SUMMIT",
           font(SANS_BLACK, 33), INK)
    block(c, (26, 394), "“Nuclear war must never be fought,” the three "
          "leaders agree in Shenzhen — but no deal on arms control, "
          "Ukraine, Iran or Taiwan. Trump rates it “12 out of 10.”",
          font(SANS_REG, 16.5), 950, 23, (40, 48, 58))


def panel(c, box, tint, art, centering, kicker, kcol, headline, sub):
    shadow(c, box)
    c.rrect(box, 10, fill=tint, outline=LINE, width=1)
    x, y = box[0], box[1]
    paste_art(c, art, (x + 8, y + 8, x + 148, y + 162),
              centering=centering)
    c.text((x + 164, y + 12), kicker, font(SANS_XBOLD, 12.5), kcol)
    block(c, (x + 164, y + 33), headline, font(SANS_BLACK, 21), 312, 26)
    block(c, (x + 164, y + 92), sub, font(SANS_REG, 14), 312, 19,
          (40, 48, 58))


def mini(c, box, tint, art, centering, kicker, kcol, headline, sub):
    shadow(c, box)
    c.rrect(box, 10, fill=tint, outline=LINE, width=1)
    x, y = box[0], box[1]
    paste_art(c, art, (x + 8, y + 8, x + 128, y + 88),
              centering=centering)
    c.text((x + 140, y + 10), kicker, font(SANS_XBOLD, 11), kcol)
    block(c, (x + 140, y + 27), headline, font(SANS_BLACK, 17), 330, 21)
    c.text((x + 140, y + 71), sub, font(SANS_REG, 12.5), (40, 48, 58))


def build():
    c = Canvas()
    masthead(c)
    hero(c)
    panel(c, (18, 504, 504, 674), (247, 240, 230), "art-kyiv.webp", (0.5, 0.4),
          "KYIV • UKRAINE", RED, "RUSSIAN BARRAGE HITS KYIV EMBASSIES",
          "Daytime strike damages the Austrian & Dutch missions and a "
          "cathedral. EU summons Moscow's envoy; UK pledges 1,000+ "
          "drones.")
    panel(c, (520, 504, 1006, 674), (239, 244, 236), "art-court.webp",
          (0.5, 0.5), "THE HAGUE • WORLD COURT", GREEN,
          "WORLD COURT: MYANMAR GENOCIDE",
          "ICJ rules Myanmar committed genocide against the Rohingya. "
          "UN: “Bring them home.” Malaysia resettles 10,000 Rohingya.")
    panel(c, (18, 688, 504, 858), (249, 236, 228), "art-riyadh.webp",
          (0.5, 0.22), "RIYADH • SAUDI ARABIA", RED,
          "HOUTHI MISSILE HITS RIYADH TOWER",
          "Windows blown out across eight floors of the capital's "
          "tallest tower, a second attack this month. Oil prices edge "
          "higher.")
    panel(c, (520, 688, 1006, 858), (234, 243, 240), "art-cop.webp",
          (0.5, 0.5), "ANTALYA • COP31 CLIMATE TALKS", GREEN,
          "COP31 DRAFT ERASES FOSSIL FUELS",
          "Final-day draft drops every mention of fossil fuels and "
          "the $120bn adaptation fund; “35 by 35” electrification "
          "stays.")
    mini(c, (18, 872, 504, 968), (236, 239, 247), "art-voyager.webp",
         (0.30, 0.5), "SPACE • NASA", NAVY,
         "VOYAGER 1 PHONES HOME FROM ONE LIGHT-DAY AWAY",
         "26 billion km out • launched 1977")
    mini(c, (520, 872, 1006, 968), (238, 244, 234), "art-markets.webp",
         (0.5, 0.35), "MARKETS • AI", GREEN,
         "ANTHROPIC IPO: RECORD $81BN RAISE",
         "Shares +17% on debut • $1.5 trillion valuation")
    c.rrect((18, 982, 1006, 1014), 8, fill=NAVY)
    c.text((512, 990), "ALSO: SEOUL UPHOLDS KAKAO FOUNDER'S ACQUITTAL • "
           "TAIWAN FLAGS 2,700 CHINA-LINKED ACCOUNTS",
           font(SANS_BOLD, 14.5), WHITE, anchor="ma")
    out = c.img.resize((1024, 1024), Image.LANCZOS)
    path = os.path.join(HERE, "entry.png")
    out.save(path)
    size = os.path.getsize(path)
    if size > 1_000_000:
        out = out.quantize(colors=256, method=Image.FASTOCTREE,
                           dither=Image.FLOYDSTEINBERG).convert("RGB")
        out.save(path, optimize=True)
        size = os.path.getsize(path)
    print("wrote", path, size, "bytes")
    return path


if __name__ == "__main__":
    build()
