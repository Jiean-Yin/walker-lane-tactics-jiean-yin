extends Node2D
## A6 Effect A trigger: one hit burst per played "damaged" event (CHANGE-BRIEF §1, rules A1-A6).
## Presentation only: it READS main's state (played_events, pieces, paused, time_scale) and
## never writes it. Every look value lives in res://effects/hit_burst.tscn; this script only
## instances the scene, places it, sets `emitting` and `speed_scale`, and frees it.
##
## A child of Main with process_priority 10, so it runs after main's _process (priority 0) in
## the same frame and sees an impact on the frame _cue_impact plays it (A1).
## The node sits at the origin with z 0, so each burst's own z_index 2 stays absolute.
##
## A3 retrigger = overlap: every event gets a NEW instance; earlier bursts keep playing.
## A4: bursts are children of this node, never of an archer. A reset (R, play again, start)
##     clears main.played_events; this node sees the list shrink and frees every live burst.
## A5: speed_scale follows main.time_scale, and is 0 while main.paused.
## A6: a burst frees itself when its longest emitter (Dust) emits `finished`.

const MainScript = preload("res://game/main.gd")
const HitBurstScene: PackedScene = preload("res://effects/hit_burst.tscn")

const HIT_OFFSET: Vector2 = Vector2(0.0, -40.0) ## base-disc centre -> body (CHANGE-BRIEF §1 "Where")
const LONGEST_EMITTER: String = "Dust"

## Bursts created since start (read by tests; never reset).
var spawned: int = 0

var _main: MainScript
var _read: int = 0 ## how many of main.played_events this node has looked at


func _ready() -> void:
	_main = get_parent() as MainScript


func _process(_delta: float) -> void:
	if _main == null:
		return
	var events: Array[Dictionary] = _main.played_events
	if events.size() < _read:
		clear_bursts()
		_read = 0
	while _read < events.size():
		var ev: Dictionary = events[_read]
		_read += 1
		if String(ev["type"]) == "damaged":
			_spawn(ev)
	var speed: float = _speed()
	for burst: Node in get_children():
		for emitter: Node in burst.get_children():
			(emitter as CPUParticles2D).speed_scale = speed


## Live bursts, oldest first (excludes ones already queued for deletion).
func live_bursts() -> Array[Node2D]:
	var out: Array[Node2D] = []
	for burst: Node in get_children():
		if not burst.is_queued_for_deletion():
			out.append(burst as Node2D)
	return out


func clear_bursts() -> void:
	for burst: Node in get_children():
		remove_child(burst)
		burst.queue_free()


func _speed() -> float:
	return 0.0 if _main.paused else _main.time_scale


func _spawn(ev: Dictionary) -> void:
	var piece: Node2D = _main.pieces.get(ev["unit"])
	if piece == null:
		return
	var burst: Node2D = HitBurstScene.instantiate() as Node2D
	add_child(burst)
	burst.position = piece.position + HIT_OFFSET
	var longest: CPUParticles2D = burst.get_node(LONGEST_EMITTER) as CPUParticles2D
	longest.finished.connect(burst.queue_free)
	var speed: float = _speed()
	for emitter: Node in burst.get_children():
		var e: CPUParticles2D = emitter as CPUParticles2D
		e.speed_scale = speed
		e.emitting = true
	spawned += 1
