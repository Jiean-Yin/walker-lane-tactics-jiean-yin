@AGENTS.md

# Project context

Every fact has a file reference. Line numbers are from commit `6a1b458` (brief v1). `git diff` shows no content change in the working copy (`project.godot` and five `.import` files differ only in line endings).

## Engine and project

- **Godot 4.7.2.stable.official.ed1daf0bf**, standard build (`README.md:11`; printed by the A6 baseline run, `evidence/a6/baseline/check_assets_60fps.log:1`). `project.godot` records only "4.7" (`godot/project.godot:15`).
- **Renderer:** Compatibility, `renderer/rendering_method="gl_compatibility"` (`godot/project.godot:25`, mobile `:26`). On it `trail_enabled` draws nothing (measured, `CHANGE-BRIEF.md` §0).
- **Main scene:** `res://game/main.tscn` (`project.godot:14`): `Main` (`Node2D`, `main.gd`), `AudioDirector`, and `ExposedDriver` with `process_priority = 10` (`godot/game/main.tscn:7-15`). Viewport 1280 × 720, stretch `canvas_items` (`project.godot:19-21`); no camera (`main.gd:18`, `VIEW` constant; no `Camera2D` in `main.tscn`).
- **Layers built in code** by `main._ready()` (`main.gd:109-128`): board z 0 (`:117`), `Pieces` y-sorted z 1 (`:119-123`), `_fx_layer` z 2 (`:124`), HUD z 3 (`:125`). Layers are `draw_layer.gd` nodes at the origin that call a draw callable (`godot/game/draw_layer.gd:1-9`).

## The two effects (node types from the brief)

- **Effect A, hit burst:** `CPUParticles2D` ×3 (`Flash`, `Splinters`, `Dust`) under `Node2D` `HitBurst`, in `godot/effects/hit_burst.tscn` (`CHANGE-BRIEF.md` §1 "The settings").
- **Effect B, arrow trail:** `GPUParticles2D` ×2 (`Streak`, `Wisps`), each with its own `ParticleProcessMaterial`, under `Node2D` `ArrowTrail`, in `godot/effects/arrow_trail.tscn` (`CHANGE-BRIEF.md` §2 "The settings").
- **Scenes they appear in:** the game, `godot/game/main.tscn` (instanced at run time; parent not yet decided), and the fixture previews `godot/previews/hit_burst_preview.tscn` and `arrow_trail_preview.tscn` (`CHANGE-BRIEF.md` §5). None of `godot/effects/` or `godot/previews/` exists yet (Glob of `godot/`).

## What owns each event or condition (no signals)

- **There are no signals.** No `signal`, `connect(` or `emit` in any `godot/**/*.gd` (searched). Playback is a cue list: `_schedule()` (`main.gd:181-185`) queues callables, `_run_cues()` (`:193-196`) calls them from `_process()` (`:162-171`) when the game clock reaches them.
- **Effect A event:** `main._cue_impact(head, hits)` (`main.gd:498-513`), scheduled at `t + DRAW_LEAD + ARROW_TIME` (`:472`). Per hit it appends to `played_events` (`:502`), takes `pieces[ev["unit"]]` (`:503`), and the `"damaged"` arm runs at `:505-511`; `"killed"` sets the defeat pose (`:512-513`). A piece's `position` is its base-disc centre (`piece.gd:4`); the archer is 80 px tall (`piece.gd:9`).
- **Not a hit:** `_cue_cancel()` (`main.gd:522-527`) for `"attack_cancelled"`; it draws "no target" and no arrow.
- **Effect B condition:** `main._arrows` non-empty (`main.gd:102`). Appended by `_cue_arrow()` (`:490-495`, scheduled at `:471`, start point `p.position + (14·facing, −36)`, `:493`). `_tick_fx()` advances each `t` and drops it once `t >= ARROW_TIME` (`:199-205`); it is called only while not paused (`:166-171`), after `_run_cues()` in the same frame (`:168`, `:171`). Tip position: `main.gd:718-721` (`ARROW_TIME` 0.35, `ARROW_ARC` 40, `:30-31`).
- **Clock and pause:** `time_scale` (`main.gd:73`), `paused` (`:77`, set only in `_set_paused()` `:297-299`); game `dt = delta * time_scale` and stops while paused (`:162-171`). The tree is never paused (`main.gd:6`).
- **Reset:** R → `_restart(true)` (`main.gd:262-263`, `:313-333`) clears cues, `_arrows` (`:319`) and floaters, then rebuilds pieces; `_build_pieces()` frees the old ones (`:336-340`). Start from the title: `_start_play()` (`:304-309`).
- **Pattern for a read-only presentation node:** `exposed_driver.gd` is a child of `Main` with `process_priority` 10, so it runs after `main._process` each frame and only reads state (`godot/game/exposed_driver.gd:1-12`, `:29-37`).
- **Input map:** built in code from `ACTION_KEYS` (`main.gd:51-65`, `_ensure_actions()` `:139-147`). F3 is already `lt_debug`; V is unused (`:53-65`).

## Test commands (all through `scripts/run-test.sh`)

Usage `scripts/run-test.sh <test-file.gd> <fps|realtime> [timeout-seconds]` (`scripts/run-test.sh:2`). It runs `${GODOT:-godot} --headless … --path godot --script res://tests/<file>` under `timeout` (default 120 s, `:13`). A number adds `--fixed-fps <n>` (`:10`); **`realtime` passes no `--fixed-fps`, so frames run on the wall clock** (`:7-8`). Log: `logs/<name>_<n>fps.log` or `logs/<name>_realtime.log` (`:12`). Exit status is Godot's, forced to 1 if the log has `SHADER ERROR` or `SCRIPT ERROR` (`:14-16`). Set `GODOT` to the console build (`:4`). From the repository root:

```bash
"$GODOT" --headless --path godot --import                   # once, and after adding resources (README.md:36); not a test
./scripts/run-test.sh test_rules.gd 60                       # 51/51
./scripts/run-test.sh test_audio_events.gd 60                # 70/70
./scripts/run-test.sh check_assets.gd 60                     # 38/38
./scripts/run-test.sh test_exposed_tint.gd 30                # 46/46, also at 60 and 144
./scripts/run-test.sh test_materials.gd 60                   # 148/148
./scripts/run-test.sh <file>.gd realtime 300                 # realtime mode with a longer timeout
```

Existing commands: `README.md:46-52`. Baseline counts: commit `5bcaf78` and `evidence/a6/baseline/`. Each suite writes `evidence/<name>-<unix time>.json` via `godot/tests/test_report.gd` (`:2`). Tests press real keys with `root.push_input()` (`test_audio_events.gd:34`, `:42`; `test_exposed_tint.gd:52`) and sample after everything else from a node with `process_priority` 1000 (`test_exposed_tint.gd:5-7`). Planned A6 files (`CHANGE-BRIEF.md` §4): `test_hit_burst_config.gd`, `test_arrow_trail_config.gd`, `test_hit_burst_state.gd`, `test_arrow_trail_state.gd`, `cost_effects.gd`; none exists yet. Clean logs with `scripts/redact-paths.sh` before committing.

## Headless facts (confirmed in review, 2026-11-08, throwaway probes under `--headless --fixed-fps 60`)

- A headless run uses a dummy renderer: it draws no particles and runs no GPU particle process. Node state (emitting, one_shot, amount_ratio, visibility, instance counts) is observable; the look is not.
- A GPU effect's headless CPU price is near zero by construction. Measured: mean frame 0.002 ms empty, 0.002 ms with 20 000 `GPUParticles2D` particles, 1.717 ms with 20 000 `CPUParticles2D` particles.
- Frame strips come from a windowed Movie Maker run, which I start.
- Headless details: a one-shot `CPUParticles2D` simulates and emits `finished` after its lifetime (frame 31 for 0.5 s at 60 fps). A one-shot `GPUParticles2D` turns `emitting` false after about its lifetime but never emits `finished`, and `capture_rect()` returns an empty rectangle. A continuous `GPUParticles2D` keeps `emitting` true, and hiding it does not change `emitting`.
- From A5, still true: the dummy renderer parses shader code; `--fixed-fps N` makes every `delta` exactly `1/N`; game time is `delta * time_scale` and stops while `paused` (`main.gd:162-171`); tests press real keys with `root.push_input()`.

# Current change

@CHANGE-BRIEF.md

# Ownership

- Files in `godot/shaders/` are hand-written by the human (Jiean) and are never edited by an agent: not created, not changed, not "fixed", not reformatted. That includes `exposed_tint.gdshader`, `linen_square.gdshader`, `hint_experiment.gdshader` and `standard_generated.gdshader`. If a shader looks wrong, report it with the evidence and stop.
- **Effect settings live in the scene files in `godot/effects/`, not in code.** Every emitter value in `CHANGE-BRIEF.md` §1-2 is saved in `hit_burst.tscn` / `arrow_trail.tscn`. Trigger code only instances a scene, places it, sets `emitting`, `speed_scale`, `visible` and position at run time, and frees it. It never sets `amount`, `lifetime`, colours, curves or any other look value.

# Godot 4 names

- Use Godot 4.7.2 class and property names only. The names in the brief's tables were listed from `ClassDB` on 2026-11-08 (`CHANGE-BRIEF.md:7`, §0).
- Godot 3 names never to write: `ParticlesMaterial` (now `ParticleProcessMaterial`; it does not exist, §0), `Particles2D` (now `GPUParticles2D`), `GradientTexture` (now `GradientTexture1D`), unsuffixed `initial_velocity`, `scale_amount`, `damping`, `angular_velocity`, `angle` (now `_min` / `_max` pairs), `flag_align_y` / `flag_disable_z` (now `particle_flag_align_y` / `particle_flag_disable_z`).
- Trap (measured, §0): `ParticleProcessMaterial` still has editor-only `initial_velocity`, `scale`, `damping`, `angle` and `angular_velocity` (Vector2 range pairs, not stored). What loading one of them from a `.tscn` does has **not** been measured; mutation 1 will show it (`CHANGE-BRIEF.md` §6 failure 2). `CPUParticles2D` has none of them.
- Types (listed from `ClassDB` in review, 2026-11-08): `CPUParticles2D.direction` / `gravity` are `Vector2`, `ParticleProcessMaterial` ones `Vector3`; `CPUParticles2D.color_ramp` is a `Gradient` and `scale_amount_curve` a `Curve`; `ParticleProcessMaterial.color_ramp` is a `GradientTexture1D` and `scale_curve` a `CurveTexture`; `CanvasItemMaterial.BLEND_MODE_MIX` = 0.
- Both particle nodes have `restart()` and a `finished` signal (`ClassDB`, review). Headless, `finished` fires only on `CPUParticles2D` (see "Headless facts"), so freeing a GPU effect must use its own game-time timer.

# Out of scope

- Game logic: `rules.gd`, the `State` machine, every timing constant, cue and transition in `main.gd`. The trigger code reads `played_events`, `_arrows`, `pieces`, `time_scale`, `paused` and `state`; it never writes them or adds cues.
- Input, except the one debug key the brief allows: V toggles vsync for the GPU price (`CHANGE-BRIEF.md` §3). No other new key, and F3 keeps its meaning.
- Everything already on screen: the board, markers, HUD, cards, floaters, the drawn arrow, the archer sprites and their A5 tint, sounds and music. The effects add nodes; they don't change `_draw_fx()` or any existing drawing.
- Existing tests and their counts (51, 70, 38, 46 at 30/60/144, 148): new checks go in new files.
- `godot/shaders/`, every A2/A3/A5 asset (art, audio, `.glb`, `.blend`, Hessian textures, materials), and `project.godot` (renderer, stretch, filters, HDR 2D). No sourced or generated image files: textures are `GradientTexture2D` inside the scenes (`CHANGE-BRIEF.md` §3).
- Godot's own `trail_enabled` (draws nothing on Compatibility), additive blending, and a fixed seed outside the preview scenes.

# Unconfirmed

1. Where effect instances are parented in the game (a new effects node under `Main`, `_fx_layer`, or `Main` itself) and which script spawns them (`main.gd` or a new read-only node like `exposed_driver.gd`). Either way a game script is edited. Not decided in the files.
2. Draw order: the brief gives `HitBurst` `z_index` 2, the same z as `_fx_layer` (`main.gd:124`), which draws HP pips, the arrow and the "−3" floater. Equal z falls back to tree order, so whether the burst is over or under the floater depends on item 1.
3. Same-frame order: the impact cue runs in `_run_cues()` before `_tick_fx()` drops the arrow (`main.gd:168`, `:171`), so the arrow may leave `_arrows` on the impact frame or the one after. Not measured.
4. How a spawner sees an event in time: no signal exists, so it must poll `played_events` / `_arrows` each frame after `main._process` (as `ExposedDriver` does with priority 10). Not tested for effects.
5. The fps or mode for each new A6 test, and whether `cost_effects.gd` uses `realtime`, are not stated in the brief or the wrapper. The brief only fixes 60 fps for the state tests (§4).
6. `CPUParticles2D` / `GPUParticles2D` behaviour with `speed_scale` 0 and with the tree paused was not run; rules A5 and B4 are predictions until the state tests run. (Hiding keeps `emitting` unchanged: measured in review.)
7. *(Resolved in review: the types and signals are now listed from `ClassDB`, see "Godot 4 names".)*
8. The agent ran nothing in Step 1; the review confirmed the 4.7.2 build in every probe's start-up line.
