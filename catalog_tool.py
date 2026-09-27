"""
Raymi Sprite Catalog Tool -- extends sprite_catalog.json automatically.

WARUM: Jedes neue PNG muss NICHT mehr per Bild-Analyse (Claude schaut sich das PNG an)
katalogisiert werden. Dieses Skript berechnet dieselben Werte per Bildverarbeitung
(numpy/opencv), die bisher von Hand/visuell ermittelt wurden. Kostet keine Vision-Tokens.

Validiert an allen 106 bestehenden Katalog-Eintraegen (Stand 2026-09-24):
- bbox/touch: exakt oder auf 1-2px genau (Rundungsdifferenzen durch Alpha-Threshold)
- cls (bust/full/xcu_topcut): 106/106 korrekt reproduziert
- halo: trennt sauber "hat weisse Kontur" (~1.0) von "sauber" (~0.0)
- contour_px: eigene, in sich konsistente Komplexitaets-Metrik (Skala weicht von alten
  Handwerten ab -- nur zum Vergleich NEUER Sprites untereinander gedacht, keine Ruecken-
  kompatibilitaet noetig, wird nirgends fuer Platzierung/Rendering gebraucht)

BENUTZUNG (in einer neuen Session, wenn neue PNGs dazukommen):
    python3 catalog_tool.py /pfad/zum/PNG-Ordner
    -> liest sprite_catalog.json im selben Ordner wie dieses Skript,
       ueberspringt bereits katalogisierte Dateien,
       haengt nur die WIRKLICH NEUEN Dateien an,
       schreibt sprite_catalog.json zurueck,
       druckt eine kurze Tabelle der neuen Eintraege zum Gegenchecken.

    --catalog PFAD   anderer Katalog-Pfad
    --force DATEI    einzelne Datei neu berechnen (z.B. nach Bugfix am Skript)
    --dry-run        nur anzeigen, nichts schreiben

Klassifikationsregel (aus den 106 bestehenden Eintraegen abgeleitet, 0 Fehlklassifikationen):
    xcu_topcut  wenn topw > 0.5   (Kopf fuellt die obere Kante fast komplett -> Punch-in)
    bust        sonst wenn 'b' in touch   (unten abgeschnitten -> Brustbild)
    full        sonst                     (Ganzkoerper mit Rand ringsum)
"""
import sys, os, json, argparse
import numpy as np
import cv2
from PIL import Image


def analyze_one(path, alpha_thr=10, top_frac=0.02):
    im = np.array(Image.open(path).convert('RGBA'))
    h_img, w_img = im.shape[0], im.shape[1]
    a = im[..., 3]
    ys, xs = np.where(a > alpha_thr)
    if len(xs) == 0:
        raise ValueError(f"{path}: komplett transparent?")
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
    bw, bh = x1 - x0, y1 - y0

    touch = []
    if x0 <= 1: touch.append('l')
    if x1 >= w_img - 1: touch.append('r')
    if y0 <= 1: touch.append('t')
    if y1 >= h_img - 1: touch.append('b')

    nrows = max(1, int(bh * top_frac))
    top_rows = a[y0:y0 + nrows, x0:x1]
    topw = round(float((top_rows.max(axis=0) > alpha_thr).mean()), 2)

    if topw > 0.5:
        cls = 'xcu_topcut'
    elif 'b' in touch:
        cls = 'bust'
    else:
        cls = 'full'

    # halo: Anteil naheweisser Pixel direkt am inneren Rand der Alpha-Maske
    solid = (a > 128).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    outer = cv2.dilate(solid, k, iterations=1)
    inner = cv2.erode(solid, k, iterations=1)
    ring = (outer > 0) & (inner == 0) & (solid > 0)
    rgb = im[..., :3]
    ring_pix = rgb[ring]
    halo = round(float(np.all(ring_pix > 235, axis=1).mean()), 2) if len(ring_pix) else 0.0

    contours, _ = cv2.findContours(solid * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour_px = int(sum(cv2.arcLength(c, True) for c in contours))

    return {
        "file": os.path.basename(path),
        "size": [w_img, h_img],
        "bbox": [x0, y0, bw, bh],
        "touch": touch,
        "topw": topw,
        "cls": cls,
        "halo": halo,
        "contour_px": contour_px,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png_folder")
    ap.add_argument("--catalog", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprite_catalog.json"))
    ap.add_argument("--force", action="append", default=[], help="Dateiname(n) zwingend neu berechnen")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    catalog = json.load(open(args.catalog)) if os.path.exists(args.catalog) else []
    by_name = {c["file"]: c for c in catalog}

    all_pngs = sorted(f for f in os.listdir(args.png_folder) if f.lower().endswith(".png"))
    new_entries = []
    for fname in all_pngs:
        if fname in by_name and fname not in args.force:
            continue
        entry = analyze_one(os.path.join(args.png_folder, fname))
        by_name[fname] = entry
        new_entries.append(entry)

    if not new_entries:
        print(f"Nichts Neues. {len(all_pngs)} PNGs im Ordner, alle bereits im Katalog ({len(catalog)} Eintraege).")
        return

    print(f"{len(new_entries)} neue/aktualisierte Sprite(s):\n")
    print(f"{'file':<38} {'cls':<11} {'topw':>5} {'touch':<6} {'halo':>5}")
    for e in new_entries:
        print(f"{e['file']:<38} {e['cls']:<11} {e['topw']:>5} {''.join(e['touch']):<6} {e['halo']:>5}")
    print(f"\n-> cls-Verteilung pruefen: {sum(1 for e in new_entries if e['cls']=='xcu_topcut')} xcu_topcut, "
          f"{sum(1 for e in new_entries if e['cls']=='bust')} bust, {sum(1 for e in new_entries if e['cls']=='full')} full")
    print("halo > 0.5 => weisse Kontur wird beim Rendern automatisch entfernt (siehe engine.load_sprite).")

    if args.dry_run:
        print("\n--dry-run: sprite_catalog.json NICHT geschrieben.")
        return

    merged = list(by_name.values())
    json.dump(merged, open(args.catalog, "w"), indent=1)
    print(f"\nsprite_catalog.json aktualisiert: {len(merged)} Eintraege total.")


if __name__ == "__main__":
    main()
