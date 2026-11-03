# Lane Tactics — standing rules for agents

These rules hold for every assignment. `CLAUDE.md` imports this file on its first line and adds the current assignment's context; `CHANGE-BRIEF.md` is the current assignment's contract.

In an interactive session, read this file, `RULES.md` (the agreed game rules) and `DESIGN-HISTORY.md` (who decided what) first, then summarize your understanding back to the user and list anything unclear before doing any work. In a non-interactive run (`claude -p`), do not stop to summarize: do the task the prompt gives and report what you could not confirm.

## What this project is

A course project (CSYE 7270, Fall 2026) that is also the user's one game for the whole semester. Each assignment adds a layer to this repository and is submitted as a git tag (`a3`, `a5`, …).

**Lane Tactics** (working title): a turn-based tactics game on a 5-lane board, seen from above, with lanes like Plants vs Zombies and chess-like moves. Three unit types (archer, rider, shielder); both sides give orders at the same time; you win by getting a unit into the enemy's back row. The human plays against an AI. `GDD.md` is the whole design; `RULES.md` is the only source of truth for the rules.

## What exists

| Layer | Where |
| --- | --- |
| Rules, design history, GDD | `RULES.md`, `DESIGN-HISTORY.md`, `GDD.md` |
| A2: the 2D asset slice (1 player archer vs 1 enemy archer; generated art, sound and music) | `godot/game/`, `godot/assets/`, records in `SOURCES.md`, `TEST-REPORT.md`, `FRICTIONAL.md` |
| A3: three Blender assets in a 3D diorama | `godot/assets/models/`, `godot/diorama/asset_diorama.tscn`, `blender/`, `tools/blender/` |
| A4: the Game Design Document | `GDD.md` and its figures in `design/gdd/` |

## How to work with this user

- **Discuss and confirm before implementing.** The user's words: "If there are still things unclear or need my confirmation, discuss with me first." When the user doesn't mention one of your proposals in a reply, that means they accept it.
- Don't just agree. Analyze both the positive and negative effects of ideas.
- Ask when something is ambiguous, rather than assuming.
- Number your questions and attach a proposed default to each, so the user can answer briefly ("all fine except 3").
- **Frictional log** (`FRICTIONAL.md`), in the format used since Assignment 2: **Wanted**, **Asked**, **Got**, **Decided**, **Next**, **Human / Claude / model**, **Still unresolved**. The AI may write the factual lines (**Asked**, **Got**, **Human / Claude / model**) from the session record. The judgment lines (**Wanted**, **Decided**, **Still unresolved**) are the user's own words: leave them as `TO FILL` and never write them yourself.
- **Every `TO FILL`, in any document, gets a labelled hint draft beside it** (for example `> *Hint (Claude):* …`): what could be written there, so the user can learn from it and rewrite it in their own words. For values the course says must be computed by hand, the hint gives the method and the set-up, not the final numbers.
- **Hand-written files:** files in `godot/shaders/` are written by the user and are never edited by an agent. Other assignments may name more; their `CLAUDE.md` says so.
- **No personal information in anything committed:** no absolute paths from this computer, no Windows username, no email address. Write paths relative to the repository or as placeholders (`<repo>`, `<Godot>`). Scripts take tool paths from environment variables (for example `GODOT`).

## Technical context

- Godot **4.7.2** (standard build, not .NET), typed GDScript, Compatibility renderer, on **Windows 11**. The game is 2D; the A3 diorama is the 3D scene.
- Headless test scripts live in `godot/tests/` and write timestamped reports to `evidence/`. They are run through `scripts/run-test.sh` (see `CLAUDE.md` for the current commands).
- Windows problems seen so far:
  - Windows Defender's Controlled Folder Access blocks Python, Node and Git Bash tools inside `Documents`, so the repository lives outside it.
  - `core.autocrlf=true` changes line endings, so file hashes can't be reproduced byte for byte.
  - Pillow was not installed in Assignment 1.
- A GitHub PR from a fork once defaulted to the instructor's repository. Check the PR base repository every time.

## Design notes that shape art and code

- **Art:** units hop between squares, so no walk cycles; units only face left or right (flip the sprite).
- **Code:** the rules engine (`godot/game/rules.gd`) is plain data (board, units, orders → list of events), with no physics, deterministic, and tested headlessly. Presentation code may read game state; it never writes it.
- **Readability features the rules depend on:** order numbers over units during attack planning; arrows or shadows for contested moves; red squares for a rider's charge bonus; planned-move arrows and a friendly-fire warning.
- **Known risks:** the rules interact a lot; strike back on every hit can cause standoffs; ordering every unit every turn is tedious (default order "stay"); busy turns need fast-forward.

## Folders

- Game assets used by Godot: `godot/assets/`. Raw downloads: `assets/_raw/` (ignored). Rejected thumbnails: `assets/rejected/`.
- Sketches: `design/tools/draw_sketches.py` and `design/tools/draw_gdd_sketches.py` write SVGs; `bash design/tools/render_png.sh <folder>` renders PNGs (headless Edge).
- Films: `youtube/<film>/`; MP4 and MP3 files stay out of git.
