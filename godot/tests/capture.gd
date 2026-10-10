extends SceneTree
## Windowed screenshot capture (needs a renderer, so NOT headless):
## Godot_v4.7.2-stable_win64.exe --path godot --script res://tests/capture.gd
## Saves PNGs of the storyboard moments to <repo>/evidence/screens-<unix time>/.

const Runner = preload("res://tests/route_runner.gd")
const MainScene = preload("res://game/main.tscn")

var main: Variant
var audio: Variant
var out_dir: String = ""
var shots: Array[String] = []
var _seen: Dictionary = {}


func _initialize() -> void:
	_run()


func _key(code: int) -> void:
	for pressed: bool in [true, false]:
		var ev: InputEventKey = InputEventKey.new()
		ev.keycode = code as Key
		ev.physical_keycode = code as Key
		ev.pressed = pressed
		root.push_input(ev)


func _shot(label: String) -> void:
	await process_frame # let the state change reach the next drawn frame
	await RenderingServer.frame_post_draw
	var img: Image = root.get_texture().get_image()
	var path: String = out_dir.path_join("%02d-%s.png" % [shots.size() + 1, label])
	img.save_png(path)
	shots.append(path)
	print("saved ", path)


func _frames(n: int) -> void:
	for i: int in n:
		await process_frame


## Waits for cond while firing one-off captures from the monitor.
func _wait(cond: Callable, max_frames: int = 20000) -> void:
	for i: int in max_frames:
		await _monitor()
		if cond.call():
			return
		await process_frame


func _once(label: String) -> bool:
	if _seen.has(label):
		return false
	_seen[label] = true
	return true


func _monitor() -> void:
	var s: String = main.state_name()
	if s == "PLAY_MOVES" and main.pieces["p1"].is_hopping() and _once("move-playback"):
		await _frames(4)
		await _shot("move-playback-hop")
	if int(audio.play_counts["SFX-HIT"]) > 0 and _once("hit"):
		await _frames(8)
		await _shot("attack-hit-enemy-hurt")
	if int(audio.play_counts["SFX-HURT"]) > 0 and _once("hurt"):
		await _frames(8)
		await _shot("player-hurt")
	if s == "PLAY_ATTACKS" and main._arrows.size() > 0 and _once("arrow"):
		await _frames(3)
		await _shot("arrow-in-flight")


func _play(route: Dictionary, tag: String) -> void:
	for step: Dictionary in route["turns"]:
		await _wait(func() -> bool: return main.state_name() == "PLAN_MOVE")
		var turn_no: int = main.rules.turn
		var mv: Vector2i = Runner.move_of(step)
		if mv == Vector2i.ZERO:
			_key(KEY_SPACE)
		else:
			if mv.x == 1:
				_key(KEY_RIGHT)
			elif mv.x == -1:
				_key(KEY_LEFT)
			if mv.y == -1:
				_key(KEY_UP)
			elif mv.y == 1:
				_key(KEY_DOWN)
			if turn_no == 1 and _once("plan-move-" + tag):
				await _shot("plan-move-marker-" + tag)
			_key(KEY_ENTER)
		await _wait(func() -> bool:
			var s: String = main.state_name()
			return s == "PLAN_ATTACK" or s == "WON" or s == "LOST" or (s == "PLAN_MOVE" and main.rules.turn > turn_no))
		if main.state_name() == "PLAN_ATTACK":
			if _once("plan-attack-" + tag):
				await _shot("plan-attack-target-" + tag)
			var t: Variant = Runner.target_of(step)
			if t == null:
				_key(KEY_SPACE)
			else:
				while main.selected_target() != t:
					_key(KEY_RIGHT)
				_key(KEY_ENTER)
			await _wait(func() -> bool:
				var s: String = main.state_name()
				return s == "WON" or s == "LOST" or (s == "PLAN_MOVE" and main.rules.turn > turn_no))
	await _wait(func() -> bool: return main.state_name() == "WON" or main.state_name() == "LOST")


func _secs(t: float) -> void:
	await create_timer(t).timeout


func _run() -> void:
	out_dir = ProjectSettings.globalize_path("res://").path_join("../evidence/screens-%d" % int(Time.get_unix_time_from_system())).simplify_path()
	DirAccess.make_dir_recursive_absolute(out_dir)
	await process_frame
	main = MainScene.instantiate()
	main.time_scale = 1.0
	root.add_child(main)
	audio = main.audio
	await _secs(0.5)
	await _shot("title")
	_key(KEY_ENTER)
	await _secs(0.3)
	await _shot("board-start")
	_key(KEY_F3)
	await _secs(0.1)
	await _shot("footprint-debug-f3")
	_key(KEY_F3)
	_key(KEY_P)
	await _secs(0.1)
	await _shot("paused")
	_key(KEY_P)
	await _secs(0.1)
	await _play(Runner.load_route("res://tests/fixtures/win_route.json"), "win")
	await _secs(0.6)
	await _shot("win-card")
	await _wait(func() -> bool: return main._card_lock <= 0.0)
	_key(KEY_ENTER)
	await _secs(0.2)
	await _shot("results-victory")
	_key(KEY_ENTER)
	await _secs(0.2)
	await _play(Runner.load_route("res://tests/fixtures/lose_route.json"), "lose")
	await _secs(1.0)
	await _shot("defeat-card")
	_key(KEY_R)
	await _secs(0.2)
	await _shot("retry-board")
	print("CAPTURE DONE: %d screenshots in %s (final state %s, retries %d)" % [shots.size(), out_dir, main.state_name(), main.retries])
	quit(0)
