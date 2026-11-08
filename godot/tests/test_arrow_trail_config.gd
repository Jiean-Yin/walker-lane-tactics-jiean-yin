extends SceneTree
## A6 headless test: Effect B (arrow trail) configuration (CHANGE-BRIEF §2 "The settings").
## ./scripts/run-test.sh test_arrow_trail_config.gd 60
##
## Loads res://effects/arrow_trail.tscn, instantiates it (not added to the tree, nothing runs),
## and reads every setting the brief names back from the loaded nodes and resources.
## The expected values below are copied from the brief's table, not from the scene file.
## Before reading a value, it checks with ClassDB that the property exists on that class in this
## Godot build and is stored (not editor-only), so a wrong name fails instead of reading null.
## A text pass over the .tscn also rejects Godot 3 / editor-only names (CHANGE-BRIEF §6, failure 2).

const Report = preload("res://tests/test_report.gd")

const SCENE_PATH: String = "res://effects/arrow_trail.tscn"
const EPS: float = 1e-4

const STREAK_COL: String = "#6E5A44"
const WISP_COL: String = "#6E5A44"  # r1 (TUNING.md): was #9A8466
const VIS_RECT: Rect2 = Rect2(-320, -200, 640, 400)

## GPUParticles2D node values per emitter (CHANGE-BRIEF §2 table, upper half).
const NODE_EXPECT: Dictionary = {
	"Streak": {
		"emitting": false, "amount": 48, "lifetime": 0.30, "one_shot": false,
		"explosiveness": 0.0, "preprocess": 0.0, "local_coords": false,
		"fixed_fps": 30, "interpolate": true, "trail_enabled": false,
		"visibility_rect": VIS_RECT, "use_fixed_seed": false,
	},
	"Wisps": {
		"emitting": false, "amount": 12, "lifetime": 0.70, "one_shot": false,
		"explosiveness": 0.0, "preprocess": 0.0, "local_coords": false,
		"fixed_fps": 30, "interpolate": true, "trail_enabled": false,
		"visibility_rect": VIS_RECT, "use_fixed_seed": false,
	},
}

## ParticleProcessMaterial values per emitter (CHANGE-BRIEF §2 table, lower half).
## direction and gravity are Vector3 on this class. "—" rows in the brief are not listed.
const MAT_EXPECT: Dictionary = {
	"Streak": {
		"particle_flag_disable_z": true, "emission_shape": 0,
		"direction": Vector3(0, -1, 0), "spread": 180.0, "gravity": Vector3(0, 0, 0),
		"initial_velocity_min": 0.0, "initial_velocity_max": 8.0,
		"damping_min": 10.0, "damping_max": 10.0,
		"scale_min": 0.30, "scale_max": 0.35,
		"turbulence_enabled": false,
	},
	"Wisps": {
		"particle_flag_disable_z": true, "emission_shape": 1, "emission_sphere_radius": 4.0,
		"direction": Vector3(0, -1, 0), "spread": 180.0, "gravity": Vector3(0, -20, 0),
		"initial_velocity_min": 10.0, "initial_velocity_max": 25.0,
		"damping_min": 15.0, "damping_max": 20.0,
		"scale_min": 0.5, "scale_max": 0.8,
		"turbulence_enabled": true,
		"turbulence_influence_min": 0.1, "turbulence_influence_max": 0.2,
		"turbulence_noise_strength": 1.0, "turbulence_noise_scale": 9.0,
	},
}

## scale_curve: value at the start and at the end of life.
const CURVES: Dictionary = {"Streak": [1.0, 0.2], "Wisps": [0.6, 1.4]}

## color_ramp: [offset, hex colour, alpha] per point.
const RAMPS: Dictionary = {
	"Streak": [[0.0, STREAK_COL, 0.8], [1.0, STREAK_COL, 0.0]],
	"Wisps": [[0.0, WISP_COL, 0.7], [1.0, WISP_COL, 0.0]],  # r1: alpha was 0.45
}

## Godot 3 (or editor-only) names that must never be written as a scene property.
const FORBIDDEN_KEYS: Array[String] = ["initial_velocity", "scale_amount", "scale", "damping", "angular_velocity",
	"angle", "flag_align_y", "flag_disable_z", "flag_rotate_y", "trail_size_modifier"]
const FORBIDDEN_TYPES: Array[String] = ["\"ParticlesMaterial\"", "\"Particles2D\"", "\"GradientTexture\""]

var rep: Report


func _initialize() -> void:
	rep = Report.new("test_arrow_trail_config")
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
	rep.check("root is a Node2D named ArrowTrail", root is Node2D and root.name == &"ArrowTrail", [root.get_class(), root.name])
	var names: Array[String] = []
	for c: Node in root.get_children():
		names.append("%s:%s" % [c.name, c.get_class()])
	rep.check("children are exactly Streak, Wisps, each a GPUParticles2D",
		names == ["Streak:GPUParticles2D", "Wisps:GPUParticles2D"], names)

	var total: int = 0
	var mats: Array[ParticleProcessMaterial] = []
	for emitter: String in ["Streak", "Wisps"]:
		var n: GPUParticles2D = root.get_node_or_null(emitter) as GPUParticles2D
		if not rep.check("%s exists as GPUParticles2D" % emitter, n != null):
			continue
		_check_props(emitter, n, "GPUParticles2D", NODE_EXPECT[emitter])
		_check_texture(emitter, n)
		_check_material(emitter, n)
		var m: ParticleProcessMaterial = n.process_material as ParticleProcessMaterial
		if rep.check("%s.process_material is a ParticleProcessMaterial" % emitter, m != null,
				n.process_material.get_class() if n.process_material != null else "null"):
			mats.append(m)
			_check_props(emitter + ".process_material", m, "ParticleProcessMaterial", MAT_EXPECT[emitter])
			_check_curve(emitter, m)
			_check_ramp(emitter, m)
		total += n.amount
	rep.check("each emitter has its own ParticleProcessMaterial", mats.size() == 2 and mats[0] != mats[1])
	rep.check("turbulence (GPU-only feature) is on for Wisps only",
		mats.size() == 2 and not mats[0].turbulence_enabled and mats[1].turbulence_enabled)
	rep.check("CPUParticles2D has no turbulence property (why Effect B is GPU)",
		not _has_prop("CPUParticles2D", "turbulence_enabled"))
	rep.check("peak count: 60 particles per trail, 120 with 2 trails alive", total == 60 and total * 2 == 120, total)
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


# ---------------------------------------------------------------- property checks

## True when `cls` (or a parent class) declares `prop` as a stored property in this build.
func _has_prop(cls: String, prop: String) -> bool:
	for d: Dictionary in ClassDB.class_get_property_list(cls, false):
		if d["name"] == prop:
			return (int(d["usage"]) & PROPERTY_USAGE_STORAGE) != 0
	return false


func _check_props(label: String, obj: Object, cls: String, want: Dictionary) -> void:
	for prop: String in want:
		if not rep.check("%s.%s is a stored %s property in this build" % [label, prop, cls], _has_prop(cls, prop)):
			continue
		var got: Variant = obj.get(prop)
		rep.check("%s.%s == %s" % [label, prop, want[prop]], _same(got, want[prop]), got)


func _check_curve(emitter: String, m: ParticleProcessMaterial) -> void:
	var ct: CurveTexture = m.scale_curve as CurveTexture
	var want: Array = CURVES[emitter]
	if not rep.check("%s.scale_curve is a CurveTexture with a Curve" % emitter, ct != null and ct.curve != null):
		return
	var c: Curve = ct.curve
	var ok: bool = c.point_count == 2 and _close(c.sample(0.0), want[0]) and _close(c.sample(1.0), want[1])
	rep.check("%s.scale_curve %.1f -> %.1f (2 points)" % [emitter, want[0], want[1]], ok,
		"points %d, sample(0) %.4f, sample(1) %.4f, max_value %.2f" % [c.point_count, c.sample(0.0), c.sample(1.0), c.max_value])


func _check_ramp(emitter: String, m: ParticleProcessMaterial) -> void:
	var gt: GradientTexture1D = m.color_ramp as GradientTexture1D
	var want: Array = RAMPS[emitter]
	if not rep.check("%s.color_ramp is a GradientTexture1D with a Gradient" % emitter, gt != null and gt.gradient != null):
		return
	var g: Gradient = gt.gradient
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


func _check_texture(emitter: String, n: GPUParticles2D) -> void:
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
	rep.check("%s.texture: soft dot 32 x 32, radial, white -> transparent (as Effect A)" % emitter,
		t.width == 32 and t.height == 32 and t.fill == GradientTexture2D.FILL_RADIAL and all_white
		and _close(first_a, 1.0) and _close(last_a, 0.0),
		"%dx%d fill %d, alpha first %.2f last %.2f, white %s" % [t.width, t.height, t.fill, first_a, last_a, all_white])


func _check_material(emitter: String, n: GPUParticles2D) -> void:
	var m: CanvasItemMaterial = n.material as CanvasItemMaterial
	rep.check("%s.material is CanvasItemMaterial, blend_mode Mix (0), not additive (failure 6)" % emitter,
		m != null and m.blend_mode == CanvasItemMaterial.BLEND_MODE_MIX,
		("%s blend %d" % [m.get_class(), m.blend_mode]) if m != null else (n.material.get_class() if n.material != null else "null"))


# ---------------------------------------------------------------- comparison

func _close(a: float, b: float) -> bool:
	return absf(a - b) <= EPS


func _same_color(a: Color, b: Color) -> bool:
	return _close(a.r, b.r) and _close(a.g, b.g) and _close(a.b, b.b) and _close(a.a, b.a)


func _same(got: Variant, want: Variant) -> bool:
	match typeof(want):
		TYPE_BOOL:
			return typeof(got) == TYPE_BOOL and got == want
		TYPE_INT:
			return typeof(got) == TYPE_INT and got == want
		TYPE_FLOAT:
			return typeof(got) == TYPE_FLOAT and _close(got, want)
		TYPE_VECTOR3:
			return typeof(got) == TYPE_VECTOR3 and _close(got.x, want.x) and _close(got.y, want.y) and _close(got.z, want.z)
		TYPE_RECT2:
			return typeof(got) == TYPE_RECT2 and _close(got.position.x, want.position.x) \
				and _close(got.position.y, want.position.y) and _close(got.size.x, want.size.x) \
				and _close(got.size.y, want.size.y)
	return got == want
