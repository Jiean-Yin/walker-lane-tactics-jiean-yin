extends SceneTree
## A7 read-back for the cycle clip `wave` on GoalFlag/FlagSprite (CHANGE-BRIEF §2, §3, §8).
## ./scripts/run-test.sh test_flag_readback.gd 60
##
## Reads the scene godot/game/goal_flag.tscn and the clip godot/animations/wave.tres back and
## compares them with the brief: the sheet slicing, every frame key inside the sheet, discrete
## updates on both tracks, key times / step / length / loop mode, the seam rule and the
## registration fix. Key times are 32-bit floats, so every time is compared within half a frame
## period of the cycle (0.0625 s), never with ==. track_problems() is a helper written here, not a
## Godot method: it lists every track whose node or property does not resolve.
##
## A short live part adds the scene to the tree and lets autoplay run for 1.5 s of process frames:
## the player must play `wave` from the scene alone, and every shown cell must keep the pole still.
## This test only reads; it never sets frame, offset or the player.

const Report = preload("res://tests/test_report.gd")

const SCENE_PATH: String = "res://game/goal_flag.tscn"
const CLIP_PATH: String = "res://animations/wave.tres"
const SHEET_PATH: String = "res://assets/art/flag/flag_red.png"

# ---- From CHANGE-BRIEF §2 (the sheet) and §3 (the cycle spec), not from the image.
const SHEET_SIZE: Vector2i = Vector2i(500, 249)
const CELL_SIZE: Vector2i = Vector2i(125, 249)
const HFRAMES: int = 4
const VFRAMES: int = 1
const FRAME_ORDER: Array[int] = [0, 1, 2, 3]
const FPS: float = 8.0
const STEP: float = 1.0 / FPS                      # 0.125
const LENGTH: float = 4 * STEP                     # 4 key intervals = 0.5
const TOL: float = STEP / 2.0                      # half a frame period
const FLAG_SCALE: float = 0.36
## Registration fix (§2): offset.x per frame key, source px.
const OFFSET_X: Array[float] = [0.0, -4.0, -2.0, 1.0]
## Pole's left edge inside cells 0-3, measured (§2, ATTRIBUTION.md). Pole x + offset.x must be equal.
const POLE_X: Array[int] = [4, 8, 6, 3]

const LIVE_FRAMES: int = 90   # 1.5 s at 60 fps = 3 loops


func _initialize() -> void:
	_run()


func _approx(a: float, b: float) -> bool:
	return absf(a - b) <= TOL


## Not a Godot method. Every track whose node or property does not resolve, as "track i: reason".
func track_problems(anim: Animation, root: Node) -> Array[String]:
	var out: Array[String] = []
	for i: int in anim.get_track_count():
		var path: NodePath = anim.track_get_path(i)
		var node_path: NodePath = NodePath(String(path).get_slice(":", 0))
		var node: Node = root.get_node_or_null(node_path)
		if node == null:
			out.append("track %d: node '%s' not found under '%s'" % [i, node_path, root.name])
			continue
		var prop: String = path.get_concatenated_subnames()
		if prop == "":
			out.append("track %d: no property in '%s'" % [i, path])
			continue
		var base: String = prop.get_slice(":", 0)
		var found: bool = false
		for p: Dictionary in node.get_property_list():
			if p["name"] == base:
				found = true
				break
		if not found:
			out.append("track %d: %s has no property '%s'" % [i, node.get_class(), base])
		elif node.get_indexed(NodePath(prop)) == null:
			out.append("track %d: '%s' reads back null" % [i, prop])
	return out


func _keys(anim: Animation, t: int) -> Array:
	var out: Array = []
	for k: int in anim.track_get_key_count(t):
		out.append([anim.track_get_key_time(t, k), anim.track_get_key_value(t, k)])
	return out


func _run() -> void:
	var rep: Report = Report.new("test_flag_readback")
	var extra: Dictionary = {}

	# ---------------------------------------------------------------- load
	var packed: PackedScene = load(SCENE_PATH) as PackedScene
	var clip_file: Animation = load(CLIP_PATH) as Animation
	if not rep.check("goal_flag.tscn loads", packed != null, SCENE_PATH) \
			or not rep.check("wave.tres loads as an Animation", clip_file != null, CLIP_PATH):
		quit(rep.finish())
		return
	var flag: Node = packed.instantiate()
	rep.check("root is GoalFlag, a Node2D", flag.name == &"GoalFlag" and flag is Node2D,
			"%s %s" % [flag.name, flag.get_class()])
	var sprite: Sprite2D = flag.get_node_or_null("FlagSprite") as Sprite2D
	var player: AnimationPlayer = flag.get_node_or_null("AnimationPlayer") as AnimationPlayer
	if not rep.check("GoalFlag/FlagSprite is a Sprite2D", sprite != null) \
			or not rep.check("GoalFlag/AnimationPlayer is an AnimationPlayer", player != null):
		quit(rep.finish())
		return

	# ---------------------------------------------------------------- sheet slicing (§2)
	var tex: Texture2D = sprite.texture
	rep.check("texture is the downloaded sheet", tex != null and tex.resource_path == SHEET_PATH,
			tex.resource_path if tex != null else "null")
	var tex_size: Vector2i = Vector2i(tex.get_size()) if tex != null else Vector2i.ZERO
	rep.check("sheet is 500 x 249", tex_size == SHEET_SIZE, tex_size)
	rep.check("hframes = 4, vframes = 1", sprite.hframes == HFRAMES and sprite.vframes == VFRAMES,
			"%d x %d" % [sprite.hframes, sprite.vframes])
	var cell: Vector2i = Vector2i(tex_size.x / maxi(sprite.hframes, 1), tex_size.y / maxi(sprite.vframes, 1))
	rep.check("cell is 125 x 249 and the grid divides the sheet exactly",
			cell == CELL_SIZE and tex_size.x % sprite.hframes == 0 and tex_size.y % sprite.vframes == 0, cell)
	rep.check("no region crop (the grid slices the sheet)", not sprite.region_enabled)
	rep.check("FlagSprite scale 0.36", sprite.scale.is_equal_approx(Vector2(FLAG_SCALE, FLAG_SCALE)), sprite.scale)

	# ---------------------------------------------------------------- player set-up (§1, §3)
	rep.check("player has clip 'wave'", player.has_animation(&"wave"), player.get_animation_list())
	var anim: Animation = player.get_animation(&"wave") if player.has_animation(&"wave") else null
	if not rep.check("the player's 'wave' is the resource wave.tres (not built in the scene or code)",
			anim != null and anim.resource_path == CLIP_PATH, anim.resource_path if anim != null else "null"):
		quit(rep.finish())
		return
	rep.check("autoplay = 'wave'", player.autoplay == &"wave", player.autoplay)
	rep.check("callback_mode_process = ANIMATION_CALLBACK_MODE_PROCESS_IDLE",
			player.callback_mode_process == AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_IDLE,
			player.callback_mode_process)
	rep.check("speed_scale = 1", is_equal_approx(player.speed_scale, 1.0), player.speed_scale)
	var anim_root: Node = player.get_node_or_null(player.root_node)
	rep.check("root_node resolves to GoalFlag", anim_root == flag, "%s -> %s" % [player.root_node, anim_root])
	if anim_root == null:
		quit(rep.finish())
		return

	# ---------------------------------------------------------------- tracks resolve
	var problems: Array[String] = track_problems(anim, anim_root)
	rep.check("track_problems() is empty: every track resolves to a real node and property",
			problems.is_empty(), "; ".join(problems))
	rep.check("exactly two tracks", anim.get_track_count() == 2, anim.get_track_count())
	var t_frame: int = anim.find_track(NodePath("FlagSprite:frame"), Animation.TYPE_VALUE)
	var t_off: int = anim.find_track(NodePath("FlagSprite:offset"), Animation.TYPE_VALUE)
	if not rep.check("value track FlagSprite:frame exists", t_frame >= 0, t_frame) \
			or not rep.check("value track FlagSprite:offset exists", t_off >= 0, t_off):
		quit(rep.finish())
		return

	# ---------------------------------------------------------------- clip settings (§3)
	rep.check("step = one frame period at 8 fps (0.125)", _approx(anim.step, STEP) and
			absf(anim.step - STEP) < 1e-6, anim.step)
	rep.check("length = 4 intervals (0.5)", _approx(anim.length, LENGTH), anim.length)
	rep.check("loop_mode = LOOP_LINEAR", anim.loop_mode == Animation.LOOP_LINEAR, anim.loop_mode)
	# value_track_get_update_mode applies to value tracks only (both are, checked above).
	rep.check("frame track uses UPDATE_DISCRETE",
			anim.value_track_get_update_mode(t_frame) == Animation.UPDATE_DISCRETE,
			anim.value_track_get_update_mode(t_frame))
	rep.check("offset track uses UPDATE_DISCRETE",
			anim.value_track_get_update_mode(t_off) == Animation.UPDATE_DISCRETE,
			anim.value_track_get_update_mode(t_off))
	rep.check("both tracks enabled", anim.track_is_enabled(t_frame) and anim.track_is_enabled(t_off))

	# ---------------------------------------------------------------- frame keys
	var fk: Array = _keys(anim, t_frame)
	extra["frame_keys"] = fk
	var n_cells: int = sprite.hframes * sprite.vframes
	var inside: bool = not fk.is_empty()
	var ints: bool = true
	var values: Array[int] = []
	for k: Array in fk:
		ints = ints and typeof(k[1]) == TYPE_INT
		var v: int = int(k[1])
		values.append(v)
		inside = inside and v >= 0 and v < n_cells
	rep.check("every frame key is an int", ints)
	rep.check("every frame key is inside the sheet (0 <= frame < hframes x vframes = %d)" % n_cells,
			inside, values)
	rep.check("frame order 0, 1, 2, 3", values == FRAME_ORDER, values)
	var times_ok: bool = fk.size() == FRAME_ORDER.size()
	var times: Array[float] = []
	for i: int in fk.size():
		times.append(float(fk[i][0]))
		times_ok = times_ok and _approx(float(fk[i][0]), i * STEP)
	rep.check("frame key times 0, 0.125, 0.25, 0.375 (within half a period)", times_ok, times)
	var spacing_ok: bool = true
	for i: int in range(1, times.size()):
		spacing_ok = spacing_ok and _approx(times[i] - times[i - 1], STEP)
	rep.check("frame keys one interval apart", spacing_ok and times.size() > 1)

	# ---------------------------------------------------------------- seam rule (§3)
	var key_at_length: bool = false
	for t: float in times:
		key_at_length = key_at_length or _approx(t, anim.length) or t > anim.length
	rep.check("seam: no frame key at (or past) length", not key_at_length, times)
	rep.check("seam: last frame key is 3, not a repeat of the first frame",
			not values.is_empty() and values[-1] == 3 and values[-1] != values[0], values)
	var tail: float = anim.length - (times[-1] if not times.is_empty() else 0.0)
	rep.check("seam: last key -> length = one interval (0.125)", _approx(tail, STEP), tail)
	var dup: bool = false
	for i: int in range(1, values.size()):
		dup = dup or values[i] == values[i - 1]
	rep.check("seam: no frame shown for two intervals in a row, wrap included",
			not dup and values.size() > 1 and values[-1] != values[0])

	# ---------------------------------------------------------------- registration fix (§2)
	var ok_: Array = _keys(anim, t_off)
	extra["offset_keys"] = ok_
	var off_times_ok: bool = ok_.size() == fk.size()
	var off_vals_ok: bool = ok_.size() == OFFSET_X.size()
	var pole: Array[float] = []
	for i: int in ok_.size():
		if i < fk.size():
			off_times_ok = off_times_ok and _approx(float(ok_[i][0]), float(fk[i][0]))
		var off: Variant = ok_[i][1]
		if typeof(off) != TYPE_VECTOR2:
			off_vals_ok = false
			continue
		if i < OFFSET_X.size():
			off_vals_ok = off_vals_ok and is_equal_approx(off.x, OFFSET_X[i]) and is_zero_approx(off.y)
		if i < values.size() and values[i] >= 0 and values[i] < POLE_X.size():
			pole.append(POLE_X[values[i]] + off.x)  # guarded: a key outside the sheet fails above, not here
	rep.check("offset keys on the same times as the frame keys", off_times_ok)
	rep.check("offset keys are Vector2(0, 0), (-4, 0), (-2, 0), (+1, 0)", off_vals_ok, ok_)
	var still: bool = pole.size() == FRAME_ORDER.size()
	for p: float in pole:
		still = still and is_equal_approx(p, pole[0])
	rep.check("pole x + offset.x is the same in every keyed cell", still, pole)
	var off_seam: bool = true
	for k: Array in ok_:
		off_seam = off_seam and not _approx(float(k[0]), anim.length)
	rep.check("offset track has no key at length either", off_seam)

	# ---------------------------------------------------------------- live: autoplay on the IDLE tick
	root.add_child(flag)
	var seen: Dictionary = {}
	var drift: Array = []
	for f: int in LIVE_FRAMES:
		await process_frame
		var shown: int = sprite.frame
		seen[shown] = true
		var px: float = POLE_X[shown] + sprite.offset.x if shown >= 0 and shown < POLE_X.size() else NAN
		if not is_equal_approx(px, POLE_X[0] + OFFSET_X[0]):
			drift.append([f, shown, sprite.offset.x])
	rep.check("live: autoplay plays 'wave' with no script call",
			player.is_playing() and player.current_animation == &"wave",
			"%s playing=%s" % [player.current_animation, player.is_playing()])
	rep.check("live: all four cells shown over 1.5 s (it loops)", seen.size() == 4, seen.keys())
	rep.check("live: offset matches the shown cell on every frame (pole still)", drift.is_empty(), drift)
	extra["live_cells_seen"] = seen.keys()

	flag.queue_free()
	quit(rep.finish(extra))
