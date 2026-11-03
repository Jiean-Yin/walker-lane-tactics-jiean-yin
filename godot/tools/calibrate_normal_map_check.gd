extends SceneTree
## Calibrates godot/tests/normal_map_check.gd on a known-good pair (Assignment 5, Step 3):
## the Hessian 380 _nor_gl file should come out low with directx = false and near 2 with directx = true,
## and the _nor_dx file the other way round. Decodes the source files, not the imported textures.
##   "$GODOT" --headless --path godot --script res://tools/calibrate_normal_map_check.gd

const Check = preload("res://tests/normal_map_check.gd")
const DIR: String = "res://assets/textures/hessian_380/"
const FILES: Array[String] = ["hessian_380_nor_gl_1k.png", "hessian_380_nor_dx_1k.png"]


func _init() -> void:
	for f: String in FILES:
		var img: Image = Image.load_from_file(ProjectSettings.globalize_path(DIR + f))
		if img == null:
			print("FAIL  could not decode %s" % f)
			quit(1)
			return
		print("%s  %d x %d, format %d: curl_ratio(directx=false) = %.4f, curl_ratio(directx=true) = %.4f" % [
			f, img.get_width(), img.get_height(), img.get_format(),
			Check.curl_ratio(img, false), Check.curl_ratio(img, true)])
	quit(0)
