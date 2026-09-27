"""
generate_audio.py — Raymi voiceover generator (edge-tts based)

USAGE (local machine only, needs internet access — will NOT run inside
Claude's chat sandbox):

    1. pip install edge-tts mutagen
    2. Paste your script text into input.txt (plain text, UTF-8)
    3. Adjust VOICE / PITCH / RATE below if you want a different sound
    4. Run: py generate_audio.py   (or: python generate_audio.py)
    5. Every run creates its own folder under output/, named by timestamp
       + a short slug from your text, and every file inside it shares that
       same unique name (no more identical "voiceover.mp3" across runs), e.g.:
         output/2026-09-19_1432_okay-so-my-best-friend/
           2026-09-19_1432_okay-so-my-best-friend.mp3        the audio
           2026-09-19_1432_okay-so-my-best-friend_words.json word-level timestamps (start/end in seconds)
           2026-09-19_1432_okay-so-my-best-friend.srt        rough word-chunked subtitle file
           2026-09-19_1432_okay-so-my-best-friend_input.txt  exact copy of the text that was synthesized

Each run gets its own folder on purpose — old takes never get overwritten,
and audio/timestamps/source-text for one take always stay together, so you
can hand a single folder back to Claude and nothing is ambiguous.

The JSON file is what matters most for scripting/captioning — exact
per-word start/end times, more precise than estimating from words/second.
If word-level timing data doesn't come back from edge-tts (a known
flakiness of some voices with this unofficial API, not a bug in this
script), the script retries once automatically, and falls back to an
evenly-distributed estimate as a last resort — clearly marked as
"estimated": true in the JSON so you always know which kind you got.
"""

import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit(
        "edge-tts is not installed.\n"
        "Run:  pip install edge-tts\n"
        "Then run this script again."
    )

# ---------------------------------------------------------------------------
# CONFIG — edit these, nothing else needs to change
# ---------------------------------------------------------------------------

INPUT_FILE = "input.txt"
OUTPUT_DIR = "output"

# Voice candidates (US/UK, female, tested as "cute"/friendly leaning):
#   en-US-AnaNeural     - young, bright, playful    (kids/cute persona)
#   en-US-AvaNeural     - warm, natural, soft
#   en-US-EmmaNeural    - bright, friendly, slightly more "professional"
#   en-US-JennyNeural   - versatile, general-purpose default
#   en-GB-SoniaNeural   - British accent, cute/cozy
# Run `edge-tts --list-voices` locally to see the full list (hundreds of
# languages/voices) if none of these fit.
VOICE = "en-US-AnaNeural"

# Prosody tuning. Format: "+N%"/"-N%" for rate/volume, "+NHz"/"-NHz" for pitch.
# Slightly lower pitch + slightly faster than the voice's raw default, per
# feedback on the first take — kept close to default on purpose.
RATE = "+17%"
PITCH = "-7Hz"
VOLUME = "+0%"

# Raymi's target speaking pace per Video-Script-Bible section 1.3, for the
# summary printout at the end (purely informational, doesn't affect output).
TARGET_WPS = 2.5

# How many synthesis attempts before falling back to estimated timing if
# edge-tts doesn't return word-boundary data.
MAX_ATTEMPTS = 2

# ---------------------------------------------------------------------------


def load_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        sys.exit(f"Input file not found: {path}\nCreate it and paste your script text into it.")
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        sys.exit(f"{path} is empty — paste your script text into it first.")
    return text


def split_words(text: str):
    return [w for w in re.split(r"\s+", text) if w]


def make_slug(text: str) -> str:
    words = split_words(text)[:5]
    slug = "-".join(re.sub(r"[^a-zA-Z0-9]", "", w).lower() for w in words)
    slug = re.sub(r"-+", "-", slug).strip("-")[:40] or "voiceover"
    return slug


def make_run_dir(stamp: str, slug: str, base: Path) -> Path:
    """One folder per run: timestamp + short slug from the text, so takes
    never collide/overwrite and audio+timestamps+source stay together."""
    run_dir = base / f"{stamp}_{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


async def synthesize_once(text: str, mp3_path: Path):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, volume=VOLUME)
    words = []
    with open(mp3_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 10_000_000
                end = start + chunk["duration"] / 10_000_000
                words.append({"word": chunk["text"], "start": round(start, 3), "end": round(end, 3)})
    return words


def get_mp3_duration(mp3_path: Path):
    try:
        from mutagen.mp3 import MP3
    except ImportError:
        return None
    try:
        return MP3(str(mp3_path)).info.length
    except Exception:
        return None


def estimate_words(text: str, duration: float):
    """Fallback only: spread words evenly across the real audio duration.
    Marked as estimated — not real per-word timing, just better than nothing."""
    words = split_words(text)
    if not words or not duration:
        return []
    per_word = duration / len(words)
    result = []
    t = 0.0
    for w in words:
        result.append({"word": w, "start": round(t, 3), "end": round(t + per_word, 3)})
        t += per_word
    return result


async def synthesize_with_retry(text: str, mp3_path: Path):
    words = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Synthesizing (attempt {attempt}/{MAX_ATTEMPTS}) ...")
        words = await synthesize_once(text, mp3_path)
        if words:
            return words, False
        print("  no word-boundary data in this attempt.")
    print("Falling back to estimated timing (evenly spread across real audio duration).")
    duration = get_mp3_duration(mp3_path)
    if duration is None:
        print(
            "  mutagen not installed, can't measure audio duration for the "
            "fallback estimate either. Run: pip install mutagen"
        )
        return [], True
    return estimate_words(text, duration), True


def write_json(words, estimated: bool, out_dir: Path, base_name: str):
    total_duration = words[-1]["end"] if words else 0.0
    word_count = len(words)
    wps = round(word_count / total_duration, 2) if total_duration else 0.0

    payload = {
        "estimated": estimated,
        "total_duration_sec": round(total_duration, 3),
        "word_count": word_count,
        "words_per_second": wps,
        "words": words,
    }
    json_path = out_dir / f"{base_name}_words.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return json_path, payload


def write_srt(words, out_dir: Path, base_name: str, words_per_line: int = 4):
    def fmt_ts(seconds: float) -> str:
        ms = int(round(seconds * 1000))
        h, ms = divmod(ms, 3_600_000)
        m, ms = divmod(ms, 60_000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    idx = 1
    for i in range(0, len(words), words_per_line):
        chunk = words[i : i + words_per_line]
        if not chunk:
            continue
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        text = " ".join(w["word"] for w in chunk)
        lines.append(f"{idx}\n{fmt_ts(start)} --> {fmt_ts(end)}\n{text}\n")
        idx += 1

    srt_path = out_dir / f"{base_name}.srt"
    srt_path.write_text("\n".join(lines), encoding="utf-8")
    return srt_path


def main():
    text = load_text(INPUT_FILE)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    slug = make_slug(text)
    # base_name carries the timestamp too, so files stay unique/sortable
    # even if you later move them out of their run folder.
    base_name = f"{stamp}_{slug}"

    run_dir = make_run_dir(stamp, slug, Path(OUTPUT_DIR))
    (run_dir / f"{base_name}_input.txt").write_text(text, encoding="utf-8")

    mp3_path = run_dir / f"{base_name}.mp3"
    words, estimated = asyncio.run(synthesize_with_retry(text, mp3_path))

    if not words:
        sys.exit(
            "No audio timing data at all (and no fallback possible). The MP3 "
            f"may still be usable at {mp3_path}. Check your internet "
            "connection and try again."
        )

    json_path, payload = write_json(words, estimated, run_dir, base_name)
    srt_path = write_srt(words, run_dir, base_name)

    expected_words = len(split_words(text))
    print()
    print(f"Done. Files written to {run_dir}/")
    print(f"  - {mp3_path.name}")
    print(f"  - {json_path.name}" + ("  (ESTIMATED timing, not exact)" if estimated else ""))
    print(f"  - {srt_path.name}")
    print(f"  - {base_name}_input.txt")
    print()
    print(f"Duration:         {payload['total_duration_sec']}s")
    print(f"Words:            {payload['word_count']}  (raw text split: {expected_words})")
    print(f"Actual pace:      {payload['words_per_second']} words/sec")
    print(f"Target pace:      {TARGET_WPS} words/sec (Video-Script-Bible sec. 1.3)")
    if payload["words_per_second"]:
        diff_pct = round((payload["words_per_second"] / TARGET_WPS - 1) * 100, 1)
        print(f"Difference:       {diff_pct:+}% vs. target")


if __name__ == "__main__":
    main()