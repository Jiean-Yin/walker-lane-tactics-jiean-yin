# BUILD-PROMPT — how to rebuild this film

Paste into Claude Code with the Brutalist checkout available. Paths are this machine's; adjust as needed.

```text
godot-gamedev walker <repo>

Read skills/make/godot-gamedev/SKILL.md and references/evidence.md, ai-explainer, riff,
godot-waikthrough's capture contract, RENDER-TARGETS.md, PIPELINE-SAFETY.md and OUTRO-LOCK.md.
Film the game at tag film-source-v1 only, on an isolated `git archive` copy.
Capture with capture/film_capture_driver.gd under Godot Movie Maker (--write-movie, --fixed-fps 30):
the real main scene in a 3840x2160 SubViewport, input events only, route fixtures from
tests/fixtures; check capture/run-03-summary.json (22/22) and the AVI/4K frame join.
Use beat_sheet.json as the script (Liam in for Bear, Kokoro am_onyx). Gameplay beats are exact
frame ranges with the scripted-input label; B14 is the slice-audio segment (kind source_report,
audio_policy preserve) with the AVI audio of the same run and no narration.
Outro: ClaudeTitleOutro, exact title, @NikBearBrown, voiced title + "At Nik Bear Brown." + 1.0 s
silent tail. Run ./art godot-gamedev --check REEL --game <repo>/godot, render, then watch and QC.
Do not publish.
```

## Commands actually used (Windows 11, Git Bash)

```bash
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PATH="<brutalist>/.venv/Scripts:$PATH"
REEL=<repo>/youtube/claude-liam-walker-lane-tactics-jiean-yin-gamedev
# isolated copy + tests
git -C <repo> archive film-source-v1 godot | tar -x -C <capture-copy>
G=<Godot>/Godot_v4.7.2-stable_win64_console.exe
$G --headless --path film-source-v1-godot --import
$G --headless --path film-source-v1-godot --script res://tests/test_rules.gd
$G --headless --path film-source-v1-godot --script res://tests/test_audio_events.gd
# capture (driver copied into the isolated copy as film/film_capture_driver.gd)
<Godot>/Godot_v4.7.2-stable_win64.exe --path film-source-v1-godot --write-movie <capture-copy>/run-03/run-03.avi \
  --fixed-fps 30 --script res://film/film_capture_driver.gd -- full <capture-copy>/run-03 <ffmpeg.exe>
# script, narration, media (reel folder)
python tools/build_sheet.py                      # authoring record; later edits were made in place
python3 <brutalist>/runtime/scripts/generate_audio_kokoro.py $REEL
python tools/pad_narration.py                    # lead/tail silence, frame-aligned beat audio
python tools/make_clips.py <capture-copy>/run-03
python tools/make_stills.py <capture-copy>/run-03 <capture-copy>/hires
python tools/set_props.py                        # highlight cues bound to measured narration
python3 <brutalist>/runtime/scripts/remotion_scenes.py $REEL
python tools/burn_labels.py                      # on-screen disclosure labels on reconstructed views
python tools/build_evidence.py
# checks and cuts (Brutalist folder)
./art godot-gamedev --check $REEL --game <repo>/godot
./art run $REEL --height 1080                    # review cut (approval-gate preview)
./art final $REEL --height 2160 --fps 30 --out $REEL/exports/landscape   # after approval only
python tools/check_audio.py <film.mp4> --offset <B14 start>
```

The SVG design sketches shown in B04 were rendered at 4× with headless Edge into `<capture-copy>\hires\` (same method as `design/tools/render_png.sh`, scale factor 4).

**Local Brutalist patch (Windows portability, from Assignment 1, not upstream):** `runtime/scripts/remotion_scenes.py` runs `npx` by bare name, which Windows `subprocess` cannot resolve (`npx.cmd`); it was changed to `shutil.which("npx") or "npx"`. **Second local patch (this film):** `runtime/remotion/src/scenes/ClaudeTitleOutro.tsx`, mascot wrapper `marginTop: 28` → `28 + Math.ceil((35 / 86) * mascotH)` (headroom for the jump/celebrate travel, so the mascot stays below the handle as OUTRO-LOCK requires; this reel's slug seeds `jump`). Review/final cuts use `ART_NO_DRAWTEXT=1`. No other toolkit file was edited for this film.
