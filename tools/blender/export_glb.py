# export_glb.py — Assignment 3: export the three assets from their .blend sources to binary glTF (.glb).
#
# Runs in headless Blender (no window, no MCP). It opens each .blend from <src_dir>, checks that the file holds
# exactly the one expected mesh object with transforms applied (location 0, rotation 0, scale 1), and exports it
# with Blender's own glTF 2.0 exporter: binary .glb, +Y Up on (the exporter's default, set explicitly here),
# materials exported, no cameras, lights or animation. Any failed check raises, so Blender exits 1.
#
# Usage, from the repository root (Git Bash shown; <src_dir> defaults to blender/):
#   <Blender exe> -b --factory-startup --python-exit-code 1 \
#       --python tools/blender/export_glb.py -- [<src_dir>] [<out_dir>]
# On 2026-10-15 <src_dir> was a scratch copy extracted with `git show <commit>:blender/<name>.blend`, so the
# export came from the committed sources and not from files open in Blender at the time.
import os
import sys

import bpy

ASSETS = ["archer_piece", "board_square", "goal_flag"]

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
src_dir = os.path.abspath(args[0]) if len(args) > 0 else os.path.join(REPO, "blender")
out_dir = os.path.abspath(args[1]) if len(args) > 1 else os.path.join(REPO, "godot", "assets", "models")
os.makedirs(out_dir, exist_ok=True)

print("export_glb: Blender", bpy.app.version_string, "| src", src_dir, "| out", out_dir)

for name in ASSETS:
    blend = os.path.join(src_dir, name + ".blend")
    bpy.ops.wm.open_mainfile(filepath=blend)

    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    others = [o.name for o in bpy.data.objects if o.type != "MESH"]
    if len(meshes) != 1 or meshes[0].name != name or others:
        raise RuntimeError("%s: expected one mesh object named %s, found meshes %s, others %s"
                           % (blend, name, [o.name for o in meshes], others))
    ob = meshes[0]
    loc, rot, scl = tuple(ob.location), tuple(ob.rotation_euler), tuple(ob.scale)
    if any(abs(c) > 1e-6 for c in loc + rot) or any(abs(c - 1.0) > 1e-6 for c in scl):
        raise RuntimeError("%s: transforms not applied: loc %s rot %s scale %s" % (name, loc, rot, scl))

    zs = [v.co.z for v in ob.data.vertices]
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    glb = os.path.join(out_dir, name + ".glb")
    bpy.ops.export_scene.gltf(
        filepath=glb,
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        use_selection=False,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_animations=False,
    )
    with open(glb, "rb") as f:
        magic = f.read(4)
    if magic != b"glTF":
        raise RuntimeError("%s: output is not binary glTF (magic %r)" % (glb, magic))
    print("EXPORTED %s | blender dims %s | z %.4f..%.4f | tris %d | materials %s | %d bytes"
          % (name, tuple(round(d, 4) for d in ob.dimensions), min(zs), max(zs), tris,
             [m.name for m in ob.data.materials], os.path.getsize(glb)))

print("export_glb: done,", len(ASSETS), "files")
