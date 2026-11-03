# MASTER QC — final export

**File:** `exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-a5-gamedev.mp4`
**SHA-256:** `f366ee660bac6ce6b2064d2b083bdb7e607876234761fd0047c5998b50453ebd` (matches the `.verified.json` receipt, status `ready`)
**Format:** H.264 3840×2160, 30/1 fps, 13,385 frames; AAC 48 kHz stereo; **7:26.2** (446.2 s); 115.2 MB.
**Game source shown:** tag `a5` (`ef5d38b`). Script approved by Jiean on 2026-11-03.

## Gates and checks (actual results, in order)

| Check | Result |
|---|---|
| `./art godot-gamedev --check` before the final cut | PASS: 39 source files, 49 exclusions, 8 components, 6 exact excerpts, code-then-result-v1, 6 pairs ([godot-gamedev-check-prerender.txt](godot-gamedev-check-prerender.txt)) |
| Pilot render B03 | code wrapped at size 34 and the third source note was cut off → size 30, one-line notes (`tools/patch_props_r1.py`) |
| Last frame of every code beat | B10, B12, B15 cut lines at size 30 (B15 hid its line-177 highlight) → per-beat sizes 24–28 (`tools/patch_props_r2.py`) |
| `./art final` attempt 1 | Gate T PASS; **REFUSED by Gate V**: 6 MAJOR `low-contrast` in B04, B06, B09, B11 ([REPORT-attempt-1.md](REPORT-attempt-1.md)). Cause: the declared label regions were copied from A3 (top-left) but the tint label sits top-right, and the diorama box was wider than the label. Fixed by declaring each beat's region at the label pill's exact measured extent; media unchanged |
| `./art final` attempt 2 | **PASS**: Gate T PASS ([../TYPECHECK.md](../TYPECHECK.md)), Gate V 0 BLOCKER / 0 MAJOR over 42 sampled frames ([REPORT.md](REPORT.md)), receipt written |
| `./art godot-gamedev --check` at handoff | PASS ([godot-gamedev-check-handoff.txt](godot-gamedev-check-handoff.txt)) |

## Inspection of the actual master (`tools/qc_master.py` → [master-qc.json](master-qc.json))

- **Frame sheets** ([frame-sheet-1.png](frame-sheet-1.png), [-2](frame-sheet-2.png), [-3](frame-sheet-3.png); 3 frames per beat): every beat shows its intended content in order.
  - B01 completes its correction ("judged by the pixels.").
  - B04 shows the archer red on turn 3.
  - B06 shows the taps, the move playing and turn 4 starting red.
  - B09 shows the scene camera, then only the dark tile flattening, then both tiles darkening.
  - B11 shows the sweep.
  - Labels are present on every engine beat and both reconstructed-interface beats.
  - The outro card has the exact title, @NikBearBrown and one mascot below the handle, with no subline ([last-frame.png](last-frame.png)).
- **Audio:** integrated −24.6 LUFS, true peak −2.9 dBFS; per-beat mean −27.6 to −26.7 dB, peaks −8.0 to −2.9 dB. Narration only: the engine captures carry no audio in the film, and the outro carries only Liam's voice. No silences over 2.5 s below −50 dB.
- **Spot ASR (faster-whisper base.en) of B00, B01, B03, BCRD, BOUT** ([asr-spot.json](asr-spot.json)): the name is heard as "Jay Ann", "J. Anne", "Jay Anion's" (run into "Yin's") and "JN": all the "Jay-An" sound Jiean asked for, never the earlier "Jee-un". Other words as written, apart from small recogniser slips ("Early red" for "Only red").
- **Known soft spots:**
  - B03 and B05 wrap their longest line onto a second row; the highlight covers both rows.
  - B12 hides the closing `}` of line 14 below its panel.
  - B15 shows line 177 but not the end of its wrapped continuation.
  - All excerpts are verbatim, and the checker verifies the full text.

## Not done by Claude

Nobody has watched and listened to the whole export in real time. **Jiean must watch the final export** (pronunciation of the name, sync of words to footage, pacing) before posting the link.
