# build_board_square.py — Assignment 3, asset B (board_square)
#
# The execute_blender_code bodies that Claude Code ran through the Blender MCP (mcp-for-blender 2.1.9,
# Blender 5.2.2 LTS) on 2026-10-15, copied here in the order they ran, so git shows how the asset was built.
# Brief: CHANGE-BRIEF.md, Assignment 3 section (commit 78b213f).
#
# Every call defined flat_material() and add_box() again, unchanged; they are written once below.
# After step 6, Claude ran a temporary 3 x 3 tiled preview (8 linked copies of the mesh) for a `look`
# and then removed it without saving; that preview code is at the end, commented out.
#
# Script route (no window), from the repository root:
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 --python tools/blender/build_board_square.py

# --- Step 0 - clean start for board_square: empty scene, metric units, save as a new .blend ----------------------
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

out_dir = r"C:\dev\walker-lane-tactics-jiean-yin\blender"
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, "board_square.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
print("objects:", len(bpy.data.objects), "| materials:", len(bpy.data.materials), "| units:", scene.unit_settings.system, scene.unit_settings.scale_length)
print("saved:", bpy.data.filepath)

# --- Helpers (defined in each of steps 1-5) ----------------------------------------------------------------------
import bmesh
from mathutils import Matrix

def flat_material(name, hex_rgb):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    srgb = [int(hex_rgb[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    mat.diffuse_color = (*lin, 1.0)
    return mat

def add_box(name, size, location, material):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((*size, 1.0)))
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(material)
    return ob

# --- Step 1 - slab: box 0.92 x 0.92 x 0.04 m, bottom on z = 0, linen #D8C7A0 -------------------------------------
ob = add_box("slab", (0.92, 0.92, 0.04), (0.0, 0.0, 0.02), flat_material("linen", "D8C7A0"))
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 2 - border strip, front: box 1.00 x 0.04 x 0.05 m at y = -0.48, darker linen #CDB98E ------------------
ob = add_box("border_front", (1.00, 0.04, 0.05), (0.0, -0.48, 0.025), flat_material("linen_border", "CDB98E"))
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 3 - border strip, back: box 1.00 x 0.04 x 0.05 m at y = +0.48 -----------------------------------------
ob = add_box("border_back", (1.00, 0.04, 0.05), (0.0, 0.48, 0.025), flat_material("linen_border", "CDB98E"))
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 4 - border strip, left: box 0.04 x 0.92 x 0.05 m at x = -0.48 (shorter, so corners do not overlap) ----
ob = add_box("border_left", (0.04, 0.92, 0.05), (-0.48, 0.0, 0.025), flat_material("linen_border", "CDB98E"))
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 5 - border strip, right: box 0.04 x 0.92 x 0.05 m at x = +0.48 ----------------------------------------
ob = add_box("border_right", (0.04, 0.92, 0.05), (0.48, 0.0, 0.025), flat_material("linen_border", "CDB98E"))
bpy.ops.wm.save_mainfile()
print(ob.name, "tris:", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")

# --- Step 6 - join into "board_square"; origin = world origin = centre of the underside; apply transforms ---------
names = ["slab", "border_front", "border_back", "border_left", "border_right"]
parts = [bpy.data.objects[n] for n in names]
active = parts[0]

with bpy.context.temp_override(active_object=active, object=active,
                               selected_objects=parts, selected_editable_objects=parts):
    bpy.ops.object.join()

ob = bpy.data.objects["slab"]
ob.name = "board_square"
ob.data.name = "board_square"

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

# --- Temporary preview, run and removed, never saved ---------------------------------------------------------------
# src = bpy.data.objects["board_square"]
# for i in (-1, 0, 1):
#     for j in (-1, 0, 1):
#         if i == 0 and j == 0:
#             continue
#         c = bpy.data.objects.new("preview_tile_%d_%d" % (i, j), src.data)  # shares the mesh, nothing copied
#         c.location = (i * 1.0, j * 1.0, 0.0)
#         bpy.context.scene.collection.objects.link(c)
# ... look(top, three_quarter) ...
# for o in [o for o in list(bpy.data.objects) if o.name.startswith("preview_tile_")]:
#     bpy.data.objects.remove(o, do_unlink=True)

# --- Revision A3-R1 (run after the first look) - darken the border: "linen_border" #CDB98E -> #9A7F55 -------------
# See CHANGE-BRIEF.md, A3-R1. The same temporary 3 x 3 preview was run again to judge it, then removed unsaved.
def set_flat_color(mat, hex_rgb):
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    srgb = [int(hex_rgb[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
    mat.diffuse_color = (*lin, 1.0)
    return bsdf

mat = bpy.data.materials["linen_border"]
bsdf = set_flat_color(mat, "9A7F55")
bpy.ops.wm.save_mainfile()
ob = bpy.data.objects["board_square"]
print("linen_border base color (linear):", tuple(round(c, 4) for c in bsdf.inputs["Base Color"].default_value))
print("materials on board_square:", [m.name for m in ob.data.materials], "| dims", tuple(round(d, 4) for d in ob.dimensions),
      "| scale", tuple(ob.scale), "| tris", sum(len(p.vertices) - 2 for p in ob.data.polygons), "| saved")
