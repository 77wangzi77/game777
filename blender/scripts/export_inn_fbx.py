"""Open inn blend and export FBX with empties."""
import bpy, sys, os

argv = sys.argv
args = argv[argv.index('--')+1:] if '--' in argv else []
blend = args[0] if len(args)>0 else 'LV_01_inn_Blockout.blend'
fbx = args[1] if len(args)>1 else 'LV_01_inn_blockout_D3.fbx'

bpy.ops.wm.open_mainfile(filepath=blend)
# select all
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(
    filepath=fbx,
    use_selection=False,
    object_types={'MESH','EMPTY','ARMATURE'},
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    add_leaf_bones=False,
    axis_forward='-Z',
    axis_up='Y',
    apply_scale_options='FBX_SCALE_ALL',
    path_mode='AUTO',
)
print('EXPORTED', fbx, 'exists', os.path.exists(fbx), 'size', os.path.getsize(fbx) if os.path.exists(fbx) else 0)
# also dump anchor CSV next to fbx
import csv
csv_path = os.path.splitext(fbx)[0] + '_anchors.csv'
rows = [('id','x','y','z','collection')]
for o in bpy.data.objects:
    if o.type == 'EMPTY' or o.name.startswith('AN_') or o.name.startswith('ENV_Inn') or o.name.startswith('PROP_'):
        # parent collection
        cols = [c.name for c in o.users_collection]
        rows.append((o.name, f'{o.location.x:.3f}', f'{o.location.y:.3f}', f'{o.location.z:.3f}', '|'.join(cols)))
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    csv.writer(f).writerows(rows)
print('CSV', csv_path, 'rows', len(rows)-1)
