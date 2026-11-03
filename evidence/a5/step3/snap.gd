extends SceneTree
func _init() -> void:
	var out: String = OS.get_cmdline_user_args()[0]
	for pair in [["res://diorama/asset_diorama.tscn", "diorama.png"], ["res://hint/hint_experiment.tscn", "hint.png"]]:
		var s: Node = (load(pair[0]) as PackedScene).instantiate()
		root.add_child(s)
		for i in 6:
			await process_frame
		await RenderingServer.frame_post_draw
		var img: Image = root.get_texture().get_image()
		img.save_png(out + "/" + pair[1])
		if pair[1] == "hint.png":
			for y in [img.get_height() / 2 - 126, img.get_height() / 2 + 126]:
				var row: Array = []
				for x in [img.get_width() / 2 - 300, img.get_width() / 2, img.get_width() / 2 + 300]:
					row.append(img.get_pixel(x, y).r8)
				print("hint row y=", y, ": ", row)
		s.free()
	quit()
