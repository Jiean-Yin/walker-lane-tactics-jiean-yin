# Film records — "Lane Tactics: From Sketch to Seed to Sound"

Assignment 2 explainer film for the Lane Tactics asset slice, built with Brutalist `godot-gamedev walker` (checkout `6a8380a`). Game source shown: **`film-source-v1` = `fcf33ef`** (`godot/` identical to `12f7283`). Title is the default from the brief; Jiean may change it.

**Final master:** `exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-gamedev.mp4` (3840×2160, 30 fps, 6:08.3), SHA-256 `543020595fe6e95c9878e14e059c9936b9b1d49097edc8b491d6254b18236aba`; receipt `exports/landscape/…verified.json` (kept in git, the MP4 is not). Link: *to add after upload by Jiean.*

| File | What it is |
|---|---|
| [beat_sheet.json](beat_sheet.json) | The script: narration, visuals, measured durations, labels, QC declarations |
| [gamedev-evidence.json](gamedev-evidence.json) | Source ledger: every `godot/` file hashed, 6 components, 3 exact excerpts, code → result pairs |
| [coverage.json](coverage.json) | Capture-contract ledger for the five gameplay clips (features shown, with times) |
| [CAPTURE.md](CAPTURE.md) | How the slice was recorded: isolated copy, Movie Maker + 4K SubViewport, input path, hashes, same-run audio join |
| [capture/](capture/) | Driver, input/event log, summary (22/22), clip records, source snapshot, test logs |
| [COMPONENTS.md](COMPONENTS.md) · [RIFF.md](RIFF.md) | Component map with one input → state → output trace; what each gameplay beat shows |
| [SHOTLIST.md](SHOTLIST.md) · [FACTCHECK.md](FACTCHECK.md) · [SOURCES.md](SOURCES.md) · [PROMPTS.md](PROMPTS.md) | Beat list with labels; every claim with its source; provenance; prompts |
| [BUILD-PROMPT.md](BUILD-PROMPT.md) · [tools/](tools/) | How to rebuild, and the scripts used (sheet, clips, composites, cues, labels, evidence, audio check) |
| [TYPECHECK.md](TYPECHECK.md) · [_qc/](_qc/) | Gate T, Gate V, audio checks, preview QC notes |
| [stills/](stills/) | 720p previews of the evidence composites |

Not in git (kept locally): the capture AVI and the 4K FFV1 master (`<capture-copy>\run-03\`), `media/`, `clips/`, `mp3/`, `_work/`, the review cut and any export.
