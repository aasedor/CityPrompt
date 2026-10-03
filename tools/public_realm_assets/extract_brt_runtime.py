"""Recover semantic BRT modules from the exact brt-v004 authoring file.

Run with Blender --background --disable-autoexec --python this_file --
--source PATH --output PATH [--dry-run]. Never saves or modifies the original.
Derived assets remain candidates until reconstructed-source and app checks pass.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

AUTHORING_SHA = '60f1652d7d5c4257ee9aeca5ffc2ba4bb259e37c3fe0aeae684648c8902547a7'
STATION_GROUPS = {
    'raised island platform', 'platform accessible approach', 'continuous tactile tile strip',
    'boarding tactile studs', 'shelter post base', 'shelter main post', 'canopy cantilever',
    'canopy longitudinal glazing bar', 'individual sloped glass canopy pane',
    'glazed platform rear screen', 'station bench pedestal', 'station timber bench slat',
    'real time display housing', 'native transit lettering 10  CENTRAL  3 MIN',
    'native transit lettering 20  RIVERSIDE  8 MIN', 'display suspension',
    'level platform to crossing landing', 'transverse junction side opening',
    'solid connected sidewalk corner ramp', 'continuous transverse zebra stripe',
    'crossing signal pole', 'crossing signal housing', 'refuge signal mast', 'refuge signal display',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(source):
    import bpy
    from mathutils import Vector
    recipe = json.loads((source/'recipe.json').read_text())
    if sha(source/'editable.blend') != AUTHORING_SHA or recipe['authoring_sha256'] != AUTHORING_SHA:
        raise ValueError('BRT authoring file is not the reviewed brt-v004 original')
    if sha(source/'assembly-preview.glb') != recipe['assembly_sha256']:
        raise ValueError('Original BRT assembly bytes changed')
    bpy.ops.wm.open_mainfile(filepath=str(source/'editable.blend'))
    bpy.context.view_layer.update()
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if len(objects) != 332:
        raise ValueError('Original BRT object inventory changed')
    bounds = lambda o: [[fn((o.matrix_world@Vector(c))[i] for c in o.bound_box) for i in range(3)] for fn in (min,max)]
    station, symbol = [], []
    ledger = []
    for o in objects:
        name = re.sub(r'\.\d+$', '', o.name)
        b = bounds(o)
        role = 'procedural-ground-or-repeated-native-module'
        if name in STATION_GROUPS or (name == 'countable native paving units' and b[0][2] > .3):
            station.append(o); role = 'station_program'
        elif (name == 'native transit lettering BUS' or name == 'marking') and b[0][0] > 1.7 and b[1][0] < 3.1 and b[0][1] > -41 and b[1][1] < -33:
            symbol.append(o); role = 'bus_symbol'
        ledger.append(dict(name=o.name, role=role, bounds=b, vertices=len(o.data.vertices)))
    if not STATION_GROUPS.issubset({re.sub(r'\.\d+$','',o.name) for o in station}):
        raise ValueError('Station extraction omitted a required semantic group')
    if len(symbol) != 4:
        raise ValueError('A bus symbol must contain original lettering and three arrow strokes')
    return recipe, station, symbol, ledger


def export(objects, anchor, path):
    import bpy
    from mathutils import Vector
    copies = []
    for source in objects:
        copy = source.copy(); copy.data = source.data.copy()
        bpy.context.collection.objects.link(copy)
        copy.location -= Vector(anchor)
        copies.append(copy)
    # Preserve authored materials but batch static geometry by material, as the
    # original exporter does. Each module is placed rigidly by the runtime.
    groups = {}
    for o in copies:
        groups.setdefault(tuple(m.name for m in o.data.materials), []).append(o)
    selected = []
    for group in groups.values():
        bpy.ops.object.select_all(action='DESELECT')
        for o in group:o.select_set(True)
        bpy.context.view_layer.objects.active=group[0]
        bpy.ops.object.join();selected.append(bpy.context.object)
    bpy.ops.object.select_all(action='DESELECT')
    for o in selected:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
    for o in selected:bpy.data.objects.remove(o,do_unlink=True)
    return dict(path=path.name,bytes=path.stat().st_size,sha256=sha(path),sourceAnchorM=anchor,
                sourceObjectNames=[o.name for o in objects])


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.output.exists():raise ValueError('Use a new output directory; derived revisions are immutable')
    recipe,station,symbol,ledger=inspect(args.source)
    if args.dry_run:
        print('DRY_RUN_PASS',len(station),'station objects;',len(symbol),'bus-symbol objects');return
    args.output.mkdir(parents=True)
    modules={
        'station_program':export(station,[0,-18,0],args.output/'station_program.glb'),
        'bus_symbol':export(symbol,[2.4,-40,0],args.output/'bus_symbol.glb'),
    }
    result=dict(schemaVersion=1,status='derived-candidate-not-runtime-approved',
                sourceDelivery='brt-v004',sourceAuthoringSha256=AUTHORING_SHA,
                sourceRecipeSha256=sha(args.source/'recipe.json'),sourceAssemblySha256=recipe['assembly_sha256'],
                extractorSha256=sha(Path(__file__)),modules=modules,sourceObjectLedger=ledger,
                sourceStationCenterM=-18,stationCrossingOffsetM=28,
                limitations=['No runtime registration by this tool. Ground reconstruction and browser checks remain required.'])
    (args.output/'extraction.json').write_text(json.dumps(result,indent=2)+'\n')
    print('EXTRACTED_CANDIDATES',json.dumps({k:v['sha256'] for k,v in modules.items()}))


if __name__=='__main__':main()
