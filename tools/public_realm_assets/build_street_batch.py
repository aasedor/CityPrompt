"""Build a single new reference-informed street fixture and origin amenity GLBs."""
import argparse, hashlib, json, math, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import scene as S
import street_furniture as F
from street_specs import STREETS, recipe, validate
from build_streets import arrow, bicycle


def patterned_paving(style):
    """Clipped metre-scale tiles, one supported top, no overlapping grass/joints.

    Global coordinates retain pattern phase across ground ownership partitions.
    All walking materials use the paving.* family understood by the ray audit.
    """
    original=S.paving
    if style=='stone':return original
    base={'brick':(.43,.34,.24),'cobble':(.35,.37,.34),'deck':(.36,.27,.17)}[style]
    for i,f in enumerate((.84,.96,1.06,1.12)):
        F.material(f'paving.tile{i}',tuple(c*f for c in base))
    def paving(x,y,w,d):
        S.box('paving underlay',(x,y,-.06),(w,d,.12),'paving')
        tw,td={'brick':(.48,.24),'cobble':(.26,.20),'deck':(3.6,.18)}[style]
        a,b=x-w/2,x+w/2;c,e=y-d/2,y+d/2;groups=[([],[]) for _ in range(4)]
        for j in range(math.floor(c/td),math.ceil(e/td)):
            y0=max(c,j*td+.004);y1=min(e,(j+1)*td-.004)
            offset=(j%2)*tw/2
            for i in range(math.floor((a-offset)/tw),math.ceil((b-offset)/tw)):
                x0=max(a,i*tw+offset+.004);x1=min(b,(i+1)*tw+offset-.004)
                if x1<=x0 or y1<=y0:continue
                verts,faces=groups[(i*13+j*7)%4];n=len(verts)
                verts.extend([(x0,y0,.003),(x1,y0,.003),(x1,y1,.003),(x0,y1,.003)])
                faces.append((n,n+1,n+2,n+3))
        for i,(verts,faces) in enumerate(groups):
            if faces:S.mesh('individual paving units',verts,faces,f'paving.tile{i}')
    return paving


def make(r):
    w,d=r['dimensions_m'];kind=r['kind'];sections={s['name']:s for s in r['sections']}
    regions=[(s['x'],0,s['width'],d,s['material']) for s in r['sections']]
    r['clear_routes']=[];r['reference_assets']=[];r['cycle_directions']=[]
    for s in r['sections']:
        name=s['name']
        if 'walk' in name or 'road' in name or name in ('cycle','shared_lane','play_lane','promenade'):
            r['clear_routes'].append(dict(name=name,a=[s['x'],-d/2+.5],b=[s['x'],d/2-.5],width=s['width']-.4))
    def x(name):return sections[name]['x']
    def width(name):return sections[name]['width']
    def asset(name,bay,y,yaw=0,dx=0):return F.place(r,name,x(bay)+dx,y,yaw)
    def kit(name,bay,y,yaw=0,scale=1,dx=0):return S.kit(name,x(bay)+dx,y,0,yaw,scale)
    def bed(bay,y,depth=5,trees=False,bw=None):
        bw=bw or width(bay)-.3;regions.append((x(bay),y,bw,depth,'soil'));S.bed(x(bay),y,bw,depth,trees,False)
    def tree(bay,y,scale=1,tree_kind='grove_tree',dx=0):
        kit(tree_kind,bay,y,y*.07,scale,dx)
    def link(y=0):
        regions.append((0,y,w,3,'paving'))
        r['clear_routes'].append(dict(name='cross_link',a=[-w/2+.2,y],b=[w/2-.2,y],width=2.6))
    def centre_marks(bay,sign=None):
        if sign:
            for yy in (-17,17):arrow(x(bay),yy,sign)
        else:
            for yy in range(-21,22,4):
                if abs(yy)>3:S.line((x(bay),yy),(x(bay),yy+1.7),.09)
    def cycles(bay):
        centre=x(bay);half=width(bay)/4
        for offset,sign in ((-half,-1),(half,1)):
            for yy in (-17,17):bicycle(centre+offset,yy,sign);arrow(centre+offset,yy+sign*1.5,sign)
            r['cycle_directions'].append(dict(x=centre+offset,sign=sign))
        centre_marks(bay)
    def lit_trees(bay,ys=(-16,-6,6,16),traditional=False,scale=1):
        for yy in ys:tree(bay,yy,scale)
        for yy in (-11,11):
            if traditional:asset('heritage_lantern',bay,yy)
            else:kit('light',bay,yy)
    def drain(bay):
        for side in (-1,1):
            xx=x(bay)+side*(width(bay)/2-.10)
            for yy in range(-int(d/2)+1,int(d/2)-1):
                if abs(yy)>2:S.line((xx,yy),(xx,yy+.30),.035,'metal',.008)
    # Small band edges remain flush, so they cannot form accidental kerbs across links.
    for s in r['sections'][:-1]:
        xx=s['x']+s['width']/2
        for ya,yb in ((-d/2,-1.6),(1.6,d/2)):S.line((xx,ya),(xx,yb),.045,'edge',.006)

    if kind=='main_street':
        link();centre_marks('road');drain('road')
        for side in ('west','east'):
            bay=side+'_furniture';lit_trees(bay,traditional=True)
            for yy in (-3.5,3.5):kit('bench',bay,yy,math.pi/2 if side=='west' else -math.pi/2)
            kit('bin',bay,20)
            parking=side+'_parking';px=x(parking)
            for yy in (-21,-14,-7,7,14,21):
                if side=='west' and -18<yy<-6:continue
                S.line((px-width(parking)/2+.12,yy),(px+width(parking)/2-.12,yy),.07)
        # Flush parklet replaces two western parking markings; no floating deck.
        regions.append((x('west_parking'),-11,2.5,7,'paving'))
        asset('timber_seat_wall','west_parking',-11,math.pi/2)
        for yy in (-14.1,-7.9):kit('planter','west_parking',yy)
        kit('bike_rack','east_furniture',-21)
    elif kind=='cycle_avenue':
        link();cycles('cycle');centre_marks('road')
        for bay in ('west_furniture','east_furniture'):lit_trees(bay)
        for yy in (-16,-7,7,16):bed('separator',yy,5,bw=1.65)
        for yy in (-20,-3.5,3.5,20):
            asset('street_bollard','separator',yy)
        for yy in (-3.5,3.5):kit('bench','east_furniture',yy,-math.pi/2)
        kit('bike_rack','west_furniture',21)
    elif kind=='planted_lane':
        link();drain('shared_lane')
        for bay,sgn in (('west_garden',-1),('east_garden',1)):
            for yy in (-13,13):bed(bay,yy,13,True);tree(bay,yy,.68,dx=-sgn*.20)
            for yy in (-2.5,2.5):bed(bay,yy,1.4)
            for yy in (-17,-14,-11,-8,8,11,14,17):asset('timber_fence_panel',bay,yy,math.pi/2,sgn*1.10)
            for yy in (-5,5):
                regions.append((x(bay),yy,2.5,3,'paving'));kit('bench',bay,yy,sgn*-math.pi/2)
            for yy in (-9,9):kit('light',bay,yy)
    elif kind=='transit_street':
        # Midblock links across a continuous flush fixture; no invented ramps.
        link();cycles('cycle');centre_marks('road')
        lit_trees('west_furniture');lit_trees('east_furniture')
        asset('transit_shelter','island',-6,-math.pi/2,dx=.55)
        asset('transit_stop_pole','island',-11,dx=-.75)
        kit('bin','island',-3,dx=.9)
        island_x=x('island')-.78
        r['clear_routes'].append(dict(name='boarding_strip',a=[island_x,-9],b=[island_x,1],width=1.25))
        # Tactile indicator strips stay on the waiting side of each cycle crossing.
        for yy in (0,10):
            if yy:regions.append((x('cycle'),yy,width('cycle')+3,2.2,'paving'))
            for j in range(7):
                xx=x('cycle')-width('cycle')/2+.2+j*.48
                S.line((xx,yy-.8),(xx,yy+.8),.25)
            for yy2 in (yy-.65,yy+.65):
                S.line((x('island')+.5,yy2),(x('island')+1.35,yy2),.12,'edge',.011)
        for yy in (-3.7,3.7):kit('bench','east_furniture',yy,-math.pi/2)
    elif kind=='market_street':
        link()
        for yy in (-15,-7,7,15):asset('market_stall','west_furniture',yy)
        asset('stone_fountain','east_furniture',-10)
        for yy in (6,13):asset('cafe_parasol','east_furniture',yy)
        for bay in ('west_furniture','east_furniture'):
            for yy in (-20,20):kit('planter',bay,yy);asset('heritage_lantern',bay,yy-2.1)
        kit('bench','east_furniture',-17)
    elif kind=='green_alley':
        link();drain('shared_lane')
        for bay,sgn in (('west_garden',-1),('east_garden',1)):
            for yy in (-15,-6,6,15):asset('planted_trellis',bay,yy,sgn*math.pi/2,sgn*.8)
            for yy in (-10,10):
                regions.append((x(bay),yy,2.7,2.7,'soil'));S.bed(x(bay),yy,2.7,2.7,True,False);tree(bay,yy,.68,dx=-sgn*.15)
            for yy in (-3.5,3.5):kit('bench',bay,yy,sgn*-math.pi/2)
            kit('light',bay,18,dx=sgn*.9)
    elif kind=='heritage_mews':
        link();drain('shared_lane')
        for bay in ('west_furniture','east_furniture'):
            for yy in (-15,-5,5,15):asset('heritage_lantern',bay,yy)
            for yy in (-11,-8,8,11):kit('planter',bay,yy,math.pi/2)
            for yy in (-18,18):asset('street_bollard',bay,yy)
            kit('bench',bay,2.8,math.pi/2)
    elif kind=='boardwalk':
        # Continuous rail at water edge, intentional unguarded route endpoints.
        for yy in range(-21,22,3):asset('boardwalk_guard','water_edge',yy,math.pi/2,dx=-.30)
        for yy in (-16,-8,8,16):asset('boardwalk_hammock','lounge',yy,math.pi/2)
        for yy in (-15,8,15):asset('cafe_table_chairs','east_furniture',yy)
        for yy in (-20,-4,4,20):kit('light','east_furniture',yy,dx=.85)
        for yy in (-5,0,5):kit('bench','lounge',yy,math.pi/2)
        # Furniture bays connect to the central route without a raised lip.
        for yy in (-12,12):
            r['clear_routes'].append(dict(name='lounge_access',a=[x('lounge'),yy],b=[x('east_furniture'),yy],width=1.5))
    elif kind=='school_street':
        F.material('paint.school_blue',(.07,.32,.58));F.material('paint.school_yellow',(.78,.51,.075))
        link();lit_trees('west_furniture',(-16,16));lit_trees('east_furniture',(-16,16))
        for bay in ('west_furniture','east_furniture'):
            for yy in (-6,6):asset('timber_seat_wall',bay,yy,math.pi/2)
            for yy in (-21,21):asset('planted_trellis',bay,yy)
            for yy in (-2.5,2.5):asset('street_bollard',bay,yy)
            for yy in (-10,10):kit('bike_rack',bay,yy)
        # Inlaid paint, never raised play obstacles in the through route.
        for i in range(40):
            yy=-20+i;xx=1.30*math.sin(yy*.24)
            S.line((xx,yy),(1.30*math.sin((yy+1)*.24),yy+1),.65,'paint.school_blue',.014)
        for i in range(8):
            yy=-15+i*.85
            S.rectline(-1.8,yy,.8,.8,.05)
        for yy in (8,11,14,17):
            points=[(-1.8+.40*math.cos(i*math.tau/24),yy+.40*math.sin(i*math.tau/24),.013) for i in range(24)]
            S.mesh('painted play dot',points,[tuple(range(24))],'paint.school_yellow')
    elif kind=='grand_promenade':
        link();centre_marks('west_road',-1);centre_marks('east_road',1)
        for bay in ('west_furniture','east_furniture'):
            lit_trees(bay,(-19,-9,9,19),True)
            for yy in (-4,4):kit('bench',bay,yy,math.pi/2 if bay.startswith('west') else -math.pi/2)
        asset('promenade_kiosk','west_furniture',-14)
        asset('market_stall','east_furniture',14)
        kit('bike_rack','east_furniture',-14);kit('bin','west_furniture',14)
    S.ground(w,d,regions)
    r.update(reference_profile=dict(observed=r['observed_features'],adapted=r['adapted_features']),
        terrain_policy='Straight level concept fixture; reconstruct every band with shared runtime ground.',
        junction_surface={'deck':'timber','cobble':'cobble','brick':'brick','stone':'pavers'}[r['pattern']],
        junction_policy='Network owns all junctions, endpoints, crossings and ramps. Omit or move modules around connections.',
        limitations=['Original section for ideation, not measured from the image or certified for traffic/accessibility/drainage.',
          'Ground-level street fixture; elevated kerbs, operational stop islands and sloped joins require runtime integration.',
          'No buildings, people, vehicles, invented water body or surrounding context included.',
          'Never repeat, bend or nonuniformly stretch assembly-preview.glb; place native amenity modules and rebuild bands.',
          'Browser, Currie terrain, route edits, Undo/Redo, reload and export remain NOT TESTED.'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=STREETS,required=True)
    p.add_argument('--kit',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=validate(recipe(a.kind))
    source=a.reference_root/r['reference'];assert source.is_file();assert a.kit.is_file();assert not a.output.exists()
    if a.dry_run:print('DRY_RUN_PASS',r['id'],r['dimensions_m']);return
    a.output.mkdir(parents=True);target=a.output/'references'/r['reference'];target.parent.mkdir(parents=True);shutil.copy2(source,target)
    r['image_references']=[dict(path=str(target.relative_to(a.output)).replace('\\','/'),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),bytes=source.stat().st_size,source=str(source))]
    r['kit_source']=dict(path=str(a.kit),sha256=hashlib.sha256(a.kit.read_bytes()).hexdigest())
    S.init(a.kit);F.init();S.paving=patterned_paving(r['pattern']);make(r)
    for name in ('build_street_batch.py','street_specs.py','street_furniture.py','sports_furniture.py','scene.py','build_streets.py','verify.py','verify_street_batch.py'):
        shutil.copy2(Path(__file__).with_name(name),a.output/name)
    w,d=r['dimensions_m'];detail_target=(0,-9,1)
    if a.kind=='transit_street':detail_target=(1,-6,1)
    S.deliver(a.output,r,[('aerial',(w*1.5,-d*.9,36),(0,0,1),max(d*1.2,w*1.8)),
        ('top',(0,0,85),(0,.001,0),70),('detail',(w*.85,-24,13),detail_target,24),
        ('street',(.7,-d/2-8,8),(0,2,1),max(w*1.35,21))])


if __name__=='__main__':main()
