"""Raymi Engine v5 - audio_mix.py (NEU in v5, additive Modul)

WARUM: proof_onigiri_v4.py und raymi_short.py hatten JEDES eine eigene Kopie
von build_audio() (fast identisch, leicht auseinandergelaufen). Bug/Feedback der
Nutzerin: Hintergrundmusik oft etwas zu laut, SFX von Animationen deutlich zu
laut. Ursache im alten Code: Musikbett auf -25dB RMS normalisiert MIT NUR -7dB
Ducking unter der Stimme (bleibt also bei -18dB und ist damit relativ pruesent),
SFX-Toene mit festen amp-Werten bis .26 OHNE Limiter, nur ein finales /max()-
Clipping. Diese Datei ersetzt die Zahlen durch deutlich konservativere, an
Loudness-Standards orientierte Werte UND buendelt die Logik an einem Ort, damit
zukuenftige Shorts nicht wieder zwei auseinanderlaufende Mix-Implementierungen
bekommen.

Aenderungen ggue. v4:
- Musikbett-Zielpegel -25 -> -30 dB RMS (leiser als vorher)
- Ducking unter der Stimme -7 -> -13 dB (Musik verschwindet fast, wenn Raymi
  spricht, statt nur leicht runterzugehen)
- SFX-Gain-Faktor 0.62x auf alle Cue-Amplituden (die alten Werte waren fuer
  Kopfhoerer gemischt, auf Handylautsprecher stachen sie hervor)
- SFX werden jetzt GENAUSO wie die Musik unter der Stimme geduckt (vorher nur
  leicht mit *0.4, jetzt *0.6 sidechain wie die Musik) UND zusaetzlich einmal
  pauschal leiser
- weicher Kompressor/Limiter (tanh soft-clip) VOR dem finalen Normalize, damit
  Peaks (Gavel-Bonk, Punch-Cut-Whoosh) nicht die ganze Mischung nach unten
  ziehen bzw. hart clippen
- alles ueber Parameter einstellbar (MixConfig), damit man pro Short leicht
  nachjustieren kann ohne den Mix-Code nochmal zu kopieren
"""
import math, wave, subprocess, os, tempfile
import numpy as np

SR = 44100


class MixConfig:
    def __init__(self, music_db=-30, duck_db=-13, sfx_gain=0.62, sfx_duck_db=-9,
                 hook_thump=True, limiter_drive=1.15, loudnorm_i=-14, loudnorm_tp=-1.5, loudnorm_lra=7,
                 voice_cfg=None):
        self.music_db = music_db              # Zielpegel Musikbett (RMS) wenn KEINE Stimme spielt
        self.duck_db = duck_db                # zusaetzliches Absenken der Musik WAEHREND die Stimme spielt
        self.sfx_gain = sfx_gain              # globaler Multiplikator auf alle SFX-Cue-Amplituden
        self.sfx_duck_db = sfx_duck_db        # Absenken der SFX waehrend die Stimme spielt
        self.hook_thump = hook_thump
        self.limiter_drive = limiter_drive    # >1 = etwas mehr Punch vor dem soft-clip
        self.loudnorm_i, self.loudnorm_tp, self.loudnorm_lra = loudnorm_i, loudnorm_tp, loudnorm_lra
        self.voice_cfg = voice_cfg            # v5: VoiceConfig() fuer die Stimm-Aufbereitung (None = Standard-Werte)


def load_audio(path, sr=SR):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(sr), '-'],
                        capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).T.copy()


def voice_gate(voice, sr=SR, smooth_ms=50, hold_ms=120):
    """Envelope 0..1 of how much the voice is 'active' right now - used to duck music & sfx."""
    env = np.abs(voice.mean(0))
    k = max(1, int(smooth_ms / 1000 * sr))
    env = np.convolve(env, np.ones(k) / k, 'same')
    gate = np.clip(env / (0.06 * env.max() + 1e-9), 0, 1)
    hk = max(1, int(hold_ms / 1000 * sr))
    gate = np.convolve(gate, np.ones(hk) / hk, 'same')
    return np.clip(gate, 0, 1)


def _db(x):
    return 10 ** (x / 20)


def soft_limiter(mix, drive=1.15):
    """Gentle tanh soft-clip: tames transient peaks (gavel/whoosh) without
    squashing the whole mix the way a hard /max() normalize does."""
    return np.tanh(mix * drive) / math.tanh(drive)


def build_mix(voice, duration_s, music_path, sfx_cues, out_path, cfg=None, sr=SR):
    """voice: (2,N) float32 already-aligned dialogue track (silence where nobody talks).
    sfx_cues: list of (t_seconds, signal[2,K] or signal[K]) already-rendered short sfx snippets,
    positioned by caller (tone-generation stays in the calling script - only the MIXING moves here).
    Writes a 16-bit PCM wav to out_path (raw; caller still runs ffmpeg loudnorm after, same as v4)."""
    cfg = cfg or MixConfig()
    voice = polish_voice(voice, sr, cfg.voice_cfg or VoiceConfig())   # v5: Stimme aufwerten, siehe VoiceConfig oben
    n = int(duration_s * sr)
    v = np.zeros((2, n), np.float32)
    L = min(n, voice.shape[1]); v[:, :L] = voice[:, :L]
    gate = voice_gate(v, sr)

    music = load_audio(music_path, sr)
    music = music / (np.sqrt((music ** 2).mean()) + 1e-9) * _db(cfg.music_db)
    bed = np.tile(music, (1, n // music.shape[1] + 1))[:, :n]
    bed *= (1 - gate * (1 - _db(cfg.duck_db)))
    fade = np.ones(n); fo, fi = int(.12 * sr), int(.05 * sr)
    fade[-fo:] = np.linspace(1, 0, fo); fade[:fi] = np.linspace(0, 1, fi)
    bed *= fade

    sfx = np.zeros((2, n), np.float32)
    for t, sig in sfx_cues:
        sig = np.asarray(sig, np.float32)
        if sig.ndim == 1:
            sig = np.stack([sig, sig])
        i = int(t * sr); k_ = min(sig.shape[1], n - i)
        if k_ > 0 and i >= 0:
            sfx[:, i:i + k_] += sig[:, :k_] * cfg.sfx_gain
    sfx *= (1 - gate * (1 - _db(cfg.sfx_duck_db)))

    mix = v + bed + sfx
    mix = soft_limiter(mix, cfg.limiter_drive)
    peak = np.abs(mix).max()
    if peak > 0.98:
        mix = mix / peak * 0.98
    pcm = (np.clip(mix, -1, 1).T * 32767).astype('<i2')
    with wave.open(out_path, 'wb') as w_:
        w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(sr); w_.writeframes(pcm.tobytes())
    return out_path


def loudnorm(in_path, out_path, cfg=None):
    cfg = cfg or MixConfig()
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', in_path, '-af',
                     f'loudnorm=I={cfg.loudnorm_i}:TP={cfg.loudnorm_tp}:LRA={cfg.loudnorm_lra}',
                     '-ar', str(SR), out_path], check=True)
    return out_path


# ------------------------------------------------------------------ v5 additions: Stimme aufwerten
# WARUM (Nutzerin: "kenne mich mit Audiofiltern nicht aus"): das sind die 5 Standard-Schritte, mit
# denen man ein Diktiergeraet/Handy-Mikro-Voiceover deutlich professioneller klingen laesst, alle
# mit vorsichtigen, bereits abgestimmten Default-Werten - nichts davon muss von Hand eingestellt
# werden, `polish_voice()` macht das automatisch fuer jede Stimme, die durch build_mix() laeuft.
# Jeder Schritt kurz erklaert (steht auch in ENGINE_NOTES_v5.md):
#   1. highpass   - schneidet ganz tiefe Frequenzen (Brummen, Poltern, Tisch-Vibrationen) weg, die
#                    eine menschliche Stimme sowieso nicht braucht
#   2. afftdn     - Rauschentfernung: nimmt ein durchgehendes leises Rauschen/Zischen (Lüfter,
#                    Raumhall, Mikro-Eigenrauschen) heraus, ohne die Stimme selbst zu veraendern
#   3. equalizer  - ein sanfter "Klarheits"-Boost in dem Frequenzbereich, der eine Stimme aus einer
#                    Musikmischung heraushebt (Konsonanten/Verstaendlichkeit), bewusst zurueckhaltend
#                    gewaehlt, weil Raymis Stimme laut Charakter-Doku ohnehin schon hoch/nasal ist -
#                    zu viel Boost hier wuerde das nur verschlimmern statt "professioneller" klingen
#   4. deesser    - daempft scharfe S/Sch-Laute (Sibilanz), die bei vielen Mikros/TTS-Stimmen
#                    unangenehm hervorstechen
#   5. acompressor- gleicht laute und leise Woerter/Saetze aneinander an, damit nichts im Mix
#                    untergeht oder ploetzlich zu laut herausspringt
class VoiceConfig:
    def __init__(self, enabled=True, highpass_hz=90, denoise_nf=-25, presence_hz=3200, presence_db=2.5,
                 deess_intensity=0.35, comp_threshold_db=-18, comp_ratio=2.5, comp_makeup_db=2.0):
        self.enabled = enabled                # auf False setzen = alte v4-Rohstimme, keine Filter
        self.highpass_hz = highpass_hz
        self.denoise_nf = denoise_nf          # ffmpeg afftdn noise-floor in dB, negativer = vorsichtiger
        self.presence_hz, self.presence_db = presence_hz, presence_db
        self.deess_intensity = deess_intensity
        self.comp_threshold_db, self.comp_ratio, self.comp_makeup_db = comp_threshold_db, comp_ratio, comp_makeup_db

    def filter_chain(self):
        return (f"highpass=f={self.highpass_hz},"
                f"afftdn=nf={self.denoise_nf},"
                f"equalizer=f={self.presence_hz}:t=q:w=1:g={self.presence_db},"
                f"deesser=i={self.deess_intensity},"
                f"acompressor=threshold={self.comp_threshold_db}dB:ratio={self.comp_ratio}:attack=5:release=80:makeup={self.comp_makeup_db}")


def polish_voice(voice, sr=SR, cfg=None):
    """voice: (2,N) float32 raw/tightened dialogue track (z.B. das Ergebnis von align()).
    Schickt sie einmal durch die Filterkette oben und gibt eine gleich lange (2,N) float32 Spur
    zurueck. Bei cfg.enabled=False wird die Eingabe unveraendert zurueckgegeben (Vergleichs-/
    Debug-Option). Laeuft ueber eine temporaere WAV-Datei, weil ffmpegs Filter nur auf Dateien/
    Streams arbeiten, nicht direkt auf numpy-Arrays."""
    cfg = cfg or VoiceConfig()
    if not cfg.enabled:
        return voice
    with tempfile.TemporaryDirectory() as td:
        raw, out = os.path.join(td, 'raw.wav'), os.path.join(td, 'polished.wav')
        pcm = (np.clip(voice, -1, 1).T * 32767).astype('<i2')
        with wave.open(raw, 'wb') as w_:
            w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(sr); w_.writeframes(pcm.tobytes())
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-af', cfg.filter_chain(), '-ar', str(sr), out], check=True)
        polished = load_audio(out, sr)
    n = voice.shape[1]  # Filter koennen die Laenge um ein paar Samples verschieben - auf Original zurechtschneiden/-polstern
    if polished.shape[1] >= n:
        return polished[:, :n]
    pad = np.zeros((2, n - polished.shape[1]), np.float32)
    return np.concatenate([polished, pad], axis=1)
