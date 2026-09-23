"""Ten finite sports-court parks using the reviewed City Prompt public-realm kit."""
import argparse, json, math, random, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import scene as S
from court_specs import COURTS, recipe

def material(name, colour, alpha=1):
    m=S.bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*colour,alpha)
    shader=m.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value=(*colour,1)
    shader.inputs['Roughness'].default_value=.9 if alpha==1 else .17
    shader.inputs['Alpha'].default_value=alpha
    if alpha<1:m.surface_render_method='DITHERED';m.use_backface_culling=False
    S.MATS[name]=m
    return m

def ring(name,x,y,z,r,wire,mat='rim'):
    n=48
    for i in range(n):
        a=math.tau*i/n;b=math.tau*(i+1)/n
        S.beam(name,(x+r*math.cos(a),y+r*math.sin(a),z),(x+r*math.cos(b),y+r*math.sin(b),z),wire,mat,6)

def basket_net(x,y,z,r):
    for i in range(12):
        a=math.tau*i/12;b=a+math.pi/12
        S.beam('basket net',(x+r*math.cos(a),y+r*math.sin(a),z),
               (x+r*.6*math.cos(b),y+r*.6*math.sin(b),z-.42),.003,'paint',4)
    for j in (1,2,3):ring('basket net',x,y,z-j*.105,r*(1-j*.1),.003,'paint')

def basketball_hoop(baseline,sign,r):
    # Pole outside the clear baseline reserve; cantilever carries the backboard.
    pole_y=baseline+sign*2.5;board_y=baseline-sign*1.2;rim_y=baseline-sign*1.575
    S.box('hoop anchor',(0,pole_y,.08),(.7,.8,.16),'metal')
    S.beam('hoop mast',(0,pole_y,0),(0,pole_y,4),.115,'metal',10)
    S.box('mast padding',(0,pole_y,.95),(.29,.31,1.7),'padding')
    S.beam('cantilever',(0,pole_y,3.8),(0,board_y,3.65),.075,'metal',8)
    S.beam('backboard brace',(0,pole_y,2.8),(0,board_y,3.3),.05,'metal',8)
    S.box('backboard',(0,board_y,3.425),(1.8,.035,1.05),'board')
    # Facing target rectangle, visible from inside the court.
    face=board_y-sign*.022
    for xx in (-.295,.295):S.box('backboard target',(xx,face,3.275),(.05,.01,.45),'paint')
    for zz in (3.05,3.50):S.box('backboard target',(0,face,zz),(.64,.01,.05),'paint')
    S.beam('rim bracket',(0,board_y,3.04),(0,rim_y+sign*.225,3.04),.025,'rim')
    ring('basket rim',0,rim_y,3.05,.225,.01);basket_net(0,rim_y,3.035,.225)
    r.setdefault('equipment',[]).append(dict(kind='basketball_hoop',x=0,y=rim_y,z=3.05,radius=.225))

def basketball_end(baseline,sign,r):
    # sign points outwards; local distance t points from the baseline into court.
    pos=lambda x,t:(x,baseline-sign*t)
    S.box('painted key',(0,baseline-sign*2.9,.003),(4.9,5.8,.004),'key')
    for x in (-2.45,2.45):S.line(pos(x,0),pos(x,5.8))
    S.line(pos(-2.45,5.8),pos(2.45,5.8))
    S.arc(0,baseline-sign*5.8,1.775,0,math.pi if sign<0 else -math.pi,width=.05)
    S.arc(0,baseline-sign*1.575,1.25,0,math.pi if sign<0 else -math.pi,width=.05)
    # Arc joins the straight corner lines exactly; no full-circle spill outside court.
    radius=6.725;xcorner=6.575;join=math.sqrt(radius**2-xcorner**2)
    steps=72
    a=math.acos(xcorner/radius)
    for i in range(steps):
        aa=a+(math.pi-2*a)*i/steps;bb=a+(math.pi-2*a)*(i+1)/steps
        S.line(pos(radius*math.cos(aa),1.575+radius*math.sin(aa)),pos(radius*math.cos(bb),1.575+radius*math.sin(bb)))
    for x in (-xcorner,xcorner):S.line(pos(x,0),pos(x,1.575+join))
    basketball_hoop(baseline,sign,r)

def court_net(width,center,end,bottom=.06,mesh_step=.075,post_height=None,padding=False):
    post_height=post_height or end+.08
    for x in (-width/2,width/2):
        S.beam('net upright',(x,0,0),(x,0,post_height),.045,'metal',10)
        if padding:S.beam('net upright padding',(x,0,.1),(x,0,1.85),.10,'padding',10)
    top=lambda x:center+(end-center)*(2*x/width)**2
    n=math.ceil(width/mesh_step)
    for i in range(n+1):
        x=-width/2+width*i/n
        S.beam('net mesh',(x,0,bottom),(x,0,top(x)),.003,'net',4)
    rows=max(1,math.ceil((center-bottom)/mesh_step))
    for j in range(rows+1):
        for i in range(32):
            x=-width/2+width*i/32;xx=-width/2+width*(i+1)/32
            z=bottom+(top(x)-bottom)*j/rows;zz=bottom+(top(xx)-bottom)*j/rows
            S.beam('net mesh',(x,0,z),(xx,0,zz),.003,'net',4)
    for i in range(48):
        x=-width/2+i*width/48;xx=x+width/48
        # Flat 50 mm tape at exact top datum, not an oversized white tube.
        S.mesh('net tape',[(x,-.008,top(x)),(xx,-.008,top(xx)),(xx,-.008,top(xx)-.05),(x,-.008,top(x)-.05)],[(0,1,2,3)],'paint')

def side_gate_fence(w,d,gate_y,h=2.8):
    for a,b in [((-w/2,-d/2),(w/2,-d/2)),((w/2,-d/2),(w/2,d/2)),
                ((w/2,d/2),(-w/2,d/2)),((-w/2,-d/2),(-w/2,gate_y-1.05)),
                ((-w/2,gate_y+1.05),(-w/2,d/2))]:S.fence_segment(a,b,h)

def raised_mesh(a,b,h,z):
    before=set(S.bpy.context.scene.objects);S.fence_segment(a,b,h)
    for o in set(S.bpy.context.scene.objects)-before:o.location.z+=z

def padel_walls():
    for y in (-10.015,10.015):
        for i in range(5):
            x=-4+i*2;S.box('end glass',(x,y,1.5),(1.986,.03,3),'glass')
        for x in (-5,-3,-1,1,3,5):S.beam('glass mullion',(x,y,0),(x,y,4),.027,'metal',8)
        raised_mesh((-5,y),(5,y),1,3)
    for x in (-5.015,5.015):
        for sign in (-1,1):
            for yy in (7,9):S.box('side glass',(x,sign*yy,1.5),(.03,1.986,3),'glass')
            for yy in (6,8,10):S.beam('glass mullion',(x,sign*yy,0),(x,sign*yy,3),.027,'metal',8)
            raised_mesh((x,sign*8),(x,sign*10),1,3)
            S.fence_segment((x,sign*1.15),(x,sign*6),3)
            # Two 1.10 m openings separated by the net support, 2.20 m clear height.
            raised_mesh((x,sign*.05),(x,sign*1.15),.8,2.2)
            S.beam('door padding',(x,sign*1.15,0),(x,sign*1.15,2.2),.06,'padding',8)
            S.beam('door padding',(x,sign*.05,2.2),(x,sign*1.15,2.2),.045,'padding',8)

def aggregate(w,d,material_name):
    rng=random.Random(17);verts=[];faces=[]
    for i in range(min(2600,int(w*d*6))):
        x=rng.uniform(-w/2+.1,w/2-.1);y=rng.uniform(-d/2+.1,d/2-.1);s=rng.uniform(.014,.05)
        k=len(verts);verts.extend([(x-s,y,.002),(x+s,y,.002),(x,y+s,.004)]);faces.append((k,k+1,k+2))
    S.mesh('fine aggregate',verts,faces,material_name)

def sports_module(r):
    kind=r['sport'];pw,pd=r['playing_m'];mw,md=r['module_m']
    gate_y=-md/2+3;gate_width=1.8
    if kind=='padel':gate_y=-.6;gate_width=.86
    surface='sand' if kind=='beach_volleyball' else 'gravel' if kind in ('bocce','petanque') else 'court'
    # Keep the underlay below playing/sand surfaces: coincident top faces turn
    # black or flicker after GLB reimport. The 12 mm reveal is a concept finish.
    S.box('sport base',(0,0,-.066),(mw,md,.108),'runoff')
    if surface in ('sand','gravel'):S.box('granular surface',(0,0,-.035),(mw,md,.07),surface);aggregate(mw,md,surface+'_grain')
    else:S.box('playing surface',(0,0,-.03),(pw,pd,.06),'court')
    if kind in ('basketball','three_x_three'):
        # FIBA boundaries lie outside the 15 x 28 / 15 x 11 inner playing area.
        S.rectline(0,0,pw+.05,pd+.05)
        basketball_end(pd/2,1,r)
        if kind=='basketball':
            basketball_end(-pd/2,-1,r);S.line((-pw/2-.15,0),(pw/2+.15,0));S.arc(0,0,1.775,width=.05)
        side_gate_fence(mw,md,gate_y,3)
    elif kind=='netball':
        S.rectline(0,0,pw-.05,pd-.05)
        for y in (-pd/6,pd/6):S.line((-pw/2,y),(pw/2,y))
        S.arc(0,0,.425,width=.05)
        for sign in (-1,1):
            y=sign*pd/2
            S.arc(0,y,4.875,0,math.pi if sign<0 else -math.pi,width=.05)
            S.beam('netball post',(0,y,0),(0,y,3.05),.04,'metal',10)
            S.beam('post cushion',(0,y,.05),(0,y,1.8),.085,'padding',10)
            ring_y=y-sign*.225
            ring('netball ring',0,ring_y,3.05,.19,.008);basket_net(0,ring_y,3.035,.19)
            r.setdefault('equipment',[]).append(dict(kind='netball_hoop',x=0,y=ring_y,z=3.05,radius=.19))
        side_gate_fence(mw,md,gate_y,2.6)
    elif kind in ('tennis','badminton','padel'):
        if kind!='padel':S.rectline(0,0,pw-.05,pd-.05,.04 if kind=='badminton' else .05)
        singles=r.get('singles_width_m',pw)
        if kind!='padel':
            for x in (-singles/2,singles/2):S.line((x,-pd/2),(x,pd/2),.04 if kind=='badminton' else .05)
        sd=r['service_distance_m']
        for sign in (-1,1):
            S.line((-singles/2,sign*sd),(singles/2,sign*sd),.04 if kind=='badminton' else .05)
            if kind=='badminton':
                S.line((-pw/2,sign*(pd/2-.76)),(pw/2,sign*(pd/2-.76)),.04)
                S.line((0,sign*sd),(0,sign*pd/2),.04)
            else:S.line((0,0),(0,sign*(sd+(.2 if kind=='padel' else 0))))
        if kind=='tennis':
            for sign in (-1,1):S.line((0,sign*(pd/2-.1)),(0,sign*pd/2),.05)
        nw=pw+1.828 if kind=='tennis' else pw-.08 if kind=='padel' else pw
        court_net(nw,r['net_center_m'],r['net_end_m'],bottom=.78 if kind=='badminton' else .03,
                  mesh_step=.05,post_height=1.55 if kind=='badminton' else 1.07 if kind=='tennis' else 1.05)
        if kind=='padel':padel_walls()
        elif kind=='tennis':side_gate_fence(mw,md,gate_y,3)
        else:
            # Low end screens frame the calm-weather garden; sides remain open.
            for y in (-md/2,md/2):S.fence_segment((-mw/2,y),(mw/2,y),2.4)
    elif kind in ('volleyball','beach_volleyball'):
        S.rectline(0,0,pw-.05,pd-.05,.05)
        if kind=='volleyball':
            S.line((-pw/2,0),(pw/2,0))
            for y in (-3,3):S.line((-pw/2,y),(pw/2,y))
        nw=pw+1.5
        court_net(nw,2.43,2.43,bottom=1.43,mesh_step=.10,post_height=2.55,padding=True)
        for x in (-pw/2,pw/2):
            for i in range(8):S.beam('antenna',(x,0,2.43+i*.1),(x,0,2.43+(i+1)*.1),.006,'paint' if i%2==0 else 'rim',6)
        # No hard perimeter fence at the edge of sand run-off.
        if kind=='volleyball':
            for y in (-md/2,md/2):S.fence_segment((-mw/2,y),(mw/2,y),2.6)
    elif kind=='bocce':
        # Natural fine aggregate lane and timber boards. Access leaf shown open.
        S.box('bocce lane',(0,0,-.025),(pw,pd,.05),'bocce_lane');aggregate(pw,pd,'gravel_grain')
        for y in (-pd/2-.07,pd/2+.07):S.box('hinged end board',(0,y,.125),(pw+.28,.14,.25),'timber')
        left=-pw/2-.07
        S.box('side board',(pw/2+.07,0,.125),(.14,pd,.25),'timber')
        for a,b in ((-pd/2,gate_y-1.05),(gate_y+1.05,pd/2)):
            S.box('side board',(left,(a+b)/2,.125),(.14,b-a,.25),'timber')
        for side in (-1,1):S.box('open access leaf',(left-.525,gate_y+side*1.15,.125),(1.05,.14,.25),'timber')
        for y in (-pd/2+4,0,pd/2-4):S.line((-pw/2,y),(pw/2,y),.015,'paint')
    elif kind=='petanque':
        for x in (-2.25,2.25):
            S.rectline(x,0,pw,pd,.015)
            # One loose throwing circle per lane, no invented sports line pattern.
            S.arc(x,-pd/2+1.2,.25,width=.015)
        # Low edging beyond the marked lanes; open west access matches the path.
        for y in (-8.1,8.1):S.box('gravel retaining edge',(0,y,.055),(10.4,.08,.11),'timber')
        S.box('gravel retaining edge',(5.2,0,.055),(.08,16.2,.11),'timber')
        for a,b in ((-8.1,gate_y-1.05),(gate_y+1.05,8.1)):
            if b>a:S.box('gravel retaining edge',(-5.2,(a+b)/2,.055),(.08,b-a,.11),'timber')
    if 'net_center_m' in r:r['equipment']=[dict(kind='court_net',height_center=r['net_center_m'],height_end=r['net_end_m'])]
    return gate_y,gate_width

def park(r,out):
    w,d=r['dimensions_m'];mw,md=r['module_m'];cy=2;front=cy-md/2
    before=set(S.bpy.context.scene.objects)
    gy,gw=sports_module(r)
    objects=list(set(S.bpy.context.scene.objects)-before)
    r['sport_asset']=S.export(out/'sport-module.glb',objects)
    for o in objects:o.location.y+=cy
    gate_y=gy+cy;walk_x=-mw/2-1.7
    bed_x=mw/2+6.7;bed_ys=[cy-md*.25,cy+md*.25]
    beds=[(x,y,4.2,5.4) for x in (-bed_x,bed_x) for y in bed_ys]
    terrace_y=front-6
    regions=[(0,cy,mw+7,md+7,'paving'),(0,front-6,w-4,10,'paving'),
             (3.2,-d/2+1.5,3,3,'paving'),
             *[(x,y,bw,bd,'soil') for x,y,bw,bd in beds],(0,cy,mw,md,None)]
    S.ground(w,d,regions)
    for x,y,bw,bd in beds:
        S.bed(x,y,bw,bd,True,False);S.kit('grove_tree',x,y,0,x*.13+y*.17)
    # Front terrace trees are deliberately on hardscape: shared builder adds wells.
    for x in (-bed_x,bed_x):S.kit('ornamental_tree',x,terrace_y,0,x*.08)
    S.pergola(0,terrace_y,7,3.3)
    for x in (-2.25,2.25):S.kit('bench',x,terrace_y+.65)
    for x in (-mw/2-4,mw/2+4):
        # Seating alcoves sit outside the continuous 1.8 m court-side walking route.
        for y in (cy-1.8,cy+3.5):
            S.SURFACES.append(dict(x=x,y=y,width=1.2,depth=3.2,material='paving'))
            S.kit('bench',x,y,0,math.copysign(math.pi/2,-x))
    for x in (-mw/2-2.8,mw/2+2.8):
        for y in (front-3,cy+md/2+2.6):S.kit('light',x,y)
    S.kit('bike_rack',5.4,terrace_y);S.kit('bin',-5.4,terrace_y)
    # Human-scale spectator table on a connected south apron.
    S.kit('picnic_table',-5.4,front-9.2)
    # Main approach passes beside the table, then through the open pergola centre.
    entry_x=3.2
    r['clear_routes']=[dict(a=[entry_x,-d/2+.1],b=[entry_x,front-9],width=1.8),
        dict(a=[entry_x,front-9],b=[0,front-9],width=1.8),
        dict(a=[0,front-9],b=[0,front-2],width=1.8),
        dict(a=[0,front-2],b=[walk_x,front-2],width=1.8),
        dict(a=[walk_x,front-2],b=[walk_x,gate_y],width=1.8)]
    # Do not label sand or the bocce leaf a paved accessible route.
    endpoint= -r['playing_m'][0]/2+1 if r['sport']!='petanque' else -4.2
    r['sport_access_routes']=[dict(a=[walk_x,gate_y],b=[endpoint,gate_y],width=gw)]
    r['fixed_program']=dict(center=[0,cy],size=[mw,md],entry=[-mw/2,gate_y],entry_width=gw)
    r['style']='Shared meadow furniture/vegetation/tree wells; original restrained sport palette'
    r['browser_testing']='DEFERRED BY USER; no browser or runtime activation in this batch'
    return [('aerial',(w*.9,-d*.9,d*.8),(0,0,.5),max(w,d)*1.40),
            ('top',(0,0,100),(0,.001,0),max(w,d)*1.1),
            ('detail',(mw*.4+7,front-12,9),(0,front-3.5,1),24),
            ('court',(-mw*.8,cy-md*.4,14),(0,cy,1),max(mw,md)*1.12)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=COURTS,required=True)
    p.add_argument('--kit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=recipe(a.kind)
    assert a.kit.is_file();assert not a.output.exists(),a.output
    if a.dry_run:print('DRY_RUN_PASS',json.dumps(r));return
    a.output.mkdir(parents=True);S.init(a.kit)
    shader=S.MATS['court'].node_tree.nodes['Principled BSDF'];shader.inputs['Base Color'].default_value=(*r['court_colour'],1)
    material('key',[.29,.40,.35]);material('padding',[.08,.13,.12]);material('rim',[.61,.20,.06]);material('board',[.65,.69,.64])
    material('glass',[.52,.69,.67],.20);material('sand',[.63,.54,.37]);material('sand_grain',[.45,.38,.24])
    material('gravel',[.39,.37,.30]);material('gravel_grain',[.25,.24,.21]);material('bocce_lane',[.51,.43,.29])
    cameras=park(r,a.output)
    for name in ('build_courts.py','court_specs.py','scene.py'):shutil.copy2(Path(__file__).with_name(name),a.output/name)
    S.deliver(a.output,r,cameras)
if __name__=='__main__':main()
