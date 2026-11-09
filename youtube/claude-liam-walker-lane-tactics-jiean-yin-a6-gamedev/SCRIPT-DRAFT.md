# SCRIPT DRAFT — "Lane Tactics: A Hit Burst and an Arrow Trail"

Assignment 6 film, Brutalist `godot-gamedev walker`. Liam (in for Bear), Kokoro `am_onyx`, 4K landscape, 30 fps, no captions. **Drafted by Claude from Jiean's own documents** (CHANGE-BRIEF with Revision 1, TUNING, TEST-REPORT "Assignment 6", FRICTIONAL "Assignment 6", README "Assignment 6"). **Status: approved by Jiean on 2026-11-08, as is** ("Approve as is"; every point below kept at its default). Narration is generated only after the capture, once the bracketed quotes are filled from tag `a6` and any changed observation sentence has been shown to Jiean. Source shown: **tag `a6`** (commit hash recorded at capture), filmed on an isolated copy. About 10 minutes.

**Footage:**
- **Game shots** are real engine output from Godot Movie Maker on an isolated copy of tag `a6`, as in the A5 film: `main.tscn` unchanged, rendered at 3840 × 2160, key presses scripted (the win route the state tests play) and labelled so. Every frame's state is logged.
- **Slow replays** (B04, B12): the same moment captured at 120 fps and played at 30, labelled "¼ SPEED".
- **Strips** are Jiean's own Movie Maker captures from `captures/`, shown as **fixtures** (preview scenes, fixed seed), never as gameplay.
- **Test and price results** are recorded logs from `evidence/a6/`, shown as output cards or rebuilt charts with their source named.
- **Human checks** are quoted in Jiean's words, never acted out.

Each code beat is followed directly by the result it produces (code → result). Line numbers below were checked against the working copy; the capture re-checks them against the tag.

**Observation sentences** in result beats ("the splinters fly mostly sideways") are written from the strips and logs. After the capture, Claude checks each one against the actual footage. Any sentence that has to change comes back to Jiean before narration is generated.

**Placeholders.** Lines in `[square brackets]` quote documents that are still `TO FILL`. They are filled verbatim from tag `a6` and shown to Jiean before narration.

---

## B00 ASK — Claude composer (label "Illustrative reconstruction of the Claude interface — not a transcript")
**Greeting:** "Hello, Liam" (as in the earlier Lane Tactics films).
**Prompt typed:** "Please use Walker to convert my game design document about Lane Tactics — archers on a five-lane board, simultaneous orders, win by reaching the enemy's back row — into two particle effects: a hit burst that shows which archer an arrow hit, and a trail that shows who shot whom. Test both, price both, and show me what a headless run cannot."
**Result lines:** `test_hit_burst_config 107/107 · test_arrow_trail_config 135/135` · `test_hit_burst_state 31/31 · test_arrow_trail_state 31/31 at 60 fps` · `Source shown: tag a6`

> Hello, this is Liam, in for Bear. Jiean Yin's game is Lane Tactics: archers on a five-lane board, where you win by reaching the enemy's back row. This assignment adds particle effects: a burst where an arrow hits, and a trail behind the arrow in flight. The prompt on screen is an illustrative reconstruction.

## B01 BLUF — hesitant writer
**Typed:** "Two particle effects for Lane Tactics: / a burst where the arrow lands, / a trail behind it in flight. / The tests decide how they look." → "The tests decide" corrects to **"Jiean's eyes decide"**.

> Two particle effects: a burst that marks the hit, and a trail that shows the shot. The tests guard every setting. How they look was decided by Jiean's eyes, one revision at a time.

## B02 SETUP — card
**Card** (from CHANGE-BRIEF §1–2):
- **Effect A, hit burst.** Job: "An arrow hit an archer, and which one." Fires on an event: every `"damaged"` event. Node: `CPUParticles2D`.
- **Effect B, arrow trail.** Job: "Who shot whom, and along which path." Runs while a condition holds: an arrow in flight (`main._arrows` not empty). Node: `GPUParticles2D`.
- Renderer: **Compatibility** · 1280 × 720 · archer 80 px tall.

> Each effect has one job. Effect A: an arrow hit an archer, and which one. It fires on an event, every damaged event. Effect B: who shot whom, and along which path. It runs while a condition holds, an arrow in flight. One is a CPU particle node, one a GPU node. And the game runs on Godot's Compatibility renderer. That matters later.

## B03 CODE — `godot/effects/hit_burst.tscn` lines 89–105 (Godot editor reconstruction; highlights 91, 96, 98, 102–105)
**Side panel:** `HitBurst` (Node2D, z 2) → `Flash` 1 · `Splinters` 14 · `Dust` 8 = 23 particles per burst.

> Effect A is one scene: a root and three CPU particle nodes, Flash, Splinters and Dust. Here are the splinters. Line ninety-one: saved not emitting, so nothing fires when a scene loads. Fourteen, born all at once. Up to seventy-five degrees either side of straight up, at one hundred forty to two hundred sixty pixels a second, and gravity pulls them back down. Line ninety-eight: local coords off, so each splinter stays where it was born.

## B04 RESULT — first hit of turn 4, real speed, then ¼-speed replay (labels "SCRIPTED KEY PRESSES · REAL GODOT RENDER · main.tscn @ a6"; replay "¼ SPEED · captured at 120 fps")

> In the real game, keys pressed by a script. The enemy's arrow lands on the player's archer. Now at a quarter speed: a red glow over the body, splinters thrown out and falling, a haze of brown dust, and after about a second, nothing. The whole burst stays inside about one board square.

## B05 CODE — `godot/game/hit_burst_driver.gd` lines 34–49 (highlights 37, 44–45, 49)
**Side panel, one input → state → output trace:** Enter confirms → the turn's attacks play → `_cue_impact` appends `"damaged"` to `played_events` (`main.gd:502`) → `HitBurstDriver` reads it the same frame (`process_priority` 10) → a burst at the archer.

> Nothing in this game sends a signal. So the driver runs every frame, right after the game's own update, and reads the list of events the game has played. Line forty-four: every new damaged event gets a burst. Line forty-nine: every emitter's speed scale is the game's speed, and zero while it's paused. The driver reads the game. It never writes it.

## B06 RESULT — a hit, then P pressed mid-burst (same label, plus "P pressed at frame N")

> The burst appears on the frame the arrow lands. Press P in the middle of it: the game's own pause. The pieces hold, and so does every splinter, in mid-air. Unpause, and it carries on from where it stopped. The game never pauses its scene tree. A speed scale of zero does it.

## B07 CODE — `godot/game/hit_burst_driver.gd` lines 71–85 (highlights 75, 77, 79, 84)

> Spawning. Line seventy-five: a new instance for every hit. That's the retrigger rule Jiean chose, overlap: an earlier burst keeps playing. Line seventy-seven: at the archer's base, plus forty pixels up, the body. Line seventy-nine: when the dust, the longest emitter, reports finished, the burst frees itself. And it's a child of the driver, never of the archer.

## B08 RESULT — the two-hit turn, both archers in frame (same label)
**On screen:** the state test's own line, `A3 overlap: … 2 bursts alive` (`evidence/a6/final/test_hit_burst_state_60fps.log`).

> Turn four: both archers hit, about a second apart. When the second hit lands, the first burst has almost faded from sight, but it is still alive. Two bursts alive at once, and the state test counted exactly that: two, on the frame of the second hit. The brief predicted that re-firing a single node would drop the second hit. A new instance per hit avoids it.

## B09 CODE — `godot/effects/hit_burst.tscn` lines 60–66 (highlight 64)
**Side panel** "TUNING.md · one setting per revision": r1 `lifetime` 0.12 → 0.36 · r2 `scale_amount_min` / `_max` 1.25 → 3.0 (lines 83–84) · r3 `lifetime` 0.36 → 1.08.

> The flash wasn't planned like this. The brief gave it point one two seconds. Jiean watched it in the game and wrote: I can barely realize it happens. So it was tuned, one setting per revision, with Claude's prediction written down before each edit. Lifetime, then size, then lifetime again. Line sixty-four now says one point oh eight seconds.

## B10 RESULT — strips r0, r1, r2, r3 × frames 10, 12, 15, 20, 30 (label "FIXTURE · hit_burst_preview.tscn · fixed seed · Jiean's Movie Maker captures, 30 fps")
**On screen, verbatim:** Jiean's request after r1, "I still cannot see the red flash clearly. Make it much larger than right now and last 3 times longer than the current status." · Jiean's verdict on r2 and r3, "r2's shining color contradict more to the background color, and r3's enlarging makes unit easier to be seen."

> Jiean's strips, with the same fixed seed in every row. Revision one, three times longer, and frame twelve barely changed. Claude had predicted "still clearly red", and was wrong. The flash is the first child, so the splinters and the dust are drawn on top of it. Revision two, about two and a half times larger, gets out from under them. Revision three keeps the glow for about a second. Jiean kept both.

## B11 CODE — `godot/effects/arrow_trail.tscn` lines 87–101 (highlights 87, 95, 98, 99)
**Side panel**, measured before the brief (CHANGE-BRIEF §0): `trail_enabled = true` → nothing drawn, and `WARNING: The Compatibility renderer does not support particle trails.`

> Effect B is two GPU particle nodes, Streak and Wisps. Godot has a trail setting, and on the Compatibility renderer it draws nothing at all, with a warning. That was measured before the brief was written. So line ninety-nine keeps it off, and line ninety-eight does the work: local coords off. The node follows the arrow, and every particle stays where it was dropped.

## B12 RESULT — an arrow in flight, real speed, then ¼-speed replay (labels as B04)
**On screen, verbatim:** Jiean's first look, "A continous black closely dotted lines into the target square. Clear."

> The arrow flies two squares, and the streak draws its arc behind it. Look closely: it's a row of dots, about twenty to twenty-five pixels apart. Line ninety-five: the GPU node steps thirty times a second, and each step leaves one dot. The brief predicted this failure. Jiean looked, and called the path clear.

## B13 CODE — `godot/game/arrow_trail_driver.gd` lines 60–79 (highlights 69, 71–74, 77–79)

> The trail's driver keeps one entry per arrow. While the arrow is in the game's list, the trail moves to its tip, with the game's own arc formula: line sixty-nine. On the frame the arrow leaves the list, both emitters stop, line seventy-four, and a countdown starts: the wisps' lifetime, seven tenths of a second of game time. Then the node is freed. A new arrow gets a new trail.

## B14 RESULT — a landing, then a later shot with P pressed mid-flight (same label)

> The arrow lands. Emission stops, the dots shrink away from the oldest end, a few wisps hang on, and the burst takes over at the target. Pause in mid-flight, and the arrow and its trail freeze together. Unpause, and both carry on. The test found one surprise in this hand-over. We'll get to it.

## B15 CODE — `godot/effects/arrow_trail.tscn` lines 64–83 (highlights 66–67, 73–74, 79, 82–83)
**Side panel** "TUNING.md · Effect B r1, Jiean's choice of two options": `Gradient_wisps` (line 59) `#9A8466` α 0.45 → `#6E5A44` α 0.7.

> The wisps carry the feature the CPU node doesn't have: turbulence, line seventy-nine. Each wisp gets an influence between point one and point two, so it drifts in a noise field, while damping slows it down. After the first strip, Jiean chose stronger wisps: the colour ramp went from a pale brown at forty-five percent to the streak's own colour at seventy.

## B16 RESULT — strips r0 (top) and r1 (bottom) at frames 16, 21, 26, 31, with Claude's pixel count beside them (label "FIXTURE · arrow_trail_preview.tscn · seed 71 · Jiean's Movie Maker captures, 30 fps")
**On screen:** pixels darker in r1: 403 · 1004 · 1264 · 1087 (frames 16, 21, 26, 31; TUNING.md) · Jiean's verdict, verbatim: [TUNING.md, Effect B r1, "My verdict"].

> Revision zero above, revision one below, same seed. In flight, almost no difference: each wisp hides behind the streak dot it was born with. After the landing, at frames twenty-six and thirty-one, the puffs stay visible along the arc, where before they had nearly gone. The curl of the turbulence doesn't show in stills. Jiean's verdict: [verdict, in Jiean's words].

## B17 CODE — `godot/tests/test_hit_burst_config.gd` lines 127–140 (highlights 135, 140)

> Now the tests. The configuration tests load each scene and read every value back against the brief: one hundred seven checks for the burst, one hundred thirty-five for the trail. This part reads the scene as plain text, line by line, looking for Godot three names, like initial velocity without its min. Why read the text? Because an old name might load without a word.

## B18 RESULT — headless output card (label "HEADLESS CHECK OUTPUT · recorded reports, no rendering")
**On screen**, from `evidence/a6/mutations/`:
- Mutation 1: `FAIL  no Godot 3 / editor-only names in the scene text (failure 2)  (["line 104: initial_velocity = 140.0"])` · `FAIL  Splinters.initial_velocity_min == 140.0  (0.0)` · 105/107, exit 1.
- Mutation 2, `spread` 75 → 60: 106/107, exit 1.
- Jiean in the running game, mutation 1: "Does not seem to have any other problem, but the red flash seemed to fade earlier."

> Jiean tested the tests. Mutation one: write initial velocity, the Godot three name, on the splinters. The scene loaded with no error and no warning, and the value read back as zero. Two checks failed: the text scan and the read-back. In the game, Jiean saw almost nothing wrong, only a flash that seemed to fade earlier. That's why it needs a test. Mutation two: one value changed, exactly one check failed.

## B19 CODE — `godot/tests/test_arrow_trail_state.gd` lines 561–570 (highlights 568–570)

> The state tests play the game with real key presses at sixty frames a second, and check every frame against the rules. This check compares each trail's stop with the hit it leads to. The brief said: within one frame. The agent's first run measured zero, minus two, zero, zero, minus two. Up to two frames early.

## B20 RESULT — headless output card (same label)
**On screen:** first run, `FAIL  B2: each stop is within one frame of the impact (stop row - damaged row in -1..1)  ([0, -2, 0, 0, -2])` · 30/31 (`evidence/a6/step5b/`) → CHANGE-BRIEF Revision 1, item 3 → bound −2..0 → **31/31** (`evidence/a6/final/`). Beside it: what no headless run can show.

> The agent didn't widen the bound to make it pass. It left the check failing, and reported it. The brief was wrong, so the brief was corrected first, in a dated revision, and only then the test: thirty-one of thirty-one. Why two frames? The arrow's clock and the hit cue advance in different places. Game timing was out of scope, so that stays open. And no headless run draws a single particle.

## B21 CODE — `godot/tests/cost_effects.gd` lines 76–86 (highlights 77, 82, 83)

> The price, first without a screen. The agent's script times each frame from a node that runs last, line seventy-seven. Six hundred frames, twice, for each case: an empty scene, the game with no effects, two bursts alive the whole time, and two trails in flight. It reports the means, and leaves the verdict to the reader.

## B22 RESULT — rebuilt chart of the recorded log (label "RECORDED LOG · evidence/a6/step7 · chart redrawn from it")
**On screen:** mean frame time above the control: Effect A ×2 **+0.0078 ms**, Effect B ×2 **+0.0066 ms** · Jiean's predictions 0.015 and 0 ms · budget 0.2 ms.

> Above the control: about eight thousandths of a millisecond for the bursts, and almost seven for the trails. Jiean had predicted zero for the GPU trail. It isn't free on the CPU: the node still moves every frame, and headless it costs about as much as the CPU burst. Both are far under the budget of point two milliseconds.

## B23 CODE — `godot/previews/price_effects.gd` lines 112–123 (highlights 115, 120–123)

> For the graphics card, a fixture holds each case at its peak. Line one fifteen reads the viewport's measured GPU time every frame, and once a second it prints the mean. Jiean read the Visual Profiler in the editor. Claude ran the same fixture unattended, each case held twice, with and without vsync.

## B24 RESULT — rebuilt chart: Jiean's Visual Profiler ranges beside the means (labels "HUMAN CHECK · Jiean, Visual Profiler" and "RECORDED LOGS · evidence/a6/gpu")
**On screen:** Jiean's ranges overlap in all three cases (vsync on 4–6.5 ms; vsync off 0–1.5 ms) · means with vsync off: off 0.1058, A ×2 0.1089 (**+0.0031**), B ×2 0.1132 (**+0.0074**) · FPS with vsync on: 180 in every case · Jiean's conclusion: [TEST-REPORT A6.6, "Jiean's conclusion"].

> Jiean's readings: the three cases overlap completely. The graph swings by about one and a half milliseconds, and the effects cost a few thousandths. Only the means separate them: three thousandths of a millisecond for the bursts, seven for the trails. Under budget, and two to three times Jiean's predictions. With vsync on, every case reads one hundred eighty frames a second, as Jiean predicted. [Jiean's conclusion, if filled.]

## B25 CODE — `godot/shaders/particles_generated.gdshader`, lines from Jiean's A6.7 table (label "Generated by the Godot editor from the Wisps material, saved by Jiean, unedited · not used by the game")
**Excerpt:** one short range chosen from the lines Jiean enters in TEST-REPORT A6.7, highlights on Jiean's rows.

> Last, the process shader. Jiean converted the wisps' material into a shader in the editor, and saved it unedited. Nearly five hundred lines, and the game doesn't use it. It's a particles shader: a start function for each new particle, and a process function for every step. [Jiean's lines, read as Jiean's table names them.]

## B26 RESULT — the wisps of B16's r1 strip, enlarged, beside Jiean's answer (labels "FIXTURE" and "Jiean's answer, TEST-REPORT A6.7")
**On screen:** [Jiean's answer: which settings live in the shader, which belong to the draw step].

> What that code does, on screen: each wisp is born with its own speed, drifts slowly upward, because its gravity points up, swells, and fades out. The game runs the material, not this file, but the file spells it out line by line. Jiean's split: [Jiean's answer].

## BCRD — who did what
> Who did what. Jiean chose both effects, their jobs and the retrigger rule, wrote every prediction, the budget and the six answers, ran the mutations, captured every strip, read the profiler, and judged every revision. Claude agents, working from the brief, wrote the scenes, the drivers, the tests and the price script; Claude Code reviewed them, made the tuning edits Jiean asked for, and built the price fixture. Caught on the way: a bound in the brief that was wrong, a prediction that ignored draw order, and a cleanup loop that deleted a strip, which Jiean captured again. No image files: the textures are gradients inside the scenes. Source shown: tag a6.

## BVDT — verdict (checked / wrong / uncertain / next)
**On screen, human judgement:** Jiean's playtest, verbatim: [TEST-REPORT A6.8, "Does it read as 'hit' and 'who shot whom'?"].

> Verdict. Checked: every setting reads back, both mutations were caught, the rules held on every frame at sixty frames a second, two bursts overlap on a two-hit turn, and both effects cost a few thousandths of a millisecond, far under budget. Wrong: the brief's one-frame bound, Claude's first flash prediction, and Jiean's price predictions, low by less than a hundredth of a millisecond. Uncertain: why the trail stops up to two frames early, what the profiler's four to six milliseconds with vsync on contain, and whether a hidden trail keeps simulating. In play, Jiean's answer: [playtest line]. Next: turn the dotted streak into a line, and predict the gap first.

## BHTF — Your Turn (composer, "suggested prompt, not a past run")
**Prompt typed:** "Raise fixed_fps on the Streak in my arrow trail from 30 to 60. Before you change anything, help me predict the gap between the dots for a two-square shot that lasts 0.35 seconds. Then I'll capture a strip and we compare."

> Your turn. Pick one setting, and predict before you look. Here's a prompt to start with: raise fixed F P S on the streak from thirty to sixty; before changing anything, predict the gap between the dots for a two-square shot of point three five seconds; then capture a strip and compare. It's one small change, and a direct test of why the trail is dotted. If the dots don't land where you predicted, that isn't a failure. That's a finding. I'm Liam, in for Bear.

## BOUT — locked outro card
> Lane Tactics: A Hit Burst and an Arrow Trail. At Nik Bear Brown.

---

### Changes after approval (each shown to Jiean first)
- **2026-11-08, observation sentences** (pilot frames, `capture/PILOT.md`; Jiean: "Yes, use them"):
  - B04: "a brown dust puff" → "a haze of brown dust"; "inside one board square" → "inside about one board square".
  - B08: "The first burst is still fading when the second starts, on the enemy." → "When the second hit lands, the first burst has almost faded from sight, but it is still alive."
- **2026-11-08, B16 spoken quote** (proposed to Jiean, not objected to):
  - the screen shows Jiean's whole Effect B r1 verdict, verbatim;
  - the voice reads only its second sentence: "Darker puffs provide extra hints for the result of the battle, which keep more attention focusing on the result of each turn within limited time."
- **2026-11-08, bracketed quotes filled from tag `a6`** (`capture/QUOTES-REVIEW.md`; Jiean: "Approve as proposed"):
  - the screen shows each quote in full, verbatim; the voice reads the excerpt in `capture/quotes.json` (`*_spoken`):
    - B24: Jiean's sentence about B's CPU cost;
    - B25: Jiean's line numbers, read with the table's labels;
    - B26: the first and last sentences of Jiean's split;
    - BVDT: the whole playtest sentence.
  - B25's code panel shows `particles_generated.gdshader` lines 252–257, with Jiean's rows 254 and 255.
  - BVDT, for accuracy: "price predictions, low by less than a hundredth of a millisecond" → "off by less than a hundredth"; on screen "(off by < 0.01 ms: three low, one high)". Effect A's CPU prediction (0.015 ms) was above the measured 0.0078 ms.
- **2026-11-08, commit IDs after the history rewrite** (TEST-REPORT A6.11): the code views' side notes now quote the pushed history's IDs (the main session's map, which matches one derived from message and author time). No narration changed.
- **2026-11-08, code excerpts fitted to the panel** (after the first render, which cut off B03 at line 99 and clipped several side notes; `tools/fit_workbench.py`). The workbench holds about 14 code rows at its smallest font. Each excerpt still shows every line the narration names by number. No narration changed.
  - New ranges: B03 91–104, B05 37–49, B07 71–80, B11 87–99, B13 62–75, B15 70–83, B17 130–140, B23 115–123. B09, B19 and B25 are unchanged.
  - Lines left off screen: B03's line 105 (velocity max 260, now in a note); B13's lines 76–79 (named in the bottom line); B17's lines 127–129; B23's lines 112–114.
  - Side notes shortened to three per beat.
- **2026-11-08, B01's on-screen correction** (found in master QC): the hesitant writer matches single words only, so the trigger "The tests decide" never fired, and the first master ended B01 on "The tests decide how they look." The text is now "Tests decide how they look." with the trigger "Tests" → "Jiean's eyes". It ends on the approved line "Jiean's eyes decide how they look.", held for 1.5 s of added silence. No narration changed.
- **2026-11-08, B10, for accuracy** (Jiean: "Yes, fix B10"): "Revision two, three times larger" → "Revision two, about two and a half times larger". r2 took the flash from 40 px to 96 px at birth (scale 1.25 → 3.0, 2.4×; TUNING r2).

### Points for Jiean to check
1. **Title:** "Lane Tactics: A Hit Burst and an Arrow Trail". Default: keep it.
2. **Your name:** the voice spells it "Jay-Ann", as you chose for the A5 film; the screen keeps "Jiean". Default: same as A5.
3. **Slow replays (B04, B12):** an arrow flies for 0.35 s, so these beats replay the same moment at ¼ speed, captured at 120 fps and labelled "¼ SPEED". Default: yes. The other option is real speed only.
4. **Your words still `TO FILL`:** the film quotes them verbatim from tag `a6`:
   - B16: your Effect B r1 verdict;
   - B24: your price conclusion;
   - B25–B26: your A6.7 line references and your shader / draw-step split;
   - BVDT: your playtest answer.

   Default: the capture waits for the tag, so these are filled by then. Anything still empty at the tag is cut from the narration, not written for you.
5. **Your r2/r3 verdict (B10)** is shown verbatim. It credits r3 with "enlarging": r2 changed the size, and r3 let the growth curve (1.0 → 1.6) run for longer, so the glow does end up larger in r3. The narration only says "Jiean kept both". Default: as written.
6. **B20's open question** (why the trail stops up to 2 frames early) is stated as open, not explained, because game timing was out of scope. Default: as written.
7. **Anything you'd say differently:** this film explains your work, so change any sentence.
