"""Write beat_sheet.json for the A5 film from the script Jiean approved (SCRIPT-DRAFT.md, 2026-11-03).

Code excerpts are read from the isolated copy of tag a5 (CAPTURE/a5/godot), never typed, so each matches its file.
Narration spells Jiean's name "Jay-Ann" for the voice only (Jiean: "a combination of Jack and Ann, sounds like
Jay-An"); everything on screen keeps "Jiean". Footage segment ranges are filled in later by tools/set_segments.py.
Usage (reel folder): CAPTURE=<capture-copy> python tools/build_sheet.py
"""
import json
import os
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = Path(os.environ["CAPTURE"]) / "a5" / "godot"
SLUG = "claude-liam-walker-lane-tactics-jiean-yin-a5-gamedev"
TITLE = "Lane Tactics: A Danger Tint and a Linen Board"
REV = "tag a5 = ef5d38bc6d5f2fbdda62a4f4001791405dee0071"
NAME = "Jay-Ann"  # voice spelling only


def lines(rel, a, b):
    text = (GAME / rel).read_text(encoding="utf-8").split("\n")
    return "\n".join(text[a - 1:b])


def voice(b):
    b.setdefault("voice", "am_onyx")
    b.setdefault("engine", "kokoro")
    return b


def workbench(bid, title, rel, a, b, narration, notes, output, role):
    return voice({
        "beat_id": bid, "act": "CODE", "narration_text": narration,
        "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "remotion": {
            "pattern": "GodotDevWorkbench", "props": {
                "mode": "code", "title": title, "project": "Lane Tactics",
                "path": "res://" + rel, "source": f"godot/{rel} · lines {a}–{b} · tag a5",
                "code": lines(rel, a, b), "startLine": a, "codeFontSize": 34,
                "inspectorLabel": "Source notes · not Inspector values", "notes": notes, "output": output}}},
        "excerpt": {"path": rel, "start_line": a, "end_line": b},
        "role_note": role})


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


TINT_LABEL = "SCRIPTED KEY PRESSES · REAL GODOT RENDER|main.tscn @ tag a5, isolated copy · Movie Maker, 30 fps · no audio"
DIO_LABEL = "SCRIPTED · REAL GODOT RENDER|asset_diorama.tscn @ tag a5 · uniforms changed in memory, no file saved"

beats = [
    voice({"beat_id": "B00", "act": "ASK",
           "narration_text": f"Hello, this is Liam, in for Bear. {NAME} Yin's game is Lane Tactics: archers on a five-lane "
                             "board, where you win by reaching the enemy's back row. This assignment adds shaders: a red "
                             "warning on the archer, and a cloth surface for the 3D board. The prompt on screen is an "
                             "illustrative reconstruction.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
                    "label": "Illustrative reconstruction of the Claude interface — not a transcript",
                    "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                        "greeting": "Hello, Liam", "topic": "WALKER · GODOT GAMEDEV",
                        "segment": "A Danger Tint and a Linen Board",
                        "command": "Please use Walker to convert my game design document about Lane Tactics — archers "
                                   "on a five-lane board, simultaneous orders, win by reaching the enemy's back row — "
                                   "into two shaders: a red tint that warns when my planned square is inside the enemy "
                                   "archer's reach, and a linen cloth material for the 3D board squares. Test both, and "
                                   "show me what a headless run cannot.",
                        "runningText": "reading CHANGE-BRIEF.md…", "folderLabel": "@NikBearBrown",
                        "modelLabel": "Claude", "effortLabel": "High",
                        "output": ["test_exposed_tint 46/46 at 30, 60 and 144 fps",
                                   "test_materials 148/148 · 3 mutations exit 1",
                                   "Source shown: tag a5 (ef5d38b)"]}}},
           "role_note": "walker B00: ClaudeComposerAsk; prompt begins 'Please use Walker to convert my game design "
                        "document about'; illustrative reconstruction, labelled. Result lines are recorded numbers "
                        "(TEST-REPORT A5.2, A5.12)."}),
    voice({"beat_id": "B01", "act": "BLUF",
           "narration_text": f"What was built: two shaders, written by hand by {NAME}, one driven by the game's state and "
                             "one by textures. The tests check the wiring. Whether they work is judged in the pixels.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on-correct",
                    "remotion": {"pattern": "BrutalistHesitantWriter", "props": {
                        "text": "Two shaders for Lane Tactics:\na warning and a weave.\nWritten by hand,\njudged by the tests.",
                        "triggerWords": "tests", "replacementWords": "pixels", "fontSize": 84, "lineSpacing": 2.3,
                        "align": "center", "seed": "lane-tactics-a5-1103", "mistakeRate": 2, "hesitateWithin": 0,
                        "hesitateBetween": 1, "charMs": 8, "ink": "#3D3929", "accent": "#D97757", "bg": "#FAF9F5"}}},
           "role_note": "walker B01: hesitant-writer summary; correction 'tests' -> 'pixels' is the assignment's point.",
           "qc": {"sparse_by_design": True,
                  "sparse_reason": "Hesitant-writer BLUF bookend: centred serif lines typed on cream."}}),
    still("B02", "SETUP",
          "The assignment asks for one shader driven by game state, one textured shader with two materials, and four "
          "answers: what a shader does, how a material differs from a shader, why a texture is information, and what "
          "Godot's shading language is. Each answer points at a line of code. One fact shapes everything: this project "
          "runs on Godot's Compatibility renderer.",
          "", "Setup: the state, the object, the four questions, the renderer (CHANGE-BRIEF §1, §4; project.godot:25)."),
    workbench("B03", "exposed_tint.gdshader: the colour line", "shaders/exposed_tint.gdshader", 1, 8,
              "Question one: what does a shader do? It runs on the graphics card, once for every pixel the sprite "
              f"covers. This one is {NAME}'s, written by hand. Line three: exposed amount, a number from zero to one. "
              "Line seven is the colour line. It mixes the sprite's own colour toward the game's red by that amount, "
              "capped at seventy percent, so the face and the bow still show. Only red, green and blue change; "
              "transparency is untouched.",
              [{"label": "Written by", "value": "Jiean, by hand (commit 80fc669)"},
               {"label": "exposed_color", "value": "#E0453A, the game's target red (main.gd:47)"},
               {"label": "Runs", "value": "once per pixel of the archer's Sprite2D"}],
              ["No agent session changed godot/shaders/"],
              "Q1 what a shader does; code beat, result B04."),
    footage("B04", "Here it is in the real game, keys pressed by a script. Two turns out of reach: no tint. Turn three: "
                   "Right plans a square inside the enemy archer's reach, and the archer turns red in a fifth of a "
                   "second. Left steps back out, and the red drains away.",
            TINT_LABEL, "Result of B03: capture tint, shots T1-T3 (turns 1-2, fade in, fade out)."),
    workbench("B05", "exposed_driver.gd: game state to uniform", "game/exposed_driver.gd", 29, 37,
              "The shader doesn't know the game. The driver tells it. Every frame it asks one question: is the planned "
              "square in reach? Line thirty-four moves the amount toward one or zero, at five per second of game time, "
              "starting from wherever it is now. That is why a quick tap turns around mid-fade instead of restarting, "
              "and why pause holds it still. Line thirty-seven hands the number to the player's own material. Every "
              "sprite gets a new material of its own, so the enemy never shares the red.",
              [{"label": "RATE", "value": "5.0 per second of game time: 0 → 1 in 0.20 s (line 18)"},
               {"label": "Own material", "value": "piece.gd:56-59, a new ShaderMaterial per sprite"},
               {"label": "Written by", "value": "claude -p agent, plan approved by Jiean (44b2acb)"}],
              ["Reads main's state; never writes it"],
              "Driver; code beat, result B06."),
    footage("B06", "Fast taps, every tenth of a second: the value turns around from where it is, and never jumps. Pause "
                   "in the middle of a fade, and it holds. Enter confirms the move, and the red fades while the move "
                   "plays. Turn four starts already in reach, so it rises again on the first frame. The enemy's tint "
                   "stays at zero in every frame of this capture.",
            TINT_LABEL, "Result of B05: capture tint, shots T4-T6 (retrigger, pause, confirm, turn 4)."),
    still("B07", "EVIDENCE",
          f"Before looking, {NAME} worked the colours out by hand. Then the engine's own frame was captured at four "
          "values. At zero and one half, the head and the base match the predictions exactly. At one, within one step: "
          "the hand sum gave one hundred point five. At two, set from code, the head reads two twenty-four, "
          "twenty-seven, thirty-four: exactly the unclamped prediction. Hint range draws the Inspector's slider. It "
          "does not clamp a value set from code. And a Windows screenshot of the same moment gave the same numbers.",
          "JIEAN'S CAPTURES · capture() in a real window, key C · not a reconstruction",
          "Controlled values: evidence/a5/captures/exposed_*.png, exposed_pixels.md, os_compare.log (TEST-REPORT A5.4)."),
    workbench("B08", "linen_dark.tres: one set of values", "materials/linen_dark.tres", 8, 16,
              "Question two: how is a material different from a shader? The shader is the program. A material is one "
              "set of values for it. Both linen materials point at the same shader, on line eleven. They differ in two "
              "lines: the tint on line thirteen, white for light and stitch-brown for dark, and normal strength on line "
              "sixteen: one for light, one and a half for dark.",
              [{"label": "linen_light.tres:13", "value": "tint = Color(1, 1, 1, 1)"},
               {"label": "linen_light.tres:16", "value": "normal_strength = 1.0"},
               {"label": "Both, line 11", "value": "shader = linen_square.gdshader"}],
              ["Made by Claude Code (98e1003); audited by an agent (MATERIALS.md)"],
              "Q2 material vs shader; code beat, result B09."),
    footage("B09", "Both tiles, under the diorama's single lamp. Turn the dark material's normal strength down to zero, "
                   "and only the dark tile goes flat. Change one line of the shared shader, in memory, and both tiles "
                   f"darken together. One program, two sets of values. {NAME} made the same two edits by hand in the "
                   "editor, and saw the same thing.",
            DIO_LABEL, "Result of B08: capture diorama, shots D0 (scene camera), D1, D5 (one material), D6 (one shader)."),
    workbench("B10", "linen_square.gdshader: what each texture means", "shaders/linen_square.gdshader", 3, 12,
              "Question three: why is a texture information? Because the same kind of pixels can mean different "
              "things. Line four reads the cloth photograph as colour, with source colour. Line nine reads roughness "
              "as plain data, with no colour hint. Line eleven reads the normal map as directions, with hint normal: "
              "each pixel is a tilt, not a shade. The import settings agree: lossless everywhere, and the normal-map "
              "flag only on the normal maps. And a curl check on the normal map tells the right green convention from "
              "the wrong one, by zero point six eight against one point three two.",
              [{"label": "Import (all)", "value": "compress/mode 0 Lossless · detect_3d off"},
               {"label": "compress/normal_map", "value": "1 on nor_gl and nor_dx · 2 on diff and rough"},
               {"label": "curl_ratio nor_gl", "value": "0.6813 (GL) · 1.3187 (DX)"}],
              ["Hessian 380, Poly Haven, CC0"],
              "Q3 texture as information; code beat, result B11."),
    footage("B11", "The interface sweep, on the light tile. U V scale down from three point six five to one half: "
                   "threads like rope. Up to eight: a fine weave. Normal strength to zero: the threads flatten into "
                   "paint. To two: deeper threads, still cloth. Roughness to zero, seen from the lamp's mirror angle: in "
                   f"this capture the tile gets slightly darker, and no highlight appears. In the editor, {NAME} saw it "
                   "turn shiny, like plastic. The two disagree, and that stays open.",
            DIO_LABEL, "Result of B10: capture diorama, shots D2 (uv_scale), D3 (normal_strength), D4 (roughness)."),
    workbench("B12", "hint_experiment.gdshader: one file, two hints", "shaders/hint_experiment.gdshader", 1, 14,
              "The hint experiment asks whether source colour changes the numbers a shader receives. One file, three "
              "greys: sixty-four, one twenty-eight, one ninety-two. Line four samples it with source colour, line five "
              "without, and line six picks which one writes albedo. Unshaded, linear tonemap, exposure one. "
              f"{NAME} predicted that the hinted quad would show the file's own values, and the plain one would come "
              "out lighter: one thirty-seven, one eighty-eight, two twenty-five.",
              [{"label": "hint_greys.png", "value": "3 × 1, greys 64, 128, 192 (write_hint_greys.gd)"},
               {"label": "Scene", "value": "Linear tonemap, exposure 1.0, glow/fog/adjust off"},
               {"label": "Prediction", "value": "A 64/128/192 · B 137/188/225 (Jiean, by hand)"}],
              ["Written by Jiean, by hand (fb8d2bf)"],
              "Hint experiment; code beat, result B13."),
    still("B13", "RESULT",
          "Measured on this renderer: both quads show sixty-four, one twenty-eight, one ninety-two. It isn't a wiring "
          "slip. Swapping the switches changes nothing, separate textures change nothing, and a plain one half written "
          "to albedo shows as one twenty-eight. On Compatibility, in this scene, neither the decode nor the encode "
          "happened. The prediction assumed Forward Plus. It's recorded, not explained away.",
          "REAL GODOT RENDER · hint_experiment.tscn @ tag a5 · 4K frame, bands read from it",
          "Result of B12: capture hint frame + evidence/a5/step3/hint_experiment_measurement.md, hint_control.log.",
          evidence=True),
    still("B14", "LANGUAGE",
          "Question four: what is Godot's shading language? A small language, close to G L S L, where Godot writes "
          "the boring parts. There's no main function and no version line: shader type picks the pipeline and its "
          "built-ins, like albedo and normal map. And it has hints that G L S L doesn't. Here is the editor's own "
          f"conversion of a standard material, beside {NAME}'s. Its line seven samples albedo with source colour, just "
          f"like {NAME}'s line four. Its line nineteen reads the normal map with hint roughness normal, where {NAME}'s "
          "line eleven uses hint normal. The same idea, with a different hint.",
          "ACTUAL SOURCE LINES · standard_generated.gdshader (editor conversion) beside linen_square.gdshader",
          "Q4 the Godot shading language; two generated lines beside their equivalents (verbatim)."),
    workbench("B15", "test_exposed_tint.gd: the name contract", "tests/test_exposed_tint.gd", 167, 177,
              "Now the tests. The agent-written test asks the engine for the shader's uniform list, and checks the "
              "names and types. A headless engine won't report defaults or source colour, so the test reads those from "
              "the shader's own text. Then it presses real keys and checks every frame against the rule.",
              [{"label": "Defaults", "value": "read from the .gdshader text (lines 180-192)"},
               {"label": "Every frame", "value": "value = move_toward(previous, state ? 1 : 0, 5 × game dt)"},
               {"label": "Written by", "value": "claude -p agent; rerun by Claude Code"}],
              ["Runs through scripts/run-test.sh at 30, 60 and 144 fps"],
              "Tests; code beat, result B16."),
    still("B16", "RESULT",
          "Forty-six of forty-six, at thirty, sixty and a hundred and forty-four frames per second; a hundred and "
          "forty-eight of a hundred and forty-eight for the materials; and the earlier suites unchanged. Then "
          f"{NAME} broke the shaders on purpose. Delete a semicolon: shader error, exit one. Rename the uniform: exit "
          "one, and the frame-by-frame value check still passed, because setting a name the shader doesn't have raises "
          "no error. Only the uniform list caught it. Delete source colour: exit one. What no headless run can show: "
          "any pixel at all. That is what the captures are for.",
          "HEADLESS CHECK OUTPUT · recorded reports, no rendering",
          "Result of B15: TEST-REPORT A5.1, A5.2, A5.12; evidence/a5/mutations/; this film's rerun on the a5 copy.",
          evidence=True),
    still("BCRD", "CREDITS",
          f"Who did what. {NAME} chose the state, the object and the cloth, wrote the three shaders and the colour line "
          "by hand, computed every prediction, ran the three mutations, took the captures, and played it. Claude agents "
          "wrote the driver, the tests and the material audit; Claude Code reviewed them and built the materials and "
          "scenes. Caught on the way: a wrong line number, two misnamed frame-rate reports, and an audit figure nobody "
          "had measured. The cloth is Hessian 380 from Poly Haven, public domain. Source shown: tag a5.",
          "", "Human and AI contributions (SOURCES.md A5), agent mistakes caught (TEST-REPORT A5.13), texture source."),
    voice({"beat_id": "BVDT", "act": "VERDICT",
           "narration_text": "Verdict. Checked: the tint follows its rules at three frame rates, the captures match the "
                             "hand predictions within one step, and hint range doesn't clamp. Wrong: the hint "
                             "experiment's prediction, on this renderer. Uncertain: why Compatibility behaves that way, "
                             "the missing roughness highlight, and a thirty-frame fade that sits exactly on its "
                             "tolerance. Next step: run the hint experiment on Forward Plus, in a copy, to see which half "
                             "belongs to the renderer.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "artifact-reveal",
                    "remotion": {"pattern": "ClaudeVerdictArtifact", "props": {
                        "artifactTitle": "Verdict", "artifactHeading": "Two Lane Tactics shaders at tag a5.",
                        "brandLabel": "@NikBearBrown",
                        "artifactLines": [
                            "Checked: the tint's rules at 30, 60 and 144 fps · captures within one step of the hand "
                            "predictions · hint_range does not clamp code.",
                            "Wrong: the hint-experiment prediction on Compatibility (both quads 64 / 128 / 192).",
                            "Uncertain: why Compatibility does this · no roughness highlight in the capture · the 30 fps "
                            "fade sits on its one-frame tolerance.",
                            "Next step: run the hint experiment on Forward+ in a copy."]}}},
           "role_note": "Verdict: checked vs wrong vs uncertain vs next step."}),
    voice({"beat_id": "BHTF", "act": "HANDOFF",
           "narration_text": "Your turn. Open your own shader, change one number, and predict before you look. Here's a "
                             "prompt to start with: change the cap from seventy to fifty percent, work out the head pixel "
                             "by hand, then capture it and compare. If the numbers miss by more than a step, that isn't a "
                             "failure. That's a finding. I'm Liam, in for Bear.",
           "shot": {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "motion": "type-on",
                    "label": "Reconstructed interface — suggested prompt, not a past run",
                    "remotion": {"pattern": "ClaudeComposerAsk", "props": {
                        "greeting": "Your turn.", "topic": "WALKER · YOUR TURN", "segment": "One Number, One Prediction",
                        "command": "Change the cap in my colour line from 0.7 to 0.5. Before you change anything, help me "
                                   "predict the head pixel at exposed_amount 1.0 by hand, then I'll capture it with C and "
                                   "we compare.",
                        "runningText": "paste this into Claude…", "folderLabel": "@NikBearBrown",
                        "modelLabel": "Claude", "effortLabel": "High"}}},
           "role_note": "Your Turn: one bounded change + prediction + capture; Liam signs off."}),
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
    "script_status": "approved by Jiean on 2026-11-03 (SCRIPT-DRAFT.md), unchanged",
    "pronunciation_note": "Narration spells Jiean as 'Jay-Ann' for the voice only (Jiean: 'like Jack and Ann, "
                          "Jay-An'); Kokoro read plain 'Jiean' as 'Jee-un'. Screen text keeps 'Jiean'.",
    "teaching_contract": "code-then-result-v1",
    "game": {"name": "walker-lane-tactics-jiean-yin", "repository": "https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin",
             "source_revision": REV, "engine": "Godot 4.7.2.stable.official.ed1daf0bf", "renderer": "Compatibility"},
    "audio_policy_note": "Narration only. Engine captures carry no audio track in the film; the outro card carries only "
                         "Liam's voice.",
    "labels": {"engine": "SCRIPTED · REAL GODOT RENDER", "student": "JIEAN'S CAPTURES",
               "reconstruction": "Illustrative reconstruction of the Claude interface — not a transcript",
               "editor": "Godot editor reconstruction (printed by GodotDevWorkbench)",
               "headless": "HEADLESS CHECK OUTPUT · recorded reports, no rendering"},
}

(REEL / "beat_sheet.json").write_text(json.dumps({"metadata": metadata, "beats": beats}, indent=2, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
print(len(beats), "beats;", sum(len(b["narration_text"].split()) for b in beats), "words")
