"""Build the 'own' media slots: student-footage beats, engine-capture beats and evidence stills (native 4K).

Every picture here is an actual file: the student's recordings and screenshot (FOOTAGE dir), frames of capture
run-02 (orbit-4k.mkv, lossless), or numbers read from the recorded JSON reports. Labels, insets and cards are ours.
Footage keeps its real timecodes: each segment is cut at [t0, t1) of the source, converted to 30 fps CFR by frame
repetition (the recordings are variable-frame-rate screen captures), never sped up or slowed. Footage audio is
dropped (narration only). Writes media/<beat>.mp4, stills/<beat>.png (previews) and capture/clips.json.

Usage (reel folder, Brutalist venv python): python tools/make_media.py [B04 B05 ...]
Env: FOOTAGE (default C:/dev/a3-footage), CAPTURE (default C:/dev/a3-capture), BRUTALIST (default C:/dev/brutalist.art)
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
FOOTAGE = Path(os.environ.get("FOOTAGE", "C:/dev/a3-footage"))
CAPTURE = Path(os.environ.get("CAPTURE", "C:/dev/a3-capture"))
FD = Path(os.environ.get("BRUTALIST", "C:/dev/brutalist.art")) / "runtime/fonts"
SERIF = str(FD / "EB_Garamond/static/EBGaramond-Medium.ttf")
SANS = str(FD / "Inter/static/Inter_28pt-Regular.ttf")
SANS_M = str(FD / "Inter/static/Inter_28pt-Medium.ttf")
MONO = str(FD / "PT_Mono/PTMono-Regular.ttf")
W, H, FPS = 3840, 2160, 30
SAFE = (192, 108, 3648, 2052)
PAGE, INK, SOFT, SPARK, CARD, BORDER, LABEL = "#FAF9F5", "#3D3929", "#73705F", "#D97757", "#FFFFFF", "#E5E2D9", "#303D34"
SRC = {"archer": FOOTAGE / "a3-blender-archer-build-2026-10-15.mp4", "flag": FOOTAGE / "a3-blender-flag-build.mp4",
       "orbit": CAPTURE / "run-02" / "orbit-4k.mkv", "shot": FOOTAGE / "Check 3 asset in Godot.png"}
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


def tc(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:04.1f}"


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


# ------------------------------------------------------------------ footage beats

FIT_ARCHER = (242, 300, 3356, 1752)  # x, y, w, h of the scaled 2560 x 1336 frame
INSETS = {  # source crop (x, y, w, h) at 2560 x 1336, zoom, placement in the 4K frame
    "mode": [((70, 41, 300, 32), 4.0, (330, 700))],
    "move": [((877, 83, 352, 28), 3.5, (330, 660)), ((1702, 224, 346, 29), 3.0, (330, 860))],
    "saved": [((1702, 563, 346, 109), 3.0, (330, 640)), ((1126, 1305, 282, 29), 3.0, (330, 1040))],
}
CROP_FLAG = (577, 40, 1420, 1300)  # conversation column only: no sidebar (account name), no side panel
FLAG_NOTES = {
    "prompt": ["0:04.5 – 0:11.7", "Jiean types the prompt", "\u201cApprove\u201d and sends it.",
               "", "Above it: Jiean's earlier question", "and Claude's reply.",
               "", "0:14 – 1:42: no visible change", "in the window (not shown)."],
    "reports": ["1:42.6 – 1:52.6", "Claude's step reports appear:", "base 44 tris · pole 28 · flag 12,",
                "0.45 × 0.30 × 1.20 m, 84 triangles,", "and an edge-on warning.",
                "", "Blender is not on screen", "anywhere in this recording."],
}


def page_png(label1, label2, out):
    im = Image.new("RGB", (W, H), PAGE)
    p = pill(label1, label2, 48, 44)
    im.paste(p, (SAFE[0], 116), p)
    im.save(out)


def footage_segment(bid, i, seg, label, out):
    src = SRC[seg["src"]]
    t0, t1 = seg["t0"], seg["t1"]
    n = round((t1 - t0) * FPS)
    l1, l2 = label.split("|")
    l2 = l2.replace("three excerpts, cuts marked", f"excerpt {i + 1}: {tc(t0)}–{tc(t1)}")
    if seg["src"] == "flag":
        l2 = l2 + f" · {tc(t0)}–{tc(t1)}"
    bg = WORK / f"{bid}-{i}-page.png"
    page_png(l1, l2, bg)
    inputs = ["-loop", "1", "-framerate", str(FPS), "-i", str(bg), "-ss", f"{t0:.3f}", "-t", f"{t1 - t0 + 0.5:.3f}",
              "-i", str(src)]
    fc = []
    if seg["src"] == "archer":
        x, y, w, h = FIT_ARCHER
        fc.append(f"[1:v]fps={FPS},scale={w}:{h}:flags=lanczos,setsar=1[f]")
        fc.append(f"[0:v][f]overlay={x}:{y}:shortest=0[b0]")
        last = "b0"
        k = 0
        for (cx, cy, cw, ch), z, (px, py) in INSETS.get(seg.get("inset", ""), []):
            k += 1
            zw, zh = int(cw * z), int(ch * z)
            fc.append(f"[1:v]fps={FPS},crop={cw}:{ch}:{cx}:{cy},scale={zw}:{zh}:flags=lanczos,"
                      f"pad={zw + 16}:{zh + 16}:8:8:color=0xD97757[z{k}]")
            fc.append(f"[{last}][z{k}]overlay={px}:{py}[b{k}]")
            last = f"b{k}"
        if k:
            tag = WORK / f"{bid}-{i}-zoomtag.png"
            pill("zoom of the same frame", "", 40, 40).save(tag)
            inputs += ["-i", str(tag)]
            fc.append(f"[{last}][2:v]overlay={INSETS[seg['inset']][0][2][0]}:{INSETS[seg['inset']][0][2][1] - 104}[bt]")
            last = "bt"
    else:
        x, y = SAFE[0], 300
        cx, cy, cw, ch = CROP_FLAG
        s = 1752 / ch
        w, h = int(cw * s), 1752
        fc.append(f"[1:v]fps={FPS},crop={cw}:{ch}:{cx}:{cy},scale={w}:{h}:flags=lanczos,setsar=1[f]")
        fc.append(f"[0:v][f]overlay={x}:{y}:shortest=0[b0]")
        notes = WORK / f"{bid}-{i}-notes.png"
        im = Image.new("RGBA", (SAFE[2] - (x + w + 72), 1752), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        yy = 40
        for j, ln in enumerate(FLAG_NOTES[seg["crop"]]):
            f = font(SANS_M, 60) if j == 0 else font(SANS, 52)
            d.text((0, yy), ln, font=f, fill=SPARK if j == 0 else INK)
            yy += 92 if ln else 50
        im.save(notes)
        inputs += ["-i", str(notes)]
        fc.append(f"[b0][2:v]overlay={x + w + 72}:{y}[b1]")
        last = "b1"
    fc.append(f"[{last}]format=yuv420p[v]")
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[v]",
         "-frames:v", n, "-r", FPS, "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "12", out])
    return n


def engine_segment(bid, i, seg, label, out):
    a, b = seg["a"], seg["b"]
    n = b - a
    l1, l2 = seg.get("label", label).split("|")
    lbl = WORK / f"{bid}-{i}-label.png"
    pill(l1, l2 + f" · capture run-02 frames {a}–{b}").save(lbl)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a / FPS:.6f}", "-i", SRC["orbit"], "-i", lbl, "-filter_complex",
         "[0:v][1:v]overlay=150:120:format=auto,format=yuv420p[v]", "-map", "[v]", "-frames:v", n, "-r", FPS,
         "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "10", out])
    return n


def video_beat(b, records):
    bid = b["beat_id"]
    parts = []
    total = 0
    for i, seg in enumerate(b["shot"]["segments"]):
        part = WORK / f"{bid}-part{i}.mp4"
        if seg["src"] == "orbit":
            n = engine_segment(bid, i, seg, b["shot"]["label"], part)
        else:
            n = footage_segment(bid, i, seg, b["shot"]["label"], part)
        parts.append(part)
        total += n
    assert total == b["clip_frames"], (bid, total, b["clip_frames"])
    out = REEL / "media" / f"{bid}.mp4"
    lst = WORK / f"{bid}-concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
    records[bid] = {"segments": b["shot"]["segments"], "n_frames": total, "duration_s": f"{total}/{FPS}",
                    "sources": {s["src"]: {"path": str(SRC[s["src"]]), "sha256": SRC_SHA[s["src"]]}
                                for s in b["shot"]["segments"]},
                    "label": b["shot"]["label"].replace("|", " / "), "path": f"media/{bid}.mp4", "sha256": sha(out)}
    print(bid, total, "frames", records[bid]["sha256"][:12])


# ------------------------------------------------------------------ stills

def base(title, label):
    im = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(im)
    d.text((SAFE[0], SAFE[1] - 6), title, font=font(SERIF, 118), fill=INK)
    if label:
        f = font(SANS_M, 48)
        tw = d.textbbox((0, 0), label, font=f)[2]
        d.rounded_rectangle((SAFE[0], 270, SAFE[0] + tw + 56, 352), 18, fill=LABEL)
        d.text((SAFE[0] + 28, 283), label, font=f, fill="#FFFDF8")
    d.text((SAFE[2], SAFE[3] - 4), "@NikBearBrown", font=font(SERIF, 60), fill=INK, anchor="rd")
    return im


def source_line(im, text):
    ImageDraw.Draw(im).text((SAFE[0], SAFE[3] - 4), text, font=font(SANS, 42), fill=SOFT, anchor="ld")


def still_B02():
    im = base("Three assets, three jobs", "JIEAN'S OWN SCREENSHOT · Godot editor, not a reconstruction")
    d = ImageDraw.Draw(im)
    shot = Image.open(SRC["shot"]).convert("RGB")
    w = 2330
    h = round(shot.height * w / shot.width)
    im.paste(shot.resize((w, h), Image.LANCZOS), (SAFE[0], 420))
    d.rectangle((SAFE[0] - 4, 416, SAFE[0] + w + 4, 420 + h + 4), outline=BORDER, width=6)
    x0 = SAFE[0] + w + 80
    cards = [("archer_piece", "the unit: the carved archer", "0.40 × 0.40 × 0.80 m · budget 400 tris"),
             ("board_square", "the tile the five-lane board is made of", "1.00 × 1.00 × 0.05 m · budget 100"),
             ("goal_flag", "marks the enemy back row you must reach", "0.45 × 0.30 × 1.20 m · budget 150")]
    y = 420
    for name, why, size in cards:
        d.rounded_rectangle((x0, y, SAFE[2], y + 330), 22, fill=CARD, outline=BORDER, width=4)
        d.text((x0 + 36, y + 30), name, font=font(MONO, 62), fill=SPARK)
        yy = y + 120
        for ln in wrap(d, why, font(SANS_M, 50), SAFE[2] - x0 - 72):
            d.text((x0 + 36, yy), ln, font=font(SANS_M, 50), fill=INK)
            yy += 64
        d.text((x0 + 36, y + 262), size, font=font(SANS, 44), fill=SOFT)
        y += 370
    d.text((SAFE[0], 420 + h + 50), "Brief, before any build: 1 board square = 1.00 m · origin at the base of every "
           "asset · one Godot 3D \u201ctabletop diorama\u201d", font=font(SANS_M, 50), fill=INK)
    source_line(im, "Check 3 asset in Godot.png (Jiean's screenshot) · CHANGE-BRIEF.md, Assignment 3 (78b213f)")
    return im


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


def still_B13():
    im = base("Brief vs Blender vs Godot", "HEADLESS CHECK OUTPUT · recorded JSON reports, no rendering")
    d = ImageDraw.Draw(im)
    ev = CAPTURE / "e415255" / "evidence"
    run2 = json.loads((ev / "check_assets-1792106192.json").read_text(encoding="utf-8"))
    run1 = json.loads((ev / "check_assets-1792106172.json").read_text(encoding="utf-8"))
    rerun = json.loads((REEL / "capture" / "check_assets-rerun.json").read_text(encoding="utf-8"))
    m = run2["measured"]
    brief = {"archer_piece": ("0.40 × 0.40 × 0.80", 400), "board_square": ("1.00 × 1.00 × 0.05", 100),
             "goal_flag": ("0.45 × 0.30 × 1.20", 150)}
    cols = [SAFE[0], 740, 1300, 1880, 2900]
    heads = ["asset", "brief W×D×H (m)", "Blender dims (m)", "Godot AABB X×Y×Z", "tris / budget · lowest y"]
    y = 410
    for c, t in zip(cols, heads):
        d.text((c, y), t, font=font(SANS_M, 44), fill=SOFT)
    y += 80
    for name in ("archer_piece", "board_square", "goal_flag"):
        s = m[name]["aabb_size"]
        d.line((SAFE[0], y - 14, SAFE[2], y - 14), fill=BORDER, width=4)
        d.text((cols[0], y), name, font=font(MONO, 54), fill=SPARK)
        d.text((cols[1], y), brief[name][0], font=font(MONO, 46), fill=INK)
        d.text((cols[2], y), brief[name][0], font=font(MONO, 46), fill=INK)
        d.text((cols[3], y), "%.4f × %.4f × %.4f" % tuple(s), font=font(MONO, 46), fill=INK)
        d.text((cols[4], y), "%d / %d · y %.4f" % (m[name]["triangles"], brief[name][1], m[name]["aabb_min"][1]),
               font=font(MONO, 54), fill=INK)
        d.text((cols[3], y + 70), "stands on %s · colours %s" % (m[name]["stands_along"], " ".join(m[name]["albedo_hex"])),
               font=font(SANS, 44), fill=SOFT)
        y += 170
    y += 20
    cards = [("Run 1 · kept", f"{run1['passed']}/{run1['total']}",
              "measured in _initialize(), outside the tree: identity transforms, no frustum. Its one FAIL (all three at x ≈ 0) exposed it.",
              "evidence/check_assets-1792106172.json"),
             ("Run 2 · after the fix", f"{run2['passed']}/{run2['total']}",
              "waits one frame; every measurement checks its node is in the tree; camera must have 6 planes.",
              "evidence/check_assets-1792106192.json"),
             ("Film rerun · isolated copy", f"{rerun['passed']}/{rerun['total']}",
              "same script, commit e415255, run for this film on a git-archive copy.",
              "capture/check_assets-rerun.json")]
    cw = (SAFE[2] - SAFE[0] - 2 * 50) // 3
    for i, (t, score, txt, path) in enumerate(cards):
        x = SAFE[0] + i * (cw + 50)
        d.rounded_rectangle((x, y, x + cw, y + 560), 22, fill=CARD, outline=SPARK if i == 0 else BORDER, width=5)
        d.text((x + 36, y + 28), t, font=font(SANS_M, 50), fill=INK)
        d.text((x + 36, y + 100), score, font=font(SERIF, 120), fill=SPARK if i == 0 else INK)
        yy = y + 250
        for ln in wrap(d, txt, font(SANS, 42), cw - 72):
            d.text((x + 36, yy), ln, font=font(SANS, 42), fill=INK)
            yy += 56
        d.text((x + 36, y + 496), path, font=font(MONO, 42), fill=SOFT)
    y += 600
    d.text((SAFE[0], y), "Does not show: rendering (headless = dummy renderer), how colours read under the lamp, "
           "whether shapes read at game size.", font=font(SANS_M, 44), fill=INK)
    source_line(im, "TEST-REPORT.md A3.3 (Blender dims read through the MCP) · godot/tests/check_assets.gd @ e415255")
    return im


def still_BCRD():
    im = base("Who did what", "")
    d = ImageDraw.Draw(im)
    cols = [("Jiean Yin (human)", ["chose the game", "approved every plan", "recorded the sessions",
                                   "made the hand edit (bow +0.08 m in Y)", "chose the border colour #9A7F55",
                                   "chose the headless export route"]),
            ("Claude (AI)", ["proposed every number in the brief", "wrote and ran all Blender code through the MCP",
                             "exported the three .glb files", "wrote the diorama scene",
                             "wrote and fixed the headless check"])]
    cw = (SAFE[2] - SAFE[0] - 80) // 2
    for i, (head, items) in enumerate(cols):
        x = SAFE[0] + i * (cw + 80)
        d.rounded_rectangle((x, 330, x + cw, 1640), 26, fill=CARD, outline=BORDER, width=4)
        d.text((x + 50, 380), head, font=font(SERIF, 96), fill=SPARK if i == 0 else INK)
        yy = 560
        for it in items:
            d.text((x + 50, yy), "· " + it, font=font(SANS_M, 60), fill=INK)
            yy += 160
    d.text((SAFE[0], 1730), "Source shown: commit e415255 (branch a3-blender-assets) · Blender 5.2.2 LTS · Godot 4.7.2",
           font=font(SANS_M, 56), fill=INK)
    source_line(im, "FRICTIONAL.md and CHANGE-BRIEF.md, Assignment 3 sections")
    return im


STILLS = {"B02": still_B02, "B13": still_B13, "BCRD": still_BCRD}


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
