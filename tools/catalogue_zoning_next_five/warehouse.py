"""Warehouse envelope adapted from immutable services batch v003; circulation rebuilt."""
import clay_core as C

def lines(face,lo,hi,z0,z1,holes,vertical=False,pitch=.16):
    # Cut joint segments around every actual aperture; one quiet material family.
    q=lo if vertical else z0
    while q<(hi if vertical else z1):
        spans=[(z0,z1)] if vertical else [(lo,hi)]
        for h in holes:
            if (abs(q-h['u'])<h['w']/2+.04 if vertical else h['z']-.06<q<h['z']+h['h']+.04):
                a,b=(h['z']-.04,h['z']+h['h']+.04) if vertical else (h['u']-h['w']/2-.04,h['u']+h['w']/2+.04)
                spans=[v for l,r in spans for v in [(l,min(r,a)),(max(l,b),r)] if v[1]-v[0]>.02]
        for a,b in spans:
            face.part('Cladding joint',q if vertical else (a+b)/2,-.007,(a+b)/2 if vertical else q,.01 if vertical else b-a,.015,b-a if vertical else .01,'joint','cladding',0)
        q+=pitch

def warehouse(stair,stair_cut,desk):
    # Source long dock face is -Y; the glazed office wraps the +X corner.
    W,D,H=144,86,15.2
    C.box('Complete grade foundation',(0,0,.15),(W,D,.30),'foundation','foundation',0)
    goods=C.box('Warehouse raised goods floor',(0,0,.75),(W-.6,D-.6,.9),'foundation','warehouse interior',0)
    C.cut_box(goods,'Ground-level office floor exclusion',(63,-34,.75),(18,18,2))
    for sign,label in ((-1,'front'),(1,'rear')):
        f=C.Face((0,sign*D/2,0),(1,0,0),(0,-sign,0),label)
        hs=[dict(id=f'Dock {i}',u=-66+i*4.6,z=1.2,w=3.1,h=3.6) for i in range(26)]
        if sign==-1:
            hs += [dict(id='Office lobby',u=63,z=.3,w=15,h=3.5),dict(id='Office middle glass',u=63,z=4.3,w=15,h=3.65),dict(id='Office upper glass',u=63,z=8.45,w=15,h=3.35)]
        f.wall('Tilt wall long elevation',-72,72,.3,H,depth=.32,holes=hs)
        for h in hs:
            if 'Office' in h['id'] or 'office' in h['id']:
                f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=10,rows=2 if h['h']>5 else 1,sill=False,depth=.32)
                if h['id']=='Office lobby':
                    f.part('Public door transom',63,.12,2.85,3,.10,.08,'trim','public entrance')
                    for x in (62.78,63.22):
                        C.rod('Public door pull',f.p(x,.055,1.1),f.p(x,.055,1.7),.022,'hardware','public entrance')
                    f.part('Seated public landing',63,-.4,.15,3.6,.8,.3,'foundation','public approach',0)
                    f.part('Grounded public step',63,-1,.075,3.6,.4,.15,'foundation','public approach',0)
            else:
                f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='trim',panels=7)
                for dx in (-1.70,1.70):f.part('Dock rubber bumper',h['u']+dx,-.13,.85,.20,.26,.62,'hardware','dock hardware')
                f.part('Dock leveller',h['u'],-.10,1.19,3.08,.7,.10,'hardware','dock hardware')
                f.part('Dock shelter head',h['u'],-.14,4.88,3.55,.42,.18,'hardware','dock hardware')
        lines(f,-72,72,4.98,H,hs,vertical=True,pitch=6)
        lines(f,-72,72,7.5,H,hs,pitch=5)
        C.beam('Long parapet cap',(-72,sign*43,H),(72,sign*43,H),.45,.09,'trim','parapet')
    for sign,label in ((-1,'left'),(1,'right')):
        f=C.Face((sign*72,0,0),(0,1,0),(-sign,0,0),label)
        hs=[]
        if sign==1:
            hs=[dict(id='Corner office return',u=-35,z=.3,w=16,h=3.5),dict(id='Office middle return',u=-35,z=4.3,w=16,h=3.65),dict(id='Office upper return',u=-35,z=8.45,w=16,h=3.35)]
            hs += [dict(id=f'Office punched {u} {z}',u=u,z=z,w=1.4,h=2.3) for u in (-22,-18) for z in (.6,4.6,8.6)]
        hs += [dict(id='Side service exit',u=28,z=1.2,w=1.2,h=2.4)]
        f.wall('Tilt wall short elevation',-43,43,.3,H,depth=.32,holes=hs)
        for h in hs:
            if h['id']=='Side service exit':f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='trim',panels=1)
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=10 if h['w']>5 else 1,rows=2 if h['h']>5 else 1,sill=False,depth=.32)
        lines(f,-43,43,.3,H,hs,vertical=True,pitch=6);lines(f,-43,43,7.5,H,hs,pitch=5)
        C.beam('Short parapet cap',(sign*72,-43,H),(sign*72,43,H),.45,.09,'trim','parapet')
        f.part('Service landing',28,-.65,.60,1.8,1.4,1.20,'foundation','service approach',0)
        for i in range(6):
            height=1.2-i*.2
            f.part('Grounded service step',28,-1.5-i*.30,height/2,1.8,.32,height,'foundation','service approach',0)
        for u in (27.13,28.87):
            C.beam('Service stair handrail',f.p(u,-.1,2.22),f.p(u,-1.35,2.22),.045,.045,'hardware','service approach')
            C.beam('Service descending handrail',f.p(u,-1.35,2.22),f.p(u,-3.05,1.05),.045,.045,'hardware','service approach')
            for d,z in ((-.2,1.2),(-1.3,1.2),(-3.05,.03)):
                C.beam('Service guard post',f.p(u,d,z),f.p(u,d,z+1.02),.04,.04,'hardware','service approach')
    # Membrane below parapet: pale, uninterrupted field with sparse service kit.
    C.box('Continuous membrane roof',(0,0,14.62),(143.4,85.4,.25),'roof','roof',0)
    for x in range(-66,70,6):C.box('Membrane lap seam',(x,0,14.751),(.018,85,.012),'joint','roof joints',0)
    for x,y in [(-54,-25),(50,-25),(-54,25),(50,25)]:
        C.box('Seated plant curb',(x,y,14.98),(3.8,2.7,.46),'foundation','roof plant')
        C.box('Rooftop mechanical unit',(x,y,15.75),(3.4,2.3,1.12),'trim','roof plant')
        for j in range(7):C.box('Plant louvre',(x-1.5+j*.5,y-1.16,15.75),(.06,.025,.90),'hardware','roof plant',0)
        for dx in (-.9,.9):C.rod('Unit fan ring',(x+dx,y,16.31),(x+dx,y,16.35),.55,'hardware','roof plant',16)
    for x,y in [(-40,0),(0,0),(40,0),(-20,-27),(20,27)]:
        C.box('Vent curb',(x,y,14.86),(1.6,1.2,.22),'foundation','roof vents')
        C.box('Roof vent hood',(x,y,15.1),(1.8,1.4,.28),'trim','roof vents')
    # Three-level office corner, canopy, circulation and visible furniture.
    C.box('Front office canopy',(63,-44.1,3.95),(18,2.9,.25),'trim','office entrance')
    C.box('Return office canopy',(73,-35,3.95),(2.6,18,.25),'trim','office entrance')
    for x in (55,71):
        C.box('Entry canopy column',(x,-45.2,2.05),(.18,.18,3.5),'trim','office entrance')
        C.box('Grounded canopy plinth',(x,-45.2,.15),(.4,.4,.30),'foundation','office entrance',0)
    for lev,z in enumerate((.5,4.3,8.3)):
        # Edges embed in opaque carriers; the z=8.3 floor sits behind the 7.95..8.45 spandrel.
        slab=C.box('Office floor',(62.92,-33.915,z-.10),(17.68,17.69,.20),'floor','office programme',0)
        if lev:stair_cut(slab,58,-31.5,2.8)
        for x in (58,65):desk(x,-40,z)
        if lev<2:stair(58,-31.5,z,3.8 if lev==0 else 4.0,2.8,11,terminal=lev==1)
        C.qa_room_light('Warehouse office floor '+str(lev),(63,-36,z+3.2),650,5)
    C.box('Office upper ceiling',(63,-34,11.80),(17.84,17.86,.18),'interior','office programme')
    C.box('Office entrance interior step',(63,-42.83,.40),(3.6,.46,.20),'floor','public approach')
    C.box('Office enclosed rear partition',(63,-25,6),(18,.18,11.5),'interior','office programme')
    C.box('Office warehouse partition',(54,-34,6),(.18,18,11.5),'interior','office programme')
    # A readable office/hall access door, above the goods-floor step, in the rear partition.
    rear=next(o for o in C.objects() if o.name=='Office enclosed rear partition')
    C.cut_box(rear,'Rear office door cut',(67,-25,2.4),(1.5,1,2.4))
    f=C.Face((67,-25,0),(1,0,0),(0,-1,0),'office hall access')
    f.door('Office service door',0,1.2,1.5,2.4,role='hardware',panels=1)
    # Landing/riser transition is inside the office; the hall goods floor stays at 1.2m.
    for j in range(4):
        height=.5+(j+1)*.175
        C.box('Goods floor access step',(67,-26.20+j*.30,height/2),(1.8,.32,height),'foundation','office hall access')
    for x in (66.14,67.86):
        C.beam('Goods access handrail',(x,-26.42,1.55),(x,-25.22,2.25),.045,.045,'hardware','office hall access')
        for y,z in ((-26.20,.675),(-25.30,1.2)):
            C.beam('Goods access guard post',(x,y,z),(x,y,z+1.02),.04,.04,'hardware','office hall access')
    for x in (-45,-15,15):
        for y in (-20,0,20):
            for dx in (-5,5):C.box('Warehouse rack upright',(x+dx,y,5),(.15,.15,7.6),'trim','storage racks')
            for z in (2,4,6,8):
                C.box('Warehouse rack shelf',(x,y,z),(10,1.6,.14),'trim','storage racks')
                for dx in (-3,0,3):C.box('Stored carton',(x+dx,y,z+.55),(2.4,1.3,.95),'timber','storage racks')
    C.CONTACTS.append(dict(name='Access contract',main_office_entry=[63,-43,.3],goods_docks_threshold=1.2,note='Docks are freight entries; automatic pedestrian paths must target office/service exits, not dock row.'))
    C.CONTACTS.append(dict(name='Rebuilt office circulation',stair_x=58,stair_y_min=-31.5,stair_y_max=-27.9,
        rear_partition_y=-25,upper_floor_y_max=-25.07,landings=[.5,4.3,8.3],review_defect_closed='WH-01 pending independent review'))
