# Raymi — Analytics Insights & Wachstums-Strategie (Stand 2026-09-25)

Quelle: echter YouTube-Studio-Export "Videos_2026-08-28_2026-09-25" (13 Videos,
Zeitraum seit Kanalstart). Dies ist die erste Auswertung mit echten Daten statt
Recherche-Annahmen — ersetzt/ergänzt ab jetzt allgemeine Best-Practice-Guides
überall dort, wo die eigenen Zahlen etwas anderes sagen.

## 0. Kontext-Größe (nicht schönreden)

3722 Aufrufe, 10.2h Wiedergabezeit, 31 Netto-Abos über 4 Wochen, 13 Videos.
Kleiner Kanal, erste Testphase — das ist die Ausgangsbasis für alle
Schlussfolgerungen unten, nicht "was bei großen VTubern funktioniert".

## 1. Video-für-Video-Tabelle (sortiert nach Aufrufen)

| Views | Ø-Wiedergabe % | Bis-Ende % | Neue Abos | Comments | Shares | Titel |
|---|---|---|---|---|---|---|
| 1137 | 74.82 | 40.44 | 11 | 2 | 1 | "why is best friend salmon" (Debut-Short) |
| 1074 | 67.36 | 53.29 | 9 | 1 | 1 | "This VTuber Can Predict Rain (Allegedly)" |
| 1052 | 43.71 | 43.98 | 2 | 3 | 0 | "VTuber Calls Out Everyone Who Eats Rice First" |
| 139 | 35.08 | 30.99 | 3 | 1 | 0 | "New VTuber Ranks Every Ocean Creature" |
| 132 | 68.48 | 36.84 | 0 | 0 | 0 | "There's A Correct Way To Eat Onigiri (Fight Me)" |
| 47 | 24.91 | — | 0 | 1 | 0 | "meet raymi, the stingray vtuber..." (Longform-Intro) |
| 33 | 66.5 | 56.52 | 0 | 0 | 0 | "VTuber Confesses She Betrayed Her Best Friend" |
| 31 | 70.04 | 39.29 | 0 | 0 | 0 | "chat proved i havent had a REAL meal in years" |
| 28 | 71.7 | 70.59 | 0 | 0 | 0 | "This Stingray VTuber Is Done Being Called A Devil" |
| 28 | 75.72 | 23.81 | 0 | 0 | 0 | "VTuber Ranks Ocean Animals (Someone Will Get Mad)" |
| 18 | 72.96 | 43.75 | 0 | 0 | 0 | "Sharks And Rays Are Basically Cousins" |
| 1-2 | — | — | 0 | 0 | 0 | zwei sehr neue Videos, keine belastbaren Daten |

## 2. Die drei größten Erkenntnisse

**2.1 Hook-Typ schlägt Format.** Die zwei stärksten Videos teilen ein Muster:
ein SEHR spezifischer, seltsamer Einzelfakt über Raymi selbst (bester Freund
ist ein Lachs / kann angeblich Regen vorhersagen), nicht ein generisches
Format. "Ranking"-Videos (Ocean-Creature-Ranking, Ocean-Animals-Ranking)
performen über beide Auflagen hinweg am schwächsten (30.99% und 23.81%
Completion, 0-3 neue Abos trotz vergleichbarem Aufwand). Das deckt sich mit
der ursprünglichen vidIQ-Recherche ("einzigartiger Identitäts-Hook schlägt
durch" — siehe Audience-Research-Historie) und wird durch echte Zahlen
bestätigt: **Ranking-Format zurückfahren, mehr Einzelfakt-/Callout-Hooks.**

**2.2 Views ≠ Conversion.** "Rice First"-Callout zog die drittmeisten Views
(1052), aber nur 2 neue Abos und die schwächste Ø-Wiedergabe der drei
Top-Videos (43.71%). Ein reißerischer Titel zieht Klicks, aber wenn der Body
das Versprechen nicht trägt, bleibt kein Zuschauer hängen. Callout-Titel
("X ist falsch") sind ein guter Hook, brauchen aber einen strafferen,
persönlicheren Payoff (siehe 03_Video-Scripting-Guide.md Abschnitt 1) statt
nur eine Meinungsliste.

**2.3 Engagement ist der mit Abstand größte ungenutzte Hebel.** Über ALLE 13
Videos zusammen: nur 8 Kommentare, nur 2 geteilte Inhalte — bei 3722 Views.
Das ist kein Pech, das ist ein fehlendes Feature: kein einziges Video hatte
bisher einen sichtbaren (nicht nur eventuell gesprochenen), konkreten
Kommentar-Prompt. Deshalb ab v6 im Renderer verankert (siehe
`engagement.py`, `ENGINE_NOTES_v6.md`) — ein Pflicht-Beat, kein optionales
Add-on mehr. Die alte Regel "CTA nur wenn organisch" (03_Video-Scripting-
Guide.md) gilt für den Kommentar-Prompt ab jetzt NICHT mehr — die Daten sind
eindeutig genug, um die Ausnahme zu rechtfertigen.

## 3. Hook-Ranking (aus echten Daten, für die nächsten Skripte)

1. **Einzigartiger persönlicher Fakt** (salmon, rain) — höchste Ø-Wiedergabe
   UND höchste Abo-Konversion. Weiter ausbauen.
2. **Callout/"du machst X falsch"** (rice) — starker Klick-Hook, braucht
   aber einen Payoff der wirklich überrascht/unterhält, nicht nur eine
   Meinung wiederholt, sonst bricht die Wiedergabe in der Mitte ab.
3. **Confession/Direct-Address** (betrayed best friend, devil-callout) —
   kleine Stichprobe (n=28-33), aber die BESTEN Completion-Werte im ganzen
   Datensatz (56-70%). Vermutlich unterversorgt mit Reichweite, nicht mit
   Qualität — mehr davon produzieren und beobachten, ob sich das bei
   größerer Stichprobe bestätigt.
4. **Generisches Ranking/Liste** — schwächstes Muster im Datensatz auf allen
   Metriken gleichzeitig. Nicht komplett streichen (Community mag Meinungen),
   aber nicht mehr als Standard-Format nutzen.

## 4. Zielgruppe / Märkte — was die Daten HIER zeigen (und was fehlt)

Dieser Export enthält KEINE Geografie-Aufschlüsselung (nur Datum + Video +
Kennzahlen). Die Aussage "wird momentan hauptsächlich Deutschen gezeigt"
lässt sich mit diesem Datensatz nicht bestätigen oder widerlegen — dafür
fehlt der Report. Für belastbare Zahlen: YouTube Studio → Analytics →
Zielgruppe → Geografie, Zeitraum gleich lassen, als CSV exportieren und
nachreichen — dann lässt sich das hier direkt nachtragen statt zu raten.

Bis dahin, aus der bestehenden vidIQ-Keyword-Recherche (siehe Kanal-Historie,
"Audience-Research"): Suchvolumen für "vtuber" ist global stark JP-dominiert
(~35%), USA folgt mit ~13%, danach Brasilien/Vietnam (~7% je), Indien ~3%.
Raymis Positionierung ist bewusst EN-first — die Empfehlung bleibt, aktiv auf
den US/EN-Markt zu optimieren (Titel/Tags bereits EN, gut), nicht wegen der
aktuellen Zuschauer-Herkunft umzuschwenken. Sobald der Geografie-Report
vorliegt: prüfen, ob Titel/Uhrzeiten/Hashtags zufällig einen DE-lastigen
Algorithmus-Bucket getroffen haben (z. B. durch Upload-Uhrzeit oder erste
Interaktionen aus dem eigenen Umfeld) — das lässt sich beheben (z. B. gezielt
zu US-Prime-Time posten, siehe Abschnitt 5), ist aber Spekulation ohne den
Report.

## 5. Konkrete nächste Schritte (Priorität)

1. **Kommentar-Prompt ist jetzt Pflicht-Beat** (erledigt im Code, v6) — bei
   jedem neuen Short-Config in `raymi_short.py` ein `cta=(frage, sub)`-Paar
   setzen, das zur jeweiligen Story passt (siehe `sushi`/`meal` als Beispiele).
2. **Weniger Ranking-Formate, mehr Einzelfakt-/Confession-Hooks** — siehe
   Abschnitt 3. Nächste 2-3 Skripte gezielt in diese Richtung planen.
3. **Rice-First-Lehre auf zukünftige Callout-Videos anwenden**: Callout-Hook
   behalten, aber Payoff schärfen — der Moment, der überrascht/das Gegenteil
   des Erwarteten liefert, muss klar vor der Hälfte des Videos kommen (siehe
   03_Video-Scripting-Guide.md Abschnitt 2, Setup-Fenster).
4. **Geografie-Report nachreichen**, sobald verfügbar, für eine echte
   Markt-Empfehlung statt einer Hypothese.
5. **Upload-Uhrzeit testen** gegen US-Abend-/EU-Vormittags-Fenster, sobald
   genug Videos für einen Vergleich da sind (aktuell zu wenige Datenpunkte
   für eine verlässliche Aussage, absichtlich nicht erzwungen).

## 6. Ehrliche Realitäts-Einordnung (kein Sugarcoating, wie gewünscht)

31 Netto-Abos in 4 Wochen ist ein normaler, gesunder Start für einen
Ein-Personen-KI-VTuber-Kanal — kein Ausreißer nach oben, kein Alarmsignal.
Die zwei Top-Videos zeigen aber real, dass das Format funktionieren KANN
(74.8% Ø-Wiedergabe ist stark), das Problem ist aktuell Konsistenz + fehlendes
Engagement-Feature, nicht die Grundidee. Realistisches nächstes Ziel: erst
mal ein Video wiederholen, das über die organische Reichweite hinaus vom
Algorithmus selbst weitergetragen wird (kein einziges der 13 Videos hat das
bisher eindeutig getan) — das ist der nächste echte Meilenstein, nicht eine
konkrete Abonnenten-Zahl.
