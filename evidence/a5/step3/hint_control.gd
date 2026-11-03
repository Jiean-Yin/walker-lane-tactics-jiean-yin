extends SceneTree
## Control for MATERIALS.md finding 1: each quad gets its own, separately loaded texture object,
## bound only to the sampler that quad reads. Windowed run; scene files are not changed.
const TEX := "res://assets/textures/hint_experiment/hint_greys.png"
func _row(img: Image, y: int) -> Array:
	var r: Array = []
	for x in [img.get_width() / 2 - 300, img.get_width() / 2, img.get_width() / 2 + 300]:
		r.append(img.get_pixel(x, y).r8)
	return r
func _init() -> void:
	var s: Node = (load("res://hint/hint_experiment.tscn") as PackedScene).instantiate()
	root.add_child(s)
	var sh: Shader = load("res://shaders/hint_experiment.gdshader")
	var t1: Texture2D = ResourceLoader.load(TEX, "", ResourceLoader.CACHE_MODE_IGNORE)
	var t2: Texture2D = ResourceLoader.load(TEX, "", ResourceLoader.CACHE_MODE_IGNORE)
	var a := ShaderMaterial.new(); a.shader = sh; a.set_shader_parameter("use_srgb", true); a.set_shader_parameter("grey_srgb", t1)
	var b := ShaderMaterial.new(); b.shader = sh; b.set_shader_parameter("use_srgb", false); b.set_shader_parameter("grey_raw", t2)
	(s.get_node("QuadA_source_color") as MeshInstance3D).set_surface_override_material(0, a)
	(s.get_node("QuadB_no_hint") as MeshInstance3D).set_surface_override_material(0, b)
	print("separate texture objects: ", t1 != t2, " (ids ", t1.get_rid(), " / ", t2.get_rid(), ")")
	for i in 4:
		await process_frame
	await RenderingServer.frame_post_draw
	var img: Image = root.get_texture().get_image()
	print("control: quad A (source_color, own texture) ", _row(img, 234), "  quad B (no hint, own texture) ", _row(img, 486))
	s.free()
	quit()
