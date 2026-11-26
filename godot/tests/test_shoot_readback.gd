extends SceneTree
## A7 read-back for the committing clip `shoot` on the keyed cutout rig (CHANGE-BRIEF §4, §6, §8).
## ./scripts/run-test.sh test_shoot_readback.gd 60
##
## Reads godot/game/archer_rig.tscn and godot/animations/shoot.tres back and compares them with
## the brief: the rig's nodes, regions and pivots; every track resolving to a real node and
## property (or bone / blend shape, branched on track type); key times at frames 0 / 12 / 33 /
## 40 / 48 within half a frame; key values and transitions from §4's key table; step = 1/60;
## length 0.8; LOOP_NONE; MANUAL callback mode. Key times are 32-bit floats, so every time is
## compared with a tolerance, never ==. track_problems() is a helper written here, not a Godot
## method.
##
## This test only reads. It never plays, stops or advances the rig's AnimationPlayer (that is
## piece.gd's job, CLAUDE.md "One authority"); the motion between keys is sampled from the clip
## with Animation.value_track_interpolate(), which touches no node.

const Report = preload("res://tests/test_report.gd")

const SCENE_PATH: String = "res://game/archer_rig.tscn"
const CLIP_PATH: String = "res://animations/shoot.tres"
const ART_PATH: String = "res://assets/art/archer_draw.png"

# ---- From CHANGE-BRIEF §4 (phase table, key table, rig), not from the files under test.
const FPS: float = 60.0
const STEP: float = 1.0 / FPS
const TOL: float = STEP / 2.0                       # half a frame
const LENGTH_FRAMES: int = 48
const LENGTH: float = LENGTH_FRAMES / FPS           # 0.8
## Phase boundaries: startup, active (release), recovery (impact), bow drop, back to idle.
const KEY_FRAMES: Array[int] = [0, 12, 33, 40, 48]
const ART_SIZE: Vector2i = Vector2i(288, 321)
## The rig's local origin is the art's centre (the point a centred Sprite2D of the image sits on).
const ART_CENTRE: Vector2 = Vector2(144.0, 160.5)
## Sprite part -> region (art px); the part's top-left must sit at the region's own art position.
const REGIONS: Dictionary = {
	"Rig/Lower": Rect2(0, 196, 288, 125),
	"Rig/Upper/UpperSprite": Rect2(0, 0, 204, 204),
	"Rig/Upper/Bow/BowSprite": Rect2(204, 40, 84, 164),
}
## Pivot node -> art position.
const PIVOTS: Dictionary = {
	"Rig/Upper": Vector2(144, 200),   # belt
	"Rig/Upper/Bow": Vector2(236, 120),   # bow hand
}
## Node -> class, exactly (no Bone2D, no AnimatedSprite2D).
const NODE_CLASSES: Dictionary = {
	".": "Node2D",
	"Rig": "Node2D",
	"Rig/Lower": "Sprite2D",
	"Rig/Upper": "Node2D",
	"Rig/Upper/UpperSprite": "Sprite2D",
	"Rig/Upper/Bow": "Node2D",
	"Rig/Upper/Bow/BowSprite": "Sprite2D",
	"AnimationPlayer": "AnimationPlayer",
}
## Key table (§4). Art faces right; positive rotation = clockwise on screen.
## back = -x / negative angle; forward and down = positive angle.
const KEYS_POS: Array[Vector2] = [Vector2(0, 0), Vector2(0, 0), Vector2(-6, 0), Vector2(-6, 0), Vector2(0, 0)]
const KEYS_UPPER_DEG: Array[float] = [0.0, -4.0, 2.0, 2.0, 0.0]
const KEYS_BOW_DEG: Array[float] = [12.0, 0.0, 0.0, 0.0, 20.0]
const ANGLE_TOL: float = 0.0001                     # rad, for values written to 6 digits
## Transition per key (segment to the next): ease in, ease out, hold, ease in-out, last.
const TRANSITIONS: Array[float] = [2.0, 0.5, 1.0, -2.0, 1.0]


func _initialize() -> void:
	_run()


func _approx_t(a: float, b: float) -> bool:
	return absf(a - b) <= TOL


## Not a Godot method. Every track whose target does not resolve, as "track i: reason".
## Branches on track type: value / bezier tracks name a node property; 3D position, rotation and
## scale tracks name a bone of a Skeleton3D (or a Node3D with no subname); blend-shape tracks
## name a blend shape of a MeshInstance3D; method / audio / animation tracks name a node.
func track_problems(anim: Animation, root: Node) -> Array[String]:
	var out: Array[String] = []
	for i: int in anim.get_track_count():
		var path: NodePath = anim.track_get_path(i)
		var node_path: NodePath = NodePath(String(path).get_slice(":", 0))
		var node: Node = root.get_node_or_null(node_path)
		if node == null:
			out.append("track %d: node '%s' not found under '%s'" % [i, node_path, root.name])
			continue
		var sub: String = path.get_concatenated_subnames()
		match anim.track_get_type(i):
			Animation.TYPE_VALUE, Animation.TYPE_BEZIER:
				if sub == "":
					out.append("track %d: no property in '%s'" % [i, path])
					continue
				var base: String = sub.get_slice(":", 0)
				var found: bool = false
				for p: Dictionary in node.get_property_list():
					if p["name"] == base:
						found = true
						break
				if not found:
					out.append("track %d: %s has no property '%s'" % [i, node.get_class(), base])
				elif node.get_indexed(NodePath(sub)) == null:
					out.append("track %d: '%s' reads back null" % [i, sub])
			Animation.TYPE_POSITION_3D, Animation.TYPE_ROTATION_3D, Animation.TYPE_SCALE_3D:
				if sub == "":
					if not node is Node3D:
						out.append("track %d: 3D transform track on %s, not a Node3D" % [i, node.get_class()])
				elif not node is Skeleton3D:
					out.append("track %d: bone '%s' on %s, not a Skeleton3D" % [i, sub, node.get_class()])
				elif (node as Skeleton3D).find_bone(sub) < 0:
					out.append("track %d: skeleton has no bone '%s'" % [i, sub])
			Animation.TYPE_BLEND_SHAPE:
				if not node is MeshInstance3D:
					out.append("track %d: blend shape '%s' on %s, not a MeshInstance3D" % [i, sub, node.get_class()])
				elif (node as MeshInstance3D).find_blend_shape_by_name(StringName(sub)) < 0:
					out.append("track %d: mesh has no blend shape '%s'" % [i, sub])
			_:
				pass  # method / audio / animation tracks: the node resolving is enough
	return out


func _times(anim: Animation, t: int) -> Array[float]:
	var out: Array[float] = []
	for k: int in anim.track_get_key_count(t):
		out.append(anim.track_get_key_time(t, k))
	return out


func _values(anim: Animation, t: int) -> Array:
	var out: Array = []
	for k: int in anim.track_get_key_count(t):
		out.append(anim.track_get_key_value(t, k))
	return out


## Art position of a node under the rig at rest (no rotation in the scene): sum of positions up to Mount.
func _art_pos(mount: Node, node: Node2D) -> Vector2:
	var p: Vector2 = Vector2.ZERO
	var n: Node = node
	while n != null and n != mount and n.name != &"Rig":
		p += (n as Node2D).position
		n = n.get_parent()
	return ART_CENTRE + p


func _run() -> void:
	var rep: Report = Report.new("test_shoot_readback")
	var extra: Dictionary = {}

	# ---------------------------------------------------------------- load
	var packed: PackedScene = load(SCENE_PATH) as PackedScene
	var clip_file: Animation = load(CLIP_PATH) as Animation
	if not rep.check("archer_rig.tscn loads", packed != null, SCENE_PATH) \
			or not rep.check("shoot.tres loads as an Animation", clip_file != null, CLIP_PATH):
		quit(rep.finish())
		return
	var mount: Node = packed.instantiate()
	rep.check("root is Mount", mount.name == &"Mount", mount.name)

	# ---------------------------------------------------------------- rig structure (§4 "Rig")
	var classes_ok: bool = true
	var classes: Array[String] = []
	for p: String in NODE_CLASSES:
		var n: Node = mount.get_node_or_null(p)
		var cls: String = n.get_class() if n != null else "missing"
		classes.append("%s=%s" % [p, cls])
		classes_ok = classes_ok and cls == NODE_CLASSES[p]
	rep.check("rig nodes exist with the brief's classes", classes_ok, ", ".join(classes))
	var banned: Array[String] = []
	var stack: Array[Node] = [mount]
	var n_nodes: int = 0
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		n_nodes += 1
		if n is Bone2D or n is Skeleton2D or n is AnimatedSprite2D or n is AnimationTree:
			banned.append("%s (%s)" % [n.name, n.get_class()])
		stack.append_array(n.get_children())
	rep.check("no Bone2D, Skeleton2D, AnimatedSprite2D or AnimationTree", banned.is_empty(), banned)
	rep.check("exactly the 8 nodes of the brief", n_nodes == NODE_CLASSES.size(), n_nodes)
	if not classes_ok:
		quit(rep.finish())
		return

	var tex_ok: bool = true
	var regions_ok: bool = true
	var placed_ok: bool = true
	var region_detail: Array[String] = []
	for p: String in REGIONS:
		var s: Sprite2D = mount.get_node(p) as Sprite2D
		var r: Rect2 = REGIONS[p]
		tex_ok = tex_ok and s.texture != null and s.texture.resource_path == ART_PATH
		regions_ok = regions_ok and s.region_enabled and s.region_rect.is_equal_approx(r) and not s.centered
		var at: Vector2 = _art_pos(mount, s)
		placed_ok = placed_ok and at.is_equal_approx(r.position)
		region_detail.append("%s region %s at art %s" % [p.get_file(), s.region_rect, at])
	rep.check("every part's texture is archer_draw.png", tex_ok)
	var art: Texture2D = load(ART_PATH) as Texture2D
	rep.check("archer_draw.png is 288 x 321 and every region lies inside it",
			art != null and Vector2i(art.get_size()) == ART_SIZE and REGIONS.values().all(
				func(r: Rect2) -> bool: return Rect2(Vector2.ZERO, Vector2(ART_SIZE)).encloses(r)),
			art.get_size() if art != null else "null")
	rep.check("regions (0,196,288,125), (0,0,204,204), (204,40,84,164), region_enabled, not centred",
			regions_ok, "; ".join(region_detail))
	rep.check("each part sits at its region's own place in the art (rest pose reassembles the image)",
			placed_ok, "; ".join(region_detail))
	var pivot_ok: bool = true
	var pivot_detail: Array[String] = []
	for p: String in PIVOTS:
		var at: Vector2 = _art_pos(mount, mount.get_node(p) as Node2D)
		pivot_ok = pivot_ok and at.is_equal_approx(PIVOTS[p])
		pivot_detail.append("%s at art %s" % [p.get_file(), at])
	rep.check("pivots: Upper at the belt (144, 200), Bow at the bow hand (236, 120)", pivot_ok,
			"; ".join(pivot_detail))
	var rig: Node2D = mount.get_node("Rig") as Node2D
	rep.check("scene rest pose: Rig at (0,0), Upper and Bow unrotated, no scale on keyed nodes",
			rig.position == Vector2.ZERO and is_zero_approx((mount.get_node("Rig/Upper") as Node2D).rotation)
			and is_zero_approx((mount.get_node("Rig/Upper/Bow") as Node2D).rotation)
			and rig.scale == Vector2.ONE)

	# ---------------------------------------------------------------- player set-up (§1, §6)
	var player: AnimationPlayer = mount.get_node("AnimationPlayer") as AnimationPlayer
	rep.check("player has clip 'shoot'", player.has_animation(&"shoot"), player.get_animation_list())
	var anim: Animation = player.get_animation(&"shoot") if player.has_animation(&"shoot") else null
	if not rep.check("the player's 'shoot' is the resource shoot.tres (not built in the scene or code)",
			anim != null and anim.resource_path == CLIP_PATH, anim.resource_path if anim != null else "null"):
		quit(rep.finish())
		return
	rep.check("callback_mode_process = ANIMATION_CALLBACK_MODE_PROCESS_MANUAL",
			player.callback_mode_process == AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL,
			player.callback_mode_process)
	rep.check("no autoplay (piece.gd starts the clip)", player.autoplay == &"", player.autoplay)
	rep.check("speed_scale = 1", is_equal_approx(player.speed_scale, 1.0), player.speed_scale)
	var anim_root: Node = player.get_node_or_null(player.root_node)
	rep.check("root_node resolves to Mount", anim_root == mount, "%s -> %s" % [player.root_node, anim_root])
	if anim_root == null:
		quit(rep.finish())
		return

	# ---------------------------------------------------------------- tracks resolve
	var problems: Array[String] = track_problems(anim, anim_root)
	rep.check("track_problems() is empty: every track resolves to a real node and property, bone or blend shape",
			problems.is_empty(), "; ".join(problems))
	rep.check("exactly three tracks", anim.get_track_count() == 3, anim.get_track_count())
	var t_pos: int = anim.find_track(NodePath("Rig:position"), Animation.TYPE_VALUE)
	var t_up: int = anim.find_track(NodePath("Rig/Upper:rotation"), Animation.TYPE_VALUE)
	var t_bow: int = anim.find_track(NodePath("Rig/Upper/Bow:rotation"), Animation.TYPE_VALUE)
	if not rep.check("value tracks Rig:position, Rig/Upper:rotation, Rig/Upper/Bow:rotation exist",
			t_pos >= 0 and t_up >= 0 and t_bow >= 0, [t_pos, t_up, t_bow]):
		quit(rep.finish())
		return
	var tracks: Array[int] = [t_pos, t_up, t_bow]
	var paths: Array[String] = []
	var no_mount: bool = true
	for i: int in anim.get_track_count():
		var tp: String = String(anim.track_get_path(i))
		paths.append(tp)
		no_mount = no_mount and tp.begins_with("Rig") and not tp.contains("Sprite") and not tp.contains("Lower")
	rep.check("no track keys Mount or a sprite part (placement, facing and art belong to piece.gd)",
			no_mount, paths)
	var types_ok: bool = true
	for i: int in anim.get_track_count():
		types_ok = types_ok and anim.track_get_type(i) == Animation.TYPE_VALUE
	rep.check("no method, audio or animation tracks (all three are value tracks)", types_ok)
	var cont: bool = true
	var linear: bool = true
	var enabled: bool = true
	for t: int in tracks:
		# value_track_get_update_mode applies to value tracks only (all three are, checked above).
		cont = cont and anim.value_track_get_update_mode(t) == Animation.UPDATE_CONTINUOUS
		linear = linear and anim.track_get_interpolation_type(t) == Animation.INTERPOLATION_LINEAR
		enabled = enabled and anim.track_is_enabled(t)
	rep.check("all three tracks UPDATE_CONTINUOUS (pivot motion, not a frame track)", cont)
	rep.check("all three tracks use linear interpolation (easing comes from the key transitions)", linear)
	rep.check("all three tracks enabled", enabled)

	# ---------------------------------------------------------------- clip settings (§4, §6)
	rep.check("step = one frame period at 60 fps (1/60)", absf(anim.step - STEP) < 1e-6, anim.step)
	rep.check("length = 48 frames (0.8 s)", _approx_t(anim.length, LENGTH), anim.length)
	rep.check("loop_mode = LOOP_NONE", anim.loop_mode == Animation.LOOP_NONE, anim.loop_mode)

	# ---------------------------------------------------------------- key times (one per boundary)
	var key_table: Array = []
	for k: int in KEY_FRAMES.size():
		key_table.append({"frame": KEY_FRAMES[k], "brief_time": KEY_FRAMES[k] / FPS,
				"key_time": anim.track_get_key_time(t_pos, k) if k < anim.track_get_key_count(t_pos) else null})
	extra["key_table"] = key_table
	for t: int in tracks:
		var times: Array[float] = _times(anim, t)
		var ok: bool = times.size() == KEY_FRAMES.size()
		var on_step: bool = true
		for k: int in times.size():
			if k < KEY_FRAMES.size():
				ok = ok and _approx_t(times[k], KEY_FRAMES[k] / FPS)
			on_step = on_step and absf(times[k] * FPS - roundf(times[k] * FPS)) < 0.01
		var frames: Array = times.map(func(x: float) -> String: return "%.6f (f%.2f)" % [x, x * FPS])
		rep.check("%s: keys at frames 0 / 12 / 33 / 40 / 48 within half a frame" % anim.track_get_path(t),
				ok, ", ".join(frames))
		rep.check("%s: every key on a whole 60 fps frame (not snapped to 1/30)" % anim.track_get_path(t),
				on_step)
		rep.check("%s: no key past length, last key at length" % anim.track_get_path(t),
				not times.is_empty() and times[-1] <= anim.length + TOL and _approx_t(times[-1], anim.length))

	# ---------------------------------------------------------------- key values (§4 key table)
	var pos_v: Array = _values(anim, t_pos)
	var pos_ok: bool = pos_v.size() == KEYS_POS.size()
	for k: int in mini(pos_v.size(), KEYS_POS.size()):
		pos_ok = pos_ok and typeof(pos_v[k]) == TYPE_VECTOR2 and (pos_v[k] as Vector2).is_equal_approx(KEYS_POS[k])
	rep.check("Rig:position = rest, rest, recoiled 6 px back (-6, 0), same, rest", pos_ok, pos_v)
	for pair: Array in [[t_up, KEYS_UPPER_DEG, "Rig/Upper:rotation = 0°, lean back -4°, 2° forward, same, 0°"],
			[t_bow, KEYS_BOW_DEG, "Rig/Upper/Bow:rotation = 12° below level (+), level, level, level, 20° forward/down (+)"]]:
		var vals: Array = _values(anim, pair[0])
		var want: Array[float] = pair[1]
		var ok: bool = vals.size() == want.size()
		var degs: Array[String] = []
		for k: int in vals.size():
			var is_f: bool = typeof(vals[k]) == TYPE_FLOAT
			degs.append("%.3f°" % rad_to_deg(float(vals[k])) if is_f else type_string(typeof(vals[k])))
			if k < want.size():
				ok = ok and is_f and absf(float(vals[k]) - deg_to_rad(want[k])) < ANGLE_TOL
		rep.check(pair[2], ok, ", ".join(degs))

	# ---------------------------------------------------------------- transitions (§4 last column)
	for t: int in tracks:
		var tr: Array[float] = []
		var ok: bool = anim.track_get_key_count(t) == TRANSITIONS.size()
		for k: int in anim.track_get_key_count(t):
			tr.append(anim.track_get_key_transition(t, k))
			if k < TRANSITIONS.size():
				ok = ok and is_equal_approx(tr[k], TRANSITIONS[k])
		rep.check("%s: transitions ease in (2), ease out (0.5), hold (1), ease in-out (-2), last (1)"
				% anim.track_get_path(t), ok, tr)
	var hold_ok: bool = true
	for t: int in tracks:
		hold_ok = hold_ok and anim.track_get_key_value(t, 2) == anim.track_get_key_value(t, 3)
	rep.check("hold: keys at frames 33 and 40 have the same values on every track", hold_ok)

	# ---------------------------------------------------------------- sampled between keys (reads the clip only)
	# Ease in on 0 -> 12: at frame 6 the bow has moved less than half way (12° -> 0°).
	var bow6: float = rad_to_deg(float(anim.value_track_interpolate(t_bow, 6.0 / FPS)))
	rep.check("startup eases in: bow at frame 6 still above 6° (slow start)", bow6 > 6.0 + 0.5, "%.3f°" % bow6)
	var up6: float = rad_to_deg(float(anim.value_track_interpolate(t_up, 6.0 / FPS)))
	rep.check("startup: Upper leans back (negative) by frame 6, less than half way", up6 < 0.0 and up6 > -2.0,
			"%.3f°" % up6)
	# Ease out on 12 -> 33: past half the recoil by the middle of the active phase (frame 22).
	var pos22: Vector2 = anim.value_track_interpolate(t_pos, 22.0 / FPS)
	rep.check("active eases out: recoil past -3 px by frame 22 (fast at the release)", pos22.x < -3.0, pos22)
	# Hold on 33 -> 40.
	var still: bool = true
	for f: int in range(33, 41):
		still = still and (anim.value_track_interpolate(t_pos, f / FPS) as Vector2).is_equal_approx(KEYS_POS[2]) \
				and absf(float(anim.value_track_interpolate(t_bow, f / FPS))) < ANGLE_TOL
	rep.check("recovery frames 33-40: nothing moves (hold)", still)
	# In-out on 40 -> 48: symmetric, half way at frame 44, slow at both ends.
	var bow44: float = rad_to_deg(float(anim.value_track_interpolate(t_bow, 44.0 / FPS)))
	var bow41: float = rad_to_deg(float(anim.value_track_interpolate(t_bow, 41.0 / FPS)))
	rep.check("bow drop eases in-out: about half way (10°) at frame 44, under 1/8 of the way at frame 41",
			absf(bow44 - 10.0) < 0.5 and bow41 < 20.0 / 8.0, "f41 %.3f°, f44 %.3f°" % [bow41, bow44])
	# Every sampled angle stays inside the key range: no overshoot from the curves.
	var lo_hi_ok: bool = true
	for f: int in LENGTH_FRAMES + 1:
		var b: float = rad_to_deg(float(anim.value_track_interpolate(t_bow, f / FPS)))
		var u: float = rad_to_deg(float(anim.value_track_interpolate(t_up, f / FPS)))
		lo_hi_ok = lo_hi_ok and b >= -0.01 and b <= 20.01 and u >= -4.01 and u <= 2.01
	rep.check("no overshoot: bow stays in [0°, 20°] and Upper in [-4°, 2°] on every frame 0-48", lo_hi_ok)

	mount.free()
	quit(rep.finish(extra))
