"""Raymi Engine v3 - core (catalog-driven placement, idle motion, transitions, karaoke captions).
Single canonical engine: extend this file, never rewrite it in a new session."""
import math, os, re, glob, json, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
W, H, FPS = 1080, 1920, 30
UV, UVL, PINK, DARK, WHITE = (167, 108, 255), (208, 176, 255), (255, 130, 190), (22, 20, 46), (255, 255, 255)

def clamp(x, a=0., b=1.): return max(a, min(b, x))
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def back_out(x, s=1.9): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def lerp(a, b, t): return a + (b - a) * t
def premult(a):
    a = a.copy(); a[..., :3] = (a[..., :3].astype(np.uint16) * a[..., 3:4] // 255).astype(np.uint8); return a

# ------------------------------------------------------------------ sprites
def load_sprite(path, cat, flip=False):
    """Crop to bbox; remove baked-in white halo (cat.halo>0.5) by eroding + feathering alpha."""
    im = np.array(Image.open(path).convert('RGBA'))
    if cat.get('halo', 0) > 0.5:
        a = im[..., 3]; solid = (a > 128).astype(np.uint8)
        er = cv2.erode(solid, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=2)
        na = cv2.GaussianBlur(er * 255, (0, 0), 1.3)
        im[..., 3] = np.minimum(a, na)
    x, y, w, h = cat['bbox']; im = im[y:y + h, x:x + w]
    if flip: im = im[:, ::-1].copy()
    return im

def fit_sprite(im, width=None, height=None):
    h, w = im.shape[:2]; s = (width / w) if width else (height / h)
    return premult(cv2.resize(im, (max(2, int(w * s)), max(2, int(h * s))), interpolation=cv2.INTER_AREA))

def blit(fr, sp, px, py, fx, fy, s=1.0, rot=0.0, alpha=1.0, sy=None, add=False):
    """Draw premultiplied RGBA sp so that sprite point (px,py) lands on frame (fx,fy); scale s, rotation deg (about that point)."""
    if alpha <= .004 or s <= .01: return
    sx = s; sy = s if sy is None else sy; h, w = sp.shape[:2]; th = math.radians(rot); c, sn = math.cos(th), math.sin(th)
    ox, oy = fx - (c * sx * px - sn * sy * py), fy - (sn * sx * px + c * sy * py)
    xs, ys = [], []
    for qx, qy in ((0, 0), (w, 0), (w, h), (0, h)):
        xs.append(ox + c * sx * qx - sn * sy * qy); ys.append(oy + sn * sx * qx + c * sy * qy)
    x0, x1 = max(0, int(math.floor(min(xs)))), min(W, int(math.ceil(max(xs))))
    y0, y1 = max(0, int(math.floor(min(ys)))), min(H, int(math.ceil(max(ys))))
    if x1 <= x0 or y1 <= y0: return
    M = np.float32([[c * sx, -sn * sy, ox - x0], [sn * sx, c * sy, oy - y0]])
    wr = cv2.warpAffine(sp, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0)).astype(np.float32)
    roi = fr[y0:y1, x0:x1].astype(np.float32); rgb, a = wr[..., :3] * alpha, wr[..., 3:4] / 255. * alpha
    fr[y0:y1, x0:x1] = np.clip(roi + rgb if add else rgb + roi * (1 - a), 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ text
class Text:
    def __init__(self, font_path): self.fp, self._f, self._t = font_path, {}, {}
    def tile(self, txt, size, fill=WHITE, stroke=DARK):
        k = (txt, int(size), fill, stroke)
        if k in self._t: return self._t[k]
        size = int(size); f = self._f.setdefault(size, ImageFont.truetype(self.fp, size)); sw = max(4, size // 9)
        l, t, r, b = f.getbbox(txt, stroke_width=sw)
        im = Image.new('RGBA', (r - l + 2 * sw + 8, b - t + 2 * sw + 8), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((-l + sw + 4, -t + sw + 4), txt, font=f, fill=fill + (255,), stroke_width=sw, stroke_fill=stroke + (255,))
        self._t[k] = premult(np.array(im)); return self._t[k]

def syl(w):
    w = re.sub(r"[^a-z']", '', w.lower()); n = len(re.findall(r'[aeiouy]+', w)); return max(1, n)

def word_times(line, start, end):
    toks = line.split(); wts = [syl(t) * 1.0 + (1.2 if t[-1] in ',.!?' else 0) + 0.3 for t in toks]
    tot, t, out = sum(wts), start, []
    for tk, w in zip(toks, wts):
        d = (end - start) * w / tot; out.append(dict(w=tk, n=re.sub(r"[^a-z']", '', tk.lower()), s=t, e=t + d * .9)); t += d
    return out

def find_words(words, phrase):
    ph = [re.sub(r"[^a-z']", '', p.lower()) for p in phrase.split()]
    for i in range(len(words) - len(ph) + 1):
        if all(words[i + k]['n'] == ph[k] for k in range(len(ph))): return list(range(i, i + len(ph)))
    return []

# ------------------------------------------------------------------ background / fx
def cover(img, hh):
    h, w = img.shape[:2]; s = max(hh / h, hh * W / H / w); return cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA)

def bg_frame(bg, t, zoom=(1.05, 1.16), drift=(-0.06, 0.03), dur=8.0):
    ph, pw = bg.shape[:2]; z = lerp(*zoom, clamp(t / dur)); ch = ph / z; cw = ch * W / H
    cx = pw / 2 + drift[0] * pw * clamp(t / dur) ; cy = ph / 2 + drift[1] * ph * clamp(t / dur)
    x0 = min(max(cx - cw / 2, 0), pw - cw); y0 = min(max(cy - ch / 2, 0), ph - ch); k = W / cw
    return cv2.warpAffine(bg, np.float32([[k, 0, -x0 * k], [0, k, -y0 * k]]), (W, H), flags=cv2.INTER_LINEAR)

_vig = None
def vignette():
    global _vig
    if _vig is None:
        yy, xx = (np.arange(H)[:, None] - H / 2) / (H / 2), (np.arange(W)[None, :] - W / 2) / (W / 2)
        r = np.clip((np.sqrt(xx ** 2 + yy ** 2) / 1.414 - .3) / .7, 0, 1); _vig = (1 - .35 * r * r * (3 - 2 * r))[..., None].astype(np.float32)
    return _vig

def particles(fr, t, seed, n=16, color=(150, 110, 255)):
    rng = np.random.RandomState(seed); ov = np.zeros_like(fr)
    for _ in range(n):
        x0, sp, r, ph = rng.uniform(0, W), rng.uniform(40, 130), rng.uniform(4, 11), rng.uniform(0, 6.28)
        y = H - ((sp * t + rng.uniform(0, H)) % (H + 40)); x = x0 + 26 * math.sin(t * 1.2 + ph)
        cv2.circle(ov, (int(x), int(y)), int(r), color, -1, cv2.LINE_AA)
    ov = cv2.GaussianBlur(ov, (0, 0), 3); fr[:] = cv2.add(fr, (ov * .55).astype(np.uint8))

# ------------------------------------------------------------------ transitions (post-process a rendered scene frame)
def fx_zoom(fr, k):
    if abs(k - 1) < .003: return fr
    M = np.float32([[k, 0, W / 2 * (1 - k)], [0, k, H / 2 * (1 - k)]]); z = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    M2 = np.float32([[k * .93, 0, W / 2 * (1 - k * .93)], [0, k * .93, H / 2 * (1 - k * .93)]]); z2 = cv2.warpAffine(fr, M2, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.addWeighted(z, .8, z2, .2, 0)

def fx_glitch(fr, amt, seed):
    if amt <= .01: return fr
    rng = np.random.RandomState(seed); out = fr.copy(); sh = int(28 * amt)
    out[..., 0] = np.roll(fr[..., 0], sh, 1); out[..., 2] = np.roll(fr[..., 2], -sh, 1)
    for _ in range(int(7 * amt) + 1):
        y = rng.randint(0, H - 90); hh = rng.randint(20, 90); out[y:y + hh] = np.roll(out[y:y + hh], rng.randint(-90, 90), 1)
    return out

def fx_flash(fr, m, color=(255, 255, 255)):
    if m <= .01: return fr
    return np.clip(fr.astype(np.float32) * (1 - m) + np.array(color, np.float32) * m, 0, 255).astype(np.uint8)

def find_font(name='Raymi-Regular.ttf'):
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(here, name)): return os.path.join(here, name)
    for base in ('/mnt/user-data/uploads', '/home/claude/w'):
        for f in glob.glob(base + '/**/*', recursive=True):
            if os.path.basename(f).lower().replace('__1_', '') == name.lower(): return f

def make_aura(sp, pad=90, sigma=26, tint=(140, 95, 255)):
    h, w = sp.shape[:2]; a = np.zeros((h + 2 * pad, w + 2 * pad), np.uint8); a[pad:pad + h, pad:pad + w] = sp[..., 3]
    a = cv2.GaussianBlur(a, (0, 0), sigma); out = np.zeros(a.shape + (4,), np.uint8)
    out[..., :3] = (np.array(tint, np.float32)[None, None] * (a[..., None] / 255.)).astype(np.uint8); out[..., 3] = a; return out, pad

def fx_shake(fr, amp, t):
    if amp < .5: return fr
    M = np.float32([[1, 0, amp * math.sin(t * 95)], [0, 1, amp * math.cos(t * 83)]]); return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ------------------------------------------------------------------ v5 additions: punchier transitions / less static idle look
# REGEL bleibt: engine.py wird ERWEITERT, nichts oben wird geloescht/umgeschrieben.
# Grund fuer diesen Block (Nutzerfeedback v5): Animationen/Transitions "wirken noch
# statisch", Schnitte "nicht deutlich genug erkennbar" -> mehr sichtbare Wucht pro Cut,
# mehr durchgehende Energie im Idle (nicht nur bei Emphasis-Woertern).

def fx_chroma(fr, amt, shift=10):
    """RGB channel split ('chromatic aberration' punch). amt 0..1, only visibly kicks
    in near cuts - cheap, big perceived-impact win, stacks well with fx_zoom/fx_flash."""
    if amt <= .01: return fr
    sh = max(1, int(shift * amt)); out = fr.copy()
    out[..., 0] = np.roll(fr[..., 0], sh, 1); out[..., 2] = np.roll(fr[..., 2], -sh, 0)
    return cv2.addWeighted(out, amt, fr, 1 - amt, 0)

def fx_impact_lines(fr, amt, seed=0, n=14, color=(255, 255, 255)):
    """Radial speed-lines flashing out from center - classic manga/anime 'hit' punch-in cue,
    makes a cut register instantly even on a muted phone speaker. amt 0..1 (peaks at cut, decays fast)."""
    if amt <= .01: return fr
    rng = np.random.RandomState(seed); ov = np.zeros_like(fr); cx, cy = W / 2, H * .42
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(60, 140); r1 = r0 + rng.uniform(260, 620)
        x0, y0 = cx + r0 * math.cos(a), cy + r0 * math.sin(a); x1, y1 = cx + r1 * math.cos(a), cy + r1 * math.sin(a)
        cv2.line(ov, (int(x0), int(y0)), (int(x1), int(y1)), color, rng.randint(2, 5), cv2.LINE_AA)
    ov = cv2.GaussianBlur(ov, (0, 0), 1.1)
    return np.clip(fr.astype(np.float32) + ov.astype(np.float32) * (amt * .8), 0, 255).astype(np.uint8)

def fx_whip(fr, amt, angle=0.0):
    """Directional motion-blur whip (for a 'whip-pan' transition option). amt 0..1 = blur strength."""
    if amt <= .01: return fr
    k = max(3, int(28 * amt)) | 1
    kernel = np.zeros((k, k), np.float32); kernel[k // 2, :] = 1.0
    if angle:
        M = cv2.getRotationMatrix2D((k / 2, k / 2), angle, 1.0); kernel = cv2.warpAffine(kernel, M, (k, k))
    s = kernel.sum()
    if s > 0: kernel /= s
    blurred = cv2.filter2D(fr, -1, kernel)
    return cv2.addWeighted(blurred, amt, fr, 1 - amt, 0)

def energy_shimmer(t, base=1.0, speed=1.0, amp=0.028):
    """Small continuous multiplicative wobble so hero sprites never sit perfectly still between
    beats/emphasis pops. Cheap 2-term sine, meant to be multiplied into an existing scale factor."""
    return base * (1 + amp * math.sin(2 * math.pi * t * 1.7 * speed) + amp * .5 * math.sin(2 * math.pi * t * 3.9 * speed + 1.3))

def progress_bar(fr, frac, color=(255, 214, 84), bg=(255, 255, 255), y=10, h=8, pad=0.06):
    """Thin animated fill bar (retention/gamification cue: viewers who can see 'how much is
    left' are measurably more likely to watch to the end - see ENGINE_NOTES_v5.md). frac 0..1."""
    frac = clamp(frac); x0, x1 = int(W * pad), int(W * (1 - pad)); span = x1 - x0
    cv2.line(fr, (x0, y), (x1, y), bg, h, cv2.LINE_AA)
    if frac > 0.002:
        cv2.line(fr, (x0, y), (x0 + int(span * frac), y), color, h, cv2.LINE_AA)
    return fr

def loop_seam(fr_now, fr_first, t, dur, blend=0.30):
    """Cross-fades the last `blend` seconds of the clip into the FIRST rendered frame of the
    hook, so a looped replay (autoplay / Shorts re-loop) has no visible jump-cut - makes the
    loop feel intentional instead of a hard restart, which YouTube's own guidance ties to
    rewatch-driven retention on Shorts (see ENGINE_NOTES_v5.md)."""
    if t < dur - blend: return fr_now
    m = clamp((t - (dur - blend)) / blend)
    return cv2.addWeighted(fr_now, 1 - m, fr_first, m, 0)

# ------------------------------------------------------------------ v5 additions: Querformat/Landscape
# WARUM DAS EINFACH GEHT: jede Funktion oben liest W/H als MODUL-GLOBALS zur Laufzeit (nicht als
# beim def() eingefrorene Werte) - cover(), bg_frame(), vignette(), blit(), alle fx_*-Funktionen
# und progress_bar() rechnen bereits relativ zu W/H. Heisst: W/H einmal zentral umschalten reicht,
# OHNE eine einzige der Funktionen oben anzufassen (REGEL: nur erweitern). Was NICHT automatisch
# mitgeht: die Sprite-/Caption-PLATZIERUNG (px,py-Koordinaten) in den einzelnen Szenen-Skripten
# (proof_onigiri_v4.py, raymi_short.py) - die sind fuer das 9:16-Hochformat komponiert. Fuer
# Querformat-Videos gilt weiter die REGEL aus ENGINE_NOTES.md: neue Szene = Kopie eines
# Referenz-Skripts + eigene BEATS-Config - dafuer siehe landscape_demo_v5.py (Referenz fuer
# 16:9, analog zu proof_onigiri_v4.py fuer 9:16) und layout_preset() unten fuer sinnvolle
# Default-Anker/Sicherheitsraender pro Format.

ORIENTATIONS = {
    # (Breite, Hoehe, fps) - 'portrait' bleibt der bisherige, ungeaenderte Default (Shorts/Reels).
    'portrait':      (1080, 1920, 30),   # Shorts/TikTok/Reels 9:16 - Bisheriges Verhalten, unveraendert
    'landscape':     (1920, 1080, 30),   # Standard-YouTube-Longform 16:9, 1080p
    'landscape_hq':  (2560, 1440, 30),   # hoehere Aufloesung fuer besonders hochwertige Longform-Exports (1440p)
    'landscape_4k':  (3840, 2160, 30),   # 4K, falls die Quell-PNGs/Backgrounds die Aufloesung hergeben
}

def set_orientation(mode='portrait', w=None, h=None, fps=None):
    """Zentraler Schalter fuer die Bildformat/Aufloesung. Am Anfang eines Szenen-Skripts aufrufen,
    z.B. `engine.set_orientation('landscape')` fuer ein 16:9-Longform-Video. w/h/fps ueberschreiben
    optional die Preset-Werte (z.B. eigene Zielaufloesung). Muss VOR dem ersten sprite()/bgimg()/
    frame()-Aufruf passieren, weil Sprite-Fit und Hintergrund-Cover-Groesse von W/H abhaengen.

    WICHTIGE FALLE bei `from engine import *`: dieser Stern-Import KOPIERT W/H/FPS als eigene Namen
    in das importierende Skript - ruft das Skript set_orientation() NACH diesem Import auf, bleiben
    die Namen W/H/FPS IM SKRIPT SELBST auf den alten Werten stehen (Python kopiert Werte, keine
    Referenzen). Alle Funktionen INNERHALB engine.py sind davon nicht betroffen (die lesen ihre
    eigenen Modul-Globals neu), aber ein Szenen-Skript, das selbst `W`/`H` benutzt (z.B. in sprite()/
    bgimg()), MUSS direkt danach `W, H, FPS = engine.W, engine.H, engine.FPS` setzen. Siehe
    landscape_demo_v5.py fuer das komplette Muster."""
    global W, H, FPS, _vig
    pw, ph, pfps = ORIENTATIONS.get(mode, ORIENTATIONS['portrait'])
    W, H, FPS = (w or pw), (h or ph), (fps or pfps)
    _vig = None   # Vignette-Cache ist auf die alte Aufloesung gerendert - muss neu gebaut werden
    return W, H, FPS

def is_landscape(): return W > H

def layout_preset():
    """Liefert sinnvolle Default-Anker/Sicherheitsraender fuer die AKTUELL gesetzte Orientierung,
    als Ausgangspunkt fuer neue Szenen-Skripte (siehe landscape_demo_v5.py fuer die Anwendung):
      hero_x, hero_y   - empfohlener Ankerpunkt (Fussspitze/Bildmitte des Sprites) in Bildkoordinaten
      hero_width       - empfohlene Sprite-Zielbreite (px)
      caption_y        - empfohlene vertikale Position fuer Karaoke-Untertitel
      caption_maxw     - empfohlene maximale Textbreite, bevor umgebrochen wird
      safe_top/bottom  - Rand, der wegen Plattform-UI (Shorts-Buttons rechts, YT-Fortschrittsleiste
                          unten, Longform-Endcards oben rechts) frei bleiben sollte
    Portrait-Werte entsprechen dem, was proof_onigiri_v4.py/raymi_short.py bisher hart verdrahtet
    hatten (nur jetzt als benannte Konstanten statt Magic Numbers in jeder Szene)."""
    if is_landscape():
        return dict(hero_x=W * 0.74, hero_y=H * 0.98, hero_width=W * 0.34,
                     caption_y=H * 0.80, caption_maxw=W * 0.52,
                     safe_top=H * 0.06, safe_bottom=H * 0.08,
                     panel_x0=W * 0.04, panel_x1=W * 0.50)   # linkes Textfeld fuer Titel/Fakten/B-Roll
    return dict(hero_x=W * 0.5, hero_y=H * 0.98, hero_width=W * 1.0,
                caption_y=H * 0.79, caption_maxw=W * 0.86,
                safe_top=H * 0.09, safe_bottom=H * 0.14,
                panel_x0=W * 0.06, panel_x1=W * 0.94)
