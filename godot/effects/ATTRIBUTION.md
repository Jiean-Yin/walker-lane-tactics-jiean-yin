# Texture credits: `godot/effects/`

The particle effects use **no image files**: no sourced, downloaded or generated texture. Every particle texture is a `GradientTexture2D` resource defined inside the scene file, so the code that makes it is committed with the scene (CHANGE-BRIEF §3).

| Texture | Defined in | What it is | Used by |
|---|---|---|---|
| soft dot | `hit_burst.tscn` (`GradientTexture2D_dot`), `arrow_trail.tscn` (`GradientTexture2D_dot`) | 32 × 32, radial fill from the centre, white → transparent | `Flash`, `Dust`, `Streak`, `Wisps` |
| sliver | `hit_burst.tscn` (`GradientTexture2D_sliver`) | 4 × 16, linear fill top to bottom, transparent at both ends, white in the middle | `Splinters` |

- **Written by:** the `claude -p` agent sessions 2a and 2b (`cb9830b`, `de4f389`), from the values in CHANGE-BRIEF §1–2.
- **Licence:** ours (project code). No third-party material and no generative model.
- **Checked:** 2026-11-08.
