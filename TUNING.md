# TUNING — Assignment 6 particle effects

One entry per tuning revision, oldest first, in the format the assignment gives. Every strip is a **fixture capture** from a preview scene (`godot/previews/`), rendered with Movie Maker at 30 fps by Jiean. Claude's reading of a strip is a claim; Jiean's verdict in the running game decides.

- **"What I saw"** and **"My verdict"**: Jiean's words only.
- **Claude's reading, prediction and comparison**: copied from the session record.
- **The change**: approved by Jiean before it was made.

Effect A strip frames: 10, 12, 15, 20, 30, 50 (trigger at 10); retrigger capture also 42, 44, 47.
Effect B strip frames: 10, 13, 16, 21, 26, 31, 42 (arrow launched at 10, lands at 21).

## Effect A: first look (strip r0, before any revision)

What I saw (running game, 1280 × 720): I can see a clear hitten effect that looks like being hitten by a rock, accompanied by spreading dust that are clearly visible and vanish in a short time that can be captured by eyes. (Jiean)


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
Claude's comparison of r1 with its prediction (from `captures/hit_burst/r1/sheet_player_2x.png` next to r0's):
- **frame 10:** matches; identical to r0.
- **frame 12:** **does not match.** I predicted "still clearly red". Only a faint orange-red glow shows around the edges of the dark splinter cluster. In r0 there was none, so the change is real but small.
- **frame 15:** **partly matches.** A faint pink halo on both sides of the torso, weaker than the "about half strength" I predicted.
- **frame 20:** no red visible. I predicted a faint pink haze; close enough.
- **frames 30 and 50, and all splinters and dust:** match; pixel-for-pixel the same shapes as r0.
- **Why it is weaker than predicted:** `Flash` is the first child of `HitBurst`, so `Splinters` (opaque dark brown) and `Dust` are drawn **on top** of it. From frame 11 the splinter cluster covers the centre of the soft dot, where its alpha is highest, and the dust greys what is left. My prediction used the flash's own alpha and ignored what is drawn over it.
- **Possible next steps if you want the flash to read:** move `Flash` after `Dust` in the scene, so it draws on top; or make it larger or lighter. Each is one change, to judge separately.
My verdict (running game, 1280 × 720): Jiean: "I still cannot see the red flash clearly. Make it much larger than right now and last 3 times longer than the current status." (Recorded as **kept**: the next changes build on 0.36 s. Claude split Jiean's two requests into r2, size, and r3, length, so that each revision changes one setting.)
Strips: captures/hit_burst/r0/, captures/hit_burst/r1/
Commits: `83bd6ba` (prediction), `8aa178c` (change), `6f2263f` (strip r1 and comparison)

## 2026-11-08 -- Effect A, revision r2

What I saw (running game, 1280 × 720): see r1's verdict ("I still cannot see the red flash clearly. Make it much larger …").
Claude's reading of r1: see r1's comparison (the flash is only faintly visible after frame 10, because the splinters and dust draw over it).
Change: `Flash.scale_amount_min` / `_max` 1.25 / 1.25 → 3.0 / 3.0 (one setting, the flash's size), requested by Jiean. `Flash.lifetime` stays 0.36 until r3.
Claude's prediction for r2 (written before the edit). The flash quad goes from 40 px to 96 px at birth and grows to about 154 px by the end of its life (curve 1.0 → 1.6):
- **frame 10:** a large red glow, about 60–70 px of clearly red core, covering the archer's chest, head and arms and spilling onto the board on both sides;
- **frame 12:** a red glow about 100 px across around the dark splinter cluster, clearly visible beyond the splinters;
- **frame 15:** a pink-red halo about 120 px across at about half strength, reaching past the edges of the square;
- **frame 20:** a faint pink haze over most of the square;
- **frames 30 and 50:** unchanged;
- **Splinters and Dust:** unchanged.

Also predicted: on the red enemy the flash now spills onto the board around it, so it reads there by its edge rather than over the tunic. Risk: for 2–4 frames it hides the archer's face.
Claude's comparison of r2 with its prediction: TO FILL (after the recapture)
My verdict (running game, 1280 × 720): TO FILL (Jiean) kept | reverted, because …
> *Hint (Claude):* is the hit now obvious without staring? Is the red disc too big for an 80 px archer, and does hiding the archer for a moment bother you?
Strips: captures/hit_burst/r1/, captures/hit_burst/r2/
Commits:

## Effect B: first look (strip r0, before any revision)

What I saw (running game, 1280 × 720): A continous black closely dotted lines into the target square. Clear. (Jiean)

### Claude's reading of r0 (fixture; read after Jiean's first look, from `captures/arrow_trail/r0/sheet_path_2x.png`)

| Frame | Intent (brief §2) | What the strip shows |
|---|---|---|
| 10 (launch) | the streak starts at the bow | the arrow is not visible yet at the bow in this crop, and there is no trail yet |
| 13 | the streak follows the tip | the arrow is a third of the way along; **one** dark dot is left near the bow |
| 16 (steady) | a dark streak drawing the arc | the arrow is two-thirds of the way; behind it **3–4 separate dots, about 20–25 px apart**, each about 6 px. It is a dotted line, not a streak |
| 21 (landing) | emission stops; the streak shrinks away | the arrow has gone; **8–9 dots trace the whole arc** from the bow to the target, the older ones smaller and fainter. It reads clearly as the path, as dots |
| 26 | the streak gone within 0.3 s; wisps drift | the streak dots are mostly gone; 4–5 pale blobs (wisps) about 15–20 px, very faint |
| 31 | wisps curling and fading | the wisps are barely visible; no visible curl at this size and alpha |
| 42 | nothing | nothing left |

Summary of the claim:
- **Predicted failure 8 happened, as Jiean also saw:** one emission step per frame at 30 fps leaves one dot per step. The arrow moves about 20–25 px per frame, so the dots sit 20–25 px apart.
- **Path and timing match the intent:** the trail starts at launch, stops at landing, is gone by +0.7 s, and the arrow stays readable in front of it.
- **The wisps barely show:** `#9A8466` at alpha 0.45 over the beige board is low contrast, so the turbulence isn't visible.

