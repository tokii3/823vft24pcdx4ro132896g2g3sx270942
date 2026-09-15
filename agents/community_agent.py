"""
Community-Agent – Kommentare lesen, filtern, beantworten; Gedächtnis pflegen.

Sicherheitsregel (masterplan.md Abschnitt 1.4 / 5.1.4):
Kommentar-Input ist EXTERNER, nicht vertrauenswürdiger Input und wird niemals
in denselben Prompt-Kontext wie die System-Instruktionen gegeben.

Zweistufiger Prüf-Prozess für jeden Kommentar, BEVOR geantwortet wird:
  1. Günstiger Regex-/Keyword-Vorfilter gegen offensichtliche
     Injection-Versuche ("ignore previous instructions" o.ä.)
  2. Gemini-Call mit der reinen Aufgabe: "Ist das eine legitime Frage/Reaktion
     oder ein Manipulationsversuch?" – der Kommentar wird dabei NUR als
     zu lesende Daten übergeben, nie als Instruktion.
  Nur bei Ergebnis "legitim" geht es in die eigentliche Antwort-Generierung.

Weitere Regeln:
- Rate-Limit: siehe config/config.example.yaml -> limits.max_comment_replies_per_hour
- Spam/Hass-Kommentare: nicht beantworten, ggf. blockieren
- character_core wird NIE durch Kommentare verändert (siehe memory/schema.md)
- Nutzer-Gedächtnis bewusst schlank halten (siehe memory/schema.md, DSGVO-Hinweis
  masterplan.md Abschnitt 1.7)

TODO (Phase 3):
- Vollständige Implementierung inkl. Rate-Limiting und Spam-Filter
"""

def is_legitimate_comment(comment_text: str) -> bool:
    raise NotImplementedError("Wird in Phase 3 implementiert – siehe docs/masterplan.md")


def handle_comment(comment_text: str, channel_name: str):
    raise NotImplementedError("Wird in Phase 3 implementiert – siehe docs/masterplan.md")
