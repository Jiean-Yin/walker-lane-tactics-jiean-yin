# CHANGE-BRIEF — Lane Tactics asset slice

*Version 1, 2026-10-09, before any asset was generated. Results and changes are added as dated revisions at the bottom; predictions are not edited after the fact.*

## What the slice is

One small Godot 4.7.2 scene that proves the art, sound and music work together. It is **not** the full game. It uses a subset of [RULES.md](RULES.md):

| Kept from RULES.md | Simplified for the slice |
|---|---|
| 5 lanes × 8 columns, player on the left | 1 player archer vs 2 enemy archers, no reinforcements, no pool |
| Simultaneous move planning, 1 square in 8 directions or stay | Enemy AI: if the player is in range, stay and shoot it; otherwise step 1 column toward the player's back row in its own lane |
| Archer: HP 4, damage 3, range = the 24 squares of the 5 × 5 around it, cannot target its own square, targets must hold an enemy, never strikes back | No riders or shielders, so no strike back, charge or arrow protection. Enemies stay in their lanes, so at most two pieces ever try to enter one square: a shared square is possible (and an archer cannot shoot its own square), but contested squares cannot occur. |
| Attack order alternates one unit at a time; the side that goes first switches every turn (player first on turn 1) | — |
| A unit killed before its turn does not attack | — |
| Win check at the end of the turn: a piece in the enemy back row; elimination; ties go to the player | Turn limit 20 kept but not expected to matter |

The rules live in one plain-data script (`godot/game/rules.gd`: board, units, orders → list of events), deterministic and tested headlessly, so it can grow into the real engine later.

### Controls (keyboard)

| Key | Action |
|---|---|
| Enter | start; confirm the order; play again |
| Arrow keys / WASD | move the order marker to a neighbouring square (move phase) or cycle the valid targets (attack phase) |
| Space | stay (move phase) or hold fire (attack phase) |
| R | retry from turn 1 |
| P / Esc | pause and unpause |
| M | mute and unmute music |
| N | mute and unmute sound effects |
| F3 | show the footprint slots (debug, display only) |

## Asset list

Generated (**G**), generated then edited (**G+E**), or code-drawn by Claude (**C**, allowed in the game but not counted as generated).

| ID | What | Kind | Panels |
|---|---|---|---|
| CHAR-REF | Archer reference image, side view; every pose derives from it | G | — (sheet check) |
| CHAR-IDLE | Archer idle | G+E (background removal, scale) | 1, 2, 3, 7 |
| CHAR-DRAW | Archer drawing the bow (core action) | G+E | 4 |
| CHAR-HURT | Archer hurt, leaning back | G+E | 5 |
| CHAR-DEFEAT | Archer toppled | G+E | 6 |
| CHAR-WIN | Archer celebrating | G+E | 8, 9 |
| CHAR-HOP, CHAR-RECOVER | optional extra states | G+E | 3, 7 |
| ENEMY-* | each CHAR image recoloured teal → red | G+E (recolour) | 1–8 |
| ENV-TABLE | warm-lit wooden tabletop background around the board | G+E | 1, 2, 6, 7 |
| ENV-LINEN | linen board-square texture (tiled under the code-drawn grid) | G+E (optional) | 2–7 |
| PROP-ARROW | the flying arrow | C (G if time) | 4 |
| UI-* | HUD, markers, cards, text | C | all |
| SFX-HOP | wooden piece landing on a board | G+E (trim) | 3 |
| SFX-HIT | arrow striking a wooden piece (success) | G+E | 4 |
| SFX-HURT | the player's piece is struck, a duller crack (failure) | G+E | 5, 6 |
| SFX-WIN | short bright wooden or plucked flourish (completion) | G+E | 8 |
| MUS-LOOP | calm acoustic loop, cut at a bar boundary | G+E (loop cut) | 1–7 |

## Event-to-sound map

All sounds are triggered by `AudioDirector` from **events the rules engine has already produced**. The engine returns a list of events for each turn; playback walks that list once; each event plays at most one sound. Sound never feeds back into game state, and the engine runs identically with no audio node at all.

| Sound | Exact trigger (event) | Double-trigger guard |
|---|---|---|
| SFX-HOP | `moved` event: a piece's square changed during move playback. One per piece that moved. | Playback staggers landings by 0.12 s so simultaneous hops stay distinct; a piece that stays emits no event; key repeats (`is_echo()`) are ignored, and input is ignored during playback. |
| SFX-HIT | `damaged` event where the target is an **enemy** and the attacker is the player's archer (the arrow lands). | One `damaged` event per attack, even if more pieces share the square (one sound, numbers on each). |
| SFX-HURT | `damaged` event where the target is the **player's** archer. | Same as above. |
| SFX-WIN | the state machine enters `WON` (from the win check). | Only on the transition into `WON`; re-entering the results screen or holding Enter does not re-fire it. |

## Music behaviour

| Situation | MUS-LOOP |
|---|---|
| Title and play | loops continuously (OGG loop flag; cut at a bar boundary) |
| Pause | ducks by 12 dB; returns to full on unpause |
| Defeat | fades out over 0.5 s; silent on the defeat card |
| Win | stops at once; SFX-WIN plays alone; silent on the results card |
| Retry / play again | restarts from the beginning |
| M | mutes and unmutes the Music bus only; N does the same for the SFX bus |

## Predicted failure cases and how I will check them

1. **Generated poses drift from the reference** (head size, height or base disc change; an outline missing).
   *Check:* scale every accepted image to 1× and overlay it on the turnaround's height bar and base disc; compare it with consistency rules 1–7; record the decision in the asset log.
2. **The piece disappears against the generated background** (birch head vs linen is only 1.1 : 1).
   *Check:* an in-engine screenshot at 1× in colour and in greyscale with every state on the board; if it fails, darken or desaturate ENV-TABLE or the squares rather than change the piece.
3. **A sound fires twice for one event** (for example two pieces landing at once, a held Enter, or SFX-WIN on re-entry).
   *Check:* an automated test plays a scripted turn sequence (including rapid repeats and held input) with a counting audio sink and asserts sounds == events for each type.
4. **The music loop clicks or gaps at the seam.**
   *Check:* listen to at least 3 repetitions in the running game; an automated check compares the waveform at the loop end against the start (no jump larger than a small threshold).
5. **The slice is unreadable when muted** (a hit or win carried only by sound).
   *Check:* a muted human playtest: every sound event also has a visual (hop motion, pose change, "-3", HP pips, result card).
6. **Background removal leaves halos, or the model draws a fake checkerboard.**
   *Check:* prompt for a solid flat background; inspect the edges on both the light board and the dark table at 1×.
7. **The recolour also shifts wood and skin tones.**
   *Check:* recolour only the teal hue range, and compare the enemy beside the player at 1×.

## Revisions

### R1 — 2026-10-12: one enemy instead of two (evidence: exhaustive search, not play)

- **Observation:** with the setup above (1 player archer vs 2 marching enemy archers, HP 4, damage 3), the scripted search over every player order for 20 turns found **no win except the "ties go to the player" rule**: 52 of 45,834 order sequences win, all on a turn-7 tie where both sides reach the other's back row. The naive plan (walk forward in lane 5 and shoot) also wins on that tie. A slice that can only be won through a tie rule does not show the storyboard's win, and it gives no real decision.
- **Variants tried** (`godot/tests/analyze_variants.gd`; table in `evidence/analyze_variants-1791859618.json`): HP 6 or enemy damage 2 change nothing (two hits still kill); HP 7 lets the naive plan win; a guarding second enemy lets waiting until turn 20 win on a 1-vs-1 tie (about 90 % of sequences); two guards let the naive plan win outright. Counting only units with a target in the attack order makes the slice unwinnable.
- **Change (accepted by Jiean):** the slice uses **one marching enemy archer in lane 4** (HP 4, damage 3). Of 259,043 order sequences, 16,577 win (6.4 %), almost all by elimination, the earliest on turn 5. Both naive plans lose. Every win needs one timing decision: take the first exchange on a turn when the enemy strikes first, then finish it on the next turn, when you strike first (pillar 2, *Plans collide*).
- **Rule clarified in RULES.md:** a unit with no valid target keeps its place in the attack order and skips its attack (Jiean accepted this reading).
- **Effect on the design:** storyboard panels 1, 2, 6 and 7 show two enemies; the slice shows one. TEST-REPORT lists this difference. The two-enemy setup is kept as a config option (`TWO_ENEMY_UNITS`) for later.
- **Still to check by playing:** whether a one-enemy duel is fun, not only winnable.

### R2 — 2026-10-12: generation tools changed (no free access to the planned web tools)

- **Observation:** the planned tools were not usable for free: Adobe Firefly (art) was not available to Jiean, and Suno and ElevenLabs Music produced takes that the free plans would not let Jiean download.
- **Change:** art from **Stable Diffusion XL base 1.0 run locally**; music from **MusicGen small run locally**; sound effects stayed with **ElevenLabs** (run by Jiean). Local models record a seed for every output, so these assets are more reproducible than the web tools would have been.
- **Pose method:** each pose is generated image-to-image from the character sheet's pose sketch (strength 0.80), with the same prompt and settings as the accepted reference. IP-Adapter (conditioning on the reference image itself) was considered but not used, to avoid another 3 GB download tonight.
- The asset IDs, event-to-sound map and music behaviour above are unchanged. Results: TEST-REPORT.md.

---

# Assignment 3 — three 3D assets (Blender with Claude through the MCP)

*Version 1, 2026-10-15 18:20, committed before any asset was built. Results and corrections go in dated revisions at the bottom of this section; these predictions are not edited after the fact.*

**Who decided what:** Claude Code proposed every number below as a numbered default, from CHARACTER-SHEET.md (proportions, palette) and CONCEPT.md (pieces, linen board, back row). Jiean accepted all seven defaults without changes. At commit time the Learn-the-window session was under way and BLENDER-NOTES.md was not written yet.

**Why these three:** Lane Tactics is 2D today, so these assets live in a small Godot 3D "tabletop diorama" scene (floor, one light, a camera) that later assignments reuse. They are the three things that scene needs: a piece, the square it stands on, and the goal it walks toward.

## Scale

**1 board square = 1.00 m.** In Blender 1 unit = 1 m and Godot's 3D unit is also 1 m, so nothing is converted. The 2D slice puts two pieces in one square (left and right footprint slots, each half a square), so a piece's base must fit in half a square: at most 0.50 m wide.

Blender is Z-up; Godot is Y-up. The glTF exporter's **+Y Up** option (on by default) converts this. Blender's "height" (Z) should arrive as Godot's Y.

## The assets

| | A. Archer piece | B. Linen board square | C. Back-row goal flag |
|---|---|---|---|
| **Name / file** | `archer_piece` | `board_square` | `goal_flag` |
| **What it is in the game** | The unit: the carved wooden archer from the 2D slice, in player teal | The tile the 5-lane board is made of | Marks the back row you must reach to win |
| **Where it appears** | Standing on a board square, up to two per square | Tiled 5 lanes × N rows to make the board | One at each end of the enemy's back row, just outside lanes 1 and 5 |
| **Size W × D × H (m)** | **0.40 × 0.40 × 0.80** | **1.00 × 1.00 × 0.05** | **0.45 × 0.30 × 1.20** |
| **Size justified by** | Base 0.40 m fits a half-square slot (0.50 m) with a margin. Height 0.80 m = 2 × base, close to the sheet's ~3.5 heads with a 0.22 m head | Exactly one square. 5 cm thick, so it reads as a game board and not a floor | Taller than the piece (1.20 m vs 0.80 m), so it can be seen over the pieces in the back row. Base 0.30 m stays inside the gap beside the board |
| **Origin** | Centre of the underside, at Blender's world origin (0, 0, 0) | Centre of the underside, at the world origin | Centre of the underside of the base disc (the pole stands on it; the flag sticks out toward +X, so the box is off centre in X) |
| **Why that origin** | Godot places a node at its origin, so a piece placed at a square's centre at y = 0 stands on the board, not half inside it | Tiles sit on the table at y = 0 and pieces stand on top at y = 0.05 | Stands on the table at y = 0 |
| **Basic shapes (≤ 6)** | 6: base disc (cylinder), body (cylinder), head (sphere), hood (cone), bow (thin cube, on the +X facing side), eye (small cube, on the +X side of the head) | 5: slab (cube) + 4 border strips (cubes) | 3: base disc (cylinder), pole (cylinder), flag (thin cube) |
| **Look: what makes it recognisable** | Ball head under a dark hood, straight cylinder body, wide disc base, a bow on the facing side: a chess-like toy piece | A flat light square with a slightly darker edge, so a grid of them shows the squares | A thin pole with a red flag on top |
| **Flat colours** | Body teal `#1F6F78`; hood `#24323F`; head birch `#E2B887`; base and bow walnut `#5A3A22`; eye ink `#1B1410` | Slab linen `#D8C7A0`; border linen `#CDB98E` | Base and pole walnut `#5A3A22`; flag enemy red `#B23A2E` |
| **Triangle budget** | **400** | **100** | **150** |
| **Why that budget** | Cylinders at 12 segments (≈ 44 tris each), sphere at 12 × 6 (≈ 120), cone at 12 (≈ 22), two cubes (24): about 254. 400 leaves room if a curve looks too faceted. A default UV sphere (32 × 16, ≈ 960 tris) alone would break the course limit of 500 | 5 cubes × 12 = 60 | Base disc 12 segments (≈ 44), pole 8 segments (≈ 28), flag cube 12: about 84 |

Materials: one flat Principled BSDF per colour, base colour set on the shader node (not only the viewport colour), no textures.

Each asset is built in its own Blender file (`blender/<name>.blend`) around the world origin, with the code Claude runs saved in `tools/blender/build_<name>.py`, and exported to `godot/assets/models/<name>.glb`.

## Predicted failure cases and how I will check them

1. **An asset arrives lying on its side in Godot** (Z-up vs Y-up, or a rotation that was not applied).
   *Check:* the headless Godot script prints each asset's bounding box; the largest-height axis must be **Y**, and the Y size must match H above. Also look at it in the 3D scene.
2. **Scale is not applied, so the node scale is not 1 or the size is wrong** (for example by a factor of 2 if Claude scales the default 2 m cube, or by 10 or 100 from a unit mix-up).
   *Check:* Blender's sidebar (N) shows scale 1, 1, 1 and dimensions = brief; the headless script prints node scale (1, 1, 1) and a bounding box within ±0.01 m of the brief.
3. **The origin is in the middle, so the asset floats or sinks.**
   *Check:* the headless script prints the bounding box's lowest Y, which must be 0.00 (±0.005 m); in the scene, each asset placed at y = 0 must sit on the floor, seen from the side at floor level.
4. **Claude builds more than asked** (default segment counts, extra bevels or extra shapes) **and breaks the budget.**
   *Check:* Blender's Scene Statistics (status bar) per file: triangles ≤ budget, and the object count ≤ the shapes listed above.
5. **A colour does not survive the export** (only the viewport colour is set, or materials are merged).
   *Check:* the headless script prints each mesh surface's material albedo; compare with the hex codes above. Look at the assets under the scene's light.
6. **The MCP fails part-way** (socket drops, or Blender stops responding during a call).
   *Check:* every call's result is read; get_scene_info after each step; any error is copied word for word into FRICTIONAL.md.

## Revisions

### A3-R1 — 2026-10-15: board_square border darkened, #CDB98E → #9A7F55 (evidence: `look`, before export)

- **Observation:** built exactly as above, the border `#CDB98E` against the slab `#D8C7A0` has a contrast ratio of only **1.15 : 1**. In Blender's `look` (material shading) one square read as a flat sheet, and a temporary 3 × 3 tiled preview showed only faint grooves between squares. Prediction 5 was about colours lost in export; this is a different colour problem: the colour survived, but it was the wrong choice.
- **Options compared by Claude** (contrast vs slab / vs table `#6B4A2E` / vs walnut base `#5A3A22`): `#B39B6E` 1.61 / 2.96 / 3.80; **`#9A7F55` 2.27 / 2.10 / 2.69**; `#85693F` 3.08 / 1.55 / 1.98; walnut 6.11 / 1.28 / 1.00.
- **Change (chosen by Jiean):** border **`#9A7F55`** ("stitch brown"), the only option that keeps all three ratios above ~2: squares separate, the board edge still shows against the table, and piece bases stay distinct from the grid lines. Re-checked with the same tiled preview: the grid now reads clearly.
- **Unchanged:** size 1.00 × 1.00 × 0.05 m, origin, 60 triangles, the slab colour.
