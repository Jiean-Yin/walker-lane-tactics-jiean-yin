"""Native-4K evidence composites for the asset trace and the record beats (B04-B07, B16, B18).

Every picture placed here is an actual project file, a git-history blob, or a frame of capture run-03;
captions are ours. Reveals are timed to the measured narration (character position -> time) and the
media is rendered at the beat's frame-aligned duration, so the compiler does no retiming.

Usage (reel folder): python tools/make_stills.py <capture_dir> <hires_dir> [B04 B05 ...]
  capture_dir: <capture-copy>/run-03 (run-4k.mkv, run-03.avi)   hires_dir: SVG sketches rendered 4x by Edge
"""
import hashlib
import io
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
REPO = REEL.parents[1]
CAP = Path(sys.argv[1])
HIRES = Path(sys.argv[2])
ONLY = set(sys.argv[3:])
W, H, FPS = 3840, 2160, 30
SAFE = (192, 108, 3648, 2052)
FD = "<brutalist>/runtime/fonts/"
SERIF = FD + "EB_Garamond/static/EBGaramond-Medium.ttf"
SANS = FD + "Inter/static/Inter_28pt-Regular.ttf"
SANS_M = FD + "Inter/static/Inter_28pt-Medium.ttf"
MONO = FD + "PT_Mono/PTMono-Regular.ttf"
PAGE, INK, SOFT, SPARK, CARD, BORDER = "#FAF9F5", "#3D3929", "#73705F", "#D97757", "#FFFFFF", "#E5E2D9"
LINEN = "#D8C7A0"


def font(path, size):
    return ImageFont.truetype(path, size)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git_blob(rev_path: str) -> Image.Image:
    data = subprocess.run(["git", "-C", str(REPO), "show", rev_path], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(data)).convert("RGBA")


def master_frame(n: int) -> Image.Image:
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{n / FPS:.6f}", "-i", str(CAP / "run-4k.mkv"),
                        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def base(title, label):
    im = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(im)
    d.text((SAFE[0], SAFE[1] - 6), title, font=font(SERIF, 124), fill=INK)
    if label:
        f = font(SANS_M, 50)
        tw = d.textbbox((0, 0), label, font=f)[2]
        d.rounded_rectangle((SAFE[0], 290, SAFE[0] + tw + 56, 376), 18, fill="#303D34")
        d.text((SAFE[0] + 28, 304), label, font=f, fill="#FFFDF8")
    d.text((SAFE[2], SAFE[3] - 4), "@NikBearBrown", font=font(SERIF, 60), fill=INK, anchor="rd")
    return im


def source_line(im, text):
    ImageDraw.Draw(im).text((SAFE[0], SAFE[3] - 4), text, font=font(SANS, 44), fill=SOFT, anchor="ld")


def fit(img, box, bg=None, border=True):
    """Paste img into box (x0,y0,x1,y1) keeping aspect; returns the placed rect."""
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / img.width, (y1 - y0) / img.height)
    w, h = max(1, round(img.width * s)), max(1, round(img.height * s))
    r = img.resize((w, h), Image.LANCZOS)
    px, py = x0 + (x1 - x0 - w) // 2, y0 + (y1 - y0 - h) // 2
    return r, (px, py, px + w, py + h)


def panel(im, img, box, bg=CARD, pad=24, outline=BORDER, width=4):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, 22, fill=bg, outline=outline, width=width)
    r, rect = fit(img, (box[0] + pad, box[1] + pad, box[2] - pad, box[3] - pad))
    if r.mode == "RGBA":
        im.paste(r, rect[:2], r)
    else:
        im.paste(r, rect[:2])
    return rect


def wrap(d, text, f, width):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textbbox((0, 0), t, font=f)[2] > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def text_block(im, xy, text, f, width, fill=INK, spacing=1.32):
    d = ImageDraw.Draw(im)
    x, y = xy
    lh = int(f.size * spacing)
    for ln in wrap(d, text, f, width):
        d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def highlight(im, box, color=SPARK, width=12, radius=24):
    ImageDraw.Draw(im).rounded_rectangle(box, radius, outline=color, width=width)


def dashed_ellipse(im, box, color=SPARK, width=10, n=36):
    d = ImageDraw.Draw(im)
    cx, cy, rx, ry = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2, (box[2] - box[0]) / 2, (box[3] - box[1]) / 2
    for i in range(0, n, 2):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        pts = [(cx + rx * math.cos(a0 + (a1 - a0) * k / 6), cy + ry * math.sin(a0 + (a1 - a0) * k / 6)) for k in range(7)]
        d.line(pts, fill=color, width=width)


def cue(beat, phrase, lead=0.25):
    """Time at which `phrase` is spoken, estimated from its character position in the measured narration."""
    text = beat["narration_text"]
    i = text.find(phrase)
    if i < 0:
        raise SystemExit(f"{beat['beat_id']}: phrase not in narration: {phrase!r}")
    return max(0.0, beat["actual_duration_s"] * i / len(text) - lead)


def render(bid, states, duration_s):
    """states: [(t_start, PIL.Image)]; 8-frame crossfades; exact frame count at FPS."""
    n = math.ceil(duration_s * FPS - 1e-8)
    out = REEL / "media" / f"{bid}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-frames:v", str(n), "-c:v", "libx264", "-preset", "slow",
                          "-crf", "12", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    arrs = [np.asarray(s[1].convert("RGB"), dtype=np.float32) for s in states]
    starts = [round(s[0] * FPS) for s in states]
    fade = 8
    cache = {}
    for f in range(n):
        k = max(i for i, s in enumerate(starts) if s <= f) if f >= starts[0] else 0
        a = (f - starts[k]) / fade if k > 0 else 1.0
        if a >= 1.0:
            key = ("s", k)
            if key not in cache:
                cache[key] = arrs[k].astype(np.uint8).tobytes()
            p.stdin.write(cache[key])
        else:
            p.stdin.write((arrs[k - 1] * (1 - a) + arrs[k] * a).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit(f"ffmpeg failed for {bid}")
    states[-1][1].convert("RGB").resize((1280, 720), Image.LANCZOS).save(REEL / "stills" / f"{bid}-preview.png")
    print(bid, "->", out.name, n, "frames", sha(out)[:12])
    return out


# ---------------------------------------------------------------- beats

def b04(beat):
    title, label = "Step One: The Idle Pose, on Paper", \
        "Design sketches: SVG by Claude Code under Jiean Yin's direction — not generated art"
    im = base(title, label)
    poses = Image.open(HIRES / "poses@4x.png").convert("RGB").crop((80, 200, 960, 1180))
    init = Image.open(REPO / "design/character/init/idle.png").convert("RGB").crop((250, 160, 770, 960))
    board = Image.open(HIRES / "02-board-start@4x.png").convert("RGB")
    y0, y1 = 450, 1560
    ra = panel(im, poses, (192, y0, 1092, y1))
    rb = panel(im, init, (1152, y0, 1992, y1))
    rc = panel(im, board, (2052, y0 + 170, 3648, y1 - 170))
    d = ImageDraw.Draw(im)
    fc = font(SANS, 46)
    text_block(im, (192, y1 + 30), "CHARACTER-SHEET.md · pose 2 · idle", fc, 900)
    text_block(im, (1152, y1 + 30), "design/character/init/idle.png — the image SDXL starts from", fc, 840)
    text_block(im, (2052, y1 - 140), "STORYBOARD.md panel 2 · board at start (the sketch has two enemies; "
               "the slice has one, CHANGE-BRIEF R1)", fc, 1590)
    source_line(im, "Repository at film-source-v1 · sketches rendered from their SVG sources at 4x (headless Edge, as design/tools/render_png.sh)")
    chips = ["Ball head, one dot eye", "Base disc always visible", "Thick outline: birch on linen is only 1.1 : 1"]
    fchip = font(SANS_M, 50)
    x = 192
    boxes = []
    for c in chips:
        tw = d.textbbox((0, 0), c, font=fchip)[2]
        boxes.append((x, 1790, x + tw + 64, 1890))
        x += tw + 64 + 36
    states = [(0.0, im.copy())]
    for i, phrase in enumerate(["a ball head", "a base disc", "a thick dark outline"]):
        s = states[-1][1].copy()
        dd = ImageDraw.Draw(s)
        dd.rounded_rectangle(boxes[i], 26, fill="#F2E5D8", outline=SPARK, width=6)
        dd.text((boxes[i][0] + 32, boxes[i][1] + 20), chips[i], font=fchip, fill="#663725")
        states.append((cue(beat, phrase), s))
    s = states[-1][1].copy()
    highlight(s, (1152 - 10, y0 - 10, 1992 + 10, y1 + 10))
    states.append((cue(beat, "That sketch is also"), s))
    return render("B04", states, beat["render_s"])


def b05(beat):
    rec = json.loads((REPO / "assets/gen-log.jsonl").read_text(encoding="utf-8").splitlines()[17])
    assert rec["asset_id"] == "CHAR-IDLE" and rec["seed"] == 211
    im = base("Step Two: The Exact Recipe",
              "assets/gen-log.jsonl line 18 · values verbatim · long strings wrapped for display")
    d = ImageDraw.Draw(im)
    fh, fp, fn = font(SANS_M, 50), font(MONO, 54), font(MONO, 44)
    lx, lw = 232, 2020
    d.text((lx, 450), '"prompt"  (P4)', font=fh, fill=SOFT)
    yp = text_block(im, (lx, 530), rec["prompt"], fp, lw, spacing=1.36)
    prompt_box = (lx - 34, 430, lx + lw + 30, yp + 20)
    d.text((lx, yp + 60), '"negative_prompt"  (N2)', font=fh, fill=SOFT)
    yn = text_block(im, (lx, yp + 140), rec["negative_prompt"], fn, lw, fill=SOFT, spacing=1.36)
    rows = [("model", rec["model"]), ("mode", rec["mode"]), ("init_image", rec["init_image"]),
            ("strength", str(rec["strength"])), ("seed", str(rec["seed"])), ("steps", str(rec["steps"])),
            ("guidance", str(rec["guidance"])), ("size", f'{rec["width"]} x {rec["height"]}'),
            ("generator", rec["generator"]), ("sha256", rec["sha256"][:16] + "…")]
    rx, ry = 2390, 440
    fk, fv = font(SANS, 42), font(MONO, 46)
    d.rounded_rectangle((rx, ry, 3648, ry + 1450), 22, fill=CARD, outline=BORDER, width=4)
    row_boxes = {}
    y = ry + 34
    for k, v in rows:
        d.text((rx + 40, y), k, font=fk, fill=SOFT)
        yy = text_block(im, (rx + 40, y + 54), v, fv, 3648 - rx - 80, spacing=1.25)
        row_boxes[k] = (rx + 14, y - 14, 3634, yy + 4)
        y = yy + 26
    note = ("Reference runs (TEST-REPORT R2): strength 0.75 nearly traced the sketch; 0.85 drifted to a front "
            "view. Seeds 202 and 212 (lines 17, 19) share every other value.")
    text_block(im, (lx, max(yn + 50, 1700)), note, font(SANS, 44), lw, fill=INK)
    source_line(im, "Stable Diffusion XL base 1.0 · diffusers " + rec["diffusers"] + " · torch " + rec["torch"]
                + " · run locally on Jiean's laptop GPU (SOURCES.md)")
    states = [(0.0, im.copy())]
    for phrase, keys in [("Stable Diffusion XL", ["model"]), ("Image-to-image", ["mode", "init_image"]),
                         ("strength point eight", ["strength"]), ("Prompt P4", ["prompt"]),
                         ("thirty steps", ["steps", "guidance"]), ("three seeds", ["seed"])]:
        s = im.copy()
        for k in keys:
            highlight(s, prompt_box if k == "prompt" else row_boxes[k], width=10, radius=18)
        states.append((cue(beat, phrase), s))
    return render("B05", states, beat["render_s"])


def b06(beat):
    im = base("Raw SDXL Output — Not In-Engine", "Raw model output, downscaled · the engine never shows these files")
    d = ImageDraw.Draw(im)
    seeds = [202, 211, 212]
    boxes = [(192, 440, 1292, 1540), (1370, 440, 2470, 1540), (2548, 440, 3648, 1540)]
    log = {json.loads(l)["seed"]: json.loads(l) for l in
           (REPO / "assets/gen-log.jsonl").read_text(encoding="utf-8").splitlines()[16:19]}
    fc, fs = font(SANS_M, 54), font(MONO, 40)
    for s_, b in zip(seeds, boxes):
        p = REPO / f"assets/_raw/art/CHAR-IDLE/CHAR-IDLE-pose01-s{s_}-str0.80.png"
        assert sha(p) == log[s_]["sha256"], p
        panel(im, Image.open(p).convert("RGB"), b, pad=10)
        d.text((b[0], b[3] + 34), f"seed {s_}", font=fc, fill=INK)
        d.text((b[0], b[3] + 110), "sha256 " + log[s_]["sha256"][:12] + "…", font=fs, fill=SOFT)
    source_line(im, "assets/_raw/art/CHAR-IDLE/CHAR-IDLE-pose01-s<seed>-str0.80.png · hashes match assets/gen-log.jsonl lines 17–19")
    notes = {202: ("Claude's recommendation · not chosen", SOFT), 211: ("Jiean's choice", SPARK),
             212: ("Rejected: long hair, front-facing face", "#A44A32")}
    states = [(0.0, im.copy())]
    for phrase, s_ in [("Claude recommended", 202), ("Jiean chose", 211), ("Seed 212 was rejected", 212)]:
        s = states[-1][1].copy()
        b = boxes[seeds.index(s_)]
        txt, col = notes[s_]
        ImageDraw.Draw(s).text((b[0], b[3] + 180), txt, font=font(SANS_M, 50), fill=col)
        if s_ == 211:
            highlight(s, (b[0] - 14, b[1] - 14, b[2] + 14, b[3] + 14), width=14)
        states.append((cue(beat, phrase), s))
    return render("B06", states, beat["render_s"])


def on_linen(sprite, scale=2.6, flip=False):
    sp = sprite.transpose(Image.FLIP_LEFT_RIGHT) if flip else sprite
    sp = sp.resize((round(sp.width * scale), round(sp.height * scale)), Image.LANCZOS)
    bg = Image.new("RGBA", (sp.width + 120, sp.height + 120), LINEN)
    bg.paste(sp, (60, 60), sp)
    return bg, scale


def b07(beat):
    im = base("Jiean's Choice, Then the Logged Edits", "Actual files: raw output, git history and godot/assets — not in-engine")
    d = ImageDraw.Draw(im)
    raw = Image.open(REPO / "assets/_raw/art/CHAR-IDLE/CHAR-IDLE-pose01-s211-str0.80.png").convert("RGB")
    cut = git_blob("4d5ff51:godot/assets/art/archer_idle.png")
    fixed = Image.open(REPO / "godot/assets/art/archer_idle.png").convert("RGBA")
    enemy = Image.open(REPO / "godot/assets/art/archer_idle_enemy.png").convert("RGBA")
    assert hashlib.sha256(subprocess.run(["git", "-C", str(REPO), "show", "4d5ff51:godot/assets/art/archer_idle.png"],
                                         capture_output=True).stdout).hexdigest().startswith("a00d7b5d")
    y0, y1 = 440, 1450
    xs = [192, 1072, 1952, 2832]
    w = 816
    imgs = [raw.crop((230, 120, 800, 990)), on_linen(cut)[0], on_linen(fixed)[0], on_linen(enemy)[0]]
    rects = []
    for x, img in zip(xs, imgs):
        rects.append(panel(im, img, (x, y0, x + w, y1), pad=16))
    for x in xs[1:]:
        d.polygon([(x - 50, 930), (x - 14, 945), (x - 50, 960)], fill=SOFT)
    caps = [("1 · raw s211", "SDXL output (white ground)"),
            ("2 · cut-out", "rembg u2net, halo cleanup (rgb > 232 or alpha < 40 → transparent), scale 0.4533, "
                            "anchored on the base · commit 4d5ff51 · a00d7b5d"),
            ("3 · base redrawn", "walnut #5A3A22 ellipse 40 × 12 game px with ink outline, behind the piece · "
                                 "12f7283 · 8cf54fc3"),
            ("4 · enemy copy", "9,274 teal px (hue 165–200°, sat > 0.25) → hue 4° · 7d962587 · flipped at runtime")]
    fh, fb = font(SANS_M, 50), font(SANS, 40)
    for x, (h_, b_) in zip(xs, caps):
        d.text((x, y1 + 30), h_, font=fh, fill=INK)
        text_block(im, (x, y1 + 100), b_, fb, w, fill=SOFT, spacing=1.3)
    source_line(im, "assets/edit-log.jsonl lines 7, 29, 30 (input/output SHA-256) · design/tools/process_sprites.py · "
                    "the in-fill attempt (line 19) was rejected")
    states = [(0.0, im.copy())]
    for phrase, k in [("rembg", 1), ("scaled and anchored", 1), ("teal pixels turn red", 3)]:
        s = im.copy()
        r = rects[k]
        highlight(s, (xs[k] - 12, y0 - 12, xs[k] + w + 12, y1 + 12), width=12)
        states.append((cue(beat, phrase), s))
    s = im.copy()
    highlight(s, (xs[1] - 12, y0 - 12, xs[1] + w + 12, y1 + 12), width=12)
    r = rects[1]
    sc = (r[2] - r[0]) / (cut.width * 2.6 + 120)
    bx0 = r[0] + (60 + 0.05 * cut.width * 2.6) * sc
    bx1 = r[0] + (60 + 0.95 * cut.width * 2.6) * sc
    by1 = r[1] + (60 + cut.height * 2.6) * sc
    dashed_ellipse(s, (bx0 - 20, by1 - 150 * sc - 30, bx1 + 20, by1 + 30))
    states.append((cue(beat, "But look at the second panel"), s))
    return render("B07", states, beat["render_s"])


def b16(beat):
    a, e = 1089, 1594
    ev = [json.loads(l) for l in (REEL / "capture/run-03-inputs.jsonl").read_text(encoding="utf-8").splitlines()]
    trig = [(x["frame"], x["detail"]["id"]) for x in ev if x["event"] == "sfx_trigger" and a <= x["frame"] < e]
    music_stop = [x["frame"] for x in ev if x["event"] == "music_state" and x["detail"] == "stopped" and a <= x["frame"] < e]
    w = wave.open(str(REEL / "_work" / "B14-audio.wav"))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32).mean(1) / 32768
    hop = 480
    env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(np.maximum(env, 1e-5))
    im = base("Measured: The Segment You Just Heard",
              "B14 audio (Movie Maker AVI, same run) · held 4K frames · trigger frames from capture/run-03-inputs.jsonl")
    d = ImageDraw.Draw(im)
    # held frames at four events
    picks = [(1218 + 4, "HOP · turn 4 landing"), (1302 + 6, "HURT · you are hit"), (1333 + 6, "HIT · your arrow lands"),
             (1497 + 20, "WIN · the music stops")]
    fw = 840
    for i, (f, cap) in enumerate(picks):
        fr = master_frame(f).crop((330, 650, 2900, 2000) if "WIN" in cap else (330, 1000, 2730, 2000))
        x0 = 192 + i * (fw + 32)
        panel(im, fr, (x0, 420, x0 + fw, 420 + 600), pad=8)
        d.text((x0, 1040), cap, font=font(SANS_M, 46), fill=INK)
        d.text((x0, 1100), f"frame {f} (held)", font=font(SANS, 40), fill=SOFT)
    # plot
    px0, px1, py0, py1 = 400, 3600, 1260, 1840
    d.rectangle((px0, py0, px1, py1), fill=CARD, outline=BORDER, width=3)
    dmin, dmax = -60.0, 0.0
    T = len(x) / 48000
    pts = []
    for i, v in enumerate(db):
        t = i * hop / 48000
        pts.append((px0 + (px1 - px0) * t / T, py1 - (py1 - py0) * (min(max(v, dmin), dmax) - dmin) / (dmax - dmin)))
    d.polygon([(px0, py1)] + pts + [(px1, py1)], fill="#CFC6B5")
    d.line(pts, fill=INK, width=3)
    fa = font(SANS, 38)
    for db_tick in (-60, -40, -20, 0):
        y = py1 - (py1 - py0) * (db_tick - dmin) / (dmax - dmin)
        d.text((px0 - 20, y), f"{db_tick} dB", font=fa, fill=SOFT, anchor="rm")
    for s_ in range(0, 17, 2):
        xx = px0 + (px1 - px0) * s_ / T
        d.text((xx, py1 + 16), f"{s_} s", font=fa, fill=SOFT, anchor="ma")
    source_line(im, "RMS per 10 ms of the B14 track; markers = logged sfx_trigger frames (onset measured 3–28 ms after "
                    "the frame); music stop = logged music_state")
    groups = {"the hops": ["SFX-HOP"], "the hurt": ["SFX-HURT"], "two hits": ["SFX-HIT"], "the win": ["SFX-WIN"]}
    states = [(0.0, im.copy())]
    shown = []
    for phrase, ids in groups.items():
        shown += ids
        s = im.copy()
        dd = ImageDraw.Draw(s)
        for j, (f, sid) in enumerate(trig):
            if sid not in shown:
                continue
            xx = px0 + (px1 - px0) * ((f - a) / FPS) / T
            dd.line((xx, py0, xx, py1), fill=SPARK, width=8)
            dd.text((xx + 10, py0 + 14 + 58 * (j % 3)),
                    sid.replace("SFX-", ""), font=font(SANS_M, 46), fill="#A44A32")
        if "SFX-WIN" in shown and music_stop:
            xx = px0 + (px1 - px0) * ((music_stop[0] - a) / FPS) / T
            dd.text((xx + 150, py0 + 260), "music stops, then silence", font=font(SANS_M, 44), fill=INK, anchor="la")
        states.append((cue(beat, phrase), s))
    return render("B16", states, beat["render_s"])


def b18(beat):
    im = base("Still Uncertain — and the Next Step", "Held 4K engine frame (run-03 frame 630) and the actual sprite files · quotes verbatim")
    d = ImageDraw.Draw(im)
    fr = master_frame(630).crop((1400, 980, 2800, 1980))
    r1 = panel(im, fr, (192, 430, 1592, 1430), pad=8)
    fq = font(SERIF, 56)
    y = text_block(im, (192, 1470), "\u201cI found it not clear if the attack target is on the character's board.\u201d",
                   fq, 1400, spacing=1.2)
    y = text_block(im, (192, y + 10), "\u201ca new player cannot understand why enemy move or not.\u201d", fq, 1400, spacing=1.2)
    d.text((192, y + 16), "Jiean Yin, muted playtest (TEST-REPORT §6)", font=font(SANS, 40), fill=SOFT)
    pairs = [("hurt", "no squint"), ("defeat", "dot eye, navy bow"), ("win", "arms cover the face")]
    x0 = 1700
    cw = 630
    for i, (st, why) in enumerate(pairs):
        yy = 430 + i * 330
        sk = Image.open(REPO / f"design/character/init/{st}.png").convert("RGB")
        sk = sk.crop(sk.convert("L").point(lambda v: 255 if v < 250 else 0).getbbox())
        spr, _ = on_linen(Image.open(REPO / f"godot/assets/art/archer_{st}.png").convert("RGBA"), 1.0)
        panel(im, sk, (x0, yy, x0 + 280, yy + 300), pad=10)
        panel(im, spr, (x0 + 300, yy, x0 + 580, yy + 300), pad=10)
        d.text((x0 + 610, yy + 80), st, font=font(SANS_M, 50), fill=INK)
        d.text((x0 + 610, yy + 150), why, font=font(SANS, 44), fill=SOFT)
    d.text((x0, 1430), "sheet sketch | sprite (TEST-REPORT §2)", font=font(SANS, 40), fill=SOFT)
    box_nr = (2640 + 120, 430, 3648, 1000)
    d.rounded_rectangle(box_nr, 22, fill=CARD, outline=BORDER, width=4)
    d.text((box_nr[0] + 36, 470), "Not reproducible", font=font(SANS_M, 50), fill=INK)
    text_block(im, (box_nr[0] + 36, 550), "ElevenLabs gives no seed, and the game text Jiean added to the sound "
               "prompts was not recorded.", font(SANS, 44), box_nr[2] - box_nr[0] - 72, fill=SOFT)
    nxt = (1700, 1560, 3648, 1960)
    source_line(im, "TEST-REPORT.md §2, §6, §10 · SOURCES.md · README Known limitations")
    states = [(0.0, im.copy())]
    s = im.copy()
    highlight(s, (192, 430, 1592, 1430))
    states.append((cue(beat, "Played muted"), s))
    s = states[-1][1].copy()
    highlight(s, (x0 - 14, 416, x0 + 1040, 1400))
    states.append((cue(beat, "Some poses miss"), s))
    s = states[-1][1].copy()
    highlight(s, box_nr)
    states.append((cue(beat, "The ElevenLabs sounds"), s))
    s = states[-1][1].copy()
    dd = ImageDraw.Draw(s)
    dd.rounded_rectangle(nxt, 26, fill=CARD, outline=SPARK, width=8)
    dd.text((nxt[0] + 40, nxt[1] + 34), "Next step (Jiean's)", font=font(SANS_M, 52), fill="#663725")
    text_block(s, (nxt[0] + 40, nxt[1] + 116), "A simpler enemy that keeps moving toward the end and avoids direct "
               "contact, plus a clearer target colour.", font(SANS, 50), nxt[2] - nxt[0] - 80, fill=INK)
    states.append((cue(beat, "next step"), s))
    return render("B18", states, beat["render_s"])


def b02(beat):
    rp = beat["shot"]["replaced_remotion"]
    im = base("The Concept and Its Four Pillars", "CONCEPT.md version 1 (2026-10-09, before any asset was generated)")
    d = ImageDraw.Draw(im)
    lb = (192, 440, 1700, 1960)
    d.rounded_rectangle(lb, 26, fill=CARD, outline=BORDER, width=4)
    d.text((lb[0] + 56, lb[1] + 50), "CONCEPT.md · The game in two sentences", font=font(SANS_M, 46), fill=SOFT)
    d.line((lb[0] + 56, lb[1] + 150, lb[0] + 56, lb[1] + 860), fill="#985039", width=8)
    text_block(im, (lb[0] + 96, lb[1] + 150), rp["excerpt"], font(SERIF, 66), lb[2] - lb[0] - 160, spacing=1.3)
    d.text((lb[0] + 56, lb[3] - 90), "Exact excerpt · reconstructed reading view", font=font(SANS, 40), fill=SOFT)
    cx0, cx1 = 1780, 3648
    d.text((cx0, 440), "Design pillars — and the one look or sound choice that honours each",
           font=font(SANS_M, 44), fill=SOFT)
    boxes = []
    for i, c in enumerate(rp["cards"]):
        y0 = 540 + i * 360
        boxes.append((cx0, y0, cx1, y0 + 320))
    def draw_cards(img, lit):
        dd = ImageDraw.Draw(img)
        for i, (c, b) in enumerate(zip(rp["cards"], boxes)):
            on = i == lit
            dd.rounded_rectangle(b, 24, fill="#F2E5D8" if on else CARD, outline=SPARK if on else BORDER, width=8 if on else 4)
            dd.text((b[0] + 50, b[1] + 46), c["label"], font=font(SANS_M, 60), fill="#663725")
            text_block(img, (b[0] + 50, b[1] + 150), c["text"], font(SANS, 52), b[2] - b[0] - 100, fill=INK, spacing=1.25)
    source_line(im, "CONCEPT.md · Design pillars table (card wording shortened) · film-source-v1 = fcf33ef")
    s0 = im.copy()
    draw_cards(s0, -1)
    states = [(0.0, s0)]
    for i, ph in enumerate(["Read the board", "Plans collide", "Every piece has weight", "when you lose a piece"]):
        st = im.copy()
        draw_cards(st, i)
        states.append((cue(beat, ph), st))
    return render("B02", states, beat["render_s"])


def main():
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    (REEL / "stills").mkdir(exist_ok=True)
    (REEL / "media").mkdir(exist_ok=True)
    work = REEL / "_work"
    work.mkdir(exist_ok=True)
    if not (work / "B14-audio.wav").exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(REEL / "media/B14.mp4"), "-vn", "-c:a", "pcm_s16le",
                        str(work / "B14-audio.wav")], check=True)
    fns = {"B02": b02, "B04": b04, "B05": b05, "B06": b06, "B07": b07, "B16": b16, "B18": b18}
    for b in sheet["beats"]:
        if b["beat_id"] in fns and (not ONLY or b["beat_id"] in ONLY):
            b["render_s"] = math.ceil(b["actual_duration_s"] * FPS - 1e-8) / FPS
            fns[b["beat_id"]](b)


if __name__ == "__main__":
    main()
