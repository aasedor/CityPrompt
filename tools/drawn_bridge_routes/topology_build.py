"""Finite, source-locked bridge-only topology derivatives; no catalogue writes.

GLBs use X across, Y up, Z minus along. V/S keep their native lateral and
vertical profiles under a bounded longitudinal morph. The ring stays circular,
with metric radial deck offsets, a rigid mast and two complete native ramps.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
import trimesh

from .build_timber import _preserve_source_materials, canonical_bytes


ROOT = Path(__file__).resolve().parents[2]
COMMIT = '2e6f4860b75545aebe5a9cccabb845f3943ba8e9'
HASHES = {
    'ring': 'c1ef7008750f60ae622b2c7bb910f8d3ef352f57b4dcd492817d9b47ff0e0e11',
    'flyover': '4c075a5a31b0611a96dade6f0572247d5649ebfb4ebf17cd73f794651809c3f4',
    'weathering': '2384d6eed060180c3c68d4ba5040b0968ca6e6229d6846c27327faa204f23ac2',
}
SCRIPTS = {'ring': 'tools/clay_cable_stayed_cycle_ring/family_ring.py',
           'flyover': 'tools/clay_swooping_cycle_flyover/family_flyover.py',
           'weathering': 'tools/clay_weathering_steel_footbridge/family_corten.py'}
IDS = {'ring': 'cable_stayed_cycle_ring_route_v1', 'flyover': 'swooping_cycle_flyover_route_v1',
       'weathering': 'weathering_steel_v_footbridge_route_v1'}
THUMBNAILS = {'ring': '/archetypes/streets/dedicated-cycle-bridge/variant_1.png',
              'flyover': '/archetypes/streets/dedicated-cycle-bridge/variant_0.png',
              'weathering': '/archetypes/streets/urban-pedestrian-footbridge/variant_0.png'}
R = 33.3
XR = R * math.cos(math.radians(-122))
YS = -math.sqrt(R * R - XR * XR)
YF = -math.sqrt(36 * 36 - XR * XR) - 3
YE = YF - 58
RAMP_M = YS - YE
APEX = np.array([-11.5, 4.0])
QA = APEX + 30 * np.array([math.sin(math.radians(70)), -math.cos(math.radians(70))])
QB = APEX + 32 * np.array([-math.sin(math.radians(22)), -math.cos(math.radians(22))])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_path(style):
    return ROOT / f'frontend/public/street-kits/claude-20261023/{HASHES[style]}.glb'


def _world_meshes(scene):
    for node in sorted(scene.graph.nodes_geometry):
        matrix, key = scene.graph[node]
        mesh = scene.geometry[key].copy()
        mesh.apply_transform(matrix)
        yield node, mesh


def _pieces(mesh):
    mesh = mesh.copy()
    mesh.merge_vertices(merge_tex=True, merge_norm=True)
    # Open source ribbons/net panels are intentional; never silently repair them.
    yield from mesh.split(only_watertight=False, repair=False)


def _frame(a, b):
    a, b = np.array(a), np.array(b)
    axis = (b - a) / np.linalg.norm(b - a)
    return (a + b) / 2, axis, np.array([axis[1], -axis[0]])


def _normalize(mesh, frame, along_shift=0):
    origin, axis, right = frame
    matrix = np.array([[right[0], 0, -right[1], -np.dot(origin, right)],
                       [0, 1, 0, 0], [-axis[0], 0, axis[1], np.dot(origin, axis) + along_shift],
                       [0, 0, 0, 1]])
    result = mesh.copy()
    result.apply_transform(matrix)
    return result


def _point(point, frame):
    p = np.array(point[:2]) - frame[0]
    return [float(np.dot(p, frame[2])), float(np.dot(p, frame[1])), float(point[2])]


def _add(groups, module, mesh, role='fixed'):
    groups[module][(role, mesh.visual.material.name)].append(mesh)


def _scene(groups, materials):
    scene = trimesh.Scene(base_frame='world')
    for (role, material), meshes in sorted(groups.items()):
        mesh = trimesh.util.concatenate(meshes)
        mesh.visual = trimesh.visual.TextureVisuals(material=deepcopy(materials[material]))
        mesh.metadata['deformationRole'] = role
        scene.add_geometry(mesh, node_name=f'{role}__{material}', geom_name=f'{role}__{material}')
    return scene


def _box(center, extents, material):
    mesh = trimesh.creation.box(extents)
    mesh.apply_translation(center)
    mesh.visual = trimesh.visual.TextureVisuals(material=deepcopy(material))
    return mesh


def _oriented_box(q, u, along, across, z, length, width, height, material):
    mesh = _box([0, 0, 0], [width, height, length], material)
    # Local X is right of tower direction; local -Z is tower direction.
    matrix = np.array([[u[1], 0, -u[0], q[0] + u[0]*along - u[1]*across],
                       [0, 1, 0, z], [u[0], 0, u[1], -(q[1] + u[1]*along + u[0]*across)],
                       [0, 0, 0, 1]])
    mesh.apply_transform(matrix)
    return mesh


def _beam(a,b,width,material):
    a,b=np.array(a),np.array(b)
    mesh=_box([0,0,0],[width,width,np.linalg.norm(b-a)],material)
    matrix=trimesh.geometry.align_vectors([0,0,1],b-a)
    matrix[:3,3]=(a+b)/2
    mesh.apply_transform(matrix)
    return mesh


def _ring_kerbs(material):
    """Native profile with two source-sized throat gaps, each end closed."""
    lo, hi = 35.85, 36.0
    south = sorted([-math.acos((XR - 2.35) / 35.93), -math.acos((XR + 2.35) / 35.93)])
    north = [-south[1], -south[0]]
    intervals = [(south[1], north[0]), (north[1], south[0] + 2*math.pi)]
    for a, b in intervals:
        angles = np.linspace(a, b, max(3, round((b-a) / (2*math.pi) * 96)))
        vertices = [[r*math.cos(t), z, -r*math.sin(t)] for t in angles
                    for r, z in [(lo, 6.53), (hi, 6.53), (hi, 6.72), (lo, 6.72)]]
        faces = []
        for i in range(len(angles)-1):
            for j in range(4):
                a0, b0 = 4*i+j, 4*i+(j+1)%4
                faces.extend([(a0, b0, b0+4), (a0, b0+4, a0+4)])
        faces += [(0, 2, 1), (0, 3, 2)]
        n = 4*(len(angles)-1)
        faces += [(n, n+1, n+2), (n, n+2, n+3)]
        mesh = trimesh.Trimesh(vertices, faces, process=False)
        trimesh.repair.fix_normals(mesh)
        mesh.visual = trimesh.visual.TextureVisuals(material=deepcopy(material))
        yield mesh


def _flyover_path():
    # Exact pure geometry sampling from the pinned family_flyover.py recipe.
    ctrl = [(-270,-25),(-225,-25),(-180,-25),(-135,-23.5),(-100,-19.5),(-71,-11),(-48,2),
            (-27,12),(-11,12.5),(0,3),(13,-17),(29,-25),(48,-21),(63,-8),(80,2),
            (98,7),(120,10),(150,10),(185,10),(225,10),(270,10)]
    raw = []
    for i in range(1, len(ctrl)-2):
        p0,p1,p2,p3 = map(np.array, ctrl[i-1:i+3])
        n = max(2, int(np.linalg.norm(p2-p1)/1.4))
        for k in range(n):
            t = k/n
            raw.append(.5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    raw.append(np.array(ctrl[-2]))
    raw = np.array([p for p in raw if abs(p[0]) <= 223])
    stations = np.r_[0, np.cumsum(np.linalg.norm(np.diff(raw, axis=0), axis=1))]
    sa = stations[np.flatnonzero(raw[:,0] >= -78)[0]]
    sb = stations[np.flatnonzero(raw[:,0] <= 84)[-1]]
    zr = [.06+6.14*min(1,max(0,1-(sa-s)/100 if s<sa else 1-(s-sb)/100 if s>sb else 1)) for s in stations]
    heights = [np.mean([zr[j] for j in range(max(0,i-12),min(len(raw),i+13)) if abs(stations[j]-s)<=5]) for i,s in enumerate(stations)]
    raised = np.flatnonzero(np.array(heights) > .064)
    return np.column_stack([raw, heights])[raised[0]-1:raised[-1]+2]


def _extract_ring(source, groups, materials, records):
    frame = (np.array([XR, 0]), np.array([0,1]), np.array([1,0]))
    for node, mesh in _world_meshes(source):
        mat = mesh.visual.material.name
        if mat not in {'CLAY_CONCRETE','CLAY_WHITE','CLAY_RED','CLAY_RAMPDECK','CLAY_RAIL','CLAY_GLASS','CLAY_STEEL','CLAY_CABLE','CLAY_LANE','CLAY_CYCLE'}:
            continue
        for index,piece in enumerate(_pieces(mesh)):
            low,high = piece.bounds
            center = piece.bounds.mean(axis=0)
            across=max(abs(low[0]-XR),abs(high[0]-XR))
            ramp = (mat=='CLAY_RAMPDECK'
                    or (mat=='CLAY_WHITE' and low[2]>28 and across<2.31 and high[1]>6.5)
                    or (mat=='CLAY_CONCRETE' and low[2]>40 and across<.46)
                    or (mat=='CLAY_RAIL' and low[2]>28 and across<2.25)
                    or (mat=='CLAY_LANE' and low[2]>30 and across<.08))
            if mat == 'CLAY_LANE' and low[1] < .085:
                continue
            if mat == 'CLAY_CYCLE':
                continue
            if mat == 'CLAY_WHITE' and high[1] < .11 and low[2] > 90:
                continue
            if mat == 'CLAY_LANE' and low[2] > 35 and abs(center[0]-XR) > 2.2:
                continue
            if mat == 'CLAY_WHITE' and high[2] > 35.9 and low[2] < -35.9 and high[1] > 6.7:
                # Original partial outer kerb is replaced with the same profile and two throats.
                continue
            if mat in {'CLAY_RAIL','CLAY_GLASS'} and center[2] < 0 and abs(center[0]-XR)<2.65 and math.hypot(center[0],center[2])>R:
                # New mirrored ramp opening: complete post/panel ownership.
                continue
            radius_max=max(np.hypot(piece.vertices[:,0],piece.vertices[:,2]))
            role = 'cables' if mat == 'CLAY_CABLE' else 'pylon' if radius_max < 3.7 else 'ring'
            if ramp:
                for side, sign in [('left',1),('right',-1)]:
                    selected = piece.copy()
                    selected.vertices[:,2] *= sign
                    if sign < 0:
                        selected.faces = selected.faces[:,::-1]
                    center_y = sign*(YS+YE)/2
                    _add(groups, 'ring_ramp_'+side, _normalize(selected, frame, center_y), 'fixed')
                records.append({'node':node,'piece':index,'material':mat,'owner':'both-ramp-derivative','bounds':piece.bounds.tolist(),'triangles':len(piece.faces)})
            else:
                _add(groups,'ring_core',_normalize(piece,frame),role)
                records.append({'node':node,'piece':index,'material':mat,'owner':'ring_core','bounds':piece.bounds.tolist(),'triangles':len(piece.faces)})
    for kerb in _ring_kerbs(materials['CLAY_WHITE']):
        _add(groups,'ring_core',_normalize(kerb,frame),'ring')
    # Ring columns / island are identified as rigid source sections, not scaled feet.
    core = 2*abs(YS)
    native = core+2*RAMP_M
    ring = [[-XR+R*math.cos(a), R*math.sin(a), 6.6] for a in np.linspace(0,2*math.pi,193)]
    # Two alternative half-ring routes connect both complete source ramps.
    a0 = math.atan2(YS,XR)
    a1 = -a0
    paths=[]
    for angles in [np.linspace(a0,a1,129), np.linspace(a0,a1-2*math.pi,129)]:
        points=[[0,YE,.1],[0,YF,6.59],[0,YS,6.59]]
        points += [[-XR+R*math.cos(a),R*math.sin(a),6.6] for a in angles]
        points += [[0,-YS,6.59],[0,-YF,6.59],[0,-YE,.1]]
        paths.append({'pointsM':points,'widthM':4.0})
    descriptor={'mode':'circle-radius-v1','nativeLengthM':core,'radiusM':R,'centerAcrossM':-XR,
                'throatAlongM':abs(YS),'rigidEndM':0,'minLengthM':core*.8,'maxLengthM':core*1.3,
                'ringInnerRadiusM':30.6,'ringOuterRadiusM':36,'collarHeightM':48,'cableAnchorRadiusM':30.65,
                'pylonRole':'pylon','cableRole':'cables','ringRole':'ring'}
    return dict(frame=frame,native=native,width=145,clear=4,deck=6.6,deformation=descriptor,
                centerlines=[{'pointsM':ring,'widthM':5.1}]+paths,
                walking=[{'partKind':'ring_ramp_left','pointsM':[[0,-RAMP_M/2,.1],[0,YF-(YS+YE)/2,6.59],[0,RAMP_M/2,6.59]],'widthM':4},
                         {'partKind':'ring_core','pointsM':ring,'widthM':5.1},
                         {'partKind':'ring_ramp_right','pointsM':[[0,-RAMP_M/2,6.59],[0,-YF+(YS+YE)/2,6.59],[0,RAMP_M/2,.1]],'widthM':4}],
                endpoints=[[0,YE,.1],[0,-YE,.1]],
                parts=[{'kind':'ring_ramp_left','lengthM':RAMP_M,'mode':'fixed'},
                       {'kind':'ring_core','lengthM':core,'mode':'span','deformation':descriptor},
                       {'kind':'ring_ramp_right','lengthM':RAMP_M,'mode':'fixed'}],
                access={'gradeRamps':2,'sourceRamps':1,'mirroredSourceRamps':1,'maxNativeRampGradient':6.51/58},
                derivatives=['Second source ramp mirrored north, with new matching ring throat; scene cycle-path apron excluded.',
                             'Outer kerb rebuilt from exact native profile; original source files unchanged.'])


def _extract_flyover(source, groups, materials, records):
    path = _flyover_path()
    frame = _frame(path[0,:2],path[-1,:2])
    native = np.linalg.norm(path[-1,:2]-path[0,:2])
    for node,mesh in _world_meshes(source):
        mat=mesh.visual.material.name
        if mat in {'CLAY_UNDER','CLAY_ORANGE','CLAY_CONCRETE'}:
            _add(groups,'bridge_topology',_normalize(mesh,frame),'span')
            records.append({'node':node,'material':mat,'owner':'whole-bridge-material','bounds':mesh.bounds.tolist(),'triangles':len(mesh.faces)})
        elif mat in {'CLAY_DECK','CLAY_LANE'}:
            for index,piece in enumerate(_pieces(mesh)):
                if mat=='CLAY_DECK' and piece.extents[0] < 300:
                    continue
                if mat=='CLAY_LANE' and (piece.bounds[0,1]<.065 or piece.bounds.mean(axis=0)[0]<path[0,0] or piece.bounds.mean(axis=0)[0]>path[-1,0]):
                    continue
                _add(groups,'bridge_topology',_normalize(piece,frame),'span')
                records.append({'node':node,'piece':index,'material':mat,'owner':'raised-ribbon','bounds':piece.bounds.tolist(),'triangles':len(piece.faces)})
    points=[_point(p,frame) for p in path]
    d={'mode':'longitudinal-core-v1','nativeLengthM':float(native),'rigidEndM':15,
       'minLengthM':float(native*.85),'maxLengthM':float(native*1.2)}
    return dict(frame=frame,native=float(native),width=54,clear=6.2,deck=6.2,deformation=d,
                centerlines=[{'pointsM':points,'widthM':6.2}],walking=[{'partKind':'bridge_topology','pointsM':points,'widthM':6.2}],
                endpoints=[points[0],points[-1]],parts=[{'kind':'bridge_topology','lengthM':float(native),'mode':'span','deformation':d}],
                access={'gradeRamps':2,'nativeRiseM':6.14,'nativeRampRunM':100},
                derivatives=['Removed extended at-grade scene paths; original raised ribbon and both vertical transitions retained.'])


def _tower_local(piece,q,u):
    plan=np.column_stack([piece.vertices[:,0],-piece.vertices[:,2]])-q
    return plan@u,plan@np.array([-u[1],u[0]])


def _extract_weathering(source,groups,materials,records):
    frame=_frame(QB,QA)
    native=float(np.linalg.norm(QA-QB))
    towers=[(QA,(QA-APEX)/30),(QB,(QB-APEX)/32)]
    bodies=0
    for node,mesh in _world_meshes(source):
        mat=mesh.visual.material.name
        if mat in {'CLAY_RUST','CLAY_HARDWARE','CLAY_DECK','CLAY_MESH'}:
            candidates=list(_pieces(mesh)) if mat=='CLAY_HARDWARE' else [mesh]
        elif mat in {'CLAY_BRICK','CLAY_PALE','CLAY_GLASS','CLAY_JOINT','CLAY_CONCRETE','CLAY_TRIM'}:
            candidates=list(_pieces(mesh))
        else:
            continue
        for index,piece in enumerate(candidates):
            local=[]
            for q,u in towers:
                s,v=_tower_local(piece,q,u)
                if s.min()>-.65 and s.max()<4.85 and max(abs(v.min()),abs(v.max()))<2.55:
                    local.append((s,v))
            if mat not in {'CLAY_RUST','CLAY_HARDWARE','CLAY_DECK','CLAY_MESH'}:
                if mat=='CLAY_CONCRETE':
                    if piece.extents[0]>2:
                        continue
                elif not local:
                    if mat!='CLAY_JOINT' or piece.bounds[0,1]<6.9:
                        continue
            if mat=='CLAY_BRICK' and local and len(piece.faces)==12 and piece.extents[1]>10:
                bodies+=1
                continue
            if mat in {'CLAY_GLASS','CLAY_HARDWARE'} and local:
                s,v=local[0]
                # Open both complete door apertures while retaining their surrounds and stair slot glazing.
                door= ((piece.bounds[0,1]>=-.01 and piece.bounds[1,1]<=2.51 and max(abs(v.min()),abs(v.max()))<.81)
                       or (piece.bounds[0,1]>=6.99 and piece.bounds[1,1]<=9.61 and max(abs(v.min()),abs(v.max()))<1.21))
                if door:
                    continue
            _add(groups,'bridge_topology',_normalize(piece,frame),'span')
            records.append({'node':node,'piece':index,'material':mat,'owner':'bridge-or-complete-tower','bounds':piece.bounds.tolist(),'triangles':len(piece.faces)})
    walks=[]
    for q,u in towers:
        # Three wall shell replaces the solid illustration block, retaining its exact exterior envelope.
        for along,across,length,width in [(2.45,-2.15,4.3,.3),(2.45,2.15,4.3,.3),(4.45,0,.3,4.6)]:
            shell=_oriented_box(q,u,along,across,5.4,length,width,10.8,materials['CLAY_BRICK'])
            _add(groups,'bridge_topology',_normalize(shell,frame),'span')
        route=[_point([*q,0],frame)]
        def at(s,v,z):
            return _point([q[0]+u[0]*s-u[1]*v,q[1]+u[1]*s+u[0]*v,z],frame)
        for flight in range(4):
            reverse=flight%2
            lane=.85 if not reverse else -.85
            z0=flight*1.75
            start,end=(.9,3.7) if not reverse else (3.7,.9)
            route.append(at(start,lane,z0))
            def source_at(s,v,z):
                return [q[0]+u[0]*s-u[1]*v,z,-(q[1]+u[1]*s+u[0]*v)]
            for edge in (lane-.77,lane+.77):
                rail=_beam(source_at(start,edge,z0+1.05),source_at(end,edge,z0+2.8),.045,materials['CLAY_HARDWARE'])
                _add(groups,'bridge_topology',_normalize(rail,frame),'span')
                for s,z in [(start,z0),(end,z0+1.75)]:
                    post=_beam(source_at(s,edge,z),source_at(s,edge,z+1.05),.035,materials['CLAY_HARDWARE'])
                    _add(groups,'bridge_topology',_normalize(post,frame),'span')
            for step in range(10):
                s=start+(end-start)*(step+.5)/10
                height=z0+(step+1)*.175
                # A thin stepped flight keeps its underside parallel to the
                # treads; a filled block would obstruct the flight below it.
                bottom=max(z0,height-.2)
                stair=_oriented_box(q,u,s,lane,(height+bottom)/2,.28,1.5,height-bottom,materials['CLAY_DECK'])
                _add(groups,'bridge_topology',_normalize(stair,frame),'span')
                route.extend([at(start+(end-start)*step/10,lane,height),at(start+(end-start)*(step+1)/10,lane,height)])
            land_s=4 if not reverse else .6
            land=_oriented_box(q,u,land_s,0,z0+1.75-.06,.6,3.2,.12,materials['CLAY_DECK'])
            _add(groups,'bridge_topology',_normalize(land,frame),'span')
            route.extend([at(land_s,lane,z0+1.75),at(land_s,-lane,z0+1.75)])
        route.append(_point([*q,7],frame))
        walks.append(route)
    main=[_point([*QB,7],frame),_point([*APEX,7],frame),_point([*QA,7],frame)]
    full=walks[1]+main[1:-1]+list(reversed(walks[0]))
    d={'mode':'longitudinal-core-v1','nativeLengthM':native,'rigidEndM':7,
       'minLengthM':native*.9,'maxLengthM':native*1.15}
    return dict(frame=frame,native=native,width=52,clear=3.4,deck=7,deformation=d,
                centerlines=[{'pointsM':main,'widthM':3.4}],walking=[{'partKind':'bridge_topology','pointsM':full,'widthM':1.5}],
                endpoints=[_point([*QB,0],frame),_point([*QA,0],frame)],
                parts=[{'kind':'bridge_topology','lengthM':native,'mode':'span','deformation':d}],
                access={'towerCount':2,'risersPerTower':40,'riserM':.175,'treadM':.28,'minStairClearWidthM':1.5,
                        'solidTowerBodiesRemoved':bodies,'stairHeadroomM':3.3,
                        'mode':'authored-source-material-hollow-tower-switchback'},
                derivatives=['Solid tower illustration bodies replaced with same-envelope brick shell.',
                             'Door infill opened; four-flight internal stairs/landings added using source deck material.',
                             'Source-material stair handrails added; detailed landing guarding remains a visual review item.',
                             'No accessibility, construction certification or keeper claim.'])


def extract(style, original=None):
    original=Path(original) if original else source_path(style)
    data=original.read_bytes()
    if digest(data)!=HASHES[style]:
        raise ValueError(f'Exact {style} source hash mismatch')
    source=trimesh.load(original,force='scene',process=False)
    materials={m.visual.material.name:deepcopy(m.visual.material) for m in source.geometry.values()}
    groups=defaultdict(lambda:defaultdict(list))
    records=[]
    info={'ring':_extract_ring,'flyover':_extract_flyover,'weathering':_extract_weathering}[style](source,groups,materials,records)
    if style in {'weathering','flyover'}:
        # The drawn interval owns the full skewed end sections / whole towers,
        # rather than only their centerline endpoints or tower-face chord.
        meshes=[m for group in groups.values() for items in group.values() for m in items]
        low=min(m.bounds[0,2] for m in meshes)
        high=max(m.bounds[1,2] for m in meshes)
        shift=-(low+high)/2
        native=high-low
        for mesh in meshes:
            mesh.vertices[:,2]+=shift
        visited=set()
        for collection in [*info['centerlines'],*info['walking'],{'pointsM':info['endpoints']}]:
            for point in collection['pointsM']:
                if id(point) not in visited:
                    point[1]-=shift
                    visited.add(id(point))
        origin,axis,right=info['frame']
        info['frame']=(origin+axis*shift,axis,right)
        key='sourceTowerFaceChordM' if style=='weathering' else 'sourceRampCenterlineChordM'
        info['access'][key]=info['native']
        info['access']['nativeIntervalIncludes']=('complete tower shells, stair flights and ground door positions' if style=='weathering'
                                                  else 'complete skewed full-width raised ribbon end sections')
        info['native']=native
        minimum,maximum=(.9,1.15) if style=='weathering' else (.85,1.2)
        info['deformation'].update(nativeLengthM=native,minLengthM=native*minimum,maxLengthM=native*maximum)
        info['parts'][0]['lengthM']=native
    scenes={kind:_scene(group,materials) for kind,group in sorted(groups.items())}
    source_triangles=sum(len(m.faces) for m in source.geometry.values())
    retained=sum(r['triangles'] for r in records)
    source_script=subprocess.check_output(['git','show',f'{COMMIT}:{SCRIPTS[style]}'],cwd=ROOT)
    provenance={'schemaVersion':1,'revision':'topology-bridge-only-1','style':style,'sourceSha256':HASHES[style],
                'builderSha256':digest(Path(__file__).read_bytes()),
                'sourceBytes':len(data),'sourceAuthoring':{'commit':COMMIT,'path':SCRIPTS[style],'sha256':digest(source_script)},
                'sourceFrame':'glTF Y-up; authoring plan=(X,-Z)','outputFrame':'glTF X=across,Y=up,Z=-along; each part centered on nominal interval',
                'ownership':{'sourceTriangles':source_triangles,'retainedSourceTriangles':retained,'excludedTriangles':source_triangles-retained},
                'components':records,'moduleBoundsM':{k:s.bounds.tolist() for k,s in scenes.items()},
                'outputGeometry':{'triangles':sum(len(m.faces) for s in scenes.values() for m in s.geometry.values()),
                                  'vertices':sum(len(m.vertices) for s in scenes.values() for m in s.geometry.values())},
                'deformation':info['deformation'],'access':info['access'],'derivatives':info['derivatives'],
                'topology':{'kind':style,'nativeLengthM':info['native'],'declaredEnvelopeWidthM':info['width'],
                            'clearWidthM':info['clear'],'centerlines':info['centerlines'],'gradeEndpointsM':info['endpoints'],
                            'walkingPaths':info['walking']},
                'review':{'offlineGeometry':'measured; tests required','runtime':'NOT TESTED','visual':'NOT TESTED','publication':'NOT APPROVED'},
                'toolchain':{'trimesh':trimesh.__version__,'numpy':np.__version__}}
    provenance['_info']=info
    return scenes,provenance


def deform_longitudinal(vertices,length,descriptor):
    if not descriptor['minLengthM']-1e-8 <= length <= descriptor['maxLengthM']+1e-8:
        raise ValueError('Outside supported length')
    result=np.array(vertices,dtype=float,copy=True)
    native=descriptor['nativeLengthM']
    core=native/2-descriptor['rigidEndM']
    result[:,2]-=(length-native)/2*np.clip(-result[:,2]/core,-1,1)
    return result


def deform_ring(vertices,scale,descriptor,role):
    result=np.array(vertices,dtype=float,copy=True)
    cx=descriptor['centerAcrossM']
    if role=='pylon':
        result[:,0]+=cx*(scale-1)
        return result
    x=result[:,0]-cx
    y=-result[:,2]
    radius=np.hypot(x,y)
    if role=='cables':
        weight=np.clip((48-result[:,1])/(48-6.3),0,1)
        radial_shift=descriptor['radiusM']*(scale-1)*weight
        result[:,0]+=cx*(scale-1)+np.divide(x,radius,out=np.zeros_like(x),where=radius>1e-8)*radial_shift
        result[:,2]-=np.divide(y,radius,out=np.zeros_like(y),where=radius>1e-8)*radial_shift
        return result
    target=descriptor['radiusM']*scale+(radius-descriptor['radiusM'])
    factor=np.divide(target,radius,out=np.ones_like(radius),where=radius>1e-8)
    result[:,0]=cx*scale+x*factor
    result[:,2]=-y*factor
    return result


def build(style,output):
    output=Path(output)
    if output.resolve().is_relative_to(ROOT):
        raise ValueError('Generated topology handoff must be outside the source tree')
    scenes,provenance=extract(style)
    info=provenance.pop('_info')
    output.mkdir(parents=True,exist_ok=True)
    locks={}
    for kind,scene in scenes.items():
        data=_preserve_source_materials(trimesh.exchange.gltf.export_glb(scene,include_normals=True),source_path(style).read_bytes())
        (output/(kind+'.glb')).write_bytes(data)
        locks[kind]={'sha256':digest(data),'bytes':len(data),'url':f'/street-kits/pilots/{IDS[style]}/{kind}.glb'}
    if style=='ring':
        minimum=2*RAMP_M+info['deformation']['minLengthM']; maximum=2*RAMP_M+info['deformation']['maxLengthM']
    else:
        minimum=info['deformation']['minLengthM']; maximum=info['deformation']['maxLengthM']
    walking=[{'partKind':p['partKind'],'points':p['pointsM'],'widthM':p['widthM']} for p in info['walking']]
    bridge={'parts':info['parts'],'deckHeightM':info['deck'],'clearWidthM':info['clear'],
            'approachM':0,'endM':0,'trafficKind':'walk' if style=='weathering' else 'cycle','walkingPaths':walking}
    program={'schemaVersion':1,'adapter':'source-span-bridge-v1','bridge':bridge,'minLengthM':minimum,'maxLengthM':maximum,
             'preparedLevelOnly':True,'surfaceRegions':[],'details':[],'paving':'source-native','pavingModuleM':[.3,.15],
             'baseLiftM':0,'palette':{}}
    row={'id':IDS[style],'sourceArchetypeId':'urban_pedestrian_footbridge' if style=='weathering' else 'dedicated_cycle_bridge',
         'title':{'ring':'Cable-Stayed Cycle Ring','flyover':'Swooping Cycle Flyover','weathering':'Weathering Steel V Footbridge'}[style]+' — Draw Route',
         'status':'candidate','sourceAssemblySha256':HASHES[style],'widthM':info['width'],'fixtureLengthM':info['native'],
         'routeAxis':'local_y','junctionSurface':'pavers','sections':[
             {'name':'left_structure_reserve','x':-(info['width']+info['clear'])/4,'width':(info['width']-info['clear'])/2,'material':'source-native'},
             {'name':'clear_walk','x':0,'width':info['clear'],'material':'source-native'},
             {'name':'right_structure_reserve','x':(info['width']+info['clear'])/4,'width':(info['width']-info['clear'])/2,'material':'source-native'}],
         'placements':[],'treeWells':[],'modules':locks,'program':program,'programSha256':digest(canonical_bytes(program)),
         'thumbnailUrl':THUMBNAILS[style]}
    reference=(ROOT/'frontend/public'/THUMBNAILS[style].lstrip('/')).read_bytes()
    pointer=reference.startswith(b'version https://git-lfs.github.com/spec/v1')
    row['referenceSha256']=reference.decode('ascii').split('oid sha256:')[1].splitlines()[0] if pointer else digest(reference)
    provenance['reference']={'url':THUMBNAILS[style],'sha256':row['referenceSha256'],'hydrated':not pointer,
                             'verification':'Git LFS authoritative object OID' if pointer else 'exact local photographic reference bytes'}
    row['sourceRecipeSha256']=digest(canonical_bytes({'extraction':provenance,'nativeStreetPilot':row}))
    provenance['moduleLocks']=locks
    provenance['sourceRecipeSha256']=row['sourceRecipeSha256']
    for name,value in [('nativeStreetPilot.json',row),('provenance.json',provenance)]:
        (output/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    return row,provenance


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--style',choices=sorted(HASHES),required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    row,_=build(args.style,args.output_dir)
    print(json.dumps({'id':row['id'],'modules':row['modules'],'nativeLengthM':row['fixtureLengthM']},indent=2))


if __name__=='__main__':
    main()
