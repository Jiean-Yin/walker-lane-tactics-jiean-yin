# CAPTURE — engine footage for the A7 film

All game pictures in this film are **real Godot renders** of an isolated copy of tag `a7`, as pushed to GitHub: commit `37c4698` (tree `dd91e92`). Claude Code made them for the film on 2026-11-26. Nothing in the game was changed.

## The copy

- `git -c core.autocrlf=false archive a7` into `<capture-copy>/a7`.
- All 163 `godot/` files match their `a7` blobs (`git hash-object --no-filters`): 0 mismatches.
- `--import` exited 0 on the first run. Every suite then ran through `scripts/run-test.sh` (`capture/film-rerun.txt`). There was no `SHADER ERROR`, `SCRIPT ERROR` or `Failed loading resource`, and the counts match TEST-REPORT A7.19:

  | Suite | fps | Result |
  |---|---|---|
  | test_rules / test_audio_events / check_assets | 60 | 51/51, 70/70, 38/38 |
  | test_materials / test_hit_burst_config / test_arrow_trail_config | 60 | 148/148, 107/107, 135/135 |
  | test_hit_burst_state / test_arrow_trail_state / cost_effects | 60 | 31/31, 31/31, 25/25 |
  | test_pins_a7 / test_flag_readback / test_shoot_readback | 60 | 29/29, 43/43, 51/51 |
  | test_anim_states / test_shoot_edges | 60 | 51/51, 102/102 |
  | test_exposed_tint | 30, 60, 144 | 46/46 each |

- **Capture copy:** `<capture-copy>/capture-godot` is the filmed copy's `godot/` plus `film/a7_capture_driver.gd`. The driver is a harness only; it is kept here as `capture/a7_capture_driver.gd`, adapted from the A6 film's driver.

## The driver and the runs

`capture/a7_capture_driver.gd` runs with the windowed Godot 4.7.2 build under **Movie Maker** (`--write-movie … --fixed-fps <fps>`).
- `game/main.tscn` is instanced unchanged in a 3840 × 2160 SubViewport. The SubViewport draws the 1280 × 720 canvas scaled up (`size_2d_override`).
- Every recorded frame is piped to ffmpeg as a lossless FFV1 master.
- Keys go in as real key presses into the SubViewport (`push_input`), playing the win route the A7 tests play.
- The driver only reads state: poses, the read-only `piece.rig_snapshot()`, and the flag's cell. It logs every engine frame and fails on any skipped draw or failed expectation.

| Mode | Movie Maker | Engine frames | Master frames | Shots | Expectations |
|---|---|---|---|---|---|
| `play` | `--fixed-fps 30` | 1540 | 1276 | `P0_title` 0–120, `P1_turns_1_3` 120–240, `P2_turn4_two_shots` 240–452, `P3_turn5_kill` 452–617, `P4_pause_each_phase` 617–1084, `P5_restart_mid_shot` 1084–1276 | all 7 OK: no shot in turns 1–3; 2 shots in turn 4; 3 in run 1; paused in e1's startup, in e1's active phase and in p1's recovery; R mid-shot restarts with no shot left |
| `slow` | `--fixed-fps 120` | 983 | 640 | `S2_turn4_two_shots` 0–640 | OK (2 shots) |

- **Slow mode:** its 120 fps frames are shown at 30 fps, so ¼ speed. Every such segment says "¼ SPEED" on screen.
- **Where the recording breaks:** play master frames 617 and 1084, where unrecorded turns were played (checked in the logs). Slow has no break. No footage segment crosses a break.
- **Masters** (not in git): `play-4k.mkv` and `slow-4k.mkv`, SHA-256 in `capture/masters-sha256.txt`.
- **Records:** per-frame logs in `capture/<mode>-log.jsonl`, shot ranges in `capture/<mode>-summary.json`, Godot output in `capture/<mode>-stdout.log` (paths replaced by `<capture-copy>`).
- **No pilot.** One run per mode. Every observation sentence was checked against frames of these masters (`capture/OBSERVATIONS.md`), and none had to change.

## What the logs show (master frames)

| | play (30 fps) | slow (120 fps) |
|---|---|---|
| Turn 4, e1's shot | draw 333, arrow leaves ≈ 339, hit on p1 349, back to idle 357 | draw 225, hit 290, idle 321 |
| Turn 4, p1's shot | draw 364, hit on e1 380, idle 388 | draw 351, hit 417, idle 447 |
| Turn 5, p1's killing shot | draw 515, hit 531, idle 539 | — |
| Run 2, P in each phase | e1 draw 710; P 712–802 (startup), 811–901 (active), 939–1029 (p1's recovery) | — |
| Run 3, R mid-shot | e1 draw 1177, R 1186 → turn 1, no shot left | — |
| The flag while paused | its cell changes 72 times over the three 3 s pauses | — |

## Crops

All crops are of the 4K frame, scaled to fill, and labelled on screen.
- **Flag, 3×:** `[2560, 880, 1280, 720]`, the GoalFlag and the board's right edge (B04).
- **Both archers, 2×:** `[384, 990, 1920, 1080]` (B11, slow).

## Jiean's own captures

Shown as labelled fixture stills: B06, built from `captures/flag_registration_r1.png`, and B19, built from `captures/shoot/r0` and `r1`. Both are Jiean's Movie Maker strips from `shoot_preview.tscn`, committed at tag `a7`.
