"""Raymi Engine v5 - paths.py (NEW in v5, additive module, does not touch engine.py)

WARUM: v3/v4-Skripte hatten Asset-Ordner hart auf Claude-Sandbox-Pfade verdrahtet
(z.B. '/home/claude/w/assets/PNG', '/mnt/user-data/uploads'). Lokal beim Nutzer
existieren diese Pfade nicht -> Skript bricht sofort ab. asset_dir()/upload_dir()
suchen an mehreren plausiblen Orten und liefern den ersten Treffer, ohne dass
irgendein bestehendes Verhalten in der Sandbox wegfaellt (Sandbox-Pfade bleiben
als Fallback in der Liste).

Suchreihenfolge fuer asset_dir(name), z.B. name='PNG':
 1. Umgebungsvariable RAYMI_ASSETS (falls gesetzt) + '/' + name
 2. <dieser Ordner>/assets/<name>              <- Standard im ausgelieferten ZIP
 3. <dieser Ordner>/<name>                     <- falls jemand die Ordner flach auspackt
 4. zusaetzliche extra_globs (alte Sandbox-Glob-Muster), falls uebergeben

Suchreihenfolge fuer upload_dir():
 1. Umgebungsvariable RAYMI_UPLOADS
 2. /mnt/user-data/uploads                     <- Claude-Sandbox
 3. <dieser Ordner>/uploads                    <- lokal: einfach einen "uploads"-Ordner
                                                   neben die Skripte legen
"""
import os, glob

HERE = os.path.dirname(os.path.abspath(__file__))


def asset_dir(name, extra_globs=None):
    candidates = []
    env = os.environ.get('RAYMI_ASSETS')
    if env:
        candidates.append(os.path.join(env, name))
    candidates.append(os.path.join(HERE, 'assets', name))
    candidates.append(os.path.join(HERE, name))
    for c in candidates:
        if os.path.isdir(c):
            return c
    for pat in (extra_globs or []):
        hits = glob.glob(pat)
        if hits:
            return hits[0]
    raise FileNotFoundError(
        f"Asset-Ordner '{name}' nicht gefunden. Geprueft: {candidates}"
        + (f" + globs {extra_globs}" if extra_globs else "")
        + ". Setze RAYMI_ASSETS oder lege den Ordner unter ./assets/ ab."
    )


def upload_dir():
    env = os.environ.get('RAYMI_UPLOADS')
    if env and os.path.isdir(env):
        return env
    if os.path.isdir('/mnt/user-data/uploads'):
        return '/mnt/user-data/uploads'
    local = os.path.join(HERE, 'uploads')
    os.makedirs(local, exist_ok=True)
    return local


def output_dir():
    env = os.environ.get('RAYMI_OUTPUTS')
    if env:
        os.makedirs(env, exist_ok=True)
        return env
    if os.path.isdir('/mnt/user-data/outputs'):
        return '/mnt/user-data/outputs'
    local = os.path.join(HERE, 'outputs')
    os.makedirs(local, exist_ok=True)
    return local
