# COMPONENTS — what the A7 film explains

| Component | Files (tag `a7`) | Beats | Why this design, and one trade-off |
|---|---|---|---|
| The flag clip (`wave`) | `animations/wave.tres`, `game/goal_flag.tscn`, `assets/art/flag/flag_red.png` (+ `.import`, `ATTRIBUTION.md`), `game/main.tscn` | B02–B06 | A frame track lets the AnimationPlayer read-back see the frames and their discrete updates. Trade-off: a found sheet drifts, which costs a second (offset) track. |
| The rig clip (`shoot`) | `animations/shoot.tres`, `game/archer_rig.tscn`, the A2 draw art | B09–B11, B18–B19 | Keys written as text from a 60 fps phase table keep every key on a frame. Trade-off: parts cut from one drawing split when a part turns far (hence 8°). |
| One authority and the clocks | `game/piece.gd`, `game/main.gd` | B12–B15 | `piece.gd` alone starts, stops and advances the rig's player, by game time (MANUAL), so P freezes it; the flag runs in real time (IDLE). Trade-off: the clip runs one frame ahead of the cue clock. |
| Tests and the preview | `tests/test_flag_readback.gd`, `test_shoot_readback.gd`, `test_anim_states.gd`, `test_shoot_edges.gd`, `test_pins_a7.gd`, `previews/shoot_preview.*` | B07–B08, B16–B17, B20–B21 | Read-backs catch silently inert tracks and missing cells; edges pin every boundary. Trade-off: nothing headless draws a pixel. |

**One input → state → output trace (B12 → B13):**
1. Enter confirms turn 4's attack.
2. `main._play_attacks` schedules `_cue_draw`; on its frame, `piece.set_state("draw")` runs (`main.gd:486`).
3. `_apply_clip()` stops the player, plays `shoot` and `advance(0)`s it to frame 0 (`piece.gd:112-116`).
4. Each frame, `tick(dt)` advances it by game time (`piece.gd:181-182`).
5. The rig's pivots move on screen: play frames 333–357.
6. P stops `tick`, so the pose holds (play frames 712–802).
