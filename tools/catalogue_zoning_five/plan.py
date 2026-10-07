"""Source-only preflight; works without Blender and never generates images."""
from pathlib import Path
import argparse
import hashlib
import json

SPECS = {
    'office': dict(parent='corporate_office_campus_headquarters', variant='neoclassical_brick_headquarters',
        directory='corporate-office-campus-headquarters', index=1, title='neoclassical-brick-office',
        floors=2, dimensions=dict(width=28.8, depth=33.4, height=21.2),
        measurements=['Square two-storey brick office; three sash bays each side of a central four-column portico.',
            'Six side bays, pale horizontal courses and corner quoins; truncated hip around a balustraded flat roof terrace.',
            'One central octagonal glazed cupola, copper dome and finial; front formal garden beds.'],
        assumptions=['Metres inferred from doorway and storey proportions; not a survey.',
            'Front and oblique establish windows; top establishes square body and terrace. Rear uses six matching bays with one service door.',
            'Interior offices, two-flight stair and furniture are conceptual; reference does not show a floor plan.',
            'Architectural clay retains physical facade hierarchy; carved pediment relief is simplified. No textured-keeper claim.']),
    'row': dict(parent='rndsqr_missing_middle_townhomes', variant='rndsqr_townhome_brick_contextual',
        directory='rndsqr-missing-middle-townhomes', index=2, title='rndsqr-brick-contextual-row',
        floors=3, dimensions=dict(width=25.2, depth=15.6, height=12.65),
        measurements=['Four complete attached three-storey homes identified by four roof-access pavilions in top view.',
            'Alternating red and buff brick bays, recessed charcoal vertical slots, framed timber upper bays, private rooftop decks.',
            'Ground-level doors and individual stoops; right corner has wraparound glazing. Adjacent rows in background are context.'],
        assumptions=['Metres inferred from door height, not survey. Three full storeys plus rooftop access rooms, not four full floors.',
            'Four-unit boundary taken from top view; partial extra bay at left in hero belongs beyond that boundary.',
            'Right corner glazed ground-floor room is a flexible studio; use classification is provisional, not an automatic commercial permission.',
            'Rear windows, stairs and room partitions inferred conservatively; roof access must connect to an actual stair opening.']),
    'school': dict(parent='ecole_republicaine', variant='ecole-republicaine-provincial-brick',
        directory='ecole-republicaine', index=2, title='provincial-brick-school', floors=3,
        dimensions=dict(width=33, depth=41, height=21),
        measurements=['Three-storey brick side wings and rear teaching wing around an open court.',
            'High front roof bridge over open facade gap; separate low street wall with arched gateway.',
            'Clock tower and bell cupola on front roof; raised dormers over both street pavilions.'],
        assumptions=['Documented source reconciliation: aerial governs roof graph and dormer positions; front governs curved dormer heads and standing seams.',
            'Aerial slate/tile finish conflicts with front metal roof and is not adopted. This is an interpreted source set, not a contradiction-free photographic record.',
            'Metres inferred from doors/storeys, not survey. Classroom partitions, furniture, stairs and unseen rear service entrances are conceptual.',
            'High front bridge has no invented occupied storey; court remains open below it.'],
        source_gate='interpreted_reconciliation_recorded'),
}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source_entry(kind, source_root):
    s=SPECS[kind]
    root=Path(source_root)/'frontend/public/archetypes/buildings'/s['directory']
    entry=dict(archetype_id=s['parent'],variant_id=s['variant'],directory='.',_reference_root=str(root),sources=[])
    for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
        p=root/f'variant_{s["index"]}{suffix}'
        raw=p.read_bytes()
        if raw.startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise ValueError(f'Unhydrated source: {p}')
        try:
            from PIL import Image
        except ModuleNotFoundError:
            import bpy
            im=bpy.data.images.load(str(p),check_existing=False)
            size=list(im.size)
            if min(size)<1: raise ValueError(f'Undecodable source: {p}')
            bpy.data.images.remove(im)
        else:
            with Image.open(p) as im:
                size=list(im.size); im.verify()
        entry['sources'].append(dict(archetype_id=s['parent'],variant_id=s['variant'],role=role,
            original_path=str(p),path='sources/'+p.name,bytes=len(raw),sha256=digest(p),dimensions_px=size))
    # Inventory extra views so a future addition cannot silently escape enrollment.
    enrolled={Path(v['original_path']).name for v in entry['sources']}
    extras=[p.name for p in root.glob(f'variant_{s["index"]}*') if p.suffix.lower() in ('.png','.jpg','.jpeg') and p.name not in enrolled]
    if extras:
        raise ValueError(f'Additional views need compatibility review: {extras}')
    return entry

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True)
    p.add_argument('--kind',choices=list(SPECS),action='append');a=p.parse_args()
    output=[]
    for kind in a.kind or list(SPECS):
        e=source_entry(kind,a.source_root)
        output.append(dict(kind=kind,variant=e['variant_id'],sources=len(e['sources']),
            source_gate=SPECS[kind].get('source_gate','builder_screened_independent_pending')))
    print(json.dumps(dict(dry_run=True,geometry_written=False,generation_calls=0,candidates=output),indent=2))

if __name__=='__main__': main()
