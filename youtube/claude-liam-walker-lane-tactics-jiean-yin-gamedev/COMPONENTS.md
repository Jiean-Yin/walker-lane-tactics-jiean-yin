# COMPONENTS — what each part of the slice does, and where the film shows it

Game folder: `godot/` at `film-source-v1` (51 authored files; ledger: [gamedev-evidence.json](gamedev-evidence.json)).

| Component | Files | Data in → what changes → what the player sees/hears | Design choice and one trade-off | Beats |
|---|---|---|---|---|
| Rules engine | `game/rules.gd` | Orders (offsets, target squares) → units' cells and HP, `turn`, `result` → a list of events | Plain data, deterministic, no nodes: testable headless and reusable for the full game. Trade-off: the enemy AI (march / stay when in range) is so simple that a muted player cannot read why it moves (Jiean's playtest) | B12 (code), B13 (result) |
| Scene controller | `game/main.gd`, `game/main.tscn`, `game/draw_layer.gd`, `project.godot` | Key actions → Rules call first → event list played back on the scene's own clock (hop 0.25 s, draw 0.2 s, arrow 0.35 s, …) → board, markers, HUD, cards | Results are decided before playback, so pause, mute and fast tests never change an outcome. Trade-off: board, HUD and markers are code-drawn, so the readability problems (target marker on an occupied square) live in code, not in the generated art | B03, B09, B11, B13, B14 (running); B15 notes |
| Piece display | `game/piece.gd`, 10 `assets/art/archer_*.png` + `.import` | Piece state (idle/draw/hurt/defeat/win) → one static texture, idle scale, `flip_h` by facing, offset from the base disc | One image per state keeps generated art consistent and cheap (5 poses). Trade-off: no in-between frames; the hop is the idle image lifted 16 px in code | B04–B09 (trace), B10 (code), B11 (result) |
| Environment art | `assets/art/env_table.png` + `.import` | Drawn first, scaled to cover 1280 × 720 | A generated table behind a code-drawn board keeps the grid exact. Trade-off: the 1280 × 720 texture is enlarged 3× in a 4K render | B03 onward; B19 credit |
| Audio | `game/audio_director.gd`, `default_bus_layout.tres`, 4 `assets/sfx/*.ogg`, `assets/music/mus_loop.ogg` (+ `.import`) | Rules events (already resolved) → at most one sound per event / shot; WON → music stop then SFX-WIN; LOST → 0.5 s fade; M/N mute buses | Sound never feeds back into state, so a muted run is identical (tested). Trade-off: sound can only confirm, never explain — a muted player loses nothing, but also gains no cue about enemy intent | B14 (heard), B15 (code), B16 (measured) |
| Tests | `tests/test_rules.gd`, `test_audio_events.gd`, `route_runner.gd`, `test_report.gd`, `capture.gd`, `analyze_variants.gd`, `tests/fixtures/*.json` | Headless suites; route fixtures; exhaustive variant search | 51 + 70 checks and a search that changed the design (R1). Limit: synthetic input at 40× speed proves counts and determinism, not feel, fun or readability | B17; B12 (R1); fixtures drive B03–B14 |
| Excluded | `assets/{art,music,sfx}/.gitkeep` | — | Empty folder placeholders | — |

## One complete input → state → output trace (lose route, turn 4)

1. **Input:** Right, Enter (logged frames 564, 591) → `main._confirm_move((1,0))` → `rules.resolve_moves` → event `moved p1`; playback hops it, `audio.on_event` → SFX-HOP (frame 598).
2. **Input:** Enter on the preselected target (frame 662) → `rules.resolve_attacks` → `attack_order` puts e1 first (turn 4 is even) → e1's arrow: `damaged p1 hp 0`, `killed p1`; p1's slot is skipped (line 344).
3. **Output:** draw pose, arrow, defeat pose and SFX-HURT at frame 678; `end_turn` → LOST "shot by the enemy archer in lane 4"; music fades (frame 703) and stops (718). Seen in B13; the code is B12.
