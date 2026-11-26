# SOURCES — provenance of everything in the A7 film

- **Game source:** tag `a7` = commit `37c4698` (tree `dd91e92`), https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin, filmed on an isolated `git archive` copy (CAPTURE.md).
- **Engine footage:** `<capture-copy>/final-out/play-4k.mkv` and `slow-4k.mkv`, real Godot 4.7.2 renders (Compatibility renderer, Movie Maker), SHA-256 in `capture/masters-sha256.txt`.
- **Runtime probe:** the capture driver's per-frame logs (`capture/play-log.jsonl`, `slow-log.jsonl`) read poses, `piece.rig_snapshot()` and the flag's cell.
- **The flag sheet:** "Flag Animation Sheet" by Fokko, https://opengameart.org/content/flag-animation-sheet, **CC0**, checked 2026-11-25. Shown as downloaded, with a grid drawn by us (B04).
- **The archer art:** the A2 draw art (`assets/art/archer_draw.png`, `_enemy.png`), cropped by the rig. Its sources are in the repository's `SOURCES.md` (Assignment 2).
- **Jiean's strips:** `captures/shoot/r0`, `r1` and `captures/flag_registration_r1.png` at tag `a7`, fixture captures.
- **Jiean's words:** verbatim from tag `a7`'s TEST-REPORT.md, TUNING.md and SUBMISSION.md (`capture/quotes.json`, checked by `tools/build_sheet.py`).
- **Recorded test output:** `evidence/a7/` at tag `a7`.
- **The reference video** (World Archery, "Archery in slow motion S01E010 BONUS: Ki Bo Bae (Coach Cam)") is **not shown**. Only Jiean's frame numbers from CHANGE-BRIEF §4 appear.
- **Narration:** local Kokoro `am_onyx` ("Liam, in for Bear"), no paid service. **Scenes:** Brutalist Remotion components (`ClaudeComposerAsk`, `BrutalistHesitantWriter`, `GodotDevWorkbench`, `ClaudeVerdictArtifact`, `ClaudeTitleOutro`).
- No secrets, `.env` contents or absolute developer paths are recorded.
