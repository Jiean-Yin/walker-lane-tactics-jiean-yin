"""Bind GodotDevWorkbench line highlights to the measured narration (character position -> time).

Usage (reel folder): python tools/set_props.py
"""
import json
import math
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
FPS = 30
CODE_CUES = {
    "B07": [("The board", 42, "line 42: board_square at x = -1.2"),
            ("the archer at the origin", 44, "line 44: archer_piece, no position line = (0, 0, 0)"),
            ("the flag at one point one", 47, "line 47: goal_flag at x = 1.1"),
            ("None is lifted", 47, "every y = 0: the base origin should stand each model on the floor")],
    "B12": [("loads each model, then the diorama", 171, "lines 171-172: instance the diorama, add it to the tree"),
            ("await process", 173, "line 173: wait one frame, so the nodes are inside the tree"),
            ("before the nodes were in the scene tree", 174, "line 174: refuse to measure outside the tree"),
            ("no frustum", 181, "lines 181-182: the camera must have 6 frustum planes"),
            ("One impossible failure", 181, "run 1: all three measured at x ~ 0 -> the overlap check failed")],
}


def t_of(beat, phrase, lead=0.2):
    text = beat["narration_text"]
    i = text.find(phrase)
    if i < 0:
        raise SystemExit(f"{beat['beat_id']}: phrase not found: {phrase}")
    voice = beat.get("voice_duration_s", beat["actual_duration_s"])
    return round(max(0.0, beat.get("lead_silence_s", 0.0) + voice * i / len(text) - lead), 2)


def main():
    p = REEL / "beat_sheet.json"
    sheet = json.loads(p.read_text(encoding="utf-8"))
    for b in sheet["beats"]:
        bid = b["beat_id"]
        if bid not in CODE_CUES:
            continue
        props = b["shot"]["remotion"]["props"]
        props["durationSeconds"] = math.ceil(b["actual_duration_s"] * FPS - 1e-8) / FPS
        props["cues"] = [{"at": t_of(b, ph), "line": ln, "label": lab} for ph, ln, lab in CODE_CUES[bid]]
        print(bid, props["cues"])
    p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
