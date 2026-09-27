# Backgrounds & Musik - Manifest (Stand 2026-09-24)

REGEL: Dateien hier NICHT ansehen/anhoeren, nur diese Liste lesen. Neue Datei dazu ->
einen kurzen Einzeiler hier ergaenzen (Motiv/Stimmung reicht meist aus dem Dateinamen).

## Background/ (5 PNG, volles Bild, wird per engine.bg_frame() zoom+drift ueber die
ganze Szene gelegt - keine Sprite-Analyse noetig, nur cover-crop)
- bg rochen groß nahaufnahme.png -- Rochen (Hauptcharakter-Motiv), grosse Nahaufnahme
- bg rochen viele klein.png -- mehrere kleine Rochen, Schwarm
- bg rochen klein 2.png -- Rochen klein, Variante 2
- bg hai.png -- Hai
- pc quallen klein.png -- Quallen, klein
- bg sternenhimmel sternschnuppen.png -- (NEU v8) Sternenhimmel/Nebel-Wolken in Blau/Lila, zwei
  Sternschnuppen, keine Horizontlinie -- gut fuer nachdenkliche/dramatische/stargazing Beats
  (Raymis Hobby laut Raymi-Wissen/01_Character-Voice-and-Style.md), passt eng an die UV-Palette
- bg sonnenuntergang meer.png -- (NEU v8) Sonnenuntergang ueberm Meer, Horizont mittig, orange/pink
  Himmel zu blauem Wasser -- ruhiger/emotionaler Beat-Hintergrund (siehe bg_emotional.m4a-Paarung)
- bg strand tag sommer.png -- (NEU v8) Heller blauer Taghimmel, Wolken, Moewen, Strand -- einziger
  HELLER/Tag-Hintergrund im Set bisher (alle anderen sind dunkel/nachtblau getoent), gut fuer einen
  bewusst freundlichen/energischen Kontrast-Beat statt immer derselben nachtblauen Stimmung
- bg milchstrasse strand nacht.png -- (NEU v8) Milchstrasse ueber Strand bei Nacht, Sternschnuppe,
  Kueste rechts im Bild -- kombiniert Sternenhimmel-Stimmung mit Strand/Horizont-Tiefe

## Background-Music/ (9 m4a, als leises Bett unter Stimme gemischt, siehe
proof_onigiri_v4.py build_audio() / loop_music.py im Drive)
- bg_energetic.m4a -- energetisch, treibend (bisher Standard fuer Hook-lastige Shorts)
- bg_epic.m4a -- episch/gross
- bg_emotional.m4a -- emotional/ruhig
- bg_suspense.m4a -- spannungsgeladen
- bg_lofi_chill.m4a -- ruhig, lofi
- bg_dark_mysterious.m4a -- dunkel/mysterioes
- bg_rap_beat.m4a -- Rap-Beat (fuer den Rap-Song benutzt)
- bg_quirky.m4a -- verspielt/schraeg
- bg_chiptune.m4a -- 8-bit/verspielt

## Wenn neue Backgrounds/Musik dazukommen
Einfach oben je Datei eine Zeile anhaengen (Dateiname + 3-5 Worte Motiv/Stimmung,
meist direkt aus dem Dateinamen ablesbar). Kein Skript, keine Bildanalyse noetig -
diese Assets werden nie einzeln "katalogisiert" wie die Sprites, nur aufgelistet.
