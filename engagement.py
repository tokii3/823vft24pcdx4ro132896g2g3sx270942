"""
engagement.py — v6 addition. NEW module, nothing in engine.py/assets_*.py/
proof_onigiri_v4.py/raymi_short.py was deleted or rewritten (project rule
unchanged, see ENGINE_NOTES.md / ENGINE_NOTES_v5.md).

WARUM DIESES MODUL EXISTIERT (Grund: echte YouTube-Analytics, 2026-09-25,
siehe Raymi-Wissen/06_Analytics-Insights.md fuer die volle Auswertung):
Ueber alle 13 bisherigen Videos zusammen nur 2 "Geteilte Inhalte" und 8
Kommentare bei 3722 Aufrufen. Das ist nicht "wenig Glueck", das ist ein
fehlendes Feature: keines der bisherigen Skripte hat einen SICHTBAREN
(nicht nur gesprochenen) Kommentar-/Share-Prompt eingebaut. Die alte Regel
in 03_Video-Scripting-Guide.md ("CTA nur wenn organisch, sonst weglassen")
wird hiermit fuer den Comment-Prompt explizit AUSSER KRAFT gesetzt: der
Comment-Prompt ist ab v6 PFLICHT-Beat, nicht optional - siehe Abschnitt 8
der Scripting-Guide. Er bleibt aber in Raymis Stimme geschrieben (konkrete,
leicht kontroverse Ja/Nein- oder Ein-Wort-Frage, nie generisches "like and
subscribe").

Nutzung (z.B. am Ende von scene()/frame() in einer neuen Szene, in den
letzten ~1.2-1.8s des letzten Beats, siehe proof_onigiri_v4.py fuer die
tatsaechliche Verdrahtung):

    import engagement as E
    ...
    fr = E.cta_prompt(fr, TX, "team rice first or team rice last??", u,
                       dur=1.6, sub="say it in the comments (・`ω´・)")

Zeichnet NICHT permanent - nur innerhalb der uebergebenen dur-Sekunden
(pop-in -> hold -> pop-out), damit es wie ein bewusster Beat wirkt und
nicht wie ein aufgeklebtes Overlay das die ganze Zeit klebt.
"""
import math
import numpy as np
import cv2
from engine import W, H, UV, WHITE, DARK, clamp, smooth, ease_out, back_out, blit, premult

# ------------------------------------------------------------------ procedural speech-bubble tail/pill
# Kein Font-Glyph-Bedarf (gleiches Prinzip wie assets_v3.py) - ein simples
# abgerundetes Pill/Bubble-Shape, gezeichnet mit cv2, in Raymis UV-Palette.

def _bubble_bg(w, h, r=None, fill=(22, 20, 46), edge=UV, edge_w=6):
    r = r if r is not None else h // 2
    im = np.zeros((h, w, 4), np.uint8)
    mask = np.zeros((h, w), np.uint8)
    cv2.rectangle(mask, (r, 0), (w - r, h), 255, -1)
    cv2.rectangle(mask, (0, r), (w, h - r), 255, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)):
        cv2.circle(mask, (cx, cy), r, 255, -1)
    im[..., :3] = fill
    im[..., 3] = mask
    # thin glowing outline in brand color, so the prompt reads as "different from a caption"
    edge_mask = cv2.subtract(mask, cv2.erode(mask, np.ones((edge_w * 2 + 1, edge_w * 2 + 1), np.uint8)))
    im[edge_mask > 0, :3] = edge
    im[edge_mask > 0, 3] = 255
    return premult(im)


def cta_prompt(fr, text_engine, question, u, dur=1.5, sub=None, pos_y=0.665,
               size=64, sub_size=38, color=WHITE, accent=UV):
    """Draw an animated comment-bait pill near (but not on) the caption zone.

    fr           - current RGB frame (H,W,3), modified via blit and returned
    text_engine  - the shared engine.Text instance (font cache) already used
                   for captions, so this never falls back to a default font
                   (see 04_Asset-Creation-and-QC-Guidelines.md rule #1)
    question     - short, specific, in-character line, e.g.
                   "team rice first or rice last??" - NOT a generic CTA
    u            - local seconds since this beat/segment started (0 at pop-in)
    dur          - total on-screen time for the prompt (pop-in+hold+pop-out)
    sub          - optional small second line, e.g. "comment below (・`ω´・)"
    """
    if u < 0 or u > dur:
        return fr
    pop_in, pop_out = 0.22, 0.20
    if u < pop_in:
        k = back_out(u / pop_in)
    elif u > dur - pop_out:
        k = 1 - smooth((u - (dur - pop_out)) / pop_out)
    else:
        k = 1.0
    if k <= 0.01:
        return fr

    q_tile = text_engine.tile(question, size, color, DARK)
    lines = [q_tile]
    if sub:
        lines.append(text_engine.tile(sub, sub_size, accent, DARK))
    pad_x, pad_y, gap = 46, 28, 10
    content_w = max(l.shape[1] for l in lines)
    content_h = sum(l.shape[0] for l in lines) + gap * (len(lines) - 1)
    bw, bh = min(int(W * 0.9), content_w + pad_x * 2), content_h + pad_y * 2
    bubble = _bubble_bg(bw, bh)

    wob = 1.5 * math.sin(2 * math.pi * u / 1.6)
    cx, cy = W / 2, pos_y * H
    blit(fr, bubble, bw / 2, bh / 2, cx, cy, s=k, rot=wob * (1 - abs(k - 1)))
    yy = cy - content_h * k / 2
    for l in lines:
        blit(fr, l, l.shape[1] / 2, l.shape[0] / 2, cx, yy + l.shape[0] * k / 2, s=k)
        yy += (l.shape[0] + gap) * k
    return fr


def loop_reply_hint(fr, text_engine, u, dur=1.0, pos_y=0.94,
                     text="watch again? she counts (¬‿¬)ﾉ", size=30):
    """Tiny, understated one-liner for the very last frames, timed to land right
    as loop_seam() blends back into the hook — a small wink that acknowledges
    the loop instead of a silent hard restart. Optional, cheap, easy to skip
    per-video by simply not calling it."""
    if u < 0 or u > dur:
        return fr
    a = clamp(min(u / 0.25, (dur - u) / 0.25))
    tl = text_engine.tile(text, size, WHITE, DARK)
    blit(fr, tl, tl.shape[1] / 2, tl.shape[0] / 2, W / 2, pos_y * H, s=1.0, alpha=a)
    return fr
