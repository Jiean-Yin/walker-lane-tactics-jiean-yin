# SCRIPT DRAFT — "Lane Tactics: A Danger Tint and a Linen Board"

Assignment 5 film, Brutalist `godot-gamedev walker`. Liam (in for Bear), Kokoro `am_onyx`, 4K landscape, no captions. **Drafted by Claude from Jiean's own documents** (CHANGE-BRIEF, TEST-REPORT, LANGUAGE-NOTES, FRICTIONAL); Jiean approves it before any audio is made. Source shown: tag `a5` (`ef5d38b`), filmed on an isolated copy. About 8–9 minutes.

**Footage:** every game and 3D shot is real engine output from Godot Movie Maker on that copy (`capture/` records every frame's state and value). Key presses and uniform changes are scripted and labelled so. Jiean's own C-key captures and OS screenshot are shown as evidence stills.

Each code beat is followed directly by the result it produces (code → result).

---

## B00 ASK — Claude composer (labelled "Illustrative reconstruction of the Claude interface — not a transcript")
**Prompt typed:** "Please use Walker to convert my game design document about Lane Tactics — archers on a five-lane board, simultaneous orders, win by reaching the enemy's back row — into two shaders: a red tint that warns when my planned square is inside the enemy archer's reach, and a linen cloth material for the 3D board squares. Test both, and show me what a headless run cannot."
**Result lines:** `test_exposed_tint 46/46 at 30, 60 and 144 fps` · `test_materials 148/148 · 3 mutations exit 1` · `Source shown: tag a5 (ef5d38b)`

> Hello, this is Liam, in for Bear. Jiean Yin's game is Lane Tactics: archers on a five-lane board, where you win by reaching the enemy's back row. This assignment adds shaders: a red warning on the archer, and a cloth surface for the 3D board. The prompt on screen is an illustrative reconstruction.

## B01 BLUF — hesitant writer
**Typed:** "Two shaders for Lane Tactics: / a warning and a weave. / Written by hand, / judged by the tests." → the last word corrects to **"pixels"**.

> What was built: two shaders, written by hand by Jiean, one driven by the game's state and one by textures. The tests check the wiring. Whether they work is judged in the pixels.

## B02 SETUP — card
**Card:** State **exposed**: your planned square is inside the enemy archer's reach · Object: two linen tiles in the A3 diorama · The four questions · Renderer: **Compatibility**.

> The assignment asks for one shader driven by game state, one textured shader with two materials, and four answers: what a shader does, how a material differs from a shader, why a texture is information, and what Godot's shading language is. Each answer points at a line of code. One fact shapes everything: this project runs on Godot's Compatibility renderer.

## B03 CODE — `exposed_tint.gdshader` lines 1–8 (Godot editor reconstruction; highlights 3, 4, 7)

> Question one: what does a shader do? It runs on the graphics card, once for every pixel the sprite covers. This one is Jiean's, written by hand. Line three: exposed amount, a number from zero to one. Line seven is the colour line. It mixes the sprite's own colour toward the game's red by that amount, capped at seventy percent, so the face and the bow still show. Only red, green and blue change; transparency is untouched.

## B04 RESULT — tint in play, capture frames 46–311 (label "SCRIPTED KEY PRESSES · REAL GODOT RENDER · main.tscn @ a5", with a zoom of the same frames on the archer)

> Here it is in the real game, keys pressed by a script. Two turns out of reach: no tint. Turn three: Right plans a square inside the enemy archer's reach, and the archer turns red in a fifth of a second. Left steps back out, and the red drains away.

## B05 CODE — `exposed_driver.gd` lines 29–37 (highlights 32, 34, 37)

> The shader doesn't know the game. The driver tells it. Every frame it asks one question: is the planned square in reach? Line thirty-four moves the amount toward one or zero, at five per second of game time, starting from wherever it is now. That is why a quick tap turns around mid-fade instead of restarting, and why pause holds it still. Line thirty-seven hands the number to the player's own material. Every sprite gets a new material of its own, so the enemy never shares the red.

## B06 RESULT — tint in play, capture frames 311–628 (same label)

> Fast taps, every tenth of a second: the value turns around from where it is, and never jumps. Pause in the middle of a fade, and it holds. Enter confirms the move, and the red fades while the move plays. Turn four starts already in reach, so it rises again on the first frame. The enemy's tint stays at zero in every frame of this capture.

## B07 EVIDENCE — Jiean's C-key captures (stills of `evidence/a5/captures/exposed_0.0 … 2.0.png`, crops at P1 and P2, predicted beside measured; label "JIEAN'S CAPTURES · capture() in a real window")

> Before looking, Jiean worked the colours out by hand. Then the engine's own frame was captured at four values. At zero and one half, the head and the base match the predictions exactly. At one, within one step: the hand sum gave one hundred point five. At two, set from code, the head reads two twenty-four, twenty-seven, thirty-four: exactly the unclamped prediction. Hint range draws the Inspector's slider. It does not clamp a value set from code. And a Windows screenshot of the same moment gave the same numbers.

## B08 CODE — `linen_dark.tres` lines 8–16 (highlights 11, 13, 16; side panel: linen_light's values)

> Question two: how is a material different from a shader? The shader is the program. A material is one set of values for it. Both linen materials point at the same shader, on line eleven. They differ in two lines: the tint on line thirteen, white for light and stitch-brown for dark, and normal strength on line sixteen: one for light, one and a half for dark.

## B09 RESULT — diorama capture frames 0–195, 810–1080 (labels: "THE SCENE'S OWN CAMERA3D · REAL GODOT RENDER", then "SCRIPTED: uniform / shader code changed in memory on an isolated copy · no file saved")

> Both tiles, under the diorama's single lamp. Turn the dark material's normal strength down to zero, and only the dark tile goes flat. Change one line of the shared shader, in memory, and both tiles darken together. One program, two sets of values. Jiean made the same two edits by hand in the editor, and saw the same thing.

## B10 CODE — `linen_square.gdshader` lines 3–12 (highlights 4, 9, 11; side panel: import settings and curl ratios)

> Question three: why is a texture information? Because the same kind of pixels can mean different things. Line four reads the cloth photograph as colour, with source colour. Line nine reads roughness as plain data, with no colour hint. Line eleven reads the normal map as directions, with hint normal: each pixel is a tilt, not a shade. The import settings agree: lossless everywhere, and the normal-map flag only on the normal maps. And a curl check on the normal map tells the right green convention from the wrong one, by zero point six eight against one point three two.

## B11 RESULT — diorama capture frames 195–810 (label "SCRIPTED UNIFORM SWEEP · REAL GODOT RENDER · in memory, no file saved")

> The interface sweep, on the light tile. U V scale down from three point six five to one half: threads like rope. Up to eight: a fine weave. Normal strength to zero: the threads flatten into paint. To two: deeper threads, still cloth. Roughness to zero, seen from the lamp's mirror angle: in this capture the tile gets slightly darker, and no highlight appears. In the editor, Jiean saw it turn shiny, like plastic. The two disagree, and that stays open.

## B12 CODE — `hint_experiment.gdshader` lines 1–14 (highlights 4, 5, 6)

> The hint experiment asks whether source colour changes the numbers a shader receives. One file, three greys: sixty-four, one twenty-eight, one ninety-two. Line four samples it with source colour, line five without, and line six picks which one writes albedo. Unshaded, linear tonemap, exposure one. Jiean predicted that the hinted quad would show the file's own values, and the plain one would come out lighter: one thirty-seven, one eighty-eight, two twenty-five.

## B13 RESULT — hint capture (4K frame of `hint_experiment.tscn`) with the measured bands beside the prediction (label "REAL GODOT RENDER · hint_experiment.tscn @ a5")

> Measured on this renderer: both quads show sixty-four, one twenty-eight, one ninety-two. It isn't a wiring slip. Swapping the switches changes nothing, separate textures change nothing, and a plain one half written to albedo shows as one twenty-eight. On Compatibility, in this scene, neither the decode nor the encode happened. The prediction assumed Forward Plus. It's recorded, not explained away.

## B14 LANGUAGE — card: two lines of the editor's generated shader beside Jiean's (verbatim)
`standard_generated.gdshader:7` `uniform sampler2D texture_albedo : source_color, filter_linear_mipmap, repeat_enable;` ↔ `linen_square.gdshader:4`
`standard_generated.gdshader:19` `uniform sampler2D texture_normal : hint_roughness_normal, filter_linear_mipmap, repeat_enable;` ↔ `linen_square.gdshader:11`

> Question four: what is Godot's shading language? A small language, close to G L S L, where Godot writes the boring parts. There's no main function and no version line: shader type picks the pipeline and its built-ins, like albedo and normal map. And it has hints that G L S L doesn't. Here is the editor's own conversion of a standard material, beside Jiean's. Its line seven samples albedo with source colour, just like Jiean's line four. Its line nineteen reads the normal map with hint roughness normal, where Jiean's line eleven uses hint normal. The same idea, with a different hint.

## B15 CODE — `test_exposed_tint.gd` lines 167–177 (highlights 168, 170, 173)

> Now the tests. The agent-written test asks the engine for the shader's uniform list, and checks the names and types. A headless engine won't report defaults or source colour, so the test reads those from the shader's own text. Then it presses real keys and checks every frame against the rule.

## B16 RESULT — headless output card (recorded reports, no rendering; label "HEADLESS CHECK OUTPUT · recorded reports")
46/46 at 30 · 60 · 144 fps · 148/148 · earlier suites 51/51 · 70/70 · 38/38 · Mutation 1, `;` deleted → SHADER ERROR, exit 1 · Mutation 2, uniform renamed → exit 1 (the 529-frame value check still passed) · Mutation 3, `source_color` deleted → exit 1 (146/148) · What headless cannot show.

> Forty-six of forty-six, at thirty, sixty and a hundred and forty-four frames per second; a hundred and forty-eight of a hundred and forty-eight for the materials; and the earlier suites unchanged. Then Jiean broke the shaders on purpose. Delete a semicolon: shader error, exit one. Rename the uniform: exit one, and the frame-by-frame value check still passed, because setting a name the shader doesn't have raises no error. Only the uniform list caught it. Delete source colour: exit one. What no headless run can show: any pixel at all. That is what the captures are for.

## BCRD — who did what
> Who did what. Jiean chose the state, the object and the cloth, wrote the three shaders and the colour line by hand, computed every prediction, ran the three mutations, took the captures, and played it. Claude agents wrote the driver, the tests and the material audit; Claude Code reviewed them and built the materials and scenes. Caught on the way: a wrong line number, two misnamed frame-rate reports, and an audit figure nobody had measured. The cloth is Hessian 380 from Poly Haven, public domain. Source shown: tag a5.

## BVDT — verdict (checked / wrong / uncertain / next)
> Verdict. Checked: the tint follows its rules at three frame rates, the captures match the hand predictions within one step, and hint range doesn't clamp. Wrong: the hint experiment's prediction, on this renderer. Uncertain: why Compatibility behaves that way, the missing roughness highlight, and a thirty-frame fade that sits exactly on its tolerance. Next step: run the hint experiment on Forward Plus, in a copy, to see which half belongs to the renderer.

## BHTF — Your Turn (composer, "suggested prompt, not a past run")
**Prompt typed:** "Change the cap in my colour line from 0.7 to 0.5. Before you change anything, help me predict the head pixel at exposed_amount 1.0 by hand, then I'll capture it with C and we compare."

> Your turn. Open your own shader, change one number, and predict before you look. Here's a prompt to start with: change the cap from seventy to fifty percent, work out the head pixel by hand, then capture it and compare. If the numbers miss by more than a step, that isn't a failure. That's a finding. I'm Liam, in for Bear.

## BOUT — locked outro card
> Lane Tactics: A Danger Tint and a Linen Board. At Nik Bear Brown.

---

### Points for Jiean to check
1. **Your name:** Kokoro said "Jiean" inconsistently in the A3 film. Tell me how it should sound (for example "Jee-en"), and I'll spell it that way for the voice only; the screen keeps "Jiean".
2. **Facts that differ from LANGUAGE-NOTES:** B13 uses the measured facts (neither decode nor encode happened), not "cancelled out".
3. **B11's roughness disagreement** (engine capture vs your editor view) is stated as open.
4. **Anything here you'd say differently:** the film is your work's explainer, so change any sentence.
