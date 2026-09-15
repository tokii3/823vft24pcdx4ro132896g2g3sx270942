"""
Publish-Agent – Upload & Cross-Posting.

TODO (Phase 0):
- YouTube Data API v3 Zugang einrichten (Google Cloud Projekt, OAuth)
- Kanal-Positionierung so wählen, dass NICHT automatisch als "Made for Kids"
  eingestuft wird (siehe masterplan.md Abschnitt 1.8) – sonst fallen Kommentare
  und Community-Tab weg.

TODO (Phase 1):
- Upload-Funktion (Shorts + Long-form + Community-Post)
- Beschreibung: freiwilliger Hinweis "KI-VTuber / virtuelle Persönlichkeit"
  (siehe masterplan.md Abschnitt 1.2)

TODO (Phase 2):
- Scheduler-Anbindung (GitHub Actions Cron), zunächst mit manueller
  Freigabe vor Veröffentlichung

TODO (Phase 4):
- Cross-Posting TikTok, Instagram Reels (gleiches Videomaterial, minimal angepasst)
"""

def upload_video(path: str, title: str, description: str):
    raise NotImplementedError("Wird in Phase 1 implementiert – siehe docs/masterplan.md")
