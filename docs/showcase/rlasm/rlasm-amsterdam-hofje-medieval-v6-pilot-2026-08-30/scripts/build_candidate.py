from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
RENDERS = ROOT / "renders"
MODEL = ROOT / "model"
MATS = ROOT / "references" / "materials"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        pass


def image_material(name, filename, roughness=0.72, metallic=0.0, scale=(3.0, 3.0, 3.0), value=1.0, saturation=1.0, bump_strength=0.17, bump_distance=0.055):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(MATS / filename), check_existing=True)
    # Generated 3D coordinates must be box projected. Flat projection reads X/Y
    # only and collapses a vertical wall's shallow axis into false timber stripes.
    tex.projection = 'BOX'
    tex.projection_blend = 0.18
    coord = nodes.new("ShaderNodeTexCoord")
    # All segmented carriers share one world-space registration origin. This
    # prevents every bay from restarting the photographed bond/tile phase.
    origin = bpy.data.objects.get("RLASM_MaterialRegistrationOrigin")
    if origin is None:
        origin = bpy.data.objects.new("RLASM_MaterialRegistrationOrigin", None)
        bpy.context.collection.objects.link(origin)
        origin.empty_display_type = 'PLAIN_AXES'
    coord.object = origin
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (*scale,)
    # Object coordinates remain in metres after transform application, giving
    # one physical bond/tile scale across every separately segmented carrier.
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    grade = nodes.new("ShaderNodeHueSaturation")
    grade.inputs["Value"].default_value = value
    grade.inputs["Saturation"].default_value = saturation
    links.new(tex.outputs["Color"], grade.inputs["Color"])
    links.new(grade.outputs["Color"], bsdf.inputs["Base Color"])
    # The same exact-source sheet supplies restrained micro-relief. Geometry
    # still owns courses, profiles, openings and contacts; this is finish only.
    bump_tex = nodes.new("ShaderNodeTexImage")
    bump_tex.image = tex.image
    bump_tex.projection = 'BOX'
    bump_tex.projection_blend = 0.18
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = bump_distance
    links.new(mapping.outputs["Vector"], bump_tex.inputs["Vector"])
    links.new(bump_tex.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def simple_material(name, color, roughness=0.65, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = 0.7
    return mat


def glass_material():
    mat = image_material("MAT_Hofje_LowIronResidentialGlass", "hofje-medieval-residential-glass-tint-v1.png", 0.18, 0.0, (1.1, 1.1, 1.1), 1.0, 1.0, 0.02, 0.008)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Transmission Weight"].default_value = 0.92
    bsdf.inputs["Coat Weight"].default_value = 0.38
    bsdf.inputs["Roughness"].default_value = 0.08
    bsdf.inputs["IOR"].default_value = 1.46
    bsdf.inputs["Alpha"].default_value = 0.24
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = 'DITHERED'
    nodes=mat.node_tree.nodes; links=mat.node_tree.links
    out=nodes.get("Material Output") or next(n for n in nodes if n.bl_idname=="ShaderNodeOutputMaterial")
    for link in list(out.inputs["Surface"].links): links.remove(link)
    transparent=nodes.new("ShaderNodeBsdfTransparent")
    mix=nodes.new("ShaderNodeMixShader"); mix.inputs[0].default_value=0.18
    links.new(bsdf.outputs["BSDF"],mix.inputs[1]); links.new(transparent.outputs["BSDF"],mix.inputs[2]); links.new(mix.outputs["Shader"],out.inputs["Surface"])
    return mat


def cube(name, location, scale, material, bevel=0.0, collection=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("ConstructionEdge", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    if collection:
        for c in list(obj.users_collection): c.objects.unlink(obj)
        collection.objects.link(obj)
    return obj


def cylinder(name, location, radius, depth, material, vertices=24, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bev = obj.modifiers.new("SoftEdge", "BEVEL")
    bev.width = min(0.05, radius * 0.15)
    bev.segments = 2
    return obj


def tapered_pot(name, location, radius_bottom, radius_top, depth, material, vertices=24):
    """Source-brick chimney pot with a visible taper instead of a generic rod."""
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius_bottom, radius2=radius_top, depth=depth, location=location)
    obj=bpy.context.object; obj.name=name; obj.data.materials.append(material)
    rim=cylinder(name+"_rim",(location[0],location[1],location[2]+depth/2-0.04),radius_top+0.035,0.08,material,vertices)
    return obj


def flower_cluster(name, x, y, stone, center_material):
    """Physical white flower cluster sampled from the locked court palette."""
    cylinder(name+"_center",(x,y,0.75),0.09,0.12,center_material,16)
    for i in range(6):
        a=2*math.pi*i/6
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=0.13,location=(x+math.cos(a)*0.16,y+math.sin(a)*0.16,0.78))
        petal=bpy.context.object; petal.name=name+f"_petal{i}"; petal.scale=(1.0,0.62,0.34); petal.rotation_euler[2]=a; petal.data.materials.append(stone); petal.visible_shadow=False


def planting_mound(name, x, y, foliage, blossom):
    """Open, irregular perennial shrub using only the locked court palette."""
    foliage_parts=((-0.30,0.00,0.19),(0.08,0.10,0.22),(0.29,-0.10,0.17),(-0.03,-0.22,0.20),(-0.13,0.21,0.17),(0.17,0.28,0.15),(-0.25,-0.20,0.15),(0.02,0.31,0.16))
    for i,(dx,dy,sc) in enumerate(foliage_parts):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=sc,location=(x+dx,y+dy,0.27+sc*0.62+0.038*(i%4)))
        obj=bpy.context.object; obj.name=f"{name}_foliage{i}"; obj.scale=(1.35+0.12*(i%3),0.72+0.09*((i+1)%3),0.68+0.07*(i%4)); obj.rotation_euler[2]=(i-5.5)*0.27; obj.data.materials.append(foliage); obj.visible_shadow=False
    blossom_parts=((-0.27,0.02),(0.01,0.15),(0.22,-0.09),(-0.08,-0.18),(0.13,0.29),(-0.18,0.22),(0.31,0.13),(-0.29,-0.17),(0.02,0.32),(0.18,-0.25))
    for i,(dx,dy) in enumerate(blossom_parts):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=0.025+0.005*(i%3),location=(x+dx,y+dy,0.53+0.055*(i%4)))
        obj=bpy.context.object; obj.name=f"{name}_blossom{i}"; obj.data.materials.append(blossom); obj.visible_shadow=False


def polygon_prism(name, points, z, depth, material, bevel=0.0):
    """Horizontal physical prism used for clipped court beds and route slabs."""
    n = len(points)
    verts = [(x, y, z-depth/2) for x, y in points] + [(x, y, z+depth/2) for x, y in points]
    faces = [tuple(range(n-1, -1, -1)), tuple(range(n, 2*n))]
    for i in range(n):
        j = (i+1) % n
        faces.append((i, j, n+j, n+i))
    mesh = bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(verts, [], faces); mesh.update()
    obj = bpy.data.objects.new(name, mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("ClippedSoftEdge", "BEVEL"); mod.width=bevel; mod.segments=3
    return obj


def hedge_border(name, points, z, height, width, material):
    """Separate clipped hedge owner around a planted polygon; never a slab."""
    for i, (a, b) in enumerate(zip(points, points[1:] + points[:1])):
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx, dy)
        if length < 0.08:
            continue
        obj = cube(f"{name}_edge{i}",((a[0]+b[0])/2,(a[1]+b[1])/2,z),(length,width,height),material,0.10)
        obj.rotation_euler[2] = math.atan2(dy, dx)
        top = cube(f"{name}_continuousTop{i}",((a[0]+b[0])/2,(a[1]+b[1])/2,z+height*0.44),(length+0.08,width*0.82,height*0.20),material,0.12)
        top.rotation_euler[2] = math.atan2(dy, dx)
        # The exact source is clipped box, not a bead chain. One merged crown
        # per edge keeps a living softened arris without visible repeat pieces.
        merged = cube(f"{name}_mergedCrown{i}",((a[0]+b[0])/2,(a[1]+b[1])/2,z+height*0.43),(length+0.10,width*0.88,height*0.21),material,0.085)
        merged.rotation_euler[2] = math.atan2(dy, dx)
        merged.visible_shadow=False
    for i,(x,y) in enumerate(points):
        cube(f"{name}_joint{i}",(x,y,z),(width,width,height),material,0.10)


def vertical_prism_y(name, points_xz, y, depth, material, bevel=0.0):
    """Facade-profile carrier extruded in Y; useful for pediments and shoulders."""
    n = len(points_xz)
    verts = [(x, y-depth/2, z) for x, z in points_xz] + [(x, y+depth/2, z) for x, z in points_xz]
    faces = [tuple(range(n-1, -1, -1)), tuple(range(n, 2*n))]
    for i in range(n):
        j=(i+1)%n; faces.append((i,j,n+j,n+i))
    mesh=bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(material)
    if bevel:
        mod=obj.modifiers.new("ProfileSoftEdge","BEVEL"); mod.width=bevel; mod.segments=3
    return obj


def profile_curve(name, points, material, bevel=0.10):
    curve=bpy.data.curves.new(name+"Curve",'CURVE'); curve.dimensions='3D'; curve.bevel_depth=bevel; curve.bevel_resolution=4
    spline=curve.splines.new('BEZIER'); spline.bezier_points.add(len(points)-1)
    for bp,co in zip(spline.bezier_points,points):
        bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(obj); obj.data.materials.append(material)
    return obj


def barrel_hood(name, location, width, depth, rise, rotation_z, material):
    """Continuous faceted rolled-lead shell, extruded across the dormer."""
    section=[]
    steps=12
    for i in range(steps+1):
        t=i/steps; y=-depth/2+t*depth; z=rise*math.sin(math.pi*t)
        section.append((y,z))
    section += [(depth/2,-0.10),(-depth/2,-0.10)]
    n=len(section); verts=[]
    for sx in (-width/2,width/2):
        for y,z in section:
            x=sx; xr=x*math.cos(rotation_z)-y*math.sin(rotation_z); yr=x*math.sin(rotation_z)+y*math.cos(rotation_z)
            verts.append((location[0]+xr,location[1]+yr,location[2]+z))
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n; faces.append((i,j,n+j,n+i))
    mesh=bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(material)
    mod=obj.modifiers.new("RolledLeadEdge","BEVEL"); mod.width=0.025; mod.segments=3
    return obj


def gable_roof(name, center, length, depth, eave_z, ridge_z, axis, material):
    if axis == "X":
        verts = [(-length/2,-depth/2,eave_z),(-length/2,0,ridge_z),(-length/2,depth/2,eave_z),
                 ( length/2,-depth/2,eave_z),( length/2,0,ridge_z),( length/2,depth/2,eave_z)]
        faces = [(0,3,4,1),(1,4,5,2)]
    else:
        verts = [(-depth/2,-length/2,eave_z),(0,-length/2,ridge_z),(depth/2,-length/2,eave_z),
                 (-depth/2, length/2,eave_z),(0, length/2,ridge_z),(depth/2, length/2,eave_z)]
        # The raised pavilion gable owns both roof ends. A closed triangular
        # roof face here would sit in front of it and visually recreate the
        # generic A-gable rejected by the source-locked review.
        faces = [(0,1,4,3),(1,2,5,4)]
    verts = [(x+center[0],y+center[1],z) for x,y,z in verts]
    mesh = bpy.data.meshes.new(name+"Mesh")
    mesh.from_pydata(verts, [], faces); mesh.update()
    obj = bpy.data.objects.new(name, mesh); bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    solid = obj.modifiers.new("PhysicalRoofThickness", "SOLIDIFY")
    solid.thickness = 0.18
    solid.offset = 0.0
    bev = obj.modifiers.new("PantileEaveSoftness", "BEVEL"); bev.width=0.07; bev.segments=2
    return obj


def roof_patch(name, corners, material):
    mesh=bpy.data.meshes.new(name+"Mesh")
    mesh.from_pydata(corners,[],[(0,1,2,3)]); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(material)
    solid=obj.modifiers.new("PhysicalRoofThickness","SOLIDIFY"); solid.thickness=0.18; solid.offset=0.0
    return obj


def gable_roof_with_court_cuts(name, center, length, depth, eave_z, ridge_z, axis, material, cut_centers, court_side=-1):
    """Segment a roof field around bounded dormer holes without booleans."""
    cx,cy=center
    half_l,half_d=length/2,depth/2
    if axis == "X":
        x_min,x_max=cx-half_l,cx+half_l
        y_eave=cy-half_d if court_side < 0 else cy+half_d
        y_ridge=cy
        def z_at_y(y): return eave_z+(ridge_z-eave_z)*(abs(y-y_eave)/half_d)
        direction=1 if court_side < 0 else -1
        a=y_eave+direction*0.52; b=y_eave+direction*1.30
        # continuous apron/eave band and upslope field bound every opening
        roof_patch(name+"_CourtApron",[(x_min,y_eave,eave_z),(x_max,y_eave,eave_z),(x_max,a,z_at_y(a)),(x_min,a,z_at_y(a))],material)
        intervals=[]; cursor=x_min
        for c in sorted(cut_centers):
            left,right=c-0.45,c+0.45
            if left>cursor: intervals.append((cursor,left))
            cursor=max(cursor,right)
        if cursor<x_max: intervals.append((cursor,x_max))
        for i,(x0,x1) in enumerate(intervals):
            roof_patch(f"{name}_CourtBetween{i}",[(x0,a,z_at_y(a)),(x1,a,z_at_y(a)),(x1,b,z_at_y(b)),(x0,b,z_at_y(b))],material)
        roof_patch(name+"_CourtUpslope",[(x_min,b,z_at_y(b)),(x_max,b,z_at_y(b)),(x_max,y_ridge,ridge_z),(x_min,y_ridge,ridge_z)],material)
        y_far=cy+half_d if court_side < 0 else cy-half_d
        roof_patch(name+"_FarSlope",[(x_min,y_ridge,ridge_z),(x_max,y_ridge,ridge_z),(x_max,y_far,eave_z),(x_min,y_far,eave_z)],material)
    else:
        y_min,y_max=cy-half_l,cy+half_l
        x_eave=cx-half_d if court_side < 0 else cx+half_d
        x_ridge=cx
        def z_at_x(x): return eave_z+(ridge_z-eave_z)*(abs(x-x_eave)/half_d)
        direction=1 if court_side < 0 else -1
        a=x_eave+direction*0.52; b=x_eave+direction*1.30
        roof_patch(name+"_CourtApron",[(x_eave,y_min,eave_z),(a,y_min,z_at_x(a)),(a,y_max,z_at_x(a)),(x_eave,y_max,eave_z)],material)
        intervals=[]; cursor=y_min
        for c in sorted(cut_centers):
            left,right=c-0.45,c+0.45
            if left>cursor: intervals.append((cursor,left))
            cursor=max(cursor,right)
        if cursor<y_max: intervals.append((cursor,y_max))
        for i,(y0,y1) in enumerate(intervals):
            roof_patch(f"{name}_CourtBetween{i}",[(a,y0,z_at_x(a)),(b,y0,z_at_x(b)),(b,y1,z_at_x(b)),(a,y1,z_at_x(a))],material)
        roof_patch(name+"_CourtUpslope",[(b,y_min,z_at_x(b)),(x_ridge,y_min,ridge_z),(x_ridge,y_max,ridge_z),(b,y_max,z_at_x(b))],material)
        x_far=cx+half_d if court_side < 0 else cx-half_d
        roof_patch(name+"_FarSlope",[(x_ridge,y_min,ridge_z),(x_far,y_min,eave_z),(x_far,y_max,eave_z),(x_ridge,y_max,ridge_z)],material)
    return None


def cut_roof(roof_obj, name, location, scale, rotation_z=0.0):
    """Apply an auditable full-depth dormer cut through a thick roof field."""
    bpy.context.view_layer.objects.active = roof_obj
    roof_obj.select_set(True)
    for mod in list(roof_obj.modifiers):
        if mod.type == 'SOLIDIFY':
            bpy.ops.object.modifier_apply(modifier=mod.name)
        elif mod.type == 'BEVEL':
            roof_obj.modifiers.remove(mod)
    roof_obj.select_set(False)
    cutter = cube(name+"_PhysicalVoid", location, scale, None, 0.0)
    cutter.rotation_euler[2] = rotation_z
    bpy.context.view_layer.objects.active = roof_obj
    roof_obj.select_set(True)
    cutter.select_set(False)
    boolean = roof_obj.modifiers.new(name+"_FullDepthCut", "BOOLEAN")
    boolean.operation = 'DIFFERENCE'
    boolean.solver = 'FAST'
    boolean.object = cutter
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    finish = roof_obj.modifiers.new("PantileCutEdgeSoftness", "BEVEL")
    finish.width = 0.035
    finish.segments = 2
    roof_obj.select_set(False)
    bpy.data.objects.remove(cutter, do_unlink=True)


def gable_infill(name, plane, cross_center, span, eave_z, ridge_z, axis, material, thickness=0.44):
    """Physical brick gable prism; roof fields never masquerade as end walls."""
    t = thickness / 2
    if axis == "X":
        verts = [(plane-t,cross_center-span/2,eave_z),(plane-t,cross_center,ridge_z),(plane-t,cross_center+span/2,eave_z),
                 (plane+t,cross_center-span/2,eave_z),(plane+t,cross_center,ridge_z),(plane+t,cross_center+span/2,eave_z)]
    else:
        verts = [(cross_center-span/2,plane-t,eave_z),(cross_center,plane-t,ridge_z),(cross_center+span/2,plane-t,eave_z),
                 (cross_center-span/2,plane+t,eave_z),(cross_center,plane+t,ridge_z),(cross_center+span/2,plane+t,eave_z)]
    faces = [(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(0,2,5,3)]
    mesh = bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(verts, [], faces); mesh.update()
    obj = bpy.data.objects.new(name, mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(material)
    return obj


def arch_ring(name, center, width, spring_z, depth, material, segments=28):
    r = width / 2
    for i in range(segments):
        a0 = math.pi * i / segments
        a1 = math.pi * (i + 1) / segments
        a = (a0+a1)/2
        x = center[0] + math.cos(a) * r
        z = spring_z + math.sin(a) * r
        seg_len = r * (a1-a0) * 1.18
        obj = cube(f"{name}_voussoir_{i:02d}",(x,center[1],z),(seg_len,depth,0.34),material,0.025)
        obj.rotation_euler[1] = a - math.pi/2
    cube(name+"_left_pier",(center[0]-r+0.17,center[1],spring_z/2),(0.55,depth,spring_z),material,0.04)
    cube(name+"_right_pier",(center[0]+r-0.17,center[1],spring_z/2),(0.55,depth,spring_z),material,0.04)


def opening_assembly(name, u, plane, z, w, h, axis, normal, wall_thickness, mats, door=False, occupied="living", make_room=True):
    brick, stone, timber, glass, room, curtain = mats
    reveal_d = wall_thickness * 0.82
    if axis == "X":
        # wall runs X at Y=plane
        def box(n, uu, nn, zz, su, sn, sz, mat, bev=0): return cube(n,(uu,plane+nn*normal,zz),(su,sn,sz),mat,bev)
    else:
        def box(n, uu, nn, zz, su, sn, sz, mat, bev=0): return cube(n,(plane+nn*normal,uu,zz),(sn,su,sz),mat,bev)
    # returns live wholly inside the opening and span the cut carrier thickness
    t = 0.12
    box(name+"_jambL",u-w/2+t/2,-wall_thickness*0.08,z,t,reveal_d,h,brick,0.018)
    box(name+"_jambR",u+w/2-t/2,-wall_thickness*0.08,z,t,reveal_d,h,brick,0.018)
    box(name+"_head",u,-wall_thickness*0.08,z+h/2-t/2,w-2*t,reveal_d,t,stone,0.018)
    box(name+"_sill",u,-wall_thickness*0.08,z-h/2+t/2,w-2*t,reveal_d,t,stone,0.018)
    frame_n = -wall_thickness*0.33
    fw = 0.018
    box(name+"_frameL",u-w/2+0.18,frame_n,z,fw,0.065,h-0.22,timber,0.010)
    box(name+"_frameR",u+w/2-0.18,frame_n,z,fw,0.065,h-0.22,timber,0.010)
    box(name+"_frameTop",u,frame_n,z+h/2-0.14,w-0.28,0.065,fw,timber,0.010)
    box(name+"_frameBottom",u,frame_n,z-h/2+0.14,w-0.28,0.065,fw,timber,0.010)
    if door:
        box(name+"_doorLeaf",u,frame_n-0.03,z,w-0.32,0.075,h-0.26,timber,0.020)
        for pz in (-0.52,0.05):
            box(name+f"_doorPanel{pz}",u,frame_n-0.075,z+pz,w-0.58,0.035,0.40,timber,0.010)
            box(name+f"_doorPanelRail{pz}",u,frame_n-0.095,z+pz,w-0.44,0.025,0.035,stone,0.006)
        box(name+"_doorHandle",u+w*0.24,frame_n-0.105,z+0.02,0.045,0.035,0.12,stone,0.006)
        box(name+"_doorOverlightPane",u,frame_n-0.07,z+h/2-0.40,w-0.50,0.025,0.34,glass,0)
        box(name+"_doorOverlightRail",u,frame_n-0.01,z+h/2-0.58,w-0.42,0.055,0.045,timber,0.008)
        box(name+"_threshold",u,-wall_thickness*0.44,z-h/2+0.045,w-0.18,0.24,0.09,stone,0.012)
        for hz in (z-0.62,z+0.30): box(name+f"_hinge{hz}",u-w/2+0.21,frame_n-0.115,hz,0.035,0.026,0.15,stone,0.004)
    else:
        # Source windows read as tall Dutch timber assemblies, but the attic,
        # court and service elevations keep their distinct pane schedules.
        if "AtticWindow" in name:
            mullions=(u,); rails=(z-h/5,z+h/5)
        elif any(tag in name for tag in ("RearExterior","EastStreet","WestExterior","WestSouthEnd")):
            mullions=(u,); rails=(z-h/4,z+h/4)
        else:
            mullions=(u-w/6,u+w/6); rails=(z-h/4,z,z+h/4)
        for mi, mu in enumerate(mullions):
            box(name+f"_mullion{mi}",mu,frame_n-0.01,z,fw*0.60,0.052,h-0.26,timber,0.006)
        for ri, rz in enumerate(rails):
            box(name+f"_meetingRail{ri}",u,frame_n-0.01,rz,w-0.28,0.052,fw*0.60,timber,0.006)
        box(name+"_pane",u,frame_n-0.105,z,w-0.30,0.025,h-0.30,glass,0.0)
        # The pane is never backed by a flat opaque curtain. Narrow side
        # curtains, furniture and the farther room enclosure create visible
        # parallax and occupied depth through every representative opening.
        if make_room:
            room_n = -wall_thickness*0.5-1.05
            for side in (-1,1):
                box(name+f"_curtain{side}",u+side*(w/2-0.16),room_n+0.30,z,0.12,0.035,h-0.42,curtain,0.01)
            box(name+"_occupiedTable",u,room_n,z-h*0.27,w*0.54,0.44,0.09,timber,0.02)
            box(name+"_occupiedChair",u-w*0.22,room_n-0.30,z-h*0.12,0.16,0.18,h*0.28,timber,0.015)
            for side in (-1,1): box(name+f"_occupiedShelfSide{side}",u+side*w*0.28,room_n-0.42,z,0.045,0.12,h*0.54,timber,0.006)
            for si,sz in enumerate((z-h*0.19,z,z+h*0.19)):
                box(name+f"_occupiedShelf{si}",u,room_n-0.42,sz,w*0.60,0.12,0.045,timber,0.006)
            # The back wall is more than two metres behind the pane. The floor,
            # back wall and visible furniture prove occupied depth; projecting
            # perpendicular room-side planes are excluded because at corner
            # bays they can pierce an adjacent exterior opening.
            room_depth = 2.25
            room_center = -wall_thickness/2-room_depth/2
            box(name+"_roomBack",u,-wall_thickness/2-room_depth,z,w+1.05,0.08,h+0.55,room,0)
            box(name+"_roomFloor",u,room_center,z-h/2-0.16,w+1.05,room_depth,0.10,room,0)


def facade(name, plane, start, length, axis, normal, bays, doors, wall_h, wall_thickness, mats, passage_bays=None, shared_room_bays=None):
    brick = mats[0]
    passage_bays = set(passage_bays or ())
    shared_room_bays = set(shared_room_bays or ())
    bay = length / bays
    open_w = min(1.78, bay * 0.56)
    for i in range(bays):
        u0 = start + i*bay
        u = u0 + bay/2
        # masonry carrier is segmented around each opening, never a full wall behind glass
        this_open_w = bay*0.78 if i in passage_bays else open_w
        pier = (bay-this_open_w)/2
        def wall_box(suffix, uu, z, su, sz):
            if axis=="X": cube(f"{name}_{i}_{suffix}",(uu,plane,z),(su,wall_thickness,sz),brick,0.0)
            else: cube(f"{name}_{i}_{suffix}",(plane,uu,z),(wall_thickness,su,sz),brick,0.0)
        wall_box("pierL",u0+pier/2,wall_h/2,pier,wall_h)
        wall_box("pierR",u0+bay-pier/2,wall_h/2,pier,wall_h)
        is_door = i in doors
        if i in passage_bays:
            ground_z, ground_h = 1.50, 2.90
        elif is_door:
            ground_z, ground_h = 1.45, 2.70
            wall_box("doorHead",u,3.00,this_open_w,0.30)
        else:
            ground_z, ground_h = 1.72, 2.38
            wall_box("groundSill",u,0.27,this_open_w,0.54)
            wall_box("groundHead",u,3.02,this_open_w,0.22)
        wall_box("floorBand",u,3.15,this_open_w,0.55)
        wall_box("upperSill",u,3.48,this_open_w,0.18)
        wall_box("upperHead",u,6.02,this_open_w,0.30)
        wall_box("eaveBand",u,6.30,this_open_w,0.25)
        if i not in passage_bays:
            opening_assembly(f"{name}_ground_{i}",u,plane,ground_z,1.15 if is_door else open_w,ground_h,axis,normal,wall_thickness,mats,door=is_door,make_room=i not in shared_room_bays)
        opening_assembly(f"{name}_upper_{i}",u,plane,4.76,open_w,2.26,axis,normal,wall_thickness,mats,door=False,occupied="bedroom",make_room=True)


def pavilion_gabled_facade(plane, normal, mats):
    """Source-specific south pavilion carrier: gate + sash + one upper bay."""
    brick=mats[0]
    thickness=0.44
    def wall(name, x, z, width, height):
        cube(name,(x,plane,z),(width,thickness,height),brick,0.0)

    # Ground carrier is physically segmented around the left gate passage and
    # the right communal-room sash. No continuous wall exists behind either.
    wall("PavilionGabledGroundFarLeft",9.84,1.58,0.28,3.16)
    wall("PavilionGabledGroundMiddle",13.03,1.58,1.90,3.16)
    wall("PavilionGabledGroundFarRight",16.75,1.58,1.90,3.16)
    wall("PavilionGabledWindowSill",14.90,0.27,1.82,0.54)
    wall("PavilionGabledWindowHead",14.90,3.01,1.82,0.24)
    wall("PavilionGabledFloorBand",13.70,3.24,8.00,0.42)

    # One broad, vertically dominant upper sash matches the locked pavilion
    # hierarchy; flanking masonry carries the raised gable above.
    wall("PavilionGabledUpperLeft",11.20,4.84,3.00,2.80)
    wall("PavilionGabledUpperRight",16.20,4.84,3.00,2.80)
    wall("PavilionGabledUpperSill",13.70,3.50,2.00,0.20)
    wall("PavilionGabledUpperHead",13.70,6.16,2.00,0.34)
    wall("PavilionGabledEaveBand",13.70,6.36,8.00,0.18)
    opening_assembly("PavilionGabledGroundSash",14.90,plane,1.72,1.82,2.38,"X",normal,thickness,mats,door=False,make_room=False)
    opening_assembly("PavilionGabledUpperSash",13.70,plane,4.78,2.00,2.32,"X",normal,thickness,mats,door=False,occupied="bedroom",make_room=True)


def dormer(name, location, rotation_z, mats, lead, roof_material, shadow_room, pale_sash):
    """Small glazed lead dormer seated through an already-cut roof field."""
    brick, stone, timber, glass, room, curtain = mats

    def local_box(suffix, offset, scale, material, bevel=0.0):
        x=offset[0]*math.cos(rotation_z)-offset[1]*math.sin(rotation_z)
        y=offset[0]*math.sin(rotation_z)+offset[1]*math.cos(rotation_z)
        obj=cube(name+suffix,(location[0]+x,location[1]+y,location[2]+offset[2]),scale,material,bevel)
        obj.rotation_euler[2]=rotation_z
        return obj

    def local_roof_box(suffix, offset, scale, material, bevel=0.0):
        """Seat a thin flashing plate on the 39-degree roof plane."""
        roof_slope = 0.82
        x=offset[0]*math.cos(rotation_z)-offset[1]*math.sin(rotation_z)
        y=offset[0]*math.sin(rotation_z)+offset[1]*math.cos(rotation_z)
        z=offset[2] + roof_slope*offset[1]
        obj=cube(name+suffix,(location[0]+x,location[1]+y,location[2]+z),scale,material,bevel)
        obj.rotation_euler[0]=math.atan(roof_slope)
        obj.rotation_euler[2]=rotation_z
        return obj

    # The physical void is visible between cheek returns; no brick plate may
    # sit behind the sash. Furniture and a warm enclosure are farther upslope.
    local_box("_wellLeft",(-0.36,0.00,-0.22),(0.034,0.50,0.98),lead,0.005)
    local_box("_wellRight",(0.36,0.00,-0.22),(0.034,0.50,0.98),lead,0.005)
    local_box("_wellFloor",(0,-0.01,-0.66),(0.76,0.52,0.032),lead,0.005)
    local_box("_wellCeiling",(0,-0.01,0.27),(0.76,0.52,0.032),lead,0.005)
    # Opaque lead-wrapped cheeks close the full side depth. They prevent the
    # warm occupied back wall from reading as a false orange hood end.
    local_box("_leftLeadCheek",(-0.37,-0.01,-0.15),(0.070,0.52,0.90),lead,0.006)
    local_box("_rightLeadCheek",(0.37,-0.01,-0.15),(0.070,0.52,0.90),lead,0.006)
    local_box("_frontSill",(0,-0.31,-0.42),(0.76,0.050,0.038),lead,0.008)
    local_box("_frontHead",(0,-0.31,0.27),(0.76,0.050,0.030),lead,0.008)
    local_box("_frontJambL",(-0.33,-0.34,-0.06),(0.026,0.055,0.61),lead,0.006)
    local_box("_frontJambR",(0.33,-0.34,-0.06),(0.026,0.055,0.61),lead,0.006)
    local_box("_pane",(0,-0.40,-0.04),(0.66,0.018,0.60),glass,0)
    local_box("_mullion",(0,-0.47,-0.01),(0.012,0.024,0.64),pale_sash,0.002)
    for rz in (-0.16,0.16): local_box(f"_rail{rz}",(0,-0.47,rz),(0.68,0.024,0.011),pale_sash,0.002)
    # Pixel-ray diagnosis proved the sloped undertray was visible through the
    # high sightline. A close vertical shadow-room wall now intercepts that ray
    # before the roof plane, while desk and book remain separately offset.
    local_box("_occupiedBack",(0,0.18,-0.05),(0.70,0.045,0.76),shadow_room,0)
    local_box("_occupiedDesk",(0,0.02,-0.24),(0.54,0.24,0.06),stone,0.012)
    local_box("_occupiedBook",(-0.14,-0.01,-0.11),(0.10,0.07,0.20),timber,0.004)
    # One continuous rolled-lead hood is physically seated on both cheeks.
    # A full sloped lead undertray overlaps the bounded cut on all four sides;
    # no orange cut edge may read as a separate tab beside the cheeks.
    local_roof_box("_continuousLeadUndertray",(0,0.0,0.052),(0.94,0.90,0.032),lead,0.006)
    barrel_hood(name+"_rolledLeadHood",(location[0],location[1],location[2]+0.30),0.76,0.48,0.12,rotation_z,lead)
    # Continuous weathering chain lies on and overlaps the roof plane, closing
    # every edge of the bounded cut: rear saddle, side soakers and front apron.
    # Nothing sits below the covering where it could expose a raw void.
    local_roof_box("_rearHeadSaddle",(0,0.37,0.050),(0.88,0.14,0.032),lead,0.005)
    local_roof_box("_leftThroatClosure",(-0.39,0.0,0.050),(0.13,0.82,0.032),lead,0.005)
    local_roof_box("_rightThroatClosure",(0.39,0.0,0.050),(0.13,0.82,0.032),lead,0.005)
    local_roof_box("_apronFlashing",(0,-0.38,0.055),(0.88,0.15,0.032),lead,0.005)
    for side in (-1,1):
        for si,yy in enumerate((-0.32,-0.06,0.20,0.46)):
            local_roof_box(f"_stepFlashing{side}_{si}",(side*0.39,yy,0.072),(0.11,0.20,0.024),lead,0.004)


def build():
    print("RLASM_STAGE build_start", flush=True)
    clear_scene(); RENDERS.mkdir(exist_ok=True); MODEL.mkdir(exist_ok=True)
    brick=image_material("MAT_Hofje_AgedStretcherBrick","hofje-medieval-aged-stretcher-brick-albedo-v1.png",0.86,0,(0.54,0.54,0.54),1.00,0.88,0.19,0.034)
    roof=image_material("MAT_Hofje_WeatheredPantile","hofje-medieval-weathered-pantile-albedo-v1.png",0.84,0,(0.28,0.28,0.28),1.08,0.88,0.15,0.022)
    stone=image_material("MAT_Hofje_AgedPaleStone","hofje-medieval-pale-stone-trim-albedo-v1.png",0.88,0,(1.35,1.35,1.35),0.60,0.30,0.10,0.018)
    lead=image_material("MAT_Hofje_AgedLeadDormers","hofje-medieval-aged-lead-albedo-v1.png",0.82,0.02,(1.25,1.25,1.25),0.72,0.15,0.07,0.012)
    dormer_sash=image_material("MAT_Hofje_PalePaintedDormerSash","hofje-medieval-pale-painted-dormer-sash-v1.png",0.76,0,(1.4,1.4,1.4),0.92,0.18,0.03,0.006)
    timber=image_material("MAT_Hofje_DeepGreenTimber","hofje-medieval-deep-green-painted-timber-albedo-v1.png",0.70,0,(1,1,1),1.62,0.78,0.06,0.010)
    iron=image_material("MAT_Hofje_WroughtIron","hofje-medieval-wrought-iron-albedo-v1.png",0.42,0.62,(1,1,1))
    glass=glass_material(); lawn=image_material("MAT_Hofje_Lawn","hofje-medieval-courtyard-lawn-albedo-v1.png",0.94,0,(0.46,0.46,0.46),1.12,0.96,0.16,0.026)
    hedge=image_material("MAT_Hofje_Hedge","hofje-medieval-clipped-hedge-albedo-v1.png",0.86,0,(0.82,0.82,0.82),1.04,0.96,0.13,0.020)
    flowers=image_material("MAT_Hofje_CourtyardFlowers","hofje-medieval-courtyard-flower-albedo-v1.png",0.78,0,(2.4,2.4,2.4),1.32,0.26,0.06,0.010)
    gravel=image_material("MAT_Hofje_Gravel","hofje-medieval-courtyard-gravel-albedo-v1.png",0.92,0,(0.62,0.62,0.62),1.02,0.76,0.24,0.032)
    # Interior roles stay inside the same exact-source palette; no generic
    # plaster, timber or linen fallback enters the forward test.
    room=image_material("MAT_Hofje_OccupiedRoom","hofje-medieval-warm-interior-plaster-albedo-v1.png",0.84,0,(0.85,0.85,0.85),1.24,0.68)
    curtain=image_material("MAT_Hofje_SourceLinen","hofje-medieval-pale-stone-trim-albedo-v1.png",0.92,0,(1.8,1.8,1.8))
    interior=image_material("MAT_Hofje_SourceConditionedInteriorPlaster","hofje-medieval-warm-interior-plaster-albedo-v1.png",0.88,0,(0.72,0.72,0.72),0.86,0.56)
    dormer_room=image_material("MAT_Hofje_DormerShadowRoom","hofje-medieval-warm-interior-plaster-albedo-v1.png",0.92,0,(0.95,0.95,0.95),0.48,0.45,0.03,0.006)
    wood=image_material("MAT_Hofje_SourceTimberInterior","hofje-medieval-deep-green-painted-timber-albedo-v1.png",0.70,0,(0.8,0.8,0.8))
    mats=(brick,stone,timber,glass,room,curtain)

    # grade, street, courtyard and floor slabs
    cube("Grade",(0,0,-0.25),(46,42,0.5),gravel,0.08)
    cube("CourtyardPaving",(0,-1.5,0.015),(21.0,20.5,0.06),gravel,0.02)
    # complete wing floors and ceilings, but no opaque cores behind windows
    for nm,loc,sc in [("RearFloor",(0,11.6,0.12),(34,6.8,0.24)),("EastFloor",(13.5,-1.6,0.12),(7,23.2,0.24)),("WestFloor",(-13.7,1.5,0.12),(6.6,20.2,0.24))]: cube(nm,loc,sc,interior,0.02)
    for z in (3.15,6.2):
        cube(f"RearSlab{z}",(0,11.6,z),(33.2,6.0,0.18),wood,0.02)
        cube(f"EastSlab{z}",(13.5,-1.6,z),(6.2,22.4,0.18),wood,0.02)
        cube(f"WestSlab{z}",(-13.7,1.5,z),(5.8,19.4,0.18),wood,0.02)

    # all exposed elevations carry the same audited schedule, with quieter rear cadence
    facade("RearCourt",8.2,-16.8,33.6,"X",-1,8,{1,5},6.45,0.44,mats,shared_room_bays={2,3})
    facade("RearExterior",15.0,-16.8,33.6,"X",1,7,{3},6.45,0.44,mats)
    # The north wing begins at the pavilion return. v008 incorrectly ran both
    # carriers through each other, exposing a raw slit and blocking the gate.
    facade("EastCourt",10.0,-7.25,15.45,"Y",-1,5,{1,3},6.45,0.44,mats)
    facade("EastStreet",17.0,-7.25,21.75,"Y",1,6,{1,4},6.45,0.44,mats)
    facade("WestCourt",-10.4,-8.4,16.4,"Y",1,5,{1,3},6.45,0.44,mats)
    facade("WestExterior",-17.0,-8.4,23.0,"Y",-1,5,{2},6.45,0.44,mats)
    # South ends are inhabited elevations, not blank closure slabs.
    facade("WestSouthEnd",-8.6,-17.0,6.6,"X",-1,2,{1},6.45,0.44,mats)
    print("RLASM_STAGE facades_complete", flush=True)

    # connected roof fields and bounded junction flashings
    gable_roof_with_court_cuts("RearPantileRoof",(0,11.6),34.4,7.8,6.42,9.62,"X",roof,(-7.5,0.0,7.5),-1)
    gable_roof_with_court_cuts("EastPantileRoof",(13.5,-1.8),22.9,8.0,6.42,9.62,"Y",roof,(-2.0,),-1)
    gable_roof_with_court_cuts("WestPantileRoof",(-13.7,1.2),20.0,7.6,6.42,9.42,"Y",roof,(1.5,),1)
    gable_infill("RearWestGable",-17.18,11.6,7.75,6.42,9.62,"X",brick)
    gable_infill("RearEastGable",17.18,11.6,7.75,6.42,9.62,"X",brick)
    gable_infill("EastNorthGable",9.62,13.5,7.95,6.42,9.62,"Y",brick)
    gable_infill("WestNorthGable",11.18,-13.7,7.55,6.42,9.42,"Y",brick)
    gable_infill("WestSouthGable",-8.78,-13.7,7.55,6.42,9.42,"Y",brick)
    cube("NEValleyFlashing",(12.6,8.55,7.25),(1.0,1.5,0.12),stone,0.04).rotation_euler[2]=math.radians(45)
    cube("NWValleyFlashing",(-12.8,8.55,7.20),(1.0,1.5,0.12),stone,0.04).rotation_euler[2]=math.radians(-45)
    # ridge/eave ownership
    cube("RearRidgeCap",(0,11.6,9.66),(34.5,0.26,0.25),roof,0.08)
    cube("EastRidgeCap",(13.5,-1.8,9.66),(0.26,22.9,0.25),roof,0.08)
    cube("WestRidgeCap",(-13.7,1.2,9.46),(0.26,20.0,0.25),roof,0.08)
    for y in (7.75,15.45): cube(f"RearGutter{y}",(0,y,6.30),(34.5,0.20,0.22),iron,0.05)
    for x in (9.55,17.45): cube(f"EastGutter{x}",(x,-1.8,6.30),(0.20,23.0,0.22),iron,0.05)
    for x in (-17.55,-9.85): cube(f"WestGutter{x}",(x,1.2,6.30),(0.20,20.0,0.22),iron,0.05)
    print("RLASM_STAGE wing_roofs_complete", flush=True)

    # Street pavilion is independently load-bearing and is the source's dominant
    # tall south gable. Its four faces are segmented around real apertures.
    cube("PavilionGroundSlab",(13.7,-11.1,0.12),(7.8,7.4,0.24),interior,0.02)
    cube("PavilionUpperSlab",(13.7,-11.1,3.15),(7.8,7.4,0.18),wood,0.02)
    # Bay 0 is one continuous street-to-court barrel passage. The remaining
    # ground bays share the communal room instead of receiving box rooms.
    pavilion_gabled_facade(-15.0,-1,mats)
    facade("PavilionCourt",-7.25,9.7,8.0,"X",1,3,{1},6.45,0.44,mats,passage_bays={0},shared_room_bays={1,2})
    facade("PavilionStreet",17.55,-15.0,7.75,"Y",1,2,{1},6.45,0.44,mats,shared_room_bays={0,1})
    # Complete the west eave carrier at the pavilion/wing junction. Its two
    # source-family door bays open to the passage/communal room; no grey void.
    facade("PavilionWestJunction",9.70,-15.0,7.75,"Y",-1,2,{0,1},6.45,0.44,mats,shared_room_bays={0,1})
    # The roof ridge stays behind and below the source-defining raised gable.
    pavilion_roof=gable_roof("PavilionCrossRoof",(13.7,-11.1),8.0,8.0,6.45,10.52,"Y",roof)
    # The source gable is the street-side hierarchy: a taller, slightly tighter
    # shoulder silhouette rises clear of the cross roof into a narrow neck and
    # compact classical cap. The profile is physical wall geometry throughout.
    left_profile=[(11.34,6.45),(12.98,6.45),(12.98,11.72),(12.66,11.72),(12.66,9.54),(12.37,9.54),(12.37,9.08),(11.98,9.08),(11.98,8.76),(11.58,8.76),(11.58,8.52),(11.34,8.52)]
    right_profile=[(14.42,6.45),(16.06,6.45),(16.06,8.52),(15.82,8.52),(15.82,8.76),(15.42,8.76),(15.42,9.08),(15.03,9.08),(15.03,9.54),(14.74,9.54),(14.74,11.72),(14.42,11.72)]
    vertical_prism_y("PavilionDutchShoulderL",left_profile,-15.24,0.48,brick,0.0)
    vertical_prism_y("PavilionDutchShoulderR",right_profile,-15.24,0.48,brick,0.0)
    # Central neck carrier is segmented around the dominant tall attic sash.
    cube("PavilionAtticCarrierL",(12.84,-15.24,9.15),(0.36,0.48,5.14),brick,0.0)
    cube("PavilionAtticCarrierR",(14.56,-15.24,9.15),(0.36,0.48,5.14),brick,0.0)
    cube("PavilionAtticCarrierSill",(13.70,-15.24,7.55),(1.36,0.48,2.20),brick,0.0)
    cube("PavilionAtticCarrierHead",(13.70,-15.24,11.24),(1.36,0.48,0.96),brick,0.0)
    vertical_prism_y("PavilionCompactPediment",[(12.60,11.72),(14.80,11.72),(13.70,12.55)],-15.24,0.48,brick,0.0)
    cube("PavilionStrongCornice",(13.7,-15.48,6.58),(7.78,0.18,0.20),stone,0.016)
    cube("PavilionNeckCornice",(13.7,-15.49,11.73),(2.28,0.14,0.11),stone,0.008)
    cube("PavilionPedimentBase",(13.7,-15.50,11.77),(2.34,0.14,0.085),stone,0.008)
    ped_l=cube("PavilionPedimentCopingL",(13.15,-15.50,12.16),(1.38,0.14,0.065),stone,0.008); ped_l.rotation_euler[1]=math.radians(-37.0)
    ped_r=cube("PavilionPedimentCopingR",(14.25,-15.50,12.16),(1.38,0.14,0.065),stone,0.008); ped_r.rotation_euler[1]=math.radians(37.0)
    cube("PavilionPedimentCrown",(13.70,-15.50,12.56),(0.22,0.16,0.12),stone,0.018)
    # Small recessed roundels support rather than compete with the gable.
    for x in (11.62,15.78):
        cylinder("PavilionRoundelBrickRim",(x,-15.51,8.73),0.12,0.050,brick,32,rotation=(math.pi/2,0,0))
        cylinder("PavilionRoundelStone",(x,-15.535,8.73),0.072,0.030,stone,32,rotation=(math.pi/2,0,0))
    # gable window layered section on outward face
    opening_assembly("PavilionAtticWindow",13.7,-15.36,9.70,1.48,2.10,"X",-1,0.48,mats,False,"bedroom",make_room=False)
    cube("PavilionAtticOccupiedBack",(13.70,-13.96,9.58),(1.26,0.06,1.42),room,0.0)
    cube("PavilionAtticOccupiedDesk",(13.70,-14.35,9.02),(0.82,0.34,0.07),timber,0.012)
    cube("PavilionAtticOccupiedBook",(13.45,-14.39,9.18),(0.12,0.08,0.22),stone,0.006)

    # integrated dormers and roof crossings
    for i,(loc,rot) in enumerate([((-7.5,8.65,7.20),0),((0.0,8.65,7.20),0),((7.5,8.65,7.20),0),((10.45,-2.0,7.18),-math.pi/2),((-10.85,1.5,7.20),math.pi/2)]): dormer(f"Dormer{i+1}",loc,rot,mats,lead,roof,dormer_room,dormer_sash)
    print("RLASM_STAGE pavilion_dormers_complete", flush=True)
    # chimneys continue into building zones and penetrate roof fields
    chimney_locs=[(-12,12),( -4,12),(4,12),(12,12),(13.5,4),(13.5,-7),(-13.7,5),(-13.7,-4)]
    for i,(x,y) in enumerate(chimney_locs):
        shaft_h=4.55+(i%4)*0.38
        shaft_w=1.04+(i%3)*0.16
        shaft_d=0.86+((i+1)%3)*0.11
        shaft_z=6.30+shaft_h/2
        crown_z=6.30+shaft_h
        contact_z=9.45 if (y==12 or x==13.5) else 9.25
        cube(f"Chimney{i}_shaft",(x,y,shaft_z),(shaft_w,shaft_d,shaft_h),brick,0.045)
        cube(f"Chimney{i}_flashing",(x,y,contact_z),(shaft_w+0.42,shaft_d+0.42,0.12),lead,0.018)
        cube(f"Chimney{i}_flashingApron",(x,y-0.30,contact_z-0.06),(shaft_w+0.58,0.32,0.055),lead,0.012)
        cube(f"Chimney{i}_crown1",(x,y,crown_z+0.10),(shaft_w+0.24,shaft_d+0.22,0.18),stone,0.022)
        cube(f"Chimney{i}_crown2",(x,y,crown_z+0.27),(shaft_w+0.12,shaft_d+0.10,0.16),brick,0.020)
        pot_offsets=(-0.27,0.27) if i%3 else (-0.30,0.0,0.30)
        for j,px in enumerate(pot_offsets):
            tapered_pot(f"Chimney{i}_pot{j}",(x+px,y,crown_z+0.66+(j%2)*0.10),0.14+(j%2)*0.012,0.095+(j%2)*0.010,0.66+(j%2)*0.14,brick,18)

    # open brick gates and iron leaves; no wall behind apertures
    # A complete masonry passage now cuts through the pavilion's west bay.
    gate_x=11.033
    arch_ring("EastGateStreetArch",(gate_x,-15.26),2.10,2.02,0.54,brick)
    arch_ring("EastGateCourtArch",(gate_x,-7.18),2.10,2.02,0.54,brick)
    cube("EastGatePassageWestReturn",(9.91,-11.22,1.48),(0.22,8.10,2.96),brick,0.025)
    cube("EastGatePassageEastReturn",(12.15,-11.22,1.48),(0.22,8.10,2.96),brick,0.025)
    cube("EastGatePassageSoffit",(gate_x,-11.22,3.00),(2.46,8.10,0.16),stone,0.025)
    arch_ring("WestGate",(-10.4,-12.9),2.45,2.30,0.68,brick)
    for gx,gy,w in [(gate_x,-15.34,1.78),(-10.4,-12.97,1.95)]:
        for j in range(9): cube("GateBar",(gx-w/2+j*w/8,gy,1.1),(0.045,0.06,2.15),iron,0.01)
        cube("GateTopRail",(gx,gy,2.05),(w,0.07,0.06),iron,0.01); cube("GateBottomRail",(gx,gy,0.20),(w,0.07,0.06),iron,0.01)
    # south garden wall and fence, segmented at both gates
    for x,cw in [(-15.0,4.0),(-3.8,10.0),(3.3,3.0)]: cube("SouthBrickCurb",(x,-14.6,0.35),(cw,0.55,0.70),brick,0.04)
    for x in [i*0.45-17 for i in range(76) if abs(i*0.45-17-gate_x)>1.5 and abs(i*0.45-17+10.4)>1.6]: cube("FencePicket",(x,-14.62,1.05),(0.035,0.05,1.45),iron,0.008)
    for i,(x,w) in enumerate([(-15.0,2.7),(-4.0,8.7),(0.5,0.8),(3.8,4.6),(8.65,2.3),(14.45,4.7),(16.9,0.7)]):
        cube(f"FenceTopSegment{i}",(x,-14.62,1.65),(w,0.06,0.06),iron,0.01)

    # Formal court rebuilt from the top source: four clipped pump-facing beds,
    # pale cross paths, grass interiors, perimeter hedges and restrained blooms.
    bed_polys=[
        [(-9.25,-13.05),(-0.70,-13.05),(-0.70,-4.95),(-0.80,-4.60),(-1.08,-4.32),(-1.45,-4.15),(-9.25,-4.15)],
        [(0.70,-13.05),(7.55,-13.05),(7.55,-4.15),(1.45,-4.15),(1.08,-4.32),(0.80,-4.60),(0.70,-4.95)],
        [(-9.25,-2.85),(-1.55,-2.85),(-1.18,-2.68),(-0.92,-2.40),(-0.82,-2.05),(-0.82,5.90),(-9.25,5.90)],
        [(1.55,-2.85),(8.95,-2.85),(8.95,5.90),(0.82,5.90),(0.82,-2.05),(0.92,-2.40),(1.18,-2.68)],
    ]
    for i,pts in enumerate(bed_polys):
        cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
        lawn_pts=[(cx+(x-cx)*0.94,cy+(y-cy)*0.94) for x,y in pts]
        polygon_prism(f"ClippedLawn{i}",lawn_pts,0.10,0.08,lawn,0.035)
        hedge_border(f"ClippedHedge{i}",pts,0.28,0.46,0.34,hedge)
        # Restrained perennial borders follow the long court edges instead of
        # sitting as two icon-like flowers in the middle of each bed.
        edge_ts=((0.18,0.63),(0.22,0.78),(0.31,0.72),(0.16,0.44,0.83))[i]
        for j,t in enumerate(edge_ts):
            a,b=pts[0],pts[1]
            planting_mound(f"CourtBorder{i}_{j}",a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,hedge,flowers)
        # A second, looser planted edge makes the border read horticulturally
        # occupied while retaining the clipped geometry of the source garden.
        return_ts=((0.38,), (0.24,0.68), (0.57,), (0.20,0.54,0.86))[i]
        for j,t in enumerate(return_ts):
            a,b=pts[2],pts[3]
            planting_mound(f"CourtReturnBorder{i}_{j}",a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,hedge,flowers)
    # The locked top source concentrates mature white perennial masses in the
    # two right-hand beds rather than distributing identical beads everywhere.
    source_perennial_groups=[
        (5.20,4.05),(5.52,3.72),(5.88,4.02),(6.22,3.62),(6.58,3.95),(6.92,3.58),(7.22,3.90),
        (5.38,3.10),(5.78,2.78),(6.18,3.04),(6.58,2.72),(7.02,2.92),
        (4.72,-6.05),(5.08,-6.38),(5.45,-6.02),(5.82,-6.42),(6.18,-6.04),(6.55,-6.38),(6.88,-6.02),
        (4.92,-7.02),(5.32,-7.36),(5.72,-7.02),(6.12,-7.38),(6.52,-7.06),
        (-6.35,-10.55),(-5.90,-10.25),(-6.70,3.95)
    ]
    for i,(px,py) in enumerate(source_perennial_groups):
        planting_mound(f"SourcePositionedPerennial{i}",px,py,hedge,flowers)
    print("RLASM_STAGE garden_complete", flush=True)
    # Gate-to-court route remains level, wide and visibly open through the bars.
    polygon_prism("EastGateThroughRoute",[(10.03,-15.45),(12.03,-15.45),(12.03,-3.75),(10.03,-3.75)],0.07,0.10,gravel,0.025)
    cylinder("PumpPlinth",(0,-3.5,0.17),1.45,0.34,stone,8)
    cylinder("PumpStep",(0,-3.5,0.38),1.02,0.22,stone,8)
    cube("PumpColumn",(0,-3.5,1.25),(0.55,0.55,1.65),stone,0.08)
    cylinder("PumpCap",(0,-3.5,2.15),0.52,0.22,stone,8)
    cube("PumpSpout",(0.45,-3.5,1.45),(0.8,0.10,0.12),iron,0.03)
    for bx,by,rot in [(-8.5,-3.5,0),(8.5,-3.5,0),(0,4.3,math.pi/2)]:
        seat=cube("GardenBench",(bx,by,0.55),(2.4,0.55,0.16),wood,0.06); seat.rotation_euler[2]=rot
        back=cube("GardenBenchBack",(bx,by+(-0.24 if rot==0 else 0),1.0),(2.4,0.12,0.7),wood,0.04); back.rotation_euler[2]=rot

    # Two adjacent Rear Court ground openings share one visually continuous
    # occupied room. Its common back wall, floor, furniture and shelves prove
    # that depth is not a per-pane metadata claim or isolated glowing box.
    cube("RearSharedRoomBack",(-4.20,12.35,1.72),(8.10,0.08,2.88),room,0.0)
    cube("RearSharedRoomFloor",(-4.20,10.35,0.42),(8.10,4.05,0.10),interior,0.0)
    cube("RearSharedRoomTable",(-4.20,10.70,0.86),(2.60,0.88,0.12),timber,0.025)
    for cx in (-5.15,-3.25):
        cube("RearSharedRoomChair",(cx,9.98,0.58),(0.42,0.42,0.12),timber,0.018)
        cube("RearSharedRoomChairBack",(cx,10.16,0.93),(0.42,0.08,0.62),timber,0.018)
    for sx in (-7.15,-1.25):
        cube("RearSharedRoomShelfSide",(sx,12.03,1.60),(0.10,0.32,2.15),timber,0.008)
        for sz in (0.72,1.34,1.96,2.58): cube("RearSharedRoomShelf",(sx,11.95,sz),(1.05,0.28,0.065),timber,0.008)
    cube("RearSharedReadingDesk",(-6.30,11.05,0.84),(1.45,0.62,0.10),timber,0.020)
    cube("RearSharedReadingChairSeat",(-6.30,10.48,0.55),(0.44,0.44,0.12),timber,0.015)
    cube("RearSharedReadingChairBack",(-6.30,10.68,0.91),(0.44,0.08,0.62),timber,0.015)
    for bx,bz in ((-6.62,0.94),(-6.40,0.92),(-6.17,0.96)):
        cube("RearSharedReadingBook",(bx,11.02,bz),(0.16,0.24,0.06),stone,0.004)

    # visible domestic program near court-facing windows and dedicated interior camera
    for x,y,rot in [(-9.0,10.2,0),(-2.0,10.2,0),(5.0,10.2,0),(11.5,3.0,math.pi/2),(-11.8,3.0,-math.pi/2)]:
        table=cube("DomesticTable",(x,y,0.85),(1.25,0.75,0.10),wood,0.05); table.rotation_euler[2]=rot
        for dx,dy in [(-0.55,0),(0.55,0)]:
            chair=cube("DomesticChair",(x+dx,y+dy,0.48),(0.38,0.38,0.08),wood,0.03); chair.rotation_euler[2]=rot
        cylinder("DomesticLamp",(x,y,2.25),0.16,0.20,stone,16)
    # Navigable communal kitchen/dining room in the pavilion. Correctly scaled
    # L-counters, island, dining clearance and the south openings occupy one
    # coherent enclosure and are visible from the interior and through glazing.
    cube("CommunalRoomPlasterFloor",(14.72,-11.10,0.26),(4.92,7.20,0.10),room,0.02)
    cube("CommunalRoomPassageWall",(12.18,-11.10,1.50),(0.16,7.38,2.96),room,0.02)
    cube("CommunalRoomBaseboard",(12.28,-11.10,0.38),(0.08,7.10,0.16),timber,0.012)
    # Warm source-conditioned plaster lines only the solid interior carrier
    # portions, leaving every opening, reveal and visible return physically open.
    for j,(x,w) in enumerate(((13.08,1.72),(16.68,1.74))):
        cube(f"KitchenSouthPlasterPier{j}",(x,-14.73,1.95),(w,0.045,2.10),interior,0.008)
        cube(f"KitchenSouthTimberWainscot{j}",(x,-14.70,0.82),(w,0.055,0.72),timber,0.010)
        cube(f"KitchenSouthChairRail{j}",(x,-14.67,1.20),(w,0.065,0.07),stone,0.008)
    for j,(y,w) in enumerate(((-14.48,1.04),(-11.08,1.86),(-7.78,0.92))):
        cube(f"KitchenEastPlasterPier{j}",(17.31,y,1.95),(0.045,w,2.10),interior,0.008)
        cube(f"KitchenEastTimberWainscot{j}",(17.28,y,0.82),(0.055,w,0.72),timber,0.010)
        cube(f"KitchenEastChairRail{j}",(17.25,y,1.20),(0.065,w,0.07),stone,0.008)
    cube("KitchenEastBase",(16.55,-10.85,0.74),(0.62,4.35,0.78),wood,0.04)
    cube("KitchenEastWorktop",(16.55,-10.85,1.17),(0.76,4.48,0.09),stone,0.025)
    cube("KitchenNorthBase",(16.05,-8.75,0.74),(0.92,0.62,0.78),wood,0.04)
    cube("KitchenNorthWorktop",(16.05,-8.75,1.17),(1.05,0.76,0.09),stone,0.025)
    for y in (-12.25,-11.35,-10.45,-9.55):
        cube("KitchenCabinetDoor",(16.20,y,0.74),(0.04,0.70,0.58),timber,0.012)
    cube("KitchenSink",(16.50,-10.20,1.24),(0.42,0.68,0.055),iron,0.015)
    cylinder("KitchenFaucet",(16.34,-9.90,1.48),0.035,0.42,iron,16)
    for sy in (-11.35,-10.90): cylinder("KitchenHobRing",(16.48,sy,1.24),0.12,0.025,iron,24)
    cube("KitchenRangeHood",(16.50,-11.15,1.92),(0.34,0.56,0.14),lead,0.018)
    cube("KitchenRangeHoodFlue",(16.50,-11.15,2.36),(0.18,0.24,0.72),lead,0.012)
    cube("KitchenIsland",(14.55,-10.55,0.74),(1.65,0.78,0.78),wood,0.04)
    cube("KitchenIslandTop",(14.55,-10.55,1.17),(1.80,0.90,0.09),stone,0.025)
    cube("KitchenIslandSink",(14.20,-10.55,1.23),(0.42,0.34,0.045),iron,0.012)
    cylinder("KitchenIslandFaucet",(14.20,-10.36,1.44),0.028,0.36,iron,14)
    for hx in (14.80,15.04): cylinder("KitchenIslandHob",(hx,-10.55,1.23),0.085,0.022,iron,20)
    # Dining table is separated from the island by a 0.9 m circulation lane.
    cube("CommunalTable",(13.55,-12.92,0.76),(1.72,0.78,0.11),wood,0.035)
    for cx,cy in ((12.94,-12.92),(14.16,-12.92),(13.55,-12.30),(13.55,-13.54)):
        cylinder("DiningPlate",(cx,cy,0.85),0.10,0.022,stone,20)
        cube("DiningChair",(cx,cy+0.46 if cy < -12.0 else cy-0.46,0.44),(0.36,0.36,0.08),wood,0.03)
        cube("DiningChairBack",(cx,cy+0.60 if cy < -12.0 else cy-0.60,0.78),(0.36,0.08,0.58),wood,0.025)
    for lx,ly in ((13.45,-12.78),(14.55,-10.55)):
        cylinder("KitchenPendant",(lx,ly,2.38),0.13,0.18,lead,20)
        cylinder("KitchenPendantStem",(lx,ly,2.72),0.018,0.56,iron,12)
    cube("KitchenUndercounterFridge",(16.18,-12.22,0.73),(0.045,0.72,0.64),lead,0.018)
    cube("KitchenFridgeHandle",(16.13,-12.22,0.78),(0.025,0.42,0.035),stone,0.006)
    cube("KitchenUndercounterOven",(16.18,-11.34,0.73),(0.045,0.72,0.64),iron,0.018)
    cube("KitchenOvenHandle",(16.13,-11.34,0.96),(0.025,0.42,0.030),stone,0.006)
    for z,w in ((1.62,1.55),(2.05,1.32)):
        cube("KitchenPantryShelf",(13.55,-8.36,z),(w,0.18,0.07),timber,0.012)
        for sx in (-0.42,0.0,0.42): cylinder("KitchenShelfCrock",(13.55+sx,-8.38,z+0.10),0.07,0.16,stone,16)
    cube("KitchenSourcePlasterSplashback",(16.16,-10.85,1.52),(0.030,2.90,0.34),interior,0.008)
    cube("KitchenSourceTimberShelf",(16.00,-10.85,1.78),(0.28,2.72,0.07),timber,0.010)
    for sy in (-11.75,-11.05,-10.35,-9.65): cylinder("KitchenShelfCrockery",(15.82,sy,1.90),0.09,0.035,stone,18)
    cube("KitchenRouteRug",(13.30,-10.20,0.33),(1.45,2.30,0.025),curtain,0.02)
    for x in (12.2,15.2):
        cube("BedFrame",(x,-10.5,3.62),(1.45,2.0,0.32),wood,0.06)
        cube("BedLinen",(x,-10.5,3.84),(1.25,1.75,0.22),curtain,0.08)
    for i in range(12):
        step=cube("StairTread",(15.4,-7.8+i*0.19,0.22+i*0.24),(1.15,0.32,0.20),wood,0.02)
    cube("StairLanding",(15.4,-5.3,3.1),(1.5,1.2,0.18),wood,0.02)
    for i in range(7): cube("StairGuard",(16.0,-7.8+i*0.42,1.0+i*0.28),(0.05,0.05,1.0),iron,0.01)
    print("RLASM_STAGE program_complete", flush=True)

    # Exterior vegetation is intentionally omitted from the proof envelope;
    # the source-defining planted court carries the landscape identity.

    # GLB delivery
    if os.environ.get('RLASM_SKIP_EXPORT','0') != '1':
        bpy.ops.wm.save_as_mainfile(filepath=str(MODEL / "amsterdam-hofje-medieval-v023.blend"))
        bpy.ops.export_scene.gltf(filepath=str(MODEL / "amsterdam-hofje-medieval-v023.glb"),export_format='GLB',use_selection=False,export_yup=True)
    return dict(brick=brick,roof=roof,stone=stone,lead=lead,timber=timber,iron=iron,glass=glass,gravel=gravel,lawn=lawn,hedge=hedge,flowers=flowers)


def look_at(obj, target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def setup_render():
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=1280; scene.render.resolution_y=960; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0.78
    scene.world.color=(0.11,0.13,0.15)
    world=scene.world; world.use_nodes=True
    bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.34,0.42,0.52,1); bg.inputs['Strength'].default_value=0.55
    bpy.ops.object.light_add(type='AREA',location=(-18,-20,28)); key=bpy.context.object; key.name='BroadNorthLight'; key.data.energy=3100; key.data.shape='DISK'; key.data.size=18; look_at(key,(0,0,4))
    bpy.ops.object.light_add(type='AREA',location=(18,-4,16)); fill=bpy.context.object; fill.name='SoftFill'; fill.data.energy=1800; fill.data.size=14; look_at(fill,(0,0,4))
    bpy.ops.object.light_add(type='SUN',location=(0,0,20)); sun=bpy.context.object; sun.data.energy=2.2; sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-35))
    # local warm room lights reinforce depth, not panes
    for loc in [(-12,10.5,2.2),(-6,10.5,2.2),(-2,10.5,2.2),(1,10.5,2.2),(7,10.5,2.2),(12,-7,2.2),(12,-10,4.6),(11.0,-13.1,4.7),(15.2,-13.1,4.7)]:
        bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=260; l.data.color=(1.0,0.55,0.28); l.data.size=2.0; l.data.use_shadow=False; l.rotation_euler=(math.radians(90),0,0)
    for loc in [(-12,10.5,4.7),(-3,10.5,4.7),(6,10.5,4.7),(12,2.5,4.7),(-12,2.5,4.7),(-12,-5.0,4.7)]:
        bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.data.energy=150; l.data.color=(1.0,0.48,0.20); l.data.size=1.5; l.data.use_shadow=False; l.rotation_euler=(math.radians(90),0,0)
    bpy.ops.object.light_add(type='POINT',location=(14.0,-11.6,2.55))
    kitchen_light=bpy.context.object; kitchen_light.name='CommunalKitchenWarmLight'; kitchen_light.data.energy=520; kitchen_light.data.color=(1.0,0.56,0.30); kitchen_light.data.shadow_soft_size=1.1
    bpy.ops.object.light_add(type='POINT',location=(15.7,-8.9,1.85))
    window_light=bpy.context.object; window_light.name='PavilionWindowDepthLight'; window_light.data.energy=680; window_light.data.color=(1.0,0.48,0.22); window_light.data.shadow_soft_size=0.8
    for z in (1.75,4.55):
        bpy.ops.object.light_add(type='POINT',location=(11.35,-0.3,z)); depth_light=bpy.context.object
        depth_light.name=f'CourtWindowOccupiedDepthLight{z}'; depth_light.data.energy=420; depth_light.data.color=(1.0,0.48,0.20); depth_light.data.shadow_soft_size=0.65
    # Low-energy continuous facade lights reveal rooms without turning panes
    # into identical emissive rectangles.
    for i,loc in enumerate(((-11.5,13.1,1.9),(-6.0,13.1,1.9),(-2.0,13.1,1.9),(3.5,13.1,1.9),(9.5,13.1,1.9),(14.8,4.0,1.9),(14.8,-2.5,1.9),(-14.8,4.0,1.9),(-14.8,-2.5,1.9))):
        bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.name=f'ContinuousOccupiedFacadeLight{i}'; l.data.energy=105; l.data.color=(1.0,0.57,0.34); l.data.size=1.8; l.data.use_shadow=False; l.rotation_euler=(math.radians(90),0,0)
    for i,loc in enumerate(((-7.5,9.14,7.48),(0.0,9.14,7.48),(7.5,9.14,7.48),(10.74,-2.0,7.42),(-11.14,1.5,7.45))):
        bpy.ops.object.light_add(type='POINT',location=loc); dormer_light=bpy.context.object
        dormer_light.name=f'DormerOccupiedDepthLight{i}'; dormer_light.data.energy=3; dormer_light.data.color=(1.0,0.50,0.24); dormer_light.data.shadow_soft_size=0.40; dormer_light.data.use_shadow=False


def render_all():
    print("RLASM_STAGE render_setup", flush=True)
    setup_render(); scene=bpy.context.scene
    cameras={
        'front':((40,-61,13.5),(0,-0.5,4.7),52),
        'front_corner':((-66,-72,34),(0,0,5.0),48),
        'aerial':((-68,-64,64),(0,0,3.6),50),
        'true_top':((0,0,70),(0,0,0),50),
        'left_side':((-76,0,20),(0,0,5),48),
        'right_side':((76,0,20),(0,0,5),48),
        'rear':((0,76,20),(0,0,5),48),
        'rear_side':((-68,66,36),(0,0,5),48),
        'facade_close':((-5,-30,8),(10,-9,5.1),48),
        'architecture_close':((30,-34,15),(13.7,-14.9,8.7),50),
        'glass_close':((-5.10,0.40,2.42),(-6.30,8.18,1.64),56),
        'gate_contact_close':((11.033,-24.0,2.05),(11.033,-1.8,1.48),48),
        'roof_contact_close':((3.8,-6.2,9.45),(10.45,-2.0,7.02),62),
        'dormer_contact_close':((-4.6,2.15,9.25),(0.0,8.66,7.02),64),
        'program_interior':((12.60,-14.25,2.42),(14.90,-10.65,0.98),26),
        'courtyard_axis':((0,-26,6.2),(0,-1.5,2.4),48),
    }
    selected={v.strip() for v in os.environ.get('RLASM_RENDER_ROLES','').split(',') if v.strip()}
    for role,(loc,target,lens) in cameras.items():
        if selected and role not in selected:
            continue
        print(f"RLASM_RENDER_START {role}", flush=True)
        bpy.ops.object.camera_add(location=loc); cam=bpy.context.object; cam.name='CAM_'+role; cam.data.lens=lens; look_at(cam,target); scene.camera=cam
        if role=='true_top': cam.data.type='ORTHO'; cam.data.ortho_scale=58
        scene.render.filepath=str(RENDERS/f'{role}.png'); bpy.ops.render.render(write_still=True)
        print(f"RLASM_RENDER_DONE {role}", flush=True)
        bpy.data.objects.remove(cam,do_unlink=True)


def evidence():
    glb=MODEL/'amsterdam-hofje-medieval-v023.glb'
    data={
      'schema':'cityprompt.rlasm.builder-evidence@6.1','candidate_id':'rlasm-amsterdam-hofje-medieval-v023','lifecycle_state':'visual_review_ready',
      'generic_fallback_count':0,'source_specific_material_fallbacks':0,'mounted_perspective_photographs':0,'opening_section_order':['cut segmented carrier','returns','recessed frame','separate pane','offset occupied layer','enclosed room depth'],
      'program':'12-unit charitable residential hofje with communal kitchen, bedrooms, stairs, garden and pump visibly modeled',
      'render_files':[p.name for p in sorted(RENDERS.glob('*.png'))],'glb_bytes':glb.stat().st_size,
      'builder_decision':'pending_pixel_gate','keeper':False
    }
    (ROOT/'evidence'/'builder-evidence.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    (ROOT/'review'/'status.json').write_text(json.dumps({'schema':'cityprompt.rlasm.lifecycle@6.1','candidate_id':'rlasm-amsterdam-hofje-medieval-v023','state':'visual_review_ready','builder_gate':'pending_pixel_inspection','independent_holistic_review':'not_started','keeper':False},indent=2),encoding='utf-8')


if __name__=='__main__':
    build(); render_all()
    if os.environ.get('RLASM_SKIP_EXPORT','0') != '1': evidence()
    print(json.dumps({'status':'rendered','renders':len(list(RENDERS.glob('*.png'))) }))
