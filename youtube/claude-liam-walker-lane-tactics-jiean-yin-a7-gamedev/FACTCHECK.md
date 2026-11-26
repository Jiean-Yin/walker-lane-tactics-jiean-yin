# FACTCHECK — every claim in the A7 film, with its source

Source shown: tag `a7` (`37c4698`). TR = TEST-REPORT.md, CB = CHANGE-BRIEF.md, TU = TUNING.md, FR = FRICTIONAL.md.

| Beat | Claim | Source |
|---|---|---|
| B00 | read-backs 43/43 and 51/51; anim states 51/51; edges 102/102 at 60 fps | TR A7.3–A7.5, `capture/film-rerun.txt` |
| B02 | one loops, one commits; jobs; routes; 12 / 21 / 15 frames; CC0 sheet | CB §1–§4; `godot/assets/art/flag/ATTRIBUTION.md` |
| B03 | frame track on `FlagSprite:frame`, keys every 0.125 s, step 0.125, length 0.5, last key 3, no key at length | `godot/animations/wave.tres` lines 11–24 |
| B04 | the flag ripples about twice a second (4 cells at 8 fps = 0.5 s) from the title on; "Smooth steady ripple." | `wave.tres`; `capture/play-log.jsonl` (`flag_cell`); TR A7.9 (Jiean) |
| B05 | pole drift 4 / 8 / 6 / 3 px; offset keys 0 / −4 / −2 / +1; the sheet is never edited | `ATTRIBUTION.md`; `wave.tres` lines 29–36; CB §2 |
| B06 | the pole's darkest column at screen x 1176 in all 13 frames; "Stand still while the cloth waves." | TR A7.11 (Claude's measurement and Jiean's words) |
| B07 | line 173: every frame key below `hframes × vframes` | `godot/tests/test_flag_readback.gd` lines 165–177 |
| B08 | mutation 3 fails the frame-range check; mutation 2 fails the loop-mode check; the first run of 3 also crashed a later check, guarded since | `evidence/a7/step6/mutations/`; TR A7.6, A7.17 |
| B09 | 0.2 / 0.35 / 0.25 s = 12 / 21 / 15 frames; reference frames; the hold skipped (393 frames); bow drop at frame 40 by eye | `main.gd:29-33`; CB §4 |
| B10 | step 1/60 (line 33); key times frame ÷ 60 (line 41); three tracks | `godot/animations/shoot.tres` lines 31–43 |
| B11 | startup lean and the bow coming up level, the release, the follow-through, the hold, the drop, then idle; "All distinct…" | play frames 332–358 (`capture/OBSERVATIONS.md`); TR A7.10 (Jiean) |
| B12 | lines 112, 113, 115, 116; facing on `Mount` | `godot/game/piece.gd` lines 109–116, 255; CLAUDE.md "One authority" |
| B13 | paused in each phase, carried on; R rebuilds the archers, no shot left | `capture/play-summary.json` (7 expectations OK) |
| B14 | MANUAL, advanced by game time inside the game's update (line 182); the flag on IDLE, real time | `piece.gd` lines 170–182; `goal_flag.tscn` line 25; `main.gd:162-171` |
| B15 | the flag waves while paused; clip − arrow t = 0.20000; one frame ahead; no physics tick | `play-log.jsonl` (72 cell changes while paused); `evidence/a7/step5/test_anim_states_60fps.log`; CB revision 2; TR A7.13 |
| B16 | branches on track type; line 99: a value track must name a real property | `godot/tests/test_shoot_readback.gd` lines 88–100 |
| B17 | mutation 1 fails with "Node2D has no property 'rotaton'"; mutation 4 passes, 51/51 | `evidence/a7/step6/mutations/m1_subname.log`, `m4_cache.log`; TR A7.6 |
| B18 | Jiean's r0 words; the cut at one column; frame-48 bow key 20° → 8° (line 68) | TU r0; `shoot.tres` line 68; CB revision 4 |
| B19 | 0 px changed up to frame 29; 410–458 px in frames 31–33; Jiean disagreed with Claude about visibility; kept | TU r1; TR A7.14 (Jiean) |
| B20 | 4 boundaries × 3 offsets × 3 interrupts = 36 cases | `godot/tests/test_shoot_edges.gd` lines 31–33 |
| B21 | 102/102; Enter is the attack order one frame before the draw; cues land ±1 frame | `evidence/a7/step6/test_shoot_edges_60fps.log`; TR A7.5; CB revision 1 |
| BCRD | who did what; the three mistakes caught | SOURCES.md A7; FR A7 |
| BVDT | checked / wrong / uncertain; Jiean's summary | TR A7; SUBMISSION.md (Jiean) |
