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
