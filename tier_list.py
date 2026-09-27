"""Raymi Engine v10 - tier_list.py (NEU, additives Modul, aendert nichts an engine.py/
assets_v6.py/raymi_short.py - siehe REGEL in ENGINE_NOTES.md: nur erweitern).

WARUM DIESES MODUL (Nutzer-Feedback, QA-Pass 2026-09-26): im mitgeschickten aelteren
Referenzvideo wurde u.a. eine animierte Tier-List gezeigt (S/A/B/C-Reihen, Items poppen
nacheinander rein) - genau die Art von "gutem altem Content", die der Nutzer in der
aktuellen v9-Engine vermisst. Weder raymi_short.py noch proof_onigiri_v4.py noch
assets_v3/v4/v5/v6 hatten ueberhaupt eine Tier-List-Funktion - das war keine Regression
(kein Code wurde schlechter), sondern eine Faehigkeit, die nie in die neue Engine
uebernommen wurde. Dieses Modul schliesst genau diese Luecke, direkt auf assets_v6/engine.py
aufbauend (keine Parallel-Engine, siehe Asset-Creation-and-QC-Guidelines.md Punkt 8).

Nutzung in einer Szene (z.B. als eigener Beat in raymi_short.py/proof_onigiri_v4.py):

    import tier_list as TL
    ...
    TL.draw_tier_list(fr, t, rows=[
        ('S', GOLD,  [('nigiri', 'Nigiri'), ('onigiri', 'Onigiri')]),
        ('A', CYAN,  [('soy', 'Soy Sauce')]),
        ('B', (150,150,160), [('wasabi', 'Wasabi')]),
        ('C', RED,   [('pizza', 'Pizza auf Sushi (nein)')]),
    ], t0=beat_start, tx=TX)

`rows` ist bewusst eine simple Liste statt eines eigenen Config-Dialekts, damit ein
Szenen-Skript sie direkt aus vorhandenen CFG-Daten bauen kann. Icon-Namen sind alles, was
`assets_v6.<name>(w)` unterstuetzt (nigiri/onigiri/soy/wasabi/sponge/bowl/pizza/...); wer
stattdessen ein Sprite-PNG zeigen will, uebergibt statt eines Strings ein
`('sprite', catalog_filename)`-Tupel (siehe `_icon_surface`).
"""
import math
from engine import W, H, clamp, smooth, ease_out, back_out, lerp, blit, premult
import assets_v6 as A

ROW_H_FRAC = 0.135        # Reihenhoehe als Anteil der Bildhoehe
LABEL_W_FRAC = 0.16       # Breite der S/A/B/C-Labelspalte
PANEL_X0, PANEL_X1 = 0.05, 0.95   # linker/rechter Rand der ganzen Tafel

_ICON_BASE_W = 340   # feste Erzeugungsbreite - die tatsaechliche Anzeigegroesse kommt ueber
                     # den `s=`-Skalierungsfaktor in blit() (s.u.), nicht ueber Neubau in
                     # anderer Aufloesung. Das haelt den asset_library-Cache klein UND macht
                     # das Icon in draw_tier_list() unabhaengig von Reihenanzahl/-hoehe fittbar.
_ICON_CACHE = {}
def _icon_surface(item):
    """item ist entweder ein assets_v6-Funktionsname (str) oder ('sprite', png_dateiname)
    fuer ein echtes Sprite-PNG aus dem sprite_catalog. Ergebnisse werden pro item gecacht,
    analog zu asset()/sprite() in raymi_short.py. WICHTIG: liefert die Surface in fester
    Basisbreite _ICON_BASE_W zurueck, egal wie gross sie spaeter angezeigt wird - siehe
    _fit_scale() fuer die eigentliche Zielgroessen-Berechnung."""
    k = item if isinstance(item, str) else item
    if k in _ICON_CACHE:
        return _ICON_CACHE[k]
    if isinstance(item, tuple) and item[0] == 'sprite':
        # bewusst kein eigener Sprite-Lade-Codepfad hier (siehe QC-Guideline Punkt 8) -
        # die aufrufende Szene uebergibt ein bereits geladenes premultipliziertes RGBA-Array.
        raise NotImplementedError("('sprite', ...) Items: uebergib stattdessen direkt die "
                                  "fertige Sprite-Surface ueber icon_overrides=, siehe draw_tier_list().")
    fn = getattr(A, item)
    surf = A.with_shadow(fn(_ICON_BASE_W))
    _ICON_CACHE[k] = surf
    return surf

def _fit_scale(surf, max_w, max_h):
    """FIX (2026-09-26 QA-Pass, erster Rauchtest tier_list_preview.png): ein einzelnes Item
    in einer 1-Item-Reihe (z.B. nur 'pizza' in Tier C) bekam vorher die volle Slot-Breite als
    Ziel-PIXELBREITE fuer den Icon-BAU zugewiesen - bei quadratischen Icons (pizza() liefert
    h=w) wurde das Icon dann viel hoeher als die Reihe selbst und lief in die Nachbarreihen
    hinein. Fix: Icons werden immer in fester Basisgroesse gebaut und erst hier - unter
    Beruecksichtigung von BEIDEN Grenzen (verfuegbare Breite UND Reihenhoehe) - passend
    herunterskaliert."""
    h, w = surf.shape[:2]
    return min(max_w / w, max_h / h, 1.0)

def draw_tier_list(fr, t, rows, t0, tx=None, title=None, icon_overrides=None,
                    stagger_row=0.16, stagger_item=0.10, item_dur=0.55):
    """Zeichnet eine animierte Tier-List ins Frame `fr` (H,W,3 uint8, wird in-place veraendert).

    rows            - Liste von (label:str, color:(r,g,b), items:list[str|('sprite',..)|any])
                      items werden ueber assets_v6.<name>(w) gebaut, siehe Docstring oben;
                      icon_overrides={item: rgba_surface} erlaubt beliebige fertige Surfaces.
    t               - aktuelle Szenenzeit (Sekunden)
    t0              - Startzeit dieses Tier-List-Beats (Sekunden) - alles davor ist unsichtbar
    tx              - engine.Text-Instanz fuer Titel/Item-Beschriftung (Pflicht fuer Text,
                       siehe Asset-Creation-and-QC-Guidelines.md Punkt 1 - nie Default-Font)
    title           - optionaler Titel ueber der Tafel (z.B. "SUSHI TIER LIST")
    stagger_row     - Zeitversatz zwischen den Reihen beim Reinschieben (s)
    stagger_item    - Zeitversatz zwischen Items INNERHALB einer Reihe (s)
    item_dur        - Dauer der Pop-in-Animation eines einzelnen Items (s)
    """
    u = t - t0
    if u < 0:
        return fr
    icon_overrides = icon_overrides or {}
    x0, x1 = PANEL_X0 * W, PANEL_X1 * W
    row_h = ROW_H_FRAC * H
    top = H * 0.12 if title else H * 0.08

    if title and tx is not None:
        tt = clamp((u - 0.0) / 0.25)
        tl = tx.tile(title, 96)
        blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, W / 2, top - row_h * 0.55,
             s=back_out(tt), alpha=clamp(tt * 3))

    for ri, (label, color, items) in enumerate(rows):
        ru = u - ri * stagger_row
        if ru < 0:
            continue
        row_y0 = top + ri * row_h
        slide = 1 - ease_out(clamp(ru / 0.30))   # 1 -> 0, Reihe schiebt von links rein
        row_x0 = x0 - (x1 - x0) * slide * 0.06 - W * 0.9 * (slide ** 1.6)
        # Label-Plate (S/A/B/C)
        lab_w = (x1 - x0) * LABEL_W_FRAC
        plate = A.with_shadow(A.plate(int(lab_w), int(row_h * 0.86), fill=color, edge=(255, 255, 255)))
        ph, pw = plate.shape[:2]
        blit(fr, plate, pw / 2, ph / 2, row_x0 + lab_w / 2, row_y0 + row_h / 2, s=1.0)
        if tx is not None:
            # FIX (2026-09-26 QA-Pass): Fuellfarbe war vorher fast identisch zur Standard-
            # Kontur-Farbe (engine.DARK) -> Buchstabe verschmolz mit seiner eigenen Kontur zu
            # einem Klecks statt lesbar zu sein. Fuellung jetzt WEISS mit dunkler Kontur
            # (Standard von Text.tile()), das ist auch der Look, den Captions/Titel ueberall
            # sonst in der Engine nutzen - konsistent statt einer Einzelloesung nur hier.
            lt = tx.tile(label, int(row_h * 0.5), (255, 255, 255))
            blit(fr, lt, lt.shape[1] / 2, lt.shape[0] / 2, row_x0 + lab_w / 2, row_y0 + row_h / 2, s=1.0)
        # Reihen-Hintergrundbalken (leicht transparent, in Reihenfarbe getoent)
        bar_w = (x1 - x0) - lab_w - W * 0.02
        bar = A.with_shadow(A.plate(int(bar_w), int(row_h * 0.80),
                                     fill=tuple(max(0, c // 5) for c in color), edge=color))
        bh, bw = bar.shape[:2]
        blit(fr, bar, bw / 2, bh / 2, row_x0 + lab_w + W * 0.02 + bar_w / 2, row_y0 + row_h / 2, s=1.0, alpha=.92)

        # Items ploppen nacheinander in die Reihe, jedes an einem festen Slot
        n = max(1, len(items))
        slot_w = bar_w / n
        for ii, item in enumerate(items):
            iu = ru - ii * stagger_item
            if iu < 0 or iu > item_dur + 2.0:   # bleibt danach einfach stehen (kein Exit noetig)
                continue
            pop = back_out(clamp(iu / item_dur)) if iu < item_dur else 1.0
            surf = icon_overrides.get(item) if item in icon_overrides else _icon_surface(item)
            ih, iw = surf.shape[:2]
            fit = _fit_scale(surf, slot_w * 0.80, row_h * 0.66)
            cx = row_x0 + lab_w + W * 0.02 + slot_w * (ii + 0.5)
            cy = row_y0 + row_h * 0.42
            wob = 3 * math.sin(2 * math.pi * (t) / 2.2 + ri + ii) if iu >= item_dur else 0
            blit(fr, surf, iw / 2, ih / 2, cx, cy, s=pop * fit, rot=wob)
            name = item[1] if isinstance(item, tuple) else item
            if tx is not None and isinstance(item, tuple):
                nt = tx.tile(name, int(row_h * 0.20), (255, 255, 255))
                fit = min(1., (slot_w * .92) / nt.shape[1])
                blit(fr, nt, nt.shape[1] / 2, nt.shape[0] / 2, cx, row_y0 + row_h * 0.80, s=pop * fit)
    return fr


if __name__ == '__main__':
    # Kleiner Rauch-Test (keine Audiodatei noetig): eine Standbild-Vorschau.
    import numpy as np
    from PIL import Image
    from engine import Text, find_font, vignette
    TX = Text(find_font())
    fr = (np.ones((H, W, 3), np.float32) * np.array([26, 22, 48], np.float32) * vignette()).astype('uint8')
    GOLD, CYAN, SILVER, RED = (255, 214, 84), (120, 225, 255), (190, 195, 205), (236, 62, 88)
    draw_tier_list(fr, t=2.4, t0=0.0, tx=TX, title='SUSHI TIER LIST', rows=[
        ('S', GOLD, ['nigiri', 'onigiri']),
        ('A', CYAN, ['soy']),
        ('B', SILVER, ['wasabi', 'sponge']),
        ('C', RED, ['pizza']),
    ])
    Image.fromarray(fr).save('/home/claude/w/v9/tier_list_preview.png')
    print('wrote /home/claude/w/v9/tier_list_preview.png')
