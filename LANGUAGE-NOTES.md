# LANGUAGE-NOTES — Assignment 5: reading the Godot shading language

**Who wrote what:** the answers are Jiean's, in Jiean's own words. The course says the agent "does not write the answers" in this file, so Claude's `Pointer` boxes only say where to look (a line, a measurement, a docs page); they are not drafts. Claude may check afterwards that every line reference points where it says. Delete each pointer box once its answer is written.

The three hand-written shaders: `godot/shaders/exposed_tint.gdshader` (2D tint), `godot/shaders/linen_square.gdshader` (textured cloth), `godot/shaders/hint_experiment.gdshader` (colour experiment). The generated one: `godot/shaders/standard_generated.gdshader` (Step 4, converted from a StandardMaterial3D with albedo, normal and roughness textures; nothing in the game uses it).

## Line numbers in `standard_generated.gdshader`

| What | Line(s) |
|---|---|
| `shader_type` and `render_mode` | 3, 4 |
| The uniform for the Inspector's albedo colour | 6 |
| The uniform for the Inspector's normal-map strength | 20 |
| The albedo sampler, with its hints | 7 |
| The normal-map sampler, with its hints | 19 |
| The line that writes `ALBEDO` | 35 |
| The line that writes `ROUGHNESS` | 43 |
| The line that writes `NORMAL_MAP` | 46 |

## Questions

**1. What does `shader_type` decide? Answer for each type you used, citing the first line of each shader.**

shader_type determines what kind of built-in variables Godot gives you, and what kind of nodes the shader can be attached to.

**2. Which processor functions did you write, and when does each run? What would change if you moved your colour line into `vertex()`, and why?**

I only wrote fragment(). It runs once for every pixel the sprite or mesh covers. For a Sprite2D, that's every pixel of the archer; for a 1 m PlaneMesh, that's every pixel of the tile.

I did not write vertex() or light().

If I moved the colour line into vertex(), it would run once per vertex, not per pixel. A Sprite2D is basically one quad — four vertices. Inside vertex(), COLOR is the vertex colour times modulate, but the texture has not been applied yet. So COLOR there is not the archer's pixel colour. The tint would be computed from a flat colour and then interpolated across the quad, which is not what I want. The blend has to happen per pixel, after the texture is sampled, so it belongs in fragment().

**3. Name three built-ins you read and two you wrote. Which of the ones you read are read-only?**

Read:

COLOR in exposed_tint.gdshader — on input it's the sprite's colour (texture × modulate).

UV in linen_square.gdshader — the mesh's texture coordinate.

UV in hint_experiment.gdshader — same thing, for the 3 × 1 bands.

Wrote:

COLOR.rgb in exposed_tint.gdshader — I only change .rgb, so alpha stays as it was.

ALBEDO, ROUGHNESS, NORMAL_MAP in linen_square.gdshader — these are outputs.

Which reads are read-only: UV is read-only on input; I never write it. COLOR is not read-only — in fragment() it's also the output, so I can write to it. That's exactly why the tint line works: I read the incoming COLOR, then write the blended result back into it.

**4. For each hint you used, does it change only the Inspector, or also the value the shader receives? Cite your hint experiment.**

hint_range (exposed_amount, uv_scale, roughness_scale, normal_strength): Inspector slider only. It does not clamp a value set from code. My F9 capture at 2.0 showed the colour line extrapolating past the red — no clamp happened.

source_color: changes the value the shader receives. On Compatibility, my two quads both displayed 64 / 128 / 192. So on this renderer, the source_color decode and the final encode cancelled out, and Quad A returned the file's numbers exactly. Quad B (no hint) should have come out lighter, but the measurement file records both quads as 64 / 128 / 192. That contradicts my Forward+/Mobile prediction and needs to be written up as observed, not explained away.

hint_normal: tells Godot the texture is a tangent-space normal map, so it's treated as data, not colour. I used it on normal_tex, not on the albedo.

filter_nearest: keeps the 3 band edges sharp in hint_experiment, so the readings aren't smeared by interpolation.

repeat_enable: lets the cloth weave tile past UV 0–1, which is why uv_scale works across a 1 m square

**5. Does `hint_range` clamp a value set from code? Cite what you observed.**

No, it does not clamp. My F9 capture at exposed_amount = 2.0 shows the colour line going past the target red — the factor is 0.7 × 2 = 1.4, so mix extrapolates. The head's green channel lands around 27 instead of stopping at the red's 69. The headless check at test_exposed_tint.gd:198 also sets 2.0 and confirms the shader receives it. So hint_range is a UI hint, not a safety clamp.

**6. Which line of the generated shader makes the albedo sample as colour and the normal map as data, and what is the equivalent line in your textured shader?**

The albedo line is uniform sampler2D albedo_tex : source_color, filter_linear_mipmap, repeat_enable;. The source_color hint is the part that says "decode this as sRGB colour before the shader sees it."

The normal line is uniform sampler2D normal_tex : hint_normal, filter_linear_mipmap, repeat_enable;. hint_normal says "this is tangent-space normal data, green-up" — no colour decode.

In the textured shader they are linen_square.gdshader:4 and :11. Word by word, the difference is source_color vs hint_normal; the filtering and repeat hints are the same.

**7. Your `fragment()` runs for every pixel at once. Why can't it read what the neighbouring pixel's `fragment()` is computing, and how does game state reach it instead?**

"At once" means the GPU runs many copies of fragment() in parallel, and they don't share a scratchpad. A pixel can't look sideways at what the pixel next to it just computed, because there's no guaranteed order and no shared per-pixel memory you can read back like that.

Game state reaches the shader through a uniform, not through neighbouring pixels. The path is: exposed_driver.gd:34 computes the value, :37 calls set_shader_parameter on the material (piece.gd:65-68), and that value lands in the exposed_amount uniform at exposed_tint.gdshader:3. A uniform is the same for every pixel in that draw call, so all pixels see the same state value, and each pixel applies it to its own COLOR.

**8. Name two things the Godot shading language provides that plain GLSL does not, or makes you write yourself.**

One file, both stages. Godot lets me put vertex() and fragment() in the same .gdshader, and they can share uniforms. In GLSL I'd need two separate programs and varyings to pass data between them.

No main() and no #version. Godot supplies the entry points and the boilerplate. I write void fragment() { ... } and it runs; I don't write void main(), #version, or declare in/out for the built-ins. The uniforms I declare also show up directly in the Inspector, which plain GLSL doesn't give me.

