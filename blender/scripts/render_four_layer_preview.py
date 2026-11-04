"""Re-render four-layer overview with a safe side camera."""
import bpy, sys, os, math

argv = sys.argv
args = argv[argv.index("--") + 1 :] if "--" in argv else []
blend, png = args[0], args[1]
bpy.ops.wm.open_mainfile(filepath=blend)

# Fix camera: look at mid stack from +X side (concept slice feel)
cam = bpy.data.objects.get("CAM_Overview")
if cam is None:
    cam_data = bpy.data.cameras.new("CAM_Overview")
    cam = bpy.data.objects.new("CAM_Overview", cam_data)
    bpy.context.scene.collection.objects.link(cam)
cam.data.lens = 28
cam.data.clip_end = 500
# Stack centers around Y=27, Z=0; place camera on +X looking -X
cam.location = (42.0, 28.0, 18.0)
# aim at (0, 28, 0)
direction = cam.location - __import__("mathutils").Vector((0.0, 28.0, 0.0))
# Blender track: camera looks down -Z local; use track_to
cam.rotation_euler = (math.radians(78), 0.0, math.radians(90))

# Brighter viewport-like lighting
sun = bpy.data.objects.get("LIT_Viewport_Sun")
if sun and sun.data:
    sun.data.energy = 4.0
# add fill area light
if "LIT_Fill" not in bpy.data.objects:
    fill = bpy.data.lights.new("LIT_Fill_data", type="AREA")
    fill.energy = 800
    fill.size = 40
    fill.color = (0.7, 0.8, 1.0)
    fill_obj = bpy.data.objects.new("LIT_Fill", fill)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.location = (20, 30, -15)
    fill_obj.rotation_euler = (math.radians(60), 0, math.radians(30))

scene = bpy.context.scene
scene.camera = cam
# Blender 5 Eevee
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
    try:
        scene.render.engine = eng
        break
    except Exception:
        continue
scene.world = bpy.data.worlds.new("W_Preview") if scene.world is None else scene.world
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.08, 0.09, 0.12, 1.0)
    bg.inputs[1].default_value = 1.0

scene.render.resolution_x = 1280
scene.render.resolution_y = 1600
scene.render.filepath = png
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
# also save camera fix into blend
bpy.ops.wm.save_mainfile()
print("PREVIEW_OK", png, os.path.getsize(png) if os.path.exists(png) else 0)
