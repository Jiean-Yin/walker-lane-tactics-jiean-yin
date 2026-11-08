# SUBMISSION — Assignment 6: Creating Particle Effects with Godot and Claude

The earlier submission files are kept as [SUBMISSION-A5.md](SUBMISSION-A5.md) and [SUBMISSION-A3.md](SUBMISSION-A3.md).

| Field | Value |
|---|---|
| Assignment | Assignment 6 - Creating Particle Effects with Godot and Claude |
| Student | Jiean Yin |
| Project name | walker-lane-tactics-jiean-yin (Lane Tactics) |
| GitHub repository URL | https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin |
| Git tag and submitted commit SHA | tag `a6`; the submitted commit SHA is given in the Canvas note (a commit cannot contain its own SHA) |
| Game-source revision shown in the film | TO FILL after the film |
| Godot version, renderer, and operating system | Godot 4.7.2.stable.official.ed1daf0bf (standard build), **Compatibility** renderer (OpenGL 3.3), Windows 11 Home 10.0.26200 |
| GPU used for the GPU price | NVIDIA GeForce RTX 3070 Ti Laptop GPU (OpenGL 3.3), 180 Hz display |
| Effect A: event, node type, retrigger rule | **Hit burst** on every `"damaged"` event played by `main._cue_impact()` (an arrow hits an archer); three `CPUParticles2D` (`Flash`, `Splinters`, `Dust`) in `godot/effects/hit_burst.tscn`; retrigger **overlap**: a new instance per hit, at most 2 alive (two hits 1.05 s apart) |
| Effect B: job, condition, node type, feature Effect A doesn't use | **Trail**: who shot whom. Condition: an arrow in flight (`main._arrows` not empty). Two `GPUParticles2D` (`Streak`, `Wisps`) in `godot/effects/arrow_trail.tscn`, emitting in world space from an emitter that follows the arrow tip. Feature A lacks: **turbulence** on `Wisps` (also damping). Godot's `trail_enabled` is not used: Compatibility draws nothing with it |
| Budgets, and the price each is compared on | Effect A: 0.2 ms on both prices (CPU node). Measured headless CPU +0.0078 ms, GPU +0.0031 ms. Effect B: 0.2 ms on GPU time (GPU node). Measured GPU +0.0074 ms (headless CPU +0.0066 ms). Both under budget (TEST-REPORT A6.6) |
| Texture sources and licences (or model, version, and terms) | No image files: both particle textures are `GradientTexture2D` resources defined in the scene files (`godot/effects/ATTRIBUTION.md`). No generative model |
| Final film URL and filename | TO FILL |
| Final film SHA-256 | TO FILL |
| Summary of my work | TO FILL (Jiean) |
| Known limitations | The trail is dotted at 30 fps particle steps; the red flash is weak over the red enemy; the cancelled-attack case can't be reached in this slice; both prices are below the Visual Profiler's frame-to-frame swing (README, TEST-REPORT A6.10) |
| Changed games since Assignment 2 (yes/no; if yes, FRICTIONAL.md entry) | No: still Lane Tactics |

> *Hint (Claude) for "Summary of my work":* one or two sentences in your words. What did you choose and decide (the two effects, the retrigger rule, the predictions and budget, the tuning requests and verdicts), and what did you check yourself (the strips, the mutations, the Visual Profiler, the playtest, the process-shader lines)?
