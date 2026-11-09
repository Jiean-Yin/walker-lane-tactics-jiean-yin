# Quotes for the film, read from tag `a6` (for Jiean to check before the voice is made)

Read on 2026-11-08 by `tools/quotes.py` from an isolated copy of the local tag `a6`, never from the working checkout. Stored verbatim in `capture/quotes.json`. They were read again from the pushed tag (`7f199f9`), after the history rewrite: every quote is identical.

**Approved by Jiean, 2026-11-08: "Approve as proposed".**

The screen always shows your words in full and exactly as committed. The voice reads only the excerpt in the right-hand column. In the spoken text, `Jay-Ann` is the voice's spelling of your name, and a few symbols are spelled out for the voice; those changes are marked.

| Beat | On screen, verbatim (source) | Proposed for the voice |
|---|---|---|
| B16 | "The darker arrow flew through the lines clearly and I can easily tell where it came out and went to. Darker puffs provide extra hints for the result of the battle, which keep more attention focusing on the result of each turn within limited time." (TUNING.md, Effect B r1, My verdict) | *Already agreed:* "Darker puffs provide extra hints for the result of the battle, which keep more attention focusing on the result of each turn within limited time." |
| B24 | Your whole A6.6 conclusion, from "Both effects are under the 0.2 ms budget …" to "… not the effects' work." (TEST-REPORT.md A6.6) | "Jay-Ann's conclusion: B's C P U cost wasn't zero because the trail is moved every frame." *(CPU spelled out, "0" read as "zero". The rest of your conclusion is already said by the narration just before it: overlap, the 1.5 ms swing, means only.)* |
| B25 | Your A6.7 line numbers, beside the code (TEST-REPORT.md A6.7) | "Jay-Ann's table: shader type on line three, start on three twenty-three, process on three seventy-eight. The initial velocity is mixed from its minimum and maximum on two thirty-two. Gravity becomes the force on four twelve. Scale and colour over life are applied on two fifty-four and two fifty-five. And line four forty-one belongs to turbulence, which the wisps switch on." *(Your line numbers, read with the labels of your table's rows. This is Liam reading your table, not a quote.)* |
| B26 | Your A6.7 answer, all five lines with your line breaks: "Shader: / All settings start with uniform or #define. … / Draw Step: / Draw-side settings are texture, CanvasItemMaterial blend mode, visibility_rect." (TEST-REPORT.md A6.7) | "Shader: all settings start with uniform or hash define. Like direction, spread, gravity. Draw step: draw-side settings are texture, Canvas Item Material blend mode, visibility rect." *(Your first and last sentences. `#define`, `CanvasItemMaterial` and `visibility_rect` are spelled for the voice.)* |
| BVDT | "Yes, there are animation of shooting and getting hit, plus the effect of arrow and wounded." (TEST-REPORT.md A6.8, Does it read as "hit" and "who shot whom"?) | The whole sentence, as written. |

## B25: which lines the code panel shows

The code panel fits one short range. **Proposed: lines 252–257**, `process_display_param()`, with your rows 254 (scale over life) and 255 (colour over life) highlighted while the voice says them. This is the code behind what B26 shows: the wisps swell and fade. The side panel lists start() 323, process() 378, 254 and 255; a line under it lists your other rows (3, 232, 412, 441).

Alternative: lines 408–425, with gravity becoming the force on your line 412. The velocity itself changes further down, on line 425 (`USERDATA1.xyz += force * DELTA;`).

## One wording change in Claude's verdict (BVDT), for accuracy

The approved verdict says "Wrong: … Jay-Ann's price predictions, low by less than a hundredth of a millisecond". Three of your four price predictions were low. Effect A's headless CPU prediction was high: predicted 0.015 ms, measured 0.0078 ms (TEST-REPORT A6.6 table). All four were off by less than 0.01 ms.

**Proposed:**
- voice: "Jay-Ann's price predictions, off by less than a hundredth of a millisecond";
- screen: "Jiean's price predictions (off by < 0.01 ms: three low, one high)".

## Two notes on the tagged documents (the film does not change them)

1. **Your A6.6 conclusion** says "Both predictions were too low". That doesn't hold for Effect A's CPU prediction, which was high (above). The film shows your conclusion verbatim, as your words. Whether to change TEST-REPORT is your decision, in the main session.
2. **A6.7, "The line" column:** two cells shorten the file's text.
   - Row 232 reads `multiplier = mix(…)`; the file has `params.initial_velocity_multiplier = mix(…)`.
   - Row 254 reads `s.scale *= …`; the file has `parameters.scale *= …`.

   All eight line numbers point at the lines they name. The film's code panel shows the file's real lines.
