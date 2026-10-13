# SOURCES — walker-lane-tactics-jiean-yin

## What this project started from

- **An empty Godot 4.7.2 project.** No code was taken from the walker-jumpman starter or from my Assignment 1 project ([walker-jumpman-jiean-yin](https://github.com/Jiean-Yin/walker-jumpman-jiean-yin)), because the game logic is different.
- **Practices carried over from Assignment 1:** headless test scripts under `godot/tests/` that write timestamped reports to `evidence/`; the document set (CHANGE-BRIEF, TEST-REPORT, FRICTIONAL, SOURCES); the `.gitignore` rules for media and credentials. The A1 starter was Nik Bear Brown's [walker-jumpman](https://github.com/nikbearbrown/walker-jumpman).
- **Game rules:** [RULES.md](RULES.md) and [DESIGN-HISTORY.md](DESIGN-HISTORY.md) were written with Claude in a conversation on my other Claude account (Sep 29 – Oct 9, 2026) and handed over as files; [CLAUDE.md](CLAUDE.md) is that handoff brief.

## Generative models

| Category | Model / service | Version | Where it ran | License / terms |
|---|---|---|---|---|
| Art (character, background) | Stable Diffusion XL base 1.0, `stabilityai/stable-diffusion-xl-base-1.0` (fp16) via 🤗 diffusers 0.41.0, PyTorch 2.14.1+cu126 | base 1.0 | locally on my laptop GPU (RTX 3070 Ti Laptop, 8 GB) | CreativeML Open RAIL++-M License (free use incl. coursework; use-based restrictions apply) |
| Background removal | rembg with the U²-Net `u2net` model | rembg 2.x, u2net.onnx | locally (CPU) | rembg: MIT; U²-Net: Apache-2.0 |
| Sound effects | ElevenLabs Sound Effects (web app, free plan) | as shown in the ElevenLabs app on 2026-10-12 | ElevenLabs website, run by me | ElevenLabs free plan: non-commercial use, attribution to ElevenLabs required *(to be confirmed against my account's plan page)* |
| Music (used) | MusicGen small, `facebook/musicgen-small`, via 🤗 transformers 5.19.0 | small (300M) | locally on my laptop GPU | weights CC-BY-NC 4.0 (non-commercial; acceptable for coursework) |
| Music (tried, not used) | Suno (web app, free plan) | v6-mini and v6 preview | Suno website, run by me | free plan; outputs could not be downloaded, so nothing from Suno is in the project |
| Music (tried, not used) | ElevenLabs Music (free plan) | — | ElevenLabs website | download not available on my free plan; nothing used |

No paid generation service or purchased credits were used. No prompt names a living artist, a copyrighted character, a brand, or existing music or recordings. No voice is used.

## Asset log

Every image and music take below is recorded line by line, with its SHA-256, in [assets/gen-log.jsonl](assets/gen-log.jsonl); every edit (background removal, scaling, recolour, trims, loop cut) is in [assets/edit-log.jsonl](assets/edit-log.jsonl) with input and output hashes. Rejected outputs are kept as contact-sheet thumbnails in [assets/rejected/](assets/rejected/).

**Common image settings:** SDXL base 1.0, 30 steps, guidance 7.0, 1024 × 1024 (ENV-TABLE 1344 × 768), seed via `torch.Generator("cpu").manual_seed(seed)`, default scheduler. Reproduce any row with `design/tools/gen_images.py <ASSET-ID> [--init <image> --strength <s>] --seeds <seed> [--prompt "<prompt>"]` using the prompt below. Image-to-image rows start from a pose sketch in `design/character/init/` (Claude's code-drawn design sketch from the character sheet); the strength is how much the model may change it.

**Negative prompts:** N1 = `realistic human, photo, legs, feet, mouth, nose, teeth, multiple figures, text, watermark, checkerboard, floor, cast shadow, gradient background, blurry, extra arms` · N2 = `photo, 3d render, realistic, grey background, gradient background, legs, feet, mouth, nose, teeth, multiple figures, text, watermark, checkerboard, floor, cast shadow, gradient background, blurry, extra arms` · N3 = `text, watermark, objects, people, board game, cards, cup, blurry, frame`

**Prompts:**
- **P1:** carved painted wooden toy archer game piece, side view facing right, full body, ball-shaped light birch wood head with one black dot eye, dark navy hood, teal painted cylinder body, walnut belt, quiver on back, wooden bow, round walnut disc base, thick dark outline, flat matte colors, simple shapes, standing upright, plain flat white background
- **P2:** 2D game sprite on a plain white background, flat vector illustration of a carved wooden toy archer game piece, side view facing right, standing upright, ball-shaped birch wood head, one black dot eye, dark navy hood, teal cylinder body without legs, walnut belt, quiver, wooden bow, round walnut disc base, thick dark outline, flat colors
- **P3 (pose prompts P4–P8 are P3 with `standing upright` replaced):** 2D game sprite on a plain white background, carved wooden toy archer game piece, side view facing right, standing upright, ball-shaped birch wood head, one black dot eye, dark navy hood, teal painted cylinder body without legs, walnut belt, quiver, wooden bow, round walnut disc base, thick dark outline, painted wood grain texture
- **P4–P8 pose phrase:** idle `at rest, bow held low` · draw `drawing the bow` · hurt `tilted backward, struck` · defeat `toppled, lying on its side` · win `arms raised, bow overhead`
- **P10:** top-down view of a dark walnut wooden tabletop, warm desk lamp light from the upper left, soft pool of light in the centre, gentle dark vignette, subtle wood grain, empty, no objects
- **P9 (music):** calm instrumental loop for a thoughtful tabletop strategy game, plucked nylon guitar and kalimba, soft wooden percussion, warm low drone, steady slow pulse, 80 bpm, 4/4, same energy throughout, no vocals

### Art

| Asset ID | Model / run | Prompt and settings | Outcome (judged against) | Edits | Where used |
|---|---|---|---|---|---|
| CHAR-REF | SDXL, run ref01, txt2img | P1, N1, seeds 101–104 | **Rejected (all 4)**: photo-real 3D toys on grey gradient, no outline (sheet rules 3, 6); 102 nearest but a teal helmet and legs (rules 1, 2) | — | [rejected/CHAR-REF-ref01.png](assets/rejected/CHAR-REF-ref01.png) |
| CHAR-REF | SDXL, run ref02, txt2img | P2, N2, seeds 101–104 | **Rejected (all 4)**: now illustrated, but cartoon humans with legs and full faces (rules 1, 2) | — | [rejected/CHAR-REF-ref02.png](assets/rejected/CHAR-REF-ref02.png) |
| CHAR-REF | SDXL, run ref03, img2img from `init/idle.png`, strength 0.75 | P2, N2, seeds 101–102 | **Rejected**: matches the sheet but is almost a trace of the design sketch; flat, not wood; stray chest dot | — | [rejected/CHAR-REF-ref03.png](assets/rejected/CHAR-REF-ref03.png) |
| CHAR-REF | SDXL, run ref04, img2img, strength 0.85 | P2, N2, seeds 101–102 | **Rejected**: drifts to a front view with two eyes, one with legs (rules 2, 6) | — | [rejected/CHAR-REF-ref04.png](assets/rejected/CHAR-REF-ref04.png) |
| CHAR-REF | SDXL, run ref05, img2img, strength 0.80 | P3, N2, seeds 201–204 | **s202 accepted by Jiean** ("it looks the most like painted wood"). s201 rejected: red collar (red is the enemy colour); s203 rejected: eye too big, hood reads as hair; s204 rejected: least wooden | reference only (not in the game) | [rejected/CHAR-REF-ref05.png](assets/rejected/CHAR-REF-ref05.png), [compare at game size](assets/rejected/CHAR-REF-compare-game-size.png) |
| CHAR-IDLE | SDXL, run pose01, img2img from `init/idle.png`, strength 0.80 | P4, N2, seeds 202, 211, 212 | **s211 accepted by Jiean**; s212 rejected (long hair, front-facing face) | rembg; halo cleanup erased the model's near-white base, so the **base disc was redrawn** (walnut ellipse 40 × 12 game px with ink outline, behind the piece); scale; anchor; enemy recolour | `godot/assets/art/archer_idle.png`, `archer_idle_enemy.png` · panels 1, 2, 3, 7 |
| CHAR-DRAW | SDXL, run pose01, init `draw.png`, 0.80 | P5, N2, seeds 202, 211, 212 | **s211 accepted by Jiean**; s202 rejected (hood turned teal, breaks the palette); s212 rejected (long hair) | rembg, halo cleanup, scale, anchor, enemy recolour | `archer_draw.png`, `archer_draw_enemy.png` · panel 4 |
| CHAR-HURT | SDXL, run pose01, init `hurt.png`, 0.80 | P6, N2, seeds 202, 211, 212 | **s212 accepted by Jiean**; s202 rejected (teal hood, blue glow) | same | `archer_hurt.png`, `archer_hurt_enemy.png` · panels 4, 5 |
| CHAR-DEFEAT | SDXL, run pose01, init `defeat.png`, 0.80 | P7, N2, seeds 202, 211, 212 | **s211 accepted by Jiean**; s202 rejected (green mark on the face); s212 rejected (body melts into a brown block) | same, plus scale × 8.5/6.5 (the defeat sketch was drawn smaller) | `archer_defeat.png`, `archer_defeat_enemy.png` · panel 6 |
| CHAR-WIN | SDXL, run pose01, init `win.png`, 0.80 | P8, N2, seeds 202, 211, 212 | **s202 accepted by Jiean**; s212 rejected (arms merge into the face). In all three the arms cover the face, inherited from the sketch | same | `archer_win.png`, `archer_win_enemy.png` · panels 8, 9 |
| ENEMY-* | (edit of each CHAR image) | — | accepted: wood, walnut and navy hood unchanged | only teal pixels (hue 165–200°, saturation > 0.25) rotated to hue 4° (#B23A2E family) | `archer_*_enemy.png` |
| ENV-TABLE | SDXL, run env01, txt2img, 1344 × 768 | P10, N3, seeds 301–304 | **s301 accepted** (Claude's recommendation; Jiean did not object): warm upper-left lamp light per CONCEPT. s302 rejected (glare hotspot); s303, s304 rejected (flat, no lamp pool) | scaled to cover 1280 × 720, centre-cropped | `godot/assets/art/env_table.png` · panels 1, 2, 6, 7 · [rejected/ENV-TABLE-env01.png](assets/rejected/ENV-TABLE-env01.png) |
| — | all pose candidates side by side, full size and at 80 px on linen and table | | | | [rejected/CHAR-POSES-pose01-compare.png](assets/rejected/CHAR-POSES-pose01-compare.png) |

### Sound effects (ElevenLabs Sound Effects, run by Jiean)

Prompts: the four prompts in [design/GENERATION-PROMPTS.md §2](design/GENERATION-PROMPTS.md), with a short description of the game added by Jiean (the exact added text was not recorded). ElevenLabs gives no seed, so the downloaded file and its hash are the record.

| Asset ID | Raw file (SHA-256 prefix) | Outcome | Edits (edit-log) | Where used |
|---|---|---|---|---|
| SFX-HOP | `LandingSound.mp3` 0.48 s (`01699116`) | accepted by Jiean | no lead silence to trim; kept 0.30 s; 60 ms fade-out; peak −1 dBFS; mono OGG q6 | `godot/assets/sfx/sfx_hop.ogg` · panel 3 |
| SFX-HIT | `arrowshit.mp3` 1.00 s (`e99c4b23`) | accepted by Jiean | kept 0.55 s (tail below −40 dB); 100 ms fade-out; peak −1 dBFS | `sfx_hit.ogg` · panel 4 |
| SFX-HURT | `gethit.mp3` 2.00 s (`298ad1e2`) | accepted by Jiean | kept 1.0 s; 150 ms fade-out; peak −1 dBFS | `sfx_hurt.ogg` · panels 5, 6 |
| SFX-WIN | `win.mp3` 0.48 s (`84469a93`) | accepted by Jiean | full length; 30 ms fade-out; peak −1 dBFS | `sfx_win.ogg` · panel 8 |

### Music

| Asset ID | Model / settings | Outcome | Edits | Where used |
|---|---|---|---|---|
| MUS-LOOP (Suno) | Suno v6-mini / v6 preview, Advanced mode; Jiean's lyrics-field and style text (visible in the screenshots), e.g. styles "epic war gaming music. Should be exciting and raise up mood" | **Not used**: free plan cannot download | — | [rejected/MUS-suno-attempt-1…4.png](assets/rejected/) (cropped to the Suno page) |
| MUS-LOOP (ElevenLabs Music) | prompt in GENERATION-PROMPTS §3 | **Not used**: download not available on the free plan | — | — |
| MUS-LOOP | MusicGen small, P9, seeds 1, 2, 3, 30 s each (1500 tokens), guidance 3.0, sampling on | **s1 accepted by Jiean** ("smoother and static music won't disrupt the thinking and brings more peace"). s2 rejected by Jiean in favour of s1. s3 rejected: ~107 bpm, too fast for the "slow pulse" in the audio direction | 8 bars at 79.8 bpm (tempo estimated by script), cut from 2.864 s (strongest onset after 1.5 s), 24.06 s long, 40 ms crossfade from the audio after the cut into the start; seam jump 0.0016; OGG q6 | `godot/assets/music/mus_loop.ogg` · panels 1–7 |

## Tools

| Tool | Version | Use |
|---|---|---|
| Godot Engine | 4.7.2.stable.official.ed1daf0bf (Windows, standard build) | engine, headless tests, captures |
| Claude Code (Anthropic) | Claude desktop app, Claude Opus 5.5, Northeastern access | code, prompts, generation and processing scripts, design sketches (SVG), document drafts |
| Python | 3.11.4 (sketch script); private venv with torch, diffusers, transformers, rembg | generation and processing scripts |
| Microsoft Edge (headless) | system install | rendering sketch SVGs to PNG |
| FFmpeg | 9.0.2 full build | audio decode and OGG Vorbis encode |

## Human and AI contributions

**Jiean Yin decided:** the game and its rules (with the other Claude account, see DESIGN-HISTORY); accepting the A2 scope proposals; the one-enemy slice after the search (CHANGE-BRIEF R1); the accepted reference (s202) and every accepted pose (idle 211, draw 211, hurt 212, defeat 211, win 202); the accepted music take (s1); generating and choosing the four sound effects in ElevenLabs; the Suno and ElevenLabs Music attempts; the judgment lines in FRICTIONAL.md.

**Claude Code contributed:** the design-doc drafts and design sketches (under Jiean's direction); all prompts for the local models; running SDXL and MusicGen locally and recording seeds; written assessments of each candidate against the character sheet (recommendations, which Jiean accepted or overrode); background removal, base-disc redraw, recolour, trims and the loop cut; the Godot slice code and tests (partly through a Claude Code sub-agent in the same session); this file.

**The generative models produced:** every character pose image, the tabletop background (SDXL), the four sound effects (ElevenLabs), and the music (MusicGen). Code-drawn parts of the game (board squares, HUD, markers, arrow projectile, cards) are Claude's code, not generated art.
