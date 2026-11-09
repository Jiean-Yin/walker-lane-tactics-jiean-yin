# COMPONENTS — what the film explains

Ledger: `gamedev-evidence.json` (every authored `godot/` file at tag `a6`, hashed, associated or excluded with a reason).

| Component | Files | Beats | Code → result |
|---|---|---|---|
| Hit burst scene (Effect A) | `effects/hit_burst.tscn`, `effects/ATTRIBUTION.md` | B03, B04, B09, B10 | B03 → B04, B09 → B10 |
| Hit burst driver | `game/hit_burst_driver.gd`, `game/main.tscn`; reads `game/main.gd`, `game/piece.gd` | B05–B08 | B05 → B06, B07 → B08 |
| Arrow trail scene (Effect B) | `effects/arrow_trail.tscn` | B11, B12, B15, B16 | B11 → B12, B15 → B16 |
| Arrow trail driver | `game/arrow_trail_driver.gd` | B13, B14 | B13 → B14 |
| Previews and price fixture | `previews/hit_burst_preview`, `arrow_trail_preview`, `price_effects` (`.gd` + `.tscn`), `tools/strip_sheet.gd`, `game/vsync_debug.gd` | B10, B16, B23, B24, B26 | B23 → B24 |
| Tests | `tests/test_hit_burst_config.gd`, `test_arrow_trail_config.gd`, `test_hit_burst_state.gd`, `test_arrow_trail_state.gd`, `cost_effects.gd`, `test_report.gd`, `fixtures/win_route.json` | B17–B22 | B17 → B18, B19 → B20, B21 → B22 |
| Generated process shader | `shaders/particles_generated.gdshader` (editor-generated, saved by Jiean, unused) | B25, B26 | B25 → B26 |
| Project | `project.godot` (Compatibility, line 25) | B02, B11 | — |

## One complete trace: input → state → output (final capture, play)

1. **Input:** the script presses Enter to confirm turn 4's attack orders (play master frame 243). Key presses go into the SubViewport as real input.
2. **State, the arrow:** `main.state` becomes `PLAY_ATTACKS`. The game's cue list plays `_cue_arrow` for the enemy, and an entry appears in `main._arrows` (frame 249).
3. **Effect B:** `arrow_trail_driver.gd` runs after `main` (`process_priority` 10). It sees the new arrow, spawns an `ArrowTrail` at its start point, and moves the trail to the tip each frame (line 69, main.gd's arc formula).
4. **State, the hit:** `_cue_impact` appends a `"damaged"` event for `p1` to `main.played_events` (frame 259). On the same frame, `_tick_fx()` drops the arrow from `main._arrows`.
5. **Both drivers, same frame:**
   - The trail driver stops both emitters (line 74) and starts the 0.7 s countdown.
   - `hit_burst_driver.gd` reads the new event (line 44) and instances a `HitBurst` under itself (line 75). It places the burst at the archer's position + (0, −40) = (320, 594) (line 77), and sets every emitter's `speed_scale` from `main.time_scale` and `main.paused`.
6. **Output:** the red glow, splinters and dust appear on frame 259, over the archer's body (B04). The trail's dots fade from the oldest end.
7. **Afterwards:**
   - the burst is freed when `Dust` reports `finished` (frame 297);
   - the trail is freed 0.7 s of game time after its arrow landed.

## Trade-offs named

- **CPU node for Effect A, GPU node for Effect B.** The burst's 23 particles need no GPU-only feature, and their settings sit on the node, so the test reads them directly. The wisps need turbulence, which only the GPU node has. Headless, the GPU node's price is near zero by construction, so its real price is GPU time (B21–B24).
- **A new instance per hit (overlap) instead of re-firing one node.** This keeps the second hit of a turn (failure 1 of the brief), at the cost of up to 2 bursts alive at once (46 particles).
- **World-space emission instead of `trail_enabled`.** `trail_enabled` draws nothing on Compatibility (measured). The emitter follows the arrow with `local_coords` off, so the line is a row of dots at the GPU node's `fixed_fps` 30, about 20–25 px apart (B12).
- **Polling instead of signals.** The game sends no signals. The drivers read `played_events` and `_arrows` every frame after `main`, and never write game state. The trail stops 0 to 2 frames before the impact cue at 60 fps (Revision 1 item 3); the cause was not investigated, because game timing is out of scope.
