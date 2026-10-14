"""Cut the gameplay beats from capture run-03 (exact frame ranges, no retiming) and burn our label.

Picture: the lossless 4K master run-4k.mkv (FFV1). Sound (B14 only): the Movie Maker AVI audio of the SAME
run, cut at the same frame boundaries (48000 / 30 = 1600 samples per frame); stored losslessly (ALAC).
Narrated beats carry no game audio (the compiler drops clip audio; narration is the beat's audio).

Usage (reel folder): python tools/make_clips.py <capture_dir>   e.g. <capture-copy>/run-03
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
CAP = Path(sys.argv[1])
MASTER = CAP / "run-4k.mkv"
AVI = CAP / "run-03.avi"
FONT = "<brutalist>/runtime/fonts/Inter/static/Inter_28pt-Medium.ttf"
FPS = 30
SPF = 48000 // FPS  # audio samples per video frame in the Movie Maker AVI


def label_png(text: str, out: Path) -> tuple[int, int]:
    """Two-line label, white on translucent ink, sized for the empty HUD gap (x 1700-2760, y 110-262 at 4K)."""
    l1, l2 = text.split("|")
    f1 = ImageFont.truetype(FONT, 50)
    f2 = ImageFont.truetype(FONT, 46)
    d = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    w = max(d.textbbox((0, 0), l1, font=f1)[2], d.textbbox((0, 0), l2, font=f2)[2]) + 48
    h = 150
    img = Image.new("RGBA", (w, h), (20, 14, 10, 190))
    dr = ImageDraw.Draw(img)
    dr.text((24, 14), l1, font=f1, fill=(255, 255, 255, 255))
    dr.text((24, 80), l2, font=f2, fill=(242, 193, 78, 255))
    img.save(out)
    return w, h


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("ffmpeg failed:\n" + " ".join(map(str, cmd)) + "\n" + r.stderr[-2000:])


def main():
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    (REEL / "media").mkdir(exist_ok=True)
    (REEL / "_labels").mkdir(exist_ok=True)
    work = REEL / "_work"
    work.mkdir(exist_ok=True)
    records = {}
    for b in sheet["beats"]:
        shot = b.get("shot", {})
        if shot.get("capture") != "run-03" or "frames" not in shot:
            continue
        bid = b["beat_id"]
        a, e = shot["frames"]
        n = e - a
        lbl = work / f"label-{bid}.png"
        lw, lh = label_png(shot["label"], lbl)
        (REEL / "_labels" / f"{bid}.txt").write_text(shot["label"].replace("|", " / "), encoding="utf-8")
        x, y = 1700, 112
        out = REEL / "media" / f"{bid}.mp4"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{a / FPS:.6f}", "-i", str(MASTER), "-i", str(lbl)]
        report = b.get("kind") == "source_report"
        if report:
            cmd += ["-i", str(AVI)]
        cmd += ["-filter_complex", f"[0:v][1:v]overlay={x}:{y}:format=auto,format=yuv420p[v]", "-map", "[v]",
                "-frames:v", str(n), "-r", str(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", "10"]
        if report:
            cmd += ["-map", "2:a", "-af", f"atrim=start_sample={a * SPF}:end_sample={e * SPF},asetpts=PTS-STARTPTS",
                    "-c:a", "alac"]
        else:
            cmd += ["-an"]
        cmd += [str(out)]
        run(cmd)
        records[bid] = {"capture": "run-03", "frames": [a, e], "n_frames": n, "duration_s": f"{n}/{FPS}",
                        "audio": ("AVI samples %d-%d (ALAC, lossless)" % (a * SPF, e * SPF)) if report else "none",
                        "label": shot["label"].replace("|", " / "), "label_box_4k": [x, y, x + lw, y + lh],
                        "path": f"media/{bid}.mp4", "sha256": sha(out)}
        print(bid, records[bid]["path"], n, "frames", records[bid]["sha256"][:12])
    (REEL / "capture" / "clips.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
