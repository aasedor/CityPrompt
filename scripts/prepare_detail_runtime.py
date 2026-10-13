"""Derive a metric detail GLB without changing source geometry or source files."""
import io
import json
import math
import struct

from PIL import Image


def derive(data: bytes, scale: float, bounds, vehicle=False, texture_limit=1024):
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError('A positive uniform scale is required')
    magic, version, size = struct.unpack_from('<4sII', data)
    if (magic, version, size) != (b'glTF', 2, len(data)):
        raise ValueError('Expected a complete GLB v2')
    length, kind = struct.unpack_from('<II', data, 12)
    if kind != 0x4E4F534A:
        raise ValueError('Missing JSON chunk')
    doc = json.loads(data[20:20+length])
    if doc.get('extensionsRequired') or len(doc['buffers']) != 1:
        raise ValueError('Review extensions and additional buffers before adapting')
    binary = bytearray(data[28+length:])
    repair_normals(doc, binary)
    replacements = {}
    for image in doc.get('images', []):
        if 'uri' in image:
            raise ValueError('External images are not accepted')
        index = image['bufferView']; view = doc['bufferViews'][index]
        start = view.get('byteOffset', 0)
        with Image.open(io.BytesIO(binary[start:start+view['byteLength']])) as im:
            if max(im.size) <= texture_limit:
                continue
            im.thumbnail((texture_limit, texture_limit), Image.Resampling.LANCZOS)
            stream = io.BytesIO(); im.save(stream, format='PNG')
            replacements[index] = stream.getvalue(); image['mimeType'] = 'image/png'
    payload = bytearray()
    for index, view in enumerate(doc['bufferViews']):
        start = view.get('byteOffset', 0)
        chunk = replacements.get(index, binary[start:start+view['byteLength']])
        payload.extend(b'\0' * (-len(payload) % 4))
        view['byteOffset'] = len(payload); view['byteLength'] = len(chunk)
        payload.extend(chunk)
    doc['buffers'][0]['byteLength'] = len(payload)
    scene = doc['scenes'][doc.get('scene', 0)]
    # Avoid a cycle in inspection tools that reserve "world" as their base frame.
    for node in doc['nodes']:
        if node.get('name') == 'world':
            node['name'] = 'authored world'
    lo, hi = bounds
    cx, cz = (lo[0]+hi[0])/2, (lo[2]+hi[2])/2
    # Vehicle exports have their long axis along X. Rotate it once into Z depth.
    wrapper = {'name': 'CityPrompt metric placement', 'children': scene['nodes'],
               'scale': [scale]*3,
               'translation': [(-cz if vehicle else -cx)*scale, -lo[1]*scale,
                               (cx if vehicle else -cz)*scale]}
    if vehicle:
        wrapper['rotation'] = [0, math.sin(math.pi/4), 0, math.cos(math.pi/4)]
    scene['nodes'] = [len(doc['nodes'])]; doc['nodes'].append(wrapper)
    encoded = json.dumps(doc, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4); payload.extend(b'\0' * (-len(payload) % 4))
    return (struct.pack('<4sII', b'glTF', 2, 28+len(encoded)+len(payload))
            + struct.pack('<II', len(encoded), 0x4E4F534A) + encoded
            + struct.pack('<II', len(payload), 0x004E4942) + payload)


def repair_normals(doc, binary):
    """Repair invalid exported normals only; preserve positions and topology.

    Zero normals use area-weighted adjoining faces. Vertices belonging only to
    zero-area faces get an up normal (those faces have no rendered surface).
    """
    import numpy as np

    def accessor(index):
        a = doc['accessors'][index]
        if a.get('sparse') or a.get('normalized'):
            raise ValueError('Review sparse/normalized accessor before adapting')
        view = doc['bufferViews'][a['bufferView']]
        dtype = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5121: 'u1'}[a['componentType']]
        width = {'VEC3': 3, 'SCALAR': 1}[a['type']]
        item = np.dtype(dtype).itemsize
        return np.ndarray((a['count'], width), dtype=dtype, buffer=binary,
                          offset=view.get('byteOffset', 0)+a.get('byteOffset', 0),
                          strides=(view.get('byteStride', width*item), item))

    for mesh in doc.get('meshes', []):
        for p in mesh['primitives']:
            if 'NORMAL' not in p['attributes']:
                continue
            normals = accessor(p['attributes']['NORMAL'])
            lengths = np.linalg.norm(normals, axis=1)
            if not np.isfinite(lengths).all():
                raise ValueError('Non-finite exported normals')
            bad = np.abs(lengths-1) > 1e-5
            if not bad.any():
                continue
            zero = lengths < 1e-12
            if zero.any():
                if p.get('mode', 4) != 4:
                    raise ValueError('Normal recovery requires triangles')
                positions = accessor(p['attributes']['POSITION'])
                faces = accessor(p['indices']).ravel().reshape(-1, 3)
                weighted = np.cross(positions[faces[:, 1]]-positions[faces[:, 0]],
                                    positions[faces[:, 2]]-positions[faces[:, 0]])
                sums = np.zeros_like(normals)
                for corner in range(3):
                    np.add.at(sums, faces[:, corner], weighted)
                normals[zero] = sums[zero]
                empty = np.linalg.norm(normals, axis=1) < 1e-12
                normals[empty] = [0, 1, 0]
            normals[bad] /= np.linalg.norm(normals[bad], axis=1)[:, None]
