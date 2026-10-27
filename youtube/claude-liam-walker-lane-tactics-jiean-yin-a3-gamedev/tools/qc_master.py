"""Inspect the actual master: probe, per-beat frame sheet, per-beat loudness/peak, silent gaps, last frame.

Usage (Brutalist venv python, reel folder): python tools/qc_master.py <film.mp4>
Writes _qc/frame-sheet-*.png, _qc/last-frame.png and _qc/master-qc.json.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
FILM = Path(sys.argv[1])
QC = REEL / "_qc"


def run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)


def frame(t, w=960):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(FILM), "-frames:v", "1", "-vf",
                        f"scale={w}:-1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True)
    from io import BytesIO
    return Image.open(BytesIO(r.stdout)).convert("RGB")


def main():
    QC.mkdir(exist_ok=True)
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels,nb_frames",
                            "-of", "json", FILM]).stdout)
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    t, rows = 0.0, []
    for b in sheet["beats"]:
        d = b["actual_duration_s"]
        a = run(["ffmpeg", "-v", "info", "-ss", f"{t:.3f}", "-t", f"{d:.3f}", "-i", FILM, "-vn", "-af",
                 "volumedetect", "-f", "null", "-"]).stderr
        mean = re.search(r"mean_volume: (-?[\d.]+)", a)
        peak = re.search(r"max_volume: (-?[\d.]+)", a)
        rows.append({"beat": b["beat_id"], "start_s": round(t, 3), "dur_s": round(d, 3),
                     "mean_db": float(mean.group(1)) if mean else None, "peak_db": float(peak.group(1)) if peak else None})
        t += d
    lufs = run(["ffmpeg", "-v", "info", "-i", FILM, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    integ = re.findall(r"I:\s+(-?[\d.]+) LUFS", lufs)
    tpk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", lufs)
    sil = run(["ffmpeg", "-v", "info", "-i", FILM, "-vn", "-af", "silencedetect=noise=-50dB:d=2.5", "-f", "null", "-"]).stderr
    silences = [(float(a), float(b)) for a, b in zip(re.findall(r"silence_start: ([\d.]+)", sil),
                                                    re.findall(r"silence_end: ([\d.]+)", sil))]
    # frame sheets: 3 frames per beat (10 %, 50 %, 90 %)
    f = ImageFont.truetype(os.path.join(os.environ["WINDIR"], "Fonts", "arial.ttf"), 22)
    tiles = []
    for r in rows:
        for q in (0.1, 0.5, 0.9):
            im = frame(r["start_s"] + r["dur_s"] * q, 640)
            # QC caption goes in a strip BELOW the frame, so it never covers the picture (an earlier version drew it
            # over the top-left corner, which made B02/B07 titles look clipped on the sheet).
            tile = Image.new("RGB", (im.width, im.height + 32), "black")
            tile.paste(im, (0, 0))
            ImageDraw.Draw(tile).text((6, im.height + 4), f"{r['beat']} @ {r['start_s'] + r['dur_s'] * q:.1f}s", font=f,
                                      fill=(255, 255, 0))
            tiles.append(tile)
    per = 27
    for k in range(0, len(tiles), per):
        part = tiles[k:k + per]
        h = part[0].height
        canvas = Image.new("RGB", (640 * 3, h * ((len(part) + 2) // 3)), "black")
        for i, im in enumerate(part):
            canvas.paste(im, (640 * (i % 3), h * (i // 3)))
        canvas.save(QC / f"frame-sheet-{k // per + 1}.png")
    dur = float(probe["format"]["duration"])
    frame(dur - 0.05, 1920).save(QC / "last-frame.png")
    out = {"film": FILM.name, "probe": probe, "beats": rows, "integrated_lufs": integ[-1] if integ else None,
           "true_peak_dbfs": tpk[-1] if tpk else None, "silences_over_2_5s_below_-50dB": silences,
           "sum_of_beats_s": round(t, 3)}
    (QC / "master-qc.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "probe"}, indent=1))


if __name__ == "__main__":
    main()
