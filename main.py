#!/usr/bin/env python3
"""THE WORLD TODAY - news-image-20261126.

Draws one 1024x1024 newspaper front page summing up the world news of
Thursday 26 November 2026: 13 verified stories across 6 regions, with the
Houthi claim on Saudi Arabia's Ras Tanura refinery and Brent at $94.61
as the lead. Every fact and figure was verified against news reports of
25-26 November 2026 before drawing; claims are labelled as claims.

Stdlib only (os, struct, zlib, hashlib). Deterministic: two runs write
identical bytes. Writes entry.png to MAKEFUN_OUTPUT_DIR when set, else
next to this file.
"""

import hashlib
import os
import struct
import zlib

W = H = 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
RED = (158, 27, 27)
NAVY = (31, 58, 95)
DARKNAVY = (18, 33, 56)
ORANGE = (232, 106, 28)
YELLOW = (245, 197, 24)
GRAY = (105, 105, 100)
WHITE = (255, 255, 255)
SMOKE = (150, 150, 145)

# 5x7 bitmap font, written for this entry. Each glyph is 7 rows; each row
# is a 5-bit number, bit 4 = leftmost column. All text is set in capitals.
FONT = {
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E],
    "D": [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F],
    "3": [0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C],
    " ": [0, 0, 0, 0, 0, 0, 0],
    ".": [0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C],
    ",": [0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08],
    ":": [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00],
    ";": [0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08],
    "-": [0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00],
    "/": [0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10],
    "%": [0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13],
    "$": [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    "(": [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ")": [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    "&": [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    "+": [0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00],
    "=": [0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00],
    "?": [0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
    "'": [0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00],
    '"': [0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00],
    "\u2022": [0x00, 0x04, 0x0E, 0x0E, 0x0E, 0x04, 0x00],
}


class Canvas:
    def __init__(self):
        row = bytes(PAPER) * W
        self.pix = bytearray(row * H)

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.pix[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        fill = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.pix[i:i + (x1 - x0) * 3] = fill

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def ring(self, cx, cy, r, c, thick=2):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cy + dy, thick, c)
            self.hline(cx + dx - thick + 1, cy + dy, thick, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        ymin = max(0, min(y0, y1, y2))
        ymax = min(H - 1, max(y0, y1, y2))
        pts = [(x0, y0), (x1, y1), (x2, y2)]
        for y in range(ymin, ymax + 1):
            xs = []
            for i in range(3):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % 3]
                if ay == by:
                    continue
                if (y >= min(ay, by)) and (y < max(ay, by)):
                    xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.hline(xa, y, xb - xa + 1, c)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for r in range(7):
                bits = glyph[r]
                for col in range(5):
                    if (bits >> (4 - col)) & 1:
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centered(self, cx, y, s, scale, c):
        x = cx - self.text_width(s, scale) // 2
        self.text(x, y, s, scale, c)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns a list of lines fitting max_w."""
        words = s.split(" ")
        lines = []
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def png_bytes(w, h, pix):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += pix[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- icons

def icon_bars(cv, x, y, s, c):
    # Three ascending bars: trade / tariffs.
    cv.rect(x, y + 26, 10, 18, c)
    cv.rect(x + 14, y + 16, 10, 28, c)
    cv.rect(x + 28, y + 6, 10, 38, c)
    cv.line(x - 2, y + 44, x + 42, y + 44, c, 2)


def icon_rocket(cv, x, y, s, c):
    # Rocket rising: nose triangle, body, fins, flame.
    cv.triangle(x + 14, y + 2, x + 6, y + 18, x + 22, y + 18, c)
    cv.rect(x + 8, y + 18, 12, 18, c)
    cv.triangle(x + 8, y + 30, x + 0, y + 42, x + 8, y + 36, c)
    cv.triangle(x + 20, y + 30, x + 28, y + 42, x + 20, y + 36, c)
    cv.triangle(x + 11, y + 36, x + 17, y + 36, x + 14, y + 46, ORANGE)


def icon_missile(cv, x, y, s, c):
    # Horizontal missile, nose right: body, nose cone, tail fins, flame.
    cv.rect(x + 8, y + 18, 26, 10, c)
    cv.triangle(x + 34, y + 18, x + 34, y + 28, x + 44, y + 23, c)
    cv.triangle(x + 8, y + 18, x + 0, y + 12, x + 8, y + 24, c)
    cv.triangle(x + 8, y + 28, x + 0, y + 34, x + 8, y + 22, c)
    cv.triangle(x + 2, y + 20, x + 2, y + 26, x - 4, y + 23, ORANGE)
    cv.circle(x + 40, y + 23, 2, WHITE)


def icon_jet(cv, x, y, s, c):
    # Delta-wing jet seen from above.
    cv.triangle(x + 22, y + 2, x + 8, y + 30, x + 20, y + 30, c)
    cv.triangle(x + 22, y + 2, x + 36, y + 30, x + 24, y + 30, c)
    cv.rect(x + 20, y + 2, 4, 34, c)
    cv.triangle(x + 20, y + 36, x + 24, y + 36, x + 22, y + 44, c)


def icon_ten(cv, x, y, s, c):
    # Ten-year badge: ringed 10.
    cv.ring(x + 22, y + 22, 20, c, 3)
    cv.text(x + 12, y + 15, "10", 2, c)


def icon_balloon(cv, x, y, s, c):
    # Parade balloon: envelope, basket, string.
    cv.circle(x + 22, y + 16, 15, c)
    cv.triangle(x + 8, y + 20, x + 36, y + 20, x + 22, y + 32, c)
    cv.rect(x + 18, y + 38, 8, 6, c)
    cv.line(x + 22, y + 32, x + 22, y + 38, c, 1)


ICONS = {
    "bars": icon_bars,
    "rocket": icon_rocket,
    "missile": icon_missile,
    "jet": icon_jet,
    "ten": icon_ten,
    "balloon": icon_balloon,
}


# ---------------------------------------------------------------- page

MX = 28            # side margin
CW = 1024 - 2 * MX  # content width


def draw_hero_illustration(cv, x, y, w, h):
    """Editorial drawing of the Ras Tanura refinery at night: towers and
    tanks against a navy sky, flames rising, a red price arrow climbing."""
    cv.rect(x, y, w, h, NAVY)
    # Stars / drones in the sky.
    for sx, sy in ((70, 14), (180, 26), (300, 10), (880, 18), (940, 30)):
        cv.circle(x + sx, y + sy, 2, WHITE)
    for dx, dy in ((620, 22), (700, 34)):
        cv.rect(x + dx, y + dy, 10, 3, WHITE)
        cv.rect(x + dx + 3, y + dy - 3, 4, 9, WHITE)
    # Ground.
    cv.rect(x, y + h - 22, w, 22, DARKNAVY)
    # Storage tanks (left) - ink silhouettes so they read against the sky.
    for tx in (60, 190):
        cv.rect(x + tx, y + 78, 110, h - 78 - 22, INK)
        cv.rect(x + tx, y + 78, 110, 6, WHITE)
        cv.vline(x + tx + 55, y + 78, h - 78 - 22, DARKNAVY)
    # Distillation towers (centre) with lit windows so they read as plant.
    for tx, th in ((330, 92), (395, 108), (460, 84)):
        cv.rect(x + tx, y + h - 22 - th, 34, th, INK)
        cv.rect(x + tx - 4, y + h - 22 - th, 42, 6, INK)
        cv.rect(x + tx + 6, y + h - 22 - th - 12, 22, 12, INK)
        for wy in range(y + h - 22 - th + 14, y + h - 26, 18):
            cv.rect(x + tx + 8, wy, 4, 4, WHITE)
            cv.rect(x + tx + 22, wy, 4, 4, WHITE)
    # Flare stack (right of towers).
    cv.rect(x + 530, y + 30, 10, h - 52, INK)
    cv.triangle(x + 524, y + 30, x + 546, y + 30, x + 535, y + 12, ORANGE)
    # Flames over the middle tower and the second tank - tall and bold
    # so the fire reads at a glance.
    cv.triangle(x + 392, y + 62, x + 432, y + 62, x + 412, y + 8, ORANGE)
    cv.triangle(x + 402, y + 62, x + 422, y + 62, x + 412, y + 28, YELLOW)
    cv.triangle(x + 212, y + 78, x + 262, y + 78, x + 237, y + 30, ORANGE)
    cv.triangle(x + 224, y + 78, x + 250, y + 78, x + 237, y + 48, YELLOW)
    # Smoke puffs.
    cv.circle(x + 412, y + 6, 6, SMOKE)
    cv.circle(x + 424, y + 2, 4, SMOKE)
    cv.circle(x + 237, y + 26, 5, SMOKE)
    # Pipes along the ground.
    cv.hline(x + 20, y + h - 30, w - 40, INK)
    cv.hline(x + 20, y + h - 34, w - 40, INK)
    # Red price arrow climbing across the scene, ending below the tag.
    cv.line(x + 600, y + h - 34, x + 850, y + 56, RED, 4)
    cv.triangle(x + 850, y + 56, x + 822, y + 50, x + 838, y + 74, RED)
    # Price tag: white fill with a red border (never a red fill).
    cv.rect(x + 760, y + 8, 188, 30, WHITE)
    cv.rect(x + 760, y + 8, 188, 3, RED)
    cv.rect(x + 760, y + 35, 188, 3, RED)
    cv.rect(x + 760, y + 8, 3, 30, RED)
    cv.rect(x + 945, y + 8, 3, 30, RED)
    cv.text(x + 772, y + 15, "BRENT $94.61", 2, RED)
    # Illustration credit tag.
    cv.text(x + 12, y + h - 18, "ILLUSTRATION", 2, WHITE)


def draw_secondary(cv, x, y, num, source, headline, body, icon):
    """One 2-column grid cell: icon, tag, 2-line headline, 1-line body."""
    ICONS[icon](cv, x, y + 2, 1, NAVY)
    cv.text(x + 56, y + 2, num, 2, RED)
    cv.text(x + 56 + cv.text_width(num + " ", 2), y + 2,
            "\u2022 " + source, 2, GRAY)
    lines = cv.wrap(headline, 416, 3)
    for i, ln in enumerate(lines[:2]):
        cv.text(x + 56, y + 20 + i * 21, ln, 3, INK)
    cv.text(x, y + 62, body, 2, INK)


def draw_page():
    cv = Canvas()
    # ---- Masthead
    cv.text_centered(512, 12, "THE WORLD TODAY", 8, INK)
    cv.rect(MX, 76, CW, 6, RED)
    cv.rect(MX, 88, CW, 2, INK)
    cv.text(MX, 96, "THURSDAY 26 NOVEMBER 2026", 2, INK)
    right = "WORLD EDITION"
    cv.text(1024 - MX - cv.text_width(right, 2), 96, right, 2, INK)
    cv.rect(MX, 116, CW, 2, INK)

    # ---- Hero: Ras Tanura
    cv.text(MX, 126, "MIDDLE EAST  \u2022  RAS TANURA, SAUDI ARABIA", 2, RED)
    cv.text(MX, 148, "HOUTHIS CLAIM STRIKE ON", 6, INK)
    cv.text(MX, 194, "RAS TANURA - BRENT $94.61", 6, INK)
    draw_hero_illustration(cv, MX, 246, CW, 140)
    standfirst = (
        "YEMEN'S HOUTHIS SAY THEY HIT SAUDI ARABIA'S LARGEST REFINERY "
        "AND RIYADH'S FINANCIAL DISTRICT. RIYADH SAYS ITS DEFENCES DOWNED "
        "FOUR DRONES; BRENT CRUDE SETTLED $3.21 HIGHER AT $94.61 A BARREL.")
    for i, ln in enumerate(cv.wrap(standfirst, CW, 2)):
        cv.text(MX, 396 + i * 16, ln, 2, INK)
    cv.text(MX, 450, "SOURCE: REUTERS  \u2022  CLAIM REPORTED, DAMAGE NOT CONFIRMED",
            2, GRAY)

    # ---- By the numbers
    cv.rect(MX, 472, CW, 42, NAVY)
    stats = [
        ("BRENT $94.61", "+3.5% TODAY"),
        ("550,000", "BARRELS A DAY"),
        ("4", "DRONES DOWNED"),
    ]
    third = CW // 3
    for i, (val, lab) in enumerate(stats):
        cx = MX + third * i + third // 2
        cv.text_centered(cx, 476, val, 3, WHITE)
        cv.text_centered(cx, 497, lab, 2, WHITE)
        if i:
            cv.vline(MX + third * i, 476, 34, WHITE)

    # ---- Secondary grid: 6 stories, 2 columns x 3 rows
    cells = [
        ("02", "USTR / REUTERS", "US PROPOSES TARIFFS ON 14 PARTNERS",
         "CHINA 20%, TAIWAN 15% - PROPOSED", "bars"),
        ("03", "CMSA / REUTERS", "PAKISTAN'S FIRST ASTRONAUT IN ORBIT",
         "ALI DOCKS AT TIANGONG - CONFIRMED", "rocket"),
        ("04", "KCNA / REUTERS", "KIM ORDERS WIDER NUCLEAR DEPLOYMENT",
         "TACTICAL ARMS, ALL DOMAINS - KCNA", "missile"),
        ("05", "UKRAINE / REUTERS", "KYIV SAYS 5 JETS HIT AT SAVASLEYKA BASE",
         "3 MIG-31S, 2 SU-34S - REPORTED", "jet"),
        ("06", "NRC / LE MONDE", "COLOMBIA: 10 YEARS OF BITTER PEACE",
         "8.1M NEED AID AS VIOLENCE RETURNS", "ten"),
        ("07", "MACY'S / AP", "MACY'S 100TH PARADE POSTPONED BY STORM",
         "FIRST DELAY IN A CENTURY - SATURDAY", "balloon"),
    ]
    col_w = 472
    for i, (num, src, head, body, icon) in enumerate(cells):
        cx = MX + (i % 2) * (col_w + 24)
        cy = 524 + (i // 2) * 84
        draw_secondary(cv, cx, cy, num, src, head, body, icon)

    # ---- More today: 6 headline-only items
    cv.text(MX, 780, "MORE TODAY", 2, RED)
    cv.rect(MX, 796, CW, 2, INK)
    more = [
        ("08", "US ECONOMY GREW 4.3% IN Q3, FASTEST IN 3 YEARS", "BEA"),
        ("09", "CAIRO TANKER FIRE KILLS 31, INJURES 21", "EGYPT HEALTH MINISTRY"),
        ("10", "MUMBAI MARKS 18 YEARS SINCE THE 26/11 ATTACKS", "PTI"),
        ("11", "GUKESH VS SINDAROV: GAME 3 TODAY IN GENEVA", "FIDE"),
        ("12", "US PROPOSES 10% TARIFF ON BRAZILIAN JETS, SUGAR", "USTR"),
        ("13", "OPEC+ MEETS SUNDAY TO SET 2027 OUTPUT", "REUTERS"),
    ]
    for i, (num, head, src) in enumerate(more):
        yy = 806 + i * 20
        cv.text(MX, yy, num, 2, RED)
        cv.text(MX + cv.text_width(num + "  ", 2), yy, head, 2, INK)
        sx = MX + cv.text_width(num + "  " + head + "  -  ", 2)
        cv.text(sx, yy, src, 2, GRAY)

    # ---- Bottom strip
    cv.rect(MX, 924, CW, 2, INK)
    cv.text(MX, 936, "MARKETS:  BRENT $94.61 +3.5%   \u2022   WTI $83.68 +2.0%   \u2022   US GDP +4.3%",
            2, INK)
    cv.text_centered(512, 958,
                     "THE WORLD TODAY  \u2022  13 STORIES, 6 REGIONS  \u2022  THURSDAY 26 NOVEMBER 2026",
                     2, INK)
    cv.text_centered(512, 980,
                     "ALL STORIES FROM REPORTS OF 25-26 NOVEMBER 2026  \u2022  SOURCES NAMED WITH EACH STORY",
                     2, GRAY)
    return cv


def main():
    cv = draw_page()
    data = png_bytes(W, H, cv.pix)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(
        os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes) sha256=%s" % (
        path, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
