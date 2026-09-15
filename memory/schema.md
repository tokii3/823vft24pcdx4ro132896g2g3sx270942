# Gedächtnis-/Persönlichkeits-Schema

Speicherort (Entscheidung offen): SQLite-Datei ODER JSON/Markdown-Store in Google Drive.
Für Phase 0/1 reicht die JSON-Variante – einfacher zu debuggen, kein DB-Setup nötig.

## Tabellen/Strukturen

### character_core (fix, nur manuell änderbar)
```json
{
  "name": "Raymi",
  "species": "Mantarochen",
  "colors": ["blau", "lila"],
  "traits": ["süß", "naiv", "freundlich", "leicht tsundere"],
  "speech_style": "TODO – wird ergänzt, sobald Redewendungen feststehen"
}
```

### learned_preferences (wachsend, nur bei wiederholtem positiven Signal)
```json
[
  {
    "topic": "string",
    "first_seen": "ISO-date",
    "positive_mentions": 0,
    "threshold_reached": false
  }
]
```
Regel: `threshold_reached` wird erst true, wenn `positive_mentions >= 3` (Schwellenwert, verhindert Manipulation durch einzelne Kommentare).

### running_gags
```json
[
  {
    "id": "string",
    "description": "string",
    "origin_context": "string",
    "created_at": "ISO-date",
    "usage_count": 0
  }
]
```

### user_memory (datenschutzbewusst schlank halten)
```json
[
  {
    "channel_name": "string (öffentlich sichtbar)",
    "first_interaction": "ISO-date",
    "interaction_count": 0,
    "nickname_by_raymi": "string|null"
  }
]
```
Explizit **keine** privaten/sensiblen Daten speichern – siehe masterplan.md Abschnitt 1.7.
Löschfunktion (auf Anfrage eines Nutzers) muss vorhanden sein, sobald diese Datei produktiv befüllt wird.

## Zugriffsregel (wichtig)

`character_core` wird **niemals** automatisch durch Kommentare/Interaktionen verändert.
Nur `learned_preferences` und `running_gags` dürfen wachsen, und nur über den in
`agents/community_agent.py` beschriebenen Schwellenwert-Mechanismus.
