# TYPECHECK.md — GATE T

Reel: `claude-liam-walker-lane-tactics-jiean-yin-a6-gamedev`  |  Checked: 2026-11-08T22:13  |  Overall: PASS  |  Beats checked: 31  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B01 | ? | light | min-size §8.1: min text-run height 77px >= floor 41px | PASS | — |
| B02 | ? | — | no video | SKIP | — |
| B03 | ? | light | no-wordy-card §8.5: 2 element(s), 12 words — within budget. Detail: 2 output lines (12 wor… | PASS | — |
| B04 | ? | — | no video | SKIP | — |
| B05 | ? | light | no-wordy-card §8.5: pull-quote (11 words ≤ 12) | PASS | — |
| B06 | ? | — | no video | SKIP | — |
| B07 | ? | light | no-wordy-card §8.5: pull-quote (9 words ≤ 12) | PASS | — |
| B08 | ? | — | no video | SKIP | — |
| B09 | ? | light | no-wordy-card §8.5: pull-quote (11 words ≤ 12) | PASS | — |
| B10 | ? | — | no video | SKIP | — |
| B11 | ? | light | no-wordy-card §8.5: pull-quote (9 words ≤ 12) | PASS | — |
| B12 | ? | — | no video | SKIP | — |
| B13 | ? | light | no-wordy-card §8.5: pull-quote (11 words ≤ 12) | PASS | — |
| B14 | ? | — | no video | SKIP | — |
| B15 | ? | light | no-wordy-card §8.5: pull-quote (9 words ≤ 12) | PASS | — |
| B16 | ? | — | no video | SKIP | — |
| B17 | ? | light | no-wordy-card §8.5: pull-quote (6 words ≤ 12) | PASS | — |
| B18 | ? | — | no video | SKIP | — |
| B19 | ? | light | no-wordy-card §8.5: pull-quote (7 words ≤ 12) | PASS | — |
| B20 | ? | — | no video | SKIP | — |
| B21 | ? | light | no-wordy-card §8.5: pull-quote (11 words ≤ 12) | PASS | — |
| B22 | ? | — | no video | SKIP | — |
| B23 | ? | light | no-wordy-card §8.5: pull-quote (12 words ≤ 12) | PASS | — |
| B24 | ? | — | no video | SKIP | — |
| B25 | ? | light | no-wordy-card §8.5: 2 element(s), 12 words — within budget. Detail: 2 output lines (12 wor… | PASS | — |
| B26 | ? | — | no video | SKIP | — |
| BCRD | ? | — | no video | SKIP | — |
| BVDT | ? | light | min-size §8.1: hand-drawn pattern (ClaudeVerdictArtifact) — §8.1 hachure/crossbar fragment… | PASS | — |
| BHTF | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| BOUT | ? | dark | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 12 | 0 |
| min-size §8.1 | 17 | 0 |
| overflow §8.2 | 17 | 0 |
| contrast §8.3 | 17 | 0 |
| contrast-local §8.3b | 17 | 0 |
| bbox-overlap §8.6b | 17 | 0 |
| card-clip §8.13 | 17 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 1 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
