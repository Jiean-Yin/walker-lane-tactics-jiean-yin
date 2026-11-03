extends SceneTree
## Finds where the engine capture (1280 x 720) sits inside the OS screenshot, then compares P1 and P2.
func _init() -> void:
	var base: String = ProjectSettings.globalize_path("res://").path_join("../evidence/a5/captures/").simplify_path()
	var os_img: Image = Image.load_from_file(base + "/os_screenshot.png")
	var eng: Image = Image.load_from_file(base + "/exposed_0.0.png")
	print("os screenshot ", os_img.get_size(), "  engine capture ", eng.get_size())
	var best := Vector2i(-1, -1)
	var best_err := 1e20
	for oy in range(0, os_img.get_height() - 600):
		for ox in range(0, mini(40, os_img.get_width() - 1200)):
			var err := 0.0
			for s in [Vector2i(640, 360), Vector2i(192, 581), Vector2i(1000, 200), Vector2i(300, 650), Vector2i(800, 500)]:
				if s.y + oy >= os_img.get_height() or s.x + ox >= os_img.get_width():
					err += 9.0
					continue
				var a: Color = os_img.get_pixel(s.x + ox, s.y + oy)
				var b: Color = eng.get_pixel(s.x, s.y)
				err += absf(a.r - b.r) + absf(a.g - b.g) + absf(a.b - b.b)
			if err < best_err:
				best_err = err
				best = Vector2i(ox, oy)
	print("best offset ", best, " error ", best_err)
	for p in [Vector2i(192, 581), Vector2i(202, 634)]:
		var q: Vector2i = p + best
		if q.y < os_img.get_height():
			var a: Color = os_img.get_pixel(q.x, q.y)
			var b: Color = eng.get_pixel(p.x, p.y)
			print(p, ": OS screenshot (", a.r8, ", ", a.g8, ", ", b.b8 * 0 + a.b8, ")  engine capture (", b.r8, ", ", b.g8, ", ", b.b8, ")")
		else:
			print(p, ": outside the OS screenshot (the window was smaller than 720 px of content)")
	quit()
