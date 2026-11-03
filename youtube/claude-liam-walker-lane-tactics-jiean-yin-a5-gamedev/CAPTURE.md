# CAPTURE — engine footage for the A5 film

All game and 3D pictures in this film are **real Godot renders** of an isolated copy of tag `a5` (`ef5d38b`), made for the film on 2026-11-03 by Claude Code. Nothing in the game was changed.

## The copy

- `git -c core.autocrlf=false archive a5 godot scripts evidence/a5 …` into `<capture-copy>/a5`. Every one of the 111 `godot/` files was checked against its `a5` blob (`git hash-object`): **0 mismatches**.
- `--import`, then every suite through `scripts/run-test.sh` on that copy: test_rules 51/51, test_audio_events 70/70, check_assets 38/38 at 60 fps; test_exposed_tint 46/46 at 30, 60 and 144 fps; test_materials 148/148; no `SHADER ERROR` (`capture/film-rerun.json`).
- Capture copy: `<capture-copy>/capture-godot` = that `godot/` plus `film/a5_capture_driver.gd` (harness only, kept here as `capture/a5_capture_driver.gd`).

## The driver and the runs

`capture/a5_capture_driver.gd`, run with the windowed Godot 4.7.2 build under **Movie Maker** (`--write-movie … --fixed-fps 30`). The real scene is instanced unchanged in a 3840 × 2160 SubViewport; every frame is piped to ffmpeg as a lossless FFV1 master. For the 2D game the SubViewport draws the 1280 × 720 canvas scaled up (`size_2d_override`), as the window's `canvas_items` stretch would. The driver fails on any skipped draw and logs every frame's state.

| Mode | Scene | What the driver does | Frames | Master SHA-256 (not in git) |
|---|---|---|---|---|
| `tint` | `game/main.tscn` | presses real keys into the SubViewport (Enter, Right/Left, P), the way the game's tests do; reads state only to log it and to know when a turn starts | 997 | `f999be18977b…52d` |
| `diorama` | `diorama/asset_diorama.tscn` | the scene's own camera, then one harness camera; changes uniforms on the loaded materials **in memory only**; one shot replaces the shared Shader's code in memory (ALBEDO × 0.5), then restores it. No file is saved; the `.gdshader` file is not touched | 1245 | `59ee2fc388bd…0dd` |
| `hint` | `hint/hint_experiment.tscn` | its own orthographic camera; reads the bands from the 4K frame | 120 | `c65a12ae9b57…6c0` |

Full hashes: `capture/masters-sha256.txt`. Per-frame logs: `capture/<mode>-log.jsonl`; shot ranges: `capture/<mode>-summary.json`.

**Run 01 → run 02.** Run 01 (same day) was too far from the tiles for the weave to read, and its roughness shot guessed the lamp's mirror angle by hand (no visible change). Run 02 moved the harness camera closer, computed the mirror direction from the lamp's own transform, and lengthened the holds so each shot covers its measured narration (footage is never retimed). Only run 02 is used.

## What the logs show (tint, run 02)

- Rise and fall take 6 frames at 30 fps (0 → 0.1667 → … → 1.0), from frame 245 and frame 365.
- Taps every 0.1 s: the value turns around from where it is.
- `P` mid-fall holds the value for 60 frames (PAUSED overlay), then the fall finishes.
- Enter: the value falls during `PLAY_MOVES`; turn 4 starts in reach and it rises at once.
- The enemy's `exposed_amount` is 0.0 in every logged frame.

## Roughness: measured, not judged

From the lamp's mirror angle (computed from `Lamp.global_basis`), frames at `roughness_scale` 1 and 0 were compared over the tile's centre: mean luminance 0.657 → 0.647 (about 1.5 % darker), **no pixel brighter**. Jiean's editor check recorded "shiny like plastic". The film states both; the cause is not established.

## Jiean's own captures

`evidence/a5/captures/exposed_*.png` (key C in `debug/capture_exposed.tscn`, a real window outside the editor, 2026-11-02 22:57) and `os_screenshot.png` with `os_compare.log`, as committed at tag `a5`. Shown in B07 as stills, cropped (nearest-neighbour ×5.8) around the archer.
