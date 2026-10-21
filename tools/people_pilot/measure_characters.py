"""Measure exported/skinned GLBs in Blender at 41 times per clip; artifact-only output."""
import bpy,pathlib,json,hashlib,struct,sys,math
from mathutils import Vector
root=pathlib.Path('C:/dev-artifacts/CityPrompt/people-video-pilot-2026-10-21/characters')
reports=[]
for path in sorted((root/'runtime').glob('*.glb')):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=24
 bpy.ops.import_scene.gltf(filepath=str(path));scene=bpy.context.scene
 rig=next(o for o in scene.objects if o.type=='ARMATURE')
 for track in rig.animation_data.nla_tracks:track.mute=True
 clip_reports=[]
 for action in bpy.data.actions:
  if action.name not in ['Walk','Idle']:continue
  rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
  samples=[]
  for k in range(41):
   frame=action.frame_range[0]+(action.frame_range[1]-action.frame_range[0])*k/40
   scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
   allp=[];shoes=[]
   for obj in scene.objects:
    if obj.type!='MESH' or not obj.vertex_groups:continue
    ev=obj.evaluated_get(dg);mesh=ev.to_mesh()
    ps=[ev.matrix_world@v.co for v in mesh.vertices];allp.extend(ps)
    if 'sneaker' in obj.name:shoes.extend(ps)
    ev.to_mesh_clear()
   lo=[min(v[i] for v in allp) for i in range(3)];hi=[max(v[i] for v in allp) for i in range(3)]
   foot_centers = {side:list(rig.matrix_world @ rig.pose.bones['foot_' + side].head) for side in ['l','r']}
   samples.append({'feetBlender':foot_centers,'t':round(frame/24,6),'min':lo,'max':hi,'shoeMinZ':min(v.z for v in shoes)})
  clip_reports.append({'name':action.name,'durationSeconds':float(action.frame_range[1]/24),'sampleCount':len(samples),'sampledMinFootZ':min(s['shoeMinZ'] for s in samples),'sampledMaxFootZ':max(s['shoeMinZ'] for s in samples),'samples':samples})
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);a=j['accessors']
 tris=sum(a[p['indices']]['count']//3 for m in j['meshes'] for p in m['primitives'])
 report={'id':path.stem,'file':str(path),'sha256':hashlib.sha256(b).hexdigest(),'byteSize':len(b),'triangleCount':tris,'materials':[m['name'] for m in j['materials']],'bones':len(rig.data.bones),'meshPrimitives':sum(len(m['primitives']) for m in j['meshes']),'bufferByteLength':sum(x['byteLength'] for x in j['buffers']),'accessorDecodedBytes':sum(x['count']*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[x['type']]*{5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[x['componentType']] for x in a),'images':j.get('images',[]),'clips':clip_reports}
 reports.append(report)
(root/'measurements.json').write_text(json.dumps(reports,indent=2))
for r in reports:print('MEASURED',r['id'],r['byteSize'],r['triangleCount'],[(c['name'],c['sampledMinFootZ'],c['sampledMaxFootZ']) for c in r['clips']])
