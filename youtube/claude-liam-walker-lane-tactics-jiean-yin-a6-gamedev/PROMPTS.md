# PROMPTS — real and reconstructed

## Real prompts behind the work shown

| Prompt | Where | Session record |
|---|---|---|
| Step 1: CLAUDE.md draft | `prompts/a6/prompt-1.txt` | `evidence/a6/sessions/session-1.jsonl` |
| Step 2a: Effect A scene, config test, preview | `prompts/a6/prompt-2a-build.txt` | `session-2a-build.jsonl` |
| Step 2b: Effect B scene, config test, preview | `prompts/a6/prompt-2b-build.txt` | `session-2b-build.jsonl` |
| Step 3a: Effect A driver and state test, plan, then implementation | `prompt-3a-plan.txt`, `prompt-3a-implement.txt` | `session-3a-plan.jsonl`, `session-3a-implement.jsonl` |
| Step 3b: Effect B driver and state test, plan, then implementation | `prompt-3b-plan.txt`, `prompt-3b-implement.txt` | `session-3b-plan.jsonl`, `session-3b-implement.jsonl` |
| Step 7: headless price | `prompt-7-cost.txt` | `session-7-cost.jsonl` |

All at tag `a6`. Commit IDs quoted inside the session records are pre-rewrite IDs, by design (TEST-REPORT A6.11).

## Film prompts

- **Main session to this film session (2026-11-08):** make the A6 explainer with Brutalist `godot-gamedev walker`, using the A5 film folder as the template for the records. Draft the script and get Jiean's approval, capture from an isolated copy of tag `a6`, voice with Kokoro `am_onyx`, render, check, and ask Jiean to watch. No commit, push or upload without Jiean.
- **Jiean in this session:**
  - "Approve as is" (the script);
  - "Yes, use them" (the B04/B08 sentences, after the pilot);
  - "Approve as proposed" (the voice excerpts, the B25 range and the BVDT wording);
  - "Yes, fix B10".
- **B00 composer text** is an **illustrative reconstruction**, not a prompt that was run (labelled on screen): "Please use Walker to convert my game design document about Lane Tactics — …".
- **BHTF composer text** is a **suggested prompt**, not a past run (labelled on screen): "Raise fixed_fps on the Streak in my arrow trail from 30 to 60. Before you change anything, help me predict the gap between the dots for a two-square shot that lasts 0.35 seconds. Then I'll capture a strip and we compare."
