"""Fill the A7 footage beats' segment ranges (final capture, <capture-copy>/final-out) and per-segment labels.

Frame numbers are master frames of play-4k.mkv (30 fps) and slow-4k.mkv (120 fps, shown at 30 = 1/4 speed). Every
range lies inside one unbroken stretch of recording (SPANS) and was chosen from the event anchors in the capture logs
(capture/play-log.jsonl: draws, hits, P and R presses). Each beat's footage is at least as long as its lead +
narration, so nothing is retimed. Crops are of the 4K frame, scaled to fill, and say so in their label.
Usage (reel folder): python tools/set_segments.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
# Master-frame spans recorded without a break in engine time (checked in the logs: play breaks at 617 and 1084, where
# unrecorded turns were played; slow has no break). A segment may cross shots only inside one span.
SPANS = {"play": [(0, 617), (617, 1084), (1084, 1276)], "slow": [(0, 640)]}
PLAY = "SCRIPTED KEY PRESSES · REAL GODOT RENDER|main.tscn @ tag a7, isolated copy · Movie Maker, 30 fps · no audio"
FLAG3 = ("CROPPED 3× · REAL GODOT RENDER|the GoalFlag beside the enemy's back row · main.tscn @ tag a7 · Movie Maker, "
         "30 fps")
SLOW2 = "¼ SPEED · CROPPED 2× · REAL GODOT RENDER|120 fps capture played at 30 · both archers · main.tscn @ tag a7"
CROP_FLAG = [2560, 880, 1280, 720]  # 4K pixels: the flag (foot at canvas (1176, 458)) and the board's right edge
CROP2 = [384, 990, 1920, 1080]      # 4K pixels: both archers in turn 4 (e1 at column 3, p1 at column 1)
SEAM = "Smooth steady ripple."      # TEST-REPORT.md A7.9, Jiean, verbatim
ACTION = ("All distinct. While drawing, the archer lean back with bows moving, and retreating clearly after the arrow "
          "flying away.")       # TEST-REPORT.md A7.10, Jiean, verbatim
CLOCK = ("PASS  5 shot 1 (e1, from idle, row 222): on the arrow's first frame (game frame 12) clip position - arrow t "
         "= DRAW_LEAD 0.2 within half a frame  (0.20000)")

SEGMENTS = {
    # title (the flag waving under the title card), turns 1-3, turn 4's orders: the flag cropped 3x, sheet inset
    "B04": [{"src": "play", "a": 0, "b": 452, "crop": CROP_FLAG, "label": FLAG3, "inset": "sheet",
             "quote_pos": "bottom-left", "quote_width": 1500,
             "quote": [[SEAM, False], ["Jiean, five or more wraps (TEST-REPORT A7.9)", True]]}],
    # turn 4 at real speed around e1's shot (draw 333, hit on p1 349, idle 357); then 1/4 speed, both shots
    # (e1 draw 225, hit 290, idle 321; p1 draw 351, hit 417, idle 447); then turn 5 at real speed (draw 515, idle 539)
    "B11": [{"src": "play", "a": 300, "b": 380, "label": PLAY},
            {"src": "slow", "a": 200, "b": 480, "crop": CROP2, "label": SLOW2},
            {"src": "play", "a": 452, "b": 617, "label": PLAY, "quote_pos": "bottom-right", "quote_width": 1900,
             "quote": [[ACTION, False], ["Jiean, in play (TEST-REPORT A7.10)", True]]}],
    # run 2 turn 4: e1 draw 710, P 712-802 (startup), P 811-901 (active), p1 hit 937, P 939-1029 (recovery);
    # run 3: e1 draw 1177, R 1186
    "B13": [{"src": "play", "a": 700, "b": 1040, "label": PLAY},
            {"src": "play", "a": 1166, "b": 1270, "label": PLAY}],
    # the same run 2 turn, full frame: the archers frozen while the flag (right edge) keeps waving; run 3 after it
    "B15": [{"src": "play", "a": 617, "b": 1084, "label": PLAY, "quote_pos": "bottom-right", "quote_width": 2400,
             "quote": [[CLOCK, "mono"], ["test_anim_states.gd, 60 fps · evidence/a7/step5/test_anim_states_60fps.log",
                                         True]]},
            {"src": "play", "a": 1084, "b": 1180, "label": PLAY}],
}
LEAD = {"B04": 0.3, "B11": 0.3, "B13": 0.5, "B15": 0.3}
ROLE = {
    "B04": "Result of B03: play P0-P1 (title, turns 1-3, turn 4 orders), cropped 3× on the GoalFlag, with flag_red.png "
           "and its 4 × 1 grid inset; Jiean's A7.9 words.",
    "B11": "Result of B10: play P2 (turn 4, e1's shot) at real speed, slow S2 (both turn-4 shots) at ¼ speed (2× crop), "
           "play P3 (turn 5) at real speed; Jiean's A7.10 words.",
    "B13": "Result of B12: play P4 (run 2 turn 4: P in e1's startup, in e1's active phase, in p1's recovery) and P5 "
           "(run 3: R in e1's active phase).",
    "B15": "Result of B14: play P4 full frame (archers frozen, the flag waving while paused) and P5, with the recorded "
           "test_anim_states line burned in.",
}


def inside(seg):
    return any(a <= seg["a"] < seg["b"] <= b for a, b in SPANS[seg["src"]])


sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
for b in sheet["beats"]:
    bid = b["beat_id"]
    if bid in SEGMENTS:
        for s in SEGMENTS[bid]:
            assert inside(s), (bid, s)
        b["shot"]["segments"] = SEGMENTS[bid]
        b["lead_silence_s"] = LEAD[bid]
        b["role_note"] = ROLE[bid]
        n = sum(s["b"] - s["a"] for s in SEGMENTS[bid]) if bid != "B04" else 452
        need = (LEAD[bid] + b["actual_duration_s"]) * 30
        assert n >= need, (bid, n, need)
        print(f"{bid}: {n} frames = {n / 30:.2f} s (needs {need / 30:.2f} s)")
(REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
