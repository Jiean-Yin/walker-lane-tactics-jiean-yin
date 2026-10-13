"""Local music generation for Lane Tactics with Meta's MusicGen (transformers).

Each take is logged (model, prompt, seed, sampling settings, length, SHA-256)
to assets/gen-log.jsonl. Output: assets/_raw/music/<ID>-<run>-s<seed>.wav
(raw WAV is ignored by git; the game uses the OGG loop cut by process_audio.py).

Also prints a tempo estimate (onset-envelope autocorrelation) so the loop can
be cut on a bar boundary.

Example (repo root):  <venv>/Scripts/python.exe design/tools/gen_music.py --seeds 1 2 3 --seconds 30
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "assets" / "_raw" / "music"
LOG = ROOT / "assets" / "gen-log.jsonl"
MODEL = "facebook/musicgen-small"
PROMPT = ("calm instrumental loop for a thoughtful tabletop strategy game, plucked nylon guitar and kalimba, "
          "soft wooden percussion, warm low drone, steady slow pulse, 80 bpm, 4/4, same energy throughout, no vocals")


def tempo(x: np.ndarray, sr: int) -> float:
    hop = 512
    frames = np.lib.stride_tricks.sliding_window_view(x, 1024)[::hop]
    env = np.sqrt((frames ** 2).mean(axis=1))
    onset = np.maximum(0, np.diff(env))
    onset -= onset.mean()
    ac = np.correlate(onset, onset, mode="full")[len(onset) - 1:]
    fps = sr / hop
    lo, hi = int(fps * 60 / 160), int(fps * 60 / 55)          # search 55-160 bpm
    lag = lo + int(np.argmax(ac[lo:hi]))
    return 60 * fps / lag


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--seconds", type=float, default=30.0)
    ap.add_argument("--guidance", type=float, default=3.0)
    ap.add_argument("--prompt", type=str, default=PROMPT)
    ap.add_argument("--run", type=str, default=None)
    ap.add_argument("--asset-id", type=str, default="MUS-LOOP")
    a = ap.parse_args()

    import torch
    import transformers
    from transformers import AutoProcessor, MusicgenForConditionalGeneration

    run = a.run or time.strftime("%Y%m%d-%H%M%S")
    RAW.mkdir(parents=True, exist_ok=True)
    proc = AutoProcessor.from_pretrained(MODEL)
    model = MusicgenForConditionalGeneration.from_pretrained(MODEL).to("cuda")
    sr = model.config.audio_encoder.sampling_rate
    frame_rate = model.config.audio_encoder.frame_rate          # tokens per second
    tokens = int(a.seconds * frame_rate)
    inputs = proc(text=[a.prompt], padding=True, return_tensors="pt").to("cuda")
    for seed in a.seeds:
        torch.manual_seed(seed)
        t0 = time.time()
        audio = model.generate(**inputs, do_sample=True, guidance_scale=a.guidance, max_new_tokens=tokens)
        x = audio[0, 0].float().cpu().numpy()
        path = RAW / f"{a.asset_id}-{run}-s{seed}.wav"
        sf.write(path, x, sr)
        bpm = tempo(x, sr)
        rec = {"asset_id": a.asset_id, "run": run, "file": str(path.relative_to(ROOT)).replace("\\", "/"),
               "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "model": MODEL,
               "transformers": transformers.__version__, "torch": torch.__version__, "mode": "text-to-music",
               "prompt": a.prompt, "seed": seed, "seed_api": "torch.manual_seed", "do_sample": True,
               "guidance": a.guidance, "max_new_tokens": tokens, "seconds": round(len(x) / sr, 2),
               "sample_rate": sr, "tempo_estimate_bpm": round(bpm, 1),
               "gen_seconds": round(time.time() - t0, 1), "time": time.strftime("%Y-%m-%d %H:%M:%S")}
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        print("wrote", rec["file"], f"{rec['seconds']} s, ~{rec['tempo_estimate_bpm']} bpm ({rec['gen_seconds']} s)")


if __name__ == "__main__":
    main()
