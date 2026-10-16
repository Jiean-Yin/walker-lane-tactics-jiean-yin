# Film records — "Lane Tactics in 3D: A Piece, a Square, a Goal"

Assignment 3 explainer film for the three Lane Tactics 3D assets (archer piece, board square, goal flag: built in Blender by Claude through the Blender MCP, exported to Godot, shown in a small diorama scene), built with Brutalist `godot-gamedev walker` (checkout `6a8380a`). Game source shown: **commit `e415255`**. The title is a default chosen for this build; Jiean may change it (the outro re-reads it, so a new title means re-rendering BOUT).

**Final master:** `exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-a3-gamedev.mp4` — 3840×2160, 30 fps, 4:41.5, SHA-256 `83d2489e2ee1f6e6c2d5ffc1df5387f086fba0c51a983904e08b93a2d4ad4240`; checks and QC in [_qc/MASTER-QC.md](_qc/MASTER-QC.md). Not published; link: *to add by Jiean after upload*.

| File | What it is |
|---|---|
| [beat_sheet.json](beat_sheet.json) | The script: narration, visuals, measured durations, labels, footage ranges |
| [gamedev-evidence.json](gamedev-evidence.json) | Source ledger: every `godot/` file at e415255 hashed, 5 components (the A3 additions), the A2 slice excluded with reason, 2 exact excerpts + 2 external (Blender script) excerpts, 4 code → result pairs |
| [CAPTURE.md](CAPTURE.md) | Student footage (what it contains, ranges used, privacy crop) and the new Movie Maker capture run-02 (isolated copy, scripted camera, hashes, join check) |
| [capture/](capture/) | Driver, run summary (assertions), per-frame camera log, join check, the film's rerun of the headless check (38/38), source snapshot, clip records |
| [COMPONENTS.md](COMPONENTS.md) · [RIFF.md](RIFF.md) | Component map with one input → state → output trace; what each footage/engine range shows |
| [SHOTLIST.md](SHOTLIST.md) · [FACTCHECK.md](FACTCHECK.md) · [SOURCES.md](SOURCES.md) · [PROMPTS.md](PROMPTS.md) | Beats and labels; every claim with its source; provenance; prompts (real and reconstructed) |
| [BUILD-PROMPT.md](BUILD-PROMPT.md) · [tools/](tools/) | How to rebuild, and the scripts used |
| [_qc/](_qc/) | Checker output, master QC (frame sheets, loudness), notes |
| [stills/](stills/) | 720p previews of the evidence composites |

Not in git (kept locally): the student's footage (`<footage>`), the capture AVI and 4K FFV1 master (`<capture-copy>\run-02\`), `media/`, `mp3/`, `_work/`, and the exported MP4.

**Limits the film states:** Claude's archer build and Blender building the flag are not in the student's footage (the archer clip starts after the build; the flag clip shows only the Claude window), so the film shows Claude's prompt/report text and the finished assets instead, and says so. The engine footage uses a scripted camera, not a human look check (TEST-REPORT A3.5 is still Jiean's to fill).
