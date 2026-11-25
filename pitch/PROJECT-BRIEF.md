# PROJECT-BRIEF — Lane Tactics, final project pitch

*Assignment 8, 2026-11-24. Jiean chose the project and accepted each answer below (2026-11-24, "Defaults fine, go"); Claude Code drafted the wording from Jiean's answers and the repository. Past tense only for what exists at a tag; everything else is "will".*

**Stack:** Godot 4.7.2 standard (not .NET), typed GDScript, **Compatibility** renderer (`godot/project.godot:25`), export target **Windows desktop** (an export has not been attempted yet). Claude Code for agent work.

## 1. What is it?

Lane Tactics is a turn-based tactics game where both sides give their orders at the same time on a five-lane board, and you win by getting a piece into the enemy's back row. When it is done, it **will be a Windows desktop build of one level**, from title screen to end screen: you against the AI, with all three unit types (archer, rider, shielder), plus a test report a stranger can rerun.

## 2. Why would anyone care?

It gives a player who likes short tactics puzzles the tension of **guessing what the opponent will do this turn**, because both sides commit at once and the moves resolve together.
- **Plants vs Zombies** has the lanes, but you react to waves; nobody out-guesses you.
- **Into the Breach** shows you the enemy's moves before you act, so it is a puzzle with full information. Lane Tactics hides the enemy's orders until both sides have committed.
- What is mine: one rules engine (`godot/game/rules.gd`) that is plain data in, events out, deterministic and tested headlessly, so every rule interaction can be pinned by a test.

## 3. Who opens it, and what do they do?

- **Target role:** gameplay programmer. **Reader:** a lead engineer (or a hiring manager passing it to one).
- **First sixty seconds:** they run the export, press a key on the title screen, and give one archer an order; the on-board markers show the move and the target, so no manual is needed. Then they open `TEST-REPORT.md` and rerun one suite with one command.

## 4. What does it prove about me?

| Skill | Evidence that will back it |
|---|---|
| Gameplay rules and state | `rules.gd` with pinned behaviour tests for every unit interaction (today 51 checks, archers only, `test_rules.gd`) |
| Shaders and materials | the "exposed" tint and linen board (tag `a5`), material checks (148) |
| Particle effects | hit burst and arrow trail (tag `a6`), config and state tests, measured price |
| Animation and state | Assignment 7 clips, pinned by state tests (will exist) |
| Profiling | headless CPU price plus Visual Profiler GPU time on one named laptop GPU (done for A6; will be repeated on the export) |
| Verification habits | headless suites, Movie Maker captures, Jiean's own playtest for what tests cannot judge, and agent briefs with scoped tools (`CHANGE-BRIEF.md`, `AGENTS.md`) |

A reviewer could fairly conclude: I can build a small, testable rules engine and keep presentation (shaders, particles, animation) from changing game state. They could not conclude I can ship a big game: this is one level.

## 5. In, out, first

- **In:** one level, three unit types, the AI opponent, title and end screens, a keyboard menu, saved settings.
- **Out (deliberately):** no multiplayer, and only one of the four campaign episodes in `GDD.md` (no hills, night raid or giant).
- **First:** the full turn loop with all three unit types against the AI on one board. **How anyone would know it ran:** a new headless test plays complete matches through the real key path and checks that each one ends in a win or a loss, and a Movie Maker capture shows one match.

## 6. What could sink it?

The rules interact a lot. Every hit triggers a strike back, so two shielders or two archers facing each other could **stall a match forever** (a known risk in `AGENTS.md`). What I will do: pin each pair interaction in `test_rules.gd`, and run an AI-against-AI soak test that counts matches still going after 40 turns; if any stall, change the rule in `RULES.md` first and log it in `FRICTIONAL.md`.

## 7. Why this project?

A mix: half showing what I can already do, half learning.
- **Already have, with evidence:** shaders (tag `a5`), particle effects and their price (tag `a6`), headless tests and test reports (`TEST-REPORT.md`), Blender assets (tag `a3`).
- **New to me:** animation clips and an animation state machine (A7), an AI that plays three unit types, a desktop export, and a save system.

---

## Exists today

| Thing | Where to see it |
|---|---|
| 1 player archer vs 1 enemy archer on the five-lane board, with generated art, sound and music | `film-source-v1` (`fcf33ef`) |
| Three Blender assets in a 3D diorama | tag `a3` (`090d157`) |
| The game design document | `GDD.md` (in `main`) |
| Danger tint and linen board shaders | tag `a5` (`ef5d38b`) |
| Hit burst and arrow trail, with tests and price | tag `a6` (`7f199f9`) |
| A simple enemy AI (march or guard, shoot if in range) | `godot/game/rules.gd:208-238` at tag `a6` |
| Headless suites: rules 51, audio 70, assets 38, tint 46, materials 148 | `TEST-REPORT.md`, `evidence/a6/` |

## Will exist

- Rider and shielder units, with rule tests for every pair.
- An AI that orders all three unit types.
- Title → level → end screen, keyboard menu, saved settings.
- Animation clips (Assignment 7).
- A Windows desktop export and a fresh-clone test report.
- The AI-against-AI stall test.
