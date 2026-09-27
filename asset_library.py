"""Raymi Engine v9 - asset_library.py (NEU, additives Modul, nichts Bestehendes angefasst)

WARUM: assets_v3/v4/v5 haben JEDES Mal neu gezeichnet, JEDES Mal im selben Prozess
(_AS-Dict in proof_onigiri_v4.py/raymi_short.py cached nur INNERHALB eines Renders,
siehe cache_util.py-Kommentar dazu) - zwischen SESSIONS ging jedes Asset verloren.
Feedback: "Assets muessen wiederverwendbar sein und gespeichert werden, nach jeder
Videoerstellung eine Datei ausgeben, die ich einspeisen kann, damit diese Assets in
Zukunft genutzt werden koennen."

Dieses Modul ist GENAU das:
 1. Eine EINZIGE, session-uebergreifende Bibliothek unter `assets_library/`
    (`library.json` Manifest + `png/<name>.png` Dateien), gefunden ueber dasselbe
    Suchmuster wie paths.py (RAYMI_ASSET_LIBRARY-Env, sonst Ordner neben den
    Skripten - falls du einen frueheren Pack-Export wieder hochlaedst, wird er
    automatisch gefunden, kein manueller Pfad noetig).
 2. `AssetLibrary.cached(name, builder, params=None, ...)` - der zentrale Aufruf,
    den assets_v6.py fuer JEDES Icon benutzt: gibt es `name` mit demselben
    Parameter-Hash schon in der Bibliothek, wird die gespeicherte PNG geladen
    (kein Neuzeichnen, garantiert IDENTISCHES Aussehen ueber alle Videos hinweg -
    das ist "Wiederverwendbarkeit"). Sonst wird `builder()` genau EINMAL aufgerufen,
    das Ergebnis auf Platte geschrieben und im Manifest eingetragen.
 3. `export_pack(path)` - schreibt EINE zip-Datei (Manifest + alle PNGs). Das ist
    "die Datei, die ich einspeisen kann": naechste Session einfach in
    /mnt/user-data/uploads hochladen und `AssetLibrary().import_uploaded_packs()`
    (macht assets_v6.py beim Import automatisch) zieht sie wieder in
    `assets_library/` ein - Icons aus frueheren Videos stehen sofort wieder bereit,
    ohne dass irgendetwas neu gezeichnet wird.

BENUTZUNG (siehe auch ENGINE_NOTES_v9.md):
    python3 asset_library.py pack /mnt/user-data/outputs/raymi_assets_pack.zip
        -> nach einem Render manuell ein Pack exportieren (Download-Datei)
    python3 asset_library.py import /pfad/zu/altem_pack.zip
        -> ein zuvor heruntergeladenes Pack wieder einspeisen
    python3 asset_library.py list
        -> zeigt alle aktuell gespeicherten Assets (Name/Art/Groesse/erzeugt am)
"""
import os, sys, json, glob, hashlib, shutil, zipfile, datetime
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def _root():
    env = os.environ.get('RAYMI_ASSET_LIBRARY')
    if env:
        os.makedirs(env, exist_ok=True)
        return env
    r = os.path.join(HERE, 'assets_library')
    os.makedirs(r, exist_ok=True)
    return r


def _params_hash(params):
    if params is None:
        return ''
    return hashlib.sha1(repr(sorted(params.items()) if isinstance(params, dict) else params).encode()).hexdigest()[:16]


class AssetLibrary:
    def __init__(self, root=None):
        self.root = root or _root()
        self.png_dir = os.path.join(self.root, 'png')
        os.makedirs(self.png_dir, exist_ok=True)
        self.manifest_path = os.path.join(self.root, 'library.json')
        self.manifest = self._load_manifest()
        self._mem = {}   # in-process cache, avoids re-decoding the same PNG twice in one render

    # ---------------------------------------------------------------- manifest io
    def _load_manifest(self):
        if os.path.exists(self.manifest_path):
            try:
                return json.load(open(self.manifest_path, encoding='utf-8'))
            except Exception:
                pass
        return {'version': 1, 'assets': {}}

    def _save_manifest(self):
        tmp = self.manifest_path + '.tmp'
        json.dump(self.manifest, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        os.replace(tmp, self.manifest_path)

    # ---------------------------------------------------------------- core reuse call
    def get(self, name, params=None):
        """Returns a premultiplied RGBA numpy array if `name` (with matching params-hash)
        is already saved, else None. Loads from disk only once per process (in-memory cache)."""
        entry = self.manifest['assets'].get(name)
        if not entry:
            return None
        if params is not None and entry.get('params_hash') != _params_hash(params):
            return None   # caller asked for the same name but different look -> treat as miss
        if name in self._mem:
            return self._mem[name]
        p = os.path.join(self.png_dir, entry['file'])
        if not os.path.exists(p):
            return None
        from engine import premult
        arr = premult(np.array(Image.open(p).convert('RGBA')))
        self._mem[name] = arr
        return arr

    def put(self, name, arr, kind='icon', params=None, tags=None, notes=''):
        fname = f'{name}.png'
        Image.fromarray(arr).save(os.path.join(self.png_dir, fname))
        self.manifest['assets'][name] = dict(
            file=fname, kind=kind, params_hash=_params_hash(params), tags=tags or [],
            notes=notes, w=int(arr.shape[1]), h=int(arr.shape[0]),
            created=self.manifest['assets'].get(name, {}).get('created', _now()),
            updated=_now(),
        )
        self._mem[name] = arr
        self._save_manifest()
        return arr

    def cached(self, name, builder, params=None, kind='icon', tags=None, notes=''):
        """THE call every asset function in assets_v6.py goes through:
            lib.cached('medal_gold', lambda: medal(420, GOLD), params=dict(w=420, col=GOLD))
        Same name+params -> loaded from assets_library/ (identical pixels, no redraw, works
        across sessions once a pack has been re-imported). New name or changed params ->
        builder() runs once, result is saved for every future video."""
        hit = self.get(name, params)
        if hit is not None:
            return hit
        arr = builder()
        return self.put(name, arr, kind=kind, params=params, tags=tags, notes=notes)

    # ---------------------------------------------------------------- pack export/import
    def export_pack(self, out_path):
        """Writes ONE zip (manifest + every cached PNG) to out_path - this is 'die Datei,
        die ich einspeisen kann' for a future session. Call once after finishing a video."""
        os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
        with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(self.manifest_path, 'library.json')
            for fname in sorted(os.listdir(self.png_dir)):
                z.write(os.path.join(self.png_dir, fname), f'png/{fname}')
        return out_path

    def import_pack(self, path):
        """Merges a previously exported pack (zip OR an already-unzipped folder containing
        library.json + png/) into this library. Newer 'updated' timestamp wins per asset,
        so importing an old pack never clobbers assets already improved in this session."""
        if os.path.isdir(path):
            man = json.load(open(os.path.join(path, 'library.json'), encoding='utf-8'))
            src_png = os.path.join(path, 'png')
            for name, entry in man['assets'].items():
                self._merge_entry(name, entry, os.path.join(src_png, entry['file']))
            return
        with zipfile.ZipFile(path) as z, _tempdir() as td:
            z.extractall(td)
            man = json.load(open(os.path.join(td, 'library.json'), encoding='utf-8'))
            for name, entry in man['assets'].items():
                self._merge_entry(name, entry, os.path.join(td, 'png', entry['file']))

    def _merge_entry(self, name, entry, src_file):
        cur = self.manifest['assets'].get(name)
        if cur and cur.get('updated', '') >= entry.get('updated', ''):
            return   # local copy is same age or newer, keep it
        if os.path.exists(src_file):
            shutil.copyfile(src_file, os.path.join(self.png_dir, entry['file']))
            self.manifest['assets'][name] = entry
            self._mem.pop(name, None)
        self._save_manifest()

    def import_uploaded_packs(self, upload_dir=None):
        """Auto-picks up ANY raymi_assets_pack*.zip sitting in the uploads folder (same
        search paths.upload_dir() already uses) and merges it in - so re-uploading last
        session's exported file is enough, no path-typing required."""
        try:
            import paths
            upload_dir = upload_dir or paths.upload_dir()
        except Exception:
            upload_dir = upload_dir or '/mnt/user-data/uploads'
        hits = sorted(glob.glob(os.path.join(upload_dir, '*raymi_assets_pack*.zip')))
        for h in hits:
            try:
                self.import_pack(h)
            except Exception as e:
                print(f'[asset_library] konnte {h} nicht importieren: {e}')
        return hits

    def list_assets(self):
        return self.manifest['assets']


def _now():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


class _tempdir:
    def __enter__(self):
        import tempfile
        self._d = tempfile.mkdtemp()
        return self._d
    def __exit__(self, *a):
        shutil.rmtree(self._d, ignore_errors=True)


# ---------------------------------------------------------------- shared singleton
# assets_v6.py importiert genau diese eine Instanz, damit ALLE Szenen-Skripte in
# einem Render dieselbe Bibliothek/denselben In-Memory-Cache teilen (gleiches Muster
# wie die geteilten _S/_BG-Dicts in raymi_short.py, nur session-uebergreifend).
LIB = AssetLibrary()


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'pack':
        out = sys.argv[2] if len(sys.argv) > 2 else 'raymi_assets_pack.zip'
        LIB.export_pack(out)
        n = len(LIB.list_assets())
        print(f'{n} Assets exportiert -> {out}')
    elif cmd == 'import':
        LIB.import_pack(sys.argv[2])
        print(f'importiert aus {sys.argv[2]}, jetzt {len(LIB.list_assets())} Assets in der Bibliothek.')
    elif cmd == 'list':
        for name, e in sorted(LIB.list_assets().items()):
            print(f"{name:<22} {e['kind']:<10} {e['w']}x{e['h']:<6} tags={','.join(e.get('tags') or [])}  {e.get('updated','')}")
        print(f'{len(LIB.list_assets())} Assets total in {LIB.root}')
    else:
        print(__doc__)
