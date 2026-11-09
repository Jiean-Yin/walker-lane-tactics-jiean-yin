"""Write SHOTLIST.md from beat_sheet.json (frame counts are the measured, frame-exact ones).
Usage (reel folder): python tools/write_shotlist.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
rows = []
for i, b in enumerate(sheet["beats"], 1):
    shot = b["shot"]
    if shot.get("remotion"):
        vis = shot["remotion"]["pattern"]
        props = shot["remotion"]["props"]
        if vis == "GodotDevWorkbench":
            vis += f": {props['source']}, highlights " + " / ".join(str(c["line"]) for c in props.get("cues", []))
        label = shot.get("label") or ("Godot editor reconstruction · source-backed teaching view"
                                      if vis.startswith("GodotDevWorkbench") else "—")
    elif shot.get("segments"):
        vis = "final capture: " + " + ".join(f"{s['src']} {s['a']}–{s['b']}" for s in shot["segments"])
        label = " / ".join(sorted({(s.get("label") or shot["label"]).split("|")[0] for s in shot["segments"]}))
    else:
        vis = "still: " + shot.get("composite", "")
        label = shot.get("label") or "—"
    rows.append(f"| {i} | {b['beat_id']} {b['act']} | {vis} | {label} | {b['clip_frames']} |")
total = sum(b["clip_frames"] for b in sheet["beats"])
text = (f"# SHOTLIST — {sheet['metadata']['title']}\n\n"
        "3840×2160, 30 fps. Durations are frame counts from the measured narration (or the exact clip length for "
        "engine beats; nothing retimed). Labels in short form.\n\n"
        "| # | Beat | Visual | Label on screen | Frames |\n|---|---|---|---|---|\n" + "\n".join(rows) +
        f"\n\nTotal {total} frames = {total / 30:.1f} s.\n\nCode → result pairs: B03 → B04, B05 → B06, B07 → B08, "
        "B09 → B10, B11 → B12, B13 → B14, B15 → B16, B17 → B18, B19 → B20, B21 → B22, B23 → B24, B25 → B26 (each "
        "result immediately follows its code). Footage: play = the 30 fps capture; slow = the 120 fps capture shown "
        "at 30 fps (¼ speed).\n")
(REEL / "SHOTLIST.md").write_text(text, encoding="utf-8")
print(f"SHOTLIST.md: {len(rows)} beats, {total} frames")
