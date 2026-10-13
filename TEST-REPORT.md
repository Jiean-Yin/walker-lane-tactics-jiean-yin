# TEST-REPORT — Lane Tactics asset slice

| | |
|---|---|
| Source revision tested | `12f7283` (all generated assets in place) |
| Engine | Godot 4.7.2.stable.official.ed1daf0bf, standard build, Compatibility renderer |
| OS | Windows 11 Home 10.0.26200 |
| Testers | Jiean Yin (human playtest, sound on and muted); automated suites and scripted captures run by Claude Code |
| Date | 2026-10-12 / 13 |

## 1. Startup and controls (fresh copy)

A fresh `git clone` of GitHub `main` at `12f7283` into an empty folder, then:

```bash
<Godot console exe> --headless --path godot --import
<Godot console exe> --headless --path godot --script res://tests/test_rules.gd
<Godot console exe> --headless --path godot --script res://tests/test_audio_events.gd
<Godot console exe> --headless --path godot --quit-after 300
```

| Check | Result |
|---|---|
| Import | no errors |
| test_rules | **51/51** ([evidence/fresh-clone-test_rules-1791864624.json](evidence/fresh-clone-test_rules-1791864624.json)) |
| test_audio_events | **70/70** ([evidence/fresh-clone-test_audio_events-1791864624.json](evidence/fresh-clone-test_audio_events-1791864624.json)) |
| Main scene, 300 frames headless | runs; at the forced quit Godot prints `ERROR: 2 resources still in use at exit`, an engine shutdown warning with no gameplay effect (not investigated further) |
| Used assets present | 16 files: 10 archer sprites + `env_table.png`, 4 SFX OGG, `mus_loop.ogg` |
| Controls | Jiean played with Enter, arrows/WASD, Space, R, P/Esc, M, N and F3 (section 6): "All fine". Every state change is also driven by the scripted input in test_audio_events and capture.gd |

## 2. Character against the sheet

![character vs sheet](evidence/compare/character-vs-sheet.png)

Left: the character-sheet design sketch. Middle: the generated sprite after the logged edits. Right: the same state cropped from an in-engine screenshot (`evidence/screens-1791864538/`, scripted input).

| State | Matches the sheet | Mismatch |
|---|---|---|
| idle | proportions, one eye, navy hood, teal body, base disc | the base disc is redrawn by hand (the model painted it near-white and the halo cleanup erased it; see R3) |
| draw | bow arm forward, arrow nocked, base | — |
| hurt | leans back away from the attacker | the eye is open; the sheet's hurt pose has a squint |
| defeat | toppled, bow beside it | the eye is a dot, not the sheet's ✕; the bow came out navy, not walnut |
| win | arms and bow overhead | the arms cover the face; this comes from the sketch, not the model |
| **Orientation** | the player faces right; the enemy is the same image flipped to face left; the enemy's hurt pose leans away from the player | — |
| **Collision** (F3, [03-footprint-debug-f3.png](evidence/screens-1791864538/03-footprint-debug-f3.png)) | the art is anchored on the base-disc centre in the 64 × 96 slot | the bow in draw and the toppled body in defeat reach beyond the slot. As the sheet states, rules resolve per square, so this never changes a result |

## 3. Storyboard against the slice

Each pair is in `evidence/compare/storyboard-*.png` (left: design sketch; right: engine screenshot from scripted input).

| Panel | Slice screenshot | Differences and why |
|---|---|---|
| P1 Title (design view, eye level) | [01-title](evidence/compare/storyboard-01-title.png) | The slice shows a text card over the board, not pieces lined up at eye level. The game camera has no eye-level view; the title art stays a design view |
| P2 Board at start | [02-board-start](evidence/compare/storyboard-02-board-start.png) | **One enemy, not two** (CHANGE-BRIEF R1). Lane numbers, the who-strikes-first line and mute status were added to the HUD |
| P3 Move | [05-move-playback-hop](evidence/compare/storyboard-03-move.png) | The hop uses the idle image lifted in code (no CHAR-HOP generated, as the brief allowed). The planned-move marker is in [12-plan-move-marker-lose](evidence/screens-1791864538/12-plan-move-marker-lose.png) |
| P4 Hit | [09-attack-hit-enemy-hurt](evidence/compare/storyboard-04-hit.png) | As designed: marked target square, arrow, enemy hurt pose, "-3" |
| P5 Being hit (design view, low angle) | [08-player-hurt](evidence/compare/storyboard-05-hurt.png) | The slice shows the same moment from the fixed high angle (hurt pose, "-3", HP pips). The low angle is not a game camera |
| P6 Defeat | [14-defeat-card](evidence/compare/storyboard-06-defeat.png) | As designed: toppled piece, cause named on the card. One enemy |
| P7 Retry | [15-retry-board](evidence/compare/storyboard-07-retry.png) | The piece returns in the idle pose (no CHAR-RECOVER generated); the retry counter is in the HUD |
| P8 Win (design view, Dutch angle) | [10-win-card](evidence/compare/storyboard-08-win.png) | The slice is level (no Dutch tilt), as the storyboard said. The win shown is "ENEMY DEFEATED" (elimination); "BACK ROW REACHED" also exists in code but the capture route wins by elimination |
| P9 Results | [11-results-victory](evidence/compare/storyboard-09-results.png) | As designed |

Not covered by the slice: the eye-level title art (P1), the low-angle (P5) and Dutch-angle (P8) design views, and the second enemy in P1, P2, P6 and P7.

## 4. Sound events

| Event | Sound | Automated: triggers = events | Human (Jiean) |
|---|---|---|---|
| a piece lands in a new square | SFX-HOP | win route 5 = 5 moved events, lose route 7 = 7 | Part A: "All fine" |
| the player's arrow damages the enemy | SFX-HIT | 2 = 2 / 1 = 1 | " |
| the player is damaged | SFX-HURT | 1 = 1 / 2 = 2 | " |
| entering WON | SFX-WIN | 1 on the win route, 0 on the lose route | " |

Rapid repeats and held input: the scripted runs send held (echo) Enter and repeated presses during playback. They add no events and no sounds (test_audio_events). The sounds are generated files loaded from `godot/assets/sfx` (new check: "all four generated SFX and the music loop are loaded").

## 5. Music

| Check | Evidence | Result |
|---|---|---|
| Loop seam | `process_audio.py`: 8 bars at 79.8 bpm, 40 ms crossfade, sample jump at the wrap 0.0016 (below the clip's typical step) | pass |
| Seam by ear, 3+ repetitions (about 75 s on the title) | Jiean, Part A | "All fine" |
| Pause ducks, unpause restores; defeat fades out; win stops before SFX-WIN; retry restarts | test_audio_events music checks (flags read from the AudioDirector) | pass |
| M mutes music only, N mutes effects only | test_audio_events (buses) + Jiean | pass / "All fine" |

## 6. Human playtest — Jiean Yin, 2026-10-13

**Checklist played** (given by Claude): Part A with sound on: the title music over 3 loops; a loss and a win played as a new player would; P, R, M, N, F3. Part B, all muted: one more game.

**Jiean's report (verbatim):**

> All fine. For part B, I found it not clear if the attack target is on the character's board. We need to change at least the color later for clear viewing. And the enemy's moving logic seems weird, a new player cannot understand why enemy move or not. I will suggest making some easy logic first like "enemy try keep moving to the end and may avoid direct contact with the opponent". For now, we keep that only for testing art and sound.

**What this means for the predictions:** prediction 5 (the slice is unreadable when muted) **partly happened**. The sounds were not the problem. Without sound, the target marker on an occupied square and the enemy's reason for moving or stopping are not readable. Both are recorded as known limitations (section 10). The art-and-sound purpose of the slice was judged fine.

## 7. Automated checks added by this project

| Suite | Command | What it proves | Result |
|---|---|---|---|
| `tests/test_rules.gd` | see section 1 | setup, legal moves, 24-square range, friendly fire, alternating attack order, killed-before-turn, attack cancelled, every win and loss condition, determinism, V4 default; the win route is not a tie | 51/51 |
| `tests/test_audio_events.gd` | see section 1 | the full scene driven by synthetic key presses on the win and lose routes: sounds == events for each id, echo/rapid input adds nothing, the muted run ends in an identical rules snapshot, music behaviour, all assets loaded | 70/70 |
| `tests/analyze_variants.gd` | `--script res://tests/analyze_variants.gd` | exhaustive search over every player order for rule variants (used for R1) | [evidence/analyze_variants-1791859618.json](evidence/analyze_variants-1791859618.json) |
| `tests/capture.gd` | windowed exe `--script res://tests/capture.gd` | 15 engine screenshots from scripted input | [evidence/screens-1791864538/](evidence/screens-1791864538/) |

No assertion was removed or loosened. One label was corrected: the check named "no sound files present" became "every logged trigger's file flag matches whether its stream is loaded". The label had become false once real files existed; the logic was always the flag check. A stricter check was added beside it.

## 8. Inspect-and-revise cycles

| # | Observation (evidence) | Change | Result |
|---|---|---|---|
| R1 | The exhaustive search found 1 vs 2 archers winnable only through the tie rule (`analyze_variants`) | one marching enemy (CHANGE-BRIEF R1, accepted by Jiean) | winnable without a tie; both naive plans lose |
| R2 | CHAR-REF ref01 came out photo-real 3D on grey; ref02 cartoon humans with legs (`assets/rejected/CHAR-REF-ref01/02`) | prompt rewritten to lead with "2D game sprite on a plain white background"; then image-to-image from the sheet's idle sketch with a strength sweep 0.75 → 0.85 → 0.80 | 0.75 too close to the sketch, 0.85 drifted from the sheet; 0.80 accepted (s202) |
| R3 | The idle s211 cut-out lost its base disc: the model painted it near-white and the halo cleanup removed it (`assets/_raw` check sheet; rule 1 "base disc always visible") | first a fill inside the outline (left a gap, rejected), then a base disc redrawn behind the piece at the sheet's 40 × 12 size, logged in edit-log | base visible in game ([character-vs-sheet](evidence/compare/character-vs-sheet.png), idle row) |
| R4 | Every pose prompt was 78–81 CLIP tokens, so SDXL would cut off "painted wood grain texture", the phrase that made s202 read as wood | shortened only the pose phrases; the piece description stays word-for-word | all prompts ≤ 77 tokens |
| R5 | Muted playtest: target marker and enemy logic unclear (section 6) | **not changed in this slice** (Jiean's decision); planned next | — |

## 9. Predictions (CHANGE-BRIEF) against results

| # | Prediction | What happened |
|---|---|---|
| 1 | Poses drift from the reference | **Happened:** with the same seed, draw and hurt lost the navy hood (s202 turned teal), and two seeds grew long hair. Caught by the sheet check, and those seeds were rejected |
| 2 | Piece disappears against the background | **Did not happen:** all states read at 80 px on linen and table (comparison sheets); the dark outline carries the birch head as the sheet required |
| 3 | A sound fires twice | **Did not happen:** counts equal events, including held and rapid input |
| 4 | Music loop clicks | **Did not happen:** seam metric pass; Jiean heard no problem |
| 5 | Unreadable when muted | **Partly happened:** see section 6 |
| 6 | Background-removal halos | **Happened:** a white halo under the base of CHAR-REF s202 and s203. The cleanup step (near-white → transparent) removed it, but it also erased idle s211's near-white base (R3) |
| 7 | Recolour shifts wood and skin | **Did not happen:** only the teal hue range changed; the navy hood and the wood are unchanged |

## 10. Known limitations and uncertainty

- **Muted readability:** the red target marker is hard to see on a square that holds a piece; the enemy's reason for moving or stopping is not shown (Jiean's playtest). Next step proposed by Jiean: a simpler enemy that keeps moving toward the end and avoids direct contact.
- **Pose mismatches:** hurt has no squint; defeat has a dot eye and a navy bow; the arms cover the face in win.
- **One enemy, not two;** P1/P5/P8 design views are not game cameras.
- **Reproducibility:** the SDXL and MusicGen rows can be reproduced from their seeds. The ElevenLabs sounds cannot (no seed, and the exact added game description was not recorded).
- **One human tester** (the author); no new-player evidence. Tested on Windows only.
- The engine's `2 resources still in use at exit` warning on forced quit was not investigated.
