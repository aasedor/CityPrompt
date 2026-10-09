"""Versioned finite building runner; refuses unreviewed or modified sources."""
import argparse
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
sys.path.append(str(HERE.parent/'catalogue_services_batch'))
sys.path.append(str(HERE.parent/'catalogue_affordable_five'))
import clay_core as C
from contract import source_entry


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--family',choices=['courtyard','seniors','health','market','transit'],required=True)
    p.add_argument('--source-review',type=Path,required=True)
    p.add_argument('--version',type=int,required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--resolution',type=int,default=1440)
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    import importlib
    family=importlib.import_module('family_'+a.family)
    source=source_entry(ROOT/'frontend/public/archetypes/buildings'/family.SLUG,
                        family.SLUG,json.loads(a.source_review.read_text(encoding='utf-8')))
    m=family.manifest(a.version)
    extra=[HERE/'contract.py',HERE/'geometry.py',Path(family.__file__),HERE.parent/'catalogue_affordable_five/assemblies.py']
    out=C.prepare_candidate(a,source,m,__file__,extra_scripts=extra)
    if out is None:return
    cameras=C.setup(family.PALETTE,m['camera_roster'],a.resolution)
    # Existing compact-house QA lights intersect these larger buildings.
    # Keep review illumination outside their complete envelopes.
    for name,position in [('key',(-35,-40,40)),('fill',(38,-18,35)),('rear',(-20,40,38))]:
        light=C.bpy.data.objects['QA '+name]
        light.location=position;light.data.energy*=5
        C.look_at(light,(0,0,5))
    # Furniture-scale bevels are retained selectively; thousands of tiny mortar
    # edges do not need their own modifiers.
    C.bevel=lambda *args,**kwargs:None
    print('AUTHORING_START '+m['candidate'],flush=True)
    family.build()
    print('AUTHORING_COMPLETE '+m['candidate'],flush=True)
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data)
        C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.deliver(out,m,cameras)


if __name__=='__main__':main()
