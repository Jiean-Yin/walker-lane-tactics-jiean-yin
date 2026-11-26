"""Fit the GodotDevWorkbench code beats to the panel (A7 film; limits measured in the A6 film's first render).

The workbench lays out at 1920 x 1080: its code panel holds about 14 rows at codeFontSize 23, 13 at 24, 12 at 26,
11 at 28-30 and 10 at 34, and wraps lines longer than about 1000 px. The side-notes column (390 px) holds about
three notes of 5 value lines in all. The first render cut off B03's lines 100-105 and several notes. Each excerpt
below still contains every line the narration names by number; the code text is read from the tag copy, never
typed. Run after tools/build_sheet.py and before tools/set_props.py.
Usage (reel folder): CAPTURE=<capture-copy> python tools/fit_workbench.py
"""
import json
import math
import os
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = Path(os.environ["CAPTURE"]) / "a7" / "godot"
ROWS = {23: 14, 24: 13, 26: 12, 28: 11, 30: 11, 34: 10}
CHARS = {23: 72, 24: 69, 26: 64, 28: 59, 30: 55, 34: 49}  # conservative: about 1000 px of mono text per row

FIT = {  # beat: (start, end, codeFontSize, notes [(label, value)], output)
    "B03": (11, 24, 23, [("flag_red.png", "500 × 249 → 4 × 1 cells of 125 × 249"),
                         ("Seam rule", "no key at length"), ("Written by", "agent 3 (b21c881)")],
            ["Sheet: Flag Animation Sheet by Fokko, CC0"]),
    "B05": (26, 36, 26, [("Pole's left edge", "x = 4, 8, 6, 3 in cells 0–3"), ("Offset.x", "0, −4, −2, +1 source px"),
                         ("One writer", "the flag's AnimationPlayer")],
            ["The sheet itself is never edited"]),
    "B07": (165, 177, 23, [("Also checked", "discrete · step 0.125 · LOOP_LINEAR"), ("Result", "43/43 at 60 fps"),
                           ("Written by", "agent 3; guard by Claude Code")],
            ["Key times compared within half a frame, never =="]),
    "B10": (31, 43, 23, [("Key time = frame ÷ 60", "f0 · f12 0.2 · f33 0.55 · f40 · f48 0.8"),
                         ("Tracks", "Rig position · Upper and Bow rotation"), ("Written by", "agent 4 (0e60554)")],
            ["LOOP_NONE · 0.8 s = 48 frames at 60 fps"]),
    "B12": (109, 116, 28, [("Rig, Upper, Bow", "written only by the clip"), ("Mount", "place, facing, visibility: piece.gd"),
                           ("Written by", "agent 5; plan approved by Jiean")],
            ["POSE_CLIPS: draw → shoot; other poses → no clip"]),
    "B14": (170, 182, 23, [("shoot", "MANUAL · advance(dt), game time"), ("wave", "IDLE · process tick, real time"),
                           ("tick()", "not while paused (main.gd:166)")],
            ["Gameplay reads _arrows on the process tick; no physics tick"]),
    "B16": (88, 100, 23, [("Also checked", "keys f0/12/33/40/48 · step 1/60"), ("Result", "51/51 at 60 fps"),
                          ("Written by", "agent 4 (0e60554)")],
            ["track_problems() is a test helper, not Godot API"]),
    "B18": (61, 68, 30, [("Tuning r1", "bow's frame-48 key 20° → 8°"), ("Approved by", "Jiean: \"Approve r1\""),
                         ("Read-back", "expected values follow the brief")],
            ["One change per revision; prediction before the edit"]),
    "B20": (29, 38, 26, [("Cases", "4 boundaries × 3 offsets × 3 keys"), ("Result", "102/102 at 60 fps"),
                         ("Written by", "Claude Code (ab95468)")],
            ["Keys go in through Input.parse_input_event"]),
}


def rows(code, font):
    return sum(max(1, math.ceil(len(ln.replace("\t", "  ")) / CHARS[font])) for ln in code.split("\n"))


def main():
    p = REEL / "beat_sheet.json"
    sheet = json.loads(p.read_text(encoding="utf-8"))
    for b in sheet["beats"]:
        bid = b["beat_id"]
        if bid not in FIT:
            continue
        a, z, font, notes, output = FIT[bid]
        props = b["shot"]["remotion"]["props"]
        rel = props["path"].removeprefix("res://")
        code = "\n".join((GAME / rel).read_text(encoding="utf-8").split("\n")[a - 1:z])
        n = rows(code, font)
        assert n <= ROWS[font], (bid, n, ROWS[font])
        assert len(notes) <= 3 and all(len(v) <= 46 for _, v in notes), bid
        assert len(" · ".join(output)) <= 140, (bid, len(" · ".join(output)))
        assert all(len(o.split()) <= 12 for o in output), (bid, "Gate T §8.5: at most 12 words per output")
        props.update({"code": code, "startLine": a, "codeFontSize": font,
                      "source": f"godot/{rel} · lines {a}–{z} · tag a7",
                      "notes": [{"label": k, "value": v} for k, v in notes], "output": output})
        b["excerpt"] = {"path": rel, "start_line": a, "end_line": z}
        print(f"{bid}: {rel} {a}-{z}, font {font}, {n}/{ROWS[font]} rows")
    p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
