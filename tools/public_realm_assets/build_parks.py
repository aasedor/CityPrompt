"""Three finite original park concepts using the current City Prompt kit."""
import argparse, sys, json, math, shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import scene as S

SPECS={
 'pickleball':dict(id='student_pickleball_garden_v1',title='Pickleball Social Garden',dimensions_m=[34,34],playing_m=[6.096,13.4112],module_m=[10.8,20],
   source='https://usapickleball.org/construction/',programme='One court, open entrance, shaded social terrace, two planted gardens'),
 'futsal':dict(id='student_futsal_park_v1',title='Community Futsal Park',dimensions_m=[42,60],playing_m=[20,40],module_m=[26,46],
   source='https://www.thefa.com/-/media/cfa/global/files/mini-soccer-youth-futsal-handbook.ashx?la=en',programme='One outdoor concept court, two 3 x 2 m goals, open entry, shaded team terrace'),
 'reading':dict(id='student_reading_garden_v1',title='Shaded Reading Garden',dimensions_m=[30,26],programme='Two reading pergolas, open central lawn, clear crosswalks, layered planting and social seats'),
}
def net(w):
    for x in (-w/2,w/2):S.beam('net post',(x,0,0),(x,0,.98),.038,'metal',8)
    for i in range(43):
        x=-w/2+i*w/42;h=.8636+.0508*(abs(x)/(3.048))**2
        S.beam('net vertical',(x,0,.05),(x,0,min(h,.94)),.0035,'net',4)
    for j in range(8):S.beam('net horizontal',(-w/2,0,.06+j*.1),(w/2,0,.06+j*.1),.0035,'net',4)
    for i in range(24):
        x1=-w/2+i*w/24;x2=x1+w/24
        S.beam('white net tape',(x1,0,.8636+.0508*(x1/3.048)**2),(x2,0,.8636+.0508*(x2/3.048)**2),.015,'paint',6)
def goal(y,sign):
    # Clear inner opening 3.00 x 2.00 m, 80 mm posts, weighted rear frame.
    for x in (-1.54,1.54):S.box('goal post',(x,y,1.04),(.08,.08,2.08),'paint')
    S.box('goal crossbar',(0,y,2.04),(3.16,.08,.08),'paint')
    rear=y+sign*1.05
    for x in (-1.54,1.54):
        S.beam('goal rear frame',(x,y,.04),(x,rear,.04),.035,'metal')
        S.beam('goal support',(x,y,2),(x,rear,1.5),.025,'metal')
        for i in range(12):
            yy=y+sign*i*1.05/11;h=2-i*.5/11
            S.beam('side net',(x,yy,.08),(x,yy,h),.004,'net',4)
        for j in range(1,15):S.beam('side net',(x,y,j*.1),(x,rear,j*.1),.004,'net',4)
    S.box('weighted goal base',(0,rear,.08),(3.16,.18,.16),'metal')
    for i in range(25):
        x=-1.5+i*3/24
        S.beam('rear net',(x,rear,.12),(x,rear,1.5),.004,'net',4)
        S.beam('roof net',(x,y,2),(x,rear,1.5),.004,'net',4)
    for j in range(1,15):S.beam('rear net',(-1.5,rear,j*.1),(1.5,rear,j*.1),.004,'net',4)
def sports(kind,out,r):
    w,d=r['dimensions_m'];mw,md=r['module_m'];pw,pd=r['playing_m'];cy=3 if kind=='pickleball' else 2
    before=set(S.bpy.context.scene.objects)
    S.box('runoff',(0,0,-.06),(mw,md,.12),'runoff')
    S.box('playing surface',(0,0,.002),(pw,pd,.004),'court')
    S.rectline(0,0,pw-.0508 if kind=='pickleball' else pw-.08,pd-.0508 if kind=='pickleball' else pd-.08,.0508 if kind=='pickleball' else .08)
    if kind=='pickleball':
        S.box('non volley zone',(0,0,.005),(pw-.1,4.2672,.003),'kitchen')
        for yy in (-2.1336,2.1336):S.line((-pw/2,yy),(pw/2,yy),.0508)
        for sign in (-1,1):S.line((0,sign*2.1336),(0,sign*pd/2),.0508)
        net(6.7056);S.enclosure(mw,md,2.7)
    else:
        S.line((-10,0),(10,0),.08);S.arc(0,0,3)
        for sign in (-1,1):
            y=sign*20;goal(y,sign)
            # Penalty boundary: two 6 m quarter circles joined across goal width.
            if sign==1:
                S.arc(-1.58,y,6,math.pi,1.5*math.pi);S.arc(1.58,y,6,1.5*math.pi,2*math.pi)
            else:
                S.arc(-1.58,y,6,math.pi/2,math.pi);S.arc(1.58,y,6,0,math.pi/2)
            S.line((-1.58,y-sign*6),(1.58,y-sign*6),.08)
            for dd in (6,10):S.arc(0,y-sign*dd,.06,width=.06)
        S.enclosure(mw,md,3,5)
    module=list(set(S.bpy.context.scene.objects)-before)
    r['sport_asset']=S.export(out/'sport-module.glb',module)
    for o in module:o.location.y+=cy
    south=-d/2+4
    beds=[(-w/2+4,-4,4,7), (w/2-4,-4,4,7),(-w/2+4,d/2-6,4,6),(w/2-4,d/2-6,4,6)]
    regions=[(0,0,mw+4,d,'paving'),(-w/2+4,south,8,4,'paving'),(w/2-4,south,8,4,'paving'),
      *[(x,y,bw,bd,'soil') for x,y,bw,bd in beds],(0,cy,mw,md,None)]
    S.ground(w,d,regions)
    for x,y,bw,bd in beds:S.bed(x,y,bw,bd,True,False)
    for x in (-w/2+4,w/2-4):
        for y in (-4,d/2-6):S.kit('grove_tree',x,y,0,abs(y)*.3)
        S.kit('ornamental_tree',x,south,0,x*.12,.9)
    S.pergola(0,south,7,3)
    for x in (-2.1,2.1):S.kit('bench',x,south+.65)
    for x in (-mw/2-1.2,mw/2+1.2):
        for y in (cy-3,cy+5):S.kit('bench',x,y,0,math.copysign(math.pi/2,-x))
        S.kit('light',x,south+3)
    S.kit('bike_rack',mw/2+1.25,south)
    S.kit('bin',-mw/2-1.25,south)
    r['clear_routes']=([dict(a=[0,-d/2+.1],b=[0,cy-md/2+2],width=1.8)] if kind=='pickleball' else
      [dict(a=[0,-d/2+.1],b=[0,-23.5],width=1.8),dict(a=[0,-23.5],b=[5,-23.5],width=1.8),dict(a=[5,-23.5],b=[5,-18],width=1.8)])
    r['fixed_program']=dict(center=[0,cy],size=[mw,md],entry=[0 if kind=='pickleball' else 5,cy-md/2],entry_width=2)
    r['limitations']=['Outdoor neighbourhood concept, not certified competition or accessibility design.','Court geometry is fixed size; surrounding park may be redesigned, never squeeze court or runoff.']
    scale=max(w,d)*1.45
    return [('aerial',(w*.8,-d*.9,d*.85),(0,0,1),scale),('top',(0,0,90),(0,.001,0),max(w,d)*1.12),
      ('detail',(12,south-11,9),(0,south+4,1),21)]
def reading(r):
    w,d=r['dimensions_m'];beds=[(x,y,4,2.5) for x in (-11,11) for y in (-3.25,3.25)]+[(-5.5,9,5,3),(5.5,9,5,3),(-5.5,-9,5,3),(5.5,-9,5,3)]
    regions=[(0,0,3,d,'paving'),(0,0,w,3,'paving'),(-10,0,7,d,'paving'),(10,0,7,d,'paving'),
      (0,9,w,5,'paving'),(0,-9,w,5,'paving'),(0,-5,6.6,4,'paving'),(0,5,6.6,4,'paving'),*[(x,y,bw,bd,'soil') for x,y,bw,bd in beds]]
    S.ground(w,d,regions)
    for x,y,bw,bd in beds:S.bed(x,y,bw,bd,False,False)
    for x in (-10,10):
        for y in (-8.5,8.5):S.kit('grove_tree',x,y,0,x*.2+y*.1)
    for y in (-5,5):
        S.pergola(0,y,6,3.5)
        for x in (-2,2):S.kit('bench',x,y,0,math.copysign(math.pi/2,-x))
    for x in (-10,10):
        S.kit('backless_bench',x,-6)
        S.kit('picnic_table',x,6)
        for y in (-11,11):S.kit('light',x,y)
    S.kit('bike_rack',4,-11);S.kit('bin',-4,-11)
    r['clear_routes']=[dict(a=[0,-12.8],b=[0,12.8],width=1.8),dict(a=[-14.8,0],b=[14.8,0],width=1.8)]
    r['limitations']=['Original concept, no compliance claim.','Level preview only; surfaces and approaches need shared terrain integration.']
    return [('aerial',(28,-34,30),(0,0,0),39),('top',(0,0,60),(0,.001,0),34),('detail',(12,-16,9),(0,-4,1),22)]
def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=SPECS,required=True);p.add_argument('--kit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);r=dict(SPECS[a.kind]);assert a.kit.is_file();assert not a.output.exists()
    if a.dry_run:print('DRY_RUN_PASS',json.dumps(r));return
    a.output.mkdir(parents=True);S.init(a.kit)
    cameras=reading(r) if a.kind=='reading' else sports(a.kind,a.output,r)
    for name in ('build_parks.py','scene.py'):shutil.copy2(Path(__file__).with_name(name),a.output/name)
    S.deliver(a.output,r,cameras)
if __name__=='__main__':main()
