# SUBMISSION — Assignment 2: Generate Art, Sound, and Music for Your Game

| Field | Value |
|---|---|
| Assignment | Assignment 2 - Generate Art, Sound, and Music for Your Game |
| Student | Jiean Yin |
| Project name | walker-lane-tactics-jiean-yin |
| Game concept in one sentence | A turn-based tactics game where carved wooden pieces on a five-lane tabletop board receive secret, simultaneous orders, and you win by standing a piece on the enemy's back row. |
| GitHub repository/folder URL | https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin |
| Started from | An empty Godot 4.7.2 project (practices and document set carried over from my Assignment 1, which extended Nik Bear Brown's walker-jumpman) |
| Submitted commit SHA | Given in the Canvas submission note: the `main` commit that contains this file's final version. A commit cannot contain its own SHA. |
| Source revision shown in the film | tag `film-source-v1` = `fcf33eff6c501d32624532ca197257a646552991` (the `godot/` folder is identical to `12f7283`, the tested revision) |
| Godot version and operating system | Godot 4.7.2.stable.official.ed1daf0bf (standard build, Compatibility renderer) · Windows 11 Home 10.0.26200 |
| Generative models used | **Stable Diffusion XL base 1.0** (Stability AI), run locally on my laptop GPU, CreativeML Open RAIL++-M: character poses and the tabletop background. **MusicGen small** (Meta), run locally, weights CC-BY-NC 4.0: the music loop. **ElevenLabs Sound Effects**, free web plan, run by me, non-commercial use only (ElevenLabs Terms of Use §1(c)): the four sound effects. **rembg / U²-Net**, local, MIT / Apache-2.0: background removal. Tried and not used: Suno v6-mini/v6 preview and ElevenLabs Music (free plans could not download). |
| Final film URL and filename | *TO FILL after rendering* |
| Final film SHA-256 | *TO FILL after rendering* |

## Summary of my work

- **Design before generation** (commit `92417a2`, Oct 9 22:46, before the first Suno attempt at 23:03): CONCEPT (core loop, 4 pillars, art and audio direction), STORYBOARD (9 panels, 3 views, 4 angles), CHARACTER-SHEET (archer turnaround and 12 poses, silhouette test, orientation, collision overlay, palette check, consistency rules), CHANGE-BRIEF (asset list, event-to-sound map, music behaviour, 7 predicted failures).
- **Generated assets in the running slice:** the archer in 5 states (idle, draw, hurt, defeat, win) plus red enemy copies; the tabletop background; 4 sound effects on real events; a seamless 8-bar music loop with pause/defeat/win/retry behaviour; M/N mute music and effects separately. Every generation, kept or rejected, is in the asset log (SOURCES.md, assets/gen-log.jsonl, assets/edit-log.jsonl), with rejected thumbnails in assets/rejected/.
- **Verification:** a fresh clone passes 51/51 rules and 70/70 sound-event checks (sounds equal events, held/rapid input adds nothing, a muted run ends identically). My own playtest with sound on and muted is in TEST-REPORT §6. Five inspect-and-revise cycles, including the one-enemy rule change found by exhaustive search (CHANGE-BRIEF R1) and the redrawn idle base disc.
- **Explainer film:** Brutalist `godot-gamedev walker`; reel records in `youtube/claude-liam-walker-lane-tactics-jiean-yin-gamedev/`.

## Known limitations

- Muted play: the attack target is hard to see on an occupied square, and the enemy's movement is not explained (my playtest).
- The slice has one enemy; the storyboard drew two.
- Pose mismatches against the sheet (hurt has no squint; defeat has a dot eye and a navy bow; the arms cover the face in win); the idle base disc is redrawn by hand.
- The ElevenLabs sounds cannot be reproduced exactly (no seed; the added game description was not recorded).
- One human tester; Windows only.

## Verification before submitting

- [ ] Fresh clone of the submitted commit runs and passes both test suites (TEST-REPORT §1 commands)
- [ ] `git diff film-source-v1 <submitted-commit> -- godot/` is empty (the film shows the submitted game source)
- [ ] The film file's SHA-256 matches the value above, and the link opens for a reviewer
- [ ] Source ZIP made from the same commit, without `.godot/`, `assets/_raw/`, credentials, or MP4/MP3/WAV files
