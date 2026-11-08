extends SceneTree
## A6 price: headless CPU time per frame for four cases (CHANGE-BRIEF §4 "Price", §7).
## ./scripts/run-test.sh cost_effects.gd 60 300
##
## Cases, each measured the same way, in ROUNDS rounds (forward order, then reverse order, so a
## drift over the run shows as a difference between rounds rather than between cases):
##   empty     : a bare Node2D under root (the control: what the measuring itself costs).
##   game_off  : main.tscn at PLAN_MOVE, turn 1, both archers on their start squares; no event
##               is played, so HitBurstDriver and ArrowTrailDriver are idle (both effects off).
##   burst_x2  : game_off + Effect A held at the most bursts the brief allows alive at once
##               (rule A3: 2). Two HitBurst instances, first started 0.6 s apart; each is freed
##               when its Dust emits `finished` (as the driver does, A6) and replaced at once by
##               a new instance (A3 = overlap, not restart), so 2 are alive on every sampled frame.
##   trail_x2  : game_off + Effect B in its heaviest state (§2 "Peak count": 2 trails,
##               120 particles). Two ArrowTrail instances emitting continuously while moving along
##               a two-square shot arc (ArrowTrailDriver.tip_of, the formula of main.gd:718-721),
##               half a flight apart.
##
## The effect scenes are only instanced, placed, given emitting / speed_scale and freed here,
## as the drivers do; no look value is set and no effect or gameplay file is changed. Game state
## is never written: the only input is the real Enter key press that starts play.
##
## Per sampled frame, a Sampler node (process_priority 1000, so it runs last) records:
##   frame_us   : wall time between its consecutive _process calls = one whole main-loop
##                iteration. With --fixed-fps the loop is not throttled to real time, so headless
##                this is the frame's CPU time (process + physics + the dummy render step).
##   process_us : Performance.TIME_PROCESS (the engine's process-step time; the value read in
##                frame N is the one measured for frame N-1).
## Mean, standard deviation, min, median, p95 and max are printed for both.
##
## PASS/FAIL checks only confirm the set-up (state, live effect counts, sample counts). The
## prices are reported, not judged; pairs that should differ but don't are printed as NOTE lines.

const Report = preload("res://tests/test_report.gd")
const MainScene = preload("res://game/main.tscn")
const BurstScene = preload("res://effects/hit_burst.tscn")
const TrailScene = preload("res://effects/arrow_trail.tscn")
const TrailDriver = preload("res://game/arrow_trail_driver.gd")
const MainScript = preload("res://game/main.gd")

const WARMUP_FRAMES: int = 90 ## 1.5 s at 60 fps: past one burst cycle and a trail's 0.7 s fill
const SAMPLE_FRAMES: int = 600 ## 10 s at 60 fps
const ROUNDS: int = 2
const MAX_WAIT: int = 600
const CASES: Array[String] = ["empty", "game_off", "burst_x2", "trail_x2"]
## Pairs that should differ, and why.
const PAIRS: Array = [
	["empty", "game_off", "the game scene does work every frame (board, HUD, pieces, drivers)"],
	["game_off", "burst_x2", "Effect A is a CPU node: 2 bursts simulate on the CPU"],
	["game_off", "trail_x2", "Effect B is a GPU node: headless near zero is the prediction (§7, answer 4)"],
	["burst_x2", "trail_x2", "CPU effect vs GPU effect"],
]

const BURST_STAGGER: int = 36 ## 0.6 s between the two bursts' first starts
const HIT_OFFSET: Vector2 = Vector2(0.0, -40.0) ## CHANGE-BRIEF §1 "Where"
const ARROW_START: Vector2 = Vector2(14.0, -36.0) ## main.gd:493 (x times facing)
const SHOT: Vector2 = Vector2(256.0, -96.0) ## two squares forward, one lane up (SQUARE 128 x 96)


## Records one row per frame, after every other _process() of that frame.
class Sampler extends Node:
	var recording: bool = false
	var last_usec: int = -1
	var frame_us: PackedFloat64Array = PackedFloat64Array()
	var process_us: PackedFloat64Array = PackedFloat64Array()
	var probe: Callable ## extra per-frame check (live effect counts), called while recording
	var min_delta: float = INF
	var max_delta: float = 0.0

	func start() -> void:
		frame_us = PackedFloat64Array()
		process_us = PackedFloat64Array()
		last_usec = -1
		recording = true

	func _process(delta: float) -> void:
		var now: int = Time.get_ticks_usec()
		if recording:
			min_delta = minf(min_delta, delta)
			max_delta = maxf(max_delta, delta)
			if last_usec >= 0:
				frame_us.append(float(now - last_usec))
				process_us.append(Performance.get_monitor(Performance.TIME_PROCESS) * 1.0e6)
			if probe.is_valid():
				probe.call()
		last_usec = now


## Effect A rig: two slots, started `stagger` frames apart. A burst lives until its longest
## emitter (Dust) emits `finished`, exactly as HitBurstDriver frees it (rule A6); on that signal
## the slot frees it and instances a new one at once, so 2 bursts stay alive.
class BurstRig extends Node2D:
	var scene: PackedScene
	var spots: Array[Vector2] = []
	var stagger: int = 36
	var slots: Array[Node2D] = [null, null]
	var spawned: int = 0
	var _frame: int = 0

	func _process(_delta: float) -> void:
		for k: int in slots.size():
			if _frame == k * stagger:
				_respawn(k)
		_frame += 1

	func _respawn(k: int) -> void:
		var old: Node2D = slots[k]
		if old != null and is_instance_valid(old):
			remove_child(old)
			old.queue_free()
		var burst: Node2D = scene.instantiate() as Node2D
		add_child(burst)
		burst.position = spots[k]
		(burst.get_node("Dust") as CPUParticles2D).finished.connect(_respawn.bind(k))
		for e: Node in burst.get_children():
			(e as CPUParticles2D).speed_scale = 1.0
			(e as CPUParticles2D).emitting = true
		slots[k] = burst
		spawned += 1

	## Live bursts (the driver's definition: not yet freed after Dust finished).
	func alive() -> int:
		var n: int = 0
		for b: Node2D in slots:
			if b != null and is_instance_valid(b) and not b.is_queued_for_deletion():
				n += 1
		return n


## Effect B rig: trails that emit continuously and follow an arrow tip that loops its flight.
class TrailRig extends Node2D:
	var scene: PackedScene
	var arrows: Array[Dictionary] = [] ## {"from", "to", "t"} as in main._arrows
	var trails: Array[Node2D] = []
	var flight: float = 0.35

	func setup() -> void:
		for a: Dictionary in arrows:
			var trail: Node2D = scene.instantiate() as Node2D
			add_child(trail)
			trail.position = TrailDriver.tip_of(a)
			for e: Node in trail.get_children():
				(e as GPUParticles2D).speed_scale = 1.0
				(e as GPUParticles2D).emitting = true
			trails.append(trail)

	func _process(delta: float) -> void:
		for i: int in trails.size():
			var a: Dictionary = arrows[i]
			a["t"] = fmod(float(a["t"]) + delta, flight)
			trails[i].position = TrailDriver.tip_of(a)

	## Emitters currently emitting, over all trails.
	func emitting_count() -> int:
		var n: int = 0
		for t: Node2D in trails:
			for e: Node in t.get_children():
				if (e as GPUParticles2D).emitting:
					n += 1
		return n


var rep: Report
var sampler: Sampler
var fps: int = 0
var results: Dictionary = {} ## case -> {"frame_us": PackedFloat64Array, "process_us": ...}
var setup_notes: Dictionary = {} ## case -> per-round set-up facts
var _probe_min: int = 0
var _probe_max: int = 0


func _initialize() -> void:
	_run()


func _key(code: int) -> void:
	for pressed: bool in [true, false]:
		var ev: InputEventKey = InputEventKey.new()
		ev.keycode = code as Key
		ev.physical_keycode = code as Key
		ev.pressed = pressed
		root.push_input(ev)


func _frames(n: int) -> void:
	for i: int in n:
		await process_frame


func _stats(v: PackedFloat64Array) -> Dictionary:
	var n: int = v.size()
	if n == 0:
		return {"n": 0}
	var sorted: Array = Array(v)
	sorted.sort()
	var sum: float = 0.0
	for x: float in v:
		sum += x
	var mean: float = sum / n
	var sq: float = 0.0
	for x: float in v:
		sq += (x - mean) * (x - mean)
	var sd: float = sqrt(sq / maxi(n - 1, 1))
	return {
		"n": n, "mean": mean, "sd": sd, "min": sorted[0], "p50": sorted[n / 2],
		"p95": sorted[mini(n - 1, int(ceil(n * 0.95)) - 1)], "max": sorted[n - 1],
	}


func _fmt(s: Dictionary) -> String:
	if int(s.get("n", 0)) == 0:
		return "no samples"
	return "n %d  mean %.4f ms  sd %.4f  min %.4f  p50 %.4f  p95 %.4f  max %.4f" % [
		s["n"], s["mean"] / 1000.0, s["sd"] / 1000.0, s["min"] / 1000.0, s["p50"] / 1000.0,
		s["p95"] / 1000.0, s["max"] / 1000.0]


## Builds one case under root and returns its top node (null on failure).
func _build(case_name: String, round_i: int) -> Node:
	if case_name == "empty":
		var empty: Node2D = Node2D.new()
		empty.name = "Empty"
		root.add_child(empty)
		return empty
	var main: MainScript = MainScene.instantiate() as MainScript
	root.add_child(main)
	await _frames(2)
	_key(KEY_ENTER)
	var ok: bool = false
	for i: int in MAX_WAIT:
		await process_frame
		if main.state_name() == "PLAN_MOVE" and main.pieces.size() == 2:
			ok = true
			break
	var tag: String = "%s r%d" % [case_name, round_i]
	rep.check("%s: game at PLAN_MOVE with 2 pieces" % tag, ok, main.state_name())
	var hb: Node = main.get_node("HitBurstDriver")
	var at: Node = main.get_node("ArrowTrailDriver")
	rep.check("%s: drivers idle (no burst, no trail, no event played)" % tag,
		hb.get_child_count() == 0 and at.get_child_count() == 0 and main.played_events.is_empty(),
		"bursts %d, trails %d, events %d" % [hb.get_child_count(), at.get_child_count(), main.played_events.size()])
	var player: Node2D = null
	var enemy: Node2D = null
	for p: Node2D in main.pieces.values():
		if p.get("facing") == 1 and player == null:
			player = p
		else:
			enemy = p
	if player == null or enemy == null:
		rep.check("%s: found player and enemy archers" % tag, false)
		return main
	if case_name == "burst_x2":
		var rig: BurstRig = BurstRig.new()
		rig.name = "CostBurstRig"
		rig.scene = BurstScene
		rig.stagger = BURST_STAGGER
		rig.spots = [player.position + HIT_OFFSET, enemy.position + HIT_OFFSET]
		main.add_child(rig)
	elif case_name == "trail_x2":
		var rig2: TrailRig = TrailRig.new()
		rig2.name = "CostTrailRig"
		rig2.scene = TrailScene
		rig2.flight = MainScript.ARROW_TIME
		var f1: Vector2 = player.position + Vector2(ARROW_START.x * player.get("facing"), ARROW_START.y)
		var f2: Vector2 = enemy.position + Vector2(ARROW_START.x * enemy.get("facing"), ARROW_START.y)
		rig2.arrows = [
			{"from": f1, "to": f1 + SHOT, "t": 0.0},
			{"from": f2, "to": f2 + Vector2(-SHOT.x, -SHOT.y), "t": MainScript.ARROW_TIME * 0.5},
		]
		rig2.z_index = 2
		main.add_child(rig2)
		rig2.setup()
	return main


func _measure(case_name: String, round_i: int) -> void:
	var node: Node = await _build(case_name, round_i)
	var tag: String = "%s r%d" % [case_name, round_i]
	var probe_fn: Callable = Callable()
	_probe_min = 1 << 30
	_probe_max = -1
	if case_name == "burst_x2":
		var rig: BurstRig = node.get_node("CostBurstRig") as BurstRig
		probe_fn = func() -> void:
			var n: int = rig.alive()
			_probe_min = mini(_probe_min, n)
			_probe_max = maxi(_probe_max, n)
	elif case_name == "trail_x2":
		var rig2: TrailRig = node.get_node("CostTrailRig") as TrailRig
		probe_fn = func() -> void:
			var n: int = rig2.emitting_count()
			_probe_min = mini(_probe_min, n)
			_probe_max = maxi(_probe_max, n)
	await _frames(WARMUP_FRAMES)
	sampler.probe = probe_fn
	sampler.start()
	await _frames(SAMPLE_FRAMES + 1)
	sampler.recording = false
	sampler.probe = Callable()
	rep.check("%s: %d frames sampled" % [tag, SAMPLE_FRAMES], sampler.frame_us.size() >= SAMPLE_FRAMES,
		sampler.frame_us.size())
	if case_name == "burst_x2":
		rep.check("%s: 2 bursts alive on every sampled frame (rule A3 maximum)" % tag,
			_probe_min == 2 and _probe_max == 2, "min %d, max %d" % [_probe_min, _probe_max])
	elif case_name == "trail_x2":
		rep.check("%s: 2 trails x 2 emitters emitting on every sampled frame (§2 peak)" % tag,
			_probe_min == 4 and _probe_max == 4, "min %d, max %d" % [_probe_min, _probe_max])
	var fs: Dictionary = _stats(sampler.frame_us)
	var ps: Dictionary = _stats(sampler.process_us)
	print("CASE %-9s round %d  frame   %s" % [case_name, round_i, _fmt(fs)])
	print("CASE %-9s round %d  process %s" % [case_name, round_i, _fmt(ps)])
	if not results.has(case_name):
		results[case_name] = {"frame_us": PackedFloat64Array(), "process_us": PackedFloat64Array(), "rounds": []}
	var entry: Dictionary = results[case_name]
	var fa: PackedFloat64Array = entry["frame_us"]
	fa.append_array(sampler.frame_us)
	entry["frame_us"] = fa # assign back: a packed array read from a Dictionary may be a copy
	var pa: PackedFloat64Array = entry["process_us"]
	pa.append_array(sampler.process_us)
	entry["process_us"] = pa
	(entry["rounds"] as Array).append({"round": round_i, "frame": fs, "process": ps})
	root.remove_child(node)
	node.free()
	await _frames(10)


func _run() -> void:
	rep = Report.new("cost_effects")
	await process_frame
	print("cost_effects: Godot %s, warm-up %d, samples %d per case per round, %d rounds" % [
		Engine.get_version_info().get("string", ""), WARMUP_FRAMES, SAMPLE_FRAMES, ROUNDS])
	sampler = Sampler.new()
	sampler.name = "CostSampler"
	sampler.process_priority = 1000
	root.add_child(sampler)
	for r: int in ROUNDS:
		var order: Array[String] = CASES.duplicate()
		if r % 2 == 1:
			order.reverse()
		for c: String in order:
			await _measure(c, r + 1)

	fps = roundi(1.0 / sampler.max_delta) if sampler.max_delta > 0.0 else 0
	rep.check("fixed rate: every sampled delta is the same (--fixed-fps)",
		is_equal_approx(sampler.min_delta, sampler.max_delta),
		"delta %.6f .. %.6f s, %d fps" % [sampler.min_delta, sampler.max_delta, fps])

	print("")
	print("POOLED (all rounds)")
	var pooled: Dictionary = {}
	for c: String in CASES:
		var fsum: PackedFloat64Array = _pooled(c, "frame_us")
		var psum: PackedFloat64Array = _pooled(c, "process_us")
		pooled[c] = {"frame": _stats(fsum), "process": _stats(psum)}
		print("CASE %-9s frame   %s" % [c, _fmt(pooled[c]["frame"])])
		print("CASE %-9s process %s" % [c, _fmt(pooled[c]["process"])])

	print("")
	print("DIFFERENCES (pooled mean, B - A; t = difference / standard error of the difference)")
	var diffs: Array = []
	for pair: Array in PAIRS:
		for metric: String in ["frame", "process"]:
			var a: Dictionary = pooled[pair[0]][metric]
			var b: Dictionary = pooled[pair[1]][metric]
			var d: float = float(b["mean"]) - float(a["mean"])
			var se: float = sqrt(pow(float(a["sd"]), 2) / float(a["n"]) + pow(float(b["sd"]), 2) / float(b["n"]))
			var t: float = d / se if se > 0.0 else 0.0
			var same_value: bool = is_equal_approx(float(a["mean"]), float(b["mean"]))
			var line: String = "%-8s %-9s -> %-9s  %+.4f ms  (t %+.1f)" % [metric, pair[0], pair[1], d / 1000.0, t]
			print(line)
			var note: String = ""
			if same_value:
				note = "identical means: the script may be measuring only itself"
			elif absf(t) < 2.0:
				note = "not distinguishable from noise (|t| < 2)"
			if note != "":
				print("NOTE  %s %s vs %s: %s. Expected to differ because %s." % [metric, pair[0], pair[1], note, pair[2]])
			diffs.append({"metric": metric, "a": pair[0], "b": pair[1], "diff_us": d, "t": t, "note": note})

	root.remove_child(sampler)
	sampler.free()
	await _frames(5)
	quit(rep.finish({"fps_ticks": fps, "warmup_frames": WARMUP_FRAMES, "sample_frames": SAMPLE_FRAMES,
		"rounds": ROUNDS, "units": "microseconds", "pooled": pooled, "differences": diffs,
		"per_round": _per_round()}))


func _pooled(c: String, key: String) -> PackedFloat64Array:
	return results[c][key] as PackedFloat64Array


func _per_round() -> Dictionary:
	var out: Dictionary = {}
	for c: String in results.keys():
		out[c] = results[c]["rounds"]
	return out
