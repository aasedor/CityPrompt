"""Validate embedded buffers, allocations and textures before geometry decoding."""
import base64
from io import BytesIO
import struct

from fastapi import HTTPException
from PIL import Image


def validate_glb_resources(doc: dict, payload: bytes, json_end: int) -> None:
    def invalid(message='The GLB has broken embedded resources. Export it again with textures embedded.'):
        raise HTTPException(422, message)

    def index(items, value):
        if type(value) is not int or not 0 <= value < len(items):
            invalid()
        return items[value]

    def data_uri(uri):
        if not isinstance(uri, str) or not uri.startswith('data:') or ';base64,' not in uri:
            invalid()
        return base64.b64decode(uri.split(';base64,', 1)[1], validate=True)

    binary = b''
    offset = json_end
    while offset < len(payload):
        if offset + 8 > len(payload):
            invalid()
        length, kind = struct.unpack_from('<II', payload, offset)
        if length % 4 or offset + 8 + length > len(payload):
            invalid()
        if kind == 0x004E4942:
            if binary:
                invalid()
            binary = payload[offset + 8:offset + 8 + length]
        offset += length + 8
    buffers = []
    for i, item in enumerate(doc.get('buffers', [])):
        raw = data_uri(item['uri']) if 'uri' in item else binary if i == 0 else b''
        length = item.get('byteLength')
        if type(length) is not int or not 0 <= length <= len(raw):
            invalid()
        buffers.append(raw[:length])
    views = doc.get('bufferViews', [])
    for view in views:
        raw = index(buffers, view.get('buffer'))
        start, length = view.get('byteOffset', 0), view.get('byteLength')
        if type(start) is not int or type(length) is not int or start < 0 or length < 0 or start + length > len(raw):
            invalid()
    components = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT2': 4, 'MAT3': 9, 'MAT4': 16}
    byte_sizes = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
    decoded_bytes = 0
    for accessor in doc.get('accessors', []):
        count, kind, component = accessor.get('count'), accessor.get('type'), accessor.get('componentType')
        if type(count) is not int or not 0 <= count <= 3_000_000 or kind not in components or component not in byte_sizes:
            invalid('This model is too complex or has invalid geometry data. Simplify it before importing.')
        element = components[kind] * byte_sizes[component]
        decoded_bytes += count * element
        if decoded_bytes > 128 * 1024 * 1024:
            invalid('This model is too complex. Simplify it before importing.')
        if 'bufferView' in accessor:
            view = index(views, accessor['bufferView'])
            start, stride = accessor.get('byteOffset', 0), view.get('byteStride', element)
            if type(start) is not int or type(stride) is not int or start < 0 or stride < element or start + max(0, count - 1) * stride + (element if count else 0) > view['byteLength']:
                invalid()
        if 'sparse' in accessor:
            sparse = accessor['sparse']; sparse_count = sparse.get('count')
            if type(sparse_count) is not int or not 0 <= sparse_count <= count:
                invalid()
            for field, size in [('indices', byte_sizes.get(sparse.get('indices', {}).get('componentType'), 0)), ('values', element)]:
                record = sparse.get(field, {}); view = index(views, record.get('bufferView'))
                start = record.get('byteOffset', 0)
                if not size or type(start) is not int or start < 0 or start + sparse_count * size > view['byteLength']:
                    invalid()
    images = doc.get('images', [])
    pixels = 0
    for image in images:
        if 'uri' in image:
            raw = data_uri(image['uri'])
        else:
            view = index(views, image.get('bufferView'))
            buffer = index(buffers, view.get('buffer'))
            raw = buffer[view.get('byteOffset', 0):view.get('byteOffset', 0) + view['byteLength']]
        if raw.startswith(b'\xabKTX 20\xbb\r\n\x1a\n'):
            if len(raw) < 80:
                invalid()
            width, height = struct.unpack_from('<II', raw, 20)
        else:
            with Image.open(BytesIO(raw)) as picture:
                width, height = picture.size
                picture.verify()
        pixels += width * height
        if not 0 < width <= 8192 or not 0 < height <= 8192 or pixels > 64 * 1024 * 1024:
            invalid('The textures are too large. Use smaller embedded textures before importing.')
    textures = doc.get('textures', [])
    for texture in textures:
        source = texture.get('source', texture.get('extensions', {}).get('KHR_texture_basisu', {}).get('source'))
        index(images, source)
    def material_textures(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.lower().endswith('texture') and isinstance(item, dict):
                    index(textures, item.get('index'))
                material_textures(item)
        elif isinstance(value, list):
            for item in value:
                material_textures(item)
    material_textures(doc.get('materials', []))
    for mesh in doc.get('meshes', []):
        for primitive in mesh.get('primitives', []):
            if 'material' in primitive:
                index(doc.get('materials', []), primitive['material'])
