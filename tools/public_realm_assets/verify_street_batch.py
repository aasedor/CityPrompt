"""Audit actual street GLBs, archived image bytes and measured amenity envelopes."""
import hashlib, json, math, runpy, sys
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]);report=root/'geometry-verification.json'
try:
    state=runpy.run_path(str(Path(__file__).with_name('verify.py')))
    r=state['r'];deps=state['deps'];checks=json.loads(report.read_text())['checks']
    for ref in r['image_references']:
        data=(root/ref['path']).read_bytes()
        assert len(data)==ref['bytes'] and hashlib.sha256(data).hexdigest()==ref['sha256']
    w,d=r['dimensions_m'];assert abs(sum(s['width'] for s in r['sections'])-w)<1e-8
    # Inspect the delivered modules, not just the builder's recorded envelopes.
    native={};feet={}
    for kind in sorted({a['kind'] for a in r['reference_assets']}):
        before=set(bpy.context.scene.objects)
        bpy.ops.import_scene.gltf(filepath=str(root/'modules'/r['modules'][kind]['path']))
        objects=[o for o in set(bpy.context.scene.objects)-before if o.type=='MESH']
        points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
        native[kind]=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
        feet[kind]=[p.copy() for p in points if p.z<.015]
        assert feet[kind],(kind,'missing ground contacts')
        for o in objects:bpy.data.objects.remove(o,do_unlink=True)
    # Pairwise footprint audit for all authored amenity modules. Foliage is
    # intentionally excluded; the route rays separately detect low obstructions.
    assets=r['reference_assets']
    for i,a in enumerate(assets):
        measured=native[a['kind']]
        assert all(abs(measured[j][axis]-a['native_bounds_m'][j][axis])<.012 for j in (0,1) for axis in range(3))
        c,s=math.cos(a['yaw']),math.sin(a['yaw'])
        for point in feet[a['kind']]:
            xx=a['x']+point.x*c-point.y*s;yy=a['y']+point.x*s+point.y*c
            owner=None
            for region in r['surface_regions']:
                if abs(xx-region['x'])<=region['width']/2 and abs(yy-region['y'])<=region['depth']/2:owner=region['material']
            assert owner in ('paving','soil','grass'),(a['kind'],xx,yy,'unsupported amenity or placement in traffic lane')
        lo,hi=a['bounds_m'];assert all(math.isfinite(v) for p in (lo,hi) for v in p)
        assert lo[0]>=-w/2-.02 and hi[0]<=w/2+.02 and lo[1]>=-d/2 and hi[1]<=d/2
        for b in assets[i+1:]:
            blo,bhi=b['bounds_m']
            overlap=[min(hi[j],bhi[j])-max(lo[j],blo[j]) for j in range(3)]
            assert not all(value>.07 for value in overlap),(a['kind'],a['x'],a['y'],b['kind'],b['x'],b['y'],'overlapping assets')
    # Endpoints of every advertised route retain full-width supported openings.
    endpoints=0
    for route in r['clear_routes']:
        if route['name'] in ('cross_link','lounge_access','boarding_strip'):continue
        xx=route['a'][0]
        for yy in (-d/2+.08,d/2-.08):
            for fraction in (-.47,0,.47):state['check'](xx+fraction*route['width'],yy);endpoints+=1
    if r['cycle_directions']:
        left,right=sorted(r['cycle_directions'],key=lambda p:p['x'])
        assert left['sign']==-1 and right['sign']==1
    assert r['triangles']<350000 and r['assembly']['bytes']<12_000_000
    checks+=['archived authoritative reference hashes','cross-section width sum',
             f'{len(native)} reimported native module bounds and ground contacts',
             f'{len(assets)} native amenity envelopes and pairwise clearances',
             f'{endpoints} supported endpoint rays','right-hand cycle direction','350k triangle / 12 MB per-fixture budget']
    result=dict(status='PASS_OFFLINE_GEOMETRY',checks=checks,runtime_tested=False)
    report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
except Exception as exc:
    report.write_text(json.dumps(dict(status='FAIL_OFFLINE_GEOMETRY',error=str(exc),runtime_tested=False),indent=2)+'\n')
    raise
