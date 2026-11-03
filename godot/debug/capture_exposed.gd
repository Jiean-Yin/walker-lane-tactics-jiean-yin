extends Node
## A5 controlled-value captures for the "exposed" tint (CHANGE-BRIEF §3, "Use It").
## A debug scene, not part of the game: it runs the real main.tscn in a real window, and C captures the
## player archer at exposed_amount 0.0, 0.5, 1.0 and 2.0 with the course's capture() function. (C, not F9: run from
## the editor, F9 is caught by the editor and pauses the project.)
## Run (needs a window, not headless):  "$GODOT" --path godot res://debug/capture_exposed.tscn
## then press Enter on the title card, wait for turn 1, press C. The window closes when it is done.
## Writes evidence/a5/captures/exposed_<value>.png and exposed_pixels.md (P1, P2 beside the predictions).

const MainScene: PackedScene = preload("res://game/main.tscn")
const VALUES: Array[float] = [0.0, 0.5, 1.0, 2.0]
## Screen points from CHANGE-BRIEF §3 (player at the start square, turn 1), and Jiean's predictions there.
const POINTS: Dictionary = {"P1 head": Vector2i(192, 581), "P2 base disc": Vector2i(202, 634)}
const PREDICTED: Dictionary = {
	"P1 head": {0.0: "(224, 174, 117)", 0.5: "(224, 137, 96)", 1.0: "(224, 101, 76)", 2.0: "(224, 27, 34) if not clamped"},
	"P2 base disc": {0.0: "(90, 58, 34)", 0.5: "(137, 62, 42)", 1.0: "(184, 66, 51)", 2.0: "-"},
}

var _main: Node
var _busy: bool = false


func _ready() -> void:
	_main = MainScene.instantiate()
	add_child(_main)


func _input(event: InputEvent) -> void:
	var key: InputEventKey = event as InputEventKey
	if key == null or not key.pressed or key.echo or key.physical_keycode != KEY_C or _busy:
		return
	get_viewport().set_input_as_handled()
	_run()


## From the Assignment 5 text ("Use It"), unchanged apart from types.
func capture(driver: Node, mat: ShaderMaterial, param: StringName, value: float, path: String) -> void:
	driver.set_process(false) # also set_physics_process(false) if the driver writes there
	mat.set_shader_parameter(param, value)
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
	driver.set_process(true)


func _run() -> void:
	_busy = true
	var driver: Node = _main.get_node("ExposedDriver")
	var mat: ShaderMaterial = _main.pieces["p1"].tint_material()
	var dir: String = ProjectSettings.globalize_path("res://").path_join("../evidence/a5/captures").simplify_path()
	DirAccess.make_dir_recursive_absolute(dir)
	var lines: Array[String] = [
		"# Controlled-value captures: exposed_amount (%s)" % Time.get_datetime_string_from_system(),
		"",
		"Godot %s, renderer %s, window %s. Captured with the course's capture() in `godot/debug/capture_exposed.gd`:" % [
			Engine.get_version_info()["string"], RenderingServer.get_current_rendering_method(), get_viewport().get_texture().get_size()],
		"the driver is paused, the value set, and the frame read after `frame_post_draw`. Game state: %s, turn %d." % [
			_main.STATE_NAMES[_main.state], _main.rules.turn],
		"",
		"| Point | Value | Predicted (CHANGE-BRIEF §3) | Measured RGB | Difference per channel |",
		"|---|---|---|---|---|",
	]
	for v: float in VALUES:
		var file: String = "exposed_%s.png" % str(v)
		var path: String = dir.path_join(file)
		await capture(driver, mat, &"exposed_amount", v, path)
		var img: Image = Image.load_from_file(path)
		for point_name: String in POINTS:
			var p: Vector2i = POINTS[point_name]
			var c: Color = img.get_pixel(p.x, p.y)
			lines.append("| %s %s | %s | %s | (%d, %d, %d) | %s |" % [point_name, p, str(v), PREDICTED[point_name][v], c.r8, c.g8, c.b8, _diff(PREDICTED[point_name][v], c)])
	var stored: Variant = mat.get_shader_parameter("exposed_amount")
	lines.append("")
	lines.append("After the 2.0 capture the material reads back %s; the driver resumed afterwards." % str(stored))
	var f: FileAccess = FileAccess.open(dir.path_join("exposed_pixels.md"), FileAccess.WRITE)
	f.store_string("\n".join(lines) + "\n")
	f.close()
	print("\n".join(lines))
	get_tree().quit()


func _diff(pred: String, c: Color) -> String:
	var m: RegExMatch = RegEx.create_from_string("\\((\\d+), (\\d+), (\\d+)\\)").search(pred)
	if m == null:
		return "-"
	return "(%+d, %+d, %+d)" % [c.r8 - int(m.get_string(1)), c.g8 - int(m.get_string(2)), c.b8 - int(m.get_string(3))]
