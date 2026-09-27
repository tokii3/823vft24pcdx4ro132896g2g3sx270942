# Raymi Engine v8 — was ist neu (Addendum zu ENGINE_NOTES.md / _v5 / _v6 / _v7)

REGEL gilt weiter: nichts an engine.py/assets_v3.py/assets_v4.py/proof_onigiri_v4.py/
raymi_short.py/landscape_demo_v5.py/engagement.py wurde geloescht oder umgeschrieben, nur
ergaenzt. Alle bisherigen Notes bleiben gueltig, dies ist nur der Zusatz fuer diese Session.

## Ausloeser

Vier neue, hochwertige 16:9-Hintergrundbilder wurden bereitgestellt (Sternenhimmel,
Sonnenuntergang-Meer, heller Tag-Strand, Milchstrasse-Strand-Nacht), plus der Wunsch nach
weiteren, fuer zukuenftige Videos nuetzlichen Assets.

## Was neu ist

### 1. Vier neue Hintergruende in `assets/Background/`

- `bg sternenhimmel sternschnuppen.png` — Sternenhimmel/Nebelwolken, zwei Sternschnuppen, kein
  Horizont. Passt zu stargazing/nachdenklichen/dramatischen Beats.
- `bg sonnenuntergang meer.png` — Sonnenuntergang ueberm Meer, Horizont mittig.
- `bg strand tag sommer.png` — heller blauer Taghimmel mit Wolken/Moewen. **Der einzige helle
  Tag-Hintergrund im ganzen Set** — bisher waren alle 5 bestehenden Hintergruende dunkel/nachtblau
  getoent (siehe proof_onigiri_v4.py `scene()`: `fr * [.55,.50,.78] * vignette()` dunkelt ohnehin
  ab, das funktioniert mit einem hellen Quellbild trotzdem gut, siehe Testbilder unten).
- `bg milchstrasse strand nacht.png` — Milchstrasse ueber Strand, Sternschnuppe, Kueste rechts.

Alle vier sind wie die bestehenden 5 Hintergruende reine "volles Bild, per `bg_frame()`
zoom+drift"-Assets — KEINE Sprite-Analyse/Katalogisierung noetig (gilt nur fuer Charakter-PNGs,
siehe ENGINE_NOTES.md). Eintraege in `BACKGROUNDS_AND_MUSIC.md` ergaenzt (Regel aus der Datei
befolgt: ein Einzeiler pro Datei, Dateien selbst nicht angesehen/analysiert ausser zur
Kurzbeschreibung — hier zusaetzlich mit `engine.cover()`/`bg_frame()`/`vignette()` durch die
ECHTE Render-Pipeline gerendert und visuell geprueft, siehe Session-Log, nicht nur benannt).
Alle vier laufen unveraendert durch `bgimg()` in proof_onigiri_v4.py/raymi_short.py (gleiches
Glob-Matching-Muster wie bisher) — fuer ein neues Video-Skript einfach den Dateinamen in einem
neuen `BG`-Dict/`bg=`-Feld referenzieren, kein Code-Wechsel noetig.

**Achtung Encoding:** der Dateiname vermeidet bewusst ein "ß" (ASCII `milchstrasse` statt
`milchstraße`) — ein bestehender Hintergrund (`bg rochen groß nahaufnahme.png`) zeigt im
ausgepackten ZIP als `bg rochen gro#U00df nahaufnahme.png` (siehe der `.replace('#U00df', 'ß')`
Workaround in `bgimg()`); neue Dateien mit Sonderzeichen im Namen lieber vermeiden statt den
Workaround jedes Mal zu erweitern.

### 2. `assets_v5.py` (NEU, eigenes Modul, nichts Bestehendes angefasst)

13 neue prozedural gezeichnete Assets, gleiches Prinzip wie assets_v3/v4 (SS-Supersampling,
Ink-Outline, `with_shadow()`-kompatibel, KEIN Font-Glyph-Bedarf — Text kommt wie bei
`scroll()`/`label()` immer vom aufrufenden Szenen-Code via `TX.tile()`):

- **`bell()`** — das in `Raymi-Wissen/04_Asset-Creation-and-QC-Guidelines.md` Abschnitt 1
  explizit als FEHLEND genannte Branding-Asset ("eigener Subscribe-Button/Badge im Raymi-Look").
  Kombiniert mit `assets_v4.plate()` + `TX.tile('SUBSCRIBE')` (exakt das bestehende
  Icon+Plate+Text-Muster aus `label`/`stamp` in raymi_short.py) ergibt das gewuenschte Badge.
- **`heart()`** — Like/Love-Reaktion.
- **`medal(w, col)`** — Rang-Medaille, Farbe per Parameter (`assets_v5.GOLD/SILVER/BRONZE`
  vordefiniert); die Platznummer selbst kommt vom Aufrufer per `TX.tile()`, gleiches Muster wie
  `label`/`stamp`.
- **`trophy()`** — Sieger-/Payoff-Moment.
- **`clock()`** — Uhr/Countdown-/Timer-Beats.
- **`flame()`** — "heisse Meinung"/Hype-Callouts.
- **`meter(w, h, frac, col)`** — Fuellstands-Balken (z.B. "Spice-Level", "Hype-Meter"), Farbe
  faellt automatisch in Gruen/Gold/Rot je nach `frac`, wenn nicht explizit gesetzt.
- **`vs_panel(w, h, col_a, col_b)`** — zweifarbiges Diagonal-Panel mit Blitz-Trenner fuer
  A-vs-B-Vergleichsbeats; Labels kommen wieder vom Aufrufer.
- **`shell()`** — Jakobsmuschel (Scharnier oben, gefaecherte Rippen) — Ozean-Requisit.
- **`starfish()`** — Seestern — Ozean-Requisit.
- **`moon_stars()`** — Mondsichel + Funkeln — Nachthimmel-Sticker, passt thematisch direkt zu den
  drei neuen Nacht-/Dämmerungs-Hintergruenden oben.
- **`comment_icon()`** / **`share_arrow()`** — kleine Badge-Icons als optionale Ergaenzung neben
  `engagement.cta_prompt()`s Sprechblase (die Pille selbst bleibt UNVERAENDERT in `engagement.py`
  — diese beiden sind zusaetzliche, separat platzierbare Sticker, kein Ersatz).

Grund fuer dieses konkrete Set: QC-Punkt 9 in `04_Asset-Creation-and-QC-Guidelines.md`
("Keine Icon-/Prop-Vielfalt... nicht nur ein Standard-Set von 5 Hintergruenden ohne jedes
Zusatz-Asset") war bisher nur mit Essens-Icons (assets_v3/v4) abgedeckt — Ranking-, Vergleichs-,
Countdown- und Ozean-/Nacht-Beats hatten noch KEIN passendes gezeichnetes Asset.

Alle 13 wurden einzeln UND als Sammel-Sheet gerendert und visuell geprueft (`python3
assets_v5.py` schreibt ein Kontroll-Sheet, gleiches Muster wie `assets_v3.py`/`assets_v4.py`
am Dateiende) — keine Platzhalter, alle produktionsfertig.

### 3. Nicht verdrahtet (bewusst, wie bei assets_v4 in v5)

Genau wie `assets_v4.py` beim Erscheinen NICHT sofort in `proof_onigiri_v4.py` nachgetragen
wurde (das Skript war zu dem Zeitpunkt schon ein fertiges Referenz-Video, siehe ENGINE_NOTES.md
"NEUE VIDEOS = Kopie davon"), wird `assets_v5.py` in dieser Session NICHT in die bestehenden
`asset()`-Dispatch-Dicts von `proof_onigiri_v4.py`/`raymi_short.py` eingetragen — beide sind
abgeschlossene Referenz-/Produktions-Skripte fuer bereits existierende Videos, kein neues Video
wurde in dieser Session gebaut (kein Voiceover vorhanden). Fuer das naechste neue Video: einfach
`import assets_v5 as A5` in der Kopie des Referenz-Skripts ergaenzen und die gewuenschten Kinds
im lokalen `asset()`-Dict eintragen (gleiches Muster wie `assets_v4`-Kinds in `raymi_short.py`).

## TODO (uebernommen aus v5/v6/v7, unveraendert offen)

- Config-Loader (JSON) statt Config im Skript
- `fx_whip` als dritte Cut-Art verdrahten
- CTA-Strategie fuer Longform (`landscape_demo_v5.py`)
- Geografie-Report einpflegen, sobald exportiert
- Naechstes neues Short-Skript: die vier neuen Hintergruende + `assets_v5.py`-Icons tatsaechlich
  in einer BEATS-Config verwenden (bisher nur isoliert durch die Render-Pipeline getestet, noch
  in keinem echten Video-Export kombiniert)
