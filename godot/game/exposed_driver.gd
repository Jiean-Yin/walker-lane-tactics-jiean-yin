extends Node
## A5 "exposed" tint driver (CHANGE-BRIEF §1-2). Presentation only: it READS main's state
## (state, planned_offset, paused, time_scale, rules, pieces) and never writes it.
##
## A child of Main with process_priority 10, so it runs after main's _process (priority 0) in
## the same frame and sees every state change main made in that frame.
##
## exposed = state == PLAN_MOVE and the player is alive and some living enemy is in reach
##           of the planned square (Rules.in_range(player_cell + planned_offset, enemy_cell)).
## The amount moves linearly toward 1 (exposed) or 0 at RATE per second of GAME time
## (delta * main.time_scale), turning around from its current value (R2, R3, R5), and holds
## still while main.paused (R4). Only the player archer's material is written (R6).

const MainScript = preload("res://game/main.gd")
const RulesScript = preload("res://game/rules.gd")

const RATE: float = 5.0 ## per second of game time: 0 -> 1 in 0.20 s (R2)

## The current value; it survives a retry, so a red archer fades out on the new sprite.
var amount: float = 0.0

var _main: MainScript


func _ready() -> void:
	_main = get_parent() as MainScript


func _process(delta: float) -> void:
	if _main == null:
		return
	if not _main.paused:
		var target: float = 1.0 if is_exposed() else 0.0
		amount = move_toward(amount, target, RATE * delta * _main.time_scale)
	var p: Variant = _main.pieces.get(MainScript.PLAYER_ID)
	if p != null:
		p.set_exposed_amount(amount)


func is_exposed() -> bool:
	if _main.state != MainScript.State.PLAN_MOVE:
		return false
	var rules: RulesScript = _main.rules
	if not rules.is_alive(MainScript.PLAYER_ID):
		return false
	var dest: Vector2i = RulesScript.cell_of(rules.get_unit(MainScript.PLAYER_ID)) + _main.planned_offset
	for e: Dictionary in rules.alive_units(RulesScript.ENEMY):
		if RulesScript.in_range(dest, RulesScript.cell_of(e)):
			return true
	return false
