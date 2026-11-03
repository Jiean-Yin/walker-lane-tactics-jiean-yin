extends SceneTree
## A5 headless test: the "exposed" tint (CHANGE-BRIEF §1-2, §5).
## ./scripts/run-test.sh test_exposed_tint.gd <fps>   (run at 30, 60 and 144)
##
## Drives main.tscn through the real game loop with real key presses (root.push_input), and
## samples the player's and the enemy's exposed_amount every frame from a Sampler node with
## process_priority 1000, i.e. after main (0) and the driver (10) in the same frame.
## The "exposed" condition is recomputed here from main's public state, as the oracle.
## main.time_scale stays 1 except where the R4 time-scale check needs 0.5 (see there).

const Report = preload("res://tests/test_report.gd")
const MainScript = preload("res://game/main.gd")
const RulesScript = preload("res://game/rules.gd")
const MainScene = preload("res://game/main.tscn")

const SHADER_PATH: String = "res://shaders/exposed_tint.gdshader"
const RATE: float = 5.0
const FULL: float = 0.2 ## 0 -> 1 in 0.20 s of game time
const EPS: float = 1e-6
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
var sampler: Sampler
var fps: int = 0
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


func _cell(id: String) -> Vector2i:
	return RulesScript.cell_of(main.rules.get_unit(id))


func _pmat() -> ShaderMaterial:
	return main.pieces["p1"].tint_material()


func _emat() -> ShaderMaterial:
	return main.pieces["e1"].tint_material()


## The spec's condition (CHANGE-BRIEF §1), computed from main's state.
func _oracle() -> bool:
	if main.state != MainScript.State.PLAN_MOVE or not main.rules.is_alive("p1"):
		return false
	var dest: Vector2i = _cell("p1") + main.planned_offset
	for e: Dictionary in main.rules.alive_units(RulesScript.ENEMY):
		if RulesScript.in_range(dest, RulesScript.cell_of(e)):
			return true
	return false


func _param(m: ShaderMaterial) -> float:
	if m == null:
		return -1.0
	var v: Variant = m.get_shader_parameter("exposed_amount")
	return float(v) if v != null else -2.0


func _row(delta: float) -> Dictionary:
	var pm: ShaderMaterial = _pmat()
	var em: ShaderMaterial = _emat()
	return {
		"dt": delta,
		"gdt": 0.0 if main.paused else delta * main.time_scale,
		"paused": main.paused,
		"state": _s(),
		"cond": _oracle(),
		"v": _param(pm),
		"e": _param(em),
		"pm": pm.get_instance_id() if pm != null else 0,
		"em": em.get_instance_id() if em != null else 0,
		"turn": main.rules.turn,
	}


func _last() -> Dictionary:
	return sampler.rows[-1]


func _frames(n: int) -> void:
	for i: int in n:
		await process_frame


func _wait(cond: Callable) -> bool:
	for i: int in MAX_FRAMES:
		if cond.call():
			return true
		await process_frame
	return false


## Waits until the last sampled value equals `value` (exactly).
func _wait_value(value: float) -> bool:
	await process_frame
	return await _wait(func() -> bool: return _last()["v"] == value)


## Waits until `t` seconds of game time have been sampled.
func _wait_game_time(t: float) -> void:
	var acc: float = 0.0
	while acc < t - EPS:
		await process_frame
		acc += float(_last()["gdt"])


## From row i0 on: the game time, real frames and unpaused frames until v == value.
func _segment(i0: int, value: float) -> Dictionary:
	var t: float = 0.0
	var frames: int = 0
	var max_gdt: float = 0.0
	for j: int in range(i0, sampler.rows.size()):
		var r: Dictionary = sampler.rows[j]
		t += float(r["gdt"])
		max_gdt = maxf(max_gdt, float(r["gdt"]))
		frames += 1
		if r["v"] == value:
			return {"ok": true, "t": t, "frames": frames, "frame": max_gdt, "end": j}
	return {"ok": false, "t": t, "frames": frames, "frame": max_gdt, "end": -1}


func _within(seg: Dictionary, expected: float) -> bool:
	return seg["ok"] and absf(float(seg["t"]) - expected) <= float(seg["frame"]) + EPS


func _fmt(seg: Dictionary, expected: float) -> String:
	return "%.4f s game time in %d frames, expected %.4f s +- %.4f" % [seg["t"], seg["frames"], expected, seg["frame"]]


# ---------------------------------------------------------------- shader checks (no scene)

func _check_shader() -> void:
	var shader: Shader = load(SHADER_PATH) as Shader
	rep.check("shader loads: %s" % SHADER_PATH, shader != null)
	if shader == null:
		return
	var uniforms: Dictionary = {}
	for u: Dictionary in shader.get_shader_uniform_list():
		uniforms[String(u["name"])] = u
	rep.check("uniform list is exactly [exposed_amount, exposed_color] (case 8)",
		uniforms.size() == 2 and uniforms.has("exposed_amount") and uniforms.has("exposed_color"), uniforms.keys())
	var a: Dictionary = uniforms.get("exposed_amount", {})
	rep.check("exposed_amount: type float (3), hint_range (1) 0.0..1.0",
		int(a.get("type", -1)) == TYPE_FLOAT and int(a.get("hint", -1)) == PROPERTY_HINT_RANGE
		and String(a.get("hint_string", "")).begins_with("0.0,1.0"), [a.get("type"), a.get("hint"), a.get("hint_string")])
	var c: Dictionary = uniforms.get("exposed_color", {})
	rep.check("exposed_color: type vec4 (20)", int(c.get("type", -1)) == TYPE_COLOR, c.get("type"))

	# Defaults and source_color are not reported headless: read them from the source text.
	var src: String = FileAccess.get_file_as_string(SHADER_PATH)
	var flat: String = _squash(src)
	rep.check("source: shader_type canvas_item; and no render_mode",
		flat.contains("shader_type canvas_item;") and not flat.contains("render_mode"))
	rep.check("source: no sampler uniform of its own", not flat.contains("sampler2D"))
	var time_re: RegEx = RegEx.create_from_string("\\bTIME\\b")
	rep.check("source: TIME is not used (R7)", time_re.search(src) == null)
	rep.check("source: exposed_amount : hint_range(0.0, 1.0) = 0.0",
		flat.contains("uniform float exposed_amount : hint_range(0.0, 1.0) = 0.0;"))
	rep.check("source: exposed_color : source_color = vec4(0.878, 0.271, 0.227, 1.0)",
		flat.contains("uniform vec4 exposed_color : source_color = vec4(0.878, 0.271, 0.227, 1.0);"))
	rep.check("source: the colour line is Jiean's",
		flat.contains("COLOR.rgb = mix(COLOR.rgb, exposed_color.rgb, exposed_amount * 0.7);"))

	var scratch: ShaderMaterial = ShaderMaterial.new()
	scratch.shader = shader
	scratch.set_shader_parameter("exposed_amount", 2.0)
	var stored: Variant = scratch.get_shader_parameter("exposed_amount")
	rep.check("set 2.0 from code is stored as 2.0 (hint_range does not clamp storage; drawing: by eye)",
		stored != null and is_equal_approx(float(stored), 2.0), stored)


## Collapses whitespace so formatting does not matter: "a  :b" -> "a : b" style is normalised.
func _squash(s: String) -> String:
	var re: RegEx = RegEx.create_from_string("\\s+")
	var out: String = re.sub(s, " ", true)
	for p: String in ["( ", " )", " ,", " ;"]:
		while out.contains(p):
			out = out.replace(p, p.strip_edges())
	return out


# ---------------------------------------------------------------- frame-by-frame rules

## R2/R3/R4 over every sampled frame: the value moves toward the state's target at exactly
## RATE * game dt, from its previous value (no jump, no restart), and holds while paused.
func _check_every_frame() -> void:
	var bad: Array[String] = []
	var enemy_bad: Array[String] = []
	var shared: int = 0
	for i: int in range(1, sampler.rows.size()):
		var r: Dictionary = sampler.rows[i]
		var prev: float = float(sampler.rows[i - 1]["v"])
		var expect: float = move_toward(prev, 1.0 if r["cond"] else 0.0, RATE * float(r["gdt"]))
		if absf(float(r["v"]) - expect) > EPS and bad.size() < 6:
			bad.append("frame %d: %s cond %s prev %.5f got %.5f want %.5f" % [i, r["state"], r["cond"], prev, r["v"], expect])
		if float(r["e"]) != 0.0 and enemy_bad.size() < 6:
			enemy_bad.append("frame %d: %.5f" % [i, r["e"]])
		if r["pm"] == r["em"] or r["pm"] == 0 or r["em"] == 0:
			shared += 1
	rep.check("every frame (%d): value = move_toward(previous, state ? 1 : 0, 5 x game dt) (R1, R2, R3, R4, R5)" % sampler.rows.size(),
		bad.is_empty(), bad)
	rep.check("every frame: enemy exposed_amount == 0.0 (R6, case 2)", enemy_bad.is_empty(), enemy_bad)
	rep.check("every frame: player and enemy have a material each, never the same one (R6, case 2)", shared == 0, "%d bad frames" % shared)


# ---------------------------------------------------------------- scenario

func _run() -> void:
	await process_frame
	main = MainScene.instantiate()
	root.add_child(main)
	await process_frame
	sampler = Sampler.new()
	sampler.name = "TintSampler"
	sampler.process_priority = 1000
	sampler.row_fn = _row
	root.add_child(sampler)
	await process_frame
	await process_frame
	# --fixed-fps is an engine argument (not in OS.get_cmdline_args()), and the first frames'
	# delta is not always 1/fps (seen at 30 and 144), so fps comes from frames 31-40, which must agree.
	await _frames(38)
	var first_dts: Array[float] = []
	for r: Dictionary in sampler.rows.slice(0, 10):
		first_dts.append(snappedf(float(r["dt"]), 0.000001))
	var tail: Array[Dictionary] = sampler.rows.slice(-10)
	var steady: bool = true
	for r: Dictionary in tail:
		steady = steady and float(r["dt"]) == float(tail[0]["dt"])
	fps = roundi(1.0 / float(tail[0]["dt"]))
	summary["fps"] = fps
	summary["first_deltas"] = first_dts
	print("INFO  fps %d from frames 31-40; first 10 deltas: %s" % [fps, first_dts])
	rep = Report.new("test_exposed_tint_%dfps" % fps)
	rep.check("frames 31-40 all have delta 1/%d (a steady fixed step to measure with)" % fps, steady
		and absf(float(tail[0]["dt"]) * fps - 1.0) < EPS, tail[0]["dt"])
	_check_shader()
	var driver: Node = main.get_node_or_null("ExposedDriver")
	rep.check("main.tscn has the ExposedDriver node, process_priority 10 < sampler 1000",
		driver != null and driver.process_priority == 10 and sampler.process_priority > driver.process_priority)
	rep.check("main.time_scale == 1 and Engine.time_scale == 1 at the start", main.time_scale == 1.0 and Engine.time_scale == 1.0)

	# --- title -> turn 1; assert the start cells instead of assuming them
	_key(KEY_ENTER)
	await _frames(2)
	rep.check("turn 1 PLAN_MOVE: p1 at (0,4), e1 at (7,3)", _s() == "PLAN_MOVE" and main.rules.turn == 1
		and _cell("p1") == Vector2i(0, 4) and _cell("e1") == Vector2i(7, 3), [_s(), _cell("p1"), _cell("e1")])
	var pm0: int = _pmat().get_instance_id()
	var em0: int = _emat().get_instance_id()
	rep.check("each sprite's material uses exposed_tint.gdshader, starts at 0.0, and they differ (R6)",
		_pmat().shader.resource_path == SHADER_PATH and _emat().shader.resource_path == SHADER_PATH
		and pm0 != em0 and _param(_pmat()) == 0.0 and _param(_emat()) == 0.0)

	# --- turns 1 and 2: Right + Enter (never in reach)
	for turn: int in [1, 2]:
		_key(KEY_RIGHT)
		await _frames(3)
		_key(KEY_ENTER)
		if not await _wait(func() -> bool: return _s() == "PLAN_MOVE" and main.rules.turn == turn + 1):
			rep.check("reached turn %d" % (turn + 1), false, _s())
			_finish()
			return
		var want_p: Vector2i = Vector2i(turn, 4)
		var want_e: Vector2i = Vector2i(7 - turn, 3)
		rep.check("turn %d PLAN_MOVE: p1 at %s, e1 at %s" % [turn + 1, want_p, want_e],
			_cell("p1") == want_p and _cell("e1") == want_e, [_cell("p1"), _cell("e1")])
	await _wait_game_time(0.3)
	var all_zero: bool = true
	for r: Dictionary in sampler.rows:
		if r["v"] != 0.0:
			all_zero = false
	rep.check("turns 1-2 and turn 3 before any key: every sample is 0.0 (R1)", all_zero)
	rep.check("turn 3 standing square (2,4) is out of reach of (5,3)", not _oracle())
	rep.check("same player material through turns 1-3 (pose changes keep it)", _pmat().get_instance_id() == pm0)

	# --- R1/R2: Right plans (3,4), distance 2 -> rise 0 -> 1 in 0.20 s
	var i0: int = sampler.rows.size()
	_key(KEY_RIGHT)
	await _wait_value(1.0)
	rep.check("Right plans (3,4) and it is in reach (state begins)", main.planned_offset == Vector2i(1, 0) and sampler.rows[i0]["cond"])
	var first: float = float(sampler.rows[i0]["v"])
	rep.check("rise: the first frame already moves by 5 x dt (begins on the first frame)",
		absf(first - RATE * float(sampler.rows[i0]["gdt"])) <= EPS, first)
	var seg: Dictionary = _segment(i0, 1.0)
	rep.check("rise 0 -> 1 takes 0.20 s of game time (R2)", _within(seg, FULL), _fmt(seg, FULL))
	var rise_frames: int = seg["frames"]
	summary["rise"] = seg
	await _frames(10)
	rep.check("holds at 1.0 while the state holds (R1)", _last()["v"] == 1.0)

	# --- Left: back to (2,4), out of reach -> fall 1 -> 0 in 0.20 s
	i0 = sampler.rows.size()
	_key(KEY_LEFT)
	await _wait_value(0.0)
	seg = _segment(i0, 0.0)
	rep.check("fall 1 -> 0 takes 0.20 s of game time (R2)", not sampler.rows[i0]["cond"] and _within(seg, FULL), _fmt(seg, FULL))
	summary["fall"] = seg

	# --- R5: Right, Left once the value passes 0.5 -> 0 after v x 0.20 s
	_key(KEY_RIGHT)
	await _wait(func() -> bool: return float(_last()["v"]) >= 0.5)
	await process_frame
	var v0: float = float(_last()["v"])
	i0 = sampler.rows.size()
	_key(KEY_LEFT)
	await _wait_value(0.0)
	seg = _segment(i0, 0.0)
	rep.check("ends mid-rise at v = %.3f: reaches 0 after v x 0.20 s (R5)" % v0, v0 > 0.0 and v0 < 1.0 and _within(seg, v0 * FULL),
		_fmt(seg, v0 * FULL))

	# --- R3: tap Right / Left faster than 0.20 s (Right held 0.08 s, Left 0.06 s, so most turns are mid-way)
	var r3_start: int = sampler.rows.size()
	var right: bool = true
	for k: int in 10:
		_key(KEY_RIGHT if right else KEY_LEFT)
		await _wait_game_time(0.08 if right else 0.06)
		right = not right
	var r3_end: int = sampler.rows.size()
	var turns_mid: int = 0
	var drops: Array[String] = []
	var wrong_dir: Array[String] = []
	for i: int in range(r3_start + 1, r3_end):
		var r: Dictionary = sampler.rows[i]
		var p: Dictionary = sampler.rows[i - 1]
		if r["cond"] != p["cond"] and float(p["v"]) > 0.0 and float(p["v"]) < 1.0:
			turns_mid += 1
		if r["cond"] and float(r["v"]) == 0.0:
			drops.append("frame %d" % i)
		if r["cond"] and float(r["v"]) < float(p["v"]) or not r["cond"] and float(r["v"]) > float(p["v"]):
			wrong_dir.append("frame %d" % i)
	rep.check("retrigger: the state flipped %d times mid-transition (the test reached R3's case)" % turns_mid, turns_mid >= 6, turns_mid)
	rep.check("retrigger: no frame at 0 while the state holds (R3, case 1)", drops.is_empty(), drops)
	rep.check("retrigger: never falls while true, never rises while false; turns around from its current value (R3)",
		wrong_dir.is_empty(), wrong_dir)
	if main.planned_offset != Vector2i.ZERO:
		_key(KEY_LEFT)
	await _wait_value(0.0)

	# --- R4: pause mid-rise
	i0 = sampler.rows.size()
	_key(KEY_RIGHT)
	await _wait(func() -> bool: return float(_last()["v"]) >= 0.4)
	_key(KEY_P)
	await process_frame
	var held: float = float(_last()["v"])
	var p_start: int = sampler.rows.size() - 1
	await _frames(30)
	var still: bool = main.paused
	for i: int in range(p_start, sampler.rows.size()):
		if float(sampler.rows[i]["v"]) != held or not sampler.rows[i]["paused"]:
			still = false
	rep.check("paused mid-rise at %.3f: value constant for 30+ frames (R4, case 4)" % held, still and held > 0.0 and held < 1.0)
	_key(KEY_P)
	await _wait_value(1.0)
	seg = _segment(i0, 1.0)
	rep.check("with a pause inside, the rise still takes 0.20 s of unpaused game time (R4)", _within(seg, FULL)
		and int(seg["frames"]) >= rise_frames + 30, _fmt(seg, FULL))
	_key(KEY_LEFT)
	await _wait_value(0.0)

	# --- R4: time scale. Does Engine.time_scale scale delta under --fixed-fps?
	Engine.time_scale = 0.5
	await _frames(2)
	var scaled_dt: float = float(_last()["dt"])
	var engine_scales: bool = absf(scaled_dt - 0.5 / float(fps)) < EPS
	summary["engine_time_scale_scales_delta_under_fixed_fps"] = engine_scales
	summary["delta_with_engine_time_scale_0_5"] = scaled_dt
	print("INFO  Engine.time_scale 0.5 under --fixed-fps %d: delta = %.6f (1/fps = %.6f) -> %s" % [fps, scaled_dt, 1.0 / fps,
		"scaled, using Engine.time_scale" if engine_scales else "NOT scaled, using main.time_scale = 0.5 instead"])
	if not engine_scales:
		Engine.time_scale = 1.0
		main.time_scale = 0.5
	var how: String = "Engine.time_scale" if engine_scales else "main.time_scale"
	i0 = sampler.rows.size()
	_key(KEY_RIGHT)
	await _wait_value(1.0)
	seg = _segment(i0, 1.0)
	var real: float = float(seg["frames"]) / float(fps)
	rep.check("%s 0.5: rise still 0.20 s of game time (R4)" % how, _within(seg, FULL), _fmt(seg, FULL))
	rep.check("%s 0.5: twice the frames, about 0.40 s real time (R4)" % how,
		absi(int(seg["frames"]) - 2 * rise_frames) <= 2 and absf(real - 2.0 * FULL) <= 2.0 / fps + EPS,
		"%d frames (%.4f s real) vs %d at scale 1" % [seg["frames"], real, rise_frames])
	Engine.time_scale = 1.0
	main.time_scale = 1.0
	await _frames(2)

	# --- the state ends on confirm: Enter -> PLAY_MOVES, fall 1 -> 0 in 0.20 s
	rep.check("before Enter: at 1.0, planning (3,4)", _last()["v"] == 1.0 and main.planned_offset == Vector2i(1, 0))
	i0 = sampler.rows.size()
	_key(KEY_ENTER)
	await _wait_value(0.0)
	seg = _segment(i0, 0.0)
	rep.check("Enter (confirm) ends it: falls 1 -> 0 in 0.20 s during %s" % sampler.rows[i0]["state"],
		sampler.rows[i0]["state"] == "PLAY_MOVES" and _within(seg, FULL), _fmt(seg, FULL))

	# --- turn 3 attacks: hold fire; turn 4 begins with the standing square in reach
	if not await _wait(func() -> bool: return _s() == "PLAN_ATTACK" or (_s() == "PLAN_MOVE" and main.rules.turn == 4)):
		rep.check("turn 3 reached attack planning", false, _s())
		_finish()
		return
	if _s() == "PLAN_ATTACK":
		_key(KEY_SPACE)
	var turn4_first: int = -1
	if await _wait(func() -> bool: return _s() == "PLAN_MOVE" and main.rules.turn == 4):
		for i: int in range(sampler.rows.size() - 1, 0, -1):
			if sampler.rows[i]["state"] == "PLAN_MOVE" and sampler.rows[i - 1]["state"] != "PLAN_MOVE":
				turn4_first = i
				break
	rep.check("turn 4 PLAN_MOVE: p1 at (3,4) alive, e1 at (4,3)", turn4_first > 0 and main.rules.is_alive("p1")
		and _cell("p1") == Vector2i(3, 4) and _cell("e1") == Vector2i(4, 3), [_s(), main.rules.turn, _cell("p1"), _cell("e1")])
	if turn4_first > 0:
		var r4: Dictionary = sampler.rows[turn4_first]
		rep.check("turn 4 begins already in reach: rises from the first PLAN_MOVE frame (Begins)",
			r4["cond"] and absf(float(r4["v"]) - RATE * float(r4["gdt"])) <= EPS, r4["v"])
	await _wait_value(1.0)
	rep.check("same player material until the retry", _pmat().get_instance_id() == pm0)

	# --- R (retry) while red: new sprite, new material; fades out from 1 (answer 1)
	var old_p: int = _pmat().get_instance_id()
	i0 = sampler.rows.size()
	_key(KEY_R)
	rep.check("R: turn 1, p1 back at (0,4), e1 at (7,3)", _s() == "PLAN_MOVE" and main.rules.turn == 1
		and _cell("p1") == Vector2i(0, 4) and _cell("e1") == Vector2i(7, 3), [_cell("p1"), _cell("e1")])
	var new_p: ShaderMaterial = _pmat()
	rep.check("R: the new sprite has a new material with the shader, not the old one or the enemy's (R6, case 5)",
		new_p != null and new_p.shader != null and new_p.shader.resource_path == SHADER_PATH
		and new_p.get_instance_id() != old_p and new_p.get_instance_id() != _emat().get_instance_id())
	await _wait_value(0.0)
	seg = _segment(i0, 0.0)
	rep.check("R while at 1.0: the new sprite fades 1 -> 0 in 0.20 s (no jump)",
		absf(float(sampler.rows[i0]["v"]) - (1.0 - RATE * float(sampler.rows[i0]["gdt"]))) <= EPS and _within(seg, FULL),
		_fmt(seg, FULL))
	await _frames(5)
	rep.check("after R: the new sprite's value is driven (0.0) and the enemy's stays 0.0", _last()["v"] == 0.0 and _last()["e"] == 0.0)

	_check_every_frame()
	_finish()


func _finish() -> void:
	summary["frames_sampled"] = sampler.rows.size() if sampler != null else 0
	var code: int = rep.finish(summary)
	if main != null:
		main.queue_free()
	if sampler != null:
		sampler.row_fn = Callable()
		sampler.queue_free()
	await _frames(3)
	quit(code)
