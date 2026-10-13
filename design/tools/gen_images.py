"""Local image generation for Lane Tactics with Stable Diffusion XL base 1.0.

Every image is logged (model, revision, prompt, negative prompt, seed, steps,
guidance, size, init image + strength, output SHA-256) to assets/gen-log.jsonl,
so any accepted or rejected output can be reproduced with one command.

Prompts are kept short on purpose: SDXL's text encoders read 77 tokens.

Examples (repo root; PY = the Python of a private venv with torch + diffusers):
  PY=<venv>/Scripts/python.exe
  $PY design/tools/gen_images.py CHAR-REF --seeds 101 102 103 104
  $PY design/tools/gen_images.py CHAR-IDLE --init design/character/init/idle.png --strength 0.7 --seeds 101
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "assets" / "_raw" / "art"
LOG = ROOT / "assets" / "gen-log.jsonl"
MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

# v1 prompts (run ref01) produced photo-real 3D toys on grey; v2 leads with the
# 2D sprite style and the white background so the 77-token limit cannot cut them.
# v3 (run ref05, accepted CHAR-REF s202): no "flat vector illustration"; ends with wood grain.
PIECE = ("ball-shaped birch wood head, one black dot eye, dark navy hood, teal painted cylinder body without legs, "
         "walnut belt, quiver, wooden bow, round walnut disc base, thick dark outline, painted wood grain texture")
HEAD = "2D game sprite on a plain white background, carved wooden toy archer game piece, side view facing right"


def char(pose: str) -> str:
    return f"{HEAD}, {pose}, {PIECE}"


PROMPTS = {
    "CHAR-REF": char("standing upright"),
    "CHAR-IDLE": char("at rest, bow held low"),
    "CHAR-DRAW": char("drawing the bow"),
    "CHAR-HURT": char("tilted backward, struck"),
    "CHAR-DEFEAT": char("toppled, lying on its side"),
    "CHAR-WIN": char("arms raised, bow overhead"),
    "ENV-TABLE": ("top-down view of a dark walnut wooden tabletop, warm desk lamp light from the upper left, "
                  "soft pool of light in the centre, gentle dark vignette, subtle wood grain, empty, no objects"),
    "ENV-LINEN": "seamless woven natural beige linen fabric texture, flat even lighting, top-down, fine weave, no folds",
}
NEGATIVE = {
    "char": ("photo, 3d render, realistic, grey background, gradient background, legs, feet, mouth, nose, teeth, multiple figures, text, watermark, "
             "checkerboard, floor, cast shadow, gradient background, blurry, extra arms"),
    "env": "text, watermark, objects, people, board game, cards, cup, blurry, frame",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("asset_id", choices=sorted(PROMPTS))
    ap.add_argument("--seeds", type=int, nargs="+", default=[101, 102, 103, 104])
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--cfg", type=float, default=7.0)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--init", type=str, default=None, help="init image for image-to-image")
    ap.add_argument("--strength", type=float, default=0.7)
    ap.add_argument("--prompt", type=str, default=None, help="override the stored prompt (logged)")
    ap.add_argument("--run", type=str, default=None, help="label for this run (default: timestamp)")
    a = ap.parse_args()

    import torch
    import diffusers
    from diffusers import StableDiffusionXLImg2ImgPipeline, StableDiffusionXLPipeline
    from PIL import Image

    kind = "env" if a.asset_id.startswith("ENV") else "char"
    prompt = a.prompt or PROMPTS[a.asset_id]
    negative = NEGATIVE[kind]
    run = a.run or time.strftime("%Y%m%d-%H%M%S")
    out_dir = RAW / a.asset_id
    out_dir.mkdir(parents=True, exist_ok=True)

    common = dict(torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
    if a.init:
        pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(MODEL, **common)
        init = Image.open(ROOT / a.init if not Path(a.init).is_absolute() else a.init).convert("RGB")
        init = init.resize((a.width, a.height))
    else:
        pipe = StableDiffusionXLPipeline.from_pretrained(MODEL, **common)
        init = None
    pipe.enable_model_cpu_offload()   # fits the 8 GB laptop GPU
    revision = getattr(pipe.config, "_commit_hash", None) or "unknown"

    for seed in a.seeds:
        g = torch.Generator("cpu").manual_seed(seed)
        t0 = time.time()
        if init is not None:
            img = pipe(prompt=prompt, negative_prompt=negative, image=init, strength=a.strength,
                       num_inference_steps=a.steps, guidance_scale=a.cfg, generator=g).images[0]
            name = f"{a.asset_id}-{run}-s{seed}-str{a.strength:.2f}.png"
        else:
            img = pipe(prompt=prompt, negative_prompt=negative, width=a.width, height=a.height,
                       num_inference_steps=a.steps, guidance_scale=a.cfg, generator=g).images[0]
            name = f"{a.asset_id}-{run}-s{seed}.png"
        path = out_dir / name
        img.save(path)
        rec = {
            "asset_id": a.asset_id, "run": run, "file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(path), "model": MODEL, "model_revision": revision,
            "diffusers": diffusers.__version__, "torch": torch.__version__,
            "mode": "img2img" if init is not None else "txt2img",
            "prompt": prompt, "negative_prompt": negative, "seed": seed, "generator": "torch cpu",
            "steps": a.steps, "guidance": a.cfg, "width": a.width, "height": a.height,
            "init_image": a.init, "strength": a.strength if init is not None else None,
            "seconds": round(time.time() - t0, 1), "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        print("wrote", rec["file"], f"({rec['seconds']} s)")

    # contact sheet of this run (thumbnails for the asset log / rejected record)
    files = sorted(out_dir.glob(f"{a.asset_id}-{run}-*.png"))
    if files:
        th = 256
        sheet = Image.new("RGB", (th * len(files), th + 24), "white")
        from PIL import ImageDraw
        dr = ImageDraw.Draw(sheet)
        for i, fp in enumerate(files):
            im = Image.open(fp).convert("RGB")
            im.thumbnail((th, th))
            sheet.paste(im, (i * th, 0))
            dr.text((i * th + 4, th + 6), fp.stem.split("-s")[-1], fill="black")
        sheet.save(out_dir / f"contact-{run}.png")
        print("contact sheet", (out_dir / f"contact-{run}.png").relative_to(ROOT))


if __name__ == "__main__":
    main()
