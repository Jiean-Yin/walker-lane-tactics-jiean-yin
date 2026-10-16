# SOURCES — provenance for every picture, number and line in the film

## Game source shown

- Repository: https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin, branch `a3-blender-assets`.
- **Commit `e415255`** = `e41525548f68b2752917ef4544024a1b2492510a` ("Draft the A3 test report from the measured numbers; add the check script's uid"). `godot/` at this commit is the demonstrated game source. Assignment 3 assets were built in `0609504`, `d4c87d1`, `fbb0a90`, exported and scened in `bacb97b`; the brief was committed first in `78b213f`.
- Isolated copy: `git -c core.autocrlf=false archive e415255 …` → `<capture-copy>\e415255\`; every `godot/` file byte-identical to its blob. `build_id` (SHA-256 of [capture/source-snapshot.txt](capture/source-snapshot.txt)) `54af8178ff472b719520b7750901193bde4c93e8431342a9a84be4aedf4d3c00`.
- Hashes of every authored `godot/` file, component associations, exclusions and excerpts: [gamedev-evidence.json](gamedev-evidence.json).

## Code excerpts shown (all verbatim, checked by tools/build_evidence.py)

| Beat | File @ e415255 | Lines | Shown with |
|---|---|---|---|
| B03 | `tools/blender/build_archer_piece.py` (SHA-256 in gamedev-evidence.json `external_excerpts`) | 135, 140 | ClaudeCodeBeat (comment markers ours) |
| B07 | `godot/diorama/asset_diorama.tscn` | 41–47 | GodotDevWorkbench (Godot editor reconstruction) |
| B10 | `tools/blender/build_board_square.py` | 142–143 | ClaudeCodeBeat (comment marker ours) |
| B12 | `godot/tests/check_assets.gd` | 171–182 | GodotDevWorkbench (Godot editor reconstruction) |

## Student material (supplied for this film; local, not in git)

| File | SHA-256 | Used in |
|---|---|---|
| `a3-blender-archer-build-2026-10-15.mp4` (Jiean's screen recording) | `4bee3340de3199935c8fea9a8506664f080f957bedb4a9fcec2c4fd63fad5bf6` | B04, B05 |
| `a3-blender-flag-build.mp4` (Jiean's screen recording) | `06f12a7ddbde2bd69dd896fd899a4c3389ce5476434617174057cfa2388d1d06` | B06 (cropped) |
| `Check 3 asset in Godot.png` (Jiean's Godot editor screenshot) | `126db200c866eb25119b1aa8bf1442565903804df2c739519518e677f7ba828a` | B02 |

## Engine capture (new for this film)

Godot 4.7.2 Movie Maker, run-02: `orbit-4k.mkv` `f3e6a847d422e02d68aa8be6f99a5d234790c92ffdc92233f95b2aff21be97fa` (FFV1 3840×2160, 1500 frames), `orbit.avi` `9f9d5d39ff8033957b980ea1d09c31b5e7036bc975d605ea2da5c81c78b7c6e4`. Driver, summary, camera log and join check in [capture/](capture/); method in [CAPTURE.md](CAPTURE.md). Runtime scene tree probe (logged by the driver): `WorldEnvironment, Floor (MeshInstance3D), Lamp (DirectionalLight3D), Camera3D, board_square, archer_piece, goal_flag (Node3D instances)`.

## Recorded numbers

| Report | SHA-256 | Result |
|---|---|---|
| `evidence/check_assets-1792106172.json` (run 1, faulty, kept) | `95847bf36275c4784e5f3d53c31a97727740f54b7f31170201459966674ccb43` | 32/33 |
| `evidence/check_assets-1792106192.json` (run 2) | `dc39e1e351362e71eec39c130a274704757904917731f682d1a5898e21d2e6a0` | 38/38 |
| [capture/check_assets-rerun.json](capture/check_assets-rerun.json) (this film, isolated copy) | `2d84507fc4573c58c6563416ae08eb27121271e63135c457d611820c44d5d5bb` | 38/38 |

Blender dimensions in B13 are TEST-REPORT A3.3's "Blender dimensions" column (read through the MCP after each build and again by `export_glb.py`); they were not re-measured for the film.

## Documents read (Assignment 3 sections)

CHANGE-BRIEF.md (brief `78b213f` + A3-R1), FRICTIONAL.md, TEST-REPORT.md, BLENDER-NOTES.md (uncommitted at the time of reading; the film does not quote it), README.md. Working-tree blob ids at reading time (other sessions were editing): TEST-REPORT `09f074c4…`, FRICTIONAL `2db3e05a…`, BLENDER-NOTES `861a6aba…`, CHANGE-BRIEF `ad1ac00a…`. Facts are taken from the committed text at `e415255` where the two differ (FACTCHECK.md marks working-tree-only facts).

## Tools and versions

Brutalist `<brutalist>` checkout `6a8380a` with the local Windows patches recorded in BUILD-PROMPT.md; Kokoro `am_onyx` (local, free); Remotion via `runtime/scripts/remotion_scenes.py`; FFmpeg 9.0.2 (Gyan full build); Pillow 10.4 / NumPy 2.4 in the Brutalist venv; Godot 4.7.2 standard. Fonts: EB Garamond, Inter, PT Mono from `<brutalist>/runtime/fonts` (OFL). No imported third-party assets; no paid calls; no secrets.
