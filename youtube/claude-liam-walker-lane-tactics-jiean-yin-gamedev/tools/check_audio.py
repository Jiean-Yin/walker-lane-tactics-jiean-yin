"""Verify that the slice-audio segment really carries the game's own sound, in the logged order.

For every SFX trigger logged by the capture driver inside the segment, the actual game file
(godot/assets/sfx/*.ogg) is matched against the recording around the logged frame (normalised
cross-correlation, mono 48 kHz). A control match at a random time in the same segment shows how
specific the match is. Also reports loudness (EBU R128 via ffmpeg) of the segment.

Usage (reel folder):
  python tools/check_audio.py media/B14.mp4                    # the clip itself, offset 0
  python tools/check_audio.py <film.mp4> --offset <seconds>    # the segment inside a rendered cut
Writes _qc/audio-check-<name>.json
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

import numpy as np

REEL = Path(__file__).resolve().parents[1]
REPO = REEL.parents[1]
SR, FPS, A, E = 48000, 30, 1089, 1594
FILES = {"SFX-HOP": "sfx_hop.ogg", "SFX-HIT": "sfx_hit.ogg", "SFX-HURT": "sfx_hurt.ogg", "SFX-WIN": "sfx_win.ogg"}


def decode(path, start=None, dur=None):
    cmd = ["ffmpeg", "-v", "error"]
    if start is not None:
        cmd += ["-ss", f"{start:.6f}"]
    cmd += ["-i", str(path)]
    if dur is not None:
        cmd += ["-t", f"{dur:.6f}"]
    cmd += ["-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)


def ncc(x, tpl, lo, hi):
    best, lag = -1.0, None
    tn = (tpl - tpl.mean()) / (np.linalg.norm(tpl - tpl.mean()) + 1e-12)
    for i in range(max(0, lo), min(len(x) - len(tpl), hi), 6):  # 0.5 ms steps
        seg = x[i:i + len(tpl)]
        s = seg - seg.mean()
        v = float(np.dot(s, tn) / (np.linalg.norm(s) + 1e-12))
        if v > best:
            best, lag = v, i
    return best, lag


def loudness(path, start, dur):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(path),
                        "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"Integrated loudness:\s+I:\s+(-?[\d.]+) LUFS", r.stderr)
    p = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    return (float(m.group(1)) if m else None), (float(p.group(1)) if p else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("--offset", type=float, default=0.0)
    a = ap.parse_args()
    media = Path(a.media)
    dur = (E - A) / FPS
    x = decode(media, a.offset, dur)
    ev = [json.loads(l) for l in (REEL / "capture/run-03-inputs.jsonl").read_text(encoding="utf-8").splitlines()]
    trig = [(e["frame"], e["detail"]["id"]) for e in ev if e["event"] == "sfx_trigger" and A <= e["frame"] < E]
    rng = np.random.default_rng(7)
    rows = []
    for f, sid in trig:
        tpl = decode(REPO / "godot/assets/sfx" / FILES[sid])[: int(0.25 * SR)]
        t = (f - A) / FPS
        v, lag = ncc(x, tpl, int((t - 0.03) * SR), int((t + 0.08) * SR))
        ct = float(rng.uniform(0.5, dur - 0.5))
        while min(abs(ct - (g - A) / FPS) for g, _ in trig) < 0.6:
            ct = float(rng.uniform(0.5, dur - 0.5))
        cv, _ = ncc(x, tpl, int((ct - 0.03) * SR), int((ct + 0.08) * SR))
        rows.append({"sfx": sid, "logged_frame": f, "expected_s": round(t, 3),
                     "matched_s": round(lag / SR, 4) if lag is not None else None,
                     "lag_ms": round((lag / SR - t) * 1000, 1) if lag is not None else None,
                     "ncc": round(v, 3), "control_time_s": round(ct, 2), "control_ncc": round(cv, 3)})
    lufs, peak = loudness(media, a.offset, dur)
    rms = float(np.sqrt(np.mean(x ** 2)))
    tail = x[int(((1497 - A) / FPS + 0.7) * SR):]
    out = {"media": str(media), "offset_s": a.offset, "segment_frames": [A, E], "duration_s": round(dur, 4),
           "integrated_lufs": lufs, "true_peak_dbfs": peak, "rms_dbfs": round(20 * np.log10(max(rms, 1e-9)), 1),
           "after_win_rms_dbfs": round(20 * np.log10(max(float(np.sqrt(np.mean(tail ** 2))), 1e-9)), 1) if len(tail) else None,
           "order_logged": [s for _, s in trig],
           "order_matched": [r["sfx"] for r in sorted(rows, key=lambda r: r["matched_s"] or 0)],
           "all_matched": all(r["ncc"] >= 0.4 and r["ncc"] > r["control_ncc"] + 0.2 for r in rows),
           "events": rows}
    (REEL / "_qc").mkdir(exist_ok=True)
    dst = REEL / "_qc" / f"audio-check-{media.stem}.json"
    dst.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    for r in rows:
        print(f"{r['sfx']:9} expected {r['expected_s']:6.3f}s  matched {r['matched_s']}s  lag {r['lag_ms']} ms  "
              f"ncc {r['ncc']}  (control {r['control_ncc']})")
    print("LUFS", lufs, "peak", peak, "after-win RMS", out["after_win_rms_dbfs"], "all_matched", out["all_matched"],
          "order ok", out["order_logged"] == out["order_matched"])


if __name__ == "__main__":
    main()
