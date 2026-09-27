# Raymi Engine v5 - was ist neu (Addendum zu ENGINE_NOTES.md)

REGEL gilt weiter: nichts an engine.py/assets_v3.py/proof_onigiri_v4.py/raymi_short.py
wurde geloescht oder umgeschrieben, nur ergaenzt bzw. an klar markierten Stellen
("v5:"-Kommentare im Code) getunt. ENGINE_NOTES.md bleibt unveraendert gueltig,
dies hier ist nur der Zusatz fuer Session 6.

## Was diese Version bringt (kurz)
1. Assets aus dem additions-Paket eingepflegt (nicht ueberschrieben): assets_v4.py
   (nigiri/soy/wasabi/sponge/bowl/pizza/plate/stamp_frame) + raymi_short.py
   (generischer Short-Builder fuer sushi/meal) liegen jetzt direkt neben engine.py.
2. Portable Pfade (paths.py) - Assets/Uploads/Outputs werden relativ zum Skript
   gesucht, mit den alten Sandbox-Pfaden nur noch als Fallback. Das Engine-ZIP
   laeuft dadurch "out of the box", wenn du es lokal entpackst und die
   assets/PNG, assets/Background, assets/Background-Music-Ordner daneben liegen
   (liegen im ZIP schon so).
3. Disk-Cache (cache_util.py) fuer Schritte, die vorher bei JEDEM Render-Batch
   neu gemacht wurden:
   - Sprite freistellen + resizen + Aura blurren (pro Sprite/Variante)
   - Hintergrundbild auf Zielaufloesung skalieren
   - Audio-Alignment (ffmpeg silencedetect + volle mp3-Dekodierung) in
     raymi_short.py - lief bisher bei JEDEM Skriptstart neu (auch bei
     'stills'/'video'-Batches), jetzt nur beim allerersten Mal pro Short.
   Cache liegt unter .cache/ neben den Skripten, invalidiert sich automatisch
   wenn sich eine PNG/mp3 aendert (Dateigroesse+mtime sind Teil des Cache-Keys).
   .cache/ ist NICHT im ZIP enthalten (reine Laufzeit-Ablage, baut sich beim
   ersten Render von selbst wieder auf).
4. Audio-Mix vereinheitlicht (audio_mix.py) - behebt genau das gemeldete
   Problem "Hintergrundmusik etwas zu laut, SFX von Animationen viel zu laut":
   - Musikbett-Zielpegel: -25dB -> -30dB RMS
   - Ducking der Musik WAEHREND die Stimme spricht: -7dB -> -13dB (vorher blieb
     die Musik praesent, jetzt tritt sie beim Sprechen fast komplett zurueck)
   - SFX-Pegel: globaler Faktor 0.62x auf alle Cue-Amplituden
   - SFX werden jetzt GENAUSO wie die Musik unter der Stimme geduckt (-9dB),
     vorher nur schwach mit einem festen *0.4-Faktor
   - weicher Soft-Limiter (tanh) VOR dem finalen Normalize statt hartem
     /max()-Clipping, damit einzelne Peaks (Gavel-Bonk, Whoosh) nicht die ganze
     Mischung nach unten ziehen
   proof_onigiri_v4.py und raymi_short.py hatten das vorher JEDES fuer sich
   dupliziert und leicht unterschiedlich - jetzt eine Implementierung, ein Ort
   zum Nachjustieren (audio_mix.MixConfig).
5. Mehr Bewegung/Wucht (Feedback: "wirkt noch statisch", "Transitions nicht
   deutlich genug erkennbar"), alles in engine.py als neue Funktionen ergaenzt:
   - fx_chroma: RGB-Kanal-Versatz ("chromatic aberration") kurz am Schnitt
   - fx_impact_lines: radiale Speedlines-Flash am Punch-Cut (Anime-Hit-Cue,
     macht einen Schnitt auch auf leisem Handylautsprecher sofort spuerbar)
   - fx_whip: Richtungs-Motion-Blur fuer einen optionalen Whip-Pan-Übergang
   - energy_shimmer: kleine kontinuierliche Skalierungs-Wobble, damit Raymi
     zwischen Beats/Emphasis-Woertern nie ganz stillsteht
   - progress_bar: duenner Fortschrittsbalken oben (siehe Recherche unten)
   - loop_seam: ueberblendet die letzten 0.3s in den allerersten Hook-Frame ->
     sauberer Loop bei Shorts-Replay/Autoplay statt hartem Neustart-Sprung
   In proof_onigiri_v4.py/raymi_short.py konkret hochgedreht: Punch-Zoom
   1.22->1.34, Flash .30->.40, Emphasis-Pop .055->.085, Idle-Rotation
   2.1/.5 -> 3.0/.9. scene()/frame() rufen die neuen FX jetzt mit auf.

## Recherche-Kurzfassung (YouTube-Algorithmus/Hooks/Retention, Stand 2026)
Quellen: mehrere aktuelle "YouTube Shorts best practices 2026"-Guides.
- Erste 3 Sekunden entscheiden: 20-40% der Zuschauer springen in den ersten
  10s ab, wenn der Hook das Titel-/Thumbnail-Versprechen nicht SOFORT
  einloest. Keine langsamen Intros/Branding-Sequenzen vor dem Payoff.
  -> im Code schon durch die 0.30s Hook-Punch-In-Animation abgedeckt, mit v5
  zusaetzlich schneller/knalliger (Zoom/Flash/Chroma direkt beim ersten Beat).
- "Pattern Interrupt": ploetzlicher Zoom, Soundeffekt oder Kamerawechsel haelt
  die Aufmerksamkeit gegen das Scroll-Verhalten der Shorts-Feed-Nutzer. Muss
  UNMISSVERSTAENDLICH sein, nicht subtil. -> Grund fuer die deutlich
  verstaerkten Cut-FX in v5 (Chroma+Impact-Lines+staerkerer Zoom/Flash statt
  nur leichtem Zoom+Flash wie in v4).
- Shorts-Algorithmus gewichtet "watch-all rate" (wird das Video komplett zu
  Ende geschaut) sehr stark, staerker als reine View-Zahl. Kurze, dichte
  Videos ohne Leerlauf schlagen laengere. -> bestaetigt den bestehenden
  Half-Sentence-Cut-Rhythmus aus ENGINE_NOTES.md, keine Kuerzung noetig.
- Rewatch/Loop-Verhalten (Video startet nach Ende sofort neu) zaehlt fuer die
  Retention-Kurve positiv, wenn der Uebergang Ende->Anfang nicht wie ein harter
  Schnitt wirkt. -> loop_seam() (siehe oben).
- Sichtbarer Fortschritt/Countdown erhoeht nachweislich die Wahrscheinlichkeit,
  dass bis zum Ende geschaut wird (Viewer sehen "wie viel noch kommt").
  -> progress_bar() (siehe oben), bewusst duenn/dezent gehalten, damit es
  nicht vom Sprite ablenkt.
Kein neues Video wurde erzeugt (wie gewuenscht) - diese Punkte sind als
Engine-Faehigkeiten/Tuning eingebaut, fuer den naechsten tatsaechlichen
Video-Export bereit.

## Benutzung (unveraendert + neu)
Befehle wie in ENGINE_NOTES.md, nur zwei neue Umgebungsvariablen optional:
  RAYMI_ASSETS   - falls du die assets/ nicht direkt neben die Skripte legst
  RAYMI_UPLOADS  - Ordner mit Voiceover-mp3 + Text (ersetzt /mnt/user-data/uploads)
  RAYMI_CACHE    - falls du den .cache/-Ordner woanders haben willst
Ohne diese Variablen: einfach die ZIP-Struktur so lassen wie geliefert
(assets/PNG, assets/Background, assets/Background-Music neben den .py-Dateien),
dann funktioniert alles ohne weitere Anpassung.

Getestet in dieser Session: proof_onigiri_v4.py wurde mit den echten
mitgelieferten Assets importiert und an 5 Zeitpunkten (Hook, Mitte, zwei
Cut-Grenzen, Loop-Ende) tatsaechlich gerendert und visuell geprueft (Sprites,
Chroma/Impact-Lines/Progress-Bar/Loop-Seam sichtbar korrekt). audio_mix.py
wurde separat mit echtem Musiktrack + synthetischer Stimme durchgemessen:
RMS waehrend Sprache 0.29 vs. RMS in Sprechpausen (nur Musik) 0.038 - Ducking
greift spuerbar. raymi_short.py wurde nur bis zum fehlerfreien Import/Compile
geprueft (braucht echte Voiceover-mp3+Text-Uploads fuer einen vollen Render,
die in dieser Session nicht vorlagen) - nutzt aber exakt dieselben gepatchten
Funktionen (sprite/bgimg/build_audio/frame) wie proof_onigiri_v4.py.

## TODO (unveraendert von v4, weiterhin offen)
- Config-Loader (JSON) statt Config im Skript, gemeinsamer Code fuer alle Shorts
- Exakte Wortzeiten aus _words.json statt geschaetzt
- Weitere Layout-Presets, Ganzkoerper-Cutaways, Tierlist/Rhythmgame-Assets
- fx_whip ist geschrieben, aber noch in keinem TRANS-Preset verdrahtet -
  naechstes Mal als dritte Cut-Art (neben zoompunch/glitch) ausprobieren

---

## Nachtrag (gleiche Session, Teil 2): Wissenspaket, Querformat, Stimm-Politur

### Raymi-Wissen/ eingepflegt
Der Ordner `Raymi-Wissen/` (00_README bis 05_Channel-Brand-Info) liegt jetzt
im Engine-Paket. Ersetzt das alte Google-Drive-Doku-System als Wissensquelle
fuer alles, was NICHT Code/Render-Logik ist (Charakter-Voice, Lore/Memory,
Script-Guide, Asset-QC-Checkliste, Channel-Infos). `04_Asset-Creation-and-QC-
Guidelines.md` ist besonders relevant fuer neue Szenen-Skripte (Kopfabschneiden,
Font-Pflicht, Bounce nur auf emph-Woertern etc.) - vor jedem neuen Video kurz
gegenlesen. Reine Dokumente, keine Code-Aenderung noetig, um sie "einzupflegen".

### Querformat/Landscape-Rendering (NEU)
engine.py kann jetzt zwischen Hochformat (Shorts, bisheriger Default) und
Querformat (Longform) umschalten:
- `engine.set_orientation('portrait'|'landscape'|'landscape_hq'|'landscape_4k')`
  setzt W/H/FPS zentral um. Funktioniert praktisch ohne Aenderung an den
  bestehenden engine.py-Funktionen, weil die alle W/H als Modul-Globals zur
  Laufzeit lesen (cover, bg_frame, vignette, blit, alle fx_*, progress_bar) -
  ein zentraler Schalter reicht.
- WICHTIGE FALLE: `from engine import *` kopiert W/H/FPS als eigene Namen in
  das Skript. Ruft ein Skript set_orientation() danach auf, muss es selbst
  `W, H, FPS = engine.W, engine.H, engine.FPS` neu ziehen (steht auch im
  Docstring von set_orientation()). landscape_demo_v5.py macht das vor.
- `engine.layout_preset()` liefert orientierungsabhaengige Default-Anker
  (Hero-Position/-Breite, Caption-Zone, linkes Textpanel, Sicherheitsraender)
  statt hart codierter Hochformat-Zahlen wie in proof_onigiri_v4.py/
  raymi_short.py. Fuer Querformat: Hero steht rechts im Bild (kleiner, nicht
  bildfuellend), links bleibt Platz fuer ein Titel-/Fakten-Textpanel -
  klassisches Explainer-/Longform-Layout statt des Shorts-Vollbild-Portraits.
- `landscape_demo_v5.py` (NEU, analog zu proof_onigiri_v4.py fuer 9:16) ist
  die Referenz zum Kopieren fuer ein echtes 16:9-Video: zeigt Hero-Placement,
  Textpanel, Karaoke-Caption in der begrenzten Caption-Zone, UND dass die
  v5-Cut-FX (Chroma-Split, Impact-Lines, Zoom/Flash), Progress-Bar und
  Loop-Seam unveraendert im Querformat funktionieren. Mit den mitgelieferten
  Assets gerendert und visuell geprueft (Hook-Frame + Schnitt-Frame) - Kopf/
  Ohren nicht abgeschnitten, Textpanel und Caption sauber im sicheren Bereich.
  Fuer ein echtes Video: Skript kopieren, echtes Voiceover + align()-Pipeline
  wie in raymi_short.py einbauen (bisher nur mit geschaetztem word_times()-
  Timing getestet, kein echtes Voiceover in dieser Session vorhanden).
- "Qualitativ hochwertig" fuer echte Longform-Exports: `landscape_hq` (1440p)
  oder `landscape_4k` nutzen, sofern die PNG-Assets/Backgrounds die
  Aufloesung hergeben (Sprites werden bei sehr hoher Zielbreite hochskaliert,
  nicht neu gerendert - bei 4K ggf. Kantenqualitaet der Sprites pruefen).

### Stimme klingt jetzt automatisch besser (audio_mix.py: VoiceConfig/polish_voice)
Kein Fachwissen noetig - `build_mix()` schickt jede Stimme jetzt automatisch
durch eine 5-stufige Filterkette (`audio_mix.VoiceConfig`/`polish_voice()`,
vorsichtig vor-eingestellt, siehe Kommentare in audio_mix.py fuer die
Erklaerung jedes einzelnen Schritts):
1. Hochpassfilter (90Hz) - entfernt Brummen/Poltern unterhalb der Stimme
2. Rauschentfernung (afftdn) - nimmt durchgehendes Hintergrundrauschen raus
3. sanfter Praesenz-Boost bei 3.2kHz - macht die Stimme im Mix verstaendlicher,
   bewusst zurueckhaltend gewaehlt (Raymis Stimme ist laut Charakter-Doku
   ohnehin schon hoch/nasal, siehe Raymi-Wissen/01_Character-Voice-and-Style.md)
4. De-Esser - daempft scharfe S/Sch-Laute
5. Kompressor - gleicht laute/leise Stellen aneinander an
Abschaltbar/anpassbar ueber `audio_mix.MixConfig(voice_cfg=audio_mix.VoiceConfig(...))`,
z.B. `enabled=False` fuer die alte unbehandelte Stimme zum Vergleich. Mit
echtem Musiktrack + synthetischer Stimme end-to-end getestet (siehe erster
Teil dieser Notes) - funktioniert ohne Formatfehler, Laufzeit ca. 1s fuer
5s Audio.

