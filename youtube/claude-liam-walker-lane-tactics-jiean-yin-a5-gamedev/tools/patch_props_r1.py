"""Revision after the B03 pilot render (2026-11-03): at codeFontSize 34 the colour line wrapped and the third source
note was cut off at the panel's bottom. Code size 30 (as in the A3 film) and one-line notes. Code text is unchanged.
Usage (reel folder): python tools/patch_props_r1.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
NOTES = {
    "B03": [("Written by", "Jiean, by hand (80fc669)"), ("exposed_color", "#E0453A (main.gd:47)"),
            ("Runs", "once per sprite pixel")],
    "B05": [("RATE", "5.0 per s of game time"), ("Own material", "piece.gd:56-59"),
            ("Written by", "claude -p agent (44b2acb)")],
    "B08": [("linen_light.tres:13", "tint white"), ("linen_light.tres:16", "normal_strength 1.0"),
            ("Both, line 11", "linen_square.gdshader")],
    "B10": [("Import, all", "Lossless · detect_3d off"), ("normal_map flag", "only the two normal maps"),
            ("curl, nor_gl", "0.68 GL · 1.32 DX")],
    "B12": [("hint_greys.png", "3 × 1: 64, 128, 192"), ("Scene", "Linear tonemap, exposure 1"),
            ("Jiean predicted", "B 137 / 188 / 225")],
    "B15": [("Defaults", "read from the source text"), ("Every frame", "checked against the rule"),
            ("Written by", "claude -p agent")],
}
p = REEL / "beat_sheet.json"
sheet = json.loads(p.read_text(encoding="utf-8"))
for b in sheet["beats"]:
    if b["beat_id"] in NOTES:
        props = b["shot"]["remotion"]["props"]
        props["codeFontSize"] = 30
        props["notes"] = [{"label": k, "value": v} for k, v in NOTES[b["beat_id"]]]
p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("patched", ", ".join(NOTES))
