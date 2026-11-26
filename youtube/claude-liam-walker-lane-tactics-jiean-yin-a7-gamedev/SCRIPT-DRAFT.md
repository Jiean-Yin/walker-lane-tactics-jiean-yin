# SCRIPT DRAFT — "Lane Tactics: A Waving Flag and a Committed Shot"

Assignment 7 film, Brutalist `godot-gamedev walker`. Liam (in for Bear), Kokoro `am_onyx`, 4K landscape, 30 fps, no captions.

- **Drafted by** Claude from Jiean's own documents: CHANGE-BRIEF with revisions 1–4, TUNING "Assignment 7", TEST-REPORT "Assignment 7", FRICTIONAL "Assignment 7", SUBMISSION and README "Assignment 7".
- **Status:** approved by Jiean on 2026-11-26, as is ("Approve as is"; every point below kept at its default).
- **Source shown:** tag `a7` (`37c4698`), filmed on an isolated copy.
- **Length:** about 9 minutes.

**Footage:**
- **Game shots** are real engine output: Godot Movie Maker on an isolated copy of tag `a7`, with `main.tscn` unchanged, rendered at 3840 × 2160.
  - Key presses are scripted (the win route the tests play) and labelled so. Every frame's state is logged.
- **Slow replays** capture the same moment at 120 fps and play it at 30, labelled "¼ SPEED". A shot lasts 0.8 s, so its three phases need the slow replay to be seen.
- **Strips** are Jiean's own Movie Maker captures from `captures/shoot/`, shown as **fixtures** (the preview scene), never as gameplay.
- **Test results** are recorded logs from `evidence/a7/`, shown as output cards with their source named.
- **Human checks** are quoted in Jiean's words, never acted out.
- **The reference video is never shown** (standard YouTube licence). Only Jiean's frame numbers appear.

**Code and results:**
- Each code beat is followed directly by the result it produces (code → result).
- Line numbers were checked against tag `a7`. The capture checks them again.
- **Observation sentences** in result beats are written from the strips and logs. After the capture, Claude checks each one against the footage. Any sentence that has to change comes back to Jiean before narration is generated.

---

## B00 ASK — Claude composer (label "Illustrative reconstruction of the Claude interface — not a transcript")
**Greeting:** "Hello, Liam".
**Prompt typed:** "Please use Walker to convert my game design document about Lane Tactics — archers on a five-lane board, simultaneous orders, win by reaching the enemy's back row — into two animations: a goal flag that waves from a sprite sheet, and an archer's shot that moves a rig through startup, active and recovery. Test both, and show me what a headless run cannot."
**Result lines:** `test_flag_readback 43/43 · test_shoot_readback 51/51` · `test_anim_states 51/51 · test_shoot_edges 102/102 at 60 fps` · `Source shown: tag a7`

> Hello, this is Liam, in for Bear. Jiean Yin's game is Lane Tactics: archers on a five-lane board, where you win by reaching the enemy's back row. This assignment adds two animations: a flag that loops, and a shot that commits. The prompt on screen is an illustrative reconstruction.

## B01 BLUF — hesitant writer
**Typed:** "Two animations for Lane Tactics: / a flag that waves, / an archer that shoots. / Seconds decide the timing." The trigger "Seconds" corrects to **"Frames"**. This is a single-word trigger, as the A6 master QC requires.

> Two animations: a flag that waves, and a shot with three phases. Every key is a time, but the timing was designed in frames, sixty to the second, and only then turned into keys.

## B02 SETUP — card
**Card** (from CHANGE-BRIEF §1, SUBMISSION):
- **`wave`, the cycle.** Job: where the goal is. Route: Sprite2D with an AnimationPlayer frame track. Sheet: "Flag Animation Sheet" by Fokko, CC0.
- **`shoot`, the committing action.** Job: who is shooting, and when. Route: a cutout rig keyed as resource text, three parts cut from the draw art.
- Startup 12 · active 21 · recovery 15 frames at 60 fps · Compatibility renderer · 1280 × 720.

> One clip loops, one commits. The flag tells a new player where the goal is. It's a found sheet, played by a frame track. The shot tells you who is shooting, and when: a rig of three parts cut from the archer's drawing, moved by keys. Startup, active, recovery: twelve, twenty-one and fifteen frames.

## B03 CODE — `godot/animations/wave.tres` lines 11–24 (Godot editor reconstruction; highlights 11–13, 17, 21, 24)
**Side panel:** `flag_red.png` 500 × 249 → `hframes` 4 × `vframes` 1 → cells of 125 × 249, frames 0–3.

> A clip is a list of keys, not a movie. This one keys a single integer: the sprite's frame, line seventeen. Four keys, an eighth of a second apart, and the step is one frame period at eight frames a second. The length is half a second, four intervals, so there's no key at the end: the last frame is three, and the wrap goes straight back to zero. Which picture is frame three? The slicing decides, not the image.

## B04 RESULT — the sheet as downloaded with its 4 × 1 grid drawn over it, then the flag in the real game at real speed (labels "FILE AS DOWNLOADED · grid overlay" and "SCRIPTED KEY PRESSES · REAL GODOT RENDER · main.tscn @ a7")

> The sheet as downloaded: four cells, left to right. In the game, the flag stands on the table beside the enemy's back row and ripples, about twice a second, from the title screen on. Jiean watched it through more than five wraps: smooth, steady ripple.

## B05 CODE — `godot/animations/wave.tres` lines 29–36 (highlights 29, 36)
**Side panel**, measured in the sheet (`ATTRIBUTION.md`): the pole's left edge sits at x = 4, 8, 6, 3 in cells 0–3.

> Found sheets drift. In this one, the pole sits at a different place in each cell, by up to five pixels. Editing the sheet would make it a derivative. So a second track keys the sprite's offset, on the same four times: zero, minus four, minus two, plus one. The pole should stand still while the cloth moves.

## B06 RESULT — `captures/flag_registration_r1.png` (label "FIXTURE CROPS · 13 frames of Jiean's r1 strip · guide line drawn on the strip")

> Thirteen frames, cropped from Jiean's strip, with a line drawn at the pole. The cloth changes shape; the pole doesn't move. Its darkest column sits on the same screen pixel in all thirteen. Jiean's check: the pole stands still while the cloth waves.

## B07 CODE — `godot/tests/test_flag_readback.gd` lines 163–177 (highlights 165, 173, 175)

> The read-back test reads the clip back against the brief. Line one seventy-three: every frame key has to be a cell the sheet actually has, fewer than horizontal times vertical frames. Why test that? A key for a cell that doesn't exist loads without a word.

## B08 RESULT — headless output card (label "HEADLESS CHECK OUTPUT · recorded reports, no rendering")
**On screen**, from `evidence/a7/step6/mutations/`:
- Mutation 3, a frame key of 4: `FAIL  every frame key is inside the sheet (0 <= frame < hframes x vframes = 4)  ([0, 1, 2, 4])` · exit 1.
- Mutation 2, loop mode set to none: `FAIL  loop_mode = LOOP_LINEAR  (0)` · exit 1.

> Break it on purpose, in a throwaway copy. Key a fifth cell: the game would show a blank frame with no error, and the test fails on exactly that check. Turn the loop off: the flag would wave once and stop, and the loop-mode check fails. And on the first try, the fifth cell also crashed a later check in the test. That index is now guarded.

## B09 SETUP — the phase table (card, CHANGE-BRIEF §4 and revision 4)
**Card:** Jiean's reference frames (World Archery slow-motion clip, 25 fps, **not shown**, proportions only):
- draw f747 → f809 → **startup 0–12**;
- the hold, 393 frames, **skipped**;
- release f1202 → follow-through f1275 → **active 12–33**;
- follow-through hold → bow drop to f1385 → **recovery 33–48**.
- Bow drop at frame **40**, chosen by eye.

> Feel is designed in frames. The game already fixes how long a shot takes: point two seconds to draw, point three five while the arrow flies, point two five to recover. At sixty frames a second: twelve, twenty-one, fifteen. Jiean measured a slow-motion archer, frame by frame, to space the motion inside each phase. The real archer holds at full draw for longer than the whole of our shot. The game skips that. Jiean put the bow drop at frame forty, by eye.

## B10 CODE — `godot/animations/shoot.tres` lines 31–44 (highlights 31, 33, 41, 44)
**Side panel:** key time = frame ÷ 60: f0 0.0 · f12 0.2 · f33 0.55 · f40 0.666667 · f48 0.8.

> The table becomes keys. Line thirty-three: the step is one sixtieth. The default is one thirtieth, and frame thirty-three falls between two of those. Line forty-one: a key at every boundary, each time a frame divided by sixty. Three tracks move the rig: the whole archer recoils, the upper body leans, and the bow turns at the hand.

## B11 RESULT — one shot in the real game, real speed, then ¼-speed replay with the phase names over it (labels as B04, plus "¼ SPEED · captured at 120 fps")

> One shot at real speed, then at a quarter. Startup: the archer leans back and the bow comes up level. The arrow leaves. Active: the archer eases forward through the follow-through while the arrow flies. Recovery: a short hold after the hit, then the bow drops, and the archer is back in the idle pose. Jiean's check: all distinct.

## B12 CODE — `godot/game/piece.gd` lines 109–116 (highlights 112, 113, 115, 116)
**Side panel**, one authority (CLAUDE.md): `Rig`, `Upper`, `Bow` ← the rig's AnimationPlayer only · the player is started, stopped and advanced only by `piece.gd` · `Mount` (place, facing, visibility) ← `piece.gd` only.

> One authority: exactly one thing writes each animated node. The clip writes the rig's three pivots, and nothing else. Only the piece script starts it: when the pose becomes draw, line one thirteen looks up its clip, line one fifteen plays it, and line one sixteen applies frame zero at once. Line one twelve stops the last one first, so no old pose carries over. Facing lives one node up, so the clip and the script never touch the same node.

## B13 RESULT — real play with interrupts: P in startup, P in active, P in recovery, then R mid-shot (labels as B04, plus "P pressed at frame N" / "R pressed at frame N")

> Now interrupt it. Pause in the startup, during the flight, and after the hit: each time, the archer holds mid-motion, and carries on from the same pose when unpaused. Press R in the middle of a shot: the archers are rebuilt, and nothing from the old shot comes back.

## B14 CODE — `godot/game/piece.gd` lines 166–182 (highlights 166, 181, 182)

> Two clocks. A player can advance on the process tick, or the physics tick, or not on its own at all. This one is manual. Line one eighty-two: the piece advances it by the game's own time, from inside the game's update. So when the game pauses, the clip stops. The flag's player is different: it runs on the process tick, in real time.

## B15 RESULT — split: the flag waving while the game is paused (footage, label "P pressed · game paused"), beside a headless card (label "HEADLESS CHECK OUTPUT")
**On screen**, from `evidence/a7/step5/test_anim_states_60fps.log`: `clip position - arrow t = DRAW_LEAD 0.2 … (0.20000)` (all three shots) · the clip at 1/60 s on the draw frame.

> Paused: the archers freeze, the flag keeps waving. That's by design: wind isn't part of the game. And the two clocks agree to within a frame. On the arrow's first frame, the clip is exactly point two seconds ahead of the arrow: one sixtieth of a second ahead of the cue clock, because it advances right after the cue, in the same frame. No physics tick anywhere.

## B16 CODE — `godot/tests/test_shoot_readback.gd` lines 86–102 (highlights 88, 89, 99, 100)

> The rig's read-back resolves every track to a real node and property. It branches on track type: a 3D transform track names a bone, not a property, so a plain check would call every bone track broken. Here, a value track has to name a property the node really has, line ninety-nine.

## B17 RESULT — headless output card (same label)
**On screen**, from `evidence/a7/step6/mutations/`:
- Mutation 1, `Rig/Upper:rotation` renamed `rotaton` in the clip only: `FAIL  track_problems() is empty …  (track 1: Node2D has no property 'rotaton')` · exit 1.
- Mutation 4, empty import cache: rig read-back **51/51**, as predicted.

> Rename one property in the clip, a single letter, and in the game the upper body would just stop leaning. No error, no warning: a track that points at nothing is silently inert. The read-back names the track and the missing property. Mutation four empties the import cache, and this one passes, as predicted: the rig is keyed in text, so no import setting can be lost.

## B18 CODE — `godot/animations/shoot.tres` lines 61–68 (highlight 68)
**Side panel** "TUNING.md · one change, Jiean's approval": the bow's frame-48 key 20° → 8° (brief revision 4).

> Strips are where the motion gets judged. Jiean watched the first strip before Claude read it, and wrote: the bow seems to leave the archer's hand. Claude found why: the bow turns at the hand, but the rig cuts the drawing at one column, so the forearm and the string stay behind. One change: the bow's last key, line sixty-eight, from twenty degrees to eight.

## B19 RESULT — strips r0 (top) and r1 (bottom), bow hand at 6×, frames 15, 29, 31, 33 (label "FIXTURE · shoot_preview.tscn · Jiean's Movie Maker captures, 30 fps")
**On screen, verbatim:** Jiean's r0 note "The bow seems to leave the archer's hand while retreating the bow though." · r1 "This time the bow stays in arhcer's hand, and it is still clear to see the bow lowering a the end." · pixels changed: frames 10–29 **0**, frames 31–33 410–458.

> Revision zero above, revision one below. Up to frame twenty-nine, not one pixel changed. In the drop, the gap at the hand closes to about a pixel. Claude had worried that eight degrees might be too small to see. Jiean watched it in the game, and disagreed: the bow stays in the hand, and the lowering is still clear. Kept.

## B20 CODE — `godot/tests/test_shoot_edges.gd` lines 31–34 (highlights 31–33)

> Edges. At every boundary of the table, frames zero, twelve, thirty-three and forty-eight, three interrupts, P, R and Enter, each arriving one frame before, on, and after. Thirty-six cases, and each one first proves its key landed on the frame it was aimed at.

## B21 RESULT — headless output card (label "HEADLESS CHECK OUTPUT")
**On screen:** `SUMMARY test_shoot_edges: 102/102` (`evidence/a7/step6/`) · the pins `29/29`, before and after the clips · measured: impact 32 / 34, back to idle 47 / 49 against the table's 33 and 48 (brief revision 1) · beside it: what no headless run can show.

> One hundred two out of one hundred two. Two findings on the way. One frame before the draw, the game is still waiting for the attack order: there, Enter is the order itself, so the first version of the test was wrong, and was fixed to match the game. And the game's own cues land a frame early or late, so the end pose shows for zero or two frames. Game timing was out of scope, so that stays as it is. None of this draws a single pixel.

## BCRD — who did what
> Who did what. Jiean chose both clips, the sheet and the reference, measured its frames, wrote the phase table, the predictions and the answers, captured every strip, and judged every one, including the human checks. Claude agents, working from the brief, wrote the clips, the read-backs and the wiring. Claude Code reviewed them, wrote the pins, the edge tests and the preview, and made the one tuning change Jiean approved. Caught on the way: a recovery split that fell outside the clip, a capture folder that didn't exist, and an author email in a transcript, removed before anything was pushed. The flag sheet is by Fokko, CC0. Source shown: tag a7.

## BVDT — verdict (checked / wrong / uncertain / next)
**On screen, human judgement:** Jiean's summary, verbatim: "I chose and measured the exact number of adjustment, and predicted the possible failure to avoid. I approved most of the adjustments suggesstions by Claude. Every test were followed by my own human check." (SUBMISSION.md)

> Verdict. Checked: every track resolves, every key sits on its frame, both loop modes and the frame range are pinned, three mutations fail their tests and the fourth passes for the right reason, the pins didn't move, and a hundred and two edge cases hold. Wrong: where Claude's rig cut the drawing, which split the bow from the hand at twenty degrees, and a frame-before-the-draw assumption in a test. Uncertain: why the game's cues land a frame off, and the recoil, still about a pixel and a half on screen. In Jiean's words: every test was followed by a human check. Next: make the release readable.

## BHTF — Your Turn (composer, "suggested prompt, not a past run")
**Prompt typed:** "In shoot.tres, change the recoil key at frame 33 from 6 to 18 pixels in the art. Before you change anything, help me predict how many screen pixels that is at the rig's scale, and which strip frames should show it. Then I'll capture a strip and we compare."

> Your turn. One key, and a prediction first. Here's a prompt to start with: raise the recoil at frame thirty-three from six to eighteen pixels in the art; before changing anything, predict how far that moves on screen, and on which strip frames. Then capture a strip and compare. If the release still doesn't read, that isn't a failure. That's a finding. I'm Liam, in for Bear.

## BOUT — locked outro card
> Lane Tactics: A Waving Flag and a Committed Shot. At Nik Bear Brown.

---

### Points for Jiean to check
1. **Title:** "Lane Tactics: A Waving Flag and a Committed Shot". Default: keep it.
2. **Your name:** the voice says "Jay-Ann", as in the A5 and A6 films; the screen keeps "Jiean". Default: same.
3. **Slow replays (B11, B13):** a shot lasts 0.8 s, so these beats replay it at ¼ speed (120 fps capture, labelled). Default: yes.
4. **Your words, quoted verbatim, typos kept:** B04, B06, B11, B19, BVDT. On screen they appear exactly as written ("arhcer's", "a the end", "suggesstions"). The voice reads them with the spelling corrected. Default: as described.
5. **B19, "Jiean disagreed":** this is your TEST-REPORT A7.14 answer (Claude thought the lean and the bow angle were too small to catch; you found them clear). Default: as written.
6. **B21's open question** (why the cues land a frame off) is stated as open, not explained, because game timing was out of scope. Default: as written.
7. **Length:** about 9 minutes, 22 beats. To save time, B05–B06 (registration) and B16–B17 (track check) could be cut, which would bring it to about 7 minutes. Default: keep all.
8. **Anything you'd say differently:** this film explains your work, so change any sentence.
