# BUILD-PROMPT — how to rebuild this film

Paste into Claude Code with the Brutalist checkout available.

```text
godot-gamedev walker <repo>

Read skills/make/godot-gamedev/SKILL.md and references/evidence.md, ai-explainer, riff, RENDER-TARGETS.md,
PIPELINE-SAFETY.md and OUTRO-LOCK.md. Film the Assignment 6 particle effects at tag a6 only, on an isolated
`git -c core.autocrlf=false archive` copy. Capture with capture/a6_capture_driver.gd under Godot Movie Maker
(--write-movie), modes play (--fixed-fps 30) and slow (--fixed-fps 120, shown at 1/4 speed and labelled), each
the real game/main.tscn in a 3840x2160 SubViewport; check capture/<mode>-summary.json. Use Jiean's committed
strips as labelled fixture stills. Use beat_sheet.json as the script (approved by Jiean; Liam in for Bear,
Kokoro am_onyx; the voice says the name "Jay-Ann"). Jiean's words come from the tag only (tools/quotes.py).
Outro: ClaudeTitleOutro, exact title, @NikBearBrown, voiced title + "At Nik Bear Brown." + 1.0 s silent tail.
Run ./art godot-gamedev --check REEL --game <capture-copy>/a6/godot, render, then watch and QC.
Do not publish, commit or push.
```

## Commands actually used (Windows 11, Git Bash)

```bash
export PYTHONUTF8=1 CAPTURE=<capture-copy> BRUTALIST=<brutalist> REPO=<repo> RUN=final-out
PY=<brutalist>/.venv/Scripts/python.exe
REEL=<repo>/youtube/claude-liam-walker-lane-tactics-jiean-yin-a6-gamedev
# isolated copy of the tag, every godot/ file checked against its a6 blob (git hash-object --no-filters)
git -C <repo> -c core.autocrlf=false archive a6 | tar -x -C <capture-copy>/a6
"$GODOT" --headless --path <capture-copy>/a6/godot --import         # then every suite via scripts/run-test.sh
cp -r <capture-copy>/a6/godot <capture-copy>/capture-godot           # + film/a6_capture_driver.gd (harness only)
<Godot console exe> --path <capture-copy>/capture-godot --write-movie <capture-copy>/final-out/play.avi \
    --fixed-fps 30 --script res://film/a6_capture_driver.gd -- play <capture-copy>/final-out <ffmpeg> 30
<Godot console exe> --path <capture-copy>/capture-godot --write-movie <capture-copy>/final-out/slow.avi \
    --fixed-fps 120 --script res://film/a6_capture_driver.gd -- slow <capture-copy>/final-out <ffmpeg> 120
$PY tools/quotes.py                                         # Jiean's words, verbatim from the tag copy
$PY tools/build_sheet.py                                    # the approved script; code read from the a6 copy
$PY <brutalist>/runtime/scripts/generate_audio_kokoro.py $REEL
$PY tools/anchors.py                                        # event frames per shot (read-only)
$PY tools/set_segments.py && $PY tools/pad_narration.py     # footage ranges; frame-exact beat audio, never retimed
$PY tools/fit_workbench.py                                  # code excerpts and notes fitted to the panel
$PY tools/set_props.py                                      # code-line highlight cues from the narration
$PY tools/make_media.py                                     # engine beats and evidence stills
$PY <brutalist>/runtime/scripts/remotion_scenes.py $REEL
$PY tools/burn_labels.py                                    # B00 and BHTF reconstruction labels
$PY tools/build_evidence.py <capture-copy>/a6/godot
$PY tools/write_shotlist.py
$PY tools/set_label_regions.py                              # each footage beat's QC region = its label pill
export PATH="<brutalist>/.venv/Scripts:$PATH"               # ./art calls python3 (the Windows one is a store stub)
cd <brutalist> && ./art godot-gamedev --check $REEL --game <capture-copy>/a6/godot
ART_NO_DRAWTEXT=1 ./art final $REEL --height 2160 --fps 30 --out $REEL/exports/landscape
$PY $REEL/tools/qc_master.py $REEL/exports/landscape/<slug>.mp4
```

- **Order:** the narration was voiced in two passes, because five beats quote Jiean. `DRAFT=1 tools/build_sheet.py` writes `beat_sheet.draft.json` with those five beats marked `[PLACEHOLDER]`, which Kokoro skips. Their voice excerpts were added after Jiean approved them (`capture/QUOTES-REVIEW.md`).
- **Toolkit:** the Brutalist checkout carries the same local patches as the A5 film (Windows `npx.cmd`; outro mascot headroom). They are not upstream. No toolkit file was edited for this film.
