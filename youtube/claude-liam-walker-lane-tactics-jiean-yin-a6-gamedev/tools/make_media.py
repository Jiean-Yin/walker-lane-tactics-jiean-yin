"""Build the 'own' media slots for the A6 film: engine-capture beats and evidence stills (native 4K).

Every picture is an actual file:
- frames of the capture masters (play-4k.mkv at 30 fps, slow-4k.mkv at 120 fps; lossless FFV1, real Godot renders of
  the tag-a6 copy). Segments are cut at exact frame indices; each source frame becomes one 30 fps output frame, so
  the play master keeps real speed and the slow master plays at 1/4 speed (labelled "¼ SPEED" on screen). Nothing
  else is retimed; capture audio is not used;
- Jiean's own strips in captures/ of the tag-a6 copy (fixture captures, Movie Maker, 30 fps);
- text and numbers read from the tag-a6 copy's recorded logs and documents, and Jiean's words from
  capture/quotes.json (verbatim, read from the tag by tools/quotes.py).
Labels, cards and layout are ours. Writes media/<beat>.mp4, stills/<beat>.png (720p previews), capture/clips.json.
Usage (reel folder, Brutalist venv python): python tools/make_media.py [B04 B10 ...]
Env (required): CAPTURE (<capture-copy>), BRUTALIST (<brutalist>); RUN (default "run-02")
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
CAPTURE = Path(os.environ["CAPTURE"])
A6 = CAPTURE / "a6"
RUN = CAPTURE / os.environ.get("RUN", "run-02")
FD = Path(os.environ["BRUTALIST"]) / "runtime/fonts"
SERIF = str(FD / "EB_Garamond/static/EBGaramond-Medium.ttf")
SERIF_I = str(FD / "EB_Garamond/static/EBGaramond-Italic.ttf")
SANS = str(FD / "Inter/static/Inter_28pt-Regular.ttf")
SANS_M = str(FD / "Inter/static/Inter_28pt-Medium.ttf")
MONO = str(FD / "PT_Mono/PTMono-Regular.ttf")
W, H, FPS = 3840, 2160, 30
SAFE = (192, 108, 3648, 2052)
PAGE, INK, SOFT, SPARK, CARD, BORDER, LABEL = "#FAF9F5", "#3D3929", "#73705F", "#D97757", "#FFFFFF", "#E5E2D9", "#303D34"
GOOD, BAD = "#2F6B4F", "#B23A2E"
MEASURED, PREDICTED = "#C2613F", "#2F6FB0"  # validated pair on #FAF9F5 (dataviz validate_palette.js, all checks pass)
SRC = {"play": RUN / "play-4k.mkv", "slow": RUN / "slow-4k.mkv"}
SRC_FPS = {"play": 30, "slow": 120}
ONLY = set(sys.argv[1:])
WORK = REEL / "_work"
Q = json.loads((REEL / "capture/quotes.json").read_text(encoding="utf-8"))


def font(p, s):
    return ImageFont.truetype(p, s)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("ffmpeg failed:\n" + " ".join(map(str, cmd)) + "\n" + r.stderr[-2000:])


def quote(key):
    v = Q.get(key)
    if not v:
        raise SystemExit(f"quotes.json '{key}' is empty: Jiean's words come from tag a6, never from this script")
    return v


def wrap(d, text, f, width):
    out = []
    for para in text.split("\n"):  # keep the writer's own line breaks (Jiean's A6.7 answer has several)
        cur = ""
        for w_ in para.split(" "):
            t = (cur + " " + w_).strip()
            if d.textbbox((0, 0), t, font=f)[2] > width and cur:
                out.append(cur)
                cur = w_
            else:
                cur = t
        if cur:
            out.append(cur)
    return out


def text_block(d, xy, text, f, width, fill=INK, gap=1.32):
    x, y = xy
    size = f.size
    for ln in wrap(d, text, f, width):
        d.text((x, y), ln, font=f, fill=fill)
        y += int(size * gap)
    return y


def pill(text1, text2, size1=50, size2=44, alpha=235, bg=(48, 61, 52)):
    f1, f2 = font(SANS_M, size1), font(SANS, size2)
    d = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    w = max(d.textbbox((0, 0), text1, font=f1)[2], d.textbbox((0, 0), text2, font=f2)[2] if text2 else 0) + 56
    h = 96 if not text2 else 164
    im = Image.new("RGBA", (w, h), (*bg, alpha))
    dr = ImageDraw.Draw(im)
    dr.text((28, 20), text1, font=f1, fill=(255, 253, 248, 255))
    if text2:
        dr.text((28, 92), text2, font=f2, fill=(242, 193, 78, 255))
    return im


def quote_card(lines, width=2600):
    """Cream card for verbatim words over footage. lines: [(text, style)], style True = attribution (sans, soft),
    False = a person's words (serif italic), "mono" = a log line, verbatim (mono)."""
    d = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    fq, fa, fm = font(SERIF_I, 64), font(SANS_M, 40), font(MONO, 50)
    rows = []
    for t, style in lines:
        f = fm if style == "mono" else (fa if style else fq)
        for ln in wrap(d, t, f, width - 112):
            rows.append((ln, f))
    h = 56 + sum(int(f.size * 1.3) for _, f in rows) + 40
    im = Image.new("RGBA", (width, h), (250, 249, 245, 238))
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, 10, h), fill=SPARK)
    y = 48
    for ln, f in rows:
        dr.text((56, y), ln, font=f, fill=SOFT if f is fa else INK)
        y += int(f.size * 1.3)
    return im


def frame_png(src, n, out):
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC[src], "-vf", f"select='eq(n\\,{n})'", "-frames:v", "1",
         "-update", "1", out])
    return Image.open(out).convert("RGB")


# ------------------------------------------------------------------ engine beats

def engine_segment(bid, i, seg, label, out):
    a, b = seg["a"], seg["b"]
    n = b - a
    l1, l2 = seg.get("label", label).split("|")
    src = seg["src"]
    lbl = WORK / f"{bid}-{i}-label.png"
    p = pill(l1, l2 + f" · capture frames {a}–{b} at {SRC_FPS[src]} fps", 46, 40)
    p.save(lbl)
    vf = f"select='between(n\\,{a}\\,{b - 1})',setpts=N/({FPS}*TB)"
    if seg.get("crop"):  # [x, y, w, h] of the 4K frame, scaled to fill: labelled as a crop
        x, y, w, h = seg["crop"]
        vf += f",crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=lanczos"
    inputs = ["-i", SRC[src], "-i", lbl]
    fc = f"[0:v]{vf}[v0];[v0][1:v]overlay={W - 150 - p.width}:110:format=auto[v1]"
    last = "v1"
    if seg.get("quote"):
        qc = quote_card(seg["quote"], seg.get("quote_width", 2600))
        qp = WORK / f"{bid}-{i}-quote.png"
        qc.save(qp)
        inputs += ["-i", qp]
        qx = W - 150 - qc.width if seg.get("quote_pos") == "bottom-right" else (W - qc.width) // 2
        fc += f";[{last}][2:v]overlay={qx}:{H - 150 - qc.height}:format=auto[v2]"
        last = "v2"
    fc += f";[{last}]format=yuv420p[v]"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-frames:v", n, "-r", FPS,
         "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "12", out])
    return n


def video_beat(b, records):
    bid = b["beat_id"]
    parts, total = [], 0
    for i, seg in enumerate(b["shot"]["segments"]):
        part = WORK / f"{bid}-part{i}.mp4"
        total += engine_segment(bid, i, seg, b["shot"]["label"], part)
        parts.append(part)
    assert total == b["clip_frames"], (bid, total, b["clip_frames"])
    out = REEL / "media" / f"{bid}.mp4"
    lst = WORK / f"{bid}-concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
    records[bid] = {"segments": b["shot"]["segments"], "n_frames": total, "duration_s": f"{total}/{FPS}",
                    "sources": {s["src"]: {"file": f"<capture-copy>/{RUN.name}/{SRC[s['src']].name}",
                                           "fps": SRC_FPS[s["src"]], "sha256": SRC_SHA[s["src"]]}
                                for s in b["shot"]["segments"]},
                    "label": b["shot"]["label"].replace("|", " / "), "path": f"media/{bid}.mp4", "sha256": sha(out)}
    print(bid, total, "frames", records[bid]["sha256"][:12])


# ------------------------------------------------------------------ stills

def base(title, label):
    im = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(im)
    d.text((SAFE[0], SAFE[1] - 6), title, font=font(SERIF, 118), fill=INK)
    if label:
        f = font(SANS_M, 46)
        tw = d.textbbox((0, 0), label, font=f)[2]
        d.rounded_rectangle((SAFE[0], 270, SAFE[0] + tw + 56, 350), 18, fill=LABEL)
        d.text((SAFE[0] + 28, 282), label, font=f, fill="#FFFDF8")
    d.text((SAFE[2], SAFE[3] - 4), "@NikBearBrown", font=font(SERIF, 60), fill=INK, anchor="rd")
    return im


def source_line(im, text):
    ImageDraw.Draw(im).text((SAFE[0], SAFE[3] - 4), text, font=font(SANS, 42), fill=SOFT, anchor="ld")


def card(d, box, head, body, accent=False, head_size=56, body_size=46, head_fill=None):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 24, fill=CARD, outline=SPARK if accent else BORDER, width=5)
    d.text((x0 + 40, y0 + 32), head, font=font(SANS_M, head_size), fill=head_fill or (SPARK if accent else INK))
    yy = y0 + 40 + head_size + 34
    for para in body:
        yy = text_block(d, (x0 + 40, yy), para, font(SANS, body_size), x1 - x0 - 80) + 14
    return yy


def strip(effect, rev, frame, box, scale):
    """Crop of one of Jiean's strip frames (1280 x 720), nearest-neighbour scaled."""
    p = A6 / "captures" / effect / rev / f"frame{frame:08d}.png"
    return Image.open(p).convert("RGB").crop(box).resize(((box[2] - box[0]) * scale, (box[3] - box[1]) * scale),
                                                          Image.NEAREST)


def log_line(path, pattern):
    for ln in (A6 / path).read_text(encoding="utf-8").splitlines():
        if re.search(pattern, ln):
            return ln.strip()
    raise SystemExit(f"{path}: no line matches {pattern!r}")


def still_B02():
    im = base("Two effects, two jobs", "")
    d = ImageDraw.Draw(im)
    hit = frame_png("play", SHOTS["b02_hit"], WORK / "B02-hit.png")
    fly = frame_png("play", SHOTS["b02_flight"], WORK / "B02-flight.png")
    tw = 1640
    th = round(tw * 9 / 16)
    cards = [(hit, "Effect A · hit burst", "CPUParticles2D ×3 · fires on an event: every \"damaged\" event",
              "Job: \"An arrow hit an archer, and which one.\""),
             (fly, "Effect B · arrow trail", "GPUParticles2D ×2 · runs while a condition holds: an arrow in flight",
              "Job: \"Who shot whom, and along which path.\"")]
    for k, (img, head, sub, job) in enumerate(cards):
        x = SAFE[0] + k * (tw + 176)
        im.paste(img.resize((tw, th), Image.LANCZOS), (x, 330))
        d.rectangle((x - 4, 326, x + tw + 4, 330 + th + 4), outline=BORDER, width=6)
        d.text((x, 330 + th + 24), f"main.tscn @ tag a6 · capture frame {SHOTS['b02_hit' if k == 0 else 'b02_flight']}",
               font=font(SANS, 38), fill=SOFT)
        y = 330 + th + 110
        d.text((x, y), head, font=font(SANS_M, 64), fill=SPARK)
        d.text((x, y + 92), job, font=font(SERIF_I, 64), fill=INK)
        text_block(d, (x, y + 190), sub, font(SANS, 46), tw)
    d.text((SAFE[0], 1840), "Renderer: Compatibility (OpenGL 3.3), project.godot:25 · 1280 × 720 · archer 80 px tall",
           font=font(MONO, 48), fill=INK)
    source_line(im, "CHANGE-BRIEF.md §1, §2 (the jobs, verbatim) · real Godot frames from the film's capture of the tag-a6 copy")
    return im


# Effect A strips: player archer (column 0, lane 5) in hit_burst_preview; frames of brief §5
A_BOX = (112, 504, 272, 664)
A_FRAMES = [10, 12, 15, 20, 30]
A_REVS = [("r0", "brief values: lifetime 0.12 · scale 1.25"), ("r1", "lifetime 0.12 → 0.36"),
          ("r2", "scale_amount 1.25 → 3.0"), ("r3", "lifetime 0.36 → 1.08 (now)")]


def still_B10():
    im = base("The flash, tuned by eye", "FIXTURE · hit_burst_preview.tscn · fixed seed · Jiean's Movie Maker captures, 30 fps")
    d = ImageDraw.Draw(im)
    cell, gap, x0, y0 = 352, 16, SAFE[0] + 470, 450
    for c, fr in enumerate(A_FRAMES):
        d.text((x0 + c * (cell + gap) + cell // 2, y0 - 14), f"frame {fr}", font=font(SANS_M, 40), fill=INK, anchor="md")
    for r, (rev, what) in enumerate(A_REVS):
        y = y0 + r * (cell + gap)
        d.text((SAFE[0], y + 60), rev, font=font(SERIF, 96), fill=SPARK if rev == "r3" else INK)
        text_block(d, (SAFE[0], y + 190), what, font(SANS, 38), 440, fill=SOFT)
        for c, fr in enumerate(A_FRAMES):
            tile = strip("hit_burst", rev, fr, A_BOX, 1).resize((cell, cell), Image.NEAREST)
            im.paste(tile, (x0 + c * (cell + gap), y))
    xq = x0 + 5 * (cell + gap) + 60
    wq = SAFE[2] - xq
    y = y0
    d.text((xq, y), "Jiean, after r1", font=font(SANS_M, 42), fill=SOFT)
    y = text_block(d, (xq, y + 60), "“I still cannot see the red flash clearly. Make it much larger than right now "
                   "and last 3 times longer than the current status.”", font(SERIF_I, 54), wq) + 40
    d.text((xq, y), "Claude's r1 prediction, frame 12", font=font(SANS_M, 42), fill=SOFT)
    y = text_block(d, (xq, y + 60), "“still clearly red”: did not match. Splinters and dust draw over the "
                   "flash (first child).", font(SANS, 46), wq) + 40
    d.text((xq, y), "Jiean's verdict on r2 and r3: kept", font=font(SANS_M, 42), fill=SOFT)
    text_block(d, (xq, y + 60), "“r2's shining color contradict more to the background color, and r3's enlarging "
               "makes unit easier to be seen.”", font(SERIF_I, 54), wq)
    source_line(im, "captures/hit_burst/r0–r3 (crops 160 × 160 px around the player archer) · TUNING.md, Jiean's words verbatim")
    return im


# Effect B strips: the arrow's path in arrow_trail_preview (player archer to column 2, lane 4)
B_BOX = (150, 420, 530, 700)
B_FRAMES = [16, 21, 26, 31]
B_PIXELS = {16: 403, 21: 1004, 26: 1264, 31: 1087}  # TUNING.md, Claude's comparison of r1 with r0


def still_B16():
    im = base("Stronger wisps: before and after", "FIXTURE · arrow_trail_preview.tscn · seed 71 · Jiean's Movie Maker captures, 30 fps")
    d = ImageDraw.Draw(im)
    tw, gap, x0, y0 = 760, 24, SAFE[0] + 220, 420
    th = round(tw * (B_BOX[3] - B_BOX[1]) / (B_BOX[2] - B_BOX[0]))
    for c, fr in enumerate(B_FRAMES):
        d.text((x0 + c * (tw + gap) + tw // 2, y0 - 12), f"frame {fr}" + (" · lands" if fr == 21 else ""),
               font=font(SANS_M, 40), fill=INK, anchor="md")
    for r, rev in enumerate(["r0", "r1"]):
        y = y0 + r * (th + gap)
        d.text((SAFE[0], y + th // 2 - 50), rev, font=font(SERIF, 96), fill=SPARK if rev == "r1" else INK)
        for c, fr in enumerate(B_FRAMES):
            im.paste(strip("arrow_trail", rev, fr, B_BOX, 1).resize((tw, th), Image.NEAREST), (x0 + c * (tw + gap), y))
    y = y0 + 2 * (th + gap) + 10
    for c, fr in enumerate(B_FRAMES):
        d.text((x0 + c * (tw + gap) + tw // 2, y), f"{B_PIXELS[fr]} px darker in r1", font=font(SANS_M, 42),
               fill=MEASURED, anchor="ma")
    y += 100
    d.text((SAFE[0], y), "Jiean's verdict on Effect B r1", font=font(SANS_M, 42), fill=SOFT)
    text_block(d, (SAFE[0], y + 60), "“" + quote("b_r1_verdict") + "”", font(SERIF_I, 58), SAFE[2] - SAFE[0] - 400)
    source_line(im, "captures/arrow_trail/r0, r1 (crops of the arrow's path) · pixel count: TUNING.md · verdict: TUNING.md, verbatim")
    return im


def still_B18():
    im = base("Testing the tests", "HEADLESS CHECK OUTPUT · recorded reports, no rendering")
    d = ImageDraw.Draw(im)
    m1 = "evidence/a6/mutations/mutation-1.log"
    m2 = "evidence/a6/mutations/mutation-2.log"
    lines1 = [log_line(m1, r"^FAIL .*scene text"), log_line(m1, r"^FAIL .*Splinters\.initial_velocity_min")]
    sum1 = log_line(m1, r"^SUMMARY").split(" -> ")[0]
    sum2 = log_line(m2, r"^SUMMARY").split(" -> ")[0]
    fail2 = log_line(m2, r"^FAIL ")
    x, wd = SAFE[0], SAFE[2] - SAFE[0]
    y = 410
    d.rounded_rectangle((x, y, x + wd, y + 470), 22, fill=CARD, outline=SPARK, width=5)
    d.text((x + 40, y + 30), "Mutation 1 · Splinters: initial_velocity_min = 140.0 written as initial_velocity = 140.0",
           font=font(SANS_M, 56), fill=INK)
    yy = y + 130
    for ln in lines1:
        yy = text_block(d, (x + 40, yy), ln, font(MONO, 50), wd - 80, fill=BAD) + 18
    d.text((x + 40, yy + 16), sum1 + " · exit 1 · the scene loaded with no error or warning", font=font(SANS_M, 52), fill=INK)
    y += 520
    d.rounded_rectangle((x, y, x + wd, y + 330), 22, fill=CARD, outline=BORDER, width=4)
    d.text((x + 40, y + 30), "Mutation 2 · Splinters.spread 75 → 60", font=font(SANS_M, 56), fill=INK)
    text_block(d, (x + 40, y + 120), fail2, font(MONO, 50), wd - 80, fill=BAD)
    d.text((x + 40, y + 220), sum2 + " · exit 1 · only that check", font=font(SANS_M, 52), fill=INK)
    y += 400
    d.text((x, y), "Jiean, mutation 1 in the running game", font=font(SANS_M, 42), fill=SOFT)
    text_block(d, (x, y + 60), "“Does not seem to have any other problem, but the red flash seemed to fade earlier.”",
               font(SERIF_I, 58), wd)
    source_line(im, "evidence/a6/mutations/mutation-1.log, mutation-2.log (lines verbatim) · TEST-REPORT.md A6.3")
    return im


def still_B20():
    im = base("A failing check, reported", "HEADLESS CHECK OUTPUT · recorded reports, no rendering")
    d = ImageDraw.Draw(im)
    first = log_line("evidence/a6/step5b/test_arrow_trail_state_60fps.log", r"^FAIL .*B2")
    first_sum = log_line("evidence/a6/step5b/test_arrow_trail_state_60fps.log", r"^SUMMARY").split(" -> ")[0]
    final = log_line("evidence/a6/final/test_arrow_trail_state_60fps.log", r"B2: each stop")
    final_sum = log_line("evidence/a6/final/test_arrow_trail_state_60fps.log", r"^SUMMARY").split(" -> ")[0]
    overlap = log_line("evidence/a6/final/test_hit_burst_state_60fps.log", r"A3 overlap")
    x, wd = SAFE[0], SAFE[2] - SAFE[0]
    cw = (wd - 2 * 80) // 3
    y = 410
    steps = [("1 · Agent's first run", [first, first_sum], BAD, True),
             ("2 · The brief corrected", ["CHANGE-BRIEF Revision 1, item 3: the trail stops 0 to 2 frames before the "
                                          "impact cue at 60 fps, not within one frame. Why: not investigated (game "
                                          "timing out of scope)."], INK, False),
             ("3 · Then the test", [final, final_sum], GOOD, True)]
    for k, (head, body, col, mono) in enumerate(steps):
        bx = x + k * (cw + 80)
        d.rounded_rectangle((bx, y, bx + cw, y + 820), 22, fill=CARD, outline=SPARK if k == 0 else BORDER, width=5)
        d.text((bx + 40, y + 30), head, font=font(SANS_M, 60), fill=INK)
        yy = y + 150
        for para in body:
            yy = text_block(d, (bx + 40, yy), para, font(MONO if mono else SANS, 50 if mono else 56), cw - 80,
                            fill=col if mono else INK) + 36
        if k < 2:
            d.text((bx + cw + 40, y + 410), "→", font=font(SANS_M, 80), fill=SPARK, anchor="mm")
    y += 890
    d.text((x, y), "Effect A's state test, the same final run (verbatim, up to its detail):", font=font(SANS_M, 44),
           fill=SOFT)
    text_block(d, (x, y + 64), overlap.split("  (")[0], font(MONO, 46), wd, fill=GOOD)
    d.text((x, y + 250), "What no headless run can show: any particle. The dummy renderer draws nothing.",
           font=font(SANS_M, 56), fill=INK)
    source_line(im, "evidence/a6/step5b and evidence/a6/final (lines verbatim) · CHANGE-BRIEF.md Revision 1 · TEST-REPORT.md A6.4")
    return im


def hbar_chart(d, box, rows, axis_max, ticks, unit, legend):
    """Horizontal bars (measured) with diamond markers (predicted). rows: [(label, measured, predicted)]."""
    x0, y0, x1, y1 = box
    lab_w = 900
    px0, px1 = x0 + lab_w, x1 - 60
    sx = lambda v: px0 + (px1 - px0) * v / axis_max
    row_h = (y1 - y0 - 140) // len(rows)
    for t in ticks:  # recessive grid
        d.line((sx(t), y0, sx(t), y1 - 120), fill=BORDER, width=3)
        d.text((sx(t), y1 - 100), f"{t:g}", font=font(SANS, 40), fill=SOFT, anchor="ma")
    d.text((px1, y1 - 40), unit, font=font(SANS, 40), fill=SOFT, anchor="ra")
    for i, (label, meas, pred) in enumerate(rows):
        cy = y0 + i * row_h + row_h // 2
        d.text((x0, cy), label, font=font(SANS_M, 50), fill=INK, anchor="lm")
        bh = 84
        d.rounded_rectangle((px0, cy - bh // 2, sx(meas), cy + bh // 2), 8, fill=MEASURED)
        d.text((sx(meas) + 24, cy - 6), f"+{meas:g} ms", font=font(SANS_M, 50), fill=INK, anchor="lm")
        px, s = sx(pred), 30
        d.polygon([(px, cy + 70 - s), (px + s, cy + 70), (px, cy + 70 + s), (px - s, cy + 70)], fill=PREDICTED,
                  outline=PAGE)
        right = px > (px0 + px1) / 2  # label on the inner side, so it never crosses the safe edge
        d.text((px - 44 if right else px + 44, cy + 70), f"predicted {pred:g}", font=font(SANS, 42), fill=SOFT,
               anchor="rm" if right else "lm")
    d.line((px0, y0, px0, y1 - 120), fill=INK, width=4)
    lx = x0
    for col, name, shape in legend:
        if shape == "bar":
            d.rounded_rectangle((lx, y1 - 40, lx + 60, y1 - 4), 6, fill=col)
        else:
            d.polygon([(lx + 30, y1 - 44), (lx + 52, y1 - 22), (lx + 30, y1), (lx + 8, y1 - 22)], fill=col)
        d.text((lx + 80, y1 - 22), name, font=font(SANS, 40), fill=INK, anchor="lm")
        lx += 120 + d.textbbox((0, 0), name, font=font(SANS, 40))[2]


def still_B22():
    im = base("The price without a screen", "RECORDED LOG · evidence/a6/step7 · chart redrawn from it")
    d = ImageDraw.Draw(im)
    hbar_chart(d, (SAFE[0], 440, SAFE[2] - 60, 1450),
               [("Effect A ×2 · CPU node · 46 particles", 0.0078, 0.015),
                ("Effect B ×2 · GPU node · 120 particles", 0.0066, 0.0)],
               0.016, [0, 0.004, 0.008, 0.012, 0.016], "mean CPU time per frame above the control, ms",
               [(MEASURED, "measured (mean of 1200 frames)", "bar"), (PREDICTED, "Jiean's prediction", "diamond")])
    y = 1540
    d.text((SAFE[0], y), "Budget (Jiean): 0.2 ms per frame. This axis ends at 0.016 ms: the budget is 12.5 times wider.",
           font=font(SANS_M, 52), fill=INK)
    d.text((SAFE[0], y + 90), "Control: the game at PLAN_MOVE, effects off, 0.1220 ms · empty scene 0.0032 ms · A vs B "
           "headless: −0.0012 ms (t −1.3), not told apart", font=font(SANS, 44), fill=SOFT)
    source_line(im, "godot/tests/cost_effects.gd, 2 rounds × 600 frames at 60 fps · TEST-REPORT.md A6.6 · CHANGE-BRIEF.md §7")
    return im


def still_B24():
    im = base("The price on the graphics card", "HUMAN CHECK · Jiean, Visual Profiler   |   RECORDED LOGS · evidence/a6/gpu")
    d = ImageDraw.Draw(im)
    # left: Jiean's ranges (one axis, 0-7 ms)
    lx0, lx1, y0 = SAFE[0], SAFE[0] + 1640, 420
    d.text((lx0, y0), "Visual Profiler, read by eye (Jiean)", font=font(SANS_M, 50), fill=INK)
    ranges = [("0 · effects off", (4, 6), (0, 1.5)), ("1 · Effect A ×2", (4.5, 6.5), (0.3, 1.5)),
              ("2 · Effect B ×2", (4.5, 6.5), (0.3, 1.2))]
    px0, px1 = lx0 + 420, lx1 - 20
    sx = lambda v: px0 + (px1 - px0) * v / 7.0
    for t in range(0, 8):
        d.line((sx(t), y0 + 100, sx(t), y0 + 760), fill=BORDER, width=3)
        d.text((sx(t), y0 + 780), str(t), font=font(SANS, 40), fill=SOFT, anchor="ma")
    d.text((px1, y0 + 840), "Render Viewport GPU time, ms", font=font(SANS, 40), fill=SOFT, anchor="ra")
    for i, (lab, on, off) in enumerate(ranges):
        cy = y0 + 180 + i * 210
        d.text((lx0, cy + 30), lab, font=font(SANS_M, 46), fill=INK, anchor="lm")
        d.rounded_rectangle((sx(on[0]), cy - 26, sx(on[1]), cy + 20), 8, fill=MEASURED)
        d.rounded_rectangle((sx(off[0]), cy + 40, sx(off[1]), cy + 86), 8, fill=PREDICTED)
    ly = y0 + 900
    for col, name, k in [(MEASURED, "vsync on", 0), (PREDICTED, "vsync off", 1)]:
        xx = lx0 + k * 420
        d.rounded_rectangle((xx, ly, xx + 60, ly + 36), 6, fill=col)
        d.text((xx + 80, ly + 18), name, font=font(SANS, 40), fill=INK, anchor="lm")
    # right: means (one axis, 0-0.008 ms above case 0)
    rx0, rx1 = SAFE[0] + 1820, SAFE[2]
    d.text((rx0, y0), "Means of 10 one-second readings, vsync off", font=font(SANS_M, 50), fill=INK)
    qx0, qx1 = rx0 + 360, rx1 - 300
    sq = lambda v: qx0 + (qx1 - qx0) * v / 0.008
    for t in [0, 0.002, 0.004, 0.006, 0.008]:
        d.line((sq(t), y0 + 100, sq(t), y0 + 620), fill=BORDER, width=3)
        d.text((sq(t), y0 + 640), f"{t:g}", font=font(SANS, 38), fill=SOFT, anchor="ma")
    d.text((qx1, y0 + 700), "GPU ms above case 0", font=font(SANS, 40), fill=SOFT, anchor="ra")
    for i, (lab, meas, pred) in enumerate([("A ×2", 0.0031, 0.001), ("B ×2", 0.0074, 0.003)]):
        cy = y0 + 220 + i * 230
        d.text((rx0, cy), lab, font=font(SANS_M, 50), fill=INK, anchor="lm")
        d.rounded_rectangle((qx0, cy - 40, sq(meas), cy + 40), 8, fill=MEASURED)
        d.text((sq(meas) + 20, cy), f"+{meas:g}", font=font(SANS_M, 48), fill=INK, anchor="lm")
        px, s = sq(pred), 28
        d.polygon([(px, cy + 70 - s), (px + s, cy + 70), (px, cy + 70 + s), (px - s, cy + 70)], fill=PREDICTED,
                  outline=PAGE)
        d.text((px + 40, cy + 70), f"Jiean predicted {pred:g}", font=font(SANS, 40), fill=SOFT, anchor="lm")
    d.text((rx0, y0 + 790), "Off case 0.1058 ms · A 0.1089 · B 0.1132 · budget 0.2 ms", font=font(SANS, 44), fill=INK)
    d.text((rx0, y0 + 860), "FPS with vsync on: 180 · 180 · 180 (display 180 Hz)", font=font(SANS_M, 46), fill=INK)
    d.text((rx0, y0 + 930), "FPS with vsync off: 1518 · 1430 · 1381", font=font(SANS, 44), fill=SOFT)
    y = 1440
    d.text((SAFE[0], y), "Jiean's conclusion", font=font(SANS_M, 42), fill=SOFT)
    text_block(d, (SAFE[0], y + 60), "“" + quote("price_conclusion") + "”", font(SERIF_I, 52), SAFE[2] - SAFE[0] - 400)
    source_line(im, "TEST-REPORT.md A6.6: Jiean's readings, sweep_vsync_on.log / sweep_vsync_off.log, Jiean's conclusion verbatim")
    return im


W_BOX = (190, 420, 470, 640)  # the wisps along the arc after the landing (arrow_trail_preview r1)


def still_B26():
    im = base("What the process shader does", "FIXTURE · arrow_trail_preview.tscn r1, wisps enlarged   |   Jiean's answer, TEST-REPORT A6.7")
    d = ImageDraw.Draw(im)
    tw, gap, y0 = 1100, 40, 420
    th = round(tw * (W_BOX[3] - W_BOX[1]) / (W_BOX[2] - W_BOX[0]))
    for c, fr in enumerate([21, 26, 31]):
        x = SAFE[0] + c * (tw + gap)
        im.paste(strip("arrow_trail", "r1", fr, W_BOX, 1).resize((tw, th), Image.NEAREST), (x, y0))
        d.text((x, y0 + th + 20), f"frame {fr}" + (" · lands" if fr == 21 else f" · +{(fr - 21) / 30:.2f} s"),
               font=font(SANS_M, 40), fill=INK)
    y = y0 + th + 120
    d.text((SAFE[0], y), "Jiean: which settings live in the shader, which in the draw step", font=font(SANS_M, 42), fill=SOFT)
    text_block(d, (SAFE[0], y + 60), "“" + quote("a67_split") + "”", font(SERIF_I, 52), SAFE[2] - SAFE[0] - 400)
    source_line(im, "captures/arrow_trail/r1 · godot/shaders/particles_generated.gdshader (editor-generated, unused) · "
                    "TEST-REPORT.md A6.7, verbatim")
    return im


def still_BCRD():
    im = base("Who did what", "")
    d = ImageDraw.Draw(im)
    cols = [("Jiean Yin (human)", ["chose both effects, their jobs and the retrigger rule",
                                   "wrote every prediction, the budget and the six answers",
                                   "approved each agent plan; ran both mutations",
                                   "captured every strip; read the Visual Profiler",
                                   "judged every revision; generated the process shader"]),
            ("Claude (AI)", ["claude -p agents: the scenes, drivers, config and state tests, the price script",
                             "Claude Code: reviewed each run, made the tuning edits Jiean asked for, built the price "
                             "fixture and the V key",
                             "caught: a wrong bound in the brief, a prediction that ignored draw order, a cleanup loop "
                             "that deleted a strip (recaptured by Jiean)"])]
    cw = (SAFE[2] - SAFE[0] - 80) // 2
    for i, (head, items) in enumerate(cols):
        x = SAFE[0] + i * (cw + 80)
        d.rounded_rectangle((x, 330, x + cw, 1660), 26, fill=CARD, outline=BORDER, width=4)
        d.text((x + 50, 370), head, font=font(SERIF, 96), fill=SPARK if i == 0 else INK)
        yy = 540
        for it in items:
            for j, ln in enumerate(wrap(d, it, font(SANS_M, 52), cw - 140)):
                d.text((x + 50, yy), ("· " if j == 0 else "  ") + ln, font=font(SANS_M, 52), fill=INK)
                yy += 72
            yy += 40
    d.text((SAFE[0], 1730), f"Textures: GradientTexture2D inside the scenes, no image file · Source shown: tag a6 "
           "· Godot 4.7.2", font=font(SANS_M, 50), fill=INK)
    source_line(im, "SOURCES.md Assignment 6 · FRICTIONAL.md Assignment 6 · TUNING.md")
    return im


STILLS = {"B02": still_B02, "B10": still_B10, "B16": still_B16, "B18": still_B18, "B20": still_B20, "B22": still_B22,
          "B24": still_B24, "B26": still_B26, "BCRD": still_BCRD}
SHOTS = json.loads((REEL / "capture/stills-frames.json").read_text(encoding="utf-8")) \
    if (REEL / "capture/stills-frames.json").exists() else {}


def still_beat(b, records):
    bid = b["beat_id"]
    im = STILLS[bid]()
    png = WORK / f"{bid}.png"
    im.save(png)
    (REEL / "stills").mkdir(exist_ok=True)
    im.resize((1280, 720), Image.LANCZOS).save(REEL / "stills" / f"{bid}.png")
    n = b["clip_frames"]
    out = REEL / "media" / f"{bid}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", FPS, "-i", png, "-frames:v", n, "-r", FPS,
         "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-tune", "stillimage", out])
    records[bid] = {"still": True, "n_frames": n, "path": f"media/{bid}.mp4", "sha256": sha(out),
                    "preview": f"stills/{bid}.png"}
    print(bid, "still", n)


SRC_SHA = {}


def main():
    WORK.mkdir(exist_ok=True)
    (REEL / "media").mkdir(exist_ok=True)
    for k, p in SRC.items():
        SRC_SHA[k] = sha(p)
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    rec_path = REEL / "capture" / "clips.json"
    records = json.loads(rec_path.read_text(encoding="utf-8")) if rec_path.exists() else {}
    for b in sheet["beats"]:
        bid = b["beat_id"]
        if ONLY and bid not in ONLY:
            continue
        if b["shot"].get("segments"):
            video_beat(b, records)
        elif bid in STILLS:
            still_beat(b, records)
    rec_path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
