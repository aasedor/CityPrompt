"""Copy unchanged provider originals into one authoritative, reviewed source set."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image


def capture(spec_path, target):
    spec=json.loads(Path(spec_path).read_text(encoding='utf-8'))
    target=Path(target)
    if target.exists():raise FileExistsError('Source packages are immutable: '+str(target))
    records=[]
    for record in spec['records']:
        path=Path(record['generated_path'])
        with Image.open(path) as img:
            img.load();size=list(img.size)
        raw=path.read_bytes()
        records.append(dict(record,file=record['role']+'.png',sha256=hashlib.sha256(raw).hexdigest(),
                            bytes=len(raw),dimensions_px=size))
    if {r['role'] for r in records}!={'front','oblique','top'}:raise ValueError('Three roles required')
    target.mkdir(parents=True)
    for r in records:shutil.copy2(r['generated_path'],target/r['file'])
    provenance=dict(spec,origin='original_generated_design',records=records)
    (target/'generation-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('spec');p.add_argument('target');a=p.parse_args()
    capture(a.spec,a.target)
