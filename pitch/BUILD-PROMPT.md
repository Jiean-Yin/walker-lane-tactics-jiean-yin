# BUILD-PROMPT — how to rebuild the pitch film

## The prompts (Claude Code, 2026-11-24)

1. Jiean: the A8 assignment PDF, then "Can we finish assignment 8 tonight? If yes, let's get going."
2. Claude Code answered with a plan and eight numbered questions, each with a default (project, role and reader, comparables, in/out/first, risk, why, format, README name).
3. Jiean: "Defaults fine, go".

## Commands (Windows 11, Git Bash, from the repository root)

```bash
export PYTHONUTF8=1
PY=<brutalist>/.venv/Scripts/python.exe
# 1. narration: one mp3 per beat in pitch/mp3/, durations written back to beat_sheet.json
$PY <brutalist>/runtime/scripts/generate_audio_kokoro.py pitch
# 2. slides, cuts and the master (pitch/exports/lane-tactics-pitch-a8.mp4, 3840x2160, 24 fps)
$PY pitch/tools/build_film.py \
    --a6-master youtube/claude-liam-walker-lane-tactics-jiean-yin-a6-gamedev/exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-a6-gamedev.mp4 \
    --fonts <brutalist>/runtime/fonts
# 3. Brutalist gates on the master (reports copied into pitch/gates/)
$PY <brutalist>/runtime/scripts/master_check.py pitch --mp4 pitch/exports/lane-tactics-pitch-a8.mp4
$PY <brutalist>/runtime/scripts/loudness_check.py pitch --mp4 pitch/exports/lane-tactics-pitch-a8.mp4
# 4. checksum
sha256sum pitch/exports/lane-tactics-pitch-a8.mp4
```

The A6 master is not in git (MP4); rebuild it from that film's `BUILD-PROMPT.md`, or use the copy linked in the repository README. Footage ranges are the `SEGMENTS` table in `tools/build_film.py`.
