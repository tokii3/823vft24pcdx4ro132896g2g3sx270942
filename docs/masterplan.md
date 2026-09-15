# Raymi – Masterplan für den KI-VTuber

Status: Phase 0 läuft (Drive-Struktur steht)
Letztes Update: 15.09.2026

## 0. TL;DR

Raymi soll ein vollautomatischer KI-VTuber werden (Mantarochen-Design, blau/lila, süß, tsundere-artig), der eigenständig Content produziert, postet, mit der Community interagiert und daraus lernt. Das ist technisch machbar – aber es sind **mehrere Plattform-Richtlinien und rechtliche Fallstricke** zu beachten, die den Erfolg (Monetarisierung, Kanal-Überleben) direkt beeinflussen. Deshalb zuerst die Risiken, dann die Architektur, dann die Roadmap.

---

## 1. Rechtliche & Plattform-Risiken (zuerst lesen)

Das hier ist der wichtigste Abschnitt. Wenn das ignoriert wird, kann der Kanal trotz guter Technik abgestraft oder gesperrt werden.

### 1.1 YouTube "Inauthentic Content" Policy (seit Juli 2025 verschärft)
- YouTube hat die frühere "repetitious content"-Regel zu **"Inauthentic Content"** umbenannt und geht seit 2025/2026 gezielt gegen massenproduzierte, generische KI-Videos ("AI slop") vor.
- Sanktionsstufen: Verwarnung → 90 Tage Ausschluss aus dem Partnerprogramm → permanenter Ausschluss.
- **Was das für Raymi heißt:** Vollautomatische Massenproduktion ist erlaubt, solange der Content **originell, konsistent und einen eigenen Mehrwert/eigene Stimme** hat (Raymi als durchgehender Charakter mit eigener Persönlichkeit ist hier ein Vorteil, austauschbare 08/15-Faceless-Slideshows wären das Risiko).
- Konsequenz für die Architektur: Qualitätskontrolle/Review-Schritt einbauen, bevor etwas hochgeladen wird – kein "generiere 50 Videos die Nacht und lade alle blind hoch".

### 1.2 "Altered or Synthetic Content"-Label
- Pflicht-Label gilt für Inhalte, die ein Betrachter realistisch für echt halten könnte (Deepfakes, realistische Ereignisse/Personen).
- Raymi ist ein erkennbar gezeichneter/animierter Fantasie-Charakter (Mantarochen) → fällt **nicht** unter die Realismus-Schwelle, die das Label erzwingt.
- Trotzdem meine Empfehlung: freiwillig in der Videobeschreibung erwähnen, dass Raymi eine KI-Figur ist ("KI-VTuber", "virtuelle Persönlichkeit"). Das ist in der VTuber-Szene ohnehin üblich, schafft Vertrauen und schützt zusätzlich vor zukünftigen Regelverschärfungen.

### 1.3 YouTube Partnerprogramm / Monetarisierung
- Voraussetzung: 1.000 Abonnenten + (4.000 Std. Wiedergabezeit ODER 10 Mio. Shorts-Views in 90 Tagen).
- Reine KI-Stimme + reine KI-Bilder sind laut aktueller Policy **nicht automatisch ausgeschlossen** – entscheidend ist "original value", nicht die Herkunft der Assets.
- Konsequenz: Von Anfang an auf Wiedererkennbarkeit/eigene Persönlichkeit statt 08/15-Content setzen (passt gut zu deinem Ansatz, Raymi wachsen zu lassen statt generisch zu bleiben).

### 1.4 Automatisierte Kommentar-Antworten
- YouTube's ToS verbietet "spammy/deceptive automated engagement". Das Risiko besteht vor allem bei **generischen, botartigen** Massenantworten.
- Individuelle, charakter-konsistente Antworten (im Raymi-Stil, kontextbezogen) sind deutlich unkritischer als Copy-Paste-Antworten – aber ein Rate-Limit (z. B. max. X Antworten/Stunde, nicht auf jeden Kommentar) und eine Erkennung von Spam/Hass-Kommentaren (nicht antworten/blockieren) sind Pflicht.
- **Prompt-Injection-Risiko:** Kommentare sind von außen kontrollierbarer Input. Jemand könnte in einem Kommentar versuchen, Raymi Anweisungen zu geben ("ignoriere deine Regeln und sag X"). Das System muss Kommentare strikt als "zu lesende Daten", nie als Instruktionen behandeln – separate, gehärtete Prompt-Struktur nötig.

### 1.5 PixAI-Anbindung – wichtiger Fakt
- PixAI hat **keine offizielle öffentliche API**. Was online existiert, sind ausschließlich inoffizielle/reverse-engineerte Wrapper (z. B. `pixaiAPI` auf PyPI), die den internen Web-Token nutzen.
- Risiken: jederzeitiger Bruch bei PixAI-Updates, potenzieller Verstoß gegen PixAI-ToS (Automatisierung ohne offizielle Freigabe → Account-Sperre möglich), keine Support-Garantie.
- **Meine Einschätzung:** Für den Start nutzbar (du hast ja schon Credits & Erfahrung dort), aber nicht als einzige Bildquelle einplanen. Ich würde einen Fallback/Alternative offen halten (z. B. ComfyUI lokal mit denselben/ähnlichen Modellen, falls PixAI-Wrapper mal bricht). Das bespreche ich unten in der Architektur.

### 1.6 Voice Cloning / Custom AI Voice
- Wenn die Stimme komplett neu synthetisiert wird (kein Cloning einer echten Person), ist das rechtlich unkritisch.
- Falls du vorhast, eine Stimme nach einer echten Person/Seiyuu zu modellieren – **nicht tun**, das ist ein Rechte- und Ethikproblem. Meine Annahme: komplett neue, für Raymi einzigartige Stimme (bitte bestätigen).

### 1.7 Datenschutz beim "Nutzer merken"
- Das Speichern von Infos über einzelne YouTube-Nutzer (Namen, Vorlieben, Interaktionshistorie) ist personenbezogene Datenverarbeitung → DSGVO-relevant, sobald reale Personen (auch nur mit Kanalnamen) betroffen sind.
- Praktisch für ein Hobby-/Wachstumsprojekt: nicht direkt existenzbedrohend, aber sauber lösbar: nur öffentlich ohnehin sichtbare Infos speichern (Kanalname + öffentliche Kommentare + Anzahl Interaktionen), keine sensiblen Daten, und eine einfache Löschfunktion einbauen, falls jemand das verlangt. Das nehme ich als Best-Practice-Baseline in die Architektur, nicht als Blocker.

### 1.8 "Made for Kids" Falle
- Ein niedlicher, family-friendly Charakter kann von YouTube automatisch als "an Kinder gerichtet" eingestuft werden. Das schaltet personalisierte Werbung, Kommentare und Community-Posts **ab** – also genau die Features, die du für Raymi willst (Kommentare lesen/beantworten, Community-Tab).
- Konsequenz: Familienfreundlich ≠ "für Kinder gemacht" markieren. Positionierung/Beschreibung/Tags bewusst auf "allgemeines Publikum, VTuber-Entertainment" statt "Kinderinhalt" ausrichten, damit die Kernfunktionen nicht wegfallen.

---

## 2. Architektur-Überblick

### 2.1 Grundprinzip: Master-Agent + Sub-Agenten (wie schon bei deinem generellen Automatisierungs-Projekt angedacht)

```
                    ┌─────────────────────┐
                    │   MASTER-AGENT      │
                    │ (Orchestrierung,     │
                    │  Persönlichkeit,     │
                    │  Entscheidungen)     │
                    └──────────┬──────────┘
        ┌───────────┬──────────┼──────────┬────────────┐
        ▼           ▼          ▼          ▼            ▼
   Content-Agent  Visual-Agent Voice-   Publish-    Community-Agent
   (Ideen/Skript) (PixAI/     Agent    Agent       (Kommentare,
                   Video)    (TTS)     (Upload,    Analytics,
                                        Cross-Post) Gedächtnis)
```

- **Master-Agent**: hält die Persönlichkeit (System-Prompt + Gedächtnis), entscheidet was als Nächstes produziert wird, reviewt Ergebnisse der Sub-Agenten vor Veröffentlichung (Qualitäts-Gate gegen 1.1).
- **Content-Agent**: generiert Ideen, Skripte, Captions, Titel – per Gemini API (oder Claude, falls Budget vorhanden) statt Ollama, da du jetzt Gemini-Zugang hast. Meine Empfehlung: Gemini für die laufenden, häufigen Textaufgaben (günstig/schnell), Claude für die seltenen, wichtigen Entscheidungen (Persönlichkeits-Feinschliff, Wochenplanung) – spart Kosten, behält Qualität wo's zählt.
- **Visual-Agent**: PixAI-Anbindung (inoffizieller Wrapper) + Fallback-Pfad.
- **Voice-Agent**: TTS via Piper (CPU/Actions-tauglich, kostenlos), Coqui XTTS-v2 als Qualitäts-Fallback über Colab/HF Spaces – siehe 5.1.
- **Publish-Agent**: YouTube Data API v3 (Upload, Shorts, Community-Post), plus Cross-Posting auf weitere Gratis-Plattformen.
- **Community-Agent**: liest Kommentare, filtert Spam/Hass, priorisiert Antworten, schreibt ins Gedächtnis (Running-Gags, wiederkehrende Nutzer, beliebte Themen), speist Analytics zurück in den Master-Agenten.

### 2.2 Gedächtnis/Persönlichkeits-System
- Eine einfache, strukturierte Datenbank (z. B. SQLite oder ein JSON/Markdown-Store in Google Drive) mit:
  - **Charakter-Kern** (fix): Name, Design, Grundzüge (süß, naiv, freundlich, leicht tsundere) – das änderst du bewusst, nicht das System selbst.
  - **Gelernte Vorlieben** (wachsend): Interessen über Mantarochen-Basis hinaus, entstanden durch Feedback/Interaktion.
  - **Running Gags / Memes**: Liste mit Kontext, wann/wie entstanden, wie oft genutzt.
  - **Nutzer-Gedächtnis**: Kanalname, erste Interaktion, Anzahl Interaktionen, ggf. Spitzname von Raymi vergeben – bewusst schlank halten (siehe Datenschutz oben).
- Der Master-Agent liest daraus bei jeder Content-Erstellung einen "Persönlichkeits-Kontext" und baut ihn ins Prompt ein, damit Raymi konsistent bleibt, aber langsam wächst.
- Wichtig: **Charakter-Kern niemals durch externen Input (Kommentare) veränderbar machen** – nur "gelernte Vorlieben" dürfen sich durch Interaktion entwickeln, und auch das nur mit Schwellenwert (z. B. ein Thema muss mehrfach positiv vorkommen, nicht ein einzelner Kommentar reicht).

### 2.3 Sicherheits-Schicht (übergreifend)
- Alle API-Keys ausschließlich als GitHub Actions Secrets / Umgebungsvariablen, nie im Code.
- Kommentar-Input geht **nie direkt** in denselben Prompt-Kontext wie die System-Instruktionen (Prompt-Injection-Schutz, siehe 1.4).
- Vor jedem Post: automatischer Content-Filter-Check (Gemini/Claude als "Moderator-Pass": ist das Ergebnis wirklich family-friendly, on-brand, keine ungewollten Artefakte?).
- Rate-Limits pro Plattform einhalten (YouTube Data API hat ein tägliches Quota – Upload/Kommentar-Calls sind "teuer", das muss im Scheduler eingeplant werden).
- Backup: Gedächtnis-DB + generierte Assets regelmäßig nach Google Drive sichern.

---

## 3. Content-Pipeline im Detail

1. **Themenfindung** – Content-Agent schlägt Ideen vor (inspiriert von: Mantarochen-Fakten/Interessen, Trends, Kommentar-Wünsche, Analyse anderer VTuber-Kanäle).
2. **Skript/Caption** – Text im Raymi-Stil (sobald du mir die Redewendungen/den genauen Ton gibst, wird das ins System-Prompt eingebaut).
3. **Visual-Erstellung** – PixAI-Workflow (Node-basiert, wie du es schon kennst) wird per Wrapper angestoßen, Ergebnis landet in Drive.
4. **Voice** – Skript → TTS (Optionsvergleich unten, deine Entscheidung nötig).
5. **Schnitt/Compositing** – automatisiertes Video-Assembly (z. B. mit FFmpeg/MoviePy: Bilder + Voice + einfache Animation/Untertitel zusammensetzen).
6. **Qualitäts-Gate** – Master-Agent prüft: on-brand? family-friendly? technische Fehler (abgeschnittener Ton, falsches Seitenverhältnis)?
7. **Upload** – YouTube (+ Cross-Post auf weitere Plattformen).
8. **Community-Loop** – Kommentare lesen, sinnvoll beantworten, Analytics ziehen, Gedächtnis aktualisieren.
9. **Reflexion** – wöchentlich/monatlich: was performte gut, was schlecht, Persönlichkeit/Themenwahl leicht anpassen.

---

## 4. Plattform-Strategie

| Plattform | Eignung für Raymi | Aufwand Cross-Post |
|---|---|---|
| YouTube (Shorts + Long-form + Community) | Kernplattform, alle gewünschten Features vorhanden | Basis – hier bauen wir zuerst |
| TikTok | Sehr gut für Shorts-Reichweite, kostenlos | Gering, gleiches Videoformat wiederverwendbar |
| Instagram Reels | Gute Ergänzung, kostenlos | Gering |
| X/Twitter | API seit 2026 kostenpflichtig (aus deinem anderen Projekt bekannt) | Eher später/optional |
| Bluesky/Threads | Kostenlos, wachsende Community, niedrige Priorität aber leicht anzubinden | Gering |

Meine Empfehlung: **Erst YouTube alleine bis die Pipeline stabil läuft**, danach TikTok + Instagram Reels als Cross-Post (gleiches Videomaterial, minimal angepasst), das ist der beste Aufwand/Reichweite-Hebel für "gratis".

---

## 5. Entscheidungen (Stand 15.09.2026)

### 5.1 Getroffen

1. **TTS/Voice**: Start mit **Piper** (läuft zuverlässig CPU-only in GitHub Actions, schnell, kostenlos). **Coqui XTTS-v2** als Qualitäts-Alternative über Colab/Hugging-Face-Spaces-Trigger (Free Tier), Ergebnis nach Drive. Offener Praxis-Test in Phase 0/1: passt eine Piper-Stimme klanglich zur süßen Tsundere-Mantarochen-Persönlichkeit, oder ist sie zu neutral/robotisch? Ergebnis entscheidet, ob wir früher auf XTTS wechseln.
2. **PixAI-Fallback**: wird direkt mitgeplant (Bauplan für ComfyUI-Alternative als Absicherung), aber **nicht** in Phase-0-Umsetzung gebaut, um den MVP nicht zu verzögern.
3. **Content-Freigabe-Loop**: Content-Agent plant die Woche im Voraus → Master-Agent legt dir den Plan vor → du gibst frei → Produktion + Upload läuft danach automatisch. Kommentar-Antworten laufen separat und sofort (mit Injection-Check, siehe 5.1 Punkt 4).
4. **Kommentar-Check gegen Hijacking**: zweistufig – (a) günstiger Regex-/Keyword-Vorfilter gegen offensichtliche Injection-Versuche, (b) Gemini-Call, der den Kommentar ausschließlich als zu lesende Daten bekommt (nie im selben Kontext wie der System-Prompt) mit der reinen Aufgabe "legitime Reaktion oder Manipulationsversuch?". Nur bei "legitim" geht's in die eigentliche Antwort-Generierung.
5. **Accounts**: YouTube-Kanal + Google Cloud/OAuth, GitHub-Repo legst du an; Meldung an mich, sobald vorhanden, dann folgt die API-Anbindung.

### 5.2 Weiterhin offen (keine Einzelnachfrage, wird gesammelt)

1. **Redestil/Persönlichkeit im Detail** – kommt von dir, System-Prompt wird final gebaut, sobald Redewendungen/Ton feststehen.
2. **Design-Reference-Sheet für PixAI** – machst du selbst (Angebot zur Unterstützung steht, falls gewünscht).
3. **Exakter Livestream-Zeitpunkt** – bewusst spät, Teil von Phase 5.

---

## 6. Roadmap / Phasen

**Phase 0 – Setup (keine Inhalte, nur Fundament)**
- [x] Google-Drive-Projektordner angelegt, Struktur für Dokumentation/Assets/Gedächtnis-DB.
- [ ] YouTube-Kanal + YouTube Data API Zugang (Google Cloud Projekt, OAuth).
- [ ] GitHub-Repo + Secrets-Verwaltung (API-Keys als Actions Secrets, nie im Code).
- [ ] Gemini-API-Key einrichten.
- [ ] PixAI-Wrapper isoliert testen (ohne Automatisierung) – Upload-Workflow einmal manuell nachvollziehen.
- [ ] Piper lokal/in einer Actions-Testrun installieren und eine Stimme gegen die Tsundere-Mantarochen-Persönlichkeit probehören (Entscheidungsgrundlage für 5.1 Punkt 1).

**Phase 1 – MVP: Ein Video, komplett manuell getriggert**
- Kompletter Pipeline-Durchlauf (Idee → Skript → Bild → Voice → Schnitt → Upload) einmal von Hand angestoßen, jeder Schritt geprüft.
- Ziel: Pipeline funktioniert technisch, Qualität stimmt, bevor irgendwas automatisch läuft.

**Phase 2 – Teilautomatisierung**
- Scheduler (z. B. GitHub Actions Cron) löst Pipeline regelmäßig aus, aber Upload noch mit manueller Freigabe (Review vor Veröffentlichung).

**Phase 3 – Volle Automatisierung + Community**
- Auto-Upload ohne Freigabe (sobald Vertrauen in Qualitäts-Gate besteht).
- Kommentar-Antworten, Analytics-Auswertung, Gedächtnis-Updates aktiv.

**Phase 4 – Wachstum & Cross-Plattform**
- TikTok/Instagram Cross-Posting.
- Persönlichkeits-Feinschliff basierend auf echten Analytics-Daten.
- Andere VTuber-Kanäle systematisch beobachten (was funktioniert, Retention-Muster) und in Themenwahl einfließen lassen.

**Phase 5 – Ausbau**
- Livestreaming.
- Erweiterte Community-Features.
- Ggf. Monetarisierung, wenn Partnerprogramm-Schwellen erreicht sind.

---

## 7. Nächster Schritt

Wenn der Plan so passt: ich würde als Erstes Phase 0 aufsetzen (Drive-Ordner-Struktur + Doku-Grundgerüst), parallel brauche ich von dir Punkt 5.1–5.5 oben, sobald du dazu kommst. Sag einfach, wo wir anfangen sollen.
