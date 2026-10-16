"""Same-run join check: 4K FFV1 master frame i (downscaled to 1280x720) vs Movie Maker AVI frame i, and i +/- 1.

Usage (Brutalist venv python): python tools/join_check.py <run_dir>  -> prints JSON, writes capture/run-02-join.json
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

REEL = Path(__file__).resolve().parents[1]
RUN = Path(sys.argv[1])
W, H = 1280, 720


def frames(path, scale):
    vf = f"scale={W}:{H}:flags=area" if scale else "null"
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "gray",
                        "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W).astype(np.int16)


def main():
    a = frames(RUN / "orbit-4k.mkv", True)
    b = frames(RUN / "orbit.avi", False)
    n = len(a)
    same = [float(np.abs(a[i] - b[i]).mean()) for i in range(n)]
    off = [float(np.abs(a[i] - b[i + 1]).mean()) for i in range(0, n - 1, 25)]
    out = {"master_frames": n, "avi_frames": len(b), "same_index_mad_mean": round(float(np.mean(same)), 3),
           "same_index_mad_max": round(float(np.max(same)), 3),
           "plus_one_offset_mad_mean_sampled": round(float(np.mean(off)), 3),
           "plus_one_offset_mad_max_sampled": round(float(np.max(off)), 3)}
    (REEL / "capture" / "run-02-join.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
