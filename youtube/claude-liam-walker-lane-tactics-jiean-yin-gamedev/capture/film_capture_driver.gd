extends SceneTree
## Film capture driver for the Lane Tactics asset slice (isolated copy of film-source-v1 only).
##
## Run under Godot Movie Maker so the engine's own audio mix is recorded:
##   Godot_v4.7.2-stable_win64.exe --path <copy> --write-movie <out>/run.avi --fixed-fps 30 \
##       --script res://film/film_capture_driver.gd -- <mode> <out_dir>
##   mode: probe | full
##
## - The real main scene (res://game/main.tscn, unchanged) runs inside a 3840x2160 SubViewport whose
##   2D canvas is the game's 1280x720 logical size, stretched (the project's canvas_items stretch).
##   A TextureRect shows that SubViewport in the 1280x720 window, so Movie Maker's AVI is a
##   720p picture of the SAME frames, with the engine's audio mix (music + SFX) of the same run.
## - Every rendered SubViewport frame is also saved as a 4K PNG (frames/%05d.png), with the
##   engine process-frame number logged, so the 4K picture and the AVI audio can be joined by frame.
## - Input only through InputEventKey pushed into the SubViewport (main.gd's _unhandled_input),
##   at normal simulation speed (main.time_scale stays 1.0). No teleporting, no rules calls,
##   no state writes. The driver only READS main/rules/audio state to decide when to press.
## - Logs every press, every rules event shown, every sound trigger and music state change per frame.
## - Asserts the expected outcomes and quits nonzero on any failure.

const W := 3840
const H := 2160
const LOGICAL := Vector2i(1280, 720)
const FPS := 30
const SFX := ["SFX-HOP", "SFX-HIT", "SFX-HURT", "SFX-WIN"]

var sub: SubViewport
var main: Node
var audio: Node
var frame: int = 0
var out_dir: String = ""
var frames_dir: String = ""
var mode: String = "full"
var log_lines: Array[String] = []
var failed: String = ""
var notes: Array[String] = []
var last_proc: int = -1
var proc_at_frame0: int = -1
var _seen_sfx: Dictionary = {}
var _seen_played: int = 0
var _seen_music: int = 0
var _last_state: String = ""
var save_ms_total: float = 0.0
var readback_ms_total: float = 0.0
var _pipe: FileAccess
var _ffmpeg_pid: int = -1
var ffmpeg_path: String = ""


func _initialize() -> void:
	call_deferred("run")


# ---------------------------------------------------------------- logging

func log_event(kind: String, detail: Variant = "") -> void:
	var entry: Dictionary = {"frame": frame, "t_s": snappedf(float(frame) / FPS, 0.001),
		"process_frame": Engine.get_process_frames(), "event": kind, "detail": detail}
	if is_instance_valid(main):
		entry["state"] = main.state_name()
		entry["turn"] = main.rules.turn
	log_lines.append(JSON.stringify(entry))


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


## Called once per captured frame: records what the scene showed or played on that frame.
func _observe() -> void:
	if not is_instance_valid(main):
		return
	var s: String = main.state_name()
	if s != _last_state:
		log_event("state", s)
		_last_state = s
	var played: Array = main.played_events
	if played.size() < _seen_played:
		_seen_played = 0 # retry / play again clears the scene's played-event list
	while _seen_played < played.size():
		var ev: Dictionary = played[_seen_played]
		log_event("rules_event_shown", {"type": ev.get("type", ""), "unit": ev.get("unit", ""),
			"team": ev.get("team", ""), "hp_after": ev.get("hp_after", null)})
		_seen_played += 1
	var plog: Array = audio.play_log
	var n: int = int(_seen_sfx.get("n", 0))
	while n < plog.size():
		var e: Dictionary = plog[n]
		log_event("sfx_trigger", {"id": e["id"], "unit": e.get("unit", ""), "music": e.get("music", ""),
			"file_loaded": e.get("file", false)})
		n += 1
	_seen_sfx["n"] = n
	var mh: Array = audio.music_history
	while _seen_music < mh.size():
		log_event("music_state", mh[_seen_music])
		_seen_music += 1


# ---------------------------------------------------------------- input

func _key(code: Key, pressed: bool) -> InputEventKey:
	var e: InputEventKey = InputEventKey.new()
	e.keycode = code
	e.physical_keycode = code
	e.pressed = pressed
	return e


func tap(code: Key, label: String) -> void:
	sub.push_input(_key(code, true))
	sub.push_input(_key(code, false))
	log_event("key", label)


# ---------------------------------------------------------------- frames

## Advance one engine frame (fixed 1/30 s of game time), then grab the SubViewport frame drawn in it.
func step() -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var pf: int = Engine.get_process_frames()
	if last_proc >= 0 and pf != last_proc + 1:
		fail("frame %d: process frame jumped %d -> %d (a draw was skipped)" % [frame, last_proc, pf])
	last_proc = pf
	if proc_at_frame0 < 0:
		proc_at_frame0 = pf
	_observe()
	if frames_dir != "":
		var t0: int = Time.get_ticks_usec()
		var img: Image = sub.get_texture().get_image()
		var t1: int = Time.get_ticks_usec()
		if img == null or img.get_width() != W or img.get_height() != H:
			fail("frame %d: SubViewport image is not %dx%d" % [frame, W, H])
		else:
			if img.get_format() != Image.FORMAT_RGBA8:
				img.convert(Image.FORMAT_RGBA8)
			# Raw RGBA frame straight into ffmpeg's stdin (lossless FFV1 master, see _open_encoder).
			_pipe.store_buffer(img.get_data())
		readback_ms_total += (t1 - t0) / 1000.0
		save_ms_total += (Time.get_ticks_usec() - t0) / 1000.0
	frame += 1


## 4K master: raw RGBA frames are piped to ffmpeg and stored losslessly (FFV1, RGB) - no PNG step.
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
	log_event("encoder", {"ffmpeg": ffmpeg_path, "args": " ".join(args), "pid": _ffmpeg_pid})
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


func hold(seconds: float) -> void:
	for i: int in int(round(seconds * FPS)):
		await step()


func until(cond: Callable, max_seconds: float, what: String) -> bool:
	var n: int = 0
	while not cond.call():
		if n >= int(max_seconds * FPS):
			fail("timed out waiting for: " + what)
			return false
		await step()
		n += 1
	return true


func counts() -> Dictionary:
	return (audio.play_counts as Dictionary).duplicate()


func delta(before: Dictionary) -> Dictionary:
	var d: Dictionary = {}
	for id: String in SFX:
		d[id] = int(audio.play_counts[id]) - int(before[id])
	return d


# ---------------------------------------------------------------- one route, human-paced

## move: [dcol, dlane]; target: [col, lane] or null. Dwell times are a scripted "thinking" pause so the
## planning markers are visible; they never change the rules (planning has no clock in this slice).
func play_turn(move: Vector2i, target: Variant, think_move: float, think_attack: float) -> void:
	if not await until(func() -> bool: return main.state_name() == "PLAN_MOVE", 20.0, "PLAN_MOVE"):
		return
	var turn_no: int = main.rules.turn
	log_event("turn_start", turn_no)
	await hold(think_move)
	if move == Vector2i.ZERO:
		tap(KEY_SPACE, "Space (stay) turn %d" % turn_no)
	else:
		if move.x == 1:
			tap(KEY_RIGHT, "Right (plan step) turn %d" % turn_no)
		elif move.x == -1:
			tap(KEY_LEFT, "Left (plan step) turn %d" % turn_no)
		if move.y == -1:
			tap(KEY_UP, "Up (plan step) turn %d" % turn_no)
		elif move.y == 1:
			tap(KEY_DOWN, "Down (plan step) turn %d" % turn_no)
		await hold(0.9) # the planned-move marker and arrow stay on screen
		expect(main.planned_offset == move, "turn %d planned offset %s" % [turn_no, str(move)])
		tap(KEY_ENTER, "Enter (confirm move) turn %d" % turn_no)
	await until(func() -> bool:
		var s: String = main.state_name()
		return s == "PLAN_ATTACK" or s == "WON" or s == "LOST" or (s == "PLAN_MOVE" and main.rules.turn > turn_no),
		20.0, "end of move playback, turn %d" % turn_no)
	if main.state_name() == "PLAN_ATTACK":
		await hold(think_attack)
		if target == null:
			tap(KEY_SPACE, "Space (hold fire) turn %d" % turn_no)
		else:
			var t: Vector2i = Vector2i(int(target[0]), int(target[1]))
			var guard: int = 0
			while main.selected_target() != t and guard < 30:
				tap(KEY_RIGHT, "Right (next target) turn %d" % turn_no)
				await step()
				guard += 1
			expect(main.selected_target() == t, "turn %d target %s selectable" % [turn_no, str(t)])
			tap(KEY_ENTER, "Enter (shoot) turn %d" % turn_no)
		await until(func() -> bool:
			var s: String = main.state_name()
			return s == "WON" or s == "LOST" or (s == "PLAN_MOVE" and main.rules.turn > turn_no),
			20.0, "end of combat playback, turn %d" % turn_no)
	elif target != null:
		fail("turn %d: route has a target but attack planning was skipped" % turn_no)


func play_route(path: String, think_move: float, think_attack: float) -> void:
	var route: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	log_event("route_start", route["name"])
	for step_data: Dictionary in route["turns"]:
		var m: Array = step_data["move"]
		await play_turn(Vector2i(int(m[0]), int(m[1])), step_data["target"], think_move, think_attack)
		if failed != "":
			return
	await until(func() -> bool: return main.state_name() == "WON" or main.state_name() == "LOST", 20.0, "route end")
	log_event("route_end", {"name": route["name"], "result": main.rules.result, "reason": main.rules.reason})


# ---------------------------------------------------------------- run

func run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	mode = args[0] if args.size() > 0 else "full"
	out_dir = args[1] if args.size() > 1 else ProjectSettings.globalize_path("res://../film-out")
	ffmpeg_path = args[2] if args.size() > 2 else "ffmpeg"
	DirAccess.make_dir_recursive_absolute(out_dir)
	frames_dir = "pipe"
	if not _open_encoder(out_dir.path_join("run-4k.mkv")):
		quit(1)
		return

	sub = SubViewport.new()
	sub.size = Vector2i(W, H)
	sub.size_2d_override = LOGICAL
	sub.size_2d_override_stretch = true
	sub.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	sub.disable_3d = true
	root.add_child(sub)
	var view: TextureRect = TextureRect.new()
	view.texture = sub.get_texture()
	view.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	view.stretch_mode = TextureRect.STRETCH_SCALE
	view.size = Vector2(LOGICAL)
	root.add_child(view)
	main = (load("res://game/main.tscn") as PackedScene).instantiate()
	sub.add_child(main)
	audio = main.audio
	expect(is_equal_approx(main.time_scale, 1.0), "main.time_scale is 1.0 (normal speed)")
	log_event("capture_start", {"mode": mode, "engine": Engine.get_version_info().get("string", ""),
		"window": str(root.size), "subviewport": str(sub.size), "logical": str(LOGICAL),
		"fixed_fps": Engine.max_fps, "movie": OS.has_feature("movie")})

	if mode == "probe":
		await hold(1.0)
		tap(KEY_ENTER, "Enter (start)")
		await hold(1.0)
		_finish()
		return

	# ---- Take A: title, board, the naive lose route, defeat card (music fades)
	expect(main.state_name() == "TITLE" and audio.music_state == "playing", "title with music playing")
	await hold(3.0)
	tap(KEY_ENTER, "Enter (start)")
	await hold(2.0)
	var before: Dictionary = counts()
	await play_route("res://tests/fixtures/lose_route.json", 1.0, 1.8)
	var dl: Dictionary = delta(before)
	expect(main.state_name() == "LOST" and main.rules.reason == "shot by the enemy archer in lane 4",
		"lose route ends LOST: shot by the enemy archer in lane 4")
	expect(dl == {"SFX-HOP": 7, "SFX-HIT": 1, "SFX-HURT": 2, "SFX-WIN": 0}, "lose route sounds %s" % str(dl))
	expect(main.pieces["p1"].state == "defeat", "defeat: player piece toppled")
	await hold(3.6)
	expect(audio.music_state == "stopped", "defeat: music faded out and stopped")

	# ---- Take B: retry, footprints on the fresh board, the win route, win card, results
	tap(KEY_R, "R (retry)")
	await hold(1.6)
	expect(main.state_name() == "PLAN_MOVE" and main.retries == 1 and audio.music_state == "playing",
		"retry: turn 1, retries 1, music restarted")
	tap(KEY_F3, "F3 (footprints on)")
	await hold(2.8)
	expect(main.debug_footprints, "F3 footprints shown")
	tap(KEY_F3, "F3 (footprints off)")
	await hold(0.8)
	before = counts()
	await play_route("res://tests/fixtures/win_route.json", 1.1, 1.8)
	var dw: Dictionary = delta(before)
	expect(main.state_name() == "WON" and main.rules.result_kind == "elimination" and main.rules.turn == 5,
		"win route ends WON by elimination on turn 5")
	expect(dw == {"SFX-HOP": 5, "SFX-HIT": 2, "SFX-HURT": 1, "SFX-WIN": 1}, "win route sounds %s" % str(dw))
	expect(audio.music_state == "stopped", "win: music stopped")
	expect(main.pieces["p1"].state == "win", "win: player piece in the win pose")
	await hold(3.2)
	await until(func() -> bool: return main._card_lock <= 0.0, 5.0, "win card lock")
	tap(KEY_ENTER, "Enter (results)")
	await hold(2.6)
	expect(main.show_results, "results card shown")
	_finish()


func _finish() -> void:
	_close_encoder()
	log_event("capture_end", {"frames": frame, "failed": failed, "pipe_write_ms_avg": save_ms_total / maxf(1.0, frame), "readback_ms_avg": readback_ms_total / maxf(1.0, frame)})
	var f: FileAccess = FileAccess.open(out_dir.path_join("inputs.jsonl"), FileAccess.WRITE)
	for line: String in log_lines:
		f.store_line(line)
	f.close()
	var summary: Dictionary = {"mode": mode, "frames": frame, "fps": FPS, "failed": failed, "notes": notes, "master": "run-4k.mkv (FFV1 lossless, bgr0)",
		"process_frame_at_frame0": proc_at_frame0, "subviewport": [W, H], "logical": [LOGICAL.x, LOGICAL.y],
		"play_counts_total": audio.play_counts if is_instance_valid(audio) else {},
		"music_history": audio.music_history if is_instance_valid(audio) else []}
	var s: FileAccess = FileAccess.open(out_dir.path_join("summary.json"), FileAccess.WRITE)
	s.store_string(JSON.stringify(summary, "\t"))
	s.close()
	print("CAPTURE %s: %d frames, failed='%s'" % [mode, frame, failed])
	quit(0 if failed == "" else 1)
