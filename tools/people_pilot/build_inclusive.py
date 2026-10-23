"""Finite inclusive fixed-pose architectural entourage. Blender5.2, external outputs.

Immutable existing CC0-derived human GLBs + original mobility equipment and a CC0 dog.
No runtime activation here. --only manual-wheelchair is the measured pilot.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
from mathutils import Vector,Matrix,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from inclusive_shapes import child_coordinate

ROOT=Path('C:/dev-artifacts/CityPrompt/people-inclusive-2026-10-23')
PUBLIC=Path('C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public')
EQUIPMENT=ROOT/'sources/kenney/Models/GLB format'
HUMAN_ROOT=None

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def visible_meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render]
def points(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    result=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear();return result
def bounds(objects):
    vs=[v for o in objects for v in points(o)]
    return Vector([min(v[i] for v in vs) for i in range(3)]),Vector([max(v[i] for v in vs) for i in range(3)])
def material(name,color,roughness=.7):
    def linear(v):return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4
    rgba=tuple(linear(int(color[i:i+2],16)/255) for i in (1,3,5))+(1,)
    m=bpy.data.materials.new(name);m.diffuse_color=rgba;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=rgba;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=roughness;return m
def box(name,location,size,mat,bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Soft manufactured edges','BEVEL');b.width=bevel;b.segments=2;o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL')
    return o
def tube(name,a,b,radius,mat,vertices=16):
    a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o
def sphere(name,location,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=location);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o
def wheel(name,x,y,radius,width,mat,rim,spokes=False):
    bpy.ops.mesh.primitive_torus_add(major_segments=40 if spokes else 24,minor_segments=10,major_radius=radius-width/2,minor_radius=width/2,location=(x,y,radius),rotation=(0,math.pi/2,0));o=bpy.context.object;o.name=name+'_tyre';o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    tube(name+'_hub',(x-.025,y,radius),(x+.025,y,radius),.026,rim)
    if spokes:
        for i in range(12):
            a=2*math.pi*i/12;tube(name+'_spoke_'+str(i),(x,y,radius),(x,y+math.sin(a)*(radius-.025),radius+math.cos(a)*(radius-.025)),.003,rim,8)
        bpy.ops.mesh.primitive_torus_add(major_segments=40,minor_segments=8,major_radius=radius-.045,minor_radius=.007,location=(x+math.copysign(.045,x),y,radius),rotation=(0,math.pi/2,0));push=bpy.context.object;push.name=name+'_pushrim';push.data.materials.append(rim)
    else:
        tube(name+'_wheel_centre',(x-width*.35,y,radius),(x+width*.35,y,radius),radius*.62,rim)
def chair_geometry(power=False):
    before=set(bpy.context.scene.objects);metal=material('Chair satin aluminium','#aeb7bd',.36);rubber=material('Chair rubber tyres','#242a30',.9);fabric=material('Chair upholstered graphite','#343d46',.93);accent=material('Chair frame teal','#2b6971',.5)
    box('Upholstered seat',(0,0,.465),(.43,.43,.05),fabric,.018)
    box('Upholstered backrest',(0,.22,.70),(.43,.045,.43),fabric,.02)
    for x in [-.22,.22]:
        tube('Back upright',(x,.235,.42),(x,.235,.94),.014,metal);tube('Push handle',(x,.235,.93),(x,.33,.93),.02,rubber)
        tube('Seat rail',(x,-.22,.44),(x,.22,.44),.014,accent)
    if not power:
        for x in [-.32,.32]:wheel('Manual rear',x,.12,.30,.052,rubber,metal,True)
        for x in [-.24,.24]:
            wheel('Manual caster',x,-.39,.075,.03,rubber,metal)
            tube('Caster fork',(x,-.39,.075),(x,-.39,.25),.012,metal)
            tube('Front frame',(math.copysign(.22,x),-.20,.44),(x,-.39,.17),.014,accent)
        tube('Cross brace',(-.22,.10,.31),(.22,-.15,.44),.011,metal);tube('Cross brace',(.22,.10,.31),(-.22,-.15,.44),.011,metal)
    else:
        box('Battery and motor housing',(0,.02,.26),(.45,.52,.20),accent,.045)
        for x in [-.28,.28]:wheel('Powered drive',x,.02,.18,.065,rubber,metal)
        for x in [-.22,.22]:
            for y in [-.31,.32]:wheel('Powered caster',x,y,.075,.032,rubber,metal)
            tube('Armrest support',(x,.14,.47),(x,.14,.68),.013,metal)
            box('Padded armrest',(x,-.015,.68),(.065,.33,.045),fabric,.018)
        box('Right control pod',(-.25,-.19,.695),(.09,.13,.035),rubber,.016);tube('Joystick',(-.25,-.205,.71),(-.25,-.205,.735),.009,metal);sphere('Joystick cap',(-.25,-.205,.735),(.018,.018,.012),rubber)
    for x in [-.16,.16]:
        tube('Footplate hanger',(x,-.20,.43),(x,-.44,.065),.012,metal)
        box('Footplate',(x,-.46,.037),(.19,.27,.025),fabric,.012)
    return [o for o in bpy.context.scene.objects if o not in before]
def freeze(objects,prefix):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();out=[]
    for o in objects:
        if o.type!='MESH' or o.hide_render:continue
        mesh=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);mesh.transform(o.matrix_world)
        baked=bpy.data.objects.new(prefix+'_'+o.name,mesh);bpy.context.collection.objects.link(baked);out.append(baked)
    return out
def remove(objects):
    for o in list(objects):
        if o.name in bpy.data.objects:bpy.data.objects.remove(o,do_unlink=True)
def load_person(source_id,placement=(0,0,0),scale=1):
    folder='people-pilot-v1' if source_id.startswith('people-pilot') else 'people-community-v1'
    path=PUBLIC/'street-kits'/folder/(source_id+'.glb')
    if HUMAN_ROOT:
        source=json.loads((HUMAN_ROOT/'source-map.json').read_text())[source_id]
        path=Path(source['path']);assert digest(path)==source['sha256'],'Clothed source hash changed'
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path));objects=[o for o in bpy.context.scene.objects if o not in before]
    rig=next(o for o in objects if o.type=='ARMATURE')
    idle=next(strip.action for track in rig.animation_data.nla_tracks for strip in track.strips if strip.action and strip.action.name.split('.')[0]=='Idle')
    for t in rig.animation_data.nla_tracks:t.mute=True
    rig.animation_data.action=idle;rig.animation_data.action_slot=idle.slots[0]
    for o in objects:
        if o.parent is None and o.type!='MESH':o.location+=Vector(placement);o.scale*=scale
    bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
    # Blender creates a display-only Icosphere for imported bone custom shapes;
    # it is not in the source GLB scene and must never become model geometry.
    bone_shapes={bone.custom_shape for bone in rig.pose.bones if bone.custom_shape}
    return {'rig':rig,'objects':objects,'meshes':[o for o in objects if o.type=='MESH' and not o.hide_render and o not in bone_shapes],'source':str(path),'sha256':digest(path)}
def joint(person,name):return person['rig'].matrix_world@person['rig'].pose.bones[name].head
def aim(person,name,end,target):
    rig=person['rig'];bone=rig.pose.bones[name];a=joint(person,name);b=joint(person,end);target=Vector(target)
    delta=(b-a).normalized().rotation_difference((target-a).normalized())
    transform=Matrix.Translation(a)@delta.to_matrix().to_4x4()@Matrix.Translation(-a)
    bone.matrix=rig.matrix_world.inverted()@transform@rig.matrix_world@bone.matrix;bpy.context.view_layer.update()
def pose_arm(person,side,elbow,hand):
    shoulder=joint(person,'upperarm_'+side);current_elbow=joint(person,'lowerarm_'+side);current_hand=joint(person,'hand_'+side)
    upper=(current_elbow-shoulder).length;lower=(current_hand-current_elbow).length;target=Vector(hand);axis=target-shoulder
    distance=max(abs(upper-lower)+.001,min(axis.length,upper+lower-.001));axis.normalize();target=shoulder+axis*distance
    bend=Vector(elbow)-shoulder;bend-=axis*bend.dot(axis)
    if bend.length<1e-5:bend=Vector((1,0,0))
    bend.normalize();along=(upper*upper-lower*lower+distance*distance)/(2*distance)
    wanted=shoulder+axis*along+bend*math.sqrt(max(0,upper*upper-along*along))
    aim(person,'upperarm_'+side,'lowerarm_'+side,wanted);aim(person,'lowerarm_'+side,'hand_'+side,target)
def palm(person,side):
    bone=person['rig'].pose.bones['hand_'+side];return person['rig'].matrix_world@((bone.head+bone.tail)/2)
def pose_palm(person,side,elbow,target):
    # Aim the hand's centre, not its wrist, at a real equipment contact.
    rig=person['rig'];bone=rig.pose.bones['hand_'+side]
    hand_rotation=(rig.matrix_world@bone.matrix).to_quaternion()
    target=Vector(target);wrist=target-(palm(person,side)-joint(person,'hand_'+side))
    for _ in range(8):
        pose_arm(person,side,elbow,wrist)
        world=rig.matrix_world@bone.matrix
        bone.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(world.translation,hand_rotation,world.to_scale())
        bpy.context.view_layer.update()
        error=target-palm(person,side)
        if error.length<.001:break
        wrist+=error
    gap=(target-palm(person,side)).length
    assert gap<.006,(side,'unreachable palm contact',gap,list(target),list(palm(person,side)))
    return gap

def seated(person,footplate=.0495):
    rig=person['rig'];contacts={};rotations={};offsets={}
    for side in ['l','r']:
        shoe=next(o for o in person['meshes'] if o.name.split('.')[0]=='Low_top_sneaker_'+side)
        offsets[side]=joint(person,'foot_'+side).z-min(v.z for v in points(shoe))
        rotations[side]=(rig.matrix_world@rig.pose.bones['foot_'+side].matrix).to_quaternion()
    # Translate the imported complete body, not its skeleton alone.
    top=rig
    while top.parent:top=top.parent
    top.location.z+=.54-joint(person,'pelvis').z;bpy.context.view_layer.update()
    for side in ['l','r']:
        hip=joint(person,'thigh_'+side);knee=joint(person,'calf_'+side);foot=joint(person,'foot_'+side)
        lower=(foot-knee).length;ankle_z=footplate+offsets[side]
        target=Vector((hip.x,-.40,ankle_z));upper=(knee-hip).length
        shoe=next(o for o in person['meshes'] if o.name.split('.')[0]=='Low_top_sneaker_'+side)
        # Measure evaluated shoe vertices after each fit; parent nonuniform scale
        # can otherwise leave a gap despite an analytically correct ankle.
        for iteration in range(5):
            axis=target-hip;distance=axis.length;axis.normalize()
            assert abs(upper-lower)<distance<upper+lower
            pole=Vector((0,-1,0));pole-=axis*pole.dot(axis);pole.normalize()
            along=(upper*upper-lower*lower+distance*distance)/(2*distance)
            wanted=hip+axis*along+pole*math.sqrt(max(0,upper*upper-along*along))
            aim(person,'thigh_'+side,'calf_'+side,wanted)
            aim(person,'calf_'+side,'foot_'+side,target)
            foot_bone=rig.pose.bones['foot_'+side];world=rig.matrix_world@foot_bone.matrix
            foot_bone.matrix=rig.matrix_world.inverted()@Matrix.LocRotScale(world.translation,rotations[side],world.to_scale());bpy.context.view_layer.update()
            gap=min(v.z for v in points(shoe))-footplate
            if abs(gap)<.0005:break
            target.z-=gap
        sole=min(v.z for v in points(shoe));contacts['shoe_'+side]=sole
        assert abs(sole-footplate)<.001,(side,'footplate air gap',sole-footplate)
        contacts['footplateTop']=footplate
        contacts['ankle_'+side]=list(joint(person,'foot_'+side))
    return contacts
def equipment(name,scale=(1,1,1),yaw=math.pi,location=(0,0,0)):
    before=set(bpy.context.scene.objects);path=EQUIPMENT/(name+'.glb');bpy.ops.import_scene.gltf(filepath=str(path));objs=[o for o in bpy.context.scene.objects if o not in before]
    parent=bpy.data.objects.new('Derived_'+name,None);bpy.context.collection.objects.link(parent)
    for o in objs:
        if o.parent is None:o.parent=parent
    parent.scale=scale;parent.rotation_euler.z=yaw;parent.location=location;bpy.context.view_layer.update()
    return objs+[parent],{'path':str(path),'sha256':digest(path),'scale':scale,'yaw':yaw,'location':location}
def render(root,name,objects,view='front'):
    low,high=bounds(objects);center=(low+high)/2;size=max(high.x-low.x,high.y-low.y,high.z-low.z)
    floor_mat=material('QA_floor','#c6cfcb');bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005));floor=bpy.context.object;floor.name='QA_floor';floor.data.materials.append(floor_mat)
    bpy.ops.object.camera_add(location=center+Vector((3.6,-6,2.4)));camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=size*1.35
    scene=bpy.context.scene;scene.camera=camera
    for loc,power in [((3,-4,5),700),((-3,-2,4),450),((0,4,4),550)]:
        bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=4;light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
    if scene.world is None:scene.world=bpy.data.worlds.new('QA_world')
    scene.world.color=(.3,.3,.3);scene.render.engine='CYCLES';scene.render.threads_mode='FIXED';scene.render.threads=8;scene.cycles.samples=24;scene.render.resolution_x=640;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.filepath=str(root/'qa'/(name+'.png'));bpy.ops.render.render(write_still=True)
def export_model(name,objects,sources,contacts):
    for o in bpy.context.scene.objects:o.select_set(False)
    for o in objects:o.select_set(True)
    low,high=bounds(objects);assert abs(low.z)<.012,(name,'bad datum',low[:]);assert high.z<2.2
    path=ROOT/'runtime'/(name+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_animations=False,export_skins=False,export_materials='EXPORT',export_extras=True,export_apply=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'editable'/(name+'.blend')))
    meshes=sum(len(o.data.polygons) for o in objects);triangles=sum(sum(max(1,len(p.vertices)-2) for p in o.data.polygons) for o in objects)
    report={'id':name,'sha256':digest(path),'bytes':path.stat().st_size,'boundsXYZBlender':{'min':list(low),'max':list(high)},'dimensions':[high.x-low.x,high.y-low.y,high.z-low.z],'triangles':triangles,'meshFaces':meshes,'objects':len(objects),'sourceInputs':sources,'contacts':contacts,'staticPose':True,'unit':'metre','up':'+Y glTF','forward':'+Z glTF','groundDatum':0}
    (ROOT/'measurements'/(name+'.json')).write_text(json.dumps(report,indent=2));render(ROOT,name,objects);print('ASSET_PASS',name,report['bytes'],triangles,list(high-low),contacts,flush=True)
def build_manual():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=24
    person=load_person('people-pilot-commuter');contacts=seated(person)
    for side,x in [('l',.32),('r',-.32)]:pose_arm(person,side,(x,.05,.90),(x,-.02,.64))
    chair=chair_geometry()
    baked=freeze(person['meshes']+[o for o in chair if o.type=='MESH'],'manual');remove(person['objects']+chair)
    export_model('people-inclusive-manual-wheelchair',baked,[{'path':person['source'],'sha256':person['sha256']},{'author':'CityPrompt','component':'Original detailed fixed manual wheelchair; tubes, pushrims, spokes, casters, upholstered seat and footplates','referenceOnly':'Kenney CC0 equipment inspected but its block geometry rejected, not included in this derivative'}],contacts)
def person_source(person):return {'path':person['source'],'sha256':person['sha256']}
def finish_person_role(role,people,extras,sources,contacts):
    baked=freeze([mesh for p in people for mesh in p['meshes']]+[o for o in extras if o.type=='MESH'],role)
    remove([o for p in people for o in p['objects']]+extras)
    export_model('people-inclusive-'+role,baked,[person_source(p) for p in people]+sources,contacts)
def build_power():
    person=load_person('people-community-andre');contacts=seated(person,.0495)
    for side,x in [('l',.25),('r',-.25)]:pose_arm(person,side,(x,.06,.9),(x,-.20,.74))
    # The source ring collar stretches into tabs in the seated pose. Replace
    # only that garment detail with two small authored folded polo leaves.
    person['meshes']=[o for o in person['meshes'] if 'collar' not in o.name.lower()]
    chair=chair_geometry(True)
    neck=joint(person,'neck_01');collar_mat=material('Plum polo folded collar','#724154')
    for sign in [-1,1]:
        vertices=[neck+Vector((sign*x,y,z)) for x,y,z in [(.012,-.075,.015),(.072,-.070,-.010),(.040,-.105,-.050),(.014,-.105,-.025)]]
        mesh=bpy.data.meshes.new('Polo collar leaf');mesh.from_pydata(vertices,[],[(0,1,2,3)]);obj=bpy.data.objects.new('Folded short polo collar',mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(collar_mat);obj.modifiers.new('Fabric thickness','SOLIDIFY').thickness=.002;chair.append(obj)
    contacts['right_palm']=list(palm(person,'r'))
    finish_person_role('power-wheelchair',[person],chair,[{'author':'CityPrompt','component':'Original powered wheelchair frame, battery, six wheels, armrests and joystick'}],contacts)
def recolor(person,find,value):
    for obj in person['meshes']:
        for index,mat in enumerate(obj.data.materials):
            if mat and find.lower() in mat.name.lower():obj.data.materials[index]=material('Inclusive_'+find,value)
def cane_geometry(grip):
    before=set(bpy.context.scene.objects);white=material('White cane reflective shaft','#f0f0e7');red=material('White cane red tip','#b9252a');black=material('White cane handgrip','#292d31')
    grip=Vector(grip);tip=Vector((grip.x+.055,grip.y-.58,.012));length=(grip-tip).length;direction=(grip-tip).normalized()
    tube('White cane red lower section',tip,tip+direction*.19,.009,red);tube('White cane white shaft',tip+direction*.19,grip-direction*.06,.007,white);tube('Black cane grip',grip-direction*.06,grip+direction*.035,.014,black);sphere('Rolling cane tip',tip,(.014,.014,.012),white)
    return [o for o in bpy.context.scene.objects if o not in before],{'caneTip':list(tip),'grip':list(grip),'lengthMetres':length}
def build_cane():
    person=load_person('people-community-ava');pose_arm(person,'r',(-.28,-.02,1.08),(-.24,-.15,.96))
    extra,contacts=cane_geometry(palm(person,'r'));finish_person_role('white-cane',[person],extra,[{'author':'CityPrompt','component':'White long cane, reflective shaft, red lower section, black grip and rolling tip'}],contacts)
def build_senior():
    person=load_person('people-community-clara');recolor(person,'hair','#bab4a9');recolor(person,'jacket','#718d79');recolor(person,'shirt','#e7dfcf');
    finish_person_role('older-woman',[person],[],[{'author':'CityPrompt','component':'Grey hair and softened sage/taupe wardrobe on existing licensed adult base; stylized age cues'}],{})
def rollator_geometry(grips):
    before=set(bpy.context.scene.objects);frame=material('Rollator burgundy frame','#75383e',.5);metal=material('Rollator aluminium','#adb8bd',.4);rubber=material('Rollator rubber','#272d33');fabric=material('Rollator bag','#3c454a')
    for x in [-.27,.27]:
        for y in [-.43,.08]:wheel('Rollator',x,y,.075,.034,rubber,metal)
        tube('Rollator front upright',(x,-.43,.075),(x,.035,1.065),.014,frame);tube('Rollator rear leg',(x,.08,.075),(x,-.13,.65),.014,frame)
        tube('Rollator handgrip',(x,-.04,1.065),(x,.12,1.065),.018,rubber);tube('Rollator brake',(x-.025,-.035,.96),(x-.025,.07,.96),.007,metal)
    box('Rollator sitting shelf',(0,-.23,.55),(.45,.28,.04),fabric,.018);box('Rollator shopping bag',(0,-.25,.37),(.40,.25,.28),fabric,.035)
    tube('Rollator front crossbar',(-.27,-.25,.67),(.27,-.25,.67),.013,frame)
    return [o for o in bpy.context.scene.objects if o not in before]
def build_rollator():
    person=load_person('people-pilot-neighbour',(0,.20,0));recolor(person,'hair','#bcb7ae');recolor(person,'jacket','#526b84')
    for side,x in [('l',.27),('r',-.27)]:pose_palm(person,side,(x,.11,1.13),(x,.045,1.065))
    grips={side:list(palm(person,side)) for side in ['l','r']};extra=rollator_geometry(grips)
    finish_person_role('older-man-rollator',[person],extra,[{'author':'CityPrompt','component':'Original four-wheel rollator, grips, brakes, shelf and bag; silver hair'}],{'palms':grips,'gripDatum':1.065})
def child_head_masks(person):
    masks=[]
    for obj in person['meshes']:
        head_groups={g.index for g in obj.vertex_groups if 'head' in g.name.lower()}
        masks.append({v.index for v in obj.data.vertices if sum(g.weight for g in v.groups if g.group in head_groups)>.5})
    return masks

def child_shape(objects,offset,head_masks):
    low,high=bounds(objects)
    for obj,head in zip(objects,head_masks):
        for v in obj.data.vertices:v.co=child_coordinate(v.co,offset,is_head=v.index in head,datum=low.z)
    return {'bodyFactor':.60,'headFactor':1.02,'headWidthFactor':.96,'headSelection':'source Head skin weights > .5; raised hand excluded','sourceHeight':high.z-low.z,'resultHeight':bounds(objects)[1].z-bounds(objects)[0].z}

def build_family():
    parent=load_person('people-community-imani',(-.32,0,0));pose_arm(parent,'l',(-.05,.02,1.13),(.065,-.025,.84))
    child=load_person('people-community-leo');pose_palm(child,'r',(-.32,-.02,1.50),(-.35,-.035,palm(parent,'l').z/.60))
    recolor(child,'skin','#a56c4c');recolor(child,'hair','#30241f')
    head_masks=child_head_masks(child)
    parent_baked=freeze(parent['meshes'],'parent');child_baked=freeze(child['meshes'],'child');shape=child_shape(child_baked,(.37,0,0),head_masks)
    # Match the held-hand positions after nonuniform child-specific proportions.
    pp=palm(parent,'l');cp=palm(child,'r');cp=Vector(child_coordinate(cp,(.37,0,0)))
    correction=Vector((pp.x-cp.x,pp.y-cp.y,0))
    for obj in child_baked:
        for v in obj.data.vertices:v.co+=correction
    contacts={'parentPalm':list(pp),'childPalmAfterShape':[cp.x+correction.x,cp.y+correction.y,cp.z],'handGapMetres':abs(pp.z-cp.z),'childProportions':shape}
    assert contacts['handGapMetres']<.006,contacts
    remove(parent['objects']+child['objects']);export_model('people-inclusive-family-parent-child',parent_baked+child_baked,[person_source(parent),person_source(child),{'author':'CityPrompt','component':'Child-specific shorter torso/legs and relatively larger head/face; held-hand pose, fixed two-person group'}],contacts)
def stroller_geometry():
    before=set(bpy.context.scene.objects);frame=material('Stroller champagne frame','#99988a',.45);rubber=material('Stroller rubber','#292e33');fabric=material('Stroller navy fabric','#3b5264');trim=material('Stroller lining','#d6c9b4');skin=material('Infant warm skin','#bc8c6b');blanket=material('Infant cream blanket','#e4dac0')
    for x in [-.23,.23]:
        wheel('Stroller rear',x,.25,.11,.04,rubber,frame);wheel('Stroller front',x,-.40,.085,.035,rubber,frame)
        tube('Stroller side frame',(x,-.40,.085),(x,.30,1.10),.014,frame);tube('Stroller rear frame',(x,.25,.11),(x,-.20,.59),.014,frame)
    tube('Stroller pushbar',(-.23,.30,1.10),(.23,.30,1.10),.022,rubber)
    box('Stroller seat',(0,-.11,.47),(.36,.53,.055),fabric,.035);back=box('Stroller backrest',(0,.12,.65),(.36,.055,.36),fabric,.025);back.rotation_euler.x=-.20
    box('Stroller basket',(0,-.08,.26),(.37,.42,.13),fabric,.025)
    # Open-front curved canopy; infant remains visible through the opening.
    verts=[];faces=[]
    for y in [.03,.27]:
        for i in range(17):
            a=math.pi*i/16;verts.append((.23*math.cos(a),y,.76+.23*math.sin(a)))
    for i in range(16):faces.append((i,i+1,i+18,i+17))
    mesh=bpy.data.meshes.new('Curved stroller canopy');mesh.from_pydata(verts,[],faces);obj=bpy.data.objects.new('Open front stroller canopy',mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(fabric);obj.modifiers.new('Canopy fabric thickness','SOLIDIFY').thickness=.005
    sphere('Infant head',(0,.035,.735),(.080,.074,.085),skin);sphere('Infant swaddled body',(0,-.10,.58),(.11,.18,.085),blanket)
    sphere('Infant nose',(0,-.040,.745),(.012,.015,.012),skin)
    for x in [-.026,.026]:sphere('Infant closed eye',(x,-.035,.755),(.009,.005,.0035),rubber)
    sphere('Infant cap',(0,.045,.785),(.081,.074,.043),trim)
    return [o for o in bpy.context.scene.objects if o not in before]
def build_stroller():
    person=load_person('people-community-noah',(0,.50,0))
    for side,x in [('l',.19),('r',-.19)]:pose_palm(person,side,(x,.38,1.22),(x,.30,1.10))
    contacts={'palms':{s:list(palm(person,s)) for s in ['l','r']},'pushbarHeight':1.10,'personCount':2,'infantPose':'seated/swaddled in stroller'}
    extra=stroller_geometry();finish_person_role('family-stroller',[person],extra,[{'author':'CityPrompt','component':'Original stroller frame, four wheels, fabric canopy/basket and stylized swaddled infant'}],contacts)
def build_guide():
    person=load_person('people-community-mateo');pose_arm(person,'l',(.31,.01,1.12),(.31,-.05,.97));grip=palm(person,'l')
    dog_file=ROOT/'sources/dog/Animal Pack Vol.2 by @Quaternius/OBJ/Dog.obj';before=set(bpy.context.scene.objects);bpy.ops.wm.obj_import(filepath=str(dog_file));dog=[o for o in bpy.context.scene.objects if o not in before and o.type=='MESH']
    low,high=bounds(dog)
    if (high-low).x>(high-low).y:
        for o in dog:o.rotation_euler.z+=math.pi/2
    bpy.context.view_layer.update();low,high=bounds(dog);scale=.69/(high.z-low.z)
    baked=freeze(dog,'guide_dog');remove(dog)
    for o in baked:
        for v in o.data.vertices:v.co=(v.co-Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z)))*scale
    # The high ear/head region identifies the head end of this fixed source pose.
    heads=[v.co for o in baked for v in o.data.vertices if v.co.z>.54];flip=sum(v.y for v in heads)/len(heads)>0
    for o in baked:
        for v in o.data.vertices:
            if flip:v.co.x=-v.co.x;v.co.y=-v.co.y
            v.co+=Vector((.57,-.17,0))
    fur=material('Guide dog golden coat','#ba8848',.95)
    for o in baked:
        o.data.materials.clear();o.data.materials.append(fur)
    black=material('Guide dog harness webbing','#2c333b');metal=material('Guide dog harness handle','#aeb6b5',.4)
    extra_start=set(bpy.context.scene.objects)
    sphere('Guide dog dark nose',(.5675,-.738,.601),(.019,.012,.012),black)
    for x in [.513,.622]:sphere('Guide dog eye',(x,-.631,.608),(.008,.009,.008),black)
    box('Guide harness back strap',(.57,-.17,.455),(.26,.055,.035),black,.012)
    for x in [.45,.69]:tube('Guide harness side strap',(x,-.17,.45),(x,-.22,.27),.012,black)
    tube('Guide harness chest strap',(.45,-.30,.31),(.69,-.30,.31),.013,black)
    for x in [.46,.68]:tube('Rigid guide handle',(x,-.17,.475),grip,.009,metal)
    sphere('Guide handle grip',grip,(.032,.020,.020),black)
    harness=[o for o in bpy.context.scene.objects if o not in extra_start]
    person_baked=freeze(person['meshes'],'handler');harness_baked=freeze(harness,'harness');remove(person['objects']+harness)
    export_model('people-inclusive-guide-dog',person_baked+baked+harness_baked,[person_source(person),{'path':str(dog_file),'sha256':digest(dog_file),'author':'Quaternius CC0','sourceArchiveSha256':'6d8f6789d65dbdb352ebad98a4209f26b41b384e87d81bc05e9ca76139db1248'},{'author':'CityPrompt','component':'Fitted guide harness, rigid handle and coordinated handler grip'}],{'handleGrip':list(grip),'dogHeight':.69,'dogHeadFlippedToForward':flip})
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only',default='manual-wheelchair');parser.add_argument('--person-root',type=Path);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    HUMAN_ROOT=args.person_root
    for name in ['runtime','qa','editable','measurements']:(ROOT/name).mkdir(parents=True,exist_ok=True)
    builders={'manual-wheelchair':build_manual,'power-wheelchair':build_power,'white-cane':build_cane,'guide-dog':build_guide,'older-woman':build_senior,'older-man-rollator':build_rollator,'family-parent-child':build_family,'family-stroller':build_stroller}
    roles=list(builders) if args.only=='all' else [args.only]
    for role in roles:
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=24
        builders[role]()
