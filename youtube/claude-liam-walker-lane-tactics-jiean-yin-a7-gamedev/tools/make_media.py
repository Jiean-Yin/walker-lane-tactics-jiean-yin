"""Build the 'own' media slots for the A7 film: engine-capture beats and evidence stills (native 4K).

Every picture is an actual file:
- frames of the capture masters (play-4k.mkv at 30 fps, slow-4k.mkv at 120 fps; lossless FFV1, real Godot renders of
  the tag-a7 copy). Segments are cut at exact frame indices; each source frame becomes one 30 fps output frame, so
  the play master keeps real speed and the slow master plays at 1/4 speed (labelled "¼ SPEED" on screen). Nothing
  else is retimed; capture audio is not used;
- the flag sheet as downloaded and Jiean's own strips in captures/ of the tag-a7 copy (fixture captures);
- text and numbers read from the tag-a7 copy's recorded logs and documents, and Jiean's words from
  capture/quotes.json (checked verbatim against the tag by tools/build_sheet.py).
Labels, cards and layout are ours. Writes media/<beat>.mp4, stills/<beat>.png (720p previews), capture/clips.json.
Adapted from the A6 film's tools/make_media.py.
Usage (reel folder, Brutalist venv python): python tools/make_media.py [B04 B06 ...]
Env (required): CAPTURE (<capture-copy>), BRUTALIST (<brutalist>); RUN (default "final-out")
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
A7 = CAPTURE / "a7"
RUN = CAPTURE / os.environ.get("RUN", "final-out")
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
MEASURED = "#C2613F"
SRC = {"play": RUN / "play-4k.mkv", "slow": RUN / "slow-4k.mkv"}
SRC_FPS = {"play": 30, "slow": 120}
ONLY = set(sys.argv[1:])
WORK = REEL / "_work"
Q = {k: v["text"] for k, v in json.loads((REEL / "capture/quotes.json").read_text(encoding="utf-8"))["quotes"].items()}


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


def wrap(d, text, f, width):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w_ in para.split(" "):
            t = (cur + " " + w_).strip()
            if d.textbbox((0, 0), t, font=f)[2] > width and cur:
                out.append(cur)
                cur = w_
            else:
                cur = t
        out.append(cur)
    return out


def text_block(d, xy, text, f, width, fill=INK, gap=1.32):
    x, y = xy
    for ln in wrap(d, text, f, width):
        d.text((x, y), ln, font=f, fill=fill)
        y += int(f.size * gap)
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
    fq, fa, fm = font(SERIF_I, 64), font(SANS_M, 40), font(MONO, 46)
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


def sheet_inset():
    """flag_red.png as downloaded (tag a7), 4 x 1 grid drawn over it, on a cream card with its caption."""
    sh = Image.open(A7 / "godot/assets/art/flag/flag_red.png").convert("RGBA")
    sc = 2.4
    w, h = int(sh.width * sc), int(sh.height * sc)
    img = sh.resize((w, h), Image.NEAREST)
    card_w, card_h = w + 80, h + 250
    im = Image.new("RGBA", (card_w, card_h), (250, 249, 245, 242))
    im.paste(img, (40, 40), img)
    d = ImageDraw.Draw(im)
    for c in range(5):
        x = 40 + int(c * w / 4)
        d.line((x, 40, x, 40 + h), fill=SPARK, width=6)
    d.rectangle((40, 40, 40 + w, 40 + h), outline=SPARK, width=6)
    for c in range(4):
        d.text((40 + int((c + 0.5) * w / 4), 40 + h + 20), f"frame {c}", font=font(SANS_M, 44), fill=INK, anchor="ma")
    d.text((40, 40 + h + 92), "flag_red.png as downloaded · 500 × 249", font=font(SANS, 34), fill=SOFT)
    d.text((40, 40 + h + 140), "hframes 4 × vframes 1 · grid drawn by us", font=font(SANS, 34), fill=SOFT)
    p = WORK / "inset-sheet.png"
    im.save(p)
    return p


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
    last, k = "v1", 2
    if seg.get("inset") == "sheet":
        inputs += ["-i", sheet_inset()]
        fc += f";[{last}][{k}:v]overlay=150:110:format=auto[v{k}]"
        last, k = f"v{k}", k + 1
    if seg.get("quote"):
        qc = quote_card(seg["quote"], seg.get("quote_width", 2600))
        qp = WORK / f"{bid}-{i}-quote.png"
        qc.save(qp)
        inputs += ["-i", qp]
        pos = seg.get("quote_pos")
        qx = W - 150 - qc.width if pos == "bottom-right" else (150 if pos == "bottom-left" else (W - qc.width) // 2)
        fc += f";[{last}][{k}:v]overlay={qx}:{H - 150 - qc.height}:format=auto[v{k}]"
        last, k = f"v{k}", k + 1
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


def log_line(path, pattern):
    for ln in (A7 / path).read_text(encoding="utf-8").splitlines():
        if re.search(pattern, ln):
            return ln.strip()
    raise SystemExit(f"{path}: no line matches {pattern!r}")


def mono_lines(d, xy, lines, width, size=44, fill=INK, gap=1.3):
    x, y = xy
    for ln in lines:
        y = text_block(d, (x, y), ln, font(MONO, size), width, fill=fill, gap=gap) + 18
    return y


def still_B02():
    im = base("One clip loops, one commits", "")
    d = ImageDraw.Draw(im)
    flag = frame_png("play", 300, WORK / "B02-flag.png").crop((2560, 880, 3840, 1600))
    shot = frame_png("play", 336, WORK / "B02-shot.png").crop((1280, 1080, 2560, 1800))
    tw, th = 1640, 922
    cards = [(flag, "wave · the cycle", "Job: where the goal is.",
              "Sprite2D with an AnimationPlayer frame track · flag_red.png sliced 4 × 1 · 8 fps · LOOP_LINEAR · "
              "\"Flag Animation Sheet\" by Fokko, CC0", "capture frame 300, cropped 3×"),
             (shot, "shoot · the committing action", "Job: who is shooting, and when.",
              "Cutout rig keyed as resource text · three parts cut from the draw art · 60 fps · LOOP_NONE",
              "capture frame 336, cropped 3×")]
    for k, (img, head, job, sub, cap) in enumerate(cards):
        x = SAFE[0] + k * (tw + 176)
        im.paste(img.resize((tw, th), Image.LANCZOS), (x, 330))
        d.rectangle((x - 4, 326, x + tw + 4, 330 + th + 4), outline=BORDER, width=6)
        d.text((x, 330 + th + 20), f"main.tscn @ tag a7 · {cap}", font=font(SANS, 38), fill=SOFT)
        y = 330 + th + 100
        d.text((x, y), head, font=font(SANS_M, 64), fill=SPARK)
        d.text((x, y + 92), job, font=font(SERIF_I, 64), fill=INK)
        text_block(d, (x, y + 190), sub, font(SANS, 46), tw)
    d.text((SAFE[0], 1850), "Startup 12 · active 21 · recovery 15 frames at 60 fps · Compatibility renderer · "
           "1280 × 720", font=font(MONO, 50), fill=INK)
    source_line(im, "CHANGE-BRIEF.md §1–§4 · real Godot frames from the film's capture of the tag-a7 copy")
    return im


def still_B06():
    im = base("The pole stands still", "FIXTURE CROPS · 13 frames of Jiean's r1 strip · guide line drawn on the strip")
    d = ImageDraw.Draw(im)
    st = Image.open(A7 / "captures/flag_registration_r1.png").convert("RGB")
    w = SAFE[2] - SAFE[0]
    h = round(w * st.height / st.width)
    im.paste(st.resize((w, h), Image.NEAREST), (SAFE[0], 440))
    y = 440 + h + 60
    d.text((SAFE[0], y), "strip frames 9, 10, 15, 16, 20, 25, 26, 29, 30, 31, 32, 33, 34 · the pole's darkest column: "
           "screen x 1176 in all 13", font=font(SANS_M, 50), fill=INK)
    y += 140
    d.text((SAFE[0], y), "Jiean, TEST-REPORT A7.11", font=font(SANS_M, 42), fill=SOFT)
    text_block(d, (SAFE[0], y + 60), "“" + Q["registration"] + "”", font(SERIF_I, 76), w)
    source_line(im, "captures/flag_registration_r1.png (tag a7), cropped from captures/shoot/r1 · offset track: "
                    "animations/wave.tres lines 29–36")
    return im


def still_B08():
    im = base("Breaking the flag clip on purpose", "HEADLESS CHECK OUTPUT · recorded reports, no rendering")
    d = ImageDraw.Draw(im)
    m3 = "evidence/a7/step6/mutations/m3_cell.log"
    m2 = "evidence/a7/step6/mutations/m2_loop.log"
    m3g = "evidence/a7/step6/mutations/m3_cell_guarded.log"
    cw = SAFE[2] - SAFE[0]
    y = 420
    y = card(d, (SAFE[0], y, SAFE[2], y + 520), "Mutation 3 · a frame key of 4, a cell the sheet does not have",
             []) + 10
    y = mono_lines(d, (SAFE[0] + 40, y), [log_line(m3, r"^FAIL .*inside the sheet"),
                                         log_line(m3g, r"^SUMMARY").split(" -> ")[0] + "  ·  exit 1 (after the guard)"],
                   cw - 80)
    y = 1000
    y = card(d, (SAFE[0], y, SAFE[2], y + 400), "Mutation 2 · loop_mode set to LOOP_NONE", []) + 10
    mono_lines(d, (SAFE[0] + 40, y), [log_line(m2, r"^FAIL .*loop_mode"),
                                     log_line(m2, r"^SUMMARY").split(" -> ")[0] + "  ·  exit 1"], cw - 80)
    d.text((SAFE[0], 1500), "In the game: a blank frame with no error · a flag that waves once and stops.",
           font=font(SANS_M, 56), fill=INK)
    d.text((SAFE[0], 1600), "First try of mutation 3: the test also stopped on an unguarded index (SCRIPT ERROR); "
           "guarded since (dc17389).", font=font(SANS, 46), fill=SOFT)
    source_line(im, "evidence/a7/step6/mutations/m2_loop.log, m3_cell.log, m3_cell_guarded.log · each run in a git "
                    "worktree, thrown away after")
    return im


def still_B09():
    im = base("Feel designed in frames", "The reference video is not shown: Jiean's frame numbers only")
    d = ImageDraw.Draw(im)
    x0, x1 = SAFE[0] + 40, SAFE[2] - 40
    span = x1 - x0
    y = 520
    d.text((SAFE[0], y - 90), "The game's shot at 60 fps (main.gd:29-33; CHANGE-BRIEF §4)", font=font(SANS_M, 50),
           fill=INK)
    phases = [(0, 12, "Startup · 12", "#E9D9C3"), (12, 33, "Active · 21", "#F3C9B3"), (33, 48, "Recovery · 15",
                                                                                         "#D9E3D5")]
    for a, b, name, col in phases:
        xa, xb = x0 + span * a / 48, x0 + span * b / 48
        d.rectangle((xa, y, xb, y + 200), fill=col, outline=INK, width=4)
        d.text(((xa + xb) / 2 if a != 33 else xa + 40, y + 50), name, font=font(SANS_M, 60), fill=INK,
               anchor="ma" if a != 33 else "la")
    for f, txt in [(0, "f0 · 0.0 s"), (12, "f12 · 0.2 s"), (33, "f33 · 0.55 s"), (40, "f40"), (48, "f48 · 0.8 s")]:
        x = x0 + span * f / 48
        d.line((x, y + (130 if f == 40 else -20), x, y + 230), fill=SPARK if f == 40 else INK,
               width=6 if f == 40 else 4)
        d.text((x, y + 250), txt, font=font(MONO, 44), fill=SPARK if f == 40 else INK,
               anchor="la" if f == 0 else ("ra" if f == 48 else "ma"))
    d.text((x0 + span * 40 / 48, y + 320), "bow drop: frame 40, chosen by eye", font=font(SANS_M, 46), fill=SPARK,
           anchor="ma")
    y = 1150
    d.text((SAFE[0], y), "Jiean's reference: World Archery slow-motion clip, 25 fps (proportions only)",
           font=font(SANS_M, 50), fill=INK)
    rows = [("draw", "f747 → f809", "62", "startup 0–12"),
            ("hold at full draw", "f809 → f1202", "393", "skipped: the game has no hold"),
            ("release, follow-through", "f1202 → f1275", "73", "active 12–33"),
            ("follow-through hold, bow drop", "f1275 → f1385", "110", "recovery 33–48")]
    cols = [SAFE[0], SAFE[0] + 1050, SAFE[0] + 1700, SAFE[0] + 2150]
    for i, h in enumerate(["stretch", "video frames", "gap", "game phase"]):
        d.text((cols[i], y + 110), h, font=font(SANS_M, 42), fill=SOFT)
    for r, row in enumerate(rows):
        yy = y + 190 + r * 92
        for i, cell in enumerate(row):
            d.text((cols[i], yy), cell, font=font(MONO if i in (1, 2) else SANS, 48),
                   fill=SOFT if "skipped" in row[3] else INK)
    source_line(im, "CHANGE-BRIEF.md §4 (Jiean's measurements; recovery split, chosen by eye) · revision 4")
    return im


def still_B17():
    im = base("A track that points at nothing", "HEADLESS CHECK OUTPUT · recorded reports, no rendering")
    d = ImageDraw.Draw(im)
    m1 = "evidence/a7/step6/mutations/m1_subname.log"
    m4 = "evidence/a7/step6/mutations/m4_cache.log"
    cw = SAFE[2] - SAFE[0]
    y = card(d, (SAFE[0], 420, SAFE[2], 1000), "Mutation 1 · Rig/Upper:rotation renamed Rig/Upper:rotaton, in the clip "
             "only", []) + 10
    mono_lines(d, (SAFE[0] + 40, y), [log_line(m1, r"^FAIL .*track_problems"),
                                     log_line(m1, r"^SUMMARY").split(" -> ")[0] + "  ·  exit 1"], cw - 80)
    y = card(d, (SAFE[0], 1060, SAFE[2], 1450), "Mutation 4 · delete godot/.godot, --import, run the rig read-back",
             []) + 10
    mono_lines(d, (SAFE[0] + 40, y), [log_line(m4, r"^SUMMARY").split(" -> ")[0] + "  ·  exit 0, as predicted"],
               cw - 80)
    d.text((SAFE[0], 1540), "In the game, mutation 1: the upper body would just stop leaning. No error, no warning.",
           font=font(SANS_M, 56), fill=INK)
    d.text((SAFE[0], 1640), "Mutation 4 passes for the right reason: the rig is keyed in text, so no import setting "
           "can be lost.", font=font(SANS, 46), fill=SOFT)
    source_line(im, "evidence/a7/step6/mutations/m1_subname.log, m4_cache.log · each run in a git worktree")
    return im


BOX = (175, 545, 245, 615)  # 70 x 70 around the player archer's bow hand in the shoot preview (1280 x 720)


def crop_strip(rev, fr, scale):
    p = A7 / "captures/shoot" / rev / f"frame{fr:08d}.png"
    return Image.open(p).convert("RGB").crop(BOX).resize(((BOX[2] - BOX[0]) * scale, (BOX[3] - BOX[1]) * scale),
                                                          Image.NEAREST)


def still_B19():
    im = base("The bow stays in the hand", "FIXTURE · shoot_preview.tscn · Jiean's Movie Maker captures, 30 fps")
    d = ImageDraw.Draw(im)
    frames = [15, 29, 31, 33]
    tile, gap, x0, y0 = 520, 24, SAFE[0] + 300, 450
    pix = {15: "0 px changed", 29: "0 px changed", 31: "410 px changed", 33: "456 px changed"}
    for c, fr in enumerate(frames):
        d.text((x0 + c * (tile + gap) + tile // 2, y0 - 14), f"frame {fr}", font=font(SANS_M, 42), fill=INK,
               anchor="md")
    for r, (rev, what) in enumerate([("r0", "bow drop 20°"), ("r1", "bow drop 8°")]):
        y = y0 + r * (tile + gap)
        d.text((SAFE[0], y + 150), rev, font=font(SERIF, 110), fill=SPARK if rev == "r1" else INK)
        d.text((SAFE[0], y + 300), what, font=font(SANS, 42), fill=SOFT)
        for c, fr in enumerate(frames):
            im.paste(crop_strip(rev, fr, 1).resize((tile, tile), Image.NEAREST), (x0 + c * (tile + gap), y))
    yy = y0 + 2 * (tile + gap) + 10
    for c, fr in enumerate(frames):
        d.text((x0 + c * (tile + gap) + tile // 2, yy), pix[fr], font=font(SANS_M, 40), fill=MEASURED, anchor="ma")
    xq = x0 + 4 * (tile + gap) + 40
    wq = SAFE[2] - xq
    y = y0
    d.text((xq, y), "Jiean, first look at r0", font=font(SANS_M, 40), fill=SOFT)
    y = text_block(d, (xq, y + 56), "“" + Q["r0"] + "”", font(SERIF_I, 54), wq) + 36
    d.text((xq, y), "Jiean, r1 in play", font=font(SANS_M, 40), fill=SOFT)
    y = text_block(d, (xq, y + 56), "“" + Q["r1"] + "”", font(SERIF_I, 54), wq) + 36
    d.text((xq, y), "Verdict", font=font(SANS_M, 40), fill=SOFT)
    text_block(d, (xq, y + 56), "“" + Q["r1_verdict"] + "”", font(SERIF_I, 54), wq)
    source_line(im, "captures/shoot/r0, r1 (70 × 70 px around the bow hand, 7.4×) · pixel counts: TUNING.md r1 · "
                    "Jiean's words: TUNING.md, verbatim")
    return im


def still_B21():
    im = base("Every boundary, every interrupt", "HEADLESS CHECK OUTPUT · recorded reports, no rendering")
    d = ImageDraw.Draw(im)
    edges = log_line("evidence/a7/step6/test_shoot_edges_60fps.log", r"^SUMMARY").split(" -> ")[0]
    pins0 = log_line("evidence/a7/pins/test_pins_a7_60fps.log", r"^SUMMARY").split(" -> ")[0]
    pins1 = log_line("evidence/a7/step6/test_pins_a7_60fps_repin.log", r"^SUMMARY").split(" -> ")[0]
    cw = SAFE[2] - SAFE[0]
    half = (cw - 80) // 2
    y = card(d, (SAFE[0], 420, SAFE[0] + half, 1180), "Recorded", []) + 10
    mono_lines(d, (SAFE[0] + 40, y), [edges, pins0 + "  (before the clips)", pins1 + "  (after)",
                                     "impact 32 / 34 · idle 47 / 49 game frames (table: 33, 48)"], half - 80, size=42)
    x2 = SAFE[0] + half + 80
    card(d, (x2, 420, SAFE[2], 1180), "Found on the way",
         ["One frame before the draw the game is still in PLAN_ATTACK: there, Enter is the attack order. The first "
          "version of the test assumed otherwise; the test was fixed, not the game.",
          "The game's cues land a frame early or late, so the end pose shows for 0 or 2 frames (brief revision 1)."],
         accent=True, body_size=44)
    card(d, (SAFE[0], 1260, SAFE[2], 1820), "What no headless run can show",
         ["Headless runs draw nothing: whether the motion reads, whether the seam is clean, and how the clips look "
          "against the art are Jiean's checks in the running game (TEST-REPORT A7.9–A7.12)."], body_size=46)
    source_line(im, "evidence/a7/step6/test_shoot_edges_60fps.log · evidence/a7/pins/ · evidence/a7/step6/ · "
                    "CHANGE-BRIEF revision 1")
    return im


def still_BCRD():
    im = base("Who did what", "")
    d = ImageDraw.Draw(im)
    cols = [("Jiean Yin (human)", ["chose both clips, the sheet and the reference; measured its frames",
                                   "wrote the phase table (bow drop at frame 40, by eye), the predictions and the "
                                   "seven answers",
                                   "approved each plan and the one tuning change",
                                   "captured every strip; judged every one; ran the human checks"]),
            ("Claude (AI)", ["claude -p agents: CLAUDE.md, both clips, both read-backs, the wiring",
                             "Claude Code: reviewed each run, wrote the pins, the edge tests and the preview, made "
                             "tuning r1",
                             "caught: a recovery split outside the clip, a missing capture folder, an author email in "
                             "a transcript (removed before any push)"])]
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
    d.text((SAFE[0], 1730), "Flag sheet: \"Flag Animation Sheet\" by Fokko, CC0 · Source shown: tag a7 · Godot 4.7.2",
           font=font(SANS_M, 50), fill=INK)
    source_line(im, "SOURCES.md Assignment 7 · FRICTIONAL.md Assignment 7 · TUNING.md")
    return im


STILLS = {"B02": still_B02, "B06": still_B06, "B08": still_B08, "B09": still_B09, "B17": still_B17, "B19": still_B19,
          "B21": still_B21, "BCRD": still_BCRD}


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
