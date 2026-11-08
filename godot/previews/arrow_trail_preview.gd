extends Node2D
## A6 fixture preview for Effect B, the arrow trail (CHANGE-BRIEF §5). Not gameplay.
##
## Background: the real board drawn by main.tscn after the game has started (PLAN_MOVE, turn 1),
## both archers on their start squares (player column 0 lane 5, enemy column 7 lane 4; shown
## lane numbers, rules.gd:50-55). There is no camera, so 1280 x 720 is the in-game scale.
##
## The condition "an arrow is in flight" is played here, not in main: an arrow drawn the way
## main.gd:716-728 draws it flies from the player archer to column 2, lane 4 (cell (2, 3)), a
## two-square shot. Start and end points use main's own formulas (main.gd:493-494), and the tip
## follows main's arc (main.gd:718-722). The arrow's clock advances by delta and the arrow is
## dropped once t >= ARROW_TIME, as _tick_fx() does (main.gd:199-205). At 30 fps that is:
##   frame 10: launch, trail placed at the bow and set emitting;
##   frame 21: t = 11/30 s >= 0.35 s, the arrow lands, emitting set false (0.35 s x 30 = 10.5 frames).
## Main's game state is only read, never written.
##
## The Trail instance has a fixed seed in the .tscn (71), so every capture is the same; the
## effect scene itself has none. This script only places the trail and sets `emitting`; every
## look value is in res://effects/arrow_trail.tscn. The frame counter counts _process() calls from 0.

const START_FRAME: int = 10
const END_FRAME: int = 21 ## for the log only; the end comes from t >= ARROW_TIME, as in main
const TARGET_CELL: Vector2i = Vector2i(2, 3) ## column 2, shown lane 4

var _frame: int = -1
var _flying: bool = false
var _t: float = 0.0
var _from: Vector2 = Vector2.ZERO
var _to: Vector2 = Vector2.ZERO
var _arrow_time: float = 0.35
var _arrow_arc: float = 40.0
var _col_ink: Color = Color.BLACK
var _col_card: Color = Color.WHITE

@onready var _main: Node2D = $Main
@onready var _trail: Node2D = $Trail
@onready var _arrow: Node2D = $Arrow


func _ready() -> void:
	var k: Dictionary = _main.get_script().get_script_constant_map()
	_arrow_time = float(k["ARROW_TIME"])
	_arrow_arc = float(k["ARROW_ARC"])
	_col_ink = k["COL_INK"]
	_col_card = k["COL_CARD"]
	_arrow.draw.connect(_draw_arrow)
	# The same call Enter makes on the title screen: turn 1, PLAN_MOVE, pieces on start squares.
	_main.call("_start_play")
	var p: Node2D = _main.get("pieces")["p1"]
	_from = p.position + Vector2(14.0 * float(p.get("facing")), -36.0)
	_to = (_main.call("_cell_rect", TARGET_CELL) as Rect2).get_center() + Vector2(0.0, 2.0)
	_trail.position = _from
	print("PREVIEW arrow_trail: state %s, from %s to %s, ARROW_TIME %.2f" % [_main.call("state_name"), _from, _to, _arrow_time])


func _process(delta: float) -> void:
	_frame += 1
	if _frame == START_FRAME:
		_flying = true
		_t = 0.0
		_trail.position = _tip()
		_set_emitting(true)
		print("PREVIEW frame %d: launch at %s, emitting" % [_frame, _trail.position])
	elif _flying:
		_t += delta
		if _t >= _arrow_time:
			_flying = false
			_trail.position = _to
			_set_emitting(false)
			print("PREVIEW frame %d: landed at %s (t %.3f s), emitting off (brief: frame %d)" % [_frame, _to, _t, END_FRAME])
		else:
			_trail.position = _tip()
	_arrow.queue_redraw()


func _tip() -> Vector2:
	var s: float = clampf(_t / _arrow_time, 0.0, 1.0)
	return _from.lerp(_to, s) + Vector2(0.0, -_arrow_arc * 4.0 * s * (1.0 - s))


func _set_emitting(on: bool) -> void:
	for emitter: Node in _trail.get_children():
		(emitter as GPUParticles2D).emitting = on


## The arrow shape of main.gd:722-728, at the current tip.
func _draw_arrow() -> void:
	if not _flying:
		return
	var s: float = clampf(_t / _arrow_time, 0.0, 1.0)
	var pos: Vector2 = _tip()
	var vel: Vector2 = (_to - _from) + Vector2(0.0, -_arrow_arc * 4.0 * (1.0 - 2.0 * s))
	var dir: Vector2 = vel.normalized()
	var side: Vector2 = Vector2(-dir.y, dir.x)
	_arrow.draw_line(pos - dir * 30.0, pos, Color("#5A3A22"), 3.0)
	_arrow.draw_colored_polygon(PackedVector2Array([pos + dir * 8.0, pos + side * 4.5, pos - side * 4.5]), _col_ink)
	_arrow.draw_line(pos - dir * 30.0, pos - dir * 36.0 + side * 5.0, _col_card, 2.0)
	_arrow.draw_line(pos - dir * 30.0, pos - dir * 36.0 - side * 5.0, _col_card, 2.0)
