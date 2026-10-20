"""Concept sketches for the GDD (GDD.md): cast, abilities, levels, game flow.

Drawn by Claude Code as SVG under Jiean Yin's direction. Like draw_sketches.py,
these are design sketches, not generated game art. Everything labelled
"proposed" (monster pieces, mountains, night, Mend, the boss) is not in
RULES.md until Jiean confirms it.

Run:  py -3.11 design/tools/draw_gdd_sketches.py   (from the repo root)
Then: bash design/tools/render_png.sh design/gdd
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_sketches import (HOOD, INK, LINEN, PAPER, RED, TABLE, TEAL, WALNUT, WOOD,  # noqa: E402
                           archer, arrow_path, board_rect, limb, svg, text)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "design" / "gdd"

GOBLIN = "#8E9A5B"    # painted goblin skin
FUR = "#6E6A66"       # painted wolf
GIANT = "#B79B74"     # giant's skin, darker stained wood
BONE = "#EFE6D2"      # horns, tusks
HILL = "#8C6F4E"      # carved wooden hill on a mountain square
HILL_TOP = "#B39470"
GOLD = "#F2D24B"      # selection, torch, Mend glow
GOLD_DARK = "#B8860B"  # proposed moves drawn on light squares
NIGHT = "#0E1424"
GREY = "#6b6257"
CREDIT = "Design sketch by Claude Code (SVG) under Jiean Yin's direction — not generated art."


# ---- Piece helpers (base-disc centre at the origin, facing right) ------------
def place(x, y, s, face, parts):
    return f'<g transform="translate({x},{y}) scale({s * face},{s})">{"".join(parts)}</g>'


def shadow(rx):
    return f'<ellipse cx="0" cy="0" rx="{rx}" ry="5" fill="#000" opacity="0.18"/>'


def disc(rx, ry=6):
    return f'<ellipse cx="0" cy="-4" rx="{rx}" ry="{ry}" fill="{WALNUT}" stroke="{INK}" stroke-width="2.5"/>'


def eye(x, y, col=INK, r=2.0):
    edge = f' stroke="{INK}" stroke-width="1"' if col != INK else ""
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"{edge}/>'


def pole(x1, y1, x2, y2):
    ang = math.atan2(y2 - y1, x2 - x1)
    tx, ty = x2 + 9 * math.cos(ang), y2 + 9 * math.sin(ang)
    l1 = (x2 + 4 * math.cos(ang + 1.6), y2 + 4 * math.sin(ang + 1.6))
    l2 = (x2 + 4 * math.cos(ang - 1.6), y2 + 4 * math.sin(ang - 1.6))
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{WALNUT}" stroke-width="2.6" stroke-linecap="round"/>'
            f'<path d="M {tx:.1f},{ty:.1f} L {l1[0]:.1f},{l1[1]:.1f} L {l2[0]:.1f},{l2[1]:.1f} Z" fill="#9AA3A8" '
            f'stroke="{INK}" stroke-width="1.5"/>')


def head(cx, cy, r, monster=False):
    """Ball head with a helmet (player) or a goblin's long ear and leather cap."""
    skin = GOBLIN if monster else WOOD
    out = []
    if monster:   # the long ear points back and up, behind the head
        out.append(f'<path d="M {cx - 3},{cy - 5} L {cx - r - 14},{cy - 15} L {cx - 6},{cy + 4} Z" fill="{skin}" '
                   f'stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{skin}" stroke="{INK}" stroke-width="2.5"/>')
    cap = WALNUT if monster else HOOD
    out.append(f'<path d="M {cx - r},{cy - 1} Q {cx - r},{cy - r - 6} {cx},{cy - r - 6} '
               f'Q {cx + r},{cy - r - 6} {cx + r},{cy - 1} Z" fill="{cap}" stroke="{INK}" stroke-width="2.2"/>')
    out.append(eye(cx + r * 0.5, cy + 1, GOLD if monster else INK, 2.2 if monster else 2.0))
    return "".join(out)


def rider(x, y, s=1.0, team=TEAL, face=1, monster=False):
    """Rider on a carved horse (player) or a goblin on a wolf (monster)."""
    mount = FUR if monster else WOOD
    p = [shadow(26), disc(26, 7),
         f'<rect x="-7" y="-20" width="14" height="14" fill="{WALNUT}" stroke="{INK}" stroke-width="2"/>']
    tail = "M -22,-32 q -12,4 -9,16"
    p.append(f'<path d="{tail}" fill="none" stroke="{INK}" stroke-width="5.5" stroke-linecap="round"/>')
    p.append(f'<path d="{tail}" fill="none" stroke="{mount}" stroke-width="2.5" stroke-linecap="round"/>')
    p.append(f'<ellipse cx="0" cy="-29" rx="24" ry="11" fill="{mount}" stroke="{INK}" stroke-width="2.5"/>')
    if monster:   # wolf: pointed ear, long snout, a fang
        p.append(f'<path d="M 12,-36 L 18,-52 L 21,-62 L 27,-53 L 30,-52 L 44,-45 L 30,-40 L 18,-24 Z" '
                 f'fill="{mount}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
        p.append(eye(28, -48, GOLD))
        p.append(f'<path d="M 35,-43 l 2,5 l 2,-4 z" fill="{BONE}" stroke="{INK}" stroke-width="1"/>')
    else:         # horse: a chess-knight head
        p.append(f'<path d="M 12,-36 L 20,-56 L 23,-63 L 27,-56 L 36,-50 L 34,-43 L 25,-43 L 19,-24 Z" '
                 f'fill="{mount}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
        p.append(eye(28, -52))
        p.append(f'<path d="M 15,-38 L 21,-55" stroke="{WALNUT}" stroke-width="3"/>')
    p.append(f'<rect x="-9" y="-60" width="18" height="30" rx="7" fill="{team}" stroke="{INK}" stroke-width="2.5"/>')
    p.append(f'<rect x="-9" y="-45" width="18" height="4" fill="{WALNUT}" stroke="{INK}" stroke-width="1.2"/>')
    p.append(head(0, -70, 9, monster))
    p.append(pole(-2, -46, 46, -64))
    p.append(limb(0, -52, 11, -50, GOBLIN if monster else WOOD, 5))
    return place(x, y, s, face, p)


def shielder(x, y, s=1.0, team=TEAL, face=1, monster=False):
    """Shielder (player) or goblin shielder (monster): the same piece with a goblin head."""
    p = [shadow(22), disc(22),
         f'<rect x="-13" y="-54" width="26" height="49" rx="9" fill="{team}" stroke="{INK}" stroke-width="2.5"/>',
         f'<rect x="-13" y="-31" width="26" height="5" fill="{WALNUT}" stroke="{INK}" stroke-width="1.5"/>',
         head(0, -66, 11.5, monster),
         # a round shield seen from the side: a tall ellipse in team paint, walnut rim and boss
         f'<ellipse cx="17" cy="-32" rx="10" ry="25" fill="{team}" stroke="{INK}" stroke-width="3"/>',
         f'<ellipse cx="17" cy="-32" rx="6" ry="20" fill="none" stroke="{WALNUT}" stroke-width="3"/>',
         f'<circle cx="18" cy="-32" r="4" fill="{WALNUT}" stroke="{INK}" stroke-width="1.5"/>']
    return place(x, y, s, face, p)


def giant_boss(x, y, s=1.0, team=RED, face=1):
    """The boss: a giant with a tower shield and a goblin archer riding on its back shoulder."""
    p = [shadow(30), disc(30, 8),
         f'<rect x="-19" y="-84" width="38" height="79" rx="13" fill="{team}" stroke="{INK}" stroke-width="2.8"/>',
         f'<rect x="-19" y="-48" width="38" height="6" fill="{WALNUT}" stroke="{INK}" stroke-width="1.5"/>',
         f'<path d="M -5,-105 q -6,-12 -17,-13 q 9,5 8,16 Z" fill="{BONE}" stroke="{INK}" stroke-width="1.8"/>',
         f'<path d="M 3,-107 q 2,-12 12,-16 q -5,7 -3,15 Z" fill="{BONE}" stroke="{INK}" stroke-width="1.8"/>',
         f'<circle cx="0" cy="-96" r="13" fill="{GIANT}" stroke="{INK}" stroke-width="2.5"/>',
         eye(7, -97, GOLD, 2.4),
         f'<path d="M 8,-89 l 3,-6 l 2,6 z" fill="{BONE}" stroke="{INK}" stroke-width="1"/>',
         limb(4, -70, 18, -58, GIANT, 7),
         # tower shield: walnut planks with iron studs
         f'<rect x="16" y="-92" width="16" height="86" rx="3" fill="{WALNUT}" stroke="{INK}" stroke-width="3"/>']
    for yy in (-71, -49, -27):
        p.append(f'<line x1="16" y1="{yy}" x2="32" y2="{yy}" stroke="{INK}" stroke-width="1.5"/>')
        p.append(f'<circle cx="24" cy="{yy + 10}" r="2" fill="#9AA3A8" stroke="{INK}" stroke-width="1"/>')
    rider_s = 0.62   # the shoulder goblin, relative to the giant
    return place(x, y, s, face, p) + goblin_archer(x - 17 * s * face, y - 82 * s, s * rider_s, face)


def goblin_archer(x, y, s=1.0, face=-1):
    """The archer piece in red paint with a goblin head: long ear, leather cap, yellow eye."""
    over = [f'<path d="M -6,-68 L -28,-81 L -9,-57 Z" fill="{GOBLIN}" stroke="{INK}" stroke-width="2" '
            f'stroke-linejoin="round"/>',
            f'<circle cx="0" cy="-63" r="11.5" fill="{GOBLIN}" stroke="{INK}" stroke-width="2.5"/>',
            f'<path d="M -12,-62 Q -13,-79 2,-78 Q 10,-77 9,-70 Q 0,-72 -4,-62 Z" fill="{WALNUT}" '
            f'stroke="{INK}" stroke-width="2.2"/>',
            eye(6, -63, GOLD, 2.2)]
    return archer(x, y, s, team=RED, face=face) + place(x, y, s, face, over)


# ---- Diagram helpers -----------------------------------------------------------
def token(cx, cy, letter, team, r=10, opacity=1.0):
    return (f'<g opacity="{opacity}"><circle cx="{cx}" cy="{cy}" r="{r}" fill="{team}" stroke="{INK}" stroke-width="2"/>'
            + text(cx, cy + 4.5, letter, 12, "middle", fill="#fff", weight="bold") + '</g>')


def cell(x0, y0, cw, ch, c, r):
    """Centre of square (c, r)."""
    return x0 + c * cw + cw / 2, y0 + r * ch + ch / 2


def mark(x0, y0, cw, ch, c, r, fill=RED, opacity=0.3, stroke=None, dash=""):
    st = f' stroke="{stroke}" stroke-width="2.5"' if stroke else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x0 + c * cw + 2}" y="{y0 + r * ch + 2}" width="{cw - 4}" height="{ch - 4}" '
            f'fill="{fill}" fill-opacity="{opacity}"{st}{d}/>')


def hill(x0, y0, cw, ch, c, r):
    x, y = x0 + c * cw, y0 + r * ch
    return (f'<path d="M {x + 3},{y + ch - 2} Q {x + cw * 0.25},{y + 3} {x + cw / 2},{y + 3} '
            f'Q {x + cw * 0.75},{y + 3} {x + cw - 3},{y + ch - 2} Z" fill="{HILL}" stroke="{INK}" stroke-width="1.5"/>'
            f'<path d="M {x + cw * 0.3},{y + ch * 0.4} Q {x + cw / 2},{y + ch * 0.2} {x + cw * 0.7},{y + ch * 0.4}" '
            f'fill="none" stroke="{HILL_TOP}" stroke-width="2"/>')


def tabled_board(x0, y0, cols, rows, cw, ch, back_rows=True):
    out = [f'<rect x="{x0 - 8}" y="{y0 - 8}" width="{cols * cw + 16}" height="{rows * ch + 16}" fill="{TABLE}"/>',
           board_rect(x0, y0, cols, rows, cw, ch)]
    if back_rows:
        out.append(f'<rect x="{x0}" y="{y0}" width="{cw}" height="{rows * ch}" fill="{TEAL}" opacity="0.15"/>')
        out.append(f'<rect x="{x0 + (cols - 1) * cw}" y="{y0}" width="{cw}" height="{rows * ch}" fill="{RED}" '
                   f'opacity="0.15"/>')
    return "".join(out)


def card(x, y, w, h, title):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#c9bfae"/>'
            + text(x + 12, y + 22, title, 14, weight="bold"))


def lines(x, y, rows, size=11, gap=15, fill=INK):
    return "".join(text(x, y + i * gap, row, size, fill=fill) for i, row in enumerate(rows))


def tag(x, y, label, col):
    w = len(label) * 6.2 + 12
    return (f'<rect x="{x}" y="{y - 12}" width="{w}" height="16" rx="3" fill="{col}"/>'
            + text(x + 6, y, label, 10, fill="#fff", weight="bold"))


# ---- 1. Cast ---------------------------------------------------------------------
def cast():
    w, h = 1000, 730
    b = [text(20, 30, "Cast — the unit pieces (2x) and the boss (1.5x), side view as the game camera sees them", 16, weight="bold")]
    cols = (130, 370, 610, 860)
    rows = (
        ("Player army — carved wooden pieces, teal paint, face right", 250, [
            (archer(cols[0], 250, 2), "Archer", "1 step · shoots within 2 · HP 4", "built (A2 slice)", TEAL),
            (rider(cols[1], 250, 2), "Rider", "2 steps, first one early · charge · HP 6", "agreed rules, no art", GREY),
            (shielder(cols[2], 250, 2), "Shielder", "1 step · guards its squaremate · HP 10", "agreed rules, no art", GREY),
        ]),
        ("Goblin army — carved wooden goblins, red paint, face left (agreed 2026-10-19)", 600, [
            (goblin_archer(cols[0], 600, 2), "Goblin archer", "plays as an archer", "agreed, no art", RED),
            (rider(cols[1], 600, 2, team=RED, face=-1, monster=True), "Wolf rider", "a goblin on a wolf; plays as a rider",
             "agreed, no art", RED),
            (shielder(cols[2], 600, 2, team=RED, face=-1, monster=True), "Goblin shielder", "plays as a shielder",
             "agreed, no art", RED),
            (giant_boss(cols[3], 600, 1.5, face=-1), "Giant (boss)", "shield + a goblin archer on its shoulder",
             "numbers later", GREY),
        ]),
    )
    for title, ground, units in rows:
        b.append(text(20, ground - 190, title, 13, weight="bold", fill=GREY))
        b.append(f'<line x1="40" y1="{ground}" x2="960" y2="{ground}" stroke="#c9bfae"/>')
        for i, (g, name, role, status, col) in enumerate(units):
            cx = cols[i]
            b.append(g)
            b.append(text(cx, ground + 26, name, 14, "middle", weight="bold"))
            b.append(text(cx, ground + 43, role, 11, "middle"))
            b.append(tag(cx - len(status) * 3.1 - 6, ground + 62, status, col))
    b.append(lines(cols[3] - 90, 120, ["The boss arrives as an enemy", "reinforcement on a later turn,",
                                       "walks 1 square a turn and pushes", "whatever is in front of it;",
                                       "its shoulder goblin dies with it."], 11, 15, GREY))
    b.append(text(20, h - 28, "All three enemy types share one goblin head, so one goblin reference image can carry across them. "
                              "Type is read from the weapon or mount.", 11))
    b.append(text(20, h - 10, CREDIT, 11, fill=GREY))
    return svg(w, h, "".join(b))


# ---- 2. Abilities ----------------------------------------------------------------
def abilities():
    w, h = 1000, 640
    b = [text(20, 30, "Abilities — agreed unit rules (red) and the 2026-10-19 additions (gold)", 16, weight="bold")]

    # A. Archer range
    x, y = 20, 46
    b.append(card(x, y, 470, 280, "Archer range"))
    gx, gy, cw, ch = x + 16, y + 40, 28, 28
    b.append(board_rect(gx, gy, 7, 7, cw, ch))
    for c in range(7):
        for r in range(7):
            d = max(abs(c - 3), abs(r - 3))
            if d in (1, 2):
                b.append(mark(gx, gy, cw, ch, c, r))
            elif d == 3:
                b.append(mark(gx, gy, cw, ch, c, r, fill=GOLD, opacity=0.18, stroke=GOLD, dash="4 3"))
    b.append(hill(gx, gy, cw, ch, 3, 3))
    b.append(token(*cell(gx, gy, cw, ch, 3, 3), "A", TEAL))
    b.append(lines(x + 230, y + 56, [
        "Agreed: any of the 24 squares within",
        "two steps (red); never its own square.",
        "",
        "Added: on a mountain, one more",
        "ring (gold): 48 squares.",
        "",
        "The board is 5 lanes tall, so from the",
        "middle lane the extra ring only adds",
        "reach along the lanes: 7 columns of 8.",
    ]))

    # B. Rider charge
    x, y = 510, 46
    b.append(card(x, y, 470, 280, "Rider charge"))
    cw, ch = 24, 24
    for k, (gx, steps, label, bonus) in enumerate(((x + 16, 2, "agreed: 2 steps", "+2"),
                                                    (x + 246, 3, "added: from a mountain", "+3"))):
        gy = y + 50
        b.append(board_rect(gx, gy, 8, 5, cw, ch))
        if k == 1:
            b.append(hill(gx, gy, cw, ch, 1, 2))
        end = 1 + steps
        for r in (1, 2, 3):
            b.append(mark(gx, gy, cw, ch, end + 1, r))
        for st in range(steps):
            x1, y1 = cell(gx, gy, cw, ch, 1 + st, 2)
            x2, y2 = cell(gx, gy, cw, ch, 2 + st, 2)
            col = GOLD_DARK if k == 1 and st == 0 else INK
            b.append(arrow_path(x1 + 6, y1, x2 - 6, y2, col))
        b.append(token(*cell(gx, gy, cw, ch, end, 2), "R", TEAL, 9))
        b.append(text(gx, gy + 5 * ch + 18, label, 11, weight="bold"))
        b.append(text(gx, gy + 5 * ch + 34, f"red squares: charge {bonus} damage", 11))
    b.append(lines(x + 16, y + 226, [
        "Agreed: two steps in the same direction give +2 on the 3 squares ahead.",
        "Added: starting on a mountain adds one step to the first move (gold)",
        "and raises the bonus to +3 (placeholder). Entering a mountain ends a move.",
    ]))

    # C. Shielder protection
    x, y = 20, 340
    b.append(card(x, y, 470, 280, "Shielder protection"))
    gx, gy, cw, ch = x + 20, y + 44, 80, 56
    b.append(board_rect(gx, gy, 5, 2, cw, ch))
    b.append(hill(gx, gy, cw, ch, 0, 1))
    sx, sy = cell(gx, gy, cw, ch, 0, 1)
    b.append(token(sx - 16, sy + 4, "S", TEAL))
    b.append(token(sx + 16, sy + 4, "A", TEAL))
    ex, ey = cell(gx, gy, cw, ch, 2, 0)
    b.append(token(ex, ey, "A", RED))
    b.append(f'<path d="M {ex - 12},{ey - 4} Q {(ex + sx) / 2},{ey - 40} {sx + 22},{sy - 14}" fill="none" '
             f'stroke="{INK}" stroke-width="2" stroke-dasharray="5 4"/>')
    b.append(lines(x + 16, y + 180, [
        "An arrow into the square does half (round down) to the shielder: 3 becomes 1.",
        "Its squaremate takes 0, or half once the shielder is at or below half health.",
        "Added: on a mountain the shielder takes 1 less from every hit, and every",
        "hit deals at least 1 damage, so the shielder is never immune.",
        "(The squaremate's 0 is a block, not a hit.)",
    ]))

    # D. Mend
    x, y = 510, 340
    b.append(card(x, y, 470, 280, "Mend — the player's one commander ability"))
    frames = (("turn N, planning", "pick one hurt unit", 1, "pick"),
              ("end of turn N", "it glows as a reminder", 1, "glow"),
              ("turn N+1, after combat", "+3 HP if it survived", 4, "heal"))
    for i, (when, what, hp, state) in enumerate(frames):
        fx, fy = x + 20 + i * 150, y + 46
        b.append(f'<rect x="{fx}" y="{fy}" width="120" height="84" fill="{LINEN}" stroke="#9c8a66"/>')
        tx, ty = fx + 60, fy + 42
        if state != "pick":
            b.append(f'<circle cx="{tx}" cy="{ty}" r="20" fill="{GOLD}" opacity="0.45"/>')
        b.append(f'<circle cx="{tx}" cy="{ty}" r="16" fill="none" stroke="{GOLD}" stroke-width="3" '
                 f'stroke-dasharray="{"5 3" if state == "pick" else "0"}"/>')
        b.append(token(tx, ty, "A", TEAL, 11))
        if state == "heal":
            b.append(text(tx + 22, ty - 14, "+3", 15, weight="bold", fill="#3c8a3c"))
        for k in range(4):
            col = TEAL if k < hp else "#bbb"
            b.append(f'<rect x="{fx + 32 + k * 14}" y="{fy + 92}" width="10" height="12" fill="{col}" stroke="{INK}"/>')
        b.append(text(fx, fy + 124, when, 11, weight="bold"))
        b.append(text(fx, fy + 139, what, 10))
        if i < 2:
            b.append(arrow_path(fx + 124, fy + 42, fx + 146, fy + 42))
    b.append(lines(x + 16, y + 214, [
        "Only the player has Mend. The AI never uses it and ignores the glow, so",
        "the delay means the unit must survive one more turn of combat first.",
        "2 uses per level; +3 is a placeholder.",
    ]))
    b.append(text(20, h - 8, CREDIT, 11, fill=GREY))
    return svg(w, h, "".join(b))


# ---- 3. Levels ---------------------------------------------------------------------
def levels():
    w, h = 1000, 640
    b = [text(20, 30, "Levels — four episodes, each adds one idea (2026-10-19)", 16, weight="bold")]
    cw, ch, cols, rows = 34, 24, 8, 5

    def episode(x, y, title, body_rows):
        b.append(card(x, y, 470, 280, title))
        b.append(lines(x + 14, y + 196, body_rows))
        return x + 16, y + 44

    # Episode 1
    gx, gy = episode(20, 46, "Episode 1 · Open Field (day)", [
        "1-1 First Shot: your archer vs one goblin archer (the built slice).",
        "1-2 Wolves: riders and wolf riders join.",
        "1-3 Shield Wall: shielders and goblin shielders join; first full army draft.",
        "Teaches the three counters one at a time.",
    ])
    b.append(tabled_board(gx, gy, cols, rows, cw, ch))
    for (c, r, L) in ((0, 1, "R"), (0, 2, "A"), (1, 3, "S")):
        b.append(token(*cell(gx, gy, cw, ch, c, r), L, TEAL, 9))
    for (c, r, L) in ((7, 3, "R"), (7, 2, "A"), (6, 1, "S")):
        b.append(token(*cell(gx, gy, cw, ch, c, r), L, RED, 9))

    # Episode 2
    gx, gy = episode(510, 46, "Episode 2 · The Hills", [
        "Mountain squares: archers shoot one ring further, riders get one more",
        "first step and a +3 charge, shielders take 1 less per hit (never below 1),",
        "and pieces on a hill see further at night. Entering a hill ends a move.",
        "Placed in mirror pairs. 2-1 One Hill · 2-2 Twin Peaks",
    ])
    b.append(tabled_board(gx, gy, cols, rows, cw, ch))
    for (c, r) in ((3, 1), (4, 3), (1, 4), (6, 0)):
        b.append(hill(gx, gy, cw, ch, c, r))
    b.append(token(*cell(gx, gy, cw, ch, 3, 1), "A", TEAL, 9))
    b.append(token(*cell(gx, gy, cw, ch, 0, 3), "S", TEAL, 9))
    b.append(token(*cell(gx, gy, cw, ch, 4, 3), "A", RED, 9))
    b.append(token(*cell(gx, gy, cw, ch, 7, 1), "R", RED, 9))

    # Episode 3 (night): mist over every square your pieces have never been near
    gx, gy = episode(20, 334, "Episode 3 · Night Raid", [
        "Mist: a square stays dark until one of your pieces has been near it.",
        "Enemies sleep or walk a fixed patrol until alarmed. Red squares show",
        "where an enemy would notice you, even while it is hidden in the mist.",
        "3-1 Sleeping Camp · 3-2 Patrols and Hills (night + mountains)",
    ])
    visited = [(0, 3), (1, 3), (2, 3), (0, 1), (1, 1)]   # squares your pieces have stood on
    hills = [(2, 3), (6, 3)]
    seen = set()
    for (vc, vr) in visited:
        k = 3 if (vc, vr) in hills else 2                # one square further from a hill
        seen |= {(c, r) for c in range(cols) for r in range(rows) if max(abs(c - vc), abs(r - vr)) <= k}
    patrol = [(5, 1), (5, 0), (4, 0), (4, 1)]            # fixed loop; (5, 0) is its next step
    sleeper = (7, 3)

    def zone(e):
        return {(c, r) for c in range(cols) for r in range(rows) if 0 < max(abs(c - e[0]), abs(r - e[1])) <= 2}

    danger = (zone(patrol[1]) | zone(sleeper)) & seen    # the patrol's zone after its next step
    b.append(tabled_board(gx, gy, cols, rows, cw, ch))
    for (c, r) in sorted(danger):
        b.append(mark(gx, gy, cw, ch, c, r, opacity=0.35))
    for (c, r) in ((0, 3), (1, 3), (0, 1)):              # footprints: squares already reached
        fx, fy = cell(gx, gy, cw, ch, c, r)
        b.append(f'<circle cx="{fx}" cy="{fy}" r="3" fill="{TEAL}" opacity="0.6"/>')
    for i in range(len(patrol)):
        (c1, r1), (c2, r2) = patrol[i], patrol[(i + 1) % len(patrol)]
        x1, y1 = cell(gx, gy, cw, ch, c1, r1)
        x2, y2 = cell(gx, gy, cw, ch, c2, r2)
        sx, sy = (x2 - x1) * 0.3, (y2 - y1) * 0.3
        b.append(arrow_path(x1 + sx, y1 + sy, x2 - sx, y2 - sy, INK, "" if i == 0 else "3 3"))
    b.append(token(*cell(gx, gy, cw, ch, *patrol[0]), "A", RED, 9))
    zx, zy = cell(gx, gy, cw, ch, *sleeper)
    b.append(token(zx, zy, "A", RED, 9))
    b.append(text(zx + 8, zy - 7, "z", 12, weight="bold", fill="#fff"))
    holes = "".join(f'<rect x="{gx + c * cw}" y="{gy + r * ch}" width="{cw}" height="{ch}" fill="#000"/>'
                    for (c, r) in sorted(seen))
    b.append(f'<defs><mask id="mist"><rect x="0" y="0" width="{w}" height="{h}" fill="#fff"/>{holes}</mask></defs>')
    b.append(f'<rect x="{gx}" y="{gy}" width="{cols * cw}" height="{rows * ch}" fill="{NIGHT}" opacity="0.82" '
             f'mask="url(#mist)"/>')
    for (c, r) in hills:                                 # mountains are known from the start
        b.append(hill(gx, gy, cw, ch, c, r))
    b.append(token(*cell(gx, gy, cw, ch, 2, 3), "A", TEAL, 9))
    b.append(token(*cell(gx, gy, cw, ch, 1, 1), "R", TEAL, 9))
    b.append(lines(gx + cols * cw + 14, gy + 4, [
        "lit: within 2 of every square", "your pieces have stood on", "(3 from a hill); stays lit",
        "dark: mist", "hills: always shown", "red: an enemy would", "notice you here",
        "arrows: a fixed patrol", "(solid: its next step)", "z: asleep, in the mist"], 10, 13))

    # Episode 4 (boss)
    gx, gy = episode(510, 334, "Episode 4 · The Giant", [
        "It arrives as a reinforcement on a later turn and walks 1 square a turn.",
        "Before each step it hits and pushes back everything in front; a unit with",
        "no room behind is destroyed. It cannot be blocked, only killed.",
        "Win: eliminate every enemy (no turn limit). Lose: it reaches your back row.",
    ])
    b.append(tabled_board(gx, gy, cols, rows, cw, ch))
    bx, by = cell(gx, gy, cw, ch, 7, 2)
    b.append(f'<rect x="{bx - 17}" y="{by - 24}" width="34" height="36" rx="5" fill="{RED}" stroke="{INK}" stroke-width="2.5"/>')
    b.append(text(bx, by + 2, "GIANT", 8, "middle", fill="#fff", weight="bold"))
    b.append(token(bx - 12, by - 24, "A", RED, 7))
    b.append(arrow_path(bx - 20, by, bx - 2 * cw + 6, by, RED))
    b.append(text(bx + 4, by + 30, "arrives turn 8+", 10, "end", fill=INK))
    for (c, r, L) in ((3, 1, "S"), (4, 2, "A"), (4, 4, "R"), (3, 3, "A")):
        b.append(token(*cell(gx, gy, cw, ch, c, r), L, TEAL, 9))
    b.append(token(*cell(gx, gy, cw, ch, 6, 0), "A", RED, 9))
    b.append(text(20, h - 8, CREDIT, 11, fill=GREY))
    return svg(w, h, "".join(b))


# ---- 4. Game flow ----------------------------------------------------------------
def box(x, y, w, h, title, rows=(), built=False):
    stroke = TEAL if built else "#8a8073"
    dash = "" if built else ' stroke-dasharray="7 5"'
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{stroke}" '
           f'stroke-width="{3 if built else 2}"{dash}/>' + text(x + w / 2, y + 22, title, 14, "middle", weight="bold"))
    for i, row in enumerate(rows):
        out += text(x + w / 2, y + 40 + i * 15, row, 11, "middle")
    return out


def flow():
    w, h = 1000, 480
    b = [text(20, 30, "Game flow — the full game; teal boxes exist in the built slice", 16, weight="bold")]
    top = 50
    b.append(box(20, top, 150, 64, "Title", ["press Enter"], built=True))
    b.append(box(210, top, 200, 64, "Episode & level select", ["unlocked levels"]))
    b.append(box(450, top, 220, 64, "Briefing", ["story text, board, terrain,", "enemy army"]))
    b.append(box(710, top, 270, 64, "Army draft", ["split the pool into archers,", "riders and shielders"]))
    for x1, x2 in ((170, 210), (410, 450), (670, 710)):
        b.append(arrow_path(x1 + 2, top + 32, x2 - 2, top + 32))
    loop_y = 160
    b.append(box(120, loop_y, 760, 120, "Turn loop (both sides plan at once)", [], built=True))
    b.append(lines(150, loop_y + 50, ["1 Reinforce: place new soldiers", "2 Plan moves (+ Mend)",
                                      "3 Riders' first step", "4 Main move"], 12, 17))
    b.append(lines(450, loop_y + 50, ["5 Plan attacks", "6 Combat, one unit at a time", "7 Contested moves; Mend heals land",
                                      "8 Win check: no winner → next turn"], 12, 17))
    b.append(text(860, loop_y + 112, "slice: archers only, steps 2, 4, 5, 6, 8", 10, "end", fill=GREY))
    b.append(arrow_path(780, top + 64, 780, loop_y - 2))
    bot = 330
    b.append(box(120, bot, 170, 64, "Victory", ["back row reached,", "or the enemy is gone"], built=True))
    b.append(box(340, bot, 220, 64, "Results", ["turns, hits, retries;", "Enter: next level"], built=True))
    b.append(box(600, bot, 170, 64, "Defeat", ["the card names the cause"], built=True))
    b.append(box(810, bot, 170, 64, "Retry (R)", ["same level, same draft"], built=True))
    b.append(arrow_path(205, loop_y + 120, 205, bot - 2))
    b.append(arrow_path(685, loop_y + 120, 685, bot - 2))
    b.append(arrow_path(290, bot + 32, 338, bot + 32))
    b.append(arrow_path(770, bot + 32, 808, bot + 32))
    b.append(arrow_path(860, bot, 860, loop_y + 122))
    # results -> level select (next level unlocks)
    b.append(f'<path d="M 450,{bot + 64} L 450,412 L 40,412 L 40,138 L 300,138" fill="none" stroke="{INK}" '
             f'stroke-width="3" stroke-dasharray="7 5"/>')
    b.append(arrow_path(300, 138, 300, top + 66))
    b.append(text(60, 406, "next level unlocks", 11))
    b.append(f'<rect x="20" y="430" width="22" height="14" rx="3" fill="#fff" stroke="{TEAL}" stroke-width="3"/>')
    b.append(text(50, 442, "in the built slice", 11))
    b.append(f'<rect x="170" y="430" width="22" height="14" rx="3" fill="#fff" stroke="#8a8073" stroke-width="2" '
             f'stroke-dasharray="5 3"/>')
    b.append(text(200, 442, "planned", 11))
    b.append(text(280, 442, "P / Esc pauses from any play state; M and N mute music and sound.", 11))
    b.append(text(20, h - 10, CREDIT, 11, fill=GREY))
    return svg(w, h, "".join(b))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("cast", cast), ("abilities", abilities), ("levels", levels), ("flow", flow)):
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print(f"wrote design/gdd/{name}.svg")


if __name__ == "__main__":
    main()
