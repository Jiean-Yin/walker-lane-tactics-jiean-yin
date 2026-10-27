# CAPTURE — Lane Tactics Assignment 3 film

Two kinds of moving picture are in this film, and they are labelled differently on screen:

1. **The student's own screen recordings** (Blender and the Claude window), made by Jiean Yin on 2026-10-15. Used as excerpts with their real timecodes; nothing reconstructed.
2. **A new engine capture** of the real diorama scene, made for this film with Godot Movie Maker on an isolated copy of commit `e415255`, with a scripted camera.

## 1. Student footage (<footage>, not in git)

| File | SHA-256 | Format |
|---|---|---|
| `a3-blender-archer-build-2026-10-15.mp4` | `4bee3340de3199935c8fea9a8506664f080f957bedb4a9fcec2c4fd63fad5bf6` | H.264 2560×1336, variable frame rate (613 frames in 43.27 s), AAC audio |
| `a3-blender-flag-build.mp4` | `06f12a7ddbde2bd69dd896fd899a4c3389ce5476434617174057cfa2388d1d06` | H.264 2560×1368, variable frame rate (3236 frames in 209.1 s), AAC audio |
| `Check 3 asset in Godot.png` | `126db200c866eb25119b1aa8bf1442565903804df2c739519518e677f7ba828a` | PNG 2560×1368, Jiean's Godot editor screenshot |

The other PNGs in that folder are unrelated and were not opened for the film.

**What the footage contains (inspected with ffprobe, frame-timestamp gaps, scene detection and frame sheets at 1–2 s spacing, then 0.5 s spacing around each used range):**

- **Archer clip (0:00–0:43):** Blender only, full screen. It starts **after** Claude's build: the finished archer orbits in Object Mode (0:00–0:09.6; from the facing side the bow covers the eye), Tab into Edit Mode with the bow selected (~0:09.7), a move that starts free (~0:17.5–0:25) and is then constrained to global Y (~0:25.5), the typed value 0.08 (header `D: [0.08] = 8 cm (0.0800 m) along global Y`, ~0:28.5), confirmed (~0:31), orbit in Edit Mode, Object Mode with sidebar Dimensions 0.4 / 0.4 / 0.8 m (~0:39), status bar `Saved "archer_piece.blend"` (~0:40.5). **No Claude window and no prompt to Claude are in this clip; Claude's archer build itself is not recorded.**
- **Flag clip (0:00–3:29):** the Claude desktop window only. 0:04.5–0:11.7 Jiean types `Approve` and sends it (~0:11.7); the view then scrolls to show the earlier exchange (Jiean: "Keep recording with the Claude window visible when you approve. Do you mean I should turn on my recording while you are working? tell me briefly"; Claude's reply asking for Blender to be on screen) and the sent `Approve`. From 0:14 to ~1:42 the window shows no change; at ~1:42 Claude's step reports appear (base disc 0.30 × 0.30 × 0.04 m, 44 triangles; pole 0.04 × 0.04 × 1.16 m, 28; flag 0.28 × 0.02 × 0.20 m, 12; joined 0.45 × 0.30 × 1.20 m, 84 triangles; "reads well from front/angled views but goes nearly invisible edge-on from the side"). 2:18–3:29: the summary, "Commit the goal flag?", "Yes, commit it", the commit table. **Blender never appears in this clip**, so Blender building the flag is not on video.
- **Privacy check:** the flag clip shows the Claude app's sidebar (other session names and the account label "Jiean · Premium Seat · Northeastern…") and a side panel (local path, branch). The film uses only a crop of the conversation column (x 577–1997, y 40–1340 of 2560×1368), so neither is shown. No email address, other application or notification is visible in the used ranges. The archer clip is Blender full screen; nothing private is visible. Both clips' own audio tracks are not used (narration only).

**Ranges used** (each cut at [t0, t1) of the source and converted to 30 fps CFR by repeating frames — the recordings are variable-frame-rate screen captures; no speed change):

| Beat | Source range | Shows |
|---|---|---|
| B04 | archer 0:00.0–0:09.6 | the finished archer orbiting; bow in front of the eye on the facing side |
| B05 | archer 0:09.6–0:12.6 · 0:24.5–0:31.5 · 0:38.0–0:43.2 | Edit Mode with the bow selected · the move along global Y, 0.08 typed and confirmed · Object Mode, Dimensions 0.4/0.4/0.8, saved. Omitted: 0:12.6–0:24.5 (view change, start of the same move as a free drag) and 0:31.5–0:38.0 (Edit-Mode orbit). Each excerpt carries its own timecode label. |
| B06 | flag 0:04.5–0:14.0 · 1:42.6–1:52.6 | Jiean types and sends `Approve` · Claude's step reports. Omitted: 0:14–1:42 (no visible change). |
| B02 | the PNG | Jiean's screenshot of the scene in the Godot editor |

B05 adds 3×–4× zoom insets that crop the **same frame's** own UI text (mode selector; move header and Median Y; Dimensions and the "Saved" status), drawn with an orange border and the tag "zoom of the same frame".

## 2. Engine capture run-02 (new for this film)

| Field | Value |
|---|---|
| Game source | commit `e415255` = `e41525548f68b2752917ef4544024a1b2492510a` (branch `a3-blender-assets`) |
| Isolated copy | `git -c core.autocrlf=false archive e415255 godot tools/blender evidence/check_assets-*.json …` extracted to `<capture-copy>\e415255\` (outside the repository). All 59 authored files of `godot/` checked byte-identical to the commit's blobs with `git hash-object`. A second copy `<capture-copy>\capture-godot\` adds only the harness file `film/diorama_orbit_driver.gd` ([capture/diorama_orbit_driver.gd](capture/diorama_orbit_driver.gd), SHA-256 `abd41688…`). |
| `build_id` | SHA-256 of [capture/source-snapshot.txt](capture/source-snapshot.txt) (`git ls-tree -r e415255 godot \| sort -k4`, 71 entries incl. `.uid`) = `54af8178ff472b719520b7750901193bde4c93e8431342a9a84be4aedf4d3c00` |
| Engine | Godot 4.7.2.stable.official.ed1daf0bf, Compatibility renderer (OpenGL 3.3, NVIDIA GeForce RTX 3070 Ti Laptop GPU), Windows 11 Home 10.0.26200 |
| Command | `Godot_v4.7.2-stable_win64.exe --path capture-godot --write-movie <run-02>/orbit.avi --fixed-fps 30 --script res://film/diorama_orbit_driver.gd -- full <run-02> <ffmpeg.exe>` |

**Method.** The driver instances the unchanged `res://diorama/asset_diorama.tscn` in a 3840×2160 SubViewport with its own World3D and shows it in the 1280×720 window (so Movie Maker's AVI is a 720p picture of the same frames). Each SubViewport frame is read back and piped raw into ffmpeg as a lossless FFV1 4K master (`orbit-4k.mkv`). The SubViewport keeps the project's rendering defaults: the project sets no MSAA/FXAA, so none is added. Shot A uses the scene's own `Camera3D` as saved; shots B–F use one harness `Camera3D` added **beside** the scene (not inside it) on a scripted path that looks at a target. Nothing in the scene is moved, edited or added to; the driver only reads node positions to aim. The scene has no audio. Movie Maker renders offline at a fixed 1/30 s step, so this is not evidence of real-time frame rate.

| Shot | Frames | Camera |
|---|---|---|
| A_scene_camera | 0–120 | scene `Camera3D` (0, 1.1, 3), unchanged |
| B_orbit_360 | 120–600 | harness, one 360° orbit, radius 3.3 m, 0.85 m above a target at (−0.15, 0.35, 0), eased |
| C_low_angle | 600–840 | harness, 6 cm above the floor at z = 2.2, tracking x −2.0 → 1.8 |
| D_archer_profile | 840–1080 | harness, archer from +X (its facing side) round to 25° off +Z, radius 0.95 m |
| E_flag_edge_to_front | 1080–1320 | harness, flag from exactly +X (edge-on) round to +Z (not used in the film) |
| F_board_from_above | 1320–1500 | harness, board square from above, rising |

**Assertions** (all passed, [capture/run-02-summary.json](capture/run-02-summary.json)): the scene has WorldEnvironment, Floor, Lamp, Camera3D, board_square, archer_piece, goal_flag; the scene camera is at (0, 1.1, 3) as saved; every captured frame is 3840×2160; the process frame advances by exactly 1 per captured frame. Per-frame camera path: [capture/run-02-camera-log.jsonl](capture/run-02-camera-log.jsonl).

| File (local, not in git) | SHA-256 |
|---|---|
| `<capture-copy>\run-02\orbit-4k.mkv` (FFV1 3840×2160, 1500 frames) | `f3e6a847d422e02d68aa8be6f99a5d234790c92ffdc92233f95b2aff21be97fa` |
| `<capture-copy>\run-02\orbit.avi` (MJPEG 1280×720, 1502 frames) | `9f9d5d39ff8033957b980ea1d09c31b5e7036bc975d605ea2da5c81c78b7c6e4` |

**Same-run join** ([capture/run-02-join.json](capture/run-02-join.json)): master frame *i* downscaled matches AVI frame *i*+1 (mean absolute difference 0.86 grey levels, max 1.09, every 25th frame); at the same index the difference jumps to 65.6 at shot cuts, so the AVI carries one extra leading frame. The film uses the 4K master only.

**Discarded take:** run-01 (same driver, first version): shot D put the camera at x 1.25, where the goal flag's pole (x 1.1) blocked the archer; shot F drifted onto the archer; a shot G from below the floor showed the one-sided floor plane disappearing and was dropped as not needed. Deleted; no frame of run-01 is in the film. A first isolated copy extracted with `core.autocrlf=true` (CRLF text files) was replaced by the LF copy before run-02 so every file matches its blob.

**Headless check on the isolated copy (2026-10-15):** `Godot_v4.7.2-stable_win64_console.exe --headless --path e415255/godot --script res://tests/check_assets.gd --fixed-fps 60` → **38/38**, exit 0 ([capture/check_assets-rerun.json](capture/check_assets-rerun.json), log [capture/check_assets-rerun.log](capture/check_assets-rerun.log)). Import before it: exit 0, no line containing error, warn or fail.

## From capture to film

Engine beats are exact frame ranges of `orbit-4k.mkv` (`-ss a/30`, `-frames:v n`, H.264 crf 10, 30 fps), no speed change, with our two-line label burned top-left. Footage beats are composited on the cream page with a label pill; the conversation crop and the zoom insets are described above. Per-beat records with hashes: [capture/clips.json](capture/clips.json).

| Beat | Source | Frames | Label |
|---|---|---|---|
| B04 | archer 0:00.0–0:09.6 | 288 | STUDENT'S SCREEN RECORDING |
| B05 | archer, three excerpts | 90 + 210 + 156 | STUDENT'S SCREEN RECORDING (per-excerpt timecode) |
| B06 | flag, two excerpts | 285 + 300 | STUDENT'S SCREEN RECORDING (per-excerpt timecode) |
| B08 | run-02 0–120, 120–600 | 600 | THE SCENE'S OWN CAMERA3D / SCRIPTED CAMERA · REAL GODOT RENDER |
| B09 | run-02 600–1080 | 480 | SCRIPTED CAMERA · REAL GODOT RENDER |
| B11 | run-02 1320–1500 | 180 | SCRIPTED CAMERA · REAL GODOT RENDER |
