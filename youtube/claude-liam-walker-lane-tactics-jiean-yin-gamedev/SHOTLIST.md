# SHOTLIST — Lane Tactics: From Sketch to Seed to Sound

Total 6:08.2 (368.20 s) at 30 fps. Times are the review-cut timeline.

| Beat | Start | Dur (s) | Visual (filled by) | On-screen label | Audio |
|---|---|---|---|---|---|
| B00 | 0:00.0 | 18.27 | ClaudeComposerAsk: "Hello, Liam", Walker prompt types, output lines | Illustrative reconstruction of the Claude interface — not a transcript | Liam |
| B01 | 0:18.3 | 13.30 | BrutalistHesitantWriter: "…judged in folders" → "…judged in the running game" | — | Liam (0.8 s lead) |
| B02 | 0:31.6 | 19.77 | GodotDesignBoard: CONCEPT.md two-sentence excerpt + four pillar cards lit on cue | (component: "Reconstructed reading view. Exact excerpt") | Liam |
| B03 | 0:51.3 | 10.93 | run-03 frames 0–327: title, board, lose-route turns 1–2 | SCRIPTED INPUT · REAL GODOT RENDER / film-source-v1 · game audio muted | Liam |
| B04 | 1:02.3 | 16.83 | Composite: sheet pose 2, init/idle.png, storyboard panel 2; rule chips on cue | Design sketches: SVG by Claude Code under Jiean Yin's direction — not generated art | Liam |
| B05 | 1:19.1 | 18.83 | Composite: gen-log line 18 (prompt P4, N2, settings); rows highlighted on cue | assets/gen-log.jsonl line 18 · values verbatim · long strings wrapped for display | Liam |
| B06 | 1:37.9 | 17.50 | Composite: raw s202 / s211 / s212 with hashes; choice and rejection on cue | Raw model output, downscaled · the engine never shows these files (title: "Raw SDXL Output — Not In-Engine") | Liam |
| B07 | 1:55.4 | 16.70 | Composite: raw → cut-out (4d5ff51, base gone) → base redrawn → enemy copy | Actual files: raw output, git history and godot/assets — not in-engine | Liam |
| B08 | 2:12.1 | 19.00 | ClaudeCodeBeat: process_sprites.py lines 43–50 + line 100 | Actual source excerpt (process_sprites.py @ film-source-v1) · reconstructed code view | Liam |
| B09 | 2:31.1 | 7.20 | run-03 frames 812–1027: retry, F3 slots and base discs | SCRIPTED INPUT · REAL GODOT RENDER / … game audio muted | Liam |
| B10 | 2:38.3 | 16.90 | GodotDevWorkbench: piece.gd 175–185, lines lit on cue | Godot editor reconstruction · source-backed teaching view (component) | Liam |
| B11 | 2:55.2 | 7.40 | run-03 frames 328–549: turn-3 exchange (draw, hurt, flip) | SCRIPTED INPUT … | Liam |
| B12 | 3:02.6 | 16.53 | GodotDevWorkbench: rules.gd 341–346 | Godot editor reconstruction (component) | Liam |
| B13 | 3:19.2 | 8.73 | run-03 frames 550–811: turn 4, defeat card | SCRIPTED INPUT … | Liam |
| **B14** | **3:27.9** | **16.83** | **run-03 frames 1089–1593: win-route turns 3–5, win card** | **SLICE AUDIO — NO NARRATION / music + SFX as recorded, same run** | **game audio only (source_report, preserve)** |
| B15 | 3:44.7 | 16.00 | GodotDevWorkbench: audio_director.gd 105–118 | Godot editor reconstruction (component) | Liam |
| B16 | 4:00.7 | 14.00 | Measurement figure: held 4K frames at HOP/HURT/HIT/WIN + B14 RMS envelope, markers on cue | B14 audio (Movie Maker AVI, same run) · held 4K frames · trigger frames from capture/run-03-inputs.jsonl | Liam |
| B17 | 4:14.7 | 17.43 | ClaudeCodeBeat: verbatim console lines of the isolated-copy test run | Recorded console output · verbatim lines, omissions marked … | Liam |
| B18 | 4:32.2 | 21.07 | Composite: held engine frame 630 (target on occupied square) + quotes, pose pairs, not-reproducible box, next step | Held 4K engine frame (run-03 frame 630) and the actual sprite files · quotes verbatim | Liam |
| B19 | 4:53.2 | 21.80 | FormACard: models, human/AI contributions, source revision | — | Liam |
| BVDT | 5:15.0 | 21.03 | ClaudeVerdictArtifact | — | Liam |
| BHTF | 5:36.1 | 26.80 | ClaudeComposerAsk "Your turn." with the suggested prompt | Reconstructed interface · suggested prompt, not a past run | Liam (signs off) |
| BOUT | 6:02.9 | 5.33 | ClaudeTitleOutro: exact title, @NikBearBrown, slug-seeded mascot, no subline | — | Liam reads title + "At Nik Bear Brown." + 1.0 s silence; no music, no game audio |

Asset trace (requirement 2): B04 design → B05 prompt/settings → B06 raw outputs → B07 choice and edits → B08 cause → B09 in-engine result (plus B03, B11, B13, B14 running).
