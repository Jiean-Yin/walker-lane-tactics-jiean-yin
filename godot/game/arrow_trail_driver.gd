extends Node2D
## A6 Effect B trigger: one arrow trail per arrow in flight (CHANGE-BRIEF §2, rules B1-B6).
## Presentation only: it READS main's state (_arrows, played_events, paused, time_scale) and
## never writes it. Every look value lives in res://effects/arrow_trail.tscn; this script only
## instances the scene, places it, sets `emitting` and `speed_scale`, and frees it.
##
## A child of Main with process_priority 10, so it runs after main's _process (priority 0) in
## the same frame: it sees an arrow on the frame _cue_arrow adds it, and sees it gone on the
## frame _tick_fx drops it.
## The node sits at the origin with z_index 2 (main.tscn): above the board (z 0) and the pieces
## (z 1); equal to main's _fx_layer, which comes later in the tree, so the drawn arrow, HP pips
## and floaters stay on top of the trail.
##
## B1: a new ArrowTrail per new entry of main._arrows (matched by identity), placed at the
##     arrow's `from` point on its first frame, emitting.
## B2: on later frames it follows the arrow tip (formula of main.gd:718-721). On the frame the
##     arrow leaves main._arrows, emitting stops and the trail stays at its last tip position;
##     it is freed after its longest emitter lifetime (Wisps, 0.7 s) of game time.
## B3: a reset (R, play again, start) clears main.played_events; this node sees the list shrink
##     and frees every trail at once.
## B4 / B6: speed_scale is main.time_scale, and 0 while main.paused; the free timer runs on the
##     same clock. With the tree paused this node does not process, so nothing changes.
## B5: this node never reads or writes `visible`.

const MainScript = preload("res://game/main.gd")
const ArrowTrailScene: PackedScene = preload("res://effects/arrow_trail.tscn")

## Trails created since start (read by tests; never reset).
var spawned: int = 0

var _main: MainScript
var _seen_events: int = 0 ## size of main.played_events last frame (a drop means a reset)
## One entry per live trail: {"arrow": the main._arrows Dictionary, "trail": Node2D,
## "landed": bool, "left": game seconds until the trail is freed (after landing)}.
var _trails: Array[Dictionary] = []


func _ready() -> void:
	_main = get_parent() as MainScript


## The arrow tip, as main._draw_fx draws it (main.gd:718-721).
static func tip_of(arrow: Dictionary) -> Vector2:
	var s: float = clampf(float(arrow["t"]) / MainScript.ARROW_TIME, 0.0, 1.0)
	var from: Vector2 = arrow["from"]
	var to: Vector2 = arrow["to"]
	return from.lerp(to, s) + Vector2(0.0, -MainScript.ARROW_ARC * 4.0 * s * (1.0 - s))


func _process(delta: float) -> void:
	if _main == null:
		return
	var events: Array[Dictionary] = _main.played_events
	if events.size() < _seen_events:
		clear_trails()
	_seen_events = events.size()
	var speed: float = _speed()
	var dt: float = delta * speed
	var keep: Array[Dictionary] = []
	for tr: Dictionary in _trails:
		var trail: Node2D = tr["trail"]
		if tr["landed"]:
			tr["left"] = float(tr["left"]) - dt
			if float(tr["left"]) <= 0.0:
				remove_child(trail)
				trail.queue_free()
				continue
		elif _in_flight(tr["arrow"]):
			trail.position = tip_of(tr["arrow"])
		else:
			tr["landed"] = true
			tr["left"] = _longest_lifetime(trail)
			for emitter: Node in trail.get_children():
				(emitter as GPUParticles2D).emitting = false
		keep.append(tr)
	_trails = keep
	for arrow: Dictionary in _main._arrows:
		if not _tracked(arrow):
			_spawn(arrow)
	for tr: Dictionary in _trails:
		for emitter: Node in (tr["trail"] as Node).get_children():
			(emitter as GPUParticles2D).speed_scale = speed


## Live trails, oldest first.
func live_trails() -> Array[Node2D]:
	var out: Array[Node2D] = []
	for tr: Dictionary in _trails:
		out.append(tr["trail"] as Node2D)
	return out


func clear_trails() -> void:
	for tr: Dictionary in _trails:
		var trail: Node = tr["trail"]
		remove_child(trail)
		trail.queue_free()
	_trails.clear()


func _speed() -> float:
	return 0.0 if _main.paused else _main.time_scale


func _in_flight(arrow: Dictionary) -> bool:
	for a: Dictionary in _main._arrows:
		if is_same(a, arrow):
			return true
	return false


func _tracked(arrow: Dictionary) -> bool:
	for tr: Dictionary in _trails:
		if is_same(tr["arrow"], arrow):
			return true
	return false


func _longest_lifetime(trail: Node) -> float:
	var longest: float = 0.0
	for emitter: Node in trail.get_children():
		longest = maxf(longest, (emitter as GPUParticles2D).lifetime)
	return longest


func _spawn(arrow: Dictionary) -> void:
	var trail: Node2D = ArrowTrailScene.instantiate() as Node2D
	add_child(trail)
	trail.position = arrow["from"]
	var speed: float = _speed()
	for emitter: Node in trail.get_children():
		var e: GPUParticles2D = emitter as GPUParticles2D
		e.speed_scale = speed
		e.emitting = true
	_trails.append({"arrow": arrow, "trail": trail, "landed": false, "left": 0.0})
	spawned += 1
