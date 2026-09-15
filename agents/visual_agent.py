"""
Visual-Agent – Bild-/Video-Erstellung über PixAI (inoffizieller Wrapper).

WICHTIG: PixAI hat keine offizielle öffentliche API. Genutzt wird ein
inoffizieller/reverse-engineerter Wrapper (z. B. pixaiAPI auf PyPI), der den
internen Web-Token nutzt. Siehe masterplan.md Abschnitt 1.5 für Risiken.

TODO (Phase 0/1):
- PixAI-Wrapper isoliert testen (ohne Automatisierung) – manueller Durchlauf zuerst
- Session-Token aus Secret PIXAI_SESSION_TOKEN laden (niemals hart codieren)
- Ergebnis-Bilder nach Google Drive schieben (über Google Drive Connector)

TODO (später, Bauplan siehe masterplan.md Abschnitt 5.1.2):
- ComfyUI-Fallback-Pfad als Absicherung, falls PixAI-Wrapper bricht
  (nicht Teil des Phase-0/1-MVP, nur mitgeplant)
"""

def generate_visual(prompt: str):
    raise NotImplementedError("Wird in Phase 1 implementiert – siehe docs/masterplan.md")
