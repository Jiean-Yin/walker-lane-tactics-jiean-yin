extends SceneTree
## Film capture driver for the Lane Tactics A6 film (isolated copy of tag a6 only).
## Harness file: it lives in film/ of the capture copy and is NOT part of the game.
##
## Run under Godot Movie Maker (window build, not headless):
##   <Godot>.exe --path <copy> --write-movie <out>/<mode>.avi --fixed-fps <fps> \
##       --script res://film/a6_capture_driver.gd -- <mode> <out_dir> <ffmpeg> <fps>
##   mode: play (30 fps, real speed) | slow (120 fps; the film plays these frames at 30 = 1/4 speed, labelled)
##
## - main.tscn (unchanged) is instanced inside a 3840x2160 SubViewport that draws the 1280x720 canvas scaled up
##   (size_2d_override), as the window's canvas_items stretch would. Recorded frames are piped raw to ffmpeg as a
##   lossless FFV1 4K master (<mode>-4k.mkv) at the capture's own frame rate; Movie Maker's AVI is a 720p picture.
## - Real key presses are pushed into the SubViewport, the same way the game's tests press keys, playing the win
##   route the A6 state tests play (tests/fixtures/win_route.json). Nothing in the game is called or set directly;
##   the driver only reads state, to log it and to know when to press the next key.
## - play: run 1 = title, turns 1-3 (no shot), turn 4 (two hits, enemy first), turn 5 (killing hit), results.
##   Play again (Enter, Enter), turns 1-3 unrecorded, then run 2 turn 4 with P pressed mid-burst (P4); turn 5 and
##   play again unrecorded, then run 3 turn 4 with P pressed mid-flight (P5). Pause holds are sized to the narration.
## - slow: turns 1-3 unrecorded, then turn 4 and turn 5 recorded.
## - Every engine frame is logged (state, arrows, live bursts and trails), recorded or not. Quits nonzero on any
##   failed expectation or skipped draw.

const W := 3840
const H := 2160
const WINDOW := Vector2i(1280, 720)

var fps: int = 30
var sub: SubViewport
var scene: Node
var burst_driver: Node
var trail_driver: Node
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
var _max_bursts: int = 0
var _max_trails: int = 0


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


func _p(v: Vector2) -> Array:
	return [snappedf(v.x, 0.01), snappedf(v.y, 0.01)]


## What the frame shows, for the log. Read-only.
func state_row() -> Dictionary:
	var arrows: Array = []
	for a: Dictionary in scene._arrows:
		arrows.append({"t": snappedf(float(a["t"]), 0.0001), "from": _p(a["from"]), "to": _p(a["to"])})
	var bursts: Array = []
	for b: Node2D in burst_driver.live_bursts():
		bursts.append({"id": b.get_instance_id(), "pos": _p(b.position)})
	var trails: Array = []
	for t: Node2D in trail_driver.live_trails():
		var em: Array = []
		for e: Node in t.get_children():
			em.append((e as GPUParticles2D).emitting)
		trails.append({"id": t.get_instance_id(), "pos": _p(t.position), "emitting": em})
	var hits: Array = []
	var events: Array = scene.played_events
	if events.size() < _seen_events:
		_seen_events = 0
	while _seen_events < events.size():
		var ev: Dictionary = events[_seen_events]
		_seen_events += 1
		if String(ev["type"]) == "damaged":
			hits.append(String(ev["unit"]))
	_max_bursts = maxi(_max_bursts, bursts.size())
	_max_trails = maxi(_max_trails, trails.size())
	return {"state": s(), "turn": scene.rules.turn, "paused": scene.paused, "time_scale": scene.time_scale,
		"arrows": arrows, "bursts": bursts, "trails": trails, "hits": hits,
		"bursts_spawned": burst_driver.spawned, "trails_spawned": trail_driver.spawned}


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


# ---------------------------------------------------------------- modes

func run_play(turns: Array) -> void:
	var sh: int = begin_shot("P0_title")
	await hold(1.0)
	end_shot("P0_title", sh, "title card: no burst, no trail")
	sh = begin_shot("P1_turns_1_3")
	await start_from_title(0.0)
	for i: int in 3:
		if not await play_turn(turns[i], "run 1 turn %d" % (i + 1), 0.4):
			return
	end_shot("P1_turns_1_3", sh, "turns 1-3: both sides hold, no shot: no burst, no trail")
	expect(burst_driver.spawned == 0 and trail_driver.spawned == 0, "no effect in turns 1-3")
	sh = begin_shot("P2_turn4_two_hits")
	if not await play_turn(turns[3], "run 1 turn 4", 0.6):
		return
	await hold(1.5)
	end_shot("P2_turn4_two_hits", sh, "turn 4: the enemy shoots first (hit on p1), then the player (hit on e1)")
	expect(burst_driver.spawned == 2 and trail_driver.spawned == 2, "turn 4: 2 bursts and 2 trails")
	expect(_max_bursts == 2, "turn 4: 2 bursts alive at once")
	sh = begin_shot("P3_turn5_kill")
	var turn5_done: Callable = func() -> bool: return s() == "WON"
	if not await give_orders(turns[4], "run 1 turn 5", 0.6):
		return
	if not await wait_until(turn5_done, "run 1 WON"):
		return
	await hold(2.0)
	end_shot("P3_turn5_kill", sh, "turn 5: the player's killing hit on e1; results card")
	expect(burst_driver.spawned == 3, "run 1: 3 bursts in total")
	# Holds below are sized to the measured narration of B06 (14.4 s) and B14 (15.5 s), so that no footage is
	# retimed. Each pause gets its own turn, so each has a clean lead-in and tail.
	if not await play_again("run 2"):
		return
	for i: int in 3:
		if not await play_turn(turns[i], "run 2 turn %d" % (i + 1), 0.1):
			return
	sh = begin_shot("P4_pause_burst")
	var spawned_before: int = burst_driver.spawned
	if not await give_orders(turns[3], "run 2 turn 4", 0.6):
		return
	if not await wait_until(func() -> bool: return burst_driver.spawned > spawned_before, "run 2 first hit"):
		return
	await hold(0.25)
	key(KEY_P)
	await hold(6.5)
	expect(scene.paused and not burst_driver.live_bursts().is_empty(), "run 2: burst alive while paused")
	key(KEY_P)
	await wait_until(turn_done.bind(4), "run 2 turn 4 playback")
	await hold(3.0)
	end_shot("P4_pause_burst", sh, "run 2 turn 4: P 0.25 s after the first hit, mid-burst, held 6.5 s")
	if not await give_orders(turns[4], "run 2 turn 5", 0.1):
		return
	if not await wait_until(func() -> bool: return s() == "WON", "run 2 WON"):
		return
	if not await play_again("run 3"):
		return
	for i: int in 3:
		if not await play_turn(turns[i], "run 3 turn %d" % (i + 1), 0.1):
			return
	sh = begin_shot("P5_pause_flight")
	var trails_before: int = trail_driver.spawned
	if not await give_orders(turns[3], "run 3 turn 4", 0.6):
		return
	if not await wait_until(func() -> bool:
			return trail_driver.spawned > trails_before and scene._arrows.size() > 0 \
				and float(scene._arrows[0]["t"]) >= 0.15, "run 3 first arrow mid-flight"):
		return
	key(KEY_P)
	await hold(5.0)
	expect(scene.paused and not trail_driver.live_trails().is_empty(), "run 3: trail alive while paused")
	key(KEY_P)
	spawned_before = burst_driver.spawned
	if not await wait_until(func() -> bool: return burst_driver.spawned > spawned_before, "run 3 first hit"):
		return
	await hold(4.0)
	end_shot("P5_pause_flight", sh, "run 3 turn 4: P mid-flight of the enemy's arrow, held 5 s; then the landing")


## From the results card (WON): Enter after the card lock, Enter again; then wait for turn 1. Unrecorded.
func play_again(label: String) -> bool:
	if not await wait_until(func() -> bool: return float(scene._card_lock) <= 0.0, "%s card lock" % label):
		return false
	key(KEY_ENTER)
	await step()
	key(KEY_ENTER)
	if not await wait_until(func() -> bool: return s() == "PLAN_MOVE" and scene.rules.turn == 1, "%s turn 1" % label):
		return false
	expect(burst_driver.live_bursts().is_empty() and trail_driver.live_trails().is_empty(),
		"%s play again: no live burst or trail" % label)
	return true


func run_slow(turns: Array) -> void:
	await start_from_title(0.0)
	for i: int in 3:
		if not await play_turn(turns[i], "slow turn %d" % (i + 1), 0.05):
			return
	var sh: int = begin_shot("S2_turn4_two_hits")
	if not await play_turn(turns[3], "slow turn 4", 0.3):
		return
	await hold(1.5)
	end_shot("S2_turn4_two_hits", sh, "turn 4 at %d fps (the film plays it at 30 = 1/4 speed)" % fps)
	sh = begin_shot("S3_turn5_kill")
	if not await give_orders(turns[4], "slow turn 5", 0.3):
		return
	await wait_until(func() -> bool: return s() == "WON", "slow WON")
	await hold(1.0)
	end_shot("S3_turn5_kill", sh, "turn 5 at %d fps" % fps)
	expect(burst_driver.spawned == 3 and trail_driver.spawned == 3, "slow: 3 bursts, 3 trails")


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
	burst_driver = scene.get_node_or_null("HitBurstDriver")
	trail_driver = scene.get_node_or_null("ArrowTrailDriver")
	if burst_driver == null or trail_driver == null:
		fail("main.tscn lacks HitBurstDriver or ArrowTrailDriver")
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
	log_event("capture_end", {"frames": frame, "master_frames": mframe, "failed": failed,
		"max_bursts_alive": _max_bursts, "max_trails_alive": _max_trails})
	var f: FileAccess = FileAccess.open(out_dir.path_join("%s-log.jsonl" % mode), FileAccess.WRITE)
	for line: String in log_lines:
		f.store_line(line)
	f.close()
	var summary: Dictionary = {"mode": mode, "fps": fps, "engine_frames": frame, "master_frames": mframe,
		"failed": failed, "notes": notes, "shots": shots, "max_bursts_alive": _max_bursts,
		"max_trails_alive": _max_trails, "master": "%s-4k.mkv (FFV1 lossless, bgr0, %d fps)" % [mode, fps],
		"subviewport": [W, H]}
	var sfile: FileAccess = FileAccess.open(out_dir.path_join("%s-summary.json" % mode), FileAccess.WRITE)
	sfile.store_string(JSON.stringify(summary, "\t"))
	sfile.close()
	print("CAPTURE %s: %d engine frames, %d master frames, failed='%s'" % [mode, frame, mframe, failed])
	quit(0 if failed == "" else 1)
