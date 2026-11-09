# FACTCHECK — every claim in the narration, with its source

Source revision: tag `a6` = `7f199f9` (tree `f336766`), as pushed to GitHub. "copy" = the isolated git-archive copy of that tag used for the film. "capture" = the film's final capture (`capture/play-log.jsonl`, `slow-log.jsonl`; master frames). Line numbers are the copy's.

| Beat | Claim | Source |
|---|---|---|
| B00 | Lane Tactics: archers on a five-lane board; win by reaching the enemy's back row | AGENTS.md "What this project is"; RULES.md |
| B00 | On screen: 107/107, 135/135, 31/31, 31/31 at 60 fps | TEST-REPORT A6.1, A6.11; `capture/film-rerun.txt` |
| B01 | Settings guarded by tests; the look decided by Jiean's eyes, one revision at a time | TEST-REPORT A6.2, A6.5; TUNING.md (one setting per revision, Jiean's verdicts) |
| B02 | Effect A's job and event, Effect B's job and condition, verbatim jobs | CHANGE-BRIEF §1, §2 |
| B02 | CPU node for A, GPU node for B; Compatibility renderer | CHANGE-BRIEF §1, §2 "Node type"; `godot/project.godot:25` |
| B03 | Root and three CPUParticles2D; line 91 `emitting = false`; 14, explosiveness 1.0; spread 75; 140–260 px/s; gravity (0, 900); line 98 `local_coords = false` | `godot/effects/hit_burst.tscn:89-105` |
| B04 | The enemy's arrow lands on the player's archer; red glow, splinters, brown haze, gone after about a second; inside about one board square | capture: play arrow 249, hit 259; slow hit 290, first burst freed 436 (146 frames = 1.22 s); frames inspected (`capture/PILOT.md`, final crops); board square 128 × 96 (`main.gd:19`) |
| B05 | No signals; the driver runs after main each frame and reads `played_events`; line 44; line 49; never writes | CLAUDE.md "There are no signals"; `godot/game/hit_burst_driver.gd:34-49`, `:67-68`; `main.tscn` (`process_priority` 10) |
| B06 | The burst appears on the hit's frame; P freezes pieces and splinters; unpause resumes; the tree is never paused; speed_scale 0 | capture: play hit 636, burst on 636; P 645, unpause 840; "run 2: burst alive while paused" OK; `main.gd:6`; `hit_burst_driver.gd:49`, `:68` |
| B07 | Line 75 new instance per hit (Jiean's overlap rule); line 77 + (0, −40); line 79 freed on Dust.finished; child of the driver | `hit_burst_driver.gd:20`, `:71-85`; CHANGE-BRIEF §1 A3, A6 |
| B08 | Two hits about a second apart; at the second hit the first burst has almost faded but is alive; the state test counted 2 on the second hit's frame; the brief predicted the dropped retrigger | capture: play 259 and 290 (1.03 s); slow 417–436 two alive; `evidence/a6/final/test_hit_burst_state_60fps.log:30` (on screen, verbatim); CHANGE-BRIEF §6 failure 1 |
| B09 | Brief: 0.12 s; Jiean: "I can barely realize it happens"; one setting per revision with a prediction first; lifetime, size, lifetime; line 64 = 1.08 | CHANGE-BRIEF §1; TUNING.md:42 (verbatim); TUNING r1–r3; `hit_burst.tscn:64`; Revision 1 item 1 |
| B10 | Same seed; r1 three times longer (0.12 → 0.36), frame 12 barely changed; Claude predicted "still clearly red", wrong; Flash is the first child; r2 about 2.5× larger (40 → 96 px at birth, scale 1.25 → 3.0); r3 about a second (1.08 s); Jiean kept both | TUNING r1 (prediction and comparison), r2 (prediction: 40 px → 96 px), r3; Jiean's verdicts verbatim (TUNING.md:62, :87) |
| B11 | Two GPU nodes; `trail_enabled` draws nothing on Compatibility with a warning, measured before the brief; line 99 off; line 98 `local_coords` off | CHANGE-BRIEF §0; `godot/effects/arrow_trail.tscn:87-101` |
| B12 | Two-square shot; a row of dots about 20–25 px apart; line 95 fixed_fps 30; the brief predicted it; Jiean called the path clear | capture frames (2× crop; path about 250 px in 10.5 steps); `arrow_trail.tscn:95`; CHANGE-BRIEF §6 failure 8; TUNING.md:125 (verbatim on screen) |
| B13 | One entry per arrow; line 69 to the tip with the game's arc; line 74 both stop; 0.7 s countdown; freed; a new trail per arrow | `godot/game/arrow_trail_driver.gd:43-47`, `:60-79`; `main.gd:718-721` |
| B14 | Emission stops at the landing; dots shrink from the oldest end; wisps hang on; the burst takes over; pause freezes arrow and trail; one surprise (B2) | capture: slow trail stop 416, hit 417; play P 1083, unpause 1233, hit 1238; "run 3: trail alive while paused" OK; Revision 1 item 3 |
| B15 | Line 79 turbulence; influence 0.1–0.2; damping; colour ramp from pale brown at 45 % to the streak's colour at 70 % | `arrow_trail.tscn:59`, `:64-83`; Revision 1 item 4; TUNING Effect B r1 |
| B16 | r0 above, r1 below, same seed; in flight each wisp hides behind its streak dot; frames 26 and 31 differ most; no curl in stills; Jiean's verdict (voice: its second sentence) | TUNING Effect B r1 (pixel counts 403 / 1004 / 1264 / 1087; TUNING.md:181-182; verdict :185, verbatim) |
| B17 | 107 and 135 checks; the scene read as text for Godot 3 names; old names can load silently | `godot/tests/test_hit_burst_config.gd:80`, `:127-140`; TEST-REPORT A6.1; CHANGE-BRIEF §6 failure 2 |
| B18 | Mutation 1: no error, value read back 0, two checks failed; Jiean saw a flash that seemed to fade earlier; mutation 2: one check failed | TEST-REPORT A6.3; `evidence/a6/mutations/` (log lines verbatim on screen) |
| B19 | Every frame at 60 fps with real keys; stop vs hit; brief: within one frame; first run 0, −2, 0, 0, −2 | `godot/tests/test_arrow_trail_state.gd:561-570`; Revision 1 item 3; `evidence/a6/step5b/` |
| B20 | The agent left the check failing and reported it; brief corrected first, then the test (31/31); why two frames is open; no headless run draws particles | TEST-REPORT A6.4 table (B2 row); FRICTIONAL A6; Revision 1 item 3; `evidence/a6/final/`; CLAUDE.md "Headless facts" |
| B21 | Line 77, a node that runs last; 600 frames twice per case; four cases; means only | `godot/tests/cost_effects.gd:76-86`; TEST-REPORT A6.6 |
| B22 | +0.0078 (A), +0.0066 (B); Jiean predicted 0 for B; B costs about as much as A headless; budget 0.2 ms | TEST-REPORT A6.6 headless table and Claude's reading 5; CHANGE-BRIEF §7 |
| B23 | Line 115 measured GPU time each frame, a mean once a second; Jiean's Visual Profiler; Claude's unattended sweep, each case twice, vsync on and off | `godot/previews/price_effects.gd:112-123`; TEST-REPORT A6.6 |
| B24 | Ranges overlap; swing about 1.5 ms; +0.0031 and +0.0074; about 2.5 to 3 times the predictions (0.001, 0.003); 180 fps with vsync on, as predicted; Jiean's conclusion (voice: one sentence) | TEST-REPORT A6.6 (verbatim on screen); CHANGE-BRIEF §7, §8 answer 4 |
| B25 | Converted by Jiean in the editor, unedited, about 490 lines, unused; start() and process(); Jiean's line numbers 3, 323, 378, 232, 412, 254, 255, 441 | TEST-REPORT A6.7 (Jiean's rows; each line checked in the copy); `godot/shaders/particles_generated.gdshader:252-257` on screen |
| B26 | Each wisp: own speed, drifts up (gravity −20), swells (0.6 → 1.4), fades (α 0.7 → 0); Jiean's split (voice: first and last sentences) | `arrow_trail.tscn:59-83`; CHANGE-BRIEF §2; TEST-REPORT A6.7 (verbatim on screen) |
| BCRD | Who did what; the bound, the draw-order prediction, the deleted strip; textures are gradients | SOURCES.md A6; CHANGE-BRIEF header; FRICTIONAL A6; TUNING r1; `effects/ATTRIBUTION.md` |
| BVDT | Checked / wrong / uncertain / next; Jiean's playtest answer (verbatim) | the rows above; TEST-REPORT A6.6 (predictions: three low, one high), A6.8 |
| BHTF | Suggested prompt (fixed_fps 30 → 60) | not a past run; labelled as a suggestion |

**Corrections made while checking**, each shown to Jiean and approved:
- **BVDT:** "low by" → "off by less than a hundredth of a millisecond". Effect A's CPU prediction was high.
- **B10:** "three times larger" → "about two and a half times larger".

**Noted, not changed (Jiean's own words, quoted verbatim):**
- Jiean's A6.6 conclusion says "Both predictions were too low", which does not hold for Effect A's CPU prediction.
- Two cells of the A6.7 table shorten the file's text (rows 232 and 254). The film shows the file's real lines.

**Voice spelling:** the narration spells Jiean as "Jay-Ann", as in the A5 film. Screen text keeps "Jiean".
