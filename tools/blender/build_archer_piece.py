# build_archer_piece.py — Assignment 3, asset A (archer_piece)
#
# The execute_blender_code bodies that Claude Code ran through the Blender MCP (mcp-for-blender 2.1.9,
# Blender 5.2.2 LTS) on 2026-10-15, copied here in the order they ran, so git shows how the asset was built.
# Brief: CHANGE-BRIEF.md, Assignment 3 section (commit 78b213f).
#
# Calls that ran but did not survive (logged in FRICTIONAL.md, 2026-10-15 18:17–18:20):
#   - Step 0 ran twice more and step 1 twice more, because Blender was closed and reopened by hand in between.
#   - Step 1, try 1, used the operator instead of bmesh and lost the connection when Blender was closed:
#         bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.20, depth=0.05, location=(0.0, 0.0, 0.025))
#         ob = bpy.context.active_object; ob.name = "base_disc"; ob.data.materials.append(flat_material("walnut", "5A3A22"))
#   From try 2 on, every part is built with bmesh and each step saves the .blend.
#
# The bodies below are the final run (steps 0–7). Hand edits made later in Blender's window are not in this file;
# they are recorded in FRICTIONAL.md and live in blender/archer_piece.blend.
#
# Script route (no window), from the repository root:
#   <Blender exe> -b --factory-startup --python-exit-code 1 --python tools/blender/build_archer_piece.py

# --- Step 0 - clean start for archer_piece: empty scene, metric units, save the .blend ---------------------------
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
path = os.path.join(out_dir, "archer_piece.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("objects:", len(bpy.data.objects), "| units:", scene.unit_settings.system, scene.unit_settings.scale_length, scene.unit_settings.length_unit)
print("saved:", bpy.data.filepath)

# --- Step 1 - base disc: cylinder, 12 segments, 0.40 m across, 0.05 m tall, bottom on z = 0, walnut #5A3A22 -------
import bpy, bmesh

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

ob = add_mesh_object(
    "base_disc",
    lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                                     radius1=0.20, radius2=0.20, depth=0.05),
    (0.0, 0.0, 0.025),
    flat_material("walnut", "5A3A22"),
)
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 2 - body: cylinder, 12 segments, 0.26 m across, from z 0.05 to 0.50 (0.45 tall), teal #1F6F78 ----------
# (flat_material and add_mesh_object were defined again, unchanged, in this call)
ob = add_mesh_object(
    "body",
    lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                                     radius1=0.13, radius2=0.13, depth=0.45),
    (0.0, 0.0, 0.275),
    flat_material("team_teal", "1F6F78"),
)
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 3 - head: UV sphere, 12 segments x 6 rings, 0.22 m across, centre at z 0.61, birch #E2B887 -------------
# (helpers defined again, unchanged)
ob = add_mesh_object(
    "head",
    lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=6, radius=0.11),
    (0.0, 0.0, 0.61),
    flat_material("birch", "E2B887"),
)
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 4 - hood: cone, 12 segments, 0.25 m across at the base, from z 0.64 to 0.80, hood paint #24323F --------
# In this call add_mesh_object also merged doubles, so the cone tip is one vertex, not 12:
def add_mesh_object_merged(name, build, location, material):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)  # a cone tip must be one vertex, not 12
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(material)
    return ob

ob = add_mesh_object_merged(
    "hood",
    lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12,
                                     radius1=0.125, radius2=0.0, depth=0.16),
    (0.0, 0.0, 0.72),
    flat_material("hood", "24323F"),
)
bpy.ops.wm.save_mainfile()
print(ob.name, "verts:", len(ob.data.vertices), "faces:", len(ob.data.polygons),
      "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 5 - bow: thin cube 0.03 x 0.06 x 0.50 m on the +X (facing) side, centre (0.165, 0, 0.40), walnut ------
# The size is baked into the mesh (bmesh matrix), so the object's scale stays 1, 1, 1.
from mathutils import Matrix

def box(sx, sy, sz):
    return lambda bm: bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((sx, sy, sz, 1.0)))

ob = add_mesh_object("bow", box(0.03, 0.06, 0.50), (0.165, 0.0, 0.40), flat_material("walnut", "5A3A22"))
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 6 - eye: small cube 0.03 m on the +X side of the head, centre (0.105, 0, 0.60), below the hood, ink -----
ob = add_mesh_object("eye", box(0.03, 0.03, 0.03), (0.105, 0.0, 0.60), flat_material("ink", "1B1410"))
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 7 - join into "archer_piece"; origin = world origin = centre of the underside; apply transforms ---------
names = ["base_disc", "body", "head", "hood", "bow", "eye"]
parts = [bpy.data.objects[n] for n in names]
active = parts[0]

with bpy.context.temp_override(active_object=active, object=active,
                               selected_objects=parts, selected_editable_objects=parts):
    bpy.ops.object.join()

ob = bpy.data.objects["base_disc"]
ob.name = "archer_piece"
ob.data.name = "archer_piece"

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
