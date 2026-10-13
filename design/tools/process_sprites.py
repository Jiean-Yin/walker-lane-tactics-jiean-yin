"""Turn accepted SDXL pose outputs into game sprites (player + enemy recolour).

For each state:
  1. background removal with rembg (u2net), then halo cleanup: pixels that are
     near-white (all channels > --white) or faint (alpha < 40) become transparent
     (the CHAR-REF check showed a white halo under the base);
  2. crop to the piece; rescale so every pose shares the idle pose's pixel scale
     (the defeat init sketch was drawn at 6.5/8.5 of the others' size);
  3. pad so the base-disc centre is the image's horizontal centre and the base
     sits on the bottom edge (piece.gd anchors images this way);
  4. enemy copy: only teal paint pixels (hue 165-200 deg, saturation > 0.25)
     are rotated to the enemy red hue; wood, walnut and navy hood are untouched.

Every output is logged to assets/edit-log.jsonl with input/output SHA-256.

Example (repo root):
  <venv>/Scripts/python.exe design/tools/process_sprites.py idle=assets/_raw/art/CHAR-IDLE/....png draw=...
"""
from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "godot" / "assets" / "art"
LOG = ROOT / "assets" / "edit-log.jsonl"
INIT_SCALE = {"defeat": 6.5}          # sketch scale used in make_init_images.py (others 8.5)
IDLE_PX = 320                         # exported idle height in pixels (4x the 80 px game height)
ENEMY_HUE = 4 / 360                   # #B23A2E


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def cutout(src: Path, session, white: int) -> Image.Image:
    from rembg import remove
    im = remove(Image.open(src).convert("RGB"), session=session)
    a = np.array(im)
    rgb, al = a[..., :3].astype(int), a[..., 3]
    halo = (rgb.min(axis=2) > white) | (al < 40)
    a[..., 3] = np.where(halo, 0, al)
    return Image.fromarray(a)


def base_centre_x(im: Image.Image) -> float:
    al = np.array(im)[..., 3]
    rows = np.nonzero(al.max(axis=1) > 0)[0]
    band = al[max(rows[0], rows[-1] - max(3, (rows[-1] - rows[0]) // 25)):rows[-1] + 1]
    cols = np.nonzero(band.max(axis=0) > 0)[0]
    return (cols[0] + cols[-1]) / 2


def recolour(im: Image.Image) -> tuple[Image.Image, int]:
    a = np.array(im).astype(np.float32) / 255
    out = a.copy()
    n = 0
    h, w = a.shape[:2]
    flat = a.reshape(-1, 4)
    res = out.reshape(-1, 4)
    for i in np.nonzero(flat[:, 3] > 0)[0]:
        r, g, b = flat[i, :3]
        hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
        if 165 / 360 <= hh <= 200 / 360 and ss > 0.25:
            res[i, :3] = colorsys.hsv_to_rgb(ENEMY_HUE, min(1.0, ss * 1.1), min(1.0, vv * 1.15))
            n += 1
    return Image.fromarray((out * 255).round().astype(np.uint8)), n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs", nargs="+", help="state=path (state in idle, draw, hurt, defeat, win)")
    ap.add_argument("--white", type=int, default=232)
    a = ap.parse_args()
    from rembg import new_session
    session = new_session("u2net")
    srcs = dict(p.split("=", 1) for p in a.pairs)
    cuts = {s: cutout(ROOT / f, session, a.white) for s, f in srcs.items()}
    idle = cuts["idle"].crop(cuts["idle"].getbbox())
    k = IDLE_PX / idle.height                         # one scale for all poses
    OUT.mkdir(parents=True, exist_ok=True)
    for state, im in cuts.items():
        im = im.crop(im.getbbox())
        f = k * 8.5 / INIT_SCALE.get(state, 8.5)
        im = im.resize((max(1, round(im.width * f)), max(1, round(im.height * f))), Image.LANCZOS)
        cx = base_centre_x(im) if state != "defeat" else im.width / 2
        half = int(np.ceil(max(cx, im.width - cx))) + 2
        canvas = Image.new("RGBA", (2 * half, im.height + 2), (0, 0, 0, 0))
        canvas.paste(im, (int(round(half - cx)), 0), im)
        enemy, n = recolour(canvas)
        for img, name in ((canvas, f"archer_{state}.png"), (enemy, f"archer_{state}_enemy.png")):
            dst = OUT / name
            img.save(dst)
            rec = {"op": "sprite", "state": state, "src": srcs[state], "src_sha256": sha(ROOT / srcs[state]),
                   "dst": str(dst.relative_to(ROOT)).replace("\\", "/"), "dst_sha256": sha(dst),
                   "steps": ["rembg u2net", f"halo: rgb>{a.white} or alpha<40 -> transparent",
                             f"scale {f:.4f} (idle -> {IDLE_PX} px)", "pad: base centre at x centre, base on bottom edge"]
                   + ([f"enemy recolour: {n} teal px (hue 165-200, sat>0.25) -> hue 4 deg"] if "enemy" in name else []),
                   "size": list(img.size), "time": time.strftime("%Y-%m-%d %H:%M:%S")}
            with LOG.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
            print("wrote", rec["dst"], rec["size"])


if __name__ == "__main__":
    main()
