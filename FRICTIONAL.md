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

---

# Assignment 3 — First 3D assets with Claude, the Blender MCP and Blender

Same format as above. Machine: Windows 11 Home 10.0.26200, Blender 5.2.2 LTS (the chapter used 5.1.2), Godot 4.7.2. The course's setup commands are written for macOS; every place this machine needed something different is listed in the entry.

## 2026-10-15 17:50–18:05 — Blender MCP setup, manual route, on Windows

- **Wanted:** TO FILL *(hint: how long you expected setup to take, and whether you expected the macOS steps to work as written on Windows)*
- **Asked:** Claude Code (desktop app, Code tab) to install uv and register the MCP for Blender server with the course's manual steps, and to record what differed. I approved installing uv.
- **Got:**
  1. **uv.** The course's `brew install uv` is macOS-only. Claude used the README's Windows installer, `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` (the README's uv line has no `-ExecutionPolicy ByPass`; Claude added it). It installed **uv 0.13.1** to `C:\Users\Optim\.local\bin`. The installer put that folder on the user PATH itself (checked with `[Environment]::GetEnvironmentVariable("Path","User")`), so the README's separate PATH step was not needed.
  2. **`claude` was not on PATH.** The desktop app bundles its own Claude Code; Claude ran it by full path, version **2.1.295**.
  3. **The course's register line failed.** `claude mcp add -e DISABLE_TELEMETRY=true blender -- uvx mcp-for-blender` printed `Invalid environment variable format: blender, environment variables should be added as: -e KEY1=value1 -e KEY2=value2`: `-e` accepts several values, so it read `blender` as a second variable. Putting the name first worked: `claude mcp add blender -e DISABLE_TELEMETRY=true -- C:\Users\Optim\.local\bin\uvx.exe mcp-for-blender`. Claude used the full path to `uvx.exe` because the desktop app was started before uv existed, so it may not see the new PATH (the README's "spawn uvx ENOENT" warning). Whether a bare `uvx` would have failed was **not tested**.
  4. `claude mcp get blender` reported *Local config (private to you in this project)*, `√ Connected`, `DISABLE_TELEMETRY=true`. That only shows the server process starts; Blender was not connected at that point, so it proves nothing about the Blender link.
  5. **Server version:** `mcp-for-blender` **2.1.9** (also the latest on PyPI today). uv chose Python 3.14.3; the README warns that very new Pythons can lack wheels, but the server started.
  6. **Add-on.** `uvx mcp-for-blender addon-paths` listed `…\Blender Foundation\Blender\5.2\scripts\addons (missing)`. `uvx mcp-for-blender install-addon` created it and wrote `blender_mcp.py` (add-on version 1.8, SHA-256 `eb0facf69781a30e69792532087d8d41c6a14fcd323353250abe7988ee297fa5`).
  7. **Claude read the add-on code before it was enabled:** the socket binds `localhost`, port 9876; all six service toggles (Poly Haven, Hyper3D, Hunyuan3D, Sketchfab, Tripo, Poly Pizza) default to off; the start button's label in this version is **Connect to Claude** (the course said the code labels it "Connect to MCP server"; that string appears once elsewhere in the file).
- **Decided:** TO FILL
- **Human / Claude / model:** Claude ran every command and read the add-on code; I approved the install and registration. No generation service is enabled.
- **Still unresolved:** whether a new Claude Code session sees the Blender tools and reaches Blender (not tried yet). TO FILL *(hint: anything about the unauthenticated socket that worries you)*

## 2026-10-15 18:05 — Connection test from a new Claude Code session

- **Wanted:** TO FILL *(hint: did you expect it to connect on the first try?)*
- **Asked:** a new Claude Code session (forked from the setup session so it would load the new server) to check the link only, with no building.
- **Got:**
  1. **The tools are there.** The new session listed nine `blender` tools: `execute_blender_code`, `look`, `get_scene_info`, `generate_3d`, `search_assets`, `import_asset`, `get_addon_status`, `disable_telemetry`, `record_trajectory_feedback`. These are the same nine names the course gives for 2.1.9, so the old session's missing tools came from it being started before the server was registered, not from a broken registration.
  2. **Attempt 1, 18:05:** `get_addon_status` → `Error checking addon status: Could not connect to Blender. Make sure the Blender addon is running.` `get_scene_info` → `Error getting scene info: Could not connect to Blender. Make sure the Blender addon is running.`
  3. Claude checked why: `blender.exe` was running (PID 26896), `netstat` showed nothing listening on port 9876, and the saved preferences (`userpref.blend`) did not mention `blender_mcp`. Blender had been opened for the window session *before* the add-on was installed, so the add-on was never loaded. Next: restart Blender, enable *Interface: MCP for Blender*, click **Connect to Claude**, try again.
  4. **Attempt 2, 18:16, after I restarted Blender and enabled the add-on: connected.** `get_addon_status` returned `up_to_date: true`, protocol 13 of 13, add-on 1.8, `blender_version: "5.2.2 LTS"`, libraries polyhaven/sketchfab/polypizza all `off`, generators tripo `off (Premium only)`, hunyuan3d `off`, hyper3d `off`, `telemetry_consent: false`. `get_scene_info` returned Blender's default scene: `Cube` at (0, 0, 0), scale 1, size 2.0 × 2.0 × 2.0, 6 faces; `Light` (point, 1000 W); `Camera`. `netstat` showed Blender listening on `127.0.0.1:9876` only (not on all interfaces).
  5. The status text calls the add-on "Interface: Blender MCP" and its button "Start MCP Server"; the Preferences entry and the panel say "MCP for Blender" and "Connect to Claude". Same add-on, three names.
- **Decided:** TO FILL
- **Human / Claude / model:** Claude ran the calls and the checks; I restarted Blender and enabled the add-on between attempt 1 and attempt 2. TO FILL *(hint: anything you noticed in the Preferences or the N panel)*
- **Still unresolved:** TO FILL

## 2026-10-15 18:17–18:20 — Archer build: Blender restarts twice during the first steps (predicted failure 6)

- **Wanted:** TO FILL
- **Asked:** after the brief commit (`78b213f`) I approved Claude's archer plan and started recording.
- **Got:**
  1. **Step 0** (delete the default objects, metric units, save `blender/archer_piece.blend`) succeeded: `objects: 0 | units: METRIC 1.0 METERS`, file saved.
  2. **Step 1, try 1** (`bpy.ops.mesh.primitive_cylinder_add`, 12 segments): `Error executing code: Connection to Blender lost: [WinError 10053] 你的主机中的软件中止了一个已建立的连接。` ("An established connection was aborted by the software in your host machine"). `get_scene_info` then showed Blender's **default** scene again (Cube, Light, Camera), and `blender.exe` had a new process ID (32864 → 9344): Blender had closed and started again.
  3. Claude repeated step 0 in the new Blender (succeeded), then **step 1, try 2** built the disc with `bmesh.ops.create_cone` (data API, no operator), in case the operator had caused it. The call returned `Code executed successfully: base_disc tris: 44`, but the next `get_scene_info` returned `Error getting scene info: Not connected to Blender`, and `blender.exe` had a new process ID again (9344 → 14908).
  4. Claude found **no crash record**: no `*.crash.txt` in `%TEMP%` and no Application event mentioning Blender in the last 15 minutes.
  5. **Cause:** I told Claude "I closed and reopened Blender myself". So the drops were not an MCP or Blender fault; each restart started a new, unsaved default scene and cut the socket mid-call. The `bmesh` change in try 2 was therefore not needed, but it is kept (it works and needs no operator context).
- **Decided:** TO FILL
- **Human / Claude / model:** I closed and reopened Blender, because TO FILL. Claude diagnosed it from process IDs and the scene contents, and logged it.
- **Still unresolved:** TO FILL

## 2026-10-15 18:20–18:23 — Archer piece built through the MCP

- **Wanted:** TO FILL
- **Asked:** the approved plan: one `execute_blender_code` call per part, `get_scene_info` after each, then join, apply transforms and look. Every body is in [tools/blender/build_archer_piece.py](tools/blender/build_archer_piece.py); the source is `blender/archer_piece.blend`.
- **Got:**
  - Each part landed where the plan said (scale 1, rotation 0 on every part): base disc 0.40 × 0.40 × 0.05 (44 tris), body 0.26 × 0.26 × 0.45 (44), head 0.22 (120), hood 0.25 × 0.25 × 0.16 (22), bow 0.03 × 0.06 × 0.50 (12), eye 0.03 (12). `get_scene_info` rounds to 2 decimals, so the disc's z 0.025 shows as 0.03.
  - The first hood would have had 12 vertices at its tip (bmesh makes a "cone" with a zero-radius top ring); Claude merged them so the tip is one vertex (13 verts, 22 tris).
  - After join + apply: one object `archer_piece`, location (0, 0, 0), rotation (0, 0, 0), scale (1, 1, 1), dimensions **0.40 × 0.40 × 0.80 m** (brief: 0.40 × 0.40 × 0.80), mesh z from 0.0000 to 0.8000, **254 triangles** (budget 400), 5 materials, 0 non-manifold edges, 0 loose vertices.
  - **What Claude got wrong (seen in `look`, not in the numbers):** from the facing (+X) side the bow (z 0.15–0.65) stands in front of the eye (z 0.60), so the eye cannot be seen in profile, which is the view the game uses. That was a mistake in Claude's plan. Also, a straight thin cube reads more like a staff than a bow.
  - Not checked yet: Blender's own Scene Statistics in the status bar (Claude counted triangles from the mesh), and how it looks in Godot.
- **Decided:** TO FILL *(hint: why you fixed the eye this way rather than moving the eye or lowering the bow)*
- **Human / Claude / model:** plan and code by Claude; approval and recording by me. No generation service.
- **Still unresolved:** TO FILL

## 2026-10-15 ~18:30 — My hand edit: the bow moved off the eye (inspect-and-revise cycle 1)

- **Wanted:** TO FILL
- **Asked:** I asked Claude for step-by-step instructions because I was not familiar with Blender yet. Claude suggested the edit (move only the bow 0.08 m along Y in Edit Mode, with Tab → L → G Y 0.08 → Enter → Tab, then check the sidebar and save).
- **Got:** I made the edit myself in Blender's window with the mouse and keyboard and saved with Ctrl+S. Claude then checked it read-only through the MCP: the bow's 8 vertices moved from y −0.03…0.03 to **y 0.05…0.11** (x 0.15…0.18 and z 0.15…0.65 unchanged), so exactly +0.08 m. The object is still at location (0, 0, 0), rotation (0, 0, 0), scale (1, 1, 1), dimensions 0.40 × 0.40 × 0.80 m, 254 triangles, Object Mode, no unsaved changes. In the `look` side (+X) view the eye is now visible beside the bow.
- **Decided:** TO FILL
- **What it taught me about the interface:** TO FILL *(hint: Object Mode vs Edit Mode; that shortcuts go to the area under the mouse; why the sidebar's dimensions did not change)*
- **Human / Claude / model:** the edit in Blender was mine; the instructions and the check were Claude's. Not in `tools/blender/build_archer_piece.py` (that file holds only Claude's code); the result is in `blender/archer_piece.blend`.
- **Still unresolved:** TO FILL

## 2026-10-15 ~18:40 — Board square built through the MCP

- **Wanted:** TO FILL
- **Asked:** I approved Claude's plan (slab + 4 border strips, one call each, then join and apply) and recorded the build in a new clip. Code: [tools/blender/build_board_square.py](tools/blender/build_board_square.py); source `blender/board_square.blend`.
- **Got:**
  - Every call succeeded on the first try; no connection drops this time. Each part had scale 1 and rotation 0: slab 0.92 × 0.92 × 0.04, front/back strips 1.00 × 0.04 × 0.05 at y ∓0.48, left/right strips 0.04 × 0.92 × 0.05 at x ∓0.48, 12 tris each.
  - After join + apply: one object `board_square`, location (0, 0, 0), rotation (0, 0, 0), scale (1, 1, 1), **1.00 × 1.00 × 0.05 m** (brief: 1.00 × 1.00 × 0.05), mesh x and y −0.5000…0.5000, z 0.0000…0.0500, **60 triangles** (budget 100), 2 materials.
  - **What `look` showed:** as Claude warned before building, the border colour `#CDB98E` is too close to the slab `#D8C7A0` (contrast ≈ 1.1 : 1). One square alone reads as a flat sheet with a hardly visible rim. In a temporary 3 × 3 tiled preview (never saved) the squares do separate, through 8 cm faint grooves where two borders meet, but the grid is weak. The viewport also makes both linens look greyer than the hex codes suggest (Blender's default viewport lighting, not checked further).
- **Decided:** I chose to darken the border as a brief revision (A3-R1), after Claude compared four colours: **B `#9A7F55`**. Why: TO FILL
- **Then (inspect-and-revise cycle 2):** Claude changed only the `linen_border` material (linear base colour 0.3231, 0.2122, 0.0908) and saved; size, scale and the 60 triangles did not change. The same temporary 3 × 3 preview now shows a clearly readable grid with a visible board edge. The change is recorded as revision A3-R1 in CHANGE-BRIEF.md (the original colour stays in the table above it) and as the last block of the build script.
- **Human / Claude / model:** plan, code and the contrast table by Claude; approval, recording and the colour choice by me. No generation service.
- **Still unresolved:** TO FILL *(hint: does the darker grid still look like linen under Godot's light?)*

## 2026-10-15 ~18:55 — Goal flag built through the MCP

- **Wanted:** TO FILL
- **Asked:** I approved Claude's plan (base disc, pole, flag; one call each, then join and apply). I asked whether I had to record while Claude worked; Claude said yes, with Blender and the Claude window on screen, from approval until the flag is done. Code: [tools/blender/build_goal_flag.py](tools/blender/build_goal_flag.py); source `blender/goal_flag.blend`.
- **Got:**
  - All calls succeeded first time. Parts: base disc 0.30 × 0.30 × 0.04 (44 tris), pole 0.04 × 0.04 × 1.16 on the disc (28), flag 0.28 × 0.02 × 0.20 at x 0.02…0.30, z 0.98…1.18 (12); each with scale 1, rotation 0.
  - After join + apply: one object `goal_flag`, location (0, 0, 0), rotation (0, 0, 0), scale (1, 1, 1), **0.45 × 0.30 × 1.20 m** (brief: 0.45 × 0.30 × 1.20), mesh x −0.1500…0.3000 (off centre in X, as the brief says), z 0.0000…1.2000, **84 triangles** (budget 150), 2 materials, 0 non-manifold edges.
  - **What `look` showed:** it reads as a red flag on a pole from the front and three-quarter views. From exactly +X the flag is edge-on (2 cm thick) and nearly disappears, so it only reads when the camera looks roughly along Y. The 4 cm pole is visible at this framing; not yet judged at game distance.
- **Decided:** TO FILL *(hint: is a flat box acceptable as a flag for now? how should the two flags face the camera in Godot?)*
- **Human / Claude / model:** plan and code by Claude; approval and recording by me. No generation service.
- **Still unresolved:** TO FILL

## 2026-10-15 19:14–19:16 — Export (headless Blender), Godot import, diorama scene and the headless check

- **Wanted:** TO FILL
- **Asked:** I told Claude to export with headless Blender from the **committed** .blend files and **not** to use the MCP, because I was using Blender myself, and to save the export script in `tools/blender/`.
- **Got:**
  1. **Export.** Claude extracted the three .blend files from commit `fbb0a90` with `git show` into a scratch folder (their SHA-256 matched the working copies) and ran `blender.exe -b --factory-startup --python-exit-code 1 --python tools/blender/export_glb.py -- <scratch> godot/assets/models` (Blender 5.2.2, glTF add-on 5.2.40; the script first checked the exporter's option names). The script refuses a file unless it holds one mesh with location 0, rotation 0, scale 1; it exports GLB with `export_yup=True` and checks the file starts with `glTF`. Exit 0; `archer_piece.glb` 17 764 bytes, `board_square.glb` 5 028, `goal_flag.glb` 5 828.
  2. **Import.** `Godot_v4.7.2-stable_win64_console.exe --headless --path godot --import`: exit 0; a second run printed no line containing error, warn or fail.
  3. **Scene.** `godot/diorama/asset_diorama.tscn`: a 5 × 3 m floor in the table colour `#6B4A2E` at y = 0, one DirectionalLight3D ("Lamp", from the upper left, with shadows), a WorldEnvironment (dark background, weak warm ambient), a Camera3D at (0, 1.1, 3) tilted down 12°, and the three assets side by side on the floor at x = −1.2, 0 and 1.1. Claude wrote the .tscn by hand; nobody has opened it in the editor yet.
  4. **Check, run 1 — Claude's check was wrong.** `godot/tests/check_assets.gd` reported 32/33 with many engine errors (`Condition "!is_inside_tree()" is true` from `get_global_transform`, and `!is_inside_world()` from `get_frustum`). It measured inside `_initialize()`, before the nodes were in the scene tree, so every global transform was identity and the camera had no frustum. Several of the 32 passes therefore proved nothing: the diorama floor and camera-view checks passed for assets whose scene positions had been ignored. The one FAIL (assets overlapping in X: all three measured at x ≈ 0) is what exposed it. The report is kept: `evidence/check_assets-1792106172.json`.
  5. **Check, run 2, after Claude's fix** (wait one frame after `add_child`; every measurement first checks its node is in the tree; the camera check requires 6 frustum planes): **38/38 PASS, exit 0, no engine errors** — `evidence/check_assets-1792106192.json`. Godot numbers (W × H × D, Godot is Y-up): archer 0.40 × 0.80 × 0.40, board 1.00 × 0.05 × 1.00, flag 0.45 × 1.20 × 0.30, all match the brief to 4 decimals; each stands along Y; lowest point y = 0.0000; every node scale (1, 1, 1), rotation 0; triangles 254 / 60 / 84; albedo colours arrived exactly (archer `5A3A22 1F6F78 E2B887 24323F 1B1410`, board `D8C7A0 9A7F55`, flag `5A3A22 B23A2E`). In the diorama each asset's lowest point is 0.0000 m from the floor mesh's top (measured against the Floor, not against the asset itself), all corners are inside the camera's view, and the three do not overlap.
- **What the check does not show:** that anything renders or looks right (headless uses a dummy renderer), how the colours read under the lamp, or whether the shapes read as what they are. Godot also generated LODs on import (`meshes/generate_lods=true`), which the check does not look at.
- **Decided:** TO FILL
- **Human / Claude / model:** the export-route decision (headless, from committed files, no MCP) was mine; the export script, scene, check and the fix were Claude's.
- **Still unresolved:** TO FILL *(hint: what you see when you open the scene and walk the camera around, including from behind and below)*
