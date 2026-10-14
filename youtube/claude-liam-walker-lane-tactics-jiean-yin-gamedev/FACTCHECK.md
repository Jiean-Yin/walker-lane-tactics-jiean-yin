# FACTCHECK — Lane Tactics: From Sketch to Seed to Sound

Every factual claim in the narration or on screen, with its source. Sources are files in this repository at `film-source-v1` (= `fcf33ef`) unless marked *film build* (this film's own capture or re-run, records in `capture/` and `_qc/`).

| Beat | Claim | Source | Status |
|---|---|---|---|
| B00 | Jiean designed Lane Tactics on paper first, then used generative models for art, sound and music; Claude Code built a small Godot slice | README; CHANGE-BRIEF ("design docs committed before any generation", commit `92417a2` precedes `4d5ff51`); SOURCES "Human and AI contributions" | ✓ |
| B00 | The composer prompt is an illustrative reconstruction, not a transcript | labelled on screen; no such prompt exists in the record | ✓ (disclosed) |
| B00 output | 51/51 rules checks, 70/70 sound checks; source film-source-v1 (fcf33ef) | TEST-REPORT §1; `git rev-parse film-source-v1^{commit}` | ✓ |
| B01 | One small playable slice; assets judged in the running game, not a folder | README "What the slice demonstrates"; assignment text in CLAUDE.md | ✓ |
| B02 | Wooden pieces, five-lane board, orders at the same moment, both plans play out, first onto the other's back row wins | CONCEPT.md "The game in two sentences" (excerpt verbatim on screen) | ✓ |
| B02 | Four pillars and one visual/sound choice each | CONCEPT.md "Design pillars" table (card wording shortened, marked on screen) | ✓ |
| B03 | Teal archer faces right, red faces left; plan one step, both move at once, each piece hops | CHARACTER-SHEET "Orientation"; rules.gd `resolve_moves`; capture run-03 frames 150–327 | ✓ observed |
| B04 | Idle pose: ball head, one dot eye, navy hood, teal body, base disc always visible, thick outline | CHARACTER-SHEET consistency rules 1–3, 5 | ✓ |
| B04 | Birch wood on linen is only 1.1 : 1 contrast | CHARACTER-SHEET "Palette" weak spot | ✓ |
| B04 | The sketch is the image the model starts from | gen-log line 18 `init_image: design/character/init/idle.png` | ✓ |
| B05 | SDXL base 1.0, run locally; img2img at strength 0.8; P4; N2; 30 steps; guidance 7; three seeds | gen-log lines 17–19; SOURCES "Common image settings", P3/P4 definitions | ✓ |
| B05 | In the reference runs 0.75 nearly traced the sketch and 0.85 drifted to a front view | SOURCES asset log rows ref03/ref04; TEST-REPORT §8 R2 | ✓ (narration says "in the reference runs") |
| B06 | Claude recommended 202; Jiean chose 211; 212 rejected for long hair and a front-facing face | FRICTIONAL "Poses"; SOURCES CHAR-IDLE row | ✓ |
| B06 | Every seed and hash is logged, so any row can be regenerated | SOURCES ("Reproduce any row with design/tools/gen_images.py …"); TEST-REPORT §10 ("SDXL and MusicGen rows can be reproduced from their seeds") | ✓ as the project claims it; this film did not re-run SDXL |
| B06 | Raw-file hashes match the log | *film build*: `sha256sum` of the three files = gen-log `sha256` (asserted in tools/make_stills.py) | ✓ |
| B07 | rembg u2net cut-out, halo cleanup, scale/anchor, enemy recolour of teal pixels only, each logged with hashes | edit-log.jsonl lines 7, 29, 30; process_sprites.py docstring | ✓ |
| B07 | Panel 2 (commit 4d5ff51) has lost its base disc | `git show 4d5ff51:godot/assets/art/archer_idle.png` (SHA-256 `a00d7b5d…` = edit-log line 7) | ✓ observed |
| B08 | Any pixel brighter than 232 in all three channels becomes transparent | process_sprites.py line 48 `rgb.min(axis=2) > white`, line 100 `default=232` | ✓ |
| B08 | That fixed the reference image's white halo; s211's near-white base was erased by the same line | TEST-REPORT §9 prediction 6, §8 R3; SOURCES CHAR-IDLE edits | ✓ |
| B08 | Fix: walnut disc redrawn behind the piece at the sheet's 40 × 12 | edit-log line 29 ("redrawn base disc behind the piece: walnut #5A3A22 ellipse 40x12 game px with ink outline") | ✓ |
| B09 | Retry brings both archers back in idle; F3 draws slots and base discs | main.gd `_restart`, `_draw_fx` F3 block; run-03 frames 812–967 | ✓ observed |
| B10 | One static image per state; idle image's scale; flip_h for the enemy; position from the base | piece.gd lines 175–185 (verbatim), 9, 15 | ✓ |
| B11 | Turn 3 of the naive route: both step in, player strikes first; draw, arrow, enemy hurt; enemy answers | lose_route.json description; run-03 log frames 385–507 | ✓ observed |
| B12 | Attacks resolve one unit at a time; first side alternates; a unit killed before its turn doesn't fire | rules.gd lines 158–160, 239–268, 341–346 | ✓ |
| B12 | One enemy because an exhaustive search showed two could only be beaten on the tie rule | CHANGE-BRIEF R1 (52 of 45,834 sequences, all turn-7 ties) | ✓ |
| B13 | Turn 4: enemy strikes first, player topples, its own arrow never flies | run-03 log frames 662–703 (one `attack` event, by e1; `killed` p1); defeat card text | ✓ observed |
| B14 | Slice audio is the game's own music + SFX, no narration | *film build*: B14 samples identical to the Movie Maker AVI; `_qc/audio-check-B14.json` | ✓ measured |
| B15 | Rules resolve the turn first, playback feeds events; moved → hop, damage on enemy → hit, on you → hurt, win state → win once; sound decides nothing | audio_director.gd lines 2, 103–118, 166–173; main.gd lines 4–5, 411, 507 | ✓ |
| B16 | Each spike lines up with a logged rules event, in order; win where the music stops | *film build*: `_qc/audio-check-B14.json` (7/7 matched, 1–11 ms), run-03 log | ✓ measured |
| B16 | A fully muted run ends in exactly the same state | test_audio_events.gd checks "muted win route: same result and snapshot as unmuted" (TEST-REPORT §7) | ✓ |
| B17 | Fresh clone: 51/51 and 70/70; the film's build re-ran both on its isolated copy | TEST-REPORT §1; *film build* capture/test_rules.log, test_audio_events.log | ✓ |
| B17 | Every sound fires once per event, held keys add nothing, muted run identical | TEST-REPORT §4, §7 | ✓ |
| B17 | Jiean played it with sound on and fully muted | TEST-REPORT §6 | ✓ |
| B18 | Muted: target unclear on an occupied square; enemy movement unexplained | TEST-REPORT §6 (quotes verbatim on screen) | ✓ |
| B18 | Hurt no squint, defeat dot eye (and navy bow), win arms over the face | TEST-REPORT §2 | ✓ |
| B18 | ElevenLabs sounds can't be regenerated: no seed (and the added game text was not recorded) | SOURCES "Sound effects"; TEST-REPORT §10 | ✓ |
| B18 | Jiean's next step: an enemy that keeps moving toward the end and avoids direct contact, plus a clearer target colour | TEST-REPORT §6 and §10; README Known limitations | ✓ |
| B19 | SDXL (local): every archer pose and the tabletop; rembg cut-outs; ElevenLabs (run by Jiean): four SFX; MusicGen (local): the loop | SOURCES "Generative models" and asset log | ✓ |
| B19 | Jiean chose every accepted image, sound and take and made the scope calls; Claude Code drew sketches, wrote prompts and code, ran models, built this film | SOURCES "Human and AI contributions" (ENV-TABLE s301 was Claude's recommendation that Jiean did not object to — "chose" is the record's own framing of acceptance) | ✓ with that nuance |
| BVDT | Defects and untested items as listed; one human tester (the author); Windows only | TEST-REPORT §6, §10 | ✓ |
| BHTF | Threshold 232 is the current default; 245 is a suggested experiment, not a run | process_sprites.py line 100 | ✓ (suggestion) |

## Corrections made before rendering

1. **piece.gd line numbers.** The first draft cited `piece.gd` lines 405–415; those numbers came from a concatenated listing (`cat -n audio_director.gd piece.gd`). The excerpt is lines **175–185** of `piece.gd`; the pilot render caught it (the code panel was empty) and the sheet, cues and notes were corrected.
2. **Reference-run wording.** "0.75 traced the sketch, 0.85 drifted" happened in the CHAR-REF runs, not the pose runs; B05 now says "in the reference runs".
3. **"Rejected" vs "not chosen".** Seed 202 for idle is not marked rejected in SOURCES; B06 says "Claude's recommendation · not chosen".
