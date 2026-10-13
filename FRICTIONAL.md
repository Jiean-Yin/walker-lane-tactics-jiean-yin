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
