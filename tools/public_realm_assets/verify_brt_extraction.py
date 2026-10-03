"""Blender round-trip check of recovered BRT meshes against their source objects.

No source writes or runtime activation. Compares both directions by material,
including vertices hidden from a camera, after restoring each source anchor.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def vertices(objects, anchor=(0, 0, 0)):
    from mathutils import Vector
    result = {}
    for obj in objects:
        mesh = obj.to_mesh()
        for polygon in mesh.polygons:
            material = mesh.materials[polygon.material_index]
            # Reimport may append .001 to a material name.
            name = material.name.rsplit('.', 1)[0] if material.name.rsplit('.', 1)[-1].isdigit() else material.name
            points = result.setdefault(name, set())
            for index in polygon.vertices:
                p = obj.matrix_world @ mesh.vertices[index].co + Vector(anchor)
                points.add(tuple(p))
        obj.to_mesh_clear()
    return result


def distance(a, b):
    from mathutils.kdtree import KDTree
    tree = KDTree(len(b))
    for i, point in enumerate(b):
        tree.insert(point, i)
    tree.balance()
    return max(tree.find(point)[2] for point in a)


def main():
    import bpy
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--derived', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    manifest = json.loads((args.derived / 'extraction.json').read_text())
    source = args.source / 'editable.blend'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['sourceAuthoringSha256']
    reports = {}
    for kind, module in manifest['modules'].items():
        path = args.derived / module['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == module['sha256']
        bpy.ops.wm.open_mainfile(filepath=str(source))
        selected = [bpy.data.objects[name] for name in module['sourceObjectNames']]
        original = vertices(selected)
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(path))
        restored = vertices([o for o in set(bpy.data.objects) - before if o.type == 'MESH'], module['sourceAnchorM'])
        assert original.keys() == restored.keys(), 'Recovered module changed its material groups'
        errors = {name: max(distance(points, restored[name]), distance(restored[name], points))
                  for name, points in original.items()}
        assert max(errors.values()) < .0001, f'Geometry drift in {kind}: {errors}'
        points = [p for group in restored.values() for p in group]
        low = [min(p[i] for p in points) - module['sourceAnchorM'][i] for i in range(3)]
        high = [max(p[i] for p in points) - module['sourceAnchorM'][i] for i in range(3)]
        reports[kind] = dict(status='PASS', sha256=module['sha256'], materialCount=len(original),
                             bounds=dict(plan=[low[:2], high[:2]], height=[low[2], high[2]]),
                             sourceObjectCount=len(selected), maxVertexErrorM=max(errors.values()))
    args.report.write_text(json.dumps(dict(status='PASS', modules=reports,
        scope='Original source geometry and material grouping; visual/runtime acceptance remains separate.'), indent=2) + '\n')
    print('SOURCE_ROUND_TRIP_PASS', json.dumps(reports))


if __name__ == '__main__':
    main()
