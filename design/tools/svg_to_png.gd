extends SceneTree
## Rasterize the design-sketch SVGs to PNG (Godot's built-in SVG loader).
## Run: Godot --headless --path godot --script res://../design/tools/svg_to_png.gd
## (or pass absolute folders after "--": -- <dir> [<dir> ...]).

func _init() -> void:
	for dir_path in OS.get_cmdline_user_args():
		var dir := DirAccess.open(dir_path)
		if dir == null:
			push_error("cannot open " + dir_path)
			continue
		for f in dir.get_files():
			if not f.ends_with(".svg"):
				continue
			var src := FileAccess.get_file_as_string(dir_path.path_join(f))
			var img := Image.new()
			var err := img.load_svg_from_string(src, 1.0)
			if err != OK:
				push_error("svg load failed: " + f)
				continue
			img.save_png(dir_path.path_join(f.get_basename() + ".png"))
			print("wrote ", f.get_basename(), ".png ", img.get_size())
	quit()
