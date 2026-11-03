extends SceneTree
func _init() -> void:
	print("Environment.BG_COLOR=", Environment.BG_COLOR, " AMBIENT_SOURCE_COLOR=", Environment.AMBIENT_SOURCE_COLOR, " TONE_MAPPER_LINEAR=", Environment.TONE_MAPPER_LINEAR)
	print("Camera3D.PROJECTION_ORTHOGONAL=", Camera3D.PROJECTION_ORTHOGONAL, " Image.FORMAT_RGB8=", Image.FORMAT_RGB8, " FORMAT_L8=", Image.FORMAT_L8, " FORMAT_RGBA8=", Image.FORMAT_RGBA8)
	print("TYPE_BOOL=", TYPE_BOOL, " TYPE_FLOAT=", TYPE_FLOAT, " TYPE_COLOR=", TYPE_COLOR, " TYPE_OBJECT=", TYPE_OBJECT, " PROPERTY_HINT_RANGE=", PROPERTY_HINT_RANGE, " PROPERTY_HINT_RESOURCE_TYPE=", PROPERTY_HINT_RESOURCE_TYPE)
	var total := 0
	for p in ["res://assets/textures/hessian_380/hessian_380_diff_1k.jpg", "res://assets/textures/hessian_380/hessian_380_rough_1k.png", "res://assets/textures/hessian_380/hessian_380_nor_gl_1k.png", "res://assets/textures/hessian_380/hessian_380_nor_dx_1k.png", "res://assets/textures/hint_experiment/hint_greys.png"]:
		var t: Texture2D = load(p)
		var img: Image = t.get_image()
		var n: int = img.get_data().size()
		if not p.ends_with("nor_dx_1k.png") and not p.ends_with("hint_greys.png"):
			total += n
		print(p.get_file(), ": imported format ", img.get_format(), " (", img.get_format_name() if img.has_method("get_format_name") else "", "), mipmaps ", img.has_mipmaps(), ", compressed ", img.is_compressed(), ", data bytes ", n)
	print("three bound linen textures, data bytes total: ", total)
	quit()
