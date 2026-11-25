# SOURCES — Assignment 8 pitch film

## What Jiean made

- The game and every layer shown or named: Lane Tactics, tags `a3`, `a5`, `a6` and `film-source-v1` (see the repository's `SOURCES.md` for each layer's assets and their provenance).
- The project choice and the acceptance of the seven answers in `PROJECT-BRIEF.md` (2026-11-24).

## What Claude contributed (Claude Code, Claude Opus 5.5, 2026-11-24)

- The wording of `PROJECT-BRIEF.md` and the narration in `beat_sheet.json`, drafted from Jiean's accepted answers and the repository.
- `tools/build_film.py` (slides, cuts, assembly) and the drawn slides: text, boxes and two simple figures drawn in code, labelled *constructed* on screen.
- `README.md`, `BUILD-PROMPT.md`, this file, and the factual lines of `FRICTIONAL.md`.

## Footage

- Gameplay in beats B02 and B05 is cut from Jiean's Assignment 6 film master (`youtube/claude-liam-walker-lane-tactics-jiean-yin-a6-gamedev/`, SHA-256 `68124efb8d904f0eb81a8ee462470ed6ec43e23f1826fac922c26510b00075c6`). That master is a Godot Movie Maker capture of **tag `a6` (`7f199f9`)** with scripted key presses. Its burned-in labels (scripted key presses, ¼ speed, cropped) stay visible, and the pitch adds its own label.
- No new capture, no generated images, no third-party footage.

## Tools and third-party assets

| What | Licence | Use |
|---|---|---|
| Brutalist toolkit, checkout `6a8380a` (`<brutalist>`) | the toolkit's own | Kokoro narration step `runtime/scripts/generate_audio_kokoro.py`; quality gates |
| Kokoro-82M via kokoro-onnx, voice `am_onyx` (local) | Apache-2.0 | narration (AI voice reading Jiean's words, said so in the film) |
| EB Garamond, Inter, PT Mono (from `<brutalist>/runtime/fonts`) | SIL OFL 1.1 | slide text |
| FFmpeg, Pillow | LGPL/GPL build; HPND | cutting, assembly, loudness; drawing |

The comparable games (Plants vs Zombies, Into the Breach) are named in text only; no art, footage or audio from either is used.
No paid generation, no API key, no account.
