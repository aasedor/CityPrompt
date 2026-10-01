"""Exact corner-cafe family: open courtyard, ochre/stone facades and seated mansard."""
import argparse, importlib.util, json, math, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'catalogue_duplex_pilot'))
import clay_core as C
import bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon,intersect_line_line_2d
spec=importlib.util.spec_from_file_location('shared_building',HERE.parent/'showcase_building_trio/build.py');B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
PALETTE=dict(B.PALETTE,wall=(.57,.36,.16),stone=(.69,.62,.47),roof=(.32,.34,.32),trim=(.11,.18,.12),glass=(.35,.40,.35),timber=(.35,.23,.12),mortar=(.45,.34,.21))
PLAN=[(-18,18),(-10,-13),(-3,-18),(3,-18),(10,-13),(22,22),(13,22),(4,-3),(-1,-5),(-5,-1),(-9,18)]
UPPER_RING_DEPTH=3.7  # Larger offsets fold across the narrow left wing.

def local_bevel(obj,width=.012,segments=1):
    """Apply the same small edge chamfer without a scene-wide operator update."""
    if width<=0:return
    bm=bmesh.new();bm.from_mesh(obj.data)
    edges=[e for e in bm.edges if e.is_manifold and e.calc_face_angle(0)>.523599]
    bmesh.ops.bevel(bm,geom=edges,offset=width,segments=segments,affect='EDGES',clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()

def offset(poly,d):
    result=[]
    for i,p in enumerate(poly):
        a=Vector(poly[i-1]);b=Vector(p);c=Vector(poly[(i+1)%len(poly)]);v=(b-a).normalized();w=(c-b).normalized();n=Vector((-v.y,v.x))*d;m=Vector((-w.y,w.x))*d
        # Infinite-line intersection: the segment helper drops concave mitres.
        den=v.x*w.y-v.y*w.x
        delta=m-n
        q=b+n if abs(den)<1e-8 else b+n+v*((delta.x*w.y-delta.y*w.x)/den)
        result.append(tuple(q))
    return result

def slab(name,poly,z,thick,role):
    # Concave courtyard remains empty; triangulate its actual polygon.
    verts=[Vector((x,y,z)) for x,y in poly];tris=tessellate_polygon([verts])
    for tri in tris:
        pts=[tuple(verts[v] if isinstance(v,int) else v) for v in tri]
        C.solid_surface(name,pts,thick,role,'floor' if role=='floor' else 'envelope')

def balcony(face,u,z,width):
    face.part('stone balcony bearing',u,-.48,z,width,1.02,.16,'stone','balconies',0)
    a=face.p(u-width/2,-.98,z+.08);b=face.p(u+width/2,-.98,z+.08)
    C.railing('wrought balcony',a,b,.92,.20,'hardware')
    for side in (-1,1):C.railing('balcony return',face.p(u+side*width/2,0,z+.08),face.p(u+side*width/2,-.98,z+.08),.92,.20,'hardware')
    for i in range(max(1,int(width/.34))):
        xx=u-width/2+.18+i*.34
        for j in range(12):
            a=j*math.tau/12;b=(j+1)*math.tau/12
            C.rod('balcony scroll',face.p(xx+.14*math.cos(a),-.99,z+.53+.25*math.sin(a)),face.p(xx+.14*math.cos(b),-.99,z+.53+.25*math.sin(b)),.011,'hardware','balconies',6)
    for side in (-1,1):face.part('balcony stone console',u+side*(width/2-.3),-.33,z-.30,.18,.58,.50,'stone','balconies',0)

def awning(face,length,idx,striped=False):
    outer=offset(PLAN,-2.1)
    a=Vector(face.o);ends=[(Vector((*outer[k],0))-a).dot(face.t) for k in (idx,(idx+1)%len(PLAN))]
    if idx==0:ends[0]=0
    if idx==4:ends[1]=length
    n=max(1,round(length/.35))
    for i in range(n):
        a=i*length/n;b=(i+1)*length/n;role='white' if striped and i%2 else 'trim'
        aa=ends[0]+(ends[1]-ends[0])*i/n;bb=ends[0]+(ends[1]-ends[0])*(i+1)/n
        C.solid_surface('continuous mitered cafe canvas',[face.p(a,0,3.64),face.p(b,0,3.64),face.p(bb,-2.1,3.10),face.p(aa,-2.1,3.10)],.035,role,'cafe awning')
        face.part('awning valance',(aa+bb)/2,-2.10,3.02,bb-aa,.045,.17,role,'cafe awning',0)
    for u in (.2,length-.2):C.beam('awning folding support',face.p(u,.06,2.45),face.p(u,-2.05,3.10),.027,.027,'hardware','cafe awning')

def roof_z(d):return 13.65+d*1.65 if d<=2.1 else 17.115+(d-2.1)*1.15

def dormer(face,u,d=.22,upper=False):
    w=1.25 if upper else 1.6;bottom=roof_z(d)+.06;h=1.4 if upper else 2.35;back=d+(h+.1)/(1.15 if upper else 1.65)
    # Lower dormer body cuts into its real sloped carrier and shares its roof datum.
    front=C.Face(face.p(u-w/2,d,0),face.t,face.n,face.label+' dormer')
    B.open_wall(front,w,bottom,bottom+h,[dict(id=face.label+f' dormer {u}',u=w/2,z=bottom+.18,w=w-.28,h=h-.35,cols=2)],role='roof',depth=.13)
    for side in (-1,1):
        x=u+side*w/2
        C.solid_surface('dormer closed cheek',[face.p(x,d,bottom),face.p(x,back,roof_z(back)-.10),face.p(x,back,bottom+h),face.p(x,d,bottom+h)],.08,'roof','dormers')
    profile=[(i*w/16,bottom+h+.20*math.sin(i*math.pi/16)) for i in range(17)]
    front.panel('segmental dormer crown',profile+[(w,bottom+h-.07),(0,bottom+h-.07)],d-.02-d,d+.13-d,'roof','dormers')
    for i in range(16):
        x0=u-w/2-.1+i*(w+.2)/16;x1=u-w/2-.1+(i+1)*(w+.2)/16
        z0=bottom+h+.22*math.sin(i*math.pi/16);z1=bottom+h+.22*math.sin((i+1)*math.pi/16)
        C.solid_surface('seated curved zinc dormer hood',[face.p(x0,d-.09,z0),face.p(x1,d-.09,z1),face.p(x1,back+.06,z1),face.p(x0,back+.06,z0)],.09,'roof','dormers')
    return (u-w/2-.015,u+w/2+.015,d-.01,back+.07)

def build():
    slab('ground foundation',PLAN,.20,.20,'foundation')
    for z in (3.9,7.1,10.3,13.5):slab('occupied storey floor',offset(PLAN,.3),z,.20,'floor')
    slab('upper attic floor inside mansard',offset(PLAN,2.08),16.9,.20,'floor')
    ring1=offset(PLAN,2.1);ring2=offset(PLAN,UPPER_RING_DEPTH)
    for idx,(a,b) in enumerate(zip(PLAN,PLAN[1:]+PLAN[:1])):
        vec=Vector((b[0]-a[0],b[1]-a[1],0));length=vec.length;t=vec.normalized();n=Vector((-t.y,t.x,0));face=C.Face((*a,0),t,n,f'face{idx}')
        print('BUILD_FACE',idx,flush=True)
        street=idx<5;bays=1 if idx==2 else max(1,round(length/(3.5 if street else 3.8)));centres=[(i+.5)*length/bays for i in range(bays)];holes=[]
        for i,u in enumerate(centres):
            holes.append(dict(id=f'ground {idx}-{i}',u=u,z=.2,w=min(2.7,length/bays-.55),h=3.2,cols=2,door=True))
            for j,z in enumerate((4.35,7.55,10.75)):holes.append(dict(id=f'upper {idx}-{i}-{j}',u=u,z=z,w=1.25,h=2.05,cols=2,frame='stone'))
        B.open_wall(face,length,.2,13.55,holes,role='wall' if street else 'stone',depth=.36)
        for z,h,depth in [(3.85,.24,.35),(7.1,.12,.20),(10.3,.12,.20),(13.45,.28,.40),(13.65,.12,.50)]:face.part('continuous stone string course',length/2,-.10,z,length,depth,h,'stone','facade detail',0)
        for u in (.26,length-.26):
            for j in range(20):face.part('alternating corner stone',u,-.055,4.15+j*.46,.58 if j%2 else .74,.15,.43,'stone','masonry',0)
        # Small mortar beds and perpend joints preserve ochre-brick scale.
        if street:
            for j in range(64):
                z=4.05+j*.14
                spans=[(0,length)]
                for h in holes:
                    if h['z']-.14<z<h['z']+h['h']+.14:
                        cuts=(h['u']-h['w']/2-.15,h['u']+h['w']/2+.15);spans=[seg for lo,hi in spans for seg in ((lo,min(hi,cuts[0])),(max(lo,cuts[1]),hi)) if seg[1]-seg[0]>.02]
                for lo,hi in spans:face.part('fine brick bed joint',(lo+hi)/2,-.007,z,hi-lo,.015,.008,'mortar','masonry',0)
        for i,u in enumerate(centres):
            for j,z in enumerate((4.35,7.55,10.75)):
                for side in (-1,1):face.part('window stone architrave',u+side*.73,-.06,z+1.05,.13,.20,2.25,'stone','window surround',0)
                face.part('window stone head',u,-.10,z+2.2,1.65,.27,.13,'stone','window surround',0)
                # Curtains and rooms are geometry behind the physical glazing.
                for side in (-1,1):face.part('interior curtain',u+side*.43,.62,z+.95,.28,.04,1.85,'interior','rooms',0)
                face.part('enclosed room back',u,4.1,z+1.0,2.7,.10,2.7,'interior','rooms',0)
                if street:
                    C.solid_surface('green window awning',[face.p(u-.73,-.04,z+2.12),face.p(u+.73,-.04,z+2.12),face.p(u+.73,-.65,z+1.91),face.p(u-.73,-.65,z+1.91)],.025,'trim','window awning')
                    if j==1:balcony(face,u,z-.12,3.35 if idx==2 else 2.65)
                    else:C.railing('window iron guard',face.p(u-.63,-.22,z+.02),face.p(u+.63,-.22,z+.02),.63,.14,'hardware')
                    face.part('window flower box',u,-.29,z+.16,.62,.22,.16,'wall','flower boxes',0)
                    for k in range(8):
                        x=u-.27+k*.077
                        C.rod('windowbox stem',face.p(x,-.28,z+.23),face.p(x,-.28,z+.40),.014,'leaf','flower boxes',5)
            if street and idx!=2:
                # Actual tables/chairs inside and beneath the continuous cafe canopy.
                for dd in (-1.0,2.0):
                    pos=face.p(u,dd,.2);B.table(*pos)
        if street:awning(face,length,idx,idx==2)
        if idx==2:B.label('CAFE L\u2019AMOUR',(0,-20.13,3.02),.28,'bronze')
        # Roof skin is clipped to mitered tier boundaries, with true dormer apertures.
        dormers=[]
        if street:
            for u in centres:
                def fits_at_depth(depth,halfwidth):
                    ring=offset(PLAN,depth)
                    ends=[(Vector((*ring[k],0))-Vector((*a,0))).dot(t) for k in (idx,(idx+1)%len(PLAN))]
                    return ends[0]+halfwidth+.12<u<ends[1]-halfwidth-.12
                if fits_at_depth(1.78,.80):dormers.append(dormer(face,u))
                if fits_at_depth(3.60,.625):dormers.append(dormer(face,u,2.20,True))
        cuts=sorted(set([-20,length+20,0,length,*[v for h in dormers for v in h[:2]],*[i*.6 for i in range(1,math.ceil(length/.6))]]))
        ds=sorted(set([0,2.1,UPPER_RING_DEPTH,*[v for h in dormers for v in h[2:]]]))
        def limits(d):
            ring=ring1 if d<=2.1 else ring2;frac=d/2.1 if d<=2.1 else (d-2.1)/(UPPER_RING_DEPTH-2.1)
            origin=PLAN if d<=2.1 else ring1
            pa=Vector(origin[idx]).lerp(Vector(ring[idx]),frac);pb=Vector(origin[(idx+1)%len(PLAN)]).lerp(Vector(ring[(idx+1)%len(PLAN)]),frac)
            return (Vector((pa.x-a[0],pa.y-a[1],0)).dot(t),Vector((pb.x-a[0],pb.y-a[1],0)).dot(t))
        for u,v in zip(cuts,cuts[1:]):
            for d,e in zip(ds,ds[1:]):
                if d<0 or e>UPPER_RING_DEPTH or any(lo<(u+v)/2<hi and dd<(d+e)/2<ee for lo,hi,dd,ee in dormers):continue
                l0,r0=limits(d);l1,r1=limits(e)
                poly=[(l0,d),(r0,d),(r1,e),(l1,e)]
                for bound,sgn in ((u,1),(v,-1)):
                    clipped=[]
                    for a0,b0 in zip(poly,poly[1:]+poly[:1]):
                        ina=sgn*(a0[0]-bound)>=0;inb=sgn*(b0[0]-bound)>=0
                        if ina:clipped.append(a0)
                        if ina!=inb:
                            frac=(bound-a0[0])/(b0[0]-a0[0]);clipped.append((bound,a0[1]+frac*(b0[1]-a0[1])))
                    poly=clipped
                if len(poly)<3:continue
                C.solid_surface('sealed mansard roof carrier',[face.p(uu,dd,roof_z(dd)) for uu,dd in poly],.12,'roof','mansard')
                if abs(u/.6-round(u/.6))<.01 and l0<=u<=r0 and l1<=u<=r1:C.beam('zinc standing seam',face.p(u,d,roof_z(d)+.025),face.p(u,e,roof_z(e)+.025),.018,.026,'roof','roof seam')
        if idx in (0,4):
            for u in [length*.22,length*.52,length*.83]:
                face.part('masonry chimney stack',u,3.3,18.8,.65,2.7,2.7,'wall','chimneys',0)
                face.part('chimney stone cap',u,3.3,20.18,.85,2.9,.15,'stone','chimneys',0)
                for j in range(6):C.rod('terracotta chimney pot',face.p(u,2.25+j*.42,20.18),face.p(u,2.25+j*.42,20.65),.09,'wall','chimneys',12)
    # Straight-skeleton faces own each planar pitch and its exact hip/valley.
    cap=json.loads((HERE/'cafe_roof.json').read_text())
    assert cap['plan']==[list(p) for p in PLAN] and cap['depth']==UPPER_RING_DEPTH
    assert max((Vector(a)-Vector(b)).length for a,b in zip(cap['ring'],ring2))<1e-5
    base=roof_z(UPPER_RING_DEPTH);slope=(20-base)/max(n[2] for n in cap['nodes'])
    for indices in cap['faces']:
        outline=[Vector((cap['nodes'][i][0],cap['nodes'][i][1],base+slope*cap['nodes'][i][2])) for i in indices[:-1]]
        origin=outline[0];t=(outline[1]-origin).normalized();n=Vector((-t.y,t.x,0))
        assert max(abs(p.z-(base+slope*(p-origin).dot(n))) for p in outline)<1e-5
        C.solid_surface('planar upper zinc roof pitch',[tuple(p) for p in outline],.10,'roof','roof')
        uv=[((p-origin).dot(t),(p-origin).dot(n)) for p in outline]
        for k in range(math.ceil(min(p[0] for p in uv)/.6),math.floor(max(p[0] for p in uv)/.6)+1):
            u=k*.6;cross=[]
            for a,b in zip(uv,uv[1:]+uv[:1]):
                if (a[0]<=u<b[0]) or (b[0]<=u<a[0]):cross.append(a[1]+(b[1]-a[1])*(u-a[0])/(b[0]-a[0]))
            cross.sort()
            for lo,hi in zip(cross[::2],cross[1::2]):
                if hi-lo<.02:continue
                points=[origin+t*u+n*d+Vector((0,0,slope*d+.018)) for d in (lo,hi)]
                C.beam('straight upper zinc standing seam',points[0],points[1],.016,.021,'roof','roof seam')
    # Courtyard remains an open void; circulation is conceptual, no occupied-building compliance claim.

def roster():
    target=(1,1,9);r=85
    views=[dict(name=n,location=p,target=target,ortho_scale=61) for n,p in [('front',(0,-r,10)),('left_side',(-r,0,10)),('right_side',(r,0,10)),('rear',(0,r,10))]]
    views += [dict(name='front_corner',location=(48,-65,29),target=target),dict(name='aerial',location=(45,-53,69),target=target),dict(name='top',location=(0,0,100),target=(0,.001,0),ortho_scale=62),dict(name='rear_side',location=(-44,62,33),target=target)]
    views += [dict(name=n,location=p,target=t,whole=False,lens=l) for n,p,t,l in [('facade_close',(8,-31,9),(0,-18,7),40),('architecture_close',(19,-28,23),(3,-16,16),40),('glass_close',(2,-23,2),(0,-16,2),38),('roof_contact',(10,-27,26),(0,-15,16),43),('courtyard',(0,25,9),(0,0,8),24),('walk',(4,-30,1.65),(0,-15,8),25)]]
    return views

def main():
    p=argparse.ArgumentParser();p.add_argument('--lock',type=Path,required=True);p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--dry-run',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    source=next(s for s in json.loads(a.lock.read_text())['entries'] if s['kind']=='cafe');entry=dict(archetype_id=source['archetype_id'],variant_id=source['variant_id'],directory='.',_reference_root=str(Path(source['sources'][0]['path']).parent),sources=[dict(s,original_path=s['path'],path='sources/'+Path(s['path']).name) for s in source['sources']]);views=roster()
    manifest=dict(candidate=f'neighbourhood-corner-cafe-clay-v{a.version:03d}',method=C.METHOD,archetype_id=entry['archetype_id'],variant_id=entry['variant_id'],representation_kind='architectural_clay',camera_roster=views,state='prework',keeper_claimed=False,runtime_seed_allowed=False,measurement_contract=dict(dimensions_m=dict(width=44,depth=44,height=20.65),floors=6,front='-Y',bottom_datum_m=0,measurement_basis='Exact reference proportions, inferred metric modules; not surveyed'),identity_contract=['V-shaped perimeter block and open rear courtyard','Ochre brick panels in cream stone courses','Wrapping green cafe canopy and striped corner canopy','Recessed windows, iron balconies, closed mansard with real dormers and multi-pot chimneys'],hidden_view_assumptions=['Unseen rear courtyard continues cream-stone window grammar','Concept interiors and floor slabs behind windows; apartment plans are inferred'],limitations=['Native fixed assembly; no mesh stretching','Architectural clay, not textured keeper','Runtime checks pending'])
    out=C.prepare_candidate(a,entry,manifest,__file__,[HERE.parent/'showcase_building_trio/build.py',HERE/'cafe_roof.json',HERE/'prepare_cafe_roof.py'])
    if out is None:return
    cams=C.setup(PALETTE,views,1440);C.fit=B.efficient_fit;C.bevel=local_bevel;C.bpy.context.scene.cycles.samples=20
    C.bpy.ops.object.light_add(type='SUN');sun=C.bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2.2;sun.data.angle=.14
    build();C.deliver(out,manifest,cams)
if __name__=='__main__':main()
