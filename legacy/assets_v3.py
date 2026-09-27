"""Procedurally drawn support assets (no font glyph dependencies). All return premultiplied RGBA."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw
from engine import premult
SS = 3
INK = (28, 24, 58, 255)

def _fin(im, w, h): return premult(np.array(im.resize((w, h), Image.LANCZOS)))
def _mask_poly(w, h, pts, round_px):
    m = Image.new('L', (w * SS, h * SS), 0); ImageDraw.Draw(m).polygon([(x * w * SS, y * h * SS) for x, y in pts], fill=255)
    m = cv2.GaussianBlur(np.array(m), (0, 0), round_px * SS); return ((m > 120) * 255).astype(np.uint8)

def with_shadow(sp, blur=16, off=(0, 14), col=(8, 6, 30), a=.55, pad=50):
    h, w = sp.shape[:2]; al = np.zeros((h + 2 * pad, w + 2 * pad), np.uint8); al[pad + off[1]:pad + off[1] + h, pad + off[0]:pad + off[0] + w] = sp[..., 3][:h, :w]
    al = cv2.GaussianBlur(al, (0, 0), blur); out = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8)
    out[..., :3] = (np.array(col, np.float32)[None, None] * (al[..., None] * a / 255.)).astype(np.uint8); out[..., 3] = (al * a).astype(np.uint8)
    inner = out[pad:pad + h, pad:pad + w].astype(np.float32); src = sp.astype(np.float32); sa = src[..., 3:4] / 255.
    out[pad:pad + h, pad:pad + w] = np.clip(src + inner * (1 - sa), 0, 255).astype(np.uint8)
    return out

def onigiri(w=640):
    h = int(w * .95); m = _mask_poly(w, h, [(.5, .10), (.05, .86), (.95, .86)], 34); W2, H2 = w * SS, h * SS
    outline = cv2.dilate(m, np.ones((SS * 16 + 1, SS * 16 + 1), np.uint8))
    yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32); yy /= H2; xx /= W2
    rice = np.zeros((H2, W2, 3), np.float32); base = np.array([252, 251, 246], np.float32); shade = np.array([205, 214, 238], np.float32)
    t = np.clip((yy - .3) / .6 + (xx - .5) * .25, 0, 1)[..., None]; rice[:] = base * (1 - t * .55) + shade * t * .55
    rng = np.random.RandomState(4); g = Image.fromarray(rice.astype(np.uint8)); d = ImageDraw.Draw(g)
    for _ in range(90):
        x, y = rng.uniform(.14, .86) * W2, rng.uniform(.18, .55) * H2; r = rng.uniform(.012, .02) * W2
        d.ellipse((x - r, y - r * .6, x + r, y + r * .6), fill=(226, 230, 240))
    rice = np.array(g).astype(np.float32)
    nori = np.zeros_like(rice); nori[:] = (30, 40, 46); nori += (np.clip(1 - np.abs(xx - .30) * 6, 0, 1) * 34)[..., None] * np.array([.5, .8, .9])
    band = ((yy > .60 + .008 * np.sin(xx * 30)) & (xx > .27) & (xx < .73))[..., None]; col = np.where(band, nori, rice)
    rgba = np.zeros((H2, W2, 4), np.uint8); rgba[..., :3] = np.where(outline[..., None] > 0, np.array(INK[:3]), 0); rgba[..., 3] = outline
    inner = m > 0; rgba[inner, :3] = col[inner].astype(np.uint8)
    return _fin(Image.fromarray(rgba), w, h)

def badge(kind, w=360):
    im = Image.new('RGBA', (w * SS, w * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im); S = w * SS; c = S / 2
    fill = (236, 62, 88, 255) if kind == 'x' else (64, 208, 132, 255)
    d.ellipse((S * .04, S * .04, S * .96, S * .96), fill=INK); d.ellipse((S * .10, S * .10, S * .90, S * .90), fill=fill)
    d.ellipse((S * .16, S * .14, S * .70, S * .52), fill=tuple(min(255, v + 34) for v in fill[:3]) + (255,)) if False else None
    lw = int(S * .11)
    if kind == 'x':
        for a, b in (((.32, .32), (.68, .68)), ((.68, .32), (.32, .68))): d.line((a[0] * S, a[1] * S, b[0] * S, b[1] * S), fill=(255, 255, 255, 255), width=lw)
        for p in ((.32, .32), (.68, .68), (.68, .32), (.32, .68)): d.ellipse((p[0] * S - lw / 2, p[1] * S - lw / 2, p[0] * S + lw / 2, p[1] * S + lw / 2), fill=(255, 255, 255, 255))
    else:
        pts = [(.27 * S, .52 * S), (.44 * S, .68 * S), (.74 * S, .34 * S)]; d.line(pts, fill=(255, 255, 255, 255), width=lw, joint='curve')
        for p in (pts[0], pts[2]): d.ellipse((p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2), fill=(255, 255, 255, 255))
    return _fin(im, w, w)

def gavel(w=420):
    """upright gavel: handle vertical, head on top. pivot = handle bottom (w/2, h)."""
    h = int(w * 1.05); im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    d.rounded_rectangle((S * .44, H2 * .30, S * .56, H2 * .98), radius=S * .05, fill=INK); d.rounded_rectangle((S * .465, H2 * .32, S * .535, H2 * .96), radius=S * .035, fill=(196, 132, 74, 255))
    d.rounded_rectangle((S * .10, H2 * .02, S * .90, H2 * .34), radius=S * .09, fill=INK); d.rounded_rectangle((S * .14, H2 * .05, S * .86, H2 * .31), radius=S * .07, fill=(226, 164, 92, 255))
    for x in (.20, .80): d.rounded_rectangle((S * (x - .045), H2 * .02, S * (x + .045), H2 * .34), radius=S * .03, fill=(255, 214, 84, 255), outline=INK, width=SS * 3)
    d.rounded_rectangle((S * .30, H2 * .08, S * .60, H2 * .13), radius=S * .02, fill=(255, 236, 190, 255))
    return _fin(im, w, h)

def scroll(w=760):
    h = int(w * .52); im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im); S = w * SS; H2 = h * SS
    d.rounded_rectangle((S * .05, H2 * .10, S * .95, H2 * .90), radius=S * .03, fill=INK); d.rounded_rectangle((S * .075, H2 * .16, S * .925, H2 * .84), radius=S * .02, fill=(250, 240, 214, 255))
    for y in (.06, .78):
        d.rounded_rectangle((S * .02, H2 * y, S * .98, H2 * (y + .16)), radius=H2 * .08, fill=INK); d.rounded_rectangle((S * .035, H2 * (y + .03), S * .965, H2 * (y + .13)), radius=H2 * .05, fill=(226, 186, 120, 255))
    for i, yy in enumerate((.66, .72)): d.rounded_rectangle((S * .20, H2 * yy, S * (.80 - .1 * i), H2 * (yy + .022)), radius=SS * 4, fill=(214, 198, 160, 255))
    cx, cy, r = S * .86, H2 * .70, S * .06; d.ellipse((cx - r * 1.15, cy - r * 1.15, cx + r * 1.15, cy + r * 1.15), fill=INK); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(232, 72, 96, 255))
    return _fin(im, w, h)

def starburst(w=700, n=14, col=(255, 214, 84)):
    im = np.zeros((w, w, 4), np.uint8); c = w / 2; pts = []
    for i in range(n * 2):
        r = c * (.98 if i % 2 == 0 else .55); a = math.pi * i / n; pts.append((int(c + r * math.cos(a)), int(c + r * math.sin(a))))
    m = np.zeros((w, w), np.uint8); cv2.fillPoly(m, [np.array(pts, np.int32)], 255); m = cv2.GaussianBlur(m, (0, 0), 6)
    yy, xx = np.mgrid[0:w, 0:w]; rr = np.sqrt((xx - c) ** 2 + (yy - c) ** 2) / c; g = np.clip(1.15 - rr, 0, 1)
    a = (m * g).astype(np.uint8); im[..., :3] = (np.array(col)[None, None] * (a[..., None] / 255.)).astype(np.uint8); im[..., 3] = a
    return im

def sparkle(w=200):
    S = w * SS; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    d.polygon([(c, 0), (c + S * .09, c - S * .09), (S, c), (c + S * .09, c + S * .09), (c, S), (c - S * .09, c + S * .09), (0, c), (c - S * .09, c - S * .09)], fill=(255, 255, 255, 255))
    return _fin(im, w, w)

if __name__ == '__main__':   # asset sheet for a quick visual check
    sheet = Image.new('RGB', (2000, 560), (50, 44, 96)); x = 10
    for sp in (with_shadow(onigiri(380)), with_shadow(badge('x', 220)), with_shadow(badge('ok', 220)), with_shadow(gavel(260)), with_shadow(scroll(520))):
        rgba = Image.fromarray(sp); sheet.paste(rgba, (x, 20), rgba); x += rgba.size[0] + 10
    st = Image.fromarray(starburst(300)); sheet.paste(st, (10, 300), st); sp_ = Image.fromarray(sparkle(120)); sheet.paste(sp_, (350, 330), sp_)
    sheet.save('/home/claude/w/proof/assets_sheet.png')
