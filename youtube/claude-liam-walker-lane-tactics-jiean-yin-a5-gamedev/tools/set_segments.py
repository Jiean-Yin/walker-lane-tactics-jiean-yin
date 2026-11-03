"""Fill the footage beats' segment ranges (capture run-02 frame numbers) and per-segment labels.

Ranges follow the shot boundaries in capture/<mode>-summary.json; each beat's footage is at least as long as its
lead + narration, so nothing is retimed. Usage (reel folder): python tools/set_segments.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
SEGMENTS = {
    "B04": [{"src": "tint", "a": 46, "b": 455}],
    "B06": [{"src": "tint", "a": 455, "b": 997}],
    "B09": [{"src": "diorama", "a": 0, "b": 135,
             "label": "THE SCENE'S OWN CAMERA3D · REAL GODOT RENDER|asset_diorama.tscn @ tag a5, camera as saved"},
            {"src": "diorama", "a": 135, "b": 225,
             "label": "HARNESS CAMERA · REAL GODOT RENDER|both materials at their saved values"},
            {"src": "diorama", "a": 930, "b": 1110,
             "label": "SCRIPTED · REAL GODOT RENDER|linen_dark normal_strength 1.5 → 0 → 1.5, in memory · no file saved"},
            {"src": "diorama", "a": 1110, "b": 1245,
             "label": "SCRIPTED · REAL GODOT RENDER|shader code ALBEDO × 0.5 in memory · the .gdshader file is untouched"}],
    "B11": [{"src": "diorama", "a": 225, "b": 510,
             "label": "SCRIPTED SWEEP · REAL GODOT RENDER|light tile uv_scale 3.65 → 0.5 → 8.0 → 3.65, in memory"},
            {"src": "diorama", "a": 510, "b": 705,
             "label": "SCRIPTED SWEEP · REAL GODOT RENDER|light tile normal_strength 1 → 0 → 2 → 1, in memory"},
            {"src": "diorama", "a": 705, "b": 930,
             "label": "SCRIPTED SWEEP · REAL GODOT RENDER|light tile roughness_scale 1 → 0 → 1, from the lamp's mirror angle"}],
}
LEAD = {"B04": 0.3, "B06": 0.3, "B09": 0.3, "B11": 0.3}

sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
for b in sheet["beats"]:
    if b["beat_id"] in SEGMENTS:
        b["shot"]["segments"] = SEGMENTS[b["beat_id"]]
        b["lead_silence_s"] = LEAD[b["beat_id"]]
(REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("segments set:", ", ".join(SEGMENTS))
