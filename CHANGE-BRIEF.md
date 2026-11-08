# CHANGE-BRIEF — Assignment 6: particle effects

*Version 1, 2026-11-08. Committed before any effect exists and before the first agent prompt. Results and corrections go in dated revisions at the bottom; this version is not edited afterwards. The Assignment 5 brief is kept at tag `a5` (`git show a5:CHANGE-BRIEF.md`).*

**Who wrote what:** Jiean chose both effects, their jobs and the retrigger rule. Claude Code drafted the wording, filled in the project facts (file and line references), measured the engine facts marked "measured", and proposed the setting values. Jiean reviewed and accepted the values. **Every prediction, the price budget and the six answers are Jiean's own.**

**Engine:** Godot **4.7.2** standard (`README.md`), Compatibility renderer (`godot/project.godot:25`). The game is 2D: 1280 × 720 viewport, no camera (`main.gd:18`). Every class and property name below is a Godot 4.7.2 name. They were listed from `ClassDB` in a throwaway probe on 2026-11-08.

## 0. Engine facts measured before writing (throwaway probes, 2026-11-08, outside the repository)

| Fact | How it was measured |
|---|---|
| `CPUParticles2D` has **no** `amount_ratio`; `GPUParticles2D` has it, along with `use_fixed_seed` and `seed` | `ClassDB.class_get_property_list` |
| **The Compatibility renderer does not support particle trails.** A `GPUParticles2D` with `trail_enabled = true` drew **nothing**, and Godot printed `WARNING: The Compatibility renderer does not support particle trails.` | windowed Movie Maker render, 30 frames |
| `GPUParticles2D` draws on Compatibility (a moving world-space emitter left a dotted line, one dot per frame at 30 fps) | same render |
| The viewport reports GPU time on Compatibility: 0.094 ms with 20 000 particles, 0.018 ms after hiding them (NVIDIA GeForce RTX 3070 Ti Laptop GPU, OpenGL 3.3) | `RenderingServer.viewport_get_measured_render_time_gpu` |
| Defaults: `CPUParticles2D` and `GPUParticles2D` both start with `emitting = true`; `GPUParticles2D.fixed_fps` = 30, `interpolate` = true, `visibility_rect` = (−100, −100, 200, 200) | `ClassDB` probe |
| `ParticlesMaterial` (Godot 3) does not exist. `ParticleProcessMaterial` still has editor-only properties named `initial_velocity` and `scale` (Vector2, usage EDITOR + INTERNAL, not stored). `CPUParticles2D` has neither | `ClassDB` probe |

## 1. Effect A — hit burst

### The job

| | |
|---|---|
| What it tells the player | **An arrow hit an archer, and which one.** Today a hit shows the hurt pose, a red "−3" and fewer HP pips (`main.gd:505-511`). Two hits in one turn come 1.05 s apart, and a new player can miss which archer took which. The burst marks the moment and the place of each hit. |
| Event, script and variable | A `"damaged"` event played by `main._cue_impact()` (`godot/game/main.gd:498-513`, match arm `:505`). Each played event is appended to `main.played_events` (`main.gd:502`). The hit archer is `main.pieces[ev["unit"]]` (`main.gd:503`). A killing hit is also a `"damaged"` event (hp_after 0), followed by `"killed"` (`:512-513`). |
| Where | The hit archer's body: its node position (centre of the base disc, `piece.gd:4`) + (0, −40). The archer is 80 px tall on screen (`piece.gd:9`). |
| How often | Each archer has 4 HP and an arrow deals 3 (`rules.gd:12-13`), so a hit goes 4 → 1 and the next one kills. In a turn where both archers shoot, the two impacts land **1.05 s apart**: 0.2 + 0.35 + 0.25 + 0.25 s (`main.gd:29-33`, `:474`). |

### The intent block

- **Timing phases:**
  1. **Impact** (0 – 0.1 s): a red flash over the archer's torso, strongest on the first frame and gone by about frame +4 at 30 fps.
  2. **Outward** (0 – 0.45 s): wood splinters spray up and out, reach about one archer height, then fall under gravity.
  3. **Dissipation** (0.1 – 1.2 s): a brown dust puff swells and thins, and is gone by 1.2 s. That is just after the return shot of the same turn lands (1.05 s), so in a two-hit turn the first puff and the second flash overlap briefly.
- **Contrast against the named background:**
  - **Lightest:** the board's light square `#D8C7A0` (`main.gd:41`) under the linen overlay.
  - **Darkest:** the dark wood table `env_table.png` (`main.gd:619`) just outside the board edge. The player's start square (column 0, lane 5) touches the table on two sides.
  - **Value, not hue:** splinters and dust are darker than the board (dark wood `#3A2616`, dust `#7A5A3A`). The flash is the game's target red `#E0453A` (`main.gd:47`), a mid value that also reads on the dark table.
  - **No additive blend:** adding light to a pale board pushes it towards white and loses the contrast.
- **Scale against the character** (archer 80 px tall at 1280 × 720):
  - the flash is about 40 px across (half an archer) and grows to about 64 px;
  - splinters land within about 80 px of the hit point;
  - the dust grows to about 60 px;
  - the whole burst stays inside about one board square (128 × 96, `main.gd:19`).
- **Change over life:**
  - flash: scale 1.0 → 1.6 while alpha 0.9 → 0;
  - splinters: colour red → dark wood in the first fifth, alpha fades in the last third, scale 1.0 → 0.6;
  - dust: scale 0.6 → 1.6 while alpha 0.55 → 0.
- **Variation:** splinter speed 140–260 px/s, direction ±75° around straight up, random angle and spin, scale 0.8–1.2; dust angle, spin and scale random. No hue variation: the colours stay on the game's palette. No fixed seed in the effect scene, so repeated hits differ.
- **Emitters** (three under one root):
  - `Flash` (1 particle): the moment of the hit;
  - `Splinters` (14): the force and direction of the hit;
  - `Dust` (8): the after-image that fades.

### The settings

**Node type:** `CPUParticles2D` for all three emitters.
- **Why CPU:** a burst of 23 particles needs no GPU-only feature. Its settings live on the node, so the configuration test reads them directly. And its process step runs on the CPU, so its headless price is a real number that can be compared with a budget. That gives a contrast with Effect B (section 2), whose headless price is near zero.
- **Missing on this node** (answer 1): `amount_ratio`, turbulence, attractors, collision, sub-emitters and trails.

**Scene:** `godot/effects/hit_burst.tscn`, root `Node2D` named `HitBurst`, children `Flash`, `Splinters`, `Dust`.

| Setting | `Flash` | `Splinters` | `Dust` |
|---|---|---|---|
| `emitting` saved in the scene | `false` | `false` | `false` |
| `amount` | 1 | 14 | 8 |
| `lifetime` (s) | 0.12 | 0.45 | 1.2 |
| `one_shot` | `true` | `true` | `true` |
| `explosiveness` | 1.0 | 1.0 | 0.9 |
| `lifetime_randomness` | 0.0 | 0.3 | 0.3 |
| `local_coords` | `false` | `false` | `false` |
| `emission_shape` | point (0) | point (0) | sphere (1), `emission_sphere_radius` 10 |
| `direction` | (0, −1) | (0, −1) | (0, −1) |
| `spread` (°) | 0 | 75 | 180 |
| `gravity` (px/s²) | (0, 0) | (0, 900) | (0, −30) |
| `initial_velocity_min` / `_max` (px/s) | 0 / 0 | 140 / 260 | 10 / 35 |
| `angle_min` / `_max` (°) | 0 / 0 | 0 / 360 | 0 / 360 |
| `angular_velocity_min` / `_max` (°/s) | 0 / 0 | −720 / 720 | −30 / 30 |
| `damping_min` / `_max` | 0 / 0 | 0 / 0 | 0 / 0 |
| `scale_amount_min` / `_max` | 1.25 / 1.25 | 0.8 / 1.2 | 1.0 / 1.4 |
| `scale_amount_curve` | 1.0 → 1.6 | 1.0 → 0.6 | 0.6 → 1.6 |
| `color_ramp` | `#E0453A` α 0.9 → `#E0453A` α 0 | 0.0 `#E0453A` α 1; 0.2 `#3A2616` α 1; 0.7 `#3A2616` α 1; 1.0 `#3A2616` α 0 | 0.0 `#7A5A3A` α 0.55; 1.0 `#7A5A3A` α 0 |
| `particle_flag_align_y` | `false` | `true` (each splinter points along its velocity) | `false` |
| `texture` | soft dot: `GradientTexture2D` 32 × 32, radial, white → transparent | sliver: `GradientTexture2D` 4 × 16, white, transparent at both ends | soft dot (as `Flash`) |
| `material` | `CanvasItemMaterial`, `blend_mode` Mix (0) | same | same |

- **Root:** `z_index` 2, above the pieces (`main.gd:122`, z 1) and below the HUD (`main.gd:125`, z 3).
- **`local_coords` off, and why:** the particles stay where the hit happened even if the root were moved. The root sits on an effects layer that never moves, so this matters only if someone parents the burst to the archer.
- **Not applicable:** `visibility_rect` (CPU node) and `preprocess` (the burst must never be running when a scene loads).
- **Peak count:** 23 particles per burst, and at most 2 bursts alive at once (rule A3), so **46**.

### Observable rules

| # | Rule |
|---|---|
| A1 | One burst per `"damaged"` event, on the frame `_cue_impact` plays it, at the hit archer's position + (0, −40). This includes the killing hit. |
| A2 | Never otherwise: not when a scene loads, not on `"attack_cancelled"` ("no target", `main.gd:522-527`), not on an arrow that hits nobody, not on R. |
| A3 | **Retrigger: overlap.** Each event creates a new `HitBurst` instance; earlier bursts keep playing. The most bursts alive at once in this slice is **2** (two hits in one turn, 1.05 s apart, burst life 1.2 s). |
| A4 | **Freed parent:** a burst is not a child of the archer, so it doesn't die with it. A killing hit doesn't free the archer anyway: it plays its defeat pose (`main.gd:512-513`). Archers are freed only on R or play again (`main.gd:336-340`), and R also clears every live burst, as it clears arrows (`main.gd:319`). |
| A5 | **Game time:** a burst runs on the game clock. Its `speed_scale` follows `main.time_scale` (`main.gd:73`), and it is 0 while the game is paused with P/Esc (`main.paused`, `main.gd:77`, `:297-299`), so the burst freezes with the pieces. If the tree were paused, its processing stops and it holds still (the game never pauses the tree, `main.gd:6`). |
| A6 | Each burst instance frees itself once its longest emitter has finished (`Dust`, 1.2 s of game time). |

## 2. Effect B — arrow trail

### The job

| | |
|---|---|
| Which job | **A trail.** |
| What it tells the player | **Who shot whom, and along which path.** The arrow is a small 30 px shape in flight for only 0.35 s (`main.gd:30`, `:716-727`). The trail stays on screen for a moment after it lands, so the shot can be followed back to the archer who fired it. That answers the A2 playtest problem ("could not tell why the enemy stops and shoots") and leads straight into Effect A at the impact. |
| Condition, script and variable | **An arrow is in flight:** `main._arrows` is not empty (`godot/game/main.gd:102`). An entry is added by `_cue_arrow()` (`main.gd:490-495`), and removed in `_tick_fx()` when its `t` reaches `ARROW_TIME` (`main.gd:203-205`), within one frame of the impact cue (`main.gd:472`). The arrow tip's position each frame is `from.lerp(to, s) + (0, −ARROW_ARC · 4 · s · (1 − s))` with `s = t / ARROW_TIME` (`main.gd:718-721`). |
| Feature Effect A doesn't use | **Turbulence** (`ParticleProcessMaterial.turbulence_enabled`), a GPU-only feature: `CPUParticles2D` has no turbulence. Also **damping**, which Effect A leaves at 0. **Not used: Godot's own `trail_enabled`,** because Compatibility doesn't draw particle trails (section 0). The trail is made by world-space emission from a moving emitter. |

### The intent block

- **Timing phases:**
  1. **Launch** (first frame of the arrow): the streak starts at the bow.
  2. **Flight** (0 – 0.35 s): a dark streak follows the arrow tip and draws its arc on the board. The streak is never longer than about 1.5 squares, because each streak particle lives 0.3 s.
  3. **Landing and after** (0.35 – 1.05 s): emission stops at the impact. The streak shrinks away within 0.3 s, and a few dust wisps drift and curl (turbulence) for up to 0.7 s, then nothing is left. That is before the next arrow of the turn is fired.
- **Contrast against the named background:**
  - Arrows fly over the board: the light square `#D8C7A0` is the lightest, the dark square `#CDB98E` (`main.gd:42`) the darkest. Arrows don't fly over the table.
  - The streak is a warm grey-brown `#6E5A44`: darker than both squares, but lighter than the arrow's walnut shaft `#5A3A22` and ink head `#1B1410` (`main.gd:725-726`), so the arrow itself still reads at the front of its trail.
  - The wisps are a paler `#9A8466` at low alpha, a mid value between the streak and the board.
- **Scale against the character:**
  - streak particles about 10 px, shrinking to 2 px;
  - wisps 16–26 px, growing to about 35 px;
  - the whole trail spans at most the shot's length, up to 2 squares (≈ 256 px, `Rules.in_range`, `rules.gd:121`), plus the arc (40 px, `main.gd:31`).
- **Change over life:**
  - streak: scale 1.0 → 0.2, alpha 0.8 → 0, so the tail tapers;
  - wisps: scale 0.6 → 1.4, alpha 0.45 → 0, so they spread out and fade.
- **Variation:** streak particles get a small random velocity (0–8 px/s), so the line isn't ruler-straight. Each wisp has its own direction (spread 180°), speed 10–25 px/s and turbulence influence 0.1–0.2.
- **Emitters** (two under one root that follows the arrow tip):
  - `Streak` (48): the arrow's path;
  - `Wisps` (12, turbulent): the dust stirred up behind it.

### The settings

**Node type:** `GPUParticles2D` for both emitters.
- **Why GPU:** turbulence exists only on the GPU node.
- **Missing on this node:** with this renderer, it lacks trails (`trail_enabled` draws nothing on Compatibility, measured) and collision with the 2D signed-distance field (not used).

**Scene:** `godot/effects/arrow_trail.tscn`, root `Node2D` named `ArrowTrail`, children `Streak` and `Wisps`.

| Setting | `Streak` | `Wisps` |
|---|---|---|
| `emitting` saved in the scene | `false` | `false` |
| `amount` | 48 | 12 |
| `lifetime` (s) | 0.30 | 0.70 |
| `one_shot` | `false` | `false` |
| `explosiveness` | 0.0 | 0.0 |
| `preprocess` (s) | 0.0 | 0.0 |
| `local_coords` | **`false`** | **`false`** |
| `fixed_fps` | 30 (default) | 30 (default) |
| `interpolate` | `true` (default) | `true` (default) |
| `trail_enabled` | `false` | `false` |
| `visibility_rect` | (−320, −200, 640, 400), **set and checked** | same |
| `texture` | soft dot (as in Effect A) | soft dot |
| `material` | `CanvasItemMaterial`, `blend_mode` Mix (0) | same |
| `process_material` | `ParticleProcessMaterial` | `ParticleProcessMaterial` (its own) |
| `particle_flag_disable_z` | `true` | `true` |
| `emission_shape` | point (0) | sphere (1), `emission_sphere_radius` 4 |
| `direction` | (0, −1, 0) | (0, −1, 0) |
| `spread` (°) | 180 | 180 |
| `gravity` | (0, 0, 0) | (0, −20, 0) |
| `initial_velocity_min` / `_max` (px/s) | 0 / 8 | 10 / 25 |
| `damping_min` / `_max` | 10 / 10 | 15 / 20 |
| `scale_min` / `_max` | 0.30 / 0.35 | 0.5 / 0.8 |
| `scale_curve` | 1.0 → 0.2 | 0.6 → 1.4 |
| `color_ramp` | `#6E5A44` α 0.8 → α 0 | `#9A8466` α 0.45 → α 0 |
| `turbulence_enabled` | `false` | **`true`** |
| `turbulence_influence_min` / `_max` | — | 0.1 / 0.2 |
| `turbulence_noise_strength`, `_noise_scale` | — | defaults (1.0, 9.0) |

- **`local_coords` off, and why:** emitted particles must stay where the arrow was. With it on, the whole trail would move with the arrow tip and show as a blob at the arrow, not a line behind it.
- **`visibility_rect`:** in the emitter's own coordinates. The trail lies behind the moving tip, up to one shot length (≈ 260 px with the arc) plus the wisps' drift, so the rectangle covers ±320 px by ±200 px. It is set, not generated (generation needs the editor and a running emitter).
- **`preprocess`:** 0. A trail must start empty at the bow, and no arrow exists when a scene loads.
- **Peak count:** 60 particles per trail. Arrows never fly at the same time in this slice (1.05 s apart, 0.35 s flight), but a fading trail can still be alive when the next arrow starts, so allow **2 trails, 120 particles**.

### Observable rules

| # | Rule |
|---|---|
| B1 | **Starts** on the frame an arrow appears in `main._arrows` (`_cue_arrow`, `main.gd:490-495`): a new `ArrowTrail` at the arrow's start point, emitting. |
| B2 | **Follows** the arrow tip every frame (the formula at `main.gd:718-721`). **Stops** emitting on the frame the arrow leaves `main._arrows` (`main.gd:205`). Its particles then die within 0.7 s of game time, and the node is freed. |
| B3 | **Never otherwise:** not when a scene loads, not on `"attack_cancelled"` (no arrow is drawn), not after R (R clears arrows, `main.gd:319`, and every trail with them). |
| B4 | **Paused:** with the game paused (P/Esc, `main.paused`), the trail's `speed_scale` is 0, so it freezes with the frozen arrow and resumes on unpause. With the tree paused, `GPUParticles2D` stops processing and holds still; the game never pauses the tree (`main.gd:6`), so the test does it. |
| B5 | **Hidden:** while `visible` is false, nothing is drawn. Hiding doesn't change `emitting`, and no code reacts to visibility. Whether the GPU keeps simulating while hidden is not observable headlessly; Jiean's prediction is in answer 5. |
| B6 | **Game time:** `speed_scale` follows `main.time_scale`, as Effect A does. |

## 3. Boundaries

Unchanged:
- collision, movement and input (one exception: the debug key **V**, which toggles vsync for the GPU price; the assignment requires it, and F9 is caught by the editor, found in A5);
- the state machine and every timing constant in `main.gd`;
- the rules engine (`godot/game/rules.gd`);
- every existing test and its expected counts (`test_rules` 51, `test_audio_events` 70, `check_assets` 38, `test_exposed_tint` 46 at 30/60/144, `test_materials` 148);
- the Assignment 5 shaders in `godot/shaders/` (hand-written, never edited by an agent);
- the board, the HUD, the archer sprites and their tint, the sounds and music, and every A2/A3/A5 asset file.

Effect settings live in the scene files in `godot/effects/`, not in code. The trigger code may **read** `main.played_events`, `main._arrows`, `main.pieces`, `main.time_scale`, `main.paused` and `main.state`. It never writes game state.

**Textures:** no sourced or generated image files. Both soft-dot and sliver textures are `GradientTexture2D` resources defined inside the scene files, so the code that makes them is committed, and `SOURCES.md` records this.

## 4. Evidence split

| Rule | Checked by | How |
|---|---|---|
| Every setting in sections 1 and 2, the turbulence feature, `trail_enabled` off, `emitting` saved as false | headless | `test_hit_burst_config.gd` and `test_arrow_trail_config.gd` load each scene and read every value back, with this brief's values as the expected values |
| A1, A2, A3 (two hits inside one lifetime), A4, A5, A6 | headless | `test_hit_burst_state.gd`: real key presses through `root.push_input()` at 60 fps play a turn where both archers hit. It counts live bursts per frame and checks each one's position against the hit archer. Zero bursts before the first hit and after R; pause holds `speed_scale` at 0 |
| B1–B4, B6 | headless | `test_arrow_trail_state.gd`: the same kind of turn. The trail exists while `main._arrows` is non-empty, follows the tip within 1 px, stops emitting when the arrow lands and is freed after 0.7 s. Pause, tree pause, and `visible` toggled with `emitting` unchanged |
| The look: flash, splinters, dust, streak, wisps; contrast; scale; timing phases | frame strip (fixture) + **eyes** | Movie Maker strips from the preview scenes (section 5); Jiean's verdict in the running game at 1280 × 720 |
| B5's look while hidden, the edge of the screen, scene load | **eyes** | Jiean in the running game |
| It reads as "hit" / "who shot whom" in play | **eyes** | Jiean's playtest, including two-hit turns |
| Price | headless + Visual Profiler | `cost_effects.gd` (with an empty-scene control); Visual Profiler GPU time on the RTX 3070 Ti Laptop GPU |

## 5. Frame strips

**Background (both previews):** the real board drawn by `main.tscn` after the game has started (PLAN_MOVE, turn 1), with both archers at their start squares: player at column 0, lane 5; enemy at column 7, lane 4 (`rules.gd:52-55`). In the preview scene only, the effect instance has `use_fixed_seed = true` and a stated `seed`. These are **fixture captures**.

**Effect A** (`godot/previews/hit_burst_preview.tscn`):
- **Trigger:** frame 10, on the player archer. The player's start square touches the table, so the strip shows the burst over both the lightest and the darkest background.
- **Retrigger export:** when on, a second burst on the enemy archer at frame **42** (1.05 s × 30 fps ≈ 31.5 frames after frame 10).
- **Frames to read (30 fps):** 10, 12, 15, 20, 30, 50; with the retrigger on, also 42, 44 and 47.

What each should show: 
Frame 10 (trigger, +0 s): the first burst opens with a small cluster of sparks at the hit square; splinters have not appeared yet.

Frame 12 (+0.07 s): the spark cluster spreads slightly; the first splinter particles begin to appear.

Frame 15 (+0.17 s): sparks and splinters are both visible; the sparks are starting to fade at the edges.

Frame 20 (+0.33 s): the splinter fan is widest here; the spark cluster is dimmer and thinner.

Frame 30 (+0.67 s): the second burst has started, so two clusters overlap; the first burst's splinters are near the end of their life.

Frame 50 (+1.33 s): both bursts are near full; the first burst's sparks are gone and only its splinters remain.

Retrigger, frames 42 / 44 / 47: what is left of burst 1, and the start of burst 2 on the enemy archer.

**Effect B** (`godot/previews/arrow_trail_preview.tscn`):
- **Trigger:** an arrow drawn the way `main.gd:716-727` draws it flies from the player archer to column 2, lane 4. That is a real two-square shot (`rules.gd:121`), using the arc formula of `main.gd:718-721`.
- **Condition:** starts at frame 10 (launch) and ends at frame **21** (landing: 0.35 s × 30 fps = 10.5 frames).
- **Frames to read:** 10 (start), 13, 16 (steady, mid-flight), 21 (landing, condition ends), 26, 31, 42 (after: +0.7 s, everything gone).

What each should show: A continuous line that can show the path of the arrow clearly. Earlier part of line gets faded earlier, and the hit effect will happen when the middle of the line disapper. 

**Capture command** (Jiean runs it; the folder name per revision is `r<N>`):

```bash
mkdir -p captures/hit_burst/r0
"$GODOT" --path godot res://previews/hit_burst_preview.tscn --write-movie "$PWD/captures/hit_burst/r0/frame.png" --fixed-fps 30 --quit-after 60
```

Godot 4.7.2 names frames `frame00000010.png` (8 digits, measured). Only the strip frames are committed.

## 6. Predicted failures

| # | Failure | Check that catches it |
|---|---|---|
| 1 | **Dropped retrigger:** one burst node re-fired with `emitting = true` while still emitting does nothing, so the second hit of a turn has no burst. | State test: two hits 1.05 s apart, two live bursts at once (A3). |
| 2 | **Godot 3 names** (`initial_velocity` for `initial_velocity_min`, `scale_amount` for `scale_amount_min`) load silently and leave defaults: splinters that don't fly. | Configuration test; mutation 1. |
| 3 | **Saved `emitting = true`** (the engine default, measured): a burst plays when a scene loads, and a trail appears without an arrow. | Configuration test reads `emitting` = false; state test counts zero before the first event. |
| 4 | **Trail with `local_coords` on:** the "trail" moves with the arrow and is never a line. | Configuration test; strip frames 13 and 16. |
| 5 | **`trail_enabled` on Compatibility:** the whole emitter draws nothing (measured). | Configuration test asserts `trail_enabled` = false; strip. |
| 6 | **Additive blend over the pale board:** the burst washes out to white. | Configuration test asserts Mix; strip frame 10 over the light square. |
| 7 | **Effects ignore the game's own pause:** particles keep moving while P holds the board still. | State tests: `speed_scale` 0 while `main.paused`. |
| 8 | **Dotted trail:** at 700–900 px/s and one emission per particle step at `fixed_fps` 30, the streak breaks into dots. | Strip frames 13 and 16; Jiean's eyes in play (the real game runs above 30 fps, the particles still step at 30). |
| 9 | **Null texture:** each particle draws as a grey square. | Configuration test asserts every `texture` is non-null. |

## 7. Price predictions and budget (Jiean)

| | Effect A (CPU) | Effect B (GPU) |
|---|---|---|
| Peak particle count | 46 | 120 |
| Predicted headless CPU price (ms per frame, above the control) | 0.015ms | 0ms |
| Predicted GPU time (ms per frame, effect on − off) | 0.001ms | 0.003ms |
| Budget, and the price it is compared on | 0.2ms (CPU node: both prices) | 0.2ms (GPU node: GPU time) |


## 8. Answers (Jiean)

1. Which node type does each effect use, and which features in your brief does it lack? Effect A use CPUParticles2D, and need nothing. Effect B is GPUParticles2D, which does have turbulence. However, there was a warning on Compatibility that a node draw nothing using trail, and that turns me to use moving world-space emitter instead: the emitter follows the arrow and leaves one dot per frame behind it.
2. With `local_coords` as you set it, what does Effect A do if its parent moves after the event? local_coords is off, meaning world space. The burst is one-shot, so by the time the parent moves, every particle has already been born and stays exactly where it was born.
3. Under the retrigger rule, each "damaged" event spawns a new HitBurst and the earlier one keeps playing. Only the two archers can land hits in this slice, and their hits are 1.05 s apart while a burst lives 1.2 s, so the second burst starts before the first has died. At most 2 bursts are alive at once, and at 23 particles per burst that is a peak of 46 particles. There is no melee in this slice, so nothing else can add a third burst.
4. A headless run reports ≈0 for the GPU effect: the dummy renderer draws nothing and never runs the particle shader, so what is left is the node's CPU-side bookkeeping, which is negligible. The headless number is CPU time, not GPU time. With vsync on, FPS reads the display refresh rate in both cases, effect off and effect on, because each frame finishes far inside 1/refresh and vsync waits for the next refresh regardless; a sub-millisecond effect does not move the readout.
5. First frame after load: there is no arrow yet, so there is no trail either way — nothing appears with or without preprocess. Preprocess matters mid-game: if the effect starts while an arrow already exists, preprocess makes the trail appear already "full" at the bow, as if it had been running; without it the trail starts empty and fills in as the arrow moves. Paused: pressing P in the game sets speed_scale to 0, so the emitter stops advancing and the trail holds its last state on screen; the test's tree pause does the same, with existing dots staying drawn and no new ones emitted. Hidden: rule B5 applies — the node stops drawing but keeps simulating by default, so unhiding shows the trail where it would have been; I did not freeze it on hide.
6. Emission — when and how many: amount, one_shot, explosiveness, lifetime, and the emission shape decide when particles are born and how many per event. Process — how each particle moves and changes: initial velocity, spread, gravity, damping, turbulence, and the scale and colour curves and ramps; I also file local_coords here, because it picks the coordinate space the simulation runs in rather than what the particles look like, though it could sit under emission as where particles are born relative to the parent. Draw — what it looks like: texture, material, blend mode, and z-index; I also file visibility_rect here under draw/culling, because it only affects whether the node is drawn, not how particles behave.

## Revisions

### Revision 1, 2026-11-08 (results; drafted by Claude from the measurements and Jiean's verdicts)

1. **Effect A `Flash`, tuned (TUNING.md r1–r3, Jiean's requests and verdicts, all kept):** `lifetime` 0.12 → 0.36 → **1.08 s**; `scale_amount_min` / `_max` 1.25 → **3.0**. The §1 intent "gone by about frame +4 at 30 fps" and "about 40 px across, grows to about 64 px" no longer hold: the flash is now about 100 px across at birth, grows to about 150 px and lasts about 1 s (strip r3). Every other §1 value is unchanged. The config test's expected values follow (`1079375`, `cc9e1ee`).
2. **Rule A6, measured:** a burst frees itself on `Dust.finished`. With `lifetime_randomness` 0.3 and `explosiveness` 0.9 that can be anywhere from 0.84 to 1.32 s of game time, not exactly 1.2 s. Measured: 1.22, 1.28 and 1.23 s (`test_hit_burst_state.gd`, 60 fps, `evidence/a6/tuning/`). Rule A3 (at most 2 bursts, and 2 at once in a two-hit turn) held in every run; a burst freed before 1.05 s would break the overlap, which has not been seen.
3. **Rule B2, corrected:** "stops emitting on the frame the arrow leaves `main._arrows`" holds, but that frame is **0 to 2 frames before** the impact cue at 60 fps, not "within one frame" of it (§2 table). Measured offsets for the five shots of the test run: 0, −2, 0, 0, −2 frames. The arrow's `t` (`main.gd:199-205`) and the impact cue (`:472`) are advanced in different places; why they differ by up to 2 frames was not investigated, because game timing is out of scope. The state test's bound follows: −2 to 0 frames.
