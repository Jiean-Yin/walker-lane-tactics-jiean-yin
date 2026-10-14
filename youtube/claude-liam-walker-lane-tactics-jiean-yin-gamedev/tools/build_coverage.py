"""coverage.json (godot-waikthrough capture contract) for the gameplay clips used in this gamedev film.

Scope: the features this film SHOWS. It is not a complete walkthrough; implemented features that are not
filmed are listed under "not_filmed" (outside "features") so the structural check is not mistaken for a
completeness claim. Times are seconds inside each clip, derived from capture/run-03-inputs.jsonl frames.
Usage (reel folder): python tools/build_coverage.py
"""
import hashlib
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
BUILD_ID = hashlib.sha256((REEL / "capture/source-snapshot.txt").read_bytes()).hexdigest()
CLIP_START = {"B03": 0, "B11": 328, "B13": 550, "B09": 812, "B14": 1089}


def t(clip, frame):
    return round((frame - CLIP_START[clip]) / 30, 3)


def ev(clip, beat, f0, fa, f1, obs, riff):
    return {"capture": f"run-03-{clip}", "beat_id": beat, "start_s": t(clip, f0), "action_s": t(clip, fa),
            "end_s": t(clip, f1), "observation": obs, "riff": riff}


def main():
    clips = json.loads((REEL / "capture/clips.json").read_text(encoding="utf-8"))
    captures = {f"run-03-{bid}": {"path": c["path"], "sha256": hashlib.sha256((REEL / c["path"]).read_bytes()).hexdigest(),
                                  "build_id": BUILD_ID, "method": "scripted-input",
                                  "input_log": "capture/run-03-inputs.jsonl",
                                  "source": f"run-03 frames {c['frames'][0]}-{c['frames'][1] - 1} of the 4K master"}
                for bid, c in clips.items()}
    F = [
        ("title-start", [ev("B03", "B03", 0, 90, 150, "Title card with controls; Enter shows the turn-1 board.",
                            "Start is one key; the board is readable before any rule is explained.")]),
        ("idle-and-facing", [ev("B03", "B03", 90, 110, 150, "Teal archer bottom-left faces right, red archer in lane 4 faces left, both idle.",
                                "Facing carries team without colour (pillar 1).")]),
        ("plan-move-marker", [ev("B03", "B03", 150, 180, 207, "Yellow legal squares; Right moves the planned square and draws an arrow.",
                                 "The plan is visible before it is committed.")]),
        ("simultaneous-move-hop", [ev("B03", "B03", 207, 214, 238, "Both pieces hop to their new squares 0.13 s apart.",
                                      "Moves resolve together, then play back; the hop is the idle image lifted in code.")]),
        ("target-and-attack-order", [ev("B11", "B11", 385, 420, 460, "Red target marker on the enemy's square; order numbers 1 (you), 2 (enemy).",
                                        "Who strikes first is shown before the shot.")]),
        ("draw-pose", [ev("B11", "B11", 455, 462, 475, "Player switches to the draw pose; the arrow flies.", "One static image per state.")]),
        ("hurt-pose", [ev("B11", "B11", 470, 477, 500, "Enemy shows the hurt pose (flipped) with -3 and fewer pips; then the player is hurt.",
                          "Hurt leans away from the attacker; HP pips change with the hit.")]),
        ("killed-before-turn", [ev("B13", "B13", 660, 678, 703, "Enemy shoots first on turn 4; the player topples and never fires.",
                                   "Alternating first side decides the duel.")]),
        ("defeat-card", [ev("B13", "B13", 690, 703, 811, "Defeat card: 'Shot by the enemy archer in lane 4', retry keys.",
                            "The cause stays on screen (pillar 4).")]),
        ("retry", [ev("B09", "B09", 812, 813, 860, "R: fresh board at turn 1, retries 1, both archers idle.", "Retry is instant.")]),
        ("f3-footprints", [ev("B09", "B09", 845, 860, 944, "Red 64x96 slots and blue 40x12 base discs drawn on both pieces.",
                              "The art is anchored on the base disc; rules use squares, not pixels.")]),
        ("slice-audio-sfx-and-music", [ev("B14", "B16", 1100, 1130, 1594,
                                          "Heard in B14 (no narration): SFX-HOP, HOP, HOP, HURT, HIT, HIT, WIN with the music loop; "
                                          "music stops at the win. B16 is the narrated beat that shows this interval measured.",
                                          "Each sound is one rules event, in event order.")]),
        ("win-pose-and-card", [ev("B14", "B16", 1490, 1497, 1594, "Enemy toppled, player in the win pose, 'ENEMY DEFEATED' card.",
                                  "Elimination win on turn 5, no tie rule.")]),
    ]
    data = {"schema_version": 1,
            "scope": "Features shown in this gamedev film (not a complete walkthrough).",
            "game": {"name": "walker-lane-tactics-jiean-yin", "build_id": BUILD_ID,
                     "build_id_method": "SHA-256 of capture/source-snapshot.txt = git ls-tree -r film-source-v1 godot | sort -k4"},
            "captures": captures,
            "features": [{"id": i, "status": "implemented", "evidence": e} for i, e in F]
                        + [{"id": "second-enemy", "status": "planned", "evidence": [],
                            "reason": "Storyboard drew two enemies; the slice uses one (CHANGE-BRIEF R1). TWO_ENEMY_UNITS kept for later."},
                           {"id": "riders-shielders", "status": "planned", "evidence": [],
                            "reason": "RULES.md unit types beyond the archer; not in the asset slice."}],
            "not_filmed": [
                {"id": "pause-duck", "status": "implemented", "where_verified": "test_audio_events.gd (P/Esc, -12 dB), in run-03 not used"},
                {"id": "mute-music-sfx", "status": "implemented", "where_verified": "test_audio_events.gd (M/N buses); Jiean's playtest"},
                {"id": "results-card-play-again", "status": "implemented", "where_verified": "captured in run-03 frames 1594-1671, not used in the film"},
                {"id": "back-row-win", "status": "implemented", "where_verified": "test_rules.gd; not reached on the capture routes"}]}
    (REEL / "coverage.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("coverage.json:", len(F), "shown features,", len(captures), "captures")


if __name__ == "__main__":
    main()
