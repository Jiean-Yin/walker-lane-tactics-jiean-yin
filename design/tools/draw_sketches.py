"""Design sketches for Lane Tactics (storyboard + character sheet).

Drawn by Claude Code as SVG under Jiean Yin's direction. These are DESIGN
specifications, not generated game art: they exist so generated images can be
judged against fixed proportions, palette and poses.

Run:  py -3.11 design/tools/draw_sketches.py   (from the repo root)
"""
from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAR = ROOT / "design" / "character"
BOARD = ROOT / "design" / "storyboard"

# ---- Palette (CHARACTER-SHEET.md) -------------------------------------------
INK = "#1B1410"      # outline, eye, bowstring
WOOD = "#E2B887"     # carved birch: head, hands
TEAL = "#1F6F78"     # player team paint (tunic)
HOOD = "#24323F"     # hood / cap paint
WALNUT = "#5A3A22"   # bow, belt, quiver, base disc
RED = "#B23A2E"      # enemy team paint (runtime recolor of TEAL)
LINEN = "#D8C7A0"    # board square
LINEN2 = "#CDB98E"   # alternate board square
TABLE = "#6B4A2E"    # table top around the board
PAPER = "#F4EFE4"    # sketch background
FX = True             # draw effect marks (impact star, sparkles, motion lines, ghost)

# On-screen geometry (viewport 1280x720): one square = 128 x 96 px,
# a unit is ~86 px tall at scale 1, its base disc 40 x 10 px.
SQ_W, SQ_H = 128, 96
UNIT_H = 86


def svg(w: int, h: int, body: str, bg: str = PAPER) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="Segoe UI, Arial, sans-serif">'
        f'<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'
    )


def text(x, y, s, size=12, anchor="start", fill=INK, weight="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{fill}" font-weight="{weight}">{s}</text>')


# ---- The archer --------------------------------------------------------------
POSES = {
    #            tilt  lift  sy    bow hand      back hand     extra
    "idle":      dict(tilt=0,   lift=0,  sy=1.0,  bow=(13, -30), back=(-8, -30)),
    "ready":     dict(tilt=4,   lift=0,  sy=1.0,  bow=(17, -44), back=(-6, -36)),
    "hop":       dict(tilt=6,   lift=16, sy=1.06, bow=(15, -40), back=(-12, -44)),
    "land":      dict(tilt=0,   lift=0,  sy=0.86, bow=(16, -26), back=(-14, -26)),
    "draw":      dict(tilt=-3,  lift=0,  sy=1.0,  bow=(24, -46), back=(-2, -46), string=True, arrow=True),
    "release":   dict(tilt=5,   lift=0,  sy=1.0,  bow=(25, -46), back=(-16, -54), lines=True),
    "hurt":      dict(tilt=-16, lift=0,  sy=1.0,  bow=(17, -24), back=(-14, -50), chip=True, eye="squint"),
    "defeat":    dict(tilt=-90, lift=0,  sy=1.0,  bow=(14, -30), back=(-8, -30), eye="x", dropped=True, dx=44),
    "celebrate": dict(tilt=0,   lift=5,  sy=1.0,  bow=(16, -84), back=(-16, -84), sparkle=True),
    "blocked":   dict(tilt=10,  lift=0,  sy=1.0,  bow=(18, -36), back=(-12, -40), ghost=True),
    "recover":   dict(tilt=-38, lift=0,  sy=1.0,  bow=(12, -20), back=(-18, -12), dx=22),
}


def limb(x1, y1, x2, y2, color, w=6):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" '
            f'stroke-width="{w + 3}" stroke-linecap="round"/>'
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{w}" stroke-linecap="round"/>')


def archer(x, y, s=1.0, team=TEAL, face=1, pose="idle", view="side", sil=False,
           show_ground=True):
    """Archer piece with its base-disc centre at (x, y)."""
    p = POSES[pose]
    c = (lambda col: INK) if sil else (lambda col: col)
    ink = INK
    parts = []
    # contact shadow stays on the ground even when the piece hops
    if show_ground and not sil and pose != "defeat":
        rx = 20 * (0.75 if p["lift"] > 8 else 1.0)
        parts.append(f'<ellipse cx="0" cy="0" rx="{rx}" ry="5" fill="#000" opacity="0.18"/>')
    if p.get("ghost") and not sil and FX:
        parts.append(f'<g transform="translate(40,0)" opacity="0.4">'
                     f'<ellipse cx="0" cy="-3" rx="20" ry="5" fill="none" stroke="{ink}" '
                     f'stroke-dasharray="4 3" stroke-width="2"/>'
                     f'<rect x="-11" y="-52" width="22" height="46" rx="8" fill="none" '
                     f'stroke="{ink}" stroke-dasharray="4 3" stroke-width="2"/>'
                     f'<circle cx="0" cy="-62" r="11" fill="none" stroke="{ink}" '
                     f'stroke-dasharray="4 3" stroke-width="2"/></g>')

    # pivot: the front-bottom edge for falls, the base centre otherwise
    pivot_x = -20 if p["tilt"] <= -60 else 0
    body = []
    # base disc
    body.append(f'<ellipse cx="0" cy="-4" rx="20" ry="6" fill="{c(WALNUT)}" '
                f'stroke="{ink}" stroke-width="2.5"/>')
    # quiver on the back
    if view in ("side", "threequarter"):
        qx = {"side": -17, "threequarter": -14}[view]
        body.append(f'<rect x="{qx}" y="-56" width="9" height="26" rx="2" fill="{c(WALNUT)}" '
                    f'stroke="{ink}" stroke-width="2" transform="rotate(-12 {qx + 4} -43)"/>')
        for i, fx in enumerate((qx - 2, qx + 2, qx + 6)):
            body.append(f'<line x1="{fx + 1}" y1="-57" x2="{fx - 2}" y2="-66" stroke="{ink}" '
                        f'stroke-width="2.4"/>')
    # back arm (behind body)
    bx, by = p["back"]
    if view == "side":
        body.append(limb(-2, -46, bx, by, c(WOOD)))
        body.append(f'<circle cx="{bx}" cy="{by}" r="3.6" fill="{c(WOOD)}" stroke="{ink}" stroke-width="2"/>')
    # body: carved cylinder painted in team colour, walnut belt
    body.append(f'<rect x="-12" y="-52" width="24" height="47" rx="9" fill="{c(team)}" '
                f'stroke="{ink}" stroke-width="2.5"/>')
    body.append(f'<rect x="-12" y="-30" width="24" height="5" fill="{c(WALNUT)}" '
                f'stroke="{ink}" stroke-width="1.5"/>')
    if p.get("chip") and not sil:
        body.append(f'<path d="M 9,-46 l 4,3 l -3,4 l 3,4" fill="none" stroke="{PAPER}" stroke-width="2.4"/>')
    if view == "back":
        body.append(f'<rect x="-5" y="-54" width="10" height="26" rx="2" fill="{c(WALNUT)}" stroke="{ink}" stroke-width="2"/>')
    # head + hood
    body.append(f'<circle cx="0" cy="-63" r="11.5" fill="{c(WOOD)}" stroke="{ink}" stroke-width="2.5"/>')
    if view == "side":
        hood = "M -12,-62 Q -13,-79 2,-78 Q 10,-77 9,-70 Q 0,-72 -4,-62 Z"
    elif view == "back":
        hood = "M -12,-60 Q -13,-79 0,-79 Q 13,-79 12,-60 Q 0,-55 -12,-60 Z"
    else:
        hood = "M -12,-62 Q -11,-79 0,-79 Q 11,-79 12,-62 Q 6,-73 -6,-73 Q -10,-70 -12,-62 Z"
    body.append(f'<path d="{hood}" fill="{c(HOOD)}" stroke="{ink}" stroke-width="2.2"/>')
    # eyes: one on the facing side (side), two (front), none (back)
    eye = p.get("eye")
    eyes = {"side": [6], "threequarter": [1, 7], "front": [-4, 4], "back": []}[view]
    if not sil:
        for ex in eyes:
            if eye == "x":
                body.append(f'<path d="M {ex - 2.5},-65.5 l 5,5 M {ex + 2.5},-65.5 l -5,5" '
                            f'stroke="{ink}" stroke-width="1.8"/>')
            elif eye == "squint":
                body.append(f'<path d="M {ex - 3},-64 l 3,-1.5 l 3,1.5" fill="none" stroke="{ink}" stroke-width="1.8"/>')
            else:
                body.append(f'<circle cx="{ex}" cy="-63" r="2" fill="{ink}"/>')
    # bow arm + bow (in front of body)
    hx, hy = p["bow"]
    if p.get("dropped"):
        hx, hy = 14, -30
    if view in ("front", "threequarter", "back"):
        hx, hy = (15, -30) if view != "back" else (-15, -30)
    body.append(limb(3, -46, hx, hy, c(WOOD)))
    bow_col = c(WALNUT)
    if not p.get("dropped"):
        up = pose == "celebrate"
        if up:   # bow held horizontally overhead
            bow = f"M -22,{hy + 2} Q 0,{hy - 12} 22,{hy + 2}"
            string = f"M -22,{hy + 2} L 22,{hy + 2}"
        else:
            bow = f"M {hx - 1},{hy - 18} Q {hx + 10},{hy} {hx - 1},{hy + 18}"
            if p.get("string"):
                string = f"M {hx - 1},{hy - 18} L {bx},{by} L {hx - 1},{hy + 18}"
            else:
                string = f"M {hx - 1},{hy - 18} L {hx - 1},{hy + 18}"
        body.append(f'<path d="{string}" fill="none" stroke="{ink}" stroke-width="1.2"/>')
        body.append(f'<path d="{bow}" fill="none" stroke="{ink}" stroke-width="5.5" stroke-linecap="round"/>')
        body.append(f'<path d="{bow}" fill="none" stroke="{bow_col}" stroke-width="3" stroke-linecap="round"/>')
        if p.get("arrow"):
            body.append(f'<line x1="{bx}" y1="{by}" x2="{hx + 12}" y2="{hy}" stroke="{ink}" stroke-width="2"/>')
            body.append(f'<path d="M {hx + 12},{hy} l -5,-3 l 0,6 z" fill="{ink}"/>')
    body.append(f'<circle cx="{hx}" cy="{hy}" r="3.6" fill="{c(WOOD)}" stroke="{ink}" stroke-width="2"/>')
    if view == "side" and pose == "celebrate":
        body.append(limb(-2, -46, bx, by, c(WOOD)))
        body.append(f'<circle cx="{bx}" cy="{by}" r="3.6" fill="{c(WOOD)}" stroke="{ink}" stroke-width="2"/>')

    tf = f"translate({p.get('dx', 0)},{-p['lift']}) translate({pivot_x},0) rotate({p['tilt']}) translate({-pivot_x},0) scale(1,{p['sy']})"
    parts.append(f'<g transform="{tf}">{"".join(body)}</g>')

    if p.get("dropped") and not sil:   # bow lying beside the toppled piece
        parts.append(f'<path d="M 30,-3 Q 48,-12 66,-3" fill="none" stroke="{INK}" stroke-width="5.5"/>'
                     f'<path d="M 30,-3 Q 48,-12 66,-3" fill="none" stroke="{WALNUT}" stroke-width="3"/>')
    if not sil and FX:
        if p.get("lines"):
            parts.append(''.join(f'<line x1="{36 + i * 4}" y1="{-52 + i * 6}" x2="{52 + i * 4}" y2="{-52 + i * 6}" '
                                 f'stroke="{INK}" stroke-width="1.5"/>' for i in range(3)))
        if pose == "land":
            parts.append(f'<path d="M -30,-2 l -8,-4 M 30,-2 l 8,-4 M -26,-8 l -6,-6 M 26,-8 l 6,-6" '
                         f'stroke="{INK}" stroke-width="1.5"/>')
        if pose == "hurt":
            parts.append(f'<path d="M 30,-50 l 6,-6 l 1,7 l 7,-2 l -5,6 l 6,3 l -7,1 l 1,7 l -5,-5 l -4,5 l -1,-7 l -7,1 l 5,-5 z" '
                         f'fill="#F2D24B" stroke="{INK}" stroke-width="1.5"/>')
        if p.get("sparkle"):
            parts.append(''.join(f'<path d="M {sx},{sy} l 2,-6 l 2,6 l 6,2 l -6,2 l -2,6 l -2,-6 l -6,-2 z" fill="#F2D24B" '
                                 f'stroke="{INK}" stroke-width="1"/>' for sx, sy in ((-30, -86), (26, -96), (34, -64))))
        if pose == "recover":
            parts.append(f'<path d="M -34,-40 q -8,10 0,22" fill="none" stroke="{INK}" stroke-width="1.8" '
                         f'marker-end="none"/><path d="M -34,-18 l -4,-5 l 6,0 z" fill="{INK}"/>')
    return f'<g transform="translate({x},{y}) scale({s * face},{s})">{"".join(parts)}</g>'


# ---- Character sheet images --------------------------------------------------
POSE_LABELS = [
    ("idle", "2 · idle", "planning, no order yet"),
    ("ready", "3 · ready / selected", "unit is selected for orders"),
    ("hop", "4 · hop (airborne)", "move playback, between squares"),
    ("land", "5 · landing", "arrives in new square (SFX-HOP)"),
    ("draw", "6 · draw (core action)", "attack wind-up, target chosen"),
    ("release", "7 · release (follow-through)", "arrow away, control returns"),
    ("hurt", "8 · hurt", "takes damage; leans away from attacker"),
    ("defeat", "9 · defeat", "health 0: piece topples"),
    ("celebrate", "10 · celebrate", "reached enemy back row: win"),
    ("blocked", "11 · blocked / waiting", "contested square: waits, ghost shows try"),
    ("recover", "12 · recover (retry)", "piece stands back up on retry"),
]


def turnaround():
    w, h = 900, 340
    b = [text(20, 30, "1 · Turnaround — front · three-quarter · side · back (shown at 2x)", 16, weight="bold")]
    ground = 270
    for i, (view, lab) in enumerate((("front", "front"), ("threequarter", "three-quarter"),
                                     ("side", "side (drawn facing right)"), ("back", "back"))):
        cx = 150 + i * 190
        b.append(archer(cx, ground, 2, view=view))
        b.append(text(cx, ground + 40, lab, 13, "middle"))
    # height bar
    top = ground - UNIT_H * 2 + 14
    b.append(f'<line x1="40" y1="{ground}" x2="860" y2="{ground}" stroke="{INK}" stroke-dasharray="6 4"/>')
    b.append(f'<line x1="40" y1="{top}" x2="860" y2="{top}" stroke="{INK}" stroke-dasharray="6 4" opacity="0.6"/>')
    b.append(f'<line x1="50" y1="{ground}" x2="50" y2="{top}" stroke="{INK}" stroke-width="3"/>')
    for k in range(0, 87, 10):
        yy = ground - k * 2
        b.append(f'<line x1="44" y1="{yy}" x2="56" y2="{yy}" stroke="{INK}"/>')
    b.append(text(60, top - 6, "height bar: 80 px on screen (head top), base disc 40 x 12 px", 12))
    b.append(text(20, h - 12, "Design sketch by Claude Code (SVG) under Jiean Yin's direction — not generated art.", 11, fill="#6b6257"))
    return svg(w, h, "".join(b))


def poses_sheet():
    cols, cw, rh = 4, 230, 255
    rows = math.ceil(len(POSE_LABELS) / cols)
    w, h = cols * cw + 20, rows * rh + 60
    b = [text(20, 30, "Poses 2–12 (pose 1 = turnaround) — drawn facing right, shown at 2x", 16, weight="bold")]
    for i, (pose, lab, state) in enumerate(POSE_LABELS):
        r, cc = divmod(i, cols)
        ox, oy = 20 + cc * cw, 50 + r * rh
        b.append(f'<rect x="{ox}" y="{oy}" width="{cw - 10}" height="{rh - 10}" fill="#fff" stroke="#c9bfae"/>')
        b.append(f'<line x1="{ox + 10}" y1="{oy + 200}" x2="{ox + cw - 20}" y2="{oy + 200}" stroke="#c9bfae"/>')
        b.append(archer(ox + cw / 2 - 5, oy + 200, 2 if pose != "defeat" else 1.6, pose=pose))
        b.append(text(ox + 8, oy + 222, lab, 13, weight="bold"))
        b.append(text(ox + 8, oy + 238, state, 11))
    b.append(text(20, h - 10, "Design sketch by Claude Code (SVG) under Jiean Yin's direction — not generated art.", 11, fill="#6b6257"))
    return svg(w, h, "".join(b))


def board_rect(x0, y0, cols, rows, sw, sh):
    out = []
    for r in range(rows):
        for cc in range(cols):
            col = LINEN if (r + cc) % 2 == 0 else LINEN2
            out.append(f'<rect x="{x0 + cc * sw}" y="{y0 + r * sh}" width="{sw}" height="{sh}" fill="{col}" '
                       f'stroke="#9c8a66" stroke-width="1"/>')
    return "".join(out)


def silhouette():
    # actual on-screen size: squares 128 x 96 px, unit scale 1
    w, h = 1000, 330
    b = [text(20, 28, "Silhouette test at actual on-screen size (1280x720 viewport, square = 128 x 96 px, unit scale 1)", 15, weight="bold")]
    b.append(f'<rect x="20" y="44" width="420" height="230" fill="{TABLE}"/>')
    b.append(board_rect(30, 60, 3, 2, SQ_W, SQ_H))
    b.append(archer(30 + 64, 60 + 88, 1, sil=True))
    b.append(archer(30 + 128 + 40, 60 + 96 + 88, 1, sil=True))
    b.append(archer(30 + 128 + 88, 60 + 96 + 88, 1, face=-1, sil=True))
    b.append(archer(30 + 256 + 64, 60 + 88, 1, pose="draw", sil=True))
    b.append(text(30, 296, "two units sharing one square sit in left/right slots", 11))
    x = 470
    for i, (pose, lab, _) in enumerate(POSE_LABELS):
        cx = x + (i % 6) * 85
        cy = 140 + (i // 6) * 130
        b.append(archer(cx, cy, 1, pose=pose, sil=True))
        b.append(text(cx, cy + 18, lab.split(" · ")[1].split(" ")[0], 10, "middle"))
    b.append(text(470, 316, "Pass if each state is still recognisable as a black shape at 1x.", 12))
    return svg(w, h, "".join(b))


def collision():
    cols, cw, rh = 4, 230, 250
    sel = ["idle", "hop", "draw", "release", "hurt", "defeat", "celebrate", "blocked"]
    rows = math.ceil(len(sel) / cols)
    w, h = cols * cw + 20, rows * rh + 110
    b = [text(20, 28, "Collision overlay at 2x — red: footprint slot (half square, 64 x 96 px on screen); "
               "blue: base disc 40 x 12 px", 14, weight="bold")]
    for i, pose in enumerate(sel):
        r, cc = divmod(i, cols)
        ox, oy = 20 + cc * cw, 44 + r * rh
        gx, gy = ox + cw / 2 - 5, oy + 205
        b.append(f'<rect x="{ox}" y="{oy}" width="{cw - 10}" height="{rh - 10}" fill="#fff" stroke="#c9bfae"/>')
        b.append(archer(gx, gy, 2, pose=pose))
        b.append(f'<rect x="{gx - 64}" y="{gy - 192 + 8}" width="128" height="192" fill="none" stroke="#C0392B" '
                 f'stroke-width="2.5" stroke-dasharray="7 4"/>')
        b.append(f'<ellipse cx="{gx}" cy="{gy - 8}" rx="40" ry="12" fill="none" stroke="#2E6FD0" stroke-width="2.5"/>')
        b.append(text(ox + 8, oy + 232, pose, 13, weight="bold"))
    b.append(text(20, h - 52, "Rules resolve per square, not per pixel: the slot is what can be targeted, clicked and blocked.", 12))
    b.append(text(20, h - 34, "Art beyond the slot (bow tip in draw/release, the toppled piece in defeat, hop lift) never changes a result.", 12))
    b.append(text(20, h - 12, "Design sketch by Claude Code (SVG) under Jiean Yin's direction — not generated art.", 11, fill="#6b6257"))
    return svg(w, h, "".join(b))


def lum(hexc):
    r, g, bb = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(bb)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def palette():
    sw = [(INK, "ink outline"), (WOOD, "birch wood"), (TEAL, "player team paint"),
          (HOOD, "hood paint"), (WALNUT, "walnut: bow, belt, base"), (RED, "enemy team paint (recolor)")]
    w, h = 980, 330
    b = [text(20, 28, "Palette — checked against the board (linen) and the table", 15, weight="bold")]
    for i, (col, lab) in enumerate(sw):
        x = 20 + i * 158
        b.append(f'<rect x="{x}" y="44" width="148" height="70" fill="{col}" stroke="{INK}"/>')
        b.append(text(x, 132, col, 13, weight="bold"))
        b.append(text(x, 148, lab, 11))
        b.append(text(x, 166, f"vs linen {contrast(col, LINEN):.1f}:1", 11))
        b.append(text(x, 182, f"vs table {contrast(col, TABLE):.1f}:1", 11))
    b.append(f'<rect x="20" y="200" width="300" height="110" fill="{TABLE}"/>')
    b.append(board_rect(40, 210, 2, 1, 128, 96))
    b.append(archer(40 + 64, 210 + 88, 1))
    b.append(archer(40 + 192, 210 + 88, 1, team=RED, face=-1))
    b.append(text(340, 230, f"Board squares: linen {LINEN} / {LINEN2}; table {TABLE}.", 12))
    b.append(text(340, 250, "Team paint is the largest area of the piece, so it carries team identity; the ink", 12))
    b.append(text(340, 266, "outline separates the piece from both the light board and the dark table.", 12))
    b.append(text(340, 286, "Team is ALSO shown without colour: player faces right, enemy faces left.", 12))
    return svg(w, h, "".join(b))


# ---- Storyboard panels (640 x 360, 16:9) --------------------------------------
PW, PH = 640, 360


def panel(body, label, bg="#EDE6D6"):
    tag = (f'<rect x="8" y="8" width="{len(label) * 6.6 + 16}" height="22" fill="{INK}" opacity="0.85"/>'
           + text(16, 23, label, 12, fill="#fff"))
    return svg(PW, PH, body + tag, bg)


def game_board(x0=64, y0=96, sw=64, sh=48, cols=8, rows=5):
    out = [f'<rect x="{x0 - 16}" y="{y0 - 16}" width="{cols * sw + 32}" height="{rows * sh + 32}" fill="{TABLE}"/>']
    out.append(board_rect(x0, y0, cols, rows, sw, sh))
    out.append(f'<rect x="{x0}" y="{y0}" width="{sw}" height="{rows * sh}" fill="{TEAL}" opacity="0.12"/>')
    out.append(f'<rect x="{x0 + (cols - 1) * sw}" y="{y0}" width="{sw}" height="{rows * sh}" fill="{RED}" opacity="0.12"/>')
    return "".join(out)


def sq(c, r, x0=64, y0=96, sw=64, sh=48):
    return x0 + c * sw + sw / 2, y0 + r * sh + sh - 4


def hud(turn="TURN 1 · PLAN MOVE", hp=4, extra=""):
    pips = "".join(f'<rect x="{470 + i * 16}" y="44" width="12" height="16" fill="{TEAL if i < hp else "#bbb"}" '
                   f'stroke="{INK}"/>' for i in range(4))
    return (f'<rect x="0" y="36" width="{PW}" height="32" fill="#2b2420" opacity="0.9"/>'
            + text(64, 57, turn, 13, fill="#fff", weight="bold") + text(420, 57, "HP", 12, fill="#fff") + pips
            + text(560, 57, extra, 12, fill="#fff"))


def arrow_path(x1, y1, x2, y2, col=INK, dash=""):
    ang = math.atan2(y2 - y1, x2 - x1)
    hx1, hy1 = x2 - 9 * math.cos(ang - 0.45), y2 - 9 * math.sin(ang - 0.45)
    hx2, hy2 = x2 - 9 * math.cos(ang + 0.45), y2 - 9 * math.sin(ang + 0.45)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="3"{d}/>'
            f'<path d="M {x2},{y2} L {hx1},{hy1} L {hx2},{hy2} z" fill="{col}"/>')


def storyboard():
    S = 0.5   # unit scale inside a 64x48 square
    panels = {}

    # P1 title — wide, eye level, design view
    b = [f'<rect x="0" y="230" width="{PW}" height="130" fill="{TABLE}"/>',
         f'<rect x="0" y="222" width="{PW}" height="10" fill="{LINEN}" stroke="#9c8a66"/>',
         f'<ellipse cx="320" cy="-40" rx="260" ry="200" fill="#F7E7B5" opacity="0.55"/>',
         text(320, 78, "LANE TACTICS", 40, "middle", weight="bold"), text(320, 106, "press Enter", 16, "middle")]
    for i, xx in enumerate((120, 200, 280)):
        b.append(archer(xx, 230, 1.2))
    for xx in (380, 460, 540):
        b.append(archer(xx, 230, 1.2, team=RED, face=-1))
    panels["01-title"] = panel("".join(b), "P1 · WIDE · EYE LEVEL · DESIGN VIEW (title)")

    # P2 board at start — wide, high angle, gameplay
    b = [game_board(), hud()]
    b.append(archer(*sq(0, 4), S))
    b.append(archer(*sq(7, 1), S, team=RED, face=-1))
    b.append(archer(*sq(7, 3), S, team=RED, face=-1))
    b.append(text(64, 352, "your back row (teal tint)", 11) + text(576, 352, "enemy back row (red tint)", 11, "end"))
    panels["02-board-start"] = panel("".join(b), "P2 · WIDE · HIGH ANGLE · GAMEPLAY (first thing in play)")

    # P3 core action: move — medium, high angle, gameplay (cropped board)
    x0, y0, sw, sh = 64, 60, 128, 88
    b = [game_board(x0, y0, sw, sh, 4, 3)]
    sel = (x0 + 1 * sw + sw / 2, y0 + 2 * sh + sh - 8)
    for dc in (-1, 0, 1):
        for dr in (-1, 0):
            if dc or dr:
                cx, cy = x0 + (1 + dc) * sw, y0 + (2 + dr) * sh
                b.append(f'<rect x="{cx + 4}" y="{cy + 4}" width="{sw - 8}" height="{sh - 8}" fill="none" '
                         f'stroke="#F2D24B" stroke-width="3" stroke-dasharray="8 5"/>')
    b.append(archer(*sel, 1.0, pose="ready"))
    b.append(arrow_path(sel[0] + 30, sel[1] - 40, sel[0] + sw - 10, sel[1] - sh - 20, "#F2D24B"))
    b.append(archer(sel[0] + sw, sel[1] - sh - 8, 1.0, pose="hop"))
    b.append(text(330, 350, "planned move (yellow) → hop playback → SFX-HOP on landing", 12, "middle"))
    panels["03-move"] = panel("".join(b), "P3 · MEDIUM · HIGH ANGLE · GAMEPLAY (core action: move)")

    # P4 success: shoot and hit — medium, high angle, gameplay
    b = [game_board(x0, y0, sw, sh, 4, 3)]
    a = (x0 + sw / 2 + 10, y0 + 2 * sh + sh - 8)
    e = (x0 + 2 * sw + sw / 2, y0 + 1 * sh + sh - 8)
    b.append(f'<rect x="{x0 + 2 * sw + 4}" y="{y0 + sh + 4}" width="{sw - 8}" height="{sh - 8}" fill="{RED}" '
             f'opacity="0.25" stroke="{RED}" stroke-width="3"/>')
    b.append(archer(*a, 1.0, pose="release"))
    b.append(f'<path d="M {a[0] + 60},{a[1] - 46} Q {(a[0] + e[0]) / 2 + 30},{e[1] - 150} {e[0] - 14},{e[1] - 50}" '
             f'fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    b.append(archer(*e, 1.0, team=RED, face=-1, pose="hurt"))
    b.append(text(e[0] + 40, e[1] - 70, "-3", 22, weight="bold", fill=RED))
    b.append(text(330, 350, "target square marked → arrow arcs → enemy hurt pose + SFX-HIT", 12, "middle"))
    panels["04-hit"] = panel("".join(b), "P4 · MEDIUM · HIGH ANGLE · GAMEPLAY (success: hit)")

    # P5 failure: archer is hit — close-up, low angle, design view
    b = [f'<rect x="0" y="0" width="{PW}" height="360" fill="#3a2c22"/>',
         f'<ellipse cx="420" cy="-20" rx="260" ry="160" fill="#F7E7B5" opacity="0.35"/>',
         f'<rect x="0" y="300" width="{PW}" height="60" fill="{LINEN}"/>']
    b.append(archer(450, 318, 3.7, team=RED, face=-1, pose="release"))
    b.append(archer(150, 372, 2.8, pose="hurt"))
    b.append(text(150, 60, "camera on the table surface, looking up:", 13, "middle", fill="#fff"))
    b.append(text(150, 78, "the enemy piece towers over you", 13, "middle", fill="#fff"))
    panels["05-hurt"] = panel("".join(b), "P5 · CLOSE-UP · LOW ANGLE · DESIGN VIEW (failure: hit)")

    # P6 defeat in play — medium, high angle, gameplay
    b = [game_board(), hud("TURN 5 · DEFEAT", 0)]
    b.append(archer(*sq(3, 3), S, pose="defeat"))
    b.append(archer(*sq(5, 3), S, team=RED, face=-1))
    b.append(f'<rect x="170" y="150" width="300" height="80" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>')
    b.append(text(320, 182, "DEFEATED — shot by the enemy archer in lane 4", 13, "middle", weight="bold"))
    b.append(text(320, 208, "R  retry      M  music      N  sound", 12, "middle"))
    panels["06-defeat"] = panel("".join(b), "P6 · WIDE · HIGH ANGLE · GAMEPLAY (failure: defeat)")

    # P7 retry / recover — medium, high angle, gameplay
    b = [game_board(), hud("TURN 1 · PLAN MOVE", 4, "retry #1")]
    p0 = sq(0, 4)
    b.append(archer(*p0, S * 1.6, pose="recover"))
    b.append(f'<ellipse cx="{p0[0]}" cy="{p0[1] - 2}" rx="30" ry="9" fill="none" stroke="#F2D24B" stroke-width="3"/>')
    b.append(archer(*sq(7, 1), S, team=RED, face=-1))
    b.append(archer(*sq(7, 3), S, team=RED, face=-1))
    b.append(text(320, 352, "pieces reset; your archer stands back up; music returns", 12, "middle"))
    panels["07-retry"] = panel("".join(b), "P7 · WIDE · HIGH ANGLE · GAMEPLAY (recovery / retry)")

    # P8 win — medium, Dutch angle, design view
    inner = [game_board(0, 96, 80, 60, 4, 3)]
    inner.append(archer(280, 96 + 2 * 60 + 56, 1.5, pose="celebrate"))
    inner.append(archer(120, 96 + 60 + 56, 1.0, team=RED, face=-1, pose="defeat"))
    b = [f'<g transform="translate(250,10) rotate(9 160 180)">{"".join(inner)}</g>',
         text(130, 120, "BACK ROW", 30, "middle", weight="bold"), text(130, 150, "REACHED", 30, "middle", weight="bold"),
         text(130, 190, "SFX-WIN · music stops", 13, "middle")]
    panels["08-win"] = panel("".join(b), "P8 · MEDIUM · DUTCH ANGLE · DESIGN VIEW (success: win)")

    # P9 end of session — close-up, eye level, gameplay UI
    b = [f'<rect x="120" y="60" width="400" height="250" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>',
         text(320, 110, "VICTORY", 34, "middle", weight="bold"),
         text(320, 150, "turns: 6     hits: 4     retries: 1", 15, "middle"),
         text(320, 200, "Enter  play again", 15, "middle"), text(320, 226, "Esc  quit", 15, "middle")]
    b.append(archer(470, 290, 0.8, pose="celebrate"))
    panels["09-results"] = panel("".join(b), "P9 · CLOSE-UP · EYE LEVEL · GAMEPLAY UI (end of session)")
    return panels


def main():
    CHAR.mkdir(parents=True, exist_ok=True)
    BOARD.mkdir(parents=True, exist_ok=True)
    (CHAR / "turnaround.svg").write_text(turnaround(), encoding="utf-8")
    (CHAR / "poses.svg").write_text(poses_sheet(), encoding="utf-8")
    (CHAR / "silhouette.svg").write_text(silhouette(), encoding="utf-8")
    (CHAR / "collision.svg").write_text(collision(), encoding="utf-8")
    (CHAR / "palette.svg").write_text(palette(), encoding="utf-8")
    for name, s in storyboard().items():
        (BOARD / f"{name}.svg").write_text(s, encoding="utf-8")
    for a, b in ((TEAL, LINEN), (RED, LINEN), (INK, TABLE), (TEAL, TABLE)):
        print(f"contrast {a} vs {b}: {contrast(a, b):.2f}")


if __name__ == "__main__":
    main()
