extends SceneTree
## A7 Step 2 behaviour pins (CHANGE-BRIEF §8 "pins"): what the game does today, before any clip is wired.
## ./scripts/run-test.sh test_pins_a7.gd 60
##
## Drives main.tscn through the real game loop with real key presses sent through
## Input.parse_input_event (the A7 default). Such an event reaches main._unhandled_input one frame
## later (CLAUDE.md "Headless facts"), so every key is followed by frame waits. A Sampler node with
## process_priority 1000 records one row per frame, after main (0) and the A6 drivers (10).
##
## Run 1 ("win"): title -> win route (tests/fixtures/win_route.json) -> WON. Pins the state order,
##   each archer's pose order, and the three shots' timings: arrow, impact and back-to-idle frames
##   after the draw frame (nominal 12 / 33 / 48 at 60 fps, CHANGE-BRIEF §4), and the _arrows window.
## Run 2 ("interrupts"): R, the win route's turns 1-3, then turn 4 with Enter during the first
##   shot's startup (ignored), P held for 30 frames during its active phase, and R during the
##   second shot's active phase.
##
## The expected values are today's behaviour, measured with this test before any A7 change. The
## brief predicts that none of them changes when the clips are wired (CHANGE-BRIEF §8).

const Report = preload("res://tests/test_report.gd")
const Runner = preload("res://tests/route_runner.gd")
const RulesScript = preload("res://game/rules.gd")
const MainScene = preload("res://game/main.tscn")

const MAX_FRAMES: int = 20000
const PAUSE_FRAMES: int = 30

## Pinned: main.state with consecutive repeats collapsed, run 1 (title -> WON). Turns 1-3 have no
## target in range, so they skip PLAN_ATTACK (measured).
const STATE_ORDER: Array[String] = ["TITLE",
	"PLAN_MOVE", "PLAY_MOVES", "PLAY_ATTACKS",
	"PLAN_MOVE", "PLAY_MOVES", "PLAY_ATTACKS",
	"PLAN_MOVE", "PLAY_MOVES", "PLAY_ATTACKS",
	"PLAN_MOVE", "PLAY_MOVES", "PLAN_ATTACK", "PLAY_ATTACKS",
	"PLAN_MOVE", "PLAY_MOVES", "PLAN_ATTACK", "PLAY_ATTACKS", "WON"]
## Pinned: each archer's pose with consecutive repeats collapsed, run 1 (from the title). There is no
## hop image, so a hop shows idle (piece.gd:16, OPTIONAL_FALLBACK) and "hop" never appears (measured).
const P1_POSES: Array[String] = ["idle", "hurt", "draw", "idle", "draw", "idle", "win"]
const E1_POSES: Array[String] = ["idle", "draw", "idle", "hurt", "idle", "defeat"]
## Pinned: per shot in run 1, game frames after the draw frame: [unit, arrow, impact, idle, arrow_end].
## arrow_end = the first frame with _arrows empty again. Nominal 12 / 33 / 48 (CHANGE-BRIEF §4); the
## cue list fires each cue on the first frame its time is reached on the summed 1/60 s clock, so the
## impact and idle cues land one frame early or late (measured; the brief's revision records it).
const SHOTS: Array = [
	["e1", 12, 32, 47, 32],
	["p1", 12, 34, 49, 32],
	["p1", 12, 32, 47, 32],
]
## Pinned: turn 4's two shots start this many frames apart (nominal 63 = 1.05 s).
const TURN4_GAP: int = 62
## Frames to wait on WON before Enter is accepted (CARD_LOCK 0.5 s, main.gd:37, :283).
const CARD_WAIT: int = 45


## Records one row per frame, after every other _process() of that frame.
class Sampler extends Node:
	var row_fn: Callable
	var rows: Array[Dictionary] = []

	func _process(delta: float) -> void:
		if row_fn.is_valid():
			rows.append(row_fn.call(delta))


var rep: Report
var main: Variant
var sampler: Sampler
var phase: String = "load"


func _initialize() -> void:
	_run()


# ---------------------------------------------------------------- helpers

## One key press and release through Input.parse_input_event, then two frames so main has read it.
func _key(code: int) -> void:
	for pressed: bool in [true, false]:
		var ev: InputEventKey = InputEventKey.new()
		ev.keycode = code as Key
		ev.physical_keycode = code as Key
		ev.pressed = pressed
		Input.parse_input_event(ev)
	await _frames(2)


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


func _pose(id: String) -> String:
	var p: Variant = main.pieces.get(id)
	return String(p.state) if p != null else ""


func _damaged_played() -> int:
	var n: int = 0
	for ev: Dictionary in main.played_events:
		if ev["type"] == "damaged":
			n += 1
	return n


func _row(delta: float) -> Dictionary:
	var p1: Variant = main.pieces.get("p1")
	var e1: Variant = main.pieces.get("e1")
	return {"i": sampler.rows.size(), "phase": phase, "state": _s(), "p1": _pose("p1"), "e1": _pose("e1"),
		"p1_id": p1.get_instance_id() if p1 != null else 0, "e1_id": e1.get_instance_id() if e1 != null else 0,
		"arrows": main._arrows.size(), "ignored": int(main.ignored_inputs), "paused": bool(main.paused),
		"turn": int(main.rules.turn), "damaged": _damaged_played(), "delta": delta}


static func _collapse(seq: Array) -> Array:
	var out: Array = []
	for v: Variant in seq:
		if out.is_empty() or out[-1] != v:
			out.append(v)
	return out


func _rows_of(ph: String) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for r: Dictionary in sampler.rows:
		if r["phase"] == ph:
			out.append(r)
	return out


## Every shot in `rows`: the row index where a unit enters "draw", then the first later rows where an
## arrow appears, a damaged event is played, the unit leaves "draw", and _arrows is empty again.
## Paused rows are skipped, so the offsets count game frames.
static func _shots(rows: Array[Dictionary]) -> Array:
	var out: Array = []
	for i: int in range(1, rows.size()):
		for id: String in ["e1", "p1"]:
			if rows[i][id] == "draw" and rows[i - 1][id] != "draw":
				out.append(_measure(rows, i, id))
	out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["start"] < b["start"])
	return out


static func _measure(rows: Array[Dictionary], start: int, id: String) -> Dictionary:
	var m: Dictionary = {"unit": id, "start": start, "arrow": -1, "impact": -1, "idle": -1, "arrow_end": -1,
		"paused_frames": 0}
	var game: int = 0
	for j: int in range(start + 1, rows.size()):
		if rows[j]["paused"]:
			m["paused_frames"] += 1
			continue
		game += 1
		if m["arrow"] < 0 and rows[j]["arrows"] > rows[j - 1]["arrows"]:
			m["arrow"] = game
		if m["arrow"] >= 0 and m["arrow_end"] < 0 and rows[j]["arrows"] == 0:
			m["arrow_end"] = game
		if m["impact"] < 0 and rows[j]["damaged"] > rows[j - 1]["damaged"]:
			m["impact"] = game
		if rows[j][id] != "draw":
			m["idle"] = game
			m["left_to"] = rows[j][id]
			break
	return m


func _route_turn(step: Dictionary, label: String) -> bool:
	if not await _wait(func() -> bool: return _s() == "PLAN_MOVE"):
		rep.check("%s: reached PLAN_MOVE" % label, false, _s())
		return false
	var turn_no: int = main.rules.turn
	var mv: Vector2i = Runner.move_of(step)
	if mv == Vector2i.ZERO:
		await _key(KEY_SPACE)
	else:
		if mv.x == 1:
			await _key(KEY_RIGHT)
		elif mv.x == -1:
			await _key(KEY_LEFT)
		if mv.y == -1:
			await _key(KEY_UP)
		elif mv.y == 1:
			await _key(KEY_DOWN)
		await _key(KEY_ENTER)
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
			await _key(KEY_SPACE)
		else:
			var n: int = 0
			while main.selected_target() != t and n < 30:
				await _key(KEY_RIGHT)
				n += 1
			if main.selected_target() != t:
				rep.check("%s: target %s selectable" % [label, t], false, main.targets)
				return false
			await _key(KEY_ENTER)
	elif t != null:
		rep.check("%s: the route's target %s could be ordered" % [label, t], false, _s())
		return false
	return true


func _turn_done(turn_no: int) -> bool:
	var s: String = _s()
	return s == "WON" or s == "LOST" or (s == "PLAN_MOVE" and main.rules.turn > turn_no)


func _play_turn(step: Dictionary, label: String) -> bool:
	var turn_no: int = main.rules.turn
	if not await _route_turn(step, label):
		return false
	if not await _wait(_turn_done.bind(turn_no)):
		rep.check("%s: attack playback finished" % label, false, _s())
		return false
	return true


# ---------------------------------------------------------------- run

func _run() -> void:
	rep = Report.new("test_pins_a7")
	await process_frame
	main = MainScene.instantiate()
	root.add_child(main)
	sampler = Sampler.new()
	sampler.name = "Sampler"
	sampler.process_priority = 1000
	root.add_child(sampler)
	sampler.row_fn = _row

	var win: Dictionary = Runner.load_route("res://tests/fixtures/win_route.json")
	var turns: Array = win["turns"]

	# ---------------------------------------------------- run 1: title -> win route -> WON
	phase = "win"
	await _frames(10)
	await _key(KEY_ENTER)
	rep.check("Enter on the title (parse_input_event) starts turn 1 in PLAN_MOVE", _s() == "PLAN_MOVE"
		and main.rules.turn == 1, "%s, turn %d" % [_s(), main.rules.turn])
	for i: int in turns.size():
		if not await _play_turn(turns[i], "win turn %d" % (i + 1)):
			quit(rep.finish())
			return
	await _frames(10)
	rep.check("run 1 ends in WON (elimination)", _s() == "WON" and String(main.last_result.get("kind", "")) == "elimination",
		"%s %s" % [_s(), main.last_result])

	var r1: Array[Dictionary] = _rows_of("win")
	var odd: Array = r1.filter(func(r: Dictionary) -> bool: return not is_equal_approx(float(r["delta"]), 1.0 / 60.0))
	rep.check("fixed frame rate: every sampled delta is 1/60 s (%d frames; run at 60)" % r1.size(), odd.is_empty(),
		"%d other deltas" % odd.size())
	var states: Array = _collapse(r1.map(func(r: Dictionary) -> String: return r["state"]))
	rep.check("pin: main.state order, title to WON (%d states)" % STATE_ORDER.size(), states == Array(STATE_ORDER), states)
	var p1p: Array = _collapse(r1.map(func(r: Dictionary) -> String: return r["p1"]))
	var e1p: Array = _collapse(r1.map(func(r: Dictionary) -> String: return r["e1"]))
	rep.check("pin: p1 pose order", p1p == Array(P1_POSES), p1p)
	rep.check("pin: e1 pose order", e1p == Array(E1_POSES), e1p)

	var shots: Array = _shots(r1)
	rep.check("pin: run 1 has %d shots, in order %s" % [SHOTS.size(), SHOTS.map(func(s: Array) -> String: return s[0])],
		shots.size() == SHOTS.size() and shots.map(func(s: Dictionary) -> String: return s["unit"]) == SHOTS.map(func(s: Array) -> String: return s[0]),
		shots)
	for k: int in mini(shots.size(), SHOTS.size()):
		var s: Dictionary = shots[k]
		var e: Array = SHOTS[k]
		var label: String = "shot %d (%s, draw on row %d)" % [k + 1, s["unit"], s["start"]]
		rep.check("pin: %s: arrow appears %d frames after the draw (startup)" % [label, e[1]], s["arrow"] == e[1], s["arrow"])
		rep.check("pin: %s: impact %d frames after the draw (startup + active)" % [label, e[2]], s["impact"] == e[2], s["impact"])
		rep.check("pin: %s: back to idle %d frames after the draw (startup + active + recovery)" % [label, e[3]],
			s["idle"] == e[3] and s.get("left_to", "") == "idle", "%d -> %s" % [s["idle"], s.get("left_to", "")])
		rep.check("pin: %s: _arrows empty again %d frames after the draw (0-2 frames before the impact)" % [label, e[4]],
			s["arrow_end"] == e[4] and s["impact"] - s["arrow_end"] >= 0 and s["impact"] - s["arrow_end"] <= 2, s["arrow_end"])
	if shots.size() >= 2:
		rep.check("pin: turn 4's two shots start %d frames apart (nominal 63 = 1.05 s)" % TURN4_GAP,
			shots[1]["start"] - shots[0]["start"] == TURN4_GAP, shots[1]["start"] - shots[0]["start"])
	var ign1: int = r1[-1]["ignored"]
	rep.check("pin: run 1 ignored no input (every key was legal where it was pressed)", ign1 == 0, ign1)

	# ---------------------------------------------------- run 2: interrupts during turn 4's shots
	phase = "interrupts"
	await _frames(CARD_WAIT)
	await _key(KEY_ENTER) # results card
	await _key(KEY_ENTER) # play again -> turn 1
	rep.check("Enter, Enter on WON: play again, turn 1 in PLAN_MOVE", _s() == "PLAN_MOVE" and main.rules.turn == 1,
		"%s, turn %d" % [_s(), main.rules.turn])
	for i: int in 3:
		if not await _play_turn(turns[i], "interrupts turn %d" % (i + 1)):
			quit(rep.finish())
			return
	if not await _route_turn(turns[3], "interrupts turn 4"):
		quit(rep.finish())
		return
	# First shot (e1): Enter during startup, then P for PAUSE_FRAMES during the active phase.
	if not await _wait(func() -> bool: return _pose("e1") == "draw"):
		rep.check("turn 4: e1 draws", false, _pose("e1"))
		quit(rep.finish())
		return
	var ign0: int = main.ignored_inputs
	await _key(KEY_ENTER)
	rep.check("pin: Enter during the startup is ignored (ignored_inputs + 1, still PLAY_ATTACKS, e1 still draw)",
		main.ignored_inputs == ign0 + 1 and _s() == "PLAY_ATTACKS" and _pose("e1") == "draw",
		"%d -> %d, %s, %s" % [ign0, main.ignored_inputs, _s(), _pose("e1")])
	await _wait(func() -> bool: return main._arrows.size() > 0)
	await _frames(5)
	var clock0: float = main._clock
	var arrow_t0: float = float(main._arrows[0]["t"]) if main._arrows.size() > 0 else -1.0
	await _key(KEY_P)
	var paused_from: float = main._clock
	await _frames(PAUSE_FRAMES)
	rep.check("pin: P in the active phase pauses: game clock, arrow t and e1's pose hold for %d frames" % PAUSE_FRAMES,
		main.paused and is_equal_approx(main._clock, paused_from) and _pose("e1") == "draw" and main._arrows.size() == 1,
		"paused %s, clock %.4f -> %.4f, pose %s, arrows %d" % [main.paused, paused_from, main._clock, _pose("e1"), main._arrows.size()])
	await _key(KEY_P)
	rep.check("pin: P again resumes (paused false, clock moves)", not main.paused and main._clock > paused_from,
		"clock %.4f -> %.4f (arrow t was %.4f at %.4f)" % [paused_from, main._clock, arrow_t0, clock0])
	# Second shot (p1): R during its active phase.
	if not await _wait(func() -> bool: return _pose("p1") == "draw"):
		rep.check("turn 4: p1 draws", false, _pose("p1"))
		quit(rep.finish())
		return
	await _wait(func() -> bool: return main._arrows.size() > 0)
	await _frames(5)
	var old_p1: int = main.pieces["p1"].get_instance_id()
	var retries0: int = main.retries
	await _key(KEY_R)
	rep.check("pin: R in the active phase restarts: turn 1, PLAN_MOVE, _arrows empty, retries + 1",
		_s() == "PLAN_MOVE" and main.rules.turn == 1 and main._arrows.is_empty() and main.retries == retries0 + 1,
		"%s, turn %d, arrows %d, retries %d" % [_s(), main.rules.turn, main._arrows.size(), main.retries])
	rep.check("pin: R rebuilt the archers (new p1 instance, pose recover or idle, not draw)",
		main.pieces["p1"].get_instance_id() != old_p1 and _pose("p1") in ["recover", "idle"],
		"pose %s" % _pose("p1"))
	await _frames(90)
	rep.check("pin: after R no cue from the old turn fires (no draw, no arrow, no damage for 90 frames)",
		_pose("p1") == "idle" and _pose("e1") == "idle" and main._arrows.is_empty() and _damaged_played() == 0,
		"%s %s arrows %d damaged %d" % [_pose("p1"), _pose("e1"), main._arrows.size(), _damaged_played()])

	var r2: Array[Dictionary] = _rows_of("interrupts")
	var s2: Array = _shots(r2)
	if s2.size() >= 1:
		var a: Dictionary = s2[0]
		var e: Array = SHOTS[0]
		rep.check("pin: the paused shot keeps run 1's timing, %d / %d / %d game frames (%d paused frames not counted)"
			% [e[1], e[2], e[3], a["paused_frames"]],
			a["unit"] == e[0] and a["arrow"] == e[1] and a["impact"] == e[2] and a["idle"] == e[3]
			and a["paused_frames"] >= PAUSE_FRAMES, a)
	else:
		rep.check("pin: run 2 recorded the paused shot", false, s2)

	print("MEASURED run 1 shots: %s" % [shots])
	print("MEASURED run 2 shots: %s" % [s2])
	quit(rep.finish({"shots_run1": shots, "shots_run2": s2, "state_order": states, "p1_poses": p1p, "e1_poses": e1p}))
