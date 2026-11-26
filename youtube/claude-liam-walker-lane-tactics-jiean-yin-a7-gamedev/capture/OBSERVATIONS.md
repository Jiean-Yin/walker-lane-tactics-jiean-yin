# Observation sentences checked against the final capture

Claude checked each result beat's observation sentences against frames of `play-4k.mkv` and `slow-4k.mkv` and against the logs, before narration. **None had to change**, so nothing went back to Jiean.

| Beat | Sentence | Checked against |
|---|---|---|
| B04 | "the flag stands on the table beside the enemy's back row and ripples, about twice a second, from the title screen on" | play frames 60 and 300 (the flag beside lane 3, on the title card and in play); `flag_cell` changes every 0.125 s, so one ripple of 4 cells = 0.5 s |
| B11 | "the archer leans back and the bow comes up level. The arrow leaves … eases forward … a short hold after the hit, then the bow drops … back in the idle pose" | play frames 332, 333, 336, 339, 345, 350, 353, 356, 358, cropped on e1 (draw, bow up, the arrow leaving at 339, follow-through, hold, drop, idle) |
| B13 | "each time, the archer holds mid-motion, and carries on from the same pose when unpaused … the archers are rebuilt, and nothing from the old shot comes back" | play-summary.json expectations (paused in each phase; R restarts with no shot left); play-log clip_t constant across each pause |
| B15 | "Paused: the archers freeze, the flag keeps waving" | play frame 850 (PAUSED card; the flag visible at the right edge); `flag_cell` changes 72 times while paused |
