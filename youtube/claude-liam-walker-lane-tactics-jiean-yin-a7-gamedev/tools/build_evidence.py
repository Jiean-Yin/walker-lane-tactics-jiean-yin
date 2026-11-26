"""Write gamedev-evidence.json (schema 1, teaching_contract code-then-result-v1) for the A7 film.

--game is the isolated git-archive copy of tag a7's godot/ folder (each file checked against its a7 blob). Every
authored file is hashed and either associated with a component this film explains (the Assignment 7 additions and
the state they read) or excluded with a reason. Code beats' displayed code must equal the file's lines; the excerpt
list is read from the beat sheet's own "excerpt" fields. Frame numbers below are master frames of the final capture
(<capture-copy>/final-out; play 30 fps, slow 120 fps), from capture/play-log.jsonl and slow-log.jsonl.
Adapted from the A6 film's tools/build_evidence.py.
Usage (reel folder): python tools/build_evidence.py <capture-copy>/a7/godot
"""
import hashlib
import json
import sys
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = Path(sys.argv[1])

COMPONENTS = {
    "flag-clip": {
        "explanation": "animations/wave.tres: a frame track keying FlagSprite:frame 0-3 at 0/0.125/0.25/0.375 s, step "
                       "0.125, length 0.5, LOOP_LINEAR, no key at length (the seam rule), plus a discrete offset track "
                       "0/-4/-2/+1 for the sheet's pole drift (B03, B05). game/goal_flag.tscn: Sprite2D hframes 4 x "
                       "vframes 1 on assets/art/flag/flag_red.png (Fokko, CC0, as downloaded), AnimationPlayer autoplay "
                       "wave, callback mode IDLE; instanced in game/main.tscn at (1176, 458), z 1. Results: B04, B06.",
        "beat_ids": ["B02", "B03", "B04", "B05", "B06"],
        "files": ["animations/wave.tres", "game/goal_flag.tscn", "assets/art/flag/flag_red.png",
                  "assets/art/flag/flag_red.png.import", "assets/art/flag/ATTRIBUTION.md", "game/main.tscn"]},
    "rig-clip": {
        "explanation": "animations/shoot.tres: three value tracks (Rig:position, Rig/Upper:rotation, "
                       "Rig/Upper/Bow:rotation) keyed at frames 0/12/33/40/48 of a 60 fps phase table (step 1/60, "
                       "length 0.8, LOOP_NONE), the bow's frame-48 key tuned 20 -> 8 degrees (B10, B18). "
                       "game/archer_rig.tscn: Mount > Rig > Lower, Upper > UpperSprite, Bow > BowSprite, regions of the "
                       "A2 draw art, AnimationPlayer MANUAL with root_node Mount. Results: B11, B19.",
        "beat_ids": ["B09", "B10", "B11", "B18", "B19"],
        "files": ["animations/shoot.tres", "game/archer_rig.tscn", "assets/art/archer_draw.png",
                  "assets/art/archer_draw_enemy.png", "assets/art/archer_draw.png.import",
                  "assets/art/archer_draw_enemy.png.import"]},
    "one-authority-and-clocks": {
        "explanation": "game/piece.gd: POSE_CLIPS (draw -> shoot); _apply_clip() stops, plays and advance(0)s the rig's "
                       "player on set_state (lines 109-116, B12); tick(dt) advances it by game time inside main._process "
                       "after the cues (lines 181-182, B14); Mount is the only node piece.gd writes on the rig. "
                       "game/main.gd owns the state machine and the cue list that sets the poses. Results: B13 "
                       "(interrupts), B15 (clocks).",
        "beat_ids": ["B12", "B13", "B14", "B15"],
        "files": ["game/piece.gd", "game/main.gd"]},
    "tests-and-preview": {
        "explanation": "tests/test_flag_readback.gd (43 checks: frame range, discrete updates, step, loop mode, seam; "
                       "B07) and test_shoot_readback.gd (51: track_problems branched on track type, key times, step, "
                       "loop mode; B16); test_anim_states.gd (51) and test_shoot_edges.gd (102: P, R, Enter one frame "
                       "before/on/after frames 0, 12, 33, 48; B20); test_pins_a7.gd (29, before and after the clips); "
                       "test_report.gd, route_runner.gd and fixtures/win_route.json. previews/shoot_preview (.tscn/.gd) "
                       "is the fixture for Jiean's strips (B19). Results: B08, B17, B21.",
        "beat_ids": ["B07", "B08", "B16", "B17", "B19", "B20", "B21"],
        "files": ["tests/test_flag_readback.gd", "tests/test_shoot_readback.gd", "tests/test_anim_states.gd",
                  "tests/test_shoot_edges.gd", "tests/test_pins_a7.gd", "tests/test_report.gd",
                  "tests/route_runner.gd", "tests/fixtures/win_route.json", "previews/shoot_preview.gd",
                  "previews/shoot_preview.tscn"]},
    "project": {
        "explanation": "project.godot: main scene res://game/main.tscn and the Compatibility renderer (line 25), "
                       "1280 x 720 (B02).",
        "beat_ids": ["B02"],
        "files": ["project.godot"]},
}
EARLIER = ("Earlier-assignment file (A2 2D slice, A3 diorama, A5 shaders and materials, A6 particle effects), "
           "unchanged by Assignment 7 except where listed above; explained in the earlier films.")
PAIRS = [
    ("B03", "B04", "Final capture, play 0-452 (title, turns 1-3, turn 4 orders), cropped 3x on the GoalFlag: the flag's "
                   "cell changes every 0.125 s (flag_cell in play-log.jsonl cycles 0, 1, 2, 3), from the title card on; "
                   "inset: flag_red.png as downloaded with its 4 x 1 grid. Jiean's A7.9 words verbatim."),
    ("B05", "B06", "captures/flag_registration_r1.png (tag a7): the GoalFlag cropped from the 13 kept frames of Jiean's "
                   "r1 strip; the pole's darkest column is at screen x 1176 in all 13 (TEST-REPORT A7.11). Jiean's "
                   "words verbatim."),
    ("B07", "B08", "evidence/a7/step6/mutations: mutation 3 (a frame key of 4) fails 'every frame key is inside the "
                   "sheet' (exit 1; 37/43 after the guard); mutation 2 (LOOP_NONE) fails 'loop_mode = LOOP_LINEAR' "
                   "(41/43, exit 1). Each in a git worktree."),
    ("B10", "B11", "Final capture, play 300-380 (e1 draws at 333, its arrow leaves at 339, hit on p1 at 349, back to "
                   "idle at 357), slow 200-480 at 1/4 speed (2x crop: e1 draw 225, hit 290, idle 321; p1 draw 351, hit "
                   "417, idle 447), play 452-617 (turn 5: p1 draw 515, idle 539). Jiean's A7.10 words verbatim."),
    ("B12", "B13", "Final capture, play 700-1040 (run 2 turn 4): e1 draws at 710; P at 712-802 in its startup, 811-901 "
                   "in its active phase (arrow in flight), 939-1029 in p1's recovery (clip past 0.6 s); each pose and "
                   "clip held while paused ('run 2: paused in ...' OK x3 in play-summary.json); then play 1166-1270 "
                   "(run 3): e1 draws at 1177, R at 1186: turn 1, no shot left ('run 3' OK)."),
    ("B14", "B15", "Final capture, play 617-1084 and 1084-1180, full frame: while paused the archers hold and the "
                   "GoalFlag keeps changing cell (flag_cell changes while paused in play-log.jsonl). On screen: "
                   "evidence/a7/step5/test_anim_states_60fps.log, clip position - arrow t = 0.20000 for each shot."),
    ("B16", "B17", "evidence/a7/step6/mutations: mutation 1 (Rig/Upper:rotation -> rotaton, clip only) fails "
                   "track_problems with 'track 1: Node2D has no property rotaton' (exit 1); mutation 4 (empty import "
                   "cache) leaves the rig read-back at 51/51, as predicted."),
    ("B18", "B19", "captures/shoot/r0 and r1 (shoot_preview, Jiean's Movie Maker captures), frames 15, 29, 31, 33 around "
                   "the bow hand: 0 pixels changed up to frame 29, 410-458 in 31-33 (TUNING.md r1); Jiean's r0, r1 and "
                   "verdict words verbatim."),
    ("B20", "B21", "evidence/a7/step6/test_shoot_edges_60fps.log: 102/102; evidence/a7/pins and step6: the pins 29/29 "
                   "before and after the clips; measured impact 32/34 and idle 47/49 game frames (CHANGE-BRIEF "
                   "revision 1)."),
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
                     "game_dir": "isolated git-archive copy of a7:godot (core.autocrlf=false)",
                     "note": f"All {len(inv)} authored files (and the .uid files) are byte-identical to the a7 blobs."},
            "files": files, "components": [{"id": k, **v} for k, v in COMPONENTS.items()],
            "excerpts": excerpts, "exclusions": exclusions, "code_result_pairs": pairs, "still_quotes": quotes}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gamedev-evidence.json: {len(files)} files, {len(exclusions)} exclusions, {len(excerpts)} excerpts, "
          f"{len(pairs)} pairs, {len(quotes)} still quotes")


if __name__ == "__main__":
    main()
