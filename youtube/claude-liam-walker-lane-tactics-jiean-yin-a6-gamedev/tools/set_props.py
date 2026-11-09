"""Bind GodotDevWorkbench line highlights to the measured narration (character position -> time), and set every
Remotion beat's durationSeconds to its frame-exact length. Every highlighted line is the line the narration names,
in the excerpt read from the tag-a6 copy (checked by tools/build_sheet.py's excerpts).

Usage (reel folder): python tools/set_props.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
FPS = 30
CODE_CUES = {
    "B03": [("Line ninety-one", 91, "line 91: saved with emitting = false"),
            ("born all at once", 96, "line 92: 14 particles · line 96: explosiveness 1.0"),
            ("Up to seventy-five degrees", 102, "line 102: spread 75° around straight up"),
            ("at one hundred forty", 104, "line 104: 140 px/s minimum · line 105, just below: 260 maximum"),
            ("gravity pulls them", 103, "line 103: gravity (0, 900) px/s²"),
            ("Line ninety-eight", 98, "line 98: local_coords = false")],
    "B05": [("reads the list of events", 37, "line 37: main.played_events, read only"),
            ("Line forty-four", 44, "line 44: a new \"damaged\" event → _spawn()"),
            ("Line forty-nine", 49, "line 49: speed_scale = game speed"),
            ("The driver reads the game", 46, "line 46: _speed() reads main.paused and main.time_scale")],
    "B07": [("Line seventy-five", 75, "line 75: a new HitBurst instance per hit"),
            ("Line seventy-seven", 77, "line 77: archer position + (0, −40)"),
            ("Line seventy-nine", 79, "line 79: Dust.finished → queue_free"),
            ("a child of the driver", 76, "line 76: added under the driver, not the archer")],
    "B09": [("The flash wasn't planned", 60, "line 60: Flash, one particle"),
            ("Line sixty-four", 64, "line 64: lifetime 1.08 s (brief: 0.12 s)")],
    "B11": [("two GPU particle nodes", 87, "line 87: Streak, a GPUParticles2D"),
            ("line ninety-nine keeps it off", 99, "line 99: trail_enabled = false"),
            ("line ninety-eight does the work", 98, "line 98: local_coords = false")],
    "B13": [("While the arrow is in the game's list", 68, "line 68: still in main._arrows?"),
            ("line sixty-nine", 69, "line 69: to the tip, with main.gd's arc formula"),
            ("line seventy-four", 74, "line 74: both emitters stop"),
            ("a countdown starts", 72, "line 72: the longest lifetime, 0.7 s of game time"),
            ("Then the node is freed", 66, "line 66: queue_free()")],
    "B15": [("turbulence, line seventy-nine", 79, "line 79: turbulence_enabled = true"),
            ("an influence between point one and point two", 82, "lines 82–83: influence 0.1 to 0.2"),
            ("damping slows it down", 73, "lines 73–74: damping 15 to 20"),
            ("the colour ramp went", 78, "line 78: color_ramp → Gradient_wisps (line 59)")],
    "B17": [("reads the scene as plain text", 132, "line 132: the scene file, line by line, as text"),
            ("looking for Godot three names", 135, "line 135: a key in FORBIDDEN_KEYS"),
            ("Why read the text", 140, "line 140: fails on any hit, naming the line")],
    "B19": [("compares each trail's stop", 566, "lines 562–567: the nearest hit to each stop"),
            ("The brief said: within one frame", 568, "line 568: the brief's bound was −1 to 1"),
            ("The agent's first run measured", 569, "line 569: now −2 to 0 (Revision 1)")],
    "B21": [("line seventy-seven", 77, "line 77: the wall clock, in a node that runs last"),
            ("Six hundred frames", 82, "line 82: one frame time per frame"),
            ("It reports the means", 82, "the means per case: 2 × 600 frames")],
    "B23": [("Line one fifteen", 115, "line 115: the viewport's measured GPU time"),
            ("once a second it prints the mean", 120, "lines 118–123: once a second, the mean")],
    "B25": [("Jay-Ann's table", 252, "process_display_param(): every particle, every step"),
            ("two fifty-four", 254, "line 254: scale over life (Jiean's row)"),
            ("two fifty-five", 255, "line 255: colour over life (Jiean's row)")],
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
