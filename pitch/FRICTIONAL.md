# FRICTIONAL — Assignment 8, final project pitch film

Same format as the repository's `FRICTIONAL.md`. Claude Code writes the factual lines (**Asked**, **Got**, **Human / Claude / model**) from the session record. The judgment lines (**Wanted**, **Decided**, **Still unresolved**) are Jiean's: they are `TO FILL`, each with a labelled hint to rewrite in Jiean's own words.

---

## 2026-11-24 — Choosing the project and the seven answers

- **Wanted:** TO FILL
  > *Hint (Claude):* what you want the final project to show a lead engineer, and why a finished one-level slice of Lane Tactics rather than a tool or an effects pack.
- **Asked:** Claude Code to read the A8 brief and the repository, and to propose the project and the seven answers with a default for each.
- **Got:** a proposal: Lane Tactics taken to a one-level vertical slice (title to end screen, three unit types, AI), Windows desktop export, Compatibility renderer; gameplay programmer read by a lead engineer; Plants vs Zombies and Into the Breach as comparables; out: multiplayer and episodes 2–4; first: the full turn loop with three units; risk: strike-back stalls.
- **Decided:** TO FILL
  > *Hint (Claude):* that you accepted the defaults ("Defaults fine, go"), and whether anything in the brief should change now that you read it written out, especially the two comparable games: you should have played both.
- **Next:** Assignment 7 (animation) feeds the "animation and state" line of answer 4.
- **Human / Claude / model:** the project and the acceptance of each answer were Jiean's; the wording, the repository facts and the tag references were Claude Code's (Claude Opus 5.5). No generative model.
- **Still unresolved:** TO FILL
  > *Hint (Claude):* whether the export target stays Windows desktop or also adds a web export (the risk the course names: web means Compatibility only, which this game already uses); and whether the stall test's 40-turn limit is the right number.

## 2026-11-24 — Building the film on the deadline day

- **Wanted:** TO FILL
  > *Hint (Claude):* a short, honest pitch film finished before 23:59 on the due date, rather than a long one handed in late.
- **Asked:** Claude Code at 22:31, about 90 minutes before the deadline, whether the film could be finished tonight.
- **Got:**
  - The Brutalist checkout (`6a8380a`) has **no `show-tell` skill**, and its full `godot-gamedev walker` pipeline took most of a day for the A6 film. The A8 brief also forbids the instructor's name, persona and credit line, which that workflow's locked outro uses.
  - So the film was built with a lean local script (`tools/build_film.py`): Brutalist's own Kokoro narration step (`generate_audio_kokoro.py`, voice `am_onyx`), slides drawn with Pillow and labelled *constructed*, and real gameplay cut from the A6 film master (tag `a6`, scripted key presses, labels burned in by the A6 capture).
  - No new gameplay capture was made: the footage is A6's.
  - Brutalist's own gates were run on the master (`gates/`). Attempt 1: `loudness_check` passed (−20.3 LUFS, −2.0 dBTP); `master_check` **failed** one frame (t = 76 s): its label-band heuristic read the dark wood table in the bottom-left of the real A6 footage as a review label. The toolkit's own exemption for external footage is a `SOURCE-CUT` shot type, so beats B02 and B05 were marked `SOURCE-CUT` in `beat_sheet.json`; the risk slide's figure was also moved down (it overlapped the title). Attempt 2: both gates **passed** (`gates/MASTERCHECK.md`, `gates/LOUDNESS.md`).
- **Decided:** TO FILL
  > *Hint (Claude):* whether the lean film is the one you submit, or you re-render later with a fresh capture; and whether you watched the whole film before submitting.
- **Human / Claude / model:** the decision to finish tonight was Jiean's; the script, the build script and the slides were Claude Code's. Narration: Kokoro-82M (local, Apache-2.0), reading Jiean's accepted words.
- **Still unresolved:** TO FILL
  > *Hint (Claude):* that the footage shows only the A6 slice (one archer each), so nothing of the will-exist part is shown as play; and whether to update Brutalist to a checkout that has `show-tell`.
