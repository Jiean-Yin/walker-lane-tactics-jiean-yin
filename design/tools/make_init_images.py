"""Init images for image-to-image generation (one pose per 1024x1024 white canvas).

Each image is a design-sketch pose from draw_sketches.py with effect marks and
ground shadow removed. The image model uses it only as a starting point; the
asset log records the strength used.

Run (repo root): py -3.11 design/tools/make_init_images.py && bash design/tools/render_png.sh design/character/init
"""
import draw_sketches as d
from pathlib import Path

OUT = d.ROOT / "design" / "character" / "init"
POSES = ["idle", "draw", "hurt", "defeat", "win"]
NAME_TO_POSE = {"win": "celebrate"}


def main():
    d.FX = False
    OUT.mkdir(parents=True, exist_ok=True)
    for name in POSES:
        pose = NAME_TO_POSE.get(name, name)
        scale = 8.5 if pose != "defeat" else 6.5
        x = 512 if pose != "defeat" else 470
        body = d.archer(x, 900, scale, pose=pose, show_ground=False)
        (OUT / f"{name}.svg").write_text(d.svg(1024, 1024, body, bg="#FFFFFF"), encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
