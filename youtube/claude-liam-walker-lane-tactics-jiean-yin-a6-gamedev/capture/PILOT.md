# Pilot capture (driver test only, not film footage)

On 2026-11-08, before the `a6` tag existed, the capture driver was tested on an isolated copy of the then-current commit, `d7845ac` in the pushed history (the branch history was rewritten once before its first push) (`git -c core.autocrlf=false archive`, outside the repository). This was done only to test the driver and to check the approved script's observation sentences against real frames. **No pilot frame is used in the film.** The film's footage is captured again from an isolated copy of tag `a6`.

| Mode | Movie Maker | Engine frames | Master frames | Result |
|---|---|---|---|---|
| `play` | `--fixed-fps 30` | 939 | 844 | pass |
| `slow` | `--fixed-fps 120` | 1476 | 1133 | pass |

Checks that passed:
- `play`: no effect in turns 1–3; turn 4 has 2 bursts and 2 trails, with 2 bursts alive at once; run 1 has 3 bursts; play again leaves no live burst or trail; no skipped draw.
- `slow`: 3 bursts and 3 trails.

## What the pilot frames showed (play, 30 fps)

- **Hit and burst:** the first hit's burst appears on the frame of the `"damaged"` event (master frame 259).
  - The trail stops on that same frame.
  - The red glow, splinters and "−3" are visible at once.
  - The splinters fly mostly sideways.
  - From about +0.3 s, a warm brown haze hangs over the archer.
  - Nothing is visible by about +1.0 s.
- **Two-hit turn:** at the second hit (31 frames, 1.03 s later), the first burst is still alive as a node. On screen it has almost completely faded: at most a faint warm haze shows.
- **The trail:** a row of dots behind the arrow, about 20–25 px apart (1280 × 720 scale). The oldest dots, at the shooter's end, fade first after the landing; faint wisps stay for a few frames.
- **Pause:** P mid-flight freezes the arrow and the trail, and P mid-burst freezes the splinters in mid-air. Both happen under the PAUSED overlay, which dims the board.
- **Slow mode (120 fps):** the dot spacing is the same as at 30 fps, since the GPU particles step at `fixed_fps` 30.
  - In this run the second trail stopped 1 frame (1/120 s) before its impact cue.
  - The first burst was freed 1.275 s after its hit.

## Sentences that did not match the frames (changed with Jiean's OK, "Yes, use them", 2026-11-08)

- B04: "a brown dust puff" → "a haze of brown dust". "inside one board square" → "inside about one board square".
- B08: "The first burst is still fading when the second starts, on the enemy." does not hold on screen. Proposed instead: "When the second hit lands, the first burst has almost faded from sight, but it is still alive."
