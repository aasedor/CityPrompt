"""Copy an original generated image without alteration and record its source chain."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image
from plan import SPECS

FILES = {'front': 'variant_0.png', 'oblique': 'variant_0_angle_60.png', 'top': 'variant_0_angle_90.png'}

def capture(kind, role, record_file):
    root = Path(__file__).resolve().parents[2] / 'frontend/public/archetypes/buildings' / SPECS[kind]['slug']
    record = json.loads(Path(record_file).read_text(encoding='utf-8'))
    source = Path(record['source'])
    if not source.is_file() or source.suffix.lower() != '.png':
        raise ValueError('Expected generated PNG')
    root.mkdir(parents=True, exist_ok=True)
    target = root / FILES[role]
    if target.exists():
        raise FileExistsError(target)
    provenance = root / 'generation-provenance.json'
    data = json.loads(provenance.read_text(encoding='utf-8')) if provenance.exists() else dict(
        origin='original_generated_design', generator='built-in image_gen', records=[], not_surveyed=True,
        metadata_authority='Pixels govern geometry; programmes and metric dimensions are authored design assumptions.')
    if any(r['role'] == role for r in data['records']):
        raise ValueError('Role already recorded')
    for input_role in record['input_roles']:
        if input_role not in {r['role'] for r in data['records']}:
            raise ValueError('Missing prior source role: '+input_role)
    with Image.open(source) as im:
        size = list(im.size)
        im.verify()
    shutil.copy2(source, target)
    raw = target.read_bytes()
    data['records'].append(dict(role=role, file=target.name, source=str(source), prompt=record['prompt'],
        input_roles=record['input_roles'], sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), dimensions_px=size))
    provenance.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(str(target))

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=list(SPECS),required=True)
    p.add_argument('--role',choices=list(FILES),required=True);p.add_argument('--record-file',required=True)
    a=p.parse_args();capture(a.kind,a.role,a.record_file)
