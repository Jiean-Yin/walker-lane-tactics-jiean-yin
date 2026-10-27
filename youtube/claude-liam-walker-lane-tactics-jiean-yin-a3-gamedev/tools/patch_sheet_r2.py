"""In-place sheet revision after the first Remotion pass (recorded, not regenerated):

- B01: 3.4 s silent tail so the hesitant writer finishes its correction on screen (first render ended mid-word).
- B03: largeText off (the 101-character source lines were clipped at the large size).
- B10: show lines 142-143 only (line 132's 117-character comment was clipped).
- B07: shorter Camera3D note (was clipped at the panel's bottom).
- B12: excerpt lines 171-182 at the minimum code size, two notes (lines past 176 were cut off).
- evidence_media on the result beats B04, B08, B11, B13.
Usage (reel folder): CAPTURE=<capture-copy> python tools/patch_sheet_r2.py
"""
import json
import os
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = Path(os.environ["CAPTURE"]) / "e415255/godot"


def main():
    p = REEL / "beat_sheet.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    B = {b["beat_id"]: b for b in s["beats"]}
    B["B01"]["tail_silence_s"] = 3.4
    B["B03"]["shot"]["remotion"]["props"]["largeText"] = False
    B["B10"]["shot"]["remotion"]["props"]["code"] = ("# lines 142-143 (revision A3-R1, run after the first look)\n"
                                                     "mat = bpy.data.materials[\"linen_border\"]\n"
                                                     "bsdf = set_flat_color(mat, \"9A7F55\")")
    B["B10"]["shot"]["label"] = "Actual source excerpt (build_board_square.py @ e415255, lines 142-143) · reconstructed code view"
    B["B10"]["role_note"] = "Code beat: CHANGE-BRIEF A3-R1. Lines 142-143 verbatim; the comment line is our marker. Result in B11."
    B["B07"]["shot"]["remotion"]["props"]["notes"][2] = {"label": "Camera3D (lines 35-39)", "value": "(0, 1.1, 3), fov 50"}
    pr = B["B12"]["shot"]["remotion"]["props"]
    pr["code"] = "\n".join((GAME / "tests/check_assets.gd").read_text(encoding="utf-8").splitlines()[170:182])
    pr["startLine"] = 171
    pr["codeFontSize"] = 23
    pr["source"] = "godot/tests/check_assets.gd · lines 171–182 · commit e415255"
    pr["notes"] = [{"label": "Run 1 (…1792106172.json)", "value": "32/33: measured in _initialize(), outside the tree; kept"},
                   {"label": "Run 2 (…1792106192.json)", "value": "38/38 after the fix"}]
    pr["output"] = ["Headless: dummy renderer, nothing is drawn · godot --headless --script res://tests/check_assets.gd"]
    B["B12"]["role_note"] = "Code beat: check_assets.gd lines 171-182 verbatim. Result (the recorded numbers) in B13."
    for r in ("B04", "B08", "B11", "B13"):
        B[r]["shot"]["evidence_media"] = f"media/{r}.mp4"
    p.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("patched")


if __name__ == "__main__":
    main()

# r3 (Gate T, applied in place after the first ./art final attempt was blocked):
#   B03 sparkLine -> "Bow reaches z 0.65; eye at z 0.60; both on +X" (13 -> 11 words)
#   B07 output -> ["Hand-written by Claude; not yet saved from the editor (A3.8)"]
#   B03/B10 ClaudeCodeBeat titles -> bare file names (the revision stays in the burned label)
