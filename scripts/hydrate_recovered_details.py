"""Install a reviewed local asset bundle; never download, publish or overwrite conflicts."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def hydrate(bundle, public, rows, check=False):
    pending = []
    for row in rows:
        for url, digest in [(row['url'], row['sha256']), (row['thumbnailUrl'], row['thumbnailSha256'])]:
            relative = Path(url.lstrip('/'))
            if relative.parts[:2] != ('park-kits', 'recovered-details-v1') or '..' in relative.parts:
                raise ValueError('Unexpected recovered asset path')
            target = public / relative
            source = target if check else bundle / relative.name
            data = source.read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f'Checksum mismatch: {source}')
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError(f'Refusing conflicting target: {target}')
            pending.append((source, target))
    if not check:
        for source, target in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.resolve() != target.resolve():
                shutil.copyfile(source, target)
    return len(pending)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle', type=Path)
    p.add_argument('--public-dir', type=Path, required=True)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    if not args.check and not args.bundle:
        p.error('--bundle is required unless --check is used')
    root = Path(__file__).resolve().parents[1]
    rows = json.loads((root/'frontend/src/features/parks/recoveredDetails.json').read_text())
    print(f'{hydrate(args.bundle, args.public_dir, rows, args.check)} verified files')
