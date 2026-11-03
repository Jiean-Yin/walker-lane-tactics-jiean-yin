@AGENTS.md

# Project context

Every fact below has a file reference. Line numbers are from commit `5a32988`.

- **Engine:** Godot 4.7 (`godot/project.godot:9`, `config/features` "4.7"); the exact build, 4.7.2 standard (not .NET), is recorded in `README.md` (tool table) and `AGENTS.md`.
- **Renderer:** Compatibility, `renderer/rendering_method="gl_compatibility"` (`godot/project.godot:24`, mobile also Compatibility at `:25`). HDR 2D is not set in `project.godot`. Default 2D texture filter is set to 1 (`project.godot:23`).
- **Main scene:** `res://game/main.tscn` (`godot/project.godot:7`): a `Node2D` running `godot/game/main.gd` plus an `AudioDirector` node (`godot/game/main.tscn:6-10`). Viewport 1280 × 720, stretch `canvas_items` (`project.godot:15-18`).
- **3D scene:** `godot/diorama/asset_diorama.tscn`, not connected to the 2D game (`README.md`, A3 section).

## The object the `exposed` tint shades (2D)

- The player archer is a `piece.gd` node (`godot/game/piece.gd`), built by `main._build_pieces()` (`godot/game/main.gd:336-352`) under the y-sorted `Pieces` root (`main.gd:119-123`). Pieces are freed and rebuilt on start (`main.gd:308`) and on retry / play again (`main.gd:329`).
- It is drawn by one `Sprite2D` child, `_sprite` (`piece.gd:35`), created once in `setup()` (`piece.gd:51-54`). `_apply_visual()` (`piece.gd:163-186`) swaps its `texture` per pose, sets `modulate`, `scale`, `flip_h` and `position`. No material is set anywhere today.
- Textures: `res://assets/art/archer_<state>.png` for the player, `archer_<state>_enemy.png` for the enemy (`piece.gd:4-6`, `:135-148`); `archer_idle_enemy.png` exists, so the enemy idle has `modulate` white. Only if an enemy image is missing does it fall back to the player image with `ENEMY_TINT` in `modulate` (`piece.gd:17`, `:141-143`).
- Without any image the piece draws a code placeholder in `_draw()` and hides the sprite (`piece.gd:170-173`, `:191-233`); a material on the sprite would not shade that.
- The pieces' own clock: `tick(dt)` is called by main with scaled time and not while paused (`piece.gd:110-111`, `main.gd:162-171`).

## The game state that drives the effect

- Owner: `godot/game/main.gd`. Fields: `state` (`main.gd:76`, enum at `:13`), `planned_offset` (`main.gd:86`), `paused` (`main.gd:77`, set only in `_set_paused()` `:297-299`), `time_scale` (`main.gd:73`). `PLAYER_ID` is `"p1"` (`main.gd:17`); `pieces` maps unit id → piece (`main.gd:93`).
- PLAN_MOVE begins in `_begin_plan_move()` (`main.gd:357-362`, resets `planned_offset` to zero); arrows change it via `_adjust_move()` (`main.gd:365-369`); Enter / Space leave it via `_confirm_move()` → `PLAY_MOVES` (`main.gd:372-381`); R calls `_restart(true)` (`main.gd:262-263`, `:313-333`).
- Game time: `dt = delta * time_scale`, advanced only when `not paused` (`main.gd:162-171`). The game never uses `get_tree().paused` (`main.gd:6`).
- Unit cells live in `rules.units` (`godot/game/rules.gd:29`); read with `RulesScript.cell_of()` and `rules.get_unit()`, liveness with `rules.is_alive()` (used at `main.gd:656`). Reach: `Rules.in_range()` (`rules.gd:120-123`, Chebyshev 1..2).
- Target red `COL_TARGET = #E0453A` (`main.gd:47`); board squares `#D8C7A0` / `#CDB98E` (`main.gd:41-42`).

## The 3D object for the textured shader

- Scene: `godot/diorama/asset_diorama.tscn`. Today it holds `WorldEnvironment` (ambient colour light, energy 0.35, `:15-25`), a 5 × 3 m `Floor` `PlaneMesh` with an inline `StandardMaterial3D` (`:7-13`, `:27-28`), one `DirectionalLight3D` `Lamp` with shadows (`:30-33`), `Camera3D` at (0, 1.1, 3), fov 50 (`:35-39`), and the three A3 `.glb` instances (`:41-47`).
- The brief's objects, `LinenSquareLight` and `LinenSquareDark` (`MeshInstance3D` + 1 m `PlaneMesh`), **do not exist yet**; the A3 `board_square.glb` is not used because it has no UVs (`CHANGE-BRIEF.md` §4).
- Material source (planned, per `CHANGE-BRIEF.md` §4): `ShaderMaterial` files `godot/materials/linen_light.tres` and `linen_dark.tres` using `godot/shaders/linen_square.gdshader`, with textures from `godot/assets/textures/hessian_380/` (files present; credits in `ATTRIBUTION.md` there).
- `godot/tests/check_assets.gd` loads this scene (`:168`) and requires exactly one `Light3D` (`:183-187`).

## Test commands (all through `scripts/run-test.sh`)

The wrapper (`scripts/run-test.sh`) takes `<test-file.gd> <fps>`, runs `${GODOT:-godot} --headless --path godot --script res://tests/<file> --fixed-fps <fps>` under `timeout 120`, tees to `logs/<name>_<fps>fps.log`, and fails if the log contains `SHADER ERROR` or `SCRIPT ERROR`. Set `GODOT` to the console build. Run from the repository root:

```bash
./scripts/run-test.sh test_rules.gd 60         # rules engine, 51/51 at baseline
./scripts/run-test.sh test_audio_events.gd 60  # main.tscn driven by key presses, 70/70
./scripts/run-test.sh check_assets.gd 60       # A3 diorama assets, 38/38
```

Baseline counts and the two known non-failing `ERROR` lines are in commit `eb1ff2a` and `evidence/a5/baseline/`. Each suite also writes `evidence/<name>-<unix time>.json` (`godot/tests/test_report.gd:2`, `:34`). Before the first run, and after adding textures or shaders, import once (not a test, so not through the wrapper; `README.md` A3 section): `"$GODOT" --headless --path godot --import`. Clean saved logs with `scripts/redact-paths.sh` before committing them.

Not wrapper suites: `godot/tests/capture.gd` needs a real renderer (`capture.gd:2-3`), and `analyze_variants.gd` is analysis (`analyze_variants.gd:2`). `route_runner.gd` and `test_report.gd` are helpers.

# Current change

@CHANGE-BRIEF.md

# Ownership

Files in `godot/shaders/` are hand-written by the human (Jiean) and are never edited by an agent: not created, not changed, not "fixed", not reformatted. That includes `exposed_tint.gdshader`, `linen_square.gdshader` and `hint_experiment.gdshader`. If a shader looks wrong, report it with the evidence and stop.

# Out of scope

- Game rules and state: `godot/game/rules.gd`, the `State` machine, every timing constant and transition in `main.gd`, and how input is handled. No new key. The driver reads `state`, `planned_offset`, `paused`, `time_scale` and unit cells; it never writes them.
- Everything the player sees apart from the archer sprite's tint: the board drawing, markers, HUD, cards, effects, the enemy piece's look, sounds and music.
- Existing tests and their expected counts (`test_rules`, `test_audio_events`, `check_assets`): new checks go in new test files.
- Every A2 and A3 asset file: the art PNGs, sounds, music, the `.glb` models, `.blend` files and Blender scripts. No importer material on `board_square.glb`; the existing diorama nodes, lamp, environment and camera stay as they are (only the two new tiles are added).
- Engine and project settings: renderer, HDR 2D, stretch, filters in `project.godot`.
- No use of `TIME` in the tint; no shared `ShaderMaterial` across pieces; the DirectX normal map is never bound.

# Unconfirmed

1. The exact Godot build (4.7.2) is only in `README.md`/`AGENTS.md`; `project.godot` says "4.7". Not run in this step.
2. `godot/shaders/`, `godot/materials/`, the two linen tiles, `hint_greys.png` and the script that writes it, and the A5 test files do not exist yet; their names and the commands that will run them are not known. They should go through the wrapper at 30, 60 and 144 fps (`CHANGE-BRIEF.md` R2).
3. The Hessian 380 textures have no `.import` files yet, so the import settings in `CHANGE-BRIEF.md` §4 (lossless, normal-map flag, mipmaps) are not in place and were not checked.
4. Where the driver will live (in `main.gd`, in `piece.gd`, or a new node) is not decided in the files. A new driver means editing a game script, which this step did not do; the brief allows presentation code that only reads state.
5. Whether `_apply_visual()` resetting the sprite each pose change would interact with a material was not checked; nothing in `piece.gd` sets or clears `material` today.
6. The brief's pixel predictions (P1, P2 screen positions) and the Compatibility-renderer behaviour of `source_color` were not re-measured here.
7. The import command is taken from `README.md`; `scripts/run-test.sh` has no import mode.
