# TUNING — Assignment 6 particle effects

One entry per tuning revision, oldest first, in the format the assignment gives. Every strip is a **fixture capture** from a preview scene (`godot/previews/`), rendered with Movie Maker at 30 fps by Jiean. Claude's reading of a strip is a claim; Jiean's verdict in the running game decides.

- **"What I saw"** and **"My verdict"**: Jiean's words only.
- **Claude's reading, prediction and comparison**: copied from the session record.
- **The change**: approved by Jiean before it was made.

Effect A strip frames: 10, 12, 15, 20, 30, 50 (trigger at 10); retrigger capture also 42, 44, 47.
Effect B strip frames: 10, 13, 16, 21, 26, 31, 42 (arrow launched at 10, lands at 21).

## Effect A: first look (strip r0, before any revision)

What I saw (running game, 1280 × 720): I can see a clear hitten effect that looks like being hitten by a rock, accompanied by spreading dust that are clearly visible and vanish in a short time that can be captured by eyes.


### Claude's reading of r0 (fixture; read after Jiean's first look, from `captures/hit_burst/r0/sheet_player_2x.png` and `r0_retrigger/sheet_enemy_2x.png`)

Distances are screen pixels, estimated from the 2× crops; the archer is 80 px tall.

| Frame | Intent (brief §1) | What the strip shows |
|---|---|---|
| 9 (control) | nothing | nothing: no early burst |
| 10 (trigger) | red flash over the torso, strongest | **matches in timing**: the red flash appears on exactly frame 10 (no off-by-one). It is about 30 px across, smaller than the 40 px planned, because the soft dot fades towards its edge. A faint grey dust smear is already over the torso. |
| 12 (+0.07 s) | flash fading, splinters leaving | flash no longer visible; dark-brown splinters in a tight cluster around the chest, about 20–25 px out. The splinters' red phase (first 20% of 0.45 s) is already over. |
| 15 (+0.17 s) | flash gone, splinters at their widest | splinters as short dark streaks, 40–60 px to both sides at chest height. Most fly **sideways**; only one or two go above the head. They point along their motion and show no visible spin. |
| 20 (+0.33 s) | splinters falling and darkening | splinters thinner and fainter, 55–65 px out, a few dropping towards the base. A faint brown haze around the upper body. |
| 30 (+0.67 s) | only dust, larger and thinner | only a faint brown halo, about 50 px, mostly behind the bow on the left. It reads as a soft shadow more than dust. |
| 50 (+1.33 s) | nothing | nothing left. |
| 42 retrigger, player | what is left of burst 1 | nothing visible (frame 38 still shows a faint halo). So the two bursts overlap as nodes (dust lives up to 1.2 s), but **not visibly** at 1.07 s. |
| 42 / 44 / 47, enemy | flash, then splinters | **the red flash is weak on the enemy**: `#E0453A` over the red tunic `#B23A2E` and the red-tinted back column has little value contrast; it shows mainly over the face. Splinters (44, 47) read well, as on the player. |

Summary of the claim:
- **Timing and scale match the intent.** The whole burst stays inside about one board square, and in this strip it never reaches the table.
- **Weak points:**
  1. the flash nearly disappears on the red enemy;
  2. the dust starts on frame 10 with the flash, drawn over the archer, so it greys the body instead of reading as a separate puff afterwards;
  3. the splinters spray out more than up.

## 2026-11-08 -- Effect A, revision r1

What I saw (running game, 1280 × 720): Jiean: "Let the red flash last longer, at least 3 times as long as now. I can barely realize it happens."
Claude's reading of r0: see "Claude's reading of r0" above (flash visible on frames 10–11 only, about 30 px; weak on the red enemy).
Change: `Flash.lifetime` 0.12 → 0.36 s (3×, the minimum Jiean asked for), requested by Jiean. Nothing else changes; the config test's expected value follows.
Claude's prediction for r1 (written before the edit). The flash alpha falls linearly from 0.9 to 0, and its scale grows from 1.0 to 1.6 over 0.36 s instead of 0.12 s:
- **frame 10:** unchanged, the same 30 px red dot at full strength;
- **frame 12** (+0.07 s, 19% of its life): still clearly red, alpha ≈ 0.73, about 10% larger, instead of gone;
- **frame 15** (+0.17 s, 46%): red still visible at about half strength, ≈ 1.3× the frame-10 size. The splinters are drawn on top of it (they come after `Flash` in the tree);
- **frame 20** (+0.33 s, 93%): almost gone, a faint pink haze;
- **frames 30 and 50:** unchanged from r0;
- **Splinters and Dust** are pixel-identical to r0 in every frame (same fixed seeds, separate emitters).

Not fixed by this change: the flash is still `#E0453A` on the red enemy, so it stays weak there (frames 42–44).
Claude's comparison of r1 with its prediction: TO FILL (after the recapture)
My verdict (running game, 1280 × 720): TO FILL (Jiean) kept | reverted, because …
> *Hint (Claude):* say whether the flash now registers as a hit without staring, whether 0.36 s now feels too long next to the splinters, and how it looks on the enemy.
Strips: captures/hit_burst/r0/, captures/hit_burst/r1/
Commits:

## Effect B: first look (strip r0, before any revision)

What I saw (running game, 1280 × 720): TO FILL (Jiean)

> *Hint (Claude):* say whether you see a continuous line or dots, how long the trail is compared with the shot, whether the wisps curl visibly, and whether the trail is gone before the next arrow.
