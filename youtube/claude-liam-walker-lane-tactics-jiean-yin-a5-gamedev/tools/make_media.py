"""Build the 'own' media slots for the A5 film: engine-capture beats and evidence stills (native 4K).

Every picture is an actual file: frames of capture run-02 (tint-4k.mkv, diorama-4k.mkv, hint-4k.mkv, lossless FFV1,
real Godot renders of the tag-a5 copy), Jiean's own captures (evidence/a5/captures, made with key C in a real
window), or text read from the a5 files and recorded reports. Labels, cards and layout are ours. Engine segments are
cut at exact frame numbers and never retimed; capture audio is not used. Writes media/<beat>.mp4, stills/<beat>.png
(720p previews) and capture/clips.json.
Usage (reel folder, Brutalist venv python): python tools/make_media.py [B04 B07 ...]
Env (required): CAPTURE (<capture-copy>), BRUTALIST (<brutalist>)
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
CAPTURE = Path(os.environ["CAPTURE"])
A5 = CAPTURE / "a5"
RUN = CAPTURE / "run-02"
FD = Path(os.environ["BRUTALIST"]) / "runtime/fonts"
SERIF = str(FD / "EB_Garamond/static/EBGaramond-Medium.ttf")
SANS = str(FD / "Inter/static/Inter_28pt-Regular.ttf")
SANS_M = str(FD / "Inter/static/Inter_28pt-Medium.ttf")
MONO = str(FD / "PT_Mono/PTMono-Regular.ttf")
W, H, FPS = 3840, 2160, 30
SAFE = (192, 108, 3648, 2052)
PAGE, INK, SOFT, SPARK, CARD, BORDER, LABEL = "#FAF9F5", "#3D3929", "#73705F", "#D97757", "#FFFFFF", "#E5E2D9", "#303D34"
GOOD, BAD = "#2F6B4F", "#B23A2E"
SRC = {"tint": RUN / "tint-4k.mkv", "diorama": RUN / "diorama-4k.mkv", "hint": RUN / "hint-4k.mkv"}
ONLY = set(sys.argv[1:])
WORK = REEL / "_work"


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


def frame_png(src, n, out):
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC[src], "-vf", f"select='eq(n\\,{n})'", "-frames:v", "1",
         "-update", "1", out])
    return Image.open(out).convert("RGB")


# ------------------------------------------------------------------ engine beats

def engine_segment(bid, i, seg, label, out):
    a, b = seg["a"], seg["b"]
    n = b - a
    l1, l2 = seg.get("label", label).split("|")
    lbl = WORK / f"{bid}-{i}-label.png"
    p = pill(l1, l2 + f" · capture run-02 frames {a}–{b}", 46, 40)
    p.save(lbl)
    # 2D game: top-right, over the music/sound status, clear of the turn counter, HP and the board;
    # 3D: top-left, over the dark background or the floor
    x = W - 150 - p.width if seg["src"] == "tint" else 150
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a / FPS:.6f}", "-i", SRC[seg["src"]], "-i", lbl, "-filter_complex",
         f"[0:v][1:v]overlay={x}:110:format=auto,format=yuv420p[v]", "-map", "[v]", "-frames:v", n, "-r", FPS,
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
                    "sources": {s["src"]: {"file": f"<capture-copy>/run-02/{SRC[s['src']].name}",
                                           "sha256": SRC_SHA[s["src"]]} for s in b["shot"]["segments"]},
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


def wrap(d, text, f, width):
    words, out, cur = text.split(" "), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textbbox((0, 0), t, font=f)[2] > width and cur:
            out.append(cur)
            cur = w_
        else:
            cur = t
    if cur:
        out.append(cur)
    return out


def card(d, box, head, body, accent=False, head_size=56, body_size=46):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 24, fill=CARD, outline=SPARK if accent else BORDER, width=5)
    d.text((x0 + 40, y0 + 32), head, font=font(SANS_M, head_size), fill=SPARK if accent else INK)
    yy = y0 + 40 + head_size + 34
    for para in body:
        for ln in wrap(d, para, font(SANS, body_size), x1 - x0 - 80):
            d.text((x0 + 40, yy), ln, font=font(SANS, body_size), fill=INK)
            yy += int(body_size * 1.32)
        yy += 14
    return yy


def still_B02():
    im = base("Two shaders, four questions", "")
    d = ImageDraw.Draw(im)
    tint = frame_png("tint", 330, WORK / "B02-tint.png")      # turn 3, the archer fully red (run-02 log)
    dio = frame_png("diorama", 160, WORK / "B02-dio.png")      # the two tiles, harness camera
    tw = 1640
    th = round(tw * 9 / 16)
    for k, (img, cap) in enumerate([(tint, "main.tscn · turn 3: the planned square is in reach (capture run-02 frame 330)"),
                                    (dio, "asset_diorama.tscn · the two linen tiles (capture run-02 frame 160)")]):
        x = SAFE[0] + k * (tw + 176)
        im.paste(img.resize((tw, th), Image.LANCZOS), (x, 330))
        d.rectangle((x - 4, 326, x + tw + 4, 330 + th + 4), outline=BORDER, width=6)
        d.text((x, 330 + th + 24), cap, font=font(SANS, 40), fill=SOFT)
    y = 330 + th + 120
    d.text((SAFE[0], y), "State: exposed", font=font(SANS_M, 58), fill=SPARK)
    d.text((SAFE[0], y + 80), "your planned square is inside the enemy archer's reach", font=font(SANS, 48), fill=INK)
    x2 = SAFE[0] + tw + 176
    d.text((x2, y), "Object: two 1 m linen tiles", font=font(SANS_M, 58), fill=SPARK)
    d.text((x2, y + 80), "one shader, two materials, in the A3 diorama", font=font(SANS, 48), fill=INK)
    y += 210
    qs = ["1  What does a shader do?", "2  How is a material different from a shader?",
          "3  Why is a texture information?", "4  What is the Godot shading language?"]
    for k, q in enumerate(qs):  # 1, 2 on the left; 3, 4 on the right
        d.text((SAFE[0] + (k // 2) * (tw + 176), y + (k % 2) * 78), q, font=font(SANS_M, 52), fill=INK)
    d.text((SAFE[0], y + 200), "Renderer: Compatibility (OpenGL 3.3), project.godot:25", font=font(MONO, 50), fill=INK)
    source_line(im, "CHANGE-BRIEF.md §1, §4 · real Godot frames from capture run-02 of the tag-a5 copy")
    return im


def still_B07():
    im = base("Predicted by hand, then captured", "JIEAN'S CAPTURES · capture() in a real window, key C · not a reconstruction")
    d = ImageDraw.Draw(im)
    cap = A5 / "evidence/a5/captures"
    vals = ["0.0", "0.5", "1.0", "2.0"]
    # archer region of the 1280 x 720 capture (player at the start square), enlarged x4 with nearest-neighbour
    crop = (132, 520, 262, 650)
    tw = 760
    for k, v in enumerate(vals):
        src = Image.open(cap / f"exposed_{v}.png").convert("RGB").crop(crop).resize((tw, tw), Image.NEAREST)
        x = SAFE[0] + k * (tw + 140)
        im.paste(src, (x, 400))
        d.rectangle((x - 4, 396, x + tw + 4, 400 + tw + 4), outline=SPARK if v == "2.0" else BORDER, width=6)
        sx = tw / (crop[2] - crop[0])
        for (px, py) in [(192, 581), (202, 634)]:
            cx, cy = x + (px - crop[0]) * sx, 400 + (py - crop[1]) * sx
            d.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), outline="#FFFFFF", width=6)
        d.text((x, 400 + tw + 24), f"exposed_amount = {v}", font=font(SANS_M, 50), fill=INK)
    rows = [("P1 head (192, 581)", ["224, 174, 117", "224, 137, 96", "224, 101, 76", "224, 27, 34"],
             ["224, 174, 117", "224, 137, 96", "224, 100, 75", "224, 27, 34"]),
            ("P2 base (202, 634)", ["90, 58, 34", "137, 62, 42", "184, 66, 51", "—"],
             ["90, 58, 34", "137, 62, 42", "184, 66, 50", "255, 73, 67"])]
    y = 400 + tw + 120
    for name, pred, meas in rows:
        d.text((SAFE[0], y), name, font=font(SANS_M, 46), fill=SOFT)
        for k in range(4):
            x = SAFE[0] + k * (tw + 140)
            d.text((x, y + 66), "predicted " + pred[k], font=font(MONO, 44), fill=INK)
            ok = pred[k] == meas[k]
            d.text((x, y + 126), "measured  " + meas[k], font=font(MONO, 44), fill=GOOD if ok else SPARK)
        y += 230
    d.text((SAFE[0], y + 10), "Within one step everywhere. At 2.0 nothing clamps: hint_range only shapes the Inspector "
           "slider. An OS screenshot at 0.0 read the same values.", font=font(SANS_M, 46), fill=INK)
    source_line(im, "evidence/a5/captures/exposed_*.png, exposed_pixels.md, os_compare.log · predictions: CHANGE-BRIEF.md §3, §6")
    return im


def still_B13():
    im = base("The hint experiment, measured", "REAL GODOT RENDER · hint_experiment.tscn @ tag a5 · 4K frame, bands read from it")
    d = ImageDraw.Draw(im)
    fr = frame_png("hint", 60, WORK / "B13-hint.png")
    # the frame itself, with the band values read from it at the same points the capture driver logged
    pts = {"A": int(H * 0.325), "B": int(H * 0.675)}
    xs = [W // 2 - 900, W // 2, W // 2 + 900]
    read = {q: [fr.getpixel((x, y))[0] for x in xs] for q, y in pts.items()}
    pw = 1900
    ph = round(pw * 9 / 16)
    im.paste(fr.resize((pw, ph), Image.LANCZOS), (SAFE[0], 410))
    d.rectangle((SAFE[0] - 4, 406, SAFE[0] + pw + 4, 410 + ph + 4), outline=BORDER, width=6)
    d.text((SAFE[0] + 40, 410 + int(ph * 0.12)), "A  source_color", font=font(SANS_M, 44), fill="#FFFFFF")
    d.text((SAFE[0] + 40, 410 + int(ph * 0.56)), "B  no hint", font=font(SANS_M, 44), fill="#FFFFFF")
    d.text((SAFE[0], 410 + ph + 24), "capture run-02, hint-4k.mkv frame 60 (orthographic scene camera)",
           font=font(SANS, 40), fill=SOFT)
    x0 = SAFE[0] + pw + 120
    cols = [x0, x0 + 260, x0 + 820]
    y = 430
    for c, t in zip(cols, ["band", "Quad A", "Quad B"]):
        d.text((c, y), t, font=font(SANS_M, 48), fill=INK)
    for c in cols[1:]:
        d.text((c, y + 62), "predicted / measured", font=font(SANS, 38), fill=SOFT)
    y += 140
    pred_b = [137, 188, 225]
    for k, v in enumerate([64, 128, 192]):
        d.line((x0, y - 12, SAFE[2], y - 12), fill=BORDER, width=4)
        d.text((cols[0], y), str(v), font=font(MONO, 60), fill=INK)
        d.text((cols[1], y), f"{v} / {read['A'][k]}", font=font(MONO, 60), fill=GOOD if read["A"][k] == v else SPARK)
        d.text((cols[2], y), f"{pred_b[k]} / {read['B'][k]}", font=font(MONO, 60), fill=SPARK)
        y += 110
    y += 40
    card(d, (x0, y, SAFE[2], y + 560), "Not a wiring slip",
         ["Switches swapped at run time: no change.", "Each quad given its own texture: no change.",
          "A constant ALBEDO 0.5 shows 128: no encode on the way out.",
          "So on Compatibility, here, neither decode nor encode happened."], accent=True, body_size=44)
    source_line(im, "evidence/a5/step3/hint_experiment_measurement.md, hint_control.log · prediction: CHANGE-BRIEF.md §3")
    return im


def still_B14():
    im = base("Generated beside hand-written", "ACTUAL SOURCE LINES · editor conversion of a StandardMaterial3D beside Jiean's shader")
    d = ImageDraw.Draw(im)
    gen = (A5 / "godot/shaders/standard_generated.gdshader").read_text(encoding="utf-8").split("\n")
    mine = (A5 / "godot/shaders/linen_square.gdshader").read_text(encoding="utf-8").split("\n")
    pairs = [(7, 4, "source_color", "source_color", "both: decode the photograph as sRGB colour"),
             (19, 11, "hint_roughness_normal", "hint_normal", "both: read it as tangent-space normal data, not colour")]
    y = 430
    fm = font(MONO, 48)
    for g, m, gh, mh, note in pairs:
        for k, (path, n, line, hint) in enumerate([("standard_generated.gdshader", g, gen[g - 1], gh),
                                                   ("linen_square.gdshader", m, mine[m - 1], mh)]):
            d.text((SAFE[0], y), f"{path}:{n}", font=font(SANS_M, 44), fill=SOFT)
            y += 66
            d.rounded_rectangle((SAFE[0], y, SAFE[2], y + 104), 16, fill="#F2EFE6", outline=BORDER, width=3)
            d.text((SAFE[0] + 32, y + 24), line, font=fm, fill=INK)
            i = line.find(hint)
            if i >= 0:
                x = SAFE[0] + 32 + d.textbbox((0, 0), line[:i], font=fm)[2]
                xe = SAFE[0] + 32 + d.textbbox((0, 0), line[:i + len(hint)], font=fm)[2]
                d.line((x, y + 88, xe, y + 88), fill=SPARK, width=8)
            y += 150
        d.text((SAFE[0], y - 20), note + (" · the hint differs" if gh != mh else ""), font=font(SANS_M, 48), fill=SPARK)
        y += 110
    d.text((SAFE[0], y + 10), "No main(), no #version, no in/out declarations: shader_type picks the pipeline and its "
           "built-ins (ALBEDO, NORMAL_MAP).", font=font(SANS_M, 46), fill=INK)
    source_line(im, "godot/shaders/standard_generated.gdshader (generated, saved by Jiean, ad54134) · linen_square.gdshader (Jiean, fb8d2bf)")
    return im


def still_B16():
    im = base("What the tests proved", "HEADLESS CHECK OUTPUT · recorded reports, no rendering")
    d = ImageDraw.Draw(im)
    rr = json.loads((REEL / "capture" / "film-rerun.json").read_text(encoding="utf-8"))
    cw = (SAFE[2] - SAFE[0] - 2 * 60) // 3
    y = 410
    runs = [("test_exposed_tint", "46/46", "at 30 · 60 · 144 fps", "every frame through real key presses"),
            ("test_materials", "148/148", "at 60 fps", "uniform lists, hints from source, import settings"),
            ("earlier suites", "51 · 70 · 38", "rules · audio · assets", "unchanged from the baseline")]
    for k, (t, score, sub, txt) in enumerate(runs):
        x = SAFE[0] + k * (cw + 60)
        d.rounded_rectangle((x, y, x + cw, y + 420), 22, fill=CARD, outline=BORDER, width=4)
        d.text((x + 40, y + 30), t, font=font(MONO, 52), fill=INK)
        d.text((x + 40, y + 100), score, font=font(SERIF, 130), fill=GOOD)
        d.text((x + 40, y + 270), sub, font=font(SANS_M, 44), fill=INK)
        d.text((x + 40, y + 336), txt, font=font(SANS, 40), fill=SOFT)
    y += 480
    muts = [("Mutation 1 · one ';' deleted", "exit 1", "SHADER ERROR: Expected a ';' · uniform list [] · 42/46"),
            ("Mutation 2 · uniform renamed", "exit 1", "uniform list shows exposed_amt · 42/46 · the 529-frame value "
                                                       "check still PASSED: no error for an unknown name"),
            ("Mutation 3 · source_color deleted", "exit 1", "no SHADER ERROR · the two hint checks fail · 146/148")]
    for k, (t, ex, txt) in enumerate(muts):
        x = SAFE[0] + k * (cw + 60)
        d.rounded_rectangle((x, y, x + cw, y + 520), 22, fill=CARD, outline=SPARK, width=5)
        d.text((x + 40, y + 30), t, font=font(SANS_M, 46), fill=INK)
        d.text((x + 40, y + 100), ex, font=font(SERIF, 120), fill=BAD)
        yy = y + 260
        for ln in wrap(d, txt, font(SANS, 42), cw - 80):
            d.text((x + 40, yy), ln, font=font(SANS, 42), fill=INK)
            yy += 56
    y += 580
    d.text((SAFE[0], y), "No headless run can show any pixel: colours, edges, the hint decode, the normal map's light, "
           "whether red reads as danger.", font=font(SANS_M, 48), fill=INK)
    for k, ln in enumerate(wrap(d, f"This film's rerun on the tag-a5 copy: {rr['summary']}", font(SANS, 42),
                                SAFE[2] - SAFE[0])):
        d.text((SAFE[0], y + 80 + k * 58), ln, font=font(SANS, 42), fill=SOFT)
    source_line(im, "TEST-REPORT.md A5.1, A5.2, A5.12 · evidence/a5/mutations/ · capture/film-rerun.json")
    return im


def still_BCRD():
    im = base("Who did what", "")
    d = ImageDraw.Draw(im)
    cols = [("Jiean Yin (human)", ["chose the state, the object and the cloth", "wrote the three shaders by hand",
                                   "wrote the colour line, computed every prediction", "approved the agent's plan",
                                   "ran the three mutations", "took the captures, ran the sweep, played it"]),
            ("Claude (AI)", ["claude -p agents: CLAUDE.md, the driver and its test, the material audit",
                             "Claude Code: reviewed each agent run, reran every suite",
                             "built the materials, tiles, hint scene, capture tool",
                             "caught: a wrong line number, two misnamed fps reports, an unmeasured audit figure"])]
    cw = (SAFE[2] - SAFE[0] - 80) // 2
    for i, (head, items) in enumerate(cols):
        x = SAFE[0] + i * (cw + 80)
        d.rounded_rectangle((x, 330, x + cw, 1660), 26, fill=CARD, outline=BORDER, width=4)
        d.text((x + 50, 370), head, font=font(SERIF, 96), fill=SPARK if i == 0 else INK)
        yy = 540
        for it in items:
            for j, ln in enumerate(wrap(d, it, font(SANS_M, 54), cw - 140)):
                d.text((x + 50, yy), ("· " if j == 0 else "  ") + ln, font=font(SANS_M, 54), fill=INK)
                yy += 74
            yy += 46
    d.text((SAFE[0], 1730), "Texture: Hessian 380, Poly Haven, CC0 (colormass, Rico Cilliers) · Source shown: tag a5 (ef5d38b) · Godot 4.7.2",
           font=font(SANS_M, 50), fill=INK)
    source_line(im, "SOURCES.md and TEST-REPORT.md A5.13 · godot/assets/textures/hessian_380/ATTRIBUTION.md")
    return im


STILLS = {"B02": still_B02, "B07": still_B07, "B13": still_B13, "B14": still_B14, "B16": still_B16, "BCRD": still_BCRD}


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
