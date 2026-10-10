# FRICTIONAL — Lane Tactics (Assignment 2)

A dated log of the design as it happened: what I wanted the player to see or hear, what I asked for, what came back, and what I decided.

**How this log is written:** Claude Code writes the factual lines (**Asked**, **Got**, **Human / Claude / model**) from the session record. The judgment lines (**Wanted**, **Decided**, **Still unresolved**) are mine. Where one is still open it says `TO FILL`, followed by a *hint* that Claude drafted as a prompt for my own thinking. Hints are replaced, not kept. Entries marked *retrospective* were written after the fact from [DESIGN-HISTORY.md](DESIGN-HISTORY.md).

---

## 2026-09-29 — Real-time idea dropped for turn-based *(retrospective)*

- **Wanted:** TO FILL — *hint (Claude's draft, replace in your own words): what you liked about the Clash Royale-style idea, and what you actually wanted the player to feel when deploying and commanding soldiers.*
- **Asked:** Claude (other account) to estimate a real-time, Clash Royale-style game with deploy, hold and move orders.
- **Got:** an estimate of 40–60 h for a first playable scene, and two concerns: per-unit commands make it a small RTS, and top-down units walking in every direction are the worst case for consistent generated art. Alternatives offered: army-wide commands, rally points, side view.
- **Decided:** TO FILL — *hint: you switched to turn-based play with PvZ lanes and chess-like moves. Was it mainly the art-consistency risk, the workload, or that turn-based planning is closer to the game you want?*
- **Next:** rules worked out in three rounds (Oct 6 and Oct 9); see DESIGN-HISTORY §3–6.
- **Human / Claude / model:** the idea and the switch were mine; the estimates and risk analysis were Claude's. No generative model was involved.
- **Still unresolved:** TO FILL — *hint: does turn-based play keep enough of the excitement you liked in real time? Simultaneous orders are the bet.*

## 2026-10-09 — Archer range: star shape vs the full 5 × 5 *(retrospective)*

- **Wanted:** TO FILL — *hint: what "two steps away" meant in your head, and why the archer needs that much reach.*
- **Asked:** Claude to write the rules draft from the agreed decisions.
- **Got:** a range diagram with 16 squares in a star shape.
- **Decided:** corrected it in a doc comment: the archer reaches all 24 squares of the 5 × 5 around it except its own. TO FILL — *hint: why the full square is better for play (easier to read? stronger archers to counter riders?).*
- **Human / Claude / model:** the diagram was Claude's; the correction was mine.
- **Still unresolved:** TO FILL — *hint: is a 24-square range too strong on a board only 5 lanes tall (it covers every lane from the middle lane)?*

## 2026-10-09 — Contested squares and the "shadow" *(retrospective)*

- **Wanted:** TO FILL — *hint: what you wanted to happen when two pieces try to enter a full square, and what the player should see.*
- **Asked:** Claude to formalize the idea.
- **Got:** the rule as written in RULES.md: waiting units fight from their start square and enter afterwards in attack order; the check repeats until no square is over its limit.
- **Decided:** TO FILL — *hint: why "show the attempt, settle after combat" instead of simply bouncing both pieces back.*
- **Human / Claude / model:** the idea and the arrow-or-shadow display were mine; the step-by-step resolution was Claude's.
- **Still unresolved:** TO FILL — *hint: will chains of waiting units be readable on screen? (Not tested yet; the asset slice cannot produce contested squares.)*

## 2026-10-09 — Scoping the assignment: what the asset slice has to prove

- **Wanted:** TO FILL — *hint: finish tonight with a slice that really runs, rather than a full rules engine or only a folder of images.*
- **Asked:** Claude Code (this account) to read the handoff (CLAUDE.md, RULES.md, DESIGN-HISTORY.md) against the assignment and list questions with defaults.
- **Got:** 12 numbered proposals. Main ones: the archer as the main character (most consistent for image models); enemies as the same art recoloured red; a PvZ-style high-angle camera with pieces in profile; painted wooden tabletop pieces as the art style; web tools I operate myself (Firefly, ElevenLabs, Suno) with Claude writing and logging the prompts; a one-archer-vs-two slice. Claude also pushed back on showing images only in a document: the assignment judges the running scene.
- **Decided:** accepted all 12 defaults. I asked for hint drafts next to the TO FILL lines in this log. TO FILL — *hint: which of these choices you were least sure about, and why you accepted it anyway.*
- **Human / Claude / model:** proposals by Claude; decisions by me. No generative model yet.
- **Still unresolved:** TO FILL — *hint: whether the wooden-piece style will still fit once riders and horses exist.*

## 2026-10-09 — Design sketches and the silhouette check (before any generation)

- **Wanted:** TO FILL — *hint: a piece the player can recognise as "my archer, in this state" at 80 px tall on a linen square.*
- **Asked:** Claude Code to draw the storyboard (9 panels, 3 views, 4 angles) and the character sheet (12 poses, silhouette, collision, palette) as SVG design sketches from one parametric figure, so proportions cannot drift between poses.
- **Got:**
  - The **silhouette test** shows hurt, defeat, celebrate, draw and hop are distinct, but idle, ready, landing and blocked are almost the same black shape.
  - The **palette check** shows birch wood vs linen at only 1.1 : 1, so the head disappears on the board without its outline.
  - Practical issues: Windows Controlled Folder Access blocked creating the repo under `Documents` from both Git Bash and PowerShell (as in A1), so the repo is at `C:\dev\walker-lane-tactics-jiean-yin`; Godot's SVG loader dropped all text, so PNGs are rendered with headless Edge instead.
- **Decided:** TO FILL — *hint: whether you accept generating only the states with distinct silhouettes (idle, draw, hurt, defeat, win) and making the outline a hard rejection rule.*
- **Human / Claude / model:** pose list, layout and sketches by Claude under my direction; the checks were computed by Claude's script. No generative model yet.
- **Still unresolved:** TO FILL — *hint: does "selected" need its own pose later, or is the yellow outline enough?*
