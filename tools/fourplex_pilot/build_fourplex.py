"""One-image RLASM v6.1 fourplex candidate. Run with Blender 5.x --background --python ... -- --output DIR [--pilot].

The street-facing composition follows the locked oblique photograph. Hidden
elevations and the residential room layout are explicit design inferences.
Generated GLBs and renders live outside the source tree until independent review.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


args = argparse.ArgumentParser()
args.add_argument("--output", required=True)
args.add_argument("--pilot", action="store_true")
args.add_argument("--materials-dir")
config = args.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
OUT = Path(config.output).resolve()
OUT.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


def mat(name, rgb, rough=0.7, metal=0, alpha=1, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, alpha)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Alpha"].default_value = alpha
    if emission:
        p.inputs["Emission Color"].default_value = (*emission, 1)
        p.inputs["Emission Strength"].default_value = 0.38
    if alpha < 1:
        m.surface_render_method = "DITHERED"
    return m


# Palette measured from the photograph's black vertical cladding, cool white
# lap siding, charcoal shingle, dark brick plinth, and warm inhabited glazing.
M = {
    "dark": mat("Source dark charcoal board-and-batten", (0.105, .111, .121), .82),
    "dark_alt": mat("Weathered charcoal board variation", (.128, .136, .145), .86),
    "white": mat("Source cool ivory horizontal lap", (.79, .78, .74), .83),
    "white_alt": mat("Ivory lap edge", (.69, .69, .66), .8),
    "brick": mat("Deep charcoal running-bond brick", (.19, .18, .17), .88),
    "mortar": mat("Warm grey brick joints", (.32, .31, .29), .9),
    "roof": mat("Weathered black architectural shingle", (.115, .12, .135), .94),
    "roof_alt": mat("Architectural shingle tonal variation", (.14, .145, .155), .96),
    "fascia": mat("White painted gable and eaves trim", (.83, .82, .78), .65),
    "soffit": mat("Warm underside soffit", (.64, .63, .59), .74),
    "black": mat("Black powder-coated frames and rail", (.045, .049, .054), .48, .15),
    "glass": mat("Layered smoked low-iron glass", (.19, .24, .26), .12, 0, .24),
    "room": mat("Warm occupied room plane", (.59, .46, .29), .9, 0, 1, (.9, .62, .30)),
    "curtain": mat("Sheer interior curtains", (.68, .64, .53), .92),
    "wood": mat("Warm interior joinery", (.39, .26, .17), .67),
    "concrete": mat("Exposed pale cast-concrete stoops", (.61, .59, .55), .94),
    "stone": mat("Foundation and walkway", (.48, .47, .43), .95),
    "soil": mat("Mulched planted bed", (.15, .12, .09), 1),
    "grass": mat("Front lawn", (.19, .28, .12), .98),
    "leaf": mat("Planted green foliage", (.13, .22, .095), .93),
    "leaf2": mat("Lighter shrub foliage", (.2, .29, .12), .91),
    "flower": mat("Pale hydrangea flower", (.83, .81, .65), .86),
    "light": mat("Recessed porch light", (.95, .7, .32), .36, 0, 1, (.95, .55, .22)),
}

TEXTURE_ROLES={
    "dark":("dark_siding",1.75,3.0),
    "white":("white_lap",2.0,.95),
    "brick":("charcoal_brick",1.15,.72),
    "roof":("roof_shingle",1.65,1.15),
}

def bind_material_textures():
    if not config.materials_dir:return
    root=Path(config.materials_dir).resolve()
    for key,(role,_,_) in TEXTURE_ROLES.items():
        material=M[key];nodes=material.node_tree.nodes;links=material.node_tree.links
        bsdf=nodes.get("Principled BSDF")
        tex=nodes.new("ShaderNodeTexImage");tex.name=f"{role} source albedo";tex.image=bpy.data.images.load(str(root/f"{role}-albedo.png"))
        tex.extension="REPEAT"
        links.new(tex.outputs["Color"],bsdf.inputs["Base Color"])
        normal_tex=nodes.new("ShaderNodeTexImage");normal_tex.image=bpy.data.images.load(str(root/f"{role}-normal.png"))
        normal_tex.image.colorspace_settings.name="Non-Color";normal_tex.extension="REPEAT"
        normal=nodes.new("ShaderNodeNormalMap");normal.inputs["Strength"].default_value=.42
        links.new(normal_tex.outputs["Color"],normal.inputs["Color"])
        links.new(normal.outputs["Normal"],bsdf.inputs["Normal"])
        rough=nodes.new("ShaderNodeTexImage");rough.image=bpy.data.images.load(str(root/f"{role}-roughness.png"))
        rough.image.colorspace_settings.name="Non-Color";rough.extension="REPEAT"
        links.new(rough.outputs["Color"],bsdf.inputs["Roughness"])

def map_world_uv(obj, key):
    role,tile_u,tile_v=TEXTURE_ROLES[key]
    uv=obj.data.uv_layers.active or obj.data.uv_layers.new(name="RLASM metre-scale UV")
    for polygon in obj.data.polygons:
        normal=(obj.matrix_world.to_3x3()@polygon.normal).normalized()
        for loop_index in polygon.loop_indices:
            loop=obj.data.loops[loop_index]
            point=obj.matrix_world@obj.data.vertices[loop.vertex_index].co
            if key=="roof":u,v=point.y/tile_u,point.x/tile_v
            elif abs(normal.x)>abs(normal.y):u,v=point.y/tile_u,point.z/tile_v
            else:u,v=point.x/tile_u,point.z/tile_v
            uv.data[loop_index].uv=(u,v)

bind_material_textures()


def cube(name, x, y, z, sx, sy, sz, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    o = bpy.context.object
    o.name = name
    o.dimensions = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Small physical edge", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o


def mesh(name, vertices, faces, material):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def beam(name, a, b, width, depth, material):
    mid = (Vector(a) + Vector(b)) / 2
    direction = Vector(b) - Vector(a)
    obj = cube(name, *mid, width, depth, direction.length, material)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return obj


def panel_wall(name, xmin, xmax, y, zmin, zmax, openings, material, thickness=.23):
    """Continuous opaque carrier with real empty cells at all openings."""
    xs = sorted({xmin, xmax, *(value for a, b, _, _ in openings for value in (a, b))})
    zs = sorted({zmin, zmax, *(value for _, _, a, b in openings for value in (a, b))})
    for i, (xa, xb) in enumerate(zip(xs, xs[1:])):
        for j, (za, zb) in enumerate(zip(zs, zs[1:])):
            mx, mz = (xa + xb) / 2, (za + zb) / 2
            if xa < xmin - 1e-5 or xb > xmax + 1e-5 or za < zmin - 1e-5 or zb > zmax + 1e-5:
                continue
            if any(a < mx < b and c < mz < d for a, b, c, d in openings):
                continue
            cube(f"{name}_carrier_{i}_{j}", mx, y, mz, xb-xa, thickness, zb-za, material)


def opening(name, x, y, z, w, h, entrance=False, facing=-1):
    """Cut carrier is assembled separately; this builds returns and layered optics."""
    y_face = y + facing * .13
    depth = .42
    frame = M["fascia"] if z > 4.5 else M["black"]
    for side in (-1, 1):
        cube(f"{name}_deep_jamb_{side}", x+side*(w/2-.055), y, z+h/2, .11, depth, h, M["white"] if entrance else frame)
    # Keep the returns flush with the jambs; projecting dark ends looked like
    # square holes in the white cladding from street distance.
    cube(name+"_head_return", x, y, z+h-.065, w, depth, .13, frame)
    cube(name+"_sill_return", x, y, z+.045, w+.08, depth, .09, M["concrete"] if entrance else frame)
    if not entrance:
        # A single flat exterior casing ring bridges the physical returns.
        # Its non-overlapping quads avoid the black corner blocks created by
        # separate deep frame cubes and their contact shadows.
        face_y = y + facing*.305
        outer = (x-w/2-.06, x+w/2+.06, z-.06, z+h+.06)
        inner = (x-w/2+.08, x+w/2-.08, z+.08, z+h-.08)
        x0,x1,z0,z1 = outer
        a,b,c,d = inner
        quads = [((x0,z0),(x1,z0),(x1,c),(x0,c)),
                 ((x0,d),(x1,d),(x1,z1),(x0,z1)),
                 ((x0,c),(a,c),(a,d),(x0,d)),
                 ((b,c),(x1,c),(x1,d),(b,d))]
        for index,quad in enumerate(quads):
            verts=[(px,face_y,pz) for px,pz in quad]
            mesh(f"{name}_face_casing_{index}", verts,
                 [tuple(range(4)) if facing < 0 else (3,2,1,0)], frame)
    if z > 4.5:
        for side in (-1, 1):
            for edge in (z+.065, z+h-.065):
                cube(f"{name}_casing_corner_{side}_{edge:.2f}",
                     x+side*(w/2-.055), y+facing*.227, edge,
                     .14, .035, .14, frame)
    if entrance:
        # The outer door plane is set back, leaving a usable porch recess.
        cube(name+"_inset_door", x, y-facing*.33, z+h*.48, w-.18, .055, h-.15, M["black"])
        cube(name+"_door_lite", x, y-facing*.29, z+h*.64, w*.48, .018, h*.50, M["glass"])
        cube(name+"_door_lite_mullion", x, y-facing*.265, z+h*.64, .032, .029, h*.49, M["black"])
        cube(name+"_door_handle", x+w*.32, y-facing*.28, z+h*.48, .035, .07, .22, M["fascia"])
        cube(name+"_door_threshold", x, y+facing*.23, z+.035, w-.12, .28, .07, M["concrete"])
        return
    cube(name+"_optical_pane", x, y-facing*.075, z+h*.51, w-.13, .018, h-.14, M["glass"])
    cube(name+"_mullion", x, y_face, z+h*.51, .045, .045, h-.13, M["black"])
    cube(name+"_upper_rail", x, y_face, z+h*.69, w-.12, .045, .04, M["black"])
    # Warm room, curtains and a rear wall sit distinctly behind the optical layer.
    cube(name+"_room_depth", x, y-facing*1.02, z+h*.52, w-.23, .025, h-.2, M["room"])
    for side in (-1, 1):
        cube(f"{name}_curtain_{side}", x+side*(w*.32), y-facing*.33, z+h*.53, w*.13, .015, h*.77, M["curtain"])
    cube(name+"_interior_sill", x, y-facing*.29, z+.15, w*.79, .24, .055, M["wood"])
    # Restrained inhabited detail stays behind the glazing and never becomes
    # a false exterior sticker or a collision surface at an entrance.
    if w > 1.9:
        for level in range(3):
            cube(f"{name}_interior_shelf_{level}", x-w*.31, y-facing*.77,
                 z+.28+level*.38, w*.20, .24, .055, M["wood"])
        cube(name+"_warm_lamp", x+w*.23, y-facing*.73, z+h*.60,
             .17, .12, .24, M["light"])


def front_cladding(name, xmin, xmax, y, z0, z1, dark, openings):
    panel_wall(name, xmin, xmax, y, z0, z1, openings, M["dark"] if dark else M["white"])
    if dark:
        x = xmin + .18
        count = 0
        while x < xmax - .1:
            if not any(a-.02 < x < b+.02 for a,b,c,d in openings if c < z1 and d > z0):
                cube(f"{name}_batten_{count}", x, y-.135, (z0+z1)/2, .042, .025, z1-z0, M["dark_alt"])
            x += .34; count += 1
    else:
        z=z0+.16; count=0
        while z<z1-.02:
            for xa,xb in zip([xmin]+[b for a,b,c,d in openings if c<z<d], [a for a,b,c,d in openings if c<z<d]+[xmax]):
                if xb-xa>.02:
                    cube(f"{name}_lap_{count}_{xa:.2f}", (xa+xb)/2, y-.137, z, xb-xa, .025, .03, M["white_alt"])
            z += .18; count += 1


def gable(name, left, right, front, rear, eave, ridge, dark):
    mid=(left+right)/2
    mesh(name+"_front_triangle",
         [(left,front,eave),(right,front,eave),(mid,front,ridge),
          (left,front+.22,eave),(right,front+.22,eave),(mid,front+.22,ridge)],
         [(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)],
         M["dark"] if dark else M["white"])
    mesh(name+"_rear_triangle",
         [(left,rear,eave),(right,rear,eave),(mid,rear,ridge)],[(0,2,1)],M["white"])
    over=.42; front_outer=front-.48; rear_outer=rear+.42
    for side in (-1,1):
        xa=mid; xb=mid+side*(right-left)/2+side*over
        za=ridge+.12; zb=eave-.05
        mesh(name+f"_slope_{side}",
             [(xa,front_outer,za),(xb,front_outer,zb),(xb,rear_outer,zb),(xa,rear_outer,za),
              (xa,front_outer,za-.12),(xb,front_outer,zb-.12),(xb,rear_outer,zb-.12),(xa,rear_outer,za-.12)],
             [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)], M["roof"])
        beam(name+f"_white_front_rake_{side}",(xa,front_outer-.045,za),(xb,front_outer-.045,zb),.13,.12,M["fascia"])
        beam(name+f"_rear_rake_{side}",(xa,rear_outer,za),(xb,rear_outer,zb),.11,.11,M["fascia"])
        cube(name+f"_eave_fascia_{side}",xb,rear/2+front/2,zb-.045,.12,rear_outer-front_outer,.16,M["fascia"])
        # The source-derived asphalt material carries the shingle pattern. Long
        # raised course bars made this roof read as standing-seam metal.
    beam(name+"_ridge_cap",(mid,front_outer, ridge+.13),(mid,rear_outer,ridge+.13),.13,.12,M["roof_alt"])
    # Vertical gable battens follow the sloped envelope; no pasted elevation.
    if dark:
        x=left+.2
        while x<right-.1:
            ztop=ridge-abs(x-mid)*(ridge-eave)/(mid-left)-.13
            if ztop>eave+.1:
                cube(f"{name}_front_gable_batten_{x:.2f}",x,front-.018,(eave+ztop)/2,.034,.028,ztop-eave,M["dark_alt"])
            x+=.34


UNIT=5.35; FRONT=-5.25; REAR=5.25; WIDTH=UNIT*4
for i in range(4):
    left=-WIDTH/2+i*UNIT; right=left+UNIT; cx=(left+right)/2
    # The stepped front wall and alternating gable fields follow the photo's
    # staggered, charcoal-dominant street elevation.
    front=FRONT+[ -.18,.13,-.05,.15 ][i]
    dark=[True,False,True,True][i]
    door=(left+.46,left+1.53,1.16,3.51)
    living=(left+2.03,right-.36,1.73,3.25)
    upper=(cx-.85,cx+.85,4.85,6.75)
    base_openings=[(left+.47,left+1.45,.64,1.08)]
    cube(f"unit{i+1}_foundation",cx,0,.36,UNIT,10.52,.72,M["concrete"])
    panel_wall(f"unit{i+1}_front_brick",left,right,front,.72,1.47,base_openings,M["brick"])
    front_cladding(f"unit{i+1}_front_lap",left,right,front,1.47,4.19,False,[door,living])
    front_cladding(f"unit{i+1}_upper_cladding",left,right,front,4.19,7.05,dark,[upper])
    opening(f"unit{i+1}_entry",(door[0]+door[1])/2,front,door[2],door[1]-door[0],door[3]-door[2],True)
    opening(f"unit{i+1}_living_window",(living[0]+living[1])/2,front,living[2],living[1]-living[0],living[3]-living[2])
    opening(f"unit{i+1}_bedroom_window",cx,front,upper[2],upper[1]-upper[0],upper[3]-upper[2])
    opening(f"unit{i+1}_basement_window",left+.96,front,.65,.95,.4)
    # A dark physical brick base with running bond relief, restrained at city distance.
    for row in range(4):
        z=.81+row*.16
        offset=.21 if row%2 else 0
        x=left+offset
        while x<right:
            cube(f"unit{i+1}_brick_joint_{row}_{x:.2f}",x,front-.135,z,.022,.014,.14,M["mortar"])
            x+=.43
    for step in range(5):
        h=.23*(step+1)
        y=front-2.52+step*.40
        cube(f"unit{i+1}_entry_stair_{step}",left+1.0,y,h/2,1.67,.42,h,M["concrete"],.018)
    cube(f"unit{i+1}_entry_landing",left+1.0,front-.42,1.10,1.72,1.25,.16,M["concrete"],.018)
    for side in (-1,1):
        rx=left+1.0+side*.76
        for step in range(5):
            yy=front-2.54+step*.40
            cube(f"unit{i+1}_rail_post_{side}_{step}",rx,yy,.52+step*.23, .045,.045,1.04,M["black"])
        beam(f"unit{i+1}_sloped_handrail_{side}",(rx,front-2.56,1.03),(rx,front-.55,2.12),.055,.055,M["black"])
    # Deep supported entry canopy, lit from its underside.
    cube(f"unit{i+1}_entry_canopy",left+1.0,front-.76,3.83,2.18,1.67,.18,M["roof"])
    cube(f"unit{i+1}_canopy_soffit",left+1.0,front-.76,3.72,2.12,1.60,.045,M["soffit"])
    cube(f"unit{i+1}_canopy_fascia",left+1.0,front-1.60,3.77,2.22,.12,.22,M["fascia"])
    cube(f"unit{i+1}_porch_sconce",left+1.71,front-.22,3.20,.09,.07,.18,M["light"])
    # Shared-party walls, occupied ground and first floor, and a modest rear elevation.
    cube(f"unit{i+1}_ground_floor",cx,0,1.17,UNIT-.12,10.30,.14,M["wood"])
    cube(f"unit{i+1}_first_floor",cx,0,4.19,UNIT-.12,10.30,.18,M["wood"])
    back_door=(left+.48,left+1.52,1.16,3.47)
    back_window=(left+2.05,right-.35,1.69,3.27)
    back_upper=(cx-.75,cx+.75,4.91,6.64)
    panel_wall(f"unit{i+1}_rear_wall",left,right,REAR,.72,7.05,[back_door,back_window,back_upper],M["white"])
    opening(f"unit{i+1}_rear_entry",(back_door[0]+back_door[1])/2,REAR,back_door[2],back_door[1]-back_door[0],back_door[3]-back_door[2],entrance=True,facing=1)
    opening(f"unit{i+1}_rear_living",(back_window[0]+back_window[1])/2,REAR,back_window[2],back_window[1]-back_window[0],back_window[3]-back_window[2],facing=1)
    opening(f"unit{i+1}_rear_bedroom",cx,REAR,back_upper[2],back_upper[1]-back_upper[0],back_upper[3]-back_upper[2],facing=1)
    cube(f"unit{i+1}_rear_terrace",left+1.0,REAR+.88,.16,2.04,1.74,.24,M["concrete"])
    for step in range(4):
        height=.25*(step+1)
        cube(f"unit{i+1}_rear_stair_{step}",left+1.0,REAR+2.49-step*.39,height/2,1.4,.4,height,M["concrete"],.014)
    cube(f"unit{i+1}_rear_landing",left+1.0,REAR+.3,1.08,1.55,.76,.16,M["concrete"])
    if i<3:
        cube(f"party_wall_{i+1}",right,0,4.12,.18,10.50,5.86,M["white"])
    # House scale interior organization visible through front and rear glazing.
    cube(f"unit{i+1}_entry_sidewall",left+1.75,-3.45,2.66,.11,3.1,2.9,M["white"])
    cube(f"unit{i+1}_living_rearwall",cx,-.42,2.67,UNIT-.3,.12,2.8,M["white"])
    cube(f"unit{i+1}_sofa_base",cx+.63,-2.02,1.56,1.45,.76,.42,M["curtain"],.08)
    cube(f"unit{i+1}_sofa_back",cx+.63,-1.70,1.90,1.45,.17,.71,M["curtain"],.05)
    cube(f"unit{i+1}_upper_bed",cx,-2.15,4.50,1.55,2.0,.37,M["wood"])
    cube(f"unit{i+1}_upper_bedding",cx,-2.15,4.73,1.43,1.9,.13,M["curtain"])
    gable(f"unit{i+1}_roof",left,right,front,REAR,7.05,9.45,dark)
    # Low stoop planting restrained so every entry stays clear and walkable.
    bedx=left+3.57
    cube(f"unit{i+1}_planting_bed",bedx,front-1.14,.08,2.45,1.85,.16,M["soil"])
    for n,(dx,dy,scale) in enumerate([(-.78,-.2,.45),(-.27,.22,.38),(.33,-.16,.5),(.84,.18,.35)]):
        for leaf in range(6):
            theta=leaf*math.tau/6+n*.37
            ox=math.cos(theta)*scale*.48;oy=math.sin(theta)*scale*.38
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=scale*.54,
                location=(bedx+dx+ox,front-1.16+dy+oy,.25+scale*.8+(leaf%3)*.045))
            shrub=bpy.context.object;shrub.name=f"unit{i+1}_shrub_{n}_leaf_{leaf}"
            shrub.scale=(.84,.73,.64);shrub.data.materials.append(M["leaf" if (n+leaf)%3 else "leaf2"])
        if n in (0,2):
            for f in range(7):
                theta=f*math.tau/7
                bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=.044,
                    location=(bedx+dx+math.cos(theta)*scale*.38,front-1.38+dy+math.sin(theta)*scale*.25,.59+scale*.5))
                bpy.context.object.name=f"unit{i+1}_flower_{n}_{f}"
                bpy.context.object.data.materials.append(M["flower"])

# End elevations continue the real weathering envelope and cut their carriers.
for side in (-1,1):
    x=side*WIDTH/2
    apertures=[(-3.65,-2.32,1.82,3.27),(-3.65,-2.32,4.92,6.61),(1.66,2.99,4.92,6.61)]
    ys=sorted({FRONT,REAR,*(v for a,b,c,d in apertures for v in (a,b))})
    zs=sorted({.72,1.47,4.19,7.05,*(v for a,b,c,d in apertures for v in (c,d))})
    for yi,(ya,yb) in enumerate(zip(ys,ys[1:])):
        for zi,(za,zb) in enumerate(zip(zs,zs[1:])):
            midy,midz=(ya+yb)/2,(za+zb)/2
            if any(a<midy<b and c<midz<d for a,b,c,d in apertures):
                continue
            material=M["brick"] if midz<1.47 else M["white"] if midz<4.19 else M["dark"]
            cube(f"endwall_{side}_carrier_{yi}_{zi}",x,midy,midz,.23,yb-ya,zb-za,material)
    for idx,(ya,yb,za,zb) in enumerate(apertures):
        ym=(ya+yb)/2;w=yb-ya;h=zb-za
        for edge_y in (ya+.06,yb-.06):
            cube(f"end_{side}_window_{idx}_jamb_{edge_y:.2f}",x+side*.07,edge_y,(za+zb)/2,.35,.12,h,M["black"])
        for edge_z in (za+.045,zb-.045):
            cube(f"end_{side}_window_{idx}_return_{edge_z:.2f}",x+side*.07,ym,edge_z,.36,w,.09,M["black"])
        cube(f"end_{side}_window_{idx}_pane",x+side*.155,ym,(za+zb)/2,.025,w-.15,h-.14,M["glass"])
        cube(f"end_{side}_window_{idx}_mullion",x+side*.185,ym,(za+zb)/2,.05,.045,h-.16,M["black"])
        cube(f"end_{side}_window_{idx}_occupied_room",x-side*.37,ym,(za+zb)/2,.025,w-.22,h-.2,M["room"])
    for z in [1.56+.18*n for n in range(15)]:
        for ya,yb in zip(ys,ys[1:]):
            ym=(ya+yb)/2
            if any(a<ym<b and c<z<d for a,b,c,d in apertures):continue
            cube(f"end_{side}_lap_{z:.2f}_{ya:.2f}",x+side*.132,ym,z,.025,yb-ya,.028,M["white_alt"])
    for y in [FRONT+.34*n for n in range(1,31)]:
        if any(a<y<b and c<5.6<d for a,b,c,d in apertures):continue
        cube(f"end_{side}_batten_{y:.2f}",x+side*.133,y,5.62,.023,.037,2.81,M["dark_alt"])
    cube(f"endwall_{side}_brick_base",x,0,1.03,.27,10.5,.67,M["brick"])

# Simple shallow roof eave troughs and downspouts at the three valleys.
for i in range(1,4):
    x=-WIDTH/2+i*UNIT
    beam(f"valley_{i}_gutter",(x,FRONT-.54,7.00),(x,REAR+.4,7.00),.11,.11,M["black"])
    beam(f"valley_{i}_downspout",(x,FRONT-.21,7.02),(x,FRONT-.21,.35),.09,.09,M["black"])

# A short strip of public realm supplies grade and scale without masking the model.
cube("front_lawn",0,FRONT-1.83,.025,WIDTH+1.3,3.9,.05,M["grass"])
cube("street_sidewalk",0,FRONT-3.66,.045,WIDTH+2.0,1.0,.09,M["concrete"])
for i in range(4):
    cx=-WIDTH/2+i*UNIT+1.0
    cube(f"unit{i+1}_front_walk",cx,FRONT-2.44,.07,1.55,2.08,.14,M["concrete"])

model=OUT/"reference-fourplex-v1.glb"
# Group same-material parts into a small number of draw calls without changing
# the authored opening, contact or circulation geometry.
parts={}
for obj in list(bpy.data.objects):
    if obj.type=="MESH":
        for key in TEXTURE_ROLES:
            if obj.active_material==M[key]:map_world_uv(obj,key)
        parts.setdefault(obj.active_material.name,[]).append(obj)
for material_name, group in parts.items():
    bpy.ops.object.select_all(action="DESELECT")
    for obj in group:obj.select_set(True)
    bpy.context.view_layer.objects.active=group[0]
    bpy.ops.object.join()
    group[0].name="RLASM_"+material_name[:45]
bpy.ops.object.select_all(action="DESELECT")
for obj in bpy.data.objects:obj.select_set(obj.type=="MESH")
bpy.context.view_layer.objects.active=next(o for o in bpy.data.objects if o.type=="MESH")
bpy.ops.export_scene.gltf(filepath=str(model),export_format="GLB",use_selection=True,export_yup=True,export_apply=True)
print(f"EXPORTED {model} {model.stat().st_size} bytes")

# Render neutral proof views; preview lamps and pavement are already authored.
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.samples=20 if config.pilot else 24
scene.render.resolution_x=1200
scene.render.resolution_y=850
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.world.use_nodes=True
scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value=(.78,.82,.88,1)
scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value=.75

def area_light(name, location, power, size):
    data=bpy.data.lights.new(name,"AREA");data.energy=power;data.shape="DISK";data.size=size
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    obj.location=location;obj.rotation_euler=(Vector((0,0,3))-obj.location).to_track_quat("-Z","Y").to_euler()

area_light("Neutral broad key",(-13,-20,19),4200,14)
area_light("Soft right fill",(14,-9,16),1900,11)

def camera(name, loc, target, ortho):
    data=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    obj.location=loc;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    data.type="ORTHO";data.ortho_scale=ortho;scene.camera=obj
    scene.render.filepath=str(OUT/"renders"/(name+".png"));(OUT/"renders").mkdir(exist_ok=True)
    bpy.ops.render.render(write_still=True)

camera("front_corner",(-23,-24,14),(0,-.6,4.1),29)
if not config.pilot:
    camera("front",(0,-27,4.5),(0,-.7,4.5),27)
    camera("aerial",(-22,-21,28),(0,-.3,4.0),30)
    camera("left_side",(-27,-1,8),(0,0,4.4),18)
    camera("right_side",(27,-1,8),(0,0,4.4),18)
    camera("rear",(0,27,4.5),(0,0,4.5),27)
    camera("rear_side",(22,21,16),(0,0,4.1),30)
    camera("facade_close",(-8,-14,7),(-7,-5.1,4.2),13)
    camera("architecture_close",(-13,-14,12),(-8,-4.5,7.2),12)
    camera("glass_close",(-8,-9,5),(-7.8,-5.1,2.6),6)
    camera("roof_junction",(-4,-13,16),(-2.7,-5,7.6),12)
    camera("entry_circulation",(-10,-11,5),(-9.7,-5.8,1.8),8)

print("RENDERS_COMPLETE",OUT/"renders")
