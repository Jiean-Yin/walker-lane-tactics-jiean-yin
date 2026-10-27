# build_goal_flag.py — Assignment 3, asset C (goal_flag)
#
# The execute_blender_code bodies that Claude Code ran through the Blender MCP (mcp-for-blender 2.1.9,
# Blender 5.2.2 LTS) on 2026-10-15, copied here in the order they ran, so git shows how the asset was built.
# Brief: CHANGE-BRIEF.md, Assignment 3 section (commit 78b213f).
#
# Every call defined flat_material() and add_mesh_object() again, unchanged; they are written once below.
#
# Script route (no window), from the repository root:
#   <Blender exe> -b --factory-startup --python-exit-code 1 --python tools/blender/build_goal_flag.py

# --- Step 0 - clean start for goal_flag: empty scene, metric units, save as a new .blend -------------------------
import bpy, os

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
    for block in list(coll):
        if block.users == 0:
            coll.remove(block)

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'
scene.cursor.location = (0.0, 0.0, 0.0)

out_dir = os.environ.get("LT_BLEND_DIR", os.path.join(os.getcwd(), "blender"))  # <repo>/blender (the MCP run wrote its absolute path here)
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, "goal_flag.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("objects:", len(bpy.data.objects), "| materials:", len(bpy.data.materials), "| units:", scene.unit_settings.system, scene.unit_settings.scale_length)
print("saved:", bpy.data.filepath)

# --- Helpers (defined in each of steps 1-3) ----------------------------------------------------------------------
import bmesh
from mathutils import Matrix

def flat_material(name, hex_rgb):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    srgb = [int(hex_rgb[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
    mat.diffuse_color = (*lin, 1.0)
    return mat

def add_mesh_object(name, build, location, material):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(material)
    return ob

def box(sx, sy, sz):
    return lambda bm: bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((sx, sy, sz, 1.0)))

# --- Step 1 - base disc: cylinder, 12 segments, 0.30 m across, 0.04 m tall, bottom on z = 0, walnut #5A3A22 -------
ob = add_mesh_object(
    "flag_base",
    lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                                     radius1=0.15, radius2=0.15, depth=0.04),
    (0.0, 0.0, 0.02),
    flat_material("walnut", "5A3A22"),
)
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 2 - pole: cylinder, 8 segments, 0.04 m across, from z 0.04 to 1.20 (1.16 tall), walnut ----------------
ob = add_mesh_object(
    "pole",
    lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8,
                                     radius1=0.02, radius2=0.02, depth=1.16),
    (0.0, 0.0, 0.62),
    flat_material("walnut", "5A3A22"),
)
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 3 - flag: thin box 0.28 x 0.02 x 0.20 m, x 0.02..0.30 toward +X, z 0.98..1.18, enemy red #B23A2E ------
ob = add_mesh_object("flag", box(0.28, 0.02, 0.20), (0.16, 0.0, 1.08), flat_material("enemy_red", "B23A2E"))
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 4 - join into "goal_flag"; origin = world origin = centre of the base disc's underside; apply transforms
names = ["flag_base", "pole", "flag"]
parts = [bpy.data.objects[n] for n in names]
active = parts[0]

with bpy.context.temp_override(active_object=active, object=active,
                               selected_objects=parts, selected_editable_objects=parts):
    bpy.ops.object.join()

ob = bpy.data.objects["flag_base"]
ob.name = "goal_flag"
ob.data.name = "goal_flag"

with bpy.context.temp_override(active_object=ob, object=ob,
                               selected_objects=[ob], selected_editable_objects=[ob]):
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

for o in bpy.data.objects:
    o.select_set(o is ob)
bpy.context.view_layer.objects.active = ob

xs = [v.co.x for v in ob.data.vertices]; ys = [v.co.y for v in ob.data.vertices]; zs = [v.co.z for v in ob.data.vertices]
tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
bpy.ops.wm.save_mainfile()
print("objects in scene:", [o.name for o in bpy.data.objects])
print("location", tuple(round(c, 4) for c in ob.location), "rotation", tuple(round(c, 4) for c in ob.rotation_euler), "scale", tuple(round(c, 4) for c in ob.scale))
print("dimensions", tuple(round(d, 4) for d in ob.dimensions))
print("mesh bounds x %.4f..%.4f y %.4f..%.4f z %.4f..%.4f" % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
print("triangles", tris, "| materials", [m.name for m in ob.data.materials], "| saved")
