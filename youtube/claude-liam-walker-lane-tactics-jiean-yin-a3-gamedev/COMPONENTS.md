# COMPONENTS — what Assignment 3 added, and where the film shows it

Source: commit `e415255`. Assignment 3 added exactly eight authored files under `godot/` (`git diff --stat film-source-v1 e415255 -- godot`, ignoring one `.uid`), plus the Blender sources and scripts outside `godot/`. Everything else in `godot/` is the unchanged Assignment 2 slice (excluded in [gamedev-evidence.json](gamedev-evidence.json) with that reason).

| Component | Files | What enters → what changes → what you see | Beats |
|---|---|---|---|
| **Build scripts** (outside `godot/`) | `tools/blender/build_archer_piece.py`, `build_board_square.py`, `build_goal_flag.py` | The `execute_blender_code` bodies Claude ran through the Blender MCP, one call per part (bmesh primitives, flat Principled BSDF per colour), then join + apply transforms → one mesh per `.blend`, origin at the base, scale 1 | B03 (bow and eye lines) → B04; B10 (A3-R1 colour) → B11 |
| **archer_piece** | `assets/models/archer_piece.glb` (+ `.import`), `blender/archer_piece.blend` | 6 shapes, 254 tris, 0.40 × 0.40 × 0.80 m. Bow (z 0.15–0.65) in front of the eye (z 0.60) on +X → eye hidden in profile → Jiean's hand edit: bow +0.08 m in Y (Edit Mode) | B02, B04, B05, B09 |
| **board_square** | `assets/models/board_square.glb` (+ `.import`) | slab + 4 border strips, 60 tris, 1.00 × 1.00 × 0.05 m; border `#CDB98E` → `#9A7F55` (A3-R1, 1.15 → 2.27 : 1) | B02, B10, B11 |
| **goal_flag** | `assets/models/goal_flag.glb` (+ `.import`) | base, pole, flag box 0.28 × 0.02 × 0.20 m; 84 tris; 0.45 × 0.30 × 1.20 m; 2 cm cloth → edge-on from ±X | B02, B06, B08 |
| **Export** (outside `godot/`) | `tools/blender/export_glb.py` | headless Blender from the committed `.blend` files, `export_yup=True`; refuses unless one mesh with location 0, rotation 0, scale 1 | named in BCRD (route chosen by Jiean); not excerpted |
| **Diorama scene** | `diorama/asset_diorama.tscn`, `project.godot` | floor 5 × 3 m at y 0, one DirectionalLight3D, WorldEnvironment, Camera3D (0, 1.1, 3), the three `.glb` at x −1.2 / 0 / 1.1, y 0 → the three stand on the floor in view | B07 → B08, B09 |
| **Headless check** | `tests/check_assets.gd`, `tests/test_report.gd` | loads each `.glb`, then the diorama; waits a frame (line 173); measures AABB, height axis, lowest y, scale/rotation, triangles, albedo, floor gap, frustum, overlap → JSON report | B12 → B13 |

## One complete input → state → output trace

**Input:** line 135 of `build_archer_piece.py` puts the bow box (0.03 × 0.06 × 0.50 m) at (0.165, 0, 0.40) on the facing (+X) side; line 140 puts the eye cube at (0.105, 0, 0.60) on the same side.
**State:** the joined mesh has bow vertices at x 0.15–0.18, y −0.03…0.03, z 0.15–0.65 — in front of the eye seen from +X. No number fails: size 0.40 × 0.40 × 0.80, 254 tris.
**Output:** in Jiean's recording (B04, 0:00–0:09.6) the bow covers the eye from the side. Jiean's hand edit moves the bow's 8 vertices +0.08 m along Y (B05; read back through the MCP as y 0.05…0.11, FRICTIONAL ~18:30). After export (+Y up: Blender Y → Godot −Z), the running scene from +X shows the eye beside the bow (B09, run-02 shot D).

## Trade-offs named in the film

- One MCP call per part made every step checkable (`get_scene_info` after each), but the plan was checked against numbers, and the eye problem only showed when someone looked.
- A thin box is the cheapest flag (12 tris) but vanishes edge-on; not fixed, the diorama's own camera faces its broad side.
- The headless check is repeatable and exact to four decimals, but it uses a dummy renderer: it cannot see the pale linen under the lamp or the edge-on flag.
