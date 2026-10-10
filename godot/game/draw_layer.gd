extends Node2D
## A canvas layer whose drawing is delegated to a callable (board, effects, HUD).

var draw_fn: Callable


func _draw() -> void:
	if draw_fn.is_valid():
		draw_fn.call(self)
