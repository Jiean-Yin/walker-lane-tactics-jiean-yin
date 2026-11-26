"""Print the event anchors of a capture run from its per-frame logs (read-only): for each recorded shot, the master
frames where an arrow appears, a trail stops emitting, a hit is played, a key is pressed, and the live burst count.
Used to choose the footage segments (tools/set_segments.py). Usage: CAPTURE=<capture-copy> RUN=<run> python tools/anchors.py
"""
import json
import os
from pathlib import Path

RUN = Path(os.environ["CAPTURE"]) / os.environ.get("RUN", "final-out")


def rows(mode):
    with open(RUN / f"{mode}-log.jsonl", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def anchors(mode):
    summ = json.loads((RUN / f"{mode}-summary.json").read_text(encoding="utf-8"))
    out = {"fps": summ["fps"], "shots": {}}
    rs = rows(mode)
    for sh in summ["shots"]:
        a, b = sh["master_frames"]
        ev = {"arrow": [], "trail_stop": [], "hit": [], "key": [], "bursts": []}
        prev_trails, prev_emit, prev_b = None, {}, None
        for r in rs:
            m = r.get("mframe", -1)
            if not r.get("rec") or not (a <= m < b):
                continue
            if r["event"] == "key":
                ev["key"].append([m, r["detail"]])
            if r["event"] != "frame":
                continue
            d = r["detail"]
            if prev_trails is not None and d["trails_spawned"] > prev_trails:
                ev["arrow"].append(m)
            prev_trails = d["trails_spawned"]
            for t in d["trails"]:
                on = any(t["emitting"])
                if prev_emit.get(t["id"]) and not on:
                    ev["trail_stop"].append(m)
                prev_emit[t["id"]] = on
            for u in d["hits"]:
                ev["hit"].append([m, u])
            nb = len(d["bursts"])
            if nb != prev_b:
                ev["bursts"].append([m, nb])
                prev_b = nb
        out["shots"][sh["shot"]] = {"range": [a, b], **ev}
    return out


if __name__ == "__main__":
    for mode in ("play", "slow"):
        print(mode, json.dumps(anchors(mode), indent=1))
