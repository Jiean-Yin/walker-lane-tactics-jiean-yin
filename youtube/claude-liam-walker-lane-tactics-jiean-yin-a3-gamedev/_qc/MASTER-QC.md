# MASTER QC — final export

**File:** `exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-a3-gamedev.mp4`
**SHA-256:** `83d2489e2ee1f6e6c2d5ffc1df5387f086fba0c51a983904e08b93a2d4ad4240` (matches the `.verified.json` receipt, status `ready`)
**Format:** H.264 3840×2160, 30/1 fps, 8445 frames; AAC 48 kHz stereo; **4:41.5** (281.5 s); 35.3 MB.

## Gates and checks (actual results, in order)

| Check | Result |
|---|---|
| `./art godot-gamedev --check` before rendering | PASS — 10 source files, 49 exclusions, 5 components, 2 exact excerpts, code-then-result-v1, 2 pairs ([godot-gamedev-check-prerender.txt](godot-gamedev-check-prerender.txt)) |
| `./art final` attempt 1 | **BLOCKED by Gate T**: B03 sparkLine 13 words, B07 output line 13 words (> 12). Fixed (shorter text), re-rendered B03, B07, B10 |
| `./art final` attempt 2 | **REFUSED by Gate V** (final_frame_check): 6 BLOCKER `edge-bleed` (B04–B06 label pill above the title-safe top edge), 2 MAJOR `low-contrast` (B08, B09, dark engine scene). Fixed: footage label and picture moved inside title-safe; B08/B09/B11 declare `qc.contrast_regions` for the burned label with a reason |
| `./art final` attempt 3 | **PASS**: Gate T PASS ([../TYPECHECK.md](../TYPECHECK.md)), Gate V 0 BLOCKER / 0 MAJOR over 36 sampled frames ([REPORT.md](REPORT.md)), 18/18 slots filled, receipt written |
| `./art godot-gamedev --check` at handoff | PASS ([godot-gamedev-check-handoff.txt](godot-gamedev-check-handoff.txt)) |
| tools/build_evidence.py external excerpts | B03 (build_archer_piece.py 135, 140) and B10 (build_board_square.py 142–143) shown verbatim; hashes recorded |

## Inspection of the actual master (tools/qc_master.py → [master-qc.json](master-qc.json))

- **Frame sheets** ([frame-sheet-1.png](frame-sheet-1.png), [frame-sheet-2.png](frame-sheet-2.png); 3 frames per beat at 10/50/90 %): every beat shows its intended content in order; labels present on every footage, engine and reconstructed beat; B01 completes its correction ("judged in the running scene.") before the cut; B12 shows all lines 171–182; B13 table and cards legible; outro card = exact title, @NikBearBrown, one mascot below the handle, no subline ([last-frame.png](last-frame.png)).
- **Audio:** integrated −24.5 LUFS, true peak −2.9 dBFS; per-beat mean −26.2 to −28.7 dB, peaks −2.9 to −8.2 dB; narration only (footage audio dropped; the diorama has no sound); the outro card carries only Liam's voice, no jingle.
- **Silences > 2.5 s below −50 dB** (all intentional, picture keeps moving or holding): 27.3–31.3 s (B01 writer finishing), 103.3–107.7 s (end of B06 reports excerpt), 137.3–142.4 s (end of the B08 orbit), 153.0–158.1 s (end of B09 archer profile).
- **Spot ASR (faster-whisper base.en) of B05, B10, BCRD:** words as written, except the name "Jiean", which the recogniser hears inconsistently — Kokoro's pronunciation of the name should be checked by ear.
- **Known soft spot:** B03's two source lines are 101 characters, so they sit at the normal (not large) code size: readable at 4K full screen, small on a phone.

## Not done by Claude

Nobody has watched and listened to the whole export in real time. **Jiean must watch the final export before submitting** (sync of words to footage, the pronunciation of names, overall pacing).

## Follow-up 2026-10-15: "B02 and B07 titles clipped" (student's report from the frame sheet)

- **Cause: the QC sheet, not the film.** The first version of `tools/qc_master.py` drew its black "beat @ time" caption box over the top-left corner of every tile (0–260 × 0–30 px of a 640 px tile = 0–1560 × 0–180 px at 4K). On B02 and B07 that box covered the top of the title, so the titles looked clipped on `frame-sheet-1.png`.
- **The master was measured, not just viewed:** first ink row of the title in the actual 4K frames: B02 (t 39.5 s) **y = 138 px**, B07 (t 114.9 s) **y = 114 px**; the title-safe top edge is 108 px (5 % of 2160). Both titles sit fully inside title-safe, unclipped and readable (full-resolution crops checked). Gate V on this master: 0 BLOCKER / 0 MAJOR.
- **Fix:** `tools/qc_master.py` now writes the caption in a strip **below** each tile; `frame-sheet-1.png`, `frame-sheet-2.png`, `last-frame.png` and `master-qc.json` were regenerated from the same master. In the new sheet, B02 ("Three assets, three jobs") and B07 ("asset_diorama.tscn: Three Models, One Floor") show complete titles at all three sampled times.
- **No re-render:** the film itself had nothing to fix, so the master was not rebuilt and is unchanged: SHA-256 `83d2489e2ee1f6e6c2d5ffc1df5387f086fba0c51a983904e08b93a2d4ad4240` is still current, not superseded. (B07's title position is set by the shared `GodotDevWorkbench` component, which is outside the reel folder and was not edited.) `./art godot-gamedev --check` rerun: see [godot-gamedev-check-handoff.txt](godot-gamedev-check-handoff.txt).
