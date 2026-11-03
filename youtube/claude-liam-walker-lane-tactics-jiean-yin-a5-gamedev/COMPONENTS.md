# COMPONENTS — what the film explains

Ledger: `gamedev-evidence.json` (every authored `godot/` file at tag `a5`, hashed, associated or excluded with a reason).

| Component | Files | Beats | Code → result |
|---|---|---|---|
| Exposed tint shader | `shaders/exposed_tint.gdshader` | B03, B04, B06, B07 | B03 → B04 |
| Exposed driver | `game/exposed_driver.gd`, `game/piece.gd`, `game/main.tscn`, reads `game/main.gd`, `game/rules.gd` | B05, B06 | B05 → B06 |
| Linen materials | `shaders/linen_square.gdshader`, `materials/linen_light.tres`, `linen_dark.tres`, `diorama/asset_diorama.tscn`, the Hessian 380 textures and `.import` files | B08–B11 | B08 → B09, B10 → B11 |
| Hint experiment | `shaders/hint_experiment.gdshader`, `hint/hint_experiment.tscn`, `materials/hint_srgb.tres`, `hint_raw.tres`, `hint_greys.png`, `tools/write_hint_greys.gd` | B12, B13 | B12 → B13 |
| Generated shader | `shaders/standard_generated.gdshader` | B14 | (still, verbatim lines) |
| Tests | `tests/test_exposed_tint.gd`, `test_materials.gd`, `normal_map_check.gd`, `test_report.gd`, `tools/calibrate_normal_map_check.gd`, `MATERIALS.md`, the earlier suites | B10, B15, B16 | B15 → B16 |
| Capture tool | `debug/capture_exposed.gd`, `.tscn` | B07 | — |
| Project | `project.godot` (Compatibility, line 25) | B02, B13 | — |

## One complete trace: input → state → output

1. **Input:** the player presses Right on turn 3 (capture frame 245; `game/main.gd` `_unhandled_input` → `_adjust_move`).
2. **State:** `main.planned_offset` becomes (1, 0); `state` is `PLAN_MOVE`; the planned cell (3, 4) is within the enemy's Chebyshev reach 1–2 of (5, 3) (`rules.gd:120-123`).
3. **Driver:** `exposed_driver.gd:33` sets the target to 1.0; line 34 moves `amount` by 5 × 1/30 = 0.1667 per frame; line 37 writes it to the player's own `ShaderMaterial` (`piece.gd:65-68`).
4. **Shader:** `exposed_tint.gdshader:7` mixes each archer pixel 0.1667 × 0.7 of the way toward #E0453A on that frame, and reaches the full 70 % after six frames (frame 250).
5. **Output:** the archer turns red on screen (B04); Jiean's C-key captures measure the same mix at fixed values (B07).

## Trade-offs named

- **One `ShaderMaterial` per sprite** (R6): no shared-material bleed onto the enemy, at the cost of one material per piece.
- **`move_toward` on game time:** frame-rate independent and turns around on retrigger; at 30 fps floating-point rounding makes a full fade 7 frames (0.233 s), exactly on R2's one-frame tolerance.
- **Lossless 1K textures:** exact data for the curl check and the normal map, at about 9.8 MB of GPU memory for the three bound textures (MATERIALS.md review).
