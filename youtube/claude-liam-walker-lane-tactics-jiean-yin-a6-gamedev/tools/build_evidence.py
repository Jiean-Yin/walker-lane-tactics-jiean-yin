"""Write gamedev-evidence.json (schema 1, teaching_contract code-then-result-v1) for the A6 film.

--game is the isolated git-archive copy of tag a6's godot/ folder (each file checked against its a6 blob). Every
authored file is hashed and either associated with a component this film explains (the Assignment 6 additions and
the state they read) or excluded with a reason. Code beats' displayed code must equal the file's lines; the excerpt
list is read from the beat sheet's own "excerpt" fields. Frame numbers below are master frames of the final capture
(<capture-copy>/final-out; play 30 fps, slow 120 fps), from capture/play-log.jsonl and slow-log.jsonl.
Usage (reel folder): python tools/build_evidence.py <capture-copy>/a6/godot
"""
import hashlib
import json
import sys
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = Path(sys.argv[1])

COMPONENTS = {
    "hit-burst-scene": {
        "explanation": "effects/hit_burst.tscn: root HitBurst (Node2D, z 2) with three CPUParticles2D, Flash (1), "
                       "Splinters (14), Dust (8); every look value saved in the scene, emitting saved false, local_coords "
                       "off, Mix blend, GradientTexture2D textures inside the scene (B03). Flash tuned r1-r3: lifetime "
                       "1.08 s, scale_amount 3.0 (B09, CHANGE-BRIEF Revision 1 item 1). Results: B04, B10.",
        "beat_ids": ["B03", "B04", "B09", "B10"],
        "files": ["effects/hit_burst.tscn", "effects/ATTRIBUTION.md"]},
    "hit-burst-driver": {
        "explanation": "game/hit_burst_driver.gd, a node in game/main.tscn with process_priority 10: each frame it reads "
                       "main.played_events (main.gd:502), spawns a new HitBurst per \"damaged\" event at the archer's "
                       "position + (0, -40), frees it on Dust.finished, and sets every emitter's speed_scale to "
                       "main.time_scale, 0 while main.paused (B05, B07). It never writes game state. Results: B06 (pause), "
                       "B08 (two bursts alive at once).",
        "beat_ids": ["B05", "B06", "B07", "B08"],
        "files": ["game/hit_burst_driver.gd", "game/main.tscn", "game/main.gd", "game/piece.gd"]},
    "arrow-trail-scene": {
        "explanation": "effects/arrow_trail.tscn: root ArrowTrail with two GPUParticles2D, Streak (48) and Wisps (12), "
                       "each with its own ParticleProcessMaterial; trail_enabled false (draws nothing on Compatibility, "
                       "measured), local_coords false, fixed_fps 30, visibility_rect set (B11); Wisps turbulence on, "
                       "influence 0.1-0.2, colour ramp tuned in Effect B r1 (B15, Revision 1 item 4). Results: B12, B16.",
        "beat_ids": ["B11", "B12", "B15", "B16"],
        "files": ["effects/arrow_trail.tscn"]},
    "arrow-trail-driver": {
        "explanation": "game/arrow_trail_driver.gd (main.tscn, process_priority 10): one trail per entry of main._arrows, "
                       "moved to the tip with main.gd's arc formula (tip_of, lines 43-47); stops both emitters on the "
                       "frame the arrow leaves the list and frees the node after the longest lifetime of game time "
                       "(B13). Result: B14.",
        "beat_ids": ["B13", "B14"],
        "files": ["game/arrow_trail_driver.gd"]},
    "previews-and-price-fixture": {
        "explanation": "previews/hit_burst_preview and arrow_trail_preview (.tscn/.gd): fixture scenes with a fixed seed "
                       "that Jiean captured with Movie Maker for the strips (B10, B16, B26); tools/strip_sheet.gd lays "
                       "them out. previews/price_effects (.tscn/.gd) holds each case at its peak and prints the viewport's "
                       "measured GPU time (B23); game/vsync_debug.gd is the V key for vsync. Result: B24.",
        "beat_ids": ["B10", "B16", "B23", "B24", "B26"],
        "files": ["previews/hit_burst_preview.gd", "previews/hit_burst_preview.tscn", "previews/arrow_trail_preview.gd",
                  "previews/arrow_trail_preview.tscn", "previews/price_effects.gd", "previews/price_effects.tscn",
                  "tools/strip_sheet.gd", "game/vsync_debug.gd"]},
    "tests": {
        "explanation": "tests/test_hit_burst_config.gd (107 checks) and test_arrow_trail_config.gd (135) read every "
                       "scene value back and scan the scene text for Godot 3 names (B17); test_hit_burst_state.gd and "
                       "test_arrow_trail_state.gd (31 each) play tests/fixtures/win_route.json with real key presses at "
                       "60 fps and check every frame (B19); cost_effects.gd times frames headless (B21); test_report.gd "
                       "writes the JSON reports. Results: B18 (mutations), B20 (the B2 bound), B22 (headless price).",
        "beat_ids": ["B17", "B18", "B19", "B20", "B21", "B22"],
        "files": ["tests/test_hit_burst_config.gd", "tests/test_arrow_trail_config.gd", "tests/test_hit_burst_state.gd",
                  "tests/test_arrow_trail_state.gd", "tests/cost_effects.gd", "tests/test_report.gd",
                  "tests/fixtures/win_route.json"]},
    "generated-shader": {
        "explanation": "shaders/particles_generated.gdshader: the editor's conversion of the Wisps ParticleProcessMaterial, "
                       "saved by Jiean, unused by the game. Jiean's A6.7 rows: shader_type 3, start() 323, process() 378, "
                       "232, 412, 255, 254, 441; B25 shows lines 252-257. Result: B26.",
        "beat_ids": ["B25", "B26"],
        "files": ["shaders/particles_generated.gdshader"]},
    "project": {
        "explanation": "project.godot: main scene res://game/main.tscn and the Compatibility renderer (line 25), on which "
                       "trail_enabled draws nothing (B02, B11).",
        "beat_ids": ["B02", "B11"],
        "files": ["project.godot"]},
}
EARLIER = ("Earlier-assignment file (A2 2D slice, A3 diorama, A5 shaders and materials), unchanged by Assignment 6 "
           "except where listed above; explained in the earlier films.")
PAIRS = [
    ("B03", "B04", "Final capture, play 110-271 then slow 250-572 (1/4 speed, 3x crop): turn 4, the enemy's arrow "
                   "appears at play 249 and lands on the player's archer at play 259 / slow 290; the burst appears on that "
                   "frame at (320, 594) on the 1280x720 canvas, the hit point, and the trail stops on the same frame. The "
                   "first burst is freed 146 slow frames (1.22 s of game time) after the hit."),
    ("B05", "B06", "Final capture, play 527-979 (run 2, turn 4): hit at 636; P at 645, 0.3 s after the hit; the game "
                   "stays paused 195 frames (6.5 s) and the burst stays alive and still ('run 2: burst alive while "
                   "paused' OK in play-summary.json); unpause at 840; the second hit at 862; no burst left at 900."),
    ("B07", "B08", "Final capture, play 200-330 and slow 250-699 (2x crop): two hits 31 play frames apart (259 and 290; "
                   "1.03 s) / slow 290 and 417; two bursts alive from the second hit until the first is freed (play "
                   "290-297, slow 417-436); max bursts alive in the run: 2. On screen: the state test's A3 overlap line "
                   "(evidence/a6/final/test_hit_burst_state_60fps.log:30)."),
    ("B09", "B10", "Jiean's Movie Maker strips captures/hit_burst/r0-r3 (hit_burst_preview, fixed seed), frames 10, 12, 15, "
                   "20, 30: the flash lasts and grows with each revision; Jiean's request and verdict verbatim (TUNING.md)."),
    ("B11", "B12", "Final capture, play 245-315, slow 230-520 and 845-1006 (2x crop): every trail is a row of dots "
                   "behind the tip, about 20-25 px apart on the 1280x720 canvas, the same at 120 fps (the GPU node steps "
                   "at fixed_fps 30); Jiean's first look verbatim (TUNING.md:125)."),
    ("B13", "B14", "Final capture, slow 397-592 (2x crop): the player's arrow; the trail stops emitting at slow 416, one "
                   "frame (1/120 s) before the hit at 417; then play 1063-1358 (run 3): P at 1083 freezes the arrow and "
                   "its trail for 150 frames (5 s; 'run 3: trail alive while paused' OK); unpause at 1233; hit at 1238."),
    ("B15", "B16", "captures/arrow_trail/r0 and r1, frames 16, 21, 26, 31 (arrow_trail_preview, seed 71): pixels darker "
                   "in r1: 403, 1004, 1264, 1087 (TUNING.md); Jiean's verdict verbatim."),
    ("B17", "B18", "evidence/a6/mutations: mutation 1 (Splinters initial_velocity for initial_velocity_min) and mutation "
                   "2 (Splinters spread 75 -> 60) both exit 1 with the named checks failing (TEST-REPORT A6.3); "
                   "Jiean's words on mutation 1 in the running game."),
    ("B19", "B20", "evidence/a6/step5b: 30/31, the B2 check failing with offsets [0, -2, 0, 0, -2]; CHANGE-BRIEF "
                   "Revision 1 item 3 revises the bound to -2..0; evidence/a6/final: 31/31."),
    ("B21", "B22", "TEST-REPORT A6.6 headless table: control 0.1220 ms; Effect A x2 +0.0078 ms (t 8.1); Effect B x2 "
                   "+0.0066 ms (t 8.0); Jiean's predictions 0.015 and 0 ms; budget 0.2 ms."),
    ("B23", "B24", "TEST-REPORT A6.6: Jiean's Visual Profiler ranges overlap in all three cases; the sweep's means with "
                   "vsync off 0.1058 / 0.1089 (+0.0031) / 0.1132 (+0.0074) ms; FPS with vsync on 180 in every case; "
                   "Jiean's conclusion verbatim."),
    ("B25", "B26", "captures/arrow_trail/r1 frames 21, 26, 31, enlarged: the wisps drift upward, swell and fade "
                   "(gravity (0, -20, 0), scale_curve 0.6 -> 1.4, colour ramp alpha 0.7 -> 0); Jiean's shader / "
                   "draw-step split verbatim (TEST-REPORT A6.7)."),
]
QUOTES = [("B02", "project.godot", 25)]


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
             ".gdshader": "Godot shader", ".tres": "resource", ".import": "import settings sidecar",
             ".png": "image", ".jpg": "image", ".md": "document", ".json": "test fixture"}
    files = [{"path": f, "sha256": sha(GAME / f), "role": roles.get(Path(f).suffix, "file"), "component_ids": owner[f]}
             for f in inv if f in owner]
    exclusions = [{"path": f, "reason": EARLIER} for f in inv if f not in owner]
    excerpts = []
    for b in sheet["beats"]:
        ex = b.get("excerpt")
        if not ex:
            continue
        a, z = ex["start_line"], ex["end_line"]
        text = "\n".join((GAME / ex["path"]).read_text(encoding="utf-8").split("\n")[a - 1:z])
        if b["shot"]["remotion"]["props"]["code"] != text:
            raise SystemExit(f"{b['beat_id']}: displayed code differs from {ex['path']}:{a}-{z}")
        excerpts.append({"beat_id": b["beat_id"], "path": ex["path"], "start_line": a, "end_line": z, "text": text})
    pairs = []
    for c, r, o in PAIRS:
        m = f"media/{r}.mp4"
        if beats[r]["shot"].get("evidence_media") != m:
            raise SystemExit(f"{r}: evidence_media not set")
        if not any(e["beat_id"] == c for e in excerpts):
            raise SystemExit(f"{c}: no excerpt")
        pairs.append({"code_beat": c, "result_beat": r, "observation": o, "media": {"path": m, "sha256": sha(REEL / m)}})
    quotes = [{"beat_id": bid, "path": path, "line": n,
               "text": (GAME / path).read_text(encoding="utf-8").split("\n")[n - 1]} for bid, path, n in QUOTES]
    data = {"schema_version": 1, "teaching_contract": "code-then-result-v1",
            "game": {"name": "walker-lane-tactics-jiean-yin", "project": "godot/project.godot",
                     "source_revision": sheet["metadata"]["game"]["source_revision"],
                     "game_dir": "isolated git-archive copy of a6:godot (core.autocrlf=false)",
                     "note": f"All {len(inv)} authored files (and the .uid files) are byte-identical to the a6 blobs."},
            "files": files, "components": [{"id": k, **v} for k, v in COMPONENTS.items()],
            "excerpts": excerpts, "exclusions": exclusions, "code_result_pairs": pairs, "still_quotes": quotes}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gamedev-evidence.json: {len(files)} files, {len(exclusions)} exclusions, {len(excerpts)} excerpts, "
          f"{len(pairs)} pairs, {len(quotes)} still quotes")


if __name__ == "__main__":
    main()
