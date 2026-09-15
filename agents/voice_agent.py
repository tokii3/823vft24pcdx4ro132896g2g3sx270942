"""
Voice-Agent – Text-to-Speech.

Entscheidung (masterplan.md Abschnitt 5.1.1):
- Start mit Piper (CPU-tauglich, läuft in GitHub Actions, kostenlos)
- Coqui XTTS-v2 als Qualitäts-Alternative über Colab/Hugging-Face-Spaces-Trigger
  (Free Tier), Ergebnis nach Google Drive schieben
- Offener Praxistest: klingt eine Piper-Stimme passend zur süßen
  Tsundere-Mantarochen-Persönlichkeit, oder zu neutral/robotisch?

TODO (Phase 0):
- Piper lokal/in Actions-Testrun installieren, 2-3 Stimmen probehören
- Ergebnis dokumentieren, Entscheidung ggf. auf XTTS umstellen

TODO (Phase 1):
- engine-Auswahl aus config.yaml (piper/xtts) implementieren
"""

def synthesize(script: str, engine: str = "piper"):
    raise NotImplementedError("Wird in Phase 0/1 implementiert – siehe docs/masterplan.md")
