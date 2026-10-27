# BUILD-PROMPT — how to rebuild this film

Paste into Claude Code with the Brutalist checkout available. Paths are this machine's; adjust as needed.

```text
godot-gamedev walker <repo>

Read skills/make/godot-gamedev/SKILL.md and references/evidence.md, ai-explainer, riff,
godot-waikthrough's capture contract, RENDER-TARGETS.md, PIPELINE-SAFETY.md and OUTRO-LOCK.md.
Film the Assignment 3 assets at commit e415255 only, on an isolated `git -c core.autocrlf=false archive` copy.
Capture res://diorama/asset_diorama.tscn with capture/diorama_orbit_driver.gd under Godot Movie Maker
(--write-movie, --fixed-fps 30): the real scene in a 3840x2160 SubViewport, shot A through the scene's own
camera, shots B-F through one harness camera beside the scene; check capture/run-02-summary.json.
Use the student's recordings only as labelled excerpts with their real timecodes (see CAPTURE.md), cropped to
the conversation column in the flag clip. Use beat_sheet.json as the script (Liam in for Bear, Kokoro am_onyx).
Outro: ClaudeTitleOutro, exact title, @NikBearBrown, voiced title + "At Nik Bear Brown." + 1.0 s silent tail.
Run ./art godot-gamedev --check REEL --game <capture-copy>/e415255/godot, render, then watch and QC.
Do not publish, commit or push.
```

## Commands actually used (Windows 11, Git Bash)

```bash
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PATH="<brutalist>/.venv/Scripts:$PATH"
REEL=<repo>/youtube/claude-liam-walker-lane-tactics-jiean-yin-a3-gamedev
G=<Godot>/Godot_v4.7.2-stable_win64_console.exe
# isolated copies (outside the repo); every godot/ file checked against its blob with git hash-object
git -C <repo> -c core.autocrlf=false archive e415255 godot tools/blender evidence/check_assets-1792106192.json \
    evidence/check_assets-1792106172.json CHANGE-BRIEF.md TEST-REPORT.md FRICTIONAL.md | tar -x -C <capture-copy>/e415255
cp -r <capture-copy>/e415255/godot <capture-copy>/capture-godot   # + film/diorama_orbit_driver.gd (harness only)
$G --headless --path <capture-copy>/e415255/godot --import
$G --headless --path <capture-copy>/e415255/godot --script res://tests/check_assets.gd --fixed-fps 60   # 38/38
$G --headless --path <capture-copy>/capture-godot --import
# engine capture (run-02)
<Godot>/Godot_v4.7.2-stable_win64.exe --path <capture-copy>/capture-godot --write-movie <capture-copy>/run-02/orbit.avi \
  --fixed-fps 30 --script res://film/diorama_orbit_driver.gd -- full <capture-copy>/run-02 <ffmpeg.exe>
python tools/join_check.py <capture-copy>/run-02
# script, narration, media (reel folder); the film tools read these and have no built-in paths
export FOOTAGE=<footage> CAPTURE=<capture-copy> BRUTALIST=<brutalist>
python tools/build_sheet.py                      # authoring record; later edits were made in place in beat_sheet.json
python3 <brutalist>/runtime/scripts/generate_audio_kokoro.py $REEL
python tools/pad_narration.py                    # lead/tail silence, frame-exact beat audio
python tools/make_media.py                       # footage beats, engine beats, evidence stills (FOOTAGE, CAPTURE, BRUTALIST env)
python tools/set_props.py                        # GodotDevWorkbench highlight cues bound to measured narration
python3 <brutalist>/runtime/scripts/remotion_scenes.py $REEL --only <beat>   # each Remotion beat
python tools/burn_labels.py                      # disclosure labels on reconstructed views
python tools/build_evidence.py <capture-copy>/e415255/godot <capture-copy>/e415255/tools/blender
# checks and the final cut (Brutalist folder)
./art godot-gamedev --check $REEL --game <capture-copy>/e415255/godot
ART_NO_DRAWTEXT=1 ./art final $REEL --height 2160 --fps 30 --out $REEL/exports/landscape
python tools/qc_master.py $REEL/exports/landscape/<slug>.mp4    # frame sheet + loudness per beat
```

**Local Brutalist patches (Windows portability, carried over from Assignments 1–2, not upstream):** `runtime/scripts/remotion_scenes.py` runs `npx` through `shutil.which("npx")` (Windows `npx.cmd`); `runtime/remotion/src/scenes/ClaudeTitleOutro.tsx` gives the mascot headroom below the handle (`marginTop: 28 + Math.ceil((35 / 86) * mascotH)`). No toolkit file was edited for this film.
