# Raymi-Wissenspaket — für den Engine-Ordner

Stand: 2026-09-25. Dieses Paket ersetzt das Google-Drive-Doku-System als
Wissensquelle für alles, was NICHT bereits Code/Render-Logik ist. Es enthält
nur aktuell gültiges Wissen (keine verworfenen Design-Stände, keine
PixAI/Tsubaki3-Prompts — die betreffen die Bild-Erzeugung, nicht den
Renderer). Bei jedem neuen Chat einfach diesen Ordner zusammen mit dem
Engine-Code (engine.py, assets_v3.py, sprite_catalog.json, ENGINE_NOTES.md,
BACKGROUNDS_AND_MUSIC.md, catalog_tool.py, generate_audio.py) hochladen.

## Enthaltene Dateien

- **01_Character-Voice-and-Style.md** — wie Raymi redet/schreibt: Persönlichkeit,
  Sprachregeln, Kaomojis, Beispieldialoge, Umgang mit heiklen Themen.
- **02_Lore-and-Memory.md** — Raymis "Gedächtnis": feste Fakten, Running Gags,
  Wachstums-Meilensteine (Abos/Views), bereits getroffene Entscheidungen zu
  wiederkehrenden Fragen (z.B. "bist du KI?"). Diese Datei IST das Gedächtnis
  für die manuelle Produktion — es gibt aktuell kein separates Laufzeit-
  Gedächtnissystem (Datenbank o.ä.), das wäre ein eigenes, späteres Projekt
  (der automatisierte Community-/Kommentar-Agent), nicht Teil dieses Renderers.
- **03_Video-Scripting-Guide.md** — wie Videos gescriptet werden: Hook/Setup/
  Body/Payoff-Struktur, Pacing-Regeln, Anti-Slop-Checkliste, Content-Formate,
  Titel/Thumbnail-Prinzipien.
- **04_Asset-Creation-and-QC-Guidelines.md** — Anforderungen an Assets
  (Charakter-PNGs, prozedural gezeichnete Icons/Buttons, Branding-Pflichten
  wie Raymi-Font auf jedem Text-Asset) plus die Qualitäts-Checkliste, die aus
  den bisherigen Regressions-Fällen (falscher Font, kopfabschneidende Bilder,
  wild bouncende Wörter, generische Bokeh-Kreise, neu erfundene Render-Module
  statt der bestehenden Engine) abgeleitet ist.
- **05_Channel-Brand-Info.md** — aktuelle Kanalbeschreibung/Hashtags/
  Business-Mail, falls mal Video-Beschreibungen oder Community-Posts
  mitgeschrieben werden sollen.
- **06_Analytics-Insights.md** (NEU, v6) — Auswertung des ersten echten
  YouTube-Studio-Exports (13 Videos): Hook-Ranking, Engagement-Befund
  (Kommentar-Prompt jetzt Pflicht-Beat), Markt-/Geografie-Lücke, nächste
  Schritte. Quelle für Abschnitt 6 in 03_Video-Scripting-Guide.md.

## Bewusst NICHT enthalten

- Alle als SUPERSEDED markierten Drive-Dokumente (alte Design-Stände: Devil-
  Horns, Tentacle-Horns, Gothic-Kleid, Cape/Umhang — Cape wurde in Session 12
  final aus dem Design entfernt).
- PixAI/Tsubaki3-Prompt-Bausteine und der Prompting-Guide — reine Bild-
  Erzeugung, nicht Teil des Renderers.
- Connector-/Architektur-Dokumente (Canva, vidIQ, Metricool, geplanter
  Automatisierungs-Agent) — die betreffen ein anderes, noch nicht gebautes
  System, nicht die lokale Render-Pipeline.
- Asset-Namenskonventionen für die Bild-Ablage — durch `sprite_catalog.json`
  + `catalog_tool.py` ersetzt (automatische Analyse statt manuellem
  Namensschema).
