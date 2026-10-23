"""Finite picker-locked CC0 wardrobe derivatives; Blender 5.2, external output.

Run --pilot first. --remaining is an explicit finite checkpoint after review.
Original downloads, existing GLBs, picker images and manifests are read-only.
The anatomy-derived upper garments inherit all original vertex weights; no
independent shoulder yokes or axis-guessed sleeve tubes are used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_characters as base
from wardrobe_rules import WARDROBES, PILOT_IDS, coverage

ROOT = Path('C:/dev-artifacts/CityPrompt/people-wardrobe-2026-10-23')
SOURCES = Path('C:/dev-artifacts/CityPrompt/people-video-pilot-2026-10-21/characters/sources')
PUBLIC = Path('C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public')
REPO = Path(__file__).resolve().parents[2]
DESIGNS = {d['id']: d for d in base.DESIGNS + json.loads(Path(__file__).with_name('community_designs.json').read_text())}
REFERENCES = {d['id']: d for d in json.loads((REPO / 'frontend/src/features/people/peopleAppearancePreviews.json').read_text())}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_weights(body, vertex):
    return {body.vertex_groups[g.group].name: g.weight for g in vertex.groups if g.weight > 0}


def torso_weights(v):
    anchors = [(.96, 'pelvis'), (1.07, 'spine_01'), (1.22, 'spine_02'), (1.39, 'spine_03')]
    for (lo, low), (hi, high) in zip(anchors, anchors[1:]):
        if v[2] < hi:
            t = max(0., min(1., (v[2] - lo) / (hi - lo)))
            return {low: 1 - t, high: t}
    return {'spine_03': 1.}


def soft_box(name, center, size, mat, rig, bone='spine_03', bevel=.018):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.data.materials.append(mat)
    group = obj.vertex_groups.new(name=bone)
    group.add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
    modifier = obj.modifiers.new('Rounded_cloth_edges', 'BEVEL')
    modifier.width = bevel
    modifier.segments = 3
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.modifiers.new('Adult_humanoid_skin', 'ARMATURE').object = rig
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def ribbon(name, centers, width, mat, rig, weight_fn=torso_weights):
    """Skinned fabric strip following front/back contours in rest coordinates."""
    verts, faces, weights = [], [], []
    for p in centers:
        for dx in [-width / 2, width / 2]:
            v = (p[0] + dx, p[1], p[2])
            verts.append(v)
            weights.append(weight_fn(v))
    for i in range(len(centers) - 1):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    return base.weighted_mesh(name, verts, faces, weights, rig, [mat])


def cloth_pattern(obj, wardrobe):
    """Embedded authored fabric texture; no unsupported procedural material."""
    if not (wardrobe.get('stripes') or wardrobe.get('plaid')):
        return
    image = bpy.data.images.new('Broad_rugby_stripes' if wardrobe.get('stripes') else 'Ochre_navy_woven_plaid', width=128, height=128)
    pixels = []
    for y in range(128):
        for x in range(128):
            if wardrobe.get('stripes'):
                col = '#e7dfcb' if y % 64 >= 32 else wardrobe['top']
            else:
                cross = min(x % 64, y % 64)
                col = '#293a49' if cross < 12 else '#b99a5e' if cross < 15 else wardrobe['top']
                if x % 64 < 4 and y % 64 < 4:
                    col = '#25313e'
            pixels.extend(wardrobe_base_color(col))
    image.pixels = pixels
    image.pack()
    mat = obj.data.materials[0].copy()
    mat.name = image.name + '_cloth'
    node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    node.image = image
    node.interpolation = 'Linear'
    mat.node_tree.links.new(node.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    obj.data.materials[0] = mat
    uv = obj.data.uv_layers.new(name='Authored_fabric_UV')
    for poly in obj.data.polygons:
        for loop in poly.loop_indices:
            p = obj.data.vertices[obj.data.loops[loop].vertex_index].co
            t = max(0., min(1., (abs(p.x) - .22) / .17))
            t = t * t * (3 - 2 * t)
            axial = p.z * (1 - t) + (1.48 - (abs(p.x) - .22)) * t
            u = p.x * (1 - t) + p.y * t
            uv.data[loop].uv = (u * 4, axial * (2.8 if wardrobe.get('stripes') else 4.))


def wardrobe_base_color(value):
    # Generated PNG pixels are sRGB values; material constants use linear RGB.
    return tuple(int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)) + (1,)


def cloth_from_anatomy(body, rig, wardrobe, mats):
    """Copy only covered source triangles, preserving shoulder topology/weights.

    Source anatomy stays present under all cloth. Matching underlay materials
    prevent tiny motion-dependent penetration exposing skin or open cavities.
    """
    neck = rig.data.bones['neck_01'].head_local.z
    shoulder = abs(rig.data.bones['upperarm_l'].head_local.x)
    wrist = abs(rig.data.bones['lowerarm_l'].tail_local.x)
    hem_level = 1.055 if wardrobe.get('cropped') else .94 if wardrobe.get('blazer') or wardrobe.get('opening') else .985
    # The CC0 base is explicitly a superhero. Reduce only the radial bulk of
    # its deltoids/biceps to the ordinary adult silhouette in the picker;
    # skeleton landmarks, hand positions and face anatomy stay registered.
    for vertex in body.data.vertices:
        p = vertex.co
        if shoulder - .035 < abs(p.x) < wrist - .025 and p.z > 1.16:
            side = 'l' if p.x > 0 else 'r'
            arm = rig.data.bones['upperarm_' + side]
            influence = min(1., max(0., (abs(p.x) - shoulder + .035) / .09),
                            max(0., (wrist - .025 - abs(p.x)) / .08))
            radial = 1 - .20 * influence
            p.y = arm.head_local.y + (p.y - arm.head_local.y) * radial
            p.z = arm.head_local.z + (p.z - arm.head_local.z) * radial
    if not wardrobe.get('wrap') or wardrobe.get('socks') or wardrobe.get('opening'):
        # Split source neck triangles at the crew edge before assigning fabric.
        # Per-face painting without this split produced a serrated neckline.
        bm = bmesh.new()
        bm.from_mesh(body.data)
        heights = [.10, .20 if wardrobe.get('boot') else .005 if wardrobe.get('sandal') else .045 if wardrobe['lower'] == 'dress' else .09]
        if not wardrobe.get('wrap'):
            heights.append(neck + .02)
        if wardrobe.get('socks'):
            heights.extend([.11, .31])
        if wardrobe['lower'] == 'shorts':
            heights.append(.60)
        for height in heights:
            bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                                  plane_co=(0, 0, height), plane_no=(0, 0, 1),
                                  dist=.000001, clear_inner=False, clear_outer=False)
        if wardrobe.get('opening'):
            for x in [-.06, .06]:
                bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                                      plane_co=(x, 0, 0), plane_no=(1, 0, 0),
                                      dist=.000001, clear_inner=False, clear_outer=False)
        bm.to_mesh(body.data)
        bm.free()
    body.data.update()
    keys = ['skin', 'jacket', 'shirt', 'trousers', 'socks', 'shoes']
    for key in keys[1:]:
        body.data.materials.append(mats[key])
    selected = []
    for p in body.data.polygons:
        c = p.center
        key = coverage(wardrobe, c, neck, shoulder, wrist)
        if not wardrobe.get('wrap') and .99 < c.z < neck + .02 and abs(c.x) < .17:
            # The source neck is a continuous weighted cylinder. Use it as the
            # high crew fabric underlay instead of adding a floating chest bib.
            key = 'shirt' if wardrobe.get('opening') and c.y < 0 and abs(c.x) < .06 else 'jacket'
        if wardrobe['sleeve'] == 'none' and shoulder - .04 - abs(c.x) + max(0., 1.35 - c.z) * .9 < 0:
            key = 'skin'
        if key in ('jacket', 'shirt') and min(body.data.vertices[i].co.z for i in p.vertices) < .985:
            key = 'trousers'
        if key == 'socks' and max(body.data.vertices[i].co.z for i in p.vertices) > .31:
            key = 'skin'
        skirt_underlay = .53 if wardrobe['lower'] == 'skirt' else wardrobe.get('hem', .5) + .03
        if wardrobe['lower'] in ('dress', 'skirt') and skirt_underlay < c.z < 1.04:
            key = 'trousers'
        if c.z < (.20 if wardrobe.get('boot') else .005 if wardrobe.get('sandal') else .045 if wardrobe['lower'] == 'dress' else .09):
            key = 'shoes'
        p.material_index = keys.index(key)
        if key in ('jacket', 'shirt'):
            selected.append(p)
    arm_limit = {'none': shoulder + .005, 'short': shoulder + .17,
                 'threequarter': wrist - .13, 'long': wrist - .035}[wardrobe['sleeve']]
    def field(co, ws):
        x, y, z = co
        neckline = neck - .025 + max(0, abs(x) - (.055 if wardrobe.get('wrap') else .105)) * 2.2
        if wardrobe.get('wrap') and y < 0:
            neckline -= max(0, 1 - abs(x) / .115) * .17
        # Head and neck vertices never grow shoulder fabric.
        head = ws.get('Head', 0) + ws.get('neck_01', 0)
        arm_field = arm_limit - abs(x)
        if wardrobe['sleeve'] == 'none':
            arm_field = shoulder - .04 - abs(x) + max(0., 1.35 - z) * .9
        return min(z - hem_level, arm_field, neckline - z,
                   (.65 - head) if z > neck else 1.)
    verts, weights, faces, indices = [], [], [], []
    for poly in body.data.polygons:
        polygon = []
        for i in poly.vertices:
            v = body.data.vertices[i]
            ws = source_weights(body, v)
            if abs(v.co.x) < shoulder and v.co.z < 1.075:
                ws = {'pelvis': 1.}
            polygon.append((v.co.copy(), ws, field(v.co, ws)))
        clipped = []
        for current, following in zip(polygon, polygon[1:] + polygon[:1]):
            p, w, f = current
            q, wq, fq = following
            if f >= 0:
                clipped.append((p, w))
            if (f >= 0) != (fq >= 0):
                t = f / (f - fq)
                wi = {k: w.get(k, 0) * (1 - t) + wq.get(k, 0) * t for k in w.keys() | wq.keys()}
                clipped.append((p.lerp(q, t), wi))
        if len(clipped) < 3:
            continue
        start = len(verts)
        center = sum((v for v, _ in clipped), Vector()) / len(clipped)
        if wardrobe.get('opening') and center.y < 0 and abs(center.x) < .060001:
            continue
        verts.extend(tuple(v) for v, w in clipped)
        weights.extend(w for v, w in clipped)
        faces.append(tuple(range(start, start + len(clipped))))
        indices.append(0)
    obj = base.weighted_mesh('Anatomical_continuous_top', verts, faces, weights, rig,
                             [mats['jacket'], mats['shirt']], indices)
    # Smooth source muscles into fabric; clamp the cloth outside the original
    # surface by expanding around the anatomical torso/arm axes.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.000001)
    neckline = [v for v in bm.verts if v.is_boundary and v.co.z > 1.2 and abs(v.co.x) < shoulder - .04]
    for _ in range(4):
        updates = {}
        for v in neckline:
            adjacent = [e.other_vert(v).co for e in v.link_edges if e.is_boundary]
            if len(adjacent) == 2:
                updates[v] = v.co.lerp((adjacent[0] + adjacent[1]) * .5, .55)
        for v, co in updates.items():
            v.co = co
    interior = [v for v in bm.verts if not v.is_boundary and not
                (wardrobe.get('opening') and v.co.y < 0 and abs(abs(v.co.x) - .06) < .00001)]
    for _ in range(7):
        bmesh.ops.smooth_vert(bm, verts=interior, factor=.45, use_axis_x=True,
                             use_axis_y=True, use_axis_z=True)
    bm.to_mesh(obj.data)
    bm.free()
    for v in obj.data.vertices:
        p = v.co
        is_hem = abs(p.z - hem_level) < .00001
        is_cuff = abs(abs(p.x) - arm_limit) < .00001
        is_opening = wardrobe.get('opening') and p.y < 0 and abs(abs(p.x) - .06) < .00001
        if abs(p.x) < shoulder:
            # Project torso fabric onto smooth elliptical tailoring sections.
            # Copying skin normals alone embossed the superhero's abdomen and
            # chest through the garment; fabric must have its own silhouette.
            rx = .206 + max(0., min(1., (p.z - 1.10) / .24)) * .027
            ry = .158 + max(0., min(1., (p.z - 1.10) / .24)) * .014
            a = math.atan2((p.y - .025) / ry, p.x / rx)
            target = Vector((rx * math.cos(a), .025 + ry * math.sin(a), p.z))
            blend = max(0., min(1., (1.43 - p.z) / .095))
            p.x += (target.x - p.x) * blend
            p.y += (target.y - p.y) * blend
        else:
            arm = rig.data.bones['upperarm_l' if p.x > 0 else 'upperarm_r']
            p.y = arm.head_local.y + (p.y - arm.head_local.y) * 1.14
            p.z = arm.head_local.z + (p.z - arm.head_local.z) * 1.14
        # Body-derived garment edges retain the source anatomy's alignment.
        p += v.normal * .007
        if is_hem:
            p.z = hem_level
        if is_cuff:
            p.x = math.copysign(arm_limit, p.x)
        if is_opening:
            p.x = math.copysign(.065, p.x)
            p.y = .025 - ry * math.sqrt(max(0, 1 - (.065 / rx) ** 2))
    obj['construction'] = 'Source anatomy topology and normalized source weights; continuous shoulders'
    obj['source_skin_preserved'] = True
    cloth_pattern(obj, wardrobe)
    if wardrobe.get('opening'):
        verts, faces, ws = [], [], []
        for z in [min(hem_level, .985), 1.08, 1.22, 1.36, neck - .005]:
            half_width = .066 if z < 1.4 else .052
            ry = .158 + max(0., min(1., (z - 1.10) / .24)) * .014
            for x in [-half_width, 0, half_width]:
                y = .025 - ry * math.sqrt(max(0., 1 - (x / .23) ** 2)) + .009
                v = (x, y, z)
                verts.append(v)
                ws.append(torso_weights(v))
        for row in range(4):
            for column in range(2):
                a = row * 3 + column
                faces.append((a, a + 1, a + 4, a + 3))
        base.weighted_mesh('Continuous_fitted_undershirt_front', verts, faces, ws, rig, [mats['shirt']])
    # Keep the complete source anatomy, but contain the covered underlay inside
    # actual fabric. Patterned cloth made same-colour legacy penetrations clear.
    for v in body.data.vertices:
        p = v.co
        f = field(p, source_weights(body, v))
        if f > .003:
            t = min(1., f / .025)
            if abs(p.x) < shoulder + .02:
                p.x *= 1 - .12 * t
                p.y = .025 + (p.y - .025) * (1 - .16 * t)
            else:
                side = 'l' if p.x > 0 else 'r'
                arm = rig.data.bones['upperarm_' + side]
                p.y = arm.head_local.y + (p.y - arm.head_local.y) * (1 - .23 * t)
                p.z = arm.head_local.z + (p.z - arm.head_local.z) * (1 - .23 * t)
        covered_leg = wardrobe['lower'] == 'trousers' and .11 < p.z < .88 or wardrobe['lower'] == 'shorts' and .61 < p.z < .88
        if covered_leg:
            tx = rig.data.bones['thigh_l' if p.x > 0 else 'thigh_r'].head_local.x
            p.x = tx + (p.x - tx) * .84
            p.y = .025 + (p.y - .025) * .75
    return obj


def make_skirt(rig, wardrobe, mats):
    """Continuous wrap overlap with thigh-following hem and no trouser panel."""
    hem = wardrobe.get('hem', .5)
    rings = [(hem, .31, .24), ((hem + .98) / 2, .285, .22), (.91, .255, .195),
             (1.025, .205, .163)]
    if wardrobe['lower'] == 'skirt':
        rings.insert(1, (.52, .298, .231))
    def weights(v):
        influence = min(.68, max(0, (1.02 - v[2]) / (1.02 - hem)) * .68)
        blend = max(0, min(1, .5 + v[0] / .17))
        return {'pelvis': 1 - influence, 'thigh_l': influence * blend,
                'thigh_r': influence * (1 - blend)}
    obj = base.ring_mesh('Continuous_wrap_skirt', rings, weights, rig, [mats['trousers']],
                         center=(0, .025), segments=48)
    if wardrobe['lower'] == 'skirt':
        # Genuine front walking slit below the knees. Legs remain complete skin
        # beneath it; no painted trouser panel substitutes for the skirt.
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        opening = [f for f in bm.faces if f.calc_center_median().z < .52 and
                   f.calc_center_median().y < -.12 and abs(f.calc_center_median().x) < .055]
        bmesh.ops.delete(bm, geom=opening, context='FACES')
        bm.to_mesh(obj.data)
        bm.free()
        return obj
    # Separate overlapping front panel: seam remains legible without any gap.
    verts, faces, ws = [], [], []
    for row, (z, rx, ry) in enumerate(rings):
        for i in range(15):
            a = -math.pi * .86 + math.pi * .70 * i / 14
            v = (rx * math.cos(a), .025 + (ry + .008) * math.sin(a), z + (.025 * i / 14 if row == 0 else 0))
            verts.append(v)
            ws.append(weights(v))
    for row in range(len(rings) - 1):
        for i in range(14):
            a = row * 15 + i
            faces.append((a, a + 1, a + 16, a + 15))
    base.weighted_mesh('Overlapping_wrap_panel', verts, faces, ws, rig, [mats['trousers']])
    return obj


def make_legs(rig, wardrobe, mats):
    for side in ['l', 'r']:
        tx = rig.data.bones['thigh_' + side].head_local.x
        width = wardrobe.get('leg_width', 1.)
        def weights(v):
            t = max(0., min(1., (v[2] - .47) / .16))
            return {'thigh_' + side: t, 'calf_' + side: 1 - t}
        if wardrobe['lower'] == 'shorts':
            rings = [(.60, .090, .113), (.72, .103, .127), (.91, .103, .137)]
        else:
            rings = [(.11, .062 * width, .073 * width), (.29, .065 * width, .079 * width),
                     (.51, .080 * width, .09 * width), (.70, .103, .12), (.93, .108, .14)]
        if wardrobe['lower'] in ('trousers', 'shorts'):
            base.ring_mesh('Tailored_' + wardrobe['lower'] + '_' + side, rings, weights, rig,
                           [mats['trousers']], center=(tx, .025), segments=24)
        if wardrobe.get('socks'):
            base.ring_mesh('White_crew_sock_' + side, [(.09, .052, .063), (.20, .059, .067), (.31, .064, .075)],
                           lambda v: {'calf_' + side: 1}, rig, [mats['socks']], center=(tx, .065), segments=24)
        foot = rig.data.bones['foot_' + side]
        flat = wardrobe['lower'] == 'dress' and not wardrobe.get('boot')
        if wardrobe.get('sandal'):
            rings = [(-.009, .059, .149), (.006, .064, .153), (.015, .062, .151)]
        elif flat:
            rings = [(-.009, .059, .149), (.006, .064, .153), (.035, .060, .146), (.06, .045, .11)]
        elif wardrobe.get('boot') or wardrobe.get('hightop'):
            rings = [(-.009, .062, .151), (.02, .067, .155), (.065, .064, .14), (.13, .05, .085), (.21, .052, .071)]
        else:
            rings = [(-.009, .062, .151), (.012, .069, .159), (.045, .068, .153), (.085, .056, .13), (.112, .042, .072)]
        shoe = base.ring_mesh('Low_top_sneaker_' + side, rings, lambda v: {'foot_' + side: 1}, rig,
                              [mats['shoes']], center=(foot.head_local.x, -.055), segments=28)
        bm = bmesh.new()
        bm.from_mesh(shoe.data)
        bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary])
        bm.to_mesh(shoe.data)
        bm.free()
        shoe['footwear_style'] = 'flat' if flat else 'sandal' if wardrobe.get('sandal') else 'ankle_boot' if wardrobe.get('boot') else 'loafer' if wardrobe['shoe'].startswith('#54') else 'sneaker'
        if wardrobe.get('sandal'):
            anatomy = next(o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name.lower().startswith('superhero'))
            for y in [-.135, -.045]:
                source = [v.co.z for v in anatomy.data.vertices if abs(v.co.x - foot.head_local.x) < .045 and abs(v.co.y - y) < .035 and v.co.z < .16]
                top = max(source, default=.05) + .004
                verts = []
                for x in [-.055, -.03, 0, .03, .055]:
                    for dy in [-.014, .014]:
                        verts.append((foot.head_local.x + x, y + dy, .018 + (top - .018) * math.cos(x / .055 * math.pi / 2)))
                base.weighted_mesh('Curved_tan_sandal_strap_' + side, verts,
                                   [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(4)],
                                   [{'foot_' + side: 1} for v in verts], rig, [mats['shoes']])
        if wardrobe.get('socks'):
            blue = base.material('Navy_retro_sneaker_panels', '#435b72')
            # Lateral bands follow the foot and preserve the closed sole mesh.
            for sign in [-1, 1]:
                soft_box('Blue_retro_panel_' + side, (foot.head_local.x + sign * .061, -.05, .055),
                         (.009, .12, .027), blue, rig, 'foot_' + side, .006)
    # Original weighted hip anatomy supplies the closed crotch/waist region.
    # An independent cylindrical hip tube made trousers look like two layers.


def accessories(rig, wardrobe, mats):
    extras = wardrobe.get('accessories', ())
    if 'belt' in extras:
        base.ring_mesh('Fabric_waist_belt', [(1.008, .178, .149), (1.045, .176, .147)],
                       lambda v: {'pelvis': 1}, rig, [mats['jacket']], center=(0, .025), segments=40)
        soft_box('Tied_fabric_belt_knot', (.11, -.13, 1.025), (.045, .038, .045), mats['jacket'], rig, 'pelvis', .01)
        ribbon('Hanging_belt_tie', [(.12, -.143, 1.03), (.14, -.167, .94), (.15, -.18, .84)], .025,
               mats['jacket'], rig, lambda v: {'pelvis': 1})
    for kind in extras:
        if kind.startswith('backpack'):
            mat = base.material('Canvas_backpack_' + kind, '#4b5a38' if 'olive' in kind else '#283448')
            soft_box('Canvas_backpack', (0, .225, 1.25), (.30, .18, .40), mat, rig, bevel=.045)
            soft_box('Backpack_front_pocket', (0, .332, 1.18), (.23, .055, .19), mat, rig, bevel=.025)
            for s in [-1, 1]:
                ribbon('Backpack_shoulder_strap', [(s * .13, -.132, 1.10), (s * .15, -.153, 1.32),
                                                  (s * .15, -.07, 1.49), (s * .14, .10, 1.50), (s * .13, .25, 1.36)], .038, mat, rig)
        elif kind.startswith('tote') or kind in ('shoulder_bag', 'crescent_bag', 'sling'):
            mat = base.material('Bag_' + kind, '#d6cfbb' if 'cream' in kind or kind == 'crescent_bag' else '#66704e' if 'olive' in kind else '#635142' if kind == 'shoulder_bag' else '#222c35')
            side = -.23
            if kind == 'sling':
                soft_box('Crossbody_chest_sling', (-.025, -.19, 1.22), (.19, .085, .22), mat, rig, bevel=.035)
                ribbon('Diagonal_crossbody_sling_strap', [(.17, -.07, 1.46), (.04, -.18, 1.30),
                                                       (-.09, -.18, 1.10), (-.18, -.12, 1.00)], .028, mat, rig)
                continue
            soft_box(kind, (side, .01, .91), (.18, .105, .24), mat, rig, 'pelvis', .03)
            ribbon('Bag_shoulder_strap', [(side, -.055, .94), (-.20, -.13, 1.20), (-.14, -.09, 1.46),
                                         (-.17, .14, 1.43), (side, .07, 1.)], .021, mat, rig)
        elif kind == 'laptop':
            mat = base.material('Closed_laptop', '#464e56', .4)
            soft_box('Closed_plain_laptop', (-.29, -.04, 1.08), (.024, .23, .31), mat, rig, 'pelvis', .008)
        elif kind == 'books':
            for k, col in enumerate(['#d1ba8a', '#486273']):
                mat = base.material('Notebook_cover', col)
                soft_box('Plain_notebook', (-.25, -.09 - k * .023, 1.03), (.15, .022, .23), mat, rig, 'pelvis', .004)
        elif kind in ('cap', 'beanie'):
            mat = base.material(kind + '_fabric', '#293c50' if kind == 'cap' else '#73745c')
            bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=(0, .015, 1.76))
            obj = bpy.context.object
            obj.name = kind
            obj.scale = (.115, .118, .105)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            obj.data.materials.append(mat)
            group = obj.vertex_groups.new(name='Head')
            group.add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
            obj.modifiers.new('Adult_humanoid_skin', 'ARMATURE').object = rig
            if kind == 'cap':
                soft_box('Baseball_cap_brim', (0, -.108, 1.745), (.20, .15, .012), mat, rig, 'Head', .015)


def wardrobe_shell(body, rig, design, mats, wardrobe=None):
    """Reusable for inclusive people: call at original unposed source anatomy."""
    wardrobe = dict(wardrobe or design.get('wardrobe') or WARDROBES[design['id']])
    mats['socks'] = base.material(design['id'] + '_white_crew_socks', '#e9e6db')
    cloth_from_anatomy(body, rig, wardrobe, mats)
    make_legs(rig, wardrobe, mats)
    if wardrobe['lower'] in ('dress', 'skirt'):
        make_skirt(rig, wardrobe, mats)
    accessories(rig, wardrobe, mats)
    if wardrobe.get('collar'):
        neck = rig.data.bones['neck_01'].head_local
        base.ring_mesh('Shirt_folded_collar', [(neck.z - .055, .085, .08), (neck.z - .01, .060, .058)],
                       lambda v: {'neck_01': 1}, rig, [mats['shirt'] if wardrobe.get('stripes') else mats['jacket']], center=(0, neck.y), segments=24)
        for sign in [-1, 1]:
            verts = [(sign * .055, -.035, neck.z + .015), (sign * .115, -.10, neck.z - .025),
                     (sign * .08, -.135, neck.z - .085), (sign * .045, -.105, neck.z - .055)]
            base.weighted_mesh('Folded_front_polo_collar', verts, [(0, 1, 2, 3)],
                               [torso_weights(v) for v in verts], rig,
                               [mats['shirt'] if wardrobe.get('stripes') else mats['jacket']])
    if wardrobe.get('blazer'):
        for sign in [-1, 1]:
            verts = [(sign * .075, -.105, 1.46), (sign * .175, -.137, 1.37),
                     (sign * .08, -.157, 1.17), (sign * .045, -.153, 1.31)]
            base.weighted_mesh('Tailored_folded_blazer_lapel', verts, [(0, 1, 2, 3)],
                               [torso_weights(v) for v in verts], rig, [mats['jacket']])
        for x in [-.13, .13]:
            soft_box('Blazer_jetted_hip_pocket', (x, -.13, 1.01), (.105, .013, .012), mats['jacket'], rig, 'pelvis', .004)
    if wardrobe.get('piping'):
        piping = base.material('Track_jacket_cream_piping', '#d9d8c6')
        for sign in [-1, 1]:
            ribbon('Cream_track_jacket_piping', [(sign * .19, -.09, 1.43), (sign * .18, -.14, 1.26), (sign * .16, -.14, 1.06)], .009, piping, rig)
    if wardrobe.get('hoodie'):
        neck = rig.data.bones['neck_01'].head_local
        base.ring_mesh('Resting_pullover_hood', [(neck.z - .14, .112, .09), (neck.z - .02, .095, .088)],
                       lambda v: {'spine_03': 1}, rig, [mats['jacket']], center=(0, .09), segments=32)
        soft_box('Kangaroo_pouch', (0, -.145, 1.08), (.23, .024, .13), mats['jacket'], rig, 'spine_01', .025)
        for sign in [-1, 1]:
            ribbon('Cream_hood_drawstring', [(sign * .045, -.12, 1.46), (sign * .046, -.15, 1.32)], .008, mats['socks'], rig)
    if wardrobe.get('coat'):
        # Existing coat outfit has trousers beneath a separate open coat hem.
        base.coat_skirt(rig, mats['jacket'])
    return wardrobe


def build_one(root, identity, wardrobe_override=None, render=True):
    """Build from immutable CC0 downloads with stable IDs, 65 bones, Walk/Idle.

    Returns editable .blend and runtime GLB paths. Passing an independent design
    dict and wardrobe_override supports fixed-pose derivatives without changing
    this finite catalogue. The override supplies physical garment definitions.
    """
    root = Path(root)
    design = dict(DESIGNS[identity] if isinstance(identity, str) else identity)
    wardrobe = dict(wardrobe_override or WARDROBES[design['id']])
    design.update(jacket=wardrobe['top'], trousers=wardrobe['bottom'], shoes=wardrobe['shoe'],
                  shirt=wardrobe.get('undershirt', '#e8e0d0'), coat=False, wardrobe=wardrobe)
    root.mkdir(parents=True, exist_ok=True)
    (root / 'qa').mkdir(exist_ok=True)
    if not (root / 'sources').exists():
        raise RuntimeError('Create external sources junction to immutable source directory first')
    original_shell, original_render = base.clothing_shell, base.setup_render
    base.clothing_shell = wardrobe_shell
    def limited_render(*args):
        bpy.context.scene.render.threads_mode = 'FIXED'
        bpy.context.scene.render.threads = 8
        original_render(*args)
    base.setup_render = limited_render if render else lambda *_: None
    def annotate():
        parent = bpy.data.objects[design['id']]
        parent['wardrobe_version'] = 'picker-locked-v1'
        parent['wardrobe'] = json.dumps(wardrobe, sort_keys=True)
        parent['license'] = 'CC0-1.0 derivative'
        # Preserve catalogue-specific proportions and the original facial fit.
        parent.scale.x *= design.get('body_width', 1.)
        parent.scale.y *= design.get('body_depth', 1.)
        face_width = design.get('face_width', 1.)
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                for v in obj.data.vertices:
                    if v.co.z > 1.51:
                        v.co.x *= 1 + (face_width - 1) * min(1., (v.co.z - 1.51) / .10)
        bpy.context.view_layer.update()
    try:
        base.build(root, design, before_export=annotate)
    finally:
        base.clothing_shell, base.setup_render = original_shell, original_render
    reference = REFERENCES.get(design['id'])
    evidence = dict(id=design['id'], wardrobe=wardrobe,
                    generatorSha256=sha(__file__), rulesSha256=sha(Path(__file__).with_name('wardrobe_rules.py')),
                    glbSha256=sha(root / 'runtime' / (design['id'] + '.glb')),
                    source=str(SOURCES), sourceLicense='CC0-1.0',
                    topology='continuous original shoulder topology with original normalized vertex weights; complete source skin underlay',
                    rejectedLegacyPieces=['Hip_length_overshirt', 'Relaxed_sleeve', 'Closed_shoulder_yoke'])
    if reference:
        path = PUBLIC / reference['url'].lstrip('/')
        assert sha(path) == reference['sha256'], 'Picker reference changed; review the current image'
        evidence.update(reference=reference, referencePath=str(path))
    (root / (design['id'] + '.source.json')).write_text(json.dumps(evidence, indent=2))
    return root / (design['id'] + '.blend'), root / 'runtime' / (design['id'] + '.glb')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--only')
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--remaining', action='store_true')
    parser.add_argument('--no-render', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if sum([bool(args.only), args.pilot, args.remaining]) != 1:
        parser.error('Choose exactly one --only ID, --pilot or finite --remaining checkpoint')
    ids = [args.only] if args.only else PILOT_IDS if args.pilot else [i for i in WARDROBES if i not in PILOT_IDS]
    for identity in ids:
        build_one(args.root, identity, render=not args.no_render)
