extends SceneTree
func _row(img: Image, y: int) -> Array:
	var r: Array = []
	for x in [img.get_width() / 2 - 300, img.get_width() / 2, img.get_width() / 2 + 300]:
		r.append(img.get_pixel(x, y).r8)
	return r
func _init() -> void:
	var s: Node = (load("res://hint/hint_experiment.tscn") as PackedScene).instantiate()
	root.add_child(s)
	var a: ShaderMaterial = s.get_node("QuadA_source_color").get_surface_override_material(0)
	var b: ShaderMaterial = s.get_node("QuadB_no_hint").get_surface_override_material(0)
	print("A use_srgb=", a.get_shader_parameter("use_srgb"), " B use_srgb=", b.get_shader_parameter("use_srgb"), " same material: ", a == b)
	for flip in [false, true]:
		if flip:
			a.set_shader_parameter("use_srgb", false)
			b.set_shader_parameter("use_srgb", true)
		for i in 4:
			await process_frame
		await RenderingServer.frame_post_draw
		var img: Image = root.get_texture().get_image()
		print("swapped=", flip, "  top quad ", _row(img, 234), "  bottom quad ", _row(img, 486))
	var tex: Texture2D = a.get_shader_parameter("grey_srgb")
	print("texture format on GPU path: ", tex.get_image().get_format(), " (4 = RGB8)")
	print("viewport: hdr_2d=", root.use_hdr_2d, " env tonemap=", (s.get_node("WorldEnvironment") as WorldEnvironment).environment.tonemap_mode)
	s.free()
	quit()
