# Raymi Engine v6 — was ist neu (Addendum zu ENGINE_NOTES.md / ENGINE_NOTES_v5.md)

REGEL gilt weiter: nichts an engine.py/assets_v3.py/assets_v4.py/
proof_onigiri_v4.py/raymi_short.py/landscape_demo_v5.py wurde geloescht oder
umgeschrieben, nur ergaenzt. ENGINE_NOTES.md und ENGINE_NOTES_v5.md bleiben
unveraendert gueltig, dies hier ist der Zusatz fuer diese Session.

## Ausloeser: echte YouTube-Analytics statt nur Recherche

Diesmal kein allgemeiner "Best Practices 2026"-Guide, sondern ein echter
Studio-Export (13 Videos, 3722 Views, 4 Wochen) als Grundlage. Volle
Auswertung: `Raymi-Wissen/06_Analytics-Insights.md` (NEU). Kernbefund, der
diese Version treibt: ueber alle 13 Videos zusammen nur 8 Kommentare und 2
geteilte Inhalte — der Renderer hatte bisher schlicht kein eingebautes
Feature dafuer, nur die Hoffnung, dass ein Skript "organisch" danach fragt.

## Was neu ist

1. **`engagement.py` (NEU, eigenes Modul, nichts Bestehendes angefasst).**
   `cta_prompt()` zeichnet eine animierte Sprechblase (prozedural, cv2,
   Raymis UV-Palette, KEIN Font-Fallback — nutzt den bestehenden `Text`-Cache
   wie Captions) mit einer konkreten, leicht kontroversen Frage plus
   optionaler zweiter Zeile ("comment below"-artig, aber in Raymis Stimme
   geschrieben statt generisch). `loop_reply_hint()` ist ein optionaler,
   sehr dezenter Ein-Zeiler fuer die letzten Frames vor dem `loop_seam()`.
2. **Verdrahtet, nicht nur dokumentiert:**
   - `proof_onigiri_v4.py`: ein CTA-Aufruf am Ende von `_core_frame()`
     (Text hart passend zum Onigiri-Thema), zeitlich klar vor dem
     `loop_seam()`-Blend-Fenster platziert.
   - `raymi_short.py`: config-getrieben — jedes `CFG[...]` bekommt optional
     ein `cta=(frage, sub)`-Paar (siehe `sushi`/`meal` als Beispiele), generisch
     in `_core_frame()` ausgelesen und gezeichnet. Fuer jeden neuen Short in
     Zukunft einfach dieses Paar in der Config ergaenzen — kein Zusatzcode noetig.
   - Nicht in `landscape_demo_v5.py` verdrahtet (Longform braucht eine andere
     CTA-Logik, z. B. gesprochen + Endcard statt Pill-Overlay mitten im
     Video — siehe TODO unten, bewusst nicht geraten/erzwungen).
3. **`Raymi-Wissen/06_Analytics-Insights.md` (NEU)** — die vollstaendige
   Datenauswertung: Video-fuer-Video-Tabelle, Hook-Ranking aus echten Zahlen,
   Engagement-Befund, Markt-/Geografie-Luecke (dieser Export hat KEINE
   Geografie-Daten — Empfehlung: Studio → Analytics → Zielgruppe → Geografie
   separat exportieren, dann nachtragen statt zu raten), naechste Schritte.
4. **`03_Video-Scripting-Guide.md`** — neuer Abschnitt 7: der Kommentar-Prompt
   ist ab jetzt PFLICHT-Beat (Ausnahme von der alten "CTA nur wenn organisch"-
   Regel, explizit datenbasiert begruendet, siehe 06_Analytics-Insights.md
   Abschnitt 2.3), plus das Hook-Ranking aus Abschnitt 3 dort verlinkt.
5. **`04_Asset-Creation-and-QC-Guidelines.md`** — QC-Checkliste um einen
   Punkt ergaenzt: sichtbarer Kommentar-Prompt vor Export pruefen.

## Was NICHT gemacht wurde (bewusst, keine Vermutung als Fakt verkauft)

- Kein neues Video gerendert/exportiert in dieser Session — die CTA-Verdrahtung
  in `proof_onigiri_v4.py`/`raymi_short.py` ist Code-seitig korrekt (gleiche
  `blit()`/`Text`-Pfade wie ueberall sonst, `u<0 or u>dur`-Guard in
  `cta_prompt()` verhindert falsches Rendern ausserhalb des Fensters), aber
  NICHT dieses Mal wie in v5 an 5 Zeitpunkten visuell nachgerendert/geprueft
  (kein Voiceover/keine Assets dieser konkreten Videos in dieser Session
  hochgeladen). Vor dem naechsten echten Export einmal `stills` an der
  CTA-Zeitmarke pruefen (z. B. `py proof_onigiri_v4.py stills 9.0` /
  `py raymi_short.py sushi stills <t>`).
- Keine Geografie-/Markt-Aussage ueber die tatsaechliche Zuschauerherkunft
  getroffen (Datengrundlage fehlt, siehe oben) — nur die bestehende
  Keyword-Recherche als Hypothese weitergefuehrt, klar als solche markiert.
- `fx_whip` (aus v5, geschrieben aber ungenutzt) weiterhin nicht in ein
  TRANS-Preset verdrahtet — unveraendert offen, siehe TODO.

## TODO (uebernommen aus v5 + neu)
- Config-Loader (JSON) statt Config im Skript
- Exakte Wortzeiten aus `_words.json` statt geschaetzt
- `fx_whip` als dritte Cut-Art verdrahten
- CTA-Strategie fuer Longform (`landscape_demo_v5.py`) separat entwerfen
  (gesprochen + Endcard statt Pill-Overlay)
- Geografie-Report einpflegen, sobald exportiert (siehe 06_Analytics-Insights.md)
- Naechster echter Export: pruefen ob der CTA-Beat tatsaechlich mehr
  Kommentare/Shares bringt (aktuell reine Hypothese aus der Datenanalyse,
  noch nicht an echten Zahlen validiert — das kann erst NACH ein paar mit
  v6 produzierten Videos passieren)
