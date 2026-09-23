"""Two exact-source civic/industrial clay constructors; no runtime writes."""
import argparse
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import clay_core as C

PALETTE=dict(wall=(.48,.32,.16),timber=(.43,.255,.105),trim=(.13,.17,.12),
    roof=(.12,.145,.155),foundation=(.43,.43,.39),glass=(.34,.40,.40),
    hardware=(.065,.07,.065),interior=(.64,.58,.47),floor=(.36,.25,.15),
    joint=(.28,.19,.11))
SPECS={
 'hall':dict(parent='community_recreation_centre',variant='rec_centre_timber_hall',directory='community_recreation_centre',index=1,
   title='timber-community-hall',dimensions=dict(width=16.4,depth=20.4,height=9.65),floors=1,
   measurements='Compact timber hall, longitudinal main gable, opposed side gables, continuous low hipped veranda, front paired timber doors with two narrow windows; expressed posts and knee braces.',
   assumptions=['Rear doors/windows and occupied hall with tables, chairs, stage and service room are inferred.', 'Metres inferred from doors and porch posts, not survey. Source parent dimensions describe a different recreation centre and are not used.', 'Street, mature trees, play area and parking are separate context.']),
 'warehouse':dict(parent='modern_bigbox_warehouse',variant='warehouse_tilt_wall_mega',directory='modern_bigbox_warehouse',index=1,
   title='tilt-wall-warehouse',dimensions=dict(width=144,depth=86,height=15.2),floors=1,
   measurements='Deep rectangular high-bay warehouse, repetitive dock rows along long elevations, three-level corner office glazing at front-right, pale panel joints and sparse mechanical equipment on a flat parapet roof.',
   assumptions=['Dock count resolved to 26 per long face from partly occluded reference rhythm. Rear docks follow top view.', 'Office has three local levels; warehouse is one high-bay storey. Interior racks, dispatch space, stair and partitions are inferred.', 'Yard, trucks, guardhouse, parking and public street are separate site elements, not attached to building.', 'Dimensions inferred from dock doors, not survey. This is a large industrial asset, never shrink to a residential plot.'])}

def cameras(kind):
    if kind=='hall':
        roster=[('front',(0,-35,5),(0,0,4.5)),('front_corner',(-28,-33,20),(0,0,4)),('aerial',(-29,-34,34),(0,0,3)),('top',(0,0,45),(0,.001,0)),('left_side',(-38,0,5),(0,0,4.5)),('right_side',(38,0,5),(0,0,4.5)),('rear',(0,36,5),(0,0,4.5)),('rear_side',(29,32,23),(0,0,4))]
        details=[('facade_close',(-13,-22,9),(0,-8,5)),('architecture_close',(7,-15,4),(3,-9.7,2.7)),('glass_close',(-5,-12,2.8),(-4,-8,1.8)),('roof_contact',(17,-14,17),(4,0,6)),('side_projection',(-19,-6,10),(-6,1,5.8)),('hall_interior',(0,-7.5,2),(0,6,2))]
    else:
        roster=[('front',(0,-205,40),(0,0,7)),('front_corner',(165,-170,85),(0,0,5)),('aerial',(155,-175,165),(0,0,3)),('top',(0,0,250),(0,.001,0)),('left_side',(-190,0,35),(0,0,7)),('right_side',(190,0,35),(0,0,7)),('rear',(0,205,40),(0,0,7)),('rear_side',(-165,175,95),(0,0,5))]
        details=[('facade_close',(18,-70,12),(5,-43,5)),('architecture_close',(87,-62,10),(63,-43,3)),('glass_close',(77,-54,10),(66,-43,7)),('roof_contact',(65,-38,28),(52,-25,15)),('side_projection',(96,-23,14),(72,-29,7)),('dock_close',(-17,-57,6),(-21,-43,3))]
    return [dict(name=n,location=l,target=t,**({'ortho_scale':24 if kind=='hall' else 172} if n=='top' else {})) for n,l,t in roster]+[dict(name=n,location=l,target=t,whole=False,lens=45) for n,l,t in details]

def manifest(kind,version):
    s=SPECS[kind];cams=cameras(kind)
    return dict(candidate=f'{s["title"]}-clay-v{version:03d}',method=C.METHOD,representation_kind='architectural_clay',
        archetype_id=s['parent'],variant_id=s['variant'],state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        supersedes=f'{s["title"]}-clay-v{version-1:03d}' if version>1 else None,
        finite_corrections=(['Lower gable frame below weathering skin; align cross-gable standing seams downslope.'] if kind=='hall' and version==2 else ['Scale neutral QA lighting to the full warehouse envelope; align side exits with goods floor and add grounded access stairs.'] if kind=='warehouse' and version==2 else ['Ground canopy columns on plinths and give main lobby paired door hardware, a transom and seated approach steps.'] if kind=='warehouse' and version==3 else []),
        measurement_contract=dict(dimensions_m=s['dimensions'],observed_storeys=s['floors'],source_measurements=s['measurements'],hidden_assumptions=s['assumptions']),
        roof_contract=dict(type='joined main and side gables with continuous hipped veranda' if kind=='hall' else 'flat membrane behind continuous panel parapet; seated equipment'),
        material_contract=dict(profile='texture-free semantic architectural clay',authority='exact source timber courses and green/grey standing seams' if kind=='hall' else 'pale concrete panel grid, dark framed office glass, sectional docks and light membrane',limitations='Not textured keeper approval.'),
        identity_contract=dict(owner='native geometry and joints',bitmap_stickers='none'),
        contact_contract=['All foundation minima at grade zero; full apertures and occupied depth.', 'Every roof surface has one owner; projections seated on their carrier.'],
        programme_contract=dict(storeys=s['floors'],description=s['measurements'],limitations=s['assumptions']),
        camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])

def cleanup():
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data);C.bmesh.ops.triangulate(bm,faces=list(bm.faces))
        C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()

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

def furnish(x,y,z=0):
    C.box('Community table',(x,y,z+.77),(2.1,.85,.10),'timber','hall programme')
    for dx in (-.85,.85):
        for dy in (-.30,.30):C.box('Table leg',(x+dx,y+dy,z+.4),(.07,.07,.74),'hardware','hall programme')
    for dy in (-.85,.85):
        for dx in (-.65,.65):
            C.box('Chair seat',(x+dx,y+dy,z+.46),(.45,.44,.07),'timber','hall programme')
            C.box('Chair back',(x+dx,y+dy+math.copysign(.21,dy),z+.72),(.45,.06,.52),'timber','hall programme')
            for vx in (-.17,.17):
                for vy in (-.16,.16):C.box('Chair leg',(x+dx+vx,y+dy+vy,z+.23),(.045,.045,.44),'hardware','hall programme',0)

def hall():
    C.box('Veranda and hall continuous slab',(0,0,.10),(16.4,20.4,.20),'foundation','foundation',0)
    C.box('Hall timber floor',(0,0,.225),(11.5,15.5,.05),'floor','hall programme',0)
    for sign,label in ((-1,'front'),(1,'rear')):
        f=C.Face((0,sign*8,0),(1,0,0),(0,-sign,0),label)
        holes=[dict(id='Paired public doors',u=0,z=.2,w=3.6,h=2.7)]+[dict(id='Hall window',u=x,z=.85,w=1.05,h=1.75) for x in (-4,4)]
        f.wall('Timber end wall',-6,6,.2,5.0,holes=holes)
        f.door('Left timber door',-.9,.2,1.8,2.7,panels=2,panel_cols=4);f.door('Right timber door',.9,.2,1.8,2.7,panels=2,panel_cols=4)
        for h in holes[1:]:f.window(h['id']+str(h['u']),h['u'],h['z'],h['w'],h['h'],cols=1,rows=3)
        lines(f,-6,6,.3,5,holes)
        f.panel('Enclosed main gable',[(-6,5.0),(6,5.0),(0,9.48)],0,.27,'wall','gable')
        for i in range(-29,30):
            u=i*.20;top=9.48-abs(u)*.746
            if top>5.01:f.part('Vertical gable board joint',u,-.008,(5+top)/2,.012,.018,top-5,'joint','gable courses',0)
        for a,b in [((-5.9,5.1),(0,9.48)),((0,9.48),(5.9,5.1)),((-3.4,6.9),(3.4,6.9)),((0,6.9),(0,9.35)),((-2.2,8),(0,6.9)),((0,6.9),(2.2,8))]:
            C.beam('Front gable timber frame',f.p(a[0],-.10,a[1]-.18),f.p(b[0],-.10,b[1]-.18),.20,.22,'timber','gable frame')
    for sign,label in ((-1,'left'),(1,'right')):
        f=C.Face((sign*6,0,0),(0,1,0),(-sign,0,0),label)
        hs=[dict(id=f'Side hall window {y}',u=y,z=.8,w=1.5,h=2.05) for y in (-5,-1.6,1.8,5.2)]
        f.wall('Long enclosed hall wall',-8,8,.2,5.0,holes=hs)
        for h in hs:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,rows=2)
        lines(f,-8,8,.3,5,hs)
        # Source-visible side gables are opaque timber, not invented glass dormers.
        g=C.Face((sign*6.4,0,0),(0,1,0),(-sign,0,0),label+' gable')
        g.panel('Side gable enclosure',[(-2.2,4.66),(4.2,4.66),(1,8.27)],0,.28,'wall','cross gable')
        for i in range(31):
            y=-2.05+i*.2;top=8.27-abs(y-1)*1.128
            if top>4.7:g.part('Side gable boarding',y,-.007,(top+4.7)/2,.012,.018,top-4.7,'joint','cross gable',0)
        for a,b in [((-2.2,4.8),(1,8.4)),((1,8.4),(4.2,4.8)),((-1.6,5.5),(3.6,5.5)),((1,5.5),(1,8.3))]:
            C.beam('Side gable frame',g.p(a[0],-.07,a[1]-.18),g.p(b[0],-.07,b[1]-.18),.18,.2,'timber','cross gable')
        # Exact union boundary removes the main roof under both cross gables.
        xy=[(0,-8.4),(6.4,-8.4),(6.4,-2.2),(1.6,1),(6.4,4.2),(6.4,8.4),(0,8.4)]
        C.solid_surface('Main joined roof',[(sign*x,y,9.6-.75*x) for x,y in xy],.12,'roof','roof union')
        for ya in (-2.2,4.2):
            C.solid_surface('Cross gable roof',[(sign*6.4,ya,4.8),(sign*6.4,1,8.4),(sign*1.6,1,8.4)],.12,'roof','roof union')
            C.beam('Bounded valley flashing',(sign*6.4,ya,4.81),(sign*1.6,1,8.41),.07,.03,'roof','weathering')
        for i in range(41):
            y=-8.2+i*.4;xe=(9.6-(8.4-abs(y-1)*1.125))/.75 if -2.2<y<4.2 else 6.4
            C.beam('Main roof standing seam',(0,y,9.61),(sign*xe,y,9.61-.75*xe),.025,.025,'roof','roof seams')
        for i in range(1,13):
            x=1.6+i*.38;span=(x-1.6)*.75/1.125
            for direction in (-1,1):
                C.beam('Cross roof downslope seam',(sign*x,1,8.412),(sign*x,1+direction*span,8.412-span*1.125),.025,.025,'roof','roof seams')
        C.beam('Cross ridge',(sign*1.6,1,8.43),(sign*6.45,1,8.43),.12,.06,'trim','weathering')
    C.beam('Main ridge',(0,-8.45,9.62),(0,8.45,9.62),.12,.06,'trim','weathering')
    # Four bounded hipped veranda planes with posts under the outer bearing line.
    inner=[(-6.1,-8.1,4.1),(6.1,-8.1,4.1),(6.1,8.1,4.1),(-6.1,8.1,4.1)]
    outer=[(-8,-10,3.35),(8,-10,3.35),(8,10,3.35),(-8,10,3.35)]
    for i in range(4):
        j=(i+1)%4;C.solid_surface('Continuous veranda roof',[inner[i],inner[j],outer[j],outer[i]],.12,'roof','veranda roof')
        C.beam('Veranda hip',inner[i],outer[i],.07,.05,'roof','veranda roof')
        C.beam('Veranda bearing beam',(outer[i][0],outer[i][1],3.18),(outer[j][0],outer[j][1],3.18),.23,.25,'timber','porch support')
        length=(C.Vector(outer[j])-C.Vector(outer[i])).length
        for k in range(1,int(length/.4)):
            t=k/(length/.4);a=C.Vector(outer[i]).lerp(C.Vector(outer[j]),t);b=C.Vector(inner[i]).lerp(C.Vector(inner[j]),t)
            a.z+=.015;b.z+=.015;C.beam('Veranda standing seam',a,b,.022,.022,'roof','roof seams')
    for y in (-9.85,9.85):
        for x in (-7.85,-3.15,3.15,7.85):
            C.box('Front veranda post',(x,y,1.69),(.23,.23,2.98),'timber','porch support')
            for dx in (-.68,.68):
                if abs(x+dx)<8:C.beam('Porch knee brace',(x,y,2.40),(x+dx,y,3.18),.16,.16,'timber','porch support')
    for x in (-7.85,7.85):
        for y in (-6,-2,2,6):
            C.box('Side veranda post',(x,y,1.69),(.23,.23,2.98),'timber','porch support')
            for dy in (-.65,.65):C.beam('Side knee brace',(x,y,2.45),(x,y+dy,3.18),.16,.16,'timber','porch support')
    C.box('Small community stage',(0,5.8,.43),(7,2.8,.36),'timber','hall programme')
    C.box('Stage step',(0,4.15,.31),(3,.5,.12),'timber','hall programme')
    for x in (-2.6,2.6):
        for y in (-4,0):furnish(x,y,.25)
    C.box('Service room wall',(4.5,4.8,1.8),(.18,5,3.1),'interior','service room')
    C.box('Service room end',(5.1,2.3,1.8),(1.2,.18,3.1),'interior','service room')
    C.qa_room_light('hall',(0,1,4.5),450,4)
    C.CONTACTS.append(dict(name='Public entry',front_threshold=[0,-8,.2],porch_edge=[0,-10.2,.2],note='Raised 0.2m slab: Sol must test accessible approach; no route acceptance claimed.'))

def warehouse():
    # Source long dock face is -Y; the glazed office wraps the +X corner.
    W,D,H=144,86,15.2
    C.box('Complete grade foundation',(0,0,.15),(W,D,.30),'foundation','foundation',0)
    goods=C.box('Warehouse raised goods floor',(0,0,.75),(W-.6,D-.6,.9),'foundation','warehouse interior',0)
    C.cut_box(goods,'Ground-level office floor exclusion',(63,-34,.75),(18,18,2))
    for sign,label in ((-1,'front'),(1,'rear')):
        f=C.Face((0,sign*D/2,0),(1,0,0),(0,-sign,0),label)
        hs=[dict(id=f'Dock {i}',u=-66+i*4.6,z=1.2,w=3.1,h=3.6) for i in range(26)]
        if sign==-1:
            hs += [dict(id='Office lobby',u=63,z=.3,w=15,h=3.5),dict(id='Two-level office glass',u=63,z=4.3,w=15,h=7.5)]
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
            hs=[dict(id='Corner office return',u=-35,z=.3,w=16,h=3.5),dict(id='Office upper return',u=-35,z=4.3,w=16,h=7.5)]
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
    for z in (.3,4.1,8.1):
        slab=C.box('Office floor',(63,-34,z+.10),(17,17,.20),'floor','office programme',0)
        if z>1:C.cut_box(slab,'Office stair floor aperture',(58,-26.6,z+.10),(1.5,5.4,1))
        for x in (58,65):
            C.box('Office desk',(x,-40,z+.8),(2,.9,.10),'timber','office programme')
            for dx in (-.8,.8):C.box('Desk support',(x+dx,-40,z+.4),(.07,.7,.8),'trim','office programme')
        if z<8:
            for i in range(20):C.box('Office stair tread',(58,-29+i*.25,z+.1+(i+1)*.2),(1.3,.28,.14),'trim','office circulation')
    C.box('Office enclosed rear partition',(63,-25,6),(18,.18,11.5),'interior','office programme')
    C.box('Office warehouse partition',(54,-34,6),(.18,18,11.5),'interior','office programme')
    for x in (-45,-15,15):
        for y in (-20,0,20):
            for dx in (-5,5):C.box('Warehouse rack upright',(x+dx,y,5),(.15,.15,7.6),'trim','storage racks')
            for z in (2,4,6,8):
                C.box('Warehouse rack shelf',(x,y,z),(10,1.6,.14),'trim','storage racks')
                for dx in (-3,0,3):C.box('Stored carton',(x+dx,y,z+.55),(2.4,1.3,.95),'timber','storage racks')
    C.CONTACTS.append(dict(name='Access contract',main_office_entry=[63,-43,.3],goods_docks_threshold=1.2,note='Docks are freight entries; automatic pedestrian paths must target office/service exits, not dock row.'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=list(SPECS),required=True);p.add_argument('--source-root',type=Path,required=True)
    p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=SPECS[a.kind];root=a.source_root/'frontend/public/archetypes/buildings'/s['directory']
    if (a.source_root/'source-entry.json').exists():
        entry=C.read_json(a.source_root/'source-entry.json');entry['_reference_root']=str(a.source_root/'sources')
    else:
        entry=dict(archetype_id=s['parent'],variant_id=s['variant'],directory='.',_reference_root=str(root),sources=[])
        for role,suffix in [('front','.png'),('oblique','_angle_60.jpg'),('top','_angle_90.jpg')]:
            f=root/f'variant_{s["index"]}{suffix}';entry['sources'].append(dict(role=role,original_path=str(f),path='sources/'+f.name,bytes=f.stat().st_size,sha256=C.digest(f)))
    m=manifest(a.kind,a.version);out=C.prepare_candidate(a,entry,m,__file__)
    if out is None:return
    palette=PALETTE.copy()
    if a.kind=='warehouse':palette.update(wall=(.58,.54,.43),joint=(.34,.33,.29),trim=(.32,.33,.30),roof=(.64,.65,.62),floor=(.46,.44,.39))
    cams=C.setup(palette,m['camera_roster'],a.resolution)
    if a.kind=='warehouse':
        # House-sized QA lamps can sit inside a high-bay roof. Scale the review
        # environment to this envelope; these lights never enter the GLB.
        for obj in C.bpy.context.scene.objects:
            if obj.type=='LIGHT':
                obj.location*=6;obj.data.energy*=36;obj.data.size*=6;C.look_at(obj,(0,0,7))
            if obj.name=='QA ground - excluded':obj.scale*=5
    (hall if a.kind=='hall' else warehouse)();cleanup();C.deliver(out,m,cams)

if __name__=='__main__':main()
