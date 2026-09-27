"""Raymi Engine v9 - raymi_style.py (NEU, additives Modul, nichts Bestehendes angefasst)

WARUM: assets_v3/v4/v5 sehen laut Feedback "billig"/"generisch" aus und ihre Farben
weichen leicht voneinander ab (proof_onigiri_v4.py definiert z.B. sein eigenes
CYAN/GOLD lokal, assets_v5.py definiert eigenes GOLD/SILVER/BRONZE/RED/GREEN erneut).
Jede Funktion malte ausserdem nur EINEN flachen Fill + EINE Outline - kein
Gradient, kein Licht/Schatten-Modell, kein wiederkehrendes "Materialgefuehl". Das
ist der eigentliche Grund fuer den "billig"-Eindruck, nicht die Formen selbst.

Dieses Modul ist die EINZIGE Quelle fuer:
 1. Die kanonische Farbpalette (ein Ort statt N leicht abweichender Kopien)
 2. Ein wiederverwendbares "Material"-Renderpipeline (Gradient-Fill + weicher
    Kontakt-/Wurfschatten + Rim-Light + Speculer-Highlight + einheitliche
    Tinten-Outline), die JEDES neue Asset benutzt statt jedes Mal neu erfunden
    zu werden -> gleiches "Material" auf jedem Icon = wirkt wie EIN Kanal-Look
    statt wie zusammengewuerfelte Cliparts.
 3. Eine harte Regel+Helper fuer Text-auf-Assets: `text_plate()` ist der EINZIGE
    Weg, Text auf ein Asset zu bringen, und geht zwingend durch die vom Aufrufer
    uebergebene `engine.Text`-Instanz (Raymi-Regular.ttf) - kein Font-Fallback
    ist ueberhaupt erreichbar, weil die Funktion keinen anderen Codepfad hat
    (siehe Raymi-Wissen/04_Asset-Creation-and-QC-Guidelines.md Regel #1).

Nichts hier ersetzt assets_v3/v4/v5 (die REGEL "nur ergaenzen" gilt weiter - alte
Videos, die noch assets_v3/v4/v5 importieren, rendern unveraendert weiter). Neue
Assets (siehe assets_v6.py) nutzen dieses Modul.
"""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw
from engine import premult, UV, UVL, PINK, DARK, WHITE

SS = 4   # v9: 3 -> 4 Supersampling - sichtbar sauberere Kanten bei Kreisen/Kurven auf grossen Icons

# ---------------------------------------------------------------- EINE kanonische Palette
# (ersetzt die bisher an 3 Stellen leicht unterschiedlich kopierten CYAN/GOLD/SILVER/BRONZE/
# RED/GREEN-Werte in proof_onigiri_v4.py / raymi_short.py / assets_v5.py - neue Assets ziehen
# ab jetzt IMMER von hier, damit jedes Icon zur selben Marke gehoert.)
INK       = (16, 13, 30)            # etwas dunkler/satter als das alte (28,24,58) - druckt kraeftiger
INK_WARM  = (30, 20, 40)            # leicht warmer Unterton fuer weiche Schattenkerne
GOLD      = (255, 200, 70)
SILVER    = (206, 213, 224)
BRONZE    = (205, 138, 86)
RED       = (233, 68, 92)
GREEN     = (72, 205, 140)
CYAN      = (110, 214, 255)
UV_C, UVL_C, PINK_C = UV, UVL, PINK

PALETTE = dict(UV=UV_C, UVL=UVL_C, PINK=PINK_C, GOLD=GOLD, SILVER=SILVER, BRONZE=BRONZE,
                RED=RED, GREEN=GREEN, CYAN=CYAN, INK=INK, WHITE=WHITE, DARK=DARK)


def _canvas(w, h):
    return Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))


_GRAIN = {}
def _grain_tile(sz=384, seed=7):
    """v9.1: cached fine-noise tile, tiled and multiplied into every finished icon by _fin()
    below. WARUM: die reine Gradient+Rim+Specular-Pipeline aus v9.0 sah zwar "lit" aus, aber
    immer noch computer-perfekt glatt - genau das liest sich als 'vektor/clipart' statt als
    gestaltetes Asset. Echte gedruckte/gerenderte Marken-Assets (auch Sumis/Charakter-Kunst)
    haben immer eine minimale Textur/Koernung statt mathematisch reiner Flaechen. Eine
    Tick-Menge Rauschen (nur innerhalb der Alpha-Maske, sehr fein) ist der billigste und
    zuverlaessigste Hebel dagegen und wirkt auf JEDES Asset, das durch _fin() laeuft - also
    praktisch alle."""
    if sz not in _GRAIN:
        rng = np.random.RandomState(seed)
        g = rng.normal(0, 1, (sz, sz)).astype(np.float32)
        g = cv2.GaussianBlur(g, (0, 0), 0.55)
        g = g / (np.abs(g).max() + 1e-6)
        _GRAIN[sz] = g
    return _GRAIN[sz]


def _fin(im, w, h):
    arr = np.array(im.resize((w, h), Image.LANCZOS)).astype(np.float32)
    gt = _grain_tile()
    gy = np.arange(arr.shape[0]) % gt.shape[0]
    gx = np.arange(arr.shape[1]) % gt.shape[1]
    noise = gt[gy][:, gx]
    a = arr[..., 3:4] / 255.
    arr[..., :3] = np.clip(arr[..., :3] + noise[..., None] * 3.4 * a, 0, 255)
    return premult(arr.astype(np.uint8))


# ---------------------------------------------------------------- Material-Pipeline
def gradient_mask_fill(mask, col_top, col_bot, bias=0.15):
    """mask: uint8 HxW alpha shape. Returns HxWx4 uint8 RGBA - a 3-stop vertical gradient
    (highlight top -> body -> shadow bottom, v9.1, was a flat 2-stop lerp) clipped to the
    mask, with a slight center-light bias AND a soft warm/cool temperature shift (warmer
    near the top light, slightly cooler in the shadow) - the single biggest cue that
    separates a 'rendered material' from a flat vector fill, which was the core of the
    'billig/lieblos' feedback on v9.0."""
    H2, W2 = mask.shape[:2]
    yy = np.linspace(0, 1, H2, dtype=np.float32)[:, None]
    xx = np.linspace(-1, 1, W2, dtype=np.float32)[None, :]
    light = np.clip(1 - (xx ** 2) * bias - yy * 0.10, 0, 1)
    t = np.clip(yy * np.ones((1, W2), np.float32), 0, 1)
    top, bot = np.array(col_top, np.float32), np.array(col_bot, np.float32)
    mid = top * .55 + bot * .45
    w1 = np.clip(1 - t * 2, 0, 1); w2 = np.clip(1 - np.abs(t * 2 - 1), 0, 1); w3 = np.clip(t * 2 - 1, 0, 1)
    rgb = top[None, None] * w1[..., None] + mid[None, None] * w2[..., None] + bot[None, None] * w3[..., None]
    warm = np.array([10, 3, -8], np.float32)
    rgb = rgb + warm[None, None] * (1 - t[..., None]) * .8 - warm[None, None] * t[..., None] * .5
    rgb = np.clip(rgb * (0.86 + 0.22 * light[..., None]), 0, 255)
    out = np.zeros((H2, W2, 4), np.uint8)
    out[..., :3] = rgb.astype(np.uint8)
    out[..., 3] = mask
    return out


def metallic_fill(mask, base_col, bands=3.2, ang=0.0):
    """v9.1 (NEU): banded 'brushed metal' gradient for trophy()/medal() - a flat gold-colored
    shape reads as a cardboard cutout, not a medal. Alternating light/dark streaks (like
    reflections sweeping across a curved metal surface) are the concrete cue that makes gold
    look like metal instead of yellow paint. Same call contract as gradient_mask_fill (mask
    in, RGBA out) so it drops straight into the existing icon-compositing helpers."""
    H2, W2 = mask.shape[:2]
    yy = np.linspace(0, 1, H2, dtype=np.float32)
    band = 0.5 + 0.5 * np.sin(yy * bands * math.pi * 2 + 0.6)
    band = band ** 1.7
    base = np.array(base_col, np.float32)
    lo, hi = base * 0.58, np.clip(base * 1.32 + 18, 0, 255)
    col = lo[None, :] * (1 - band[:, None]) + hi[None, :] * band[:, None]
    rgb = np.tile(col[:, None, :], (1, W2, 1))
    out = np.zeros((H2, W2, 4), np.uint8)
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[..., 3] = mask
    return out


def specular(w, h, cx, cy, rx, ry, alpha=100, ang=-24):
    """Highlight cue. v9.1: a soft ambient blob PLUS a small crisp glint offset toward the
    light (real polished-surface highlights are never one uniform blur - always a soft base
    + a tight hot spot) - was one flat blob in v9.0, which read as a dull sticker."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(255, 255, 255, alpha))
    arr = np.array(im)
    arr[..., 3] = cv2.GaussianBlur(arr[..., 3], (0, 0), min(rx, ry) * .35)
    gx, gy, gr = cx - rx * .30, cy - ry * .34, max(1.5, min(rx, ry) * .26)
    glint = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glint).ellipse((gx - gr, gy - gr * .68, gx + gr, gy + gr * .68), fill=(255, 255, 255, min(255, alpha + 130)))
    garr = np.array(glint)
    garr[..., 3] = cv2.GaussianBlur(garr[..., 3], (0, 0), max(0.6, gr * .16))
    arr = np.maximum(arr, garr)
    M = cv2.getRotationMatrix2D((cx, cy), ang, 1.0)
    arr = cv2.warpAffine(arr, M, (w, h), flags=cv2.INTER_LINEAR)
    return arr


def rim_shade(mask, strength=70):
    """Darkens the lower-inner edge of a filled shape (contact/ambient-occlusion feel).
    v9.1: slightly stronger (was 60) and tinted toward INK_WARM instead of flat neutral grey,
    so the shading ties back into the brand ink color instead of looking like a generic
    drop-shadow filter."""
    H2, W2 = mask.shape[:2]
    solid = (mask > 10).astype(np.uint8)
    inner = cv2.erode(solid, np.ones((max(3, W2 // 40), max(3, W2 // 40)), np.uint8))
    ring = ((solid > 0) & (inner == 0)).astype(np.float32)
    yy = np.linspace(0, 1, H2, dtype=np.float32)[:, None]
    ring *= np.clip(yy * 1.3, 0, 1)
    ring = cv2.GaussianBlur(ring, (0, 0), max(2, W2 * .01))
    out = np.zeros((H2, W2, 4), np.uint8)
    out[..., :3] = INK_WARM
    out[..., 3] = np.clip(ring * strength, 0, 255).astype(np.uint8)
    return out


def layer_over(bottom, top):
    """v9.1 (NEU): standard premultiplied-alpha 'over' compositor for stacking two finished
    (h,w,4) icon layers (e.g. trophy handles UNDER the cup body) - needed because several
    v9.1 icons are now built as more than one independently-shaded region-with-its-own-
    specular layer instead of a single regions() call."""
    ta = top[..., 3:4].astype(np.float32) / 255.
    out = np.zeros_like(bottom)
    out[..., :3] = np.clip(top[..., :3].astype(np.float32) + bottom[..., :3].astype(np.float32) * (1 - ta), 0, 255).astype(np.uint8)
    ba = bottom[..., 3:4].astype(np.float32) / 255.
    out[..., 3] = np.clip((ta + ba * (1 - ta)) * 255., 0, 255).astype(np.uint8)[..., 0]
    return out


def cast_shadow(sp, blur=18, off=(0, 16), a=.42, pad=60, col=(6, 5, 20)):
    """Soft drop shadow, same contract as assets_v3.with_shadow() (drop-in compatible),
    tuned slightly softer/darker to match the v9 material look."""
    h, w = sp.shape[:2]
    al = np.zeros((h + 2 * pad, w + 2 * pad), np.uint8)
    al[pad + off[1]:pad + off[1] + h, pad + off[0]:pad + off[0] + w] = sp[..., 3][:h, :w]
    al = cv2.GaussianBlur(al, (0, 0), blur)
    out = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8)
    out[..., :3] = (np.array(col, np.float32)[None, None] * (al[..., None] * a / 255.)).astype(np.uint8)
    out[..., 3] = (al * a).astype(np.uint8)
    inner = out[pad:pad + h, pad:pad + w].astype(np.float32)
    src = sp.astype(np.float32); sa = src[..., 3:4] / 255.
    out[pad:pad + h, pad:pad + w] = np.clip(src + inner * (1 - sa), 0, 255).astype(np.uint8)
    return out


def outline_and_fill(w, h, draw_shape_fn, col_top, col_bot, outline_px=None, S=None, H2=None):
    """The v9 'one shape, full material' helper: draw_shape_fn(draw, grow_px) must draw the
    silhouette (only, no color logic) onto a supersampled canvas at TWO passes internally is
    NOT needed here - this helper calls it once at grow=outline_px for the ink ring and once
    at grow=0 for the fill mask, then applies gradient + rim-shade + specular consistently.
    Returns a finished (w,h) premultiplied RGBA array, ready for cast_shadow()."""
    S = S or w * SS; H2 = H2 or h * SS
    ow = outline_px if outline_px is not None else max(4, int(S * .018))
    ink_im = Image.new('L', (S, H2), 0); draw_shape_fn(ImageDraw.Draw(ink_im), ow)
    ink_im = np.array(ink_im)
    fill_im = Image.new('L', (S, H2), 0); draw_shape_fn(ImageDraw.Draw(fill_im), 0)
    fill_mask = np.array(fill_im)
    body = gradient_mask_fill(fill_mask, col_top, col_bot)
    shade = rim_shade(fill_mask)
    sa = shade[..., 3:4] / 255.
    body[..., :3] = np.clip(body[..., :3].astype(np.float32) * (1 - sa * .55), 0, 255).astype(np.uint8)
    canvas = np.zeros((H2, S, 4), np.uint8)
    canvas[ink_im > 10] = list(INK) + [255]
    fa = (body[..., 3:4] / 255.)
    canvas[..., :3] = (canvas[..., :3].astype(np.float32) * (1 - fa) + body[..., :3].astype(np.float32) * fa).astype(np.uint8)
    canvas[..., 3] = np.maximum(canvas[..., 3], body[..., 3])
    ys, xs = np.where(fill_mask > 10)
    if len(xs):
        cx, cy = xs.mean(), ys.min() + (ys.max() - ys.min()) * .30
        rx = ry = (xs.max() - xs.min()) * .30
        hi = specular(S, H2, cx, cy, rx, ry * .6)
        ha = (hi[..., 3:4] / 255.) * (canvas[..., 3:4] / 255.)
        canvas[..., :3] = np.clip(canvas[..., :3].astype(np.float32) + hi[..., :3].astype(np.float32) * ha, 0, 255).astype(np.uint8)
    return _fin(Image.fromarray(canvas), w, h)


# ---------------------------------------------------------------- Text-auf-Asset (einziger Weg)
def text_plate(tx_engine, text, w, size=64, fill=WHITE, plate_fill=INK, plate_edge=None,
               pad_x=44, pad_y=26, radius=None):
    """The ONLY way an asset in this module puts text on itself. tx_engine MUST be the
    shared engine.Text instance (Raymi-Regular.ttf) already used for captions - there is no
    other code path here that could fall back to a default font (QC-Guidelines rule #1).
    Returns a finished rounded plate with the text baked in, premultiplied RGBA."""
    tile = tx_engine.tile(text, size, fill, INK)
    th, tw = tile.shape[:2]
    pw, ph = min(w, tw + pad_x * 2) if w else tw + pad_x * 2, th + pad_y * 2
    r = radius if radius is not None else ph * .32
    im = _canvas(pw, ph); d = ImageDraw.Draw(im); S, H2 = pw * SS, ph * SS
    edge = plate_edge or UV
    d.rounded_rectangle((0, 0, S - 1, H2 - 1), radius=r * SS, fill=tuple(edge) + (255,))
    e = max(4, int(S * .012))
    d.rounded_rectangle((e, e, S - 1 - e, H2 - 1 - e), radius=r * SS - e, fill=tuple(plate_fill) + (255,))
    plate = _fin(im, pw, ph)
    fit = min(1., (pw - pad_x * 1.2) / max(tw, 1))
    tw2, th2 = max(1, int(tw * fit)), max(1, int(th * fit))
    tile_rs = cv2.resize(tile, (tw2, th2), interpolation=cv2.INTER_AREA)
    x0, y0 = (pw - tw2) // 2, (ph - th2) // 2
    roi = plate[y0:y0 + th2, x0:x0 + tw2].astype(np.float32)
    src = tile_rs.astype(np.float32); a = src[..., 3:4] / 255.
    merged_rgb = np.clip(src[..., :3] * a + roi[..., :3] * (1 - a), 0, 255)
    merged_a = np.maximum(roi[..., 3:4], src[..., 3:4])
    plate[y0:y0 + th2, x0:x0 + tw2] = np.concatenate([merged_rgb, merged_a], axis=-1).astype(np.uint8)
    return plate


def regions(w, h, specs, S=None, H2=None, outline_px=None):
    """Multi-part shape compositor: specs = [(draw_fn(d), col_top, col_bot), ...], each
    draw_fn(d) draws ONE region's silhouette (white) onto a shared supersampled L canvas.
    Regions are gradient-filled + rim-shaded individually (so a two-tone object like a
    rice ball or a sponge keeps its correct per-part colors) and composited in the given
    z-order; ONE ink outline is derived from the union silhouette and ONE specular
    highlight is added over the combined shape, so the whole object still reads as one
    consistent, lit material instead of several flat-colored parts glued together."""
    S = S or w * SS; H2 = H2 or h * SS
    ow = outline_px if outline_px is not None else max(6, int(S * .018))
    masks = []
    for draw_fn, _, _ in specs:
        # draw_fn uses FINAL (w,h) coordinates (0..w, 0..h) for caller convenience, then gets
        # upscaled to the supersampled (S,H2) canvas - smoother than drawing at 1x and cheaper
        # than asking every caller to track two coordinate spaces.
        im = Image.new('L', (w, h), 0)
        draw_fn(ImageDraw.Draw(im))
        masks.append(cv2.resize(np.array(im), (S, H2), interpolation=cv2.INTER_LINEAR))
    union = np.zeros((H2, S), np.uint8)
    for m in masks:
        union = np.maximum(union, m)
    ink_grow = cv2.dilate(union, np.ones((ow, ow), np.uint8))
    canvas = np.zeros((H2, S, 4), np.uint8)
    canvas[ink_grow > 10] = list(INK) + [255]
    for m, (_, ct, cb) in zip(masks, specs):
        body = gradient_mask_fill(m, ct, cb)
        shade = rim_shade(m); sa = shade[..., 3:4] / 255.
        body[..., :3] = np.clip(body[..., :3].astype(np.float32) * (1 - sa * .4), 0, 255).astype(np.uint8)
        fa = body[..., 3:4] / 255.
        canvas[..., :3] = (canvas[..., :3] * (1 - fa) + body[..., :3] * fa).astype(np.uint8)
        canvas[..., 3] = np.maximum(canvas[..., 3], body[..., 3])
    ys, xs = np.where(union > 10)
    if len(xs):
        cx, cy = xs.mean(), ys.min() + (ys.max() - ys.min()) * .25
        r = (xs.max() - xs.min()) * .26
        hi = specular(S, H2, cx, cy, r, r * .5)
        ha = (hi[..., 3:4] / 255.) * (canvas[..., 3:4] / 255.)
        canvas[..., :3] = np.clip(canvas[..., :3].astype(np.float32) + hi[..., :3].astype(np.float32) * ha, 0, 255).astype(np.uint8)
    return _fin(Image.fromarray(canvas), w, h)


if __name__ == '__main__':
    print('raymi_style.py: palette + material pipeline, import from assets_v6.py')
