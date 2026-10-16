extends SceneTree
## Film capture driver for the Lane Tactics A3 asset diorama (isolated copy of commit e415255 only).
## Harness file: it lives in film/ of the capture copy and is NOT part of the game.
##
## Run under Godot Movie Maker:
##   Godot_v4.7.2-stable_win64.exe --path <copy> --write-movie <out>/orbit.avi --fixed-fps 30 \
##       --script res://film/diorama_orbit_driver.gd -- <mode> <out_dir> <ffmpeg.exe>
##   mode: probe | full
##
## - The real scene res://diorama/asset_diorama.tscn (unchanged) is instanced inside a 3840x2160 SubViewport
##   with its own World3D. A TextureRect shows the SubViewport in the 1280x720 window, so Movie Maker's AVI
##   is a 720p picture of the same frames. Every SubViewport frame is also piped raw (RGBA) to ffmpeg as a
##   lossless FFV1 4K master (orbit-4k.mkv).
## - Shot A uses the scene's own Camera3D. All other shots use ONE harness Camera3D, added beside the scene
##   (not inside it), that moves on a scripted path and looks at a target. Nothing in the scene is moved,
##   added to or edited; the driver only reads node positions to aim the camera.
## - The SubViewport keeps the project's rendering defaults (no MSAA, no FXAA, no debanding): the project
##   sets none, so none are added here.
## - Logs the shot ranges and the camera transform per frame; asserts the scene content; quits nonzero on
##   any failure or skipped draw.

const W := 3840
const H := 2160
const WINDOW := Vector2i(1280, 720)
const FPS := 30

var sub: SubViewport
var scene: Node3D
var cam: Camera3D
var frame: int = 0
var out_dir: String = ""
var mode: String = "full"
var ffmpeg_path: String = "ffmpeg"
var log_lines: Array[String] = []
var shots: Array[Dictionary] = []
var failed: String = ""
var notes: Array[String] = []
var last_proc: int = -1
var _pipe: FileAccess
var _ffmpeg_pid: int = -1


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
	var active: Camera3D = sub.get_camera_3d()
	log_event("camera", {"camera": str(active.get_path()) if active else "none",
		"pos": _v(active.global_position) if active else [], "fwd": _v(-active.global_basis.z) if active else []})
	frame += 1


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
	log_event("encoder", {"ffmpeg": ffmpeg_path, "args": " ".join(args)})
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


## Point the harness camera from pos at target.
func aim(pos: Vector3, target: Vector3) -> void:
	cam.global_position = pos
	cam.look_at(target, Vector3.UP)


## One shot: n frames, place(u) -> [pos, target] with u in 0..1 (eased by the caller where wanted).
func shot(name: String, seconds: float, place: Callable, use_scene_camera: bool = false) -> void:
	var n: int = int(round(seconds * FPS))
	var start: int = frame
	if use_scene_camera:
		(scene.get_node("Camera3D") as Camera3D).make_current()
	else:
		cam.make_current()
	for i: int in n:
		if not use_scene_camera:
			var u: float = float(i) / float(maxi(1, n - 1))
			var pt: Array = place.call(u)
			aim(pt[0], pt[1])
		await step()
	shots.append({"shot": name, "frames": [start, frame], "seconds": "%d/%d" % [frame - start, FPS],
		"camera": "scene Camera3D (unchanged)" if use_scene_camera else "harness Camera3D (scripted path)"})
	log_event("shot", shots[-1])


func orbit(center: Vector3, radius: float, height: float, a0_deg: float, a1_deg: float, u: float) -> Vector3:
	var a: float = deg_to_rad(lerpf(a0_deg, a1_deg, u))
	# angle 0 = on +Z (the scene camera's side), 90 = on +X
	return center + Vector3(sin(a) * radius, height, cos(a) * radius)


func run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	mode = args[0] if args.size() > 0 else "full"
	out_dir = args[1] if args.size() > 1 else ProjectSettings.globalize_path("res://../film-out")
	ffmpeg_path = args[2] if args.size() > 2 else "ffmpeg"
	DirAccess.make_dir_recursive_absolute(out_dir)
	if not _open_encoder(out_dir.path_join("orbit-4k.mkv")):
		quit(1)
		return

	sub = SubViewport.new()
	sub.size = Vector2i(W, H)
	sub.own_world_3d = true
	sub.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(sub)
	var view: TextureRect = TextureRect.new()
	view.texture = sub.get_texture()
	view.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	view.stretch_mode = TextureRect.STRETCH_SCALE
	view.size = Vector2(WINDOW)
	root.add_child(view)

	scene = (load("res://diorama/asset_diorama.tscn") as PackedScene).instantiate() as Node3D
	sub.add_child(scene)
	cam = Camera3D.new()
	cam.name = "HarnessCamera"
	cam.fov = 50.0
	sub.add_child(cam)
	await process_frame

	var names: Array[String] = []
	for c: Node in scene.get_children():
		names.append("%s:%s" % [c.name, c.get_class()])
	log_event("scene_tree", names)
	for n: String in ["WorldEnvironment", "Floor", "Lamp", "Camera3D", "board_square", "archer_piece", "goal_flag"]:
		expect(scene.get_node_or_null(n) != null, "scene has %s" % n)
	var scene_cam: Camera3D = scene.get_node("Camera3D") as Camera3D
	expect(scene_cam.position.is_equal_approx(Vector3(0, 1.1, 3)), "scene camera at (0, 1.1, 3) as saved")
	var archer: Vector3 = (scene.get_node("archer_piece") as Node3D).global_position
	var board: Vector3 = (scene.get_node("board_square") as Node3D).global_position
	var flag: Vector3 = (scene.get_node("goal_flag") as Node3D).global_position
	log_event("capture_start", {"mode": mode, "engine": Engine.get_version_info().get("string", ""),
		"renderer": RenderingServer.get_current_rendering_method(), "window": str(root.size),
		"subviewport": str(sub.size), "msaa_3d": sub.msaa_3d, "screen_space_aa": sub.screen_space_aa,
		"fixed_fps": Engine.max_fps, "movie": OS.has_feature("movie"),
		"archer": _v(archer), "board": _v(board), "flag": _v(flag)})

	if mode == "probe":
		await shot("probe_scene_camera", 1.0, Callable(), true)
		await shot("probe_orbit", 1.0, func(u: float) -> Array:
			return [orbit(Vector3(0, 0.35, 0), 3.4, 1.0, 0.0, 20.0, u), Vector3(0, 0.35, 0)])
		_finish()
		return

	var mid: Vector3 = Vector3(-0.15, 0.35, 0.0)
	# A: the scene exactly as saved, through its own camera.
	await shot("A_scene_camera", 4.0, Callable(), true)
	# B: one slow full orbit around all three, from the scene camera's side (+Z), clockwise seen from above.
	await shot("B_orbit_360", 16.0, func(u: float) -> Array:
		return [orbit(mid, 3.3, 0.85, 0.0, 360.0, smooth(u)), mid])
	# C: floor level, low angle: the camera sinks to 6 cm above the floor in front and tracks left to right.
	await shot("C_low_angle", 8.0, func(u: float) -> Array:
		var x: float = lerpf(-2.0, 1.8, smooth(u))
		return [Vector3(x, 0.06, 2.2), Vector3(x * 0.6, 0.25, 0.0)])
	# D: archer close-up, from its facing side (+X, the profile the 2D game uses) round toward the front (+Z).
	# Radius 0.9 m keeps the camera between the archer (x 0) and the goal flag (x 1.1), so the pole never blocks it.
	await shot("D_archer_profile", 8.0, func(u: float) -> Array:
		var c: Vector3 = archer + Vector3(0, 0.45, 0)
		return [orbit(c, 0.95, 0.08, 90.0, 25.0, smooth(u)), c])
	# E: goal flag, from exactly +X (edge-on) round to the front (+Z), where the flag shows its broad side.
	await shot("E_flag_edge_to_front", 8.0, func(u: float) -> Array:
		var c: Vector3 = flag + Vector3(0.15, 0.75, 0)
		return [orbit(c, 1.9, 0.0, 90.0, 0.0, smooth(u)), c])
	# F: board square from above, rising and turning, to show the darker border strips.
	await shot("F_board_from_above", 6.0, func(u: float) -> Array:
		var c: Vector3 = board + Vector3(0, 0.03, 0)
		return [orbit(c, lerpf(1.5, 1.0, smooth(u)), lerpf(1.4, 2.0, smooth(u)), -40.0, -80.0, smooth(u)), c])
	_finish()


func _finish() -> void:
	_close_encoder()
	log_event("capture_end", {"frames": frame, "failed": failed})
	var f: FileAccess = FileAccess.open(out_dir.path_join("orbit-log.jsonl"), FileAccess.WRITE)
	for line: String in log_lines:
		f.store_line(line)
	f.close()
	var summary: Dictionary = {"mode": mode, "frames": frame, "fps": FPS, "failed": failed, "notes": notes,
		"shots": shots, "master": "orbit-4k.mkv (FFV1 lossless, bgr0)", "subviewport": [W, H]}
	var s: FileAccess = FileAccess.open(out_dir.path_join("orbit-summary.json"), FileAccess.WRITE)
	s.store_string(JSON.stringify(summary, "\t"))
	s.close()
	print("CAPTURE %s: %d frames, failed='%s'" % [mode, frame, failed])
	quit(0 if failed == "" else 1)
