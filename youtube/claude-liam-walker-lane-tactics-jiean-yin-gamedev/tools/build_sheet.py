"""Author beat_sheet.json for the Lane Tactics gamedev film (run once; later steps edit it in place).

Excerpts are read from the actual files so the displayed code is verbatim.
Usage (from the reel folder):  python tools/build_sheet.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
REPO = REEL.parents[1]
GODOT = REPO / "godot"
TITLE = "Lane Tactics: From Sketch to Seed to Sound"
SLUG = "claude-liam-walker-lane-tactics-jiean-yin-gamedev"
REV = "film-source-v1 = fcf33ef"


def lines(path: Path, a: int, b: int) -> str:
    return "\n".join(path.read_text(encoding="utf-8").splitlines()[a - 1:b])


def narr(bid, act, text, shot, **extra):
    b = {"beat_id": bid, "act": act, "narration_text": text, "voice": "am_onyx", "engine": "kokoro"}
    b.update(extra)
    b["shot"] = shot
    return b


GAMEPLAY_LABEL = "SCRIPTED INPUT · REAL GODOT RENDER|film-source-v1 · game audio muted"
GAMEPLAY_QC = {
    "full_bleed": True,
    "full_bleed_reason": "Real Godot gameplay capture: the game's table, board and HUD run edge to edge by design; "
                         "the skill forbids reframing gameplay to fill a frame. Underfill/contrast checks still apply.",
}


def gameplay(bid, frames, role, text, hold_s=0.0, extra_label=""):
    shot = {"type": "VIDEO", "source": "own", "treatment": "none", "capture": "run-03",
            "frames": list(frames), "capture_kind": "godot-engine-gameplay (scripted input, Movie Maker run)",
            "label": GAMEPLAY_LABEL + extra_label,
            "typography_note": "Raw engine capture: the HUD text is the game's own UI (diegetic). "
                               "The burned label is ours and is measured separately."}
    if hold_s:
        shot["final_frame_hold_s"] = hold_s
    return narr(bid, "GAMEPLAY", text, shot, role_note=role, qc=dict(GAMEPLAY_QC))


# Verbatim lines from capture/test_rules.log and capture/test_audio_events.log (this build's re-run).
CONSOLE = "\n".join([
    "> godot --headless --path film-source-v1-godot --script res://tests/test_rules.gd",
    "…",
    "SUMMARY test_rules: 51/51 passed -> <capture-copy>/evidence/test_rules-1791865246.json",
    "> godot --headless --path film-source-v1-godot --script res://tests/test_audio_events.gd",
    "PASS  win route: SFX-HOP triggers == moved events  (5 vs 5)",
    "PASS  win route: SFX-HURT triggers == damaged-on-player events  (1 vs 1)",
    "PASS  win route: SFX-WIN triggers == 1  (1)",
    "PASS  win route: rapid presses during playback were ignored  (120 spam, 120 ignored)",
    "PASS  echo inputs never acted  (43 echoes sent, 43 ignored, [])",
    "…",
    "PASS  muted win route: same result and snapshot as unmuted",
    "PASS  muted win route: same events as unmuted",
    "…",
    "SUMMARY test_audio_events: 70/70 passed -> <capture-copy>/evidence/test_audio_events-1791865247.json",
    "# godot = <Godot>/Godot_v4.7.2-stable_win64_console.exe",
])

piece = GODOT / "game" / "piece.gd"
rules = GODOT / "game" / "rules.gd"
audio = GODOT / "game" / "audio_director.gd"
sprites = REPO / "design" / "tools" / "process_sprites.py"

beats = [
    narr("B00", "ASK",
         "Hello — this is Liam, in for Bear. Jiean Yin designed a game called Lane Tactics on paper first, then used "
         "generative models for its art, sound and music, and Claude Code built a small Godot slice to test them "
         "together. This prompt is an illustrative reconstruction, not a transcript. Everything after it comes from "
         "the real project.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
          "label": "Illustrative reconstruction of the Claude interface — not a transcript",
          "remotion": {"pattern": "ClaudeComposerAsk", "props": {
              "greeting": "Hello, Liam", "topic": "WALKER · GODOT GAMEDEV", "segment": "From Sketch to Seed to Sound",
              "command": "Please use Walker to convert my game design document about Lane Tactics — carved wooden "
                         "archers on a five-lane tabletop board, chess-like moves, both sides ordering at once — into "
                         "a small playable Godot slice that proves the generated art, sound effects and music.",
              "runningText": "reading CONCEPT.md…", "folderLabel": "@NikBearBrown", "modelLabel": "Claude",
              "effortLabel": "High",
              "output": ["Archer poses: SDXL. Sounds: ElevenLabs. Music: MusicGen.",
                         "Rules checks 51/51 · sound checks 70/70.",
                         "Source shown: film-source-v1 (fcf33ef)."]}}},
         role_note="walker B00 — ClaudeComposerAsk; prompt begins 'Please use Walker to convert my game design "
                   "document about …'. Illustrative reconstruction, labelled. Liam introduces himself first."),
    narr("B01", "BLUF",
         "What was built: one small playable slice of Lane Tactics, where the generated assets are judged in the "
         "running game, not in a folder. We'll follow one archer from sketch to seed to screen, and hear four sounds "
         "the rules fire.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
          "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
              "text": "Lane Tactics: generated assets,\njudged in folders.\nOne archer, from sketch to seed.\n"
                      "Four sounds, fired by the rules.",
              "triggerWords": "folders", "replacementWords": "the running game",
              "fontSize": 84, "lineSpacing": 2.3, "align": "center", "seed": "lane-tactics-6194",
              "mistakeRate": 2, "hesitateWithin": 0, "hesitateBetween": 1, "charMs": 8,
              "ink": "#3D3929", "accent": "#D97757", "bg": "#FAF9F5"}}},
         lead_silence_s=0.8,
         role_note="walker B01 — hesitant-writer overview of what was built. Correction 'in a folder' -> 'in the "
                   "running game' is the assignment's own point (judged in the running scene, not the image folder).",
         qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer BLUF bookend: centred serif lines typed on "
             "cream; mostly-cream frames are the mandated design."}),
    narr("B02", "CONCEPT",
         "The concept, in plain terms. Carved wooden pieces on a five-lane board. You and an AI general give orders "
         "at the same moment, both plans play out together, and the first side onto the other's back row wins. Four "
         "pillars. Read the board at a glance. Plans collide. Every piece has weight. And when you lose a piece, you "
         "can see why. Each pillar names one look or sound choice, so it can be checked later.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
          "remotion": {"pattern": "GodotDesignBoard", "props": {
              "title": "The Concept and Its Four Pillars",
              "section": "CONCEPT.md · The game in two sentences",
              "excerpt": "You command a small army of carved wooden pieces on a five-lane tabletop board, and you "
                         "face an AI general who gives its orders at the same moment you give yours. Each turn you "
                         "decide where every piece steps and what it strikes; then both plans play out together, and "
                         "the first side to stand a piece on the enemy's back row wins.",
              "source": "CONCEPT.md version 1 (2026-10-09, before any asset was generated) · " + REV,
              "status": "Design pillars · each with one visual or sound choice that honours it",
              "visualLabel": "CONCEPT.md, Design pillars table (wording shortened on the cards)",
              "layout": "cards",
              "cards": [
                  {"label": "1 · Read the board at a glance", "text": "Team paint, thick outline, and facing: teal right, red left."},
                  {"label": "2 · Plans collide", "text": "Patient music while you plan; sharp single sounds on the reveal."},
                  {"label": "3 · Every piece has weight", "text": "Pieces hop and land with a wooden clack (SFX-HOP)."},
                  {"label": "4 · Fair, readable consequences", "text": "The target is marked before the hit; HP pips drop with the sound."}],
              "cues": []}}},
         role_note="Requirement 1: concept and four pillars in plain terms (CONCEPT.md)."),
    gameplay("B03", (0, 328),
             "Real capture run-03 frames 0-327: title (music starts), Enter, board at start, lose-route turns 1-2 "
             "(planned-move marker, both pieces hop). Idle state on the board.",
             "The running slice, driven by scripted input. Your teal archer faces right; the red one faces left. "
             "You plan one step, both sides move at once, and each piece hops."),
    narr("B04", "TRACE-DESIGN",
         "Step one was paper. The character sheet fixes the idle pose: a ball head with one dot eye, a navy hood, a "
         "teal body, a base disc that is always visible, and a thick dark outline, because birch wood on linen is "
         "only 1.1 to 1 contrast. That sketch is also the image the model starts from.",
         {"type": "STILL", "source": "own", "treatment": "none", "motion": "hold",
          "composite": "tools/make_stills.py B04",
          "label": "Design sketches (SVG by Claude Code under Jiean Yin's direction) — not generated art",
          "typography_note": "Composite of design sketches with our captions (>= 41 px at 4K, inside title-safe)."},
         role_note="Asset trace 1/6 (CHAR-IDLE): character-sheet pose 2 idle, storyboard panel 2, and the img2img "
                   "init image design/character/init/idle.png."),
    narr("B05", "TRACE-PROMPT",
         "Step two: the exact recipe, from the asset log. Stable Diffusion XL base 1.0, run locally. Image-to-image "
         "from that sketch at strength point eight. In the reference runs, point seven five had traced the sketch, "
         "and point eight five drifted to a front view. Prompt P4, negative prompt N2, thirty steps, guidance seven, "
         "and three seeds.",
         {"type": "STILL", "source": "own", "treatment": "none", "motion": "hold",
          "composite": "tools/make_stills.py B05",
          "label": "assets/gen-log.jsonl, CHAR-IDLE seed 211 — values verbatim, long strings wrapped for display",
          "typography_note": "Composite of the logged record with our captions (>= 41 px at 4K)."},
         role_note="Asset trace 2/6: gen-log.jsonl line 18 (CHAR-IDLE pose01 s211): model, img2img, init image, "
                   "strength 0.8, P4 prompt, N2 negative, seed, steps, guidance, size."),
    narr("B06", "TRACE-RAW",
         "Three raw outputs, straight from the model, and not in the engine yet. Same prompt, three seeds, three "
         "different pieces. Claude recommended seed 202. Jiean chose 211. Seed 212 was rejected for long hair and a "
         "front-facing face. Every seed and hash is logged, so any row can be regenerated.",
         {"type": "STILL", "source": "own", "treatment": "none", "motion": "hold",
          "composite": "tools/make_stills.py B06",
          "label": "Raw SDXL output — not in-engine",
          "typography_note": "Three raw 1024x1024 outputs (downscaled) with our captions."},
         role_note="Asset trace 3/6: assets/_raw/art/CHAR-IDLE/*.png (s202, s211, s212), hashes match gen-log; "
                   "Jiean's choice s211."),
    narr("B07", "TRACE-EDITS",
         "Then the edits, each one logged with input and output hashes. rembg, with its U-two-net model, cuts out "
         "the background. A cleanup pass removes the white halo. The piece is scaled and anchored on its base. The "
         "enemy is the same art: only teal pixels turn red. But look at the second panel. The base disc is gone.",
         {"type": "STILL", "source": "own", "treatment": "none", "motion": "hold",
          "composite": "tools/make_stills.py B07",
          "label": "Asset files from the repository history and assets/edit-log.jsonl — not in-engine",
          "typography_note": "Composite of the actual sprite files with our captions."},
         role_note="Asset trace 4/6: raw s211 -> 4d5ff51 archer_idle.png (rembg u2net + halo cleanup + scale/anchor; "
                   "base erased, sha a00d7b5d) -> 12f7283 archer_idle.png (base disc redrawn, sha 8cf54fc3) -> "
                   "archer_idle_enemy.png (teal -> red, sha 7d962587)."),
    narr("B08", "CAUSE",
         "Here is the cause. This line treats any pixel brighter than 232 in all three channels as halo, and makes "
         "it transparent. That fixed the reference image's white halo. But seed 211 had painted its base near-white, "
         "so the same line erased it. The fix was a logged hand edit: a walnut disc, redrawn behind the piece at the "
         "sheet's 40 by 12.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
          "label": "Actual source excerpt (design/tools/process_sprites.py @ film-source-v1) · reconstructed code view",
          "remotion": {"pattern": "ClaudeCodeBeat", "props": {
              "title": "design/tools/process_sprites.py — film-source-v1",
              "code": "# lines 43-50\n" + lines(sprites, 43, 50) + "\n\n# line 100\n" + lines(sprites, 100, 100),
              "sparkLine": "Near-white means halo — even when it is the base.",
              "language": "python", "largeText": True}}},
         role_note="Requirement 5 cause->effect: the halo-cleanup threshold (default --white 232) erased idle s211's "
                   "near-white base; the base disc was redrawn (edit-log). Verbatim lines 43-50 and 100."),
    gameplay("B09", (812, 1028),
             "Asset trace 6/6, in-engine result. Real capture run-03 frames 812-1027: R retry -> both archers back in "
             "idle; F3 footprint slots (red 64x96) and base discs (blue 40x12) drawn by the game; F3 off; win-route turn 1 starts (enemy hop).",
             "In the engine: retry brings both archers back in idle. F3 draws each footprint slot and base disc."),
    narr("B10", "CODE",
         "Now the code that puts that image on the board. piece dot g d swaps one static image per state. Every "
         "pose takes the idle image's scale, so all five share one pixel size. flip h turns the enemy to face left. "
         "And the position is measured up from the base, so every pose stands on the same spot.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
          "remotion": {"pattern": "GodotDevWorkbench", "props": {
              "mode": "code", "title": "piece.gd: One Image per State, One Anchor",
              "project": "Lane Tactics asset slice", "path": "res://game/piece.gd",
              "source": "godot/game/piece.gd · lines 175–185 · " + REV,
              "code": lines(piece, 175, 185), "startLine": 175, "codeFontSize": 24,
              "inspectorLabel": "Source notes — not Inspector values",
              "notes": [
                  {"label": "STATES (line 15)", "value": "idle, draw, hurt, defeat, win (+ hop, recover → idle)"},
                  {"label": "TARGET_HEIGHT (line 9)", "value": "80 px; idle image sets the scale"}],
              "cues": [], "output": ["Display only: piece.gd never decides anything (line 2)"]}}},
         role_note="Code beat: piece.gd _apply_visual lines 175-185 (verbatim). Result follows in B11."),
    gameplay("B11", (328, 550),
             "Result of B10. Real capture run-03 frames 328-549: lose-route turn 3 — planned step, hops, target "
             "marker and order numbers, then the exchange: player draw, arrow, enemy hurt (flipped, facing left), "
             "enemy draw, player hurt, both back to idle.",
             "Turn three of a naive plan: both step in, and you strike first. Draw, arrow, the enemy's hurt pose. Then it answers."),
    narr("B12", "CODE",
         "Why that plan loses is in rules dot g d. Attacks resolve one unit at a time, and the side that strikes "
         "first alternates every turn. A unit killed before its turn simply doesn't fire. The slice has one enemy, "
         "not two, because an exhaustive search showed two could only be beaten on the tie rule.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
          "remotion": {"pattern": "GodotDevWorkbench", "props": {
              "mode": "code", "title": "rules.gd: Who Strikes First",
              "project": "Lane Tactics asset slice", "path": "res://game/rules.gd",
              "source": "godot/game/rules.gd · lines 341–346 · " + REV,
              "code": lines(rules, 341, 346), "startLine": 341, "codeFontSize": 30,
              "inspectorLabel": "Source notes — not Inspector values",
              "notes": [
                  {"label": "first_side() (line 160)", "value": "PLAYER if turn % 2 == 1 else ENEMY"},
                  {"label": "CHANGE-BRIEF R1", "value": "two enemies: only tie wins (52 of 45,834)"}],
              "cues": [], "output": ["Rules return plain events; the scene only plays them back (line 7)"]}}},
         role_note="Code beat: rules.gd attack loop lines 341-346 (killed before its turn). Result follows in B13. "
                   "R1 one-enemy change (analyze_variants.gd)."),
    gameplay("B13", (550, 812),
             "Result of B12. Real capture run-03 frames 550-811: lose-route turn 4 — enemy strikes first (order 1), "
             "player toppled (defeat pose) before its own shot; defeat card 'Shot by the enemy archer in lane 4'. "
             "Final frame held to finish the sentence (labelled).",
             "Turn four. The enemy strikes first, your archer topples, and its own arrow never flies. Next: the "
             "winning route, with only the slice's own sound.",
             hold_s=0.0),
    {"beat_id": "B14", "act": "SLICE_AUDIO", "kind": "source_report", "clock": "source", "audio_policy": "preserve",
     "role_note": "Requirement 4: the slice's own audio (music + SFX) with no narration. NOT a fellow's report: the "
                  "compiler's source_report/preserve mechanism is used only because it is the supported way to keep a "
                  "clip's own audio unretimed and unvoiced. Real capture run-03 frames 1089-1593: win-route turns 3-5 "
                  "and the win card. Picture: the 4K master; sound: the AVI audio of the SAME Movie Maker run, sliced "
                  "at the same frame boundaries (1600 samples per frame). Events in order: HOP (t3), HOP+HOP (t4), "
                  "HURT, HIT (t4), HIT (t5, kill), WIN (music stops).",
     "shot": {"type": "VIDEO", "source": "own", "treatment": "none", "capture": "run-03",
              "frames": [1089, 1594],
              "label": "SLICE AUDIO — NO NARRATION|music + SFX as recorded, same run",
              "typography_note": "Raw engine capture with the game's own HUD; our label measured separately."},
     "qc": dict(GAMEPLAY_QC)},
    narr("B15", "CODE",
         "What you just heard is wired in audio director dot g d. The rules resolve the whole turn first; playback "
         "then feeds each event here. A move plays the hop. Damage on the enemy plays the hit. Damage on you plays "
         "the hurt. And entering the win state plays the win, once. Sound never decides anything.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
          "remotion": {"pattern": "GodotDevWorkbench", "props": {
              "mode": "code", "title": "audio_director.gd: Events In, Sounds Out",
              "project": "Lane Tactics asset slice", "path": "res://game/audio_director.gd",
              "source": "godot/game/audio_director.gd · lines 105–118 (inside on_event, line 104) · " + REV,
              "code": lines(audio, 105, 118), "startLine": 105, "codeFontSize": 23,
              "inspectorLabel": "Source notes — not Inspector values",
              "notes": [
                  {"label": "SFX-WIN (lines 166–173)", "value": "on_won(): music stops, win plays once"},
                  {"label": "Header (line 2)", "value": "It never touches game state."}],
              "cues": [], "output": ["Callers: main.gd 411 (landing), 507 (HP change)"]}}},
         role_note="Code beat: audio_director.gd on_event lines 103-118 (verbatim). Result follows in B16."),
    narr("B16", "EVIDENCE",
         "Here is that segment, measured from the recording. Every spike lines up with a logged rules event: the "
         "hops, the hurt, two hits, and the win, right where the music stops. And the tests confirm the other half: "
         "a fully muted run ends in exactly the same state.",
         {"type": "VIDEO", "source": "own", "treatment": "none",
          "composite": "tools/make_stills.py B16",
          "evidence_media": "media/B16.mp4",
          "label": "Measured from capture run-03 audio · trigger frames from capture/run-03-inputs.jsonl",
          "typography_note": "Our measurement figure (waveform + held 4K frames), captions >= 41 px."},
         role_note="Result of B15: RMS envelope of B14's audio (same AVI audio) with the logged sfx_trigger frames "
                   "marked, plus held 4K frames at HOP/HURT/HIT/WIN. Labelled held frames."),
    narr("B17", "TESTS",
         "What was tested. On a fresh clone, all 51 rules checks and all 70 sound checks pass, and this film's build "
         "re-ran both on its isolated copy. Every sound fires once per event, held keys add nothing, and a muted run "
         "ends in the identical state. Jiean also played it, with sound on and fully muted.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
          "label": "Recorded console output (verbatim lines; omissions marked …)",
          "remotion": {"pattern": "ClaudeCodeBeat", "props": {
              "title": "test_rules.log + test_audio_events.log — isolated copy of film-source-v1, 2026-10-13",
              "code": CONSOLE,
              "sparkLine": "TEST-REPORT, fresh clone of 12f7283: the same 51/51 and 70/70.",
              "language": "console", "largeText": False}}},
         role_note="Requirement 6 (tested): TEST-REPORT §1/§4/§7 plus this build's re-run on the isolated copy "
                   "(logs in capture/). Console lines are verbatim."),
    narr("B18", "UNCERTAIN",
         "What's still uncertain. Played muted, Jiean couldn't tell whether a target was on an occupied square, or "
         "why the enemy moved or stopped. Some poses miss the sheet: no squint when hurt, a dot eye in defeat, arms "
         "over the face in the win. The ElevenLabs sounds can't be regenerated: there is no seed. Jiean's next step: "
         "a simpler enemy that keeps marching toward the end and avoids direct contact, plus a clearer target colour.",
         {"type": "STILL", "source": "own", "treatment": "none", "motion": "hold",
          "composite": "tools/make_stills.py B18",
          "label": "Held frames: 4K engine frame (run-03) and evidence/compare crops · quotes verbatim",
          "typography_note": "Composite with our captions (>= 41 px at 4K)."},
         role_note="Requirement 6 (uncertain + next step): TEST-REPORT §6 quote, §2 pose mismatches, §10."),
    narr("B19", "CREDITS",
         "Who made what. Stable Diffusion XL, run locally, made every archer pose and the tabletop, and rembg cut "
         "them out. ElevenLabs made the four sound effects, run by Jiean. MusicGen made the music loop. Jiean picked or approved "
         "every image, sound and take, and made the scope calls. Claude Code drew the sketches, wrote the "
         "prompts and the code, ran the models, and built this film. The source shown is the tag film source v one.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
          "remotion": {"pattern": "FormACard", "props": {
              "lines": [
                  "SDXL base 1.0 (local): every archer pose and the tabletop. rembg u2net: the cut-outs.",
                  "ElevenLabs Sound Effects, run by Jiean: HOP, HIT, HURT, WIN. MusicGen small (local): the loop.",
                  "Jiean Yin: the game, the scope calls, and the pick or approval of every asset.",
                  "Claude Code: sketches, prompts, model runs, edits, Godot code and tests, this film."],
              "meta": [
                  "Game source shown: film-source-v1 = fcf33ef (godot/ identical to 12f7283) · github.com/Jiean-Yin/walker-lane-tactics-jiean-yin",
                  "Narration: Kokoro am_onyx (Liam) · captures: Godot 4.7.2 Movie Maker, scripted input"],
              "dark": False}}},
         role_note="Requirement 6 (contributions, which model made which asset, source revision): SOURCES.md.",
         qc={"sparse_by_design": True, "sparse_reason": "Form A credits card: four centred lines plus a two-line "
             "colophon; the negative space is the card form."}),
    narr("BVDT", "VERDICT",
         "Verdict. Working on screen: five archer states, a recoloured enemy, hop, hit, hurt and win sounds fired by "
         "rules events, and music that stops for the win. Defects: the target marker is hard to read on an occupied "
         "square, enemy moves go unexplained, and three poses miss the sheet. Untested: whether it's fun, and how a "
         "newcomer reads it. One human has played it, the author. Those are Jiean's calls, not the machine's.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-reveal",
          "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
              "artifactTitle": "Verdict", "artifactHeading": "Lane Tactics slice at film-source-v1.",
              "brandLabel": "@NikBearBrown",
              "artifactLines": [
                  "Works on screen: five archer states, enemy recolour, four sounds from rules events, music stop on win.",
                  "Defects: target marker unclear on an occupied square; enemy moves unexplained; three pose mismatches.",
                  "Untested: fun, and newcomers. One human tester, the author. Windows only.",
                  "Human judgment: Jiean picked or approved every asset and owns the next step."]}}},
         role_note="Verdict: observed working vs defects vs untested vs human judgment."),
    narr("BHTF", "HANDOFF",
         "Your turn. Paste this. Use Walker on my Godot slice: raise the near-white halo threshold in my sprite "
         "pipeline from 232 to 245. Before running it, predict which sprites change and whether any base disc comes "
         "back. Then rerun the edits, compare the output hashes with my edit log, and show both versions in the "
         "engine. The point is the prediction. Write it down first, then let the hashes and the running scene tell "
         "you whether you were right. Liam, in for Bear.",
         {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
          "label": "Reconstructed interface · suggested prompt, not a past run",
          "remotion": {"pattern": "ClaudeComposerAsk", "props": {
              "greeting": "Your turn.", "topic": "WALKER · YOUR TURN", "segment": "One Threshold, One Prediction",
              "command": "Use Walker on my Godot slice: raise the near-white halo threshold in my sprite pipeline "
                         "from 232 to 245. Before running it, predict which sprites change and whether any base disc "
                         "comes back. Then rerun the edits, compare the output hashes with my edit log, and show both "
                         "versions in the engine.",
              "runningText": "paste this into Claude…", "folderLabel": "@NikBearBrown", "modelLabel": "Claude",
              "effortLabel": "High"}}},
         role_note="Your Turn: read aloud verbatim, discussed, one bounded change + prediction + test; Liam signs off."),
    {"beat_id": "BOUT", "act": "OUTRO", "kind": "outro_voice",
     "role_note": "OUTRO-LOCK: ClaudeTitleOutro, exact title, @NikBearBrown, slug-seeded mascot, no subline. Spoken, "
                  "never scored; 1.0 s silent tail. No jingle, no game audio.",
     "narration_text": TITLE + ". At Nik Bear Brown.", "voice": "am_onyx", "engine": "kokoro", "tail_hold_s": 1.0,
     "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "mascot-title",
              "remotion": {"pattern": "ClaudeTitleOutro", "props": {
                  "title": TITLE + ".", "slug": SLUG, "handle": "@NikBearBrown", "subline": ""}}}},
]

sheet = {
    "metadata": {
        "title": TITLE, "slug": SLUG, "topic": "WALKER · GODOT GAMEDEV",
        "kind": "godot-gamedev", "skill": "godot-gamedev", "modifier": "walker", "brand": "claude-liam",
        "audience": "Course reviewers and makers following Walker/Claude workflows",
        "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
        "palette": "claude", "style_preset": "claude", "ground": "#FAF9F5", "aspect_ratio": "16:9", "fit": "crop",
        "captions": False, "channel": "@NikBearBrown", "folderLabel": "@NikBearBrown",
        "greeting": "Hello, Liam", "greeting_note": "English-only film (Jiean's request): Hello. Liam never takes Wagwan.",
        "persona": "Liam (in for Bear)", "presenter": "Liam (in for Bear)", "in_for_bear": True,
        "title_status": "default title from the brief; the student may change it",
        "game": {"name": "walker-lane-tactics-jiean-yin",
                 "repository": "https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin",
                 "source_revision": "film-source-v1 = fcf33eff6c501d32624532ca197257a646552991 (godot/ identical to 12f7283)",
                 "engine": "Godot 4.7.2.stable.official.ed1daf0bf"},
        "audio_policy_note": "Narration only on narrated beats (game audio muted under narration). The slice's own "
                             "music + SFX are heard only in B14 (labelled 'Slice audio — no narration'). The outro "
                             "card carries only Liam's voice.",
        "labels": {
            "gameplay": GAMEPLAY_LABEL, "slice_audio": "SLICE AUDIO — NO NARRATION",
            "reconstruction": "Illustrative reconstruction of the Claude interface — not a transcript",
            "editor": "Godot editor reconstruction (printed by GodotDevWorkbench)",
            "raw": "Raw SDXL output — not in-engine", "held": "held frame"},
    },
    "beats": beats,
}

out = REEL / "beat_sheet.json"
out.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", out, len(beats), "beats")
