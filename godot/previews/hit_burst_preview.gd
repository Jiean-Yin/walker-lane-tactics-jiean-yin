extends Node2D
## A6 fixture preview for Effect A, the hit burst (CHANGE-BRIEF §5). Not gameplay.
##
## Background: the real board drawn by main.tscn after the game has started (PLAN_MOVE, turn 1),
## both archers on their start squares (player column 0 lane 5, enemy column 7 lane 4). There
## is no camera, so 1280 x 720 is the in-game scale.
##
## Burst1 fires on the player archer at frame 10. With `retrigger` on (or `-- --retrigger` on
## the command line), Burst2 fires on the enemy archer at frame 42 (1.05 s x 30 fps after 10).
## Two separate instances, as rule A3 (overlap) asks. Their seeds are fixed in the .tscn
## (Burst1: 61, Burst2: 62), so every capture is the same; the effect scene itself has none.
##
## This script only places the bursts and sets `emitting`; every look value is in
## res://effects/hit_burst.tscn. The frame counter counts _process() calls from 0.

const TRIGGER_FRAME: int = 10
const RETRIGGER_FRAME: int = 42
const HIT_OFFSET: Vector2 = Vector2(0.0, -40.0) ## base-disc centre -> body (CHANGE-BRIEF §1 "Where")

@export var retrigger: bool = false

var _frame: int = -1

@onready var _main: Node2D = $Main
@onready var _burst1: Node2D = $Burst1
@onready var _burst2: Node2D = $Burst2


func _ready() -> void:
	if "--retrigger" in OS.get_cmdline_user_args():
		retrigger = true
	# The same call Enter makes on the title screen: turn 1, PLAN_MOVE, pieces on start squares.
	_main.call("_start_play")
	print("PREVIEW hit_burst: retrigger %s, state %s" % ["on" if retrigger else "off", _main.call("state_name")])


func _process(_delta: float) -> void:
	_frame += 1
	if _frame == TRIGGER_FRAME:
		_fire(_burst1, "p1")
	elif retrigger and _frame == RETRIGGER_FRAME:
		_fire(_burst2, "e1")


func _fire(burst: Node2D, unit: String) -> void:
	var piece: Node2D = _main.get("pieces")[unit]
	burst.position = piece.position + HIT_OFFSET
	for emitter: Node in burst.get_children():
		(emitter as CPUParticles2D).emitting = true
	print("PREVIEW frame %d: %s on %s at %s" % [_frame, burst.name, unit, burst.position])
