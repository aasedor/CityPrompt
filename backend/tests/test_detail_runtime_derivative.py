import importlib.util
import io
from pathlib import Path

import numpy as np
import pytest
import trimesh


def test_metric_wrapper_preserves_proportions_and_rotates_vehicle_only_once():
    spec = importlib.util.spec_from_file_location('detail_runtime', Path(__file__).resolve().parents[2] / 'scripts/prepare_detail_runtime.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    model = trimesh.creation.box([1, .3, .4]); model.apply_translation([.2, .5, -.1])
    source = model.export(file_type='glb')
    result = module.derive(source, 5, model.bounds.tolist(), vehicle=True)
    scene = trimesh.load(io.BytesIO(result), file_type='glb', force='scene', process=False)
    assert np.allclose(scene.extents, [2, 1.5, 5], atol=1e-6)
    assert np.allclose(scene.bounds[0], [-1, 0, -2.5], atol=1e-6)
    assert sum(len(m.faces) for m in scene.geometry.values()) == len(model.faces)
    with pytest.raises(ValueError): module.derive(source, -1, model.bounds.tolist())


def test_invalid_normals_are_repaired_without_moving_vertices():
    import struct
    spec = importlib.util.spec_from_file_location('detail_runtime', Path(__file__).resolve().parents[2] / 'scripts/prepare_detail_runtime.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    positions = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 1]], dtype='<f4')
    payload = bytearray(positions.tobytes()+np.zeros((3, 3), dtype='<f4').tobytes()+struct.pack('<HHH', 0, 1, 2))
    doc = {'bufferViews': [{'byteOffset': 0}, {'byteOffset': 36}, {'byteOffset': 72}],
           'accessors': [{'bufferView': 0, 'componentType': 5126, 'type': 'VEC3', 'count': 3},
                         {'bufferView': 1, 'componentType': 5126, 'type': 'VEC3', 'count': 3},
                         {'bufferView': 2, 'componentType': 5123, 'type': 'SCALAR', 'count': 3}],
           'meshes': [{'primitives': [{'attributes': {'POSITION': 0, 'NORMAL': 1}, 'indices': 2}]}]}
    module.repair_normals(doc, payload)
    assert payload[:36] == positions.tobytes()
    assert np.allclose(np.frombuffer(payload[36:72], dtype='<f4').reshape(3, 3), [0, -1, 0])
