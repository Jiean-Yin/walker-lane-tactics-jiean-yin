extends SceneTree
## Contact sheet of strip frames for reading (not a test, not gameplay): crops each frame around a point and
## scales it with nearest-neighbour, so a ~60 px effect is readable. Writes one PNG.
## usage: "$GODOT" --headless --path godot --script res://tools/strip_sheet.gd -- <frame dir> <out.png> <cx> <cy> <half> <scale> <cols> <frame> <frame> ...
func _init() -> void:
	var a := OS.get_cmdline_user_args()
	var dir: String = a[0]; var out: String = a[1]
	var cx := int(a[2]); var cy := int(a[3]); var half := int(a[4]); var sc := int(a[5]); var cols := int(a[6])
	var frames := a.slice(7)
	var cell := half * 2 * sc
	var rows := int(ceil(frames.size() / float(cols)))
	var sheet := Image.create(cols * cell + (cols - 1) * 4, rows * cell + (rows - 1) * 4, false, Image.FORMAT_RGB8)
	sheet.fill(Color.WHITE)
	for i in frames.size():
		var img := Image.load_from_file("%s/frame%08d.png" % [dir, int(frames[i])])
		img.convert(Image.FORMAT_RGB8)
		var r := Rect2i(cx - half, cy - half, half * 2, half * 2).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
		var crop := Image.create(half * 2, half * 2, false, Image.FORMAT_RGB8)
		crop.fill(Color.BLACK)
		crop.blit_rect(img, r, r.position - Vector2i(cx - half, cy - half))
		crop.resize(cell, cell, Image.INTERPOLATE_NEAREST)
		sheet.blit_rect(crop, Rect2i(0, 0, cell, cell), Vector2i((i % cols) * (cell + 4), (i / cols) * (cell + 4)))
	sheet.save_png(out)
	print("saved ", out, " ", sheet.get_size())
	quit()
