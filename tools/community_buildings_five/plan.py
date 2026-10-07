"""Finite exact-reference community building batch, October 2026."""
from pathlib import Path
import hashlib

SPECS = {
    'grocer': dict(parent='montreal_depanneur', variant='montreal_depanneur_modern',
        directory='montreal-depanneur', index=3, title='brick-corner-grocery', label='Brick Corner Grocery',
        floors=2, dimensions=dict(width=11.4, depth=12.4, height=7.9),
        measurements=['Two-storey nearly square brick corner building with three tall upper windows on each street elevation.',
            'Ground-floor corner alone is chamfered; the upper corner and flat roof stay square.',
            'Two broad front shop windows, one side shop window, wraparound fascia, and separate narrow front entrance.'],
        assumptions=['Metric scale inferred from door and storey proportions, not a survey.',
            'Rear and party-wall-facing windows, retail fixtures and internal stair are inferred.',
            'Upper floor is one conceptual dwelling above a small grocery. No alcohol, tobacco or restaurant programme assumed.',
            'Snow, surrounding houses and street trees are context and excluded. Flat roof is not an occupied terrace.']),
    'hall': dict(parent='civic_modernism_rec_centre',variant='rec_clerestory_modern',directory='civic_modernism_rec_centre',index=2,
        title='clerestory-neighbourhood-hall',label='Clerestory Neighbourhood Hall',floors=1,dimensions=dict(width=26,depth=27,height=7.0),
        measurements=['One tall white hall with continuous high clerestory and broad shallow roof overhang.',
            'Slender inclined perimeter supports carry the deep timber soffit.',
            'Lower dark-brick L-wing joins through a recessed glazed entrance connector; two distinct roof fields.'],
        assumptions=['Metres inferred from door proportions. Clerestory is not a second occupied storey.',
            'Public community recreation programme, meeting tables and activity floor are inferred; no regulation sports court claimed.',
            'Rear service openings and internal support rooms are inferred. Neighbouring school blocks and roadway are context.']),
    'cabin': dict(parent='parkitecture_recreational',variant='rec_log_cabin_vernacular',directory='parkitecture_recreational',index=1,
        title='log-recreation-cabin',label='Log Recreation Cabin',floors=1,dimensions=dict(width=12,depth=11.5,height=6.0),
        measurements=['Single-storey horizontal log hall on a stone base with full-width front porch and four timber posts.',
            'Gable ridge runs across the frontage; front roof slope changes pitch over the porch.',
            'One left-side masonry chimney, front central door with two shuttered windows, paired side windows.'],
        assumptions=['Metric dimensions inferred from doors; not a survey. Rear opening schedule and indoor activity programme inferred.',
            'Day-use recreation shelter, no overnight accommodation assumed. Fireplace is an unlit concept feature.',
            'Log and shingle depth is geometric clay; not textured wood or final stone material. Surrounding forest and fence are site context.']),
    'inglewood': dict(parent='inglewood_heritage_brick_commercial',variant='inglewood_deco_infill',directory='inglewood-heritage-brick-commercial',index=2,
        title='inglewood-corner-merchants',label='Inglewood Corner Merchants',floors=2,dimensions=dict(width=14.5,depth=17.5,height=11.0),
        measurements=['Two-storey red brick corner block with three broad segmental-arched ground-floor bays on each street elevation.',
            'Upper paired sash windows flank central balcony doors; supported balconies on front and right side.',
            'Decorated parapet, central roof skylight and rear roof-access room; flat rectangular plan.'],
        assumptions=['Visible Edwardian-style reference governs geometry despite legacy variant name deco.',
            'Metric scale, concealed rear openings, upper offices and connected internal stair are inferred.',
            'Retail ground floor and offices above; no restaurant or residential occupancy assumed. Roof is service access, not a public terrace.']),
    'shops': dict(parent='commercial_strip_mall',variant='strip_weathered_1980s',directory='commercial-strip-mall',index=3,
        title='prairie-neighbourhood-shops',label='Prairie Neighbourhood Shops',floors=1,dimensions=dict(width=30,depth=22,height=5.8),
        measurements=['Four one-storey shop units below a shallow shingled false-mansard fascia.',
            'Beige storefront piers, timber vertical sign band, glazed doors and paired display windows.',
            'Flat main roof, metal side walls, two rooftop mechanical units and smaller ventilation terminals.'],
        assumptions=['Metric size inferred from doors; surrounding parking and road must be designed by students.',
            'Teaching tenants are deli, hardware, liquor retail and gifts as in references; each component needs its own use screening.',
            'Internal tenant partitions, fixtures, rear service doors and roof maintenance access are inferred. No occupied upper floor.']),
}

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def source_entry(kind, source_root):
    s=SPECS[kind]
    root=Path(source_root)/'frontend/public/archetypes/buildings'/s['directory']
    entry=dict(archetype_id=s['parent'],variant_id=s['variant'],_reference_root=str(root),sources=[])
    for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
        p=root/f'variant_{s["index"]}{suffix}'
        raw=p.read_bytes()
        if raw.startswith(b'version https://git-lfs.github.com/spec/v1'): raise ValueError('Unhydrated source '+str(p))
        try:
            from PIL import Image
        except ModuleNotFoundError:
            import bpy
            im=bpy.data.images.load(str(p),check_existing=False);size=list(im.size);bpy.data.images.remove(im)
        else:
            with Image.open(p) as im: size=list(im.size); im.verify()
        entry['sources'].append(dict(archetype_id=s['parent'],variant_id=s['variant'],role=role,
            original_path=str(p),path='sources/'+p.name,bytes=len(raw),sha256=digest(p),dimensions_px=size))
    enrolled={Path(v['original_path']).name for v in entry['sources']}
    extras=[p.name for p in root.glob(f'variant_{s["index"]}*') if p.suffix.lower() in ('.png','.jpg','.jpeg') and p.name not in enrolled]
    if extras: raise ValueError('Additional source roles require review: '+str(extras))
    return entry
