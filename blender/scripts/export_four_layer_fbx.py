"""Export four-layer blockout FBX + anchors CSV. Blender 5.x"""
import bpy, sys, os, csv

argv = sys.argv
args = argv[argv.index("--") + 1 :] if "--" in argv else []
blend = args[0]
fbx = args[1]
bpy.ops.wm.open_mainfile(filepath=blend)
bpy.ops.export_scene.fbx(
    filepath=fbx,
    use_selection=False,
    object_types={"MESH", "EMPTY", "ARMATURE"},
    use_mesh_modifiers=True,
    mesh_smooth_type="FACE",
    add_leaf_bones=False,
    axis_forward="-Z",
    axis_up="Y",
    apply_scale_options="FBX_SCALE_ALL",
    path_mode="AUTO",
)
print("EXPORTED", fbx, os.path.getsize(fbx) if os.path.exists(fbx) else 0)
csv_path = os.path.splitext(fbx)[0] + "_anchors.csv"
rows = [("id", "type", "x", "y", "z", "collection")]
for o in bpy.data.objects:
    if o.name.startswith("AN_") or o.type == "EMPTY":
        cols = [c.name for c in o.users_collection]
        rows.append(
            (
                o.name,
                o.type,
                f"{o.location.x:.3f}",
                f"{o.location.y:.3f}",
                f"{o.location.z:.3f}",
                "|".join(cols),
            )
        )
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)
print("CSV", csv_path, "rows", len(rows) - 1)

# preview render
png = os.path.splitext(fbx)[0] + "_preview.png"
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 1600
scene.render.filepath = png
if "CAM_Overview" in bpy.data.objects:
    scene.camera = bpy.data.objects["CAM_Overview"]
bpy.ops.render.render(write_still=True)
print("PREVIEW", png, os.path.exists(png))
