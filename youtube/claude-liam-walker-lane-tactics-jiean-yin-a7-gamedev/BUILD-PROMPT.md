# BUILD-PROMPT — how to rebuild this film

Paste into Claude Code with the Brutalist checkout available.

```text
godot-gamedev walker <repo>

Read skills/make/godot-gamedev/SKILL.md and references/evidence.md, ai-explainer, riff, RENDER-TARGETS.md,
PIPELINE-SAFETY.md and OUTRO-LOCK.md. Film the Assignment 7 animations at tag a7 only, on an isolated
`git -c core.autocrlf=false archive` copy. Capture with capture/a7_capture_driver.gd under Godot Movie Maker
(--write-movie), modes play (--fixed-fps 30) and slow (--fixed-fps 120, shown at 1/4 speed and labelled), each
the real game/main.tscn in a 3840x2160 SubViewport; check capture/<mode>-summary.json. Use Jiean's committed
strips as labelled fixture stills. Use beat_sheet.json as the script (approved by Jiean; Liam in for Bear,
Kokoro am_onyx; the voice says the name "Jay-Ann"). Jiean's words come from the tag only (tools/build_sheet.py).
Outro: ClaudeTitleOutro, exact title, @NikBearBrown, voiced title + "At Nik Bear Brown." + 1.0 s silent tail.
Run ./art godot-gamedev --check REEL --game <capture-copy>/a7/godot, render, then watch and QC.
Do not publish, commit or push.
```

## Commands actually used (Windows 11, Git Bash)

```bash
export PYTHONUTF8=1 CAPTURE=<capture-copy> BRUTALIST=<brutalist> RUN=final-out
PY=<brutalist>/.venv/Scripts/python.exe
REEL=<repo>/youtube/claude-liam-walker-lane-tactics-jiean-yin-a7-gamedev
git -C <repo> -c core.autocrlf=false archive a7 | tar -x -C <capture-copy>/a7   # every godot/ file checked against its blob
"$GODOT" --headless --path <capture-copy>/a7/godot --import                    # then every suite via scripts/run-test.sh
cp -r <capture-copy>/a7/godot <capture-copy>/capture-godot                       # + film/a7_capture_driver.gd (harness only)
<Godot console exe> --path <capture-copy>/capture-godot --write-movie <capture-copy>/final-out/play.avi \
    --fixed-fps 30 --script res://film/a7_capture_driver.gd -- play <capture-copy>/final-out <ffmpeg> 30
<Godot console exe> --path <capture-copy>/capture-godot --write-movie <capture-copy>/final-out/slow.avi \
    --fixed-fps 120 --script res://film/a7_capture_driver.gd -- slow <capture-copy>/final-out <ffmpeg> 120
python tools/build_sheet.py                                  # the approved script; code and quotes read from the a7 copy
$PY <brutalist>/runtime/scripts/generate_audio_kokoro.py $REEL
python tools/set_segments.py && python tools/pad_narration.py   # footage ranges; frame-exact beat audio, never retimed
python tools/fit_workbench.py && python tools/set_props.py      # code excerpts fitted; highlight cues from the narration
$PY tools/make_media.py                                         # engine beats and evidence stills
$PY <brutalist>/runtime/scripts/remotion_scenes.py $REEL
python tools/burn_labels.py
python tools/build_evidence.py <capture-copy>/a7/godot
python tools/write_shotlist.py && python tools/set_label_regions.py
export PATH="<brutalist>/.venv/Scripts:$PATH"
cd <brutalist> && ./art godot-gamedev --check $REEL --game <capture-copy>/a7/godot
ART_NO_DRAWTEXT=1 ./art final $REEL --height 2160 --fps 30 --out $REEL/exports/landscape
$PY $REEL/tools/qc_master.py $REEL/exports/landscape/<slug>.mp4
```

- **Order:** the narration was voiced before the panels were fitted, because the Kokoro step rewrites the beat sheet. `fit_workbench.py` and `set_props.py` run after it.
- **Toolkit:** the Brutalist checkout carries the same local Windows patches as the A5 and A6 films (`npx.cmd`, outro mascot headroom). They are not upstream. No toolkit file was edited for this film.
