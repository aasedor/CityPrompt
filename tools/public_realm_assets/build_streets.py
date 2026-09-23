"""Two original straight street-section assets; network geometry remains runtime-owned."""
import argparse,sys,math,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import scene as S
SPECS={
 'shared':dict(id='student_planted_shared_street_v1',title='Planted Shared Street',dimensions_m=[18,48],
   bands=[('edge',.5),('walk',2),('furnishing_garden',3.75),('shared_lane',5.5),('furnishing_garden',3.75),('walk',2),('edge',.5)],
   programme='Flush shared carriageway, two unobstructed sidewalks, four garden rooms and two social bays'),
 'promenade':dict(id='student_garden_cycle_promenade_v1',title='Garden Cycle Promenade',dimensions_m=[16,48],
   bands=[('garden',4),('walk',3),('planted_separator',2),('two_way_cycle',3.5),('garden',3.5)],
   programme='Separate walking and cycling routes, planted separator, connected rest bays and a flush cross-link'),
}
def arrow(x,y,sign):
    S.line((x,y-sign*.55),(x,y+sign*.55),.10)
    S.line((x,y+sign*.55),(x-.3,y+sign*.18),.10)
    S.line((x,y+sign*.55),(x+.3,y+sign*.18),.10)
def bicycle(x,y,sign):
    def p(a,b):return(x-b*sign,y+a*sign)
    for cx in (-.33,.33):
        for j in range(20):
            a=j*math.tau/20;b=(j+1)*math.tau/20
            S.line(p(cx+.23*math.cos(a),-.35+.23*math.sin(a)),p(cx+.23*math.cos(b),-.35+.23*math.sin(b)),.035)
    for a,b in [((-.33,-.35),(-.14,.05)),((-.14,.05),(.08,-.35)),((.08,-.35),(-.33,-.35)),((-.14,.05),(.23,.05)),((.23,.05),(.08,-.35)),((.23,.05),(.33,-.35)),((.23,.05),(.19,.22)),((.19,.22),(.35,.22))]:S.line(p(*a),p(*b),.045)
def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',required=True,choices=SPECS);p.add_argument('--kit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=dict(SPECS[a.kind]);w,d=r['dimensions_m']
    assert abs(sum(b[1] for b in r['bands'])-w)<1e-8;assert a.kit.is_file();assert not a.output.exists()
    if a.dry_run:print('DRY_RUN_PASS',r['id'],w);return
    a.output.mkdir(parents=True);S.init(a.kit);regions=[];x=-w/2
    for kind,width in r['bands']:
        material='paving' if kind in ('walk','shared_lane') else 'cycle' if kind=='two_way_cycle' else 'grass'
        regions.append((x+width/2,0,width,d,material));x+=width
    # Generous cross-link at midblock, free of planting and furniture.
    regions.append((0,0,w,4,'paving'))
    if a.kind=='shared':
        beds=[(x,y,3,7) for x in (-4.7,4.7) for y in (-14,14)]
        for x in (-4.625,4.625):
            for y in (-5.5,5.5):regions.append((x,y,3.75,5,'paving'))
        regions += [(-4.625,21,3.75,3,'paving'),(4.625,-21,3.75,3,'paving')]
        r['clear_routes']=[dict(a=[x,-23.8],b=[x,23.8],width=1.8) for x in (-7.5,7.5)]
        r['clear_routes'] += [dict(a=[0,-23.8],b=[0,23.8],width=5),dict(a=[-8.8,0],b=[8.8,0],width=3)]
        r['clear_routes'] += [dict(a=[side*7.5,y+1.7],b=[side*3.4,y+1.7],width=1.2) for side in (-1,1) for y in (-5.5,5.5)]
    else:
        beds=[(-6,y,3,7) for y in (-14,14)]+[(6,y,3,7) for y in (-14,14)]+[(0,y,1.7,7) for y in (-14,14)]
        for y in (-6,6):regions.append((-5.8,y,3.8,4,'paving'))
        regions += [(-6,21,4,3,'paving'),(-6,-21,4,3,'paving')]
        r['clear_routes']=[dict(a=[-2.5,-23.8],b=[-2.5,23.8],width=2.7),dict(a=[2.75,-23.8],b=[2.75,23.8],width=3.1),dict(a=[-7.8,0],b=[7.8,0],width=3)]
    regions += [(x,y,bw,bd,'soil') for x,y,bw,bd in beds]
    S.ground(w,d,regions)
    for x,y,bw,bd in beds:S.bed(x,y,bw,bd,True,False)
    if a.kind=='shared':
        for x in (-4.7,4.7):
            for y in (-14,14):S.kit('grove_tree',x,y,0,y*.15)
            for y in (-5.5,5.5):S.kit('bench',x,y,0,math.copysign(math.pi/2,-x))
            S.kit('light',x,-8);S.kit('light',x,8)
        S.kit('bike_rack',-4.7,21);S.kit('bin',4.7,-21)
        # Restrained crosswise paving bands visually slow the shared surface.
        for y in (-22,-9,9,22):
            for yy in (y-.15,y+.15):S.line((-2.75,yy),(2.75,yy),.07,'edge',.004)
        # Drainage slots remain outside both clear pedestrian routes.
        for x in (-2.7,2.7):
            for i in range(94):S.line((x,-23.5+i*.5),(x,-23.28+i*.5),.025,'metal',.005)
    else:
        for x in (-5.6,5.6):
            for y in (-14,14):S.kit('grove_tree',x,y,0,y*.15)
        for y in (-6,6):S.kit('bench',-6.4,y,0,math.pi/2)
        for y in (-9,9):S.kit('light',-.55,y)
        S.kit('bike_rack',-6,21);S.kit('bin',-6,-21)
        for y in range(-23,24,3):
            if abs(y)>3:S.line((2.75,y),(2.75,y+1.2),.075)
        for x,sign in ((1.875,-1),(3.625,1)):
            for y in (-19,19):bicycle(x,y,sign);arrow(x,y+sign*1.6,sign)
        r['clear_routes'] += [dict(a=[-5.7,y],b=[-2.5,y],width=1.5) for y in (-6,6)]
    r.update(fixed_width_m=w,fixture_length_m=d,terrain_policy='Level model only; runtime must rebuild all bands along shared sampled ground.',
      junction_policy='No junction or road endpoint is supplied. Omit furniture near network intersections and create connections with the shared street pipeline.',
      limitations=['Original concept, not an official street-manual section or safety certification.','Do not repeat, bend or nonuniformly scale assembly-preview.glb along a route.','No production catalogue activation; route editing, slope, recovery and export remain untested.'])
    for n in ('build_streets.py','scene.py'):shutil.copy2(Path(__file__).with_name(n),a.output/n)
    S.deliver(a.output,r,[('aerial',(32,-43,35),(0,0,1),64),('top',(0,0,80),(0,.001,0),65),('detail',(13,-13,10),(0,-5,1),24)])
if __name__=='__main__':main()
