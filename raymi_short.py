"""Raymi short builder v4.1 - copy of proof_onigiri_v4 logic, generalised:
 - reads a voiceover mp3 + input text, finds sentence boundaries from pauses, tightens the pauses,
 - word times = engine.word_times() inside each real sentence window (replace with _words.json when available),
 - loop-friendly: last beat re-uses the hook pose/background, audio has no long tail.
Usage: py raymi_short.py <sushi|meal> <align|audio|stills t..|video a b|finish>"""
import sys, os, re, json, math, subprocess, glob, wave, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from engine import *
# FIX (2026-09-26 QA-Pass): dieses Skript importierte bisher assets_v3/assets_v4 (flacher
# Fill, kein Material-Look) - assets_v6 existiert bereits, ist laut eigenem Docstring 1:1
# drop-in-kompatibel ("Funktionsnamen/Signaturen sind absichtlich drop-in-kompatibel zu
# assets_v3/v4/v5"), lief aber in KEINEM Render-Skript. Das war die Hauptursache fuer
# "Asset-Generierung schwach/lieblos": alle bisherigen Kurzvideos nutzten den alten,
# flachen Look statt der laengst gebauten Gradient/Rim-Shade/Specular-Pipeline + der
# wiederverwendbaren assets_library/-Cache. A4 (assets_v4) entfaellt, da assets_v6 alle
# frueher aus v4 genutzten Funktionen (nigiri/soy/wasabi/sponge/bowl/pizza/plate) bereits
# selbst mitbringt - siehe ENGINE_NOTES_v10.md.
import assets_v6 as A
import paths, cache_util, audio_mix   # v5: portable paths + disk cache + shared tuned audio mix (see ENGINE_NOTES_v5.md)
import engagement as E   # v6: mandatory comment-bait beat, config-driven via CFG[...]['cta']

SHORT = sys.argv[1]
UP = paths.upload_dir()
PNG = paths.asset_dir('PNG', extra_globs=['/home/claude/w/assets/PNG'])
BGD = paths.asset_dir('Background', extra_globs=['/home/claude/w/assets/Background'])
MUS = paths.asset_dir('Background-Music', extra_globs=['/home/claude/w/assets/Background-Music'])
OUT = os.path.join(HERE, f'render_{SHORT}'); os.makedirs(OUT, exist_ok=True); os.makedirs(paths.output_dir(), exist_ok=True)
CAT = {c['file']: c for c in json.load(open(HERE + '/sprite_catalog.json'))}
TX = Text(find_font()); CYAN, GOLD, RED, GREEN = (120, 225, 255), (255, 214, 84), (236, 62, 88), (64, 208, 132)
SR = 44100
S_ = lambda n: 'RAY_' + n.replace('#', '_UV_') + '.png'
def hero(n, **k): return dict(mode='hero', sprite=S_(n), **k)
def inset(n, **k): return dict(mode='inset', sprite=S_(n), **k)
def xcu(n, **k): return dict(mode='xcu', sprite=S_(n), **k)
BG = dict(a='bg rochen klein 2.png', b='bg hai.png', c='bg rochen viele klein.png', d='pc quallen klein.png', e='bg rochen groß nahaufnahme.png')

# =========================================================================== CONFIG (per short)
CFG = {}
CFG['sushi'] = dict(
    mp3='voiceover_sushi.mp3', txt='input_used_sushi.txt', music='bg_quirky.m4a', out='Raymi_Short_Sushi.mp4',
    hook=[("I SAW HOW", WHITE), ("YOU EAT", WHITE), ("SUSHI", GOLD)],
    cta=("worst sushi crime you've witnessed??", "confess in the comments (¬‿¬)"),  # v6: mandatory, see engagement.py
    trans=[None, 'zoompunch', 'zoompunch', 'glitch', 'zoompunch', 'zoompunch', 'glitch', 'zoompunch', 'glitch', 'zoompunch'],
    beats=[
     dict(n=2, bg=BG['a'], emph=['sushi', 'anything'], split_at=['not'], segs=[hero('WS_F_NEUTRAL_CALM#023', cut='none'), hero('WS_F_SMUG_PLAY#045', flip=True, cut='punch', xoff=30)],
          assets=[dict(kind='nigiri', trig='sushi', pos=(.83, .60), size=.32, dur=1.5)]),
     dict(n=1, bg=BG['b'], emph=['judging', 'spiritual level'], split_at=['judging'], segs=[hero('WS_F_NEUTRAL_CALM#037', cut='none', xoff=-20), hero('WS_F_UPSET_DRAMA#048', cut='slide', dirn=1)],
          assets=[dict(kind='gavel', trig='judging', pos=(.80, .34), size=.36, dur=1.4, shake=14, t_off=-.05)]),
     dict(n=2, bg=BG['c'], emph=['three crimes', 'at least one'], split_at=['and'], segs=[hero('WS_F_SURPRISE_DRAMA#028', cut='none'), inset('WS_F_SMUG_PLAY#045', flip=True, cut='punch')],
          assets=[dict(kind='scroll', trig='crimes', pos=(.5, .215), size=.84, dur=2.3, text=[('3 CRIMES', 170, -.055, (70, 40, 48)), ('YOU DID ONE', 90, .09, (176, 60, 82))])]),
     dict(n=1, bg=BG['d'], emph=['soy sauce', 'swimming pool'], split_at=['swimming'], segs=[hero('WS_F_UPSET_DRAMA#032', cut='slide', dirn=1), hero('WS_F_WORRIED_DRAMA#024', flip=True, cut='punch')],
          assets=[dict(kind='label', trig='one', pos=(.5, .13), size=.55, dur=2.0, text='CRIME 1', col=RED, tsize=150), dict(kind='soy', trig='soy', pos=(.80, .62), size=.40, dur=1.9)]),
     dict(n=1, bg=BG['a'], emph=['wasabi', 'crying'], split_at=['strong'], segs=[hero('WS_F_NEUTRAL_CALM#026', cut='punch'), hero('WS_F_CRY_DRAMA#043', cut='punch')],
          assets=[dict(kind='label', trig='two', pos=(.5, .13), size=.55, dur=2.0, text='CRIME 2', col=RED, tsize=150), dict(kind='wasabi', trig='wasabi', pos=(.83, .62), size=.30, dur=1.8)]),
     dict(n=2, bg=BG['b'], emph=['worst', 'everyone'], split_at=['almost'], segs=[hero('WS_F_SURPRISE_DRAMA#031', cut='punch'), inset('WS_F_UPSET_DRAMA#034', cut='punch')],
          assets=[dict(kind='label', trig='three', pos=(.5, .13), size=.55, dur=2.6, text='CRIME 3', col=RED, edge=GOLD, tsize=150, shake=16), dict(kind='x', trig='everyone', pos=(.82, .30), size=.24, dur=1.4, shake=10)]),
     dict(n=1, bg=BG['e'], emph=['rice side'], split_at=[], segs=[hero('WS_F_SURP#001', cut='punch')],
          assets=[dict(kind='soy', trig='dip', pos=(.81, .66), size=.40, dur=1.6), dict(kind='nigiri', trig='dip', pos=(.83, .50), size=.30, dur=1.6, rot=180, t_off=.15)]),
     dict(n=1, bg=BG['c'], emph=['fish side down', 'always'], split_at=['always'], segs=[hero('WS_F_HAPPY_PLAY#046', flip=True, cut='slide', dirn=-1), hero('WS_F_SMUG_PLAY#045', cut='punch')],
          assets=[dict(kind='nigiri', trig='fish', pos=(.83, .60), size=.32, dur=1.9), dict(kind='ok', trig='always', pos=(.86, .38), size=.18, dur=1.1)]),
     dict(n=1, bg=BG['d'], emph=['sponge'], split_at=[], segs=[hero('WS_F_THINK_CALM#036', cut='punch')],
          assets=[dict(kind='sponge', trig='sponge', pos=(.80, .60), size=.36, dur=1.5)]),
     dict(n=2, bg=BG['a'], emph=['sushi', 'yeah'], split_at=['saw'], segs=[hero('WS_F_SMUG_PLAY#045', flip=True, cut='punch'), hero('WS_F_NEUTRAL_CALM#023', cut='none')],
          assets=[dict(kind='nigiri', trig='sushi', pos=(.83, .60), size=.32, dur=1.5)]),
    ])
CFG['meal'] = dict(
    mp3='voiceover_meal.mp3', txt='input_used_meal.txt', music='bg_energetic.m4a', out='Raymi_Short_Meal.mp4',
    hook=[("NO REAL MEAL", WHITE), ("IN YEARS", WHITE), ("CHAT PROVED IT", GOLD)],
    cta=("snack or real meal, you decide", "defend your worst combo below owo"),  # v6: mandatory, see engagement.py
    trans=[None, 'zoompunch', 'glitch', 'zoompunch', 'zoompunch', 'glitch', 'zoompunch', 'zoompunch'],
    beats=[
     dict(n=2, bg=BG['a'], emph=['real meal', 'chat'], split_at=['chat'], segs=[hero('WS_F_NEUTRAL_CALM#023', cut='none'), hero('WS_F_SMUG_PLAY#045', flip=True, cut='punch', xoff=30)],
          assets=[dict(kind='bowl', trig='meal', pos=(.84, .68), size=.30, dur=1.8), dict(kind='x', trig='years', pos=(.80, .40), size=.25, dur=1.3, shake=12)]),
     dict(n=2, bg=BG['b'], emph=['no rice', 'no meal', 'snack'], split_at=['no rice', "so it's"], segs=[hero('WS_F_NEUTRAL_CALM#037', cut='none', xoff=-20), hero('WS_F_THINK_CALM#036', cut='punch'), inset('WS_F_SMUG_PLAY#045', flip=True, cut='punch')],
          assets=[dict(kind='scroll', trig='rice', pos=(.5, .215), size=.84, dur=2.0, text=[('NO RICE', 165, -.055, (70, 40, 48)), ('NO MEAL', 95, .09, (176, 60, 82))]),
                  dict(kind='stamp', trig='snack', pos=(.72, .62), size=.50, dur=1.6, text='SNACK', rot=-8, shake=14)]),
     dict(n=4, bg=BG['d'], emph=['snack', 'birthday dinner'], split_at=['pizza', 'pasta', 'my entire'],
          segs=[hero('WS_F_THINK_CALM#036', cut='none'), hero('WS_F_SURPRISE_DRAMA#035', cut='slide', dirn=1), hero('WS_F_SURPRISE_DRAMA#029', flip=True, cut='punch'), hero('WS_F_UPSET_DRAMA#034', cut='punch')],
          # FIX (2026-09-26 QA-Pass): die 3 SNACK-Stempel sassen vorher bei x=.28/.50/.72 mit
          # Groesse .44/.44/.56 UND komplett gleichzeitig (kein t_off) - bei ~1080px Breite
          # ueberlappten sie sich sichtbar in der Mitte, statt als 3 klar getrennte Stempel zu
          # wirken ("Schrift/Assets ueberlappen manchmal"). Fix: weiter auseinandergezogen
          # (x=.20/.50/.80), kleiner (.34/.34/.40 statt .44/.44/.56) und leicht zeitversetzt
          # (t_off), damit sie nacheinander statt gleichzeitig aufploppen.
          assets=[dict(kind='pizza', trig='pizza', pos=(.80, .52), size=.30, dur=1.0),
                  dict(kind='stamp', trig='snack', n=0, pos=(.20, .62), size=.34, dur=1.2, text='SNACK', rot=-8, shake=10, t_off=0.0),
                  dict(kind='stamp', trig='snack', n=1, pos=(.80, .62), size=.34, dur=1.2, text='SNACK', rot=7, shake=10, t_off=0.10),
                  dict(kind='stamp', trig='snack', n=2, pos=(.5, .70), size=.40, dur=1.6, text='SNACK', rot=-4, shake=14, t_off=0.20)]),
     dict(n=1, bg=BG['e'], emph=['good part'], split_at=['good'], segs=[hero('WS_F_NEUTRAL_CALM#027', cut='punch'), hero('WS_F_HAPPY_ENERG#047', cut='punch')],
          assets=[dict(kind='burst', trig='good', pos=(.80, .40), size=.34, dur=1.4)]),
     dict(n=3, bg=BG['c'], emph=['no rules', 'no limits', 'no portions'], split_at=['no limits', 'no portions'],
          segs=[hero('WS_F_HAPPY_PLAY#044', cut='punch'), inset('WS_F_HAPPY_PLAY#046', flip=True, cut='punch'), inset('WS_F_SMUG_PLAY#045', cut='punch')],
          assets=[dict(kind='label', trig='rules', pos=(.5, .095), size=.62, dur=4.0, text='NO RULES', col=(28, 24, 58), edge=GOLD, tsize=150),
                  dict(kind='label', trig='limits', pos=(.5, .165), size=.62, dur=2.6, text='NO LIMITS', col=(28, 24, 58), edge=GOLD, tsize=150),
                  dict(kind='label', trig='portions', pos=(.5, .235), size=.66, dur=1.6, text='NO PORTIONS', col=(28, 24, 58), edge=GOLD, tsize=150, shake=12)]),
     dict(n=1, bg=BG['b'], emph=['not overeating'], split_at=[], segs=[hero('WS_F_UPSET_DRAMA#048', cut='punch')],
          assets=[dict(kind='label', trig='overeating', pos=(.5, .13), size=.62, dur=1.6, text='OVEREATING', col=RED, tsize=150), dict(kind='x', trig='not', pos=(.82, .34), size=.24, dur=1.3, shake=10)]),
     dict(n=2, bg=BG['d'], emph=['snacking', 'professionally'], split_at=['professionally'], segs=[hero('WS_F_SMUG_PLAY#045', flip=True, cut='punch'), hero('WS_F_HAPPY_PLAY#046', cut='punch')],
          assets=[dict(kind='scroll', trig='professionally', pos=(.5, .215), size=.84, dur=1.9, text=[('CERTIFIED', 150, -.055, (70, 40, 48)), ('SNACKER', 105, .09, (176, 60, 82))]),
                  dict(kind='gavel', trig='professionally', pos=(.84, .60), size=.34, dur=1.4, shake=16, t_off=-.05)]),
     dict(n=1, bg=BG['a'], emph=['officially'], split_at=['officially'], segs=[hero('WS_F_SMUG_PLAY#045', flip=True, cut='punch'), hero('WS_F_NEUTRAL_CALM#023', cut='none')],
          assets=[dict(kind='bowl', trig='why', pos=(.84, .68), size=.30, dur=2.0), dict(kind='ok', trig='officially', pos=(.80, .40), size=.22, dur=1.0)]),
    ])
C = CFG[SHORT]; BEATS = C['beats']; TRANS = C['trans']

# =========================================================================== audio alignment (pauses -> sentences, tighten pauses)
def load_audio(p): return audio_mix.load_audio(p)

# v5: align() used to redecode + re-run ffmpeg silencedetect on the FULL voiceover every single
# time the script starts - and it starts once per render command (align/audio/stills/video x N
# batches/finish, see ENGINE_NOTES.md "Befehle"). That's the exact "Schritte die nur einmal
# gemacht werden muessen" case from the v5 request: cache the (voice track, sentence times)
# pair to disk, keyed by the mp3+txt file contents, so only the FIRST run per short pays for it.
#
# v7: this used to hard-crash (`assert len(ends) == len(sents)`) whenever ffmpeg's silence
# detection didn't find EXACTLY one pause per sentence - which happens often (a comma-pause
# gets picked up, two short sentences run together without a real gap, an ellipsis creates an
# extra one, ...). No local _words.json from generate_audio.py is needed or used anywhere in
# this pipeline (grep the repo - nothing reads it), so that was never the actual dependency;
# the crash was. On crash there was no fallback, so the mp3 had to be re-analysed by hand
# outside the script every time. Now: try a small grid of silencedetect thresholds first (best
# quality - real pause-cut, gap-tightened audio); if NONE of them land on the right sentence
# count, fall back to a proportional split of the untouched, continuous audio track, weighted by
# each sentence's syllable count (same weighting word_times() already uses one level down, for
# words inside a sentence) - always succeeds, never blocks a render. The chosen mode is recorded
# in align.json (`estimated: true/false`) so it's visible afterwards which one was used, without
# needing to listen to the audio to find out.
def _silence_segments(mp3, noise_db, dur_s):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', mp3, '-af', f'silencedetect=noise={noise_db}dB:d={dur_s}', '-f', 'null', '-'], capture_output=True, text=True)
    ss = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', r.stderr)]; se = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    return [0.0] + se[:len(ss) - 1], ss

def _pause_based_align(mp3, sents):
    """Grid of thresholds, first one whose silence count matches len(sents) wins. Returns
    (starts, ends, noise_db, dur_s) or None if no combo matches."""
    for noise_db, dur_s in ((-35, .28), (-30, .28), (-40, .28), (-35, .20), (-35, .40), (-30, .20), (-40, .40), (-30, .40), (-40, .20)):
        starts, ends = _silence_segments(mp3, noise_db, dur_s)
        if len(ends) == len(sents):
            return starts, ends, noise_db, dur_s
    return None

def _proportional_align(mp3, sents):
    """Fallback when no pause-threshold combo lines up with the sentence count - must never
    fail. Splits the raw, untouched voice track by each sentence's syllable-weight (no
    gap-tightening, since we don't know real pause locations here)."""
    vo = load_audio(mp3); total = vo.shape[1] / SR
    weights = [sum(syl(w) + 0.3 for w in re.findall(r"[A-Za-z']+", s)) or 1 for s in sents]
    totw = sum(weights) or 1; times, t = [], 0.0
    for s, w in zip(sents, weights):
        d = total * w / totw; times.append(dict(text=s, s=round(t, 3), e=round(t + d, 3))); t += d
    return vo, times

def _compute_align(mp3, txtp):
    text = open(txtp, encoding='utf-8').read().strip()
    sents = [s for s in re.split(r'(?<=[.!?])\s+', text.replace('\r', '')) if s.strip()]
    hit = _pause_based_align(mp3, sents)
    if hit:
        starts, ends, noise_db, dur_s = hit
        vo = load_audio(mp3); total = vo.shape[1] / SR; lead, tail, gap = .03, .06, .17; pieces, times, tn = [], [], 0.0
        for i, (a, b) in enumerate(zip(starts, ends)):
            a0, b0 = max(0., a - lead), min(total, b + tail); p = vo[:, int(a0 * SR):int(b0 * SR)].copy(); f = int(.008 * SR); p[:, :f] *= np.linspace(0, 1, f); p[:, -f:] *= np.linspace(1, 0, f)
            pieces.append(p); s = tn + (a - a0); times.append(dict(text=sents[i], s=round(s, 3), e=round(s + (b - a), 3))); tn += (b0 - a0)
            g = gap if i < len(ends) - 1 else .04; pieces.append(np.zeros((2, int(g * SR)), np.float32)); tn += g
        print(f"[align] pause-matched at {noise_db}dB/{dur_s}s: {len(sents)}/{len(sents)} sentences, gaps tightened to {gap}s.")
        return np.concatenate(pieces, 1), times, False
    print(f"[align] WARNING: no silencedetect threshold matched {len(sents)} sentences - "
          f"falling back to proportional (syllable-weighted) timing on the raw, untightened audio. "
          f"Render continues; cuts/captions are estimated rather than pause-exact for this short.")
    vo, times = _proportional_align(mp3, sents)
    return vo, times, True

def align():
    mp3, txtp = f"{UP}/{C['mp3']}", f"{UP}/{C['txt']}"
    key = cache_util.stable_key('align_' + SHORT, [mp3, txtp])
    vcache, jcache = os.path.join(cache_util.CACHE_DIR, f'align_{SHORT}_{key}.npy'), os.path.join(cache_util.CACHE_DIR, f'align_{SHORT}_{key}.json')
    if os.path.exists(vcache) and os.path.exists(jcache):
        v, payload = np.load(vcache), json.load(open(jcache, encoding='utf-8'))
        times, estimated = payload['sents'], payload.get('estimated', False)
    else:
        v, times, estimated = _compute_align(mp3, txtp)
        try: np.save(vcache, v); json.dump(dict(sents=times, estimated=estimated), open(jcache, 'w', encoding='utf-8'))
        except Exception: pass
    json.dump(dict(dur=v.shape[1] / SR, estimated=estimated, sents=times), open(OUT + '/align.json', 'w'), indent=1)
    if estimated:
        print('[align] NOTE: align.json used ESTIMATED (proportional) timing for this short - see warning above.')
    return v, times, v.shape[1] / SR

VOICE, SENTS, DUR = align()
# ---- beats: words from real sentence windows
k0 = 0
for b in BEATS:
    ss_ = SENTS[k0:k0 + b['n']]; k0 += b['n']; b['s'], b['e'] = ss_[0]['s'], ss_[-1]['e']; b['words'] = []
    for s in ss_: b['words'] += word_times(s['text'], s['s'], s['e'])
if k0 != len(SENTS):
    raise SystemExit(f"CFG['{SHORT}']['beats'] n-values sum to {k0} sentences, but align() found "
                      f"{len(SENTS)} sentences in {C['txt']}. Sentences detected:\n" +
                      '\n'.join(f'  [{i}] {s["text"]}' for i, s in enumerate(SENTS)) +
                      "\nFix the 'n' values in CFG so they sum to the real sentence count above.")
def find_all(words, phrase):
    ph = [re.sub(r"[^a-z']", '', p.lower()) for p in phrase.split()]; out = []
    for i in range(len(words) - len(ph) + 1):
        if all(words[i + k]['n'] == ph[k] for k in range(len(ph))): out.append(list(range(i, i + len(ph))))
    return out
B = [0.0] + [(BEATS[i - 1]['e'] + BEATS[i]['s']) / 2 for i in range(1, len(BEATS))] + [DUR]
for bi, b in enumerate(BEATS):
    ws = b['words']; b['emph_idx'] = sorted({i for p in b['emph'] for grp in find_all(ws, p) for i in grp})
    sp = [ws[find_all(ws, p)[0][0]]['s'] - .03 for p in b['split_at']]; assert len(sp) == len(b['segs']) - 1, (bi, b['split_at'])
    b['seg_t'] = [B[bi]] + sp + [B[bi + 1]]
    for a in b['assets']:
        g = find_all(ws, a['trig']); assert g, (bi, a['trig']); a['t0'] = ws[g[min(a.get('n', 0), len(g) - 1)][0]]['s'] + a.get('t_off', 0)

# =========================================================================== scene
_S, _BG, _AU, _AS, _PL = {}, {}, {}, {}, {}
# v5: same disk-cache treatment as proof_onigiri_v4.py - a Short's render also runs as several
# batched 'video a b' subprocesses, so sprite-fit/aura and background-cover are cached to disk
# once instead of being recomputed at the start of every batch (see ENGINE_NOTES_v5.md).
def _load_fit_aura(png_path, bbox, halo, flip, width):
    im = load_sprite(png_path, {'bbox': bbox, 'halo': halo}, flip); fitted = fit_sprite(im, width=width)
    aura, pad = make_aura(fitted); return {'sp': fitted, 'aura': aura, 'pad': np.array([pad], dtype=np.int64)}
_load_fit_aura = cache_util.disk_cache(watch_files=lambda a, kw: [a[0]])(_load_fit_aura)
def sprite(sg):
    wf = {'hero': 1.0, 'inset': .74, 'xcu': 1.26}[sg['mode']]; k = (sg['sprite'], sg.get('flip', False), wf)
    if k not in _S:
        cat = CAT[sg['sprite']]; d = _load_fit_aura(os.path.join(PNG, sg['sprite']), tuple(cat['bbox']), cat.get('halo', 0), sg.get('flip', False), wf * W)
        _S[k] = d['sp']; _AU[k] = (d['aura'], int(d['pad'][0]))
    return _S[k], _AU[k]
def _load_bg_cover(bg_path, target_h):
    return cover(cv2.cvtColor(cv2.imread(bg_path), cv2.COLOR_BGR2RGB), target_h)
_load_bg_cover = cache_util.disk_cache(watch_files=lambda a, kw: [a[0]])(_load_bg_cover)
def bgimg(n):
    if n not in _BG:
        p = [f for f in glob.glob(BGD + '/*.png') if os.path.basename(f) == n or os.path.basename(f).replace('#U00df', 'ß') == n][0]
        _BG[n] = _load_bg_cover(p, int(H * 1.25))
    return _BG[n]
def asset(kind, wpx):
    k = (kind, wpx)
    if k not in _AS:
        f = dict(onigiri=A.onigiri, x=lambda w: A.badge('x', w), ok=lambda w: A.badge('ok', w), gavel=A.gavel, scroll=A.scroll, nigiri=A.nigiri, soy=A.soy, wasabi=A.wasabi, sponge=A.sponge, bowl=A.bowl, pizza=A.pizza)
        _AS[k] = A.starburst(wpx) if kind == 'burst' else A.with_shadow(f[kind](wpx))
    return _AS[k]
def seg_index(bi, t):
    st = BEATS[bi]['seg_t']; k = max(i for i in range(len(BEATS[bi]['segs'])) if t >= st[i] - 1e-6); return k, t - st[k], st[k + 1] - st[k]

def scene(bi, t):
    b = BEATS[bi]; lt = max(0., t - B[bi]); k, u, sdur = seg_index(bi, t); sg = b['segs'][k]
    fr = bg_frame(bgimg(b['bg']), lt, dur=(b['e'] - b['s']) + .8, drift=(-.05 if bi % 2 == 0 else .05, .02)).astype(np.float32)
    fr = fr * np.array([.55, .50, .78], np.float32) * vignette(); fr = np.clip(fr + np.array([18, 10, 40], np.float32) * .6, 0, 255).astype(np.uint8)
    particles(fr, t, 11 + bi, n=22)
    sp, (au, pad) = sprite(sg); h, w = sp.shape[:2]
    # v5: bigger emphasis pop + idle rotation/breath (feedback: animations felt static between cuts)
    pop = sum(.085 * math.sin(math.pi * clamp((t - b['words'][i]['s']) / .24)) for i in b['emph_idx'])
    rot = 3.0 * math.sin(2 * math.pi * t / 3.4 + bi) + .9 * math.sin(2 * math.pi * t / 1.7); breath = energy_shimmer(t, amp=.020)
    cut = sg.get('cut', 'none'); cs, dx = 1.0, 0.
    if cut == 'punch': cs = lerp(1.20, 1.0, ease_out(u / .15))
    elif cut == 'slide': dx = sg.get('dirn', 1) * 240 * (1 - back_out(u / .26, 1.4))
    if bi == 0 and k == 0: cs = lerp(1.30, 1.0, ease_out(t / .26))
    slow = 1 + .035 * smooth(u / max(sdur, .5)); glow = .36 + .30 * math.sin(2 * math.pi * t / .8) ** 2 + 8 * pop
    if sg['mode'] in ('hero', 'inset'):
        top = (.225 if sg['mode'] == 'hero' else .40) * H; s = cs * slow * breath * (1 + pop)
        fx_, fy_ = W / 2 + sg.get('xoff', 0) + dx + 6 * math.sin(2 * math.pi * t / 2.7), top + h + 8 * math.sin(2 * math.pi * t / 2.0)
        blit(fr, au, w / 2 + pad, h + pad, fx_, fy_, s=s, rot=rot, alpha=min(1, glow), add=True); blit(fr, sp, w / 2, h, fx_, fy_, s=s, rot=rot)
    else:
        s = lerp(1.0, 1.13, smooth(lt / (b['e'] - b['s']))) * cs * (1 + pop) * breath
        blit(fr, sp, w / 2, h * .42, W / 2 + 10 * math.sin(2 * math.pi * t / 3.1), H * .50, s=s, rot=rot * .6)
    if cut == 'punch' and u < .06: fr = fx_flash(fr, .22 * (1 - u / .06))
    draw_assets(fr, bi, t)
    return fr, (sg['mode'] == 'inset')

def plate_for(pw, ph, col, edge):
    k = (pw, ph, col, edge)
    if k not in _PL: _PL[k] = A.with_shadow(A.plate(pw, ph, col, edge))
    return _PL[k]

# FIX (2026-09-26 QA-Pass): Feedback "Assets erscheinen immer einfach nur" - der generische
# Zweig unten (x/ok/nigiri/soy/wasabi/sponge/bowl/pizza, alles ohne eigene Choreo wie
# gavel/scroll/burst/label) nutzte fuer JEDES Asset exakt dieselbe Ein-/Ausblendung
# (back_out-Scale-Pop). Kein Beat-Autor muss dafuer jeden Asset-Eintrag von Hand um ein
# 'anim'-Feld erweitern: die Variante wird deterministisch aus (kind, trig) gehasht, damit
# ein Video bei jedem Render gleich aussieht, aber verschiedene Assets sichtbar
# unterschiedlich hereinkommen (Pop / Fallen+Abprallen / Reinschieben / Reindrehen).
_ANIM_KINDS = ('pop', 'drop', 'slide', 'spin')
def _stable_hash(s):
    """Deterministischer String-Hash statt Pythons eingebautem hash(): der Render laeuft als
    mehrere 'video a b'-Subprozess-Batches (siehe cache_util.py/ENGINE_NOTES.md) und Pythons
    hash() fuer Strings ist PRO PROZESS zufaellig salted (PYTHONHASHSEED) - mit hash() waere
    dasselbe Asset in Batch 1 vs. Batch 2 als unterschiedliche Animation gerendert worden
    (sichtbarer Bruch an der Batch-Grenze). md5 ist prozess-/session-unabhaengig stabil.
    """
    return int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)
def _anim_variant(kind, trig):
    return _ANIM_KINDS[_stable_hash(f'{kind}|{trig}') % len(_ANIM_KINDS)]

def _anim_offsets(kind, trig, u, dur, wpx):
    """Liefert (scale_in, extra_dx, extra_dy, extra_rot, exit_k) fuer den generischen
    Asset-Zweig. exit_k ist ein zusaetzlicher 0..1-Fade/Scale-Faktor fuer den Ausstieg,
    damit jede Variante auch anders VERSCHWINDET statt immer gleich wegzuschrumpfen."""
    v = _anim_variant(kind, trig)
    intro = clamp(u / .22); outro = 1 - smooth((u - (dur - .16)) / .16)
    if v == 'drop':
        # faellt von oben rein, ein Bounce am Ziel, faellt am Ende leicht weiter durch
        yy = -wpx * .9 * (1 - back_out(intro)) if u < .22 else 0
        dy_out = wpx * .5 * smooth(clamp((u - (dur - .16)) / .16))
        return back_out(intro), 0, yy + dy_out, 0, outro
    if v == 'slide':
        side = 1 if (_stable_hash(f'{kind}|{trig}|side') % 2) else -1
        xx = side * wpx * .8 * (1 - ease_out(intro)) if u < .22 else 0
        dx_out = -side * wpx * .6 * smooth(clamp((u - (dur - .16)) / .16))
        return ease_out(intro), xx + dx_out, 0, 0, outro
    if v == 'spin':
        rot = lerp(-160, 0, back_out(intro)) if u < .22 else 0
        rot_out = 90 * smooth(clamp((u - (dur - .16)) / .16))
        return back_out(intro), 0, 0, rot + rot_out, outro
    return back_out(intro), 0, 0, 0, outro   # 'pop' - bisheriges Standardverhalten

def draw_assets(fr, bi, t):
    for a in BEATS[bi]['assets']:
        u = t - a['t0']; dur = a['dur']
        if u < 0 or u > dur: continue
        k, wpx = a['kind'], int(a['size'] * W); pop = back_out(u / .22) * (1 - smooth((u - (dur - .15)) / .15)); fx, fy = a['pos'][0] * W, a['pos'][1] * H
        if k == 'gavel':
            sp = asset('gavel', wpx); h_, w_ = sp.shape[:2]; ang = lerp(-58, 4, smooth((u + .05) / .17)) if u < .30 else 4 - 3 * math.exp(-(u - .30) * 9) * math.sin((u - .30) * 40)
            blit(fr, sp, w_ / 2, h_ - 50, fx, fy, s=pop, rot=ang); continue
        if k == 'scroll':
            sp = asset('scroll', wpx); h_, w_ = sp.shape[:2]; blit(fr, sp, w_ / 2, h_ / 2, fx, fy, s=pop, rot=-2 + 1.2 * math.sin(u * 5))
            for txt, size, dy, col in a['text']:
                tl = TX.tile(txt, size, col, (250, 240, 214)); fit = min(1., .62 * wpx / tl.shape[1]); blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, fx, fy + dy * wpx, s=pop * fit)
            continue
        if k == 'burst':
            sp = asset('burst', wpx); h_, w_ = sp.shape[:2]; blit(fr, sp, w_ / 2, h_ / 2, fx, fy, s=pop * (1 + .05 * math.sin(u * 12)), rot=u * 40, alpha=.95); continue
        if k in ('label', 'stamp'):
            stmp = k == 'stamp'; tcol = (226, 52, 72) if stmp else a.get('tcol', WHITE); pl_col = (255, 246, 240) if stmp else a.get('col', (28, 24, 58)); edge = (226, 52, 72) if stmp else a.get('edge', WHITE)
            tl = TX.tile(a['text'], a.get('tsize', 150 if not stmp else 170), tcol, pl_col if stmp else DARK); pw, ph = tl.shape[1] + 90, tl.shape[0] + 50
            pl = plate_for(pw, ph, pl_col, edge); fit = min(1., wpx / pw); rot = a.get('rot', 0) + 2.5 * math.sin(u * 5); sc = pop * fit * (lerp(1.5, 1.0, ease_out(u / .10)) if stmp else 1)
            blit(fr, pl, pl.shape[1] / 2, pl.shape[0] / 2, fx, fy, s=sc, rot=rot); blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, fx, fy, s=sc, rot=rot); continue
        sp = asset(k, wpx); h_, w_ = sp.shape[:2]; wob = 4 * math.sin(2 * math.pi * u / .9) + a.get('rot', 0); sh = 10 * math.sin(u * 70) * (1 - clamp(u / .4)) if k == 'x' else 0
        sc_in, dx_, dy_, rot_, exit_k = _anim_offsets(k, a['trig'], u, dur, wpx)
        pop2 = sc_in * exit_k
        if k in ('x', 'ok'): blit(fr, asset('burst', int(wpx * 1.8)), wpx * .9, wpx * .9, fx + dx_, fy + dy_, s=pop2, alpha=(.14 if k == 'x' else .45), add=True)
        blit(fr, sp, w_ / 2, h_ / 2, fx + sh + dx_, fy + dy_, s=pop2, rot=wob + rot_)

def shake_amp(t):
    ev = [(0.0, 12)] + [(a['t0'] + (.17 if a['kind'] == 'gavel' else 0), a['shake']) for b in BEATS for a in b['assets'] if a.get('shake')]
    return sum(amp * math.exp(-(t - t0) / .11) for t0, amp in ev if t >= t0)

HOOK_END = min(SENTS[1]['e'] + .25, 3.6)
def overlay(fr, t, cap_y):
    bi = max(k for k in range(len(BEATS)) if B[k] <= t); b = BEATS[bi]
    if t < HOOK_END:
        al = 1 - clamp((t - (HOOK_END - .25)) / .22)
        for r, (txt, col) in enumerate(C['hook']):
            d = r * .07; k = lerp(1.8, 1.0, ease_out((t - d) / .16)); size = 128 if r < 2 else 190; tl = TX.tile(txt, size, col); fit = min(1., .92 * W / tl.shape[1]); yy = (.075 + r * .062) * H if r < 2 else .275 * H
            shk = 7 * math.sin(t * 70 + r) * (1 - clamp(t / .4)); blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, W / 2 + shk, yy, s=k * fit * (1 + .04 * math.sin(2 * math.pi * t / .9) * (r == 2)), alpha=clamp((t - d) * 12) * al)
    ws = b['words']; n = len(ws); chunks = [list(range(i, min(i + 2, n))) for i in range(0, n, 2)]
    for ci, c in enumerate(chunks):
        s0 = ws[c[0]]['s'] - .04; e0 = ws[c[-1]]['e'] + .15
        if ci + 1 < len(chunks): e0 = min(e0, ws[chunks[ci + 1][0]]['s'] - .05)
        if not (s0 <= t < e0): continue
        act = max([i for i in c if ws[i]['s'] <= t] or [c[0]]); tiles = []
        for i in c:
            emph = i in b['emph_idx']; on = (i == act); size = 290 if emph else 240; col = (GOLD if emph else CYAN) if on else WHITE
            sc = 1 + (.09 * (1 - ease_out((t - ws[i]['s']) / .16)) if on else 0) + (.06 if emph else 0); tiles.append((TX.tile(ws[i]['w'], size, col), sc, i))
        gap = 46; tot = sum(tl.shape[1] * sc for tl, sc, _ in tiles) + gap * (len(tiles) - 1); fit = min(1., .92 * W / tot); x = W / 2 - tot * fit / 2
        for tl, sc, i in tiles:
            wd = tl.shape[1] * sc * fit; jit = (5 * math.sin(t * 60 + i) * (1 - clamp((t - ws[i]['s']) / .2))) if (i in b['emph_idx'] and i == act) else 0
            blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, x + wd / 2 + jit, cap_y * H, s=sc * fit); x += wd + gap * fit

def _core_frame(t):
    t = min(t, DUR - 1e-3); bi = max(k for k in range(len(BEATS)) if B[k] <= t)
    fr, inset_ = scene(bi, t); overlay(fr, t, .865 if inset_ else .79)
    for j in range(1, len(BEATS)):
        kind, d = TRANS[j], t - B[j]
        # v5: punchier zoom/flash + chroma-split + radial impact lines on every cut (feedback:
        # transitions "nicht deutlich genug erkennbar" - see ENGINE_NOTES_v5.md)
        if kind == 'zoompunch':
            if -.10 <= d < 0: fr = fx_zoom(fr, 1 + .42 * smooth((d + .10) / .10))
            elif 0 <= d < .16: fr = fx_zoom(fr, lerp(1.34, 1.0, ease_out(d / .16)))
            fr = fx_flash(fr, .40 * clamp(1 - abs(d) / .06))
            fr = fx_chroma(fr, .8 * clamp(1 - abs(d) / .10))
            if 0 <= d < .14: fr = fx_impact_lines(fr, 1 - d / .14, seed=j)
        elif kind == 'glitch' and -.10 <= d < .16:
            fr = fx_glitch(fr, math.sin(math.pi * (d + .10) / .26), int(t * 30))
            fr = fx_chroma(fr, .6 * math.sin(math.pi * clamp((d + .10) / .26)))
    fr = fx_shake(fr, shake_amp(t), t); fr = fx_flash(fr, .8 * clamp(1 - t / .10))
    fr = progress_bar(fr, t / DUR)   # v5: retention progress cue
    # v6: mandatory comment-bait beat, read from CFG[SHORT]['cta'] — see engagement.py and
    # Raymi-Wissen/06_Analytics-Insights.md (near-zero comments/shares across all 13 prior videos).
    # Timed to end 0.9s before DUR so it's clear of the loop_seam crossfade window.
    cta = C.get('cta')
    if cta:
        q, sub = cta
        fr = E.cta_prompt(fr, TX, q, t - (DUR - 0.9 - 1.5), dur=1.5, sub=sub)
    # FIX (2026-09-26 QA-Pass): subscribe_badge() wurde in assets_v6 extra fuer diesen Zweck
    # gebaut (04_Asset-Creation-and-QC-Guidelines.md Punkt 1 - "Subscribe-Button/Badge im
    # Raymi-Look"), aber KEIN Render-Skript hat ihn je gezeichnet. Klein, oben rechts, nur in
    # den letzten 1.1s (weit weg von Hook/Caption/CTA-Bubble, siehe ENGINE_NOTES_v10.md fuer
    # die Positions-Ueberlegung), damit ein Branding-Element im Bild ist statt komplett zu fehlen.
    fr = _subscribe_badge_overlay(fr, t)
    fr = E.loop_reply_hint(fr, TX, t - (DUR - 0.85), dur=0.85)
    return fr

_SUB = {}
def _subscribe_badge_overlay(fr, t):
    u = t - (DUR - 1.10); dur = 1.10
    if u < 0 or u > dur: return fr
    if 'b' not in _SUB: _SUB['b'] = A.with_shadow(A.subscribe_badge(TX, int(W * .30)))
    sp = _SUB['b']; h_, w_ = sp.shape[:2]
    k = back_out(clamp(u / .22)) if u < .22 else (1 - smooth((u - (dur - .22)) / .22))
    blit(fr, sp, w_ / 2, h_ / 2, W * .80, H * .105, s=k)
    return fr

_FIRST = {}
def frame(t):
    fr = _core_frame(t)
    if t > DUR - 0.30:   # v5: crossfade tail into the hook frame for a seamless Shorts re-loop
        if 'f' not in _FIRST: _FIRST['f'] = _core_frame(0.0)
        fr = loop_seam(fr, _FIRST['f'], t, DUR, blend=0.30)
    return fr

# =========================================================================== audio mix
# v5: mixing (music level, ducking, sfx level, limiter) now lives in audio_mix.py so this file
# and proof_onigiri_v4.py share ONE tuned implementation (feedback: music slightly too loud,
# animation SFX much too loud - see ENGINE_NOTES_v5.md for the exact dB changes). This function
# still only builds the *cues* (what sound, when) - unchanged logic, just no manual mix math.
def build_audio(path):
    rng = np.random.default_rng(5)
    def tone(f0, f1, d, amp, dec): x = np.arange(int(d * SR)) / SR; f = f0 + (f1 - f0) * x / d; return np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-x / dec) * amp
    cues = [(0.0, tone(120, 45, .3, .22, .09))]
    for b in BEATS:
        for a in b['assets']:
            t0, kd = a['t0'], a['kind']
            if kd == 'x': cues.append((t0, tone(330, 190, .16, .10, .07)))
            elif kd == 'ok': cues.append((t0, tone(1320, 1320, .22, .07, .09) + tone(880, 880, .22, .05, .09)))
            elif kd == 'gavel': cues.append((t0 + .17, tone(190, 90, .18, .26, .05) + rng.standard_normal(int(.18 * SR)) * np.exp(-np.arange(int(.18 * SR)) / SR / .008) * .10))
            elif kd == 'stamp': cues.append((t0 + .02, tone(170, 60, .16, .24, .05) + rng.standard_normal(int(.16 * SR)) * np.exp(-np.arange(int(.16 * SR)) / SR / .006) * .08))
            elif kd == 'burst': cues.append((t0, tone(900, 1800, .18, .05, .07)))
            else: cues.append((t0, tone(420, 880, .09, .07, .05)))
    for j in range(1, len(BEATS)):
        if TRANS[j] == 'zoompunch':
            w = rng.standard_normal(int(.3 * SR)); w = np.convolve(w, np.ones(14) / 14, 'same') * np.hanning(len(w)) * .12; cues.append((B[j] - .12, w))
        elif TRANS[j] == 'glitch':
            g = rng.standard_normal(int(.2 * SR)) * np.hanning(int(.2 * SR)) * .08; cues.append((B[j] - .10, g))
    audio_mix.build_mix(VOICE, DUR, f"{MUS}/{C['music']}", cues, path, cfg=audio_mix.MixConfig())

NF = int(round(DUR * FPS))
if __name__ == '__main__':
    cmd = sys.argv[2]
    if cmd == 'align': print(json.dumps(dict(dur=DUR, frames=NF, beats=[(round(x['s'], 2), round(x['e'], 2)) for x in BEATS], B=[round(x, 2) for x in B]))); print(HOOK_END)
    elif cmd == 'audio':
        build_audio(OUT + '/mix_raw.wav'); subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', OUT + '/mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=7', '-ar', '44100', OUT + '/mix.wav'], check=True); print('audio ok')
    elif cmd == 'video':
        a, b_ = int(sys.argv[3]), min(int(sys.argv[4]), NF); out = f'{OUT}/part_{a:04d}.mp4'
        pr = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for f in range(a, b_): pr.stdin.write(frame(f / FPS).tobytes())
        pr.stdin.close(); pr.wait(); print('part', a, b_)
    elif cmd == 'stills':
        for t in sys.argv[3:]: Image.fromarray(frame(float(t))).save(f'{OUT}/still_{float(t):05.2f}.png')
    elif cmd == 'finish':
        parts = sorted(glob.glob(OUT + '/part_*.mp4')); open(OUT + '/list.txt', 'w').write(''.join(f"file '{p}'\n" for p in parts))
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', OUT + '/list.txt', '-i', OUT + '/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', os.path.join(paths.output_dir(), C['out'])], check=True); print('final ok')
