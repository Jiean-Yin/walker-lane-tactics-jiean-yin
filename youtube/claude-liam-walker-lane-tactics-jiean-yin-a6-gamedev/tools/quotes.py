"""Read Jiean's own words for the film's bracketed quotes from the isolated copy of tag a6 (never from the working
checkout, never written by Claude) and store them verbatim in capture/quotes.json.

Raw fields (verbatim from the tag):
  b_r1_verdict      TUNING.md, Effect B r1, "My verdict (running game, 1280 × 720): …"
  price_conclusion  TEST-REPORT.md A6.6, "Jiean's conclusion: …"
  a67_rows          TEST-REPORT.md A6.7 table rows: {what, lines, line}
  a67_split         TEST-REPORT.md A6.7, the answer after "…belong to the draw step instead: "
  playtest_reads    TEST-REPORT.md A6.8, the row "Does it read as \"hit\" and \"who shot whom\"?"
Each field is None if the tag still says TO FILL. The *_spoken fields and a67_range (B25's excerpt) are chosen after
reading the raw words, shown to Jiean, and then added by hand; this script keeps any already present.
Usage (reel folder): CAPTURE=<capture-copy> REPO=<repo> python tools/quotes.py
"""
import json
import os
import re
import subprocess
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
COPY = Path(os.environ["CAPTURE"]) / "a6"
OUT = REEL / "capture/quotes.json"


def filled(s):
    s = (s or "").strip()
    return None if (not s or "TO FILL" in s) else s


def section(text, start, stop):
    a = text.index(start)
    b = text.find(stop, a + len(start))
    return text[a:b if b > 0 else len(text)]


tuning = (COPY / "TUNING.md").read_text(encoding="utf-8")
report = (COPY / "TEST-REPORT.md").read_text(encoding="utf-8")

b_r1 = section(tuning, "## 2026-11-08 -- Effect B, revision r1", "\nStrips:")
# Only the words inside Jiean: "…"; the note after it ("(Recorded as **kept**.)") is the log's, not Jiean's.
m = re.search(r'^My verdict \(running game, 1280 × 720\):\s*Jiean:\s*"(.*)"', b_r1, re.M)
b_r1_verdict = filled(m.group(1) if m else None)

a66 = section(report, "## A6.6 Price", "## A6.7")
m = re.search(r"^Jiean's conclusion:\s*(.*?)(?:\s*\(Jiean\))?\s*$", a66, re.M)  # the trailing "(Jiean)" is a marker
price_conclusion = filled(m.group(1) if m else None)

a67 = section(report, "## A6.7 The process shader", "## A6.8")
rows = []
for line in a67.splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) == 3 and cells[0] not in ("What", "---") and not set(cells[0]) <= {"-"}:
        rows.append({"what": cells[0], "lines": filled(cells[1]), "line": cells[2]})
a67_rows = rows if rows and all(r["lines"] for r in rows) else None
# Jiean's answer runs from the line after the question (which ends "(Jiean)") to the end of the section, line breaks kept.
m = re.search(r"belong to the draw step instead:[^\n]*\n(.*)\Z", a67, re.S)
a67_split = filled("\n".join(ln.rstrip() for ln in m.group(1).strip().splitlines()) if m else None)

a68 = section(report, "## A6.8 In play", "## A6.9")
m = re.search(r'^\| Does it read as "hit" and "who shot whom"\? \|\s*(.*?)\s*\|\s*$', a68, re.M)
playtest_reads = filled(m.group(1) if m else None)

# The pushed tag (2026-11-08, after the one history rewrite): its commit and tree.
commit, tree = subprocess.run(["git", "-C", os.environ["REPO"], "rev-parse", "a6^{commit}", "a6^{tree}"],
                              capture_output=True, text=True, check=True).stdout.split()
old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
q = {"source_revision": f"tag a6 = {commit} (tree {tree})", "read_from": "<capture-copy>/a6 (git archive of tag a6)",
     "b_r1_verdict": b_r1_verdict, "price_conclusion": price_conclusion, "a67_rows": a67_rows,
     "a67_split": a67_split, "playtest_reads": playtest_reads}
for k, v in old.items():
    if k.endswith("_spoken") or k in ("a67_range", "approved_by"):
        q[k] = v
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(q, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
for k in ("b_r1_verdict", "price_conclusion", "a67_rows", "a67_split", "playtest_reads"):
    print(f"{k}: {'MISSING (still TO FILL at the tag)' if q[k] is None else 'ok'}")
