import json
import struct
import uuid
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, UploadFile

from app.services.glb_import import inspect_glb, MAX_GLB_BYTES
from app.services.user_generated_models import generated_entry, is_user_generated
from app.models.models import Building


def glb(width=12, height=9, depth=20, translation=None, external=False):
    vertices = [(x, y, z) for x in (0, width) for y in (0, height) for z in (0, depth)]
    raw = struct.pack('<24f', *(v for p in vertices for v in p))
    raw += struct.pack('<36H', *[0, 1, 2, 1, 3, 2, 4, 6, 5, 5, 6, 7, 0, 4, 1, 1, 4, 5,
                               2, 3, 6, 3, 7, 6, 0, 2, 4, 2, 6, 4, 1, 5, 3, 3, 5, 7])
    doc = {'asset': {'version': '2.0'}, 'scene': 0, 'scenes': [{'nodes': [0]}],
           'nodes': [{'mesh': 0, 'translation': translation or [0, 0, 0]}],
           'meshes': [{'primitives': [{'attributes': {'POSITION': 0}, 'indices': 1}]}],
           'buffers': [{'byteLength': len(raw)}],
           'bufferViews': [{'buffer': 0, 'byteOffset': 0, 'byteLength': 96},
                           {'buffer': 0, 'byteOffset': 96, 'byteLength': 72}],
           'accessors': [{'bufferView': 0, 'componentType': 5126, 'count': 8, 'type': 'VEC3',
                          'min': [0, 0, 0], 'max': [width, height, depth]},
                         {'bufferView': 1, 'componentType': 5123, 'count': 36, 'type': 'SCALAR'}]}
    if external:
        doc['images'] = [{'uri': 'https://example.com/private.png'}]
    text = json.dumps(doc).encode(); text += b' ' * (-len(text) % 4)
    return struct.pack('<4sII', b'glTF', 2, 28 + len(text) + len(raw)) + struct.pack('<II', len(text), 0x4E4F534A) + text + struct.pack('<II', len(raw), 0x004E4942) + raw


def test_measures_original_geometry_with_offset_origin_and_converts_units():
    result = inspect_glb(glb(1200, 900, 2000, [10000, -4000, 500]), 'centimetres')
    assert result['width_m'] == pytest.approx(12)
    assert result['depth_m'] == pytest.approx(20)
    assert result['height_meters'] == pytest.approx(9)
    assert result['triangles'] == 12


def test_arbitrary_game_scale_can_be_given_a_real_building_height_without_distortion():
    result = inspect_glb(glb(1.2, 1, 2), 'metres', target_height_m=10)
    assert result['width_m'] == pytest.approx(12)
    assert result['depth_m'] == pytest.approx(20)
    assert result['height_meters'] == pytest.approx(10)


def changed_glb(change):
    raw = glb(); length = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20 + length]); change(doc)
    text = json.dumps(doc).encode(); text += b' ' * (-len(text) % 4)
    tail = raw[20 + length:]
    return struct.pack('<4sII', b'glTF', 2, 20 + len(text) + len(tail)) + struct.pack('<II', len(text), 0x4E4F534A) + text + tail


def test_imports_valid_dense_geometry_beyond_standard_building_complexity():
    # Meshy exports can have >3M index elements while remaining within the
    # upload and decoded-resource budgets. Repeated box faces keep this fixture
    # self-contained and exercise the real geometry decoder without a binary.
    original = glb()
    length = struct.unpack_from('<I', original, 12)[0]
    doc = json.loads(original[20:20 + length])
    triangles = 1_000_004
    indices = struct.pack('<3I', 0, 1, 2) * triangles
    binary = original[28 + length:28 + length + 96] + indices
    doc['buffers'][0]['byteLength'] = len(binary)
    doc['bufferViews'][1]['byteLength'] = len(indices)
    doc['accessors'][1].update(componentType=5125, count=triangles * 3)
    text = json.dumps(doc).encode()
    text += b' ' * (-len(text) % 4)
    payload = (struct.pack('<4sII', b'glTF', 2, 28 + len(text) + len(binary))
               + struct.pack('<II', len(text), 0x4E4F534A) + text
               + struct.pack('<II', len(binary), 0x004E4942) + binary)
    result = inspect_glb(payload, 'metres')
    assert result['triangles'] == triangles
    assert (result['width_m'], result['height_meters'], result['depth_m']) == (12, 9, 20)


def test_large_scene_description_is_bounded_by_upload_size_not_building_complexity():
    payload = changed_glb(lambda d: d.update(extras={'source_note': 'a' * (4 * 1024 * 1024)}))
    assert inspect_glb(payload, 'metres')['triangles'] == 12


@pytest.mark.parametrize('width,height,depth', [(0.5, 1, 0.8), (1200, 900, 2000), (1e-6, 2e-6, 3e-6)])
def test_valid_native_dimensions_are_preserved_without_building_size_restrictions(width, height, depth):
    result = inspect_glb(glb(width, height, depth), 'metres')
    assert result['width_m'] == pytest.approx(width)
    assert result['depth_m'] == pytest.approx(depth)
    assert result['height_meters'] == pytest.approx(height)


@pytest.mark.parametrize('kind,count', [('SCALAR', 100_000_000), ('MAT4', 3_000_000)])
def test_bounds_all_accessor_allocations_before_loading_geometry(monkeypatch, kind, count):
    import trimesh
    loader = MagicMock(side_effect=RuntimeError('Geometry loader must not run'))
    monkeypatch.setattr(trimesh, 'load', loader)
    raw = changed_glb(lambda d: d['accessors'].append({'componentType': 5126, 'type': kind, 'count': count}))
    with pytest.raises(HTTPException):
        inspect_glb(raw, 'metres')
    loader.assert_not_called()


def test_rejects_broken_embedded_texture_before_the_browser_loads_it():
    def break_image(d):
        d['images'] = [{'bufferView': 999, 'mimeType': 'image/png'}]
        d['textures'] = [{'source': 0}]
        d['materials'] = [{'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}}}]
        d['meshes'][0]['primitives'][0]['material'] = 0
    with pytest.raises(HTTPException, match=''):
        inspect_glb(changed_glb(break_image), 'metres')


@pytest.mark.parametrize('payload,units', [(b'not a model', 'metres'), (glb()[:-4], 'metres'),
    (glb(external=True), 'metres'), (glb(0, 9, 20), 'metres'), (glb(), 'furlongs'),
    (glb(float('inf'), 9, 20), 'metres')])
def test_rejects_unusable_models_without_storage_or_network(payload, units):
    with pytest.raises(HTTPException) as exc:
        inspect_glb(payload, units)
    assert exc.value.status_code == 422


def test_private_uploaded_source_is_discoverable_at_measured_size():
    building = Building(id=uuid.uuid4(), project_id=uuid.uuid4(), name='My GLB', generation_engine='imported_glb',
        model_url='/api/v1/files/projects/p/models/a.glb', generation_status='completed', height_meters=9,
        specifications={'imported_glb': {'width_m': 12, 'depth_m': 20, 'height_meters': 9}})
    assert is_user_generated(building)
    entry = generated_entry(building)
    assert (entry['width_m'], entry['depth_m'], entry['size_estimated'], entry['source_kind']) == (12, 20, False, 'imported_glb')


@pytest.mark.asyncio
async def test_upload_checks_editor_before_reading_or_storing(monkeypatch):
    from app.api.v1 import model_library as api
    denied = AsyncMock(side_effect=HTTPException(403, 'Editor required'))
    monkeypatch.setattr(api, 'check_project_permission', denied)
    upload = SimpleNamespace(read=AsyncMock(), filename='building.glb')
    with pytest.raises(HTTPException) as exc:
        await api.import_glb(uuid.uuid4(), upload, 'My GLB', 'metres', SimpleNamespace(id=uuid.uuid4()), SimpleNamespace(), None)
    assert exc.value.status_code == 403
    upload.read.assert_not_awaited()


@pytest.mark.asyncio
async def test_upload_preserves_bytes_in_protected_project_storage(monkeypatch):
    from app.api.v1 import model_library as api
    from app.services import glb_import
    payload = glb(); stored = MagicMock()
    monkeypatch.setattr(api, 'check_project_permission', AsyncMock())
    monkeypatch.setattr(glb_import, 'store_glb', stored)
    db = SimpleNamespace(add=MagicMock(), flush=AsyncMock(), commit=AsyncMock())
    pid = uuid.uuid4()
    result = await api.import_glb(pid, UploadFile(filename='house.glb', file=BytesIO(payload)), 'My GLB', 'metres', SimpleNamespace(id=uuid.uuid4()), db, None)
    assert stored.call_args.args[1] == payload
    assert stored.call_args.args[0].startswith(f'projects/{pid}/models/')
    assert result['name'] == 'My GLB' and result['source_kind'] == 'imported_glb'
    assert result['model_url'].startswith(f'/api/v1/files/projects/{pid}/models/')
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_storage_failure_does_not_save_a_bogus_model(monkeypatch):
    from app.api.v1 import model_library as api
    from app.services import glb_import
    monkeypatch.setattr(api, 'check_project_permission', AsyncMock())
    monkeypatch.setattr(glb_import, 'store_glb', MagicMock(side_effect=RuntimeError('offline')))
    db = SimpleNamespace(add=MagicMock(), commit=AsyncMock())
    with pytest.raises(HTTPException) as exc:
        await api.import_glb(uuid.uuid4(), UploadFile(filename='house.glb', file=BytesIO(glb())), 'House', 'metres', SimpleNamespace(id=uuid.uuid4()), db, None)
    assert exc.value.status_code == 503
    db.add.assert_not_called(); db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_imported_model_attachment_does_not_invent_two_storeys(monkeypatch):
    from app.services import user_generated_models as models
    original = Building(id=uuid.uuid4(), project_id=uuid.uuid4(), name='Import', generation_engine='imported_glb',
        generation_status='completed', model_url='/api/v1/files/projects/p/models/a.glb', height_meters=40,
        specifications={'imported_glb': {'width_m':12, 'depth_m':14, 'height_meters':40}})
    result=MagicMock(); result.scalar_one_or_none.return_value=original
    db=SimpleNamespace(execute=AsyncMock(return_value=result),add=MagicMock(),flush=AsyncMock())
    zone=SimpleNamespace(zone_type='building', project_id=uuid.uuid4(),geometry='footprint',properties={})
    monkeypatch.setattr(models,'copy_generated_file',lambda url,key:f'/api/v1/files/{key}')
    await models.attach_generated_model(db,zone,SimpleNamespace(id=uuid.uuid4()),str(original.id))
    assert 'floors' not in zone.properties and 'floor_count' not in zone.properties
