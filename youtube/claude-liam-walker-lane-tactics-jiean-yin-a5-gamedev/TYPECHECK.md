# TYPECHECK.md — GATE T

Reel: `claude-liam-walker-lane-tactics-jiean-yin-a5-gamedev`  |  Checked: 2026-11-03T01:20  |  Overall: PASS  |  Beats checked: 21  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B01 | ? | light | min-size §8.1: min text-run height 81px >= floor 41px | PASS | — |
| B02 | ? | — | no video | SKIP | — |
| B03 | ? | light | no-wordy-card §8.5: pull-quote (5 words ≤ 12) | PASS | — |
| B04 | ? | — | no video | SKIP | — |
| B05 | ? | light | no-wordy-card §8.5: pull-quote (6 words ≤ 12) | PASS | — |
| B06 | ? | — | no video | SKIP | — |
| B07 | ? | — | no video | SKIP | — |
| B08 | ? | light | no-wordy-card §8.5: pull-quote (10 words ≤ 12) | PASS | — |
| B09 | ? | — | no video | SKIP | — |
| B10 | ? | light | no-wordy-card §8.5: pull-quote (5 words ≤ 12) | PASS | — |
| B11 | ? | — | no video | SKIP | — |
| B12 | ? | light | no-wordy-card §8.5: pull-quote (6 words ≤ 12) | PASS | — |
| B13 | ? | — | no video | SKIP | — |
| B14 | ? | — | no video | SKIP | — |
| B15 | ? | light | no-wordy-card §8.5: pull-quote (9 words ≤ 12) | PASS | — |
| B16 | ? | — | no video | SKIP | — |
| BCRD | ? | — | no video | SKIP | — |
| BVDT | ? | light | min-size §8.1: hand-drawn pattern (ClaudeVerdictArtifact) — §8.1 hachure/crossbar fragment… | PASS | — |
| BHTF | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| BOUT | ? | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 6 | 0 |
| min-size §8.1 | 11 | 0 |
| overflow §8.2 | 11 | 0 |
| contrast §8.3 | 11 | 0 |
| contrast-local §8.3b | 11 | 0 |
| bbox-overlap §8.6b | 11 | 0 |
| card-clip §8.13 | 11 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 1 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
