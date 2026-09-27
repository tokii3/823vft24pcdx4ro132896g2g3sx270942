"""Raymi assets v5 - additional procedurally drawn support assets (extends assets_v3/assets_v4,
never replaces them - see REGEL in ENGINE_NOTES.md). All return premultiplied RGBA. Same look:
dark ink outline, flat bright fill, Raymi's UV/palette where a color has no obvious real-world
counterpart. No font glyphs used anywhere in this file (rule #1 in
Raymi-Wissen/04_Asset-Creation-and-QC-Guidelines.md) - any text that belongs ON these assets
(e.g. a rank number on a medal, "SUBSCRIBE" next to the bell) is drawn separately by the calling
scene via the shared engine.Text/TX instance, exactly like the existing 'label'/'card'/'scroll'
assets already do.

WARUM DIESE ASSETS (v8, siehe ENGINE_NOTES_v8.md):
 - bell(): das in 04_Asset-Creation-and-QC-Guidelines.md Abschnitt 1 explizit genannte, bisher
   FEHLENDE Branding-Asset ("ein eigener Subscribe-Button/Badge im Raymi-Look") - kombiniert mit
   assets_v4.plate()+TX.tile('SUBSCRIBE') ergibt genau das gewuenschte Icon+Text-Badge-Muster.
 - medal()/trophy(): fehlende Icon-Vielfalt fuer Ranking-/Vergleichs-Beats (Punkt 9 der QC-Liste
   "Keine Icon-/Prop-Vielfalt" - bisher nur Essens-Assets, nichts fuer "Platz 1/2/3"-Momente).
 - clock()/meter(): fuer Countdown-/Grad-Beats ("wie sehr stimmt das zu", Hype-/Spice-Meter).
 - flame(), vs_panel(): Reaction-/Vergleichs-Callouts ("heisse Meinung", "X vs Y").
 - shell()/starfish()/moon_stars(): Ozean-/Nacht-Requisiten, passend zu Raymis Stingray-Lore und
   zu den v8-Hintergruenden (Sternenhimmel/Milchstrasse/Sonnenuntergang, siehe
   BACKGROUNDS_AND_MUSIC.md) - bisher gab es KEIN einziges Requisit ausserhalb von Essen.
 - comment_icon()/share_arrow(): kleine Badge-Icons, die neben engagement.cta_prompt()'s
   Sprechblase platziert werden koennen (die Pille selbst bleibt unveraendert in engagement.py).
"""
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from engine import premult, UV, UVL, PINK, DARK, WHITE
from assets_v3 import SS, INK, _fin, with_shadow
from assets_v4 import _canvas, _outlined

# rank-medal presets - reused by callers instead of guessing colors by hand
GOLD, SILVER, BRONZE = (255, 214, 84), (203, 210, 222), (207, 142, 92)
RED, GREEN = (236, 62, 88), (64, 208, 132)


def bell(w=420):
    """Notification-bell icon (UV palette) - pair with assets_v4.plate()+TX.tile('SUBSCRIBE')
    for the branding-guide's requested Subscribe badge; also works alone as a small
    'notifications on' sticker."""
    h = int(w * 1.0); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    def shapes(d, g, ink):
        d.pieslice((S * .18 - g, H2 * .10 - g, S * .82 + g, H2 * .82 + g), 180, 360, fill=ink or UV)
        d.rectangle((S * .18 - g, H2 * .46, S * .82 + g, H2 * .70 + g), fill=ink or UV)
        d.polygon([(S * .10 - g, H2 * .70 + g), (S * .90 + g, H2 * .70 + g), (S * .78 + g, H2 * .58), (S * .22 - g, H2 * .58)], fill=ink or UV)
    _outlined(d, S, shapes, SS * 7)
    d.rounded_rectangle((S * .44, H2 * .02, S * .56, H2 * .14), radius=S * .06, fill=INK)
    d.rounded_rectangle((S * .46, H2 * .03, S * .54, H2 * .12), radius=S * .04, fill=UVL)
    d.ellipse((S * .40, H2 * .72, S * .60, H2 * .90), fill=INK); d.ellipse((S * .43, H2 * .74, S * .57, H2 * .87), fill=UVL)
    hi = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(hi).ellipse((S * .30, H2 * .22, S * .48, H2 * .40), fill=(255, 255, 255, 90))
    im = Image.alpha_composite(im, hi)
    return _fin(im, w, h)


def heart(w=420):
    """Flat UV/pink heart - like/love/favorite reactions."""
    h = int(w * .90); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    def shapes(d, g, ink):
        for cx in (.30, .70): d.ellipse((S * (cx - .27) - g, H2 * .06 - g, S * (cx + .27) + g, H2 * .60 + g), fill=ink or PINK)
        d.polygon([(S * .06 - g, H2 * .34), (S * .94 + g, H2 * .34), (S * .50, H2 * .96 + g)], fill=ink or PINK)
    _outlined(d, S, shapes, SS * 7)
    hi = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(hi).ellipse((S * .16, H2 * .14, S * .40, H2 * .34), fill=(255, 255, 255, 110))
    im = Image.alpha_composite(im, hi)
    return _fin(im, w, h)


def medal(w=420, col=GOLD):
    """Ranking medal (circle + double ribbon tails). Pass col=assets_v5.GOLD/SILVER/BRONZE.
    The rank number itself is drawn by the caller via TX.tile on top, same pattern as the
    'label'/'stamp' assets in raymi_short.py."""
    h = int(w * 1.35); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    d.polygon([(S * .30, H2 * .0), (S * .46, H2 * .0), (S * .40, H2 * .46), (S * .22, H2 * .40)], fill=INK)
    d.polygon([(S * .70, H2 * .0), (S * .54, H2 * .0), (S * .60, H2 * .46), (S * .78, H2 * .40)], fill=INK)
    d.polygon([(S * .315, H2 * .015), (S * .445, H2 * .015), (S * .395, H2 * .43), (S * .245, H2 * .38)], fill=tuple(min(255, v + 26) for v in col) + (255,))
    d.polygon([(S * .685, H2 * .015), (S * .555, H2 * .015), (S * .605, H2 * .43), (S * .755, H2 * .38)], fill=col + (255,))
    cy = H2 * .60; r = S * .38
    d.ellipse((S / 2 - r - SS * 7, cy - r - SS * 7, S / 2 + r + SS * 7, cy + r + SS * 7), fill=INK)
    d.ellipse((S / 2 - r, cy - r, S / 2 + r, cy + r), fill=col + (255,))
    d.ellipse((S / 2 - r * .74, cy - r * .74, S / 2 + r * .74, cy + r * .74), outline=tuple(max(0, v - 45) for v in col) + (255,), width=int(SS * 6))
    hi = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(hi).ellipse((S / 2 - r * .55, cy - r * .8, S / 2 + r * .05, cy - r * .15), fill=(255, 255, 255, 95))
    im = Image.alpha_composite(im, hi)
    return _fin(im, w, h)


def trophy(w=380):
    """Trophy cup - 'winner'/payoff reveal moments."""
    h = int(w * 1.15); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    def shapes(d, g, ink):
        d.rounded_rectangle((S * .30 - g, H2 * .04 - g, S * .70 + g, H2 * .52 + g), radius=S * .06 + g, fill=ink or GOLD)
        for side in (-1, 1):
            cx = .50 + side * .335; d.arc((S * (cx - .16) - g, H2 * .04 - g, S * (cx + .16) + g, H2 * .40 + g), 250 if side < 0 else -70, 110 if side < 0 else 250, fill=ink or GOLD, width=int(S * .07 + g))
        d.rounded_rectangle((S * .44 - g, H2 * .50 - g, S * .56 + g, H2 * .74 + g), radius=S * .02 + g, fill=ink or GOLD)
        d.rounded_rectangle((S * .24 - g, H2 * .74 - g, S * .76 + g, H2 * .84 + g), radius=S * .03 + g, fill=ink or GOLD)
        d.rounded_rectangle((S * .14 - g, H2 * .84 - g, S * .86 + g, H2 * .96 + g), radius=S * .03 + g, fill=ink or GOLD)
    _outlined(d, S, shapes, SS * 7)
    star = [(0, -1), (.22, -.3), (.95, -.3), (.36, .12), (.58, .82), (0, .38), (-.58, .82), (-.36, .12), (-.95, -.3), (-.22, -.3)]
    cx, cy, r = S * .50, H2 * .26, S * .13
    d.polygon([(cx + p[0] * r, cy + p[1] * r) for p in star], fill=(255, 246, 214, 255))
    return _fin(im, w, h)


def clock(w=420):
    """Simple clock face with hands fixed at ~10-past - countdown/timer/'how long' beats."""
    h = w; im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS
    d.ellipse((S * .04, S * .04, S * .96, S * .96), fill=INK)
    d.ellipse((S * .10, S * .10, S * .90, S * .90), fill=(250, 240, 214, 255))
    d.ellipse((S * .13, S * .13, S * .87, S * .87), outline=UV, width=int(S * .02))
    cx = cy = S / 2
    for i in range(12):
        a = math.pi * 2 * i / 12; x0, y0 = cx + math.cos(a) * S * .37, cy + math.sin(a) * S * .37
        x1, y1 = cx + math.cos(a) * S * .42, cy + math.sin(a) * S * .42
        d.line((x0, y0, x1, y1), fill=INK, width=int(S * .014))
    d.line((cx, cy, cx + math.cos(math.radians(-60)) * S * .22, cy + math.sin(math.radians(-60)) * S * .22), fill=INK, width=int(S * .05))
    d.line((cx, cy, cx + math.cos(math.radians(30)) * S * .32, cy + math.sin(math.radians(30)) * S * .32), fill=INK, width=int(S * .035))
    d.ellipse((cx - S * .035, cy - S * .035, cx + S * .035, cy + S * .035), fill=RED + (255,))
    return _fin(im, w, h)


def flame(w=360):
    """Fire icon - 'hot take'/hype callouts."""
    h = int(w * 1.25); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    def outer(d, g, ink):
        d.polygon([(S * .50, H2 * .0 - g), (S * .86 + g, H2 * .48), (S * .78 + g, H2 * .48), (S * .95 + g, H2 * .78),
                    (S * .68, H2 * 1.0 + g), (S * .32, H2 * 1.0 + g), (S * .05 - g, H2 * .78), (S * .22 - g, H2 * .48),
                    (S * .14 - g, H2 * .48)], fill=ink or (255, 138, 46, 255))
    _outlined(d, S, outer, SS * 7)
    d.polygon([(S * .50, H2 * .30), (S * .68, H2 * .60), (S * .60, H2 * .78), (S * .50, H2 * .90), (S * .40, H2 * .78), (S * .32, H2 * .60)], fill=(255, 214, 84, 255))
    return _fin(im, w, h)


def meter(w=680, h=140, frac=0.7, col=None, bg=(255, 246, 240)):
    """Horizontal gauge/meter (e.g. 'spice level', 'hype meter'). frac 0..1 = fill amount.
    col defaults to a green->gold->red ramp by frac; pass an explicit color to override."""
    im = _canvas(w, h); d = ImageDraw.Draw(im); S, H2 = w * SS, h * SS; frac = max(0., min(1., frac))
    if col is None: col = GREEN if frac < .45 else (GOLD if frac < .8 else RED)
    d.rounded_rectangle((0, 0, S - 1, H2 - 1), radius=H2 * .5, fill=INK)
    pad = SS * 8
    d.rounded_rectangle((pad, pad, S - 1 - pad, H2 - 1 - pad), radius=H2 * .5 - pad, fill=bg + (255,))
    fw = max(H2 - 2 * pad, (S - 4 * pad) * frac)
    d.rounded_rectangle((pad * 2, pad * 2, pad * 2 + fw, H2 - 1 - pad * 2), radius=(H2 - 4 * pad) * .5, fill=col + (255,))
    return _fin(im, w, h)


def vs_panel(w=760, h=420, col_a=(84, 138, 226), col_b=(226, 72, 96)):
    """Diagonal two-tone comparison panel with a lightning-bolt divider (A vs B beats). Labels for
    each side are drawn on top by the caller via TX.tile, same pattern as scroll()/label()."""
    im = _canvas(w, h); d = ImageDraw.Draw(im); S, H2 = w * SS, h * SS
    d.rounded_rectangle((0, 0, S - 1, H2 - 1), radius=H2 * .08, fill=INK)
    pad = SS * 9
    mask = Image.new('L', (S, H2), 0); ImageDraw.Draw(mask).rounded_rectangle((pad, pad, S - 1 - pad, H2 - 1 - pad), radius=H2 * .08 - pad, fill=255)
    panel = Image.new('RGBA', (S, H2), col_a + (255,)); dp = ImageDraw.Draw(panel)
    bolt = [(.56, 0), (1.0, 0), (1.0, .44), (.60, .58), (1.0, .58), (.46, 1.0), (.46, .60), (0, .60), (0, .40)]
    dp.polygon([(x * S, y * H2) for x, y in bolt], fill=col_b + (255,))
    dp.line([(x * S, y * H2) for x, y in bolt[:5]] + [(bolt[4][0] * S, bolt[4][1] * H2)], fill=INK, width=int(SS * 5), joint='curve')
    panel.putalpha(mask)
    im = Image.alpha_composite(im, panel)
    return _fin(im, w, h)


def shell(w=440):
    """Scallop shell (flat hinge on top, fanned ribs, rounded bottom) - ocean-prop variety
    (Raymi is a stingray, food icons alone got repetitive)."""
    h = int(w * .78); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    cx, hy, r = S * .5, H2 * .30, S * .46
    def outer(d, g, ink):
        d.pieslice((cx - r - g, hy - r - g, cx + r + g, hy + r + g), 0, 180, fill=ink or (255, 198, 178, 255))
    _outlined(d, S, outer, SS * 7)
    n = 7
    for i in range(n):
        a = math.radians(-72 + 144 * i / (n - 1))
        tip = (cx + r * .97 * math.sin(a), hy + r * .97 * math.cos(a))
        d.line((cx, hy, tip[0], tip[1]), fill=(235, 150, 128, 255), width=int(S * .022))
    d.pieslice((cx - r, hy - r, cx + r, hy + r), 0, 180, outline=(235, 150, 128, 255), width=int(S * .014))
    d.ellipse((cx - S * .09, hy - S * .09, cx + S * .09, hy + S * .09), fill=(255, 232, 220, 255), outline=INK, width=int(SS * 4))
    return _fin(im, w, h)


def starfish(w=420):
    """Five-arm starfish icon - ocean-prop variety."""
    h = w; im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; cx = cy = S / 2
    def outer(d, g, ink):
        pts = []
        for i in range(10):
            a = -math.pi / 2 + math.pi * i / 5; r = (S * .46 if i % 2 == 0 else S * .19) + g
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=ink or (255, 158, 96, 255))
    _outlined(d, S, outer, SS * 8)
    rng = np.random.RandomState(7)
    for i in range(10):
        a = -math.pi / 2 + math.pi * i / 5; r = S * .30
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        rad = S * .018
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(226, 118, 62, 255))
    return _fin(im, w, h)


def moon_stars(w=460):
    """Crescent moon + small sparkle - night-sky sticker, thematically matches the v8
    starfield/beach-at-night backgrounds (see BACKGROUNDS_AND_MUSIC.md)."""
    h = int(w * .82); im = _canvas(w, h); S = w * SS; H2 = h * SS
    # crescent = ellipse minus offset ellipse; fiddlier than a plain ImageDraw fill, so built
    # directly as a numpy mask (dilated copy in INK for the outline, same visual result as
    # the _outlined() helper used elsewhere in this file).
    moon_mask = Image.new('L', (S, H2), 0); dm = ImageDraw.Draw(moon_mask)
    dm.ellipse((S * .06, H2 * .06, S * .74, H2 * .74), fill=255)
    dm.ellipse((S * .22, H2 * .0, S * .90, H2 * .68), fill=0)
    grown = cv2.dilate(np.array(moon_mask), np.ones((SS * 15, SS * 15), np.uint8))
    layer = np.zeros((H2, S, 4), np.uint8); layer[grown > 0] = list(INK[:3]) + [255]
    layer[np.array(moon_mask) > 0] = list(UVL) + [255]
    im = Image.fromarray(layer)
    dd = ImageDraw.Draw(im)
    star = [(0, -1), (.22, -.22), (1, 0), (.22, .22), (0, 1), (-.22, .22), (-1, 0), (-.22, -.22)]
    for cx, cy, r in ((S * .82, H2 * .30, S * .07), (S * .90, H2 * .55, S * .04)):
        dd.polygon([(cx + p[0] * r, cy + p[1] * r) for p in star], fill=(255, 255, 255, 255))
    return _fin(im, w, h)


def comment_icon(w=360):
    """Small speech-bubble badge icon - pairs with engagement.cta_prompt()'s pill (that stays
    unchanged in engagement.py) as an accent icon, or stands alone as a 'comments' sticker."""
    h = int(w * .84); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    def outer(d, g, ink):
        d.rounded_rectangle((S * .05 - g, H2 * .05 - g, S * .95 + g, H2 * .74 + g), radius=H2 * .24 + g, fill=ink or UV)
        d.polygon([(S * .22 - g, H2 * .70), (S * .40 - g, H2 * .70), (S * .18 - g, H2 * .96 + g)], fill=ink or UV)
    _outlined(d, S, outer, SS * 7)
    for i, x in enumerate((.30, .50, .70)):
        r = S * .045
        d.ellipse((S * x - r, H2 * .38 - r, S * x + r, H2 * .38 + r), fill=(255, 255, 255, 255))
    return _fin(im, w, h)


def share_arrow(w=380):
    """Share/forward icon (three connected nodes) - complements comment_icon() for engagement badges."""
    h = w; im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS
    nodes = {(0.78, 0.22): 0.14, (0.22, 0.5): 0.14, (0.78, 0.78): 0.14}
    def outer(d, g, ink):
        for (x, y), r in nodes.items():
            rr = S * r + g; d.ellipse((S * x - rr, S * y - rr, S * x + rr, S * y + rr), fill=ink or UV)
        d.line((S * .22, S * .5, S * .78, S * .22), fill=ink or UV, width=int(S * .07 + g * 2))
        d.line((S * .22, S * .5, S * .78, S * .78), fill=ink or UV, width=int(S * .07 + g * 2))
    _outlined(d, S, outer, SS * 6)
    for (x, y), r in nodes.items():
        rr = S * r * .55
        d.ellipse((S * x - rr, S * y - rr, S * x + rr, S * y + rr), fill=(255, 255, 255, 230))
    return _fin(im, w, h)


if __name__ == '__main__':   # asset sheet for a quick visual check, same pattern as assets_v3/v4
    sheet = Image.new('RGB', (3400, 1300), (50, 44, 96))
    row1 = [bell(300), heart(280), medal(260, GOLD), medal(260, SILVER), medal(260, BRONZE), trophy(260), clock(280), flame(240)]
    row2 = [meter(480, 100, .72), vs_panel(480, 280), shell(300), starfish(260), moon_stars(320), comment_icon(260), share_arrow(260)]
    for row, y in ((row1, 10), (row2, 440)):
        x = 10
        for sp in row:
            sp2 = with_shadow(sp); rgba = Image.fromarray(sp2); sheet.paste(rgba, (x, y), rgba); x += rgba.size[0] + 20
    sheet.save('/home/claude/work/assets_v5_sheet.png')
    print('wrote assets_v5_sheet.png')
