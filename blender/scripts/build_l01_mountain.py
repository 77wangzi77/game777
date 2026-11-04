"""L01 高山关 · 单关灰模（按清晰关卡01概念）Blender 5.x · 1BU=1m · Y-up 对齐 Unity"""
import bpy, os, sys, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0


def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c) if parent else bpy.context.scene.collection.children.link(c)
    if parent:
        # already linked above wrongly if parent None handled
        pass
    return c


def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    if parent is None:
        bpy.context.scene.collection.children.link(c)
    else:
        parent.children.link(c)
    return c


def link(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)


def mat(name, color, emission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.85
        if emission > 0 and "Emission Strength" in bsdf.inputs:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission
    return m


def cube(name, loc, scale, coll, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    link(obj, coll)
    return obj


def cylinder(name, loc, radius, depth, coll, material=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    link(obj, coll)
    return obj


def empty(name, loc, coll, empty_type="PLAIN_AXES", size=0.5):
    bpy.ops.object.empty_add(type=empty_type, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.empty_display_size = size
    link(obj, coll)
    return obj


def point_light(name, loc, coll, color=(1, 0.6, 0.3), energy=100):
    data = bpy.data.lights.new(name + "_data", "POINT")
    data.color = color
    data.energy = energy
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    coll.objects.link(obj)
    return obj


M_STONE = mat("M_L01_Stone", (0.45, 0.45, 0.48))
M_ROCK = mat("M_L01_Rock", (0.28, 0.30, 0.34))
M_PATH = mat("M_L01_Path", (0.55, 0.54, 0.50))
M_WOOD = mat("M_L01_Wood", (0.38, 0.24, 0.14))
M_ROOF = mat("M_L01_Roof", (0.12, 0.12, 0.14))
M_PINE = mat("M_L01_Pine", (0.16, 0.30, 0.16))
M_WATER = mat("M_L01_Water", (0.40, 0.55, 0.65), 0.3)
M_WARM = mat("M_L01_Warm", (0.55, 0.38, 0.28))

root = collection("LV_01_Mountain")
col_env = collection("ENV_L01_Mountain", root)
col_prop = collection("PROP_L01", root)
col_an = collection("Anchors_L01", root)
col_lit = collection("LIT_L01", root)

# --- Cave mouth frame (player start looking out) ---
cube("ENV_L01_CaveMouth_Top", (0, 6.2, -10), (8, 1.4, 1.6), col_env, M_STONE)
cube("ENV_L01_CaveMouth_L", (-4.2, 3.2, -10), (1.4, 5.0, 1.6), col_env, M_STONE)
cube("ENV_L01_CaveMouth_R", (4.2, 3.2, -10), (1.4, 5.0, 1.6), col_env, M_STONE)
cube("ENV_L01_CaveMouth_Sill", (0, 0.35, -9.2), (8, 0.5, 2.5), col_env, M_PATH)
# side / back rock shell (open toward -Z mouth)
cube("ENV_L01_CliffWall_Back", (0, 7, 12), (22, 14, 2.5), col_env, M_ROCK)
cube("ENV_L01_CliffWall_L", (-11, 6, 1), (2.5, 12, 22), col_env, M_ROCK)
cube("ENV_L01_CliffWall_R", (11, 6, 1), (2.5, 12, 22), col_env, M_ROCK)
cube("ENV_L01_CliffWall_Ceil", (0, 13.5, 1), (22, 1.5, 22), col_env, M_ROCK)

# --- Winding cliff path & stairs (mouth → peak) ---
cube("ENV_L01_CliffPath_01", (0, 0.2, -6.5), (5.0, 0.35, 5.0), col_env, M_PATH)
cube("ENV_L01_CliffPath_02", (2.5, 0.9, -2.5), (4.0, 0.35, 4.0), col_env, M_PATH)
cube("ENV_L01_CliffPath_03", (3.5, 1.8, 1.5), (3.5, 0.35, 3.5), col_env, M_PATH)
cube("ENV_L01_Stair_Set_A", (2.0, 2.6, 4.5), (2.4, 1.5, 3.2), col_env, M_PATH)
cube("ENV_L01_Stair_Set_B", (0.5, 3.8, 7.0), (2.2, 1.6, 2.8), col_env, M_PATH)
cube("ENV_L01_PeakPlatform", (0, 5.0, 9.5), (7.0, 0.45, 6.5), col_env, M_PATH)

# --- Pavilion on peak (柱 + 歇山顶 proxy) ---
for nm, xy in [("FL", (-1.5, 8.5)), ("FR", (1.5, 8.5)), ("BL", (-1.5, 10.5)), ("BR", (1.5, 10.5))]:
    cube(f"ENV_L01_Pavilion_Post_{nm}", (xy[0], 6.3, xy[1]), (0.3, 2.4, 0.3), col_env, M_WOOD)
cube("ENV_L01_Pavilion_Deck", (0, 5.25, 9.5), (3.6, 0.2, 3.2), col_env, M_WOOD)
cube("ENV_L01_Pavilion_Beam", (0, 7.6, 9.5), (3.4, 0.25, 3.0), col_env, M_WOOD)
cube("ENV_L01_Pavilion_Roof", (0, 8.0, 9.5), (4.6, 0.55, 4.0), col_env, M_ROOF)
cube("ENV_L01_Pavilion_RoofUpper", (0, 8.55, 9.5), (3.2, 0.35, 2.6), col_env, M_ROOF)
cube("ENV_L01_Pavilion_Ridge", (0, 8.9, 9.5), (2.8, 0.2, 0.35), col_env, M_ROOF)

# --- Lower stone gate on path ---
cube("ENV_L01_StoneGate_L", (-1.6, 1.8, -3.5), (0.4, 2.4, 0.4), col_env, M_STONE)
cube("ENV_L01_StoneGate_R", (1.6, 1.8, -3.5), (0.4, 2.4, 0.4), col_env, M_STONE)
cube("ENV_L01_StoneGate_Lint", (0, 3.2, -3.5), (3.6, 0.4, 0.5), col_env, M_STONE)

# --- Props ---
cube("PROP_L01_PineTree_A", (-5.0, 4.5, 6.0), (0.8, 6.5, 0.8), col_prop, M_PINE)
cube("PROP_L01_PineTree_B", (5.2, 5.2, 8.0), (0.7, 5.5, 0.7), col_prop, M_PINE)
cube("PROP_L01_PineTree_C", (-3.5, 3.0, 0.5), (0.6, 4.5, 0.6), col_prop, M_PINE)
cube("PROP_L01_Waterfall_FX", (8.5, 5.0, 2.0), (1.0, 9.0, 2.0), col_prop, M_WATER)
cube("PROP_L01_PrayerTablet", (-2.2, 5.8, 9.0), (0.12, 0.8, 0.45), col_prop, M_WOOD)
cube("PROP_L01_Rail_Pine_L", (-2.2, 5.6, 9.5), (0.15, 0.7, 4.5), col_prop, M_STONE)
cube("PROP_L01_Rail_Pine_R", (2.2, 5.6, 9.5), (0.15, 0.7, 4.5), col_prop, M_STONE)
cube("PROP_L01_WindChime", (1.8, 7.4, 8.7), (0.15, 0.5, 0.15), col_prop, M_WARM)

# --- Lights ---
point_light("LIT_L01_Torch_L", (-3.5, 2.6, -8.5), col_lit, (1.0, 0.55, 0.25), 140)
point_light("LIT_L01_Torch_R", (3.5, 2.6, -8.5), col_lit, (1.0, 0.55, 0.25), 140)
point_light("LIT_L01_Pavilion", (0, 6.8, 9.5), col_lit, (1.0, 0.7, 0.35), 110)
point_light("LIT_L01_Path", (2.5, 2.2, 1.0), col_lit, (1.0, 0.6, 0.3), 60)

# --- Anchors ---
empty("AN_Teleport_L01_Spawn", (0, 1.0, -7.5), col_an, "SINGLE_ARROW", 0.9)
empty("AN_Teleport_L01_Gate", (0, 1.5, -3.5), col_an, "SINGLE_ARROW", 0.7)
empty("AN_Teleport_L01_MidPath", (3.0, 2.3, 1.5), col_an, "SINGLE_ARROW", 0.7)
empty("AN_Teleport_L01_PreAscent", (0, 5.5, 9.0), col_an, "SINGLE_ARROW", 0.9)
empty("AN_Look_L01_MouthOut", (0, 2.5, -12), col_an, "PLAIN_AXES", 0.4)
empty("AN_Look_L01_Pavilion", (0, 7.0, 11.5), col_an, "PLAIN_AXES", 0.4)
empty("AN_Look_L01_Ascent", (0, 6.5, 12.5), col_an, "PLAIN_AXES", 0.4)
empty("AN_Look_UI_task", (0, 6.2, 8.2), col_an, "PLAIN_AXES", 0.35)

# Camera focused on L01 playable volume
cam_data = bpy.data.cameras.new("CAM_L01")
cam = bpy.data.objects.new("CAM_L01", cam_data)
bpy.context.scene.collection.objects.link(cam)
cam.location = (18, 8, -18)
direction = Vector((0, 5, 2)) - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
cam_data.lens = 28
scene.camera = cam

sun = bpy.data.lights.new("LIT_L01_Sun", "SUN")
sun.energy = 2.5
sun_o = bpy.data.objects.new("LIT_L01_Sun", sun)
bpy.context.scene.collection.objects.link(sun_o)
sun_o.rotation_euler = (math.radians(50), math.radians(15), math.radians(30))

out = None
argv = sys.argv
if "--" in argv:
    a = argv[argv.index("--") + 1 :]
    if a:
        out = a[0]
if not out:
    out = os.path.join(os.getcwd(), "LV_01_Mountain_Blockout.blend")
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED", out)
print("MESH", len([o for o in bpy.data.objects if o.type == "MESH"]))
print("AN", len([o for o in bpy.data.objects if o.name.startswith("AN_")]))
