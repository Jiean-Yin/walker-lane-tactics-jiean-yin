# FACTCHECK — every claim in the narration, with its source

Source revision: tag `a5` (`ef5d38b`). "copy" = the isolated git-archive copy of that tag used for the film.

| Beat | Claim | Source |
|---|---|---|
| B00 | Lane Tactics: archers on a five-lane board; win by reaching the enemy's back row | RULES.md; AGENTS.md "What this project is" |
| B00 | Result lines 46/46 at 30/60/144, 148/148, 3 mutations exit 1 | TEST-REPORT A5.2, A5.3, A5.9; capture/film-rerun.json |
| B01 | Two shaders written by hand by Jiean | commits 80fc669, fb8d2bf; SOURCES.md A5 "Code and documents" |
| B02 | The assignment's requirements and four questions | Assignment 5 text ("Your task", "Use It", "Ship It") |
| B02 | Compatibility renderer | godot/project.godot:25 |
| B03 | One run per pixel of the sprite; line 3 exposed_amount 0–1; line 7 mix × 0.7; only rgb | godot/shaders/exposed_tint.gdshader:3, :7 |
| B04 | Two turns out of reach: no tint; turn 3 Right → red in a fifth of a second; Left drains it | capture/tint-log.jsonl: p1 0.0 until frame 245, 1.0 at 250 (6 frames = 0.20 s), falls from 365 to 0.0 at 370 |
| B05 | move_toward at 5 per second of game time; line 34; line 37; own material per sprite | godot/game/exposed_driver.gd:18, :32-37; godot/game/piece.gd:56-59 |
| B06 | Taps turn around, never jump; pause holds; Enter fades during the move; turn 4 rises at once; enemy 0 every frame | capture/tint-log.jsonl: taps at frames 479–497 every 3 frames (0.1 s); Left 599, P 602 and 662 (paused 602–661, value held); Right 692 (rises), Enter 722 (falls 722–727 during PLAY_MOVES; the attack plan confirmed at 743); turn 4 PLAN_MOVE from frame 816, rising 0 → 1 by 821; max e1 = 0 |
| B07 | Hand predictions; captures at 0/0.5/1/2; exact at 0 and 0.5; within one step at 1 (100.5); 2.0 → (224, 27, 34); hint_range does not clamp; OS screenshot same | CHANGE-BRIEF §3, §6 answer 7; evidence/a5/captures/exposed_pixels.md, os_compare.log; TEST-REPORT A5.4 |
| B08 | Both materials point at the same shader on line 11; tint line 13; normal_strength line 16 (1.0 / 1.5) | godot/materials/linen_dark.tres:11, :13, :16; linen_light.tres:13, :16 |
| B09 | Dark normal_strength to 0 changes only the dark tile; ALBEDO × 0.5 in memory darkens both; Jiean made the same edits by hand | capture/diorama-summary.json shots D5, D6; TEST-REPORT A5.8 (Jiean's words) |
| B10 | Line 4 source_color; line 9 no hint; line 11 hint_normal; import settings; curl 0.68 vs 1.32 | godot/shaders/linen_square.gdshader:4, :9, :11; the four .import files; TEST-REPORT A5.10, A5.11 |
| B11 | uv_scale 0.5 rope / 8 fine; normal_strength 0 flat / 2 deep; roughness 0 slightly darker, no highlight; Jiean saw it shiny | capture/diorama-summary.json D2–D4; CAPTURE.md "Roughness: measured"; TEST-REPORT A5.7 (Jiean's words) |
| B12 | 64/128/192; line 4 with source_color, 5 without, 6 picks; unshaded, Linear, exposure 1; prediction 137/188/225 | godot/shaders/hint_experiment.gdshader:4-6; godot/hint/hint_experiment.tscn; CHANGE-BRIEF §3 |
| B13 | Both quads 64/128/192; switches swapped, separate textures, constant 0.5 → 128; neither decode nor encode; prediction assumed Forward+ | capture/hint-summary.json (4K bands); evidence/a5/step3/hint_experiment_measurement.md, hint_control.log; MATERIALS.md Review; CHANGE-BRIEF §3 "Renderer" |
| B14 | No main, no version line; generated line 7 source_color = Jiean's line 4; line 19 hint_roughness_normal vs line 11 hint_normal | godot/shaders/standard_generated.gdshader:7, :19; linen_square.gdshader:4, :11 (verbatim on screen) |
| B15 | Uniform list via the engine; defaults/source_color from text; real keys; every frame checked | godot/tests/test_exposed_tint.gd:167-177, :179-192; CLAUDE.md "Headless facts" |
| B16 | 46/46 ×3, 148/148, earlier suites unchanged; three mutations exit 1; renamed uniform: value check still passed; no headless pixels | TEST-REPORT A5.1, A5.2; evidence/a5/mutations/; capture/film-rerun.json |
| BCRD | Who did what; mistakes caught; Hessian 380 CC0; tag a5 | SOURCES.md A5; TEST-REPORT A5.13; FRICTIONAL A5; ATTRIBUTION.md |
| BVDT | Checked / wrong / uncertain / next | the rows above; TEST-REPORT A5.3 (30 fps fade 7 frames) |
| BHTF | Suggested prompt (cap 0.7 → 0.5) | not a past run; labelled as a suggestion |

**Corrections made while checking:** B15's third highlight was moved from line 173 to line 177 (the defaults are read on lines 180–192, which are not on screen).

**Voice spelling:** the narration text spells Jiean as "Jay-Ann" (Jiean's instruction: "like Jack and Ann, Jay-An"); Kokoro's phonemes for "Jay-Ann" are /dʒeɪ-æn/. Plain "Jiean" was read /dʒiːən/. Screen text keeps "Jiean".
