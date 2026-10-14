"""Bind Remotion highlight cues to the measured narration (character position -> time) and set durations.

Usage (reel folder): python tools/set_props.py
"""
import json
import math
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
FPS = 30

CODE_CUES = {
    "B10": [("swaps one static image", 180, "line 180: one static texture per state"),
            ("idle image's scale", 179, "lines 176-179: every pose uses the idle image's scale"),
            ("flip h", 184, "line 184: flip_h turns the enemy to face left"),
            ("measured up from the base", 185, "line 185: positioned from the base disc")],
    "B12": [("one unit at a time", 341, "line 341: attack_order() alternates sides, one unit each"),
            ("killed before its turn", 344, "lines 343-344: killed before its turn -> no attack"),
            ("The slice has one enemy", 341, "R1: one marching enemy (analyze_variants.gd search)")],
    "B15": [("feeds each event here", 105, "line 105: on_event(ev) matches the event type"),
            ("A move plays the hop", 107, "line 107: moved -> SFX-HOP"),
            ("Damage on the enemy", 118, "line 118: damaged enemy, by the player -> SFX-HIT"),
            ("Damage on you", 115, "line 115: damaged player -> SFX-HURT"),
            ("Sound never decides", 103, "no state is written here; tests: muted run == unmuted run")],
}
CARD_CUES = {"B02": ["Read the board", "Plans collide", "Every piece has weight", "when you lose a piece"]}


def t_of(beat, phrase, lead=0.2):
    text = beat["narration_text"]
    i = text.find(phrase)
    if i < 0:
        raise SystemExit(f"{beat['beat_id']}: phrase not found: {phrase}")
    return round(max(0.0, beat["actual_duration_s"] * i / len(text) - lead), 2)


def main():
    p = REEL / "beat_sheet.json"
    sheet = json.loads(p.read_text(encoding="utf-8"))
    for b in sheet["beats"]:
        props = ((b.get("shot") or {}).get("remotion") or {}).get("props")
        if props is None:
            continue
        dur = math.ceil(b["actual_duration_s"] * FPS - 1e-8) / FPS
        bid = b["beat_id"]
        if bid in CODE_CUES:
            props["durationSeconds"] = dur
            props["cues"] = [{"at": t_of(b, ph), "line": ln, "label": lab} for ph, ln, lab in CODE_CUES[bid]]
        if bid in CARD_CUES:
            props["durationSeconds"] = dur
            props["cues"] = [{"at": t_of(b, ph), "card": i} for i, ph in enumerate(CARD_CUES[bid])]
    p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("cues set")


if __name__ == "__main__":
    main()
