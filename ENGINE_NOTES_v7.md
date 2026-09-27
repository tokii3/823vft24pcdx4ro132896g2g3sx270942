# Raymi Engine v7 — was ist neu (Addendum zu ENGINE_NOTES.md / _v5 / _v6)

REGEL gilt weiter: nichts an engine.py/assets_v3.py/assets_v4.py/proof_onigiri_v4.py/
raymi_short.py/landscape_demo_v5.py wurde geloescht oder umgeschrieben, nur ergaenzt.
Alle bisherigen Notes bleiben gueltig, dies ist nur der Zusatz fuer diese Session.

## Ausloeser

Feedback: die Audio-Timing-JSON aus `tts/generate_audio.py` (`*_words.json`) kommt beim
Uebergeben an eine neue Session nie mit an — nur mp3 + eine Text-Kopie. Klingt nach
fehlendem Feature, ist aber keins: **`_words.json` wird im gesamten Render-Code (engine.py,
raymi_short.py, proof_onigiri_v4.py) nirgends gelesen** (nachgeprueft per grep). Sie war
immer nur ein in den Notes vermerktes TODO fuer spaeter, nie eine tatsaechliche
Abhaengigkeit. `raymi_short.py align()` arbeitet schon seit v4 ausschliesslich mit mp3 + txt
(Pausenerkennung per `ffmpeg silencedetect`, Wort-Timing pro Satz per Silben-Heuristik aus
`engine.word_times()`).

Der eigentliche Grund, warum Audio bisher trotzdem oft von Hand nachanalysiert wurde: die
alte `_compute_align()` hatte einen harten `assert len(ends) == len(sents)` — Anzahl der per
Pausenerkennung gefundenen Stille-Luecken musste EXAKT zur Satzanzahl (Split an `.!?`)
passen. Passte das nicht (Komma-Pause erkannt, zwei Saetze ohne ausreichende Pause
dazwischen, eine "..."-Pause zaehlt als extra Luecke, ...), ist das Skript hart gecrasht —
kein Fallback, also musste die mp3 manuell abgehoert/getimet werden.

## Was neu ist (nur `raymi_short.py`, additiv)

1. **Schwellenwert-Grid statt fixem `-35dB/0.28s`.** `_pause_based_align()` probiert eine
   kleine Reihe von `(noise_db, dur_s)`-Kombinationen durch und nimmt die erste, deren
   Stille-Anzahl zur Satzanzahl passt — erhoeht die Chance, ueberhaupt auf dem echten
   Pausen-Pfad zu landen (bester Fall: exakt geschnittenes, luecken-gestrafftes Audio wie
   bisher).
2. **Proportionaler Fallback (`_proportional_align()`), wenn KEINE Kombination passt.**
   Verteilt die volle, unangetastete Audiospur anteilig nach Silben-Gewicht pro Satz (gleiche
   Gewichtung, die `word_times()` schon eine Ebene tiefer fuer Woerter-in-einem-Satz nutzt).
   Kein Luecken-Straffen (weil keine echten Pausen-Positionen bekannt sind), aber die Spur
   wird garantiert vollstaendig verwendet und das Skript **bricht nie mehr ab**.
3. **Sichtbar, welcher Modus lief.** `align.json` traegt jetzt `"estimated": true/false`.
   `false` = echter Pausen-Schnitt (bevorzugt), `true` = proportionaler Fallback. Damit ist
   auf einen Blick klar, welche Qualitaetsstufe ein Take bekommen hat, ohne die Audiodatei
   nochmal anzuhoeren.
4. **Verstaendlicher Fehler statt nacktem `AssertionError`**, falls die `n`-Werte in
   `CFG[...]['beats']` nicht zur tatsaechlichen Satzanzahl summieren — die Meldung listet
   jetzt alle erkannten Saetze mit Index auf, damit sich die Config direkt korrigieren laesst
   statt erst selbst nachzaehlen zu muessen.

Alle vier Punkte wurden isoliert getestet (synthetisches Audio mit echten Pausen: Treffer-
Fall UND Mismatch-Fall geprueft; proportionaler Fallback deckt die volle Dauer ab und
verteilt plausibel nach Satzlaenge/Silbenzahl) — siehe Session-Log, kein echtes Voiceover
noetig fuer diesen Test.

## Was das NICHT aendert

- `tts/generate_audio.py` bleibt wie es ist (produziert weiterhin optional eine
  `_words.json`, falls sie doch mal gebraucht wird) — sie ist jetzt nur explizit als
  **optional, nicht benoetigt** markiert statt als offenes TODO. Falls das lokale
  edge-tts-Problem (Wort-Boundary-Daten kommen nicht zurueck) je gefixt wird, aendert das
  nichts am Renderer — er braucht sie so oder so nicht.
- `proof_onigiri_v4.py` bleibt unveraendert (nutzt sein eigenes festes `BEATS`-Timing, kein
  `align()`-Aufruf, war von diesem Problem nie betroffen).
- Bisheriges Audio-Alignment-Cache-Format (`align_<short>_<key>.npy`/`.json` in `.cache/`)
  wird durch den neuen `"estimated"`-Schluessel im JSON minimal erweitert, aber
  abwaertskompatibel gelesen (`payload.get('estimated', False)`), alte Cache-Dateien ohne
  dieses Feld werden weiterhin als "nicht geschaetzt" interpretiert und einfach neu erzeugt,
  falls der Cache-Key sich ohnehin schon durch die Code-Aenderung aendert.

## TODO — aktualisiert

- ~~Exakte Wortzeiten aus `_words.json` statt geschaetzt~~ — bewusst NICHT mehr angestrebt,
  siehe oben (Praeferenz: robuster Pausen-/Silben-Ansatz ohne externe Abhaengigkeit).
- Aus v5/v6 weiterhin offen: Config-Loader (JSON) statt Config im Skript, `fx_whip` als dritte
  Cut-Art verdrahten, CTA-Strategie fuer Longform, Geografie-Report einpflegen.
- Naechster sinnvoller Schritt laut Nutzer-Feedback (separates Thema, noch nicht umgesetzt):
  ein Auto-Beat-Builder, der aus Rohtext + Sentence-Timing automatisch einen CFG-Entwurf
  (Beats/Sprite-Vorschlaege/Emphase-Woerter) generiert, plus Stimmungs-Tags im
  `sprite_catalog.json` dafuer — separates groesseres Vorhaben, hier nicht mit angefasst.
