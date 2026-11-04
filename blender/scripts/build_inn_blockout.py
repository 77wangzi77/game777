"""LV_01_inn seven-zone graybox. ENV_Inn_* naming. Blender 5.x"""
import bpy, sys, os
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

def coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c

def link(obj, c):
    for x in list(obj.users_collection):
        x.objects.unlink(obj)
    c.objects.link(obj)

def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes.get('Principled BSDF')
    if n:
        n.inputs['Base Color'].default_value = (*rgb, 1)
        if 'Roughness' in n.inputs:
            n.inputs['Roughness'].default_value = 0.85
    return m

def cube(name, loc, scale, c, m=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if m:
        if o.data.materials: o.data.materials[0]=m
        else: o.data.materials.append(m)
    link(o, c)
    return o

def empty(name, loc, c, etype='PLAIN_AXES', size=0.5):
    bpy.ops.object.empty_add(type=etype, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.empty_display_size = size
    link(o, c)
    return o

M_STONE = mat('M_Inn_Stone', (0.5, 0.48, 0.45))
M_COLD = mat('M_Inn_Cold', (0.4, 0.45, 0.55))
M_WARM = mat('M_Inn_Warm', (0.55, 0.4, 0.28))
M_PATH = mat('M_Inn_Path', (0.55, 0.52, 0.48))
M_PROP = mat('M_Inn_Prop', (0.6, 0.5, 0.35))

root = coll('LV_01_inn')
c_porch = coll('ENV_Inn_Porch', root)
c_hall = coll('ENV_Inn_Hall', root)
c_wing = coll('ENV_Inn_Wing', root)
c_upper = coll('ENV_Inn_Upper', root)
c_yard = coll('ENV_Inn_Yard', root)
c_kit = coll('ENV_Inn_Kitchen', root)
c_bam = coll('ENV_Inn_Bamboo', root)
c_an = coll('Anchors', root)
c_col = coll('Colliders', root)

# Layout along +Y as forward into inn: Porch(z=-8) -> Hall(0) -> Wing(+X) Upper(+Y) Yard(+Z) Kitchen(-X) Bamboo(+Z far)
# Use Y-up; Z depth into building

# PORCH
cube('ENV_Inn_Porch_Floor', (0, 0.05, -8), (6, 0.1, 4), c_porch, M_PATH)
cube('ENV_Inn_Porch_Rail_L', (-2.8, 0.6, -8), (0.15, 1.0, 3.5), c_porch, M_STONE)
cube('ENV_Inn_Porch_Rail_R', (2.8, 0.6, -8), (0.15, 1.0, 3.5), c_porch, M_STONE)
cube('ENV_Inn_Porch_DoorFrame', (0, 1.5, -6), (2.2, 2.8, 0.4), c_porch, M_STONE)
cube('PROP_Inn_WindChime', (-1.2, 2.2, -7), (0.2, 0.5, 0.2), c_porch, M_PROP)
empty('AN_Teleport_spawn', (0, 0.2, -9), c_an, 'SINGLE_ARROW', 0.8)
empty('AN_Look_UI_menu', (1.5, 1.5, -8), c_an, 'PLAIN_AXES', 0.4)
empty('AN_Look_UI_dialogue', (0, 1.5, -6.5), c_an, 'PLAIN_AXES', 0.4)
empty('AN_Trigger_bell', (-1.2, 1.6, -7), c_an, 'CUBE', 0.4)

# HALL
cube('ENV_Inn_Hall_Floor', (0, 0.05, 0), (8, 0.1, 8), c_hall, M_PATH)
cube('ENV_Inn_Hall_Wall_N', (0, 2, 4), (8, 4, 0.3), c_hall, M_WARM)
cube('ENV_Inn_Hall_Wall_S', (0, 2, -4), (8, 4, 0.3), c_hall, M_WARM)
cube('ENV_Inn_Hall_Wall_W', (-4, 2, 0), (0.3, 4, 8), c_hall, M_WARM)
cube('ENV_Inn_Hall_Wall_E', (4, 2, 0), (0.3, 4, 8), c_hall, M_WARM)
# door holes approximated by not blocking porch connection - open south wall center already has frame
cube('ENV_Inn_Hall_HostPad', (-2, 0.15, 1.5), (1.2, 0.2, 1.2), c_hall, M_STONE)
cube('ENV_Inn_Hall_GuestPad', (2, 0.15, 1.5), (1.2, 0.2, 1.2), c_hall, M_STONE)
empty('AN_Teleport_hall', (0, 0.2, 0), c_an, 'SINGLE_ARROW', 0.8)
empty('AN_Look_host', (-2, 1.5, 1.5), c_an, 'PLAIN_AXES', 0.4)
empty('AN_Look_guest', (2, 1.5, 1.5), c_an, 'PLAIN_AXES', 0.4)
empty('AN_Look_UI_choice', (0, 1.5, -1), c_an, 'PLAIN_AXES', 0.4)

# WING (+X)
cube('ENV_Inn_Wing_Floor', (7, 0.05, 0), (4, 0.1, 5), c_wing, M_PATH)
cube('ENV_Inn_Wing_Wall', (9, 1.5, 0), (0.3, 3, 5), c_wing, M_STONE)
cube('PROP_Inn_Clue_RedHerring', (7.5, 1.1, 1), (0.4, 0.15, 0.3), c_wing, M_PROP)
cube('PROP_Inn_Clue_Mud', (8, 1.1, -1), (0.35, 0.15, 0.25), c_wing, M_PROP)
empty('AN_Teleport_wing', (6.5, 0.2, 0), c_an, 'SINGLE_ARROW', 0.7)
empty('AN_Trigger_prop_redherring', (7.5, 1.1, 1), c_an, 'CUBE', 0.35)
empty('AN_Trigger_prop_mud', (8, 1.1, -1), c_an, 'CUBE', 0.35)

# UPPER (+Y back, raised)
cube('ENV_Inn_Upper_Floor', (0, 3.05, 7), (5, 0.1, 4), c_upper, M_PATH)
cube('ENV_Inn_Upper_LockBox', (0, 3.5, 7), (0.8, 0.8, 0.4), c_upper, M_STONE)
cube('PROP_Inn_Clue_Scrap', (0.5, 3.9, 7.5), (0.5, 0.05, 0.35), c_upper, M_PROP)
empty('AN_Teleport_upper', (0, 3.2, 6), c_an, 'SINGLE_ARROW', 0.7)
empty('AN_Trigger_prop_scrap', (0.5, 3.9, 7.5), c_an, 'CUBE', 0.35)
empty('AN_Look_lock', (0, 3.7, 7), c_an, 'PLAIN_AXES', 0.35)

# YARD (+Z beyond hall via east? put at z=10)
cube('ENV_Inn_Yard_Floor', (0, 0.05, 12), (7, 0.1, 6), c_yard, M_COLD)
cube('PROP_Inn_Box_Fake', (0, 0.7, 12), (0.8, 0.6, 0.8), c_yard, M_PROP)
empty('AN_Teleport_yard', (0, 0.2, 10), c_an, 'SINGLE_ARROW', 0.7)
empty('AN_Trigger_prop_box', (0, 0.8, 12), c_an, 'CUBE', 0.4)

# KITCHEN (-X)
cube('ENV_Inn_Kitchen_Floor', (-7, 0.05, 0), (4, 0.1, 5), c_kit, M_WARM)
cube('ENV_Inn_Kitchen_Hearth', (-8, 0.8, 1), (1.2, 1.2, 1.2), c_kit, M_WARM)
cube('PROP_Inn_Note_Kitchen', (-7.2, 1.1, -1), (0.4, 0.05, 0.3), c_kit, M_PROP)
empty('AN_Teleport_kitchen', (-6, 0.2, 0), c_an, 'SINGLE_ARROW', 0.7)
empty('AN_Look_mute', (-7.5, 1.5, 0.5), c_an, 'PLAIN_AXES', 0.4)
empty('AN_Trigger_prop_note', (-7.2, 1.1, -1), c_an, 'CUBE', 0.35)

# BAMBOO exit far +Z
cube('ENV_Inn_Bamboo_Shell', (0, 2, 20), (6, 4, 4), c_bam, M_COLD)
cube('ENV_Inn_Bamboo_Path', (0, 0.05, 18), (2, 0.1, 6), c_bam, M_PATH)
empty('AN_Teleport_exit', (0, 0.2, 18), c_an, 'SINGLE_ARROW', 0.8)
empty('AN_Trigger_outro', (0, 1.0, 20), c_an, 'CUBE', 0.6)

# simple collider proxies for voids
cube('PROP_Collider_PorchEdge', (0, 0.5, -10.5), (7, 1, 0.3), c_col, M_STONE)
cube('PROP_Collider_YardEdge', (0, 0.5, 15.5), (8, 1, 0.3), c_col, M_STONE)

light = bpy.data.lights.new('LIT_Inn_Viewport', 'SUN')
light.energy = 2
lo = bpy.data.objects.new('LIT_Inn_Viewport', light)
bpy.context.scene.collection.objects.link(lo)
lo.rotation_euler = (0.9, 0.2, 0.3)

out = None
argv = sys.argv
if '--' in argv:
    a = argv[argv.index('--')+1:]
    if a: out = a[0]
if not out:
    out = os.path.join(os.getcwd(), 'LV_01_inn_Blockout.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
print('SAVED', out)
print('OBJECTS', len(bpy.data.objects))
print('COLLECTIONS', [c.name for c in bpy.data.collections])
