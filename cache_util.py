"""Raymi Engine v5 - cache_util.py (NEU in v5, additive Modul)

WARUM: engine.py/raymi_short.py cachen teure Berechnungen bisher nur IM RAM
(_S, _BG, _AU Dicts). Das nuetzt nichts, weil ein Render in Batches laeuft
(mehrere 'video a b'-Aufrufe = mehrere Python-Prozesse, siehe ENGINE_NOTES.md
Befehle) - jeder Batch faengt bei leeren Dicts wieder an: Sprite freistellen,
resize, Aura blurren, Hintergrund auf Zielaufloesung skalieren, Audio-Alignment
(ffmpeg silencedetect + volle Dekodierung) - alles nochmal von vorne.

disk_cache() speichert das Ergebnis EINMAL auf Platte (unter .cache/ neben dem
Skript) und laedt es danach nur noch. Kostet nichts an Bildqualitaet/Verhalten,
nur Zeit. Cache-Key = Funktionsname + Argumente + mtime der Inputdatei(en), d.h.
er invalidiert sich automatisch, wenn sich ein PNG/eine mp3 aendert.

Benutzung:
    from cache_util import disk_cache
    @disk_cache()
    def sprite(sg): ...
Ergebnis muss JSON-serialisierbar ODER ein dict aus numpy-Arrays sein (siehe
disk_cache-Docstring); alles andere wird per pickle gecacht.
"""
import os, json, pickle, hashlib, functools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.environ.get('RAYMI_CACHE', os.path.join(HERE, '.cache'))
os.makedirs(CACHE_DIR, exist_ok=True)


def _key(name, args, kwargs, file_stamps):
    h = hashlib.sha1()
    h.update(name.encode())
    h.update(repr(args).encode())
    h.update(repr(sorted(kwargs.items())).encode())
    h.update(repr(file_stamps).encode())
    return h.hexdigest()[:20]


def _stamp(path):
    try:
        st = os.stat(path)
        return (path, st.st_mtime_ns, st.st_size)
    except OSError:
        return (path, None, None)


def disk_cache(watch_files=None):
    """Decorator factory. watch_files(args, kwargs) -> list of paths whose
    mtime/size become part of the cache key (so editing a PNG/mp3 auto-busts
    the cache). If omitted, only the call args/kwargs are hashed."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            stamps = [_stamp(p) for p in watch_files(args, kwargs)] if watch_files else []
            key = _key(fn.__qualname__, args, kwargs, stamps)
            npz_path = os.path.join(CACHE_DIR, key + '.npz')
            pkl_path = os.path.join(CACHE_DIR, key + '.pkl')
            if os.path.exists(npz_path):
                d = np.load(npz_path)
                if set(d.files) == {'__single__'}:
                    return d['__single__']
                return {k: d[k] for k in d.files}
            if os.path.exists(pkl_path):
                with open(pkl_path, 'rb') as f:
                    return pickle.load(f)
            result = fn(*args, **kwargs)
            try:
                if isinstance(result, np.ndarray):
                    np.savez(npz_path, __single__=result)
                elif isinstance(result, dict) and all(isinstance(v, np.ndarray) for v in result.values()):
                    np.savez(npz_path, **result)
                elif isinstance(result, tuple) and all(isinstance(v, np.ndarray) for v in result):
                    np.savez(npz_path, **{f'__t{i}__': v for i, v in enumerate(result)})
                else:
                    with open(pkl_path, 'wb') as f:
                        pickle.dump(result, f)
            except Exception:
                pass  # caching is best-effort, never blocks a render
            return result
        return wrapped
    return deco


def json_cache(key, compute_fn, watch_files=()):
    """Simple helper for one-off JSON-able results (e.g. audio align()).
    key: short stable string. compute_fn(): -> JSON-serialisable value."""
    stamps = [_stamp(p) for p in watch_files]
    h = _key(key, (), {}, stamps)
    path = os.path.join(CACHE_DIR, f'{key}_{h}.json')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    val = compute_fn()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(val, f)
    except Exception:
        pass
    return val


def stable_key(name, watch_files=()):
    """Public helper for call sites that need to build several related cache files
    (e.g. audio align() writes both a .npy voice track and a .json sentence list
    from ONE computation) and must reuse the same key for both."""
    return _key(name, (), {}, [_stamp(p) for p in watch_files])


def npy_cache(key, compute_fn, watch_files=()):
    """Same as json_cache but for a single numpy array (e.g. decoded voice track)."""
    stamps = [_stamp(p) for p in watch_files]
    h = _key(key, (), {}, stamps)
    path = os.path.join(CACHE_DIR, f'{key}_{h}.npy')
    if os.path.exists(path):
        return np.load(path)
    val = compute_fn()
    try:
        np.save(path, val)
    except Exception:
        pass
    return val
