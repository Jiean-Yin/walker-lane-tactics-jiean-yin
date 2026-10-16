"""Author beat_sheet.json for the Assignment 3 film (authoring record; later steps add measured fields in place).

Sources: CHANGE-BRIEF.md / FRICTIONAL.md / TEST-REPORT.md (Assignment 3 sections), BLENDER-NOTES.md,
tools/blender/*.py and godot/ at commit e415255, the student's footage in <footage>, capture run-02.
Usage (reel folder): python tools/build_sheet.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
SLUG = "claude-liam-walker-lane-tactics-jiean-yin-a3-gamedev"
TITLE = "Lane Tactics in 3D: A Piece, a Square, a Goal"
REV = "e415255"

FOOT = "STUDENT'S SCREEN RECORDING"
ENGINE = "SCRIPTED CAMERA · REAL GODOT RENDER|asset_diorama.tscn @ e415255 · no audio in this scene"


def V(bid, act, text, shot, **kw):
    b = {"beat_id": bid, "act": act, "narration_text": text, "voice": "am_onyx", "engine": "kokoro", "shot": shot}
    b.update(kw)
    return b


def own_video(segments, label, note, evidence=False):
    s = {"type": "VIDEO", "source": "own", "treatment": "none", "segments": segments, "label": label,
         "typography_note": note}
    return s


def code_beat(title, code, spark, label, large=True):
    return {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "label": label,
            "remotion": {"pattern": "ClaudeCodeBeat",
                         "props": {"title": title, "code": code, "sparkLine": spark, "language": "python",
                                   "largeText": large}}}


def lines(path, a, b):
    t = (REEL.parents[1] / path).read_text(encoding="utf-8") if False else None
    return t


def main():
    beats = []
    beats.append(V("B00", "ASK",
        "Hello — this is Liam, in for Bear. Jiean Yin's game is Lane Tactics: wooden pieces on a five-lane board, "
        "and you win by reaching the enemy's back row. This assignment adds three 3D assets, built in Blender by "
        "Claude through the Blender MCP. The prompt on screen is an illustrative reconstruction.",
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "label": "Illustrative reconstruction of the Claude interface — not a transcript",
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Hello, Liam", "topic": "WALKER · GODOT GAMEDEV", "segment": "A Piece, a Square, a Goal",
             "command": "Please use Walker to convert my game design document about Lane Tactics — carved wooden "
                        "pieces on a five-lane linen board, win by standing a piece on the enemy's back row — into "
                        "three low-poly 3D assets: the archer piece, a board square and the goal flag. Build them in "
                        "Blender through the MCP, export them to Godot, and check them in a small tabletop scene.",
             "runningText": "reading CHANGE-BRIEF.md…", "folderLabel": "@NikBearBrown", "modelLabel": "Claude",
             "effortLabel": "High",
             "output": ["archer_piece 254 tris · board_square 60 · goal_flag 84",
                        "Headless check 38/38 (first run 32/33, faulty, kept)",
                        "Source shown: commit e415255"]}}},
        role_note="walker B00: ClaudeComposerAsk, prompt begins 'Please use Walker to convert my game design document "
                  "about'; describes this game. Illustrative reconstruction, labelled. Output lines are real numbers "
                  "from TEST-REPORT A3.3 / evidence reports, not a progress receipt."))
    beats.append(V("B01", "BLUF",
        "What was built: three low-poly assets, made in Blender, exported to Godot, and placed in one small diorama "
        "scene. The numbers check them. The running scene is where you see them.",
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
         "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
             "text": "Three 3D assets for Lane Tactics:\na piece, a square, a goal.\nBuilt in Blender through the MCP,\n"
                     "judged in numbers.",
             "triggerWords": "numbers", "replacementWords": "the running scene", "fontSize": 84, "lineSpacing": 2.3,
             "align": "center", "seed": "lane-tactics-a3-0915", "mistakeRate": 2, "hesitateWithin": 0,
             "hesitateBetween": 1, "charMs": 8, "ink": "#3D3929", "accent": "#D97757", "bg": "#FAF9F5"}}},
        role_note="walker B01: hesitant-writer summary of what was built; correction 'numbers' -> 'the running scene' is "
                  "the assignment's own point (judged in the running scene).",
        qc={"sparse_by_design": True,
            "sparse_reason": "Hesitant-writer BLUF bookend: centred serif lines typed on cream; mostly-cream frames are the mandated design."}))
    beats.append(V("B02", "ASSETS",
        "Here they are, in Jiean's own Godot screenshot. The archer piece is the unit. The board square is the tile "
        "the five-lane board is made of. The goal flag marks the back row you have to reach. The brief fixed one "
        "scale before any build: one square is one metre, and every origin sits at the base.",
        {"type": "STILL", "source": "own", "treatment": "none", "motion": "hold", "composite": "tools/make_media.py B02",
         "label": "JIEAN'S OWN SCREENSHOT · Godot editor, not a reconstruction",
         "typography_note": "Composite: the student's PNG at native size ratio, our cards (>= 44 px at 4K)."},
        role_note="Requirement 1: the game, the three assets and why each (CHANGE-BRIEF A3 'Why these three', 'Scale', "
                  "asset table). Picture: C:/dev/a3-footage/'Check 3 asset in Godot.png' (student's own)."))
    beats.append(V("B03", "CODE",
        "Claude built each part with one MCP call. Line 135 is the bow: a thin box reaching sixty-five centimetres "
        "up, on the facing side. Line 140 is the eye: a small cube at sixty centimetres, on the same side. Each "
        "line is fine on its own.",
        code_beat("tools/blender/build_archer_piece.py · e415255",
                  "# line 135 (step 5, the bow)\n"
                  "ob = add_mesh_object(\"bow\", box(0.03, 0.06, 0.50), (0.165, 0.0, 0.40), flat_material(\"walnut\", \"5A3A22\"))\n"
                  "\n"
                  "# line 140 (step 6, the eye)\n"
                  "ob = add_mesh_object(\"eye\", box(0.03, 0.03, 0.03), (0.105, 0.0, 0.60), flat_material(\"ink\", \"1B1410\"))",
                  "Bow: z 0.15 to 0.65 · eye: z 0.60 · both on +X",
                  "Actual source excerpt (build_archer_piece.py @ e415255, lines 135 and 140) · reconstructed code view",
                  large=False),
        role_note="Code beat (execute_blender_code body Claude ran through the MCP). Lines 135 and 140 verbatim; the two "
                  "comment lines are our markers. Result follows in B04."))
    beats.append(V("B04", "RESULT",
        "Jiean's own screen recording, just after the build. Orbit to the facing side: the bow stands right in "
        "front of the eye. No number caught this. Looking did.",
        own_video([{"src": "archer", "t0": 0.0, "t1": 9.6}],
                  f"{FOOT}|a3-blender-archer-build-2026-10-15.mp4 · 0:00.0–0:09.6 · own audio muted",
                  "Raw student footage; Blender UI text is the recording's own."),
        role_note="Result of B03. Student footage 0:00.0-0:09.6: Object Mode orbit of the finished archer; from the "
                  "facing side the bow covers the eye (FRICTIONAL 18:20-18:23, TEST-REPORT A3.4 #1).", lead_silence_s=0.2))
    beats.append(V("B05", "HAND_EDIT",
        "The fix was Jiean's, by hand, following Claude's steps. Edit Mode, with the bow selected. Then G, Y, and "
        "eight centimetres along Y. Back in Object Mode, the sidebar still reads forty by forty by eighty, and the "
        "file is saved.",
        own_video([{"src": "archer", "t0": 9.6, "t1": 12.6, "inset": "mode"},
                   {"src": "archer", "t0": 24.5, "t1": 31.5, "inset": "move"},
                   {"src": "archer", "t0": 38.0, "t1": 43.2, "inset": "saved"}],
                  f"{FOOT}|a3-blender-archer-build-2026-10-15.mp4 · three excerpts, cuts marked · own audio muted",
                  "Raw student footage with a 3x zoom inset of the same frame's own UI text (marked 'zoom')."),
        role_note="Student's hand edit (FRICTIONAL ~18:30, TEST-REPORT A3.6 #1): 0:09.6-0:12.6 Tab into Edit Mode, bow "
                  "selected; 0:24.5-0:31.5 the move constrained to global Y, typed 0.08, header 'D: [0.08] = 8 cm "
                  "(0.0800 m) along global Y', confirmed ~0:31; 0:38.0-0:43.2 Object Mode, Dimensions 0.4 / 0.4 / 0.8 m, "
                  "status 'Saved \"archer_piece.blend\"' (~0:40.5). Omitted: 0:12.6-0:24.5 (view changes and the start of "
                  "the same move, free-drag before the Y constraint) and 0:31.5-0:38.0 (orbit in Edit Mode).",
        lead_silence_s=0.3))
    beats.append(V("B06", "FLAG_PROMPT",
        "The goal flag was built the same way. Here Jiean types the prompt, Approve, and sends it. Ninety seconds "
        "later, Claude's reports appear: base, pole and flag, eighty-four triangles, and a warning that the flag "
        "nearly vanishes side-on. Blender itself is not on screen in this recording.",
        own_video([{"src": "flag", "t0": 4.5, "t1": 14.0, "crop": "prompt"},
                   {"src": "flag", "t0": 102.6, "t1": 112.6, "crop": "reports"}],
                  f"{FOOT}|a3-blender-flag-build.mp4 · Claude window, cropped · own audio muted",
                  "Student footage cropped to the conversation column (sidebar with account name and the side panel "
                  "removed); the conversation text is the recording's own."),
        role_note="The prompt to Claude on screen and what it built: 0:04.5-0:14.0 the student types 'Approve' and sends it "
                  "(~0:11.7; the earlier question 'Keep recording ... tell me briefly' is visible above); the window shows "
                  "no change from 0:14 to ~1:42; 1:42.6-1:52.6 Claude's step reports (base disc 0.30 x 0.30 x 0.04 m 44 "
                  "tris; pole; flag 0.28 x 0.02 x 0.20 m 12 tris; 0.45 x 0.30 x 1.20 m, 84 triangles; edge-on warning). "
                  "Blender never appears in this clip.", lead_silence_s=0.2))
    beats.append(V("B07", "CODE",
        "Claude wrote the diorama scene by hand: a floor, one lamp, a camera, and three instanced models. The board "
        "square at x minus one point two, the archer at the origin, the flag at one point one. None is lifted, so "
        "each base origin should stand it on the floor.",
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
         "remotion": {"pattern": "GodotDevWorkbench", "props": {
             "mode": "code", "title": "asset_diorama.tscn: Three Models, One Floor",
             "project": "Lane Tactics asset slice", "path": "res://diorama/asset_diorama.tscn",
             "source": "godot/diorama/asset_diorama.tscn · lines 41–47 · commit e415255",
             "code": None, "startLine": 41, "codeFontSize": 30,
             "inspectorLabel": "Source notes — not Inspector values",
             "notes": [{"label": "Floor (lines 7-13, 27-28)", "value": "PlaneMesh 5 x 3 m at y = 0, table colour #6B4A2E"},
                       {"label": "Lamp (lines 30-33)", "value": "one DirectionalLight3D, shadows on"},
                       {"label": "Camera3D (lines 35-39)", "value": "(0, 1.1, 3), tilted down, fov 50"}],
             "output": ["Written by Claude by hand; not yet saved from the editor (TEST-REPORT A3.8)"]}}},
        role_note="Code beat: asset_diorama.tscn lines 41-47 verbatim. Result follows in B08."))
    beats.append(V("B08", "RESULT",
        "Here it is running. First, the scene's own camera, exactly as saved. Then a scripted camera on the real "
        "scene, in one slow orbit. All three stand upright on the floor. As we pass the flag's side, the red cloth "
        "thins to a line: the edge-on problem. From behind, the flag falls into shadow.",
        own_video([{"src": "orbit", "a": 0, "b": 120, "label": "THE SCENE'S OWN CAMERA3D · REAL GODOT RENDER|asset_diorama.tscn @ e415255, camera as saved · no audio in this scene"},
                   {"src": "orbit", "a": 120, "b": 600}], ENGINE,
                  "Raw engine capture, 4K SubViewport; our label measured separately."),
        role_note="Result of B07. Capture run-02 frames 0-120 (shot A, the scene's own Camera3D) and 120-600 (shot B, "
                  "harness camera, one 360-degree orbit, radius 3.3 m, 0.85 m above the 0.35 m target).",
        lead_silence_s=0.3, qc={"full_bleed": True, "full_bleed_reason": "Real Godot render: the scene's floor and background run edge to edge; reframing would misrepresent it."}))
    beats.append(V("B09", "RESULT",
        "Down at floor level: no gap under any base, and nothing sinks into the table. Then the archer from its "
        "facing side, the profile the 2D game uses. After the hand edit, the eye shows beside the bow.",
        own_video([{"src": "orbit", "a": 600, "b": 1080}], ENGINE,
                  "Raw engine capture, 4K SubViewport; our label measured separately."),
        role_note="Capture run-02 frames 600-840 (shot C, camera 6 cm above the floor, tracking left to right) and "
                  "840-1080 (shot D, archer from +X round toward +Z, 0.95 m).", lead_silence_s=0.3,
        qc={"full_bleed": True, "full_bleed_reason": "Real Godot render: the scene's floor and background run edge to edge; reframing would misrepresent it."}))
    beats.append(V("B10", "CODE",
        "One brief revision shows here too. The original border colour was only 1.15 to 1 against the slab, so a "
        "grid read as one flat sheet. Claude compared four darker colours; Jiean chose 9A7F55, at 2.27 to 1. These "
        "two lines are the whole change.",
        code_beat("tools/blender/build_board_square.py · e415255",
                  "# lines 142-143 (revision A3-R1, run after the first look)\n"
                  "mat = bpy.data.materials[\"linen_border\"]\n"
                  "bsdf = set_flat_color(mat, \"9A7F55\")",
                  "Border #CDB98E → #9A7F55 · contrast 1.15 → 2.27 : 1",
                  "Actual source excerpt (build_board_square.py @ e415255, lines 142-143) · reconstructed code view"),
        role_note="Code beat: CHANGE-BRIEF A3-R1. Lines 142-143 verbatim; the comment line is our marker. Result in B11."))
    beats.append(V("B11", "RESULT",
        "In Godot, the darker strips frame the square. Under this lamp, though, the slab reads almost white.",
        own_video([{"src": "orbit", "a": 1320, "b": 1500}], ENGINE,
                  "Raw engine capture, 4K SubViewport; our label measured separately."),
        role_note="Result of B10. Capture run-02 frames 1320-1500 (shot F, board square from above). Observation of the "
                  "rendered pixels; not a judgement of the colour choice (A3.5 is the student's).", lead_silence_s=0.15,
        qc={"full_bleed": True, "full_bleed_reason": "Real Godot render; reframing would misrepresent it."}))
    beats.append(V("B12", "CODE",
        "Then the numbers. The check loads each model, then the diorama, and measures. Line 173, await process "
        "frame, is the fix. The first version measured before the nodes were in the scene tree, so every position "
        "read as zero and the camera had no frustum. One impossible failure, all three assets at x zero, gave it away.",
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion",
         "remotion": {"pattern": "GodotDevWorkbench", "props": {
             "mode": "code", "title": "check_assets.gd: Measure Only Inside the Tree",
             "project": "Lane Tactics asset slice", "path": "res://tests/check_assets.gd",
             "source": "godot/tests/check_assets.gd · lines 167–182 · commit e415255",
             "code": None, "startLine": 167, "codeFontSize": 26,
             "inspectorLabel": "Source notes — not Inspector values",
             "notes": [{"label": "Run 1 (evidence/check_assets-1792106172.json)", "value": "32/33 - measured in _initialize(), outside the tree; kept on purpose"},
                       {"label": "Run 2 (evidence/check_assets-1792106192.json)", "value": "38/38 after the fix"},
                       {"label": "Headless", "value": "dummy renderer: nothing is drawn"}],
             "output": ["godot --headless --path godot --script res://tests/check_assets.gd"]}}},
        role_note="Code beat: check_assets.gd lines 167-182 verbatim. Result (the recorded numbers) in B13."))
    beats.append(V("B13", "RESULT",
        "Headless numbers beside the brief. Size, height axis, scale, origin, triangles and colours all match: 254, "
        "60 and 84 triangles. The faulty first run is kept, 32 of 33. The fixed run passes 38 of 38, and so did a "
        "rerun on this film's isolated copy. But headless Godot draws nothing. How the assets look stays a human check.",
        {"type": "STILL", "source": "own", "treatment": "none", "motion": "hold", "composite": "tools/make_media.py B13",
         "label": "HEADLESS CHECK OUTPUT · recorded JSON reports, no rendering",
         "typography_note": "Composite table of TEST-REPORT A3.3 and the three JSON reports (>= 44 px at 4K)."},
        role_note="Requirement 4: brief vs Blender vs Godot (TEST-REPORT A3.3), runs 1 and 2, and our rerun on the "
                  "isolated copy (capture/check_assets-rerun.json)."))
    beats.append(V("BCRD", "CREDITS",
        "Who did what. Jiean chose the game, approved every plan, recorded the sessions, made the hand edit, and "
        "chose the border colour and the headless export route. Claude proposed the numbers, and wrote and ran the "
        "Blender code, the export, the scene and the check. Source shown: commit e, four one five, two five five.",
        {"type": "STILL", "source": "own", "treatment": "none", "motion": "hold", "composite": "tools/make_media.py BCRD",
         "label": "", "typography_note": "Text card (>= 52 px at 4K)."},
        role_note="Requirement 5: human and AI contributions (FRICTIONAL A3 'Human / Claude / model' lines, CHANGE-BRIEF "
                  "'Who decided what'), source revision."))
    beats.append(V("BVDT", "VERDICT",
        "Verdict. Checked: size, upright, scale, origin, budget and colours, headlessly, plus this scripted look at "
        "the running scene. Claude got three things wrong: the bow hid the eye, the first check proved less than it "
        "claimed, and the flag vanishes side-on, still unfixed. Uncertain: how they read at game distance, and why "
        "the linen looks so pale. Next step: Jiean's own look check in Godot.",
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-reveal",
         "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
             "artifactTitle": "Verdict", "artifactHeading": "Three Lane Tactics assets at e415255.",
             "brandLabel": "@NikBearBrown",
             "artifactLines": [
                 "Checked: size, upright, scale, origin, triangles, colours — headless 38/38; a scripted camera on the running scene.",
                 "Claude got wrong: the bow hid the eye · the first check measured outside the tree · the flag is edge-on from the side (not fixed).",
                 "Uncertain: reading at game distance; the linen renders pale under the lamp; one tester, Windows only.",
                 "Next step: Jiean's look check in Godot (TEST-REPORT A3.5), including behind and below."]}}},
        role_note="Verdict: checked vs wrong vs uncertain vs next step; the look is the student's call."))
    beats.append(V("BHTF", "HANDOFF",
        "Your turn. Paste this. Use Walker on my Lane Tactics goal flag: make the cloth six centimetres thick instead "
        "of two. Before running it, predict the triangle count, the Godot bounding box, and whether it still vanishes "
        "side-on. Then re-export, rerun the check, and orbit it in the running scene. The catch: the numbers may not "
        "move at all. Only looking will tell you. Liam, in for Bear.",
        {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
         "label": "Reconstructed interface · suggested prompt, not a past run",
         "remotion": {"pattern": "ClaudeComposerAsk", "props": {
             "greeting": "Your turn.", "topic": "WALKER · YOUR TURN", "segment": "One Thickness, One Prediction",
             "command": "Use Walker on my Lane Tactics goal flag: make the cloth 6 cm thick instead of 2. Before running "
                        "it, predict the triangle count, the Godot bounding box, and whether it still vanishes side-on. "
                        "Then re-export, rerun check_assets.gd, and orbit it in the running scene.",
             "runningText": "paste this into Claude…", "folderLabel": "@NikBearBrown", "modelLabel": "Claude",
             "effortLabel": "High"}}},
        role_note="Your Turn: one bounded change + prediction + test; Liam signs off."))
    beats.append({"beat_id": "BOUT", "act": "OUTRO", "kind": "outro_voice",
                  "role_note": "OUTRO-LOCK: ClaudeTitleOutro, exact title, @NikBearBrown, slug-seeded mascot, no subline. "
                               "Spoken, never scored; 1.0 s silent tail.",
                  "narration_text": f"{TITLE}. At Nik Bear Brown.", "voice": "am_onyx", "engine": "kokoro",
                  "tail_hold_s": 1.0,
                  "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "mascot-title",
                           "remotion": {"pattern": "ClaudeTitleOutro", "props": {
                               "title": f"{TITLE}.", "slug": SLUG, "handle": "@NikBearBrown", "subline": ""}}}})

    # verbatim code for the GodotDevWorkbench beats, from the isolated copy of e415255
    game = Path(r"C:/dev/a3-capture/e415255/godot")
    for b in beats:
        p = (b["shot"].get("remotion") or {}).get("props") or {}
        if p.get("code", "") is None:
            rel = p["path"].replace("res://", "")
            n = {"B07": (41, 47), "B12": (167, 182)}[b["beat_id"]]
            p["code"] = "\n".join((game / rel).read_text(encoding="utf-8").splitlines()[n[0] - 1:n[1]])

    meta = {
        "title": TITLE, "slug": SLUG, "topic": "WALKER · GODOT GAMEDEV", "kind": "godot-gamedev",
        "skill": "godot-gamedev", "modifier": "walker", "brand": "claude-liam",
        "audience": "Course reviewers and makers following Walker/Claude workflows", "register": "Teardown",
        "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx", "palette": "claude",
        "style_preset": "claude", "ground": "#FAF9F5", "aspect_ratio": "16:9", "fit": "crop", "captions": False,
        "channel": "@NikBearBrown", "folderLabel": "@NikBearBrown", "greeting": "Hello, Liam",
        "greeting_note": "English-only, as in the Assignment 2 film ('Hello'); Liam never takes Wagwan.",
        "persona": "Liam (in for Bear)", "presenter": "Liam (in for Bear)", "in_for_bear": True,
        "title_status": "default title chosen by Claude for this build; the student may change it",
        "game": {"name": "walker-lane-tactics-jiean-yin",
                 "repository": "https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin",
                 "source_revision": "e415255 = e41525548f68b2752917ef4544024a1b2492510a (branch a3-blender-assets)",
                 "engine": "Godot 4.7.2.stable.official.ed1daf0bf", "blender": "5.2.2 LTS"},
        "audio_policy_note": "Narration only. The student's footage is muted (its own audio track is not used); the "
                             "diorama scene has no sound. The outro card carries only Liam's voice.",
        "labels": {"footage": FOOT, "engine": ENGINE.replace("|", " / "),
                   "reconstruction": "Illustrative reconstruction of the Claude interface — not a transcript",
                   "editor": "Godot editor reconstruction (printed by GodotDevWorkbench)",
                   "headless": "HEADLESS CHECK OUTPUT · recorded JSON reports, no rendering"},
    }
    (REEL / "beat_sheet.json").write_text(json.dumps({"metadata": meta, "beats": beats}, indent=2, ensure_ascii=False)
                                          + "\n", encoding="utf-8")
    print(len(beats), "beats")


if __name__ == "__main__":
    main()
