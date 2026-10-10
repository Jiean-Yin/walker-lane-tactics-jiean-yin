# Lane Tactics — project brief for Claude Code

Read this file first, then `RULES.md` (the agreed game rules) and `DESIGN-HISTORY.md` (how each rule was decided and by whom). Before doing any work, summarize your understanding back to the user and list anything unclear.

## What this project is

A course assignment that also becomes the user's game project for the rest of the semester. The assignment text, verbatim:

> Pick the game you actually want to build. Design its look and sound on paper first, then use generative models to make the art, sound effects, and music, then prove them in a small playable Godot scene. The design lives in a short concept, a storyboard, and a character sheet. The generation is logged prompt by prompt, including what you threw away and why. The result is judged in the running scene, not in the image folder. Your Frictional log is where the design thinking shows: what you wanted, what the model gave you, and what you decided.

The chosen game is **Lane Tactics** (working title): a turn-based tactics game on a 5-lane board, viewed from the top, with lanes like Plants vs Zombies and moves like chess pieces. There are three unit types (archer, rider, shielder). Both sides give orders at the same time, and you win by getting a unit into the enemy's back row. The human plays against an AI.

## Current status (Oct 9, 2026)

| Item | Status |
| --- | --- |
| Genre and core idea | Decided |
| Game rules | Agreed and confirmed by the user: `RULES.md` is the source of truth |
| Numbers (health, damage, pool size…) | First guesses only, to be tuned in playtesting |
| Check against the full project requirements | Not done yet; the user will do it |
| Concept, storyboard, character sheet | Not started |
| Art, sound effects, music generation | Not started; no tools chosen yet |
| Godot project | Not started |

## Suggested next steps (not yet agreed with the user)

1. The user checks `RULES.md` against the full project requirements.
2. Test the rules on paper for 3–4 turns (graph paper and coins) before writing code. This is cheap, and it catches rule problems early, such as standoffs caused by strike back or confusing attack order.
3. Write the short concept, the storyboard (one turn playing out, shown shot by shot), and the character sheet (every pose each unit needs: idle, attack, hurt, death).
4. Generate the art, sound effects and music, logging every prompt, including rejected results and why they were rejected.
5. Build a small playable Godot scene that proves the look and sound. Possible first scope: a 5 × 7 or 5 × 8 board, a simple AI, and a fast-forward button for combat playback.

## How to work with this user

- **Discuss and confirm rules before implementing them.** The user's words: "If there are still things unclear or need my confirmation, discuss with me first." When the user doesn't mention one of your proposals in a reply, that means they accept it.
- Don't just agree. Analyze both the positive and negative effects of ideas.
- Ask when something is ambiguous, rather than assuming.
- Number your questions and attach a proposed default to each, so the user can answer briefly ("all fine except 3").
- **Frictional log:** follow the Assignment 1 format. Each entry has **What happened**, **Expected** and **Learned / still unsure**. The AI may write "What happened" as a factual record. The "Expected" and "Learned" lines are the user's own words; leave them as `TO FILL` and never write them yourself.

## Technical context from Assignment 1 (walker-jumpman extension)

- Godot **4.7.2** (standard build, not .NET), typed GDScript, 2D, on **Windows 11**.
- Pattern carried over from Assignment 1: headless test scripts under `godot/tests/`, run with `Godot_v4.7.2-stable_win64_console.exe --headless --path godot --script res://tests/<test>.gd`, which write timestamped reports to `evidence/`.
- Windows problems seen in Assignment 1:
  - Windows Defender's Controlled Folder Access blocked Python, Node and Git Bash tools inside `Documents`, so they worked in `C:\dev` instead.
  - `core.autocrlf=true` changes line endings, so file hashes can't be reproduced byte for byte.
  - Pillow was not installed.
- In Assignment 1, a GitHub PR from a fork defaulted to the instructor's repository. Check the PR base repository every time.

## Design notes that shape art and code

- **Art:** turn-based play means units hop or slide between squares, so no walk cycles are needed. With horizontal lanes, units only face left or right (flip the sprite). That works out to about 3–4 poses per unit type, a realistic amount of generated art to keep consistent. The visual style has not been chosen yet.
- **Code:** write the rules engine as plain data (board, units, orders → result), with no physics, deterministic, and tested headlessly. Expect the order-input and preview interface to be the biggest job.
- **Readability features the rules depend on:**
  - order numbers over units during attack planning
  - arrows or shadows showing contested moves
  - red squares marking where a rider's charge bonus applies
  - planned-move arrows and a friendly-fire warning
- **Known risks:**
  - The rules interact a lot and are hard to predict.
  - Striking back on every hit can lead to standoffs.
  - Giving every unit an order each turn is tedious; the default order is "stay".
  - A busy turn means a long combat playback, so add fast-forward.

## Where the rules came from

The rules were worked out in a Claude conversation on the user's other account, in a Claude Docs page called "Lane Tactics — Rules Draft". That page may not be readable from this account. From now on, edit `RULES.md` in this repository and treat it as the only source of truth, so the two copies don't drift apart.

## Status update (Oct 9, 2026, in this repository)

- The repository is `C:\dev\walker-lane-tactics-jiean-yin` (Controlled Folder Access blocks `Documents`).
- Assignment 2 scope was agreed: see CHANGE-BRIEF.md (a slice with one player archer vs two enemy archers, using a subset of RULES.md). The design docs (CONCEPT, STORYBOARD, CHARACTER-SHEET, CHANGE-BRIEF) were committed before any generation.
- Sketches: `design/tools/draw_sketches.py` writes the SVGs; `bash design/tools/render_png.sh` renders the PNGs (headless Edge).
- Game assets used by Godot live in `godot/assets/`; raw downloads go in `assets/_raw/` (ignored); rejected thumbnails go in `assets/rejected/`.
- Frictional: judgment lines stay `TO FILL`, with a labeled hint draft for the user to replace.
