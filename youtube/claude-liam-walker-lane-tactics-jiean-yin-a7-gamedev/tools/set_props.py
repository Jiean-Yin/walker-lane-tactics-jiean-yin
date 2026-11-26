"""Bind GodotDevWorkbench line highlights to the measured narration (character position -> time), and set every
Remotion beat's durationSeconds to its frame-exact length. Every highlighted line is the line the narration names,
in the excerpt read from the tag-a7 copy (checked by tools/build_sheet.py's excerpts).

Usage (reel folder): python tools/set_props.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
FPS = 30
CODE_CUES = {
    "B03": [("line seventeen", 17, "line 17: the track keys FlagSprite:frame"),
            ("Four keys, an eighth", 21, "line 21: keys at 0, 0.125, 0.25, 0.375 s"),
            ("the step is one frame period", 13, "line 13: step 0.125 = one frame at 8 fps"),
            ("The length is half a second", 11, "line 11: length 0.5 = four intervals"),
            ("the last frame is three", 24, "line 24: frames 0, 1, 2, 3; no key at length")],
    "B05": [("a second track keys the sprite's offset", 29, "line 29: FlagSprite:offset, discrete"),
            ("on the same", 33, "line 33: the same four times"),
            ("zero, minus four", 36, "line 36: x = 0, −4, −2, +1")],
    "B07": [("Line one seventy-three", 173, "line 173: every key < hframes × vframes"),
            ("fewer than horizontal times vertical", 165, "line 165: cells = hframes × vframes"),
            ("loads without a word", 175, "line 175: the frame-range check")],
    "B10": [("Line thirty-three", 33, "line 33: step = 1/60"),
            ("Line forty-one", 41, "line 41: key times = frame ÷ 60"),
            ("Three tracks move the rig", 37, "line 37: track 0, Rig:position")],
    "B12": [("line one thirteen", 113, "line 113: the pose's clip, from POSE_CLIPS"),
            ("line one fifteen", 115, "line 115: play(clip)"),
            ("line one sixteen", 116, "line 116: advance(0): frame 0 at once"),
            ("Line one twelve", 112, "line 112: stop() first")],
    "B14": [("Line one eighty-two", 182, "line 182: advance(dt), the game's time"),
            ("So when the game pauses", 181, "line 181: only while the clip plays")],
    "B16": [("It branches on track type", 88, "line 88: match on the track type"),
            ("a value track has to name a property", 89, "line 89: value and bezier tracks"),
            ("line ninety-nine", 99, "line 99: no such property → reported")],
    "B18": [("the bow turns at the hand", 61, "line 61: Rig/Upper/Bow:rotation"),
            ("line sixty-eight", 68, "line 68: last key 0.139626 rad = 8° (was 20°)")],
    "B20": [("frames zero, twelve", 31, "line 31: boundaries 0, 12, 33, 48"),
            ("P, R and Enter", 33, "line 33: the three interrupts"),
            ("one frame before, on, and after", 32, "line 32: offsets −1, 0, +1")],
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
        rem = b["shot"].get("remotion")
        if not rem:
            continue
        rem["props"]["durationSeconds"] = b["clip_frames"] / FPS
        bid = b["beat_id"]
        if bid in CODE_CUES:
            p0, code = rem["props"]["startLine"], rem["props"]["code"].split("\n")
            for _, ln, _ in CODE_CUES[bid]:
                assert p0 <= ln < p0 + len(code), (bid, ln)
            rem["props"]["cues"] = [{"at": t_of(b, ph), "line": ln, "label": lab} for ph, ln, lab in CODE_CUES[bid]]
            print(bid, [(c["at"], c["line"]) for c in rem["props"]["cues"]])
    p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
