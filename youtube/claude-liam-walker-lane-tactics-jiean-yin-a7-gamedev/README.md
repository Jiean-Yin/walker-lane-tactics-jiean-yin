# Film records — "Lane Tactics: A Waving Flag and a Committed Shot"

Assignment 7 explainer film for the Lane Tactics animations:
- `wave`: a goal flag played from a found sprite sheet by an AnimationPlayer frame track;
- `shoot`: an archer's committing action on a cutout rig keyed as resource text.

It also covers their one authority, the two clocks, the phase table in frames, the read-backs, mutations and edges, and one tuning revision.

**How it was made:** Brutalist `godot-gamedev walker` (checkout `6a8380a`). Game source shown: **tag `a7` (`37c4698`)**, filmed on an isolated copy. Script drafted by Claude from Jiean's documents and **approved by Jiean on 2026-11-26** ("Approve as is").

**Final master:** `exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-a7-gamedev.mp4`
- 3840×2160, 30 fps, 7:54.4;
- SHA-256 `3c2e831bcc2624b7431bc0088a1a8f612781fdbb3a2f396fd8ec9cbc526fb794`;
- checks and QC in [_qc/MASTER-QC.md](_qc/MASTER-QC.md);
- Jiean's watch-through of the full export (2026-11-26): "Ready";
- Uploaded by Jiean to YouTube: https://youtu.be/1DWyaSYxO24

| File | What it is |
|---|---|
| [SCRIPT-DRAFT.md](SCRIPT-DRAFT.md) | The script as approved (narration, visuals, labels) |
| [beat_sheet.json](beat_sheet.json) | The build script: narration, shots, measured durations, labels, footage ranges |
| [gamedev-evidence.json](gamedev-evidence.json) | Source ledger: every authored `godot/` file at tag `a7` hashed; components; exact excerpts; code → result pairs |
| [CAPTURE.md](CAPTURE.md) · [capture/](capture/) | The isolated copy, the Movie Maker driver, per-frame logs, shot ranges, master hashes, the film's rerun of every suite, the observation checks |
| [COMPONENTS.md](COMPONENTS.md) · [RIFF.md](RIFF.md) | Component map with one input → state → output trace; what each footage range shows |
| [SHOTLIST.md](SHOTLIST.md) · [FACTCHECK.md](FACTCHECK.md) · [SOURCES.md](SOURCES.md) · [PROMPTS.md](PROMPTS.md) | Beats and labels; every claim with its source; provenance; prompts |
| [BUILD-PROMPT.md](BUILD-PROMPT.md) · [tools/](tools/) | How to rebuild, and the scripts used (adapted from the A6 film's) |

Not in git: the capture copy and its FFV1 masters (`<capture-copy>`), `media/`, `mp3/`, `_work/`, and the exported MP4.

**Limits the film states:**
- Key presses in the engine footage are scripted (labelled). The ¼-speed shots are a 120 fps capture shown at 30 fps, labelled and cropped (labelled).
- The in-play human judgements are Jiean's (TEST-REPORT A7.9–A7.12, A7.14), quoted, not filmed.
- No headless run draws anything; the look is judged from Jiean's strips (labelled fixtures) and the real-game footage.
- The reference archery video is never shown (standard YouTube licence); only Jiean's frame numbers appear.
- Left open: why the game's cues land ±1 frame (game timing was out of scope); the recoil is still about 1.5 screen px.
