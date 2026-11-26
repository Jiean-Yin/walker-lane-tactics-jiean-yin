# Flag sprite sheet — credits and provenance

| | |
|---|---|
| Asset | **Flag Animation Sheet**, file `flag_red.png` |
| Source page | https://opengameart.org/content/flag-animation-sheet |
| Author | **Fokko** (OpenGameArt user), as listed on the source page |
| Published | 2020-12-13 (source page) |
| Licence | **CC0** (public domain dedication; no credit required): https://creativecommons.org/publicdomain/zero/1.0/ |
| Licence checked | 2026-11-25, by Claude Code for Jiean Yin, from the source page's "License(s)" field |
| Downloaded | 2026-11-25, from `https://opengameart.org/sites/default/files/flag_red.png` |

The course asks for provenance even though CC0 does not ask for credit. The film and `SOURCES.md` credit the author anyway.

## File

| File | Format | Bytes | SHA-256 |
|---|---|---|---|
| `flag_red.png` | PNG, 500 × 249, 8-bit colour map | 8,506 | `bbe98fe4e54613a1f024b5e9e6d62828f4378b1404a18a4aecea5606dee5a1c4` |

**Kept exactly as downloaded.** It is the editable source of the sheet. Any fix for registration drift is a node offset, never an edit of this file.

## Layout, as measured (not yet the brief's slicing)

Measured in the browser from the image's alpha channel on 2026-11-25 (pixels with alpha above 8):

- Content sits in **4 columns × 1 row**: x = 4–110, 133–239, 256–362, 378–484; y = 2–247. 500 / 4 = 125, so the cells would be **125 × 249 px**, frames 0–3 left to right.
- Inside its 125-px cell, the flag starts at x = 4, 8, 6 and 3: it **shifts by up to 5 px between frames** (registration drift, to be checked in the strip).
- Only two colours are used.

The cell size, grid and frame order the game uses are stated in `CHANGE-BRIEF.md`, and the clip is sliced from the brief, not from this note.

The same page also offers `flag_red_green.png` (a 4 × 2 version with a green row). It is not downloaded and not used.
