# SOURCES — Lane Tactics: From Sketch to Seed to Sound

## Game source shown

- Repository `Jiean-Yin/walker-lane-tactics-jiean-yin`, tag **`film-source-v1` = `fcf33eff6c501d32624532ca197257a646552991`**; `godot/` is identical to `12f7283`. All 51 authored `godot/` files are byte-identical to the tag blobs and hashed in [gamedev-evidence.json](gamedev-evidence.json).
- Outside `godot/` the film shows: `CONCEPT.md`, `CHARACTER-SHEET.md`, `STORYBOARD.md`, `CHANGE-BRIEF.md` (R1, R2), `SOURCES.md`, `TEST-REPORT.md`, `FRICTIONAL.md`, `assets/gen-log.jsonl` (line 18; lines 17, 19), `assets/edit-log.jsonl` (lines 7, 19, 29, 30), `design/tools/process_sprites.py` (lines 43–50 and 100; blob `1b7216a9`, SHA-256 of the LF blob `86fa1f69…`; the Windows checkout has CRLF), `design/character/init/idle.png`, `hurt.png`, `defeat.png`, `win.png`, `design/character/poses.svg`, `design/storyboard/02-board-start.svg`, and the git-history blob `4d5ff51:godot/assets/art/archer_idle.png` (SHA-256 `a00d7b5d…`, = edit-log line 7).
- Raw generations shown (not in git, `assets/_raw/` is ignored): `assets/_raw/art/CHAR-IDLE/CHAR-IDLE-pose01-s202|s211|s212-str0.80.png`, SHA-256 `5e98be70…`, `0b2c8d61…`, `7b628971…` — equal to `assets/gen-log.jsonl` lines 17–19.

## Engine evidence

- Native capture: `<capture-copy>\run-03\run-4k.mkv` (FFV1 3840×2160, SHA-256 `2f6c4cbf…`) and `run-03.avi` (Godot Movie Maker, SHA-256 `7c914575…`) from an isolated `git archive` copy of the tag; method, input path, hashes and checks in [CAPTURE.md](CAPTURE.md). Per-beat clips and hashes: [capture/clips.json](capture/clips.json).
- Runtime-tree probe: not needed for this film (no claim is made about runtime-only nodes; the saved scene `main.tscn` is Main + AudioDirector, everything else is created in code, as main.gd's `_ready` shows).
- Tests re-run on the isolated copy: [capture/test_rules.log](capture/test_rules.log) (51/51), [capture/test_audio_events.log](capture/test_audio_events.log) (70/70).

## Asset provenance (from the project's SOURCES.md, not re-verified by this film beyond the hashes above)

| Asset | Model / tool | Run by | Licence / terms (as the project records them) |
|---|---|---|---|
| Archer poses CHAR-IDLE/DRAW/HURT/DEFEAT/WIN, background ENV-TABLE | Stable Diffusion XL base 1.0, local (diffusers 0.41.0, torch 2.14.1+cu126) | Claude Code on Jiean's laptop GPU | CreativeML Open RAIL++-M |
| Background removal | rembg 2.x with U²-Net `u2net` | Claude Code (CPU) | rembg MIT; U²-Net Apache-2.0 |
| SFX-HOP, SFX-HIT, SFX-HURT, SFX-WIN | ElevenLabs Sound Effects, free plan | Jiean | free plan: non-commercial, attribution (project marks "to be confirmed") |
| MUS-LOOP | MusicGen small, local (transformers 5.19.0) | Claude Code | weights CC-BY-NC 4.0 |

## Film toolkit and voice

- Brutalist checkout `<brutalist>` at `6a8380a`, skill `godot-gamedev` with the `walker` modifier; components `ClaudeComposerAsk`, `BrutalistHesitantWriter`, `GodotDesignBoard`, `ClaudeCodeBeat`, `GodotDevWorkbench`, `FormACard`, `ClaudeVerdictArtifact`, `ClaudeTitleOutro` rendered with `runtime/scripts/remotion_scenes.py`.
- Local Brutalist patch carried over from Assignment 1 (not upstream): `runtime/scripts/remotion_scenes.py` resolves `npx` with `shutil.which("npx")` (Windows `npx.cmd`). Second local patch, made for this film after the approval gate: `runtime/remotion/src/scenes/ClaudeTitleOutro.tsx` gives the mascot `marginTop: 28 + ceil(35/86 × mascotH)` instead of `28`, so the slug-seeded `jump` animation (seed 4749 % 18 = 15) can no longer rise into the `@NikBearBrown` handle; measured gap at 4K 82–198 px over every frame. Title, handle, slug-seeded animation, polarity and the no-subline rule are unchanged. No other toolkit file was edited. `runtime/remotion/_bench/consumers.json` (gitignored index) is updated by the wrapper as a side effect.
- Narration: Liam (in for Bear), local Kokoro `am_onyx`, no cloning, no paid TTS.
- Evidence composites (B04–B07, B16, B18) and gameplay labels: `tools/make_stills.py`, `tools/make_clips.py` (Pillow + ffmpeg 9.0.2), fonts EB Garamond, Inter, PT Mono from `runtime/fonts` (OFL).
- Upstream documentation consulted: none beyond the Brutalist skill files and the Godot command-line behaviour observed directly (`--write-movie`, `--fixed-fps`).

## Double-check corrections

See [FACTCHECK.md](FACTCHECK.md) "Corrections made before rendering". No secrets, `.env` contents or credentials are used or shown. Absolute paths on screen are limited to the test-log lines in B17 (verbatim output) and the capture folder name.
