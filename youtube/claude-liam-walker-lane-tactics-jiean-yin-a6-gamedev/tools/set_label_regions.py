"""Declare each footage beat's contrast region at its burned label's exact extent (the A5 lesson: a region copied
from another film failed Gate V). Every segment's pill is right-aligned at the same top and height, so the region is
the narrowest pill of the beat: inside the label on every frame. Pills are measured with make_media.pill(), the
function that draws them. Usage (reel folder): CAPTURE=<capture-copy> BRUTALIST=<brutalist> python tools/set_label_regions.py
"""
import json
import sys
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REEL / "tools"))
import make_media as mm  # noqa: E402  (reads CAPTURE and BRUTALIST, draws nothing on import)

# A still whose pictures are mostly pale board crops: Gate V's whole-frame ink average read 0.28 < 0.3 there (B26,
# 2026-11-08), although its text is dark ink on the page. Its essential text lives in these boxes, measured with the
# gate's own contrast_regions() on the 4K card before declaring them (both pass).
STILL_REGIONS = {"B26": ([{"label": "title", "box": [0.05, 0.03, 0.62, 0.115]},
                          {"label": "Jiean's answer, verbatim", "box": [0.05, 0.655, 0.86, 0.865]}],
                         "Evidence still: the pictures are enlarged pale board crops (Jiean's strips), not text. The "
                         "essential text is the title and Jiean's answer, dark ink on the page, in the declared boxes.")}

sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
for b in sheet["beats"]:
    if b["beat_id"] in STILL_REGIONS:
        regions, reason = STILL_REGIONS[b["beat_id"]]
        b.setdefault("qc", {})["contrast_regions"] = regions
        b["qc"]["contrast_reason"] = reason
        print(b["beat_id"], "regions:", [r["box"] for r in regions])
    segs = b["shot"].get("segments")
    if not segs:
        continue
    boxes = []
    for s in segs:
        l1, l2 = s.get("label", b["shot"]["label"]).split("|")
        p = mm.pill(l1, l2 + f" · capture frames {s['a']}–{s['b']} at {mm.SRC_FPS[s['src']]} fps", 46, 40)
        x0, y0 = mm.W - 150 - p.width, 110
        boxes.append((x0, y0, x0 + p.width, y0 + p.height))
    x0 = max(bx[0] for bx in boxes)
    y1 = min(bx[3] for bx in boxes)
    box = [round(x0 / mm.W, 4), round(110 / mm.H, 4), round((mm.W - 150) / mm.W, 4), round(y1 / mm.H, 4)]
    b["qc"]["contrast_regions"] = [{"label": "burned disclosure label", "box": box}]
    b["qc"]["contrast_reason"] = ("Real engine render; the essential text is our burned label (white/yellow on a dark "
                                  "green pill, top right). The region is the narrowest segment pill's exact extent, "
                                  "inside the label on every frame. Scene colours are not text.")
    print(b["beat_id"], box, [bx[2] - bx[0] for bx in boxes])
(REEL / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
