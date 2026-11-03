"""Bind GodotDevWorkbench line highlights to the measured narration (character position -> time), and set every
Remotion beat's durationSeconds to its frame-exact length.

Usage (reel folder): python tools/set_props.py
"""
import json
import math
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
FPS = 30
CODE_CUES = {
    "B03": [("Line three", 3, "line 3: exposed_amount, 0.0 to 1.0, set by the driver"),
            ("Line seven is the colour line", 7, "line 7: Jiean's colour line"),
            ("capped at seventy percent", 7, "× 0.7: at full strength 70 % red, face and bow still show"),
            ("Only red, green and blue change", 7, "COLOR.rgb only: alpha untouched")],
    "B05": [("is the planned square in reach", 33, "line 33: target 1.0 if exposed, else 0.0"),
            ("Line thirty-four", 34, "line 34: move_toward at 5 per second of game time"),
            ("why pause holds it still", 32, "line 32: nothing moves while main.paused"),
            ("Line thirty-seven", 37, "line 37: only the player's own material")],
    "B08": [("on line eleven", 11, "line 11: the shared shader"),
            ("the tint on line thirteen", 13, "line 13: tint #9A7F55 (linen_light: white)"),
            ("normal strength on line sixteen", 16, "line 16: normal_strength 1.5 (linen_light: 1.0)")],
    "B10": [("Line four", 4, "line 4: albedo_tex with source_color = colour"),
            ("Line nine", 9, "line 9: roughness_tex, no colour hint = data"),
            ("Line eleven", 11, "line 11: normal_tex with hint_normal = directions"),
            ("The import settings agree", 11, "import: lossless; normal_map flag only on the normal maps")],
    "B12": [("Line four samples it", 4, "line 4: grey_srgb with source_color"),
            ("line five without", 5, "line 5: grey_raw, no hint"),
            ("line six picks", 6, "line 6: use_srgb picks which writes ALBEDO"),
            ("predicted that the hinted quad", 10, "prediction: A 64/128/192 · B 137/188/225")],
    "B15": [("uniform list", 168, "line 168: get_shader_uniform_list()"),
            ("checks the names and types", 170, "lines 170-177: names exactly, then types and hint_range"),
            ("won't report defaults or source colour", 177, "line 177: the list gives the type only, no defaults, no source_color")],
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
            rem["props"]["cues"] = [{"at": t_of(b, ph), "line": ln, "label": lab} for ph, ln, lab in CODE_CUES[bid]]
            print(bid, [(c["at"], c["line"]) for c in rem["props"]["cues"]])
    p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
