extends SceneTree
func _init() -> void:
	var s: Node = (load("res://hint/hint_experiment.tscn") as PackedScene).instantiate()
	root.add_child(s)
	var sh := Shader.new()
	sh.code = "shader_type spatial;\nrender_mode unshaded;\nvoid fragment() { ALBEDO = vec3(0.5); }\n"
	var m := ShaderMaterial.new()
	m.shader = sh
	(s.get_node("QuadA_source_color") as MeshInstance3D).set_surface_override_material(0, m)
	for i in 4:
		await process_frame
	await RenderingServer.frame_post_draw
	var img: Image = root.get_texture().get_image()
	print("constant ALBEDO 0.5 on screen: ", img.get_pixel(640, 234).r8, "  (128 = written as stored, 188 = encoded as linear)")
	s.free()
	quit()
