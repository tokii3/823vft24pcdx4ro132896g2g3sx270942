"""Raymi assets v4 - additional procedurally drawn support assets (extends assets_v3, never replaces it).
All return premultiplied RGBA. Same look: dark ink outline, flat bright fill."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from engine import premult
from assets_v3 import SS, INK, _fin, with_shadow

def _canvas(w, h): return Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))

def _outlined(d, S, draw_fn, ow):
    """draw_fn(d, grow_px, fill_override) - draws the shape set twice: grown in ink, then normal."""
    draw_fn(d, ow, INK); draw_fn(d, 0, None)

def nigiri(w=560):
    h = int(w * .66); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    def shapes(d, g, ink):
        d.rounded_rectangle((S * .12 - g, H2 * .46 - g, S * .88 + g, H2 * .92 + g), radius=H2 * .22 + g, fill=ink or (252, 251, 246, 255))
        d.rounded_rectangle((S * .04 - g, H2 * .10 - g, S * .96 + g, H2 * .62 + g), radius=H2 * .24 + g, fill=ink or (255, 132, 96, 255))
    _outlined(d, S, shapes, SS * 7)
    for i, x in enumerate((.24, .40, .56, .72)):   # fat stripes on the fish
        d.line((S * x, H2 * .17, S * (x - .05), H2 * .52), fill=(255, 200, 170, 255), width=int(SS * 9))
    d.rounded_rectangle((S * .10, H2 * .60, S * .90, H2 * .66), radius=SS * 6, fill=(226, 232, 244, 255))
    return _fin(im, w, h)

def soy(w=560):
    h = int(w * .55); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    d.ellipse((S * .03, H2 * .12, S * .97, H2 * .98), fill=INK); d.ellipse((S * .06, H2 * .16, S * .94, H2 * .92), fill=(246, 246, 250, 255))
    d.ellipse((S * .12, H2 * .24, S * .88, H2 * .80), fill=(58, 30, 22, 255)); d.ellipse((S * .22, H2 * .30, S * .48, H2 * .44), fill=(120, 74, 52, 255))
    for x, y, r in ((.66, .52, .03), (.74, .60, .02)): d.ellipse((S * (x - r), H2 * (y - r), S * (x + r), H2 * (y + r)), fill=(120, 74, 52, 255))
    return _fin(im, w, h)

def wasabi(w=460):
    h = int(w * .8); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    blobs = [(.50, .62, .40, .30), (.34, .48, .26, .26), (.66, .46, .24, .24), (.50, .30, .20, .20)]
    def shapes(d, g, ink):
        for cx, cy, rx, ry in blobs: d.ellipse((S * (cx - rx) - g, H2 * (cy - ry) - g, S * (cx + rx) + g, H2 * (cy + ry) + g), fill=ink or (128, 200, 66, 255))
    _outlined(d, S, shapes, SS * 7)
    d.ellipse((S * .26, H2 * .28, S * .42, H2 * .40), fill=(178, 228, 110, 255)); d.ellipse((S * .58, H2 * .26, S * .70, H2 * .35), fill=(178, 228, 110, 255))
    return _fin(im, w, h)

def sponge(w=520):
    h = int(w * .62); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    d.rounded_rectangle((S * .03, H2 * .06, S * .97, H2 * .96), radius=S * .06, fill=INK)
    d.rounded_rectangle((S * .06, H2 * .12, S * .94, H2 * .64), radius=S * .04, fill=(255, 214, 72, 255))
    d.rounded_rectangle((S * .06, H2 * .64, S * .94, H2 * .90), radius=S * .04, fill=(96, 188, 92, 255))
    for x, y, r in ((.20, .30, .05), (.42, .22, .04), (.62, .38, .06), (.80, .24, .04), (.32, .50, .035), (.86, .52, .04)):
        d.ellipse((S * (x - r), H2 * (y - r * 1.4), S * (x + r), H2 * (y + r * 1.4)), fill=(226, 164, 28, 255))
    return _fin(im, w, h)

def bowl(w=560):
    h = int(w * .82); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    d.ellipse((S * .12 - SS * 7, H2 * .06 - SS * 7, S * .88 + SS * 7, H2 * .66 + SS * 7), fill=INK); d.ellipse((S * .12, H2 * .06, S * .88, H2 * .66), fill=(252, 251, 246, 255))
    rng = np.random.RandomState(3)
    for _ in range(46):
        x, y = rng.uniform(.22, .78) * S, rng.uniform(.14, .44) * H2; r = S * .012
        d.ellipse((x - r, y - r * .6, x + r, y + r * .6), fill=(222, 228, 240, 255))
    d.pieslice((S * .03 - SS * 7, -H2 * .15 - SS * 7, S * .97 + SS * 7, H2 * 1.0 + SS * 7), 0, 180, fill=INK)
    d.pieslice((S * .03, -H2 * .15, S * .97, H2 * 1.0), 0, 180, fill=(84, 138, 226, 255))
    d.arc((S * .03, -H2 * .15, S * .97, H2 * 1.0), 20, 160, fill=(150, 190, 250, 255), width=SS * 8)
    return _fin(im, w, h)

def pizza(w=520):
    h = int(w * 1.0); im = _canvas(w, h); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    tri = [(.06, .14), (.94, .14), (.50, .97)]
    d.polygon([(x * S, y * H2) for x, y in tri], fill=INK, outline=INK, width=SS * 14)
    d.polygon([(x * S, y * H2) for x, y in [(.11, .17), (.89, .17), (.50, .90)]], fill=(255, 196, 72, 255))
    d.rounded_rectangle((S * .03, H2 * .05, S * .97, H2 * .20), radius=H2 * .075, fill=INK); d.rounded_rectangle((S * .06, H2 * .07, S * .94, H2 * .18), radius=H2 * .055, fill=(226, 150, 72, 255))
    for x, y, r in ((.32, .30, .07), (.64, .32, .07), (.48, .50, .065), (.50, .72, .05)):
        d.ellipse((S * (x - r) - SS * 4, H2 * (y - r) - SS * 4, S * (x + r) + SS * 4, H2 * (y + r) + SS * 4), fill=INK); d.ellipse((S * (x - r), H2 * (y - r), S * (x + r), H2 * (y + r)), fill=(214, 64, 58, 255))
    return _fin(im, w, h)

def plate(w, h, fill=(28, 24, 58), edge=(255, 255, 255), ew=6):
    """rounded label plate (premult RGBA)."""
    im = _canvas(w, h); d = ImageDraw.Draw(im); S, H2 = w * SS, h * SS
    d.rounded_rectangle((0, 0, S - 1, H2 - 1), radius=H2 * .30, fill=edge + (255,)); e = ew * SS
    d.rounded_rectangle((e, e, S - 1 - e, H2 - 1 - e), radius=H2 * .30 - e, fill=fill + (255,))
    return _fin(im, w, h)

def stamp_frame(w, h, col=(226, 52, 72)):
    """hollow double-border stamp rectangle (premult RGBA)."""
    im = _canvas(w, h); d = ImageDraw.Draw(im); S, H2 = w * SS, h * SS; c = col + (255,)
    d.rounded_rectangle((0, 0, S - 1, H2 - 1), radius=H2 * .16, outline=c, width=SS * 12)
    d.rounded_rectangle((SS * 22, SS * 22, S - 1 - SS * 22, H2 - 1 - SS * 22), radius=H2 * .10, outline=c, width=SS * 5)
    return _fin(im, w, h)

if __name__ == '__main__':
    sheet = Image.new('RGB', (2400, 700), (50, 44, 96)); x = 10
    for sp in (nigiri(380), soy(380), wasabi(300), sponge(360), bowl(340), pizza(300), plate(400, 110), stamp_frame(400, 150)):
        sp = with_shadow(sp) if sp.shape[0] > 120 else sp
        rgba = Image.fromarray(sp); sheet.paste(rgba, (x, 20), rgba); x += rgba.size[0] + 10
    sheet.save('/home/claude/w/assets_v4_sheet.png')
