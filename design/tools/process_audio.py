"""Turn raw ElevenLabs downloads into game-ready OGG files, logging every edit.

  sfx  : trim leading silence (threshold -45 dBFS), keep up to --max seconds,
         5 ms fade-in, short fade-out, peak-normalise to -1 dBFS, mono OGG.
  loop : cut [start, start + bars * beats_per_bar * 60 / bpm) from the track,
         crossfade the audio just after the cut into its start (--xfade ms) so the
         seam has no click, then report the seam jump (sample delta at the wrap).

Edits are appended to assets/edit-log.jsonl (input SHA-256, output SHA-256,
every parameter), so each game file can be traced to its raw download.

Examples (repo root):
  PY=<venv>/Scripts/python.exe
  $PY design/tools/process_audio.py sfx assets/_raw/sfx/SFX-HOP-02.mp3 godot/assets/sfx/sfx_hop.ogg --max 0.4
  $PY design/tools/process_audio.py loop assets/_raw/music/MUS-01.mp3 godot/assets/music/mus_loop.ogg --bpm 80 --bars 16 --start 8.0
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "assets" / "edit-log.jsonl"
SR = 44100


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def decode(path: Path, channels: int) -> np.ndarray:
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "x.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ac", str(channels),
                        "-ar", str(SR), str(wav)], check=True)
        data, _ = sf.read(wav, dtype="float32", always_2d=True)
    return data


def encode(data: np.ndarray, out: Path, quality: int = 6) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "y.wav"
        sf.write(wav, data, SR, subtype="PCM_16")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "libvorbis",
                        "-q:a", str(quality), str(out)], check=True)


def log(rec: dict) -> None:
    rec["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec, indent=1))


def do_sfx(a) -> None:
    x = decode(Path(a.src), 1)
    mono = x[:, 0]
    thr = 10 ** (a.threshold_db / 20)
    above = np.nonzero(np.abs(mono) > thr)[0]
    start = max(0, int(above[0]) - int(0.002 * SR)) if above.size else 0
    end = min(len(mono), start + int(a.max * SR)) if a.max else len(mono)
    y = mono[start:end].copy()
    fi, fo = int(0.005 * SR), int(a.fade_out * SR)
    y[:fi] *= np.linspace(0, 1, fi)
    if fo and fo < len(y):
        y[-fo:] *= np.linspace(1, 0, fo)
    peak = float(np.max(np.abs(y))) or 1.0
    y *= 10 ** (-1 / 20) / peak
    out = Path(a.dst)
    encode(y[:, None], out)
    log({"op": "sfx", "src": a.src, "src_sha256": sha(Path(a.src)), "dst": a.dst, "dst_sha256": sha(out),
         "trimmed_lead_s": round(start / SR, 4), "length_s": round(len(y) / SR, 4),
         "threshold_db": a.threshold_db, "max_s": a.max, "fade_in_ms": 5, "fade_out_s": a.fade_out,
         "normalise_peak_dbfs": -1})


def do_loop(a) -> None:
    x = decode(Path(a.src), 2)
    beat = 60.0 / a.bpm
    length = int(round(a.bars * a.beats_per_bar * beat * SR))
    s = int(round(a.start * SR))
    xf = int(a.xfade / 1000 * SR)
    if s + length + xf > len(x):
        raise SystemExit(f"track too short: need {(s + length + xf) / SR:.2f} s, have {len(x) / SR:.2f} s")
    body = x[s:s + length].copy()
    tail = x[s + length:s + length + xf]
    ramp = np.linspace(0, 1, xf)[:, None]
    body[:xf] = body[:xf] * ramp + tail * (1 - ramp)   # the wrap continues the audio that followed the cut
    jump = float(np.max(np.abs(body[0] - body[-1])))
    step = float(np.percentile(np.abs(np.diff(body, axis=0)), 99.9))
    out = Path(a.dst)
    encode(body, out)
    log({"op": "loop", "src": a.src, "src_sha256": sha(Path(a.src)), "dst": a.dst, "dst_sha256": sha(out),
         "bpm": a.bpm, "bars": a.bars, "beats_per_bar": a.beats_per_bar, "start_s": a.start,
         "length_s": round(length / SR, 4), "crossfade_ms": a.xfade,
         "seam_jump": round(jump, 5), "typical_step_p99_9": round(step, 5),
         "seam_ok": jump <= max(step, 0.02)})


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("sfx")
    p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--threshold-db", type=float, default=-45)
    p.add_argument("--max", type=float, default=None, help="max length in seconds after the onset")
    p.add_argument("--fade-out", type=float, default=0.03)
    q = sub.add_parser("loop")
    q.add_argument("src"); q.add_argument("dst")
    q.add_argument("--bpm", type=float, required=True)
    q.add_argument("--bars", type=int, default=16)
    q.add_argument("--beats-per-bar", type=int, default=4)
    q.add_argument("--start", type=float, default=0.0, help="cut start in seconds (on a downbeat)")
    q.add_argument("--xfade", type=float, default=30.0, help="seam crossfade in ms")
    a = ap.parse_args()
    do_sfx(a) if a.cmd == "sfx" else do_loop(a)


if __name__ == "__main__":
    main()
