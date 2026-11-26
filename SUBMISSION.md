# SUBMISSION — Assignment 7: Doing Animation with Claude and Godot

The earlier submission files are kept as [SUBMISSION-A6.md](SUBMISSION-A6.md), [SUBMISSION-A5.md](SUBMISSION-A5.md), [SUBMISSION-A3.md](SUBMISSION-A3.md) and [SUBMISSION-A2.md](SUBMISSION-A2.md).

| Field | Value |
|---|---|
| Assignment | Assignment 7 - Doing Animation with Claude and Godot |
| Student | Jiean Yin |
| Project name | walker-lane-tactics-jiean-yin (Lane Tactics) |
| GitHub repository URL | https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin |
| Git tag and submitted commit SHA | tag `a7` (SHA to be filled in after tagging and the fresh-clone check; the Canvas note gives the final submitted commit) |
| Game-source revision shown in the film | to be filled in with the film |
| Godot version, renderer, and operating system | Godot 4.7.2.stable.official.ed1daf0bf (standard build), **Compatibility** renderer (OpenGL 3.3), Windows 11 Home 10.0.26200 |
| Sprite clip: route, node, scene, frame rate | `wave`: **Sprite2D with an AnimationPlayer frame track**. Node `GoalFlag/FlagSprite` (`hframes` 4 × `vframes` 1) in `godot/game/goal_flag.tscn`, instanced in `godot/game/main.tscn`. Clip `godot/animations/wave.tres`, **8 fps**, `LOOP_LINEAR`, with a discrete `offset` track for the sheet's pole drift. |
| Rig clip: route, rig source, node, scene, frame rate | `shoot`: **cutout rig keyed as resource text**. Source: three `region_rect` crops of the A2 archer draw art under `Node2D` pivots (`Mount/Rig`, `Rig/Upper`, `Upper/Bow`). Scene `godot/game/archer_rig.tscn`, instanced by each `piece.gd`. Clip `godot/animations/shoot.tres`, **60 fps** (step 1/60), startup 12 / active 21 / recovery 15 frames, `LOOP_NONE`. |
| Which clip loops and which commits | `wave` loops; `shoot` commits |
| The one authority over each animated node | `FlagSprite` (`frame`, `offset`): the flag's `AnimationPlayer` (autoplay, `IDLE`). `Rig`, `Upper`, `Bow`: the rig's `AnimationPlayer` (`MANUAL`), started, stopped and advanced only by `piece.gd`, which reads its own pose set by `main.gd`'s cue list. `Mount` (place, scale, facing, visibility): `piece.gd`. |
| Sprite sheet source and licence (or model, version, and terms) | "Flag Animation Sheet" by Fokko, OpenGameArt, **CC0**, checked 2026-11-25; the original file is committed as downloaded (`godot/assets/art/flag/ATTRIBUTION.md`). No generative model. |
| Final film URL and filename | to be added (the film comes after the submission of the source) |
| Final film SHA-256 | to be added |
| Summary of my work | **TO FILL** (Jiean) |
| Known limitations | The release barely shows (recoil about 1.5 screen px). The rig is cut from one pose drawing, so the bow drop is kept small (8°). The flag waves in real time, by design. The shot's end pose shows for 0 or 2 frames because the game's cues land ±1 frame. The swap to the idle art is a pose pop. (README, TEST-REPORT A7.18) |
| Changed games since Assignment 2 (yes/no; if yes, FRICTIONAL.md entry) | No: still Lane Tactics |

> *Hint (Claude) for "Summary of my work":* In your own words, as in A6: what you chose and measured (the two clips, the sheet, the five reference frames, the phase table and frame 40), what you predicted, what you approved, what you saw and decided in tuning (r1 keep), and which human checks you ran.
