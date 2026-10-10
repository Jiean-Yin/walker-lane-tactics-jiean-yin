# SOURCES — walker-lane-tactics-jiean-yin

## What this project started from

- **An empty Godot 4.7.2 project.** No code was taken from the walker-jumpman starter or from my Assignment 1 project ([walker-jumpman-jiean-yin](https://github.com/Jiean-Yin/walker-jumpman-jiean-yin)), because the game logic is different.
- **Practices carried over from Assignment 1:** headless test scripts under `godot/tests/` that write timestamped reports to `evidence/`; the document set (CHANGE-BRIEF, TEST-REPORT, FRICTIONAL, SOURCES); the `.gitignore` rules for media and credentials. The A1 starter was Nik Bear Brown's [walker-jumpman](https://github.com/nikbearbrown/walker-jumpman).
- **Game rules:** [RULES.md](RULES.md) and [DESIGN-HISTORY.md](DESIGN-HISTORY.md) were written with Claude in a conversation on my other Claude account (Sep 29 – Oct 9, 2026) and handed over as files; [CLAUDE.md](CLAUDE.md) is that handoff brief.

## Generative models

*Filled in as each tool is used: name, version, where it ran, license or terms.*

| Category | Model / service | Version | Where it ran | License / terms |
|---|---|---|---|---|
| Art | | | | |
| Sound effects | | | | |
| Music | | | | |

No paid generation service or purchased credits are used. No prompt names a living artist, a copyrighted character, a brand, or existing music or recordings.

## Asset log

One row per generation that was kept or seriously considered. Rejected outputs are kept as thumbnails in `assets/rejected/`.

| Asset ID | Model and version | Prompt and settings | Outcome (judged against) | Edits | Where used |
|---|---|---|---|---|---|

## Tools

| Tool | Version | Use |
|---|---|---|
| Godot Engine | 4.7.2.stable.official.ed1daf0bf (Windows, standard build) | engine, headless tests, rasterizing check |
| Claude Code (Anthropic) | Claude desktop app, Claude Opus 5.5, Northeastern access | code, prompts, design sketches (SVG), document drafts |
| Python | 3.11.4 | design-sketch script (`design/tools/draw_sketches.py`) |
| Microsoft Edge (headless) | system install | rendering sketch SVGs to PNG |
| FFmpeg | 9.0.2 full build | audio trims, loop cuts, format conversion |

## Human and AI contributions

*Completed at the end; see FRICTIONAL.md for the running record.*
