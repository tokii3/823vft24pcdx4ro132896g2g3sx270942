"""Raymi Engine v9 - assets_v6.py (NEU, additives Modul - ersetzt NICHTS in assets_v3/v4/v5,
alte Videos die diese noch importieren rendern unveraendert weiter, siehe REGEL in
ENGINE_NOTES.md). Fuer JEDES neue Video: dieses Modul statt assets_v3/v4/v5 importieren.

WARUM DIESES MODUL (Feedback, woertlich): "erstellte assets haben schlechte qualitaet,
nutzen raymi font nicht, sehen billig und schlecht aus und passen nicht zu raymis
aesthetik" + "assets muessen wiederverwendbar sein und gespeichert werden".

Was sich konkret aendert ggue. assets_v3/v4/v5:
 1. JEDES Icon laeuft durch dieselbe Material-Pipeline aus raymi_style.py (Gradient-
    Fill statt Flat-Color, Rim-Shade/Ambient-Occlusion, ein Specular-Highlight, EINE
    konsistente Tinten-Farbe/-Staerke) - vorher hatte jede Funktion ihre eigene,
    leicht andere Umsetzung (mal Flat-Fill, mal ein zusaetzlicher Highlight-Blob, mal
    keiner). Gleiches Material auf jedem Asset = liest sich wie EIN Kanal-Look.
 2. EINE kanonische Palette (raymi_style.PALETTE) statt der bisher an 3 Stellen leicht
    unterschiedlich kopierten CYAN/GOLD/SILVER/BRONZE/RED/GREEN-Werte.
 3. Text auf einem Asset geht AUSSCHLIESSLICH durch raymi_style.text_plate() - die
    einzige Funktion hier, die ueberhaupt Text zeichnet, und die verlangt zwingend die
    aufrufende engine.Text-Instanz (Raymi-Regular.ttf). Es gibt in diesem Modul keinen
    zweiten Codepfad, der auf einen Default-Font zurueckfallen koennte.
 4. JEDES Asset ist ueber asset_library.LIB.cached() an einen Namen gebunden: einmal
    gebaut, wird es unter assets_library/png/<name>.png gespeichert und in JEDEM
    kuenftigen Video (auch in einer neuen Session, nach Re-Upload des Packs, siehe
    ENGINE_NOTES_v9.md) identisch wiederverwendet statt neu gezeichnet - das ist die
    "Wiederverwendbarkeit", nicht nur In-Prozess-Caching wie bisher (cache_util.py).

Funktionsnamen/Signaturen sind absichtlich drop-in-kompatibel zu assets_v3/v4/v5, damit
ein neues Szenen-Skript einfach `import assets_v6 as A` statt `import assets_v3 as A`
schreiben kann und der Rest des bestehenden Beat-Codes unveraendert funktioniert.
"""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw
from engine import premult, WHITE
from asset_library import LIB
from raymi_style import (SS, INK, GOLD, SILVER, BRONZE, RED, GREEN, CYAN, UV_C, UVL_C, PINK_C,
                          _canvas, _fin, gradient_mask_fill, rim_shade, specular, cast_shadow,
                          text_plate, regions, metallic_fill, layer_over)

with_shadow = cast_shadow   # drop-in alias, same call signature as assets_v3.with_shadow

# v9.1: bump whenever the material pipeline or an individual icon builder changes shape/shading,
# so LIB.cached() actually redraws instead of silently serving the OLD (pre-fix) PNG that's
# already sitting in assets_library/ under the same name+params - a plain code edit alone does
# NOT invalidate the on-disk cache (the cache key is name+params, not the builder's source).
STYLE_V = 'v91'


def _cache_name(base):
    return f'{base}_{STYLE_V}'


def _ellipse_metal(w, h, cx, cy, rx, ry, col):
    """Metallic-shaded counterpart to _ellipse() below, for round metal parts (medal disc) -
    same construction, metallic_fill() instead of gradient_mask_fill()."""
    S, H2 = w * SS, h * SS
    def mk(grow):
        im = Image.new('L', (S, H2), 0)
        ImageDraw.Draw(im).ellipse((cx * S - rx * S - grow, cy * H2 - ry * H2 - grow, cx * S + rx * S + grow, cy * H2 + ry * H2 + grow), fill=255)
        return np.array(im)
    ink = mk(max(6, int(S * .02))); fill = mk(0)
    body = metallic_fill(fill, col)
    canvas = np.zeros((H2, S, 4), np.uint8); canvas[ink > 10] = list(INK) + [255]
    fa = body[..., 3:4] / 255.; canvas[..., :3] = (canvas[..., :3] * (1 - fa) + body[..., :3] * fa).astype(np.uint8)
    canvas[..., 3] = np.maximum(canvas[..., 3], body[..., 3])
    hi = specular(S, H2, cx * S, cy * H2 - ry * H2 * .3, rx * S * .45, ry * H2 * .3)
    ha = (hi[..., 3:4] / 255.) * (canvas[..., 3:4] / 255.)
    canvas[..., :3] = np.clip(canvas[..., :3].astype(np.float32) + hi[..., :3].astype(np.float32) * ha, 0, 255).astype(np.uint8)
    return _fin(Image.fromarray(canvas), w, h)


def _ring_layer(w, h, cx, cy, r, stroke, start, end, col):
    """v9.1 (NEU): a metallic-shaded arc/ring stroke as its own finished (h,w,4) layer - used
    to build trophy() handles as thin attached loops instead of the old d.arc(...,fill=ink)
    flat-outline scribble. start/end in PIL degrees (0=3 o'clock, clockwise); caller must
    make sure end > start (add 360 if the sweep needs to cross 0)."""
    S, H2 = w * SS, h * SS
    cx_, cy_, r_, sw_ = cx * SS, cy * SS, r * SS, stroke * SS
    def mk(grow):
        im = Image.new('L', (S, H2), 0)
        ImageDraw.Draw(im).arc((cx_ - r_, cy_ - r_, cx_ + r_, cy_ + r_), start, end, fill=255, width=max(1, int(sw_ + grow)))
        return np.array(im)
    ink = mk(max(8, int(S * .022))); fill = mk(0)
    body = metallic_fill(fill, col)
    canvas = np.zeros((H2, S, 4), np.uint8); canvas[ink > 10] = list(INK) + [255]
    fa = body[..., 3:4] / 255.; canvas[..., :3] = (canvas[..., :3] * (1 - fa) + body[..., :3] * fa).astype(np.uint8)
    canvas[..., 3] = np.maximum(canvas[..., 3], body[..., 3])
    hi = specular(S, H2, cx_ - r_ * .15, cy_ - r_ * .95, r_ * .32, r_ * .16)
    ha = (hi[..., 3:4] / 255.) * (canvas[..., 3:4] / 255.)
    canvas[..., :3] = np.clip(canvas[..., :3].astype(np.float32) + hi[..., :3].astype(np.float32) * ha, 0, 255).astype(np.uint8)
    return _fin(Image.fromarray(canvas), w, h)


def _poly(w, h, pts_fn, col_top, col_bot, grow_extra=0):
    """Generic helper: pts_fn(grow) -> list of (x,y) in 0..1 space. Draws one gradient-filled,
    ink-outlined, specular-highlighted shape - the v9 default for any simple silhouette icon."""
    S, H2 = w * SS, h * SS
    def mk(grow):
        im = Image.new('L', (S, H2), 0)
        ImageDraw.Draw(im).polygon([(x * S, y * H2) for x, y in pts_fn(grow)], fill=255)
        return np.array(im)
    ink = mk(max(6, int(S * .02)) + grow_extra)
    fill = mk(0)
    body = gradient_mask_fill(fill, col_top, col_bot)
    shade = rim_shade(fill); sa = shade[..., 3:4] / 255.
    body[..., :3] = np.clip(body[..., :3].astype(np.float32) * (1 - sa[..., 0:1] * .5), 0, 255).astype(np.uint8)
    canvas = np.zeros((H2, S, 4), np.uint8)
    canvas[ink > 10] = list(INK) + [255]
    fa = body[..., 3:4] / 255.
    canvas[..., :3] = (canvas[..., :3] * (1 - fa) + body[..., :3] * fa).astype(np.uint8)
    canvas[..., 3] = np.maximum(canvas[..., 3], body[..., 3])
    ys, xs = np.where(fill > 10)
    if len(xs):
        cx, cy = xs.mean(), ys.min() + (ys.max() - ys.min()) * .28
        r = (xs.max() - xs.min()) * .28
        hi = specular(S, H2, cx, cy, r, r * .55)
        ha = (hi[..., 3:4] / 255.) * (canvas[..., 3:4] / 255.)
        canvas[..., :3] = np.clip(canvas[..., :3].astype(np.float32) + hi[..., :3].astype(np.float32) * ha, 0, 255).astype(np.uint8)
    return _fin(Image.fromarray(canvas), w, h)


def _ellipse(w, h, cx, cy, rx, ry, col_top, col_bot):
    S, H2 = w * SS, h * SS
    def mk(grow):
        im = Image.new('L', (S, H2), 0)
        ImageDraw.Draw(im).ellipse((cx * S - rx * S - grow, cy * H2 - ry * H2 - grow, cx * S + rx * S + grow, cy * H2 + ry * H2 + grow), fill=255)
        return np.array(im)
    ink = mk(max(6, int(S * .02))); fill = mk(0)
    body = gradient_mask_fill(fill, col_top, col_bot)
    canvas = np.zeros((H2, S, 4), np.uint8); canvas[ink > 10] = list(INK) + [255]
    fa = body[..., 3:4] / 255.; canvas[..., :3] = (canvas[..., :3] * (1 - fa) + body[..., :3] * fa).astype(np.uint8)
    canvas[..., 3] = np.maximum(canvas[..., 3], body[..., 3])
    hi = specular(S, H2, cx * S, cy * H2 - ry * H2 * .3, rx * S * .45, ry * H2 * .3)
    ha = (hi[..., 3:4] / 255.) * (canvas[..., 3:4] / 255.)
    canvas[..., :3] = np.clip(canvas[..., :3].astype(np.float32) + hi[..., :3].astype(np.float32) * ha, 0, 255).astype(np.uint8)
    return _fin(Image.fromarray(canvas), w, h)


# =============================================================== food icons (v3/v4 parity,
# echte Silhouetten aus assets_v3/v4 uebernommen - nur der FLACHE Fill wird durch die v9-
# Material-Pipeline ersetzt, die Formen selbst bleiben erkennbar statt zu groben Polygonen
# vereinfacht zu werden.)
def _onigiri_build(w):
    h = int(w * .95)
    tri = lambda d: d.polygon([(.5 * w, .10 * h), (.05 * w, .86 * h), (.95 * w, .86 * h)], fill=255)
    nori = lambda d: d.polygon([(.27 * w, .58 * h), (.73 * w, .58 * h), (.73 * w, .86 * h), (.27 * w, .86 * h)], fill=255)
    out = regions(w, h, [(tri, (252, 251, 246), (214, 221, 240)), (nori, (34, 46, 52), (18, 26, 30))])
    im = Image.fromarray(out); d = ImageDraw.Draw(im)
    rng = np.random.RandomState(4)
    for _ in range(46):
        x, y = rng.uniform(.16, .84) * w, rng.uniform(.16, .54) * h
        r = rng.uniform(.010, .017) * w
        d.ellipse((x - r, y - r * .6, x + r, y + r * .6), fill=(222, 228, 240, 200))
    return np.array(im)


def onigiri(w=640):
    return LIB.cached(_cache_name('onigiri'), lambda: _onigiri_build(w), params=dict(w=w, v=STYLE_V), kind='food', tags=['onigiri', 'food'])


def _badge_build(kind, w):
    col = RED if kind == 'x' else GREEN
    im = _ellipse(w, w, .5, .5, .46, .46, tuple(min(255, c + 26) for c in col), col)
    S = w
    ov = Image.fromarray(im); d = ImageDraw.Draw(ov); lw = max(6, int(S * .09))
    if kind == 'x':
        for a, b in (((.30, .30), (.70, .70)), ((.70, .30), (.30, .70))):
            d.line((a[0] * S, a[1] * S, b[0] * S, b[1] * S), fill=(255, 255, 255, 255), width=lw)
    else:
        d.line([(.28 * S, .53 * S), (.44 * S, .69 * S), (.75 * S, .33 * S)], fill=(255, 255, 255, 255), width=lw, joint='curve')
    return np.array(ov)


def badge(kind, w=360):
    return LIB.cached(_cache_name(f'badge_{kind}'), lambda: _badge_build(kind, w), params=dict(kind=kind, w=w, v=STYLE_V), kind='ui', tags=['badge', kind])


def _gavel_build(w):
    h = int(w * 1.05)
    handle = lambda d: d.rounded_rectangle((.44 * w, .28 * h, .56 * w, .98 * h), radius=.03 * w, fill=255)
    head = lambda d: d.rounded_rectangle((.10 * w, .02 * h, .90 * w, .34 * h), radius=.05 * w, fill=255)
    def studs(d):
        for x in (.20, .80):
            d.ellipse(((x - .05) * w, .04 * h, (x + .05) * w, .16 * h), fill=255)
    out = regions(w, h, [(handle, (214, 158, 92), (150, 96, 50)), (head, (232, 176, 100), (166, 108, 54)),
                          (studs, GOLD, tuple(max(0, c - 60) for c in GOLD))])
    im = Image.fromarray(out); d = ImageDraw.Draw(im)
    d.rounded_rectangle((.30 * w, .085 * h, .60 * w, .135 * h), radius=.015 * w, fill=(255, 236, 190, 220))
    return np.array(im)


def gavel(w=420):
    return LIB.cached(_cache_name('gavel'), lambda: _gavel_build(w), params=dict(w=w, v=STYLE_V), kind='prop', tags=['law', 'gavel'])


def _scroll_build(w):
    h = int(w * .52)
    body = lambda d: d.rounded_rectangle((.075 * w, .16 * h, .925 * w, .84 * h), radius=.03 * w, fill=255)
    band1 = lambda d: d.rounded_rectangle((.02 * w, .04 * h, .98 * w, .22 * h), radius=.09 * h, fill=255)
    band2 = lambda d: d.rounded_rectangle((.02 * w, .76 * h, .98 * w, .94 * h), radius=.09 * h, fill=255)
    seal = lambda d: d.ellipse((.80 * w, .60 * h, .92 * w, .80 * h), fill=255)
    out = regions(w, h, [(body, (252, 244, 220), (226, 206, 162)),
                          (band1, (232, 190, 122), (186, 138, 72)), (band2, (232, 190, 122), (186, 138, 72)),
                          (seal, (236, 78, 100), (176, 46, 64))])
    im = Image.fromarray(out); d = ImageDraw.Draw(im)
    for i, yy in enumerate((.40, .48, .56)):
        d.rounded_rectangle((.20 * w, yy * h, (.78 - .08 * i) * w, (yy + .026) * h), radius=3, fill=(196, 174, 130, 220))
    return np.array(im)


def scroll(w=760):
    return LIB.cached(_cache_name('scroll'), lambda: _scroll_build(w), params=dict(w=w, v=STYLE_V), kind='prop', tags=['scroll'])


def starburst(w=700, n=14, col=None):
    col = col or GOLD
    def build():
        c = w / 2; pts = []
        for i in range(n * 2):
            r = c * (.98 if i % 2 == 0 else .55); a = math.pi * i / n
            pts.append((c + r * math.cos(a), c + r * math.sin(a)))
        m = np.zeros((w, w), np.uint8); cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
        m = cv2.GaussianBlur(m, (0, 0), 6)
        yy, xx = np.mgrid[0:w, 0:w]; rr = np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / c
        g = np.clip(1.15 - rr, 0, 1); a = (m * g).astype(np.uint8)
        im = np.zeros((w, w, 4), np.uint8)
        im[..., :3] = (np.array(col)[None, None] * (a[..., None] / 255.)).astype(np.uint8); im[..., 3] = a
        return im
    return LIB.cached(_cache_name(f'starburst_{w}_{n}_{col}'), build, params=dict(w=w, n=n, col=col, v=STYLE_V), kind='fx', tags=['burst'])


def sparkle(w=200):
    def build():
        S = w * SS; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
        d.polygon([(c, 0), (c + S * .09, c - S * .09), (S, c), (c + S * .09, c + S * .09), (c, S), (c - S * .09, c + S * .09), (0, c), (c - S * .09, c - S * .09)], fill=(255, 255, 255, 255))
        return _fin(im, w, w)
    return LIB.cached(_cache_name('sparkle'), build, params=dict(w=w, v=STYLE_V), kind='fx', tags=['sparkle'])


def nigiri(w=560):
    def build():
        h = int(w * .66)
        rice = lambda d: d.rounded_rectangle((.12 * w, .46 * h, .88 * w, .92 * h), radius=.22 * h, fill=255)
        fish = lambda d: d.rounded_rectangle((.04 * w, .10 * h, .96 * w, .62 * h), radius=.24 * h, fill=255)
        out = regions(w, h, [(rice, (252, 251, 246), (222, 228, 240)), (fish, (255, 158, 122), (222, 84, 66))])
        im = Image.fromarray(out); d = ImageDraw.Draw(im)
        for x in (.24, .40, .56, .72):
            d.line((x * w, .17 * h, (x - .05) * w, .52 * h), fill=(255, 204, 176, 210), width=max(2, int(w * .016)))
        d.rounded_rectangle((.10 * w, .60 * h, .90 * w, .66 * h), radius=6, fill=(230, 236, 246, 230))
        return np.array(im)
    return LIB.cached(_cache_name('nigiri'), build, params=dict(w=w, v=STYLE_V), kind='food', tags=['sushi'])


def soy(w=560):
    def build():
        h = int(w * .55)
        dish = lambda d: d.ellipse((.03 * w, .12 * h, .97 * w, .98 * h), fill=255)
        pool = lambda d: d.ellipse((.12 * w, .24 * h, .88 * w, .80 * h), fill=255)
        out = regions(w, h, [(dish, (250, 250, 252), (222, 226, 236)), (pool, (70, 38, 26), (34, 16, 10))])
        im = Image.fromarray(out); d = ImageDraw.Draw(im)
        for x, y, r in ((.66, .52, .028), (.74, .60, .020)):
            d.ellipse(((x - r) * w, (y - r) * h, (x + r) * w, (y + r) * h), fill=(118, 72, 50, 220))
        return np.array(im)
    return LIB.cached(_cache_name('soy'), build, params=dict(w=w, v=STYLE_V), kind='food', tags=['soy sauce'])


def wasabi(w=460):
    def build():
        h = int(w * .8)
        blobs = [(.50, .62, .40, .30), (.34, .48, .26, .26), (.66, .46, .24, .24), (.50, .30, .20, .20)]
        def sil(d):
            for cx, cy, rx, ry in blobs:
                d.ellipse(((cx - rx) * w, (cy - ry) * h, (cx + rx) * w, (cy + ry) * h), fill=255)
        out = regions(w, h, [(sil, (168, 226, 104), (98, 162, 50))])
        im = Image.fromarray(out); d = ImageDraw.Draw(im)
        for cx, cy in ((.30, .34), (.62, .30)):
            d.ellipse(((cx - .08) * w, (cy - .06) * h, (cx + .08) * w, (cy + .06) * h), fill=(200, 240, 150, 160))
        return np.array(im)
    return LIB.cached(_cache_name('wasabi'), build, params=dict(w=w, v=STYLE_V), kind='food', tags=['wasabi'])


def sponge(w=520):
    def build():
        h = int(w * .62)
        top = lambda d: d.rounded_rectangle((.06 * w, .12 * h, .94 * w, .64 * h), radius=.04 * w, fill=255)
        bot = lambda d: d.rounded_rectangle((.06 * w, .64 * h, .94 * w, .90 * h), radius=.04 * w, fill=255)
        out = regions(w, h, [(top, (255, 224, 100), (222, 160, 40)), (bot, (120, 200, 110), (76, 152, 68))])
        im = Image.fromarray(out); d = ImageDraw.Draw(im)
        for x, y, r in ((.20, .30, .05), (.42, .22, .04), (.62, .38, .06), (.80, .24, .04), (.32, .50, .035), (.86, .52, .04)):
            d.ellipse(((x - r) * w, (y - r * 1.4) * h, (x + r) * w, (y + r * 1.4) * h), fill=(226, 164, 28, 200))
        return np.array(im)
    return LIB.cached(_cache_name('sponge'), build, params=dict(w=w, v=STYLE_V), kind='food', tags=['sponge'])


def bowl(w=560):
    def build():
        h = int(w * .82)
        rim = lambda d: d.ellipse((.12 * w, .06 * h, .88 * w, .66 * h), fill=255)
        soup = lambda d: d.pieslice((.03 * w, -.15 * h, .97 * w, 1.0 * h), 0, 180, fill=255)
        out = regions(w, h, [(rim, (252, 251, 246), (226, 230, 240)), (soup, (100, 152, 232), (54, 92, 176))])
        im = Image.fromarray(out); d = ImageDraw.Draw(im)
        d.arc((.03 * w, -.15 * h, .97 * w, 1.0 * h), 20, 160, fill=(160, 198, 250, 220), width=max(2, int(w * .014)))
        rng = np.random.RandomState(3)
        for _ in range(30):
            x, y = rng.uniform(.22, .78) * w, rng.uniform(.14, .40) * h
            r = w * .010
            d.ellipse((x - r, y - r * .6, x + r, y + r * .6), fill=(226, 232, 244, 200))
        return np.array(im)
    return LIB.cached(_cache_name('bowl'), build, params=dict(w=w, v=STYLE_V), kind='food', tags=['bowl'])


def pizza(w=520):
    def build():
        h = w
        slice_ = lambda d: d.polygon([(.11 * w, .17 * h), (.89 * w, .17 * h), (.50 * w, .90 * h)], fill=255)
        crust = lambda d: d.rounded_rectangle((.06 * w, .06 * h, .94 * w, .20 * h), radius=.06 * h, fill=255)
        out = regions(w, h, [(slice_, (255, 214, 96), (224, 150, 44)), (crust, (232, 168, 88), (188, 122, 56))])
        im = Image.fromarray(out); d = ImageDraw.Draw(im)
        for x, y, r in ((.32, .32, .065), (.62, .34, .065), (.48, .52, .06), (.50, .72, .045)):
            d.ellipse(((x - r) * w, (y - r) * h, (x + r) * w, (y + r) * h), fill=(214, 64, 58, 255), outline=(150, 30, 28, 255), width=2)
        return np.array(im)
    return LIB.cached(_cache_name('pizza'), build, params=dict(w=w, v=STYLE_V), kind='food', tags=['pizza'])


def plate(w, h, fill=INK, edge=UV_C, ew=6):
    """Plain rounded plate WITHOUT text (unchanged contract from assets_v4.plate). For text,
    prefer raymi_style.text_plate() which guarantees the Raymi font."""
    def build():
        im = _canvas(w, h); d = ImageDraw.Draw(im); S, H2 = w * SS, h * SS
        d.rounded_rectangle((0, 0, S - 1, H2 - 1), radius=H2 * .30, fill=tuple(edge) + (255,))
        e = ew * SS
        d.rounded_rectangle((e, e, S - 1 - e, H2 - 1 - e), radius=H2 * .30 - e, fill=tuple(fill) + (255,))
        return _fin(im, w, h)
    return LIB.cached(_cache_name(f'plate_{w}x{h}_{fill}_{edge}'), build, params=dict(w=w, h=h, fill=fill, edge=edge, v=STYLE_V), kind='ui', tags=['plate'])


def stamp_frame(w, h, col=RED):
    def build():
        im = _canvas(w, h); d = ImageDraw.Draw(im); S, H2 = w * SS, h * SS; c = tuple(col) + (255,)
        d.rounded_rectangle((0, 0, S - 1, H2 - 1), radius=H2 * .16, outline=c, width=SS * 12)
        d.rounded_rectangle((SS * 22, SS * 22, S - 1 - SS * 22, H2 - 1 - SS * 22), radius=H2 * .10, outline=c, width=SS * 5)
        return _fin(im, w, h)
    return LIB.cached(_cache_name(f'stamp_{w}x{h}_{col}'), build, params=dict(w=w, h=h, col=col, v=STYLE_V), kind='ui', tags=['stamp'])


# =============================================================== v5-parity icon set, v9 material
def bell(w=420):
    def build():
        h = w
        dome = lambda d: d.pieslice((.18 * w, .10 * h, .82 * w, .82 * h), 180, 360, fill=255)
        skirt = lambda d: d.rectangle((.18 * w, .46 * h, .82 * w, .70 * h), fill=255)
        flare = lambda d: d.polygon([(.10 * w, .70 * h), (.90 * w, .70 * h), (.78 * w, .58 * h), (.22 * w, .58 * h)], fill=255)
        out = regions(w, h, [(dome, UVL_C, UV_C), (skirt, UVL_C, UV_C), (flare, UV_C, tuple(max(0, c - 40) for c in UV_C))])
        im = Image.fromarray(out); d = ImageDraw.Draw(im)
        d.rounded_rectangle((.44 * w, .01 * h, .56 * w, .12 * h), radius=.05 * w, fill=INK + (255,))
        d.rounded_rectangle((.46 * w, .025 * h, .54 * w, .10 * h), radius=.035 * w, fill=tuple(UVL_C) + (255,))
        d.ellipse((.40 * w, .72 * h, .60 * w, .90 * h), fill=INK + (255,))
        d.ellipse((.43 * w, .745 * h, .57 * w, .875 * h), fill=tuple(GOLD) + (255,))
        return np.array(im)
    return LIB.cached(_cache_name('bell'), build, params=dict(w=w, v=STYLE_V), kind='branding', tags=['subscribe', 'bell'])


def heart(w=420):
    def build():
        h = int(w * .90)
        return _poly(w, h, lambda g: [(.5 - g / w, .96 + g / h), (.06 - g / w, .40), (.06 - g / w, .16 - g / h), (.30, .04 - g / h), (.5, .28),
                                       (.70, .04 - g / h), (.94 + g / w, .16 - g / h), (.94 + g / w, .40), (.5 + g / w, .96 + g / h)],
                     PINK_C, tuple(max(0, c - 60) for c in PINK_C))
    return LIB.cached(_cache_name('heart'), build, params=dict(w=w, v=STYLE_V), kind='reaction', tags=['like', 'heart'])


def medal(w=420, col=None):
    col = col or GOLD
    def build():
        h = int(w * 1.35); S, H2 = w, h
        ribbon = _poly(w, h, lambda g: [(.30 - g / w, .0), (.70 + g / w, .0), (.60, .46 + g / h), (.40, .46 + g / h)],
                       tuple(min(255, c + 26) for c in col), tuple(max(0, c - 40) for c in col))
        # v9.1: the disc (the part that actually reads as "medal") is now metallic_fill()-shaded
        # (banded brushed-metal look) instead of sharing the same smooth radial gradient as the
        # ribbon fabric - metal and cloth are different materials and shouldn't share one gradient,
        # which was a big part of why the old medal read as flat/plasticky.
        disc = _ellipse_metal(w, h, .5, .62, .37, .37, col)
        out = np.array(Image.fromarray(ribbon)); da = disc[..., 3:4] / 255.
        out[..., :3] = (out[..., :3] * (1 - da) + disc[..., :3] * da).astype(np.uint8)
        out[..., 3] = np.maximum(out[..., 3], disc[..., 3])
        im = Image.fromarray(out); d = ImageDraw.Draw(im)
        d.ellipse((S * .5 - S * .27, H2 * .62 - S * .27, S * .5 + S * .27, H2 * .62 + S * .27), outline=tuple(max(0, c - 70) for c in col) + (255,), width=int(S * .02))
        return np.array(im)
    return LIB.cached(_cache_name(f'medal_{w}_{col}'), build, params=dict(w=w, col=col, v=STYLE_V), kind='ranking', tags=['medal', 'rank'])


def trophy(w=380):
    """v9.1: rebuilt. The v9.0 handles used d.arc(start=250, end=110) for the left handle -
    PIL sweeps an arc from start to end through INCREASING angle, so that call actually swept
    through 0deg (the side FACING the cup, where PIL angle 0 = 3 o'clock) instead of through
    180deg (the outward side, 9 o'clock) - the handle bulged inward across the cup body
    instead of looping outward, which is exactly the 'sieht komisch aus' report. Rebuilt as
    two independent metallic ring layers (_ring_layer, corrected sweep direction, composited
    UNDER the cup so the tips tuck behind it like a real weld) instead of one flat-color arc
    stroke merged into the same silhouette as the cup."""
    def build():
        h = int(w * 1.15)
        canvas = np.zeros((h, w, 4), np.uint8)
        # left handle: a narrow ~110deg gap centered on 0deg (facing the cup) so the ring is
        # mostly closed and both tips lean toward the cup edge instead of floating away from
        # it. FIRST v9.1 attempt fixed the sweep DIRECTION but left a ~190deg gap - so much of
        # the circle was undrawn that the tips pointed straight up/down instead of toward the
        # cup, and the handle read as a detached comma floating next to the trophy. Right
        # handle mirrored (gap centered on 180deg).
        for side, s0, s1 in ((-1, 55, 305), (1, 235, 485)):
            hx = w * (.5 + side * .265)
            ring = _ring_layer(w, h, hx, h * .205, w * .150, w * .046, s0, s1, GOLD)
            canvas = layer_over(canvas, ring)
        cup = lambda d: d.rounded_rectangle((.30 * w, .04 * h, .70 * w, .52 * h), radius=.06 * w, fill=255)
        stem = lambda d: d.rounded_rectangle((.44 * w, .50 * h, .56 * w, .74 * h), radius=.02 * w, fill=255)
        base1 = lambda d: d.rounded_rectangle((.24 * w, .74 * h, .76 * w, .84 * h), radius=.03 * w, fill=255)
        base2 = lambda d: d.rounded_rectangle((.14 * w, .84 * h, .86 * w, .96 * h), radius=.03 * w, fill=255)
        body = regions(w, h, [(cup, tuple(min(255, c + 26) for c in GOLD), tuple(max(0, c - 40) for c in GOLD)),
                               (stem, GOLD, tuple(max(0, c - 40) for c in GOLD)),
                               (base1, GOLD, tuple(max(0, c - 40) for c in GOLD)),
                               (base2, tuple(max(0, c - 20) for c in GOLD), tuple(max(0, c - 60) for c in GOLD))])
        canvas = layer_over(canvas, body)
        im = Image.fromarray(canvas); d = ImageDraw.Draw(im)
        star = [(0, -1), (.22, -.3), (.95, -.3), (.36, .12), (.58, .82), (0, .38), (-.58, .82), (-.36, .12), (-.95, -.3), (-.22, -.3)]
        cx, cy, r = .50 * w, .26 * h, .13 * w
        d.polygon([(cx + p[0] * r, cy + p[1] * r) for p in star], fill=(255, 246, 214, 255))
        return np.array(im)
    return LIB.cached(_cache_name('trophy'), build, params=dict(w=w, v=STYLE_V), kind='ranking', tags=['trophy', 'winner'])


def clock(w=420):
    def build():
        h = w; S = w
        face = _ellipse(w, h, .5, .5, .45, .45, (255, 250, 232), (232, 218, 184))
        im = Image.fromarray(face); d = ImageDraw.Draw(im); cx = cy = S / 2
        for i in range(12):
            a = math.pi * 2 * i / 12
            d.line((cx + math.cos(a) * S * .37, cy + math.sin(a) * S * .37, cx + math.cos(a) * S * .42, cy + math.sin(a) * S * .42), fill=INK + (255,), width=int(S * .012))
        d.line((cx, cy, cx + math.cos(math.radians(-60)) * S * .22, cy + math.sin(math.radians(-60)) * S * .22), fill=INK + (255,), width=int(S * .045))
        d.line((cx, cy, cx + math.cos(math.radians(30)) * S * .32, cy + math.sin(math.radians(30)) * S * .32), fill=INK + (255,), width=int(S * .03))
        d.ellipse((cx - S * .03, cy - S * .03, cx + S * .03, cy + S * .03), fill=tuple(RED) + (255,))
        return np.array(im)
    return LIB.cached(_cache_name('clock'), build, params=dict(w=w, v=STYLE_V), kind='ui', tags=['clock', 'timer'])


def flame(w=360):
    def build():
        h = int(w * 1.25)
        outer = _poly(w, h, lambda g: [(.5, .0 - g / h), (.86 + g / w, .48), (.68, 1.0 + g / h), (.32, 1.0 + g / h), (.14 - g / w, .48)],
                      (255, 176, 74), (232, 92, 40))
        im = Image.fromarray(outer); d = ImageDraw.Draw(im); S, H2 = w, h
        d.polygon([(S * .50, H2 * .30), (S * .68, H2 * .60), (S * .50, H2 * .90), (S * .32, H2 * .60)], fill=tuple(GOLD) + (255,))
        return np.array(im)
    return LIB.cached(_cache_name('flame'), build, params=dict(w=w, v=STYLE_V), kind='reaction', tags=['hot', 'flame'])


def meter(w=680, h=140, frac=0.7, col=None, bg=(255, 246, 240)):
    def build():
        frac_ = max(0., min(1., frac))
        c = col or (GREEN if frac_ < .45 else (GOLD if frac_ < .8 else RED))
        im = _canvas(w, h); d = ImageDraw.Draw(im); S, H2 = w * SS, h * SS
        d.rounded_rectangle((0, 0, S - 1, H2 - 1), radius=H2 * .5, fill=INK + (255,))
        pad = SS * 8
        d.rounded_rectangle((pad, pad, S - 1 - pad, H2 - 1 - pad), radius=H2 * .5 - pad, fill=tuple(bg) + (255,))
        base = _fin(im, w, h)
        fw = max(h - 2 * int(pad / SS), int((w - 4 * pad / SS) * frac_))
        fill_im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); dd = ImageDraw.Draw(fill_im)
        dd.rounded_rectangle((pad / SS * 2, pad / SS * 2, pad / SS * 2 + fw, h - 1 - pad / SS * 2), radius=(h - 4 * pad / SS) * .5, fill=tuple(c) + (255,))
        farr = np.array(fill_im); grad = gradient_mask_fill(farr[..., 3], tuple(min(255, v + 30) for v in c), tuple(max(0, v - 20) for v in c))
        out = base.copy(); ga = grad[..., 3:4] / 255.
        out[..., :3] = (out[..., :3] * (1 - ga) + grad[..., :3] * ga).astype(np.uint8)
        out[..., 3] = np.maximum(out[..., 3], grad[..., 3])
        return out
    return LIB.cached(_cache_name(f'meter_{w}x{h}_{round(frac,2)}_{col}'), build, params=dict(w=w, h=h, frac=round(frac, 2), col=col, v=STYLE_V), kind='ui', tags=['meter'])


def vs_panel(w=760, h=420, col_a=(84, 138, 226), col_b=RED):
    def build():
        im = _canvas(w, h); d = ImageDraw.Draw(im); S, H2 = w * SS, h * SS
        d.rounded_rectangle((0, 0, S - 1, H2 - 1), radius=H2 * .08, fill=INK + (255,))
        pad = SS * 9
        mask = Image.new('L', (S, H2), 0); ImageDraw.Draw(mask).rounded_rectangle((pad, pad, S - 1 - pad, H2 - 1 - pad), radius=H2 * .08 - pad, fill=255)
        panel_a = Image.fromarray(gradient_mask_fill(np.array(mask), tuple(min(255, c + 24) for c in col_a), col_a))
        bolt_mask = Image.new('L', (S, H2), 0)
        bolt = [(.56, 0), (1.0, 0), (1.0, .44), (.60, .58), (1.0, .58), (.46, 1.0), (.46, .60), (0, .60), (0, .40)]
        ImageDraw.Draw(bolt_mask).polygon([(x * S, y * H2) for x, y in bolt], fill=255)
        panel_b = Image.fromarray(gradient_mask_fill(np.array(bolt_mask), tuple(min(255, c + 24) for c in col_b), col_b))
        base = _fin(im, w, h); pa = np.array(panel_a.resize((w, h), Image.LANCZOS)); pb = np.array(panel_b.resize((w, h), Image.LANCZOS))
        aa = pa[..., 3:4] / 255.; base = (base * (1 - aa) + pa * aa).astype(np.uint8)
        ba = pb[..., 3:4] / 255.; base = (base * (1 - ba) + pb * ba).astype(np.uint8)
        return base
    return LIB.cached(_cache_name(f'vs_{w}x{h}_{col_a}_{col_b}'), build, params=dict(w=w, h=h, col_a=col_a, col_b=col_b, v=STYLE_V), kind='comparison', tags=['vs'])


def shell(w=440):
    def build():
        h = int(w * .78)
        fan = lambda d: d.pieslice((.04 * w, -.16 * h, .96 * w, .90 * h), 0, 180, fill=255)
        out = regions(w, h, [(fan, (255, 214, 194), (232, 150, 120))])
        im = Image.fromarray(out); d = ImageDraw.Draw(im)
        cx, hy, r = .5 * w, .30 * h, .46 * w
        for i in range(7):
            a = math.radians(-72 + 144 * i / 6)
            tip = (cx + r * .95 * math.sin(a), hy + r * .95 * math.cos(a))
            d.line((cx, hy, tip[0], tip[1]), fill=(235, 150, 128, 230), width=max(2, int(w * .018)))
        d.ellipse((cx - w * .08, hy - w * .08, cx + w * .08, hy + w * .08), fill=(255, 234, 222, 255), outline=INK + (255,), width=3)
        return np.array(im)
    return LIB.cached(_cache_name('shell'), build, params=dict(w=w, v=STYLE_V), kind='prop', tags=['ocean', 'shell'])


def starfish(w=420):
    def build():
        h = w
        return _poly(w, h, lambda g: [
            (.5 + (.46 + g / w) * math.cos(-math.pi / 2 + math.pi * i / 5), .5 + (.46 + g / w) * math.sin(-math.pi / 2 + math.pi * i / 5)) if i % 2 == 0 else
            (.5 + (.19 + g / w) * math.cos(-math.pi / 2 + math.pi * i / 5), .5 + (.19 + g / w) * math.sin(-math.pi / 2 + math.pi * i / 5))
            for i in range(10)], (255, 178, 110), (226, 120, 66))
    return LIB.cached(_cache_name('starfish'), build, params=dict(w=w, v=STYLE_V), kind='prop', tags=['ocean', 'starfish'])


def moon_stars(w=460):
    def build():
        h = int(w * .82); S, H2 = w, h
        moon_mask = Image.new('L', (w, h), 0); dm = ImageDraw.Draw(moon_mask)
        dm.ellipse((S * .06, H2 * .06, S * .74, H2 * .74), fill=255)
        dm.ellipse((S * .22, H2 * .0, S * .90, H2 * .68), fill=0)
        mnp = np.array(moon_mask)
        grown = cv2.dilate(mnp, np.ones((7, 7), np.uint8))
        body = gradient_mask_fill(mnp, tuple(min(255, c + 20) for c in UVL_C), UV_C)
        canvas = np.zeros((h, w, 4), np.uint8); canvas[grown > 0] = list(INK) + [255]
        fa = body[..., 3:4] / 255.; canvas[..., :3] = (canvas[..., :3] * (1 - fa) + body[..., :3] * fa).astype(np.uint8)
        canvas[..., 3] = np.maximum(canvas[..., 3], body[..., 3])
        im = Image.fromarray(canvas); dd = ImageDraw.Draw(im)
        star = [(0, -1), (.22, -.22), (1, 0), (.22, .22), (0, 1), (-.22, .22), (-1, 0), (-.22, -.22)]
        for cx, cy, r in ((S * .82, H2 * .30, S * .07), (S * .90, H2 * .55, S * .04)):
            dd.polygon([(cx + p[0] * r, cy + p[1] * r) for p in star], fill=(255, 255, 255, 255))
        return np.array(im)
    return LIB.cached(_cache_name('moon_stars'), build, params=dict(w=w, v=STYLE_V), kind='prop', tags=['night', 'moon'])


def comment_icon(w=360):
    def build():
        h = int(w * .84)
        return _poly(w, h, lambda g: [(.05 - g / w, .05 - g / h), (.95 + g / w, .05 - g / h), (.95 + g / w, .74 + g / h), (.40 - g / w, .74 + g / h), (.18, .96 + g / h), (.22, .70), (.05 - g / w, .70)],
                     tuple(min(255, c + 20) for c in UV_C), UV_C)
    return LIB.cached(_cache_name('comment_icon'), build, params=dict(w=w, v=STYLE_V), kind='engagement', tags=['comment'])


def share_arrow(w=380):
    def build():
        h = w; S = w
        im = _canvas(w, h); d = ImageDraw.Draw(im); Ssup = w * SS
        nodes = {(0.78, 0.22): 0.14, (0.22, 0.5): 0.14, (0.78, 0.78): 0.14}
        for (x, y), r in nodes.items():
            d.ellipse((Ssup * x - Ssup * r, Ssup * y - Ssup * r, Ssup * x + Ssup * r, Ssup * y + Ssup * r), fill=INK + (255,))
        d.line((Ssup * .22, Ssup * .5, Ssup * .78, Ssup * .22), fill=INK + (255,), width=int(Ssup * .08))
        d.line((Ssup * .22, Ssup * .5, Ssup * .78, Ssup * .78), fill=INK + (255,), width=int(Ssup * .08))
        base = _fin(im, w, h)
        ov = Image.fromarray(base); dov = ImageDraw.Draw(ov)
        for (x, y), r in nodes.items():
            rr = w * r * .82
            dov.ellipse((x * w - rr, y * h - rr, x * w + rr, y * h + rr), fill=tuple(UV_C) + (255,))
            rr2 = rr * .5
            dov.ellipse((x * w - rr2, y * h - rr2, x * w + rr2, y * h + rr2), fill=(255, 255, 255, 210))
        return np.array(ov)
    return LIB.cached(_cache_name('share_arrow'), build, params=dict(w=w, v=STYLE_V), kind='engagement', tags=['share'])


# =============================================================== branding: subscribe badge
def subscribe_badge(tx_engine, w=560):
    """The QC-guide's explicitly-requested asset (04_Asset-Creation-and-QC-Guidelines.md
    Abschnitt 1): bell() + text_plate('SUBSCRIBE') composed into one branded badge, entirely
    through the v9 material pipeline + guaranteed Raymi font."""
    def build():
        b = bell(int(w * .62))
        pl = text_plate(tx_engine, 'SUBSCRIBE', w, size=54, fill=WHITE, plate_fill=INK, plate_edge=UV_C)
        h = b.shape[0] + pl.shape[0] + 14
        canvas = np.zeros((h, w, 4), np.uint8)
        bx = (w - b.shape[1]) // 2
        canvas[0:b.shape[0], bx:bx + b.shape[1]] = b
        py = b.shape[0] + 14; px = (w - pl.shape[1]) // 2
        canvas[py:py + pl.shape[0], px:px + pl.shape[1]] = pl
        return canvas
    return LIB.cached(_cache_name('subscribe_badge'), build, params=dict(w=w, v=STYLE_V), kind='branding', tags=['subscribe'])


if __name__ == '__main__':   # visual QC sheet, same pattern as assets_v3/v4/v5 __main__
    from engine import Text, find_font
    TX = Text(find_font())
    sheet = Image.new('RGB', (3600, 1500), (36, 32, 70))
    row1 = [with_shadow(onigiri(300)), with_shadow(badge('x', 220)), with_shadow(badge('ok', 220)), with_shadow(gavel(240)),
            with_shadow(scroll(460)), with_shadow(nigiri(320)), with_shadow(soy(300)), with_shadow(wasabi(260))]
    row2 = [with_shadow(bell(260)), with_shadow(heart(260)), with_shadow(medal(240, GOLD)), with_shadow(medal(240, SILVER)),
            with_shadow(medal(240, BRONZE)), with_shadow(trophy(240)), with_shadow(clock(260)), with_shadow(flame(220))]
    row3 = [with_shadow(meter(460, 100, .72)), with_shadow(vs_panel(460, 260)), with_shadow(shell(280)), with_shadow(starfish(240)),
            with_shadow(moon_stars(300)), with_shadow(comment_icon(240)), with_shadow(share_arrow(240)), with_shadow(subscribe_badge(TX, 460))]
    for row, y in ((row1, 10), (row2, 500), (row3, 990)):
        x = 10
        for sp in row:
            rgba = Image.fromarray(sp); sheet.paste(rgba, (x, y), rgba); x += rgba.size[0] + 24
    out_path = '/home/claude/w/v9/assets_v6_sheet.png'
    sheet.save(out_path)
    print('wrote', out_path)
    print(f'{len(LIB.list_assets())} Assets in der Bibliothek unter {LIB.root}')
