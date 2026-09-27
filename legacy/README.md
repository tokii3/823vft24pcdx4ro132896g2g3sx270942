# legacy/ — veraltete Asset-Module

`assets_v3.py`, `assets_v4.py`, `assets_v5.py` — der flache, ungeshadete
Asset-Look vor `assets_v6.py`. Seit dem QA-Pass 2026-09-26 (siehe
`../ENGINE_NOTES_v10.md`, Abschnitt 1) importiert **kein** aktives
Render-Skript (`raymi_short.py`, `proof_onigiri_v4.py`,
`landscape_demo_v5.py`) diese Dateien mehr — alle nutzen jetzt
`assets_v6.py`.

Bewusst nicht gelöscht (Projekt-Regel "erweitern statt löschen"), nur aus
dem Hauptordner heraussortiert, damit auf den ersten Blick klar ist, was
tatsächlich noch gerendert wird.

**Hinweis falls jemand die alten `__main__`-Vorschau-Sheets hier trotzdem
mal laufen lassen will:** die Dateien machen `from engine import ...` —
dafür `engine.py` (liegt eine Ebene höher) temporär hierher kopieren oder
den Projekt-Root zusätzlich in `PYTHONPATH` aufnehmen. Für den normalen
Render-Betrieb ist das nicht nötig.
