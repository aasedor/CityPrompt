"""Finite next-five source contract. No image generation or catalogue mutation."""
from pathlib import Path
import argparse
import hashlib
import json

SPECS = {
    'warehouse': dict(parent='modern_bigbox_warehouse',variant='warehouse_tilt_wall_mega',
        directory='modern_bigbox_warehouse',index=1,title='tilt-wall-warehouse',floors=3,
        dimensions=dict(width=144,depth=86,height=16.4),
        measurements=['One high-bay warehouse with three local office levels at the front-right glazed corner.',
            'Two long dock rows, pale concrete panel grid, flat membrane roof and sparse seated plant.'],
        assumptions=['Envelope preserved from services batch warehouse-v003; exact source identity checked afresh.',
            'Office programme is three levels; warehouse is one high industrial storey, never three complete floor plates.',
            'Dimensions and dock cadence inferred, not survey. Office circulation rebuilt to resolve independent review WH-01.',
            'Yard, trucks, gatehouse and public roads remain separate site objects.']),
    'tiltup': dict(parent='industrial_park_modernism', variant='industrial_tilt_up_concrete',
        directory='industrial_park_modernism', index=0, title='industrial-tilt-up-concrete', floors=2,
        dimensions=dict(width=54, depth=36, height=10.5),
        measurements=['Broad pale panelled concrete block; two office window bands on the front, repetitive grade-level loading doors on the right.',
            'Flat parapet roof, four raised corner ends, two HVAC units and three low roof hatches.',
            'Front canopy on two posts; front left office strip and taller clear-span industrial hall behind.'],
        assumptions=['Dimensions inferred from doors/storeys, not a survey.',
            'Front/oblique govern office and loading faces. Top governs rectangular roof, corner returns and sparse plant; rear loading is inferred from trucks in the top view.',
            'Office partitions, stair and hall structure are inferred. Context vehicles, roads and yard are separate site objects.']),
    'factory': dict(parent='daylight_factory', variant='factory_sawtooth_roof',
        directory='daylight_factory', index=0, title='daylight-sawtooth-factory', floors=1,
        dimensions=dict(width=49, depth=29, height=25),
        measurements=['Seven repeated asymmetric glazed roof teeth above a single brick industrial hall.',
            'Tall multi-pane arched-head windows, brick pilasters and dentilled cornice. Four front loading shutters beneath a supported canopy and raised dock.',
            'Freestanding round brick chimney at the right rear, with an open flue.'],
        assumptions=['Exact source views conflict: front/oblique seven roof teeth govern cadence; top six-band count is explicitly rejected, but its plan orientation and rear chimney location are retained.',
            'Nominal metres inferred from loading doors, not surveyed. Single industrial floor; roof glazing has open hall depth underneath.',
            'Rear windows and interior machinery are conceptual. Railway, trucks, streets and neighbouring sheds are excluded.'],
        source_gate='interpreted_reconciliation_recorded'),
    'admin': dict(parent='administrative_faculty_office_building', variant='admin_faculty_brick_bronze_fins',
        directory='administrative-faculty-office-building', index=0, title='brick-bronze-faculty-office', floors=5,
        dimensions=dict(width=34, depth=34, height=23.8),
        measurements=['Five-storey near-square brick office; narrow vertical window cadence on left front and side elevations.',
            'Full-height recessed entrance slot; projecting bronze-framed upper right corner with two broad window bays.',
            'Flat parapet roof with central rectangular plant enclosure and two screened end courts.'],
        assumptions=['Nominal dimensions inferred from doors and floor heights, not a survey.',
            'Five regular front-left bays and nine side bays reconcile partly occluded source windows.',
            'Rear facade, office rooms, stairwell and elevator core are inferred. No claim of a small low-rise office: this source is five storeys.']),
    'peaks': dict(parent='rndsqr_missing_middle_townhomes', variant='rndsqr_townhome_scandinavian_peaks',
        directory='rndsqr-missing-middle-townhomes', index=1, title='rndsqr-scandinavian-peaks-row', floors=4,
        dimensions=dict(width=33.6, depth=22, height=14.1),
        measurements=['Six attached front homes, each with an occupied glazed gable above three full storeys and a private front roof terrace.',
            'Alternating white walls, pale vertical ribs and framed timber bays; glazed wraparound right corner.',
            'Top view locks six front gables and three smaller rear roof pavilions on a broad flat roof.'],
        assumptions=['Metres inferred from doors and storeys, not surveyed. Fourth level is partially enclosed and cannot be counted as a three-storey building.',
            'Three rear pavilions are inferred shared service/storage rooms accessed from the flat roof; no duplicate houses inferred from background rows.',
            'Internal layouts and stairs are conceptual. Ground corner room is flexible occupied space; no automatic commercial-use permission.']),
}

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def source_entry(kind, source_root):
    s=SPECS[kind];root=Path(source_root)/'frontend/public/archetypes/buildings'/s['directory']
    entry=dict(archetype_id=s['parent'],variant_id=s['variant'],directory='.',_reference_root=str(root),sources=[])
    for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
        p=root/f'variant_{s["index"]}{suffix}';raw=p.read_bytes()
        if raw.startswith(b'version https://git-lfs.github.com/spec/v1'): raise ValueError(f'Unhydrated source: {p}')
        try: from PIL import Image
        except ModuleNotFoundError:
            import bpy
            im=bpy.data.images.load(str(p),check_existing=False);size=list(im.size)
            if min(size)<1: raise ValueError(f'Undecodable source: {p}')
            bpy.data.images.remove(im)
        else:
            with Image.open(p) as im:size=list(im.size);im.verify()
        entry['sources'].append(dict(archetype_id=s['parent'],variant_id=s['variant'],role=role,
            original_path=str(p),path='sources/'+p.name,bytes=len(raw),sha256=digest(p),dimensions_px=size))
    enrolled={Path(v['original_path']).name for v in entry['sources']}
    extras=[p.name for p in root.glob(f'variant_{s["index"]}*') if p.suffix.lower() in ('.png','.jpg','.jpeg') and p.name not in enrolled]
    if extras:raise ValueError(f'Additional views need compatibility review: {extras}')
    return entry

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);a=p.parse_args()
    print(json.dumps(dict(dry_run=True,generation_calls=0,candidates=[dict(kind=k,entry=source_entry(k,a.source_root),spec=s) for k,s in SPECS.items()]),indent=2))
