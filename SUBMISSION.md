# SUBMISSION — Assignment 5: Shaders, Materials, and the Godot Shading Language

The Assignment 3 submission file is kept as [SUBMISSION-A3.md](SUBMISSION-A3.md).

| Field | Value |
|---|---|
| Student | Jiean Yin |
| Project name | walker-lane-tactics-jiean-yin (Lane Tactics) |
| GitHub repository URL | https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin |
| Git tag and submitted commit SHA | tag `a5`; the submitted commit SHA is given in the Canvas note (a commit cannot contain its own SHA) |
| Game-source revision shown in the film | the film is made after the source submission (allowed); its game-source revision will be the `a5` tag, or a later revision named in the Canvas comment |
| Godot version, renderer, and operating system | Godot 4.7.2.stable.official.ed1daf0bf (standard build), **Compatibility** renderer (OpenGL 3.3), Windows 11 Home 10.0.26200 |
| Game state the shader from code communicates | **exposed**: while you plan your move, your archer turns red when the square you are about to step to lies inside the enemy archer's reach. `godot/shaders/exposed_tint.gdshader`, driven by `godot/game/exposed_driver.gd` (fades over 0.20 s of game time; holds while paused) |
| 3D object and scene given the textured shader | two 1 m tiles, `LinenSquareLight` and `LinenSquareDark`, in the A3 diorama `godot/diorama/asset_diorama.tscn`; shader `godot/shaders/linen_square.gdshader`, materials `godot/materials/linen_light.tres` and `linen_dark.tres` |
| Texture sources and licences | Poly Haven **Hessian 380** (https://polyhaven.com/a/hessian_380), CC0, colormass (photography) and Rico Cilliers (processing), checked 2026-10-31; credits and checksums in `godot/assets/textures/hessian_380/ATTRIBUTION.md`. `hint_greys.png` written by `godot/tools/write_hint_greys.gd`. No generative model |
| Final film URL and filename | added after the source submission, as a Canvas comment (allowed by the course) |
| Final film SHA-256 | added with the film link |
| Summary of my work | I manually compare the state, object and texture to choose. Hand- write three shaders and compute the predictions. |
| Known limitations | The hint experiment shows no difference on Compatibility and the unused DirectX map is still imported |
| Changed games since Assignment 2 (yes/no; if yes, FRICTIONAL.md entry) | No: still Lane Tactics |

