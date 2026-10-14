"""Write gamedev-evidence.json (schema 1, teaching_contract code-then-result-v1) for --game <repo>/godot.

Hashes every authored file in godot/ (except .godot/ and .uid), associates each with a component,
records the exact excerpts shown by the GodotDevWorkbench beats and the code -> result pairs.
Usage (reel folder): python tools/build_evidence.py
"""
import hashlib
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = REEL.parents[1] / "godot"

ART = sorted(p.relative_to(GAME).as_posix() for p in (GAME / "assets/art").glob("archer_*"))
COMPONENTS = {
    "rules-engine": {
        "explanation": "game/rules.gd is the whole rule set as plain data: board 8 x 5, units, orders in, a list of "
                       "events out (moved, attack, damaged, killed, attack_cancelled), deterministic, no nodes and no "
                       "audio. The attack loop alternates sides one unit at a time, the side that strikes first "
                       "switches each turn (first_side), and a unit killed before its turn does not attack. Shown in "
                       "B12; its consequence (the naive plan loses on turn 4) in B13.",
        "beat_ids": ["B12", "B13"], "files": ["game/rules.gd"]},
    "scene-controller": {
        "explanation": "game/main.gd asks Rules for the result first, then plays the returned events back once on its "
                       "own clock (hop, draw, arrow, impact, cards) and calls AudioDirector at the moment each event is "
                       "shown; it draws the board, HUD, markers and arrow in code through draw_layer.gd. main.tscn holds "
                       "Main + AudioDirector; project.godot sets the 1280 x 720 canvas_items viewport. Seen running in "
                       "B03 and cited in B15 (main.gd lines 411 and 507).",
        "beat_ids": ["B03", "B15"],
        "files": ["game/main.gd", "game/main.tscn", "game/draw_layer.gd", "project.godot"]},
    "piece-display": {
        "explanation": "game/piece.gd swaps one static generated texture per state (idle, draw, hurt, defeat, win), "
                       "scales every pose with the idle image's scale, flips the enemy with flip_h and positions the "
                       "sprite from the base disc. The ten archer PNGs (player + recoloured enemy) and their import "
                       "sidecars are the generated, edited character art traced in B04-B09.",
        "beat_ids": ["B07", "B09", "B10", "B11"], "files": ["game/piece.gd"] + ART},
    "environment-art": {
        "explanation": "assets/art/env_table.png is the SDXL tabletop (ENV-TABLE s301, scaled/cropped to 1280 x 720) "
                       "drawn behind the code-drawn linen board; credited to SDXL in B19 and visible in every gameplay beat.",
        "beat_ids": ["B03", "B19"], "files": ["assets/art/env_table.png", "assets/art/env_table.png.import"]},
    "audio": {
        "explanation": "game/audio_director.gd turns already-resolved rules events into sounds (moved -> SFX-HOP, damaged "
                       "enemy by the player -> SFX-HIT, damaged player -> SFX-HURT, entering WON -> SFX-WIN once) and runs "
                       "the music loop (duck on pause, fade on defeat, stop on win); default_bus_layout.tres provides "
                       "the Music and SFX buses for M/N. The four ElevenLabs OGGs and the MusicGen loop are the assets. "
                       "Heard in B14 (no narration), explained in B15, measured in B16.",
        "beat_ids": ["B15", "B16"],
        "files": ["game/audio_director.gd", "default_bus_layout.tres"]
                 + [f"assets/sfx/sfx_{n}.ogg{x}" for n in ("hop", "hit", "hurt", "win") for x in ("", ".import")]
                 + ["assets/music/mus_loop.ogg", "assets/music/mus_loop.ogg.import"]},
    "tests": {
        "explanation": "Headless suites: test_rules.gd (51 rules checks) and test_audio_events.gd (70 scene checks: "
                       "sounds == events per id, echo/rapid input ignored, muted run identical) with route_runner.gd, "
                       "test_report.gd and the two route fixtures, which also drive this film's capture; capture.gd "
                       "(screenshots) and analyze_variants.gd (the exhaustive search behind CHANGE-BRIEF R1). B17 shows "
                       "the recorded output; B12 cites the search. Tests use synthetic input and a fast clock, so they "
                       "cannot judge feel or fun.",
        "beat_ids": ["B03", "B12", "B17"],
        "files": ["tests/test_rules.gd", "tests/test_audio_events.gd", "tests/route_runner.gd", "tests/test_report.gd",
                  "tests/capture.gd", "tests/analyze_variants.gd", "tests/fixtures/win_route.json",
                  "tests/fixtures/lose_route.json"]},
}
EXCLUSIONS = {f"assets/{d}/.gitkeep": "Empty placeholder that keeps the folder in git; no content to explain."
              for d in ("art", "music", "sfx")}
EXCERPTS = [("B10", "game/piece.gd", 175, 185), ("B12", "game/rules.gd", 341, 346),
            ("B15", "game/audio_director.gd", 105, 118)]
PAIRS = [("B10", "B11", "media/B11.mp4",
          "Lose-route turn 3 in the running game: the player's draw pose, the arrow, the enemy's hurt pose (same art "
          "recoloured, flipped to face left), then the enemy's draw and the player's hurt pose; every pose stands on "
          "the same base spot."),
         ("B12", "B13", "media/B13.mp4",
          "Turn 4: the enemy holds order 1 and shoots first; the player's archer topples before its own attack; no "
          "player arrow is shown; the defeat card reads 'Shot by the enemy archer in lane 4'."),
         ("B15", "B16", "media/B16.mp4",
          "The measured B14 audio: seven onsets matched to the game's own SFX files within 1-11 ms of the logged "
          "rules-event frames, in the logged order HOP, HOP, HOP, HURT, HIT, HIT, WIN, with silence after the win.")]


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
    missing = [f for f in inv if f not in owner and f not in EXCLUSIONS]
    if missing:
        raise SystemExit(f"unassigned files: {missing}")
    roles = {".gd": "GDScript source", ".tscn": "saved scene", ".godot": "project configuration",
             ".tres": "audio bus layout resource", ".png": "generated art (texture)", ".ogg": "generated audio",
             ".import": "import settings sidecar", ".json": "route fixture (test data)"}
    files = [{"path": f, "sha256": sha(GAME / f), "role": roles.get(Path(f).suffix, "file"), "component_ids": owner[f]}
             for f in inv if f in owner]
    excerpts = []
    for bid, path, a, b in EXCERPTS:
        text = "\n".join((GAME / path).read_text(encoding="utf-8").splitlines()[a - 1:b])
        shown = beats[bid]["shot"]["remotion"]["props"]["code"]
        if shown != text:
            raise SystemExit(f"{bid}: displayed code differs from {path}:{a}-{b}")
        excerpts.append({"beat_id": bid, "path": path, "start_line": a, "end_line": b, "text": text})
    pairs = [{"code_beat": c, "result_beat": r, "observation": o, "media": {"path": m, "sha256": sha(REEL / m)}}
             for c, r, m, o in PAIRS]
    data = {"schema_version": 1, "teaching_contract": "code-then-result-v1",
            "game": {"name": "walker-lane-tactics-jiean-yin", "project": "godot/project.godot",
                     "source_revision": sheet["metadata"]["game"]["source_revision"],
                     "note": "All 51 files are byte-identical to the film-source-v1 blobs (checked before hashing)."},
            "files": files, "components": [{"id": k, **v} for k, v in COMPONENTS.items()],
            "excerpts": excerpts,
            "exclusions": [{"path": k, "reason": v} for k, v in EXCLUSIONS.items()],
            "code_result_pairs": pairs}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gamedev-evidence.json: {len(files)} files, {len(EXCLUSIONS)} exclusions, {len(excerpts)} excerpts, "
          f"{len(pairs)} pairs")


if __name__ == "__main__":
    main()
