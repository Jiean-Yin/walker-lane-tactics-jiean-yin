# Hint experiment: measured values (2026-11-02, Claude, windowed run)

Renderer: Compatibility (OpenGL 3.3), Godot 4.7.2. Scene `godot/hint/hint_experiment.tscn`:
WorldEnvironment tonemap Linear (0), exposure 1.0, glow, fog and adjustments off; orthographic camera;
`hint_srgb.tres` (use_srgb = true) on the top quad, `hint_raw.tres` (use_srgb = false) on the bottom quad,
both binding `hint_greys.png` (64, 128, 192; Lossless, no mipmaps) to both samplers.
Pixels read from the viewport image after `frame_post_draw`, at the centre of each band.

| Band (file value) | Quad A `source_color`: predicted / measured | Quad B no hint: predicted / measured |
|---|---|---|
| 64  | 64 / **64**   | 137 / **64**  |
| 128 | 128 / **128** | 188 / **128** |
| 192 | 192 / **192** | 225 / **192** |

Checks that the measurement is not a wiring mistake (`hint2.gd`):
- the two quads hold different material objects; A has use_srgb = true, B false;
- swapping the two switches at run time leaves every value unchanged;
- the texture is RGB8 (format 4); `use_hdr_2d` false; environment tonemap 0 (Linear).

Extra fact for the explanation (`hint3.gd`): a throwaway unshaded shader writing `ALBEDO = vec3(0.5)` shows **128**
(not 188), so this path writes values to the screen without the final sRGB encode. Quad A showing the file values
then means its texture was not decoded either (decoded but not encoded would read about 13, 55, 133).

Scripts: `snap.gd` (captures), `hint2.gd` (wiring check), `hint3.gd` (constant check), run with
`"$GODOT" --path godot --script <script> -- <out-folder>` (needs a window; not a headless test).
