# walker-lane-tactics-jiean-yin

**Assignment 2 — Generate Art, Sound, and Music for Your Game · Jiean Yin · Godot 4.7.2**

*Lane Tactics* (working title): a turn-based, simultaneous-orders tactics game. Carved wooden pieces fight on a five-lane tabletop board, and you win by standing a piece on the enemy's back row. This repository holds the design and the **asset slice**, a small playable scene that proves the generated art, sound effects and music work together. The full game is this semester's project.

![The slice: your archer draws on the enemy archer (engine screenshot, scripted input)](evidence/screens-1791864538/09-attack-hit-enemy-hurt.png)

**Started from:** an empty Godot 4.7.2 project (no code from walker-jumpman or my Assignment 1). The test-and-evidence practice and document set come from Assignment 1, which extended Nik Bear Brown's [walker-jumpman](https://github.com/nikbearbrown/walker-jumpman). See [SOURCES.md](SOURCES.md).

## Run it

Requires the standard **Godot 4.7.2** build (not .NET).

```bash
git clone https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin.git
cd walker-lane-tactics-jiean-yin
```

- **Windows:** clone into a folder whose path is shorter than about 120 characters (for example inside `Downloads`). The longest file path in the repository is 134 characters, and Windows rejects full paths over 260 unless `git config --global core.longpaths true` is set.
- **Editor:** open Godot, **Import**, choose `godot/project.godot`, press **Run** (F5).
- **Command line:** `<Godot exe> --path godot`
- **Tests** (headless, each writes a timestamped report to `evidence/`):

  ```bash
  <Godot console exe> --headless --path godot --import
  <Godot console exe> --headless --path godot --script res://tests/test_rules.gd
  <Godot console exe> --headless --path godot --script res://tests/test_audio_events.gd
  ```

## Controls

| Key | Action |
|---|---|
| Enter | start; confirm the order; play again |
| Arrows / WASD | move phase: choose a neighbouring square · attack phase: cycle the valid targets |
| Space | stay (move) or hold fire (attack) |
| R | retry from turn 1 |
| P / Esc | pause and unpause (music gets quieter) |
| **M** | mute and unmute **music** |
| **N** | mute and unmute **sound effects** |
| F3 | show the footprint slots (debug, display only) |

Your teal archer starts in your back row (left). One red enemy archer marches toward it. Each turn you step, then shoot any square within two steps that holds an enemy. Who strikes first alternates every turn, as the HUD shows. Win by defeating the enemy or by standing on the red back row.

## What the slice demonstrates

| | What | Made with |
|---|---|---|
| Character | the archer swaps one static image per state: **idle, draw, hurt, defeat, win**. It faces right, and the enemy is the same art recoloured and flipped. Art is anchored on the base disc inside a per-square footprint | Stable Diffusion XL base 1.0, run locally (seeds in [assets/gen-log.jsonl](assets/gen-log.jsonl)) |
| Environment | warm-lit walnut tabletop behind the code-drawn linen board | SDXL base 1.0 |
| Sound effects | **SFX-HOP** (a piece lands), **SFX-HIT** (your arrow lands), **SFX-HURT** (you are hit), **SFX-WIN** (you win), each fired once per event from the rules engine's event list | ElevenLabs Sound Effects (free plan) |
| Music | a 24-second, 8-bar loop that plays on the title and in play, ducks on pause, fades out on defeat, stops on win, and restarts on retry | MusicGen small, run locally |

The design came first, committed before any generation: [CONCEPT.md](CONCEPT.md) · [STORYBOARD.md](STORYBOARD.md) · [CHARACTER-SHEET.md](CHARACTER-SHEET.md) · [CHANGE-BRIEF.md](CHANGE-BRIEF.md) · [RULES.md](RULES.md). The rest of the record: [SOURCES.md](SOURCES.md) (models, licences, the asset log with every rejected output) · [TEST-REPORT.md](TEST-REPORT.md) · [FRICTIONAL.md](FRICTIONAL.md). Rejected outputs are in [assets/rejected/](assets/rejected/).

## Known limitations

- **Muted play:** the red target marker is hard to see on a square that holds a piece, and a new player cannot tell why the enemy moves or stops (author's playtest). Planned next: a clearer target colour and a simpler enemy that keeps moving toward the end and avoids direct contact.
- The slice uses **one enemy**; the storyboard drew two. With two, the search showed it could only be won on the tie rule (CHANGE-BRIEF R1).
- **Pose mismatches** against the sheet: hurt has no squint; defeat has a dot eye and a navy bow; the arms cover the face in the win pose. The idle base disc is redrawn by hand.
- The ElevenLabs sounds have no seed, and the exact game description added to their prompts was not recorded.
- One human tester (the author); Windows only.

## Film

**"Lane Tactics: From Sketch to Seed to Sound"**, the Brutalist `godot-gamedev walker` explainer, 6:08, 3840 × 2160, 30 fps, narrated by Liam (local Kokoro TTS).

| | |
|---|---|
| Link | [https://youtu.be/aWLQ2fvkly4](https://youtu.be/aWLQ2fvkly4) (YouTube, channel @JieanYin; video title "Lane tactics game development, sound & art test") |
| File | `claude-liam-walker-lane-tactics-jiean-yin-gamedev.mp4` (kept out of GitHub; MP4) |
| SHA-256 | `543020595fe6e95c9878e14e059c9936b9b1d49097edc8b491d6254b18236aba` |
| Game source shown | tag `film-source-v1` = `fcf33ef` (`godot/` identical to the tested `12f7283`) |

It includes a labelled segment (3:28–3:45) where the slice's own music and sound effects play with no narration over them. The film's beat sheet, script, prompts, capture records and QC are in [youtube/claude-liam-walker-lane-tactics-jiean-yin-gamedev/](youtube/claude-liam-walker-lane-tactics-jiean-yin-gamedev/). Build-machine paths in those records are written as `<repo>`, `<capture-copy>`, `<brutalist>` and `<Godot>`.
