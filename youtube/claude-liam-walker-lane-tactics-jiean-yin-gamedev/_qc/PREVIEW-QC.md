# Preview QC — approval gate (before the final 4K render)

Recorded by Claude Code, 2026-10-13. Subject: review cut `claude-liam-walker-lane-tactics-jiean-yin-gamedev-slate.mp4` (1920×1080, 30 fps, AAC 48 kHz, 368.20 s; `compile.py --review --fps 30 --height 1080` with `ART_NO_DRAWTEXT=1` after `./art run --height 1080` ran all gates — `./art run` itself compiles at the compiler's default 24 fps). **This is not the final film.** No 4K final has been rendered.

| Check | Result |
|---|---|
| `./art godot-gamedev --check REEL --game <repo>/godot` | **PASS**: 48 source files + 3 exclusions (= all 51 authored files), 6 components, 3 exact excerpts, `code-then-result-v1`, 3 code → result pairs (B10→B11, B12→B13, B15→B16). Also passes without `PYTHONUTF8`. |
| `./art godot-waikthrough --check REEL` (extra, capture contract) | **PASS**: 5 capture clips, all native 3840×2160 16:9, hashes match, input log present, 13 shown features + 2 planned. Scope is "features shown in this film", not a complete walkthrough; unfilmed implemented features are listed under `not_filmed` in coverage.json. |
| Gate L (beat lint), Gate SHAPE | clean / not applicable |
| Gate V (frame QC, 46 frames) | **0 BLOCKER, 0 MAJOR** after fixes (first run: 5 BLOCKER edge-bleed in B02/B05/B16, 1 MAJOR contrast in B18). B18 declares `contrast_regions` (quotes, pose labels, not-reproducible box) with a written reason. |
| Gate T (type_check.py) | **PASS** after fixes (first run: B08/B17 label touching the code card's right edge, B15 17-word output strip, B17 title without a filename, B14 raw footage not exempt because its shot type was `SOURCE_REPORT` → now `type: VIDEO`, `kind: source_report`). |
| Slice audio in the cut (`tools/check_audio.py <cut> --offset 207.9`) | B14 at 3:27.9–3:44.7: **all 7 logged SFX found in order** HOP, HOP, HOP, HURT, HIT, HIT, WIN by matched filter against the game's own OGG files (NCC 0.67–0.99 vs control ≤ 0.15; 1–11 ms after the logged frame); −16.5 LUFS; digital silence after the win sound (music stopped). On the clip itself the decoded samples are identical to the Movie Maker AVI. Report: `_qc/audio-check-claude-liam-walker-lane-tactics-jiean-yin-gamedev-slate.json`. |
| Narration-only beats | B13 and B15 windows: mean −27.2 dB (narration only; no game audio by design). |
| Outro audio | BOUT voice −25.4 dB mean; last 1.0 s −91 dB (silence). No jingle, no game audio. |
| No retiming | No "slowed"/"center-cut"/retime notices in the compile log; every gameplay beat's audio is padded to the clip's exact frame count; B14 frames in the cut match media/B14.mp4 at offset 0 (mean diff 0.65 vs 0.75 at ±1). Review cut SHA-256 `1de7eb72…`. |
| Labels | B00/BHTF reconstructed interface; B08/B17 actual source / recorded output; B04–B07, B16, B18 composites (design sketches, raw output, files, held frames); GodotDevWorkbench prints "Godot editor reconstruction"; gameplay "SCRIPTED INPUT · REAL GODOT RENDER / film-source-v1 · game audio muted"; B14 "SLICE AUDIO — NO NARRATION". |
| Pronouns | Narration and on-screen text refer to "Jiean" only; no gendered pronouns (searched the beat sheet). |

## Toolkit issues met (not patched)

1. **Review-cut drawtext on Windows:** `compile.py --review` builds `drawtext=fontfile=C:\…` without escaping the drive colon/backslashes, so ffmpeg rejects the filter. Worked around with the toolkit's own `ART_NO_DRAWTEXT=1` switch (PIL labels instead of the running timecode). The final export does not use drawtext.
2. **GodotDesignBoard handle below title-safe:** its hard-coded `@NikBearBrown` (bottom 4 % of the frame) reaches y 1027–1035 of 1080, a Gate V edge-bleed BLOCKER. B02 was rebuilt as our own composite with the same excerpt and cards instead of patching the component.
3. **BrutalistHesitantWriter triggers are single tokens**, so a phrase trigger ("in a folder") silently does nothing; B01 uses the one-word trigger `folders` → "the running game".

## Still for a human to judge

Watch and listen to the whole review cut: Kokoro pronunciations ("rembg", "U-two-net", "piece dot g d", "flip h"), whether the slice-audio jump (~8 LU louder than narration) is acceptable, and whether every claim matches what is on screen.

# Final master — after Jiean's approval-gate answers (2026-10-13)

Answers applied: title kept; B14 kept bit-exact (no gain change); greeting "Ciao" → "Hello" and the script/on-screen text scanned for non-English words (only proper names remain: rembg, u2net, Kokoro, MusicGen, ElevenLabs, SDXL); only B00's narration was regenerated and re-measured (18.37 s), B00 re-rendered and relabelled. Outro: at 4K the slug-seeded `jump` mascot rose into the handle (overlap at the jump peak); fixed with a documented local patch to `ClaudeTitleOutro.tsx` (mascot headroom), BOUT re-rendered; measured gap handle ink → mascot 82–198 px at 4K over every frame.

| Check (final) | Result |
|---|---|
| Export | `exports/landscape/claude-liam-walker-lane-tactics-jiean-yin-gamedev.mp4`, 3840×2160, 30 fps (11,049 frames), H.264 + AAC 48 kHz stereo, 368.333 s, 33,933,066 bytes, SHA-256 `543020595fe6e95c9878e14e059c9936b9b1d49097edc8b491d6254b18236aba` (= `.verified.json`, status `ready`) |
| Gate T / Gate V (inside `./art final`) | PASS / 0 BLOCKER, 0 MAJOR (46 frames; B18 regional contrast) |
| `godot-gamedev --check`, `godot-waikthrough --check` | PASS / PASS (re-run after the final) |
| B14 in the master (offset 208.033 s, 3:28.0–3:44.9) | 7/7 game SFX found in logged order HOP, HOP, HOP, HURT, HIT, HIT, WIN (NCC 0.60–1.00 vs control ≤ 0.15, 1–11 ms after the logged frame); −16.5 LUFS; silence after the win; picture matches media/B14.mp4 at offset 0 (0.06 vs 0.16 at ±1) |
| No narration in B14 / no game audio under narration | B14 audio is the source clip only (compiler source_report path); B13 and B15 windows: best match to game HIT/HURT 0.25 / 0.28 (no game SFX) vs 0.85 in B14 |
| Outro | voice −25.4 dB mean; final 1.0 s −91 dB (digital silence); no jingle or game audio |
| Reading-size inspection (4K crops) | B05 log record, B07 edit chain, B10/B12/B15 code, B14 label, B19 credits, BOUT: legible, no clipping, mascot below the handle |
