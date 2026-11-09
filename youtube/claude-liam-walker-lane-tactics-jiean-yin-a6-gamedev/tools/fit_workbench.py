"""Fit the GodotDevWorkbench code beats to the panel, after the first render (2026-11-08).

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
GAME = Path(os.environ["CAPTURE"]) / "a6" / "godot"
ROWS = {23: 14, 24: 13, 26: 12, 28: 11, 30: 11, 34: 10}
CHARS = {23: 72, 24: 69, 26: 64, 28: 59, 30: 55, 34: 49}  # conservative: about 1000 px of mono text per row

FIT = {  # beat: (start, end, codeFontSize, notes [(label, value)], output)
    "B03": (91, 104, 23, [("Effect A", "Flash 1 · Splinters 14 · Dust 8"), ("Line 105, just below", "velocity max 260.0"),
                          ("Written by", "agent 2a (cb9830b)")],
            ["Look values: in the scene file only", "Textures: GradientTexture2D, no image file"]),
    "B05": (37, 49, 24, [("process_priority", "10: runs after main"), ("Reads only", "main.played_events"),
                         ("Written by", "agent 3a; plan approved by Jiean (dd0ad5c)")],
            ["Enter → _cue_impact → \"damaged\" (main.gd:502) → this driver, same frame"]),
    "B07": (71, 80, 26, [("Retrigger rule", "overlap: Jiean's rule"), ("HIT_OFFSET, line 20", "(0, −40): base → body"),
                         ("Frees itself", "1.22–1.28 s (Rev. 1)")],
            ["Lines 81–84: every emitter starts at the game's speed"]),
    "B09": (60, 66, 34, [("r1 (8aa178c)", "lifetime 0.12 → 0.36"), ("r2 (1079375)", "scale 1.25 → 3.0 (83–84)"),
                         ("r3 (cc9e1ee)", "lifetime 0.36 → 1.08")],
            ["One setting per revision; Claude's prediction committed before each edit (TUNING.md)"]),
    "B11": (87, 99, 24, [("Measured, brief §0", "trail_enabled: nothing drawn"),
                         ("Godot warns", "no trails on Compatibility"), ("Written by", "agent 2b (de4f389)")],
            ["fixed_fps 30 (line 95): thirty particle steps a second"]),
    "B13": (62, 75, 23, [("tip_of, lines 43–47", "main.gd's arc formula"), ("Free timer", "0.7 s, read from the scene"),
                         ("Written by", "agent 3b; plan approved by Jiean (e1e151d)")],
            ["Lines 77–79: a new trail for each new arrow in main._arrows"]),
    "B15": (70, 83, 23, [("Effect B r1 (c3bbb9e)", "#9A8466 α 0.45 → #6E5A44 α 0.7"),
                         ("Chosen by", "Jiean, of two options"), ("GPU only", "no turbulence on CPU")],
            ["ParticleProcessMaterial_wisps (line 64) · colour ramp: Gradient_wisps (line 59)"]),
    "B17": (130, 140, 24, [("FORBIDDEN_KEYS, line 80", "initial_velocity, damping, …"),
                           ("Read-back, lines 145–149", "every §1 value"), ("Written by", "agent 2a (cb9830b)")],
            ["test_hit_burst_config 107 checks · test_arrow_trail_config 135"]),
    "B19": (561, 570, 24, [("Every frame", "after main and drivers"), ("Route", "win_route.json, real keys"),
                           ("Written by", "agent 3b; bound: Claude Code (1268b40)")],
            ["60 fps, real key presses through root.push_input()"]),
    "B21": (76, 86, 26, [("Cases", "empty · off · A ×2 · B ×2"), ("Samples", "2 × 600 frames each"),
                         ("Written by", "agent 7 (f0e5977), unedited")],
            ["Headless: no particle is drawn; this times the CPU side only"]),
    "B23": (115, 123, 24, [("Fixture", "0 off · 1 A ×2 · 2 B ×2 · V vsync"), ("Sweep", "0,1,2,0,1,2 · 8 s each"),
                           ("Written by", "Claude Code (ac38e82, 67d0b30)")],
            ["Display 180 Hz · RTX 3070 Ti Laptop GPU · OpenGL 3.3"]),
    "B25": (252, 257, 34, [("Jiean's rows", "start() 323 · process() 378"), ("Shown here", "scale 254 · colour 255"),
                           ("Jiean's other rows", "3 · 232 · 412 · 441")],
            ["Editor-generated from the Wisps material, saved by Jiean, unedited", "Rows: TEST-REPORT A6.7"]),
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
                      "source": f"godot/{rel} · lines {a}–{z} · tag a6",
                      "notes": [{"label": k, "value": v} for k, v in notes], "output": output})
        b["excerpt"] = {"path": rel, "start_line": a, "end_line": z}
        print(f"{bid}: {rel} {a}-{z}, font {font}, {n}/{ROWS[font]} rows")
    p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
