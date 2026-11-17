"""Pure-Python architectural-clay mesh kit. No Blender, no third-party packages.

Authoring is Z-up in metres: x is width, the street front faces -y, and grade is z = 0.
The GLB writer converts to glTF's Y-up frame exactly as the Blender exporter does,
(x, y, z) -> (x, z, -y), and writes one node, mesh and material per semantic role with
the same names and extras as the reviewed clay library (`CLAY_<ROLE>`), so the runtime
treats the result like every other architectural-clay delivery. Output is deterministic.
"""
from __future__ import annotations

import json
import math
import struct
from array import array

METHOD = 'RLASM v6.1 clay-first'
GENERATOR = 'City Prompt clay kit (pure Python)'


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(a):
    size = math.sqrt(dot(a, a))
    return (a[0] / size, a[1] / size, a[2] / size) if size > 1e-12 else (0.0, 0.0, 0.0)


def centroid(points):
    count = len(points)
    return (sum(p[0] for p in points) / count, sum(p[1] for p in points) / count, sum(p[2] for p in points) / count)


def newell(points):
    """Area-weighted normal of a planar ring; its direction follows the ring's winding."""
    nx = ny = nz = 0.0
    for a, b in zip(points, points[1:] + points[:1]):
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    return (nx, ny, nz)


def srgb_to_linear(hex_colour):
    out = []
    for k in (1, 3, 5):
        c = int(hex_colour[k:k + 2], 16) / 255
        out.append(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4)
    return out


def earclip(points2d):
    """Triangulate a simple polygon given as (u, v) pairs. Returns index triples, all
    wound anticlockwise. A corner is cut as an ear only when no reflex corner lies in
    it or on its edge, so the cut never crosses the outline, and a corner on a straight
    run is dropped without a triangle."""
    count = len(points2d)
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points2d, points2d[1:] + points2d[:1]))
    order = list(range(count)) if area > 0 else list(range(count - 1, -1, -1))
    tiny = 1e-12

    def turn(i, j, k):
        a, b, c = points2d[i], points2d[j], points2d[k]
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    out = []
    while len(order) > 3:
        size = len(order)
        reflex = [order[at] for at in range(size) if turn(order[at - 1], order[at], order[(at + 1) % size]) < -tiny]
        for at in range(size):
            i, j, k = order[at - 1], order[at], order[(at + 1) % size]
            bend = turn(i, j, k)
            if abs(bend) <= tiny:           # on a straight run: nothing to cut
                del order[at]
                break
            if bend < 0:
                continue
            corners = (points2d[i], points2d[j], points2d[k])
            if any(points2d[p] not in corners and turn(i, j, p) >= -tiny and turn(j, k, p) >= -tiny and turn(k, i, p) >= -tiny for p in reflex):
                continue
            out.append((i, j, k))
            del order[at]
            break
        else:
            raise ValueError('outline is not a simple polygon')
    if abs(turn(*order)) > tiny:
        out.append(tuple(order))
    return out


def inset_polygon(points2d, distance):
    """Offset a simple polygon inward by `distance`, mitring each corner."""
    count = len(points2d)
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points2d, points2d[1:] + points2d[:1]))
    sign = 1.0 if area > 0 else -1.0
    lines = []
    for a, b in zip(points2d, points2d[1:] + points2d[:1]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        size = math.hypot(dx, dy)
        nx, ny = -dy / size * sign, dx / size * sign  # inward normal
        lines.append(((a[0] + nx * distance, a[1] + ny * distance), (dx, dy)))
    out = []
    for k in range(count):
        (p, d), (q, e) = lines[k - 1], lines[k]
        det = d[0] * e[1] - d[1] * e[0]
        if abs(det) < 1e-12:
            out.append(q)
            continue
        t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / det
        out.append((p[0] + d[0] * t, p[1] + d[1] * t))
    return [(round(x, 6), round(y, 6)) for x, y in out]


def arc(cx, cy, radius, start_deg, end_deg, steps):
    """Points along an arc in a 2D plane, inclusive of both ends."""
    out = []
    for k in range(steps + 1):
        angle = math.radians(start_deg + (end_deg - start_deg) * k / steps)
        out.append((round(cx + radius * math.cos(angle), 6), round(cy + radius * math.sin(angle), 6)))   # rounded: same bytes on every platform
    return out


class Clay:
    """Triangle soup per semantic role, with outward flat normals."""

    def __init__(self):
        self.triangles = {}
        self.components = {}

    def _count(self, role):
        self.components[role] = self.components.get(role, 0) + 1

    def _emit(self, role, a, b, c, normals=None):
        """Store one triangle. `normals` gives a normal per corner for a rounded surface;
        without it the triangle is flat."""
        normal = cross(sub(b, a), sub(c, a))
        if dot(normal, normal) < 1e-16:
            return
        self.triangles.setdefault(role, []).append((a, b, c) if normals is None else (a, b, c, *normals))

    def tri(self, role, a, b, c, facing=None):
        if facing is not None and dot(cross(sub(b, a), sub(c, a)), facing) < 0:
            b, c = c, b
        self._emit(role, a, b, c)

    def quad(self, role, a, b, c, d, facing=None):
        """A planar quad a-b-c-d. `facing` is any vector on the visible side."""
        self._count(role)
        self.tri(role, a, b, c, facing)
        self.tri(role, a, c, d, facing)

    def polygon(self, role, ring, facing):
        """A planar simple polygon, triangulated by ear clipping."""
        self._count(role)
        for a, b, c in self._cap(ring):
            self.tri(role, a, b, c, facing)

    @staticmethod
    def _cap(ring):
        normal = unit(newell(ring))
        axis = (1.0, 0.0, 0.0) if abs(normal[0]) < .9 else (0.0, 1.0, 0.0)
        u = unit(cross(normal, axis))
        v = cross(normal, u)
        flat = [(dot(p, u), dot(p, v)) for p in ring]
        return [(ring[i], ring[j], ring[k]) for i, j, k in earclip(flat)]

    def box(self, role, x0, x1, y0, y1, z0, z1):
        x0, x1, y0, y1, z0, z1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)
        self._count(role)
        p = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
        for i, j, k, m in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
            self._emit(role, p[i], p[j], p[k])
            self._emit(role, p[i], p[k], p[m])

    def loft(self, role, rings, loop=False, caps=(True, True), smooth=None):
        """Skin consecutive closed rings of equal length; faces are made to point outward.

        `loop` joins the last ring back to the first (a closed band, no caps). Otherwise
        `caps` says whether to close the first and last ring with planar faces. `smooth`
        is a crease angle in degrees: where two neighbouring faces of the section meet
        at less than that, they share a normal, so an arc shades as a curve.
        """
        self._count(role)
        count = len(rings[0])
        sides, quads = [], []
        for a, b in list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if loop else []):
            for i in range(count):
                j = (i + 1) % count
                sides.append((a[i], a[j], b[j]))
                sides.append((a[i], b[j], b[i]))
                quads.append((a, b, i, j))
        ends = []
        if not loop:
            for ring, other in ((rings[0], rings[1]), (rings[-1], rings[-2])):
                away = sub(centroid(ring), centroid(other))
                faces = []
                for a, b, c in self._cap(ring):
                    faces.append((a, c, b) if dot(cross(sub(b, a), sub(c, a)), away) < 0 else (a, b, c))
                ends.append(faces)
        # Signed volume about the loft's own centre. The caps already face outward, and seen
        # from the centre they always count as positive, so the sum is positive exactly when
        # the side faces point outward too. Measured from a distant origin it is not.
        middle = centroid([p for ring in rings for p in ring])
        volume = sum(dot(sub(a, middle), cross(sub(b, middle), sub(c, middle)))
                     for a, b, c in sides + [face for faces in ends for face in faces])
        flip = -1.0 if volume < 0 else 1.0
        if smooth is None:
            for a, b, c in sides:
                self._emit(role, *((a, c, b) if volume < 0 else (a, b, c)))
        else:
            limit = math.cos(math.radians(smooth))
            flat = [mul(unit(newell([a[i], a[j], b[j], b[i]])), flip) for a, b, i, j in quads]
            for at, (a, b, i, j) in enumerate(quads):
                base = at - i                                  # first quad of this ring pair
                before, after = flat[base + (i - 1) % count], flat[base + j]
                here = flat[at]
                ni = unit(add(here, before)) if dot(here, before) > limit else here
                nj = unit(add(here, after)) if dot(here, after) > limit else here
                first, second = ((a[i], b[j], a[j]), (ni, nj, nj)), ((a[i], b[i], b[j]), (ni, ni, nj))
                if volume >= 0:
                    first, second = ((a[i], a[j], b[j]), (ni, nj, nj)), ((a[i], b[j], b[i]), (ni, nj, ni))
                for corners, normals in (first, second):
                    self._emit(role, *corners, normals)
        for faces, wanted in zip(ends, caps):
            if wanted:
                for face in faces:
                    self._emit(role, *face)

    def prism(self, role, outline, z0, z1, caps=(True, True)):
        """Extrude an (x, y) outline vertically."""
        self.loft(role, [[(x, y, z0) for x, y in outline], [(x, y, z1) for x, y in outline]], caps=caps)

    def cylinder(self, role, cx, cy, z0, z1, radius, steps=16):
        self.prism(role, arc(cx, cy, radius, 0, 360, steps)[:-1], z0, z1)

    # ---- reporting -------------------------------------------------------
    def bounds(self):
        lo, hi = [math.inf] * 3, [-math.inf] * 3
        for faces in self.triangles.values():
            for face in faces:
                for p in face[:3]:
                    for k in range(3):
                        lo[k] = min(lo[k], p[k])
                        hi[k] = max(hi[k], p[k])
        return lo, hi

    def triangle_counts(self):
        return {role: len(faces) for role, faces in self.triangles.items()}

    # ---- export ----------------------------------------------------------
    def glb(self, palette, identity):
        """Serialise as a GLB. `palette` maps role -> material settings, in node order."""
        nodes, meshes, materials, accessors, views, extensions = [], [], [], [], [], []
        blob = bytearray()

        def view(data, target):
            while len(blob) % 4:
                blob.append(0)
            views.append({'buffer': 0, 'byteOffset': len(blob), 'byteLength': len(data), 'target': target})
            blob.extend(data)
            return len(views) - 1

        for role, settings in palette.items():
            faces = self.triangles.get(role)
            if not faces:
                continue
            index, positions, normals, indices = {}, array('f'), array('f'), array('I')
            lo, hi = [math.inf] * 3, [-math.inf] * 3
            for face in faces:
                a, b, c = face[:3]
                n = unit(cross(sub(b, a), sub(c, a)))
                for p, n in zip((a, b, c), face[3:] or (n, n, n)):
                    normal = (n[0], n[2], -n[1])
                    q = (p[0], p[2], -p[1])
                    key = (round(q[0], 5), round(q[1], 5), round(q[2], 5), round(normal[0], 4), round(normal[1], 4), round(normal[2], 4))
                    at = index.get(key)
                    if at is None:
                        at = index[key] = len(index)
                        packed = struct.unpack('<3f', struct.pack('<3f', *q))
                        positions.extend(packed)
                        normals.extend(normal)
                        for k in range(3):
                            lo[k] = min(lo[k], packed[k])
                            hi[k] = max(hi[k], packed[k])
                    indices.append(at)
            first = len(accessors)
            accessors.append({'bufferView': view(positions.tobytes(), 34962), 'componentType': 5126, 'count': len(index),
                              'type': 'VEC3', 'min': lo, 'max': hi})
            accessors.append({'bufferView': view(normals.tobytes(), 34962), 'componentType': 5126, 'count': len(index), 'type': 'VEC3'})
            accessors.append({'bufferView': view(indices.tobytes(), 34963), 'componentType': 5125, 'count': len(indices), 'type': 'SCALAR'})
            name = f'CLAY_{role.upper()}'
            material = {'name': name, 'doubleSided': True, 'extras': {'cityprompt_semantic_role': role, 'texture_free': True},
                        'pbrMetallicRoughness': {'baseColorFactor': [round(c, 6) for c in srgb_to_linear(settings['colour'])] + [settings.get('alpha', 1)],
                                                 'metallicFactor': 0, 'roughnessFactor': settings.get('roughness', .78)}}
            if settings.get('alpha', 1) < 1:
                material['alphaMode'] = 'BLEND'
            if settings.get('transmission'):
                material['extensions'] = {'KHR_materials_transmission': {'transmissionFactor': settings['transmission']},
                                          'KHR_materials_ior': {'ior': 1.45}}
                for extension in material['extensions']:
                    if extension not in extensions:
                        extensions.append(extension)
            materials.append(material)
            meshes.append({'name': f'{settings["module"]} {role} mesh',
                           'primitives': [{'attributes': {'POSITION': first, 'NORMAL': first + 1}, 'indices': first + 2, 'material': len(materials) - 1}]})
            nodes.append({'name': name, 'mesh': len(meshes) - 1, 'extras': {
                'rlasm_building_object': True, 'rlasm_method': METHOD, 'cityprompt_semantic_role': role,
                'cityprompt_lego_module': settings['module'], 'representation_kind': 'architectural_clay',
                'native_geometry_only': True, **identity, 'source_component_count': self.components.get(role, 0)}})
        while len(blob) % 4:
            blob.append(0)
        document = {'asset': {'generator': GENERATOR, 'version': '2.0'}, 'scene': 0,
                    'scenes': [{'name': 'Scene', 'nodes': list(range(len(nodes)))}], 'nodes': nodes, 'materials': materials,
                    'meshes': meshes, 'accessors': accessors, 'bufferViews': views, 'buffers': [{'byteLength': len(blob)}]}
        if extensions:
            document['extensionsUsed'] = extensions
        text = json.dumps(document, separators=(',', ':')).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        return (b'glTF' + struct.pack('<II', 2, 28 + len(text) + len(blob)) + struct.pack('<II', len(text), 0x4E4F534A) + text
                + struct.pack('<II', len(blob), 0x004E4942) + bytes(blob))
