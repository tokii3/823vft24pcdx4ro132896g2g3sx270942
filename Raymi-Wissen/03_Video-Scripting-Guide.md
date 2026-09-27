# Raymi — Video Scripting Guide

Covers story/script structure only. Caption rendering, word-sync, fonts,
and transitions are already implemented in the render engine — this file
is about what to write and how to pace it, not how it gets drawn.

## 1. Core Rules (every script)

- Hook = first 0-3 seconds, decides most of the drop-off. Open ONE
  curiosity gap. Never answer the hook in the hook itself. Sound-off must
  still work: the first frame + first on-screen text alone must carry it.
  No logo, no "hey guys", no slow build.
- Setup (why should I care) resolves within 8-10 seconds of the hook
  ending, or viewers leave before the payoff.
- Deliver exactly what the hook promised — the payoff must close the
  question the hook opened, before any CTA/loop.
- Raymi's personality is the differentiator, not the topic — a generic
  narrator reading the same facts is the "inauthentic content" trap. Every
  line must sound like something SHE would say (see
  01_Character-Voice-and-Style.md).
- Brand-safe filter on every line: no religion, politics, sexual content.
- Anti-slop check before a script is done: could this exact script, with
  the name changed, run on literally any other VTuber channel unchanged?
  If yes, it's not done — needs at least one moment that only works
  because it's specifically Raymi (a lore callback, a reaction only she'd
  have).

## 2. Script Shape (targets, adjust to what the idea needs)

- 00:00-00:03 HOOK — one sentence, one idea.
- 00:03-00:10 SETUP — bridges hook to content, ends on a mini-promise.
- 00:10 to ~end-3s BODY — the actual fact/lore/opinion, broken into beats
  of roughly 4-7 seconds each. One visual idea per beat; if a beat needs
  two visual ideas, split it into two beats. Emotional beats should
  alternate — a flat tone for 30+ seconds loses retention even with good
  material.
- last ~3s PAYOFF + LOOP/CTA — closes the hook's curiosity gap explicitly.
  Loop option (end on a line/visual that echoes the hook) works well for
  lore/fact shorts specifically. Only add a spoken CTA if it fits
  organically in Raymi's voice — a bolted-on "like and subscribe" breaks
  persona and reads as slop.

## 3. Pacing & Visual Rhythm

- A visual reset (new element, camera move, or transition) at minimum
  every 4-7 seconds. Longer static holds only for a deliberate
  slow/emotional beat, never more than once per video.
- Cut frequency scales with content: fact/lore reveal beats can breathe
  slightly longer (5-7s) than punchline/reaction beats (2-4s).
- Raymi's expression should change at every meaningful line, not just at
  scene changes — a static face on dynamic dialogue reads as cheap AI
  content. Never reuse the same expression two beats in a row unless it's
  a deliberate deadpan callback (e.g. mirroring the hook's framing at the
  very end for a loop).
- Sumi is reserved for reaction-cutaway or punchline-sidekick moments, not
  a background presence in every video.
- Every beat needs at least one of: background change, motion/idle
  animation, or camera move — never leave Raymi static on a flat
  background for more than one beat in a row.

## 4. Content Formats (in active use)

- Short-form fact/lore/bit videos in her voice (salmon-friendship lore,
  outfit opinions, running gags) — brand-safe, low-cost, high-repeatability.
- Opinion/commentary Shorts on popular topics (gaming, anime, internet
  trends — never politics/religion/sexual topics) — her personality is
  the differentiator here, not neutral narration. Reaction content
  (watching/timing against live source material in real time) is
  deliberately ruled out — doesn't fit the script → voiceover → render
  pipeline.
- Occasional long-form: channel intro/lore pieces.

## 5. Title / Thumbnail Principles

- Title: specific + curiosity gap, never vague ("my best friend is a
  salmon and I will not explain why" beats "get to know me!"). Proven
  angle types for this niche: (a) drama/callout framing, (b) a unique,
  specific identity fact (stingray + salmon running gag), (c) lore-reveal/
  comeback framing.
- Thumbnail: always Raymi's face/expression + the ultraviolet/black
  palette for instant brand recognition; optional Sumi cameo once useful.
- Tag pool (combine 8-15 per video, never all at once): vtuber, pngtuber,
  indie vtuber, envtuber, vtuber shorts, vtuber clips, vtuber funny
  moments, virtual youtuber, anime girl, vtuber comedy, vtuber lore,
  vtuber debut, new vtuber, stingray vtuber, idol vtuber, asmr vtuber,
  vtuber react, vtuber reacts, cute vtuber, purple aesthetic, jirai kei.
  Only tag "asmr vtuber" when the video actually has calm/relaxed content.

## 6. Retention & Engagement Framework (v6, gegen echte Analytics validiert)

Volle Auswertung: `06_Analytics-Insights.md`. Kurzfassung, die jedes neue
Skript beeinflussen soll:

- **Hook-Ranking aus echten Daten** (beste zuerst): (1) einzigartiger
  persönlicher Einzelfakt über Raymi (salmon-friendship, rain-prediction —
  höchste Ø-Wiedergabe UND höchste Abo-Konversion), (2) Callout/"du machst
  X falsch" (zieht Klicks stark, aber Payoff muss wirklich überraschen,
  sonst bricht die Mitte weg), (3) Confession/Direct-Address (kleine
  Stichprobe bisher, aber beste Completion-Werte im ganzen Datensatz), (4)
  generisches Ranking/Liste — schwächstes Muster auf allen Metriken
  gleichzeitig, nicht mehr als Standardformat nutzen.
- **Kommentar-Prompt ist ab jetzt PFLICHT-Beat, keine Ausnahme.** Das
  überschreibt die Regel aus Abschnitt 2 ("CTA nur wenn organisch") explizit
  für den Kommentar-Prompt — Grund: über 13 Videos/3722 Views nur 8
  Kommentare, 2 Shares insgesamt (siehe 06_Analytics-Insights.md Abschnitt
  2.3). Umsetzung: eine konkrete, leicht kontroverse Ja/Nein- oder
  Ein-Wort-Frage, in Raymis Stimme (nie "like and subscribe"-generisch),
  sichtbar als Text (nicht nur gesprochen) nach dem Payoff, vor dem Loop-Ende.
  Im Renderer: `engagement.cta_prompt()` (siehe `ENGINE_NOTES_v6.md`) — bei
  jedem neuen Short-Config einfach `cta=(frage, sub)` setzen.
- **Views ≠ Conversion — im Kopf behalten:** ein reißerischer Titel zieht
  Klicks, rettet aber keinen schwachen Payoff. Wenn ein Callout-Hook gewählt
  wird, muss der Überraschungsmoment klar vor der Hälfte des Videos liegen
  (siehe Setup-Fenster oben, Abschnitt 2).

## 7. Pre-Publish Checklist

- Hook stands alone with sound off.
- Every beat has a background change, motion element, or camera move.
- No two consecutive beats share an expression (unless a deliberate
  callback).
- Safe zones respected (captions clear of platform UI overlap).
- Anti-slop check passed (Section 1).
- Hook's curiosity gap is explicitly closed by the payoff.
- Brand-safety filter passed.
- At least one distinctly-Raymi moment (lore callback, reaction only she'd
  have) is present, not just generic content with her face on it.
- A visible comment-prompt beat is present (v6, mandatory — see Section 6).
