# Raymi Engine v9 — was ist neu (Addendum zu ENGINE_NOTES.md / _v5 / _v6 / _v7 / _v8)

REGEL gilt weiter: nichts an engine.py/assets_v3.py/assets_v4.py/assets_v5.py/
proof_onigiri_v4.py/raymi_short.py/landscape_demo_v5.py/engagement.py wurde geloescht
oder umgeschrieben, nur ergaenzt. Alte Videos, die noch `assets_v3`/`assets_v4`/
`assets_v5` importieren, rendern unveraendert weiter. Alle bisherigen Notes bleiben
gueltig, dies ist nur der Zusatz fuer diese Session.

## Ausloeser

Feedback (woertlich): "erstellte assets haben schlechte qualitaet, nutzen raymi font
nicht, sehen billig und schlecht aus und passen nicht zu raymis aesthetik" + "assets
muessen wiederverwendbar sein und gespeichert werden, nach jeder Videoerstellung eine
Datei ausgeben, die ich einspeisen kann, damit diese Assets in Zukunft genutzt werden
koennen."

Zwei getrennte Probleme, zwei getrennte Loesungen:
1. **Qualitaet/Konsistenz** -> `raymi_style.py` (neu)
2. **Wiederverwendbarkeit ueber Sessions hinweg** -> `asset_library.py` (neu)
Beide zusammen genutzt von `assets_v6.py` (neu) - dem eigentlichen Ersatz-Icon-Set.

## 1. `raymi_style.py` (NEU) — eine Material-Pipeline statt N Ad-hoc-Fills

Diagnose, warum die alten Assets "billig" wirkten: jede Funktion in assets_v3/v4/v5
hatte ihre eigene, leicht andere Umsetzung — mal ein Flat-Fill, mal ein zusaetzlicher
Highlight-Blob, mal keiner, drei leicht verschiedene Kopien von GOLD/SILVER/BRONZE/
RED/GREEN/CYAN an drei Stellen im Code. Das Problem war nie eine einzelne Form,
sondern dass nichts wie "ein Material" bzw. "ein Kanal-Look" wirkte.

`raymi_style.py` ist ab jetzt die EINE Quelle fuer:
- **Die kanonische Palette** (`PALETTE`/`GOLD`/`SILVER`/`BRONZE`/`RED`/`GREEN`/`CYAN`
  neben `engine.UV`/`UVL`/`PINK`/`DARK`) - keine drei leicht abweichenden Kopien mehr.
- **`gradient_mask_fill()`** - vertikaler Gradient + leichtes Zentrumslicht statt
  Flat-Color.
- **`rim_shade()`** - Ambient-Occlusion-artige Abdunkelung am unteren Rand, gibt
  Formen Volumen statt Sticker-Flachheit.
- **`specular()`** - EIN weiches diagonales Glanzlicht pro Objekt (die "Spielzeug/
  Glas"-Anmutung, die flachen cv2-Fills fehlte).
- **`regions()`** - der Baustein fuer mehrteilige Objekte (Onigiri = Reis+Nori,
  Glocke = Kuppel+Schuerze+Klingel, Pokal = Becher+Henkel+Sockel, ...): jeder Teil
  bekommt seinen eigenen Gradient/Rim-Shade, EINE gemeinsame Tinten-Outline kommt aus
  der Vereinigung aller Teile, EIN Glanzlicht liegt ueber dem Gesamtobjekt - dadurch
  wirkt das fertige Icon als EIN Ding, nicht als zusammengesetzte Einzelteile.
- **`text_plate()`** - der EINZIGE Codepfad in diesem Paket, der ueberhaupt Text auf
  ein Asset zeichnet, und er verlangt zwingend die aufrufende `engine.Text`-Instanz
  (Raymi-Regular.ttf) als Parameter. Es gibt hier keinen zweiten Pfad, der auf einen
  Default-Font zurueckfallen koennte - behebt "nutzen raymi font nicht" strukturell
  statt nur durch Disziplin/Erinnerung (siehe QC-Guidelines Regel #1).

## 2. `asset_library.py` (NEU) — session-uebergreifende, wiederverwendbare Assets

Vorher: `_AS`-Dicts in proof_onigiri_v4.py/raymi_short.py cachen Assets nur
INNERHALB eines Renderlaufs (siehe cache_util.py-Kommentar dazu) - zwischen zwei
Chat-Sessions war jedes Icon weg und wurde beim naechsten Video stumpf neu gezeichnet
(und sah durch andere Zufallszahlen/leichte Codeaenderungen ggf. leicht anders aus).

`asset_library.py` legt eine echte, plattenpersistente Bibliothek unter
`assets_library/` an (`library.json` Manifest + `png/<name>.png`):

- **`LIB.cached(name, builder, params=...)`** ist der einzige Weg, wie `assets_v6.py`
  ein Icon erzeugt: existiert `name` mit demselben Parameter-Hash schon in der
  Bibliothek, wird die gespeicherte PNG geladen - garantiert PIXEL-IDENTISCH mit dem
  vorherigen Video, kein Neuzeichnen. Nur bei neuem Namen oder geaenderten Parametern
  (andere Groesse/Farbe) wird einmal neu gebaut und gespeichert.
- **`LIB.export_pack(pfad.zip)`** schreibt GENAU "die Datei, die ich einspeisen
  kann" - ein zip mit Manifest + allen PNGs.
- **`LIB.import_pack(pfad)`** / **`LIB.import_uploaded_packs()`** liest ein zuvor
  exportiertes Pack wieder ein (merged nach Zeitstempel, ueberschreibt nie neuere
  lokale Versionen mit einer alten Pack-Datei).
- Sucht die Bibliothek nach demselben Muster wie `paths.py` (Env `RAYMI_ASSET_LIBRARY`,
  sonst `assets_library/` neben den Skripten) - kein manuelles Pfad-Jonglieren.

### Workflow pro Video (neu)

```
# 1. (falls vorhanden) letztes Pack wieder einspeisen, EINMAL am Sessionanfang:
python3 -c "import asset_library as al; hits=al.LIB.import_uploaded_packs(); print(hits)"
#    -> findet automatisch jede *raymi_assets_pack*.zip in den Uploads

# 2. Video wie gewohnt bauen/rendern (neues Skript importiert assets_v6 statt v3/v4/v5,
#    siehe Abschnitt 4) - jedes benutzte Icon wird automatisch in assets_library/ abgelegt.

# 3. nach dem Render EINMAL:
python3 asset_library.py pack /mnt/user-data/outputs/raymi_assets_pack.zip
#    -> das ist die Datei, die du dir merkst/herunterlaedst und in der NAECHSTEN
#       Session wieder hochlaedst (Schritt 1 dort holt sie automatisch ab).

# Bibliothek jederzeit einsehen:
python3 asset_library.py list
```

Kein bestehendes Skript musste dafuer angefasst werden - Schritt 1 und 3 sind zwei
zusaetzliche, optionale Kommandozeilen-Aufrufe um den unveraenderten `align/audio/
video/finish`-Ablauf aus ENGINE_NOTES.md herum, kein Eingriff in raymi_short.py/
proof_onigiri_v4.py noetig. Wer die Bibliothek automatisch am Ende von `finish`
exportiert haben will: in der eigenen Kopie des Referenz-Skripts (siehe Abschnitt 4
der ENGINE_NOTES.md-REGEL: NEUE VIDEOS = Kopie) im `finish`-Zweig zwei Zeilen
ergaenzen:
```python
import asset_library as al
al.LIB.export_pack(os.path.join(paths.output_dir(), 'raymi_assets_pack.zip'))
```

## 3. `assets_v6.py` (NEU) — das eigentliche Icon-Set, v3/v4/v5-drop-in-kompatibel

Enthaelt ALLE Icons aus assets_v3+assets_v4+assets_v5 unter denselben Funktionsnamen/
-signaturen (`onigiri`, `badge`, `gavel`, `scroll`, `starburst`, `sparkle`, `nigiri`,
`soy`, `wasabi`, `sponge`, `bowl`, `pizza`, `plate`, `stamp_frame`, `bell`, `heart`,
`medal`, `trophy`, `clock`, `flame`, `meter`, `vs_panel`, `shell`, `starfish`,
`moon_stars`, `comment_icon`, `share_arrow`) plus NEU `subscribe_badge(tx_engine, w)` -
das in `04_Asset-Creation-and-QC-Guidelines.md` Abschnitt 1 gewuenschte, komplette
Branding-Badge (Glocke + "SUBSCRIBE"-Plate ueber `text_plate()`, siehe QC-Sheet).

Fuer ein NEUES Video reicht:
```python
import assets_v6 as A   # statt: import assets_v3 as A, assets_v4 as A4  (oder v5)
```
Der restliche Beat-/Szenen-Code (`asset(kind, wpx)`-Dispatch-Dict in raymi_short.py/
proof_onigiri_v4.py) bleibt strukturell identisch - nur die Quelle der Icons wechselt.
Bestehende Referenz-Skripte (proof_onigiri_v4.py, raymi_short.py selbst) wurden NICHT
umgestellt (REGEL: fertige Referenz-/Produktions-Skripte fuer bestehende Videos werden
nicht nachtraeglich angefasst, exakt wie assets_v4/assets_v5 beim Erscheinen auch nicht
sofort eingetragen wurden, siehe ENGINE_NOTES_v5.md/_v8.md) - fuer das naechste neue
Video einfach `assets_v6` in der Kopie importieren.

Sichtgeprueft in dieser Session: `python3 assets_v6.py` schreibt `assets_v6_sheet.png`
(alle 24 Icons + Subscribe-Badge nebeneinander) - liegt dieser Antwort bei.

## 4. Was NICHT gemacht wurde (bewusst)

- assets_v3/v4/v5 wurden NICHT geloescht/geaendert - Videos, die sie noch importieren,
  sehen unveraendert so aus wie vorher.
- proof_onigiri_v4.py/raymi_short.py wurden NICHT auf assets_v6 umgestellt (siehe oben,
  gleiche Begruendung wie bei jedem fruehren Assets-Zuwachs).
- Kein neues Video gerendert/exportiert in dieser Session - nur das Icon-Set selbst
  gebaut und per Sheet + Einzelrender (Subscribe-Badge) visuell geprueft.
- Charakter-Sprites (RAY_*.png, sprite_catalog.json) sind von alldem nicht betroffen -
  dieses Modul behandelt ausschliesslich die prozedural GEZEICHNETEN Support-Icons.

## TODO (uebernommen aus v5-v8, unveraendert offen, plus neu)

- Config-Loader (JSON) statt Config im Skript
- `fx_whip` als dritte Cut-Art verdrahten
- CTA-Strategie fuer Longform
- Geografie-Report einpflegen
- NEU: naechstes echtes Video mit `assets_v6` statt `assets_v3/v4/v5` produzieren und
  das dabei entstehende erste echte `raymi_assets_pack.zip` als Startpunkt fuer alle
  folgenden Videos benutzen (in dieser Session nur mit Platzhaltergroessen befuellt,
  kein echter Video-Kontext).
- NEU (optional, nicht umgesetzt): automatischer `finish`-Hook statt manuellem
  `asset_library.py pack`-Aufruf, falls das kuenftig gewuenscht ist (siehe Snippet
  in Abschnitt 2).

---

## Nachtrag (gleiche Session, Teil 2): v9.1 — Material-Pipeline nachgeschaerft, Pokal-Bug behoben

### Ausloeser
Feedback nach dem ersten v9-Assets_v6-Sheet: Qualitaet besser als v3/v4/v5, aber weiterhin
"lieblos"/"billig", eindeutig schlechter als die Charakter-Kunst (Sumi/Salmon-artige Assets).
Trophy() sah konkret "komisch" aus.

### Ehrliche Einordnung zuerst (kein Sugarcoating)
Sumi/Salmon-artige Bilder sind vermutlich KI-generierte/gemalte Illustrationen (PixAI/
Tsubaki3-Pipeline, siehe 00_README.md "PixAI/Tsubaki3-Prompts... betreffen die Bild-
Erzeugung"), keine prozedural gezeichneten Vektorformen. assets_v6.py/raymi_style.py sind
und bleiben eine PROZEDURALE Pipeline (PIL/cv2-Formen + Gradient/Shading-Code). Das ist ein
grundsaetzlich anderes Medium als eine gerenderte/gemalte Illustration und wird deren
Detailgrad (Materialbruch, organische Linienfuehrung, Lichtstimmung) strukturell nie 1:1
erreichen, egal wie sehr die Shading-Pipeline verbessert wird - das ist eine Grenze der
Technik, kein Bug, den man wegpatchen kann. Innerhalb dieser Grenze wurde die Pipeline in
dieser Session spuerbar nachgeschaerft (siehe unten). Falls wirklich Illustrations-Parity
mit Sumi/Salmon gewuenscht ist: der ehrliche naechste Schritt waere, Icons wie Sumi/Salmon
UEBER DIESELBE Bild-Generierungs-Pipeline zu erzeugen (mit `catalog_tool.py` katalogisiert
wie jedes andere PNG) statt sie weiter in Code zu zeichnen - das ist eine bewusste
Empfehlung, keine in dieser Session vorgenommene Aenderung.

### Konkrete Fixes/Verbesserungen (raymi_style.py, assets_v6.py)
1. **`trophy()`-Bug behoben.** Die Henkel-Arcs in v9.0 (`d.arc(start=250,end=110,...)`)
   schwenkten durch die FALSCHE Seite (PIL sweept von start zu end in aufsteigendem Winkel -
   das ging durch die dem Becher zugewandte Seite statt durch die Aussenseite), dadurch
   wirkte der Pokal verzerrt/"komisch". Ein erster Fix-Versuch behob zwar die Schwenkrichtung,
   liess die Henkel aber mit einer viel zu grossen Oeffnung (~190°) sichtbar frei neben dem
   Becher schweben statt daran anzuliegen. Endstand: Henkel als eigene, metallisch geshadete
   Ring-Layer (`_ring_layer()`, NEU) mit schmaler ~110°-Oeffnung zur Becher-Seite hin, korrekt
   unter dem Becher-Koerper compositet (`layer_over()`, NEU) - sitzen jetzt sichtbar am Becher.
2. **`metallic_fill()` (NEU, raymi_style.py)** - gebaenderter "gebuersteter Metall"-Gradient
   fuer Trophy-Henkel und Medal-Scheibe statt des bisherigen glatten Flat-Gradient. Gold sieht
   jetzt nach Metall aus statt nach gelb eingefaerbter Plastikform.
3. **`gradient_mask_fill()`** auf 3-Stopp-Gradient (Licht oben -> Koerper -> Schatten unten)
   plus warm/kalt-Farbtemperaturverschiebung erweitert (war reiner 2-Stopp-Lerp) - der groesste
   Einzelhebel gegen den "flach"-Eindruck.
4. **`specular()`** - zweiter, kleiner scharfer Glanzpunkt zusaetzlich zum weichen Blob (reale
   Hochglanz-Highlights sind nie EIN gleichmaessiger Fleck).
5. **`_fin()`** - feines Rauschen/Grain (nur innerhalb der Alpha-Maske, sehr dezent) auf JEDEM
   fertigen Asset, weil praktisch alle Icon-Builder in assets_v6.py am Ende durch `_fin()`
   laufen - dieser EINE Hebel wirkt automatisch auf alle 24 Icons, nicht nur auf einzeln
   ueberarbeitete. Bricht die mathematisch perfekte Vektorglaette auf, die den "billig"-
   Eindruck mit erzeugt.
6. **`rim_shade()`** leicht verstaerkt und auf INK_WARM statt neutralem Grau getont (haengt
   die Schattierung an die Markenfarbe statt an einen generischen Foto-Filter-Look).
7. **Cache-Versionierung (`STYLE_V='v91'`)**: JEDER `LIB.cached(...)`-Aufruf in assets_v6.py
   haengt jetzt an einem versionierten Namen - ohne das haette `asset_library.py` weiterhin
   stumpf die ALTEN (vor-Fix) PNGs aus `assets_library/` ausgeliefert, weil sich Name+Params
   nicht geaendert haetten (der Cache-Key ist name+params, nicht der Funktionscode). Ein reiner
   Code-Fix allein haette also NICHTS am ausgelieferten Bild geaendert, ohne diesen Schritt.
8. In dieser Session mitgeliefert: `raymi_assets_pack_v91.zip` (frisch gebautes Pack mit allen
   24 verbesserten Icons) - direkt als Startpunkt fuer das naechste Video nutzbar, kein
   Neuaufbau der Bibliothek noetig (`asset_library.py import raymi_assets_pack_v91.zip`).

### Sichtgeprueft
`assets_v6_sheet_v91_final.png` (alle 24 Icons + Subscribe-Badge) und eine Pokal-Grossaufnahme
bei 500px wurden in dieser Session tatsaechlich gerendert und visuell verglichen (vorher/
nachher), nicht nur behauptet.

### Was NICHT gemacht wurde
- Kein Wechsel von prozeduraler Zeichnung auf KI-generierte Icon-Bilder (siehe "Ehrliche
  Einordnung" oben) - das waere ein groesserer Schnitt (neue Bild-Assets, Katalogisierung)
  und wurde nicht ungefragt entschieden.
- assets_v3/v4/v5 weiterhin unveraendert (REGEL).
- Kein neues Video gerendert.

### TODO (ergaenzt)
- Falls Illustrations-Parity mit Sumi/Salmon wirklich das Ziel ist: Icon-Set stattdessen ueber
  die PixAI/Tsubaki3-Bild-Pipeline erzeugen lassen und per `catalog_tool.py` einpflegen, statt
  weiter an der Code-Shading-Pipeline zu drehen (siehe Einordnung oben).
- Gavel/Scroll/Bowl/Pizza etc. wurden NICHT einzeln ueberarbeitet (nur global durch die
  Pipeline-Verbesserung mitgezogen) - falls einzelne davon nach Ansehen des Sheets weiterhin
  seltsam wirken, gezielt benennen fuer eine naechste Runde statt "alles" pauschal.
