extends Node
## A6 debug key for the GPU price (assignment "Use It"): V toggles vsync, so FPS can rise above the
## display's refresh rate for an FPS comparison. Presentation only: it reads no game state and writes none.
## V is unused by the game (main.gd:53-65); F9 is not used because the editor takes it (A5 finding).

const KEY: Key = KEY_V


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY:
		var off: bool = DisplayServer.window_get_vsync_mode() == DisplayServer.VSYNC_DISABLED
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if off else DisplayServer.VSYNC_DISABLED)
		print("VSYNC %s" % ("on" if off else "off"))
