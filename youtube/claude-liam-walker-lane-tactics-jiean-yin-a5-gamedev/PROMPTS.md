# PROMPTS — real and reconstructed

## Real prompts behind the work shown

| Prompt | Where | Used for |
|---|---|---|
| Step 1: CLAUDE.md draft | `prompts/a5/prompt-1.txt` (course text, verbatim) | `claude -p`, session record `evidence/a5/sessions/session-1.jsonl` |
| Step 2: driver and test, plan first | `prompts/a5/prompt-2.txt` (course text, verbatim) | planning run, `session-2-plan.jsonl` |
| Step 2: implementation | `prompts/a5/prompt-2-implement.txt` (drafted by Claude, approved by Jiean) | `session-2-implement.jsonl` |
| Step 3: material audit | `prompts/a5/prompt-3-audit.txt` (course text, verbatim) | `session-3-audit.jsonl` |

## Film prompts

- **Jiean to Claude Code (2026-11-03):** start the film with the course's Brutalist `godot-gamedev walker` workflow; defaults accepted for title, footage, narration review, Your Turn, revision and upload. Script approved as drafted; the name is said "Jay-An".
- **B00 composer text** is an **illustrative reconstruction**, not a prompt that was run: "Please use Walker to convert my game design document about Lane Tactics — …" (labelled on screen).
- **BHTF composer text** is a **suggested prompt**, not a past run (labelled on screen): "Change the cap in my colour line from 0.7 to 0.5. Before you change anything, help me predict the head pixel at exposed_amount 1.0 by hand, then I'll capture it with C and we compare."
