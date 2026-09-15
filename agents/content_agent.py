"""
Content-Agent – Ideen, Skripte, Captions, Titel.

Nutzt Gemini API für laufende/häufige Textaufgaben (günstig/schnell).
Claude wird nur für seltene, wichtige Entscheidungen (Persönlichkeits-Feinschliff,
Wochenplanung) eingesetzt – siehe masterplan.md Abschnitt 2.1.

TODO (Phase 1):
- Gemini-API-Anbindung (Key kommt aus Secret GEMINI_API_KEY, siehe config/config.example.yaml)
- Prompt-Vorlage mit character_core + learned_preferences aus memory/
- Output-Format: Idee, Skript, Caption, Titel als strukturiertes JSON an master_agent.py
"""

def generate_content_plan():
    raise NotImplementedError("Wird in Phase 1 implementiert – siehe docs/masterplan.md")
