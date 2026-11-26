extends SceneTree
## Film capture driver for the Lane Tactics A7 film (isolated copy of tag a7 only).
## Harness file: it lives in film/ of the capture copy and is NOT part of the game.
## Adapted from the A6 film's driver (youtube/claude-liam-walker-lane-tactics-jiean-yin-a6-gamedev/capture/).
##
## Run under Godot Movie Maker (window build, not headless):
##   <Godot>.exe --path <copy> --write-movie <out>/<mode>.avi --fixed-fps <fps> \
##       --script res://film/a7_capture_driver.gd -- <mode> <out_dir> <ffmpeg> <fps>
##   mode: play (30 fps, real speed) | slow (120 fps; the film plays these frames at 30 = 1/4 speed, labelled)
##
## - main.tscn (unchanged) is instanced inside a 3840x2160 SubViewport that draws the 1280x720 canvas scaled up
##   (size_2d_override), as the window's canvas_items stretch would. Recorded frames are piped raw to ffmpeg as a
##   lossless FFV1 4K master (<mode>-4k.mkv) at the capture's own frame rate.
## - Real key presses are pushed into the SubViewport, playing the win route the A7 tests play
##   (tests/fixtures/win_route.json). Nothing in the game is called or set directly; the driver only reads state
##   (poses, the read-only piece.rig_snapshot(), the flag's cell), to log it and to know when to press a key.
## - play: run 1 = title (the flag waving), turns 1-3, turn 4 (two shots, enemy first), turn 5 (killing shot).
##   Run 2 turn 4: P in e1's startup, in e1's active phase, in p1's recovery, each held PAUSE_HOLD s.
##   Run 3 turn 4: R in e1's active phase.
## - slow: turns 1-3 unrecorded, then turn 4 recorded at 120 fps.
## - Every engine frame is logged, recorded or not. Quits nonzero on any failed expectation or skipped draw.

const W := 3840
const H := 2160
const WINDOW := Vector2i(1280, 720)
const PAUSE_HOLD: float = 3.0

var fps: int = 30
var sub: SubViewport
var scene: Node
var flag_sprite: Sprite2D
var frame: int = 0 ## engine frames stepped by the driver
var mframe: int = 0 ## frames written to the master
var rec: bool = false
var out_dir: String = ""
var mode: String = "play"
var ffmpeg_path: String = "ffmpeg"
var log_lines: Array[String] = []
var shots: Array[Dictionary] = []
var failed: String = ""
var notes: Array[String] = []
var last_proc: int = -1
var _pipe: FileAccess
var _ffmpeg_pid: int = -1
var _seen_events: int = 0
var _shots_seen: int = 0
var _prev_pose: Dictionary = {}


func _initialize() -> void:
	call_deferred("run")


func log_event(kind: String, detail: Variant = "") -> void:
	log_lines.append(JSON.stringify({"frame": frame, "mframe": mframe if rec else -1, "rec": rec,
		"t_s": snappedf(float(frame) / fps, 0.0001), "process_frame": Engine.get_process_frames(),
		"event": kind, "detail": detail}))


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


func s() -> String:
	return scene.state_name()


func pose(id: String) -> String:
	var p: Variant = scene.pieces.get(id)
	return String(p.state) if p != null else ""


func clip_t(id: String) -> float:
	var p: Variant = scene.pieces.get(id)
	if p == null:
		return -1.0
	return float(p.call("rig_snapshot").get("pos", -1.0))


## What the frame shows, for the log. Read-only.
func _piece(id: String) -> Dictionary:
	var p: Variant = scene.pieces.get(id)
	if p == null:
		return {}
	var r: Dictionary = p.call("rig_snapshot")
	var ps: String = String(p.state)
	if ps == "draw" and _prev_pose.get(id, "") != "draw":
		_shots_seen += 1
	_prev_pose[id] = ps
	return {"pose": ps, "clip": r.get("clip", ""), "clip_t": snappedf(float(r.get("pos", -1.0)), 0.0001),
		"rig": r.get("rig_visible", false), "facing": int(p.facing)}


func state_row() -> Dictionary:
	var arrows: Array = []
	for a: Dictionary in scene._arrows:
		arrows.append({"t": snappedf(float(a["t"]), 0.0001)})
	var hits: Array = []
	var events: Array = scene.played_events
	if events.size() < _seen_events:
		_seen_events = 0
	while _seen_events < events.size():
		var ev: Dictionary = events[_seen_events]
		_seen_events += 1
		if String(ev["type"]) == "damaged":
			hits.append(String(ev["unit"]))
	return {"state": s(), "turn": scene.rules.turn, "paused": scene.paused, "arrows": arrows, "hits": hits,
		"p1": _piece("p1"), "e1": _piece("e1"), "flag_cell": flag_sprite.frame,
		"flag_offset_x": flag_sprite.offset.x, "shots_seen": _shots_seen}


## Advance one engine frame (fixed 1/fps s), then pipe the SubViewport frame drawn in it if recording.
func step() -> void:
	await process_frame
	await RenderingServer.frame_post_draw
	var pf: int = Engine.get_process_frames()
	if last_proc >= 0 and pf != last_proc + 1:
		fail("frame %d: process frame jumped %d -> %d (a draw was skipped)" % [frame, last_proc, pf])
	last_proc = pf
	if rec:
		var img: Image = sub.get_texture().get_image()
		if img == null or img.get_width() != W or img.get_height() != H:
			fail("frame %d: SubViewport image is not %dx%d" % [frame, W, H])
		else:
			if img.get_format() != Image.FORMAT_RGBA8:
				img.convert(Image.FORMAT_RGBA8)
			_pipe.store_buffer(img.get_data())
	log_event("frame", state_row())
	if rec:
		mframe += 1
	frame += 1


func hold(seconds: float) -> void:
	for i: int in int(round(seconds * fps)):
		await step()


## Step until cond() is true (checked before each step); fail after max_seconds of game frames.
func wait_until(cond: Callable, what: String, max_seconds: float = 30.0) -> bool:
	var n: int = 0
	while not cond.call():
		await step()
		n += 1
		if n > int(max_seconds * fps):
			fail("not reached: %s (state %s)" % [what, s()])
			return false
	return true


func _open_encoder(path: String) -> bool:
	var args: PackedStringArray = ["-hide_banner", "-loglevel", "error", "-nostats", "-y",
		"-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % [W, H], "-framerate", str(fps), "-i", "-",
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


func begin_shot(name: String) -> int:
	rec = true
	log_event("shot_start", name)
	return mframe


func end_shot(name: String, start: int, what: String) -> void:
	shots.append({"shot": name, "master_frames": [start, mframe], "seconds": "%d/%d" % [mframe - start, fps],
		"what": what})
	log_event("shot", shots[-1])
	rec = false


# ---------------------------------------------------------------- keys and the route

func key(code: Key) -> void:
	for pressed: bool in [true, false]:
		var ev: InputEventKey = InputEventKey.new()
		ev.keycode = code
		ev.physical_keycode = code
		ev.pressed = pressed
		sub.push_input(ev)
	log_event("key", OS.get_keycode_string(code))


func move_of(st: Dictionary) -> Vector2i:
	var m: Array = st["move"]
	return Vector2i(int(m[0]), int(m[1]))


func target_of(st: Dictionary) -> Variant:
	if st["target"] == null:
		return null
	var t: Array = st["target"]
	return Vector2i(int(t[0]), int(t[1]))


func turn_done(turn_no: int) -> bool:
	return s() == "WON" or s() == "LOST" or (s() == "PLAN_MOVE" and scene.rules.turn > turn_no)


## From PLAN_MOVE: give one route step's orders through real keys, with short human-paced holds.
## Returns after the attack orders are confirmed (playback not awaited).
func give_orders(st: Dictionary, label: String, pace: float) -> bool:
	if not await wait_until(func() -> bool: return s() == "PLAN_MOVE", "%s PLAN_MOVE" % label):
		return false
	var turn_no: int = scene.rules.turn
	await hold(pace)
	var mv: Vector2i = move_of(st)
	if mv == Vector2i.ZERO:
		key(KEY_SPACE)
	else:
		if mv.x == 1:
			key(KEY_RIGHT)
		elif mv.x == -1:
			key(KEY_LEFT)
		if mv.y == -1:
			key(KEY_UP)
		elif mv.y == 1:
			key(KEY_DOWN)
		await hold(pace)
		key(KEY_ENTER)
	var after_moves: Callable = func() -> bool:
		return s() == "PLAN_ATTACK" or s() == "PLAY_ATTACKS" or s() == "WON" or s() == "LOST" \
			or (s() == "PLAN_MOVE" and scene.rules.turn > turn_no)
	if not await wait_until(after_moves, "%s move playback" % label):
		return false
	var t: Variant = target_of(st)
	if s() == "PLAN_ATTACK":
		await hold(pace)
		if t == null:
			key(KEY_SPACE)
		else:
			var n: int = 0
			while scene.selected_target() != t and n < 30:
				key(KEY_RIGHT)
				await step()
				n += 1
			if scene.selected_target() != t:
				fail("%s: target %s not selectable" % [label, t])
				return false
			await hold(pace)
			key(KEY_ENTER)
	elif t != null:
		fail("%s: the route's target %s could not be ordered" % [label, t])
		return false
	return true


func play_turn(st: Dictionary, label: String, pace: float) -> bool:
	var turn_no: int = scene.rules.turn
	if not await give_orders(st, label, pace):
		return false
	return await wait_until(turn_done.bind(turn_no), "%s playback" % label)


func start_from_title(pace: float) -> void:
	await hold(pace)
	key(KEY_ENTER)
	await wait_until(func() -> bool: return s() == "PLAN_MOVE" and scene.rules.turn == 1, "turn 1")


## From the results card (WON): Enter after the card lock, Enter again; then wait for turn 1. Unrecorded.
func play_again(label: String) -> bool:
	if not await wait_until(func() -> bool: return float(scene._card_lock) <= 0.0, "%s card lock" % label):
		return false
	key(KEY_ENTER)
	await step()
	key(KEY_ENTER)
	return await wait_until(func() -> bool: return s() == "PLAN_MOVE" and scene.rules.turn == 1, "%s turn 1" % label)


# ---------------------------------------------------------------- modes

func run_play(turns: Array) -> void:
	var sh: int = begin_shot("P0_title")
	await hold(4.0)
	end_shot("P0_title", sh, "title card: the flag waving (wave, real time)")
	sh = begin_shot("P1_turns_1_3")
	await start_from_title(0.0)
	for i: int in 3:
		if not await play_turn(turns[i], "run 1 turn %d" % (i + 1), 0.4):
			return
	end_shot("P1_turns_1_3", sh, "turns 1-3: both sides hold, no shot")
	expect(_shots_seen == 0, "no shot in turns 1-3")
	sh = begin_shot("P2_turn4_two_shots")
	if not await play_turn(turns[3], "run 1 turn 4", 0.6):
		return
	await hold(1.5)
	end_shot("P2_turn4_two_shots", sh, "turn 4: the enemy shoots first (hit on p1), then the player (hit on e1)")
	expect(_shots_seen == 2, "turn 4: 2 shots")
	sh = begin_shot("P3_turn5_kill")
	if not await give_orders(turns[4], "run 1 turn 5", 0.6):
		return
	if not await wait_until(func() -> bool: return s() == "WON", "run 1 WON"):
		return
	await hold(2.0)
	end_shot("P3_turn5_kill", sh, "turn 5: the player's killing shot; results card")
	expect(_shots_seen == 3, "run 1: 3 shots")
	# Run 2: P in each phase of turn 4's shots.
	if not await play_again("run 2"):
		return
	for i: int in 3:
		if not await play_turn(turns[i], "run 2 turn %d" % (i + 1), 0.1):
			return
	sh = begin_shot("P4_pause_each_phase")
	if not await give_orders(turns[3], "run 2 turn 4", 0.6):
		return
	# startup: e1 is drawing, its clip past frame 3 (60 fps) and before the release (0.2 s)
	if not await wait_until(func() -> bool: return pose("e1") == "draw" and clip_t("e1") >= 0.05, "run 2 e1 startup"):
		return
	key(KEY_P)
	await hold(PAUSE_HOLD)
	expect(scene.paused and pose("e1") == "draw" and clip_t("e1") < 0.2, "run 2: paused in e1's startup")
	key(KEY_P)
	# active: e1's arrow in flight, about half way
	if not await wait_until(func() -> bool: return scene._arrows.size() > 0 and float(scene._arrows[0]["t"]) >= 0.15,
			"run 2 e1 active"):
		return
	key(KEY_P)
	await hold(PAUSE_HOLD)
	expect(scene.paused and pose("e1") == "draw" and scene._arrows.size() > 0, "run 2: paused in e1's active phase")
	key(KEY_P)
	# recovery: p1's shot, after its impact (clip past 0.6 s) and before idle
	if not await wait_until(func() -> bool: return pose("p1") == "draw" and clip_t("p1") >= 0.6, "run 2 p1 recovery"):
		return
	key(KEY_P)
	await hold(PAUSE_HOLD)
	expect(scene.paused and pose("p1") == "draw" and clip_t("p1") >= 0.55, "run 2: paused in p1's recovery")
	key(KEY_P)
	await wait_until(turn_done.bind(4), "run 2 turn 4 playback")
	await hold(1.0)
	end_shot("P4_pause_each_phase", sh, "run 2 turn 4: P in e1's startup, in e1's active phase, in p1's recovery")
	if not await give_orders(turns[4], "run 2 turn 5", 0.1):
		return
	if not await wait_until(func() -> bool: return s() == "WON", "run 2 WON"):
		return
	# Run 3: R mid-shot.
	if not await play_again("run 3"):
		return
	for i: int in 3:
		if not await play_turn(turns[i], "run 3 turn %d" % (i + 1), 0.1):
			return
	sh = begin_shot("P5_restart_mid_shot")
	if not await give_orders(turns[3], "run 3 turn 4", 0.6):
		return
	if not await wait_until(func() -> bool: return scene._arrows.size() > 0 and float(scene._arrows[0]["t"]) >= 0.1,
			"run 3 e1 active"):
		return
	key(KEY_R)
	await hold(3.0)
	expect(s() == "PLAN_MOVE" and scene.rules.turn == 1 and pose("e1") != "draw" and scene._arrows.is_empty(),
		"run 3: R mid-shot restarts, no shot left")
	end_shot("P5_restart_mid_shot", sh, "run 3 turn 4: R in e1's active phase; turn 1, nothing from the old shot")


func run_slow(turns: Array) -> void:
	await start_from_title(0.0)
	for i: int in 3:
		if not await play_turn(turns[i], "slow turn %d" % (i + 1), 0.05):
			return
	var sh: int = begin_shot("S2_turn4_two_shots")
	if not await play_turn(turns[3], "slow turn 4", 0.3):
		return
	await hold(1.0)
	end_shot("S2_turn4_two_shots", sh, "turn 4 at %d fps (the film plays it at 30 = 1/4 speed)" % fps)
	expect(_shots_seen == 2, "slow: 2 shots")


# ----------------------------------------------------------------

func run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	mode = args[0] if args.size() > 0 else "play"
	out_dir = args[1] if args.size() > 1 else ProjectSettings.globalize_path("res://../film-out")
	ffmpeg_path = args[2] if args.size() > 2 else "ffmpeg"
	fps = int(args[3]) if args.size() > 3 else (120 if mode == "slow" else 30)
	DirAccess.make_dir_recursive_absolute(out_dir)
	if not _open_encoder(out_dir.path_join("%s-4k.mkv" % mode)):
		quit(1)
		return
	sub = SubViewport.new()
	sub.size = Vector2i(W, H)
	sub.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	sub.size_2d_override = WINDOW
	sub.size_2d_override_stretch = true
	root.add_child(sub)
	var view: TextureRect = TextureRect.new()
	view.texture = sub.get_texture()
	view.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	view.stretch_mode = TextureRect.STRETCH_SCALE
	view.size = Vector2(WINDOW)
	root.add_child(view)
	scene = (load("res://game/main.tscn") as PackedScene).instantiate()
	sub.add_child(scene)
	flag_sprite = scene.get_node_or_null("GoalFlag/FlagSprite") as Sprite2D
	if flag_sprite == null:
		fail("main.tscn lacks GoalFlag/FlagSprite")
		_finish()
		return
	log_event("capture_start", {"mode": mode, "fps": fps, "engine": Engine.get_version_info().get("string", ""),
		"renderer": RenderingServer.get_current_rendering_method(), "subviewport": str(sub.size),
		"size_2d_override": str(sub.size_2d_override), "movie": OS.has_feature("movie"),
		"physics_ticks": Engine.physics_ticks_per_second})
	var route: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/win_route.json"))
	if typeof(route) != TYPE_DICTIONARY:
		fail("cannot read the win route")
		_finish()
		return
	await step()
	match mode:
		"play":
			await run_play(route["turns"])
		"slow":
			await run_slow(route["turns"])
		_:
			fail("unknown mode " + mode)
	_finish()


func _finish() -> void:
	rec = false
	_close_encoder()
	log_event("capture_end", {"frames": frame, "master_frames": mframe, "failed": failed, "shots_seen": _shots_seen})
	var f: FileAccess = FileAccess.open(out_dir.path_join("%s-log.jsonl" % mode), FileAccess.WRITE)
	for line: String in log_lines:
		f.store_line(line)
	f.close()
	var summary: Dictionary = {"mode": mode, "fps": fps, "engine_frames": frame, "master_frames": mframe,
		"failed": failed, "notes": notes, "shots": shots, "shots_seen": _shots_seen,
		"master": "%s-4k.mkv (FFV1 lossless, bgr0, %d fps)" % [mode, fps], "subviewport": [W, H]}
	var sfile: FileAccess = FileAccess.open(out_dir.path_join("%s-summary.json" % mode), FileAccess.WRITE)
	sfile.store_string(JSON.stringify(summary, "\t"))
	sfile.close()
	print("CAPTURE %s: %d engine frames, %d master frames, failed='%s'" % [mode, frame, mframe, failed])
	quit(0 if failed == "" else 1)
