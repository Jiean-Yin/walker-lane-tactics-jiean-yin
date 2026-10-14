# CAPTURE — Lane Tactics gamedev film

## Game revision captured

| Field | Value |
|---|---|
| Repository | https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin |
| Tag / commit | `film-source-v1` (annotated tag object `33356773…`) → commit `fcf33eff6c501d32624532ca197257a646552991`; `godot/` is identical to `12f7283` (`git diff 12f7283 film-source-v1 -- godot` is empty) |
| Engine | Godot 4.7.2.stable.official.ed1daf0bf, Compatibility renderer (OpenGL 3.3, NVIDIA GeForce RTX 3070 Ti Laptop GPU) |
| OS | Windows 11 Home 10.0.26200 |
| `build_id` | `706032df5f992ed7fc955ab3f2663c0cd2f9089669307b529b0344bfae310a68` = SHA-256 of [capture/source-snapshot.txt](capture/source-snapshot.txt), which is `git ls-tree -r film-source-v1 godot \| sort -k4` (62 entries incl. `.uid`) |

All 51 authored files in the repository's `godot/` working tree are byte-identical to the tag's blobs (checked file by file before hashing for `gamedev-evidence.json`).

## Isolated copy

`git archive film-source-v1 godot` was extracted to `<capture-copy>\film-source-v1-godot\` (outside the repository and outside `Documents`), then imported headless. One harness file was added to the copy only: `film/film_capture_driver.gd` (SHA-256 `04aa453d…`, copied here as [capture/film_capture_driver.gd](capture/film_capture_driver.gd)). No game file was changed; no game setting was overridden (no `override.cfg`, `main.time_scale` stays 1.0, no test flags).

Existing tests on the isolated copy (2026-10-13): `test_rules.gd` **51/51**, `test_audio_events.gd` **70/70** (logs: [capture/test_rules.log](capture/test_rules.log), [capture/test_audio_events.log](capture/test_audio_events.log)). Both print the engine's shutdown warnings (`resources still in use at exit`) also seen in TEST-REPORT §1.

## Command

```bash
<Godot>/Godot_v4.7.2-stable_win64.exe --path film-source-v1-godot \
  --write-movie <capture-copy>/run-03/run-03.avi --fixed-fps 30 \
  --script res://film/film_capture_driver.gd -- full <capture-copy>/run-03 <ffmpeg.exe>
```

- **Movie Maker** (`--write-movie … --fixed-fps 30`) runs the engine at a fixed 1/30 s per frame and records the engine's own audio mix (AudioServer → PCM 48 kHz stereo, 1600 samples per frame) with the picture. This is offline rendering (73 s wall time for 55.7 s of game time), **not evidence of real-time frame rate**.
- **Why a SubViewport too:** the window (and therefore Movie Maker's picture) is 1280×720 on this 1920×1080 laptop. The driver runs the real `res://game/main.tscn` inside a **3840×2160 SubViewport** with `size_2d_override = 1280×720` and `size_2d_override_stretch = true` (the project's own canvas_items stretch), and shows that SubViewport in the window through a TextureRect. So the AVI is a 720p picture of the same frames, and every SubViewport frame is also read back and piped raw (RGBA) into ffmpeg as a **lossless FFV1 4K master** (`run-4k.mkv`, bgr0). Text, board, HUD and sprites are rasterised at 4K; the only enlarged element is the game's own 1280×720 `env_table.png` background (shown 3×).
- **Input:** `InputEventKey` press + release pushed into the SubViewport (main.gd's `_unhandled_input`) at normal simulation speed. Route moves and targets come from `tests/fixtures/lose_route.json` and `win_route.json`; scripted "thinking" pauses (0.9–1.8 s) only keep markers on screen — planning has no clock in this slice. The driver only reads state (`state_name()`, `planned_offset`, `selected_target()`, counters) to decide when to press. No teleporting, no Rules calls, no state writes.
- **Logging:** every key, every rules event shown by playback (`main.played_events`), every SFX trigger (`AudioDirector.play_log`) and every music state change, against the captured frame index: [capture/run-03-inputs.jsonl](capture/run-03-inputs.jsonl). A logged frame F is the first picture that shows the effect.
- **Assertions:** 22 expectations (routes followed, LOST "shot by the enemy archer in lane 4", lose sounds HOP 7 · HIT 1 · HURT 2 · WIN 0, music faded and stopped, retry restarts music, F3 shown, WON by elimination on turn 5, win sounds HOP 5 · HIT 2 · HURT 1 · WIN 1, music stopped, win pose, results card). All passed: [capture/run-03-summary.json](capture/run-03-summary.json). The driver quits nonzero on any failure or any skipped draw (process frame must advance by exactly 1 per captured frame).

## Run content (run-03, 1672 frames = 55.73 s)

| Frames | Content |
|---|---|
| 0–89 | Title, music playing |
| 90–149 | Enter → board at turn 1 |
| 150–702 | **Lose route** (naive: step forward every turn). T3 exchange (player first: HIT then HURT), T4 enemy first: player killed before its shot |
| 703–811 | Defeat card; music fades out (0.5 s) and stops |
| 812–967 | R → retry board (retries 1, music restarts); F3 footprints on 860–943 |
| 968–1496 | **Win route**: T1–T3 stay (enemy hops), T4 step in (HOP, HOP), enemy first (HURT), player (HIT); T5 player first (HIT, kill) |
| 1497–1593 | WON: music stops, SFX-WIN, win pose, win card |
| 1594–1671 | Results card |

## Captures and hashes

| File (kept locally, not in git) | SHA-256 |
|---|---|
| `<capture-copy>\run-03\run-03.avi` (MJPEG 1280×720 + PCM 48 kHz, 1673 frames) | `7c914575139e28b5e4123ae6825cfab5a2f9e4bc89c80db43bbca581123f7658` |
| `<capture-copy>\run-03\run-4k.mkv` (FFV1 3840×2160, 1672 frames) | `2f6c4cbffaef36973c2998dd7e2b71a871a5ae5f1856a0ae66eda20599f0f7da` |

**Same-run join check:** each 4K master frame *i* was downscaled and compared with AVI frame *i* over the whole run: mean absolute difference 0.79 grey levels (max 1.0, MJPEG noise); the ±1-frame offsets reach 73. The AVI's 1673rd frame is the extra frame Movie Maker writes at quit. So 4K frame *i* and AVI audio samples *i*·1600 … (*i*+1)·1600 come from the same engine iteration.

**Audio check (AVI):** music plays under every take (about −26 dB RMS) and for 15 of the run's 19 logged SFX triggers the largest energy jump lies 3–28 ms after the logged frame; the other 4 are hops inside pairs 0.13 s apart, where the neighbouring hop's jump is larger (energy check, not kept in git); for the film segment the game's own SFX files are matched by normalised cross-correlation in `_qc/audio-check-B14.json` (7/7 found, 1–11 ms after the logged frame, in the logged order).

**Discarded takes:** run-01 (same driver, win route before lose route; re-ordered so the naive loss comes first and F3 sits on the fresh retry board) and run-02 (rules-event log stopped after retry because the scene clears `played_events`; driver fixed). Both deleted; no frame of either is in the film. Probe runs (2 s) checked size, readback speed and alignment. A first probe that saved PNG frames on worker threads stalled and was killed.

## From capture to film

Gameplay beats are exact frame ranges of `run-4k.mkv` (`-ss a/30`, `-frames:v n`, H.264 crf 10, 30 fps), with no speed change. The only addition is our burned label in the HUD gap (x 1700–2760, y 112–262 at 4K). Per-beat records with hashes: [capture/clips.json](capture/clips.json).

| Beat | Frames | Seconds | Audio in the clip |
|---|---|---|---|
| B03 | 0–327 | 10.933 | none (narration only) |
| B11 | 328–549 | 7.400 | none |
| B13 | 550–811 | 8.733 | none |
| B09 | 812–1027 | 7.200 | none |
| B14 | 1089–1593 | 16.833 | **AVI samples 1,742,400–2,550,400, ALAC (lossless); decoded samples identical to the AVI's** |

B14 is the slice-audio segment: `kind: source_report`, `clock: source`, `audio_policy: preserve` — the compiler's supported way to keep a clip's own audio with no retiming and no narration. No sound was added, replaced, mixed, retimed or gain-changed. Its loudness is −16.2 LUFS integrated; Liam's narration measures about −24.5 LUFS, so the segment is about 8 LU louder (flagged at the approval gate, not changed).

Narrated gameplay beats carry narration only; the game's audio is muted under narration, as the on-screen label says.
