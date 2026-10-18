"""Build one finite source-locked native parkade, with immutable candidate evidence."""
import argparse,importlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'catalogue_services_batch'),str(HERE.parent/'final_five_buildings')]
import clay_core as C
import geometry as G
import build as P
import specs as S
from frame import standard_frame
from layout import frame_plan


def main():
    p=argparse.ArgumentParser();p.add_argument('--family',choices=['brick','green','solar','courtyard'],required=True)
    p.add_argument('--sources',type=Path,required=True);p.add_argument('--output',required=True)
    p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);family=importlib.import_module('family_'+a.family);s=family.SPEC
    entry=S.source_entry(a.sources);entry.update(archetype_id=s['slug'],variant_id=a.family+'-v1')
    review=json.loads((a.sources/'source-review.json').read_text(encoding='utf-8'))
    if review.get('compatible') is not True or review.get('unresolved_p0_p1_in_source_review_scope')!=[] or not {r['sha256'] for r in entry['sources']} <= {r['sha256'] for r in review.get('inspected_files',[])}:raise ValueError('Independent exact-source approval required')
    w,d,n=s['width'],s.get('frameDepth',s['depth']),s['levels'];f=frame_plan(w,d,n);h=f['towerHeight']
    cameras=G.camera_roster(w,s['depth'],h,[
        ('facade_close',(0,-d/2-25,h*.55),(0,-d/2,h*.45),48),
        ('architecture_close',(0,-10,1.8),(6,0,2),26),
        ('glass_close',(w/2+5,-d/2-8,h*.55),(w/2-2.5,-d/2+3.5,h*.5),40),
        ('ramp_headroom',(-w/2, d/2-10,5),(0,d/2-3.25,5),28),
        ('stair_contact',(w/2+3,-d/2-2,2.7),(w/2-2.5,-d/2+3,2),35),
        ('landing_seam',(w/2-7,-d/2+4,4.8),(w/2-4.8,-d/2+1,3.45),40),
        ('signature_close',(w*.42,-s['depth']*.7,h*1.3),(0,0,h*.7),48)])
    next(c for c in cameras if c['name']=='front_corner')['location']=(w*1.33,-s['depth']*2.5,h*3.3)
    m=dict(candidate=f'{s["slug"]}-clay-v{a.version:03d}',method=C.METHOD,archetype_id=s['slug'],variant_id=entry['variant_id'],
        representation_kind='architectural_clay',state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=w,depth=s['depth'],height=h),observed_storeys=n,floor_top_datums_m=f['datums'],ground_datum_m=0,axes='Author Z-up; exported GLB Y-up; frontage -Y author / +Z GLB'),
        programme_contract=dict(parking_levels=n,stair_towers=2,vehicle_ramps=n-1,ramp_clear_width_m=6,ramp_run_m=w-14,ramp_rise_m=3.3,ramp_clear_height_m=3.1,bay_dimensions_m=[2.7,5.5],main_aisle_width_m=6,no_operational_animation=True,engineering_approval=False,capacity_claimed=False),
        material_contract=dict(profile='texture-free source-palette architectural clay',textured_keeper=False),
        inference_contract=[s['description'],'Rear/side circulation and original architectural concept, no structural/accessibility/swept-path certification.'],
        runtime_contract=dict(scale='fixed_native_only',storeys='fixed_authored_assembly',review='NOT TESTED'),camera_roster=cameras,mandatory_review_views=[c['name'] for c in cameras],native_design=s)
    scripts=[HERE/x for x in ['specs.py','build.py','frame.py','layout.py','family_'+a.family+'.py']]
    for name in [a.family+'_sources.py','family_sources.py']:
        if (HERE/name).exists():scripts.append(HERE/name)
    scripts += [a.sources/'generation-provenance.json',a.sources/'source-review.json']
    if (a.sources/'design-contract.json').exists():scripts.append(a.sources/'design-contract.json')
    out=C.prepare_candidate(a,entry,m,__file__,extra_scripts=scripts)
    if out is None:return
    palette={**P.PALETTE,**dict(accent=(.55,.53,.43),timber=(.40,.31,.20),soil=(.22,.19,.12),foliage=(.20,.34,.19),planter=(.33,.40,.28)),**s.get('palette',{}),**getattr(family,'PALETTE',{})}
    cameras=C.setup(palette,cameras,a.resolution);C.bevel=lambda *args,**kwargs:None
    for name,position in [('key',(-w,-d*1.8,h*4.7)),('fill',(w,-d,h*3.5)),('rear',(-w,d*1.7,h*4))]:
        light=C.bpy.data.objects['QA '+name];light.location=position;light.data.energy*=18;light.data.size=35;C.look_at(light,(0,0,h/3))
    ctx=standard_frame(w,d,n,courtyard=s.get('courtyard'),marking_exclusions=s.get('marking_exclusions'),roof_lights=s.get('roof_lights',True))
    family.extra_geometry(ctx)
    for z in f['datums'][:-1]:
        for x in (-w*.3,0,w*.3):
            for y in (-8,6):C.qa_room_light('parking deck',(x,y,z+2.65),power=500,size=8)
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data);C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[q for q in bm.faces if q.calc_area()<=1e-10],context='FACES_ONLY');bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.deliver(out,m,cameras)


if __name__=='__main__':main()
