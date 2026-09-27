# Raymi — Asset-Erstellung & Qualitätssicherung

Ergänzt ENGINE_NOTES.md um Anforderungen an NEUE Assets/Szenen-Code und
eine Checkliste gegen die Qualitätsregression, die in mehreren Sessions
aufgetreten ist. Gilt für alles, was in/für den Renderer entsteht
(gezeichnete Icons, Badges, Overlays, neuer Szenen-Code) — nicht für die
PixAI-Charakterbilder selbst (die bleiben Bildgenerierung, nicht Teil
dieses Dokuments).

## 1. Branding-Pflicht für jedes Text-/UI-Asset

- JEDER Text auf einem Asset (Untertitel, Titel-Stempel, Buttons, Badges,
  Call-outs) MUSS über Raymis Font (Raymi-Regular.ttf) laufen — nie über
  einen Default-/Fallback-Font. Kein "#"-Glyph in dieser Font vorhanden,
  Apostroph nur in Großschreibung testen.
- Markenfarben verwenden statt generischer Platzhalterfarben: Ultraviolett
  (siehe engine.py `UV`/`UVL`), nicht z.B. hartkodiertes Gelb als
  "irgendein Highlight". Jede neue Farbe im Code muss sich bewusst auf
  Raymis Palette beziehen, nicht zufällig gewählt sein.
- Beispiel für ein noch fehlendes, aber gewünschtes Branding-Asset: ein
  eigener "Subscribe"-Button/Badge im Raymi-Look (Font + UV-Farbpalette,
  gleiches Muster wie die vorhandenen `badge()`/`with_shadow()`-Funktionen
  in assets_v3.py) statt eines generischen Plattform-Icons. Neue
  CTA-/Branding-Assets sollten nach demselben Muster prozedural gezeichnet
  werden (kein Font-Glyph-Bedarf, skaliert sauber, Schatten via
  `with_shadow()`).
  **(v8: erledigt)** `assets_v5.bell()` liefert das Icon dafür — kombiniert
  mit `assets_v4.plate()` + `TX.tile('SUBSCRIBE')` ergibt das komplette
  Badge, siehe ENGINE_NOTES_v8.md.

## 2. Asset-Qualität — was bereits mehrfach schiefging (nicht wiederholen)

Aus konkreten Regressions-Fällen destilliert:

1. **Font fällt auf Default zurück.** Passiert immer dann, wenn ein
   Text-Tile ohne explizites `font=`/über den etablierten Text-Helper
   erzeugt wird. Jeder neue Szenen-Code muss die bestehende `Text`-Klasse
   aus engine.py nutzen, nie eine eigene Text-Rendering-Funktion
   erfinden.
2. **Kopf wird abgeschnitten.** Kein Headroom-Clamping bei Zoom/Breathe/
   Bounce-Multiplikatoren — bei höherem Multiplikator wandert der Kopf
   der Figur aus dem Bild. Beim Platzieren von Sprites (`blit()`) immer
   gegen den oberen Bildrand prüfen, gerade bei `hero`/`xcu`-Modus.
3. **Wort-Hervorhebung "bounct" wahllos.** Bounce-/Pop-Effekte gehören NUR
   auf tatsächlich als `emph` markierte Wörter, nicht auf jedes Wort im
   Beat — sonst wirkt jede Silbe gleich wichtig.
4. **Glow/Sparkle-Overkill.** Additive Glow-Blobs mit zu großer
   Fläche/zu hohem Alpha wirken schnell wie überbelichtete weiße
   Bokeh-Kreise statt wie gezielte Akzente. Glow sparsam und an konkrete
   Momente (Emphase-Pop, Asset-Einblendung) gebunden einsetzen, nicht
   dauerhaft.
5. **Doppelte Hervorhebung.** Ein Wort sollte nicht gleichzeitig als
   laufender Karaoke-Untertitel UND als eigener Stempel-Titel (pop_title)
   auftauchen — wirkt redundant/zufällig.
6. **Statische Beats.** Jeder Beat braucht mindestens eine leichte
   Idle-Animation (sanftes Neigen/Atmen), sonst wirkt die Figur wie ein
   eingefrorenes PNG. Kein Beat sollte komplett bewegungslos sein.
7. **Fehlende Übergänge.** Zwischen Beats gehören definierte Transitions
   (z.B. punch/slide/whip, siehe engine.py `fx_zoom`/`fx_glitch`/
   `fx_shake`), kein harter Beat-Wechsel ohne jede Bewegung.
8. **Neu erfundene Render-Module statt bestehender Engine.** Der mit
   Abstand größte Regressions-Grund bisher: ein komplett neues Modul-Set
   wird von Grund auf geschrieben (ohne Import der bestehenden Engine),
   wodurch Karaoke-Captions, Auto-Fit, Icons und Transitions alle wieder
   neu (und schlechter) implementiert werden müssen. Regel: JEDE neue
   Szene MUSS `engine.py`/`assets_v3.py` importieren und erweitern, nie
   parallel eine eigene Engine schreiben. Kommentare im Code sollten auf
   die tatsächlich aktuell genutzten Dateien verweisen, nicht auf
   veraltete/verschobene Referenzen.
9. **Keine Icon-/Prop-Vielfalt.** Für Tier-List-, Vergleichs- oder
   Ranking-Beats müssen passende prozedurale Icons existieren (wie die
   Icon-Generatoren in assets_v3.py: Onigiri, Badge, Gavel, Scroll,
   Starburst, Sparkle) — nicht nur ein Standard-Set von 5 statischen
   Hintergründen ohne jedes Zusatz-Asset.
10. **Immer dieselbe Vorlage.** Assets/Layout sollten sich pro Video
    unterscheiden (andere Icon-Kombination, andere Hintergrund-/Musik-
    Auswahl aus BACKGROUNDS_AND_MUSIC.md, andere Übergangsarten), sonst
    wirkt jedes Video wie eine reine Textänderung derselben Vorlage.

## 3. QC-Checkliste vor Fertigstellung eines Videos

- [ ] Alle Text-Assets nutzen Raymi-Regular.ttf (Stichprobe: Standbild
      extrahieren und Font optisch prüfen, wenn unsicher)
- [ ] Kein Kopf/keine tako ears am Bildrand abgeschnitten
- [ ] Hervorhebung (Bounce/Pop/Glow) nur auf `emph`-Wörtern
- [ ] Kein Wort gleichzeitig als Caption UND als Pop-Title hervorgehoben
- [ ] Jeder Beat hat Idle-Bewegung UND mindestens einen visuellen Reset
      (Hintergrundwechsel, Kamerabewegung oder Übergang)
- [ ] Passende prozedurale Icons/Assets für den Beat-Inhalt vorhanden
      (nicht nur Sprite + Hintergrund ohne jedes Zusatzelement)
- [ ] Kein neu erfundenes Render-Modul — Code importiert nachweislich
      engine.py/assets_v3.py
- [ ] Ausdruck wechselt bei jeder inhaltlich wichtigen Zeile, keine zwei
      gleichen Ausdrücke in Folge (außer bewusster Callback)
- [ ] Video unterscheidet sich in Icon-Auswahl/Hintergrund/Musik sichtbar
      von den vorherigen Videos
- [ ] Gesamtansicht (nicht nur Einzelframes) angesehen, bevor es als
      fertig gilt — Audio-Mix/Gesamteindruck sieht man an Standbildern
      ohnehin nicht
- [ ] v6: sichtbarer Kommentar-Prompt (`engagement.cta_prompt`, ueber
      `cta=(...)` in der Short-Config) ist gesetzt und thematisch passend
      formuliert, nicht generisch — siehe 06_Analytics-Insights.md

## 4. Neue Asset-Typen anlegen

Beim Hinzufügen eines neuen PNG-Batches: `catalog_tool.py` auf den Ordner
laufen lassen (siehe ENGINE_NOTES.md) statt PNGs einzeln per Bildanalyse
zu katalogisieren — spart Vision-Tokens und ist an 106 bestehenden
Einträgen mit 0 Fehlklassifikationen validiert. Neue Hintergründe/Musik
werden nur als Ein-Zeiler in BACKGROUNDS_AND_MUSIC.md ergänzt, nicht
einzeln analysiert.
