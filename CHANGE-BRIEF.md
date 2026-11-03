# CHANGE-BRIEF — Assignment 5: shaders, materials and the Godot shading language

*Version 1, 2026-10-31, committed before either shader exists and before the first agent prompt. Results and corrections go in dated revisions at the bottom; this version is not edited after the fact. The Assignment 2 and 3 briefs are kept at tag `a3` (`git show a3:CHANGE-BRIEF.md`).*

**Who wrote what:** Jiean chose the state, the object, the textures and every design value below. Claude Code drafted the wording, filled in the project facts (file and line references) and proposed the defaults Jiean accepted. **The colour line, every predicted value and the answers marked "Jiean" are Jiean's own.**

## 1. The state

| | |
|---|---|
| Name | **exposed** |
| What it communicates | While you plan your move, your archer turns red when the square you are about to step to lies inside the enemy archer's reach (the 24 squares of the 5 × 5 around it). |
| Why the player needs it | Who shoots first alternates every turn, so stepping into reach is a real decision. The A2 playtest found that a new player could not tell why the enemy stops and shoots (README, known limitations). The tint shows the danger before you commit, and matches the GDD's red danger zones. |
| Where it is held | `godot/game/main.gd`: `state` (`main.gd:76`, value `State.PLAN_MOVE`) and `planned_offset` (`main.gd:86`); the units' cells in `rules.units` (`godot/game/rules.gd:29`). |
| Exact condition | `state == State.PLAN_MOVE` **and** the enemy archer is alive **and** `Rules.in_range(player_cell + planned_offset, enemy_cell)` (`rules.gd:121`). |
| Begins | on the first frame the condition is true: when PLAN_MOVE begins with the standing square already in reach, or when an arrow key moves the planning marker into reach. |
| Ends | on the first frame it is false: the marker moves out of reach, the move is confirmed (Enter or Space → `PLAY_MOVES`), R (retry), or the game ends. |

The driver only **reads** these values. It never writes game state.

## 2. Effect specification

### The shader

- Path: `godot/shaders/exposed_tint.gdshader`
- `shader_type canvas_item;` — no `render_mode` (default blending).
- No sampler uniforms of its own. The archer's sprite texture arrives in `COLOR` (texture × modulate).
- On a `ShaderMaterial` on the player archer's `Sprite2D` (`godot/game/piece.gd:35`, created in `setup()` at `piece.gd:51-54`).

| Uniform | Type | Hint | Default | Set by |
|---|---|---|---|---|
| `exposed_amount` | `float` | `hint_range(0.0, 1.0)` | `0.0` | the driver, every frame, from the state |
| `exposed_color` | `vec4` | `source_color` | `vec4(0.878, 0.271, 0.227, 1.0)` (`#E0453A`, the game's target red, `main.gd:47`) | the material; not changed by game code |

### The colour line (inside `fragment()`)

```glsl
COLOR.rgb = mix(COLOR.rgb, exposed_color.rgb, exposed_amount * 0.7);
```

(Jiean)

### Observable rules

| # | Rule |
|---|---|
| R1 | `exposed_amount` is `0.0` when the state is false and has settled; `1.0` when the state is true and has settled. |
| R2 | When the state begins, the value rises linearly from where it is to `1.0` at **5.0 per second of game time** (0 → 1 in **0.20 s**). When the state ends, it falls linearly to `0.0` at the same rate (1 → 0 in 0.20 s). Tolerance: **one frame period** (1/30 s, 1/60 s, 1/144 s). The same game time at 30, 60 and 144 fps. |
| R3 | **Retrigger:** if the state begins again while the value is still falling, the value turns around and rises **from its current value**: no restart from 0, no jump. If it ends while still rising, it turns around and falls from its current value. (Neither "restart" nor "ignore".) |
| R4 | **Time:** game time = `delta × main.time_scale` (the clock the pieces already use, `main.gd:162-171`), so it is **scaled** time: `Engine.time_scale = 0.5` doubles the real-time duration. While the game is paused (P/Esc, `main.paused`, `main.gd:297`) the value **holds still**. The game never uses `get_tree().paused` (`main.gd:6`); if the tree were paused, the driver would stop too and the value would hold. |
| R5 | **State ends mid-transition:** from value `v`, it reaches `0.0` after `v × 0.20 s`. |
| R6 | **Several instances:** every piece's `Sprite2D` gets its **own** `ShaderMaterial` instance, never a shared one. Only the player archer's value is driven; the enemy archer's stays `0.0`. After R (retry) or play again, the pieces are rebuilt (`main.gd:329`), and the new sprites get new materials. |
| R7 | `TIME` is not used. |

### Boundaries

Unchanged: collision, movement, input (no new key in the game), the state machine and every timing in `main.gd`, the rules engine, existing tests and their expectations, the other piece, the board, HUD and sounds, and every A2/A3 asset file. Presentation code may read game state; it never writes it.

### Evidence split

| Rule | Checked by | How |
|---|---|---|
| Shader parses; uniform names and types | headless | `get_shader_uniform_list()`; defaults read from the shader source text |
| R1, R2, R5 | headless | uniform sampled every frame from a high `process_priority` node, through real key presses, at 30, 60 and 144 fps: first value, last value, game-time duration |
| R3 | headless | arrow keys tapped back and forth faster than 0.20 s: no frame drops to 0 while the state holds |
| R4 | headless | pause pressed mid-fade: value constant; `Engine.time_scale` 0.5: duration doubles in real time, same in game time |
| R6 | headless | the two sprites' materials are different objects; the enemy's value stays 0; after R the new sprite has a material |
| The colour on screen | **eyes** | in-engine captures at the controlled values (section 3), compared with the predictions |
| It reads as "danger" in play | **eyes** | my own playtest: the state triggered by normal play several times |

## 3. Controlled inputs and predicted values

- Uniform values: **0.0, 0.5, 1.0**, plus **2.0** set from code for the `hint_range` question.
- Lighting: none; `canvas_item` output is unlit. HDR 2D is off (`project.godot` has no `rendering/viewport/hdr_2d`), so blending happens on the stored sRGB values.
- Pixels: in flat-colour regions of `archer_idle.png` (measured by Claude headlessly, 2026-10-31). The sprite is drawn at 0.248 scale, so each screen pixel averages a few texels. The 0.0 capture checks these starting values first.

| Pixel | Where (texel → about screen, player at the start square, turn 1) | Value at 0.0 (sprite) | at 0.5 | at 1.0 |
|---|---|---|---|---|
| P1 head (birch) | (84, 84) → (192, 581) | (224, 174, 117) | (224, 137, 96) | (224, 101, 76) |
| P2 base disc (walnut) | (124, 296) → (202, 634) | (90, 58, 34) | (137, 62, 42) | (184, 66, 51) |

Contrast of P1 against the light board square `#D8C7A0` at 0.0 and at 1.0: 0.474 and 0.257 (Jiean).
Contrast Ratio rises from 1.20:1 to around 2.05:1, so the tint make the head more against the square.

### Hint experiment

A 3 × 1 PNG with greys 64, 128, 192, on two unshaded quads, Linear tonemap, exposure 1.0. Predicted displayed 8-bit values (Jiean, by hand, with `encode(x)`):

| Band (file value) | Quad A: `source_color` | Quad B: no hint |
|---|---|---|
| 64 | 64 | 137 |
| 128 | 128 | 188 |
| 192 | 192 | 225 |

Which quad shows the file's values unchanged, and why: Quad A. GPU decodes sRGB to linear and then back to sRGB while to the screen, so the computation
canceled as they are exact contrast.(Jiean).

**Renderer:** this project uses **Compatibility** (`godot/project.godot:24`). The assignment's predictions assume Forward+ or Mobile, so these values are measured before any explanation is written.

## 4. Material plan

**Object:** two new flat tiles in the A3 diorama (`godot/diorama/asset_diorama.tscn`), `LinenSquareLight` and `LinenSquareDark`, each a `MeshInstance3D` with a 1 m × 1 m `PlaneMesh` (one board square), lying just above the floor, in view of the existing camera.

**Why not the A3 `board_square.glb`:** it has no UV coordinates (checked headlessly on 2026-10-31: both surfaces have no `ARRAY_TEX_UV`), so a texture cannot be placed on it. The source model must not change. Putting a material behind the importer would also change what `check_assets.gd` measures (`check_assets.gd:132-152`), and an importer material is shared by every instance, so it cannot give two looks.

**Lighting to judge under:** the diorama's own lamp (one `DirectionalLight3D`, shadows on) and its ambient light (`asset_diorama.tscn:15-33`), with the camera unchanged. Compatibility has no SSAO or SSR, so nothing has to be switched off. The diorama keeps exactly one light (`check_assets.gd:187`).

### Textures (Poly Haven **Hessian 380**, CC0; credits in `godot/assets/textures/hessian_380/ATTRIBUTION.md`)

| File | Role | What the numbers mean | Sampled as | `compress/mode` | `compress/normal_map` | `mipmaps/generate` |
|---|---|---|---|---|---|---|
| `hessian_380_diff_1k.jpg` | colour | sRGB colour | colour (`source_color`) | 0 Lossless | 2 Disable | true |
| `hessian_380_rough_1k.png` | data | roughness 0 glossy … 1 rough, linear | data (no `source_color`) | 0 Lossless | 2 Disable | true |
| `hessian_380_nor_gl_1k.png` | data | tangent-space normal, OpenGL green-up; 0.5 = no tilt | data (`hint_normal`) | 0 Lossless | 1 Enable | true |
| `hessian_380_nor_dx_1k.png` | calibration only, never bound | as above, DirectX green-down | — | 0 Lossless | 1 Enable | false |
| `hint_greys.png` (3 × 1, written by a committed script) | hint experiment | greys 64, 128, 192 | both | 0 Lossless | 2 Disable | false |

**Normal map convention:** `_nor_gl`, because Godot expects OpenGL.

**Authors and roles, licence and date checked** (used as-is by the audit): Hessian 380, https://polyhaven.com/a/hessian_380; colormass (photography), Rico Cilliers (processing); CC0 (https://polyhaven.com/license); checked 2026-10-31.

### Shader and uniforms

- Shader: `godot/shaders/linen_square.gdshader`, `shader_type spatial;`, default (lit) render mode.
- Hint-experiment shader: `godot/shaders/hint_experiment.gdshader`, `render_mode unshaded`.

| Uniform | Type | Hint | Range | Default | Group | What should change on screen across the range |
|---|---|---|---|---|---|---|
| `albedo_tex` | `sampler2D` | `source_color, filter_linear_mipmap, repeat_enable` | — | diff | surface | — |
| `tint` | `vec4` | `source_color` | colour | white | surface | white = the cloth as photographed; darker = darker cloth |
| `uv_scale` | `float` | `hint_range(0.5, 8.0, 0.05)` | 0.5–8 | 3.65 (1 m ÷ 0.274 m) | surface | weave size: small values give huge threads, large values a fine weave |
| `roughness_tex` | `sampler2D` | `filter_linear_mipmap, repeat_enable` | — | rough | relief | — |
| `roughness_scale` | `float` | `hint_range(0.0, 1.0)` | 0–1 | 1.0 | relief | 0: glossy, a sharp lamp highlight; 1: matte cloth |
| `normal_tex` | `sampler2D` | `hint_normal, filter_linear_mipmap, repeat_enable` | — | nor_gl | relief | — |
| `normal_strength` | `float` | `hint_range(0.0, 2.0)` | 0–2 | 1.0 | relief | 0: flat (threads only painted); 2: deep threads with strong light and shade |

Groups use `group_uniforms surface;` and `group_uniforms relief;`.

### The two materials

| Material | `tint` | `normal_strength` | Everything else |
|---|---|---|---|
| `godot/materials/linen_light.tres` | white `#FFFFFF` | 1.0 | defaults |
| `godot/materials/linen_dark.tres` | stitch brown `#9A7F55` (the A3 board border, CHANGE-BRIEF A3-R1 at tag `a3`) | 1.5 | defaults |

**Why:** the 2D board alternates light and dark squares (`main.gd:41-42`). Two materials from one shader give the 3D board the same checkerboard. The dark square has deeper threads, so that it reads as worn cloth and not only as a darker colour.

## 5. Predicted failure cases

1. **The tint restarts from 0 on a retrigger** (flicker). *Check:* the driver test taps the arrow keys faster than 0.20 s and asserts that the value never drops while the state holds (R3).
2. **The enemy is tinted too, because the material is shared.** *Check:* the test asserts that the two sprites' materials are different objects and that the enemy's value stays 0.0 (R6).
3. **The duration depends on the frame rate** (counting frames instead of time). *Check:* the same test at 30, 60 and 144 fps; game-time duration 0.20 s within one frame period (R2).
4. **The tint keeps fading while paused, or ignores time scale.** *Check:* pause mid-fade, then `Engine.time_scale` 0.5 (R4).
5. **After R (retry) the new sprite has no material.** *Check:* press R, then assert the material and the value (R6).
6. **A data texture sampled with `source_color`, or the colour texture without it.** *Check:* the material test reads each sampler's hints from the shader source; mutation: removing `source_color` must fail it.
7. **The DirectX normal map bound instead of the OpenGL one.** *Check:* the material test asserts the bound texture path; the curl ratio (about 0 for `_nor_gl`, about 2 for `_nor_dx` under the GL convention).
8. **A renamed uniform silently stops the effect** (`set_shader_parameter` with an unknown name raises no error). *Check:* the uniform-list assertion; mutation: rename it in the shader only.

## 6. Answers (Jiean)

1. Which renderer does project.godot name, and what does it rule out? It names the Compatibility renderer (gl_compatibility, project.godot:24), which is the OpenGL 3.3 / WebGL 2 path. So we can't use decals or compute shaders — those need Forward+ or Mobile — and we can't use VoxelGI, SDFGI or SSIL, which are Forward+ only. I'm keeping Compatibility because the final project might go on the web, and web export needs it. Neither of the two A5 shaders needs anything from the excluded list, so it costs us nothing.

2. What colour arrives in your fragment function before you change it, and what would the tempting alternative give you? By the time fragment() runs, COLOR is already the sprite's texture colour at that pixel, with the node's modulate / self_modulate (and any vertex colour) multiplied in. On the player archer modulate is white, so it's just the texture. On an enemy using the red fallback tint (piece.gd:182), the tint would already be in there. The tempting alternative is to sample the texture myself instead — that's question 3.

3. For canvas_item: what would texture(TEXTURE, UV) give you instead of COLOR? Just the raw texel from the sprite image, with no modulate on top. So it would quietly lose any tint or fade the game applies through modulate, and it would read the texture a second time for no reason.

4. For spatial: what does ALBEDO hold if you never write it, and what does COLOR hold? If I never touch ALBEDO, it stays white (vec3(1.0)), so the surface comes out white under the light. COLOR in fragment() is what came down from vertex() — the mesh's vertex colour, which is white when the mesh has none (a PlaneMesh doesn't). It is not the texture. I should double-check both against the "Spatial shaders" docs page before I lean on it.

5. How long would a frame-counting version of your effect last at 30, 60 and 144 fps? Suppose someone wrote "add 1/12 per frame", tuned for 0.20 s at 60 fps (12 frames). Then the fade always takes 12 frames, so it lasts 12 ÷ fps seconds: 30 fps → 0.40 s, 60 fps → 0.20 s, 144 fps → about 0.083 s. That is why R2 measures in game time (delta), not frames.

6. Which resource holds your uniform's default, which holds its current value, and what happens if two objects share the material? The default lives in the shader itself — the = 0.0 on the uniform line in the .gdshader. The current value lives in the ShaderMaterial: set_shader_parameter writes it there, and the material file saves whatever differs from the default. If two sprites share one material, setting the value hits both at once, so one archer's danger tint would show up on the other. That's failure case 2, and it's exactly why R6 gives every sprite its own material.

7. Does hint_range clamp a value your driver sets from code? (prediction) My prediction: it does not clamp. hint_range is only a hint for drawing the Inspector slider; set_shader_parameter("exposed_amount", 2.0) from a script goes through the material, not the Inspector. If it really is not clamped, your line at t = 2.0 uses the factor 0.7 × 2 = 1.4, and mix goes past the red: for P1, G = 174 + (69 − 174) × 1.4 = 174 − 147 = 27, B = 117 + (58 − 117) × 1.4 = 117 − 82.6 = 34.4 → 34, giving (224, 27, 34), a deeper and more saturated red than the target. This is a prediction; the test that sets 2.0 will confirm it.

## Revisions

**Revision 1, 2026-11-02 (wording only).** Section 6: Jiean rewrote answers 1–4 and 6 in Jiean's own words after version 1 was committed (`5a32988`), replacing wording that came from Claude's hint drafts; the content of each answer is unchanged. Answer 5's set-up ("add 1/12 per frame", 12 ÷ fps) comes from Claude's hint; the three durations are Jiean's. Answer 7 is Jiean's own. Nothing else in the brief changed.
