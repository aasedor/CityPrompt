"""Verify exact derivative GLBs and emit a small reproducible provenance manifest.

Run after measure_characters.py. No downloads, payment, rendering or source edits.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


ROOT = Path('C:/dev-artifacts/CityPrompt/people-video-pilot-2026-10-21/characters')
COMPONENTS = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root):
    measurements = json.loads((root / 'measurements.json').read_text())
    assert {m['id'] for m in measurements} == {
        'people-pilot-commuter', 'people-pilot-creative', 'people-pilot-neighbour'}
    actors = []
    for measured in measurements:
        path = root / 'runtime' / (measured['id'] + '.glb')
        data = path.read_bytes()
        assert data[:4] == b'glTF' and struct.unpack_from('<I', data, 8)[0] == len(data)
        json_length = struct.unpack_from('<I', data, 12)[0]
        doc = json.loads(data[20:20 + json_length])
        binary = data[28 + json_length:]
        assert sha(path) == measured['sha256'], 'Measurements do not match final runtime bytes'

        def accessor(index):
            a = doc['accessors'][index]
            view = doc['bufferViews'][a['bufferView']]
            code, size = COMPONENTS[a['componentType']]
            width = WIDTHS[a['type']]
            offset = view.get('byteOffset', 0) + a.get('byteOffset', 0)
            stride = view.get('byteStride', size * width)
            return [struct.unpack_from('<' + code * width, binary, offset + i * stride) for i in range(a['count'])]

        # Every vertex, animation value, time and skin weight is finite.
        for index in range(len(doc['accessors'])):
            assert all(math.isfinite(v) for row in accessor(index) for v in row)
        assert {a['name'] for a in doc['animations']} == {'Walk', 'Idle'}
        track_counts = {}
        for animation in doc['animations']:
            track_counts[animation['name']] = len(animation['channels'])
            for sampler in animation['samplers']:
                times = [row[0] for row in accessor(sampler['input'])]
                assert times[0] == 0 and all(b > a for a, b in zip(times, times[1:]))
            for channel in animation['channels']:
                assert channel['target']['node'] < len(doc['nodes'])
                assert channel['target']['path'] in {'translation', 'rotation', 'scale'}
        for mesh in doc['meshes']:
            for primitive in mesh['primitives']:
                attributes = primitive['attributes']
                assert {'POSITION', 'JOINTS_0', 'WEIGHTS_0'} <= attributes.keys()
                for weights in accessor(attributes['WEIGHTS_0']):
                    assert abs(sum(weights) - 1) < .0001 and min(weights) >= 0
                for joints in accessor(attributes['JOINTS_0']):
                    assert max(joints) < measured['bones']
        assert measured['byteSize'] < 2 * 1024 * 1024
        assert measured['triangleCount'] < 20000
        for clip in measured['clips']:
            assert clip['sampleCount'] == 41
            assert clip['sampledMinFootZ'] >= -.0021
            assert clip['sampledMaxFootZ'] <= .0066
        idle = next(c for c in measured['clips'] if c['name'] == 'Idle')
        walk = next(c for c in measured['clips'] if c['name'] == 'Walk')
        first = idle['samples'][0]
        dimensions = [first['max'][0] - first['min'][0], first['max'][2] - first['min'][2], first['max'][1] - first['min'][1]]
        assert 1.60 < dimensions[1] < 1.90
        foot_ranges = {side: max(s['feetBlender'][side][1] for s in walk['samples']) - min(s['feetBlender'][side][1] for s in walk['samples']) for side in ['l', 'r']}
        textures = []
        for image in doc.get('images', []):
            view = doc['bufferViews'][image['bufferView']]
            start = view.get('byteOffset', 0)
            png = binary[start:start + view['byteLength']]
            assert png[:8] == b'\x89PNG\r\n\x1a\n'
            width, height = struct.unpack_from('>II', png, 16)
            textures.append({'name': image.get('name'), 'width': width, 'height': height,
                             'encodedBytes': len(png), 'decodedRGBA8Bytes': width * height * 4,
                             'estimatedRGBA8WithMipmapsBytes': math.ceil(width * height * 4 * 4 / 3)})
        actors.append({
            'id': measured['id'], 'runtimeUrl': '/people-pilot/' + path.name,
            'artifactFile': str(path), 'sha256': measured['sha256'], 'byteSize': len(data),
            'coordinates': {'up': '+Y', 'forward': '+Z', 'unit': 'metre', 'footDatumY': 0},
            'idleFrame0DimensionsMetresXYZ': dimensions,
            'triangleCount': measured['triangleCount'], 'bones': measured['bones'],
            'meshPrimitives': measured['meshPrimitives'], 'materials': measured['materials'],
            'decodedAccessorBytes': measured['accessorDecodedBytes'],
            'textures': textures,
            'estimatedDecodedAssetBytes': measured['accessorDecodedBytes'] + sum(t['estimatedRGBA8WithMipmapsBytes'] for t in textures) + measured['bones'] * 64,
            'clips': [{'name': c['name'], 'sourceName': 'Walk_Loop' if c['name'] == 'Walk' else 'Idle_Loop',
                       'durationSeconds': c['durationSeconds'], 'channelCount': track_counts[c['name']],
                       'sampledSoleYMinMetres': c['sampledMinFootZ'], 'sampledSoleYMaxMetres': c['sampledMaxFootZ'],
                       'sampleCount': c['sampleCount']} for c in measured['clips']],
            'strideEstimateMetresPerWalkCycle': sum(foot_ranges.values()),
            'strideEstimateMethod': 'Sum of left and right ankle forward-axis ranges across 41 uniformly sampled times. Approximation; tune visually for source speed.',
            'leftRightAnkleForwardRangesMetres': foot_ranges,
            'idlePreviewFile': str(root / 'qa' / (path.stem + '.png')),
        })
    source_info = [
        ('Universal Base Characters Standard', 'universal-base-characters', 'https://quaternius.com/packs/universalbasecharacters.html'),
        ('Universal Animation Library Standard', 'universal-animation-library', 'https://quaternius.com/packs/universalanimationlibrary.html'),
    ]
    sources = []
    for title, slug, url in source_info:
        path = root / 'sources' / (slug + '-standard.zip')
        license_file = next((root / 'sources' / slug).rglob('*License*.txt'))
        assert 'CC0 1.0 Universal' in license_file.read_text()
        sources.append({'title': title, 'creator': 'Quaternius', 'officialPage': url,
                        'officialDownloadPage': 'https://quaternius.itch.io/' + slug,
                        'downloadMethod': 'Official public No thanks, just take me to the downloads, Standard file only; no sign-in or payment.',
                        'archiveFile': str(path), 'archiveByteSize': path.stat().st_size, 'archiveSha256': sha(path),
                        'license': 'CC0-1.0', 'licenseUrl': 'https://creativecommons.org/publicdomain/zero/1.0/',
                        'licenseFile': str(license_file), 'licenseSha256': sha(license_file)})
    manifest = {
        'schemaVersion': 1, 'initiative': 'people-video-pilot-2026-10-21', 'localOnly': True,
        'sources': sources,
        'derivativeAuthorship': 'Original simple outer-garment meshes, trousers, closed sneaker meshes, open-front coat hem, palettes and measured root grounding over CC0 source adult anatomy, hair and motion. These are derivatives, not wholly original anatomy or mocap.',
        'sourceSelection': 'Free Standard supplies Superhero_Female_FullBody and Superhero_Male_FullBody, plus Hair_Buns, Hair_Long and Hair_SimpleParted. Paid Regular/Source models excluded.',
        'buildTool': 'Blender 5.2.0 LTS; tools/people_pilot/build_characters.py',
        'measurementTool': 'Blender 5.2.0 LTS; tools/people_pilot/measure_characters.py',
        'footContact': 'Root-bone vertical correction baked at 24 fps from evaluated sneaker soles. In-between full-cycle samples remain within -2.04 mm to +6.48 mm of datum. Body retains source pelvis bob.',
        'limitations': ['Stylized low polygon source faces/anatomy; not photoreal characters.', 'Simple shoulder/collar seams, no cloth simulation, fingers retain source motion.', 'Stride estimate is measured ankle travel, not marker-based locomotion calibration.', 'Decoded costs estimate accessors, RGBA8 mipmapped textures and joint matrices; exclude Three.js objects, GPU allocator overhead and browser caches.', 'Browser visual review and capture integration are separate root-agent gates.'],
        'actors': actors,
    }
    output = root / 'manifest.json'; output.write_text(json.dumps(manifest, indent=2) + '\n')
    print('PASS: 3 exact GLBs; all accessors finite; skin weights/joints valid; named Walk/Idle; 246 posed bounds/sole samples; metre heights and byte/triangle budgets.')
    print('Manifest:', output)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--root', type=Path, default=ROOT)
    verify(parser.parse_args().root)
