"""Build the A8 pitch film from beat_sheet.json (lean local pipeline, no network).

Usage (Brutalist venv Python, ffmpeg on PATH):
    python pitch/tools/build_film.py --a6-master <a6-film.mp4> --fonts <brutalist>/runtime/fonts

Reads pitch/beat_sheet.json and the Kokoro narration in pitch/mp3/beat-<ID>.mp3.
Writes pitch/_work/ (slides, segments) and pitch/exports/<slug>.mp4 (3840x2160, 24 fps,
h264 yuv420p, AAC). Slides are drawn here with Pillow; footage is cut from the A6 film master
(which carries its own burned-in capture labels) and gets an extra label from this sheet.
"""
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 3840, 2160, 24
PAD_S = 0.7  # silence after each beat's narration
INK, GROUND, ACCENT, MUTED = (27, 20, 16), (250, 249, 245), (204, 120, 92), (110, 100, 90)
CARD = (238, 232, 220)

ROOT = Path(__file__).resolve().parents[1]

# Footage ranges in the A6 film master (seconds), chosen from its SHOTLIST.md beats B04/B06/B12.
SEGMENTS = {
    "B02": [(104.37, 15.0), (70.17, 5.3)],      # A6 B06 (turn 4, play) + A6 B04 first part (turn 3 moves, play)
    "B05": [(75.6, 10.5), (214.97, 12.0)],      # A6 B04 slow hit burst + A6 B12 trail at 1/4 speed
}


def font(fonts: Path, name: str, size: int):
    paths = {
        "serif": fonts / "EB_Garamond" / "static" / "EBGaramond-Medium.ttf",
        "sans": fonts / "Inter" / "static" / "Inter_28pt-Regular.ttf",
        "sansb": fonts / "Inter" / "static" / "Inter_28pt-Medium.ttf",
        "mono": fonts / "PT_Mono" / "PTMono-Regular.ttf",
    }
    p = paths[name]
    if not p.exists():
        cands = sorted((fonts).rglob("*.ttf"))
        want = {"serif": "Garamond", "sans": "Inter", "sansb": "Inter", "mono": "Mono"}[name]
        p = next(c for c in cands if want in c.name)
    return ImageFont.truetype(str(p), size)


def label_pill(img: Image.Image, text: str, F):
    d = ImageDraw.Draw(img)
    f = F("sansb", 46)
    tw = d.textlength(text, font=f)
    x1, y1 = W - 120, H - 90
    x0, y0 = x1 - tw - 80, y1 - 100
    d.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=(27, 20, 16, 225))
    d.text((x0 + 40, y0 + 22), text, font=f, fill=(250, 249, 245))


def draw_slide(v: dict, F) -> Image.Image:
    img = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(img)
    x = 260
    d.text((x, 230), v.get("kicker", ""), font=F("sansb", 64), fill=ACCENT)
    d.text((x, 340), v["title"], font=F("serif", 190), fill=INK)
    y = 640
    if "table" in v:
        for a, b in v["table"]:
            last = a == "Lane Tactics"
            d.rounded_rectangle((x, y, W - 260, y + 230), radius=30, fill=(INK if last else CARD))
            d.text((x + 70, y + 60), a, font=F("sansb", 92), fill=(GROUND if last else INK))
            d.text((x + 1450, y + 70), b, font=F("sans", 84), fill=(GROUND if last else MUTED))
            y += 280
    if "steps" in v:
        n = len(v["steps"])
        bw = (W - 2 * x - (n - 1) * 90) // n
        for i, s in enumerate(v["steps"]):
            bx = x + i * (bw + 90)
            d.rounded_rectangle((bx, y + 120, bx + bw, y + 720), radius=36, outline=INK, width=8, fill=CARD)
            d.text((bx + 60, y + 170), f"{i + 1}", font=F("serif", 220), fill=ACCENT)
            words, line, ly = s.split(), "", y + 480
            for w_ in words:
                t = (line + " " + w_).strip()
                if d.textlength(t, font=F("sansb", 84)) > bw - 120:
                    d.text((bx + 60, ly), line, font=F("sansb", 84), fill=INK)
                    line, ly = w_, ly + 100
                else:
                    line = t
            d.text((bx + 60, ly), line, font=F("sansb", 84), fill=INK)
            if i < n - 1:
                ax = bx + bw + 15
                d.polygon([(ax, y + 390), (ax + 60, y + 420), (ax, y + 450)], fill=INK)
        y += 900
    if "columns" in v:
        cols = v["columns"]
        n = len(cols)
        cw = (W - 2 * x - (n - 1) * 80) // n
        for i, col in enumerate(cols):
            cx = x + i * (cw + 80)
            d.rounded_rectangle((cx, y, cx + cw, y + 1080), radius=36, fill=CARD)
            d.text((cx + 70, y + 60), col[0], font=F("sansb", 80), fill=ACCENT)
            for j, item in enumerate(col[1:]):
                d.text((cx + 70, y + 220 + j * 150), item, font=F("sans", 72), fill=INK)
        y += 1140
    if v.get("standoff"):
        # two pieces facing each other, arrows both ways, a turn counter that keeps going
        cy = y + 520
        for px, col in ((1100, (40, 90, 120)), (2740, (170, 50, 40))):
            d.ellipse((px - 170, cy + 150, px + 170, cy + 230), fill=(80, 60, 40))
            d.rounded_rectangle((px - 90, cy - 220, px + 90, cy + 180), radius=60, fill=col)
            d.ellipse((px - 80, cy - 360, px + 80, cy - 200), fill=col)
        for yy, direction in ((cy - 120, 1), (cy + 40, -1)):
            x0, x1 = 1350, 2490
            d.line((x0, yy, x1, yy), fill=INK, width=14)
            tip = x1 if direction == 1 else x0
            d.polygon([(tip, yy), (tip - 60 * direction, yy - 36), (tip - 60 * direction, yy + 36)], fill=INK)
        d.text((1560, cy - 330), "hit → strike back → hit …", font=F("sansb", 76), fill=ACCENT)
        d.text((1640, cy + 120), "turn 41, 42, 43 …", font=F("mono", 76), fill=MUTED)
        y += 980
    for line in v.get("lines", []):
        d.text((x, y), line, font=F("sans", 76), fill=MUTED)
        y += 120
    if v.get("label"):
        label_pill(img, v["label"], F)
    return img


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a6-master", required=True, type=Path)
    ap.add_argument("--fonts", required=True, type=Path)
    a = ap.parse_args()
    F = lambda name, size: font(a.fonts, name, size)  # noqa: E731

    sheet = json.loads((ROOT / "beat_sheet.json").read_text(encoding="utf-8"))
    slug = sheet["metadata"]["slug"]
    work = ROOT / "_work"
    work.mkdir(exist_ok=True)
    segs = []
    for b in sheet["beats"]:
        bid, v = b["beat_id"], b["visual"]
        audio = ROOT / "mp3" / f"beat-{bid}.mp3"
        dur = round((float(b["actual_duration_s"]) + PAD_S) * FPS) / FPS
        out = work / f"seg-{bid}.mp4"
        afil = f"[a0]apad,atrim=0:{dur:.4f},aformat=sample_rates=48000:channel_layouts=stereo[aout]"
        if v["type"] == "slide":
            png = work / f"slide-{bid}.png"
            draw_slide(v, F).save(png)
            run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(png),
                 "-i", str(audio), "-filter_complex", f"[1:a]anull[a0];{afil};[0:v]format=yuv420p[vout]",
                 "-map", "[vout]", "-map", "[aout]", "-t", f"{dur:.4f}",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-tune", "stillimage",
                 "-c:a", "aac", "-b:a", "192k", str(out)])
        else:
            lab = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            label_pill(lab, v["label"], F)
            labpng = work / f"label-{bid}.png"
            lab.save(labpng)
            inputs, chains = [], []
            for i, (ss, dd) in enumerate(SEGMENTS[bid]):
                inputs += ["-ss", f"{ss}", "-t", f"{dd}", "-i", str(a.a6_master)]
                chains.append(f"[{i}:v]fps={FPS},scale={W}:{H},setsar=1[v{i}]")
            n = len(SEGMENTS[bid])
            vf = ";".join(chains) + ";" + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[cat];"
            vf += f"[cat]tpad=stop_mode=clone:stop_duration=30,trim=0:{dur:.4f},setpts=PTS-STARTPTS[base];"
            vf += f"[base][{n}:v]overlay=0:0,format=yuv420p[vout];"
            vf += f"[{n + 1}:a]anull[a0];{afil}"
            run(["ffmpeg", "-v", "error", "-y", *inputs, "-i", str(labpng), "-i", str(audio),
                 "-filter_complex", vf, "-map", "[vout]", "-map", "[aout]", "-t", f"{dur:.4f}",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                 "-c:a", "aac", "-b:a", "192k", str(out)])
        segs.append(out)
        print(f"{bid}: {dur:.3f} s ({v['type']})", flush=True)

    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{s.as_posix()}'\n" for s in segs), encoding="utf-8")
    joined = work / "joined.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    exp = ROOT / "exports"
    exp.mkdir(exist_ok=True)
    final = exp / f"{slug}.mp4"
    # loudness to about -20 LUFS, true peak under -1 dBTP; video stream copied unchanged
    run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-c:v", "copy",
         "-af", "loudnorm=I=-20:TP=-2:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", str(final)])
    print(final)


if __name__ == "__main__":
    main()
