"""Raymi Engine v5 - landscape_demo_v5.py (NEU in v5)

Referenz-/Proof-Skript fuer 16:9-Querformat-Longform, analog zu proof_onigiri_v4.py fuer das
9:16-Hochformat (siehe ENGINE_NOTES.md: "NEUE VIDEOS = Kopie davon mit neuer BEATS-Config" -
fuer ein echtes Longform-Video dieses Skript kopieren und Inhalt/BEATS anpassen).

Zeigt konkret:
 - engine.set_orientation('landscape') + die from-import-*-Falle (siehe Docstring von
   engine.set_orientation) - W/H muessen danach lokal neu gezogen werden
 - layout_preset() statt hart codierter Hochformat-Zahlen: Hero-Anker, Caption-Zone,
   Text-Panel passen sich automatisch an die aktuelle Orientierung an
 - klassisches Longform-/Explainer-Layout: Hero rechts im Bild (nicht bildfuellend wie im
   Hochformat-Short), linkes Textpanel fuer Titel/Fakten, Karaoke-Caption unten in einer
   auf caption_maxw begrenzten Zone (keine ueber-volle-Breite-Caption wie im 9:16-Format)
 - dieselben v5-Cut-FX (Chroma/Impact-Lines) und die Progress-Bar/Loop-Seam funktionieren
   unveraendert, weil sie in engine.py bereits relativ zu W/H rechnen

Braucht KEIN echtes Voiceover zum Testen: benutzt engine.word_times() fuer geschaetztes
Timing (derselbe Zwischenschritt, den ENGINE_NOTES.md fuer die allererste Skript-Fassung vor
dem echten Voiceover beschreibt). Exportiert keine fertige Videodatei, nur Stand-Frames zur
Kontrolle (Befehl `stills`) - fuer ein echtes Video: Kopie machen, echtes Voiceover +
align()-Pipeline wie in raymi_short.py einbauen, dann render/finish wie gewohnt.
"""
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine
from engine import *   # ACHTUNG: W/H/FPS sind hier noch die PORTRAIT-Default-Werte (siehe unten)
import assets_v6 as A   # FIX (2026-09-26 QA-Pass): war assets_v3/assets_v4 (A4 wurde hier nie benutzt) - siehe raymi_short.py
import paths

engine.set_orientation('landscape')          # 1920x1080 - siehe engine.ORIENTATIONS fuer weitere Presets (landscape_hq/landscape_4k)
W, H, FPS = engine.W, engine.H, engine.FPS   # v5: NACH set_orientation lokal neu ziehen (from-import-*-Falle, siehe engine.py)

PNG = paths.asset_dir('PNG', extra_globs=['/home/claude/w/assets/PNG'])
BGD = paths.asset_dir('Background', extra_globs=['/home/claude/w/assets/Background'])
OUT = os.path.join(HERE, 'render_landscape_demo'); os.makedirs(OUT, exist_ok=True)
CAT = {c['file']: c for c in json.load(open(HERE + '/sprite_catalog.json'))}
TX = Text(find_font())
CYAN, GOLD = (120, 225, 255), (255, 214, 84)   # gleiche Akzentfarben wie proof_onigiri_v4.py (nicht in engine.py, pro Skript definiert)
LP = engine.layout_preset()   # Hero-Anker/Caption-Zone/Textpanel fuer die AKTUELLE Orientierung

# ---- Platzhalter-Inhalt fuer die Demo (kein echtes Voiceover noetig) -------------------------
SENTS = [
    dict(text="raymi's ocean facts.", s=0.0, e=1.6),
    dict(text="stingrays are not related to sharks the way most people assume.", s=1.9, e=5.8),
]
WORDS = []
for s in SENTS:
    WORDS += word_times(s['text'], s['s'], s['e'])
DUR = SENTS[-1]['e'] + 1.6
CUT_AT = 1.75   # eine Beispiel-Schnittstelle, um die v5-Cut-FX auch im Querformat zu zeigen

RAY = 'RAY_WS_F_HAPPY_PLAY_UV_010.png'
BG = 'bg hai.png'

_S, _BG_, _AU = {}, {}, {}
def sprite():
    if 'ray' not in _S:
        cat = CAT[RAY]; im = load_sprite(os.path.join(PNG, RAY), cat)
        fitted = fit_sprite(im, width=LP['hero_width']); _S['ray'] = fitted; _AU['ray'] = make_aura(fitted)
    return _S['ray'], _AU['ray']

def bgimg():
    if 'bg' not in _BG_:
        p = os.path.join(BGD, BG); _BG_['bg'] = cover(cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB), int(H * 1.25))
    return _BG_['bg']

def _core_frame(t):
    t = min(t, DUR - 1e-3)
    fr = bg_frame(bgimg(), t, dur=DUR + 1).astype(np.float32)
    fr = fr * np.array([.55, .50, .78], np.float32) * vignette()
    fr = np.clip(fr + np.array([18, 10, 40], np.float32) * .6, 0, 255).astype(np.uint8)
    particles(fr, t, 3, n=18)

    # Hero: rechtes Drittel statt bildfuellend (layout_preset() liefert den Anker/die Breite)
    sp, (au, pad) = sprite(); h, w = sp.shape[:2]
    breath = energy_shimmer(t, amp=.018); rot = 2.4 * math.sin(2 * math.pi * t / 3.6)
    fx_, fy_ = LP['hero_x'], LP['hero_y']
    blit(fr, au, w / 2 + pad, h + pad, fx_, fy_, s=breath, rot=rot, alpha=.6, add=True)
    blit(fr, sp, w / 2, h, fx_, fy_, s=breath, rot=rot)

    # linkes Textpanel: Titel-Karte (klassisches Longform-/Explainer-Layout)
    panel_w = LP['panel_x1'] - LP['panel_x0']
    title = TX.tile('OCEAN FACTS', 92, UVL, DARK); fit_ = min(1., .82 * panel_w / title.shape[1])
    blit(fr, title, title.shape[1] / 2, title.shape[0] / 2, LP['panel_x0'] + panel_w / 2, LP['safe_top'] + 56, s=fit_)

    # Karaoke-Caption unten, auf caption_maxw begrenzt (keine volle Bildbreite wie im Hochformat)
    act = max([i for i, wd in enumerate(WORDS) if wd['s'] <= t] or [0])
    lo, hi = max(0, act - 1), min(len(WORDS), act + 2)
    if WORDS[lo]['s'] - .12 <= t <= WORDS[hi - 1]['e'] + .3:
        tiles = [(TX.tile(WORDS[i]['w'], 58, GOLD if i == act else WHITE), i) for i in range(lo, hi)]
        gap = 18; tot = sum(tl.shape[1] for tl, _ in tiles) + gap * (len(tiles) - 1)
        cfit = min(1., LP['caption_maxw'] / max(tot, 1)); x = W / 2 - tot * cfit / 2
        for tl, i in tiles:
            blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, x + tl.shape[1] * cfit / 2, LP['caption_y'], s=cfit)
            x += (tl.shape[1] + gap) * cfit

    # v5-Cut-FX auch im Querformat: gleiche Funktionen, rechnen automatisch relativ zu W/H
    d = t - CUT_AT
    if -.10 <= d < .16:
        fr = fx_zoom(fr, lerp(1.28, 1.0, ease_out(clamp(d / .16))) if d >= 0 else 1 + .35 * smooth((d + .10) / .10))
        fr = fx_flash(fr, .35 * clamp(1 - abs(d) / .06)); fr = fx_chroma(fr, .7 * clamp(1 - abs(d) / .10))
        if 0 <= d < .14: fr = fx_impact_lines(fr, 1 - d / .14, seed=1)
    fr = progress_bar(fr, t / DUR)
    return fr

_FIRST = {}
def frame(t):
    fr = _core_frame(t)
    if t > DUR - 0.30:
        if 'f' not in _FIRST: _FIRST['f'] = _core_frame(0.0)
        fr = loop_seam(fr, _FIRST['f'], t, DUR, blend=0.30)
    return fr

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'stills'
    if cmd == 'stills':
        from PIL import Image
        pts = [0.05, 1.0, 1.80, 4.0, DUR - 0.05]
        for tt in pts:
            Image.fromarray(frame(tt)).save(f'{OUT}/still_{tt:05.2f}.png')
        print('stills ok ->', OUT, '| W,H,FPS =', W, H, FPS)
    else:
        print("Befehle: 'stills' (Testbilder). Fuer ein echtes Video: Skript kopieren und die "
              "align()/build_audio()/render-Kommandos aus raymi_short.py uebernehmen.")
