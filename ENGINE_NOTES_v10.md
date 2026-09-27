# ENGINE_NOTES_v10 — QA-Pass 2026-09-26

Dieser Pass war eine reine Code-/Struktur-Analyse + gezielte Bugfixes auf dem
hochgeladenen `raymi_engine_v9`-Ordner, ausgelöst durch Nutzer-Feedback:
Ordner unstrukturiert/veraltet/doppelt, Assets wirken lieblos, Animationen
erscheinen immer gleich, Schrift/Assets überlappen manchmal, Qualitätsniveau
älterer Videos (u.a. Tier-List, Sumi-Assets) wird nicht mehr erreicht.

Kein bestehender Code wurde gelöscht oder umgeschrieben (Projekt-Regel, siehe
ENGINE_NOTES.md) — nur erweitert/umgebogen bzw. eindeutig totes/dupliziertes
Material einsortiert.

## 1. Der Hauptbefund: das gute Asset-System lief nie mit

`assets_v6.py` (Material-Pipeline: Gradient-Fill, Rim-Shade, Specular-
Highlight, EIN konsistenter Look, + `asset_library`-Wiederverwendungs-Cache)
existierte bereits vollständig und laut eigenem Docstring 1:1 drop-in-
kompatibel zu `assets_v3`/`assets_v4`. Trotzdem importierten **alle** drei
Render-/Szenen-Skripte (`raymi_short.py`, `proof_onigiri_v4.py`,
`landscape_demo_v5.py`) weiterhin `assets_v3`/`assets_v4` — den alten,
flachen Look ohne jedes Shading. Das ist mit hoher Wahrscheinlichkeit die
Hauptursache für "Asset-Generierung schwach, wirkt lieblos": die bessere
Qualität war längst gebaut, wurde nur nirgends benutzt.

**Fix:** Alle drei Skripte importieren jetzt `assets_v6` (als `A`). Geprüft:
alle von `raymi_short.py` benötigten Funktionen (`onigiri`, `badge`, `gavel`,
`scroll`, `nigiri`, `soy`, `wasabi`, `sponge`, `bowl`, `pizza`, `plate`,
`with_shadow`, `starburst`) existieren in `assets_v6.py` mit identischer
Signatur — per Smoke-Test bestätigt (siehe unten).

## 2. Animations-Monotonie ("Assets erscheinen immer einfach nur")

Der generische Zweig in `draw_assets()` (für `x`/`ok`/`nigiri`/`soy`/
`wasabi`/`sponge`/`bowl`/`pizza` — alles ohne eigene Choreografie wie
Gavel/Scroll/Burst/Label) nutzte für **jedes** Asset exakt dieselbe
Ein-/Ausblendung (`back_out`-Scale-Pop). Andere Icon-Typen (Gavel, Scroll,
Burst, Label/Stamp) hatten schon eigene Bewegungsmuster — dieser eine Zweig
nicht.

**Fix:** neues Varianten-System (`_anim_variant`, `_anim_offsets`) mit vier
Einstiegs-/Ausstiegs-Choreografien: `pop` (bisheriges Verhalten),
`drop` (fällt von oben rein, kleiner Bounce), `slide` (schiebt seitlich
rein/raus), `spin` (dreht sich rein). Die Variante wird **deterministisch**
aus `(kind, trig)` gehasht, damit kein Beat manuell angefasst werden musste
und das Ergebnis trotzdem bei jedem Render gleich aussieht.

⚠️ Dabei ein Bug im ersten Wurf selbst gefangen und korrigiert: Pythons
eingebautes `hash()` ist für Strings **pro Prozess zufällig gesalzen**
(`PYTHONHASHSEED`). Da ein Render als mehrere `video a b`-Subprozess-Batches
läuft (siehe `cache_util.py`), hätte dasselbe Asset in Batch 1 eine andere
Animation bekommen als in Batch 2 — ein sichtbarer Bruch an der
Batch-Grenze. Ersetzt durch einen stabilen `md5`-basierten Hash
(`_stable_hash`).

## 3. Konkreter Overlap-Bug gefunden und behoben

In `CFG['meal']`, Beat 3: drei "SNACK"-Stempel bei x=.28/.50/.72 mit Größe
.44/.44/.56 — und, entscheidender: **alle mit identischem Trigger-Wort
("snack") und ohne `t_off`**. Weil das Wort "snack" in diesem Beat nur
einmal vorkommt, bekamen alle drei Stempel exakt denselben Startzeitpunkt
(`t0`) zugewiesen → garantiertes gleichzeitiges Einblenden dreier
mittelgroßer Objekte auf engem Raum. Das erklärt das gemeldete
"Schrift/Assets überlappen manchmal".

**Fix:** Stempel weiter auseinandergezogen (x=.20/.50/.80), verkleinert
(.34/.34/.40 statt .44/.44/.56) und über `t_off` (0.0/0.10/0.20s)
nacheinander statt gleichzeitig gestartet.

**Allgemeine Regel für künftige Beats** (bitte bei neuen Configs beachten):
Wenn mehrere Assets denselben Trigger-Zeitpunkt bekommen (gleiches
Triggerwort, kein `n`/`t_off`-Unterschied), IMMER genug horizontalen Abstand
UND/ODER einen `t_off`-Versatz einplanen — sonst blitzen sie exakt
übereinander auf.

## 4. Bereits gebaute, aber nie verwendete Assets aktiviert

- `subscribe_badge()` (Font + UV-Palette, extra für diesen Zweck laut
  `Raymi-Wissen/04_Asset-Creation-and-QC-Guidelines.md` Punkt 1 gebaut) wurde
  von keinem Render-Skript je gezeichnet. Jetzt klein oben rechts in den
  letzten ~1.1s eingeblendet (weit weg von Hook/Captions/CTA-Bubble).
- `engagement.loop_reply_hint()` (fertig dokumentiert, nie aufgerufen) —
  jetzt in den letzten ~0.85s aktiv.

## 5. Neu: `tier_list.py` — fehlende Fähigkeit nachgebaut

Im mitgeschickten alten Referenzvideo gab es u.a. eine animierte Tier-List
(S/A/B/C-Reihen). Das war in der v9-Engine **komplett nicht vorhanden** —
keine Regression, sondern eine Fähigkeit, die beim Umbau nie in die neue
Engine übernommen wurde. Neues, eigenständiges Modul `tier_list.py`, baut
direkt auf `engine.py`/`assets_v6.py` auf (keine Parallel-Engine),
Reihen schieben nacheinander rein, Items poppen versetzt in ihre Zeile.

Per Smoke-Test verifiziert (`python3 tier_list.py` erzeugt ein Standbild).
Dabei zwei Bugs im ersten Entwurf gefunden und sofort behoben:
1. S/A/B/C-Label-Farbe war fast identisch zur Kontur-Farbe → Buchstabe las
   sich wie ein Klecks statt lesbar (Fix: weiße Füllung, wie überall sonst
   in der Engine).
2. Ein einzelnes Item in einer 1-Item-Zeile (z.B. nur "Pizza" in Tier C)
   bekam die volle Zeilenbreite als Ziel-Icon-Breite und lief bei
   quadratischen Icons in die Nachbarzeilen hinein (Fix: Icon wird jetzt in
   fester Basisgröße gebaut und über einen Fit-Faktor `_fit_scale()` unter
   Berücksichtigung von Breite UND Zeilenhöhe herunterskaliert).

Nutzung z.B. als eigener Beat:
```python
import tier_list as TL
TL.draw_tier_list(fr, t, t0=beat_start, tx=TX, title='SUSHI TIER LIST', rows=[
    ('S', GOLD,   ['nigiri', 'onigiri']),
    ('A', CYAN,   ['soy']),
    ('B', SILVER, ['wasabi', 'sponge']),
    ('C', RED,    ['pizza']),
])
```

## 6. Ordner aufgeräumt (nur eindeutig totes/dupliziertes Material bewegt)

`paths.py` löst Asset-Ordner relativ zu **seinem eigenen** Verzeichnis auf,
`raymi_short.py` lädt `sprite_catalog.json` relativ zu **seinem eigenen**
Verzeichnis, `engine.find_font()` sucht die Font relativ zu **engine.py**.
Deshalb wurde bewusst NICHT tief/verschachtelt umstrukturiert (Risiko, die
Pipeline zu zerbrechen) — alle aktiven Skripte, `sprite_catalog.json`, die
Fonts, `assets/`, `assets_library/` bleiben auf derselben Ebene wie bisher.
Verschoben wurden nur Dateien, die von KEINEM Skript mehr referenziert
werden:

- `legacy/assets_v3.py`, `legacy/assets_v4.py`, `legacy/assets_v5.py` —
  seit Fix #1 importiert sie kein aktives Skript mehr. Bewusst NICHT
  gelöscht (Projekt-Regel), aber klar als veraltet markiert und aus dem
  Hauptordner heraus, damit auf den ersten Blick klar ist, was aktiv
  gerendert wird und was nur Historie ist. Siehe `legacy/README.md`.
- `_archive/raymi_assets_pack_v91.zip` — redundantes Zip, Inhalt liegt
  bereits identisch/extrahiert in `assets_library/` vor.
- `_archive/assets_v6_sheet_v91_final.png` — ein QC-Kontaktabzug (Vorschau-
  Bild), keine Laufzeit-Abhängigkeit.
- `_archive/PNG_extra_webp_ungenutzt/` — 3 unbenutzte WebP-Dateien (~52 MB),
  keine Pipeline-Datei sucht in `PNG_extra_webp/`. EIN exaktes
  Byte-für-Byte-Duplikat (`RAY_CU_F_HAPPY_UV_001 (1).webp`, identische
  Dateigröße wie das Original) wurde gelöscht statt archiviert, weil es
  nachweislich nur ein doppelter Upload war.

Nach der Aufräumaktion erneut geprüft: alle Skripte kompilieren weiterhin,
`paths.asset_dir('PNG'/'Background')` löst weiterhin korrekt auf,
`assets_v6`/`subscribe_badge` funktionieren weiterhin.

## 7. Was mit Code-Fixes NICHT lösbar war (bewusst nicht versucht)

Die eigentliche Charakter-Artwork-Qualität im Referenzvideo (z.B. die
"Sumi"-Assets) ist Bildgenerierung/Illustration, keine Renderer-Frage — kein
Code-Fix in dieser Engine kann neue, hochwertige Charakter-Posen oder
komplett neue Prop-Illustrationen erzeugen. Das müsste über denselben Weg
laufen, über den die vorhandenen `assets/PNG/RAY_*`-Sprites entstanden sind
(PixAI o.ä., siehe `Raymi-Wissen/04_Asset-Creation-and-QC-Guidelines.md`,
Kopfzeile: "nicht für die PixAI-Charakterbilder selbst"). Empfehlung: neue
Posen/Ausdrücke separat als Bild-Generierungs-Auftrag angehen, dann per
`catalog_tool.py` automatisch in `sprite_catalog.json` einsortieren.

## 8. Nicht vollständig End-to-End getestet

Es lag keine echte Voiceover-Datei bei, daher konnte `raymi_short.py`
nicht komplett von `align()` bis `finish` durchgerendert werden (das
bräuchte `voiceover_*.mp3` + `input_used_*.txt` im Upload-Ordner). Geprüft
wurden stattdessen: Syntax aller Dateien, direkter Funktionsaufruf der
neuen/geänderten Asset-Funktionen (inkl. `subscribe_badge`), Rauchtest von
`tier_list.py` mit echtem Bild-Output, sowie `paths.py`-Auflösung nach der
Ordner-Umstrukturierung. Der erste echte Kurzvideo-Render mit einer
mitgelieferten Audiodatei ist der nächste sinnvolle Schritt.
