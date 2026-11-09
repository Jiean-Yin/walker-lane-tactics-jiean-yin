# CAPTURE — engine footage for the A6 film

All game pictures in this film are **real Godot renders** of an isolated copy of tag `a6`, as pushed to GitHub: commit `7f199f9` (tree `f336766`). Claude Code made them for the film on 2026-11-08. Nothing in the game was changed.

## The copy, and the history rewrite

**Filmed:** an archive of the local `a6` tag, made before the branch history was rewritten for its first push (TEST-REPORT A6.11).
- That tag's commit is `7876ed2` in the pushed history.
- `git -c core.autocrlf=false archive a6` into `<capture-copy>/a6`.
- Every one of the 131 `godot/` files matched its blob (`git hash-object --no-filters`): 0 mismatches.
- `--import` exited 0 on the first run, and every suite passed.

**Pushed tag:** `a6` at `7f199f9`. The copy was extracted again into `<capture-copy>/a6`, and all 131 `godot/` files match its blobs.
- Its `godot/` tree (`f66b358`) is the same as `7876ed2`'s.
- It differs from the filmed archive in one file only: `effects/ATTRIBUTION.md`, where the rewrite remapped two quoted commit IDs. The game never loads that file.
- Every scene, script and test is byte-identical, so the footage stands for the pushed tag.
- Commit IDs that the film quotes on screen are the pushed history's.
- The film's code excerpts, quotes and evidence hashes are all read from the pushed tag's copy.

**Suites on the pushed tag's copy:** `--import` exited 0 on the first run. Then every suite ran through `scripts/run-test.sh` (`capture/film-rerun.txt`). No `SHADER ERROR` or `SCRIPT ERROR`. The counts match TEST-REPORT A6.11:

  | Suite | fps | Result |
  |---|---|---|
  | test_rules | 60 | 51/51 |
  | test_audio_events | 60 | 70/70 |
  | check_assets | 60 | 38/38 |
  | test_exposed_tint | 30, 60, 144 | 46/46 each |
  | test_materials | 60 | 148/148 |
  | test_hit_burst_config | 60 | 107/107 |
  | test_arrow_trail_config | 60 | 135/135 |
  | test_hit_burst_state | 60 | 31/31 |
  | test_arrow_trail_state | 60 | 31/31 |
  | cost_effects | 60 | 25/25 |

- Capture copy: `<capture-copy>/capture-godot` = the filmed copy's `godot/` plus `film/a6_capture_driver.gd`. The driver is a harness only, kept here as `capture/a6_capture_driver.gd`.

## The driver and the runs

`capture/a6_capture_driver.gd` runs with the windowed Godot 4.7.2 build under **Movie Maker** (`--write-movie … --fixed-fps <fps>`).
- `game/main.tscn` is instanced unchanged in a 3840 × 2160 SubViewport. The SubViewport draws the 1280 × 720 canvas scaled up (`size_2d_override`), as the window's `canvas_items` stretch would.
- Every recorded frame is piped to ffmpeg as a lossless FFV1 master.
- Keys go in as real key presses into the SubViewport (`push_input`), the way the game's tests press them. They play the win route the A6 state tests play (`tests/fixtures/win_route.json`).
- The driver reads state only, to log it and to know when to press the next key.
- Every engine frame is logged: state, arrows, live bursts and trails, and hits.
- The driver fails on any skipped draw or failed expectation.

| Mode | Movie Maker | Engine frames | Master frames | Shots | Expectations |
|---|---|---|---|---|---|
| `play` | `--fixed-fps 30` | 1623 | 1359 | `P0_title` 0–30, `P1_turns_1_3` 30–150, `P2_turn4_two_hits` 150–362, `P3_turn5_kill` 362–527, `P4_pause_burst` 527–979, `P5_pause_flight` 979–1359 | all 8 OK (no effect in turns 1–3; 2 bursts and 2 trails in turn 4, 2 alive at once; 3 bursts in run 1; no burst or trail left after play again, twice; a burst alive while paused; a trail alive while paused) |
| `slow` | `--fixed-fps 120` | 1476 | 1133 | `S2_turn4_two_hits` 0–700, `S3_turn5_kill` 700–1133 | OK (3 bursts, 3 trails) |

- **Slow mode** shows the 120 fps frames at 30 fps, so ¼ speed. Every such segment says "¼ SPEED" on screen.
- **Where the recording breaks:** play master frames 527 and 979, where unrecorded turns were played (checked in the logs). Slow has no break. No footage segment crosses a break.
- **Masters** (not in git): `play-4k.mkv` and `slow-4k.mkv`. SHA-256 in `capture/masters-sha256.txt`.
- Per-frame logs: `capture/<mode>-log.jsonl`. Shot ranges: `capture/<mode>-summary.json`. Godot output, paths replaced by `<capture-copy>`: `capture/<mode>-stdout.log`.

**Pilot → final.** A pilot on a copy of commit `d7845ac` (pushed-history ID), before the tag existed, tested the driver and the script's observation sentences (`capture/PILOT.md`). No pilot frame is used. In the final run:
- each pause has its own turn: run 2, mid-burst; run 3, mid-flight;
- the holds are sized to the measured narration of B06 (14.4 s) and B14 (15.5 s), so no footage is retimed.

## What the logs show

| | play (30 fps) | slow (120 fps) |
|---|---|---|
| Turn 4, the enemy's arrow | appears 249, hit on the player 259 | 249, hit 290 |
| Turn 4, the player's arrow | appears 280, hit on the enemy 290 | 375, hit 417 |
| Trail stops emitting | 259, 290: on the hit's frame | 290 (on the hit); 416, **one frame (1/120 s) before** the hit at 417 |
| First burst freed | 297, 38 frames (1.27 s) after its hit | 436, 146 frames (1.22 s) after its hit |
| Two bursts alive | 290–297 | 417–436 |
| Turn 5, the killing hit | arrow 431, hit 441 | arrow 868, hit 909 |
| Run 2, P mid-burst | hit 636, P 645, unpause 840 (6.5 s); burst alive and still throughout | — |
| Run 3, P mid-flight | arrow 1078, P 1083 (t = 0.167 s), unpause 1233 (5 s), hit 1238 | — |

- **Positions** on the 1280 × 720 canvas: the burst on the player is at (320, 594) and on the enemy at (576, 498), each the archer's base + (0, −40).
- **Dot spacing:** the trail draws as a row of dots about 20–25 px apart, the same at 30 and at 120 fps (the GPU particles step at `fixed_fps` 30).

## Crops

All crops are of the 4K frame, scaled to fill, and labelled on screen.
- **3×, `[240, 1362, 1280, 720]`:** the player's archer and its square (B04). The enemy's archer is outside the frame.
- **2×, `[384, 990, 1920, 1080]`:** both archers and the arrow's arc (B08, B12, B14).

## Jiean's own captures

Shown as labelled fixture stills: B10, B16, B26. They are Jiean's Movie Maker strips from the preview scenes (fixed seed), committed under `captures/` at tag `a6`.
