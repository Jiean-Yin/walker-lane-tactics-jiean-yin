# FRICTIONAL — Lane Tactics (Assignment 2)

A dated log of the design as it happened: what I wanted the player to see or hear, what I asked for, what came back, and what I decided.

**How this log is written:** Claude Code writes the factual lines (**Asked**, **Got**, **Human / Claude / model**) from the session record. The judgment lines (**Wanted**, **Decided**, **Still unresolved**) are mine. Where one is still open it says `TO FILL`, followed by a *hint* that Claude drafted as a prompt for my own thinking. Hints are replaced, not kept. Entries marked *retrospective* were written after the fact from [DESIGN-HISTORY.md](DESIGN-HISTORY.md).

---

## 2026-09-29 — Real-time idea dropped for turn-based *(retrospective)*

- **Wanted:** 
I want to create a war game like Total War or Clash Royale, which lets players command based on instant changes on the battlefield. I hope players can feel satisfaction after defeating enemies by giving precise commands.
- **Asked:** Claude (other account) to estimate a real-time, Clash Royale-style game with deploy, hold and move orders.
- **Got:** an estimate of 40–60 h for a first playable scene, and two concerns: per-unit commands make it a small RTS, and top-down units walking in every direction are the worst case for consistent generated art. Alternatives offered: army-wide commands, rally points, side view.
- **Decided:** 
I decided to switch the game style to turn-based for easier development and more time allowed to think. PvZ lanes and chess-like movements are familiar nowadays, so the art and concepts are more easily accepted.
- **Next:** rules worked out in three rounds (Oct 6 and Oct 9); see DESIGN-HISTORY §3–6.
- **Human / Claude / model:** the idea and the switch were mine; the estimates and risk analysis were Claude's. No generative model was involved.
- **Still unresolved:**
In order to keep the excitement of giving instant orders at the same time as the enemy, I keep decisions secret and the battle part pre-decided at the start of the turn. Simultaneous orders can raise a lot of bugs and problems.

## 2026-10-09 — Archer range: star shape vs the full 5 × 5 *(retrospective)*

- **Wanted:**
Initially, I just wanted to make sure archers can reach targets at least 2 movements away, so they can cause damage from a safe distance.
- **Asked:** Claude to write the rules draft from the agreed decisions.
- **Got:** a range diagram with 16 squares in a star shape.
- **Decided:** corrected it in a doc comment: the archer reaches all 24 squares of the 5 × 5 around it except its own. That matches the 2-movement concept and is natural for human understanding: melee units hit their neighbors while archers hit one unit away.
- **Human / Claude / model:** the diagram was Claude's; the correction was mine.
- **Still unresolved:** 
We are unsure if the range is too far since that is literally nearly half of the whole battlefield. It needs to be tested in the future.

## 2026-10-09 — Contested squares and the "shadow" *(retrospective)*

- **Wanted:** 
When two units try to get into the same square, opponents must fight to decide who stands there. And you may not take a friendly unit's spot.
- **Asked:** Claude to formalize the idea.
- **Got:** the rule as written in RULES.md: waiting units fight from their start square and enter afterwards in attack order; the check repeats until no square is over its limit.
- **Decided:** 
If units are simply bounced back to their original squares, that does not make sense in a real fight, and it makes the best choice in the game holding a whole line and shooting every unit behind it without strategy.
- **Human / Claude / model:** the idea and the arrow-or-shadow display were mine; the step-by-step resolution was Claude's.
- **Still unresolved:** 
Waiting units' viewing and orders have not been tested. That is a development problem we need to deal with later.

## 2026-10-09 — Scoping the assignment: what the asset slice has to prove

- **Wanted:** 
Finish a slice that really runs, rather than a full rules engine or only a folder of images.
- **Asked:** Claude Code (this account) to read the handoff (CLAUDE.md, RULES.md, DESIGN-HISTORY.md) against the assignment and list questions with defaults.
- **Got:** 12 numbered proposals. Main ones: the archer as the main character (most consistent for image models); enemies as the same art recoloured red; a PvZ-style high-angle camera with pieces in profile; painted wooden tabletop pieces as the art style; web tools I operate myself (Firefly, ElevenLabs, Suno) with Claude writing and logging the prompts; a one-archer-vs-two slice. Claude also pushed back on showing images only in a document: the assignment judges the running scene.
- **Decided:** accepted all 12 defaults. I do not find logical contradictions for now, so I will proceed with caution and accept them first.
- **Human / Claude / model:** proposals by Claude; decisions by me. No generative model yet.
- **Still unresolved:** Whether the wooden-piece style will still fit once riders and horses exist.

## 2026-10-09 — Design sketches and the silhouette check (before any generation)

- **Wanted:** A piece the player can recognise as a friendly archer at 80 px tall on a linen square.
- **Asked:** Claude Code to draw the storyboard (9 panels, 3 views, 4 angles) and the character sheet (12 poses, silhouette, collision, palette) as SVG design sketches from one parametric figure, so proportions cannot drift between poses.
- **Got:**
  - The **silhouette test** shows hurt, defeat, celebrate, draw and hop are distinct, but idle, ready, landing and blocked are almost the same black shape.
  - The **palette check** shows birch wood vs linen at only 1.1 : 1, so the head disappears on the board without its outline.
  - Practical issues: Windows Controlled Folder Access blocked creating the repo under `Documents` from both Git Bash and PowerShell (as in A1), so the repo lives in a folder outside `Documents`; Godot's SVG loader dropped all text, so PNGs are rendered with headless Edge instead.
- **Decided:** 
I decided to generate only the states with distinct silhouettes (idle, draw, hurt, defeat, win) and to make the outline a hard rejection rule.
- **Human / Claude / model:** pose list, layout and sketches by Claude under my direction; the checks were computed by Claude's script. No generative model yet.
- **Still unresolved:** 
Selected units may need an extra pose for clear viewing. We will test that later.

## 2026-10-09 / 10-12 — The planned tools were not free for me

- **Wanted:** Generate with the web tools in GENERATION-PROMPTS (Firefly, ElevenLabs, Suno) without paying.
- **Asked:** Suno (v6-mini and v6 preview, Advanced mode), on 2026-10-09 from 23:03, after the design commit at 22:46. Lyrics field: the music prompt from GENERATION-PROMPTS plus game descriptions, e.g. "calm instrumental, acoustic, steady slow pulse, thoughtful board game and epic war mood…". Styles field: "epic war gaming music. Should be exciting and raise up mood" (later: "…and remain similar volume. Smooth continuation from end to start while repeating"). Screenshots: `assets/rejected/MUS-suno-attempt-1…4.png`.
- **Got:** several Suno takes (titles "Thoughtful Board Game Mood", "Strategic Pulse", "Steady Pulse"…), but the free plan would not download them; the same happened with ElevenLabs Music. Firefly was not available for free either.
- **Decided:** switched to local models that Claude ran on my laptop GPU: SDXL base 1.0 for art, MusicGen small for music. ElevenLabs Sound Effects stayed for the four sounds, which I ran myself (CHANGE-BRIEF R2).
- **Human / Claude / model:** the Suno and ElevenLabs attempts were mine; the switch was proposed by Claude and accepted by me; the local generation was run by Claude.
- **Still unresolved:** My Suno style text asked for "epic war… exciting", while CONCEPT's audio direction says calm and never heroic. I will decide a balanced version in later testing.

## 2026-10-12 — Character reference (CHAR-REF)

- **Wanted:** A piece that matches the sheet (ball head, one eye, navy hood, teal cylinder, base disc, thick outline) and still looks like painted wood.
- **Asked:** SDXL base 1.0 via Claude's script, five runs (asset log rows CHAR-REF ref01–ref05): text-only with prompt P1, then P2 ("2D game sprite…"), then image-to-image from the sheet's idle sketch at strength 0.75, 0.85 and 0.80 (P3, seeds 201–204).
- **Got:** ref01 photo-real 3D toys on grey (no outline); ref02 cartoon humans with legs and faces; 0.75 nearly a trace of the sketch; 0.85 front views with two eyes; 0.80 four candidates close to the sheet. Claude recommended s202 and pointed out a white halo under the base after background removal.
- **Decided:** s202, because "it looks the most like painted wood".
- **Human / Claude / model:** images by SDXL; prompts, runs and the written comparison by Claude; the choice by me.
- **Still unresolved:** The image-to-image route starts from Claude's drawing. I may try reference-image conditioning (IP-Adapter) next time?

## 2026-10-12 — Poses (CHAR-IDLE, DRAW, HURT, DEFEAT, WIN)

- **Wanted:** Five states that read as the same piece and are distinct at 80 px.
- **Asked:** SDXL image-to-image from each pose sketch, strength 0.80, seeds 202, 211, 212 (asset log rows CHAR-* pose01). Claude first noticed the pose prompts were 78–81 tokens, so SDXL would cut off "painted wood grain texture", and shortened only the pose phrases (TEST-REPORT R4).
- **Got:** 15 candidates ([assets/rejected/CHAR-POSES-pose01-compare.png](assets/rejected/CHAR-POSES-pose01-compare.png)). The same seed (202) did not keep the piece the same: draw and hurt turned the navy hood teal. Claude recommended idle 202, draw 211, hurt 211, defeat 211, win 202.
- **Decided:** idle 211, draw 211, hurt 212, defeat 211, win 202. I chose differently from Claude for idle and hurt. Both remain a simple and coherent design, as in the original concept, for clear distinction.
- **Next:** idle 211's base came out near-white, and the halo cleanup erased it. Claude redrew the base disc behind the piece at the sheet's size; this edit is logged (TEST-REPORT R3).
- **Human / Claude / model:** images by SDXL; background removal, base redraw and the teal → red enemy recolour by Claude's scripts; the picks by me.
- **Still unresolved:** The remaining mismatches (hurt has no squint, defeat has a dot eye and a navy bow, the win arms cover the face).

## 2026-10-12 — Sound effects (ElevenLabs)

- **Wanted:** What each of the four sounds should feel like (pillar 3: pieces on a table).
- **Asked:** ElevenLabs Sound Effects (free plan), run by me, with the four prompts in GENERATION-PROMPTS §2 plus descriptions of the game.
- **Got:** LandingSound.mp3 (0.48 s), arrowshit.mp3 (1.0 s), gethit.mp3 (2.0 s), win.mp3 (0.48 s). Claude measured that all four start immediately, then trimmed the tails, normalised and converted them to OGG (edit-log).
- **Decided:** A quick win music should be fine to mark victory. Better effects may be tested later.
- **Human / Claude / model:** sounds by ElevenLabs; the generation and choice by me; trimming and conversion by Claude.
- **Still unresolved:** the exact game description I added to the prompts was not recorded, so these sounds cannot be reproduced exactly.

## 2026-10-12 — Music loop (MusicGen)

- **Wanted:** Suitable looping music for planning that repeats while thinking.
- **Asked:** MusicGen small via Claude's script: prompt P9, seeds 1, 2, 3, 30 s each (asset log MUS-LOOP).
- **Got:** three takes estimated at ~80, ~81.5 and ~107 bpm. Claude rejected take 3 as too fast for the "slow pulse" and cut 8-bar loops from takes 1 and 2 with a crossfade at the seam (seam jump 0.0016 and 0.00006), with 3-repeat previews.
- **Decided:** s1: "smoother and static music won't disrupt the thinking and bring more peace."
- **Human / Claude / model:** music by MusicGen; the loop cut by Claude; listening and choice by me.
- **Still unresolved:** A 24-second loop may get tiring over a long game.

## 2026-10-13 — Playtest, sound on and muted

- **Wanted:** Check that the assets work together and the slice reads without sound.
- **Asked:** I played Claude's checklist (TEST-REPORT §6): the title music over 3 loops, a loss and a win, P/R/M/N/F3, then one game fully muted.
- **Got:** Part A all fine. Part B: "I found it not clear if the attack target is on the character's board… the enemy's moving logic seems weird, a new player cannot understand why enemy move or not."
- **Decided:** keep the slice as it is for testing art and sound; change the target colour and simplify the enemy later: "enemy try keep moving to the end and may avoid direct contact with the opponent."
- **Human / Claude / model:** the playtest and the decisions are mine; the checklist and this summary are Claude's.
- **Still unresolved:** What else must the board show for a muted player to understand the enemy?
