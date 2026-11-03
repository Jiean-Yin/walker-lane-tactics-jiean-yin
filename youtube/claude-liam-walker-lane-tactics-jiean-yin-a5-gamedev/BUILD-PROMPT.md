# BUILD-PROMPT — how to rebuild this film

Paste into Claude Code with the Brutalist checkout available.

```text
godot-gamedev walker <repo>

Read skills/make/godot-gamedev/SKILL.md and references/evidence.md, ai-explainer, riff, RENDER-TARGETS.md,
PIPELINE-SAFETY.md and OUTRO-LOCK.md. Film the Assignment 5 shaders at tag a5 only, on an isolated
`git -c core.autocrlf=false archive` copy. Capture with capture/a5_capture_driver.gd under Godot Movie Maker
(--write-movie, --fixed-fps 30), modes tint, diorama and hint, each the real scene in a 3840x2160 SubViewport;
check capture/<mode>-summary.json. Use Jiean's committed captures as labelled stills. Use beat_sheet.json as the
script (approved by Jiean; Liam in for Bear, Kokoro am_onyx; the voice says the name "Jay-Ann").
Outro: ClaudeTitleOutro, exact title, @NikBearBrown, voiced title + "At Nik Bear Brown." + 1.0 s silent tail.
Run ./art godot-gamedev --check REEL --game <capture-copy>/a5/godot, render, then watch and QC.
Do not publish, commit or push.
```

## Commands actually used (Windows 11, Git Bash)

```bash
export PYTHONUTF8=1 CAPTURE=<capture-copy> BRUTALIST=<brutalist>
PY=<brutalist>/.venv/Scripts/python.exe
REEL=<repo>/youtube/claude-liam-walker-lane-tactics-jiean-yin-a5-gamedev
# isolated copy, every godot/ file checked against its a5 blob
git -C <repo> -c core.autocrlf=false archive a5 godot scripts evidence/a5 CHANGE-BRIEF.md TEST-REPORT.md \
    FRICTIONAL.md LANGUAGE-NOTES.md SOURCES.md | tar -x -C <capture-copy>/a5
"$GODOT" --headless --path <capture-copy>/a5/godot --import        # then every suite via scripts/run-test.sh
cp -r <capture-copy>/a5/godot <capture-copy>/capture-godot          # + film/a5_capture_driver.gd (harness only)
for m in tint diorama hint; do
  <Godot window exe> --path <capture-copy>/capture-godot --write-movie <capture-copy>/run-02/$m.avi --fixed-fps 30 \
    --script res://film/a5_capture_driver.gd -- $m <capture-copy>/run-02 <ffmpeg>
done
$PY tools/build_sheet.py                                    # the approved script; code read from the a5 copy
$PY <brutalist>/runtime/scripts/generate_audio_kokoro.py $REEL
$PY tools/set_segments.py && $PY tools/pad_narration.py     # frame-exact beat audio; footage never retimed
$PY tools/make_media.py                                     # engine beats and evidence stills
$PY tools/set_props.py && $PY tools/patch_props_r1.py       # highlight cues; code size 30 after the pilot
$PY <brutalist>/runtime/scripts/remotion_scenes.py $REEL --only <beat> [--force]
$PY tools/burn_labels.py                                    # B00 and BHTF reconstruction labels
$PY tools/build_evidence.py <capture-copy>/a5/godot
cd <brutalist> && ./art godot-gamedev --check $REEL --game <capture-copy>/a5/godot
ART_NO_DRAWTEXT=1 ./art final $REEL --height 2160 --fps 30 --out $REEL/exports/landscape
$PY $REEL/tools/qc_master.py $REEL/exports/landscape/<slug>.mp4
```

Local Brutalist patches carried over from earlier assignments (Windows `npx.cmd`; outro mascot headroom), not upstream. No toolkit file was edited for this film.
