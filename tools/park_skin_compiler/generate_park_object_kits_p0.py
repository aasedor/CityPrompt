"""Generate the P0 archetype-owned park object kits in Blender.

The LEGO grammar owns ground and court surfaces. These GLBs provide only the
depth-bearing, repeatable objects that make each archetype legible. Start with
the footbridge pilot, review it, then run the bounded seven-family batch.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from generate_shared_park_equipment import (  # noqa: E402
    asset_metrics, box, cylinder, export_glb, import_asset, join_by_material,
    look_at, material, reset_scene, torus, tube_between,
)

DEFAULT_SPEC = SCRIPT_DIR / "park_object_kits_p0_spec.json"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--preview-dir", type=Path, required=True)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--pilot", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(argv)


def mats():
    return {
        "steel": material("ROLE_metal_charcoal", (0.065, .082, .085, 1), metallic=.72, roughness=.31),
        "galv": material("ROLE_metal_galvanized", (.43, .47, .47, 1), metallic=.74, roughness=.36),
        "white": material("ROLE_marking_white", (.92, .92, .88, 1), roughness=.57),
        "yellow": material("ROLE_safety_yellow", (.93, .63, .04, 1), metallic=.12, roughness=.46),
        "red": material("ROLE_accent_red", (.70, .075, .045, 1), roughness=.52),
        "blue": material("ROLE_accent_blue", (.035, .19, .43, 1), roughness=.48),
        "green": material("ROLE_accent_green", (.08, .32, .17, 1), roughness=.64),
        "timber": material("ROLE_timber_oiled", (.39, .18, .055, 1), roughness=.74),
        "timber2": material("ROLE_timber_weathered", (.25, .13, .058, 1), roughness=.88),
        "concrete": material("ROLE_paver_concrete", (.47, .46, .42, 1), roughness=.94),
        "stone": material("ROLE_stone_weathered", (.35, .35, .32, 1), roughness=.98),
        "stone2": material("ROLE_stone_lichen", (.43, .45, .39, 1), roughness=.99),
        "rope": material("ROLE_rope_net", (.77, .74, .64, 1), roughness=.96),
        "sand": material("ROLE_safety_sand", (.67, .54, .34, 1), roughness=.98),
        "black": material("ROLE_dark_aperture", (.012, .015, .014, 1), roughness=.7),
        "water": material("ROLE_water_fitting", (.18, .43, .48, 1), metallic=.15, roughness=.22),
    }


def cone(name, radius1, radius2, depth, location, mat, *, vertices=16, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object; obj.name = name; obj.data.materials.append(mat)
    return obj


def rock(name, location, scale, mat, seed=0):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=location)
    obj = bpy.context.object; obj.name = name
    obj.scale = (scale[0], scale[1], scale[2]); obj.rotation_euler = (.11 * seed, .17 * seed, .43 * seed)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("Weathered edges", "BEVEL"); bevel.width = .025; bevel.segments = 2
    bpy.context.view_layer.objects.active = obj; bpy.ops.object.modifier_apply(modifier=bevel.name)
    for poly in obj.data.polygons: poly.use_smooth = True
    lowest = min((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)
    if lowest < 0:
        obj.location.z -= lowest
    return obj


def mesh_net(objects, name, width, height, z0, mat, spacing=.32, x0=0, y=0):
    for i in range(max(2, round(width / spacing) + 1)):
        x = x0 - width / 2 + width * i / max(1, round(width / spacing))
        objects.append(tube_between(f"{name} vertical {i}", (x, y, z0), (x, y, z0 + height), .009, mat, vertices=5))
    for i in range(max(2, round(height / spacing) + 1)):
        z = z0 + height * i / max(1, round(height / spacing))
        objects.append(tube_between(f"{name} horizontal {i}", (x0 - width / 2, y, z), (x0 + width / 2, y, z), .009, mat, vertices=5))


def build_disc_basket(m):
    o = [cylinder("Ground sleeve", .075, 1.68, (0, 0, .84), m["galv"], vertices=18),
         cylinder("Top band", .34, .09, (0, 0, 1.68), m["yellow"], vertices=28),
         cylinder("Lower basket hub", .10, .08, (0, 0, .78), m["yellow"], vertices=20),
         torus("Basket rim", .34, .025, (0, 0, .82), m["yellow"]),
         torus("Basket lower rim", .22, .022, (0, 0, .56), m["yellow"])]
    for i in range(18):
        a = math.tau * i / 18
        o.append(tube_between(f"Chain {i}", (.28*math.cos(a), .28*math.sin(a), 1.62), (.11*math.cos(a+.14), .11*math.sin(a+.14), .88), .008, m["galv"], vertices=5))
    for i in range(14):
        a = math.tau * i / 14
        o.append(tube_between(f"Basket spoke {i}", (.09*math.cos(a), .09*math.sin(a), .79), (.33*math.cos(a), .33*math.sin(a), .82), .012, m["yellow"], vertices=6))
    return o


def build_tee_sign(m):
    return [cylinder("Post", .055, 1.32, (0,0,.66), m["timber2"], vertices=12), box("Map panel", (.58,.055,.62), (0,-.025,1.04), m["timber"], rotation=(math.radians(-8),0,0), bevel=.025), box("Map inset", (.47,.012,.48), (0,-.058,1.04), m["green"], rotation=(math.radians(-8),0,0), bevel=.012)]


def build_bocce_score(m):
    o=[cylinder("Post A",.045,1.45,(-.38,0,.725),m["steel"],vertices=12),cylinder("Post B",.045,1.45,(.38,0,.725),m["steel"],vertices=12),box("Score board",(.95,.08,.55),(0,0,1.2),m["timber"],bevel=.035)]
    for row in range(2):
        for col in range(7):
            o.append(cylinder(f"Score peg {row}-{col}",.025,.10,(-.33+col*.11,-.075,1.30-row*.22),m["red" if row else "blue"],vertices=10,rotation=(math.pi/2,0,0)))
    return o


def build_bocce_rack(m):
    o=[box("Rack shelf",(1.65,.42,.12),(0,0,.68),m["timber"],bevel=.035),box("Lower brace",(1.4,.12,.12),(0,0,.26),m["timber2"],bevel=.025)]
    for x in (-.65,.65): o.append(box(f"Leg {x}",(.12,.34,.72),(x,0,.36),m["steel"],bevel=.02))
    for i in range(6):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=.065, location=(-.55+i*.22,0,.79)); b=bpy.context.object;b.name=f"Bocce ball {i}";b.data.materials.append(m["red" if i%2 else "blue"]);o.append(b)
    return o


def climbing_wall(m, *, natural=False, traverse=False):
    if natural:
        o=[rock("Main granite boulder",(0,0,2.05),(2.35,1.75,1.6),m["stone"],2),rock("Overhang",(.55,-.55,2.65),(1.55,1.2,1.1),m["stone2"],5)]
        return o
    width=6.6 if not traverse else 8.0; height=4.35 if not traverse else 2.10; depth=1.55 if not traverse else .65
    wall_lift = .08
    o=[box("Climbing shell",(width,depth,height),(0,0,height/2+wall_lift),m["concrete"],rotation=(math.radians(-5 if traverse else -9),0,0),bevel=.07),box("Kick plate",(width+.08,depth+.05,.32),(0,0,.16),m["steel"],bevel=.025)]
    for i in range(34 if not traverse else 28):
        x=-width*.43+(i%7)*width*.145; z=.42+(i//7)*(.70 if not traverse else .40); y=-depth/2-.055
        o.append(cone(f"Hold {i}",.11+(i%4)*.018,.055,.10,(x,y,z),m[["yellow","red","blue","green"][i%4]],vertices=9,rotation=(math.pi/2,0,i*.33)))
    return o


def build_windmill(m):
    o=[cone("Windmill body",1.05,.66,2.45,(0,0,1.225),m["timber"],vertices=12),box("Door",(.52,.05,.82),(0,-.91,.46),m["black"],bevel=.08),cone("Roof",1.28,0,.72,(0,0,2.78),m["red"],vertices=16)]
    hub=(0,-1.03,2.23);o.append(cylinder("Hub",.14,.18,hub,m["yellow"],vertices=18,rotation=(math.pi/2,0,0)))
    for a in (0,math.pi/2): o.append(box(f"Sail {a}",(3.2,.09,.16),(0,-1.14,2.23),m["white"],rotation=(0,a,0),bevel=.02))
    return o


def build_loop(m):
    o=[torus("Loop",.72,.15,(0,0,.88),m["yellow"],rotation=(math.pi/2,0,0)),box("Loop base",(1.75,.58,.16),(0,0,.08),m["concrete"],bevel=.04)]
    return o


def build_mini_bridge(m):
    o=[]
    for i in range(9):
        x=-1.6+i*.4;z=.20+.34*(1-(abs(x)/1.6)**1.7);o.append(box(f"Deck slat {i}",(.36,1.15,.10),(x,0,z),m["timber"],rotation=(0,-.16*x,0),bevel=.018))
    for side in (-1,1):
        for i in range(5):
            x=-1.55+i*.775; z=.72+.34*(1-(abs(x)/1.6)**1.7);o.append(cylinder(f"Rail post {side}-{i}",.035,.75,(x,side*.55,z-.25),m["steel"],vertices=8))
        o.append(tube_between(f"Rail {side}",(-1.55,side*.55,.76),(1.55,side*.55,.76),.035,m["steel"],vertices=8))
    return o


def build_cup_flag(m):
    return [cylinder("Cup",.08,.05,(0,0,.025),m["black"],vertices=20),cylinder("Flag pole",.012,.90,(0,0,.47),m["white"],vertices=8),box("Flag",(.36,.025,.22),(.18,0,.77),m["red"],bevel=.006)]


def build_volleyball_net(m):
    o=[cylinder("Post left",.065,2.55,(-4.5,0,1.275),m["blue"],vertices=16),cylinder("Post right",.065,2.55,(4.5,0,1.275),m["blue"],vertices=16),tube_between("Top tape",(-4.5,0,2.43),(4.5,0,2.43),.025,m["white"],vertices=8),tube_between("Bottom tape",(-4.5,0,1.43),(4.5,0,1.43),.018,m["white"],vertices=8)]
    mesh_net(o,"Competition net",8.9,1.0,1.43,m["rope"],spacing=.27)
    for x in (-4.5,4.5):
        o += [tube_between(f"Guy {x} A",(x,0,2.38),(x,-1.15,0),.012,m["galv"],vertices=6),tube_between(f"Guy {x} B",(x,0,2.38),(x,1.15,0),.012,m["galv"],vertices=6)]
    return o


def build_referee_stand(m):
    o=[box("Platform",(1.0,.78,.10),(0,0,2.12),m["galv"],bevel=.02),box("Seat",(.62,.56,.10),(0,.04,2.42),m["blue"],bevel=.05)]
    for x in (-.42,.42): o += [tube_between(f"Leg {x}",(x,0,0),(x,0,2.15),.035,m["galv"],vertices=10),tube_between(f"Rail {x}",(x,0,2.14),(x,0,2.65),.035,m["galv"],vertices=10)]
    for i in range(6): o.append(box(f"Step {i}",(.72,.24,.06),(0,-.35,.25+i*.28),m["galv"],bevel=.01))
    return o


def timber_deck(m, width, length, height=.34, rails=True):
    o=[]; slats=max(3,round(length/.38))
    for i in range(slats):
        x=-length/2+(i+.5)*length/slats;o.append(box(f"Deck slat {i}",(length/slats-.025,width,.14),(x,0,height),m["timber" if i%3 else "timber2"],bevel=.012))
    for x in (-length/2+.25,0,length/2-.25):
        for y in (-width*.42,width*.42):o.append(cylinder(f"Pile {x}-{y}",.075,height+.05,(x,y,(height+.05)/2),m["timber2"],vertices=10))
    if rails:
        for side in (-1,1):
            for i in range(max(3,round(length/2.0)+1)):
                x=-length/2+length*i/max(1,round(length/2.0));o.append(cylinder(f"Rail post {side}-{i}",.045,1.05,(x,side*width/2,height+.48),m["timber2"],vertices=10))
            o.append(tube_between(f"Handrail {side}",(-length/2,side*width/2,height+1.02),(length/2,side*width/2,height+1.02),.055,m["timber2"],vertices=10))
    return o


def build_boardwalk(m): return timber_deck(m,2.4,8.0,.34,True)
def build_observation(m): return timber_deck(m,5.8,5.8,.34,True)


def build_footbridge(m):
    o=[]; n=15
    for i in range(n):
        x=-4.2+(i+.5)*8.4/n; z=.42+.28*(1-(abs(x)/4.2)**2); o.append(box(f"Arched deck slat {i}",(8.4/n-.025,2.1,.13),(x,0,z),m["timber" if i%3 else "timber2"],rotation=(0,-.12*x/4.2,0),bevel=.012))
    for side in (-1,1):
        for i in range(7):
            x=-4.05+i*1.35;z=.92+.28*(1-(abs(x)/4.2)**2);o.append(cylinder(f"Bridge post {side}-{i}",.05,1.0,(x,side*1.05,z-.05),m["galv"],vertices=10))
        for i in range(6):
            x1=-4.05+i*1.35;x2=x1+1.35;z1=1.38+.28*(1-(abs(x1)/4.2)**2);z2=1.38+.28*(1-(abs(x2)/4.2)**2);o.append(tube_between(f"Bridge rail {side}-{i}",(x1,side*1.05,z1),(x2,side*1.05,z2),.045,m["galv"],vertices=10))
    return o


def build_weir(m):
    o=[box("Weir body",(5.2,1.15,.72),(0,0,.36),m["concrete"],bevel=.04),box("Low-flow notch",(1.15,1.28,.45),(0,0,.82),m["water"],bevel=.02)]
    for x in (-2.25,2.25):o.append(box(f"Wing wall {x}",(.55,2.6,1.05),(x,.4,.525),m["concrete"],rotation=(0,0,.16*(-1 if x<0 else 1)),bevel=.04))
    return o


def build_inlet(m):
    o=[box("Headwall",(3.6,.55,1.15),(0,0,.575),m["concrete"],bevel=.05),box("Apron",(3.0,2.2,.18),(0,-1.05,.09),m["concrete"],bevel=.035),cylinder("Pipe",.44,.68,(0,-.31,.55),m["black"],vertices=24,rotation=(math.pi/2,0,0))]
    for x in (-1.45,1.45):o.append(box(f"Wing {x}",(.42,1.65,.82),(x,-.58,.41),m["concrete"],rotation=(0,0,.15*(-1 if x<0 else 1)),bevel=.035))
    return o


def build_outlet(m):
    o=[box("Control vault",(1.45,1.25,1.35),(0,0,.675),m["concrete"],bevel=.06),box("Access hatch",(1.0,.92,.10),(0,0,1.40),m["galv"],bevel=.025),cylinder("Outlet pipe",.34,.72,(0,-.72,.42),m["black"],vertices=20,rotation=(math.pi/2,0,0))]
    for x in (-.58,.58):o.append(cylinder(f"Guard rail post {x}",.035,.55,(x,0,1.58),m["galv"],vertices=10))
    o.append(tube_between("Guard rail",(-.58,0,1.85),(.58,0,1.85),.035,m["galv"],vertices=10));return o


def build_riprap(m):
    o=[]
    for i in range(16):
        x=-1.8+(i%5)*.78+(i%2)*.12;y=-1.05+(i//5)*.65;sz=.28+(i%4)*.045;o.append(rock(f"Riprap {i}",(x,y,sz*.82),(sz*1.4,sz,sz*.72),m["stone2" if i%3 else "stone"],i))
    return o


def build_gate(m):
    o=[cylinder("Gate post left",.07,1.35,(-1.65,0,.675),m["galv"],vertices=12),cylinder("Gate post right",.07,1.35,(1.65,0,.675),m["galv"],vertices=12),box("Gate top",(3.15,.07,.07),(0,0,1.28),m["galv"],bevel=.01),box("Gate bottom",(3.15,.07,.07),(0,0,.12),m["galv"],bevel=.01)]
    for i in range(7):o.append(cylinder(f"Gate picket {i}",.025,1.12,(-1.4+i*.47,0,.70),m["galv"],vertices=8))
    return o


def build_stage(m):
    o=[box("Stage deck",(9.0,5.0,.42),(0,0,.35),m["timber"],bevel=.05),box("Stage fascia",(9.15,.18,.72),(0,-2.48,.36),m["timber2"],bevel=.025),box("Back screen",(8.6,.28,2.1),(0,2.28,1.50),m["timber2"],bevel=.04)]
    for i in range(10):o.append(box(f"Deck board {i}",(.055,4.65,.035),(-4.05+i*.9,0,.575),m["timber2"],bevel=.005))
    return o


def build_seat_wall(m):
    return [box("Seat wall",(4.0,.72,.43),(0,0,.215),m["concrete"],bevel=.08),box("Timber seat cap",(4.05,.76,.09),(0,0,.475),m["timber"],bevel=.035)]


def build_aisle_rail(m):
    return [cylinder("Rail post A",.035,1.0,(-1.35,0,.50),m["galv"],vertices=10),cylinder("Rail post B",.035,1.0,(1.35,0,.50),m["galv"],vertices=10),tube_between("Handrail",(-1.35,0,1.0),(1.35,0,1.0),.045,m["galv"],vertices=10)]


def build_bollard(m):
    return [cylinder("Bollard body",.075,.88,(0,0,.44),m["steel"],vertices=18),cylinder("Light diffuser",.10,.18,(0,0,.80),m["white"],vertices=20),cone("Bollard cap",.12,.08,.10,(0,0,.92),m["steel"],vertices=20)]


BUILDERS = {
    "disc_golf_basket": build_disc_basket, "disc_golf_tee_sign": build_tee_sign,
    "bocce_score_stand": build_bocce_score, "bocce_ball_rack": build_bocce_rack,
    "climbing_competition_wall": lambda m: climbing_wall(m),
    "climbing_natural_boulder": lambda m: climbing_wall(m, natural=True),
    "climbing_traverse_wall": lambda m: climbing_wall(m, traverse=True),
    "mini_golf_windmill": build_windmill, "mini_golf_loop": build_loop,
    "mini_golf_bridge": build_mini_bridge, "mini_golf_cup_flag": build_cup_flag,
    "beach_volleyball_net": build_volleyball_net, "beach_volleyball_referee_stand": build_referee_stand,
    "wetland_boardwalk_span": build_boardwalk, "wetland_observation_deck": build_observation,
    "wetland_footbridge": build_footbridge, "stormwater_check_weir": build_weir,
    "stormwater_inlet_headwall": build_inlet, "stormwater_outlet_control": build_outlet,
    "riprap_cluster": build_riprap, "maintenance_gate": build_gate,
    "amphitheater_stage": build_stage, "amphitheater_seat_wall": build_seat_wall,
    "amphitheater_aisle_rail": build_aisle_rail, "amphitheater_bollard_light": build_bollard,
}


def setup_render(preview_dir, paths, report, pilot=False):
    reset_scene(); m=mats(); box("Review floor",(18,12,.08),(0,0,-.05),m["sand"],bevel=0)
    selected=[("wetland_footbridge",(0,0,0),0)] if pilot else []
    if not pilot:
        # One representative object from every family keeps the QA sheet legible.
        selected=[("disc_golf_basket",(-6,3,0),0),("bocce_score_stand",(-3,3,0),.2),("climbing_competition_wall",(1.5,2.8,0),-.15),("mini_golf_windmill",(6,3,0),.2),("beach_volleyball_net",(-3,-2.4,0),0),("wetland_footbridge",(3,-2.7,0),-.12),("amphitheater_stage",(0,-7.2,0),0)]
    for asset_id,loc,yaw in selected: import_asset(paths[asset_id],asset_id,loc,yaw)
    for loc,energy,size in [((-8,-9,14),1450,7),((10,6,11),900,6)]:
        bpy.ops.object.light_add(type="AREA",location=loc);light=bpy.context.object;light.data.energy=energy;light.data.shape="DISK";light.data.size=size;look_at(light,(0,0,1.4))
    bpy.ops.object.light_add(type="SUN",location=(0,0,10));bpy.context.object.rotation_euler=(math.radians(25),math.radians(-20),math.radians(35));bpy.context.object.data.energy=2.2
    bpy.ops.object.camera_add(location=(15,-19,13));camera=bpy.context.object;camera.data.lens=56;look_at(camera,(0,0,1.2));scene=bpy.context.scene;scene.camera=camera;scene.render.engine="BLENDER_EEVEE";scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG";scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get("Background");bg.inputs["Color"].default_value=(.045,.058,.065,1);bg.inputs["Strength"].default_value=.45
    preview_dir.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(preview_dir/("pilot-wetland-footbridge.png" if pilot else "park-object-kits-p0-catalogue.png"));bpy.ops.render.render(write_still=True)
    camera.location=(-16,-18,9);look_at(camera,(0,0,1.25));scene.render.filepath=str(preview_dir/("pilot-wetland-footbridge-reverse.png" if pilot else "park-object-kits-p0-reverse.png"));bpy.ops.render.render(write_still=True)


def render_family_previews(preview_dir, spec, paths):
    for family in spec["families"]:
        asset_ids = [asset["id"] for asset in family["assets"]]
        columns = min(4, len(asset_ids))
        rows = math.ceil(len(asset_ids) / columns)
        spacing_x = 10.0
        spacing_y = 9.0
        width = max(18.0, columns * spacing_x + 5.0)
        depth = max(14.0, rows * spacing_y + 5.0)
        reset_scene(); m = mats()
        box("Family review floor", (width, depth, .08), (0, 0, -.05), m["sand"], bevel=0)
        for index, asset_id in enumerate(asset_ids):
            column = index % columns
            row = index // columns
            x = (column - (columns - 1) / 2) * spacing_x
            y = ((rows - 1) / 2 - row) * spacing_y
            import_asset(paths[asset_id], asset_id, (x, y, 0), (index % 3 - 1) * .12)
        span = max(width, depth)
        for loc, energy, size in [((-span*.45,-span*.55,span*.72),1500,8),((span*.55,span*.35,span*.55),900,7)]:
            bpy.ops.object.light_add(type="AREA", location=loc); light=bpy.context.object; light.data.energy=energy; light.data.shape="DISK"; light.data.size=size; look_at(light,(0,0,1.2))
        bpy.ops.object.light_add(type="SUN",location=(0,0,10));bpy.context.object.rotation_euler=(math.radians(25),math.radians(-20),math.radians(35));bpy.context.object.data.energy=2.1
        bpy.ops.object.camera_add(location=(span*.68,-span*.88,span*.62));camera=bpy.context.object;camera.data.lens=58;look_at(camera,(0,0,1.25));scene=bpy.context.scene;scene.camera=camera;scene.render.engine="BLENDER_EEVEE";scene.render.resolution_x=1500;scene.render.resolution_y=950;scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG";scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get("Background");bg.inputs["Color"].default_value=(.045,.058,.065,1);bg.inputs["Strength"].default_value=.45
        scene.render.filepath=str(preview_dir/f"{family['id']}-objects.png");bpy.ops.render.render(write_still=True)


def main():
    args=parse_args();spec=json.loads(args.spec.resolve().read_text(encoding="utf-8"));defs={a["id"]:(f,a) for f in spec["families"] for a in f["assets"]};selected=["wetland_footbridge"] if args.pilot else list(BUILDERS);reset_scene();m=mats();paths={};report={"schemaVersion":1,"kitVersion":spec["kitVersion"],"assets":[]}
    for asset_id in selected:
        family,definition=defs[asset_id];authored=BUILDERS[asset_id](m);objects=join_by_material(authored,asset_id);dimensions,triangles=asset_metrics(objects)
        minimum = min(
            (obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box),
            key=lambda point: point.z,
        )
        if minimum.z < -.012:
            raise RuntimeError(f"{asset_id} extends below ground")
        path=args.output_root.resolve()/family["id"]/definition["filename"];export_glb(path,objects);paths[asset_id]=path;report["assets"].append({"id":asset_id,"family":family["id"],"filename":path.name,"dimensionsM":[round(dimensions.x,3),round(dimensions.y,3),round(dimensions.z,3)],"triangles":triangles,"bytes":path.stat().st_size})
        for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
    args.preview_dir.resolve().mkdir(parents=True,exist_ok=True);(args.preview_dir.resolve()/("pilot-report.json" if args.pilot else "kit-report.json")).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8");setup_render(args.preview_dir.resolve(),paths,report,args.pilot)
    if not args.pilot: render_family_previews(args.preview_dir.resolve(),spec,paths)
    print(json.dumps(report,indent=2))


if __name__ == "__main__": main()
