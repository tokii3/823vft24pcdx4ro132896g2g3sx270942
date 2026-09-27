# Raymi Engine v3 - Status & Regeln

REGEL: Diese Engine wird erweitert, nie neu geschrieben. Neue Session = dieses ZIP laden, engine.py/assets_v3.py lesen, dann nur ergaenzen.

## WICHTIG - keine Bildanalyse mehr pro Session (2026-09-24)
Alle 106 aktuellen Charakter-PNGs sind bereits in sprite_catalog.json vollstaendig
katalogisiert (bbox/touch/topw/cls/halo/contour_px). engine.py liest diese Werte
programmatisch (load_sprite()) - dafuer muss NIEMAND die PNGs einzeln ansehen.
Hintergrund-PNGs und Musik brauchen ohnehin keine Analyse, nur ein Manifest, siehe
BACKGROUNDS_AND_MUSIC.md.

Regel fuer jede neue Session:
1. sprite_catalog.json, BACKGROUNDS_AND_MUSIC.md und diese Datei lesen (Text, kein
   Bild-View) - das genuegt, um jede bestehende Datei einzuordnen.
2. Charakter-PNGs NICHT mit dem view-Tool oeffnen, nur um sie zu "verstehen" - der
   Katalog + die Ausdrucks-Liste unten reichen fuer die Szenen-Planung.
3. Kommen NEUE Charakter-PNGs dazu (Dateiname noch nicht in sprite_catalog.json):
   python3 catalog_tool.py /pfad/zum/PNG-Ordner
   Das Skript berechnet bbox/touch/topw/cls/halo/contour_px per Bildverarbeitung
   (keine Vision-Tokens) und haengt nur die neuen Eintraege an. Ergebnis kurz
   gegenchecken (Tabelle wird ausgedruckt), dann ggf. 1-2 auffaellige Sprites
   stichprobenartig ansehen statt aller.
4. Kommen neue Hintergruende/Musik dazu: einfach eine Zeile in
   BACKGROUNDS_AND_MUSIC.md ergaenzen (Motiv/Stimmung reicht aus dem Dateinamen).

## Dateien
- engine.py: Kern (Sprite laden/Halo entfernen, blit mit Pivot/Rotation, Text-Tiles, Wort-Timing, BG, Aura, Transitions zoom/glitch/flash, Shake)
- assets_v3.py: selbst gezeichnete Support-Assets (onigiri, badge x/ok, gavel, scroll, starburst, sparkle, with_shadow) - keine Font-Glyphen noetig
- sprite_catalog.json: pro PNG cls (bust / full / xcu_topcut), bbox, halo, touch
- proof_onigiri_v4.py: Referenz-Szene (Segmente, Assets, Audio, Render). NEUE VIDEOS = Kopie davon mit neuer BEATS-Config.
- Raymi-Regular.ttf: Caption-/Titelfont (kein "#"-Glyph! Apostroph nur in Grossschreibung sauber pruefen)

## Benoetigte Eingaben (nicht im ZIP, Pfade oben in proof_onigiri_v4.py anpassen)
- PNG-Ordner (106 Sprites), Background-Ordner, Background-Music-Ordner (bg_energetic.m4a etc.)
- Voice-MP3 (edge-tts) + Beat-Zeiten; best: _words.json aus generate_audio.py (aktuell noch geschaetzte Wortzeiten)
- Python: numpy, opencv-python, pillow, ffmpeg im PATH

## Befehle (Windows: py statt python3)
- python3 proof_onigiri_v4.py audio            -> Mix (Stimme + Musik + SFX, Loudnorm -14.5, Limiter)
- python3 proof_onigiri_v4.py video 0 110      -> Frames 0-109 (in Teilen rendern, dann weiter 110 240 usw.)
- python3 proof_onigiri_v4.py stills 0.6 2.2   -> Einzelbilder zum Pruefen
- python3 proof_onigiri_v4.py finish           -> Teile + Audio zusammenfuegen

## Sprite-Regeln (gemessen an allen 106 PNGs)
- 51 bust, 32 full, 23 xcu_topcut. Dateiname "WS" ist oft falsch -> immer cls aus Katalog
- Hook + Haupt-Beats: nur bust, Breite 1.0 x Bildbreite (hero) oder .74 (inset), Oberkante 22.5% bzw. 40% Hoehe, Unterkante darf aus dem Bild laufen, KEIN Fade
- xcu_topcut: nur als Vollbild-Punch-in (Breite 1.26x)
- full: nur kleine Cutaways
- halo=1.0 (20 Dateien): weisse Kontur eingebrannt, load_sprite entfernt sie
- Kopfsichere Buesten mit Ausdruck: CU_CALM_001 froehlich, CU_CALM_003 besorgt, CU_CRY_001 traenen, CU_SURP_003 Hand vor Mund, CU_SURP_004 ><, CRY_043 weinend, HAPPY_PLAY_046 froehlich, NEUTRAL_021/023/025/026/037 neutral-schmollend-genervt, SMUG_045 smug, SURPRISE_028 / SURP_001 ueberrascht, THINK_036 nachdenklich, UPSET_032/034 erschrocken-traurig, UPSET_048 Schmollen

## Look-Regeln (von Nutzerin abgenommen)
- Caption: 2 Woerter pro Chunk, immer nur EIN Chunk sichtbar, Aktivwort hellblau (120,225,255), Betonung gold (255,214,84)
- Expression-/Framing-Wechsel alle halben Saetze; Cut-Arten: punch (Zoom+Flash) oder slide
- Pro Beat mind. ein gezeichnetes Support-Asset (Icon, Schriftrolle, Diagramm, Badge)
- SFX nur mit Grund (Hook-Thump, Asset-Pop, Knock, Bonk, Ding, Whoosh, Glitch), leise, unter der Stimme geduckt

## TODO
- Config-Loader (JSON) statt Config im Skript, gemeinsamer Code fuer alle Shorts
- Weitere Transitions (iris, swipe, flash-cut), Layout-Presets, Ganzkoerper-Cutaways, Tierlist/Rhythmgame-Assets
- Exakte Wortzeiten aus _words.json
- Hook-Skripte der Shorts ueberarbeiten
