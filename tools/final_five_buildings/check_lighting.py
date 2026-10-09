"""Additional immutable evidence from exact GLB with exterior QA lights moved clear."""
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Vector

root=Path(sys.argv[sys.argv.index('--')+1]).resolve()
report=json.loads((root/'build-report.json').read_text())
out=root/'lighting-check';out.mkdir()
bpy.ops.wm.open_mainfile(filepath=str(root/report['authoring']['path']))
for obj in list(bpy.context.scene.objects):
    if obj.get('rlasm_building_object'):bpy.data.objects.remove(obj,do_unlink=True)
model=root/report['runtime']['path']
assert hashlib.sha256(model.read_bytes()).hexdigest()==report['runtime']['sha256']
bpy.ops.import_scene.gltf(filepath=str(model))
for name,position in [('key',(-35,-40,40)),('fill',(38,-18,35)),('rear',(-20,40,38))]:
    light=bpy.data.objects['QA '+name];light.location=position;light.data.energy*=5
    light.rotation_euler=(Vector((0,0,5))-light.location).to_track_quat('-Z','Y').to_euler()
records=[]
for name in ('right_side','roof_contact','courtyard','glass_close'):
    bpy.context.scene.camera=bpy.data.objects['QA '+name]
    path=out/(name+'.png');bpy.context.scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    records.append(dict(view=name,path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(out/'provenance.json').write_text(json.dumps(dict(model_sha256=report['runtime']['sha256'],
    operation='Exact GLB reimport. Only three external QA light positions/energy changed; no geometry/material/image edits.',
    records=records),indent=2))
