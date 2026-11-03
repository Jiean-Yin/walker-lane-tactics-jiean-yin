extends SceneTree
## Writes the A5 hint-experiment texture (CHANGE-BRIEF §3): a 3 x 1 RGB PNG with greys 64, 128, 192.
## Run from the repository root, then import:
##   "$GODOT" --headless --path godot --script res://tools/write_hint_greys.gd
##   "$GODOT" --headless --path godot --import
## Its import settings (lossless, no mipmaps, no normal-map flag) live in hint_greys.png.import.

const OUT: String = "res://assets/textures/hint_experiment/hint_greys.png"
const GREYS: Array[int] = [64, 128, 192]


func _init() -> void:
	var img: Image = Image.create_empty(GREYS.size(), 1, false, Image.FORMAT_RGB8)
	for x: int in GREYS.size():
		img.set_pixel(x, 0, Color8(GREYS[x], GREYS[x], GREYS[x]))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT.get_base_dir()))
	var err: Error = img.save_png(OUT)
	# Read it back from disk, so the printed values are the file's, not the memory copy's.
	var back: Image = Image.load_from_file(ProjectSettings.globalize_path(OUT))
	var vals: Array[int] = []
	for x: int in back.get_width():
		vals.append(back.get_pixel(x, 0).r8)
	print("wrote %s: error %d, %d x %d, format %d, red values %s" % [OUT, err, back.get_width(), back.get_height(), back.get_format(), vals])
	quit(0 if err == OK and vals == GREYS else 1)
