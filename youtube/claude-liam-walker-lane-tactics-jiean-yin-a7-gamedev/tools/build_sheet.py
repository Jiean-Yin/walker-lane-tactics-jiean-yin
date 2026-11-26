"""Write beat_sheet.json for the A7 film from the script Jiean approved (SCRIPT-DRAFT.md, 2026-11-26, "Approve as is").

Code excerpts are read from the isolated copy of tag a7 (CAPTURE/a7/godot), never typed, so each matches its file.
Jiean's words are checked verbatim against the tag copy's documents before anything is written (QUOTES below).
Narration spells Jiean's name "Jay-Ann" for the voice only; everything on screen keeps "Jiean". Footage segment
ranges are filled in later by tools/set_segments.py.
Usage (reel folder): CAPTURE=<capture-copy> python tools/build_sheet.py
"""
import json
import os
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
A7 = Path(os.environ["CAPTURE"]) / "a7"
GAME = A7 / "godot"
SLUG = "claude-liam-walker-lane-tactics-jiean-yin-a7-gamedev"
TITLE = "Lane Tactics: A Waving Flag and a Committed Shot"
NAME = "Jay-Ann"  # voice spelling only
REV = "tag a7 = 37c4698 (tree dd91e92)"

# Jiean's words, verbatim (typos kept on screen), each with the tag file it must appear in.
QUOTES = {
    "seam": ("TEST-REPORT.md", "Smooth steady ripple."),
    "action": ("TEST-REPORT.md", "All distinct. While drawing, the archer lean back with bows moving, and retreating "
                                 "clearly after the arrow flying away."),
    "registration": ("TEST-REPORT.md", "Stand still while the cloth waves."),
    "disagree": ("TEST-REPORT.md", "Claude considered leaning back and bow moving angle too small for human eyes to "
                                   "catch, but I think they are clear enough."),
    "r0": ("TUNING.md", "The bow seems to leave the archer's hand while retreating the bow though."),
    "r1": ("TUNING.md", "This time the bow stays in arhcer's hand, and it is still clear to see the bow lowering a "
                        "the end."),
    "r1_verdict": ("TUNING.md", "Keep: the bow now stays in the hand."),
    "summary": ("SUBMISSION.md", "I chose and measured the exact number of adjustment, and predicted the possible "
                                 "failure to avoid. I approved most of the adjustments suggesstions by Claude. Every "
                                 "test were followed by my own human check."),
}
for k, (f, q) in QUOTES.items():
    if q not in (A7 / f).read_text(encoding="utf-8"):
        raise SystemExit(f"quote '{k}' is not verbatim in tag a7's {f}; Jiean's words are never written here")
(REEL / "capture").mkdir(exist_ok=True)
(REEL / "capture/quotes.json").write_text(json.dumps({"source_revision": REV, "quotes": {
    k: {"file": f, "text": q} for k, (f, q) in QUOTES.items()}}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def Qt(k):
    return QUOTES[k][1]


def lines(rel, a, b):
    text = (GAME / rel).read_text(encoding="utf-8").split("\n")
    return "\n".join(text[a - 1:b])


def voice(b):
    b.setdefault("voice", "am_onyx")
    b.setdefault("engine", "kokoro")
    return b


def workbench(bid, title, rel, a, b, narration, notes, output, role, label=None):
    props = {"mode": "code", "title": title, "project": "Lane Tactics", "path": "res://" + rel,
             "source": f"godot/{rel} · lines {a}–{b} · tag a7", "code": lines(rel, a, b), "startLine": a,
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


PLAY_LABEL = "SCRIPTED KEY PRESSES · REAL GODOT RENDER|main.tscn @ tag a7, isolated copy · Movie Maker, 30 fps · no audio"
SLOW_LABEL = ("¼ SPEED · REAL GODOT RENDER|the same turn captured at 120 fps, played at 30 · main.tscn @ tag a7 · "
              "scripted key presses")
HEADLESS = "HEADLESS CHECK OUTPUT · recorded reports, no rendering"

beats = [
    voice({"beat_id": "B00", "act": "ASK",
           "narration_text": f"Hello, this is Liam, in for Bear. {NAME} Yin's game is Lane Tactics: archers on a five-lane "
                             "board, where you win by reaching the enemy's back row. This assignment adds two animations: "
                             "a flag that loops, and a shot that commits. The prompt on screen is an illustrative "
                             "reconstruction.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
                    "label": "Illustrative reconstruction of the Claude interface — not a transcript",
                    "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                        "greeting": "Hello, Liam", "topic": "WALKER · GODOT GAMEDEV",
                        "segment": "A Waving Flag and a Committed Shot",
                        "command": "Please use Walker to convert my game design document about Lane Tactics — archers "
                                   "on a five-lane board, simultaneous orders, win by reaching the enemy's back row — "
                                   "into two animations: a goal flag that waves from a sprite sheet, and an archer's "
                                   "shot that moves a rig through startup, active and recovery. Test both, and show me "
                                   "what a headless run cannot.",
                        "runningText": "reading CHANGE-BRIEF.md…", "folderLabel": "@NikBearBrown",
                        "modelLabel": "Claude", "effortLabel": "High",
                        "output": ["test_flag_readback 43/43 · test_shoot_readback 51/51",
                                   "test_anim_states 51/51 · test_shoot_edges 102/102 at 60 fps",
                                   "Source shown: tag a7"]}}},
           "role_note": "walker B00: ClaudeComposerAsk; prompt begins 'Please use Walker to convert my game design "
                        "document about'; illustrative reconstruction, labelled. Result lines are recorded numbers "
                        "(TEST-REPORT A7.3-A7.5)."}),
    voice({"beat_id": "B01", "act": "BLUF", "lead_silence_s": 0.8,
           "narration_text": "Two animations: a flag that waves, and a shot with three phases. Every key is a time, but "
                             "the timing was designed in frames, sixty to the second, and only then turned into keys.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
                    "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
                        "text": "Two animations for Lane Tactics:\na flag that waves,\nan archer that shoots.\nSeconds "
                                "decide the timing.",
                        # one word: the component matches single words only ("Seconds" -> "Frames")
                        "triggerWords": "Seconds", "replacementWords": "Frames", "fontSize": 80,
                        "lineSpacing": 2.2, "align": "center", "seed": "lane-tactics-a7-1126", "mistakeRate": 2,
                        "hesitateWithin": 0, "hesitateBetween": 1, "charMs": 8, "ink": "#3D3929", "accent": "#D97757",
                        "bg": "#FAF9F5"}}},
           "role_note": "walker B01: hesitant-writer summary; 'Seconds decide' -> 'Frames decide' is the film's point "
                        "(feel designed in frames).",
           "qc": {"sparse_by_design": True,
                  "sparse_reason": "Hesitant-writer BLUF bookend: centred serif lines typed on cream."}}),
    still("B02", "SETUP",
          "One clip loops, one commits. The flag tells a new player where the goal is. It's a found sheet, played by a "
          "frame track. The shot tells you who is shooting, and when: a rig of three parts cut from the archer's "
          "drawing, moved by keys. Startup, active, recovery: twelve, twenty-one and fifteen frames.",
          "", "Setup: the two clips, their jobs, routes, the sheet's licence, the phase lengths (CHANGE-BRIEF §1, §4)."),
    workbench("B03", "wave.tres: a clip is a list of keys", "animations/wave.tres", 11, 24,
              "A clip is a list of keys, not a movie. This one keys a single integer: the sprite's frame, line "
              "seventeen. Four keys, an eighth of a second apart, and the step is one frame period at eight frames a "
              "second. The length is half a second, four intervals, so there's no key at the end: the last frame is "
              "three, and the wrap goes straight back to zero. Which picture is frame three? The slicing decides, not "
              "the image.",
              [{"label": "flag_red.png", "value": "500 × 249 → hframes 4 × vframes 1 → cells of 125 × 249"},
               {"label": "Seam rule", "value": "no key at length; last key → length = one interval"},
               {"label": "Written by", "value": "claude -p agent, session 3 (b21c881)"}],
              ["Sheet: Flag Animation Sheet by Fokko, CC0"],
              "wave frame track; code beat, result B04."),
    footage("B04", "The sheet as downloaded: four cells, left to right. In the game, the flag stands on the table "
                   "beside the enemy's back row and ripples, about twice a second, from the title screen on. "
                   f"{NAME} watched it through more than five wraps: smooth, steady ripple.",
            PLAY_LABEL, "Result of B03: play P0_title (the flag waving on the title card) at real speed, with "
                        "flag_red.png and its 4 × 1 grid inset; Jiean's A7.9 words."),
    workbench("B05", "wave.tres: the registration fix", "animations/wave.tres", 26, 36,
              "Found sheets drift. In this one, the pole sits at a different place in each cell, by up to five pixels. "
              "Editing the sheet would make it a derivative. So a second track keys the sprite's offset, on the same "
              "four times: zero, minus four, minus two, plus one. The pole should stand still while the cloth moves.",
              [{"label": "Pole's left edge", "value": "x = 4, 8, 6, 3 in cells 0–3 (ATTRIBUTION.md)"},
               {"label": "Offset.x", "value": "0, −4, −2, +1 source px, discrete"},
               {"label": "One authority", "value": "the flag's AnimationPlayer writes frame and offset"}],
              ["The sheet is never edited"],
              "wave offset track; code beat, result B06."),
    still("B06", "RESULT",
          f"Thirteen frames, cropped from {NAME}'s strip, with a line drawn at the pole. The cloth changes shape; the "
          f"pole doesn't move. Its darkest column sits on the same screen pixel in all thirteen. {NAME}'s check: the "
          "pole stands still while the cloth waves.",
          "FIXTURE CROPS · 13 frames of Jiean's r1 strip · guide line drawn on the strip",
          "Result of B05: captures/flag_registration_r1.png (tag a7); Jiean's A7.11 words.", evidence=True),
    workbench("B07", "test_flag_readback.gd: frame range", "tests/test_flag_readback.gd", 163, 177,
              "The read-back test reads the clip back against the brief. Line one seventy-three: every frame key has "
              "to be a cell the sheet actually has, fewer than horizontal times vertical frames. Why test that? A key "
              "for a cell that doesn't exist loads without a word.",
              [{"label": "Also checked", "value": "discrete updates · step 0.125 · LOOP_LINEAR · the seam rule"},
               {"label": "Result", "value": "43/43 at 60 fps (TEST-REPORT A7.3)"},
               {"label": "Written by", "value": "claude -p agent, session 3; index guard by Claude Code (dc17389)"}],
              ["Key times compared within half a frame, never with =="],
              "Flag read-back; code beat, result B08."),
    still("B08", "RESULT",
          "Break it on purpose, in a throwaway copy. Key a fifth cell: the game would show a blank frame with no "
          "error, and the test fails on exactly that check. Turn the loop off: the flag would wave once and stop, and "
          "the loop-mode check fails. And on the first try, the fifth cell also crashed a later check in the test. "
          "That index is now guarded.",
          HEADLESS, "Result of B07: mutations 2 and 3 (evidence/a7/step6/mutations/), exit 1 each.", evidence=True),
    still("B09", "SETUP",
          "Feel is designed in frames. The game already fixes how long a shot takes: point two seconds to draw, point "
          "three five while the arrow flies, point two five to recover. At sixty frames a second: twelve, twenty-one, "
          f"fifteen. {NAME} measured a slow-motion archer, frame by frame, to space the motion inside each phase. The "
          "real archer holds at full draw for longer than the whole of our shot. The game skips that. "
          f"{NAME} put the bow drop at frame forty, by eye.",
          "", "The phase table (CHANGE-BRIEF §4; revisions 1 and 4). The reference video is not shown."),
    workbench("B10", "shoot.tres: keys from the phase table", "animations/shoot.tres", 31, 44,
              "The table becomes keys. Line thirty-three: the step is one sixtieth. The default is one thirtieth, and "
              "frame thirty-three falls between two of those. Line forty-one: a key at every boundary, each time a "
              "frame divided by sixty. Three tracks move the rig: the whole archer recoils, the upper body leans, and "
              "the bow turns at the hand.",
              [{"label": "Key time = frame ÷ 60", "value": "f0 0.0 · f12 0.2 · f33 0.55 · f40 0.666667 · f48 0.8"},
               {"label": "Rig", "value": "Mount > Rig > Lower, Upper > UpperSprite, Bow > BowSprite"},
               {"label": "Written by", "value": "claude -p agent, session 4 (0e60554)"}],
              ["LOOP_NONE · length 0.8 s = 48 frames"],
              "shoot keys; code beat, result B11."),
    footage("B11", "One shot at real speed, then at a quarter. Startup: the archer leans back and the bow comes up "
                   "level. The arrow leaves. Active: the archer eases forward through the follow-through while the "
                   "arrow flies. Recovery: a short hold after the hit, then the bow drops, and the archer is back in "
                   f"the idle pose. {NAME}'s check: all distinct.",
            PLAY_LABEL, "Result of B10: play P2 (turn 4, the enemy's shot) at real speed, then slow S2 (same shot) at "
                        "¼ speed, cropped on the shooting archer."),
    workbench("B12", "piece.gd: one authority", "game/piece.gd", 109, 116,
              "One authority: exactly one thing writes each animated node. The clip writes the rig's three pivots, and "
              "nothing else. Only the piece script starts it: when the pose becomes draw, line one thirteen looks up "
              "its clip, line one fifteen plays it, and line one sixteen applies frame zero at once. Line one twelve "
              "stops the last one first, so no old pose carries over. Facing lives one node up, so the clip and the "
              "script never touch the same node.",
              [{"label": "Rig, Upper, Bow", "value": "written only by the rig's AnimationPlayer (shoot)"},
               {"label": "Mount", "value": "place, facing, visibility: written only by piece.gd"},
               {"label": "Written by", "value": "claude -p agent, session 5; plan approved by Jiean (2882336)"}],
              ["POSE_CLIPS: draw → shoot; every other pose → no clip"],
              "One authority; code beat, result B13."),
    footage("B13", "Now interrupt it. Pause in the startup, during the flight, and after the hit: each time, the "
                   "archer holds mid-motion, and carries on from the same pose when unpaused. Press R in the middle of "
                   "a shot: the archers are rebuilt, and nothing from the old shot comes back.",
            PLAY_LABEL, "Result of B12: play P4 (run 2 turn 4: P in e1's startup, in e1's active phase, in p1's "
                        "recovery) and P5 (run 3: R in e1's active phase)."),
    workbench("B14", "piece.gd: the clip's clock", "game/piece.gd", 167, 182,
              "Two clocks. A player can advance on the process tick, or the physics tick, or not on its own at all. "
              "This one is manual. Line one eighty-two: the piece advances it by the game's own time, from inside the "
              "game's update. So when the game pauses, the clip stops. The flag's player is different: it runs on the "
              "process tick, in real time.",
              [{"label": "shoot", "value": "ANIMATION_CALLBACK_MODE_PROCESS_MANUAL · advance(dt), game time"},
               {"label": "wave", "value": "ANIMATION_CALLBACK_MODE_PROCESS_IDLE · real time"},
               {"label": "Gameplay reads", "value": "_arrows on the process tick (main.gd:162-171); no physics tick"}],
              ["tick() is called only while the game is not paused (main.gd:166-171)"],
              "Two clocks; code beat, result B15."),
    footage("B15", "Paused: the archers freeze, the flag keeps waving. That's by design: wind isn't part of the game. "
                   "And the two clocks agree to within a frame. On the arrow's first frame, the clip is exactly point "
                   "two seconds ahead of the arrow: one sixtieth of a second ahead of the cue clock, because it "
                   "advances right after the cue, in the same frame. No physics tick anywhere.",
            PLAY_LABEL, "Result of B14: play P4 (a pause: archers frozen, the flag waving), with the recorded "
                        "test_anim_states line (evidence/a7/step5) burned in."),
    workbench("B16", "test_shoot_readback.gd: tracks resolve", "tests/test_shoot_readback.gd", 86, 102,
              "The rig's read-back resolves every track to a real node and property. It branches on track type: a 3D "
              "transform track names a bone, not a property, so a plain check would call every bone track broken. "
              "Here, a value track has to name a property the node really has, line ninety-nine.",
              [{"label": "Also checked", "value": "keys at f0/12/33/40/48 within half a frame · step 1/60 · LOOP_NONE"},
               {"label": "Result", "value": "51/51 at 60 fps (TEST-REPORT A7.3)"},
               {"label": "Written by", "value": "claude -p agent, session 4 (0e60554)"}],
              ["track_problems() is a test helper, not a Godot method"],
              "Rig read-back; code beat, result B17."),
    still("B17", "RESULT",
          "Rename one property in the clip, a single letter, and in the game the upper body would just stop leaning. "
          "No error, no warning: a track that points at nothing is silently inert. The read-back names the track and "
          "the missing property. Mutation four empties the import cache, and this one passes, as predicted: the rig "
          "is keyed in text, so no import setting can be lost.",
          HEADLESS, "Result of B16: mutations 1 and 4 (evidence/a7/step6/mutations/).", evidence=True),
    workbench("B18", "shoot.tres: the bow key, tuned", "animations/shoot.tres", 61, 68,
              f"Strips are where the motion gets judged. {NAME} watched the first strip before Claude read it, and "
              "wrote: the bow seems to leave the archer's hand. Claude found why: the bow turns at the hand, but the "
              "rig cuts the drawing at one column, so the forearm and the string stay behind. One change: the bow's "
              "last key, line sixty-eight, from twenty degrees to eight.",
              [{"label": "Tuning r1 (TUNING.md)", "value": "frame-48 bow key 20° → 8° (0.349066 → 0.139626 rad)"},
               {"label": "Approved by", "value": "Jiean, \"Approve r1\" (brief revision 4)"},
               {"label": "Read-back", "value": "expected values follow the brief (f05c97e)"}],
              ["One change per revision; prediction written before the edit"],
              "Tuning r1; code beat, result B19."),
    still("B19", "RESULT",
          "Revision zero above, revision one below. Up to frame twenty-nine, not one pixel changed. In the drop, the "
          "gap at the hand closes to about a pixel. Claude had worried that eight degrees might be too small to see. "
          f"{NAME} watched it in the game, and disagreed: the bow stays in the hand, and the lowering is still clear. "
          "Kept.",
          "FIXTURE · shoot_preview.tscn · Jiean's Movie Maker captures, 30 fps",
          "Result of B18: captures/shoot/r0 and r1, bow hand at 6×, frames 15, 29, 31, 33; Jiean's words.",
          evidence=True),
    workbench("B20", "test_shoot_edges.gd: every boundary", "tests/test_shoot_edges.gd", 29, 38,
              "Edges. At every boundary of the table, frames zero, twelve, thirty-three and forty-eight, three "
              "interrupts, P, R and Enter, each arriving one frame before, on, and after. Thirty-six cases, and each "
              "one first proves its key landed on the frame it was aimed at.",
              [{"label": "Cases", "value": "4 boundaries × 3 offsets × 3 interrupts = 36"},
               {"label": "Result", "value": "102/102 at 60 fps (TEST-REPORT A7.5)"},
               {"label": "Written by", "value": "Claude Code, main session (ab95468)"}],
              ["Keys go in through Input.parse_input_event"],
              "Edge tests; code beat, result B21."),
    still("B21", "RESULT",
          "One hundred two out of one hundred two. Two findings on the way. One frame before the draw, the game is "
          "still waiting for the attack order: there, Enter is the order itself, so the first version of the test "
          "was wrong, and was fixed to match the game. And the game's own cues land a frame early or late, so the end "
          "pose shows for zero or two frames. Game timing was out of scope, so that stays as it is. None of this "
          "draws a single pixel.",
          HEADLESS, "Result of B20: test_shoot_edges 102/102 and the pins (evidence/a7/step6, evidence/a7/pins).",
          evidence=True),
    still("BCRD", "CREDITS",
          f"Who did what. {NAME} chose both clips, the sheet and the reference, measured its frames, wrote the phase "
          "table, the predictions and the answers, captured every strip, and judged every one, including the human "
          "checks. Claude agents, working from the brief, wrote the clips, the read-backs and the wiring. Claude Code "
          "reviewed them, wrote the pins, the edge tests and the preview, and made the one tuning change "
          f"{NAME} approved. Caught on the way: a recovery split that fell outside the clip, a capture folder that "
          "didn't exist, and an author email in a transcript, removed before anything was pushed. The flag sheet is by "
          "Fokko, CC0. Source shown: tag a7.",
          "", "Human and AI contributions (SOURCES.md A7), mistakes caught (FRICTIONAL A7), the sheet's licence."),
    voice({"beat_id": "BVDT", "act": "VERDICT",
           "narration_text": "Verdict. Checked: every track resolves, every key sits on its frame, both loop modes and "
                             "the frame range are pinned, three mutations fail their tests and the fourth passes for the "
                             "right reason, the pins didn't move, and a hundred and two edge cases hold. Wrong: where "
                             "Claude's rig cut the drawing, which split the bow from the hand at twenty degrees, and a "
                             "frame-before-the-draw assumption in a test. Uncertain: why the game's cues land a frame "
                             "off, and the recoil, still about a pixel and a half on screen. In "
                             f"{NAME}'s words: every test was followed by a human check. Next: make the release readable.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-reveal",
                    "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
                        "artifactTitle": "Verdict", "artifactHeading": "Two Lane Tactics animations at tag a7.",
                        "brandLabel": "@NikBearBrown",
                        "artifactLines": [
                            "Checked: read-backs 43/43 and 51/51 · mutations 1–3 exit 1, mutation 4 passes (keyed "
                            "rig) · pins 29/29 unchanged · edges 102/102 at 60 fps.",
                            "Wrong: the rig's cut split the bow from the hand at 20° (tuned to 8°) · the edge test's "
                            "first frame-before-the-draw assumption.",
                            "Uncertain: why the game's cues land ±1 frame · the recoil, about 1.5 screen px.",
                            "In Jiean's words: " + Qt("summary"),
                            "Next step: make the release readable; predict it first."]}}},
           "role_note": "Verdict: checked vs wrong vs uncertain vs human judgement vs next step."}),
    voice({"beat_id": "BHTF", "act": "HANDOFF",
           "narration_text": "Your turn. One key, and a prediction first. Here's a prompt to start with: raise the recoil "
                             "at frame thirty-three from six to eighteen pixels in the art; before changing anything, "
                             "predict how far that moves on screen, and on which strip frames. Then capture a strip and "
                             "compare. If the release still doesn't read, that isn't a failure. That's a finding. I'm "
                             "Liam, in for Bear.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
                    "label": "Reconstructed interface — suggested prompt, not a past run",
                    "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                        "greeting": "Your turn.", "topic": "WALKER · YOUR TURN", "segment": "One Key, One Prediction",
                        "command": "In shoot.tres, change the recoil key at frame 33 from 6 to 18 pixels in the art. "
                                   "Before you change anything, help me predict how many screen pixels that is at the "
                                   "rig's scale, and which strip frames should show it. Then I'll capture a strip and "
                                   "we compare.",
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
    "script_status": "approved by Jiean on 2026-11-26 ('Approve as is', SCRIPT-DRAFT.md); quotes verbatim from tag a7",
    "pronunciation_note": "Narration spells Jiean as 'Jay-Ann' for the voice only. Screen text keeps 'Jiean'.",
    "teaching_contract": "code-then-result-v1",
    "game": {"name": "walker-lane-tactics-jiean-yin", "repository": "https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin",
             "source_revision": REV, "engine": "Godot 4.7.2.stable.official.ed1daf0bf", "renderer": "Compatibility"},
    "audio_policy_note": "Narration only. Engine captures carry no audio track in the film; the outro card carries only "
                         "Liam's voice.",
    "labels": {"engine": "SCRIPTED KEY PRESSES · REAL GODOT RENDER", "slow": "¼ SPEED · captured at 120 fps",
               "fixture": "FIXTURE · Jiean's Movie Maker captures",
               "reconstruction": "Illustrative reconstruction of the Claude interface — not a transcript",
               "editor": "Godot editor reconstruction (printed by GodotDevWorkbench)",
               "headless": HEADLESS},
}

(REEL / "beat_sheet.json").write_text(json.dumps({"metadata": metadata, "beats": beats}, indent=2, ensure_ascii=False)
                                      + "\n", encoding="utf-8")
print(len(beats), "beats;", sum(len(b["narration_text"].split()) for b in beats), "words")
