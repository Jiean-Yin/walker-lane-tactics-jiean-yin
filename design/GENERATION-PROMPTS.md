# Generation prompts — Lane Tactics asset slice

Prompts written by Claude Code from CHARACTER-SHEET.md, STORYBOARD.md and CONCEPT.md, to be run by Jiean in free web tools. Every run gets a row in the SOURCES.md asset log, kept or rejected.

**For every run:** screenshot the page (prompt, settings, all results) and note the model version the site shows. Save downloads and screenshots to `assets/_raw/` (ignored by git) as `<ASSET-ID>-<run>-<variant>`, for example `CHAR-REF-01a.png`. No prompt names an artist, a brand, a copyrighted character, or existing music.

---

## 1. Art — Adobe Firefly (Text to Image)

Settings: aspect **1:1** for characters and **16:9** for the background; content type **Art**; no style presets unless logged. Firefly has no seed, so the screenshot and the downloaded original are the record.

### CHAR-REF — run first, then stop and review

> A single carved and painted wooden toy archer game piece, full body, strict side view facing right, standing on a round walnut wooden disc base. Smooth ball-shaped light birch wood head with one small black dot eye, no mouth, no nose. Dark navy painted hood. The body is one straight wooden cylinder with no legs, painted flat deep teal, with a thin dark walnut belt. A small walnut quiver with three arrows on its back, a simple walnut bow held upright in front. Thick even dark brown outline around every shape, flat matte enamel paint, simple rounded shapes like a board game miniature, soft warm light from the upper left. Centered, plain flat pure white background, no floor, no text.

Exclude (if offered): realistic person, legs, feet, mouth, nose, multiple figures, checkerboard, transparent background, text, watermark, gradient background, floor shadow.

**Judge against the sheet:** about 3.5 heads tall; ball head; one eye; base disc visible; thick outline; hood, quiver and bow present; profile facing right.

### Poses — each uses the accepted CHAR-REF as its reference image (Firefly "Reference" / composition + style)

Start every pose prompt with: *"The same carved wooden toy archer game piece as the reference: ball head, one dot eye, navy hood, teal cylinder body, walnut belt, quiver and bow, round walnut base disc, thick dark outline, flat matte paint, side view facing right, plain flat pure white background,"* then add:

| ID | Pose clause |
|---|---|
| CHAR-IDLE | standing upright at rest, bow held low in front of the body |
| CHAR-DRAW | leaning back slightly, bow arm extended straight forward, pulling the bowstring back toward its head with an arrow nocked |
| CHAR-HURT | tilted backward about 15 degrees on its base as if just struck from the front, eye squinting, a small chip in the paint on its chest |
| CHAR-DEFEAT | knocked over and lying flat on its side on the ground, head to the left, base disc to the right, bow dropped on the ground beside it |
| CHAR-WIN | both arms raised straight overhead holding the bow horizontally above its head in celebration |

**Plan B (if separate poses drift):** one 16:9 image —

> A character pose sheet of the same carved wooden toy archer game piece shown five times in a row, evenly spaced, same size: (1) standing at rest, (2) drawing the bow, (3) tilted back as if struck, (4) knocked over lying on its side, (5) arms raised holding the bow overhead. [same description as CHAR-REF] Plain flat pure white background, no text, no labels.

Claude slices it into separate images.

### ENV-TABLE — 16:9

> Top-down view of a dark walnut wooden tabletop, warm desk lamp light from the upper left making a soft pool of light toward the centre, gentle dark vignette at the edges, subtle wood grain, the centre left empty and evenly lit, no objects, no board, no text.

### ENV-LINEN (optional) — 1:1

> Seamless woven natural beige linen fabric texture, flat even lighting, top-down, fine weave, no folds, no pattern, no text.

---

## 2. Sound effects — ElevenLabs Sound Effects (free tier)

Settings: set **duration** by hand (values below); prompt influence high (about 0.7). Generate, listen to all takes, and download the ones you seriously consider (downloads are not capped). Claude trims the silence and converts to OGG.

| ID | Duration | Prompt |
|---|---|---|
| SFX-HOP | 0.5 s | A small wooden game piece set down firmly on a wooden game board, one short dry clack, close microphone, no reverb |
| SFX-HIT | 0.8 s | A small arrow striking a wooden toy figure, a quick sharp wooden thunk with a tiny rattle, close and dry, no reverb |
| SFX-HURT | 0.8 s | A wooden toy figure knocked hard, a dull low wooden crack followed by a short wobble on the table, dry, no reverb |
| SFX-WIN | 2 s | A short bright cheerful flourish of three rising notes on a kalimba with a soft wood block, ends cleanly, no reverb tail |

**Judge:** does it sound like wooden pieces on a table (pillar 3)? Is it short, and does it start at once? Can you tell HIT and HURT apart with your eyes closed?

---

## 3. Music — Suno (free tier: browser listening is unlimited, 7 downloads for the life of the account)

Settings: **Instrumental ON**; custom mode; title "Lane Tactics planning loop".

Style prompt:

> calm instrumental, acoustic, plucked nylon guitar and kalimba, soft wooden percussion, warm low drone, steady slow pulse, 80 bpm, 4/4, thoughtful board game mood, consistent energy, no vocals, no build-up, no big ending

**Judge (listen in the browser):** calm enough to think over (audio direction)? Steady from start to end, with no drop or build that would break a loop? Wooden or acoustic, not epic? Reject in the browser with a screenshot and one line on why; **download only finalists (1–2)**. Claude cuts an 8- or 16-bar loop at a bar boundary; you check the seam by listening to at least 3 repetitions in the game.
