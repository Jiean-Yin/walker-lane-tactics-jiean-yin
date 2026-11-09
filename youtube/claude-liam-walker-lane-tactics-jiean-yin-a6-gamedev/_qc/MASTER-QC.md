# MASTER QC — final export

- **File:** `exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-a6-gamedev.mp4`
- **SHA-256:** `68124efb8d904f0eb81a8ee462470ed6ec43e23f1826fac922c26510b00075c6`. It matches the `.verified.json` receipt, status `ready`.
- **Format:** H.264 3840×2160, 30/1 fps, 18 900 frames; AAC 48 kHz stereo; **10:30.0** (630.0 s); 58.8 MB.
- **Game source shown:** tag `a6` (`7f199f9`). Script approved by Jiean on 2026-11-08, with the dated changes in SCRIPT-DRAFT.md.

## Gates and checks (actual results, in order)

| Check | Result |
|---|---|
| `./art godot-gamedev --check` before the final cut | PASS: 25 source files, 82 exclusions, 8 components, 12 exact excerpts, code-then-result-v1, 12 pairs ([godot-gamedev-check-prerender.txt](godot-gamedev-check-prerender.txt)) |
| First render of the code views | B03 was cut off at line 99, hiding the highlights on lines 102–104, and several side notes were clipped. Every excerpt was fitted to the panel (≤ 14 rows at size 23–34), keeping every line the narration names, with three short notes (`tools/fit_workbench.py`). Checked frame by frame after the re-render |
| `./art final`, attempt 1 | **Blocked by Gate T**: 4 code-view bottom lines over 12 words (B03, B05, B07, B25); B11's "per 1/30 s" read as truncated. Lines shortened; Gate T PASS |
| `./art final`, attempt 2 | Gate T PASS; **refused by Gate V**: 2 MAJOR `low-contrast` on B26 (whole-frame 0.28 < 0.3; the card is mostly pale board crops) ([REPORT-attempt-1.md](REPORT-attempt-1.md)). B26's title and Jiean's answer were declared as text regions, measured with the gate's own function first; media unchanged |
| `./art final`, attempt 3 | Gate T PASS, Gate V PASS ([REPORT-attempt-2.md](REPORT-attempt-2.md)). **Rejected in this QC:** B01 never made its on-screen correction (the trigger was two words; the component matches single words), so it ended on "The tests decide how they look." Fixed: trigger "Tests" → "Jiean's eyes", plus 1.5 s of silent hold |
| `./art final`, attempt 4 | **PASS**: Gate T PASS ([../TYPECHECK.md](../TYPECHECK.md)); Gate V: 0 BLOCKER, 0 MAJOR over 62 sampled frames ([REPORT.md](REPORT.md)); receipt written. This is the master |
| `./art godot-gamedev --check` at handoff | PASS ([godot-gamedev-check-handoff.txt](godot-gamedev-check-handoff.txt)) |

## Inspection of the actual master (`tools/qc_master.py` → [master-qc.json](master-qc.json))

**Frame sheets** ([frame-sheet-1.png](frame-sheet-1.png) to [-4](frame-sheet-4.png), 3 frames per beat). Every beat shows its intended content in order:
- B01 ends on "Jiean's eyes decide how they look."
- B04: the enemy's hit on the player at real speed, then the burst at ¼ speed, cropped 3×.
- B06: P mid-burst under the PAUSED overlay.
- B08: both hits, with the A3 log line on a card.
- B12: the dotted arcs and the kill shot, with Jiean's first look.
- B14: the landing, then P mid-flight.
- Code views: every line and highlight is visible.
- Labels are present on every engine beat and on both reconstructed-interface beats.
- The outro card has the exact title, @NikBearBrown and one mascot, with no subline ([last-frame.png](last-frame.png)).

**Audio:**
- Integrated −24.6 LUFS, true peak −2.8 dBFS.
- Per-beat mean −27.8 to −26.6 dB, peaks −8.7 to −2.8 dB.
- Narration only: the engine captures carry no audio in the film, and the outro carries only Liam's voice.
- No silence over 2.5 s below −50 dB.

**Spot ASR** (faster-whisper base.en) of B00, B16, B24, B25, B26, BVDT and BOUT ([asr-spot.json](asr-spot.json)):
- The name is heard as "Jay Ann", "JAN" and "JN": the "Jay-An" sound of the A5 film.
- Jiean's quoted excerpts are read as approved.
- The recogniser mishears the outro title ("Lane tactics are hit bursting in a narrow trail"), a recogniser slip like those in A5.

## Human check

Jiean watched the full export (2026-11-08): "Ready as is".
