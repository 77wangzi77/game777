"""VRgame four-layer closed level graybox — Blender 5.x
Concept refs: docs/关卡概念/原画/清晰关卡0{1-4}_*.jpg + 四层连通总览
1 BU = 1 m. Naming: ENV_L0x_* / PROP_L0x_* / AN_* / LIT_*
Run:
  blender --background --python build_four_layer_blockout.py -- <out.blend>
"""
import bpy
import os
import sys
from math import radians

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0


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
        # Blender 4+/5 emission socket names vary
        for key in ("Emission Color", "Emission"):
            if key in bsdf.inputs and emission > 0:
                try:
                    bsdf.inputs[key].default_value = (*color, 1.0)
                except Exception:
                    pass
        if "Emission Strength" in bsdf.inputs and emission > 0:
            bsdf.inputs["Emission Strength"].default_value = emission
    return m


def cube(name, loc, scale, coll, material=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if material:
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    link(obj, coll)
    return obj


def cylinder(name, loc, radius, depth, coll, material=None, rot=(radians(90), 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=loc, rotation=rot
    )
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


def point_light(name, loc, coll, color=(1, 0.7, 0.4), energy=80, size=0.2):
    data = bpy.data.lights.new(name=name + "_data", type="POINT")
    data.color = color
    data.energy = energy
    data.shadow_soft_size = size
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    coll.objects.link(obj)
    return obj


M_STONE = mat("M_Block_Stone", (0.42, 0.42, 0.45))
M_ROCK = mat("M_Block_Rock", (0.28, 0.30, 0.33))
M_COLD = mat("M_Block_Cold", (0.32, 0.40, 0.55))
M_WARM = mat("M_Block_Warm", (0.55, 0.38, 0.28))
M_WOOD = mat("M_Block_Wood", (0.35, 0.22, 0.14))
M_ROOF = mat("M_Block_Roof", (0.12, 0.12, 0.14))
M_LAVA = mat("M_Block_Lava", (0.95, 0.28, 0.05), emission=3.0)
M_ALTAR = mat("M_Block_Altar", (0.62, 0.48, 0.32))
M_PATH = mat("M_Block_Path", (0.55, 0.55, 0.52))
M_GOLD = mat("M_Block_Gold", (0.75, 0.58, 0.25), emission=0.4)
M_PINE = mat("M_Block_Pine", (0.18, 0.32, 0.18))
M_WATER = mat("M_Block_Water", (0.45, 0.55, 0.65), emission=0.2)

root = collection("VRgame_FourLayer")
col_l1 = collection("ENV_L01_Mountain", root)
col_l2 = collection("ENV_L02_Bridge", root)
col_l3 = collection("ENV_L03_Magma", root)
col_l4 = collection("ENV_L04_Grotto", root)
col_conn = collection("ENV_Connectors", root)
col_anchors = collection("Anchors", root)
col_lit = collection("LIT", root)

# Vertical stack (Y up). ~18m floor-to-floor like concept slice.
Y1, Y2, Y3, Y4 = 0.0, 18.0, 36.0, 54.0

# ========== L1 Mountain · 清晰关卡01：洞口框景 → 崖径台阶 → 峰顶亭 ==========
# Outer rock shell (faceted massing)
cube("ENV_L01_CliffWall_Kit_Back", (0, Y1 + 6, 8), (18, 12, 2), col_l1, M_ROCK)
cube("ENV_L01_CliffWall_Kit_L", (-9, Y1 + 5, 0), (2, 10, 16), col_l1, M_ROCK)
cube("ENV_L01_CliffWall_Kit_R", (9, Y1 + 5, 0), (2, 10, 16), col_l1, M_ROCK)
cube("ENV_L01_CliffWall_Kit_Ceil", (0, Y1 + 11, 0), (18, 1.2, 16), col_l1, M_ROCK)
# Cave mouth frame (portal looking out — concept foreground)
cube("ENV_L01_CaveMouth_Top", (0, Y1 + 6.5, -8.2), (7, 1.2, 1.4), col_l1, M_STONE)
cube("ENV_L01_CaveMouth_L", (-3.8, Y1 + 3.5, -8.2), (1.2, 5, 1.4), col_l1, M_STONE)
cube("ENV_L01_CaveMouth_R", (3.8, Y1 + 3.5, -8.2), (1.2, 5, 1.4), col_l1, M_STONE)
cube("ENV_L01_CaveMouth_Sill", (0, Y1 + 0.4, -8.0), (7, 0.5, 2.0), col_l1, M_PATH)
# Winding cliff path / stairs (segmented)
cube("ENV_L01_CliffPath_A", (0, Y1 + 0.2, -5), (4.5, 0.35, 4), col_l1, M_PATH)
cube("ENV_L01_CliffPath_B", (2.2, Y1 + 1.0, -1.5), (3.5, 0.35, 3.5), col_l1, M_PATH)
cube("ENV_L01_Stair_Set_Lower", (1.5, Y1 + 1.8, 1.5), (2.2, 1.6, 3.0), col_l1, M_PATH)
cube("ENV_L01_Stair_Set_Mid", (0.2, Y1 + 3.2, 3.8), (2.0, 1.8, 2.5), col_l1, M_PATH)
cube("ENV_L01_PeakPlatform", (0, Y1 + 4.6, 5.5), (5.5, 0.4, 5.0), col_l1, M_PATH)
# Pavilion (柱+屋顶 proxy，古剑亭)
cube("ENV_L01_Pavilion_Post_FL", (-1.3, Y1 + 5.8, 4.5), (0.28, 2.2, 0.28), col_l1, M_WOOD)
cube("ENV_L01_Pavilion_Post_FR", (1.3, Y1 + 5.8, 4.5), (0.28, 2.2, 0.28), col_l1, M_WOOD)
cube("ENV_L01_Pavilion_Post_BL", (-1.3, Y1 + 5.8, 6.5), (0.28, 2.2, 0.28), col_l1, M_WOOD)
cube("ENV_L01_Pavilion_Post_BR", (1.3, Y1 + 5.8, 6.5), (0.28, 2.2, 0.28), col_l1, M_WOOD)
cube("ENV_L01_Pavilion_Deck", (0, Y1 + 4.85, 5.5), (3.2, 0.2, 2.8), col_l1, M_WOOD)
cube("ENV_L01_Pavilion_Roof", (0, Y1 + 7.2, 5.5), (4.0, 0.55, 3.6), col_l1, M_ROOF)
cube("ENV_L01_Pavilion_RoofRidge", (0, Y1 + 7.6, 5.5), (3.2, 0.25, 0.35), col_l1, M_ROOF)
# Pines + waterfall proxy
cube("PROP_L01_PineTree_A", (-4.2, Y1 + 3.8, 2.5), (0.7, 5.5, 0.7), col_l1, M_PINE)
cube("PROP_L01_PineTree_B", (4.0, Y1 + 4.5, 4.0), (0.6, 4.8, 0.6), col_l1, M_PINE)
cube("PROP_L01_Waterfall_FX", (6.5, Y1 + 4.0, 1.0), (0.8, 7.0, 1.5), col_l1, M_WATER)
cube("PROP_L01_PrayerTablet", (-2.0, Y1 + 5.3, 5.0), (0.15, 0.7, 0.4), col_l1, M_WOOD)
# Torches at mouth
point_light("LIT_L01_Torch_L", (-3.2, Y1 + 2.8, -7.2), col_lit, (1.0, 0.55, 0.25), 120)
point_light("LIT_L01_Torch_R", (3.2, Y1 + 2.8, -7.2), col_lit, (1.0, 0.55, 0.25), 120)
point_light("LIT_L01_Pavilion", (0, Y1 + 6.2, 5.5), col_lit, (1.0, 0.7, 0.35), 90)
empty("AN_Teleport_L01_Spawn", (0, Y1 + 1.0, -6.2), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Teleport_L01_PreAscent", (0, Y1 + 5.1, 5.2), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Look_L01_Ascent", (0, Y1 + 6.0, 7.2), col_anchors, "PLAIN_AXES", 0.4)
empty("AN_Look_L01_Moon", (0, Y1 + 9.0, -2), col_anchors, "PLAIN_AXES", 0.35)

# ========== L2 Bridge · 清晰关卡02：牌楼 → 三拱石桥 → 崖壁门楼 ==========
cube("ENV_L02_CanyonWall_L", (-8, Y2 + 6, 0), (2.0, 12, 18), col_l2, M_ROCK)
cube("ENV_L02_CanyonWall_R", (8, Y2 + 6, 0), (2.0, 12, 18), col_l2, M_ROCK)
cube("ENV_L02_CanyonCeil", (0, Y2 + 12, 0), (16, 1.2, 18), col_l2, M_ROCK)
cube("ENV_L02_MistPit", (0, Y2 - 3, 0), (12, 4, 12), col_l2, M_COLD)
# Paifang (multi-bay roof massing)
cube("ENV_L02_Paifang_Base", (0, Y2 + 1.2, -7.5), (6.5, 0.6, 2.2), col_l2, M_STONE)
cube("ENV_L02_Paifang_Col_L", (-2.4, Y2 + 3.2, -7.5), (0.45, 3.5, 0.45), col_l2, M_STONE)
cube("ENV_L02_Paifang_Col_R", (2.4, Y2 + 3.2, -7.5), (0.45, 3.5, 0.45), col_l2, M_STONE)
cube("ENV_L02_Paifang_Col_CL", (-0.8, Y2 + 3.0, -7.5), (0.35, 3.2, 0.35), col_l2, M_STONE)
cube("ENV_L02_Paifang_Col_CR", (0.8, Y2 + 3.0, -7.5), (0.35, 3.2, 0.35), col_l2, M_STONE)
cube("ENV_L02_Paifang_Roof", (0, Y2 + 5.4, -7.5), (7.2, 0.7, 3.0), col_l2, M_ROOF)
cube("ENV_L02_Paifang_RoofUpper", (0, Y2 + 6.2, -7.5), (5.0, 0.45, 2.2), col_l2, M_ROOF)
# Bridge deck + 3 arches
cube("ENV_L02_BridgeDeck", (0, Y2 + 1.15, 0), (3.2, 0.45, 13), col_l2, M_PATH)
for i, z in enumerate([-3.5, 0.0, 3.5]):
    cylinder(f"ENV_L02_BridgeArch_{i+1}", (0, Y2 + 0.2, z), 1.35, 3.0, col_l2, M_STONE, rot=(0, radians(90), 0))
cube("PROP_L02_Rail_Lion_L", (-1.75, Y2 + 1.7, 0), (0.22, 0.9, 11), col_l2, M_STONE)
cube("PROP_L02_Rail_Lion_R", (1.75, Y2 + 1.7, 0), (0.22, 0.9, 11), col_l2, M_STONE)
cube("PROP_L02_GuardianLion_L", (-2.2, Y2 + 2.0, -6.2), (0.7, 0.9, 0.7), col_l2, M_STONE)
cube("PROP_L02_GuardianLion_R", (2.2, Y2 + 2.0, -6.2), (0.7, 0.9, 0.7), col_l2, M_STONE)
for i, z in enumerate([-5, -2, 1, 4]):
    cube(f"PROP_L02_OilLamp_{i+1}", (-1.95, Y2 + 2.4, z), (0.18, 0.45, 0.18), col_l2, M_WARM)
    point_light(f"LIT_L02_Lamp_{i+1}", (-1.95, Y2 + 2.7, z), col_lit, (1.0, 0.6, 0.3), 60)
# Far gatehouse into cliff
cube("ENV_L02_FarGatehouse_Base", (0, Y2 + 2.0, 7.5), (7.0, 2.5, 4.5), col_l2, M_STONE)
cube("ENV_L02_FarGatehouse_Body", (0, Y2 + 5.5, 7.8), (6.0, 4.5, 3.8), col_l2, M_WOOD)
cube("ENV_L02_FarGatehouse_Roof", (0, Y2 + 8.4, 7.8), (7.2, 0.7, 4.5), col_l2, M_ROOF)
cube("ENV_L02_FarGatehouse_Roof2", (0, Y2 + 9.3, 7.8), (5.2, 0.5, 3.5), col_l2, M_ROOF)
cube("PROP_L02_Door_Double", (0, Y2 + 2.8, 5.6), (2.4, 3.2, 0.3), col_l2, M_WOOD)
point_light("LIT_L02_GateWarm", (0, Y2 + 3.5, 6.2), col_lit, (1.0, 0.65, 0.35), 140)
empty("AN_Teleport_L02_BridgeEntry", (0, Y2 + 1.5, -6.5), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Teleport_L02_Mid", (0, Y2 + 1.5, 0), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Teleport_L02_Gatehouse", (0, Y2 + 1.5, 5.5), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Look_L02_Forward", (0, Y2 + 3.0, 8.5), col_anchors, "PLAIN_AXES", 0.4)

# ========== L3 Magma · 清晰关卡03：玄武平台 / 岩浆河 / 封印门 ==========
cube("ENV_L03_CavernShell_FloorRim", (0, Y3 - 0.2, 0), (18, 0.6, 18), col_l3, M_ROCK)
cube("ENV_L03_CavernShell_L", (-9, Y3 + 5, 0), (1.5, 10, 16), col_l3, M_ROCK)
cube("ENV_L03_CavernShell_R", (9, Y3 + 5, 0), (1.5, 10, 16), col_l3, M_ROCK)
cube("ENV_L03_CavernShell_Back", (0, Y3 + 5, 8.5), (18, 10, 1.5), col_l3, M_ROCK)
cube("ENV_L03_CavernShell_Ceil", (0, Y3 + 10.5, 0), (18, 1.2, 16), col_l3, M_ROCK)
cube("ENV_L03_LavaRiver", (0, Y3 - 0.6, 0), (14, 0.5, 14), col_l3, M_LAVA)
# Platform maze
cube("ENV_L03_BasaltPlatform_A", (-4.5, Y3 + 1.0, -5), (5.5, 0.55, 4.0), col_l3, M_PATH)
cube("ENV_L03_BasaltPlatform_B", (1.5, Y3 + 1.3, -1.5), (3.5, 0.55, 3.0), col_l3, M_PATH)
cube("ENV_L03_BasaltPlatform_C", (-1.0, Y3 + 1.6, 3.0), (4.0, 0.55, 3.2), col_l3, M_PATH)
cube("ENV_L03_Walkway", (2.5, Y3 + 1.5, 1.0), (1.3, 0.35, 5.5), col_l3, M_PATH)
cube("PROP_L03_ChainBridge", (4.0, Y3 + 1.7, 4.5), (1.1, 0.22, 4.5), col_l3, M_STONE)
cube("ENV_L03_Stair_Basalt", (4.5, Y3 + 2.4, 6.2), (2.2, 2.0, 2.2), col_l3, M_PATH)
# Circular seal gate (cylinder + frame)
cylinder("ENV_L03_SealGate_Disk", (5.0, Y3 + 3.5, 7.6), 2.6, 0.6, col_l3, M_GOLD, rot=(0, 0, 0))
cube("ENV_L03_SealGate_Frame", (5.0, Y3 + 3.5, 8.0), (6.0, 6.0, 0.8), col_l3, M_STONE)
cube("PROP_L03_SpikeCrest", (5.0, Y3 + 6.6, 7.8), (3.5, 0.6, 0.5), col_l3, M_STONE)
cube("PROP_L03_Brazier_A", (-5.5, Y3 + 1.7, -4.5), (0.7, 0.9, 0.7), col_l3, M_LAVA)
cube("PROP_L03_Brazier_B", (0.5, Y3 + 2.2, 2.5), (0.6, 0.8, 0.6), col_l3, M_LAVA)
cube("PROP_L03_IronRail_L", (1.9, Y3 + 2.0, 1.0), (0.12, 0.7, 4.5), col_l3, M_STONE)
cube("PROP_L03_IronRail_R", (3.1, Y3 + 2.0, 1.0), (0.12, 0.7, 4.5), col_l3, M_STONE)
cube("PROP_L03_TalismanBanner", (3.5, Y3 + 4.0, 7.2), (0.1, 1.8, 0.8), col_l3, M_WARM)
point_light("LIT_L03_LavaFill", (0, Y3 + 0.5, 0), col_lit, (1.0, 0.35, 0.08), 400)
point_light("LIT_L03_Seal", (5.0, Y3 + 3.5, 6.5), col_lit, (1.0, 0.55, 0.2), 160)
empty("AN_Teleport_L03_Entry", (-4.5, Y3 + 1.5, -5.0), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Teleport_L03_Mid", (1.5, Y3 + 1.8, -1.2), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Teleport_L03_Seal", (4.5, Y3 + 2.0, 6.0), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Look_L03_SealGate", (5.0, Y3 + 3.8, 8.8), col_anchors, "PLAIN_AXES", 0.4)

# ========== L4 Grotto · 清晰关卡04：石殿 / 云龙柱 / 圆雕 / 祭坛 ==========
cube("ENV_L04_HallShell_L", (-7.5, Y4 + 5, 0), (1.5, 10, 14), col_l4, M_ROCK)
cube("ENV_L04_HallShell_R", (7.5, Y4 + 5, 0), (1.5, 10, 14), col_l4, M_ROCK)
cube("ENV_L04_HallShell_Back", (0, Y4 + 5, 7.2), (15, 10, 1.5), col_l4, M_ROCK)
cube("ENV_L04_HallShell_Ceil", (0, Y4 + 10.5, 0), (15, 1.2, 14), col_l4, M_ROCK)
cube("ENV_L04_CeilingRock", (0, Y4 + 9.2, 0), (8, 1.5, 6), col_l4, M_STONE)
cube("ENV_L04_FloorTiles", (0, Y4 + 0.12, 0), (13, 0.25, 12), col_l4, M_PATH)
# Cloud-dragon pillars
cylinder("ENV_L04_Pillar_CloudDragon_L", (-3.6, Y4 + 4.2, 2.5), 0.7, 8.0, col_l4, M_ALTAR, rot=(0, 0, 0))
cylinder("ENV_L04_Pillar_CloudDragon_R", (3.6, Y4 + 4.2, 2.5), 0.7, 8.0, col_l4, M_ALTAR, rot=(0, 0, 0))
cylinder("ENV_L04_CircularRelief", (0, Y4 + 4.5, 6.5), 2.8, 0.45, col_l4, M_GOLD, rot=(radians(90), 0, 0))
cube("ENV_L04_AltarDais", (0, Y4 + 0.7, 3.2), (4.5, 1.2, 3.2), col_l4, M_ALTAR)
cube("PROP_L04_AltarTable", (0, Y4 + 1.7, 3.2), (2.4, 0.55, 1.3), col_l4, M_WOOD)
cube("PROP_L04_BambooSlips_Stack", (0.9, Y4 + 2.15, 3.4), (0.9, 0.45, 0.55), col_l4, M_WARM)
cube("PROP_L04_IncenseBurner", (-0.7, Y4 + 2.15, 3.0), (0.35, 0.45, 0.35), col_l4, M_GOLD)
cube("PROP_L04_HangingLantern", (0, Y4 + 8.2, 0.5), (0.55, 0.9, 0.55), col_l4, M_WARM)
cube("PROP_L04_StoneLantern_L", (-5.2, Y4 + 1.3, -2.5), (0.55, 1.6, 0.55), col_l4, M_ALTAR)
cube("PROP_L04_StoneLantern_R", (5.2, Y4 + 1.3, -2.5), (0.55, 1.6, 0.55), col_l4, M_ALTAR)
cube("ENV_L04_SidePassage", (-6.2, Y4 + 2.2, -4.5), (2.2, 3.5, 4.5), col_l4, M_STONE)
cube("PROP_L04_CandleCluster", (1.4, Y4 + 2.0, 2.6), (0.5, 0.35, 0.5), col_l4, M_WARM)
point_light("LIT_L04_AltarGold", (0, Y4 + 3.5, 4.5), col_lit, (1.0, 0.75, 0.4), 200)
point_light("LIT_L04_Hang", (0, Y4 + 7.5, 0.5), col_lit, (1.0, 0.7, 0.4), 100)
empty("AN_Teleport_L04_Entry", (0, Y4 + 1.3, -5.2), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Teleport_L04_Altar", (0, Y4 + 2.0, 2.4), col_anchors, "SINGLE_ARROW", 0.8)
empty("AN_Look_L04_Altar", (0, Y4 + 2.8, 3.8), col_anchors, "PLAIN_AXES", 0.4)
empty("AN_Look_L04_Relief", (0, Y4 + 4.5, 6.8), col_anchors, "PLAIN_AXES", 0.35)
empty("AN_Save_L04", (4.2, Y4 + 1.3, -4.0), col_anchors, "SPHERE", 0.5)

# ========== Connectors ==========
cube("ENV_C12_AscentShaft", (0, (Y1 + Y2) / 2 + 1, 6.5), (3.2, 12, 3.2), col_conn, M_COLD)
cube("ENV_C23_GateShaft", (0, (Y2 + Y3) / 2 + 1, 7.5), (3.2, 12, 3.2), col_conn, M_WARM)
cube("ENV_C34_SealShaft", (5.0, (Y3 + Y4) / 2 + 1, 7.5), (3.2, 12, 3.2), col_conn, M_ALTAR)
empty("AN_Teleport_C12", (0, (Y1 + Y2) / 2 + 1, 6.5), col_anchors, "SINGLE_ARROW", 0.6)
empty("AN_Teleport_C23", (0, (Y2 + Y3) / 2 + 1, 7.5), col_anchors, "SINGLE_ARROW", 0.6)
empty("AN_Teleport_C34", (5.0, (Y3 + Y4) / 2 + 1, 7.5), col_anchors, "SINGLE_ARROW", 0.6)

# Viewport sun + overview camera (side slice like concept)
sun = bpy.data.lights.new(name="LIT_Viewport_Sun", type="SUN")
sun.energy = 1.6
sun_obj = bpy.data.objects.new("LIT_Viewport_Sun", sun)
bpy.context.scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (radians(55), radians(15), radians(25))

cam_data = bpy.data.cameras.new("CAM_Overview")
cam_data.lens = 35
cam = bpy.data.objects.new("CAM_Overview", cam_data)
bpy.context.scene.collection.objects.link(cam)
cam.location = (32, 28, -30)
cam.rotation_euler = (radians(72), 0.0, radians(48))
scene.camera = cam

out_path = None
argv = sys.argv
if "--" in argv:
    args = argv[argv.index("--") + 1 :]
    if args:
        out_path = args[0]
if not out_path:
    out_path = os.path.join(os.getcwd(), "VRgame_L01_L04_Blockout.blend")
os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=out_path)
print("SAVED", out_path)
print("OBJECTS", len(bpy.data.objects))
print("MESHES", len([o for o in bpy.data.objects if o.type == "MESH"]))
print("ANCHORS", len([o for o in bpy.data.objects if o.name.startswith("AN_")]))
