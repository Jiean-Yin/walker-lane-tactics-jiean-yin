"""Revision after viewing every code beat's last frame (2026-11-03): at size 30, B10 cut line 12, B12 cut lines 13-14,
B15 cut lines 175-177 (and the line-177 highlight); B03 and B05 wrapped their key line. Per-beat code size so every
excerpt fits its panel. Code text is unchanged. Usage (reel folder): python tools/patch_props_r2.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
SIZE = {"B03": 28, "B05": 28, "B10": 26, "B12": 26, "B15": 24}
p = REEL / "beat_sheet.json"
sheet = json.loads(p.read_text(encoding="utf-8"))
for b in sheet["beats"]:
    if b["beat_id"] in SIZE:
        b["shot"]["remotion"]["props"]["codeFontSize"] = SIZE[b["beat_id"]]
p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("patched", SIZE)
