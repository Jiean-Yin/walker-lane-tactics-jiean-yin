extends Node2D
## A6 fixture for the GPU price (not gameplay). Run it from the editor (open this scene, F6) and read the
## Visual Profiler's GPU time while each case is held:
##   0 = both effects off (the game board only), 1 = Effect A at its peak (2 hit bursts alive at all times,
##   rule A3), 2 = Effect B at its peak (2 arrow trails emitting along a two-square arc, brief §2).
## Or start with a case: `-- --case=1`. V toggles vsync (the game's own VsyncDebug node inside main.tscn).
## Every second it prints and shows the case, FPS and the viewport's measured GPU time
## (RenderingServer.viewport_get_measured_render_time_gpu), as a cross-check of the Visual Profiler.
## The effect scenes are instanced unchanged; this script only places them and sets emitting.

const BurstScene: PackedScene = preload("res://effects/hit_burst.tscn")
const TrailScene: PackedScene = preload("res://effects/arrow_trail.tscn")
const TrailDriver = preload("res://game/arrow_trail_driver.gd")
const ARROW_TIME: float = 0.35

var case_id: int = 0
var _bursts: Array[Node2D] = []
var _trails: Array[Node2D] = []
var _trail_t: Array[float] = [0.0, 0.175]
var _gpu_sum: float = 0.0
var _frames: int = 0
var _acc: float = 0.0

@onready var _main: Node2D = $Main
@onready var _label: Label = $Label


func _ready() -> void:
	_main.call("_start_play")
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(), true)
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--case="):
			_set_case.call_deferred(int(a.trim_prefix("--case=")))


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_0: _set_case(0)
			KEY_1: _set_case(1)
			KEY_2: _set_case(2)


func _set_case(c: int) -> void:
	for n: Node2D in _bursts + _trails:
		n.queue_free()
	_bursts.clear()
	_trails.clear()
	case_id = c
	if c == 1:
		for i: int in 2:
			_spawn_burst(i)
	elif c == 2:
		for i: int in 2:
			var t: Node2D = TrailScene.instantiate()
			t.z_index = 2
			add_child(t)
			for e: Node in t.get_children():
				(e as GPUParticles2D).emitting = true
			_trails.append(t)
	_gpu_sum = 0.0
	_frames = 0


func _spawn_burst(i: int) -> void:
	var b: Node2D = BurstScene.instantiate()
	add_child(b)
	var unit: String = "p1" if i == 0 else "e1"
	b.position = (_main.get("pieces")[unit] as Node2D).position + Vector2(0.0, -40.0)
	for e: Node in b.get_children():
		(e as CPUParticles2D).emitting = true
	(b.get_node("Dust") as CPUParticles2D).finished.connect(_on_burst_finished.bind(b, i))
	_bursts.append(b)


func _on_burst_finished(b: Node2D, i: int) -> void:
	if case_id != 1 or not _bursts.has(b):
		return
	_bursts.erase(b)
	b.queue_free()
	_spawn_burst(i)


func _process(delta: float) -> void:
	var p1: Node2D = _main.get("pieces")["p1"]
	var from: Vector2 = p1.position + Vector2(14.0, -36.0)
	var to: Vector2 = from + Vector2(256.0, -96.0)
	for i: int in _trails.size():
		_trail_t[i] = fmod(_trail_t[i] + delta, ARROW_TIME)
		_trails[i].position = TrailDriver.tip_of({"from": from, "to": to, "t": _trail_t[i]})
	_gpu_sum += RenderingServer.viewport_get_measured_render_time_gpu(get_viewport().get_viewport_rid())
	_frames += 1
	_acc += delta
	if _acc >= 1.0:
		_acc = 0.0
		var line: String = "PRICE case %d  fps %d  gpu %.4f ms (mean of %d frames)  vsync %s" % [
			case_id, Engine.get_frames_per_second(), _gpu_sum / maxf(1.0, _frames), _frames,
			"off" if DisplayServer.window_get_vsync_mode() == DisplayServer.VSYNC_DISABLED else "on"]
		print(line)
		_label.text = line + "\n0 off   1 Effect A x2   2 Effect B x2   V vsync   (fixture)"
		_gpu_sum = 0.0
		_frames = 0
