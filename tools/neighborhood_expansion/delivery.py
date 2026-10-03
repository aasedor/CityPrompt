"""Shared source-lock, exact-GLB export and evidence pipeline; no composition."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import bpy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'neighborhood_refinement'))
import geometry_core as C
import build_neighborhood as B
import refinements as R
import walking as W


def run(builder,spec_name,candidate_prefix,palette,cameras,construct,network,brick_tile,tile_m):
    p=argparse.ArgumentParser();p.add_argument('--output-root',type=Path,required=True)
    p.add_argument('--version',default='v001');p.add_argument('--resolution',type=int,default=1280)
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=a.output_root.resolve()
    spec=json.loads((HERE/spec_name).read_text(encoding='utf-8'))
    for s in spec['sources']:
        q=Path(s['path']);assert q.stat().st_size==s['bytes'] and C.digest(q)==s['sha256']
    candidate=candidate_prefix+'-'+a.version;out=root/candidate;camspec=cameras()
    if a.dry_run:
        print(json.dumps(dict(candidate=candidate,sources=len(spec['sources']),cameras=len(camspec),geometry_written=False)));return
    out.mkdir(parents=True,exist_ok=False)
    for n in ('sources','scripts','textures','renders','review','evidence','boards'):(out/n).mkdir()
    sources=[]
    for s in spec['sources']:
        q=Path(s['path']);shutil.copy2(q,out/'sources'/q.name)
        sources.append(dict(s,original_path=str(q),path='sources/'+q.name))
    for f in (Path(builder),Path(__file__),HERE/spec_name,Path(C.__file__),Path(B.__file__),Path(R.__file__),Path(W.__file__)):
        shutil.copy2(f,out/'scripts'/f.name)
    tex=root/'materials'/brick_tile;shutil.copy2(tex,out/'textures'/tex.name)
    provenance=root/spec['generation_provenance'];shutil.copy2(provenance,out/'sources/generation-provenance.json')
    manifest=dict(spec,candidate=candidate,state='building',source_contract=dict(sources=sources,front_is_primary=True),
        camera_roster=camspec,mandatory_review_views=[c['name'] for c in camspec],
        provenance=dict(scripts=[dict(path='scripts/'+f.name,sha256=C.digest(f)) for f in (out/'scripts').iterdir()],blender_version=bpy.app.version_string),
        material_authority=dict(path='textures/'+tex.name,sha256=C.digest(tex),tile_metres=tile_m,scope='Exact-family conditioned albedo; remaining palette finishes are prototype limitations'))
    B.write(out/'prework-manifest.json',manifest)
    cams=C.setup(palette,camspec,a.resolution);bpy.context.scene.cycles.samples=24
    # Disable specular contribution of nonarchitectural QA lamps explicitly.
    for obj in bpy.context.scene.objects:
        if obj.type=='LIGHT' and hasattr(obj.data,'specular_factor'):obj.data.specular_factor=0
    bs=C.MATS['glass'].node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value=(.96,.98,.98,1);bs.inputs['Alpha'].default_value=1
    bs.inputs['Transmission Weight'].default_value=1;bs.inputs['Roughness'].default_value=.035;bs.inputs['IOR'].default_value=1.45
    if 'lamp' in C.MATS:
        bs=C.MATS['lamp'].node_tree.nodes['Principled BSDF'];bs.inputs['Emission Color'].default_value=(1,.86,.65,1);bs.inputs['Emission Strength'].default_value=1.5
    m=C.MATS['wall'];m['texture_free']=False;m['source_conditioned']=True
    texnode=m.node_tree.nodes.new('ShaderNodeTexImage');texnode.image=bpy.data.images.load(str(tex));texnode.image.pack()
    m.node_tree.links.new(texnode.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    construct();bpy.context.view_layer.update();net=network();B.write(out/'evidence/walking-network.json',net)
    B.uv_all()
    for o in C.objects():
        if o.get('cityprompt_semantic_role')=='wall':
            for uv in o.data.uv_layers.active.data:uv.uv.x*=2.4/tile_m[0];uv.uv.y*=2.4/tile_m[1]
        o['archetype_id']=spec['archetype_id'];o['variant_id']=spec['variant_id']
    original=C.bounds(C.objects());assert abs(original[0][2])<.001,original
    audit=C.aperture_audit();B.write(out/'evidence/carrier-aperture-audit.json',audit)
    for c in camspec:
        if c['whole']:C.fit(cams[c['name']],c['target'])
    bpy.context.scene.camera=cams['front_corner'];bpy.ops.wm.save_as_mainfile(filepath=str(out/(candidate+'.blend')))
    for role in C.MATS:
        group=[o for o in C.objects() if o.get('cityprompt_semantic_role')==role]
        if not group:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in group:o.select_set(True)
        bpy.context.view_layer.objects.active=group[0]
        if len(group)>1:bpy.ops.object.join()
        bpy.context.object.name=role
    W.embed(net);glb=out/(candidate+'.glb');bpy.ops.object.select_all(action='DESELECT')
    for o in C.objects():o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_yup=True)
    payload=C.glb_json(glb)
    for o in list(C.objects()):bpy.data.objects.remove(o,do_unlink=True)
    old=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(glb))
    imported=[o for o in bpy.context.scene.objects if o not in old and o.type=='MESH']
    for o in imported:o['rlasm_building_object']=True
    bpy.context.view_layer.update();actual=C.bounds(imported)
    delta=max(abs(actual[i][j]-original[i][j]) for i in range(2) for j in range(3));assert delta<.001
    for c in camspec:
        bpy.context.scene.camera=cams[c['name']];bpy.context.scene.render.filepath=str(out/'renders'/(c['name']+'.png'))
        bpy.ops.render.render(write_still=True);print('RENDER_COMPLETE '+c['name'],flush=True)
    report=dict(candidate=candidate,status='build_valid',keeper_claimed=False,runtime_activated=False,generic_fallback_count=0,
        materials_scope='Source-conditioned masonry albedo; remaining finishes use a declared prototype palette, full keeper not claimed',
        glb=dict(path=glb.name,bytes=glb.stat().st_size,sha256=C.digest(glb),meshes=len(payload['meshes']),textures=len(payload.get('textures',[])),**C.metrics(imported)),
        native_bounds_m=actual,max_roundtrip_delta_m=delta,carrier_aperture_audit=audit['status'],opening_count=len(C.OPENINGS),
        render_source='exact exported GLB reimport without substitution',independent_review='pending')
    B.write(out/'build-report.json',report);B.write(out/'evidence/builder-evidence.json',report)
    print('BUILD_COMPLETE '+json.dumps(report),flush=True)
