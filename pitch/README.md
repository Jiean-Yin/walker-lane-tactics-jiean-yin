# Lane Tactics — final project pitch (Assignment 8)

| | |
|---|---|
| **Name** | Jiean Yin |
| **Working title** | Lane Tactics |
| **Project** | Lane Tactics taken to a one-level vertical slice: title to end screen, three unit types, you against the AI |
| **Target role** | Gameplay programmer (reader: a lead engineer) |
| **Runtime** | Godot 4.7.2 standard, GDScript, Compatibility renderer; export target Windows desktop (not yet attempted) |
| **Film** | `lane-tactics-pitch-a8.mp4` · 3840×2160 · 24 fps · 2:33 · SHA-256 `45f65fc28d8f86531112185c524ada7433a987983101bd6b875ed6e79de2f43c` · link: *to add by Jiean after upload to the course media storage* (the MP4 is not in git) |

The seven answers are in [PROJECT-BRIEF.md](PROJECT-BRIEF.md), ending with **exists today** (with tags) and **will exist**.

## Files

| File | What it is |
|---|---|
| [PROJECT-BRIEF.md](PROJECT-BRIEF.md) | One page, the seven answers, exists today vs will exist |
| [beat_sheet.json](beat_sheet.json) | Narration and visual plan, nine beats, measured narration durations |
| [BUILD-PROMPT.md](BUILD-PROMPT.md) | The prompts and the commands that rebuild the film |
| [SOURCES.md](SOURCES.md) | What was used, what Jiean made, what Claude contributed, licences |
| [FRICTIONAL.md](FRICTIONAL.md) | Dated entries for this assignment |
| [gates/](gates/) | Brutalist gate reports on the master |
| [tools/build_film.py](tools/build_film.py) | Slides, cuts and assembly |

## How the film is honest

- **Real play:** beats B02 and B05 are cut from the A6 film, a Movie Maker capture of **tag `a6` (`7f199f9`)** with scripted key presses (labelled on screen; the ¼-speed part is labelled too).
- **Constructed:** every other beat is a drawn slide, labelled *constructed* on screen.
- **Narration:** an AI voice (Kokoro `am_onyx`, local) reading Jiean's words, and it says so in its first line.
- Nothing that does not exist is shown as play.

## How to rebuild the film

See [BUILD-PROMPT.md](BUILD-PROMPT.md). In short: Kokoro narration with Brutalist's `generate_audio_kokoro.py`, then `python pitch/tools/build_film.py --a6-master <A6 film mp4> --fonts <brutalist>/runtime/fonts`, then the gates. The MP4 is not in git.
