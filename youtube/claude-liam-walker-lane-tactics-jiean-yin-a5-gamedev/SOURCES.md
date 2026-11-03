# SOURCES — A5 film

| Item | Source | Provenance |
|---|---|---|
| Game source shown | tag `a5` = `ef5d38bc6d5f2fbdda62a4f4001791405dee0071`, GitHub `Jiean-Yin/walker-lane-tactics-jiean-yin` | isolated git-archive copy; 111 `godot/` files checked against their blobs (CAPTURE.md) |
| Engine footage | Godot 4.7.2.stable.official.ed1daf0bf, Compatibility (OpenGL 3.3), Movie Maker, 30 fps, 3840 × 2160 SubViewport → FFV1 | `capture/a5_capture_driver.gd`, run 02; master hashes in `capture/masters-sha256.txt` (masters not in git) |
| Jiean's captures | `evidence/a5/captures/exposed_*.png`, `os_screenshot.png` at tag `a5` | Jiean pressed C in `debug/capture_exposed.tscn` (2026-11-02 22:57); the screenshot shows only the game window |
| Test results | `TEST-REPORT.md` A5 at tag `a5`; `evidence/a5/mutations/`; `capture/film-rerun.json` (this film's rerun on the copy) | recorded reports |
| Texture | Poly Haven **Hessian 380**, https://polyhaven.com/a/hessian_380, CC0, colormass (photography), Rico Cilliers (processing), checked 2026-10-31 | `godot/assets/textures/hessian_380/ATTRIBUTION.md` |
| Generated shader | `godot/shaders/standard_generated.gdshader`: Godot editor conversion of a StandardMaterial3D, saved by Jiean (`ad54134`) | quoted verbatim in B14 |
| Narration | Kokoro-82M (`kokoro-onnx`), voice `am_onyx`, local, no API; script drafted by Claude from Jiean's documents and approved by Jiean on 2026-11-03 | `mp3/` (not in git), `beat_sheet.json` |
| Scenes | Brutalist runtime at `<brutalist>` checkout `6a8380a`: `ClaudeComposerAsk`, `BrutalistHesitantWriter`, `GodotDevWorkbench`, `ClaudeVerdictArtifact`, `ClaudeTitleOutro` (Remotion) | `beat_sheet.json` `rendered` stamps |
| Stills | composed by `tools/make_media.py` from the files above (fonts: EB Garamond, Inter, PT Mono from the Brutalist runtime) | `stills/` previews |

No generative image, video, music or sound model was used. No upstream documentation is quoted. The Claude interface beats (B00, BHTF) are labelled reconstructions; the code views are labelled "Godot editor reconstruction".
