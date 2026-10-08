"""Finite 35-item detail extension. Dry run with Python; build with Blender.

26 components reuse existing runtime geometry/builders. Nine small amenities use
the same material palette and modelling helpers. Outputs stay external until reviewed.
"""
import argparse
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
# ID, label, category, source builder. Stable IDs are persisted in project metadata.
SPECS = [
    ('player-bench', 'Team bench', 'Seating', 'sport:player_bench'),
    ('covered-team-bench', 'Covered team bench', 'Shelters & markets', 'sport:covered_bench'),
    ('three-row-bleachers', 'Three-row bleachers with rails', 'Seating', 'sport:bleachers'),
    ('referee-chair', 'Referee chair', 'Sport & exercise', 'sport:referee_stand'),
    ('twin-court-light', 'Twin-head court light', 'Lighting', 'sport:floodlight'),
    ('festoon-lights', 'Festoon light span', 'Lighting', 'sport:festoon'),
    ('bus-shelter', 'Neighbourhood bus shelter', 'Shelters & markets', 'street:shelter'),
    ('bus-stop-pole', 'Bus stop pole & timetable', 'Street furniture', 'street:stop_pole'),
    ('timber-picket-fence', 'Timber picket fence', 'Edges & gates', 'street:fence_panel'),
    ('boardwalk-railing', 'Timber-and-steel boardwalk railing', 'Edges & gates', 'street:guard'),
    ('hammock', 'Freestanding hammock', 'Seating', 'street:hammock'),
    ('cafe-table-set', 'Cafe table & four chairs', 'Seating', 'sport:cafe_set'),
    ('backless-bench', 'Backless timber bench', 'Seating', 'kit:backless_bench'),
    ('classic-picnic-table', 'Classic picnic table', 'Seating', 'kit:picnic_table'),
    ('planted-tree-well', 'Planted tree surround', 'Landscape', 'kit:tree_well_planted'),
    ('guarded-tree-well', 'Tree surround with guard', 'Landscape', 'kit:tree_well_guarded'),
    ('compact-shrub', 'Compact leafy shrub', 'Planting', 'kit:compact_shrub'),
    ('compact-grass', 'Fine grass tuft', 'Planting', 'kit:compact_grass'),
    ('compact-perennial', 'Low flowering perennial', 'Planting', 'kit:compact_perennial'),
    ('meadow-patch', 'Wildflower meadow patch', 'Planting', 'kit:meadow_patch'),
    ('botanical-label', 'Botanical interpretation label', 'Garden & growing', 'trio:label'),
    ('corten-growing-bed', 'Corten teaching garden bed', 'Garden & growing', 'trio:bed'),
    ('garden-teaching-canopy', 'Garden teaching canopy', 'Shelters & markets', 'trio:shelter'),
    ('outdoor-cinema-screen', 'Outdoor cinema screen', 'Water & landmarks', 'trio:screen'),
    ('projection-booth', 'Timber projection booth', 'Shelters & markets', 'trio:booth'),
    ('audience-seat-row', 'Four-seat audience row', 'Seating', 'trio:seats'),
    ('low-stone-wall', 'Low stone garden wall', 'Edges & gates', 'new:stone_wall'),
    ('stepping-stone', 'Round stepping stone', 'Landscape', 'new:stepping_stone'),
    ('bicycle-pump', 'Public bicycle pump', 'Street furniture', 'new:bicycle_pump'),
    ('dog-bag-dispenser', 'Dog-waste bag dispenser', 'Street furniture', 'new:dog_bags'),
    ('fire-hydrant', 'Fire hydrant', 'Street furniture', 'new:hydrant'),
    ('wayfinding-post', 'Wayfinding fingerpost', 'Street furniture', 'new:wayfinding'),
    ('community-mailbox', 'Community mailbox', 'Street furniture', 'new:mailbox'),
    ('dog-agility-hoop', 'Dog agility hoop', 'Play', 'new:dog_hoop'),
    ('dog-agility-tunnel', 'Dog agility tunnel', 'Play', 'new:dog_tunnel'),
]


def custom(kind, S):
    if kind == 'stone_wall':
        for row in range(3):
            for i in range(6):
                S.box('stone course',(-1.25+i*.5,0,.10+row*.2),(.488,.38,.188),'warm_concrete')
        S.box('stone coping',(0,0,.63),(3.08,.46,.08),'cream')
    elif kind == 'stepping_stone':
        S.beam('round stone',(0,0,0),(0,0,.06),.32,'warm_concrete',24)
    elif kind == 'bicycle_pump':
        S.box('pump foot',(0,0,.035),(.42,.30,.07),'metal')
        S.beam('pump body',(0,0,.06),(0,0,.72),.065,'sage',12)
        S.beam('pump piston',(0,0,.7),(0,0,.92),.022,'aluminium',10)
        S.beam('pump handle',(-.18,0,.94),(.18,0,.94),.025,'metal',10)
        points=[(.08,-.02,.66),(.24,-.02,.48),(.31,-.02,.19),(.23,-.02,.10),(.14,-.02,.20)]
        for a,b in zip(points,points[1:]): S.beam('hose',a,b,.014,'metal',6)
        S.box('gauge',(0,-.068,.60),(.075,.018,.08),'cream')
    elif kind == 'dog_bags':
        S.beam('post',(0,0,0),(0,0,1.58),.04,'metal',8)
        S.box('bag dispenser',(0,0,1.2),(.3,.18,.38),'sage')
        S.box('dispensing slot',(0,-.094,1.10),(.21,.015,.045),'metal')
        S.box('sign',(0,0,1.65),(.40,.055,.28),'sage')
        for x in (-.10,0,.10):S.beam('paw motif',(x,-.032,1.69),(x,-.04,1.69),.025,'cream',8)
        S.beam('paw pad',(0,-.032,1.60),(0,-.04,1.60),.048,'cream',8)
    elif kind == 'hydrant':
        S.beam('base',(0,0,0),(0,0,.13),.20,'metal',16)
        S.beam('hydrant barrel',(0,0,.08),(0,0,.76),.13,'terracotta',16)
        S.beam('bonnet',(0,0,.76),(0,0,.89),.15,'terracotta',16)
        S.beam('top nut',(0,0,.89),(0,0,.94),.04,'metal',6)
        for x in (-1,1):S.beam('hose cap',(x*.08,0,.57),(x*.23,0,.57),.065,'aluminium',12)
        S.beam('front cap',(0,-.08,.44),(0,-.20,.44),.095,'aluminium',12)
    elif kind == 'wayfinding':
        S.beam('post',(0,0,0),(0,0,2.9),.045,'metal',10)
        for i in range(3):
            z=2.25+i*.25;sign=-1 if i%2 else 1
            pts=[(-.5,-.045,z-.085),(.5,-.045,z-.085),(.65,-.045,z),(.5,-.045,z+.085),(-.5,-.045,z+.085)]
            S.mesh('direction board',[(sign*x,y,z) for x,y,z in pts],[tuple(range(5))],'sage')
            S.box('map line',(0,-.05,z),(.55,.01,.016),'cream')
    elif kind == 'mailbox':
        for x in (-.49,.49):S.box('mailbox leg',(x,0,.35),(.09,.28,.70),'metal')
        S.box('cabinet',(0,0,1.01),(1.40,.50,.85),'aluminium')
        for i in range(4):
            for j in range(3):
                x=-.525+i*.35;z=.75+j*.26
                S.box('mail door',(x,-.258,z),(.325,.025,.235),'cream')
                S.box('letter slot',(x,-.275,z+.055),(.22,.01,.018),'metal')
                S.beam('lock',(x+.10,-.278,z-.055),(x+.10,-.29,z-.055),.015,'metal',8)
        S.box('weather cap',(0,0,1.46),(1.49,.59,.07),'metal')
    elif kind == 'dog_hoop':
        for x in (-.64,.64):
            S.box('hoop foot',(x,0,.035),(.22,.70,.07),'timber')
            S.box('hoop support',(x,0,.55),(.075,.075,1.1),'timber')
        for i in range(32):
            a=i*math.tau/32;b=(i+1)*math.tau/32
            S.beam('jump ring',(.54*math.cos(a),0,.82+.54*math.sin(a)),(.54*math.cos(b),0,.82+.54*math.sin(b)),.045,'sage',8)
    elif kind == 'dog_tunnel':
        n=32;r=.47;inner=.41
        verts=[(x,rr*math.cos(i*math.tau/n),.49+rr*math.sin(i*math.tau/n)) for x in (-1.2,1.2) for rr in (r,inner) for i in range(n)]
        faces=[]
        for i in range(n):
            j=(i+1)%n
            faces.extend([(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),(i,n+i,n+j,j),(2*n+i,2*n+j,3*n+j,3*n+i)])
        S.mesh('open tunnel',verts,faces,'sage')
        for x in (-.8,.8):S.box('tunnel cradle',(x,0,.065),(.20,.72,.13),'timber')
    else:
        raise ValueError(kind)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--kit',type=Path)
    parser.add_argument('--id',action='append')
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    specs=[s for s in SPECS if not args.id or s[0] in args.id]
    if args.id and set(args.id)-{s[0] for s in SPECS}:raise ValueError('Unknown detail ID')
    if args.dry_run:
        print(json.dumps({'count':len(specs),'objects':[s[0] for s in specs],'paid_calls':0}));return
    if not args.kit or not args.kit.is_file():
        parser.error('--kit must point to the exported runtime kit.json')
    import bpy
    sys.path.insert(0,str(ROOT/'tools/public_realm_assets'))
    import scene as S
    import sports_furniture as F
    import street_furniture as T
    import importlib.util
    spec=importlib.util.spec_from_file_location('trio',ROOT/'tools/park_trio/build_assets.py')
    trio=importlib.util.module_from_spec(spec);spec.loader.exec_module(trio)
    args.output.mkdir(parents=True,exist_ok=False)
    S.init(args.kit)
    F.material('padding',(.06,.07,.065));F.init();T.init()
    # Opaque tinted panels keep this standalone shelter economical in the viewer.
    S.MATS['glass'].node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=0
    for id,label,category,source in specs:
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        family,builder=source.split(':')
        if family=='trio':trio.export(id,getattr(trio,builder),args.output)
        else:
            if family=='kit':S.kit(builder)
            elif family=='sport':getattr(F,builder)()
            elif family=='street':getattr(T,builder)()
            else:custom(builder,S)
            S.export(args.output/(id+'.glb'),[o for o in bpy.context.scene.objects if o.type=='MESH'])
    (args.output/'sources.json').write_text(json.dumps([dict(id=i,label=l,category=c,source=s) for i,l,c,s in specs],indent=2))

if __name__=='__main__':main()
