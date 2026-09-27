"""v4 proof: half-sentence expression cuts, drawn support assets, aura, screen shake, soft purposeful SFX."""
import sys, os, json, math, subprocess, glob, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import assets_v6 as A   # FIX (2026-09-26 QA-Pass): war assets_v3 (flacher Fill) - siehe raymi_short.py
import engagement as E  # v6: mandatory comment-bait beat, see engagement.py + Raymi-Wissen/06_Analytics-Insights.md
import paths, cache_util, audio_mix   # v5: portable paths + disk cache + shared tuned audio mix (see ENGINE_NOTES_v5.md)
UP = paths.upload_dir()
PNG = paths.asset_dir('PNG', extra_globs=['/home/claude/w/PNG-*/PNG'])
BGD = paths.asset_dir('Background', extra_globs=['/home/claude/w/Background-2*/Background'])
MUS = paths.asset_dir('Background-Music', extra_globs=['/home/claude/w/Background-Music-*/Background-Music'])
HAND = os.environ.get('RAYMI_HAND', '/home/claude/hand/2026-09-23_onigiri-corner-first')
OUT = os.path.join(paths.HERE, 'render_proof4'); os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__)); CAT = {c['file']: c for c in json.load(open(HERE + '/sprite_catalog.json'))}
TX = Text(find_font()); DUR = 10.6
CYAN, GOLD = (120, 225, 255), (255, 214, 84)
P = lambda n: f'RAY_{n}_UV_{{}}.png'
BEATS = [
 dict(line="there's one correct way to eat onigiri and most of you are doing it wrong.", s=0.0, e=3.786, bg='bg rochen klein 2.png', emph=['correct way', 'wrong'], splits=[0, 7, 11], segs=[
   dict(mode='hero', sprite='RAY_WS_F_NEUTRAL_CALM_UV_023.png', cut='none'),
   dict(mode='hero', sprite='RAY_WS_F_SMUG_PLAY_UV_045.png', flip=True, cut='punch', xoff=30),
   dict(mode='hero', sprite='RAY_WS_F_UPSET_DRAMA_UV_032.png', cut='slide', dirn=1)],
   assets=[dict(kind='onigiri', trig='onigiri', pos=(.80, .585), size=.36, dur=1.4), dict(kind='x', trig='wrong', pos=(.80, .40), size=.25, dur=1.3, shake=12)]),
 dict(line="this isn't a quirk, it's basic food law and i will defend it forever.", s=3.936, e=7.751, bg='pc quallen klein.png', emph=['food law', 'forever'], splits=[0, 4, 8], segs=[
   dict(mode='hero', sprite='RAY_WS_F_NEUTRAL_CALM_UV_037.png', cut='none', xoff=-20),
   dict(mode='inset', sprite='RAY_WS_F_NEUTRAL_CALM_UV_021.png', cut='punch'),
   dict(mode='hero', sprite='RAY_WS_F_HAPPY_PLAY_UV_046.png', flip=True, cut='slide', dirn=-1)],
   assets=[dict(kind='scroll', trig='basic', pos=(.5, .215), size=.84, dur=1.75), dict(kind='gavel', trig='law', pos=(.80, .34), size=.36, dur=1.0, shake=16, t_off=-.05)]),
 dict(line="corner first, always corner first.", s=7.901, e=10.109, bg='bg hai.png', emph=['corner first', 'always'], splits=[0, 2], segs=[
   dict(mode='xcu', sprite='RAY_CU_F_ONIGIRI_UV_087.png', cut='none'),
   dict(mode='inset', sprite='RAY_CU_F_CALM_UV_001.png', cut='punch')],
   assets=[dict(kind='card', trig='always', pos=(.5, .235), size=.50, dur=1.5), dict(kind='ok', trig='always', pos=(.82, .095), size=.17, dur=1.2, t_off=.30)]),
]
B = [0.0] + [(BEATS[i - 1]['e'] + BEATS[i]['s']) / 2 for i in range(1, len(BEATS))] + [DUR]
TRANS = [None, 'zoompunch', 'glitch']
for bi, b in enumerate(BEATS):
    b['words'] = word_times(b['line'], b['s'], b['e']); b['emph_idx'] = sorted({i for p in b['emph'] for i in find_words(b['words'], p)})
    b['seg_t'] = [B[bi]] + [b['words'][i]['s'] - .03 for i in b['splits'][1:]] + [B[bi + 1]]
    for a in b['assets']:
        ti = find_words(b['words'], a['trig']); a['t0'] = b['words'][ti[0]]['s'] + a.get('t_off', 0)

_S, _BG, _AU, _AS = {}, {}, {}, {}
# v5: sprite fit+aura and background cover are now ALSO cached to disk (not just the
# in-memory dicts above), because a full render runs as several separate `video a b`
# subprocesses (see ENGINE_NOTES.md Befehle) - each one used to redo this work from
# scratch. Same pixels out, just computed once instead of once per batch.
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
        _AS[k] = {'onigiri': lambda: A.with_shadow(A.onigiri(wpx)), 'x': lambda: A.with_shadow(A.badge('x', wpx)), 'ok': lambda: A.with_shadow(A.badge('ok', wpx)),
                  'gavel': lambda: A.with_shadow(A.gavel(wpx)), 'scroll': lambda: A.with_shadow(A.scroll(wpx)), 'card': lambda: A.with_shadow(A.onigiri(wpx)), 'burst': lambda: A.starburst(wpx)}[kind]()
    return _AS[k]

def seg_index(bi, t):
    st = BEATS[bi]['seg_t']; k = max(i for i in range(len(BEATS[bi]['segs'])) if t >= st[i] - 1e-6); return k, t - st[k], st[k + 1] - st[k]

def scene(bi, t):
    b = BEATS[bi]; lt = max(0., t - B[bi]); k, u, sdur = seg_index(bi, t); sg = b['segs'][k]
    fr = bg_frame(bgimg(b['bg']), lt, dur=(b['e'] - b['s']) + .8, drift=(-.05 if bi % 2 == 0 else .05, .02)).astype(np.float32)
    fr = fr * np.array([.55, .50, .78], np.float32) * vignette(); fr = np.clip(fr + np.array([18, 10, 40], np.float32) * .6, 0, 255).astype(np.uint8)
    particles(fr, t, 11 + bi, n=22)
    sp, (au, pad) = sprite(sg); h, w = sp.shape[:2]
    # v5: bigger emphasis pop, bigger idle rotation/breath, continuous shimmer - old values
    # left Raymi looking almost frozen between cuts/emphasis words ("wirkt statisch" feedback).
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
    draw_assets(fr, bi, t, b['seg_t'][-1])
    return fr, (sg['mode'] == 'inset')

def draw_assets(fr, bi, t, bend):
    b = BEATS[bi]
    for a in b['assets']:
        u = t - a['t0']; dur = a['dur']
        if u < 0 or u > dur: continue
        k, wpx = a['kind'], int(a['size'] * W); pop = back_out(u / .22) * (1 - smooth((u - (dur - .15)) / .15)); fx, fy = a['pos'][0] * W, a['pos'][1] * H
        if k == 'gavel':
            sp = asset('gavel', wpx); h_, w_ = sp.shape[:2]; ang = lerp(-58, 4, smooth((u + .05) / .17)) if u < .30 else 4 - 3 * math.exp(-(u - .30) * 9) * math.sin((u - .30) * 40)
            blit(fr, sp, w_ / 2, h_ - 50, fx, fy, s=pop, rot=ang); continue
        if k == 'scroll':
            sp = asset('scroll', wpx); h_, w_ = sp.shape[:2]; blit(fr, sp, w_ / 2, h_ / 2, fx, fy, s=pop, rot=-2 + 1.2 * math.sin(u * 5))
            for txt, size, dy, col in (('FOOD LAW', 190, -.02, (70, 40, 48)), ('NO. 1', 100, .075, (176, 60, 82))):
                tl = TX.tile(txt, size, col, (250, 240, 214)); fit = min(1., .62 * wpx / tl.shape[1]); blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, fx, fy + dy * wpx, s=pop * fit); continue
            continue
        if k == 'card':
            sp = asset('card', wpx); h_, w_ = sp.shape[:2]; rot = 3 * math.sin(2 * math.pi * u / 1.1)
            blit(fr, sp, w_ / 2, h_ / 2, fx, fy, s=pop, rot=rot)
            cx, cy = fx, fy - h_ * .5 * pop + h_ * .245 * pop; r = (.10 * wpx) * (1 + .25 * math.sin(u * 14)) * pop; ov = fr.copy()
            cv2.circle(ov, (int(cx), int(cy)), int(r * 1.1), GOLD, 12, cv2.LINE_AA); fr[:] = cv2.addWeighted(ov, .9, fr, .1, 0)
            tl = TX.tile('FIRST BITE', 120, GOLD); fit = min(1., .40 * W / tl.shape[1]); blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, fx + .27 * W, fy + .03 * H, s=pop * fit, rot=-6)
            continue
        sp = asset(k, wpx); h_, w_ = sp.shape[:2]; wob = 4 * math.sin(2 * math.pi * u / .9); sh = 10 * math.sin(u * 70) * (1 - clamp(u / .4)) if k == 'x' else 0
        if k in ('x', 'ok'): blit(fr, asset('burst', int(wpx * 1.8)), wpx * .9, wpx * .9, fx, fy, s=pop, alpha=(.14 if k == 'x' else .45), add=True)
        blit(fr, sp, w_ / 2, h_ / 2, fx + sh, fy, s=pop, rot=wob)

def shake_amp(t):
    ev = [(0.0, 12)] + [(a['t0'] + (.17 if a['kind'] == 'gavel' else 0), a['shake']) for b in BEATS for a in b['assets'] if a.get('shake')]
    return sum(amp * math.exp(-(t - t0) / .11) for t0, amp in ev if t >= t0)

def overlay(fr, t, cap_y):
    bi = max(k for k in range(len(BEATS)) if B[k] <= t); b = BEATS[bi]
    if t < 3.2:
        al = 1 - clamp((t - 2.95) / .22)
        for r, (txt, col) in enumerate([("YOU'RE EATING", WHITE), ("ONIGIRI", WHITE), ("WRONG", GOLD)]):
            d = r * .07; k = lerp(1.8, 1.0, ease_out((t - d) / .16)); size = 128 if r < 2 else 190; tl = TX.tile(txt, size, col); fit = min(1., .92 * W / tl.shape[1]); yy = (.075 + r * .062) * H if r < 2 else .275 * H
            shk = 7 * math.sin(t * 70 + r) * (1 - clamp(t / .4)); blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, W / 2 + shk, yy, s=k * fit * (1 + .04 * math.sin(2 * math.pi * t / .9) * (r == 2)), alpha=clamp((t - d) * 12) * al)
    ws = b['words']; n = len(ws); chunks = [list(range(i, min(i + 2, n))) for i in range(0, n, 2)]
    for ci, c in enumerate(chunks):
        s0 = ws[c[0]]['s'] - .04; e0 = ws[c[-1]]['e'] + .15
        if ci + 1 < len(chunks): e0 = min(e0, ws[chunks[ci + 1][0]]['s'] - .05)      # never overlap the next chunk
        if not (s0 <= t < e0) or (bi == 0 and t < 1.3): continue
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
    fr, inset = scene(bi, t); overlay(fr, t, .865 if inset else .79)
    for j in range(1, len(BEATS)):
        kind, d = TRANS[j], t - B[j]
        # v5: punchier zoom/flash + chroma-split + radial impact lines on every cut so the cut
        # reads instantly even muted/thumbnail-scale (retention research: pattern interrupts
        # need to be UNMISTAKABLE, see ENGINE_NOTES_v5.md).
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
    fr = progress_bar(fr, t / DUR)   # v5: thin retention/progress cue (see ENGINE_NOTES_v5.md)
    # v6: mandatory comment-bait beat (analytics: 8 comments / 2 shares across 13 videos and
    # 3722 views total — near-zero without exception; see Raymi-Wissen/06_Analytics-Insights.md).
    # Placed after the payoff line, well clear of the loop_seam blend window (last 0.30s).
    fr = E.cta_prompt(fr, TX, "corner first or wrong. no in between.", t - 8.5, dur=1.5,
                       sub="fight me in the comments owo")
    return fr

_FIRST = {}
def frame(t):
    fr = _core_frame(t)
    if t > DUR - 0.30:   # v5: crossfade the tail into the hook frame -> clean loop on replay
        if 'f' not in _FIRST: _FIRST['f'] = _core_frame(0.0)
        fr = loop_seam(fr, _FIRST['f'], t, DUR, blend=0.30)
    return fr

# ---------------------------------------------------------------- audio: few, soft, purposeful cues
# v5: mixing itself (music level, ducking, sfx level, limiter) now lives in audio_mix.py so both
# this file and raymi_short.py share ONE tuned implementation instead of two copies drifting apart
# (feedback: music slightly too loud, animation SFX much too loud - see ENGINE_NOTES_v5.md for the
# exact dB changes). This function still only builds the *cues* (what sound, when) - unchanged.
SR = audio_mix.SR
def load_audio(p): return audio_mix.load_audio(p)
def build_audio(path):
    rng = np.random.default_rng(5)
    voice = load_audio(HAND + '/2026-09-23_onigiri-corner-first_audio-trimmed.mp3')
    def tone(f0, f1, d, amp, dec): x = np.arange(int(d * SR)) / SR; f = f0 + (f1 - f0) * x / d; return np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-x / dec) * amp
    cues = [(0.0, tone(120, 45, .3, .22, .09))]                                    # hook: soft low thump
    for b in BEATS:
        for a in b['assets']:
            t0 = a['t0']
            if a['kind'] == 'x': cues.append((t0, tone(330, 190, .16, .10, .07)))                                   # error bonk
            elif a['kind'] == 'ok': cues.append((t0, tone(1320, 1320, .22, .07, .09) + tone(880, 880, .22, .05, .09)))  # soft ding
            elif a['kind'] == 'gavel': cues.append((t0 + .17, tone(190, 90, .18, .26, .05) + rng.standard_normal(int(.18 * SR)) * np.exp(-np.arange(int(.18 * SR)) / SR / .008) * .10))  # knock
            elif a['kind'] in ('onigiri', 'scroll', 'card'): cues.append((t0, tone(420, 880, .09, .07, .05)))         # bloop
    w = rng.standard_normal(int(.3 * SR)); w = np.convolve(w, np.ones(14) / 14, 'same') * np.hanning(len(w)) * .12; cues.append((B[1] - .12, w))   # whoosh (zoom cut)
    g = rng.standard_normal(int(.2 * SR)) * np.hanning(int(.2 * SR)) * .08; cues.append((B[2] - .10, g))                                        # glitch
    audio_mix.build_mix(voice, DUR, os.path.join(MUS, 'bg_energetic.m4a'), cues, path, cfg=audio_mix.MixConfig())

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'audio':
        build_audio(OUT + '/mix_raw.wav'); subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', OUT + '/mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=7', '-ar', '44100', OUT + '/mix.wav'], check=True); print('audio ok')
    elif cmd == 'video':
        a, b_ = int(sys.argv[2]), int(sys.argv[3]); out = f'{OUT}/part_{a:04d}.mp4'
        pr = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for f in range(a, b_): pr.stdin.write(frame(f / FPS).tobytes())
        pr.stdin.close(); pr.wait(); print('part', a, b_)
    elif cmd == 'stills':
        for t in sys.argv[2:]: Image.fromarray(frame(float(t))).save(f'{OUT}/still_{float(t):05.2f}.png')
    elif cmd == 'finish':
        parts = sorted(glob.glob(OUT + '/part_*.mp4')); open(OUT + '/list.txt', 'w').write(''.join(f"file '{p}'\n" for p in parts))
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', OUT + '/list.txt', '-i', OUT + '/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '/mnt/user-data/outputs/Raymi_Proof_Onigiri_v4.mp4'], check=True); print('final ok')
