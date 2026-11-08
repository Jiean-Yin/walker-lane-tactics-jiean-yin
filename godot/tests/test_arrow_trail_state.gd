extends SceneTree
## A6 headless test: Effect B (arrow trail) state rules B1-B6 (CHANGE-BRIEF §2 "Observable rules", §4).
## ./scripts/run-test.sh test_arrow_trail_state.gd 60
##
## Drives main.tscn through the real game loop with real key presses (root.push_input); the
## trigger (ArrowTrailDriver) is never called directly. A Sampler node with process_priority 1000
## records one row per frame, after main (0) and the drivers (10): every arrow in main._arrows
## (the oracle; arrows are told apart by identity) with its tip by main.gd:718-721, and every
## live trail.
##
## Run 1 ("win"): title (load) -> win route (tests/fixtures/win_route.json): turn 4 has two
##   arrows, turn 5 one. Then play again.
## Run 2 ("pause"): win route turns 1-3, then turn 4. Arrow 1: P pause mid-flight, unpause,
##   main.time_scale 0.5 (no key exists for it; the one game value this test writes), then the
##   trail hidden for 4 frames. Arrow 2: SceneTree paused mid-flight. Turn 5: R mid-flight.
##
## Not covered by play: "attack_cancelled" cannot happen in this 1-vs-1 slice (valid_targets
## only offers squares holding an enemy, rules.gd:194-205), so B3's "not on a cancel" rests on
## the per-frame count (a trail only ever appears with a new arrow); the test asserts that no
## cancel occurred, so the gap stays visible.
## Feedback-loop guard: Effect B has no value -> amount_ratio mapping in the brief; the test checks
## that amount and amount_ratio never change (at time_scale 1.0 and 0.5) while speed_scale does.

const Report = preload("res://tests/test_report.gd")
const Runner = preload("res://tests/route_runner.gd")
const RulesScript = preload("res://game/rules.gd")
const MainScript = preload("res://game/main.gd")
const MainScene = preload("res://game/main.tscn")
const TrailScene = preload("res://effects/arrow_trail.tscn")

const EMITTERS: Array[String] = ["Streak", "Wisps"]
const POS_EPS: float = 1.0 ## px, CHANGE-BRIEF §4 "follows the tip within 1 px"
const HOLD_FRAMES: int = 120 ## 2 s at 60 fps: longer than a trail's whole fade
const MAX_FRAMES: int = 20000


## Records one row per frame, after every other _process() of that frame.
class Sampler extends Node:
	var row_fn: Callable
	var rows: Array[Dictionary] = []

	func _process(delta: float) -> void:
		if row_fn.is_valid():
			rows.append(row_fn.call(delta))


var rep: Report
var main: Variant
var driver: Node2D
var sampler: Sampler
var phase: String = "load"
var hidden_id: int = 0 ## instance id of the trail the test has hidden (0 = none)
var _seen: int = 0 ## oracle's read position in main.played_events
var _known: Array = [] ## every arrow Dictionary seen; its index is the arrow's number
var summary: Dictionary = {}


func _initialize() -> void:
	_run()


# ---------------------------------------------------------------- helpers

func _key(code: int) -> void:
	for pressed: bool in [true, false]:
		var ev: InputEventKey = InputEventKey.new()
		ev.keycode = code as Key
		ev.physical_keycode = code as Key
		ev.pressed = pressed
		root.push_input(ev)


func _s() -> String:
	return main.state_name()


func _frames(n: int) -> void:
	for i: int in n:
		await process_frame


func _wait(cond: Callable) -> bool:
	for i: int in MAX_FRAMES:
		if cond.call():
			return true
		await process_frame
	return false


func _cell(id: String) -> Vector2i:
	return RulesScript.cell_of(main.rules.get_unit(id))


## The arrow tip, by the formula of main.gd:718-721 (written out here, not taken from the driver).
func _tip(a: Dictionary) -> Vector2:
	var s: float = clampf(float(a["t"]) / MainScript.ARROW_TIME, 0.0, 1.0)
	var from: Vector2 = a["from"]
	var to: Vector2 = a["to"]
	return from.lerp(to, s) + Vector2(0.0, -MainScript.ARROW_ARC * 4.0 * s * (1.0 - s))


func _count_since(from: int, type: String) -> int:
	var n: int = 0
	for i: int in range(from, main.event_log.size()):
		if main.event_log[i]["type"] == type:
			n += 1
	return n


func _emitters(trail: Node) -> Array[GPUParticles2D]:
	var out: Array[GPUParticles2D] = []
	for n: String in EMITTERS:
		out.append(trail.get_node(n) as GPUParticles2D)
	return out


func _emitting(trail: Node) -> Array:
	return _emitters(trail).map(func(e: GPUParticles2D) -> bool: return e.emitting)


func _speeds(trail: Node) -> Array:
	return _emitters(trail).map(func(e: GPUParticles2D) -> float: return e.speed_scale)


## One row per frame (the oracle): events played this frame, every arrow in flight, every trail.
func _row(delta: float) -> Dictionary:
	var played: Array[Dictionary] = main.played_events
	var reset: bool = played.size() < _seen
	if reset:
		_seen = 0
	var damaged: int = 0
	while _seen < played.size():
		if played[_seen]["type"] == "damaged":
			damaged += 1
		_seen += 1
	var arrows: Array = []
	for a: Dictionary in main._arrows:
		var k: int = -1
		for j: int in _known.size():
			if is_same(_known[j], a):
				k = j
				break
		if k < 0:
			k = _known.size()
			_known.append(a)
		arrows.append({"k": k, "from": a["from"], "tip": _tip(a)})
	var trails: Array = []
	for tr: Node2D in driver.live_trails():
		var es: Array[GPUParticles2D] = _emitters(tr)
		trails.append({"id": tr.get_instance_id(), "pos": tr.position, "visible": tr.visible,
			"emitting": es.map(func(e: GPUParticles2D) -> bool: return e.emitting),
			"speed": es.map(func(e: GPUParticles2D) -> float: return e.speed_scale),
			"amount": es.map(func(e: GPUParticles2D) -> int: return e.amount),
			"ratio": es.map(func(e: GPUParticles2D) -> float: return e.amount_ratio),
			"parent_is_driver": tr.get_parent() == driver})
	return {"i": sampler.rows.size(), "phase": phase, "reset": reset, "paused": main.paused,
		"ts": main.time_scale, "delta": delta, "dt": 0.0 if main.paused else delta * main.time_scale,
		"damaged": damaged, "arrows": arrows, "trails": trails, "spawned": driver.spawned,
		"hidden_id": hidden_id, "state": _s()}


## From PLAN_MOVE: give the route step's move and attack orders through real keys.
## Returns false if the scene did not follow. Does not wait for the attack playback.
func _give_orders(step: Dictionary, label: String) -> bool:
	if not await _wait(func() -> bool: return _s() == "PLAN_MOVE"):
		rep.check("%s: reached PLAN_MOVE" % label, false, _s())
		return false
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
		_key(KEY_ENTER)
	var after_moves: Callable = func() -> bool:
		var s: String = _s()
		return s == "PLAN_ATTACK" or s == "PLAY_ATTACKS" or s == "WON" or s == "LOST" \
			or (s == "PLAN_MOVE" and main.rules.turn > turn_no)
	if not await _wait(after_moves):
		rep.check("%s: move playback finished" % label, false, _s())
		return false
	var t: Variant = Runner.target_of(step)
	if _s() == "PLAN_ATTACK":
		if t == null:
			_key(KEY_SPACE)
		else:
			var n: int = 0
			while main.selected_target() != t and n < 30:
				_key(KEY_RIGHT)
				n += 1
			if main.selected_target() != t:
				rep.check("%s: target %s selectable" % [label, t], false, main.targets)
				return false
			_key(KEY_ENTER)
	elif t != null:
		rep.check("%s: the route's target %s could be ordered" % [label, t], false, _s())
		return false
	return true


func _turn_done(turn_no: int) -> bool:
	var s: String = _s()
	return s == "WON" or s == "LOST" or (s == "PLAN_MOVE" and main.rules.turn > turn_no)


## Plays one whole route step (orders + playback).
func _play_turn(step: Dictionary, label: String) -> bool:
	var turn_no: int = main.rules.turn
	if not await _give_orders(step, label):
		return false
	if not await _wait(_turn_done.bind(turn_no)):
		rep.check("%s: attack playback finished" % label, false, _s())
		return false
	return true


## Waits for trail number `n` (driver.spawned == n) and returns it, or null.
func _wait_trail(n: int, label: String) -> Node2D:
	if not await _wait(func() -> bool: return driver.spawned >= n):
		rep.check("%s: a trail appeared" % label, false, _s())
		return null
	var live: Array[Node2D] = driver.live_trails()
	return live[-1] if not live.is_empty() else null


# ---------------------------------------------------------------- run

func _run() -> void:
	rep = Report.new("test_arrow_trail_state")
	await process_frame
	main = MainScene.instantiate()
	root.add_child(main)
	driver = main.get_node_or_null("ArrowTrailDriver") as Node2D
	sampler = Sampler.new()
	sampler.name = "Sampler"
	sampler.process_priority = 1000
	root.add_child(sampler)
	if not rep.check("main.tscn has an ArrowTrailDriver (Node2D, process_priority 10) under Main",
			driver != null and driver.process_priority == 10 and driver.get_parent() == main):
		quit(rep.finish())
		return

	var probe: Node2D = TrailScene.instantiate() as Node2D
	var scene_amounts: Array = []
	var scene_ratios: Array = []
	var fade: float = 0.0 ## longest emitter lifetime, read from the scene (not tuned here)
	for e: GPUParticles2D in _emitters(probe):
		scene_amounts.append(e.amount)
		scene_ratios.append(e.amount_ratio)
		fade = maxf(fade, e.lifetime)
	var probe_z: int = probe.z_index
	var probe_rel: bool = probe.z_as_relative
	probe.free()
	rep.check("draw order: driver z_index 2 (relative), ArrowTrail root z_index 0 relative, so a trail draws at z 2; the driver is before main's _fx_layer (z 2) in the tree, so the drawn arrow is on top",
		driver.z_index == 2 and driver.z_as_relative and probe_z == 0 and probe_rel
		and driver.get_index() < main._fx_layer.get_index(),
		"driver z %d, trail z %d rel %s, driver index %d, fx index %d"
		% [driver.z_index, probe_z, probe_rel, driver.get_index(), main._fx_layer.get_index()])
	sampler.row_fn = _row

	var win: Dictionary = Runner.load_route("res://tests/fixtures/win_route.json")
	var turns: Array = win["turns"]

	# ---------------------------------------------------- run 1: load + the win route
	await _frames(30)
	rep.check("B3 load: 30 frames on the title, no trail", _s() == "TITLE" and driver.spawned == 0
		and driver.get_child_count() == 0, "spawned %d, children %d" % [driver.spawned, driver.get_child_count()])
	phase = "win"
	_key(KEY_ENTER)
	await process_frame
	rep.check("start cells: p1 at column 0, lane 5 (zero-based (0, 4)); e1 at column 7, lane 4 ((7, 3))",
		_s() == "PLAN_MOVE" and _cell("p1") == Vector2i(0, 4) and _cell("e1") == Vector2i(7, 3),
		"%s %s %s" % [_s(), _cell("p1"), _cell("e1")])
	var log_start: int = main.event_log.size()
	for i: int in turns.size():
		if not await _play_turn(turns[i], "win turn %d" % (i + 1)):
			quit(rep.finish())
			return
	rep.check("win route ends in WON", _s() == "WON", _s())
	var attacks: int = _count_since(log_start, "attack")
	rep.check("B1 win route: 3 attack events (turn 4: two, turn 5: one) and 3 trails", attacks == 3 and driver.spawned == 3,
		"attacks %d, spawned %d" % [attacks, driver.spawned])
	rep.check("B3 cancel: no attack_cancelled in the win route (not reachable in this 1-vs-1 slice; B3's cancel case is covered only by the per-frame count)",
		_count_since(log_start, "attack_cancelled") == 0, _count_since(log_start, "attack_cancelled"))
	if not await _wait(func() -> bool: return driver.live_trails().is_empty()):
		rep.check("every trail of run 1 freed", false)
	# play again: Enter (results) after the card lock, Enter again (restart)
	phase = "again"
	await _wait(func() -> bool: return main._card_lock <= 0.0)
	_key(KEY_ENTER)
	await process_frame
	_key(KEY_ENTER)
	await process_frame
	var spawned_after_again: int = driver.spawned
	await _frames(30)
	rep.check("B3 play again: back to PLAN_MOVE turn 1, no trail for 30 frames",
		_s() == "PLAN_MOVE" and main.rules.turn == 1 and driver.spawned == spawned_after_again
		and driver.live_trails().is_empty(), "%s turn %d" % [_s(), main.rules.turn])

	# ---------------------------------------------------- run 2: pause, time scale, hidden, tree pause, R
	phase = "pause"
	for i: int in 3:
		if not await _play_turn(turns[i], "run 2 turn %d" % (i + 1)):
			quit(rep.finish())
			return
	var base: int = driver.spawned
	var t4_turn: int = main.rules.turn
	if not await _give_orders(turns[3], "run 2 turn 4"):
		quit(rep.finish())
		return

	# arrow 1: P pause
	var tr1: Node2D = await _wait_trail(base + 1, "run 2 arrow 1")
	if tr1 == null:
		quit(rep.finish())
		return
	await _frames(4)
	rep.check("run 2 arrow 1 is in flight before the pause", main._arrows.size() == 1 and _emitting(tr1) == [true, true],
		main._arrows.size())
	_key(KEY_P)
	await process_frame
	var held: Vector2 = tr1.position
	var held_t: float = float(main._arrows[0]["t"]) if not main._arrows.is_empty() else -1.0
	var clock: float = main._clock
	var hold_ok: bool = true
	for f: int in HOLD_FRAMES:
		await process_frame
		if _speeds(tr1) != [0.0, 0.0] or _emitting(tr1) != [true, true] or tr1.position != held:
			hold_ok = false
	rep.check("B4 P pause: 2 s mid-flight; every frame speed_scale 0, emitting true, trail not moved; the arrow and the game clock did not move",
		main.paused and hold_ok and tr1 in driver.live_trails() and main._clock == clock
		and not main._arrows.is_empty() and float(main._arrows[0]["t"]) == held_t,
		"paused %s, speeds %s, emitting %s, clock %f -> %f" % [main.paused, _speeds(tr1), _emitting(tr1), clock, main._clock])
	_key(KEY_P)
	await process_frame
	rep.check("B4 unpause: speed_scale back to 1.0, the trail follows the tip again",
		not main.paused and _speeds(tr1) == [1.0, 1.0] and tr1.position != held and not main._arrows.is_empty()
		and tr1.position.distance_to(_tip(main._arrows[0])) <= POS_EPS, "%s %s" % [_speeds(tr1), tr1.position])

	# arrow 1: B6 time scale (also the feedback-loop guard: speed_scale changes, amount and amount_ratio do not)
	main.time_scale = 0.5
	await _frames(4)
	rep.check("B6 time scale: with main.time_scale 0.5, speed_scale 0.5 on both emitters; amount and amount_ratio unchanged from the scene",
		_speeds(tr1) == [0.5, 0.5] and _emitters(tr1).map(func(e: GPUParticles2D) -> int: return e.amount) == scene_amounts
		and _emitters(tr1).map(func(e: GPUParticles2D) -> float: return e.amount_ratio) == scene_ratios,
		"speeds %s, amounts %s, scene %s %s" % [_speeds(tr1), _emitters(tr1).map(func(e: GPUParticles2D) -> int: return e.amount),
			scene_amounts, scene_ratios])

	# arrow 1: B5 hidden
	hidden_id = tr1.get_instance_id()
	tr1.visible = false
	var pos_before_hide: Vector2 = tr1.position
	await _frames(4)
	rep.check("B5 hidden: 4 frames with visible false; emitting unchanged (true, true), still hidden (no code reacts), the trail kept following the tip",
		not tr1.visible and _emitting(tr1) == [true, true] and not main._arrows.is_empty()
		and tr1.position != pos_before_hide and tr1.position.distance_to(_tip(main._arrows[0])) <= POS_EPS,
		"visible %s, emitting %s, in flight %d" % [tr1.visible, _emitting(tr1), main._arrows.size()])
	tr1.visible = true
	hidden_id = 0
	main.time_scale = 1.0

	# arrow 2: tree pause (the game never does this; the test does)
	var tr2: Node2D = await _wait_trail(base + 2, "run 2 arrow 2")
	if tr2 == null:
		quit(rep.finish())
		return
	await _frames(4)
	rep.check("run 2 arrow 2 is in flight before the tree pause", main._arrows.size() == 1 and _emitting(tr2) == [true, true],
		main._arrows.size())
	var tp_pos: Vector2 = tr2.position
	var tp_t: float = float(main._arrows[0]["t"])
	var clock2: float = main._clock
	paused = true
	await process_frame
	var no_process: bool = not driver.can_process() and _emitters(tr2).all(func(e: GPUParticles2D) -> bool: return not e.can_process())
	await _frames(HOLD_FRAMES)
	var tp_alive: bool = is_instance_valid(tr2) and tr2 in driver.live_trails()
	var tp_ok: bool = tp_alive and _emitting(tr2) == [true, true] and tr2.position == tp_pos \
		and float(main._arrows[0]["t"]) == tp_t and main._clock == clock2
	paused = false
	await process_frame
	rep.check("B4 tree pause: 2 s with the SceneTree paused mid-flight; the driver and both emitters do not process; the trail is alive, still emitting, not moved; the arrow and the game clock did not move",
		no_process and tp_ok, "no_process %s, alive %s, emitting %s, clock %f -> %f"
		% [no_process, tp_alive, _emitting(tr2) if tp_alive else [], clock2, main._clock])

	# turn 5: R while the arrow is in flight
	if not await _wait(_turn_done.bind(t4_turn)):
		rep.check("run 2 turn 4 finished", false, _s())
		quit(rep.finish())
		return
	if not await _give_orders(turns[4], "run 2 turn 5"):
		quit(rep.finish())
		return
	var tr3: Node2D = await _wait_trail(base + 3, "run 2 arrow 3")
	if tr3 == null:
		quit(rep.finish())
		return
	await _frames(4)
	rep.check("run 2 arrow 3 is in flight before R", main._arrows.size() == 1 and _emitting(tr3) == [true, true], main._arrows.size())
	phase = "reset"
	_key(KEY_R)
	await process_frame
	var after_r: int = driver.spawned
	var zero_frames: int = 0
	for f: int in HOLD_FRAMES:
		if driver.live_trails().is_empty() and driver.get_child_count() == 0:
			zero_frames += 1
		await process_frame
	rep.check("B3 R: zero trails on the frame after R and for the next 2 s; no new trail; back to PLAN_MOVE turn 1",
		zero_frames == HOLD_FRAMES and driver.spawned == after_r and _s() == "PLAN_MOVE" and main.rules.turn == 1,
		"zero frames %d/%d, %s turn %d" % [zero_frames, HOLD_FRAMES, _s(), main.rules.turn])

	sampler.row_fn = Callable()
	_analyze(fade, scene_amounts, scene_ratios)
	quit(rep.finish(summary))


# ---------------------------------------------------------------- per-frame analysis

func _analyze(fade: float, scene_amounts: Array, scene_ratios: Array) -> void:
	var rows: Array[Dictionary] = sampler.rows
	var frame: float = 1.0 / 60.0
	var bad_delta: int = 0
	for r: Dictionary in rows:
		if absf(float(r["delta"]) - frame) > 1e-6:
			bad_delta += 1
	rep.check("every frame's delta is exactly 1/60 s (--fixed-fps 60; the frame counts below assume it)",
		bad_delta == 0 and rows.size() > 0, "%d of %d rows differ" % [bad_delta, rows.size()])

	var prev_trails: Dictionary = {} ## id -> trail row
	var prev_arrows: Dictionary = {} ## k -> arrow row
	var prev_spawned: int = 0
	var trail_arrow: Dictionary = {} ## trail id -> arrow number
	var stopped: Dictionary = {} ## trail id -> position at the stop
	var age: Dictionary = {} ## trail id -> game seconds since its stop row
	var count_errors: Array[String] = []
	var spawn_errors: Array[String] = []
	var follow_errors: Array[String] = []
	var stop_errors: Array[String] = []
	var after_errors: Array[String] = []
	var speed_errors: Array[String] = []
	var guard_errors: Array[String] = []
	var parent_errors: Array[String] = []
	var visible_errors: Array[String] = []
	var free_ages: Array = []
	var reset_freed: int = 0
	var landed: int = 0 ## arrows that left _arrows other than by a reset
	var stop_rows: Array = []
	var damaged_rows: Array = []
	var max_live: int = 0
	var follow_rows: int = 0
	var ts_half_rows: int = 0
	for r: Dictionary in rows:
		var i: int = r["i"]
		var dt: float = r["dt"]
		var now_t: Dictionary = {}
		for t: Dictionary in r["trails"]:
			now_t[t["id"]] = t
		var now_a: Dictionary = {}
		for a: Dictionary in r["arrows"]:
			now_a[a["k"]] = a
		var new_trails: Array = []
		for t: Dictionary in r["trails"]:
			if not prev_trails.has(t["id"]):
				new_trails.append(t["id"])
		var new_arrows: Array = []
		for a: Dictionary in r["arrows"]:
			if not prev_arrows.has(a["k"]):
				new_arrows.append(a["k"])
		if not r["reset"]:
			for k: int in prev_arrows:
				if not now_a.has(k):
					landed += 1
		if int(r["damaged"]) > 0:
			damaged_rows.append(i)
		# trails that disappeared this row
		for id: int in prev_trails:
			if now_t.has(id):
				continue
			if r["reset"]:
				reset_freed += 1
			elif stopped.has(id):
				free_ages.append(snappedf(float(age[id]) + dt, 0.0001))
			else:
				after_errors.append("row %d: trail freed while its arrow was in flight" % i)
		# B1 / B3: one new trail per new arrow, never otherwise
		if new_trails.size() != new_arrows.size() or int(r["spawned"]) - prev_spawned != new_arrows.size():
			count_errors.append("row %d (%s): %d new arrows, %d new trails, spawned +%d"
				% [i, r["phase"], new_arrows.size(), new_trails.size(), int(r["spawned"]) - prev_spawned])
		for j: int in mini(new_trails.size(), new_arrows.size()):
			var t: Dictionary = now_t[new_trails[j]]
			var a: Dictionary = now_a[new_arrows[j]]
			trail_arrow[new_trails[j]] = new_arrows[j]
			if (t["pos"] as Vector2).distance_to(a["from"]) > POS_EPS:
				spawn_errors.append("row %d: trail at %s, arrow from %s" % [i, t["pos"], a["from"]])
			if t["emitting"] != [true, true]:
				spawn_errors.append("row %d: emitting %s on the spawn frame" % [i, t["emitting"]])
		# existing trails: follow, stop, hold
		for id: int in now_t:
			var t: Dictionary = now_t[id]
			if id in new_trails or not trail_arrow.has(id):
				continue
			var k: int = trail_arrow[id]
			if stopped.has(id):
				age[id] = float(age[id]) + dt
				if t["emitting"] != [false, false] or t["pos"] != stopped[id]:
					after_errors.append("row %d: after the stop, emitting %s, pos %s (stopped at %s)"
						% [i, t["emitting"], t["pos"], stopped[id]])
			elif now_a.has(k):
				follow_rows += 1
				var d: float = (t["pos"] as Vector2).distance_to(now_a[k]["tip"])
				if d > POS_EPS:
					follow_errors.append("row %d: %.3f px from the tip" % [i, d])
				if t["emitting"] != [true, true]:
					follow_errors.append("row %d: emitting %s in flight" % [i, t["emitting"]])
			else:
				stopped[id] = t["pos"]
				age[id] = 0.0
				stop_rows.append(i)
				if t["emitting"] != [false, false]:
					stop_errors.append("row %d: emitting %s on the frame the arrow left" % [i, t["emitting"]])
				if t["pos"] != prev_trails[id]["pos"]:
					stop_errors.append("row %d: moved at the stop, %s -> %s" % [i, prev_trails[id]["pos"], t["pos"]])
		# every trail, every row
		var want: float = 0.0 if r["paused"] else float(r["ts"])
		for t: Dictionary in r["trails"]:
			for s: float in t["speed"]:
				if s != want:
					speed_errors.append("row %d: speed_scale %f, want %f" % [i, s, want])
					break
			if t["amount"] != scene_amounts or t["ratio"] != scene_ratios:
				guard_errors.append("row %d: amount %s ratio %s" % [i, t["amount"], t["ratio"]])
			if not t["parent_is_driver"]:
				parent_errors.append("row %d" % i)
			if bool(t["visible"]) != (int(t["id"]) != int(r["hidden_id"])):
				visible_errors.append("row %d: visible %s" % [i, t["visible"]])
		if float(r["ts"]) == 0.5 and not (r["trails"] as Array).is_empty():
			ts_half_rows += 1
		max_live = maxi(max_live, (r["trails"] as Array).size())
		prev_trails = now_t
		prev_arrows = now_a
		prev_spawned = int(r["spawned"])

	rep.check("B1/B3 every frame: new trails == arrows that entered main._arrows that frame, and never otherwise (load, turns without shots, play again, after R)",
		count_errors.is_empty() and rows.size() > 0, "%d rows; %s" % [rows.size(), count_errors.slice(0, 5)])
	rep.check("B1: each trail starts at its arrow's from point (within %.0f px), both emitters emitting, on the frame the arrow appears" % POS_EPS,
		spawn_errors.is_empty() and trail_arrow.size() == 6, "%d trails; %s" % [trail_arrow.size(), spawn_errors.slice(0, 5)])
	rep.check("B2 follow: on every later frame in flight the trail is within %.0f px of the tip (main.gd:718-721), emitting" % POS_EPS,
		follow_errors.is_empty() and follow_rows > 0, "%d rows; %s" % [follow_rows, follow_errors.slice(0, 5)])
	rep.check("B2 stop: on the frame each arrow leaves main._arrows, both emitters stop, and the trail stays at its last tip position",
		stop_errors.is_empty() and stop_rows.size() == landed and landed == 5, "%d stops, %d landings; %s" % [stop_rows.size(), landed, stop_errors.slice(0, 5)])
	rep.check("B2 after the stop: never emitting again and never moved until freed; no trail freed while its arrow flew",
		after_errors.is_empty(), after_errors.slice(0, 5))
	var offsets: Array = []
	for s: int in stop_rows:
		var best: int = 1 << 30
		for d: int in damaged_rows:
			if absi(s - d) < absi(best):
				best = s - d
		offsets.append(best)
	# Bound revised in CHANGE-BRIEF Revision 1 item 3 (measured 0, -2, 0, 0, -2); was -1..1.
	rep.check("B2: each stop is 0 to 2 frames before the impact (stop row - damaged row in -2..0)",
		offsets.size() == 5 and offsets.all(func(o: int) -> bool: return o >= -2 and o <= 0), offsets)
	var ages_ok: bool = free_ages.size() == 5
	for a: float in free_ages:
		if a < fade - 1e-6 or a > fade + frame + 1e-6:
			ages_ok = false
	rep.check("B2 free: each landed trail freed %.2f s (+1 frame) of game time after its stop (longest emitter lifetime, from the scene)" % fade,
		ages_ok, free_ages)
	rep.check("B3 R: the one trail alive at R was cleared by the reset, not by finishing", reset_freed == 1, reset_freed)
	rep.check("B4/B6 every frame: speed_scale == 0 while main.paused, == main.time_scale otherwise",
		speed_errors.is_empty(), speed_errors.slice(0, 5))
	rep.check("feedback-loop guard: every frame, amount %s and amount_ratio %s as saved in the scene (also on %d frames at time_scale 0.5)"
		% [scene_amounts, scene_ratios, ts_half_rows], guard_errors.is_empty() and ts_half_rows > 0, guard_errors.slice(0, 5))
	rep.check("every trail is a child of ArrowTrailDriver on every frame", parent_errors.is_empty(), parent_errors.slice(0, 5))
	rep.check("B5: visible is true on every frame except where the test hid the trail (no code sets it)",
		visible_errors.is_empty(), visible_errors.slice(0, 5))
	rep.check("at most 2 trails alive at once (CHANGE-BRIEF §2 peak)", max_live <= 2, max_live)
	summary = {"fps": 60 if bad_delta == 0 else 0, "rows": rows.size(), "trails": trail_arrow.size(),
		"stop_rows": stop_rows, "damaged_rows": damaged_rows, "stop_minus_impact_frames": offsets,
		"free_ages_game_s": free_ages, "fade_s": fade, "max_live": max_live, "reset_freed": reset_freed}
