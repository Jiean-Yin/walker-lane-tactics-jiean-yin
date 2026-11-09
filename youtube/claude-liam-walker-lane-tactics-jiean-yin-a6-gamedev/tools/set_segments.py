"""Fill the footage beats' segment ranges (final capture, <capture-copy>/final-out) and per-segment labels.

Frame numbers are master frames of play-4k.mkv (30 fps) and slow-4k.mkv (120 fps, shown at 30 = 1/4 speed). Every
range lies inside one unbroken stretch of recording (SPANS) and was chosen from the event anchors printed by
tools/anchors.py (arrows, hits, P presses). Each beat's footage is at least as long as its lead + narration, so
nothing is retimed. Crops are of the 4K frame, scaled to fill, and say so in their label.
Usage (reel folder): python tools/set_segments.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
# Master-frame spans recorded without a break in engine time (checked in the logs: play jumps only at 527 and 979,
# where unrecorded turns were played; slow has no jump). A segment may cross shots only inside one span.
SPANS = {"play": [(0, 527), (527, 979), (979, 1359)], "slow": [(0, 1133)]}
PLAY = "SCRIPTED KEY PRESSES · REAL GODOT RENDER|main.tscn @ tag a6, isolated copy · Movie Maker, 30 fps · no audio"
SLOW3 = ("¼ SPEED · CROPPED 3× · REAL GODOT RENDER|120 fps capture played at 30 · around the player's archer · "
         "main.tscn @ tag a6")
SLOW2 = "¼ SPEED · CROPPED 2× · REAL GODOT RENDER|120 fps capture played at 30 · both archers · main.tscn @ tag a6"
CROP3 = [240, 1362, 1280, 720]   # 4K pixels: the player's archer and its square, the enemy outside the frame
CROP2 = [384, 990, 1920, 1080]   # 4K pixels: both archers and the arrow's arc
A3_LINE = ("PASS  A3 overlap: on the frame of turn 4's second hit, 2 bursts are alive (the first one not re-fired, "
           "a new instance)")
FIRST_LOOK = "A continous black closely dotted lines into the target square. Clear."  # TUNING.md:125, verbatim

SEGMENTS = {
    # play: turns 2-4 at real speed, the enemy's hit on the player at 259; slow: the same hit at 290, cut at 572
    "B04": [{"src": "play", "a": 110, "b": 271, "label": PLAY},
            {"src": "slow", "a": 250, "b": 572, "crop": CROP3, "label": SLOW3}],
    # run 2 turn 4: hit 636, P 645, unpause 840, second hit 862, shot end 979
    "B06": [{"src": "play", "a": 527, "b": 979, "label": PLAY}],
    # turn 4 at real speed (hits 259, 290), then at 1/4 speed (hits 290, 417; first burst freed 436)
    "B08": [{"src": "play", "a": 200, "b": 330, "label": PLAY},
            {"src": "slow", "a": 250, "b": 699, "crop": CROP2, "label": SLOW2, "quote_pos": "bottom-right",
             "quote_width": 1800,
             "quote": [[A3_LINE, "mono"],
                       ["test_hit_burst_state.gd, 60 fps · evidence/a6/final/test_hit_burst_state_60fps.log:30", True]]}],
    # both turn-4 arrows at real speed; at 1/4 speed the enemy's (249-290) and the player's (375-417); turn 5's (868-909)
    "B12": [{"src": "play", "a": 245, "b": 315, "label": PLAY},
            {"src": "slow", "a": 230, "b": 520, "crop": CROP2, "label": SLOW2},
            {"src": "slow", "a": 845, "b": 1006, "crop": CROP2, "label": SLOW2.replace("both archers", "turn 5"),
             "quote_pos": "bottom-right", "quote_width": 1800,
             "quote": [[FIRST_LOOK, False], ["Jiean, first look at Effect B (TUNING.md)", True]]}],
    # the player's arrow lands at 1/4 speed (trail stop 416, hit 417); run 3: arrow 1078, P 1083, unpause 1233, hit 1238
    "B14": [{"src": "slow", "a": 397, "b": 592, "crop": CROP2, "label": SLOW2},
            {"src": "play", "a": 1063, "b": 1358, "label": PLAY}],
}
LEAD = {"B04": 0.3, "B06": 0.5, "B08": 0.3, "B12": 0.3, "B14": 0.6}
ROLE = {  # the same wording as tools/build_sheet.py, so the sheet need not be rebuilt
    "B04": "Result of B03: play P1-P2 (turns 2-4, the enemy's hit on the player) at real speed, then slow S2 (same hit) "
           "at ¼ speed, cropped 3× around the player's archer.",
    "B06": "Result of B05: play P4 (run 2, turn 4: P 0.3 s after the first hit, held 6.5 s, then P).",
    "B08": "Result of B07: play P2 (turn 4, both hits) at real speed, then slow S2 at ¼ speed (2× crop), with the state "
           "test's A3 overlap line on screen.",
    "B12": "Result of B11: play P2 (turn 4, both arrows) at real speed, then slow S2 and S3 (three arrows) at ¼ speed "
           "(2× crop); Jiean's first look verbatim (TUNING.md).",
    "B14": "Result of B13: slow S2 (the player's arrow lands, 2× crop), then play P5 (run 3: P mid-flight, held 5 s).",
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
        n = sum(s["b"] - s["a"] for s in SEGMENTS[bid])
        print(f"{bid}: {n} frames = {n / 30:.2f} s")
(REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(REEL / "capture/stills-frames.json").write_text(json.dumps({"b02_hit": 261, "b02_flight": 286}, indent=2) + "\n",
                                                 encoding="utf-8")
