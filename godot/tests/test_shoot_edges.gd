extends SceneTree
## A7 Step 6 edge tests (CHANGE-BRIEF §8 "edge tests"): the committing action `shoot` at every phase
## boundary of the table (§4: frames 0, 12, 33, 48 at 60 fps), with each of the brief's three
## interrupts arriving one frame before the boundary, on it, and one frame after.
## ./scripts/run-test.sh test_shoot_edges.gd 60
##
## The shot under test is e1's, the first shot of turn 4 on the win route (tests/fixtures/win_route.json).
## Its pinned timing (test_pins_a7.gd, shot 1): arrow 12, impact 32, idle 47 game frames after the
## draw frame. Every case restarts with R, replays turns 1-3, gives turn 4's orders, and sends the
## interrupt key through Input.parse_input_event so that it ARRIVES (is handled by main) on the target
## frame. A calibration run measures the key's arrival lag and the draw frame, and every case asserts
## that its key really arrived on its target frame before asserting what the interrupt did.
##
## What each interrupt must do (CHANGE-BRIEF §5, §8):
## - P: paused from the arrival frame; while paused, e1's pose, its clip position and the game clock
##   do not move; after P again, the shot keeps its timing in game frames (12 / 32 / 47) and its clip
##   steps 1/60 per game frame.
## - R: on the arrival frame, turn 1 in PLAN_MOVE and retries + 1; a shooting e1 is freed with its rig;
##   the new e1 shows no clip; no draw, arrow or damage follows from the old turn.
## - Enter: ignored (ignored_inputs + 1 on the arrival frame, the pose unchanged by it); the shot keeps
##   its timing and its clip steps 1/60 per game frame.
##
## Written by Claude Code (main session). It only reads the game; it never calls set_state(), play(),
## stop() or advance().

const Report = preload("res://tests/test_report.gd")
const Runner = preload("res://tests/route_runner.gd")
const MainScene = preload("res://game/main.tscn")

const MAX_FRAMES: int = 20000
const BOUNDARIES: Array[int] = [0, 12, 33, 48] ## phase-table frames (CHANGE-BRIEF §4)
const OFFSETS: Array[int] = [-1, 0, 1]
const INTERRUPTS: Array[String] = ["P", "R", "Enter"]
const SHOT1: Array[int] = [12, 32, 47] ## pinned e1 turn-4 shot: arrow, impact, idle (test_pins_a7.gd)
const PAUSE_FRAMES: int = 10
const AFTER_R_FRAMES: int = 60
const STEP: float = 1.0 / 60.0
const TOL: float = 0.5 / 60.0


class Sampler extends Node:
	var row_fn: Callable
	var rows: Array[Dictionary] = []

	func _process(_delta: float) -> void:
		if row_fn.is_valid():
			rows.append(row_fn.call())


var rep: Report
var main: Variant
var sampler: Sampler
var turns: Array = []


func _initialize() -> void:
	_run()


# ---------------------------------------------------------------- helpers

func _send(code: int) -> void:
	for pressed: bool in [true, false]:
		var ev: InputEventKey = InputEventKey.new()
		ev.keycode = code as Key
		ev.physical_keycode = code as Key
		ev.pressed = pressed
		Input.parse_input_event(ev)


func _key(code: int) -> void:
	_send(code)
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


func _row() -> Dictionary:
	var e1: Variant = main.pieces.get("e1")
	var r: Dictionary = {"i": sampler.rows.size(), "state": _s(), "paused": bool(main.paused),
		"ignored": int(main.ignored_inputs), "retries": int(main.retries), "turn": int(main.rules.turn),
		"arrows": main._arrows.size(), "clock": float(main._clock), "damaged": 0,
		"e1_id": 0, "e1_pose": "", "e1_cur": "", "e1_playing": false, "e1_pos": -1.0, "e1_mount": false}
	for ev: Dictionary in main.played_events:
		if ev["type"] == "damaged":
			r["damaged"] += 1
	if e1 != null:
		var a: AnimationPlayer = e1._rig_anim
		r["e1_id"] = e1.get_instance_id()
		r["e1_pose"] = String(e1.state)
		r["e1_cur"] = String(a.current_animation)
		r["e1_playing"] = a.is_playing()
		r["e1_pos"] = a.current_animation_position if a.is_playing() else -1.0
		r["e1_mount"] = (e1._rig_mount as Node2D).visible
	return r


func _route_moves_and_orders(step: Dictionary, label: String, send_last: bool) -> bool:
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
			if send_last:
				await _key(KEY_ENTER)
	elif t != null:
		rep.check("%s: the route's target %s could be ordered" % [label, t], false, _s())
		return false
	return true


func _turn_done(turn_no: int) -> bool:
	var s: String = _s()
	return s == "WON" or s == "LOST" or (s == "PLAN_MOVE" and main.rules.turn > turn_no)


## R (from anywhere), then turns 1-3, then turn 4's move and target, with the attack Enter NOT sent.
func _to_turn4_target(label: String) -> bool:
	if main.paused:
		await _key(KEY_P)
	await _key(KEY_R)
	for i: int in 3:
		var turn_no: int = main.rules.turn
		if not await _route_moves_and_orders(turns[i], "%s turn %d" % [label, i + 1], true):
			return false
		if not await _wait(_turn_done.bind(turn_no)):
			rep.check("%s turn %d: playback finished" % [label, i + 1], false, _s())
			return false
	return await _route_moves_and_orders(turns[3], "%s turn 4" % label, false)


## Sends the attack Enter on the current frame and returns its row index.
func _confirm_attack() -> int:
	var row: int = sampler.rows.size()
	_send(KEY_ENTER)
	return row


func _wait_row(row: int) -> void:
	while sampler.rows.size() < row:
		await process_frame


static func _first(rows: Array, from: int, cond: Callable) -> int:
	for j: int in range(maxi(from, 0), rows.size()):
		if cond.call(rows[j]):
			return j
	return -1


## e1's shot from its draw row: arrow, impact and idle as unpaused game frames after the draw row, and
## whether the clip stepped 1/60 on every unpaused frame and held on every paused one.
static func _shot(rows: Array, draw_row: int) -> Dictionary:
	var m: Dictionary = {"arrow": -1, "impact": -1, "idle": -1, "step_bad": [], "hold_bad": []}
	var game: int = 0
	for j: int in range(draw_row + 1, rows.size()):
		var r: Dictionary = rows[j]
		var p: Dictionary = rows[j - 1]
		if r["paused"]:
			if r["e1_playing"] and p["e1_playing"] and absf(float(r["e1_pos"]) - float(p["e1_pos"])) > 1e-6:
				m["hold_bad"].append(j)
			continue
		game += 1
		if m["arrow"] < 0 and r["arrows"] > p["arrows"]:
			m["arrow"] = game
		if m["impact"] < 0 and r["damaged"] > p["damaged"]:
			m["impact"] = game
		if r["e1_playing"] and p["e1_playing"] and absf(float(r["e1_pos"]) - float(p["e1_pos"]) - STEP) > TOL:
			m["step_bad"].append(j)
		if r["e1_pose"] != "draw":
			m["idle"] = game
			break
	return m


# ---------------------------------------------------------------- run

func _run() -> void:
	rep = Report.new("test_shoot_edges")
	await process_frame
	main = MainScene.instantiate()
	root.add_child(main)
	sampler = Sampler.new()
	sampler.name = "Sampler"
	sampler.process_priority = 1000
	root.add_child(sampler)
	sampler.row_fn = _row
	turns = Runner.load_route("res://tests/fixtures/win_route.json")["turns"]

	await _frames(5)
	await _key(KEY_ENTER) # title -> turn 1

	# ---------------------------------------------------- calibration
	if not await _to_turn4_target("calibration"):
		quit(rep.finish())
		return
	var sent: int = _confirm_attack()
	await _wait(func() -> bool: return main.pieces["e1"].state == "draw")
	await process_frame
	var rows: Array = sampler.rows
	var draw_row: int = _first(rows, sent, func(r: Dictionary) -> bool: return r["e1_pose"] == "draw")
	var lead: int = draw_row - sent ## rows from sending the attack Enter to e1's draw frame
	# Arrival lag: an Enter in the startup is ignored on the row it is handled.
	var ign0: int = main.ignored_inputs
	var sent_e: int = sampler.rows.size()
	_send(KEY_ENTER)
	await _frames(3)
	var arrive: int = _first(sampler.rows, sent_e, func(r: Dictionary) -> bool: return r["ignored"] > ign0)
	var lag: int = arrive - sent_e
	rep.check("calibration: e1 draws %d rows after the attack Enter is sent; a key sent on row n is handled on row n + %d"
		% [lead, lag], draw_row > sent and lag >= 0 and lag <= 1, "draw row %d, sent %d, arrive %d" % [draw_row, sent, arrive])
	await _wait(func() -> bool: return main.pieces["e1"].state != "draw")
	await process_frame
	var cal: Dictionary = _shot(sampler.rows, draw_row)
	rep.check("calibration: e1's shot keeps the pinned timing %s" % [SHOT1],
		[cal["arrow"], cal["impact"], cal["idle"]] == Array(SHOT1), cal)

	# ---------------------------------------------------- the 36 cases
	var summary: Array = []
	for b: int in BOUNDARIES:
		for off: int in OFFSETS:
			for which: String in INTERRUPTS:
				var label: String = "%s at frame %d%+d (= %d)" % [which, b, off, b + off]
				if not await _to_turn4_target(label):
					quit(rep.finish({"cases": summary}))
					return
				var code: int = KEY_P if which == "P" else (KEY_R if which == "R" else KEY_ENTER)
				var case: Dictionary
				if b + off < 0:
					# The draw starts on the frame the attack Enter is handled (calibration: lead = lag), so
					# the frame before it is still PLAN_ATTACK: the interrupt goes in one frame before the
					# attack Enter and is handled one frame before the draw would have been.
					var x: int = sampler.rows.size()
					_send(code)
					await _wait_row(x + 1)
					_confirm_attack()
					await _wait_row(x + 3)
					case = await _check_before_draw(which, label, x + lag)
				else:
					var s0: int = _confirm_attack()
					var target: int = s0 + lead + b + off ## row on which the interrupt must be handled
					await _wait_row(target - lag)
					_send(code)
					await _wait_row(target + 1)
					case = await _check_case(which, label, s0 + lead, target)
				summary.append(case)
	quit(rep.finish({"lead": lead, "lag": lag, "calibration": cal, "cases": summary}))


func _check_case(which: String, label: String, draw_row: int, target: int) -> Dictionary:
	var rows: Array = sampler.rows
	var at: Dictionary = rows[target]
	var before: Dictionary = rows[target - 1]
	var out: Dictionary = {"case": label}
	match which:
		"P":
			var arrived: bool = at["paused"] and not before["paused"]
			rep.check("%s: P handled on its target frame (paused from it)" % label, arrived,
				"row %d paused %s, row before %s" % [target, at["paused"], before["paused"]])
			await _frames(PAUSE_FRAMES)
			var r2: Array = sampler.rows
			var held: bool = true
			for j: int in range(target, target + PAUSE_FRAMES):
				var r: Dictionary = r2[j]
				held = held and r["paused"] and r["e1_pose"] == at["e1_pose"] and is_equal_approx(r["clock"], at["clock"]) \
					and is_equal_approx(r["e1_pos"], at["e1_pos"])
			rep.check("%s: while paused, e1's pose (%s), its clip position and the game clock hold for %d frames"
				% [label, at["e1_pose"], PAUSE_FRAMES], held)
			await _key(KEY_P)
			var turn_no: int = main.rules.turn
			await _wait(_turn_done.bind(turn_no))
			var m: Dictionary = _shot(sampler.rows, _first(sampler.rows, draw_row - 1,
				func(r: Dictionary) -> bool: return r["e1_pose"] == "draw"))
			rep.check("%s: after P again the shot keeps its timing %s in game frames, the clip steps 1/60 per game frame and holds while paused"
				% [label, SHOT1], [m["arrow"], m["impact"], m["idle"]] == Array(SHOT1) and m["step_bad"].is_empty()
				and m["hold_bad"].is_empty(), m)
			out["shot"] = m
		"R":
			var arrived: bool = at["turn"] == 1 and at["state"] == "PLAN_MOVE" and at["retries"] == before["retries"] + 1
			rep.check("%s: R handled on its target frame (turn 1, PLAN_MOVE, retries + 1)" % label, arrived,
				"row %d: %s turn %d retries %d" % [target, at["state"], at["turn"], at["retries"]])
			var freed: bool = at["e1_id"] != before["e1_id"]
			rep.check("%s: R replaced e1 (was %s, clip '%s'); the new e1 shows no clip" % [label, before["e1_pose"], before["e1_cur"]],
				freed and not at["e1_mount"] and at["e1_cur"] == "" and not at["e1_playing"], at)
			await _frames(AFTER_R_FRAMES)
			var r2: Array = sampler.rows
			var quiet: bool = true
			for j: int in range(target, target + AFTER_R_FRAMES):
				var r: Dictionary = r2[j]
				quiet = quiet and r["e1_pose"] != "draw" and r["arrows"] == 0 and r["damaged"] == 0 and r["e1_cur"] == ""
			rep.check("%s: after R nothing from the old turn follows (no draw, arrow, damage or clip for %d frames)"
				% [label, AFTER_R_FRAMES], quiet)
		"Enter":
			var arrived: bool = at["ignored"] == before["ignored"] + 1
			rep.check("%s: Enter handled on its target frame and ignored (ignored_inputs + 1, in %s)" % [label, at["state"]],
				arrived and at["state"] == "PLAY_ATTACKS", "row %d ignored %d -> %d" % [target, before["ignored"], at["ignored"]])
			var turn_no: int = main.rules.turn
			await _wait(_turn_done.bind(turn_no))
			var m: Dictionary = _shot(sampler.rows, _first(sampler.rows, draw_row - 1,
				func(r: Dictionary) -> bool: return r["e1_pose"] == "draw"))
			rep.check("%s: the shot keeps its timing %s and the clip steps 1/60 per game frame" % [label, SHOT1],
				[m["arrow"], m["impact"], m["idle"]] == Array(SHOT1) and m["step_bad"].is_empty(), m)
			out["shot"] = m
	return out


## One frame before the draw: the game is still in PLAN_ATTACK, waiting for the attack Enter, which
## arrives on the next frame (target + 1). What the game does there (main.gd:251-281):
## - P pauses PLAN_ATTACK; the attack Enter that follows is ignored while paused, so no shot starts
##   until P again and a new Enter; then the shot keeps its timing.
## - R restarts (turn 1, PLAN_MOVE); the Enter that follows confirms turn 1's move, so no shot follows.
## - Enter is itself the attack order: the shot starts on this frame, and the second Enter is ignored.
func _check_before_draw(which: String, label: String, target: int) -> Dictionary:
	var rows: Array = sampler.rows
	var at: Dictionary = rows[target]
	var before: Dictionary = rows[target - 1]
	var nxt: Dictionary = rows[target + 1]
	var out: Dictionary = {"case": label}
	rep.check("%s: the frame before the draw is PLAN_ATTACK (the attack is not yet ordered)" % label,
		before["state"] == "PLAN_ATTACK" and before["e1_pose"] != "draw", before["state"])
	match which:
		"P":
			rep.check("%s: P handled on its target frame: PLAN_ATTACK paused" % label,
				at["paused"] and not before["paused"] and at["state"] == "PLAN_ATTACK", at)
			rep.check("%s: the attack Enter on the next frame is ignored while paused (ignored_inputs + 1, no draw)" % label,
				nxt["ignored"] == at["ignored"] + 1 and nxt["state"] == "PLAN_ATTACK" and nxt["e1_pose"] != "draw", nxt)
			await _frames(PAUSE_FRAMES)
			var still: bool = true
			for j: int in range(target, target + PAUSE_FRAMES):
				still = still and sampler.rows[j]["paused"] and sampler.rows[j]["e1_pose"] != "draw"
			rep.check("%s: no shot starts while paused (%d frames)" % [label, PAUSE_FRAMES], still)
			await _key(KEY_P)
			var row: int = sampler.rows.size()
			_send(KEY_ENTER)
			var turn_no: int = main.rules.turn
			await _wait(_turn_done.bind(turn_no))
			var d: int = _first(sampler.rows, row, func(r: Dictionary) -> bool: return r["e1_pose"] == "draw")
			var m: Dictionary = _shot(sampler.rows, d)
			rep.check("%s: after P and a new Enter the shot keeps its timing %s" % [label, SHOT1],
				d > 0 and [m["arrow"], m["impact"], m["idle"]] == Array(SHOT1) and m["step_bad"].is_empty(), m)
			out["shot"] = m
		"R":
			rep.check("%s: R handled on its target frame (turn 1, PLAN_MOVE, retries + 1); e1 replaced, no clip" % label,
				at["turn"] == 1 and at["state"] == "PLAN_MOVE" and at["retries"] == before["retries"] + 1
				and at["e1_id"] != before["e1_id"] and at["e1_cur"] == "" and not at["e1_mount"], at)
			await _frames(AFTER_R_FRAMES)
			var quiet: bool = true
			for j: int in range(target, target + AFTER_R_FRAMES):
				var r: Dictionary = sampler.rows[j]
				quiet = quiet and r["e1_pose"] != "draw" and r["arrows"] == 0 and r["damaged"] == 0 and r["e1_cur"] == ""
			rep.check("%s: the following Enter is a turn-1 order, and no draw, arrow, damage or clip follows (%d frames)"
				% [label, AFTER_R_FRAMES], quiet and nxt["turn"] == 1)
		"Enter":
			rep.check("%s: Enter handled on its target frame is the attack order: PLAY_ATTACKS and e1 draws on it" % label,
				at["state"] == "PLAY_ATTACKS" and at["e1_pose"] == "draw" and at["e1_cur"] == "shoot", at)
			rep.check("%s: the second Enter, on the next frame, is ignored (ignored_inputs + 1)" % label,
				nxt["ignored"] == at["ignored"] + 1, "%d -> %d" % [at["ignored"], nxt["ignored"]])
			var turn_no: int = main.rules.turn
			await _wait(_turn_done.bind(turn_no))
			var m: Dictionary = _shot(sampler.rows, target)
			rep.check("%s: the shot keeps its timing %s and the clip steps 1/60 per game frame" % [label, SHOT1],
				[m["arrow"], m["impact"], m["idle"]] == Array(SHOT1) and m["step_bad"].is_empty(), m)
			out["shot"] = m
	return out
