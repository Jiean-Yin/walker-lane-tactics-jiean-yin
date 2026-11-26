@AGENTS.md

# Project context

Every fact has a file reference. Line numbers are from commit `e08eb62` (A7 brief v1). The working copy has no content change (`git diff --ignore-cr-at-eol` is empty; `project.godot` and five `.import` files differ only in line endings).

## Engine and project

- **Godot 4.7.2.stable.official.ed1daf0bf**, standard build (`README.md:11`; first line of every A7 baseline log, e.g. `evidence/a7/baseline/check_assets_60fps.log:1`). `project.godot` records only "4.7" (`godot/project.godot:15`).
- **Renderer:** Compatibility, `renderer/rendering_method="gl_compatibility"` (`godot/project.godot:25`, mobile `:26`).
- **Main scene:** `res://game/main.tscn` (`project.godot:14`). Children of `Main` today: `AudioDirector`, `ExposedDriver`, `HitBurstDriver`, `ArrowTrailDriver` (the three with `process_priority = 10`), `VsyncDebug` (`godot/game/main.tscn:10-30`). Viewport 1280 × 720, stretch `canvas_items` (`project.godot:19-21`); no camera (`main.gd:18`).
- **Layers built in code** by `main._ready()` (`main.gd:109-128`): board z 0 (`:117`), `Pieces` y-sorted z 1 (`:119-123`), `_fx_layer` z 2 (`:124`), HUD z 3 (`:125`). The board's enemy back row is column 7 (`rules.gd:20`), tinted red at `main.gd:638-639`; board origin and square size `main.gd:19-20`.

## The two clips (route and node, from the brief)

- **`wave` (cycle):** `Sprite2D` `FlagSprite` sliced `hframes = 4`, `vframes = 1`, keyed by an `AnimationPlayer` frame track plus a discrete `offset` track, autoplay, `ANIMATION_CALLBACK_MODE_PROCESS_IDLE`. Lives in a new prop `GoalFlag` added to `main.tscn` (`CHANGE-BRIEF.md` §1-3, §7). Sheet: `godot/assets/art/flag/flag_red.png`, 500 × 249, CC0 (`godot/assets/art/flag/ATTRIBUTION.md:5-19`).
- **`shoot` (committing action):** cutout rig of plain `Node2D` pivots and `Sprite2D` parts cut by `region_rect` from `archer_draw.png` / `archer_draw_enemy.png`, keyed on `position` / `rotation`, no `Bone2D`. New scene `godot/game/archer_rig.tscn` (`Mount` → `Rig` → `Lower`, `Upper` → `UpperSprite`, `Bow` → `BowSprite`, plus `AnimationPlayer` with `root_node` = `Mount`), one instance per `piece.gd`, `ANIMATION_CALLBACK_MODE_PROCESS_MANUAL`, advanced by `piece.tick(dt)` (`CHANGE-BRIEF.md` §1, §4, §6).
- **Clip resources:** `godot/animations/shoot.tres`, `wave.tres` (`CHANGE-BRIEF.md` §7). None of `godot/animations/`, `archer_rig.tscn`, `GoalFlag` or `godot/previews/shoot_preview.tscn` exists yet (Glob of `godot/`).
- **Scenes the clips appear in:** the game `godot/game/main.tscn` (flag as a node; rig instanced at run time by each piece, pieces built by `main._build_pieces()` `main.gd:336-352`), and the fixture `godot/previews/shoot_preview.tscn` (`CHANGE-BRIEF.md` §9).

## Who owns the state machines

- **Player / game state machine:** `main.gd`, `enum State` (`main.gd:13`), field `state` (`:76`). No signals: `_schedule()` (`:181-185`) queues callables and `_run_cues()` (`:193-196`) calls them from `_process()` (`:162-179`). No `_physics_process` and no `AnimationPlayer` anywhere in `godot/**/*.gd|tscn` (searched).
- **Archer pose machine:** `piece.gd` `state` (`piece.gd:33`, poses `:15`), changed only through `set_state()` (`:82-88`). Callers: `main.gd:486` (`draw`), `:513` (`defeat`), `:519` (`idle`), `:551` (`win`); `piece.gd:92`, `:98-101`, `:116`, `:124`, `:137`, `:141`.
- **Attack cues:** `_cue_draw` at t (`main.gd:470`, `:481-487`), `_cue_arrow` at +0.2 s (`:471`, `:490-495`), `_cue_impact` at +0.55 s (`:472`, `:498-513`), `_cue_attacker_idle` at +0.8 s, only if still `draw` (`:473`, `:516-519`); constants `DRAW_LEAD` 0.2, `ARROW_TIME` 0.35, `ATTACK_RECOVER` 0.25, `ATTACK_GAP` 0.25 (`:29-33`).
- **Clock and pause:** `dt = delta * time_scale` (`main.gd:163`, `time_scale` `:73`); while `paused` (`:77`, set only in `_set_paused()` `:297-299`) no cue runs and no `piece.tick` happens (`:166-171`). Order inside one frame: `_run_cues()` → every `p.tick(dt)` → `_tick_fx(dt)` (`:168-171`). The tree is never paused (`main.gd:6`).
- **Inputs:** `_unhandled_input` (`main.gd:210-224`); gameplay keys during playback add 1 to `ignored_inputs` (`:289-290`); R → `_restart(true)` (`:262-264`, `:313-333`), which rebuilds pieces with `queue_free` (`:336-340`). V is `vsync_debug.gd` (`godot/game/vsync_debug.gd:6-13`).

## Test commands (all through `scripts/run-test.sh`)

Usage `scripts/run-test.sh <test-file.gd> <fps|realtime> [timeout-seconds]` (`scripts/run-test.sh:2`). It runs `${GODOT:-godot} --headless … --path godot --script res://tests/<file>` under `timeout` (default 120 s) (`:14`). A number adds `--fixed-fps <n>` (`:11`); **`realtime` passes no `--fixed-fps`, so frames follow the wall clock** (`:8-9`). Log: `logs/<name>_<n>fps.log` or `logs/<name>_realtime.log` (`:13`). Exit status is Godot's, forced to 1 if the log contains `SHADER ERROR`, `SCRIPT ERROR` or `Failed loading resource` (`:16`). `GODOT` = the console build (`:5`). From the repository root (counts from `evidence/a7/baseline/*.log`, `SUMMARY` lines):

```bash
"$GODOT" --headless --path godot --import          # once, and after adding resources (README.md:50); not a test
./scripts/run-test.sh test_rules.gd 60              # 51/51
./scripts/run-test.sh test_audio_events.gd 60       # 70/70
./scripts/run-test.sh check_assets.gd 60            # 38/38
./scripts/run-test.sh test_exposed_tint.gd 30       # 46/46 (also 60 and 144)
./scripts/run-test.sh test_materials.gd 60          # 148/148
./scripts/run-test.sh test_hit_burst_config.gd 60   # 107/107
./scripts/run-test.sh test_arrow_trail_config.gd 60 # 135/135
./scripts/run-test.sh test_hit_burst_state.gd 60    # 31/31
./scripts/run-test.sh test_arrow_trail_state.gd 60  # 31/31
./scripts/run-test.sh cost_effects.gd 60            # 25/25
./scripts/run-test.sh <file>.gd realtime 300        # realtime mode, longer timeout
```

Existing list: `README.md:59-72`. Planned A7 files, all at 60 (`CHANGE-BRIEF.md` §8): `test_flag_readback.gd`, `test_shoot_readback.gd`, `test_pins_a7.gd`, `test_anim_states.gd`, `test_shoot_edges.gd`; none exists yet. Each suite writes `evidence/<name>-<unix time>.json` via `godot/tests/test_report.gd:2`. Existing tests press keys with `root.push_input()` (`test_exposed_tint.gd:52`, `test_hit_burst_state.gd:61`) and sample from a node with `process_priority` 1000 (`test_exposed_tint.gd:245`). Headless runs use a dummy renderer: node state is observable, the look is not; frame strips come from Jiean's windowed Movie Maker run (`CHANGE-BRIEF.md` §9). Clean logs with `scripts/redact-paths.sh` before committing.

# Current change

@CHANGE-BRIEF.md

# Ownership

- Files in `godot/shaders/` are hand-written by the human (Jiean) and are never edited by an agent: not created, not changed, not "fixed", not reformatted. If a shader looks wrong, report it with the evidence and stop.
- **Clips live as resources** in `godot/animations/` (`shoot.tres`, `wave.tres`) or in the scene that owns them, and are **never built in code at runtime**: no `Animation.new()`, `add_track()` or `track_insert_key()` in game, preview or rig scripts. Tests may read clips back; they never create the clips the game plays.
- `flag_red.png`, `archer_draw.png` and `archer_draw_enemy.png` are never edited; the sheet's drift is fixed by the keyed `offset` track, the rig crops by `region_rect`.

# One authority

Exactly one node writes each animated property. Never add a second writer to a node that already has one.

| Animated node (property) | Its one writer | Nobody else may write |
|---|---|---|
| `GoalFlag/FlagSprite` (`frame`, `offset`) | the flag's `AnimationPlayer`, clip `wave` | no script, test or preview sets them |
| `Mount/Rig` (`position`) | the rig's `AnimationPlayer`, clip `shoot` | not `piece.gd`, not hop lift, not facing |
| `Rig/Upper`, `Upper/Bow` (`rotation`) | the rig's `AnimationPlayer`, clip `shoot` | not `piece.gd` |
| the rig's `AnimationPlayer` (play, stop, `advance`) | `piece.gd` only (`set_state` / `tick`) | not `main.gd`, drivers or tests (tests read `current_animation*`) |
| `Mount` (placement, scale, facing flip, `visible`) | `piece.gd` only | not keyed by any clip |
| piece `_sprite` (texture, position, scale, flip) | `piece.gd` `_apply_visual()` (`piece.gd:180-203`) | unchanged; not keyed |
| `exposed_amount` on each piece's `ShaderMaterial` | `ExposedDriver` via `set_exposed_amount()` (`exposed_driver.gd:37`, `piece.gd:65-68`) | the rig's parts reuse that piece's material; they add no writer |
| piece node `position` | already two writers: `main.gd` (`:350`, `:422`) and `piece.tick` hop (`piece.gd:132`) | not touched by A7 |

# Godot 4 names

- Use Godot 4.7.2 names only: `AnimationPlayer`, `AnimationLibrary`, `Animation`, `Sprite2D` (`hframes`, `vframes`, `frame`, `offset`, `region_enabled`, `region_rect`), `Animation.loop_mode` with `Animation.LOOP_NONE` / `LOOP_LINEAR`, `Animation.step`, `Animation.UPDATE_DISCRETE` / `UPDATE_CONTINUOUS`, `AnimationPlayer.speed_scale`, `callback_mode_process` with `ANIMATION_CALLBACK_MODE_PROCESS_IDLE` / `_MANUAL`, `advance()`, `autoplay`, `current_animation`, `current_animation_position`, `root_node`.
- Godot 3 names never to write: a boolean `loop` on `Animation`, `playback_speed`, `playback_process_mode`, `method_call_mode`, `AnimatedSprite` (now `AnimatedSprite2D`), `Sprite` (now `Sprite2D`), `Position2D` (now `Marker2D`). No `Bone2D`, no `AnimatedSprite2D` and no `AnimationTree` in this change (`CHANGE-BRIEF.md` §5-6).
- **Not checked in this session:** none of the names above was listed from `ClassDB` on 4.7.2 here. In particular I am **not sure** `callback_mode_process` and its enum still sit on `AnimationMixer` in 4.7.2, how per-key easing is stored in a `.tres` (`transitions` array), or that `track_problems()` (`CHANGE-BRIEF.md` §8) is a Godot method at all. Confirm with `ClassDB` before relying on them.

# Out of scope

- Game logic and timing: `rules.gd`, `main.gd`'s `State` machine, cue list, every constant and transition. Presentation reads `piece.state`, `_arrows`, `paused`, `time_scale`; it never writes game state or adds cues. The only script edits are `piece.gd` (instance, show, start and advance the rig) and the new `GoalFlag` node in `main.tscn`.
- Input: no new key; F3 and V keep their meaning. No collision, no movement change.
- Existing tests and their counts above; new checks go in new files.
- The A6 effects, their scenes and drivers; the board, HUD, floaters, the drawn arrow, sounds and music; the A5 tint (the rig carries it, never changes it); `tint_material()` must keep returning the `_sprite`'s material (`test_exposed_tint.gd:64-68`).
- `godot/shaders/`, every A2/A3/A5 asset file, the archer art, `flag_red.png` as downloaded, and `project.godot`.
- Imported rigs, `Bone2D`, `AnimatedSprite2D`, `AnimationTree`, method tracks, and any clip keying something the game reads.

# Unconfirmed

1. **Names and enums** for 4.7.2 (see "Godot 4 names"), and what `track_problems()` is: likely a test helper still to be written.
2. **Key input in the structure test:** the brief names `Input.parse_input_event` (`CHANGE-BRIEF.md` §8); every existing test uses `root.push_input()`. Not checked that both reach `main._unhandled_input` the same way headless.
3. **`MANUAL` mode:** whether `play("shoot")` already applies the frame-0 pose before the first `advance()`, and how far the clip sits ahead of the cue clock on the first frame (brief answer 5 says at most 1/60 s). Not measured.
4. **GoalFlag draw order and place:** `main.tscn` children are drawn before the layers `_ready()` adds, unless `z_index` says otherwise; its `z_index` and exact position (≈ x 1176) are not fixed in the files.
5. **Rig scale and placement:** the `_sprite` scale comes from the idle image height (`piece.gd:193-202`); how `Mount` matches it (and `BASE_FROM_BOTTOM`) for the 288 × 321 draw art is not stated.
6. **Freeing on R:** `_build_pieces()` calls `queue_free()` then `remove_child()` (`main.gd:337-339`); whether the old `AnimationPlayer` can still be read for one frame in the edge test is not measured.
7. **`_arrows` window:** leaves 0–2 frames before frame 33 (`README.md:81`, A6 brief revision 1); the pins test will measure it again.
8. The agent ran no Godot command in this step; nothing above was probed at run time.
