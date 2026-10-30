"""Finite trusted source derivatives; request data cannot add executable bridge kits."""
import hashlib
import json
import math
import re

SOURCE_BRIDGE_SOURCES = {
    'brick_arch_viaduct_route_v1': ('rail_transit_viaduct','3d5a0e6fb50d12d19de78c5ea0f992ff5a371d2269fb115e1b2e064f64c84033'),
    'rail_through_truss_route_v1': ('rail_transit_viaduct','db0886ff61868fddfe5a88b2381372983da344fe14edde4adecc8805efb7c813'),
    'steel_truss_road_bridge_route_v1': ('urban_vehicular_bridge','d01804b356b2748d9426cd29e4c16d4709a33260abacedc25c3cc3203ddbdf30'),
    'stone_arch_road_bridge_route_v1': ('urban_vehicular_bridge','5300077e633cecc901ef86bb0a78e0b7bd0dce0588c613becbb2195b92337d6d'),
    'tied_arch_shared_bridge_route_v1': ('shared_cycle_pedestrian_bridge','7900ce3b41b0a668b4c68e6dc86d55a8ee3e7eb1d06076b637e0114be5ead94e'),
    'planted_green_bridge_route_v1': ('landscape_park_pedestrian_bridge','d7dddc9371b5cf554bcb372b6d46c8fc0e6256d7335bd47ff542420463f20066'),
    'weathering_steel_v_footbridge_route_v1': ('urban_pedestrian_footbridge','2384d6eed060180c3c68d4ba5040b0968ca6e6229d6846c27327faa204f23ac2'),
    'swooping_cycle_flyover_route_v1': ('dedicated_cycle_bridge','4c075a5a31b0611a96dade6f0572247d5649ebfb4ebf17cd73f794651809c3f4'),
    'cable_stayed_cycle_ring_route_v1': ('dedicated_cycle_bridge','c1ef7008750f60ae622b2c7bb910f8d3ef352f57b4dcd492817d9b47ff0e0e11'),
}
_ID=re.compile(r'[a-z][a-z0-9_]{0,79}\Z')
_SHA=re.compile(r'[0-9a-f]{64}\Z')
SOURCE_BRIDGE_LANES={'steel_truss_road_bridge_route_v1':2,'stone_arch_road_bridge_route_v1':4}


def _number(value, *, zero=False, maximum=10000):
    return (not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value)
            and (value>=0 if zero else value>0) and value<=maximum)


def validate_source_bridge_profile(row):
    expected=SOURCE_BRIDGE_SOURCES.get(row.get('id'))
    program=row.get('program',{})
    if (expected is None or row.get('sourceArchetypeId')!=expected[0]
        or row.get('sourceAssemblySha256')!=expected[1] or program.get('adapter')!='source-span-bridge-v1'
        or row.get('routeAxis')!='local_y' or row.get('placements')!=[]
        or program.get('surfaceRegions') not in (None,[]) or not _number(row.get('widthM'),maximum=160)):
        raise ValueError('Source bridge needs its exact trusted identity and bridge-only source programme.')
    bridge=program.get('bridge',{})
    parts=bridge.get('parts')
    if (not isinstance(parts,list) or not 1<=len(parts)<=20 or bridge.get('trafficKind') not in {'walk','cycle','road','rail'}
        or not _number(bridge.get('deckHeightM')) or not _number(bridge.get('clearWidthM'))
        or bridge['clearWidthM']>row['widthM'] or not _number(bridge.get('approachM'),zero=True)
        or not _number(bridge.get('endM'),zero=True)):
        raise ValueError('Source bridge needs complete dimensions, traffic and ordered structural parts.')
    kinds=set();fixed=0;flexible=0
    for part in parts:
        kind=part.get('kind')
        if (not isinstance(kind,str) or not _ID.fullmatch(kind) or kind in kinds
            or not _number(part.get('lengthM')) or part.get('mode') not in {'fixed','span','repeat'}):
            raise ValueError('Source bridge structural part is invalid or duplicated.')
        kinds.add(kind)
        if part['mode']=='fixed':fixed+=part['lengthM']
        else:flexible+=part['lengthM']
        deformation=part.get('deformation')
        if deformation is not None:
            if (part['mode']!='span' or not isinstance(deformation,dict)
                or deformation.get('mode') not in {'longitudinal-core-v1','circle-radius-v1'}
                or not _number(deformation.get('nativeLengthM'))
                or abs(deformation['nativeLengthM']-part['lengthM'])>1e-4):
                raise ValueError('Unsupported source bridge deformation contract.')
            if deformation['mode']=='longitudinal-core-v1' and (
                not _number(deformation.get('rigidEndM'),zero=True)
                or deformation['rigidEndM']>=part['lengthM']/2):
                raise ValueError('Source bridge must retain a positive deformable core.')
            if deformation['mode']=='circle-radius-v1' and (
                not _number(deformation.get('radiusM'))
                or not _number(abs(deformation.get('centerAcrossM',float('nan'))),zero=True)):
                raise ValueError('Source ring bridge needs its radial geometry datum.')
        for companion in part.get('companions',[]):
            name=companion.get('kind')
            if (not isinstance(name,str) or not _ID.fullmatch(name) or name in kinds
                or not _number(companion.get('lengthM')) or not _number(companion.get('pitchM'))
                or companion['lengthM']>part['lengthM']+1e-6 or companion['pitchM']<companion['lengthM']-1e-6):
                raise ValueError('Bridge companions must be complete, unscaled, nonoverlapping assemblies.')
            kinds.add(name)
    if (not _number(program.get('minLengthM')) or not _number(program.get('maxLengthM'),maximum=2000)
        or flexible<=0 or program['minLengthM']<=fixed or program['maxLengthM']<program['minLengthM']):
        raise ValueError('Bridge length must leave room for complete rigid ends and a positive structural span.')
    modules=row.get('modules')
    if not isinstance(modules,dict) or set(modules)!=kinds:
        raise ValueError('Source bridge is missing a structural or landscape component.')
    locks=[row.get(key) for key in ('sourceRecipeSha256','sourceAssemblySha256','referenceSha256','programSha256')]
    for kind,module in modules.items():
        if module.get('url')!=f"/street-kits/pilots/{row['id']}/{kind}.glb":
            raise ValueError('Source bridge module URL disagrees with its trusted identity.')
        locks.append(module.get('sha256'))
    if (any(not isinstance(value,str) or not _SHA.fullmatch(value) for value in locks)
        or row['programSha256']!=hashlib.sha256(json.dumps(program,sort_keys=True,separators=(',',':')).encode()).hexdigest()):
        raise ValueError('Source bridge module or programme hash is invalid.')
    for path in bridge.get('walkingPaths',[]):
        if (not _number(path.get('widthM')) or path['widthM']>row['widthM']
            or path.get('partKind') is not None and path['partKind'] not in {part['kind'] for part in parts}
            or not isinstance(path.get('points'),list) or not 2<=len(path['points'])<=2000
            or any(not isinstance(p,list) or len(p)!=3 or any(not _number(abs(v),zero=True) for v in p)
                   for p in path['points'])):
            raise ValueError('Source bridge walking path is invalid.')
        polygon=path.get('surfacePolygon')
        if polygon is not None and (not isinstance(polygon,list) or not 3<=len(polygon)<=64
            or any(not isinstance(p,list) or len(p)!=3 or any(not _number(abs(v),zero=True) for v in p) for p in polygon)):
            raise ValueError('Source bridge walking polygon is invalid.')
