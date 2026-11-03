extends SceneTree
## Film capture driver for the Lane Tactics A5 film (isolated copy of tag a5 only).
## Harness file: it lives in film/ of the capture copy and is NOT part of the game.
##
## Run under Godot Movie Maker (window build, not headless):
##   <Godot>.exe --path <copy> --write-movie <out>/<mode>.avi --fixed-fps 30 \
##       --script res://film/a5_capture_driver.gd -- <mode> <out_dir> <ffmpeg.exe>
##   mode: tint | diorama | hint
##
## - The real scene (main.tscn, asset_diorama.tscn or hint_experiment.tscn, unchanged) is instanced inside a
##   3840x2160 SubViewport. For the 2D game the SubViewport draws the 1280x720 canvas scaled up
##   (size_2d_override), as the window's canvas_items stretch would. Every SubViewport frame is piped raw to
##   ffmpeg as a lossless FFV1 4K master (<mode>-4k.mkv); Movie Maker's AVI is a 720p picture of the same frames.
## - tint: real key presses pushed into the SubViewport, the same way the game's tests press keys. Nothing in
##   the game is called or set directly; the driver only reads state to log it and to know when a turn starts.
## - diorama: the scene's own camera, then one harness Camera3D beside the scene. Uniforms are changed at run
##   time on the loaded materials, in memory only; no file is saved. One shot replaces the shared shader's code
##   in memory (ALBEDO x 0.5), reproducing Jiean's one-shader check; the .gdshader file is not touched.
## - Logs every frame; quits nonzero on any failure or skipped draw.

const W := 3840
const H := 2160
const WINDOW := Vector2i(1280, 720)
const FPS := 30

var sub: SubViewport
var scene: Node
var cam: Camera3D
var frame: int = 0
var out_dir: String = ""
var mode: String = "tint"
var ffmpeg_path: String = "ffmpeg"
var log_lines: Array[String] = []
var shots: Array[Dictionary] = []
var failed: String = ""
var notes: Array[String] = []
var last_proc: int = -1
var _pipe: FileAccess
var _ffmpeg_pid: int = -1
var light_mat: ShaderMaterial
var dark_mat: ShaderMaterial


func _initialize() -> void:
	call_deferred("run")


func log_event(kind: String, detail: Variant = "") -> void:
	log_lines.append(JSON.stringify({"frame": frame, "t_s": snappedf(float(frame) / FPS, 0.001),
		"process_frame": Engine.get_process_frames(), "event": kind, "detail": detail}))


func fail(msg: String) -> void:
	if failed == "":
		failed = msg
		log_event("FAIL", msg)
		push_error("CAPTURE FAIL: " + msg)


func expect(cond: bool, msg: String) -> void:
	if cond:
		notes.append("OK: " + msg)
	else:
		fail("expectation failed: " + msg)


func _v(v: Vector3) -> Array:
	return [snappedf(v.x, 0.0001), snappedf(v.y, 0.0001), snappedf(v.z, 0.0001)]


## What the frame shows, for the log.
func state_row() -> Dictionary:
	if mode == "tint":
		var p: Variant = scene.pieces.get("p1")
		var e: Variant = scene.pieces.get("e1")
		return {"state": scene.state_name(), "turn": scene.rules.turn, "planned": str(scene.planned_offset),
			"paused": scene.paused,
			"p1": snappedf(float(p.tint_material().get_shader_parameter("exposed_amount")), 0.0001) if p != null else null,
			"e1": snappedf(float(e.tint_material().get_shader_parameter("exposed_amount")), 0.0001) if e != null else null}
	if mode == "diorama":
		var row: Dictionary = {}
		for k: String in ["uv_scale", "roughness_scale", "normal_strength"]:
			row["light." + k] = light_mat.get_shader_parameter(k)
		row["dark.normal_strength"] = dark_mat.get_shader_parameter("normal_strength")
		var active: Camera3D = sub.get_camera_3d()
		row["camera"] = str(active.name) if active else "none"
		return row
	return {}


## Advance one engine frame (fixed 1/30 s), then pipe the SubViewport frame drawn in it.
func step() -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var pf: int = Engine.get_process_frames()
	if last_proc >= 0 and pf != last_proc + 1:
		fail("frame %d: process frame jumped %d -> %d (a draw was skipped)" % [frame, last_proc, pf])
	last_proc = pf
	var img: Image = sub.get_texture().get_image()
	if img == null or img.get_width() != W or img.get_height() != H:
		fail("frame %d: SubViewport image is not %dx%d" % [frame, W, H])
	else:
		if img.get_format() != Image.FORMAT_RGBA8:
			img.convert(Image.FORMAT_RGBA8)
		_pipe.store_buffer(img.get_data())
	log_event("frame", state_row())
	frame += 1


func hold(seconds: float) -> void:
	for i: int in int(round(seconds * FPS)):
		await step()


func _open_encoder(path: String) -> bool:
	var args: PackedStringArray = ["-hide_banner", "-loglevel", "error", "-nostats", "-y",
		"-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % [W, H], "-framerate", str(FPS), "-i", "-",
		"-c:v", "ffv1", "-level", "3", "-threads", "8", "-slices", "24", "-slicecrc", "1", "-g", "1",
		"-pix_fmt", "bgr0", path]
	var r: Dictionary = OS.execute_with_pipe(ffmpeg_path, args, true)
	if r.is_empty():
		fail("could not start ffmpeg")
		return false
	_pipe = r["stdio"]
	_ffmpeg_pid = int(r["pid"])
	log_event("encoder", {"args": " ".join(args.slice(0, -1))})
	return true


func _close_encoder() -> void:
	if _pipe == null:
		return
	_pipe.close()
	var t0: int = Time.get_ticks_msec()
	while OS.is_process_running(_ffmpeg_pid) and Time.get_ticks_msec() - t0 < 600000:
		OS.delay_msec(100)
	if OS.is_process_running(_ffmpeg_pid):
		fail("ffmpeg did not finish")
	_pipe = null


func smooth(x: float) -> float:
	return x * x * (3.0 - 2.0 * x)


func begin_shot(name: String) -> int:
	log_event("shot_start", name)
	return frame


func end_shot(name: String, start: int, what: String) -> void:
	shots.append({"shot": name, "frames": [start, frame], "seconds": "%d/%d" % [frame - start, FPS], "what": what})
	log_event("shot", shots[-1])


# ---------------------------------------------------------------- tint (2D game, real key presses)

func key(code: Key) -> void:
	for pressed: bool in [true, false]:
		var ev: InputEventKey = InputEventKey.new()
		ev.keycode = code
		ev.physical_keycode = code
		ev.pressed = pressed
		sub.push_input(ev)
	log_event("key", OS.get_keycode_string(code))


## Step until the game is planning a move on the given turn; confirm any attack plan on the way (Enter).
func wait_plan_move(turn: int, max_seconds: float = 30.0) -> void:
	var n: int = 0
	while not (scene.state_name() == "PLAN_MOVE" and scene.rules.turn == turn):
		if scene.state_name() == "PLAN_ATTACK":
			key(KEY_ENTER)
		await step()
		n += 1
		if n > int(max_seconds * FPS):
			fail("turn %d PLAN_MOVE not reached (state %s)" % [turn, scene.state_name()])
			return


func p1() -> float:
	return float(scene.pieces["p1"].tint_material().get_shader_parameter("exposed_amount"))


func run_tint() -> void:
	scene = (load("res://game/main.tscn") as PackedScene).instantiate()
	sub.add_child(scene)
	await step()
	expect(scene.get_node_or_null("ExposedDriver") != null, "main.tscn has the ExposedDriver node")
	var s: int = begin_shot("T0_title")
	await hold(1.5)
	end_shot("T0_title", s, "title card")
	key(KEY_ENTER)
	await wait_plan_move(1)
	s = begin_shot("T1_turns_1_2")
	await hold(1.0)
	for t: int in [1, 2]:
		key(KEY_RIGHT)
		await hold(0.6)
		key(KEY_ENTER)
		await wait_plan_move(t + 1)
		await hold(0.4)
	end_shot("T1_turns_1_2", s, "turns 1-2: step right twice, out of reach; value stays 0")
	expect(p1() == 0.0, "p1 value 0 before turn 3")
	s = begin_shot("T2_fade_in")
	await hold(1.5)
	key(KEY_RIGHT) # plan (3,4): inside the enemy's reach
	await hold(4.0)
	end_shot("T2_fade_in", s, "turn 3: Right plans a square in reach; tint rises 0 -> 1 in 0.20 s")
	expect(p1() == 1.0, "p1 value 1 after the rise")
	s = begin_shot("T3_fade_out")
	key(KEY_LEFT) # back to standing still, out of reach
	await hold(3.3)
	end_shot("T3_fade_out", s, "Left: out of reach; tint falls 1 -> 0 in 0.20 s")
	s = begin_shot("T4_retrigger")
	await hold(0.5)
	for i: int in 6:
		key(KEY_RIGHT if i % 2 == 0 else KEY_LEFT)
		await hold(0.1)
	key(KEY_RIGHT)
	await hold(3.4)
	end_shot("T4_retrigger", s, "fast taps every 0.1 s: the value turns around from where it is, never jumps")
	s = begin_shot("T5_pause")
	key(KEY_LEFT)
	await hold(0.1)
	key(KEY_P)
	await hold(2.0)
	key(KEY_P)
	await hold(1.0)
	end_shot("T5_pause", s, "Left, then P mid-fade: the value holds while paused, then finishes the fall")
	s = begin_shot("T6_confirm_and_turn4")
	key(KEY_RIGHT)
	await hold(1.0)
	key(KEY_ENTER) # confirm the move into reach: PLAY_MOVES ends the state
	await wait_plan_move(4)
	await hold(6.0)
	end_shot("T6_confirm_and_turn4", s, "Enter confirms: the tint fades while the move plays; turn 4 starts in reach, so it rises again")
	_finish()


# ---------------------------------------------------------------- diorama (3D, two materials, one shader)

func aim(pos: Vector3, target: Vector3) -> void:
	cam.global_position = pos
	cam.look_at(target, Vector3.UP)


## Animate one uniform from a to b over seconds (eased), on one material.
func ramp(mat: ShaderMaterial, param: String, a: float, b: float, seconds: float) -> void:
	var n: int = int(round(seconds * FPS))
	for i: int in n:
		mat.set_shader_parameter(param, lerpf(a, b, smooth(float(i + 1) / float(n))))
		await step()


func run_diorama() -> void:
	scene = (load("res://diorama/asset_diorama.tscn") as PackedScene).instantiate()
	sub.add_child(scene)
	cam = Camera3D.new()
	cam.name = "HarnessCamera"
	cam.fov = 50.0
	sub.add_child(cam)
	await process_frame
	var lt: MeshInstance3D = scene.get_node("LinenSquareLight") as MeshInstance3D
	var dk: MeshInstance3D = scene.get_node("LinenSquareDark") as MeshInstance3D
	light_mat = lt.get_surface_override_material(0) as ShaderMaterial
	dark_mat = dk.get_surface_override_material(0) as ShaderMaterial
	expect(light_mat.resource_path == "res://materials/linen_light.tres", "light tile uses linen_light.tres")
	expect(dark_mat.resource_path == "res://materials/linen_dark.tres", "dark tile uses linen_dark.tres")
	expect(light_mat.shader == dark_mat.shader, "both materials share one Shader object")
	var shader: Shader = light_mat.shader
	var original_code: String = shader.code
	# defaults the materials leave to the shader
	light_mat.set_shader_parameter("uv_scale", 3.65)
	light_mat.set_shader_parameter("roughness_scale", 1.0)
	# close enough that the weave reads at 4K; both tiles still in frame
	var front: Vector3 = Vector3(0.0, 0.9, 1.95)
	var tiles: Vector3 = Vector3(0.0, 0.0, 0.95)
	# the lamp's mirror direction off the light tile, from the lamp's own transform (light travels along -Z)
	var lamp: DirectionalLight3D = scene.get_node("Lamp") as DirectionalLight3D
	var d: Vector3 = -lamp.global_basis.z.normalized()
	var mirror: Vector3 = Vector3(d.x, -d.y, d.z)
	var lt_centre: Vector3 = lt.global_position
	log_event("lamp", {"travel": _v(d), "mirror": _v(mirror), "light_tile": _v(lt_centre)})

	var s: int = begin_shot("D0_scene_camera")
	(scene.get_node("Camera3D") as Camera3D).make_current()
	await hold(4.5)
	end_shot("D0_scene_camera", s, "the diorama through its own camera, as saved: two linen tiles in front of the A3 models")
	cam.make_current()
	aim(front, tiles)
	s = begin_shot("D1_close_default")
	await hold(3.0)
	end_shot("D1_close_default", s, "harness camera over the tiles; both materials at their saved values")
	s = begin_shot("D2_uv_scale")
	await hold(1.0)
	await ramp(light_mat, "uv_scale", 3.65, 0.5, 2.0)
	await hold(2.0)
	await ramp(light_mat, "uv_scale", 0.5, 8.0, 2.0)
	await hold(1.5)
	await ramp(light_mat, "uv_scale", 8.0, 3.65, 1.0)
	end_shot("D2_uv_scale", s, "light tile uv_scale 3.65 -> 0.5 -> 8.0 -> 3.65 (in memory only)")
	s = begin_shot("D3_normal_strength")
	await ramp(light_mat, "normal_strength", 1.0, 0.0, 1.5)
	await hold(1.5)
	await ramp(light_mat, "normal_strength", 0.0, 2.0, 1.5)
	await hold(1.5)
	await ramp(light_mat, "normal_strength", 2.0, 1.0, 0.5)
	end_shot("D3_normal_strength", s, "light tile normal_strength 1 -> 0 -> 2 -> 1 (in memory only)")
	# from the mirror side of the lamp, where a glossy surface shows its highlight
	aim(lt_centre + mirror * 1.2, lt_centre)
	s = begin_shot("D4_roughness")
	await hold(1.0)
	await ramp(light_mat, "roughness_scale", 1.0, 0.0, 2.0)
	await hold(3.5)
	await ramp(light_mat, "roughness_scale", 0.0, 1.0, 1.0)
	end_shot("D4_roughness", s, "light tile roughness_scale 1 -> 0 -> 1, seen from the lamp's mirror side (in memory only)")
	aim(front, tiles)
	s = begin_shot("D5_one_material")
	await hold(1.5)
	await ramp(dark_mat, "normal_strength", 1.5, 0.0, 1.5)
	await hold(2.0)
	await ramp(dark_mat, "normal_strength", 0.0, 1.5, 1.0)
	end_shot("D5_one_material", s, "linen_dark normal_strength 1.5 -> 0 -> 1.5: only the dark tile changes (in memory only)")
	s = begin_shot("D6_one_shader")
	await hold(1.0)
	var edited: String = original_code.replace("* tint.rgb;", "* tint.rgb * 0.5;")
	expect(edited != original_code, "the ALBEDO line was found in the shader code")
	shader.code = edited
	log_event("shader_code", "ALBEDO line x 0.5 (in memory)")
	await hold(2.5)
	shader.code = original_code
	log_event("shader_code", "restored")
	await hold(1.0)
	end_shot("D6_one_shader", s, "shader code ALBEDO x 0.5 in memory: both tiles darken; then restored")
	_finish()


# ---------------------------------------------------------------- hint experiment

func run_hint() -> void:
	scene = (load("res://hint/hint_experiment.tscn") as PackedScene).instantiate()
	sub.add_child(scene)
	await process_frame
	var s: int = begin_shot("H0_two_quads")
	await hold(4.0)
	end_shot("H0_two_quads", s, "hint_experiment.tscn through its own orthographic camera")
	var img: Image = sub.get_texture().get_image()
	var bands: Dictionary = {}
	for q: Array in [["A_top", int(H * 0.325)], ["B_bottom", int(H * 0.675)]]:
		var row: Array = []
		for x: int in [W / 2 - 900, W / 2, W / 2 + 900]:
			row.append(img.get_pixel(x, q[1]).r8)
		bands[q[0]] = row
	log_event("bands", bands)
	notes.append("bands at 4K: %s" % str(bands))
	_finish()


# ----------------------------------------------------------------

func run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	mode = args[0] if args.size() > 0 else "tint"
	out_dir = args[1] if args.size() > 1 else ProjectSettings.globalize_path("res://../film-out")
	ffmpeg_path = args[2] if args.size() > 2 else "ffmpeg"
	DirAccess.make_dir_recursive_absolute(out_dir)
	if not _open_encoder(out_dir.path_join("%s-4k.mkv" % mode)):
		quit(1)
		return
	sub = SubViewport.new()
	sub.size = Vector2i(W, H)
	sub.own_world_3d = true
	sub.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	if mode == "tint":
		sub.size_2d_override = WINDOW
		sub.size_2d_override_stretch = true
	root.add_child(sub)
	var view: TextureRect = TextureRect.new()
	view.texture = sub.get_texture()
	view.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	view.stretch_mode = TextureRect.STRETCH_SCALE
	view.size = Vector2(WINDOW)
	root.add_child(view)
	log_event("capture_start", {"mode": mode, "engine": Engine.get_version_info().get("string", ""),
		"renderer": RenderingServer.get_current_rendering_method(), "subviewport": str(sub.size),
		"size_2d_override": str(sub.size_2d_override), "movie": OS.has_feature("movie")})
	match mode:
		"tint":
			await run_tint()
		"diorama":
			await run_diorama()
		"hint":
			await run_hint()
		_:
			fail("unknown mode " + mode)
			_finish()


func _finish() -> void:
	_close_encoder()
	log_event("capture_end", {"frames": frame, "failed": failed})
	var f: FileAccess = FileAccess.open(out_dir.path_join("%s-log.jsonl" % mode), FileAccess.WRITE)
	for line: String in log_lines:
		f.store_line(line)
	f.close()
	var summary: Dictionary = {"mode": mode, "frames": frame, "fps": FPS, "failed": failed, "notes": notes,
		"shots": shots, "master": "%s-4k.mkv (FFV1 lossless, bgr0)" % mode, "subviewport": [W, H]}
	var sfile: FileAccess = FileAccess.open(out_dir.path_join("%s-summary.json" % mode), FileAccess.WRITE)
	sfile.store_string(JSON.stringify(summary, "\t"))
	sfile.close()
	print("CAPTURE %s: %d frames, failed='%s'" % [mode, frame, failed])
	quit(0 if failed == "" else 1)
