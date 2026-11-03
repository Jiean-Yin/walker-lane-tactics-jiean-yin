# LANGUAGE-NOTES — Assignment 5: reading the Godot shading language

**Who wrote what:** the answers are Jiean's, in Jiean's own words. The course says the agent "does not write the answers" in this file, so Claude's `Pointer` boxes only say where to look (a line, a measurement, a docs page); they are not drafts. Claude may check afterwards that every line reference points where it says. Delete each pointer box once its answer is written.

The three hand-written shaders: `godot/shaders/exposed_tint.gdshader` (2D tint), `godot/shaders/linen_square.gdshader` (textured cloth), `godot/shaders/hint_experiment.gdshader` (colour experiment). The generated one: `godot/shaders/standard_generated.gdshader` (Step 4, converted from a StandardMaterial3D with albedo, normal and roughness textures; nothing in the game uses it).

## Line numbers in `standard_generated.gdshader`

| What | Line(s) |
|---|---|
| `shader_type` and `render_mode` | TO FILL |
| The uniform for the Inspector's albedo colour | TO FILL |
| The uniform for the Inspector's normal-map strength | TO FILL |
| The albedo sampler, with its hints | TO FILL |
| The normal-map sampler, with its hints | TO FILL |
| The line that writes `ALBEDO` | TO FILL |
| The line that writes `ROUGHNESS` | TO FILL |
| The line that writes `NORMAL_MAP` | TO FILL |

> **Pointer (Claude):** open the file in the shader editor (it shows line numbers). The first two lines hold the type and the render mode. Search for `uniform vec4 albedo`, `normal_scale`, `texture_albedo` and `texture_normal`; inside `fragment()`, search for `ALBEDO =`, `ROUGHNESS =` and `NORMAL_MAP =`.

## Questions

**1. What does `shader_type` decide? Answer for each type you used, citing the first line of each shader.**

TO FILL

> **Pointer (Claude):** `exposed_tint.gdshader:1`, `linen_square.gdshader:1`, `hint_experiment.gdshader:1`. Docs: *Shading language → Shader types*, and the *CanvasItem shaders* / *Spatial shaders* pages. Compare which built-ins each page lists and what kind of node each type can draw.

**2. Which processor functions did you write, and when does each run? What would change if you moved your colour line into `vertex()`, and why?**

TO FILL

> **Pointer (Claude):** your `fragment()` functions are at `exposed_tint.gdshader:6-8`, `linen_square.gdshader:16-22`, `hint_experiment.gdshader:8-14`; you wrote no `vertex()` or `light()`. Count how many vertices a `Sprite2D` quad has, and look up what `COLOR` holds inside `vertex()` on the CanvasItem shaders page (is the texture applied there yet?).

**3. Name three built-ins you read and two you wrote. Which of the ones you read are read-only?**

TO FILL

> **Pointer (Claude):** reads: `exposed_tint.gdshader:7`, `linen_square.gdshader:17`, `hint_experiment.gdshader:10`. Writes: `exposed_tint.gdshader:7`, `linen_square.gdshader:18-21`. The docs tables mark each built-in `in`, `out` or `inout`.

**4. For each hint you used, does it change only the Inspector, or also the value the shader receives? Cite your hint experiment.**

TO FILL

> **Pointer (Claude):** hints used: `hint_range` (`exposed_tint.gdshader:3`, `linen_square.gdshader:6`, `:10`, `:12`), `source_color` (`exposed_tint.gdshader:4`, `linen_square.gdshader:4-5`, `hint_experiment.gdshader:4`), `hint_normal` (`linen_square.gdshader:11`), `filter_*` and `repeat_enable`. Measurements: `evidence/a5/step3/hint_experiment_measurement.md` (both quads 64 / 128 / 192 on Compatibility) and the control in `godot/MATERIALS.md` (Review section). Your prediction was for Forward+ / Mobile (`CHANGE-BRIEF.md` §3). Say what you observed on this renderer, not only what the docs say.

**5. Does `hint_range` clamp a value set from code? Cite what you observed.**

TO FILL

> **Pointer (Claude):** your F9 capture at 2.0 (`evidence/a5/captures/exposed_pixels.md`, compare with your prediction in `CHANGE-BRIEF.md` §6 answer 7) and the headless check `godot/tests/test_exposed_tint.gd:198`.

**6. Which line of the generated shader makes the albedo sample as colour and the normal map as data, and what is the equivalent line in your textured shader?**

TO FILL

> **Pointer (Claude):** the two sampler lines you listed in the table above; yours are `linen_square.gdshader:4` and `:11`. Compare the hints word by word.

**7. Your `fragment()` runs for every pixel at once. Why can't it read what the neighbouring pixel's `fragment()` is computing, and how does game state reach it instead?**

TO FILL

> **Pointer (Claude):** the path game state takes: `godot/game/exposed_driver.gd:34` (the value), `:37` → `godot/game/piece.gd:65-68` (`set_shader_parameter`) → the uniform at `exposed_tint.gdshader:3`. Think about what "at once" means on a GPU and what a uniform is per draw call.

**8. Name two things the Godot shading language provides that plain GLSL does not, or makes you write yourself.**

TO FILL

> **Pointer (Claude):** docs page *Differences between GLSL and Godot shading language* (and *Converting GLSL to Godot shaders*). Compare one of your shaders with what a GLSL file needs at the top (`#version`, `in` / `out` declarations, `main()`), and with how your uniforms appear in the Inspector.
