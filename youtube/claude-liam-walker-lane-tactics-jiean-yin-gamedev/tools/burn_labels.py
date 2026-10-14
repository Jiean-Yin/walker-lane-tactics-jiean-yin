"""Burn the disclosure labels onto reconstructed-interface and code-view Remotion beats.

The unlabelled Remotion render is kept in _work/prelabel/; re-running is idempotent (a media file whose hash
matches the recorded labelled output is not labelled twice). GodotDevWorkbench beats need no label: the
component itself prints "Godot editor reconstruction · source-backed teaching view".
Usage (reel folder): python tools/burn_labels.py
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
FONT = "<brutalist>/runtime/fonts/Inter/static/Inter_28pt-Medium.ttf"
LABELS = {
    "B00": ("Illustrative reconstruction of the Claude interface — not a transcript", "bottom-centre"),
    "BHTF": ("Reconstructed interface · suggested prompt, not a past run", "bottom-centre"),
    "B08": ("Actual source excerpt (process_sprites.py @ film-source-v1) · reconstructed code view", "bottom-right"),
    "B17": ("Recorded console output · verbatim lines, omissions marked …", "bottom-right"),
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    rec_path = REEL / "_labels" / "burned.json"
    rec = json.loads(rec_path.read_text(encoding="utf-8")) if rec_path.exists() else {}
    pre = REEL / "_work" / "prelabel"
    pre.mkdir(parents=True, exist_ok=True)
    for bid, (text, where) in LABELS.items():
        media = REEL / "media" / f"{bid}.mp4"
        if bid in rec and sha(media) == rec[bid]["labelled_sha256"]:
            print(bid, "already labelled")
            continue
        shutil.copy2(media, pre / f"{bid}.mp4")
        f = ImageFont.truetype(FONT, 50)
        tw = ImageDraw.Draw(Image.new("RGBA", (8, 8))).textbbox((0, 0), text, font=f)
        w, h = tw[2] - tw[0] + 56, 90
        img = Image.new("RGBA", (w, h), (48, 61, 52, 235))
        ImageDraw.Draw(img).text((28, 45), text, font=f, fill=(255, 253, 248, 255), anchor="lm")
        png = REEL / "_work" / f"label-{bid}.png"
        img.save(png)
        x = (3840 - w) // 2 if where == "bottom-centre" else 3480 - w
        y = 1860 if where == "bottom-centre" else 1820
        tmp = REEL / "_work" / f"{bid}-labelled.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pre / f"{bid}.mp4"), "-i", str(png), "-filter_complex",
                        f"[0:v][1:v]overlay={x}:{y}:format=auto,format=yuv420p[v]", "-map", "[v]", "-c:v", "libx264",
                        "-preset", "medium", "-crf", "12", "-an", str(tmp)], check=True)
        shutil.move(tmp, media)
        (REEL / "_labels" / f"{bid}.txt").write_text(text, encoding="utf-8")
        rec[bid] = {"text": text, "box_4k": [x, y, x + w, y + h], "unlabelled_sha256": sha(pre / f"{bid}.mp4"),
                    "labelled_sha256": sha(media)}
        print(bid, "labelled", rec[bid]["box_4k"])
    rec_path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
