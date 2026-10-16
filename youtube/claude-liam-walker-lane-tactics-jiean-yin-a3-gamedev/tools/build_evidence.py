"""Write gamedev-evidence.json (schema 1, teaching_contract code-then-result-v1).

--game is the isolated git-archive copy of commit e415255's godot/ folder (byte-identical to the commit's blobs,
checked file by file with git hash-object). Every authored file is hashed and either associated with a component of
this film (the Assignment 3 additions) or excluded with a reason (the unchanged Assignment 2 slice).
Excerpts shown by GodotDevWorkbench beats are recorded as `excerpts`; the two Blender build-script excerpts (outside
godot/, shown with ClaudeCodeBeat) are recorded and verified here as `external_excerpts` (the checker ignores them).
Usage (reel folder): python tools/build_evidence.py [GAME_DIR] [TOOLS_DIR]
"""
import hashlib
import json
import sys
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = Path(sys.argv[1] if len(sys.argv) > 1 else "C:/dev/a3-capture/e415255/godot")
TOOLS = Path(sys.argv[2] if len(sys.argv) > 2 else "C:/dev/a3-capture/e415255/tools/blender")

COMPONENTS = {
    "archer-piece-asset": {
        "explanation": "assets/models/archer_piece.glb: the unit, 0.40 x 0.80 x 0.40 m in Godot (Blender 0.40 x 0.40 x 0.80), "
                       "254 triangles, 5 flat materials, origin at the base; built by Claude through the MCP "
                       "(tools/blender/build_archer_piece.py, B03), with Jiean's hand edit moving the bow +0.08 m in Y "
                       "(B04-B05), exported headless with +Y up. The .import sidecar holds Godot's import settings "
                       "(generate_lods=true, not examined by the check). Seen in Godot in B02, B08, B09.",
        "beat_ids": ["B02", "B04", "B05", "B09"],
        "files": ["assets/models/archer_piece.glb", "assets/models/archer_piece.glb.import"]},
    "board-square-asset": {
        "explanation": "assets/models/board_square.glb: one tile of the five-lane board, 1.00 x 0.05 x 1.00 m, 60 triangles, "
                       "slab #D8C7A0 and border #9A7F55 (revision A3-R1, chosen by Jiean, B10). Seen in Godot in B02, "
                       "B08 and from above in B11.",
        "beat_ids": ["B02", "B10", "B11"],
        "files": ["assets/models/board_square.glb", "assets/models/board_square.glb.import"]},
    "goal-flag-asset": {
        "explanation": "assets/models/goal_flag.glb: marks the enemy back row, 0.45 x 1.20 x 0.30 m, 84 triangles, "
                       "walnut base and pole, enemy-red cloth only 0.02 m thick, so it is edge-on from +/-X (Claude's "
                       "report in the student's recording, B06; seen in the orbit, B08).",
        "beat_ids": ["B02", "B06", "B08"],
        "files": ["assets/models/goal_flag.glb", "assets/models/goal_flag.glb.import"]},
    "diorama-scene": {
        "explanation": "diorama/asset_diorama.tscn, written by hand by Claude: a 5 x 3 m floor at y = 0 in the table colour, "
                       "one DirectionalLight3D with shadows, a WorldEnvironment, a Camera3D at (0, 1.1, 3), and the three "
                       ".glb scenes instanced at x = -1.2, 0 and 1.1 with y = 0 (B07). project.godot sets the "
                       "Compatibility renderer used for the capture. Shown running in B08-B09 and B11 (capture run-02).",
        "beat_ids": ["B07", "B08", "B09"],
        "files": ["diorama/asset_diorama.tscn", "project.godot"]},
    "headless-check": {
        "explanation": "tests/check_assets.gd measures each .glb alone (AABB, height axis, lowest y, node scale/rotation, "
                       "triangles, albedo colours) and then the diorama (gap to the Floor mesh's top, camera frustum, "
                       "overlap), writing a JSON report through tests/test_report.gd. Lines 171-182 (B12) hold the fix: "
                       "wait one frame and refuse to measure outside the tree. Results: run 1 32/33 (faulty), run 2 "
                       "38/38, film rerun 38/38 (B13). Headless uses a dummy renderer: nothing about looks is tested.",
        "beat_ids": ["B12", "B13"],
        "files": ["tests/check_assets.gd", "tests/test_report.gd"]},
}
A2 = ("Assignment 2 slice file, byte-identical between film-source-v1 and e415255 (git diff is empty); explained in the "
      "Assignment 2 film. Not part of the Assignment 3 assets, scene or check.")
EXCERPTS = [("B07", "diorama/asset_diorama.tscn", 41, 47), ("B12", "tests/check_assets.gd", 171, 182)]
PAIRS = [("B07", "B08", "media/B08.mp4",
          "Capture run-02: the scene's own Camera3D shows the floor and the three models side by side (board left, "
          "archer centre, flag right), then one scripted orbit: all three upright on the floor; passing +X the flag "
          "cloth is a thin line; from behind it is in shadow."),
         ("B12", "B13", "media/B13.mp4",
          "The recorded reports beside the brief: sizes, height axis Y, lowest y 0.0000, 254/60/84 triangles and "
          "every colour; run 1 32/33 (kept), run 2 38/38, the film's rerun 38/38; labelled headless, no rendering.")]
EXTERNAL = [("B03", "tools/blender/build_archer_piece.py", [135, 140], "B04", "media/B04.mp4",
             "Student's recording 0:00-0:09.6: orbiting the finished archer, the bow (to z 0.65) stands in front of "
             "the eye (z 0.60) on the facing side."),
            ("B10", "tools/blender/build_board_square.py", [142, 143], "B11", "media/B11.mp4",
             "Capture run-02 shot F: the board square from above with darker border strips; the slab renders very "
             "light under the lamp.")]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    beats = {b["beat_id"]: b for b in sheet["beats"]}
    owner = {}
    for cid, c in COMPONENTS.items():
        for f in c["files"]:
            owner.setdefault(f, []).append(cid)
    inv = sorted(p.relative_to(GAME).as_posix() for p in GAME.rglob("*") if p.is_file()
                 and not any(x in (".godot", ".git") for x in p.relative_to(GAME).parts) and p.suffix != ".uid")
    roles = {".gd": "GDScript source", ".tscn": "saved scene", ".godot": "project configuration",
             ".glb": "3D model (glTF binary, exported headless from Blender)", ".import": "import settings sidecar"}
    files = [{"path": f, "sha256": sha(GAME / f), "role": roles.get(Path(f).suffix, "file"), "component_ids": owner[f]}
             for f in inv if f in owner]
    exclusions = [{"path": f, "reason": A2} for f in inv if f not in owner]
    excerpts = []
    for bid, path, a, b in EXCERPTS:
        text = "\n".join((GAME / path).read_text(encoding="utf-8").splitlines()[a - 1:b])
        if beats[bid]["shot"]["remotion"]["props"]["code"] != text:
            raise SystemExit(f"{bid}: displayed code differs from {path}:{a}-{b}")
        excerpts.append({"beat_id": bid, "path": path, "start_line": a, "end_line": b, "text": text})
    pairs = [{"code_beat": c, "result_beat": r, "observation": o, "media": {"path": m, "sha256": sha(REEL / m)}}
             for c, r, m, o in PAIRS]
    ext = []
    for bid, path, lines, rbid, media, obs in EXTERNAL:
        src = TOOLS / Path(path).name
        all_lines = src.read_text(encoding="utf-8").splitlines()
        shown = beats[bid]["shot"]["remotion"]["props"]["code"].split("\n")
        for n in lines:
            if all_lines[n - 1] not in shown:
                raise SystemExit(f"{bid}: line {n} of {path} is not shown verbatim")
        ext.append({"beat_id": bid, "path": path, "revision": "e415255", "sha256": sha(src), "lines": lines,
                    "text": {str(n): all_lines[n - 1] for n in lines},
                    "note": "Comment lines starting '# line' in the displayed code are our markers, not source.",
                    "result_beat": rbid, "observation": obs,
                    "media": {"path": media, "sha256": sha(REEL / media)}})
        if beats[rbid]["shot"].get("evidence_media") != media:
            raise SystemExit(f"{rbid}: evidence_media not set")
    data = {"schema_version": 1, "teaching_contract": "code-then-result-v1",
            "game": {"name": "walker-lane-tactics-jiean-yin", "project": "godot/project.godot",
                     "source_revision": sheet["metadata"]["game"]["source_revision"],
                     "game_dir": "isolated git-archive copy of e415255:godot (core.autocrlf=false)",
                     "note": f"All {len(inv)} authored files are byte-identical to the e415255 blobs (git hash-object)."},
            "files": files, "components": [{"id": k, **v} for k, v in COMPONENTS.items()],
            "excerpts": excerpts, "exclusions": exclusions, "code_result_pairs": pairs,
            "external_excerpts": ext}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gamedev-evidence.json: {len(files)} files, {len(exclusions)} exclusions, {len(excerpts)} excerpts, "
          f"{len(pairs)} pairs, {len(ext)} external excerpts")


if __name__ == "__main__":
    main()
