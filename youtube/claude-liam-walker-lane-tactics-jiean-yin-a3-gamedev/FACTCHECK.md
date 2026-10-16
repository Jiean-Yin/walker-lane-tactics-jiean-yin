# FACTCHECK — every spoken or on-screen claim and its source

Sources at commit `e415255` unless marked. "FR" = FRICTIONAL.md, "TR" = TEST-REPORT.md, "CB" = CHANGE-BRIEF.md (Assignment 3 sections). Working-tree files were read on 2026-10-15 ~22:30 while other sessions were editing them; anything only in the working tree is marked *(working tree)*.

| Beat | Claim | Source | Status |
|---|---|---|---|
| B00 | Lane Tactics: wooden pieces on a five-lane board; win by reaching the enemy's back row | CLAUDE.md; CONCEPT.md; CB A3 asset C "Marks the back row you must reach to win" | ✓ |
| B00 | Three 3D assets built in Blender by Claude through the Blender MCP | CB A3 title; FR A3 builds; tools/blender/build_*.py headers | ✓ |
| B00 | Prompt is an illustrative reconstruction | label on screen; PROMPTS.md | ✓ disclosed |
| B00 (screen) | 254 / 60 / 84 tris; 38/38; first run 32/33 kept; source e415255 | TR A3.3; evidence/check_assets-1792106192.json, -1792106172.json | ✓ |
| B01 | Made in Blender, exported to Godot, placed in one diorama scene | FR 19:14–19:16; godot/diorama/asset_diorama.tscn | ✓ |
| B02 | Picture is Jiean's own Godot screenshot | `Check 3 asset in Godot.png`, supplied as the student's own (brief to this build) | ✓ (provenance from the brief) |
| B02 | Archer = the unit; board square = tile of the five-lane board; goal flag = marks the back row | CB A3 table "What it is in the game" | ✓ |
| B02 | Brief fixed before any build: 1 square = 1 m; origin at the base | CB A3 "Scale", "Origin"; brief committed in 78b213f before 0609504 | ✓ |
| B02 (cards) | sizes 0.40×0.40×0.80, 1.00×1.00×0.05, 0.45×0.30×1.20; budgets 400 / 100 / 150 | CB A3 table | ✓ |
| B03 | One MCP call per part | FR 18:20–18:23 "one execute_blender_code call per part"; build_archer_piece.py steps 1–6 | ✓ |
| B03 | Line 135: bow, thin box reaching 65 cm, facing side | build_archer_piece.py:135 box(0.03, 0.06, 0.50) at z 0.40 → z 0.15–0.65; comment line 128 "+X (facing) side" | ✓ |
| B03 | Line 140: eye, small cube at 60 cm, same side | build_archer_piece.py:140 box 0.03 at (0.105, 0, 0.60) | ✓ |
| B04 | Student's own screen recording, just after the build | footage file name/date; clip starts with the finished archer (CAPTURE.md) | ✓ |
| B04 | From the facing side the bow stands in front of the eye | footage 0:05–0:09 (seen); FR "What Claude got wrong"; TR A3.4 #1 | ✓ |
| B04 | No number caught it; looking did | FR "seen in look, not in the numbers"; TR A3.4 #1 | ✓ |
| B05 | The fix was Jiean's, by hand, following Claude's steps | FR ~18:30 "I made the edit myself… Claude suggested the edit" | ✓ |
| B05 | Edit Mode, bow selected; G, Y, eight centimetres along Y | footage 0:09.7 (Edit Mode), 0:25.5–0:31 (header `D: [0.08] = 8 cm (0.0800 m) along global Y`); FR "Tab → L → G Y 0.08" | ✓ (the G press itself is at ~0:17.5, in the omitted range; the Y constraint and value are on screen) |
| B05 | Sidebar still reads 40 by 40 by 80; file saved | footage ~0:39 Dimensions 0.4/0.4/0.8 m; ~0:40.5 `Saved "archer_piece.blend"` | ✓ |
| B06 | Flag built the same way | FR ~18:55 (one call each, then join and apply); build_goal_flag.py | ✓ |
| B06 | Jiean types the prompt "Approve" and sends it | flag clip 0:04.5–0:11.7 | ✓ |
| B06 | Ninety seconds later Claude's reports appear | sent ~0:11.7, reports appear ~1:42 (≈ 90 s of no visible change) | ✓ |
| B06 | base, pole and flag, 84 triangles, nearly vanishes side-on | flag clip 1:42.6–1:52.6 (Claude's text); FR ~18:55 | ✓ |
| B06 | Blender is not on screen in this recording | whole clip inspected (CAPTURE.md) | ✓ |
| B07 | Claude wrote the diorama by hand: floor, one lamp, a camera, three instanced models | FR 19:14 item 3; asset_diorama.tscn | ✓ |
| B07 | board at x −1.2, archer at origin, flag at 1.1; none lifted | asset_diorama.tscn:41–47 | ✓ |
| B08 | Scene's own camera, exactly as saved; then a scripted camera on the real scene | run-02 shots A (scene Camera3D) and B (harness camera); CAPTURE.md | ✓ |
| B08 | All three upright on the floor | run-02 frames 120–600 (seen); check: stands along Y, gap 0.0000 | ✓ |
| B08 | Passing the flag's side the cloth thins to a line; from behind it falls into shadow | run-02 ~frames 230–300 and ~330–420 (seen) | ✓ observation |
| B09 | Floor level: no gap, nothing sinks | run-02 600–840 (seen); check floor gap 0.0000 m | ✓ observation + measurement |
| B09 | Archer from its facing side, the profile the 2D game uses; eye beside the bow | run-02 840–1080; CB "+X facing side"; FR "the view the game uses" | ✓ |
| B10 | Original border 1.15 : 1 against the slab; grid read as a flat sheet | CB A3-R1 Observation | ✓ |
| B10 | Claude compared four darker colours; Jiean chose 9A7F55 at 2.27 : 1 | CB A3-R1 "Options compared by Claude", "Change (chosen by Jiean)" | ✓ |
| B10 | Two lines are the whole change | build_board_square.py:142–143 (the material's colour is the only change; FR cycle 2) | ✓ |
| B11 | Darker strips frame the square; the slab reads almost white under this lamp | run-02 1320–1500 (seen) | ✓ observation; cause not established |
| B12 | The check loads each model, then the diorama, and measures | check_assets.gd:41–46, 79–165, 167–214 | ✓ |
| B12 | Line 173, await process_frame, is the fix | check_assets.gd:173 and header lines 13–15 | ✓ |
| B12 | First version measured before the nodes were in the tree; positions identity; no frustum | FR 19:14 item 4; TR A3.4 #2 | ✓ ("read as zero" = identity transforms) |
| B12 | One impossible failure, all three at x zero, gave it away | evidence/check_assets-1792106172.json, the only FAIL: spans (−0.5, 0.5), (−0.2, 0.2), (−0.15, 0.3) | ✓ |
| B13 | Size, height axis, scale, origin, triangles, colours all match; 254 / 60 / 84 | check_assets-1792106192.json `measured`; TR A3.3 | ✓ |
| B13 | Faulty first run kept, 32 of 33 | check_assets-1792106172.json passed 32 total 33; TR A3.2 | ✓ |
| B13 | Fixed run 38 of 38; rerun on this film's isolated copy 38/38 | check_assets-1792106192.json; capture/check_assets-rerun.json (2026-10-15) | ✓ |
| B13 | Headless Godot draws nothing; looks stay a human check | check_assets.gd header lines 10–11; TR A3.3 "What these numbers… do not show" | ✓ |
| BCRD | Jiean: chose the game, approved every plan, recorded, made the hand edit, chose the border colour and the headless export route | CLAUDE.md; FR A3 "Human / Claude / model" lines; CB A3-R1; FR 19:14 "the export-route decision… was mine" | ✓ |
| BCRD | Claude: proposed the numbers, wrote and ran the Blender code, export, scene and check | CB A3 "Who decided what"; FR A3 entries | ✓ |
| BCRD | Source shown: commit e415255 | metadata; CAPTURE.md | ✓ |
| BVDT | Checked: size, upright, scale, origin, budget, colours (headless), plus the scripted look | TR A3.2/A3.3; run-02 | ✓ |
| BVDT | Claude got three things wrong: bow hid eye; first check proved less than claimed; flag vanishes side-on, unfixed | TR A3.4 #1–#3 | ✓ |
| BVDT | Uncertain: reading at game distance; why the linen looks pale | TR A3.3 "do not show"; A3.5 TO FILL; run-02 observation | ✓ |
| BVDT | Next step: Jiean's own look check in Godot | TR A3.5 is TO FILL at e415255 and still TO FILL in the working tree | ✓ |
| BHTF | "the numbers may not move at all" (6 cm cloth) | a box stays 12 tris; the cloth's Blender Y extent (0.06 m) stays inside the base disc's 0.30 m, so the bounding box is unchanged | ✓ prediction stated as "may"; not run |

## Not claimed (deliberately)

- Blender's Scene Statistics: Jiean's reading (254, 60, 84, matching Claude's counts) exists only in the uncommitted working-tree TEST-REPORT *(working tree)*; the film does not cite it.
- Whether the assets "look right": A3.5 is the student's open human check.
- Anything about Claude's archer build on video: it is not in the footage.

## Corrections made while building

- The first engine take (run-01) had shot D blocked by the flag pole; replaced by run-02 (CAPTURE.md).
- B08 originally labelled the scene-camera opening as "scripted camera"; split so frames 0–120 say "the scene's own Camera3D".
- First Remotion pass, inspected before the cut (tools/patch_sheet_r2.py): B01 ended mid-correction ("judged in the r…") → 3.4 s silent tail; B03's 101-character source lines were clipped at the large code size → normal size; B10's 117-character line 132 was clipped → lines 142–143 only; B12's excerpt overflowed the panel after line 176 → lines 171–182 at the minimum code size; B07's Camera3D note was clipped → shortened.
- Evidence stills: text below ~44 px at 4K raised (B13 sub-lines and paths; footage label second lines).
