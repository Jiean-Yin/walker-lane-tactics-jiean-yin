"""Write beat_sheet.json for the A6 film from the script Jiean approved (SCRIPT-DRAFT.md, 2026-11-08, "Approve as is").

Code excerpts are read from the isolated copy of tag a6 (CAPTURE/a6/godot), never typed, so each matches its file.
Narration spells Jiean's name "Jay-Ann" for the voice only (Jiean's choice for the A5 film); everything on screen keeps
"Jiean". Footage segment ranges are filled in later by tools/set_segments.py.

Quotes that were still TO FILL when the script was approved are read from the tag copy's documents by
tools/quotes.py and stored in capture/quotes.json; this script refuses to run while any is missing, so nothing is
ever written for Jiean. B25's excerpt range comes from Jiean's A6.7 table (quotes.json "a67_range").
Usage (reel folder): CAPTURE=<capture-copy> python tools/build_sheet.py
DRAFT=1 writes beat_sheet.draft.json instead, for voicing the beats that quote nothing of Jiean's before Jiean has
approved the spoken excerpts: every beat that would speak a missing *_spoken field starts with "[PLACEHOLDER]", which
the Kokoro generator skips, so nothing is voiced for Jiean in draft mode.
"""
import json
import os
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = Path(os.environ["CAPTURE"]) / "a6" / "godot"
SLUG = "claude-liam-walker-lane-tactics-jiean-yin-a6-gamedev"
TITLE = "Lane Tactics: A Hit Burst and an Arrow Trail"
NAME = "Jay-Ann"  # voice spelling only
Q = json.loads((REEL / "capture/quotes.json").read_text(encoding="utf-8"))
DRAFT = os.environ.get("DRAFT") == "1"
PENDING = "⟨PENDING JIEAN⟩"
if DRAFT:
    for k in ("b_r1_verdict_spoken", "price_conclusion_spoken", "a67_rows_spoken", "a67_split_spoken",
              "playtest_reads_spoken"):
        Q.setdefault(k, PENDING)
    Q.setdefault("a67_range", [252, 257])  # proposal only; the final range is Jiean's
REV = Q["source_revision"]  # "tag a6 = <commit> (tree <tree>)", written by tools/quotes.py
# Screen text names the tag only: its commit id may still change before the tag is pushed (the tree will not).
for k in ("b_r1_verdict", "price_conclusion", "a67_range", "a67_rows", "a67_split", "playtest_reads"):
    if not Q.get(k):
        raise SystemExit(f"quotes.json: '{k}' is missing or empty; it must come from tag a6, never be written here")


def lines(rel, a, b):
    text = (GAME / rel).read_text(encoding="utf-8").split("\n")
    return "\n".join(text[a - 1:b])


def voice(b):
    b.setdefault("voice", "am_onyx")
    b.setdefault("engine", "kokoro")
    return b


def workbench(bid, title, rel, a, b, narration, notes, output, role, label=None):
    props = {"mode": "code", "title": title, "project": "Lane Tactics", "path": "res://" + rel,
             "source": f"godot/{rel} · lines {a}–{b} · tag a6", "code": lines(rel, a, b), "startLine": a,
             "codeFontSize": 30 if b - a >= 14 else 34, "inspectorLabel": "Source notes · not Inspector values",
             "notes": notes, "output": output}
    shot = {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
            "remotion": {"pattern": "GodotDevWorkbench", "props": props}}
    if label:
        shot["label"] = label
    return voice({"beat_id": bid, "act": "CODE", "narration_text": narration, "shot": shot,
                  "excerpt": {"path": rel, "start_line": a, "end_line": b}, "role_note": role})


def still(bid, act, narration, label, role, evidence=False):
    shot = {"type": "STILL", "source": "own", "treatment": "none", "motion": "hold",
            "composite": f"tools/make_media.py {bid}", "label": label}
    if evidence:
        shot["evidence_media"] = f"media/{bid}.mp4"
    return voice({"beat_id": bid, "act": act, "narration_text": narration, "shot": shot, "role_note": role})


def footage(bid, narration, label, role):
    return voice({"beat_id": bid, "act": "RESULT", "narration_text": narration,
                  "shot": {"type": "VIDEO", "source": "own", "treatment": "none", "segments": [], "label": label,
                           "evidence_media": f"media/{bid}.mp4"},
                  "role_note": role,
                  "qc": {"full_bleed": True,
                         "full_bleed_reason": "Real Godot render, edge to edge; reframing would misrepresent it.",
                         "contrast_regions": [{"label": "burned disclosure label", "box": [0.035, 0.05, 0.62, 0.135]}],
                         "contrast_reason": "Real engine render; the essential text is our burned label (white/yellow on "
                                            "a dark green pill). Scene colours are not text."}})


PLAY_LABEL = (f"SCRIPTED KEY PRESSES · REAL GODOT RENDER|main.tscn @ tag a6, isolated copy · Movie Maker, 30 fps · "
              "no audio")
SLOW_LABEL = ("¼ SPEED · REAL GODOT RENDER|the same turn captured at 120 fps, played at 30 · main.tscn @ tag a6 · "
              "scripted key presses")
A_R = Q["a67_range"]  # [start, end] from Jiean's A6.7 rows

beats = [
    voice({"beat_id": "B00", "act": "ASK",
           "narration_text": f"Hello, this is Liam, in for Bear. {NAME} Yin's game is Lane Tactics: archers on a five-lane "
                             "board, where you win by reaching the enemy's back row. This assignment adds particle "
                             "effects: a burst where an arrow hits, and a trail behind the arrow in flight. The prompt on "
                             "screen is an illustrative reconstruction.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
                    "label": "Illustrative reconstruction of the Claude interface — not a transcript",
                    "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                        "greeting": "Hello, Liam", "topic": "WALKER · GODOT GAMEDEV",
                        "segment": "A Hit Burst and an Arrow Trail",
                        "command": "Please use Walker to convert my game design document about Lane Tactics — archers "
                                   "on a five-lane board, simultaneous orders, win by reaching the enemy's back row — "
                                   "into two particle effects: a hit burst that shows which archer an arrow hit, and a "
                                   "trail that shows who shot whom. Test both, price both, and show me what a headless "
                                   "run cannot.",
                        "runningText": "reading CHANGE-BRIEF.md…", "folderLabel": "@NikBearBrown",
                        "modelLabel": "Claude", "effortLabel": "High",
                        "output": ["test_hit_burst_config 107/107 · test_arrow_trail_config 135/135",
                                   "test_hit_burst_state 31/31 · test_arrow_trail_state 31/31 at 60 fps",
                                   "Source shown: tag a6"]}}},
           "role_note": "walker B00: ClaudeComposerAsk; prompt begins 'Please use Walker to convert my game design "
                        "document about'; illustrative reconstruction, labelled. Result lines are recorded numbers "
                        "(TEST-REPORT A6.1)."}),
    voice({"beat_id": "B01", "act": "BLUF", "lead_silence_s": 0.8,
           "narration_text": "Two particle effects: a burst that marks the hit, and a trail that shows the shot. The tests "
                             f"guard every setting. How they look was decided by {NAME}'s eyes, one revision at a time.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
                    "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
                        "text": "Two particle effects for Lane Tactics:\na burst where the arrow lands,\na trail behind it "
                                "in flight.\nTests decide how they look.",
                        # one word: the component matches single words only ("Tests" -> "Jiean's eyes")
                        "triggerWords": "Tests", "replacementWords": "Jiean's eyes", "fontSize": 80,
                        "lineSpacing": 2.2, "align": "center", "seed": "lane-tactics-a6-1108", "mistakeRate": 2,
                        "hesitateWithin": 0, "hesitateBetween": 1, "charMs": 8, "ink": "#3D3929", "accent": "#D97757",
                        "bg": "#FAF9F5"}}},
           "role_note": "walker B01: hesitant-writer summary; 'Tests decide' -> 'Jiean's eyes decide' is the film's "
                        "point (settings are tested, the look was tuned by eye).",
           "qc": {"sparse_by_design": True,
                  "sparse_reason": "Hesitant-writer BLUF bookend: centred serif lines typed on cream."}}),
    still("B02", "SETUP",
          "Each effect has one job. Effect A: an arrow hit an archer, and which one. It fires on an event, every "
          "damaged event. Effect B: who shot whom, and along which path. It runs while a condition holds, an arrow in "
          "flight. One is a CPU particle node, one a GPU node. And the game runs on Godot's Compatibility renderer. "
          "That matters later.",
          "", "Setup: the two jobs, event vs condition, node types, renderer (CHANGE-BRIEF §1, §2; project.godot:25)."),
    workbench("B03", "hit_burst.tscn: the splinters", "effects/hit_burst.tscn", 89, 105,
              "Effect A is one scene: a root and three CPU particle nodes, Flash, Splinters and Dust. Here are the "
              "splinters. Line ninety-one: saved not emitting, so nothing fires when a scene loads. Fourteen, born all "
              "at once. Up to seventy-five degrees either side of straight up, at one hundred forty to two hundred sixty "
              "pixels a second, and gravity pulls them back down. Line ninety-eight: local coords off, so each splinter "
              "stays where it was born.",
              [{"label": "HitBurst (Node2D, z 2)", "value": "Flash 1 · Splinters 14 · Dust 8 = 23 particles"},
               {"label": "Settings live in", "value": "the scene file only; trigger code never sets a look value"},
               {"label": "Written by", "value": "claude -p agent, session 2a (cb9830b)"}],
              ["Textures: GradientTexture2D inside the scene, no image file"],
              "Effect A scene; code beat, result B04."),
    footage("B04", "In the real game, keys pressed by a script. The enemy's arrow lands on the player's archer. Now at a "
                   "quarter speed: a red glow over the body, splinters thrown out and falling, a haze of brown dust, and "
                   "after about a second, nothing. The whole burst stays inside about one board square.",
            PLAY_LABEL, "Result of B03: play P1-P2 (turns 2-4, the enemy's hit on the player) at real speed, then slow S2 (same hit) at "
                        "¼ speed, cropped 3× around the player's archer."),
    workbench("B05", "hit_burst_driver.gd: reading the game", "game/hit_burst_driver.gd", 34, 49,
              "Nothing in this game sends a signal. So the driver runs every frame, right after the game's own update, "
              "and reads the list of events the game has played. Line forty-four: every new damaged event gets a burst. "
              "Line forty-nine: every emitter's speed scale is the game's speed, and zero while it's paused. The driver "
              "reads the game. It never writes it.",
              [{"label": "Trace", "value": "Enter → attacks play → _cue_impact appends \"damaged\" to played_events "
                                           "(main.gd:502) → this driver, same frame → a burst at the archer"},
               {"label": "process_priority", "value": "10: runs after main (0) every frame (main.tscn)"},
               {"label": "Written by", "value": "claude -p agent, session 3a; plan approved by Jiean (dd0ad5c)"}],
              ["Reads main's state; never writes it"],
              "Effect A driver (read side); code beat, result B06."),
    footage("B06", "The burst appears on the frame the arrow lands. Press P in the middle of it: the game's own pause. The "
                   "pieces hold, and so does every splinter, in mid-air. Unpause, and it carries on from where it "
                   "stopped. The game never pauses its scene tree. A speed scale of zero does it.",
            PLAY_LABEL, "Result of B05: play P4 (run 2, turn 4: P 0.3 s after the first hit, held 6.5 s, then P)."),
    workbench("B07", "hit_burst_driver.gd: one burst per hit", "game/hit_burst_driver.gd", 71, 85,
              "Spawning. Line seventy-five: a new instance for every hit. That's the retrigger rule "
              f"{NAME} chose, overlap: an earlier burst keeps playing. Line seventy-seven: at the archer's base, plus "
              "forty pixels up, the body. Line seventy-nine: when the dust, the longest emitter, reports finished, the "
              "burst frees itself. And it's a child of the driver, never of the archer.",
              [{"label": "Retrigger rule", "value": "overlap: a new HitBurst per \"damaged\" event (Jiean's choice)"},
               {"label": "HIT_OFFSET", "value": "(0, −40): base-disc centre → body (line 20)"},
               {"label": "Frees itself", "value": "on Dust.finished: measured 1.22–1.28 s (Revision 1)"}],
              ["R or play again: the event list shrinks, every live burst is freed (lines 38–40)"],
              "Effect A driver (spawn side); code beat, result B08."),
    footage("B08", "Turn four: both archers hit, about a second apart. When the second hit lands, the first burst has "
                   "almost faded from sight, but it is still alive. Two bursts alive at once, and the state test counted "
                   "exactly that: two, on the "
                   "frame of the second hit. The brief predicted that re-firing a single node would drop the second hit. "
                   "A new instance per hit avoids it.",
            PLAY_LABEL, "Result of B07: play P2 (turn 4, both hits) at real speed, then slow S2 at ¼ speed (2× crop), with the "
                        "state test's A3 overlap line on screen."),
    workbench("B09", "hit_burst.tscn: the flash, after tuning", "effects/hit_burst.tscn", 60, 66,
              f"The flash wasn't planned like this. The brief gave it point one two seconds. {NAME} watched it in the "
              "game and wrote: I can barely realize it happens. So it was tuned, one setting per revision, with "
              "Claude's prediction written down before each edit. Lifetime, then size, then lifetime again. Line "
              "sixty-four now says one point oh eight seconds.",
              [{"label": "r1 (8aa178c)", "value": "lifetime 0.12 → 0.36"},
               {"label": "r2 (1079375)", "value": "scale_amount_min / _max 1.25 → 3.0 (lines 83–84)"},
               {"label": "r3 (cc9e1ee)", "value": "lifetime 0.36 → 1.08"}],
              ["TUNING.md · one setting per revision · requested by Jiean"],
              "Effect A tuning; code beat, result B10."),
    still("B10", "RESULT",
          f"{NAME}'s strips, with the same fixed seed in every row. Revision one, three times longer, and frame twelve "
          "barely changed. Claude had predicted \"still clearly red\", and was wrong. The flash is the first child, so "
          "the splinters and the dust are drawn on top of it. Revision two, about two and a half times larger, gets out from under "
          f"them. Revision three keeps the glow for about a second. {NAME} kept both.",
          "FIXTURE · hit_burst_preview.tscn · fixed seed · Jiean's Movie Maker captures, 30 fps",
          "Result of B09: captures/hit_burst/r0..r3 frames 10, 12, 15, 20, 30; Jiean's words verbatim (TUNING.md).",
          evidence=True),
    workbench("B11", "arrow_trail.tscn: the streak", "effects/arrow_trail.tscn", 87, 101,
              "Effect B is two GPU particle nodes, Streak and Wisps. Godot has a trail setting, and on the "
              "Compatibility renderer it draws nothing at all, with a warning. That was measured before the brief was "
              "written. So line ninety-nine keeps it off, and line ninety-eight does the work: local coords off. The "
              "node follows the arrow, and every particle stays where it was dropped.",
              [{"label": "Measured (CHANGE-BRIEF §0)", "value": "trail_enabled = true: nothing drawn"},
               {"label": "Godot printed", "value": "WARNING: The Compatibility renderer does not support particle "
                                                    "trails."},
               {"label": "Written by", "value": "claude -p agent, session 2b (de4f389)"}],
              ["The trail = world-space emission from an emitter that follows the arrow tip"],
              "Effect B scene; code beat, result B12."),
    footage("B12", "The arrow flies two squares, and the streak draws its arc behind it. Look closely: it's a row of "
                   "dots, about twenty to twenty-five pixels apart. Line ninety-five: the GPU node steps thirty times a "
                   f"second, and each step leaves one dot. The brief predicted this failure. {NAME} looked, and called "
                   "the path clear.",
            PLAY_LABEL, "Result of B11: play P2 (turn 4, both arrows) at real speed, then slow S2 and S3 (three arrows) at ¼ "
                        "speed (2× crop); Jiean's first look verbatim (TUNING.md)."),
    workbench("B13", "arrow_trail_driver.gd: follow, stop, free", "game/arrow_trail_driver.gd", 60, 79,
              "The trail's driver keeps one entry per arrow. While the arrow is in the game's list, the trail moves to "
              "its tip, with the game's own arc formula: line sixty-nine. On the frame the arrow leaves the list, both "
              "emitters stop, line seventy-four, and a countdown starts: the wisps' lifetime, seven tenths of a second "
              "of game time. Then the node is freed. A new arrow gets a new trail.",
              [{"label": "tip_of (lines 43–47)", "value": "from.lerp(to, s) + (0, −ARROW_ARC·4·s·(1−s)), main.gd:718-721"},
               {"label": "Free timer", "value": "longest emitter lifetime, read from the scene: 0.7 s"},
               {"label": "Written by", "value": "claude -p agent, session 3b; plan approved by Jiean (e1e151d)"}],
              ["Reads main._arrows; never writes it"],
              "Effect B driver; code beat, result B14."),
    footage("B14", "The arrow lands. Emission stops, the dots shrink away from the oldest end, a few wisps hang on, and "
                   "the burst takes over at the target. Pause in mid-flight, and the arrow and its trail freeze together. "
                   "Unpause, and both carry on. The test found one surprise in this hand-over. We'll get to it.",
            PLAY_LABEL, "Result of B13: slow S2 (the player's arrow lands, 2× crop), then play P5 (run 3: P mid-flight, held 5 s)."),
    workbench("B15", "arrow_trail.tscn: the wisps", "effects/arrow_trail.tscn", 64, 83,
              "The wisps carry the feature the CPU node doesn't have: turbulence, line seventy-nine. Each wisp gets an "
              "influence between point one and point two, so it drifts in a noise field, while damping slows it down. "
              f"After the first strip, {NAME} chose stronger wisps: the colour ramp went from a pale brown at "
              "forty-five percent to the streak's own colour at seventy.",
              [{"label": "Effect B r1 (c3bbb9e)", "value": "Gradient_wisps (line 59): #9A8466 α 0.45 → #6E5A44 α 0.7"},
               {"label": "Chosen by", "value": "Jiean, of two options (\"Stronger wisps\")"},
               {"label": "GPU-only", "value": "CPUParticles2D has no turbulence"}],
              ["TUNING.md · prediction committed before the edit (f8cb529)"],
              "Effect B wisps and turbulence; code beat, result B16."),
    still("B16", "RESULT",
          "Revision zero above, revision one below, same seed. In flight, almost no difference: each wisp hides behind "
          "the streak dot it was born with. After the landing, at frames twenty-six and thirty-one, the puffs stay "
          "visible along the arc, where before they had nearly gone. The curl of the turbulence doesn't show in stills. "
          f"{NAME}'s verdict: " + Q["b_r1_verdict_spoken"],
          "FIXTURE · arrow_trail_preview.tscn · seed 71 · Jiean's Movie Maker captures, 30 fps",
          "Result of B15: captures/arrow_trail/r0, r1 frames 16, 21, 26, 31; Claude's pixel count (TUNING.md); "
          "Jiean's verdict verbatim.", evidence=True),
    workbench("B17", "test_hit_burst_config.gd: reading the scene as text", "tests/test_hit_burst_config.gd", 127, 140,
              "Now the tests. The configuration tests load each scene and read every value back against the brief: one "
              "hundred seven checks for the burst, one hundred thirty-five for the trail. This part reads the scene as "
              "plain text, line by line, looking for Godot three names, like initial velocity without its min. Why read "
              "the text? Because an old name might load without a word.",
              [{"label": "FORBIDDEN_KEYS (line 80)", "value": "initial_velocity, scale_amount, damping, "
                                                              "angular_velocity, angle, flag_align_y, …"},
               {"label": "Read-back", "value": "every §1 value: n.get(prop) == brief value (lines 145–149)"},
               {"label": "Written by", "value": "claude -p agent, session 2a (cb9830b)"}],
              ["./scripts/run-test.sh test_hit_burst_config.gd 60"],
              "Config test; code beat, result B18."),
    still("B18", "RESULT",
          f"{NAME} tested the tests. Mutation one: write initial velocity, the Godot three name, on the splinters. The "
          "scene loaded with no error and no warning, and the value read back as zero. Two checks failed: the text scan "
          f"and the read-back. In the game, {NAME} saw almost nothing wrong, only a flash that seemed to fade earlier. "
          "That's why it needs a test. Mutation two: one value changed, exactly one check failed.",
          "HEADLESS CHECK OUTPUT · recorded reports, no rendering",
          "Result of B17: evidence/a6/mutations/mutation-1.log, mutation-2.log (TEST-REPORT A6.3); Jiean's words.",
          evidence=True),
    workbench("B19", "test_arrow_trail_state.gd: the stop against the hit", "tests/test_arrow_trail_state.gd", 561, 570,
              "The state tests play the game with real key presses at sixty frames a second, and check every frame "
              "against the rules. This check compares each trail's stop with the hit it leads to. The brief said: within "
              "one frame. The agent's first run measured zero, minus two, zero, zero, minus two. Up to two frames early.",
              [{"label": "Every frame", "value": "sampled by a node with process_priority 1000, after main and the "
                                                 "drivers"},
               {"label": "Route", "value": "tests/fixtures/win_route.json through root.push_input()"},
               {"label": "Written by", "value": "claude -p agent, session 3b; bound revised by Claude Code (1268b40)"}],
              ["./scripts/run-test.sh test_arrow_trail_state.gd 60"],
              "State test; code beat, result B20."),
    still("B20", "RESULT",
          "The agent didn't widen the bound to make it pass. It left the check failing, and reported it. The brief was "
          "wrong, so the brief was corrected first, in a dated revision, and only then the test: thirty-one of "
          "thirty-one. Why two frames? The arrow's clock and the hit cue advance in different places. Game timing was "
          "out of scope, so that stays open. And no headless run draws a single particle.",
          "HEADLESS CHECK OUTPUT · recorded reports, no rendering",
          "Result of B19: evidence/a6/step5b (30/31), CHANGE-BRIEF Revision 1 item 3, evidence/a6/final (31/31).",
          evidence=True),
    workbench("B21", "cost_effects.gd: timing a frame", "tests/cost_effects.gd", 76, 86,
              "The price, first without a screen. The agent's script times each frame from a node that runs last, line "
              "seventy-seven. Six hundred frames, twice, for each case: an empty scene, the game with no effects, two "
              "bursts alive the whole time, and two trails in flight. It reports the means, and leaves the verdict to the "
              "reader.",
              [{"label": "Cases", "value": "empty · game, effects off (control) · Effect A ×2 · Effect B ×2"},
               {"label": "Samples", "value": "2 rounds × 600 frames per case, after 90 warm-up frames"},
               {"label": "Written by", "value": "claude -p agent, session 7 (f0e5977), committed unedited"}],
              ["./scripts/run-test.sh cost_effects.gd 60"],
              "Headless price; code beat, result B22."),
    still("B22", "RESULT",
          "Above the control: about eight thousandths of a millisecond for the bursts, and almost seven for the trails. "
          f"{NAME} had predicted zero for the GPU trail. It isn't free on the CPU: the node still moves every frame, "
          "and headless it costs about as much as the CPU burst. Both are far under the budget of point two "
          "milliseconds.",
          "RECORDED LOG · evidence/a6/step7 · chart redrawn from it",
          "Result of B21: TEST-REPORT A6.6 headless table; CHANGE-BRIEF §7 predictions and budget.", evidence=True),
    workbench("B23", "price_effects.gd: the GPU time", "previews/price_effects.gd", 112, 123,
              "For the graphics card, a fixture holds each case at its peak. Line one fifteen reads the viewport's "
              f"measured GPU time every frame, and once a second it prints the mean. {NAME} read the Visual Profiler in "
              "the editor. Claude ran the same fixture unattended, each case held twice, with and without vsync.",
              [{"label": "Fixture", "value": "price_effects.tscn: 0 off · 1 Effect A ×2 · 2 Effect B ×2 · V vsync"},
               {"label": "Sweep", "value": "-- --sweep=8 [--vsync=off]: cases 0,1,2,0,1,2, 8 s each, first 2 s dropped"},
               {"label": "Written by", "value": "Claude Code (ac38e82, 67d0b30)"}],
              ["Display 180 Hz · RTX 3070 Ti Laptop GPU · OpenGL 3.3"],
              "GPU price; code beat, result B24."),
    still("B24", "RESULT",
          f"{NAME}'s readings: the three cases overlap completely. The graph swings by about one and a half "
          "milliseconds, and the effects cost a few thousandths. Only the means separate them: three thousandths of a "
          f"millisecond for the bursts, seven for the trails. Under budget, and two to three times {NAME}'s "
          "predictions. With vsync on, every case reads one hundred eighty frames a second, as "
          f"{NAME} predicted. " + Q["price_conclusion_spoken"],
          "HUMAN CHECK · Jiean, Visual Profiler  |  RECORDED LOGS · evidence/a6/gpu",
          "Result of B23: TEST-REPORT A6.6 (Jiean's readings, the sweep, Jiean's conclusion verbatim).", evidence=True),
    workbench("B25", "particles_generated.gdshader: Jiean's lines", "shaders/particles_generated.gdshader",
              A_R[0], A_R[1],
              f"Last, the process shader. {NAME} converted the wisps' material into a shader in the editor, and saved "
              "it unedited. Nearly five hundred lines, and the game doesn't use it. It's a particles shader: a start "
              "function for each new particle, and a process function for every step. " + Q["a67_rows_spoken"],
              # Jiean's rows for start() and process(), then the rows inside the excerpt; the rest listed below them
              [{"label": r["what"].strip("`"), "value": f"line {r['lines']}"} for r in Q["a67_rows"]
               if r["what"] in ("`start()`", "`process()`") or A_R[0] <= int(r["lines"]) <= A_R[1]],
              ["Jiean's other rows (TEST-REPORT A6.7): " + " · ".join(
                  f"line {r['lines']} ({(r['line'] if r['lines'] == '441' else r['what']).replace('`', '')})"
                  for r in Q["a67_rows"]
                  if r["what"] not in ("`start()`", "`process()`") and not A_R[0] <= int(r["lines"]) <= A_R[1]),
               "Generated by the Godot editor from the Wisps ParticleProcessMaterial; saved by Jiean, unedited"],
              "Process shader; code beat, result B26. Lines are Jiean's (TEST-REPORT A6.7).",
              label="Generated by the Godot editor from the Wisps material, saved by Jiean, unedited · not used by the "
                    "game"),
    still("B26", "RESULT",
          "What that code does, on screen: each wisp is born with its own speed, drifts slowly upward, because its "
          "gravity points up, swells, and fades out. The game runs the material, not this file, but the file spells it "
          f"out line by line. {NAME}'s split: " + Q["a67_split_spoken"],
          "FIXTURE · arrow_trail_preview.tscn r1 wisps, enlarged  |  Jiean's answer, TEST-REPORT A6.7",
          "Result of B25: captures/arrow_trail/r1 frames 21, 26, 31 (wisps enlarged); Jiean's split verbatim.",
          evidence=True),
    still("BCRD", "CREDITS",
          f"Who did what. {NAME} chose both effects, their jobs and the retrigger rule, wrote every prediction, the "
          "budget and the six answers, ran the mutations, captured every strip, read the profiler, and judged every "
          "revision. Claude agents, working from the brief, wrote the scenes, the drivers, the tests and the price "
          "script; Claude Code reviewed them, made the tuning edits "
          f"{NAME} asked for, and built the price fixture. Caught on the way: a bound in the brief that was wrong, a "
          f"prediction that ignored draw order, and a cleanup loop that deleted a strip, which {NAME} captured again. "
          "No image files: the textures are gradients inside the scenes. Source shown: tag a6.",
          "", "Human and AI contributions (SOURCES.md A6), mistakes caught (FRICTIONAL A6, TUNING), textures."),
    voice({"beat_id": "BVDT", "act": "VERDICT",
           "narration_text": "Verdict. Checked: every setting reads back, both mutations were caught, the rules held on "
                             "every frame at sixty frames a second, two bursts overlap on a two-hit turn, and both effects "
                             "cost a few thousandths of a millisecond, far under budget. Wrong: the brief's one-frame "
                             f"bound, Claude's first flash prediction, and {NAME}'s price predictions, off by less than a "
                             "hundredth of a millisecond. Uncertain: why the trail stops up to two frames early, what the "
                             "profiler's four to six milliseconds with vsync on contain, and whether a hidden trail keeps "
                             f"simulating. In play, {NAME}'s answer: " + Q["playtest_reads_spoken"] + " Next: turn the "
                             "dotted streak into a line, and predict the gap first.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-reveal",
                    "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
                        "artifactTitle": "Verdict", "artifactHeading": "Two Lane Tactics particle effects at tag a6.",
                        "brandLabel": "@NikBearBrown",
                        "artifactLines": [
                            "Checked: config 107/107 and 135/135 · both mutations exit 1 · state 31/31 and 31/31 at "
                            "60 fps · two bursts alive on a two-hit turn · +0.003 to +0.008 ms, budget 0.2 ms.",
                            "Wrong: the brief's ±1-frame bound (measured 0 to −2) · Claude's r1 flash prediction · "
                            "Jiean's price predictions (off by < 0.01 ms: three low, one high).",
                            "Uncertain: why the trail stops up to 2 frames early · the profiler's 4–6 ms with vsync on · "
                            "whether a hidden trail keeps simulating.",
                            "In play (Jiean): " + Q["playtest_reads"],
                            "Next step: raise the streak's fixed_fps, predict the gap first."]}}},
           "role_note": "Verdict: checked vs wrong vs uncertain vs human judgement vs next step."}),
    voice({"beat_id": "BHTF", "act": "HANDOFF",
           "narration_text": "Your turn. Pick one setting, and predict before you look. Here's a prompt to start with: "
                             "raise fixed F P S on the streak from thirty to sixty; before changing anything, predict the "
                             "gap between the dots for a two-square shot of point three five seconds; then capture a strip "
                             "and compare. It's one small change, and a direct test of why the trail is dotted. If the "
                             "dots don't land where you predicted, that isn't a failure. That's a finding. I'm Liam, in "
                             "for Bear.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
                    "label": "Reconstructed interface — suggested prompt, not a past run",
                    "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                        "greeting": "Your turn.", "topic": "WALKER · YOUR TURN", "segment": "One Setting, One Prediction",
                        "command": "Raise fixed_fps on the Streak in my arrow trail from 30 to 60. Before you change "
                                   "anything, help me predict the gap between the dots for a two-square shot that lasts "
                                   "0.35 seconds. Then I'll capture a strip and we compare.",
                        "runningText": "paste this into Claude…", "folderLabel": "@NikBearBrown",
                        "modelLabel": "Claude", "effortLabel": "High"}}},
           "role_note": "Your Turn: one bounded change + prediction + strip; Liam signs off."}),
    voice({"beat_id": "BOUT", "act": "OUTRO", "kind": "outro_voice",
           "role_note": "OUTRO-LOCK: ClaudeTitleOutro, exact title, @NikBearBrown, slug-seeded mascot, no subline. "
                        "Spoken, never scored; 1.0 s silent tail.",
           "narration_text": f"{TITLE}. At Nik Bear Brown.", "tail_hold_s": 1.0,
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "mascot-title",
                    "remotion": {"pattern": "ClaudeTitleOutro", "props": {
                        "title": TITLE + ".", "slug": SLUG, "handle": "@NikBearBrown", "subline": ""}}}}),
]

metadata = {
    "title": TITLE, "slug": SLUG, "topic": "WALKER · GODOT GAMEDEV", "kind": "godot-gamedev", "skill": "godot-gamedev",
    "modifier": "walker", "brand": "claude-liam", "audience": "Course reviewers and makers following Walker/Claude workflows",
    "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx", "palette": "claude",
    "style_preset": "claude", "ground": "#FAF9F5", "aspect_ratio": "16:9", "fit": "crop", "captions": False,
    "channel": "@NikBearBrown", "folderLabel": "@NikBearBrown", "greeting": "Hello, Liam",
    "persona": "Liam (in for Bear)", "presenter": "Liam (in for Bear)", "in_for_bear": True,
    "script_status": "approved by Jiean on 2026-11-08 ('Approve as is', SCRIPT-DRAFT.md); bracketed quotes filled "
                     "verbatim from tag a6",
    "pronunciation_note": "Narration spells Jiean as 'Jay-Ann' for the voice only (Jiean's choice for the A5 film). "
                          "Screen text keeps 'Jiean'.",
    "teaching_contract": "code-then-result-v1",
    "game": {"name": "walker-lane-tactics-jiean-yin", "repository": "https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin",
             "source_revision": REV, "engine": "Godot 4.7.2.stable.official.ed1daf0bf", "renderer": "Compatibility"},
    "audio_policy_note": "Narration only. Engine captures carry no audio track in the film; the outro card carries only "
                         "Liam's voice.",
    "labels": {"engine": "SCRIPTED KEY PRESSES · REAL GODOT RENDER", "slow": "¼ SPEED · captured at 120 fps",
               "fixture": "FIXTURE · Jiean's Movie Maker captures",
               "reconstruction": "Illustrative reconstruction of the Claude interface — not a transcript",
               "editor": "Godot editor reconstruction (printed by GodotDevWorkbench)",
               "headless": "HEADLESS CHECK OUTPUT · recorded reports, no rendering"},
}

for b in beats:
    if PENDING in b["narration_text"]:
        if not DRAFT:
            raise SystemExit(f"{b['beat_id']}: a spoken excerpt is missing from quotes.json")
        b["narration_text"] = "[PLACEHOLDER] " + b["narration_text"]
(REEL / ("beat_sheet.draft.json" if DRAFT else "beat_sheet.json")).write_text(json.dumps({"metadata": metadata, "beats": beats}, indent=2, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
print(len(beats), "beats;", sum(len(b["narration_text"].split()) for b in beats), "words")
