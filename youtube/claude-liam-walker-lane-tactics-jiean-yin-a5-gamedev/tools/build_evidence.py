"""Write gamedev-evidence.json (schema 1, teaching_contract code-then-result-v1) for the A5 film.

--game is the isolated git-archive copy of tag a5's godot/ folder (each file checked against its a5 blob). Every
authored file is hashed and either associated with a component this film explains (the Assignment 5 additions and
the state they read) or excluded with a reason. Code beats' displayed code must equal the file's lines. B14 is a
still that quotes four single lines; they are verified here as `still_quotes` (not GodotDevWorkbench excerpts).
Usage (reel folder): python tools/build_evidence.py <capture-copy>/a5/godot
"""
import hashlib
import json
import sys
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = Path(sys.argv[1])

COMPONENTS = {
    "exposed-tint-shader": {
        "explanation": "shaders/exposed_tint.gdshader, hand-written by Jiean: canvas_item, exposed_amount "
                       "(hint_range 0-1, default 0.0) and exposed_color (source_color, #E0453A); line 7 mixes the "
                       "sprite's COLOR.rgb toward the red by exposed_amount * 0.7, alpha untouched (B03). Seen in play "
                       "(B04, B06) and at controlled values 0 / 0.5 / 1 / 2 in Jiean's captures (B07).",
        "beat_ids": ["B03", "B04", "B06", "B07"],
        "files": ["shaders/exposed_tint.gdshader"]},
    "exposed-driver": {
        "explanation": "game/exposed_driver.gd (a node in game/main.tscn, process_priority 10) reads main.gd's state, "
                       "planned_offset, paused and time_scale and rules.gd's cells and reach (in_range, Chebyshev 1-2); "
                       "move_toward at 5 per second of game time, holding while paused (B05). game/piece.gd gives every "
                       "sprite its own ShaderMaterial (lines 56-59) and set_exposed_amount(). Result: the capture's "
                       "taps, pause, confirm and turn 4 (B06); the per-frame log has the enemy at 0.0 throughout.",
        "beat_ids": ["B05", "B06", "B04"],
        "files": ["game/exposed_driver.gd", "game/piece.gd", "game/main.tscn", "game/main.gd", "game/rules.gd"]},
    "linen-materials": {
        "explanation": "shaders/linen_square.gdshader (Jiean): spatial; albedo_tex with source_color, roughness_tex as "
                       "data, normal_tex with hint_normal, uv_scale, roughness_scale, normal_strength (B10). Two "
                       "ShaderMaterials, materials/linen_light.tres (tint white, normal_strength 1.0) and linen_dark.tres "
                       "(#9A7F55, 1.5), on two PlaneMesh tiles in diorama/asset_diorama.tscn (B08). The Hessian 380 "
                       "textures and their .import files (Lossless, normal-map flag only on the normal maps, detect_3d "
                       "off), credited in ATTRIBUTION.md. Results: one material vs one shader (B09), the interface sweep "
                       "(B11).",
        "beat_ids": ["B08", "B09", "B10", "B11"],
        "files": ["shaders/linen_square.gdshader", "materials/linen_light.tres", "materials/linen_dark.tres",
                  "diorama/asset_diorama.tscn", "assets/textures/hessian_380/ATTRIBUTION.md",
                  "assets/textures/hessian_380/hessian_380_diff_1k.jpg",
                  "assets/textures/hessian_380/hessian_380_diff_1k.jpg.import",
                  "assets/textures/hessian_380/hessian_380_rough_1k.png",
                  "assets/textures/hessian_380/hessian_380_rough_1k.png.import",
                  "assets/textures/hessian_380/hessian_380_nor_gl_1k.png",
                  "assets/textures/hessian_380/hessian_380_nor_gl_1k.png.import",
                  "assets/textures/hessian_380/hessian_380_nor_dx_1k.png",
                  "assets/textures/hessian_380/hessian_380_nor_dx_1k.png.import"]},
    "hint-experiment": {
        "explanation": "shaders/hint_experiment.gdshader (Jiean): unshaded; grey_srgb (source_color, filter_nearest), "
                       "grey_raw (filter_nearest), use_srgb picks which writes ALBEDO (B12). hint/hint_experiment.tscn "
                       "(Linear tonemap, exposure 1.0) with materials/hint_srgb.tres and hint_raw.tres, both binding "
                       "assets/textures/hint_experiment/hint_greys.png (64/128/192, written by tools/write_hint_greys.gd). "
                       "Result: both quads 64/128/192 on Compatibility (B13).",
        "beat_ids": ["B12", "B13"],
        "files": ["shaders/hint_experiment.gdshader", "hint/hint_experiment.tscn", "materials/hint_srgb.tres",
                  "materials/hint_raw.tres", "assets/textures/hint_experiment/hint_greys.png",
                  "assets/textures/hint_experiment/hint_greys.png.import", "tools/write_hint_greys.gd"]},
    "generated-shader": {
        "explanation": "shaders/standard_generated.gdshader: the editor's conversion of a StandardMaterial3D with albedo, "
                       "normal and roughness textures, saved by Jiean, unused by the game. Lines 7 and 19 beside "
                       "linen_square.gdshader:4 and :11 (B14): source_color in both; hint_roughness_normal vs hint_normal.",
        "beat_ids": ["B14"],
        "files": ["shaders/standard_generated.gdshader"]},
    "tests": {
        "explanation": "tests/test_exposed_tint.gd (agent): uniform list via get_shader_uniform_list(), defaults and "
                       "source_color from the source text, real key presses, every frame checked (B15); "
                       "tests/test_materials.gd (agent audit) with godot/MATERIALS.md; tests/normal_map_check.gd (course "
                       "code) calibrated by tools/calibrate_normal_map_check.gd (B10's curl ratios); test_report.gd "
                       "writes the JSON reports. The earlier suites (test_rules, test_audio_events, check_assets) give "
                       "their baseline counts (B16). Results and the three mutations: B16.",
        "beat_ids": ["B15", "B16", "B10"],
        "files": ["tests/test_exposed_tint.gd", "tests/test_materials.gd", "tests/normal_map_check.gd",
                  "tests/test_report.gd", "tools/calibrate_normal_map_check.gd", "MATERIALS.md",
                  "tests/test_rules.gd", "tests/test_audio_events.gd", "tests/check_assets.gd"]},
    "capture-tool": {
        "explanation": "debug/capture_exposed.tscn and .gd: a debug scene (not the game) that runs main.tscn in a real "
                       "window; key C calls the course's capture() at exposed_amount 0, 0.5, 1, 2 and writes P1/P2 beside "
                       "the predictions. Jiean's captures from it are B07.",
        "beat_ids": ["B07"],
        "files": ["debug/capture_exposed.gd", "debug/capture_exposed.tscn"]},
    "project": {
        "explanation": "project.godot: main scene res://game/main.tscn and the Compatibility renderer (line 25) that "
                       "decides the hint experiment's result (B02, B13).",
        "beat_ids": ["B02", "B13"],
        "files": ["project.godot"]},
}
EARLIER = ("Earlier-assignment file (A2 2D slice or A3 diorama assets), unchanged by Assignment 5 except where listed "
           "above; explained in the A2 and A3 films. The tint shader recolours the A2 archer sprites at run time "
           "without changing these files.")
EXCERPTS = [("B03", "shaders/exposed_tint.gdshader", 1, 8), ("B05", "game/exposed_driver.gd", 29, 37),
            ("B08", "materials/linen_dark.tres", 8, 16), ("B10", "shaders/linen_square.gdshader", 3, 12),
            ("B12", "shaders/hint_experiment.gdshader", 1, 14), ("B15", "tests/test_exposed_tint.gd", 167, 177)]
PAIRS = [("B03", "B04", "Capture run-02 (tint), frames 46-455: two turns out of reach with the value at 0; on turn 3 "
                        "Right plans (3,4), in the enemy's reach, and the archer turns red within 6 frames; Left drains "
                        "it in 6 frames."),
         ("B05", "B06", "Capture run-02 (tint), frames 455-997: taps every 0.1 s turn around from the current value; "
                        "P mid-fade holds it (PAUSED overlay); Enter confirms and it fades during PLAY_MOVES; turn 4 "
                        "starts in reach and it rises at once. Per-frame log: enemy 0.0 in every frame."),
         ("B08", "B09", "Capture run-02 (diorama): the scene's own camera, then the harness camera; linen_dark "
                        "normal_strength 1.5 -> 0 changes only the dark tile; the shared shader's ALBEDO x 0.5 (in memory) "
                        "darkens both."),
         ("B10", "B11", "Capture run-02 (diorama), frames 225-930: light tile uv_scale 0.5 coarse / 8 fine; "
                        "normal_strength 0 flat / 2 deep; roughness_scale 0 from the lamp's mirror angle: about 1.5 % "
                        "darker, no highlight (measured)."),
         ("B12", "B13", "Capture run-02 (hint) frame 60: both quads 64 / 128 / 192, read from the 4K frame, beside "
                        "Jiean's prediction (A 64/128/192, B 137/188/225)."),
         ("B15", "B16", "Recorded reports: 46/46 at 30, 60, 144 fps; 148/148; earlier suites 51/70/38; three "
                        "mutations exit 1 (evidence/a5/mutations); the film's rerun on the a5 copy (capture/film-rerun.json).")]
QUOTES = [("B14", "shaders/standard_generated.gdshader", 7), ("B14", "shaders/standard_generated.gdshader", 19),
          ("B14", "shaders/linen_square.gdshader", 4), ("B14", "shaders/linen_square.gdshader", 11)]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    beats = {b["beat_id"]: b for b in sheet["beats"]}
    owner = {}
    for cid, c in COMPONENTS.items():
        for f in c["files"]:
            if not (GAME / f).is_file():
                raise SystemExit(f"{cid}: missing {f}")
            owner.setdefault(f, []).append(cid)
    inv = sorted(p.relative_to(GAME).as_posix() for p in GAME.rglob("*") if p.is_file()
                 and not any(x in (".godot", ".git") for x in p.relative_to(GAME).parts) and p.suffix != ".uid")
    roles = {".gd": "GDScript source", ".tscn": "saved scene", ".godot": "project configuration",
             ".gdshader": "Godot shader", ".tres": "resource (material)", ".import": "import settings sidecar",
             ".png": "image", ".jpg": "image", ".md": "document"}
    files = [{"path": f, "sha256": sha(GAME / f), "role": roles.get(Path(f).suffix, "file"), "component_ids": owner[f]}
             for f in inv if f in owner]
    exclusions = [{"path": f, "reason": EARLIER} for f in inv if f not in owner]
    excerpts = []
    for bid, path, a, b in EXCERPTS:
        text = "\n".join((GAME / path).read_text(encoding="utf-8").split("\n")[a - 1:b])
        if beats[bid]["shot"]["remotion"]["props"]["code"] != text:
            raise SystemExit(f"{bid}: displayed code differs from {path}:{a}-{b}")
        excerpts.append({"beat_id": bid, "path": path, "start_line": a, "end_line": b, "text": text})
    pairs = []
    for c, r, o in PAIRS:
        m = f"media/{r}.mp4"
        if beats[r]["shot"].get("evidence_media") != m:
            raise SystemExit(f"{r}: evidence_media not set")
        pairs.append({"code_beat": c, "result_beat": r, "observation": o, "media": {"path": m, "sha256": sha(REEL / m)}})
    quotes = [{"beat_id": bid, "path": path, "line": n,
               "text": (GAME / path).read_text(encoding="utf-8").split("\n")[n - 1]} for bid, path, n in QUOTES]
    data = {"schema_version": 1, "teaching_contract": "code-then-result-v1",
            "game": {"name": "walker-lane-tactics-jiean-yin", "project": "godot/project.godot",
                     "source_revision": sheet["metadata"]["game"]["source_revision"],
                     "game_dir": "isolated git-archive copy of a5:godot (core.autocrlf=false)",
                     "note": f"All {len(inv)} authored files (and the .uid files) are byte-identical to the a5 blobs."},
            "files": files, "components": [{"id": k, **v} for k, v in COMPONENTS.items()],
            "excerpts": excerpts, "exclusions": exclusions, "code_result_pairs": pairs, "still_quotes": quotes}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gamedev-evidence.json: {len(files)} files, {len(exclusions)} exclusions, {len(excerpts)} excerpts, "
          f"{len(pairs)} pairs, {len(quotes)} still quotes")


if __name__ == "__main__":
    main()
