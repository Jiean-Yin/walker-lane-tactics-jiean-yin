# SOURCES — A6 film

| Item | Source | Provenance |
|---|---|---|
| Game source shown | tag `a6` = `7f199f9ee4f24a3bb75b117d67e9ad0c2dfda004` (annotated tag object `fdf6c1b`), GitHub `Jiean-Yin/walker-lane-tactics-jiean-yin` | isolated git-archive copy; 131 `godot/` files checked against their blobs; every suite rerun on it (CAPTURE.md) |
| Engine footage | Godot 4.7.2.stable.official.ed1daf0bf, Compatibility (OpenGL 3.3), Movie Maker at 30 fps (play) and 120 fps (slow, shown at ¼ speed), 3840 × 2160 SubViewport → FFV1 | `capture/a6_capture_driver.gd`; masters' SHA-256 in `capture/masters-sha256.txt` (masters not in git). Filmed from the local tag before the history rewrite; the game files are identical to the pushed tag's (CAPTURE.md) |
| Jiean's strips | `captures/hit_burst/r0–r3`, `captures/arrow_trail/r0–r1` at tag `a6` | rendered by Jiean with Movie Maker from the preview scenes (fixed seed); shown as labelled fixtures (B10, B16, B26) |
| Test results | TEST-REPORT A6 at tag `a6`; `evidence/a6/mutations/`, `step5b/`, `final/`, `gpu/`; `capture/film-rerun.txt` (this film's rerun on the copy) | recorded reports, quoted verbatim where on screen |
| Jiean's words | TUNING.md (requests and verdicts), TEST-REPORT A6.6 (conclusion), A6.7 (line references, shader / draw-step split), A6.8 (playtest), at tag `a6` | read by `tools/quotes.py` from the copy into `capture/quotes.json`; voice excerpts approved by Jiean (`capture/QUOTES-REVIEW.md`) |
| Generated shader | `godot/shaders/particles_generated.gdshader`: the Godot editor's conversion of the Wisps ParticleProcessMaterial, saved by Jiean | lines 252–257 shown in B25 |
| Textures | none sourced: `GradientTexture2D` resources inside the effect scenes | `godot/effects/ATTRIBUTION.md` |
| Narration | Kokoro-82M (`kokoro-onnx`), voice `am_onyx`, local, no API. Script drafted by Claude from Jiean's documents and approved by Jiean on 2026-11-08, with the dated changes in SCRIPT-DRAFT.md | `mp3/` (not in git), `beat_sheet.json` |
| Scenes | Brutalist runtime at `<brutalist>`, checkout `6a8380a`, with the same local patches as the A5 film (Windows `npx.cmd`, outro mascot headroom). Patterns: `ClaudeComposerAsk`, `BrutalistHesitantWriter`, `GodotDevWorkbench`, `ClaudeVerdictArtifact`, `ClaudeTitleOutro` (Remotion) | `beat_sheet.json` `rendered` stamps |
| Stills | composed by `tools/make_media.py` from the files above. Fonts: EB Garamond, Inter, PT Mono, from the Brutalist runtime. Chart colours #C2613F / #2F6FB0 on #FAF9F5, checked with the dataviz palette validator | `stills/` previews |

- No generative image, video, music or sound model was used, and no upstream documentation is quoted.
- The Claude interface beats (B00, BHTF) are labelled reconstructions; the code views are labelled "Godot editor reconstruction".
