extends Node2D
## A7 fixture preview for the committing action `shoot` (CHANGE-BRIEF §9). Not gameplay.
##
## Background: the real board drawn by main.tscn after the game has started (PLAN_MOVE, turn 1),
## both archers on their start squares (player column 0 lane 5, enemy column 7 lane 4), and the
## GoalFlag waving. There is no camera, so 1280 x 720 is the in-game scale.
##
## Trigger: on frame TRIGGER_FRAME the player archer is set to `draw`, as main's _cue_draw does
## (main.gd:486); SHOT_TIME later (DRAW_LEAD + ARROW_TIME + ATTACK_RECOVER = 0.8 s, main.gd:29-33) it
## is set back to `idle`, as _cue_attacker_idle does (main.gd:519). piece.gd then plays and advances
## `shoot` exactly as in the game. No real arrow, impact or hit burst: these are fixture captures.
## At 30 fps (the capture command, CHANGE-BRIEF §9) the idle frame is 10 + 24 = 34.
##
## The frame counter counts this node's _process() calls from 0. This node runs before Main (tree
## order), so the pose is set before main ticks the piece in the same frame, as a cue would be.
## A FrameLogger child with process_priority 1000 writes one line per frame to logs/shoot_preview.log
## after everything else has run, so frame N of a Movie Maker capture lines up with line N.
##
## Written by Claude Code (main session). It sets only the piece's pose; every clip value is in
## res://animations/shoot.tres.

const TRIGGER_FRAME: int = 10
const SHOT_TIME: float = 0.8 ## s, main.gd:29-33 (0.2 + 0.35 + 0.25)
const LOG_NAME: String = "shoot_preview.log"


## Runs after every other _process() of the frame and logs the player archer's rig.
class FrameLogger extends Node:
	var preview: Node

	func _process(_delta: float) -> void:
		preview.call("log_frame")


var _frame: int = -1
var _idle_frame: int = -1
var _log: FileAccess

@onready var _main: Node2D = $Main


func _ready() -> void:
	# The same call Enter makes on the title screen: turn 1, PLAN_MOVE, pieces on start squares.
	_main.call("_start_play")
	var dir: String = ProjectSettings.globalize_path("res://").path_join("../logs").simplify_path()
	DirAccess.make_dir_recursive_absolute(dir)
	_log = FileAccess.open(dir.path_join(LOG_NAME), FileAccess.WRITE)
	var logger: FrameLogger = FrameLogger.new()
	logger.name = "FrameLogger"
	logger.preview = self
	logger.process_priority = 1000
	add_child(logger)
	_line("PREVIEW shoot: state %s, trigger frame %d, back to idle %.2f s later" % [_main.call("state_name"),
		TRIGGER_FRAME, SHOT_TIME])
	_line("frame\tpose\tclip\tclip_s\tclip_frame60\trig_shown\tsprite_shown")


func _process(delta: float) -> void:
	_frame += 1
	var p: Node2D = _main.get("pieces")["p1"]
	if _frame == TRIGGER_FRAME:
		# Fixed-rate runs (--fixed-fps, Movie Maker) give the same delta every frame.
		_idle_frame = TRIGGER_FRAME + int(round(SHOT_TIME / delta))
		p.call("set_state", "draw")
		_line("PREVIEW frame %d: p1 -> draw (idle on frame %d)" % [_frame, _idle_frame])
	elif _frame == _idle_frame and String(p.get("state")) == "draw":
		p.call("set_state", "idle")
		_line("PREVIEW frame %d: p1 -> idle" % _frame)


func log_frame() -> void:
	var p: Node2D = _main.get("pieces")["p1"]
	var r: Dictionary = p.call("rig_snapshot") # read-only; piece.gd stays the rig's only user
	var pos: float = float(r["pos"])
	_line("%d\t%s\t%s\t%s\t%s\t%s\t%s" % [_frame, p.get("state"), r["clip"],
		("%.4f" % pos) if r["playing"] else "-", ("%.1f" % (pos * 60.0)) if r["playing"] else "-",
		r["rig_visible"], r["sprite_visible"]])


func _exit_tree() -> void:
	if _log != null:
		_log.close()


func _line(text: String) -> void:
	print(text)
	if _log != null:
		_log.store_line(text)
		_log.flush()
