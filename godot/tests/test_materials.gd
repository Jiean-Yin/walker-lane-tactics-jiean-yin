extends SceneTree
## Headless audit test for the A5 materials (CHANGE-BRIEF.md section 3 "Hint experiment" and section 4).
## Pins the tables in godot/MATERIALS.md.
##   ./scripts/run-test.sh test_materials.gd 60
##
## Checks, in order:
##   1. shaders: the uniform list from get_shader_uniform_list() (names and types), each sampler's hints and each
##      default value read from the .gdshader source text (the uniform list does not carry them);
##   2. materials: the shader each references, every uniform value it sets, every texture it binds;
##   3. import settings of every bound texture (and the never-bound _nor_dx), read with ConfigFile;
##   4. scenes: which node carries which material, the lights, and the environment values that change the look;
##   5. normal maps: curl_ratio under both conventions (normal_map_check.gd), on the decoded source files.
##
## What this does NOT show: anything on screen. The headless dummy renderer draws nothing, so the look of the cloth,
## the lamp highlight, the depth of the threads and the hint-experiment pixel values are human / windowed checks.

const Report = preload("res://tests/test_report.gd")
const NormalCheck = preload("res://tests/normal_map_check.gd")

const LINEN_SHADER: String = "res://shaders/linen_square.gdshader"
const HINT_SHADER: String = "res://shaders/hint_experiment.gdshader"
const TEX_DIR: String = "res://assets/textures/hessian_380/"
const DIFF: String = TEX_DIR + "hessian_380_diff_1k.jpg"
const ROUGH: String = TEX_DIR + "hessian_380_rough_1k.png"
const NOR_GL: String = TEX_DIR + "hessian_380_nor_gl_1k.png"
const NOR_DX: String = TEX_DIR + "hessian_380_nor_dx_1k.png"
const GREYS: String = "res://assets/textures/hint_experiment/hint_greys.png"
const DIORAMA: String = "res://diorama/asset_diorama.tscn"
const HINT_SCENE: String = "res://hint/hint_experiment.tscn"

const COLOR_TOL: float = 0.5 / 255.0
const FLOAT_TOL: float = 1e-5

## Variant types as get_shader_uniform_list() reports them.
const T_BOOL: int = TYPE_BOOL      # 1
const T_FLOAT: int = TYPE_FLOAT    # 3
const T_COLOR: int = TYPE_COLOR    # 20 (vec4)
const T_OBJECT: int = TYPE_OBJECT  # 24 (sampler2D)

## Per shader: uniform -> {type, hints (as written, order kept), default (source text, "" for samplers)}.
const SHADERS: Dictionary = {
	LINEN_SHADER: {
		"albedo_tex": {"type": T_OBJECT, "hints": "source_color, filter_linear_mipmap, repeat_enable", "default": ""},
		"tint": {"type": T_COLOR, "hints": "source_color", "default": "vec4(1.0)"},
		"uv_scale": {"type": T_FLOAT, "hints": "hint_range(0.5, 8.0, 0.05)", "default": "3.65"},
		"roughness_tex": {"type": T_OBJECT, "hints": "filter_linear_mipmap, repeat_enable", "default": ""},
		"roughness_scale": {"type": T_FLOAT, "hints": "hint_range(0.0, 1.0)", "default": "1.0"},
		"normal_tex": {"type": T_OBJECT, "hints": "hint_normal, filter_linear_mipmap, repeat_enable", "default": ""},
		"normal_strength": {"type": T_FLOAT, "hints": "hint_range(0.0, 2.0)", "default": "1.0"},
	},
	HINT_SHADER: {
		"grey_srgb": {"type": T_OBJECT, "hints": "source_color, filter_nearest", "default": ""},
		"grey_raw": {"type": T_OBJECT, "hints": "filter_nearest", "default": ""},
		"use_srgb": {"type": T_BOOL, "hints": "", "default": "true"},
	},
}

## Per material: shader, values it sets (null = not set, the shader default applies), textures it binds.
const MATERIALS: Dictionary = {
	"res://materials/linen_light.tres": {
		"shader": LINEN_SHADER,
		"values": {"tint": "FFFFFF", "normal_strength": 1.0, "uv_scale": null, "roughness_scale": null},
		"textures": {"albedo_tex": DIFF, "roughness_tex": ROUGH, "normal_tex": NOR_GL},
	},
	"res://materials/linen_dark.tres": {
		"shader": LINEN_SHADER,
		"values": {"tint": "9A7F55", "normal_strength": 1.5, "uv_scale": null, "roughness_scale": null},
		"textures": {"albedo_tex": DIFF, "roughness_tex": ROUGH, "normal_tex": NOR_GL},
	},
	"res://materials/hint_srgb.tres": {
		"shader": HINT_SHADER,
		"values": {"use_srgb": true},
		"textures": {"grey_srgb": GREYS, "grey_raw": GREYS},
	},
	"res://materials/hint_raw.tres": {
		"shader": HINT_SHADER,
		"values": {"use_srgb": false},
		"textures": {"grey_srgb": GREYS, "grey_raw": GREYS},
	},
}

## CHANGE-BRIEF section 4 texture table: compress/mode, compress/normal_map, mipmaps/generate.
const IMPORTS: Dictionary = {
	DIFF: [0, 2, true],
	ROUGH: [0, 2, true],
	NOR_GL: [0, 1, true],
	NOR_DX: [0, 1, false],
	GREYS: [0, 2, false],
}

var rep: Report
var measured: Dictionary = {}


func _initialize() -> void:
	_run()


func _run() -> void:
	rep = Report.new("test_materials")
	for path: String in SHADERS.keys():
		_check_shader(path)
	_check_materials()
	_check_imports()
	await _check_diorama()
	await _check_hint_scene()
	_check_normal_maps()
	quit(rep.finish({"measured": measured}))


# ---------------------------------------------------------------- 1. shaders

## Parses "uniform <type> <name> [: hints] [= default];" lines. Returns name -> {type_name, hints, default}.
func _parse_uniforms(src: String) -> Dictionary:
	var re := RegEx.new()
	re.compile("(?m)^\\s*uniform\\s+(\\w+)\\s+(\\w+)\\s*(?::\\s*([^=;]*?))?\\s*(?:=\\s*([^;]*?))?\\s*;")
	var out: Dictionary = {}
	for m: RegExMatch in re.search_all(src):
		out[m.get_string(2)] = {"type_name": m.get_string(1), "hints": m.get_string(3).strip_edges(),
			"default": m.get_string(4).strip_edges()}
	return out


func _check_shader(path: String) -> void:
	var spec: Dictionary = SHADERS[path]
	var sh: Shader = load(path) as Shader
	if not rep.check("%s loads as a Shader" % path, sh != null):
		return
	var src: String = FileAccess.get_file_as_string(path)
	rep.check("%s: source text read" % path, not src.is_empty(), "%d chars" % src.length())

	# Uniform list from the engine (group headers have usage GROUP/SUBGROUP and are skipped).
	var listed: Dictionary = {}
	for u: Dictionary in sh.get_shader_uniform_list():
		if int(u["usage"]) & (PROPERTY_USAGE_GROUP | PROPERTY_USAGE_SUBGROUP | PROPERTY_USAGE_CATEGORY):
			continue
		listed[String(u["name"])] = int(u["type"])
	measured[path + " uniform list"] = listed
	rep.check("%s: get_shader_uniform_list() names are exactly %s" % [path, spec.keys()],
		_same_set(listed.keys(), spec.keys()), "listed %s" % [listed.keys()])
	for n: String in spec.keys():
		var want: int = spec[n]["type"]
		rep.check("%s: uniform %s has type %d" % [path, n, want], listed.get(n, -1) == want,
			"listed type %s" % listed.get(n, "missing"))

	# Hints and defaults from the source text.
	var parsed: Dictionary = _parse_uniforms(src)
	measured[path + " source uniforms"] = parsed
	rep.check("%s: source declares exactly %s" % [path, spec.keys()], _same_set(parsed.keys(), spec.keys()),
		"source %s" % [parsed.keys()])
	for n: String in spec.keys():
		var p: Dictionary = parsed.get(n, {})
		var want: Dictionary = spec[n]
		rep.check("%s: %s hints are \"%s\"" % [path, n, want["hints"]], p.get("hints", "<missing>") == want["hints"],
			"source \"%s\"" % p.get("hints", "<missing>"))
		if want["type"] != T_OBJECT:
			rep.check("%s: %s default is %s" % [path, n, want["default"]],
				p.get("default", "<missing>") == want["default"], "source \"%s\"" % p.get("default", "<missing>"))

	# Colour sampler vs data samplers (failure case 6): source_color only on colour textures.
	for n: String in spec.keys():
		if spec[n]["type"] != T_OBJECT:
			continue
		var hints: String = parsed.get(n, {}).get("hints", "")
		var is_colour: bool = n in ["albedo_tex", "grey_srgb"]
		rep.check("%s: %s %s source_color" % [path, n, "has" if is_colour else "has no"],
			("source_color" in hints) == is_colour, "hints \"%s\"" % hints)
	rep.check("%s: does not use TIME" % path, not RegEx.create_from_string("\\bTIME\\b").search(src))


# ---------------------------------------------------------------- 2. materials

func _check_materials() -> void:
	var linen_shaders: Array[Shader] = []
	for mpath: String in MATERIALS.keys():
		var spec: Dictionary = MATERIALS[mpath]
		var mat: ShaderMaterial = load(mpath) as ShaderMaterial
		if not rep.check("%s loads as a ShaderMaterial" % mpath, mat != null):
			continue
		var sp: String = mat.shader.resource_path if mat.shader != null else "<none>"
		rep.check("%s: shader is %s" % [mpath, spec["shader"]], sp == spec["shader"], sp)
		if spec["shader"] == LINEN_SHADER and mat.shader != null:
			linen_shaders.append(mat.shader)
		var vals: Dictionary = spec["values"]
		for n: String in vals.keys():
			var got: Variant = mat.get_shader_parameter(n)
			var want: Variant = vals[n]
			var ok: bool
			if want == null:
				ok = got == null
			elif want is String:
				ok = got is Color and _color_close(got as Color, Color.html(want as String))
			elif want is float:
				ok = (got is float or got is int) and absf(float(got) - float(want)) < FLOAT_TOL
			else:
				ok = got == want
			rep.check("%s: %s = %s" % [mpath, n, "not set (shader default)" if want == null else str(want)], ok,
				"material holds %s" % [_fmt(got)])
		var texs: Dictionary = spec["textures"]
		for n: String in texs.keys():
			var t: Variant = mat.get_shader_parameter(n)
			var tp: String = (t as Resource).resource_path if t is Resource else "<none>"
			rep.check("%s: %s binds %s" % [mpath, n, texs[n].get_file()], tp == texs[n], tp)
		# Every parameter the material stores must be a uniform of its shader (failure case 8, renamed uniform).
		var stored: Array[String] = []
		for prop: Dictionary in mat.get_property_list():
			var pn: String = prop["name"]
			if pn.begins_with("shader_parameter/") and mat.get(pn) != null:
				stored.append(pn.trim_prefix("shader_parameter/"))
		var unknown: Array[String] = []
		for n: String in stored:
			if not SHADERS[spec["shader"]].has(n):
				unknown.append(n)
		rep.check("%s: every stored parameter is a shader uniform" % mpath, unknown.is_empty(),
			"stored %s" % [stored])
		var dx_bound: bool = false
		for n: String in stored:
			var v: Variant = mat.get_shader_parameter(n)
			if v is Resource and (v as Resource).resource_path == NOR_DX:
				dx_bound = true
		rep.check("%s: never binds the DirectX normal map" % mpath, not dx_bound)
	rep.check("both linen materials reference %s" % LINEN_SHADER, linen_shaders.size() == 2
		and linen_shaders[0].resource_path == LINEN_SHADER and linen_shaders[1].resource_path == LINEN_SHADER)
	rep.check("both linen materials share one Shader object (resource cache)", linen_shaders.size() == 2
		and linen_shaders[0] == linen_shaders[1])
	var a: Resource = load("res://materials/linen_light.tres")
	var b: Resource = load("res://materials/linen_dark.tres")
	rep.check("the two linen materials are different objects", a != b)


# ---------------------------------------------------------------- 3. import settings

func _check_imports() -> void:
	for tpath: String in IMPORTS.keys():
		var want: Array = IMPORTS[tpath]
		var cf := ConfigFile.new()
		var err: Error = cf.load(tpath + ".import")
		if not rep.check("%s.import parses with ConfigFile" % tpath.get_file(), err == OK, "error %d" % err):
			continue
		var mode: int = int(cf.get_value("params", "compress/mode", -1))
		var nm: int = int(cf.get_value("params", "compress/normal_map", -1))
		var mip: bool = bool(cf.get_value("params", "mipmaps/generate", false))
		measured[tpath.get_file() + " import"] = {"compress/mode": mode, "compress/normal_map": nm,
			"mipmaps/generate": mip, "importer": cf.get_value("remap", "importer", ""),
			"source_file": cf.get_value("deps", "source_file", "")}
		rep.check("%s: compress/mode = %d" % [tpath.get_file(), want[0]], mode == want[0], "file %d" % mode)
		rep.check("%s: compress/normal_map = %d" % [tpath.get_file(), want[1]], nm == want[1], "file %d" % nm)
		rep.check("%s: mipmaps/generate = %s" % [tpath.get_file(), want[2]], mip == want[2], "file %s" % mip)
		rep.check("%s: source_file is the texture itself" % tpath.get_file(),
			cf.get_value("deps", "source_file", "") == tpath)
		var tex: Texture2D = load(tpath) as Texture2D
		rep.check("%s loads as a Texture2D" % tpath.get_file(), tex != null,
			"" if tex == null else "%d x %d" % [tex.get_width(), tex.get_height()])


# ---------------------------------------------------------------- 4. scenes

func _lights(node: Node, out: Array[Light3D]) -> Array[Light3D]:
	if node is Light3D:
		out.append(node as Light3D)
	for c: Node in node.get_children():
		_lights(c, out)
	return out


func _env_of(root: Node) -> Environment:
	var we: WorldEnvironment = root.get_node_or_null("WorldEnvironment") as WorldEnvironment
	return we.environment if we != null else null


func _check_diorama() -> void:
	var ps: PackedScene = load(DIORAMA) as PackedScene
	if not rep.check("%s loads" % DIORAMA, ps != null):
		return
	var root: Node = ps.instantiate()
	get_root().add_child(root)
	await process_frame
	var mats: Array[Material] = []
	for pair: Array in [["LinenSquareLight", "res://materials/linen_light.tres"],
			["LinenSquareDark", "res://materials/linen_dark.tres"]]:
		var mi: MeshInstance3D = root.get_node_or_null(pair[0]) as MeshInstance3D
		if not rep.check("diorama: %s is a MeshInstance3D" % pair[0], mi != null):
			continue
		var pm: PlaneMesh = mi.mesh as PlaneMesh
		rep.check("diorama: %s mesh is a 1 x 1 m PlaneMesh" % pair[0], pm != null and pm.size == Vector2(1, 1),
			"" if pm == null else str(pm.size))
		var m: Material = mi.get_surface_override_material(0)
		mats.append(m)
		rep.check("diorama: %s surface override 0 is %s" % [pair[0], pair[1].get_file()],
			m != null and m.resource_path == pair[1], "" if m == null else m.resource_path)
		rep.check("diorama: %s has no material_override (would hide the surface one)" % pair[0],
			mi.material_override == null)
		measured["diorama " + pair[0] + " position"] = str(mi.position)
	rep.check("diorama: the two tiles hold different materials", mats.size() == 2 and mats[0] != mats[1])

	var lights: Array[Light3D] = _lights(root, [])
	rep.check("diorama: exactly one Light3D", lights.size() == 1, "%d" % lights.size())
	if lights.size() == 1:
		var l: Light3D = lights[0]
		measured["diorama lamp"] = {"class": l.get_class(), "energy": l.light_energy, "color": l.light_color.to_html(false),
			"shadow": l.shadow_enabled, "rotation": str(l.rotation)}
		rep.check("diorama: the light is a DirectionalLight3D named Lamp", l is DirectionalLight3D and l.name == "Lamp")
		rep.check("diorama: Lamp energy 1.0 (default)", is_equal_approx(l.light_energy, 1.0), "%.3f" % l.light_energy)
		rep.check("diorama: Lamp colour (1, 0.92, 0.8)", _color_close(l.light_color, Color(1, 0.92, 0.8)),
			l.light_color.to_html(false))
		rep.check("diorama: Lamp shadows on", l.shadow_enabled)
	var env: Environment = _env_of(root)
	if rep.check("diorama: WorldEnvironment has an Environment", env != null):
		_record_env("diorama", env)
		rep.check("diorama: background Color (1)", env.background_mode == Environment.BG_COLOR, "%d" % env.background_mode)
		rep.check("diorama: ambient source Color (2)", env.ambient_light_source == Environment.AMBIENT_SOURCE_COLOR,
			"%d" % env.ambient_light_source)
		rep.check("diorama: ambient energy 0.35", is_equal_approx(env.ambient_light_energy, 0.35),
			"%.3f" % env.ambient_light_energy)
		rep.check("diorama: ambient colour (1, 0.95, 0.88)",
			_color_close(env.ambient_light_color, Color(1, 0.95, 0.88)), env.ambient_light_color.to_html(false))
		rep.check("diorama: tonemap Linear (0), not set in the scene", env.tonemap_mode == Environment.TONE_MAPPER_LINEAR,
			"%d" % env.tonemap_mode)
		rep.check("diorama: tonemap exposure 1.0, not set in the scene", is_equal_approx(env.tonemap_exposure, 1.0),
			"%.3f" % env.tonemap_exposure)
		rep.check("diorama: glow, fog and adjustments off", not env.glow_enabled and not env.fog_enabled
			and not env.adjustment_enabled)
	root.queue_free()
	await process_frame


func _check_hint_scene() -> void:
	var ps: PackedScene = load(HINT_SCENE) as PackedScene
	if not rep.check("%s loads" % HINT_SCENE, ps != null):
		return
	var root: Node = ps.instantiate()
	get_root().add_child(root)
	await process_frame
	var mats: Array[Material] = []
	for pair: Array in [["QuadA_source_color", "res://materials/hint_srgb.tres"],
			["QuadB_no_hint", "res://materials/hint_raw.tres"]]:
		var mi: MeshInstance3D = root.get_node_or_null(pair[0]) as MeshInstance3D
		if not rep.check("hint scene: %s is a MeshInstance3D" % pair[0], mi != null):
			continue
		var m: Material = mi.get_surface_override_material(0)
		mats.append(m)
		rep.check("hint scene: %s surface override 0 is %s" % [pair[0], pair[1].get_file()],
			m != null and m.resource_path == pair[1], "" if m == null else m.resource_path)
	rep.check("hint scene: the two quads hold different materials", mats.size() == 2 and mats[0] != mats[1])
	var lights: Array[Light3D] = _lights(root, [])
	rep.check("hint scene: no Light3D (both materials are unshaded)", lights.is_empty(), "%d" % lights.size())
	var env: Environment = _env_of(root)
	if rep.check("hint scene: WorldEnvironment has an Environment", env != null):
		_record_env("hint scene", env)
		rep.check("hint scene: tonemap Linear (0)", env.tonemap_mode == Environment.TONE_MAPPER_LINEAR,
			"%d" % env.tonemap_mode)
		rep.check("hint scene: exposure 1.0", is_equal_approx(env.tonemap_exposure, 1.0), "%.3f" % env.tonemap_exposure)
		rep.check("hint scene: glow, fog and adjustments off", not env.glow_enabled and not env.fog_enabled
			and not env.adjustment_enabled)
		rep.check("hint scene: background Color, black", env.background_mode == Environment.BG_COLOR
			and _color_close(env.background_color, Color.BLACK))
	root.queue_free()
	await process_frame


func _record_env(label: String, env: Environment) -> void:
	measured[label + " environment"] = {"background_mode": env.background_mode,
		"background_color": env.background_color.to_html(false), "ambient_source": env.ambient_light_source,
		"ambient_color": env.ambient_light_color.to_html(false), "ambient_energy": env.ambient_light_energy,
		"reflected_source": env.reflected_light_source, "tonemap_mode": env.tonemap_mode,
		"tonemap_exposure": env.tonemap_exposure, "tonemap_white": env.tonemap_white, "glow": env.glow_enabled,
		"fog": env.fog_enabled, "adjustments": env.adjustment_enabled}
	print("INFO  %s environment: %s" % [label, measured[label + " environment"]])


# ---------------------------------------------------------------- 5. normal maps

func _check_normal_maps() -> void:
	var ratios: Dictionary = {}
	for f: String in [NOR_GL, NOR_DX]:
		var img: Image = Image.load_from_file(ProjectSettings.globalize_path(f))
		if not rep.check("%s decodes with Image.load_from_file" % f.get_file(), img != null and not img.is_empty()):
			continue
		var gl: float = NormalCheck.curl_ratio(img, false)
		var dx: float = NormalCheck.curl_ratio(img, true)
		ratios[f] = [gl, dx]
		measured[f.get_file() + " curl_ratio"] = {"directx_false": gl, "directx_true": dx,
			"width": img.get_width(), "height": img.get_height(), "decoded_format": img.get_format()}
		print("INFO  %s  %d x %d, decoded format %d: curl_ratio(directx=false) = %.4f, curl_ratio(directx=true) = %.4f"
			% [f.get_file(), img.get_width(), img.get_height(), img.get_format(), gl, dx])
	if ratios.has(NOR_GL):
		rep.check("nor_gl (the bound map) is lower under the OpenGL convention than under DirectX",
			ratios[NOR_GL][0] < ratios[NOR_GL][1], "%.4f vs %.4f" % ratios[NOR_GL])
	if ratios.has(NOR_DX):
		rep.check("nor_dx (calibration only) is lower under the DirectX convention than under OpenGL",
			ratios[NOR_DX][1] < ratios[NOR_DX][0], "%.4f vs %.4f" % ratios[NOR_DX])


# ---------------------------------------------------------------- helpers

func _same_set(a: Array, b: Array) -> bool:
	if a.size() != b.size():
		return false
	for x: Variant in a:
		if not b.has(x):
			return false
	return true


func _color_close(a: Color, b: Color) -> bool:
	return absf(a.r - b.r) <= COLOR_TOL and absf(a.g - b.g) <= COLOR_TOL and absf(a.b - b.b) <= COLOR_TOL \
		and absf(a.a - b.a) <= COLOR_TOL


func _fmt(v: Variant) -> String:
	if v == null:
		return "null"
	if v is Color:
		return "#" + (v as Color).to_html(false).to_upper()
	return str(v)
