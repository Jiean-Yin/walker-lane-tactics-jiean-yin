extends SceneTree
## A6 headless test: Effect A (hit burst) configuration (CHANGE-BRIEF §1 "The settings").
## ./scripts/run-test.sh test_hit_burst_config.gd 60
##
## Loads res://effects/hit_burst.tscn, instantiates it (not added to the tree, nothing runs),
## and reads every setting the brief names back from the loaded nodes and resources.
## The expected values below are copied from the brief's table, not from the scene file.
## A text pass over the .tscn also rejects Godot 3 property names, which would load
## silently and leave the default (CHANGE-BRIEF §6, failure 2).

const Report = preload("res://tests/test_report.gd")

const SCENE_PATH: String = "res://effects/hit_burst.tscn"
const EPS: float = 1e-4

const RED: String = "#E0453A"
const WOOD: String = "#3A2616"
const DUST: String = "#7A5A3A"

## Plain property values per emitter (CHANGE-BRIEF §1 table). Angles are degrees, as the brief.
const EXPECT: Dictionary = {
	"Flash": {
		"emitting": false, "amount": 1, "lifetime": 1.08, "one_shot": true,
		"explosiveness": 1.0, "lifetime_randomness": 0.0, "local_coords": false,
		"emission_shape": 0, "direction": Vector2(0, -1), "spread": 0.0, "gravity": Vector2(0, 0),
		"initial_velocity_min": 0.0, "initial_velocity_max": 0.0,
		"angle_min": 0.0, "angle_max": 0.0,
		"angular_velocity_min": 0.0, "angular_velocity_max": 0.0,
		"damping_min": 0.0, "damping_max": 0.0,
		"scale_amount_min": 3.0, "scale_amount_max": 3.0,
		"particle_flag_align_y": false,
		"preprocess": 0.0, "use_fixed_seed": false,
	},
	"Splinters": {
		"emitting": false, "amount": 14, "lifetime": 0.45, "one_shot": true,
		"explosiveness": 1.0, "lifetime_randomness": 0.3, "local_coords": false,
		"emission_shape": 0, "direction": Vector2(0, -1), "spread": 75.0, "gravity": Vector2(0, 900),
		"initial_velocity_min": 140.0, "initial_velocity_max": 260.0,
		"angle_min": 0.0, "angle_max": 360.0,
		"angular_velocity_min": -720.0, "angular_velocity_max": 720.0,
		"damping_min": 0.0, "damping_max": 0.0,
		"scale_amount_min": 0.8, "scale_amount_max": 1.2,
		"particle_flag_align_y": true,
		"preprocess": 0.0, "use_fixed_seed": false,
	},
	"Dust": {
		"emitting": false, "amount": 8, "lifetime": 1.2, "one_shot": true,
		"explosiveness": 0.9, "lifetime_randomness": 0.3, "local_coords": false,
		"emission_shape": 1, "emission_sphere_radius": 10.0,
		"direction": Vector2(0, -1), "spread": 180.0, "gravity": Vector2(0, -30),
		"initial_velocity_min": 10.0, "initial_velocity_max": 35.0,
		"angle_min": 0.0, "angle_max": 360.0,
		"angular_velocity_min": -30.0, "angular_velocity_max": 30.0,
		"damping_min": 0.0, "damping_max": 0.0,
		"scale_amount_min": 1.0, "scale_amount_max": 1.4,
		"particle_flag_align_y": false,
		"preprocess": 0.0, "use_fixed_seed": false,
	},
}

## scale_amount_curve: value at the start and at the end of life.
const CURVES: Dictionary = {
	"Flash": [1.0, 1.6],
	"Splinters": [1.0, 0.6],
	"Dust": [0.6, 1.6],
}

## color_ramp: [offset, hex colour, alpha] per point.
const RAMPS: Dictionary = {
	"Flash": [[0.0, RED, 0.9], [1.0, RED, 0.0]],
	"Splinters": [[0.0, RED, 1.0], [0.2, WOOD, 1.0], [0.7, WOOD, 1.0], [1.0, WOOD, 0.0]],
	"Dust": [[0.0, DUST, 0.55], [1.0, DUST, 0.0]],
}

## texture: "dot" = GradientTexture2D 32 x 32 radial, white -> transparent;
##          "sliver" = GradientTexture2D 4 x 16, white, transparent at both ends.
const TEXTURES: Dictionary = {"Flash": "dot", "Splinters": "sliver", "Dust": "dot"}

## Godot 3 (or editor-only) names that must never be written as a scene property.
const FORBIDDEN_KEYS: Array[String] = ["initial_velocity", "scale_amount", "damping", "angular_velocity", "angle",
	"flag_align_y", "flag_disable_z", "flag_rotate_y"]
const FORBIDDEN_TYPES: Array[String] = ["\"ParticlesMaterial\"", "\"Particles2D\"", "\"GradientTexture\""]

var rep: Report


func _initialize() -> void:
	rep = Report.new("test_hit_burst_config")
	_run()
	var code: int = rep.finish({"scene": SCENE_PATH})
	quit(code)


func _run() -> void:
	_check_text()
	var packed: PackedScene = load(SCENE_PATH) as PackedScene
	rep.check("scene loads: %s" % SCENE_PATH, packed != null)
	if packed == null:
		return
	var root: Node = packed.instantiate()
	rep.check("root is a Node2D named HitBurst", root is Node2D and root.name == &"HitBurst", [root.get_class(), root.name])
	rep.check("root z_index is 2 (above Pieces z 1, below HUD z 3)", root is Node2D and (root as Node2D).z_index == 2,
		(root as Node2D).z_index if root is Node2D else "n/a")
	var names: Array[String] = []
	for c: Node in root.get_children():
		names.append("%s:%s" % [c.name, c.get_class()])
	rep.check("children are exactly Flash, Splinters, Dust, each a CPUParticles2D",
		names == ["Flash:CPUParticles2D", "Splinters:CPUParticles2D", "Dust:CPUParticles2D"], names)

	var total: int = 0
	for emitter: String in ["Flash", "Splinters", "Dust"]:
		var n: CPUParticles2D = root.get_node_or_null(emitter) as CPUParticles2D
		if not rep.check("%s exists as CPUParticles2D" % emitter, n != null):
			continue
		_check_values(emitter, n)
		_check_curve(emitter, n)
		_check_ramp(emitter, n)
		_check_texture(emitter, n)
		_check_material(emitter, n)
		total += n.amount
	rep.check("peak count: 23 particles per burst, 46 with 2 bursts alive (A3)", total == 23 and total * 2 == 46, total)
	root.free()


# ---------------------------------------------------------------- scene text

func _check_text() -> void:
	var src: String = FileAccess.get_file_as_string(SCENE_PATH)
	rep.check("scene text is readable", src != "")
	var bad: Array[String] = []
	var line_no: int = 0
	for line: String in src.split("\n"):
		line_no += 1
		var key: String = line.get_slice("=", 0).strip_edges()
		if line.contains("=") and not line.begins_with("[") and key in FORBIDDEN_KEYS:
			bad.append("line %d: %s" % [line_no, line.strip_edges()])
		for t: String in FORBIDDEN_TYPES:
			if line.begins_with("[") and line.contains("type=" + t):
				bad.append("line %d: %s" % [line_no, line.strip_edges()])
	rep.check("no Godot 3 / editor-only names in the scene text (failure 2)", bad.is_empty(), bad)


# ---------------------------------------------------------------- per emitter

func _check_values(emitter: String, n: CPUParticles2D) -> void:
	var want: Dictionary = EXPECT[emitter]
	for prop: String in want:
		var got: Variant = n.get(prop)
		rep.check("%s.%s == %s" % [emitter, prop, want[prop]], _same(got, want[prop]), got)


func _check_curve(emitter: String, n: CPUParticles2D) -> void:
	var c: Curve = n.scale_amount_curve
	var want: Array = CURVES[emitter]
	if not rep.check("%s.scale_amount_curve is a Curve" % emitter, c != null):
		return
	var ok: bool = c.point_count == 2 and _close(c.sample(0.0), want[0]) and _close(c.sample(1.0), want[1])
	rep.check("%s.scale_amount_curve %.1f -> %.1f (2 points)" % [emitter, want[0], want[1]], ok,
		"points %d, sample(0) %.4f, sample(1) %.4f, max_value %.2f" % [c.point_count, c.sample(0.0), c.sample(1.0), c.max_value])


func _check_ramp(emitter: String, n: CPUParticles2D) -> void:
	var g: Gradient = n.color_ramp
	var want: Array = RAMPS[emitter]
	if not rep.check("%s.color_ramp is a Gradient" % emitter, g != null):
		return
	var ok: bool = g.get_point_count() == want.size()
	var got: Array[String] = []
	for i: int in g.get_point_count():
		got.append("%.2f %s a%.2f" % [g.get_offset(i), g.get_color(i).to_html(false), g.get_color(i).a])
		if i < want.size():
			var w: Array = want[i]
			var col: Color = Color(String(w[1]))
			col.a = float(w[2])
			ok = ok and _close(g.get_offset(i), float(w[0])) and _same_color(g.get_color(i), col)
	var want_s: Array[String] = []
	for w: Array in want:
		want_s.append("%.2f %s a%.2f" % [w[0], w[1], w[2]])
	rep.check("%s.color_ramp %s" % [emitter, want_s], ok, got)


func _check_texture(emitter: String, n: CPUParticles2D) -> void:
	var t: GradientTexture2D = n.texture as GradientTexture2D
	if not rep.check("%s.texture is a GradientTexture2D, not null (failure 9)" % emitter, t != null,
			n.texture.get_class() if n.texture != null else "null"):
		return
	var g: Gradient = t.gradient
	if not rep.check("%s.texture has a Gradient" % emitter, g != null):
		return
	var all_white: bool = true
	for i: int in g.get_point_count():
		var c: Color = g.get_color(i)
		all_white = all_white and _close(c.r, 1.0) and _close(c.g, 1.0) and _close(c.b, 1.0)
	var first_a: float = g.get_color(0).a
	var last_a: float = g.get_color(g.get_point_count() - 1).a
	var detail: String = "%dx%d fill %d, %d points, alpha first %.2f last %.2f, white %s" % [
		t.width, t.height, t.fill, g.get_point_count(), first_a, last_a, all_white]
	if TEXTURES[emitter] == "dot":
		rep.check("%s.texture: soft dot 32 x 32, radial, white -> transparent" % emitter,
			t.width == 32 and t.height == 32 and t.fill == GradientTexture2D.FILL_RADIAL and all_white
			and _close(first_a, 1.0) and _close(last_a, 0.0), detail)
	else:
		var opaque_inside: bool = false
		for i: int in range(1, g.get_point_count() - 1):
			opaque_inside = opaque_inside or _close(g.get_color(i).a, 1.0)
		rep.check("%s.texture: sliver 4 x 16, white, transparent at both ends" % emitter,
			t.width == 4 and t.height == 16 and all_white and _close(first_a, 0.0) and _close(last_a, 0.0)
			and opaque_inside, detail)


func _check_material(emitter: String, n: CPUParticles2D) -> void:
	var m: CanvasItemMaterial = n.material as CanvasItemMaterial
	rep.check("%s.material is CanvasItemMaterial, blend_mode Mix (0), not additive (failure 6)" % emitter,
		m != null and m.blend_mode == CanvasItemMaterial.BLEND_MODE_MIX,
		("%s blend %d" % [m.get_class(), m.blend_mode]) if m != null else (n.material.get_class() if n.material != null else "null"))


# ---------------------------------------------------------------- comparison

func _close(a: float, b: float) -> bool:
	return absf(a - b) <= EPS


func _same_color(a: Color, b: Color) -> bool:
	# The scene stores 6-digit floats; one 8-bit step is 1/255, so EPS is far inside it.
	return _close(a.r, b.r) and _close(a.g, b.g) and _close(a.b, b.b) and _close(a.a, b.a)


func _same(got: Variant, want: Variant) -> bool:
	match typeof(want):
		TYPE_BOOL:
			return typeof(got) == TYPE_BOOL and got == want
		TYPE_INT:
			return typeof(got) == TYPE_INT and got == want
		TYPE_FLOAT:
			return typeof(got) == TYPE_FLOAT and _close(got, want)
		TYPE_VECTOR2:
			return typeof(got) == TYPE_VECTOR2 and _close(got.x, want.x) and _close(got.y, want.y)
	return got == want
