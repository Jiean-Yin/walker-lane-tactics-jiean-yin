# MATERIALS — A5 material audit

*Audit of the materials named in `CHANGE-BRIEF.md` (sections 3 and 4), 2026-11-02, by Claude Code, at commit `17f34c6`.
Read-only: no shader, material, scene or `.import` file was changed. Every table below is pinned by
`godot/tests/test_materials.gd` (`./scripts/run-test.sh test_materials.gd 60`, 148/148 at this commit).*

Renderer: Compatibility (`godot/project.godot:25-26`). `project.godot` sets no default environment, no HDR 2D and no
texture filter.

## 1. Materials

| Material | Shader | Uniform values it sets | Uniforms left at the shader default | Textures it binds |
|---|---|---|---|---|
| `res://materials/linen_light.tres` | `res://shaders/linen_square.gdshader` | `tint = Color(1, 1, 1, 1)` (`#FFFFFF`, `:13`); `normal_strength = 1.0` (`:16`) | `uv_scale` (3.65), `roughness_scale` (1.0) | `albedo_tex` ← `hessian_380_diff_1k.jpg` (`:12`); `roughness_tex` ← `hessian_380_rough_1k.png` (`:14`); `normal_tex` ← `hessian_380_nor_gl_1k.png` (`:15`) |
| `res://materials/linen_dark.tres` | `res://shaders/linen_square.gdshader` | `tint = Color(0.603922, 0.498039, 0.333333, 1)` (`#9A7F55`, `:13`); `normal_strength = 1.5` (`:16`) | `uv_scale` (3.65), `roughness_scale` (1.0) | the same three files as `linen_light` (`:12`, `:14`, `:15`) |
| `res://materials/hint_srgb.tres` | `res://shaders/hint_experiment.gdshader` | `use_srgb = true` (`:12`) | none | `grey_srgb` ← `hint_greys.png` (`:10`); `grey_raw` ← `hint_greys.png` (`:11`) |
| `res://materials/hint_raw.tres` | `res://shaders/hint_experiment.gdshader` | `use_srgb = false` (`:12`) | none | `grey_srgb` ← `hint_greys.png` (`:10`); `grey_raw` ← `hint_greys.png` (`:11`) |

Texture folders: `res://assets/textures/hessian_380/` and `res://assets/textures/hint_experiment/`.
All four materials have `render_priority = 0`. Both linen materials load the same `Shader` object; they are two
different `ShaderMaterial` objects. No material binds `hessian_380_nor_dx_1k.png`.

Where they are used:

| Scene | Node | Slot | Material |
|---|---|---|---|
| `res://diorama/asset_diorama.tscn` | `LinenSquareLight` (`MeshInstance3D`, 1 × 1 m `PlaneMesh`, at (−0.55, 0.002, 1)) | `surface_material_override/0` (`:57`) | `linen_light.tres` |
| `res://diorama/asset_diorama.tscn` | `LinenSquareDark` (same mesh sub-resource, at (0.55, 0.002, 1)) | `surface_material_override/0` (`:62`) | `linen_dark.tres` |
| `res://hint/hint_experiment.tscn` | `QuadA_source_color` (`QuadMesh` 1.5 × 0.5) | `surface_material_override/0` (`:32`) | `hint_srgb.tres` |
| `res://hint/hint_experiment.tscn` | `QuadB_no_hint` (same mesh sub-resource) | `surface_material_override/0` (`:37`) | `hint_raw.tres` |

## 2. Samplers

Import settings are from the `.import` file next to each texture, `[params]` section, lines 18, 24 and 26.

### `res://shaders/linen_square.gdshader` (`shader_type spatial;`, default lit render mode)

| Sampler | Hints as written (source line) | Bound by `linen_light` | Bound by `linen_dark` | `compress/mode` | `compress/normal_map` | `mipmaps/generate` |
|---|---|---|---|---|---|---|
| `albedo_tex` | `source_color, filter_linear_mipmap, repeat_enable` (`:4`) | `hessian_380_diff_1k.jpg` | `hessian_380_diff_1k.jpg` | 0 (Lossless) | 2 (Disable) | true |
| `roughness_tex` | `filter_linear_mipmap, repeat_enable` (`:9`) | `hessian_380_rough_1k.png` | `hessian_380_rough_1k.png` | 0 (Lossless) | 2 (Disable) | true |
| `normal_tex` | `hint_normal, filter_linear_mipmap, repeat_enable` (`:11`) | `hessian_380_nor_gl_1k.png` | `hessian_380_nor_gl_1k.png` | 0 (Lossless) | 1 (Enable) | true |

Other uniforms (from the source; types from `get_shader_uniform_list()`): `tint` `vec4` (type 20) `source_color`
`= vec4(1.0)` (`:5`); `uv_scale` `float` (3) `hint_range(0.5, 8.0, 0.05) = 3.65` (`:6`); `roughness_scale` `float`
`hint_range(0.0, 1.0) = 1.0` (`:10`); `normal_strength` `float` `hint_range(0.0, 2.0) = 1.0` (`:12`). Groups
`surface` (`:3`) and `relief` (`:8`), closed at `:14`. Samplers list as type 24 (Object).

### `res://shaders/hint_experiment.gdshader` (`shader_type spatial; render_mode unshaded;`)

| Sampler | Hints as written (source line) | Bound by `hint_srgb` | Bound by `hint_raw` | `compress/mode` | `compress/normal_map` | `mipmaps/generate` |
|---|---|---|---|---|---|---|
| `grey_srgb` | `source_color, filter_nearest` (`:4`) | `hint_greys.png` (read, `use_srgb` true) | `hint_greys.png` (bound, **not read**) | 0 (Lossless) | 2 (Disable) | false |
| `grey_raw` | `filter_nearest` (`:5`) | `hint_greys.png` (bound, **not read**) | `hint_greys.png` (read, `use_srgb` false) | 0 (Lossless) | 2 (Disable) | false |

Other uniform: `use_srgb` `bool` (type 1) `= true` (`:6`), which picks the sampler in `fragment()` (`:9-13`).

### Not bound anywhere

| File | `compress/mode` | `compress/normal_map` | `mipmaps/generate` | Used by |
|---|---|---|---|---|
| `hessian_380_nor_dx_1k.png` | 0 (Lossless) | 1 (Enable) | false | `godot/tests/normal_map_check.gd` calibration only (`godot/tools/calibrate_normal_map_check.gd`, `test_materials.gd`) |

All five import files match the table in `CHANGE-BRIEF.md` §4.

## 3. Lights and environment

### `res://diorama/asset_diorama.tscn` (the linen tiles)

| Setting | Value | Source |
|---|---|---|
| Lights | exactly one: `Lamp`, `DirectionalLight3D` | `:35-38` |
| Lamp direction | rotation (−0.8727, −0.6109, 0) rad (about −50°, −35°) | `:36` |
| Lamp colour | (1, 0.92, 0.8), warm | `:37` |
| Lamp energy | 1.0 (not set; default) | test reads `light_energy` |
| Lamp shadows | on | `:38` |
| Background | mode 1 (Color), (0.16, 0.15, 0.14) | `:21-22` |
| Ambient light | source 2 (Color), (1, 0.95, 0.88), energy 0.35 | `:23-25` |
| Reflected light | source 0 (Background), so reflections see the dark background colour (not set; default) | test reads `reflected_light_source` |
| Tonemap | **Linear (0), not set in the scene** (default); white 1.0 | test reads `tonemap_mode`, `tonemap_white` |
| Exposure | **1.0, not set in the scene** (default) | test reads `tonemap_exposure` |
| Glow, fog, adjustments | off (defaults) | test |
| Camera | (0, 1.1, 3), rotation x −0.2132, fov 50 | `:40-44` |

### `res://hint/hint_experiment.tscn` (the hint quads)

| Setting | Value | Source |
|---|---|---|
| Lights | none (both materials are `unshaded`) | test |
| Background | mode 1 (Color), black | `:10-11` |
| Tonemap | Linear (0), set explicitly | `:12` |
| Exposure | 1.0, set explicitly | `:13` |
| Glow, fog, adjustments | off, set explicitly | `:14-16` |
| Camera | orthographic (`projection = 1`), size 1.6, at (0, 0, 2) | `:23-27` |

## 4. Findings

Each finding is a report, not a fix. The two shaders are Jiean's hand-written files and were not touched.

1. **The hint experiment cannot tell "the hint does nothing" from "one texture, one decode state".** `CHANGE-BRIEF.md`
   §3 describes two quads, A sampling with `source_color` and B without. The build uses one shader with both
   samplers and a switch (`hint_experiment.gdshader:4-6`, `:9-13`), and both materials bind the **same**
   `Texture2D` to both samplers (`hint_srgb.tres:10-11`, `hint_raw.tres:10-11`). The measured result is that both
   quads show 64 / 128 / 192 (`evidence/a5/step3/hint_experiment_measurement.md:11-13`). Because one texture object
   feeds both samplers, this audit cannot rule out that the renderer keeps one sRGB state per texture, not per
   sampler. The run-time swap check in that file swaps the switch, not the texture, so it does not settle this either.
   *Evidence:* `hint_srgb.tres:4` and `hint_raw.tres:4`, one `ext_resource` (`uid://cs22oix1o5xsb`) for both
   samplers. *Possible control (Jiean's choice):* a material that binds the texture only to `grey_srgb`, or a
   second texture resource, measured in a windowed run.
2. **Each hint material binds a texture it never reads.** `hint_srgb` reads only `grey_srgb`, `hint_raw` reads only
   `grey_raw` (`hint_experiment.gdshader:9-13`), but each binds both (`hint_srgb.tres:10-11`, `hint_raw.tres:10-11`).
   This costs nothing (same 3 × 1 texture), but it is the reason finding 1 is open. The `use_srgb` uniform is not in
   the brief's §3 description.
3. **The curl ratios are about 0.68 / 1.32, not the "about 0 / about 2" that `CHANGE-BRIEF.md` §5 case 7 predicts.**
   *Evidence (this test's output, and `evidence/a5/step3/normal_map_calibration.log:2-3`):* `_nor_gl`
   `curl_ratio(directx=false) = 0.6813`, `(directx=true) = 1.3187`; `_nor_dx` 1.3167 / 0.6833. The bound map is
   still the lower one under the OpenGL convention, so the check gives the right answer, with a smaller margin than
   predicted.
   - The two numbers for one file always add up to 2 (0.6813 + 1.3187 = 2.0000): from `normal_map_check.gd:18-21`,
     flipping the sign `s` turns (t1 − t2)² into (t1 + t2)², and the two sum to 2(t1² + t2²). The ratio is 1 minus
     a correlation, so "about 0" needs an almost perfectly integrable map. The `_nor_dx` file is the same map with
     green flipped, so its numbers are the mirror of the `_nor_gl` numbers and add no independent evidence.
   - Unconfirmed contributor: the sources are 16-bit RGB (`hessian_380/ATTRIBUTION.md:22-23`), but
     `Image.load_from_file` decodes them as format 4 (`RGB8`) (test output, calibration log), so the finite differences
     run on 8-bit values. The fine weave and `stride = 4` (`normal_map_check.gd:9`) may also lower the correlation.
     Not tested.
4. **The never-bound DirectX normal map is imported and would ship.** `hessian_380_nor_dx_1k.png` (5,717,470 bytes,
   `ATTRIBUTION.md:23`) has a full `.import` (`hessian_380_nor_dx_1k.png.import:16-26`) and no material binds it.
   There is no `godot/export_presets.cfg` yet. An "export all resources" preset would include it. *Possible action
   later:* an exclude filter when the export preset is created.
5. **Lossless 1K textures are large on the GPU.** All three bound linen textures are `compress/mode=0` with mipmaps
   (`.import:18`, `:26`), and `detect_3d/compress_to=0` (`:40`), so Godot will not suggest VRAM compression.
   *Measured in review* (`get_image()` on the imported textures, `evidence/a5/step3/review_probe.log`): diff and
   nor_gl import as RGB8 with mipmaps, 4,194,303 bytes each; rough as L8 with mipmaps, 1,398,101 bytes; 9,786,707
   bytes for the three. This follows the brief (§4) and is fine for a two-tile diorama. It is a trade-off to revisit if the 3D board grows
   or goes to the web.
6. **Values equal to the defaults are stored anyway.** `linen_light.tres` stores `tint` white and
   `normal_strength = 1.0` (`:13`, `:16`), both equal to the shader defaults (`linen_square.gdshader:5`, `:12`).
   `hint_srgb.tres` stores `use_srgb = true` (`:12`), equal to `hint_experiment.gdshader:6`. This is harmless and
   matches the brief's §4 table explicitly. The opposite case: `uv_scale` and `roughness_scale` are **not** stored in
   either linen material, so a later change of those defaults in the shader changes both tiles at once.
7. **The diorama's tonemap and exposure are implicit.** `asset_diorama.tscn:20-25` sets no `tonemap_mode` or
   `tonemap_exposure`, so they are the defaults Linear and 1.0. The hint scene sets them explicitly
   (`hint_experiment.tscn:12-13`). With Linear, anything above 1.0 clips: the white `linen_light` under lamp energy
   1.0 plus ambient 0.35 may clip in the lit areas. Not checkable headlessly. `evidence/a5/step3/diorama_linen_tiles.png`
   is where to look.
8. **Reflections see only the dark background.** `reflected_light_source` is 0 (Background) and the background is
   (0.16, 0.15, 0.14) (`asset_diorama.tscn:21-22`). Lowering `roughness_scale` toward 0 will sharpen the lamp
   highlight, as the brief's §4 table says, but there is no environment for the cloth to reflect.
9. **Line reference drift in the brief.** `CHANGE-BRIEF.md` §3 and §6 cite `project.godot:24` for the renderer. The
   file has it at `:25` now (the editor re-saved it, as `CLAUDE.md` notes). The brief is frozen, so this goes in a
   revision if anywhere.
10. **The test logs carry an absolute path.** `test_report.gd:51` prints the globalised `evidence/` path in the
    `SUMMARY` line. Run `scripts/redact-paths.sh` on `logs/test_materials_*fps.log` before saving any of them as
    evidence. The JSON report itself holds no path.

No finding against `CHANGE-BRIEF.md` §4 itself: every sampler hint, uniform range, default, material value, bound
file and import setting matches the brief's tables, and the diorama still has exactly one light.

## 5. What the headless test cannot establish

The dummy renderer draws nothing, so the following are windowed or by-eye checks:

- any pixel value: the hint-experiment bands, the linen colour under the lamp, clipping under Linear tonemap;
- whether `source_color` actually decodes on this Compatibility path (finding 1), and whether the normal map tilts the
  lighting in the right direction on screen (the curl ratio checks the file, not the rendered result);
- whether `compress/normal_map=1` changed the format stored in the `.ctex` (the test reads the setting, not the
  imported image), and whether the 16-bit sources keep 16 bits after import;
- which mip levels and filter the GPU picks, and the shadow on the tiles;
- that the two tiles are in the camera's view (`check_assets.gd` checks this for the A3 models only);
- that the dark tile "reads as worn cloth" (§4, Why).

## Review (Claude, 2026-11-02, after the unedited audit commit)

- **Enums looked up** in Godot 4.7.2 itself (`evidence/a5/step3/review_probe.log`): `Environment.BG_COLOR` = 1,
  `AMBIENT_SOURCE_COLOR` = 2, `TONE_MAPPER_LINEAR` = 0, `Camera3D.PROJECTION_ORTHOGONAL` = 1, `Image.FORMAT_RGB8` = 4,
  `FORMAT_L8` = 0, `TYPE_BOOL` = 1, `TYPE_FLOAT` = 3, `TYPE_COLOR` = 20, `TYPE_OBJECT` = 24, `PROPERTY_HINT_RANGE` = 1,
  `PROPERTY_HINT_RESOURCE_TYPE` = 17. Every integer in this file matches.
- **Formats checked with `get_image().get_format()`**: diff 4 (RGB8), rough 0 (L8), nor_gl 4 (RGB8), nor_dx 4 (RGB8),
  hint_greys 4 (RGB8); none compressed. So the imported normal map is 8-bit RGB: the 16-bit sources do not keep 16 bits
  after import (this answers part of the §5 item on `.ctex` formats).
- **Finding 5 corrected:** the agent's "about 12–17 MB" was an estimate that assumed 3–4 bytes per pixel for every
  texture; the roughness map is one byte per pixel. Replaced with the measured sizes.
- **Finding 1, control run** (`evidence/a5/step3/hint_control.gd`, windowed): each quad given its own, separately
  loaded texture object (two different RIDs), bound only to the sampler it reads. Both quads still show
  64 / 128 / 192. So the shared texture is not the cause: on this Compatibility path, with this scene, the
  `source_color` hint changes nothing visible. Finding 1 is closed; finding 2 stays as a harmless redundancy.

## 6. Attribution

Hessian 380, https://polyhaven.com/a/hessian_380; colormass (photography), Rico Cilliers (processing); CC0
(https://polyhaven.com/license); checked 2026-10-31.
