extends SceneTree
## A7 structure test (CHANGE-BRIEF §5, §6, §8 "structure test"): the pose -> clip table against the
## AnimationPlayers, driven through the real game loop and real keys.
## ./scripts/run-test.sh test_anim_states.gd 60
##
## Keys go through Input.parse_input_event; such an event reaches main._unhandled_input one frame
## later (CLAUDE.md "Headless facts"), so every key is followed by frame waits. A Sampler node with
## process_priority 1000 records one row per frame, after main (0) and the A6 drivers (10), so a row
## shows what that frame draws. The clip is read with current_animation (the AnimationPlayer route).
## The test only reads: it never calls set_state(), play(), stop() or advance(), and builds no clip.
##
## Run 1 ("win"): title -> win route (tests/fixtures/win_route.json) -> WON: every pose the game shows.
## Run 2 ("interrupts"): play again, turns 1-3, then turn 4 with Enter during the first shot's
##   startup, P held for 30 frames during its active phase, and R during the second shot's active phase.
## No AnimationTree is used (CHANGE-BRIEF §5), so there is no advance_expression_base_node or
## advance_mode to check; check 2 asserts that no AnimationTree exists.

const Report = preload("res://tests/test_report.gd")
const Runner = preload("res://tests/route_runner.gd")
const PieceScript = preload("res://game/piece.gd")
const MainScene = preload("res://game/main.tscn")

const MAX_FRAMES: int = 20000
const PAUSE_FRAMES: int = 30
const CARD_WAIT: int = 45
const FRAME: float = 1.0 / 60.0
const HALF: float = 0.5 / 60.0
const ANG_TOL: float = 0.01 ## rad: frame 0 + one frame of an ease-in segment moves the bow < 0.002
## shoot.tres key values (read back by test_shoot_readback.gd; repeated here only to recognise poses).
const BOW_FRAME0: float = 0.20944
const BOW_END: float = 0.139626 # 8°, the bow's frame-48 key since tuning r1 (brief revision 4)
const DRAW_LEAD: float = 0.2 ## main.gd:29
## The keyed nodes: no game, preview or debug script may name them (one authority).
const KEYED_PATHS: Array[String] = ["\"Rig\"", "\"Rig/Upper\"", "\"Rig/Upper/Bow\"", "\"FlagSprite\""]
const SCAN_DIRS: Array[String] = ["res://game", "res://previews", "res://debug"]


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
var flag_anim: AnimationPlayer


func _initialize() -> void:
	_run()


# ---------------------------------------------------------------- helpers (as in test_pins_a7.gd)

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


# ---------------------------------------------------------------- sampling

func _piece_row(p: Variant) -> Dictionary:
	if p == null:
		return {}
	var a: AnimationPlayer = p._rig_anim
	var mount: Node2D = p._rig_mount
	var playing: bool = a.is_playing()
	return {"id": p.get_instance_id(), "pose": String(p.state), "src": String(p.texture_source),
		"mount": mount.visible, "sprite": (p._sprite as Sprite2D).visible,
		"cur": String(a.current_animation), "asg": String(a.assigned_animation), "playing": playing,
		"pos": a.current_animation_position if playing else -1.0,
		"rig": (mount.get_node("Rig") as Node2D).position,
		"upper": (mount.get_node("Rig/Upper") as Node2D).rotation,
		"bow": (mount.get_node("Rig/Upper/Bow") as Node2D).rotation,
		"facing": int(p.facing), "mscale_x": mount.scale.x}


func _row(delta: float) -> Dictionary:
	var arrow_t: float = float(main._arrows[0]["t"]) if main._arrows.size() > 0 else -1.0
	return {"i": sampler.rows.size(), "phase": phase, "state": _s(), "paused": bool(main.paused),
		"ignored": int(main.ignored_inputs), "arrows": main._arrows.size(), "arrow_t": arrow_t,
		"flag_cur": String(flag_anim.current_animation), "flag_playing": flag_anim.is_playing(),
		"flag_pos": flag_anim.current_animation_position if flag_anim.is_playing() else -1.0,
		"p1": _piece_row(main.pieces.get("p1")), "e1": _piece_row(main.pieces.get("e1")), "delta": delta}


func _rows_of(ph: String) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for r: Dictionary in sampler.rows:
		if r["phase"] == ph:
			out.append(r)
	return out


## A row where the piece is in draw, the clip has run to its end and stopped, and the end pose holds.
static func _is_end_hold(pr: Dictionary) -> bool:
	return pr["pose"] == "draw" and not pr["playing"] and pr["cur"] == "" and pr["asg"] == "shoot" \
		and absf(float(pr["bow"]) - BOW_END) < ANG_TOL and absf(float(pr["upper"])) < ANG_TOL \
		and (pr["rig"] as Vector2).length() < 0.01


## Every shot: the row where a piece instance enters draw, and its rows until it leaves draw.
static func _shots(rows: Array[Dictionary]) -> Array:
	var out: Array = []
	for i: int in range(1, rows.size()):
		for id: String in ["e1", "p1"]:
			var cur: Dictionary = rows[i][id]
			var prev: Dictionary = rows[i - 1][id]
			if cur.is_empty() or cur["pose"] != "draw":
				continue
			if prev.is_empty() or prev["id"] != cur["id"] or prev["pose"] != "draw":
				out.append(_measure(rows, i, id))
	out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["start"] < b["start"])
	return out


static func _measure(rows: Array[Dictionary], start: int, id: String) -> Dictionary:
	var first: Dictionary = rows[start][id]
	var m: Dictionary = {"unit": id, "start": start, "from": String(rows[start - 1][id].get("pose", "")),
		"pos0": float(first["pos"]), "cur0": first["cur"], "bow0": float(first["bow"]), "upper0": float(first["upper"]),
		"rig0": first["rig"], "arrow": -1, "lead": -1.0, "end": -1, "left_to": "", "end_hold": 0, "end_hold_ok": true,
		"step_bad": 0, "pause_bad": 0, "paused_frames": 0, "freed": false, "facing": int(first["facing"]),
		"mscale_x": float(first["mscale_x"])}
	var game: int = 0
	var last_pos: float = float(first["pos"])
	for j: int in range(start + 1, rows.size()):
		var pr: Dictionary = rows[j][id]
		if pr.is_empty() or pr["id"] != first["id"]:
			m["freed"] = true
			m["end"] = game + 1
			break
		if rows[j]["paused"]:
			m["paused_frames"] += 1
			if pr["playing"] and absf(float(pr["pos"]) - last_pos) > 1e-6:
				m["pause_bad"] += 1
			continue
		game += 1
		if pr["pose"] != "draw":
			m["end"] = game
			m["left_to"] = pr["pose"]
			m["leave_row"] = pr
			break
		if pr["playing"]:
			if absf(float(pr["pos"]) - last_pos - FRAME) > 1e-4:
				m["step_bad"] += 1
			last_pos = float(pr["pos"])
		elif _is_end_hold(pr):
			m["end_hold"] += 1
		else:
			m["end_hold_ok"] = false
		if m["arrow"] < 0 and rows[j]["arrows"] > rows[j - 1]["arrows"] and pr["playing"]:
			m["arrow"] = game
			m["lead"] = float(pr["pos"]) - float(rows[j]["arrow_t"])
	m["last_pos"] = last_pos
	return m


## Assertion 3 on every row: draw shows the rig playing shoot (or holding its end pose);
## every other pose shows the single sprite as before and no clip.
func _table_violations(rows: Array[Dictionary]) -> Array:
	var bad: Array = []
	for r: Dictionary in rows:
		for id: String in ["p1", "e1"]:
			var pr: Dictionary = r[id]
			if pr.is_empty():
				continue
			var want_clip: String = String(PieceScript.POSE_CLIPS.get(pr["pose"], "?"))
			var ok: bool
			if want_clip != "":
				ok = pr["mount"] and not pr["sprite"] and ((pr["cur"] == want_clip and pr["playing"]) or _is_end_hold(pr))
			else:
				ok = not pr["mount"] and not pr["playing"] and pr["cur"] == "" \
					and pr["sprite"] == (pr["src"] != "placeholder")
			if not ok and bad.size() < 5:
				bad.append({"row": r["i"], "id": id, "pose": pr["pose"], "cur": pr["cur"], "mount": pr["mount"],
					"sprite": pr["sprite"]})
	return bad


static func _walk(n: Node, out: Array[Node]) -> Array[Node]:
	out.append(n)
	for c: Node in n.get_children():
		_walk(c, out)
	return out


func _scan_sources() -> Dictionary:
	var hits: Dictionary = {"build": [], "player": [], "keyed": []}
	for dir: String in SCAN_DIRS:
		if not DirAccess.dir_exists_absolute(dir):
			continue
		for f: String in DirAccess.get_files_at(dir):
			if not f.ends_with(".gd"):
				continue
			var text: String = FileAccess.get_file_as_string(dir.path_join(f))
			for pat: String in ["Animation.new(", "add_track(", "track_insert_key("]:
				if text.contains(pat):
					hits["build"].append("%s: %s" % [f, pat])
			if (text.contains("AnimationPlayer") or text.contains("_rig_anim")) and f != "piece.gd":
				hits["player"].append(f)
			for pat: String in KEYED_PATHS:
				if text.contains(pat):
					hits["keyed"].append("%s: %s" % [f, pat])
	return hits


# ---------------------------------------------------------------- run

func _run() -> void:
	rep = Report.new("test_anim_states")
	await process_frame
	main = MainScene.instantiate()
	root.add_child(main)
	flag_anim = main.get_node("GoalFlag/AnimationPlayer") as AnimationPlayer
	sampler = Sampler.new()
	sampler.name = "Sampler"
	sampler.process_priority = 1000
	root.add_child(sampler)
	sampler.row_fn = _row

	# ---------------------------------------------------- 1. the table against the resources
	var table_keys: Array = PieceScript.POSE_CLIPS.keys()
	table_keys.sort()
	var states: Array = Array(PieceScript.STATES).duplicate() # a const array is read-only; sort a copy
	states.sort()
	rep.check("1 table: piece.POSE_CLIPS names exactly the poses in piece.STATES", table_keys == states,
		"%s vs %s" % [table_keys, states])
	var p1: Variant = main.pieces["p1"]
	var rig_anim: AnimationPlayer = p1._rig_anim
	var requested: Array = []
	for pose: String in PieceScript.POSE_CLIPS:
		var clip: String = PieceScript.POSE_CLIPS[pose]
		if clip != "" and not requested.has(clip):
			requested.append(clip)
	for clip: String in requested:
		rep.check("1 table: requested clip '%s' exists in the rig's AnimationPlayer" % clip, rig_anim.has_animation(clip),
			rig_anim.get_animation_list())
	rep.check("1 table: only draw requests a clip, and it is shoot", requested == ["shoot"]
		and PieceScript.POSE_CLIPS["draw"] == "shoot", requested)
	rep.check("1 flag: GoalFlag's AnimationPlayer has 'wave' and autoplays it",
		flag_anim.has_animation("wave") and String(flag_anim.autoplay) == "wave",
		"%s, autoplay '%s'" % [flag_anim.get_animation_list(), flag_anim.autoplay])

	# ---------------------------------------------------- 2. clocks and routes
	var rig_root: Node = rig_anim.get_node_or_null(rig_anim.root_node)
	rep.check("2 rig player: callback_mode_process MANUAL, root_node resolves to Mount, no autoplay",
		rig_anim.callback_mode_process == AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		and rig_root == p1._rig_mount and String(rig_anim.autoplay) == "",
		"mode %d, root %s, autoplay '%s'" % [rig_anim.callback_mode_process, rig_root, rig_anim.autoplay])
	rep.check("2 flag player: callback_mode_process IDLE",
		flag_anim.callback_mode_process == AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_IDLE,
		flag_anim.callback_mode_process)
	var gf: Node2D = main.get_node("GoalFlag") as Node2D
	rep.check("2 GoalFlag in main.tscn at (1176, 458), z_index 1 (above the board's table at z 0)",
		gf.position == Vector2(1176, 458) and gf.z_index == 1, "%s z %d" % [gf.position, gf.z_index])
	var banned: Array = []
	for n: Node in _walk(main, [] as Array[Node]):
		if n is AnimationTree or n is AnimatedSprite2D or n is Bone2D:
			banned.append("%s:%s" % [n.name, n.get_class()])
	rep.check("2 no AnimationTree, AnimatedSprite2D or Bone2D in the running game (so no advance_expression_base_node to set)",
		banned.is_empty(), banned)

	# ---------------------------------------------------- 8. material and placement
	var e1: Variant = main.pieces["e1"]
	var mat_ok: bool = true
	for p: Variant in [p1, e1]:
		for path: String in PieceScript.RIG_PARTS:
			if (p._rig_mount.get_node(path) as Sprite2D).material != p.tint_material():
				mat_ok = false
	rep.check("8 every rig part uses its own piece's tint_material() (A5 tint carried, ExposedDriver stays the one writer)",
		mat_ok and p1.tint_material() != e1.tint_material(), "p1 %s, e1 %s" % [p1.tint_material(), e1.tint_material()])

	# ---------------------------------------------------- 9. sources
	var hits: Dictionary = _scan_sources()
	rep.check("9 no game/preview/debug script builds a clip (Animation.new, add_track, track_insert_key)",
		(hits["build"] as Array).is_empty(), hits["build"])
	rep.check("9 only piece.gd touches the rig's AnimationPlayer", (hits["player"] as Array).is_empty(), hits["player"])
	rep.check("9 no script names a keyed node (Rig, Rig/Upper, Rig/Upper/Bow, FlagSprite)",
		(hits["keyed"] as Array).is_empty(), hits["keyed"])

	# ---------------------------------------------------- run 1: title -> win route -> WON
	var win: Dictionary = Runner.load_route("res://tests/fixtures/win_route.json")
	var turns: Array = win["turns"]
	phase = "win"
	await _frames(10)
	await _key(KEY_ENTER)
	rep.check("run 1: Enter on the title (parse_input_event) starts turn 1", _s() == "PLAN_MOVE", _s())
	for i: int in turns.size():
		if not await _play_turn(turns[i], "win turn %d" % (i + 1)):
			quit(rep.finish())
			return
	await _frames(10)
	rep.check("run 1: ends in WON", _s() == "WON", _s())

	var r1: Array[Dictionary] = _rows_of("win")
	var odd: Array = r1.filter(func(r: Dictionary) -> bool: return not is_equal_approx(float(r["delta"]), FRAME))
	rep.check("run 1: fixed frame rate, every delta 1/60 s (%d frames; run at 60)" % r1.size(), odd.is_empty(), odd.size())
	var bad1: Array = _table_violations(r1)
	rep.check("3 every frame of run 1: draw shows the rig playing shoot (or holding its end pose); other poses show the sprite and no clip",
		bad1.is_empty(), bad1)
	var flag_bad: Array = r1.filter(func(r: Dictionary) -> bool: return r["flag_cur"] != "wave" or not r["flag_playing"])
	rep.check("10 every frame of run 1 (title to WON): the flag plays wave", flag_bad.is_empty(), flag_bad.size())

	# transitions seen (pose entries per piece instance)
	var seen: Dictionary = {}
	for i: int in range(1, r1.size()):
		for id: String in ["p1", "e1"]:
			var a: Dictionary = r1[i - 1][id]
			var b: Dictionary = r1[i][id]
			if not a.is_empty() and not b.is_empty() and a["id"] == b["id"] and a["pose"] != b["pose"]:
				seen["%s->%s" % [a["pose"], b["pose"]]] = true
	var seen_keys: Array = seen.keys()
	seen_keys.sort()
	var entered: Dictionary = {}
	for k: String in seen_keys:
		entered[k.get_slice("->", 1)] = true
	rep.check("6 transitions: run 1 enters draw from idle and from hurt, and leaves draw for idle", seen.has("idle->draw")
		and seen.has("hurt->draw") and seen.has("draw->idle"), seen_keys)
	rep.check("6 transitions: every other shown pose of the §5 table is entered (hurt, idle after hurt, defeat, win)",
		entered.has("hurt") and seen.has("hurt->idle") and entered.has("defeat") and entered.has("win"), seen_keys)
	rep.check("6 hop and recover have no clip and are never shown (no image; brief revision 1 item 2)",
		PieceScript.POSE_CLIPS["hop"] == "" and PieceScript.POSE_CLIPS["recover"] == ""
		and not entered.has("hop") and not entered.has("recover"), seen_keys)

	var shots: Array = _shots(r1)
	rep.check("run 1 has 3 shots (e1, p1, p1, as pinned)", shots.map(func(s: Dictionary) -> String: return s["unit"])
		== ["e1", "p1", "p1"], shots.map(func(s: Dictionary) -> String: return s["unit"]))
	for k: int in shots.size():
		var s: Dictionary = shots[k]
		var label: String = "shot %d (%s, from %s, row %d)" % [k + 1, s["unit"], s["from"], s["start"]]
		rep.check("4 %s: draw frame plays shoot from 0: position 1/60 after that frame's tick" % label,
			s["cur0"] == "shoot" and absf(float(s["pos0"]) - FRAME) < HALF, "%.5f" % s["pos0"])
		rep.check("4 %s: draw frame shows the frame-0 pose, not a stale one (bow %.4f, upper %.4f, rig %s)"
			% [label, s["bow0"], s["upper0"], s["rig0"]],
			absf(float(s["bow0"]) - BOW_FRAME0) < ANG_TOL and absf(float(s["upper0"])) < ANG_TOL
			and (s["rig0"] as Vector2).length() < 0.5)
		rep.check("4 %s: the clip advances exactly 1/60 per game frame" % label, s["step_bad"] == 0, s["step_bad"])
		rep.check("5 %s: on the arrow's first frame (game frame %d) clip position - arrow t = DRAW_LEAD 0.2 within half a frame"
			% [label, s["arrow"]], s["arrow"] == 12 and absf(float(s["lead"]) - DRAW_LEAD) < HALF, "%.5f" % s["lead"])
		var leave: Dictionary = s.get("leave_row", {})
		rep.check("3 %s: back to idle on game frame %d: rig hidden, sprite shown, no clip" % [label, s["end"]],
			s["left_to"] == "idle" and not leave.is_empty() and not leave["mount"] and leave["sprite"]
			and leave["cur"] == "" and not leave["playing"], leave)
		rep.check("3 %s: measured end hold: %d frame(s) with the clip finished and the end pose held (allowed: 0-2)"
			% [label, s["end_hold"]], s["end_hold_ok"] and s["end_hold"] <= 2,
			"last playing position %.5f" % s["last_pos"])
		rep.check("8 %s: Mount.scale.x has the sign of facing (%d)" % [label, s["facing"]],
			signf(float(s["mscale_x"])) == signf(float(s["facing"])), s["mscale_x"])

	# ---------------------------------------------------- run 2: interrupts
	phase = "interrupts"
	await _frames(CARD_WAIT)
	await _key(KEY_ENTER)
	await _key(KEY_ENTER)
	for i: int in 3:
		if not await _play_turn(turns[i], "interrupts turn %d" % (i + 1)):
			quit(rep.finish())
			return
	if not await _route_turn(turns[3], "interrupts turn 4"):
		quit(rep.finish())
		return
	if not await _wait(func() -> bool: return _pose("e1") == "draw"):
		rep.check("turn 4: e1 draws", false, _pose("e1"))
		quit(rep.finish())
		return
	var ign0: int = main.ignored_inputs
	await _key(KEY_ENTER)
	rep.check("7 Enter in e1's startup: ignored_inputs + 1, e1 still draw, shoot still playing",
		main.ignored_inputs == ign0 + 1 and _pose("e1") == "draw"
		and String(main.pieces["e1"]._rig_anim.current_animation) == "shoot",
		"%d -> %d, %s" % [ign0, main.ignored_inputs, _pose("e1")])
	await _wait(func() -> bool: return main._arrows.size() > 0)
	await _frames(5)
	await _key(KEY_P)
	var pause_start: int = sampler.rows.size()
	await _frames(PAUSE_FRAMES)
	var paused_rows: Array = sampler.rows.slice(pause_start).filter(func(r: Dictionary) -> bool: return r["paused"])
	var clip_pos: Array = []
	var flag_pos: Array = []
	for r: Dictionary in paused_rows:
		if not clip_pos.has(r["e1"]["pos"]):
			clip_pos.append(r["e1"]["pos"])
		if not flag_pos.has(r["flag_pos"]):
			flag_pos.append(r["flag_pos"])
	rep.check("7 P in e1's active phase: shoot's position holds for %d paused frames (game time)" % paused_rows.size(),
		paused_rows.size() >= PAUSE_FRAMES - 1 and clip_pos.size() == 1 and paused_rows.all(
			func(r: Dictionary) -> bool: return r["e1"]["cur"] == "shoot" and r["e1"]["mount"]), clip_pos)
	rep.check("7 P: the flag keeps waving while paused (real time; %d distinct wave positions)" % flag_pos.size(),
		flag_pos.size() > 4 and paused_rows.all(func(r: Dictionary) -> bool: return r["flag_cur"] == "wave"), flag_pos.size())
	await _key(KEY_P)
	if not await _wait(func() -> bool: return _pose("p1") == "draw"):
		rep.check("turn 4: p1 draws", false, _pose("p1"))
		quit(rep.finish())
		return
	await _wait(func() -> bool: return main._arrows.size() > 0)
	await _frames(5)
	var old_p1: Object = main.pieces["p1"]
	var old_anim: String = String(old_p1._rig_anim.current_animation)
	await _key(KEY_R)
	var np1: Variant = main.pieces["p1"]
	rep.check("7 R in p1's active phase: the old p1 (which was playing '%s') is freed" % old_anim,
		old_anim == "shoot" and not is_instance_valid(old_p1), is_instance_valid(old_p1))
	rep.check("7 R: the new p1 shows no clip (rig hidden, current_animation empty, stopped)",
		np1 != old_p1 and not np1._rig_mount.visible and String(np1._rig_anim.current_animation) == ""
		and not np1._rig_anim.is_playing(), "%s %s" % [np1.state, np1._rig_anim.current_animation])
	await _frames(30)

	var r2: Array[Dictionary] = _rows_of("interrupts")
	var bad2: Array = _table_violations(r2)
	rep.check("3 every frame of run 2 (Enter, P, R): the pose -> clip table holds", bad2.is_empty(), bad2)
	var flag_bad2: Array = r2.filter(func(r: Dictionary) -> bool: return r["flag_cur"] != "wave")
	rep.check("10 every frame of run 2: the flag plays wave", flag_bad2.is_empty(), flag_bad2.size())
	var s2: Array = _shots(r2)
	if s2.size() >= 2:
		var a: Dictionary = s2[0]
		rep.check("7 paused shot (e1): clip still steps 1/60 per game frame, holds while paused, ends in idle on game frame %d"
			% a["end"], a["unit"] == "e1" and a["step_bad"] == 0 and a["pause_bad"] == 0 and a["paused_frames"] >= PAUSE_FRAMES
			and a["left_to"] == "idle", a)
		rep.check("7 R'd shot (p1): the piece is freed while in draw", s2[1]["unit"] == "p1" and s2[1]["freed"], s2[1])
	else:
		rep.check("run 2 recorded two shots", false, s2.size())

	var measured: Array = shots.map(func(s: Dictionary) -> Dictionary: return {"unit": s["unit"], "from": s["from"],
		"pos0": s["pos0"], "arrow": s["arrow"], "lead": s["lead"], "end": s["end"], "end_hold": s["end_hold"],
		"last_pos": s["last_pos"]})
	print("MEASURED run 1 shots: %s" % [measured])
	print("MEASURED transitions run 1: %s" % [seen_keys])
	quit(rep.finish({"shots_run1": measured, "transitions_run1": seen_keys}))
