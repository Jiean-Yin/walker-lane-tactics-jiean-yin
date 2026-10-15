extends SceneTree
## Headless check of the three Assignment 3 assets against CHANGE-BRIEF.md (A3 section, with revision A3-R1).
## godot --headless --path godot --script res://tests/check_assets.gd
##
## Part 1, each .glb on its own: world bounding box (all meshes), lowest Y, node scale and rotation of every node,
## which axis the asset stands along, triangle count, and material albedo colours.
## Part 2, the diorama scene: each asset's lowest point against the floor's top, the gaps between assets, and
## whether every bounding-box corner is inside the camera's view.
##
## What this does NOT show: that the assets render or look right (the dummy headless renderer draws nothing),
## that colours read well under the lamp, or that the shapes read as what they are. Those are human checks.
##
## Measurements wait one process frame after add_child(): the first version measured inside _initialize(), where
## the nodes were not yet in the tree, so global transforms were identity and the camera had no frustum. Every
## measurement now first checks that its node is inside the tree, and the camera check that it has 6 planes.

const Report = preload("res://tests/test_report.gd")

const SIZE_TOL: float = 0.01   # metres, brief prediction 2
const FLOOR_TOL: float = 0.005  # metres, brief prediction 3
const COLOR_TOL: float = 2.5 / 255.0

## W x H x D in Godot axes (X, Y, Z). The brief's W x D x H is Blender X, Y, Z; Blender Z (height) -> Godot Y.
const ASSETS: Array[Dictionary] = [
	{"name": "archer_piece", "size": Vector3(0.40, 0.80, 0.40), "budget": 400,
	 "colors": ["5A3A22", "1F6F78", "E2B887", "24323F", "1B1410"]},
	{"name": "board_square", "size": Vector3(1.00, 0.05, 1.00), "budget": 100,
	 "colors": ["D8C7A0", "9A7F55"]},
	{"name": "goal_flag", "size": Vector3(0.45, 1.20, 0.30), "budget": 150,
	 "colors": ["5A3A22", "B23A2E"]},
]

var rep: Report
var measured: Dictionary = {}


func _initialize() -> void:
	_run()


func _run() -> void:
	rep = Report.new("check_assets")
	for spec: Dictionary in ASSETS:
		await _check_asset(spec)
	await _check_diorama()
	quit(rep.finish({"measured": measured}))


func _meshes(node: Node, out: Array[MeshInstance3D]) -> Array[MeshInstance3D]:
	if node is MeshInstance3D:
		out.append(node as MeshInstance3D)
	for c: Node in node.get_children():
		_meshes(c, out)
	return out


func _world_aabb(node: Node) -> AABB:
	var box: AABB = AABB()
	var first: bool = true
	for mi: MeshInstance3D in _meshes(node, []):
		var b: AABB = mi.global_transform * mi.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box


func _all_nodes(node: Node, out: Array[Node3D]) -> Array[Node3D]:
	if node is Node3D:
		out.append(node as Node3D)
	for c: Node in node.get_children():
		_all_nodes(c, out)
	return out


func _v(v: Vector3) -> String:
	return "(%.4f, %.4f, %.4f)" % [v.x, v.y, v.z]


func _check_asset(spec: Dictionary) -> void:
	var asset_name: String = spec["name"]
	var path: String = "res://assets/models/%s.glb" % asset_name
	var packed: PackedScene = load(path) as PackedScene
	if not rep.check("%s: loads from %s" % [asset_name, path], packed != null):
		return
	var inst: Node3D = packed.instantiate() as Node3D
	root.add_child(inst)
	await process_frame
	if not rep.check("%s: instance is inside the scene tree before measuring" % asset_name, inst.is_inside_tree()):
		return

	var box: AABB = _world_aabb(inst)
	var size: Vector3 = box.size
	var want: Vector3 = spec["size"]
	var diff: Vector3 = (size - want).abs()
	rep.check("%s: bounding box W x H x D matches brief within %.2f m" % [asset_name, SIZE_TOL],
		diff.x <= SIZE_TOL and diff.y <= SIZE_TOL and diff.z <= SIZE_TOL,
		"got %s, brief %s" % [_v(size), _v(want)])

	# Upright: the brief's height must be the Y extent (Godot is Y-up). Compare against the other two axes too,
	# so a model lying on its side fails even if one dimension happens to match.
	var axes: Array[String] = ["X", "Y", "Z"]
	var stands: String = "?"
	for i: int in 3:
		if absf(size[i] - want.y) <= SIZE_TOL and (i == 1 or absf(size[1] - want.y) > SIZE_TOL):
			stands = axes[i]
			break
	rep.check("%s: stands along Y (height %.2f m on Y)" % [asset_name, want.y], stands == "Y",
		"height axis %s" % stands)

	rep.check("%s: lowest point at y = 0 (origin at the base)" % asset_name, absf(box.position.y) <= FLOOR_TOL,
		"min y %.4f, max y %.4f" % [box.position.y, box.end.y])

	var node_report: Array[String] = []
	var all_unit: bool = true
	for n: Node3D in _all_nodes(inst, []):
		var s: Vector3 = n.scale
		var r: Vector3 = n.rotation_degrees
		var ok: bool = s.is_equal_approx(Vector3.ONE) and r.is_zero_approx()
		all_unit = all_unit and ok
		node_report.append("%s %s scale %s rot %s" % [n.name, n.get_class(), _v(s), _v(r)])
	rep.check("%s: every node has scale (1, 1, 1) and rotation 0" % asset_name, all_unit, "; ".join(node_report))

	var tris: int = 0
	var found_hex: Array[String] = []
	for mi: MeshInstance3D in _meshes(inst, []):
		var mesh: Mesh = mi.mesh
		for s_i: int in mesh.get_surface_count():
			var arrays: Array = mesh.surface_get_arrays(s_i)
			var idx: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			tris += (idx.size() if idx.size() > 0 else verts.size()) / 3
			var mat: Material = mi.get_active_material(s_i)
			if mat is BaseMaterial3D:
				found_hex.append((mat as BaseMaterial3D).albedo_color.to_html(false).to_upper())
			else:
				found_hex.append("not-BaseMaterial3D")
	rep.check("%s: triangles within budget %d" % [asset_name, spec["budget"]], tris <= int(spec["budget"]),
		"%d triangles" % tris)

	var missing: Array[String] = []
	for hex: String in spec["colors"]:
		var want_c: Color = Color.html(hex)
		var hit: bool = false
		for got: String in found_hex:
			if got.begins_with("NOT"):
				continue
			var c: Color = Color.html(got)
			if absf(c.r - want_c.r) <= COLOR_TOL and absf(c.g - want_c.g) <= COLOR_TOL and absf(c.b - want_c.b) <= COLOR_TOL:
				hit = true
		if not hit:
			missing.append(hex)
	rep.check("%s: every brief colour arrived as a material albedo (±2 of 255)" % asset_name,
		missing.is_empty() and found_hex.size() == (spec["colors"] as Array).size(),
		"found %s, missing %s" % [", ".join(found_hex), ", ".join(missing)])

	measured[asset_name] = {
		"aabb_min": [box.position.x, box.position.y, box.position.z],
		"aabb_size": [size.x, size.y, size.z],
		"stands_along": stands,
		"triangles": tris,
		"albedo_hex": found_hex,
		"nodes": node_report,
	}
	inst.queue_free()


func _check_diorama() -> void:
	var packed: PackedScene = load("res://diorama/asset_diorama.tscn") as PackedScene
	if not rep.check("diorama: res://diorama/asset_diorama.tscn loads", packed != null):
		return
	var scene: Node3D = packed.instantiate() as Node3D
	root.add_child(scene)
	await process_frame
	if not rep.check("diorama: scene is inside the tree before measuring", scene.is_inside_tree()):
		return

	var floor_node: MeshInstance3D = scene.get_node("Floor") as MeshInstance3D
	var floor_box: AABB = floor_node.global_transform * floor_node.get_aabb()
	var floor_top: float = floor_box.end.y
	var cam: Camera3D = scene.get_node("Camera3D") as Camera3D
	rep.check("diorama: camera has a real frustum (6 planes), so the view check can mean something",
		cam.get_frustum().size() == 6, "%d planes" % cam.get_frustum().size())
	var lights: int = 0
	for n: Node in scene.get_children():
		if n is Light3D:
			lights += 1
	rep.check("diorama: exactly one light", lights == 1, "%d Light3D nodes" % lights)

	var spans: Array[Vector2] = []
	var on_floor: Dictionary = {}
	for spec: Dictionary in ASSETS:
		var asset_name: String = spec["name"]
		var node: Node3D = scene.get_node_or_null(asset_name) as Node3D
		if not rep.check("diorama: has %s" % asset_name, node != null):
			continue
		var box: AABB = _world_aabb(node)
		# Measured against the Floor mesh's own top, not the asset's own bounds.
		var gap: float = box.position.y - floor_top
		on_floor[asset_name] = gap
		rep.check("diorama: %s sits on the floor (gap %.4f m)" % [asset_name, gap], absf(gap) <= FLOOR_TOL,
			"asset min y %.4f, floor top %.4f" % [box.position.y, floor_top])
		var inside: bool = true
		for i: int in 8:
			inside = inside and cam.is_position_in_frustum(box.get_endpoint(i))
		rep.check("diorama: %s fully inside the camera view" % asset_name, inside, "box %s .. %s" % [_v(box.position), _v(box.end)])
		spans.append(Vector2(box.position.x, box.end.x))

	spans.sort_custom(func(a: Vector2, b: Vector2) -> bool: return a.x < b.x)
	var apart: bool = true
	for i: int in range(1, spans.size()):
		apart = apart and spans[i].x > spans[i - 1].y
	rep.check("diorama: the three assets stand side by side without overlapping in X", apart, str(spans))
	measured["diorama"] = {"floor_top_y": floor_top, "gap_to_floor": on_floor, "x_spans": spans.map(func(v: Vector2) -> Array: return [v.x, v.y])}
	scene.queue_free()
