# Film records — "Lane Tactics: A Hit Burst and an Arrow Trail"

Assignment 6 explainer film for the Lane Tactics particle effects:
- the hit burst (`CPUParticles2D`, three emitters) and the arrow trail (`GPUParticles2D`, two emitters, turbulence);
- their read-only drivers, the configuration and state tests, the price, and the editor-generated process shader.

**How it was made:** Brutalist `godot-gamedev walker` (checkout `6a8380a`). Game source shown: **tag `a6` (`7f199f9`)**, filmed on an isolated copy. Script drafted by Claude from Jiean's documents and **approved by Jiean on 2026-11-08**; later changes are dated in SCRIPT-DRAFT.md, each shown to Jiean first.

**Final master:** `exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-a6-gamedev.mp4`
- 3840×2160, 30 fps, 10:30.0;
- SHA-256 `68124efb8d904f0eb81a8ee462470ed6ec43e23f1826fac922c26510b00075c6`;
- checks and QC in [_qc/MASTER-QC.md](_qc/MASTER-QC.md);
- Jiean's watch-through of the full export (2026-11-08): "Ready as is".
- Uploaded by Jiean to YouTube: https://youtu.be/Hfi4B5O40qw

| File | What it is |
|---|---|
| [SCRIPT-DRAFT.md](SCRIPT-DRAFT.md) | The script as approved (narration, visuals, labels), with the dated changes after approval |
| [beat_sheet.json](beat_sheet.json) | The build script: narration, shots, measured durations, labels, footage ranges |
| [gamedev-evidence.json](gamedev-evidence.json) | Source ledger. Every authored `godot/` file at tag `a6` is hashed; 8 components; earlier-assignment files are excluded with a reason. 12 exact excerpts, 12 code → result pairs |
| [CAPTURE.md](CAPTURE.md) · [capture/](capture/) | The isolated copy and the history rewrite; the Movie Maker driver; per-frame logs; shot ranges; master hashes; the film's rerun of every suite; the pilot; Jiean's quotes and their review |
| [COMPONENTS.md](COMPONENTS.md) · [RIFF.md](RIFF.md) | Component map with one input → state → output trace; what each footage range shows |
| [SHOTLIST.md](SHOTLIST.md) · [FACTCHECK.md](FACTCHECK.md) · [SOURCES.md](SOURCES.md) · [PROMPTS.md](PROMPTS.md) | Beats and labels; every claim with its source; provenance; prompts, real and reconstructed |
| [BUILD-PROMPT.md](BUILD-PROMPT.md) · [tools/](tools/) | How to rebuild, and the scripts used |
| [_qc/](_qc/) | Checker output and master QC |
| [stills/](stills/) | 720p previews of the evidence stills |

Not in git: the capture copy and its FFV1 masters (`<capture-copy>`), `media/`, `mp3/`, `_work/`, and the exported MP4.

**Limits the film states:**
- Key presses in the engine footage are scripted (labelled on screen). The ¼-speed shots are a 120 fps capture shown at 30 fps, labelled, some cropped (labelled).
- The in-play human judgement is Jiean's playtest (TEST-REPORT A6.8), quoted, not filmed.
- No headless run draws a particle. The look is judged from Jiean's strips (labelled fixtures) and the real-game footage.
- Left open:
  - why the trail stops up to two frames before the impact cue (game timing was out of scope);
  - what the profiler's 4–6 ms with vsync on contains;
  - whether a hidden trail keeps simulating.
