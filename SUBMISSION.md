# SUBMISSION — Assignment 3: Your First 3D Game Assets with Claude, the Blender MCP, and Blender

| Field | Value |
|---|---|
| Assignment | Assignment 3 - Your First 3D Game Assets with Claude, the Blender MCP, and Blender |
| Student | Jiean Yin |
| Project name | walker-lane-tactics-jiean-yin (Lane Tactics) |
| GitHub repository URL | https://github.com/Jiean-Yin/walker-lane-tactics-jiean-yin |
| Git tag and submitted commit SHA | tag `a3`; the submitted commit SHA is given in the Canvas note (a commit cannot contain its own SHA) |
| Game-source revision shown in the film | `e415255` (`godot/` there is identical to the submitted tag's `godot/`: checked with `git diff e415255 a3 -- godot`, empty) |
| Godot version, Blender version, and operating system | Godot 4.7.2.stable.official.ed1daf0bf (standard build, Compatibility renderer) · Blender 5.2.2 LTS (glTF 2.0 add-on 5.2.40) · Windows 11 Home 10.0.26200 |
| The three assets and what each is for | **`archer_piece`** (0.40 × 0.40 × 0.80 m, 254 tris): the game's unit, the carved wooden archer from my 2D slice. **`board_square`** (1.00 × 1.00 × 0.05 m, 60 tris): the tile the five-lane board is made of; 1 square = 1 m sets the game's scale. **`goal_flag`** (0.45 × 0.30 × 1.20 m, 84 tris): marks the enemy back row you must reach to win. Shown side by side in `godot/diorama/asset_diorama.tscn` (floor, one light, camera) |
| MCP project and version, or "script route" | **MCP route for all three assets**: [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) **2.1.9** (PyPI), Blender add-on 1.8, run with `uvx` (uv 0.13.1) from Claude Code 2.1.295; telemetry off; every asset library and generator off. Export was done afterwards with headless Blender (`tools/blender/export_glb.py`), from the committed .blend files, by my choice |
| My hand edit in Blender | In Blender's window, in Edit Mode, I selected only the archer's bow (L) and moved it +0.08 m along Y (G Y 0.08), so the eye shows in profile; the bow had hidden it. Checked afterwards: bow y 0.05…0.11, size, scale and 254 triangles unchanged (TEST-REPORT A3.6, cycle 1) |
| Checks run (command and result) | `blender.exe -b --factory-startup --python-exit-code 1 --python tools/blender/export_glb.py -- <committed .blend copies> godot/assets/models` → exit 0, 3 GLB files. `Godot_v4.7.2-stable_win64_console.exe --headless --path godot --import` → exit 0, no error lines. `timeout 120 Godot_v4.7.2-stable_win64_console.exe --headless --path godot --script res://tests/check_assets.gd --fixed-fps 60` → **38/38** (`evidence/check_assets-1792106192.json`); the first run of that check was faulty and is kept (`evidence/check_assets-1792106172.json`, 32/33). Human look check: TEST-REPORT A3.5. Fresh-clone check of tag `a3`: TO FILL |
| Final film URL and filename | https://youtu.be/Cb2F8_0mYhk (YouTube, @JieanYin; video title "3D Game Assets with Claude, the Blender MCP, and Blender"; film title card "Lane Tactics in 3D: A Piece, a Square, a Goal") · `claude-liam-walker-lane-tactics-jiean-yin-a3-gamedev.mp4` ("Lane Tactics in 3D: A Piece, a Square, a Goal", 4:41.5, 3840 × 2160, 30 fps; kept out of GitHub) |
| Final film SHA-256 | `83d2489e2ee1f6e6c2d5ffc1df5387f086fba0c51a983904e08b93a2d4ad4240` |
| Summary of my changes | A3 brief with sizes, origins, budgets and six predicted failures, committed before any build (`78b213f`). Blender MCP set up on Windows (the course's `claude mcp add -e …` line failed; fixed form logged). Three assets built through the MCP, one Claude call per part, each in its own .blend with its code in `tools/blender/`. My hand edit (bow). Brief revision A3-R1 (darker board border, my choice from four options). Headless export, Godot import, a 3D diorama scene and a headless check. TEST-REPORT, FRICTIONAL, BLENDER-NOTES, SOURCES and README updated. Explainer film |
| Known limitations | The flag is edge-on and almost invisible from the side; the bow reads more like a staff. The headless check cannot see rendering; the visual evidence is my look check. Godot generates LODs on import, which the check does not look at. The diorama .tscn was written by hand. One computer (Windows), one tester. TO FILL (anything from your look check) |
| Changed games since Assignment 2 | No |

## Verification before submitting

- [ ] Fresh clone of tag `a3` into an empty folder: import, run `check_assets.gd` (38/38), open the diorama scene
- [ ] `git diff e415255 a3 -- godot` is empty (the film shows the submitted game source)
- [ ] The film's SHA-256 matches the value above, and the link opens for a reviewer (signed out)
- [ ] Source ZIP made from the same commit, without `.godot/`, `.blend1`, credentials or MP4/MP3/WAV files
