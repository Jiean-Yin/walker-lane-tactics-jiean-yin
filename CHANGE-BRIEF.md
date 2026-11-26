# CHANGE-BRIEF — Assignment 7: two animations

*Version 1, 2026-11-25. Committed before the first setup prompt. Results and corrections go in dated revisions at the bottom; this version is not edited afterwards. The Assignment 6 brief is kept at tag `a6` (`git show a6:CHANGE-BRIEF.md`).*

**Who wrote what:**
- **Jiean:** chose the two clips, the loop/commit split, the found sheet, the reference video, and its five event frames. Jiean also wrote the cycle's frame rate, the recovery split, every prediction, every "should show", and the seven answers (2026-11-25).
- **Claude Code:** drafted the wording, filled in the project facts (file and line references), measured the sheet and the art, and proposed the rig's parts, the key directions, the flag's place and the drift fix (marked "accepted"). Jiean accepted all of them on 2026-11-25.

**Engine:** Godot **4.7.2** standard (`README.md:11`), Compatibility renderer (`godot/project.godot:25`). 2D, 1280 × 720 viewport, no camera (`main.gd:18`). Godot 4 class and property names only.

## 1. The two clips

| | Clip 1: `wave` (the cycle) | Clip 2: `shoot` (the committing action) |
|---|---|---|
| What it communicates | **Where the goal is.** A red flag waving beside the enemy back row, the row the player wins by reaching (`main.gd:767`, red tint `:638-639`). Today the goal is only a faint red tint on the squares. | **Who is shooting, and when.** The archer draws, looses and follows through, so a shot reads as a body action and not only as a pose swap. Today `draw` is one still image for 0.8 s (`piece.gd:5`, `:82-88`). |
| Why the player needs it | The A2 playtest found new players unsure what they were aiming for. A moving flag pulls the eye to the goal from the title onwards. | Two shots in one turn are 1.05 s apart (`main.gd:29-33`, `:474`). A visible wind-up and release shows which archer fires before the arrow appears. |
| Object it plays on | A new prop, `GoalFlag`, on the table right of the enemy back row (column 7, `rules.gd:20`), beside lane 3. | Both archers. Each `piece.gd` instance gets its own rig and its own `AnimationPlayer`. |
| Route | **Sprite2D with an AnimationPlayer frame track.** The sheet is sliced with `hframes` / `vframes`, and the clip keys `frame`. Why: it is the preferred route, and the AnimationPlayer read-back sees it. | **Cutout rig keyed as resource text.** Plain `Node2D` pivots with `Sprite2D` parts cut from the existing draw art by `region_rect`, keyed on `rotation` and `position`. Why: the game is 2D, and the art is single images, not a skeleton. No `Bone2D`. |
| Authority | The flag's own `AnimationPlayer` (`autoplay = "wave"`). It reads nothing from the game. Nothing else writes `FlagSprite.frame` or `FlagSprite.offset`. | The rig's `AnimationPlayer`, started and advanced only by `piece.gd`. `set_state("draw")` plays `shoot` from 0, and `tick(dt)` advances it by game time. `piece.gd` reads its own `state`, which `main.gd`'s cue list sets (`main.gd:486`, `:519`). |
| Cycle or committing | Cycle (loops) | Committing action (startup, active, recovery) |

## 2. The sheet (Clip 1)

| | |
|---|---|
| Source | "Flag Animation Sheet", https://opengameart.org/content/flag-animation-sheet |
| Author, licence, date checked | Fokko; **CC0**; checked 2026-11-25 (`godot/assets/art/flag/ATTRIBUTION.md`) |
| Original file as downloaded | `godot/assets/art/flag/flag_red.png`, 500 × 249, SHA-256 `bbe98fe4…a5c4`, committed unchanged |
| Cell size | **125 × 249 px** |
| Grid | `hframes = 4`, `vframes = 1` (4 cells, frames 0–3) |
| Frame order for `wave` | **0, 1, 2, 3**, left to right, then back to 0 |
| Registration (measured) | The pole's left edge sits at x = 4, 8, 6, 3 inside cells 0–3, so it drifts by up to 5 px (`ATTRIBUTION.md`). **Fix (accepted):** a second discrete track in `wave`, keying `FlagSprite:offset.x` = 0, −4, −2, +1 (source px) on the same times as the frames, so the pole stands still. It is the same `AnimationPlayer`, so there is still one authority. The sheet is never edited. |
| On screen (accepted) | `FlagSprite` scale 0.36, so the flag stands about 90 px tall, a little taller than an archer (80 px, `piece.gd:9`). Pole foot on the table at about x 1176, the bottom of lane 3 (board origin and square size: `main.gd:19-20`). Final place confirmed by eye. |

## 3. The cycle spec (`wave`)

| | |
|---|---|
| Frame count | 4 |
| Frame rate | **8 fps** |
| `Animation.step` | one frame period at that rate: **0.125** |
| Length | 4 key intervals: **0.5** |
| Loop mode | `Animation.LOOP_LINEAR` |
| Track types | value track `FlagSprite:frame`, `UPDATE_DISCRETE`; value track `FlagSprite:offset`, `UPDATE_DISCRETE` |
| Clock | `callback_mode_process = ANIMATION_CALLBACK_MODE_PROCESS_IDLE` (process tick, real time; the flag keeps waving while the game is paused, because wind isn't part of the game) |
| **Seam rule (frame track)** | No duplicate frame across the wrap: there is no key at `length`, and the last key is frame 3, not 0. The gap from the last key (3 intervals) to `length` (4 intervals) equals one key interval. |

## 4. The phase table (`shoot`)

**Frame rate: 60 fps. `Animation.step` = 1/60 s.** The game's attack timings are fixed and out of scope (`main.gd:29-33`), so each phase's length comes from them. The reference only decides how motion is spaced inside a phase.

| Phase | Begins on frame | Frames | What the player may do | What the game reads |
|---|---|---|---|---|
| Startup | **0** (`_cue_draw`, `main.gd:470`, `:486`) | **12** (`DRAW_LEAD` 0.2 s) | P/Esc pauses (`main.gd:251-253`), R restarts (`:262-264`), M/N mute, F3 debug, V vsync. Enter, arrows, WASD and Space do nothing; each adds 1 to `ignored_inputs` (`:289-290`). | `piece.state == "draw"`; `_arrows` is empty |
| Active | **12** (`_cue_arrow`, `:471`, `:490-495`) | **21** (`ARROW_TIME` 0.35 s) | the same | `_arrows` is non-empty: the arrow is in flight and the A6 trail follows it. The arrow leaves `_arrows` 0–2 frames before frame 33 (A6 brief, revision 1, item 3). |
| Recovery | **33** (`_cue_impact`, `:472`, `:498-513`) | **15** (`ATTACK_RECOVER` 0.25 s) | the same | The impact on frame 33: HP pips, hurt pose, hit burst. On frame **48**, `_cue_attacker_idle` sets the attacker back to `idle` (`:473`, `:516-519`), which ends the clip. |

Clip length 48 frames = 0.8 s, `loop_mode = Animation.LOOP_NONE`.

**Reference (Jiean's measurements).** "Archery in slow motion S01E010 BONUS: Ki Bo Bae (Coach Cam)", World Archery, https://youtu.be/9o0g6FQPhts, 25 fps. The clip is slow motion by an unknown factor, so it gives **proportions only**. It is used under YouTube's standard licence: measured, never committed or shown in the film.

| Event | Video frame |
|---|---|
| Draw starts | f747 |
| Full draw (string hand at the face) | f809 |
| Release (string leaves the fingers) | f1202 |
| Follow-through ends (arms stop) | f1275 |
| Bow starts to drop in its sling | f1285 |
| Last usable frame (the shot fades to a title card at about f1390; she never reaches rest on camera) | f1385 |

| Reference stretch | Video frames | Gap | Game phase |
|---|---|---|---|
| Draw | f747 → f809 | 62 | Startup, frames 0–12, one stretch |
| Hold | f809 → f1202 | 393 | **skipped** (the game has no hold) |
| Release and follow-through | f1202 → f1275 | 73 | Active, frames 12–33, one stretch |
| Follow-through hold | f1275 → f1285 | 10 | Recovery, first part |
| Bow drop | f1285 → f1385 | 100 | Recovery, second part |
| Back to idle | (not on camera) | — | frame 48: `piece.gd` swaps to the idle art |

**Recovery split** (the one boundary inside a phase): the bow drop begins on frame **40**.

Frame 40 is **chosen by eye, not from the reference ratio**: it gives a 7-frame hold (33→40) and an 8-frame drop (40→48). The reference's 10 : 100 split would put the drop almost straight after the impact.

**Keys, one at every boundary** (Claude writes them in Step 4, with a table pairing each key time with its frame). The rig and the key directions below were **proposed by Claude and accepted by Jiean** (2026-11-25). They are in the art's own pixels and degrees; facing is handled above the rig.

| Frame | `Rig:position` | `Rig/Upper:rotation` | `Rig/Upper/Bow:rotation` | Transition into the next key |
|---|---|---|---|---|
| 0 | rest (0, 0) | 0° | bow 12° below level | ease in, accelerating towards the release |
| 12 | rest | leaning back 4° | level | ease out, fast at the release, slowing through the follow-through |
| 33 | recoiled 6 px backwards | 2° forward | level | hold (same values) |
| bow-drop frame | same as 33 | same as 33 | level | ease in-out |
| 48 | rest | 0° | bow tipped 20° forward and down | — |

**Rig (accepted).** A new scene `godot/game/archer_rig.tscn`, instanced by `piece.gd`:
- `Mount` (`Node2D`): written only by `piece.gd`, for placement, scale, facing flip and visibility.
- `Mount/Rig` (`Node2D`): keyed `position`.
  - `Rig/Lower` (`Sprite2D`): region (0, 196, 288, 125), legs and base. Not keyed.
  - `Rig/Upper` (`Node2D`): pivot at the belt (144, 200), keyed `rotation`.
    - `Upper/UpperSprite` (`Sprite2D`): region (0, 0, 204, 204), head, body, arms and quiver.
    - `Upper/Bow` (`Node2D`): pivot at the bow hand (236, 120), keyed `rotation`.
      - `Bow/BowSprite` (`Sprite2D`): region (204, 40, 84, 164).
- `AnimationPlayer`: `root_node` = `Mount`, library holding `shoot`.

The regions and pivots are measured on `archer_draw.png` (288 × 321). `archer_draw_enemy.png` has the same silhouette (alpha map compared, no difference), so both teams use the same regions. `piece.gd` sets each part's texture to the team's draw image. It also gives each part **its own piece's** existing `ShaderMaterial`, so the A5 tint carries over (it is never shared between pieces, R6, `piece.gd:56-59`).

The rig is visible only in `draw`. In every other pose, `piece.gd` shows the existing single `_sprite` as today.

## 5. The state machine

The player's state machine is `main.gd`'s `State` (`main.gd:13`) with its cue list (`:181-196`). The archer's pose machine is `piece.gd`'s `state` (`piece.gd:15`, `:82-88`), set only by `main.gd`'s cues. No `AnimationTree` is used. A constant table in `piece.gd` names the clip each pose plays:

| Pose state | Clip it plays | Entered by (condition) |
|---|---|---|
| `draw` | `shoot`, from 0 | `_cue_draw` at the attack's start (`main.gd:470`, `:486`) |
| `idle` | none (rig hidden, `AnimationPlayer` stopped) | `_cue_attacker_idle` at +0.8 s, only if still `draw` (`:473`, `:516-519`); also the hurt/recover timers (`piece.gd:134-141`) |
| `hurt`, `defeat`, `win`, `hop`, `recover` | none | `main.gd:511`, `:513`, `:551`; `piece.gd:115-116`; `main.gd:331` |
| (flag, not a pose) | `wave`, always (autoplay) | scene load |

**Transitions out of `draw`:**
- `draw` → `idle` on frame 48. This is the only way the clip ends in play.
- R frees the piece in `draw` (`main.gd:262-264`, `:336-340`), and its rig goes with it.
- P freezes it: game time stops, so `tick` doesn't advance the clip (`main.gd:166-170`).
- Gameplay keys are ignored (`main.gd:289-290`).

## 6. The two clocks

| Clip | `callback_mode_process` | Advances on | Driven by |
|---|---|---|---|
| `shoot` (each archer) | `ANIMATION_CALLBACK_MODE_PROCESS_MANUAL` | process tick, **game time**: `piece.tick(dt)` calls `advance(dt)` inside `main._process`, after `_run_cues()` (`main.gd:162-171`). It stops while paused and scales with `time_scale` (`main.gd:73`, `:77`). | `piece.gd` |
| `wave` (flag) | `ANIMATION_CALLBACK_MODE_PROCESS_IDLE` | process tick, real time | its own `AnimationPlayer` |

- **No `AnimatedSprite2D`** is used. (If one were, it would advance on the process tick with no callback-mode setting.)
- **Keyed gameplay facts: none.** Neither clip keys anything the game reads. The active window is `_arrows`, written by the cue list in `main._process` on the process tick (`main.gd:168`, `:193-196`). The game has no `_physics_process` (searched `godot/**/*.gd`).
- No method tracks.

## 7. Boundaries

**Unchanged:**
- collision (there is none), movement, input (no new key);
- the state machine and every timing constant in `main.gd`, and `rules.gd`;
- every existing test and its count (`evidence/a7/baseline/`):
  - `test_rules` 51, `test_audio_events` 70, `check_assets` 38;
  - `test_exposed_tint` 46 at 30/60/144, `test_materials` 148;
  - `test_hit_burst_config` 107, `test_arrow_trail_config` 135;
  - `test_hit_burst_state` 31, `test_arrow_trail_state` 31, `cost_effects` 25;
- `godot/shaders/` (hand-written, never edited by an agent);
- the A6 effects and their drivers;
- every A2/A3/A5 asset file, including the archer art, which the rig only crops by `region_rect`;
- `flag_red.png` as downloaded.

**Changes, named:**
- `piece.gd` gains the rig: it instances it, shows it in `draw` and starts and advances its clip.
- `main.tscn` gains the `GoalFlag` node.

Clips live as resources in `godot/animations/` (`shoot.tres`, `wave.tres`), never built in code at runtime. Presentation code may read game state; it never writes it.

## 8. Evidence split

| Rule | Checked by | How |
|---|---|---|
| Sheet slicing, frame range, discrete updates, `wave` key times, step, `LOOP_LINEAR`, the seam rule | read-back | `test_flag_readback.gd` at 60: `track_problems()`, every frame key < `hframes × vframes`, both tracks `UPDATE_DISCRETE`, keys at the cycle spec's times within half a step, no key at `length`, last key → `length` = one interval |
| Every `shoot` track resolves; keys at frames 0 / 12 / 33 / bow-drop / 48 within half a frame; step 1/60; `LOOP_NONE`; `MANUAL` | read-back | `test_shoot_readback.gd` at 60. The discrete-update check applies **only to the frame track**: `shoot`'s value tracks are continuous by design. |
| Today's behaviour: state order, pose order, attack timings 12 / 21 / 15, the `_arrows` window, ignored inputs | pins | `test_pins_a7.gd` at 60, committed before wiring, re-run after. **Predicted change: none.** The clips are presentation only. |
| `draw` plays `shoot` from 0; other poses play nothing; the flag plays `wave`; every requested clip exists | structure test | `test_anim_states.gd` at 60: the pose → clip table against the `AnimationPlayer` (`has_animation`, `current_animation`), driven by real keys through `Input.parse_input_event` |
| Interrupts at frames 0, 12, 33, 48 (one frame before, on, after) | edge tests | `test_shoot_edges.gd` at 60, with three interrupts:<br>• **P:** `current_animation_position` doesn't move while paused, and resumes on unpause.<br>• **R:** the old piece is freed, and the new piece shows no clip.<br>• **Enter:** `ignored_inputs` + 1, and the clip runs on unchanged. |
| The motion reads; phases distinct | frame strip (fixture) + **eyes** | Movie Maker strip (section 9); Jiean in play, many shots |
| The flag wraps cleanly, the pole doesn't drift, and it reads on the table | **eyes** | Jiean: five or more wraps at normal speed; the registration strip; the darkest and lightest table under the flag |
| The rig over the light square and next to the dark table | **eyes** | Jiean: the player's start square touches the table (A6 brief §1) |

## 9. The frame strip

- **Preview:** `godot/previews/shoot_preview.tscn`. The background is the real board from `main.tscn` after the game has started (PLAN_MOVE, turn 1), with both archers on their start squares, as in A6. The flag is on screen too.
- **Trigger:** frame 10. The preview sets the player archer to `draw`, as `_cue_draw` does, and sets it back to `idle` 0.8 s later, as `_cue_attacker_idle` does. No real arrow is drawn, so these are **fixture captures**.

**Frames to read** (at 30 fps; the frame = 10 + phase-table frame × 30 / 60):

| Strip frame | Phase-table frame | Boundary |
|---|---|---|
| 10 | 0 | trigger, startup begins |
| 16 | 12 | active opens (release) |
| 26 and 27 | 33 | the impact falls between them (16.5 frames after the trigger) |
| **30** | bow-drop frame | the recovery split |
| 34 | 48 | back to idle |

What each should show: **Startup, the archer's body starts to lean back and bow points front-up. Trigger, the bows start moving back as well. Release, arrow moves front and appears unclear. A pop at the swap  to idle on frame 34. Bow drops down slowly a small angle about 10, then switch back to idle.**

**Capture command** (Jiean runs it):

```bash
mkdir -p captures/shoot/r0
"$GODOT" --path godot res://previews/shoot_preview.tscn --write-movie "$PWD/captures/shoot/r0/frame.png" --fixed-fps 30 --quit-after 60
```

## 10. Predicted failures

1. Frame 33 can't be keyed — keys snap to 30 fps, so a step at 1/30 gets caught by the step and key-time assertions.

2. Two writers on the rig — piece.gd sets Rig.scale for facing while the clip keys Rig.position, caught by the one-authority rule (facing lives on Mount) and the structure test.

3. Clip not stopped on R or idle — a stale pose carries into the next draw, caught by the R edge test and current_animation.

## 11. Answers (Jiean)

1. Which route does each clip use, and what does that route's read-back see that the other route's does not? **Both AnimationPlayer routes. Both run track_problems(). Flag sees discrete mode + frame keys; rig sees continuous tracks on pivot nodes. Neither sees SpriteFrames.**
2. If your frame track is left on continuous updates, what does the sprite show between two keys, and why? **Round to whole wrong cells, never blended. frame is an integer, so continuous updates round it and show whole cells. At the wrap it sweeps back through 3, 2, 1, 0.**
3. What will `Animation.step` be, and what happens to your key times if you leave it at its default? **Step = 1/60 for shoot, 1/8 for wave. Default 1/30 snaps both: frame 33 falls between steps for shoot, and wave's 0.125 s keys don't divide evenly into 1/30, so they snap too.**
4. Which node is the one authority over each animated node, and what else in your project could write to it? **The AnimationPlayer (for Rig, Upper, Bow, FlagSprite). Second writer: piece.gd (_sprite.position, texture), a test/preview script, or editor keying.**
5. Which tick does each clip advance on, and which tick does gameplay read the active-window fact on? If they differ, what is the largest disagreement in seconds? **Both clips advance on the process tick — shoot because piece.tick calls it from inside main._process, and wave through its own player in IDLE mode. Gameplay reads _arrows on the process tick too; there is no physics tick. Inside main._process, cues run first and piece.tick runs after them (main.gd:168-170), so on the frame _cue_draw starts the clip, tick advances it by that same frame's time — putting the clip level with or one frame ahead of the cue clock, not behind. Largest disagreement: at most one frame (1/60 s ≈ 0.017 s); the exact number gets measured in the "Two clocks" check.**
6. For your cycle: what is the seam rule for its track type, and what would a duplicated frame at the wrap look like in play? **No duplicated frame at the wrap. A duplicate holds one cell for two intervals once per loop (0.25s, two frame periods) — a visible hitch on a flag.**
7. If your rig is imported: where does loop mode have to live so that a reimport keeps it, and how will you prove it survived an empty import cache? **Keyed rig: loop mode lives in the resource text (not imported). If imported: in the .import per-animation settings. Prove via mutation 4 (delete godot/.godot, --import, read-back); keyed rig survives.**

## Revisions
