# MASTER QC — the A7 film

Master: `exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-a7-gamedev.mp4` (not in git).
- **Format:** 3840 × 2160, H.264 + AAC, 30 fps, 474.433 s (7:54.4), 43,291,109 bytes.
- **SHA-256:** `3c2e831bcc2624b7431bc0088a1a8f612781fdbb3a2f396fd8ec9cbc526fb794`.

| Check | Result |
|---|---|
| `./art godot-gamedev --check` (before the render) | PASS: 25 source files, 96 exclusions, 5 components, 9 exact excerpts, 9 code → result pairs |
| Gate T (TYPECHECK.md) | PASS, 0 FAILs, 26 beats |
| Gate V (`_qc/REPORT.md`) | 52 frames sampled, 0 BLOCKER, 0 MAJOR |
| Frame sheets (`_qc/frame-sheet-1..3.png`), looked at by Claude | every beat shows its intended picture: the workbench highlights the lines the narration names; footage labels on every engine segment; Jiean's quotes verbatim; B01 ends on "Frames decide the timing."; the outro is the locked card |
| Loudness (`_qc/master-qc.json`) | integrated −24.6 LUFS, true peak −2.9 dBFS; no silence over 2.5 s below −50 dB |
| Spot ASR (faster-whisper base.en) | B01, B12, BOUT transcribe as written ("Nick Bear Brown" is the recogniser's spelling) |
| Last frame (`_qc/last-frame.png`) | the outro card, title and @NikBearBrown |

**Known blemish:** in B04's first seconds (the title card), the 3× crop on the flag catches the right ends of the title card's instruction lines. This is real footage, labelled as cropped, and left as is.

**Jiean's watch-through of the full export (2026-11-26):** "Ready". Uploaded by Jiean: https://youtu.be/1DWyaSYxO24
