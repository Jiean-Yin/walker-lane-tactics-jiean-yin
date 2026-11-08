extends SceneTree
## A6 headless test: Effect A (hit burst) state rules A1-A6 (CHANGE-BRIEF §1 "Observable rules", §4).
## ./scripts/run-test.sh test_hit_burst_state.gd 60
##
## Drives main.tscn through the real game loop with real key presses (root.push_input); the
## trigger (HitBurstDriver) is never called directly. A Sampler node with process_priority 1000
## records one row per frame, after main (0) and the driver (10): the "damaged" events that
## main played in that frame (the oracle, read from main.played_events) and every live burst.
##
## Run 1 ("win"): title (load) -> win route (tests/fixtures/win_route.json). Turn 4: two hits,
##   enemy first, 1.05 s apart; turn 5: the player's killing hit. Then play again.
## Run 2 ("pause"): win route turns 1-3, then turn 4 with P pause, time_scale 0.5 and a tree
##   pause during the first burst, and R pressed while both bursts of the turn are alive.
## Every hit and start cell the test relies on is asserted from main's event log, not assumed.

const Report = preload("res://tests/test_report.gd")
const Runner = preload("res://tests/route_runner.gd")
const RulesScript = preload("res://game/rules.gd")
const MainScene = preload("res://game/main.tscn")
const BurstScene = preload("res://effects/hit_burst.tscn")

const HIT_OFFSET: Vector2 = Vector2(0.0, -40.0) ## CHANGE-BRIEF §1 "Where"
const POS_EPS: float = 0.01
const HIT_GAP: float = 1.05 ## s between the two impacts of a two-hit turn (CHANGE-BRIEF §1)
const HOLD_FRAMES: int = 120 ## 2 s at 60 fps: longer than a burst's whole life
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
var fps: int = 0
var _seen: int = 0 ## oracle's read position in main.played_events
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


## The "damaged" events of event_log from index `from`, as [unit, by, hp_after].
func _damaged_since(from: int) -> Array:
	var out: Array = []
	for i: int in range(from, main.event_log.size()):
		var ev: Dictionary = main.event_log[i]
		if ev["type"] == "damaged":
			out.append([ev["unit"], ev["by"], int(ev["hp_after"])])
	return out


func _killed_since(from: int) -> Array:
	var out: Array = []
	for i: int in range(from, main.event_log.size()):
		if main.event_log[i]["type"] == "killed":
			out.append(main.event_log[i]["unit"])
	return out


## One row per frame (the oracle): new "damaged" events played this frame and every live burst.
func _row(delta: float) -> Dictionary:
	var played: Array[Dictionary] = main.played_events
	var reset: bool = played.size() < _seen
	if reset:
		_seen = 0
	var hits: Array = []
	while _seen < played.size():
		var ev: Dictionary = played[_seen]
		_seen += 1
		if ev["type"] == "damaged":
			var p: Node2D = main.pieces[ev["unit"]]
			hits.append({"unit": ev["unit"], "hp_after": int(ev["hp_after"]), "expect": p.position + HIT_OFFSET})
	var bursts: Array = []
	for b: Node2D in driver.live_bursts():
		var on: Array = []
		var sp: Array = []
		for e: Node in b.get_children():
			on.append((e as CPUParticles2D).emitting)
			sp.append((e as CPUParticles2D).speed_scale)
		bursts.append({"id": b.get_instance_id(), "pos": b.position, "emitting": on, "speed": sp,
			"parent_is_driver": b.get_parent() == driver})
	return {"i": sampler.rows.size(), "phase": phase, "reset": reset, "paused": main.paused, "ts": main.time_scale,
		"delta": delta, "dt": 0.0 if main.paused else delta * main.time_scale, "hits": hits, "bursts": bursts,
		"spawned": driver.spawned, "state": _s()}


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


func _live_ids() -> Array:
	var ids: Array = []
	for b: Node2D in driver.live_bursts():
		ids.append(b.get_instance_id())
	return ids


func _all_speeds() -> Array:
	var out: Array = []
	for b: Node2D in driver.live_bursts():
		for e: Node in b.get_children():
			out.append((e as CPUParticles2D).speed_scale)
	return out


# ---------------------------------------------------------------- run

func _run() -> void:
	rep = Report.new("test_hit_burst_state")
	await process_frame
	main = MainScene.instantiate()
	root.add_child(main)
	driver = main.get_node_or_null("HitBurstDriver") as Node2D
	sampler = Sampler.new()
	sampler.name = "Sampler"
	sampler.process_priority = 1000
	root.add_child(sampler)
	if not rep.check("main.tscn has a HitBurstDriver (Node2D, process_priority 10) under Main",
			driver != null and driver.process_priority == 10 and driver.get_parent() == main):
		quit(rep.finish())
		return
	sampler.row_fn = _row

	var burst_probe: Node = BurstScene.instantiate()
	var dust: CPUParticles2D = burst_probe.get_node("Dust") as CPUParticles2D
	# A6 window, read from the scene (not tuned here): each Dust particle lives
	# lifetime * (1 - lifetime_randomness * rand), so the shortest possible burst ends at
	# lifetime * (1 - lifetime_randomness); with explosiveness e the last particle is born up
	# to (1 - e) * lifetime late, so the longest ends at lifetime * (2 - e).
	var free_min: float = dust.lifetime * (1.0 - dust.lifetime_randomness)
	var free_max: float = dust.lifetime * (1.0 + (1.0 - dust.explosiveness))
	burst_probe.free()

	var win: Dictionary = Runner.load_route("res://tests/fixtures/win_route.json")
	var turns: Array = win["turns"]

	# ---------------------------------------------------- run 1: load + the win route
	await _frames(30)
	rep.check("A2 load: 30 frames on the title, no burst", _s() == "TITLE" and driver.spawned == 0
		and driver.get_child_count() == 0, "spawned %d, children %d" % [driver.spawned, driver.get_child_count()])
	phase = "win"
	_key(KEY_ENTER)
	await process_frame
	rep.check("start cells: p1 at column 0, lane 5 (zero-based (0, 4)); e1 at column 7, lane 4 ((7, 3))",
		_s() == "PLAN_MOVE" and _cell("p1") == Vector2i(0, 4) and _cell("e1") == Vector2i(7, 3),
		"%s %s %s" % [_s(), _cell("p1"), _cell("e1")])

	var log_start: int = main.event_log.size()
	for i: int in 3:
		if not await _play_turn(turns[i], "win turn %d" % (i + 1)):
			quit(rep.finish())
			return
	rep.check("win turns 1-3: no damaged event, no burst", _damaged_since(log_start).is_empty() and driver.spawned == 0,
		"damaged %s, spawned %d" % [_damaged_since(log_start), driver.spawned])

	var t4_log: int = main.event_log.size()
	if not await _play_turn(turns[3], "win turn 4"):
		quit(rep.finish())
		return
	var t4: Array = _damaged_since(t4_log)
	rep.check("win turn 4 hits: e1 hits p1 (4 -> 1), then p1 hits e1 (4 -> 1)",
		t4 == [["p1", "e1", 1], ["e1", "p1", 1]], t4)
	rep.check("win turn 4: two bursts created", driver.spawned == 2, driver.spawned)

	var t5_log: int = main.event_log.size()
	var spawned_before_t5: int = driver.spawned
	if not await _give_orders(turns[4], "win turn 5"):
		quit(rep.finish())
		return
	if not await _wait(func() -> bool: return driver.spawned > spawned_before_t5 or _s() == "WON"):
		rep.check("win turn 5: a burst appeared", false, _s())
	# A4 while the killing-hit burst is alive
	await _frames(20)
	var kb: Array[Node2D] = driver.live_bursts()
	var e1p: Node2D = main.pieces.get("e1")
	var kill_burst: Node2D = kb[-1] if not kb.is_empty() else null
	rep.check("A4: the killing-hit burst is alive 20 frames later, a child of the driver, not of the archer; the archer is still in the tree in its defeat pose",
		kill_burst != null and kill_burst.get_parent() == driver and e1p != null and is_instance_valid(e1p)
		and e1p.is_inside_tree() and not e1p.is_ancestor_of(kill_burst) and e1p.state == "defeat",
		"burst %s, e1 state %s" % [kill_burst, e1p.state if e1p != null else "none"])
	if not await _wait(func() -> bool: return _s() == "WON"):
		rep.check("win route ends in WON", false, _s())
		quit(rep.finish())
		return
	var t5: Array = _damaged_since(t5_log)
	rep.check("win turn 5 hit: p1 kills e1 (1 -> 0), no hit on p1",
		t5 == [["e1", "p1", 0]] and _killed_since(t5_log) == ["e1"], "%s killed %s" % [t5, _killed_since(t5_log)])
	rep.check("win route: 3 bursts in total == 3 damaged events", driver.spawned == 3 and _damaged_since(log_start).size() == 3,
		driver.spawned)
	if not await _wait(func() -> bool: return driver.live_bursts().is_empty()):
		rep.check("every burst of run 1 freed", false)
	# play again: Enter (results) after the card lock, Enter again (restart)
	phase = "again"
	await _wait(func() -> bool: return main._card_lock <= 0.0)
	_key(KEY_ENTER)
	await process_frame
	_key(KEY_ENTER)
	await process_frame
	var spawned_after_again: int = driver.spawned
	await _frames(30)
	rep.check("A2 play again: back to PLAN_MOVE turn 1, no burst for 30 frames",
		_s() == "PLAN_MOVE" and main.rules.turn == 1 and driver.spawned == spawned_after_again
		and driver.live_bursts().is_empty(), "%s turn %d" % [_s(), main.rules.turn])

	# ---------------------------------------------------- run 2: pause, time scale, tree pause, R
	phase = "pause"
	rep.check("run 2 start cells again (0, 4) and (7, 3)", _cell("p1") == Vector2i(0, 4) and _cell("e1") == Vector2i(7, 3))
	for i: int in 3:
		if not await _play_turn(turns[i], "run 2 turn %d" % (i + 1)):
			quit(rep.finish())
			return
	var r2_log: int = main.event_log.size()
	var base: int = driver.spawned
	if not await _give_orders(turns[3], "run 2 turn 4"):
		quit(rep.finish())
		return
	if not await _wait(func() -> bool: return driver.spawned == base + 1):
		rep.check("run 2 turn 4: first hit", false, _s())
		quit(rep.finish())
		return
	var first_id: int = _live_ids()[-1]
	await _frames(10)

	# A5: P pause
	_key(KEY_P)
	var clock: float = main._clock
	var pause_speeds_ok: bool = true
	for f: int in HOLD_FRAMES:
		await process_frame
		for s: float in _all_speeds():
			if s != 0.0:
				pause_speeds_ok = false
	rep.check("A5 pause: P held for 2 s (longer than a burst's life); every emitter's speed_scale is 0 every frame",
		main.paused and pause_speeds_ok and not _all_speeds().is_empty(), _all_speeds())
	rep.check("A5 pause: the burst is still alive after 2 s paused (its Dust has not finished) and the game clock did not move",
		first_id in _live_ids() and main._clock == clock, "clock %f -> %f" % [clock, main._clock])
	_key(KEY_P)
	await process_frame
	rep.check("A5 unpause: speed_scale back to time_scale 1.0", not main.paused and _all_speeds().all(func(s: float) -> bool: return s == 1.0),
		_all_speeds())

	# A5 / time scale: speed_scale follows main.time_scale
	main.time_scale = 0.5
	await _frames(10)
	rep.check("A5 time scale: with main.time_scale 0.5, every emitter's speed_scale is 0.5",
		_all_speeds().all(func(s: float) -> bool: return s == 0.5) and not _all_speeds().is_empty(), _all_speeds())
	main.time_scale = 1.0
	await process_frame

	# A5 tree pause (the game never does this; the test does)
	var clock2: float = main._clock
	paused = true
	await _frames(HOLD_FRAMES)
	var alive_in_tree_pause: bool = first_id in _live_ids()
	paused = false
	await process_frame
	rep.check("A5 tree pause: 2 s with the SceneTree paused; the burst holds (still alive) and the game clock did not move",
		alive_in_tree_pause and first_id in _live_ids() and main._clock - clock2 <= 1.5 / 60.0,
		"clock %f -> %f" % [clock2, main._clock])

	# second hit, then R while both bursts are alive
	if not await _wait(func() -> bool: return driver.spawned == base + 2):
		rep.check("run 2 turn 4: second hit", false, _s())
		quit(rep.finish())
		return
	var both: Array = _live_ids()
	rep.check("run 2 turn 4 hits: e1 hits p1 (4 -> 1), then p1 hits e1 (4 -> 1)",
		_damaged_since(r2_log) == [["p1", "e1", 1], ["e1", "p1", 1]], _damaged_since(r2_log))
	rep.check("A3 run 2: two bursts alive, the first one (through pause, time scale and tree pause) among them",
		both.size() == 2 and first_id in both, both)
	phase = "reset"
	_key(KEY_R)
	await process_frame
	var after_r: int = driver.spawned
	var zero_frames: int = 0
	for f: int in HOLD_FRAMES:
		if driver.live_bursts().is_empty() and driver.get_child_count() == 0:
			zero_frames += 1
		await process_frame
	rep.check("A2 / A4 R: zero bursts on the frame after R and for the next 2 s; no new burst; back to PLAN_MOVE turn 1",
		zero_frames == HOLD_FRAMES and driver.spawned == after_r and _s() == "PLAN_MOVE" and main.rules.turn == 1,
		"zero frames %d/%d, %s turn %d" % [zero_frames, HOLD_FRAMES, _s(), main.rules.turn])

	sampler.row_fn = Callable()
	_analyze(free_min, free_max)
	quit(rep.finish(summary))


# ---------------------------------------------------------------- per-frame analysis

func _analyze(free_min: float, free_max: float) -> void:
	var rows: Array[Dictionary] = sampler.rows
	var frame: float = 1.0 / 60.0
	var bad_delta: int = 0
	for r: Dictionary in rows:
		if absf(float(r["delta"]) - frame) > 1e-6:
			bad_delta += 1
	fps = 60 if bad_delta == 0 else 0
	rep.check("every frame's delta is exactly 1/60 s (--fixed-fps 60; the frame counts below assume it)",
		bad_delta == 0 and rows.size() > 0, "%d of %d rows differ" % [bad_delta, rows.size()])
	var prev: Dictionary = {} ## id -> burst row
	var prev_spawned: int = 0
	var age: Dictionary = {} ## id -> game seconds since its first row
	var born_phase: Dictionary = {}
	var count_errors: Array[String] = []
	var pos_errors: Array[String] = []
	var emit_errors: Array[String] = []
	var speed_errors: Array[String] = []
	var parent_errors: Array[String] = []
	var free_ages: Array = []
	var reset_freed: int = 0
	var max_live: int = 0
	var spawn_rows: Array = [] ## [row index, phase, burst id, unit, live bursts on that row]
	for r: Dictionary in rows:
		var now: Dictionary = {}
		for b: Dictionary in r["bursts"]:
			now[b["id"]] = b
		var new_ids: Array = []
		for b: Dictionary in r["bursts"]:
			if not prev.has(b["id"]):
				new_ids.append(b["id"])
		for id: int in prev:
			if now.has(id):
				age[id] = float(age[id]) + float(r["dt"])
			elif r["reset"]:
				reset_freed += 1
			else:
				free_ages.append([born_phase[id], snappedf(float(age[id]) + float(r["dt"]), 0.0001)])
		var hits: Array = r["hits"]
		if new_ids.size() != hits.size() or int(r["spawned"]) - prev_spawned != hits.size():
			count_errors.append("row %d (%s): %d damaged events, %d new bursts, spawned +%d"
				% [r["i"], r["phase"], hits.size(), new_ids.size(), int(r["spawned"]) - prev_spawned])
		for k: int in mini(new_ids.size(), hits.size()):
			var b: Dictionary = now[new_ids[k]]
			var expect: Vector2 = hits[k]["expect"]
			if (b["pos"] as Vector2).distance_to(expect) > POS_EPS:
				pos_errors.append("row %d: burst at %s, %s's body at %s" % [r["i"], b["pos"], hits[k]["unit"], expect])
			if not (b["emitting"] as Array).all(func(x: bool) -> bool: return x):
				emit_errors.append("row %d: emitting %s" % [r["i"], b["emitting"]])
			age[new_ids[k]] = 0.0
			born_phase[new_ids[k]] = r["phase"]
			spawn_rows.append([r["i"], r["phase"], new_ids[k], hits[k]["unit"], r["bursts"].size()])
		for b: Dictionary in r["bursts"]:
			var want: float = 0.0 if r["paused"] else float(r["ts"])
			for s: float in b["speed"]:
				if s != want:
					speed_errors.append("row %d: speed_scale %f, want %f" % [r["i"], s, want])
					break
			if not b["parent_is_driver"]:
				parent_errors.append("row %d" % r["i"])
		max_live = maxi(max_live, (r["bursts"] as Array).size())
		prev = now
		prev_spawned = int(r["spawned"])

	rep.check("A1/A2 every frame: new bursts == damaged events played that frame, and never otherwise (load, turns without hits, play again, after R)",
		count_errors.is_empty() and rows.size() > 0, "%d rows; %s" % [rows.size(), count_errors.slice(0, 5)])
	rep.check("A1 position: each burst at the hit archer's base-disc centre + (0, -40), within %.2f px" % POS_EPS,
		pos_errors.is_empty() and spawn_rows.size() == 5, "%d bursts; %s" % [spawn_rows.size(), pos_errors.slice(0, 5)])
	rep.check("A1: all three emitters emitting on the burst's first frame", emit_errors.is_empty(), emit_errors.slice(0, 5))
	rep.check("A4: every burst is a child of HitBurstDriver on every frame", parent_errors.is_empty(), parent_errors.slice(0, 5))
	rep.check("A5 every frame: speed_scale == 0 while main.paused, == main.time_scale otherwise", speed_errors.is_empty(),
		speed_errors.slice(0, 5))
	rep.check("A3: at most 2 bursts alive at once", max_live == 2, max_live)

	var win_spawns: Array = spawn_rows.filter(func(s: Array) -> bool: return s[1] == "win")
	var gap_ok: bool = false
	var gap: int = -1
	if win_spawns.size() >= 2:
		gap = int(win_spawns[1][0]) - int(win_spawns[0][0])
		gap_ok = absi(gap - roundi(HIT_GAP * 60.0)) <= 1
	rep.check("A3: turn 4's two impacts are %d +- 1 frames apart (1.05 s at 60 fps), inside one burst life" % roundi(HIT_GAP * 60.0),
		gap_ok, gap)
	rep.check("A3 overlap: on the frame of turn 4's second hit, 2 bursts are alive (the first one not re-fired, a new instance)",
		win_spawns.size() >= 2 and int(win_spawns[1][4]) == 2 and win_spawns[0][2] != win_spawns[1][2],
		win_spawns)
	rep.check("A1 killing hit: the third burst of run 1 is on e1", win_spawns.size() == 3 and win_spawns[2][3] == "e1", win_spawns)

	var ages_ok: bool = not free_ages.is_empty()
	for fa: Array in free_ages:
		var a: float = fa[1]
		if a < free_min - frame - 1e-6 or a > free_max + 2.0 * frame + 1e-6:
			ages_ok = false
	rep.check("A6: each burst not cleared by R freed itself after %.2f-%.2f s of game time (+2 frames), on Dust's finished" % [free_min, free_max],
		ages_ok and free_ages.size() == 3, free_ages)
	rep.check("A4 R: the two live bursts were cleared by the reset, not by finishing", reset_freed == 2, reset_freed)
	summary = {"fps": fps, "rows": rows.size(), "spawns": spawn_rows, "free_ages_game_s": free_ages,
		"free_window_s": [free_min, free_max], "max_live": max_live, "turn4_gap_frames": gap}
