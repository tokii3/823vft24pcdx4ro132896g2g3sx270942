# Raymi – KI-VTuber

Automatisierter KI-VTuber (Mantarochen, blau/lila, süß, tsundere-artig). Details zur Architektur, Risiken und Roadmap: siehe [`docs/masterplan.md`](docs/masterplan.md).

## Status

Phase 0 – Setup. Noch kein produktiver Code, nur Grundgerüst.

## Struktur

```
raymi-vtuber/
├── .github/workflows/   # GitHub Actions (Scheduler, Pipeline-Trigger)
├── agents/              # Master-Agent + Sub-Agenten (Content, Visual, Voice, Publish, Community)
├── memory/              # Gedächtnis-/Persönlichkeits-Schema (Charakter-Kern, gelernte Vorlieben, Running Gags)
├── config/              # Konfigurationsvorlagen (NIEMALS echte Keys hier einchecken!)
└── docs/                # Masterplan & weitere Dokumentation
```

## Wichtig: API-Keys

API-Keys (Gemini, YouTube, PixAI, ggf. TTS) werden **niemals** direkt im Code oder in Dateien in diesem Repo gespeichert. Sie gehören ausschließlich in:

**Repo-Einstellungen → Secrets and variables → Actions → New repository secret**

Details dazu bekommst du separat als Schritt-für-Schritt-Anleitung.

## Nächste Schritte

Siehe `docs/masterplan.md`, Abschnitt 6 (Roadmap) und Abschnitt 5 (Phase-0-Checkliste).
