"""
Master-Agent – Orchestrierung, Persönlichkeit, Entscheidungen.

Verantwortlich für:
- Laden des Persönlichkeits-Kontexts aus memory/schema.md-Strukturen
- Entscheidung, was als Nächstes produziert wird
- Qualitäts-Gate vor jeder Veröffentlichung (on-brand? family-friendly? technisch ok?)
- Wochenplan vorlegen / Freigabe-Loop mit dem Nutzer (siehe masterplan.md Abschnitt 5.1.3)

TODO (Phase 1):
- Persönlichkeits-Kontext laden (character_core + learned_preferences + running_gags)
- Sub-Agenten aufrufen: content_agent, visual_agent, voice_agent, publish_agent, community_agent
- Review-Schritt vor jedem Upload implementieren (siehe masterplan.md Abschnitt 1.1)
"""

def run():
    raise NotImplementedError("Wird in Phase 1 implementiert – siehe docs/masterplan.md")


if __name__ == "__main__":
    run()
