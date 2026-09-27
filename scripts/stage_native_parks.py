"""Verify and stage the finite native park inventory; never activate candidates.

Usage: python scripts/stage_native_parks.py --public-dir <vite public directory>
Without --public-dir this is a read-only verification of the archive and registry.
"""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'frontend/src/data/nativeParks.json'


def stage(archive: Path, public_dir: Path | None = None) -> dict:
    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    for park in registry['layouts']:
        geometry = {key:value for key,value in park.items() if key not in ('status','visualStatus','runtimeStatus','contentRevision')}
        digest = hashlib.sha256(json.dumps(geometry, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        if digest != park['contentRevision']:
            raise ValueError(f"Park content changed without a new revision: {park['id']}")
    files = {asset['sha256']: asset for park in registry['layouts'] for asset in park['assets'].values()}
    verified = []
    with ZipFile(archive) as source:
        # Validate the whole batch before writing any files.
        for park in registry['layouts']:
            recipe = source.read(f"evidence/validation_{park['variantId']}/recipe.json")
            if hashlib.sha256(recipe).hexdigest() != park['sourceRecipeSha256']:
                raise ValueError(f"Invalid source recipe: {park['variantId']}")
        payloads = []
        for digest, asset in files.items():
            data = source.read(asset['archivePath'])
            if hashlib.sha256(data).hexdigest() != digest or data[:4] != b'glTF':
                raise ValueError(f"Invalid native park asset: {asset['archivePath']}")
            document = json.loads(data[20:20 + int.from_bytes(data[12:16], 'little')])
            if any('uri' in item for key in ('buffers', 'images') for item in document.get(key, [])):
                raise ValueError(f"Park assets must embed their dependencies: {asset['archivePath']}")
            target = public_dir / asset['url'].lstrip('/') if public_dir else None
            if target and (not target.resolve().is_relative_to(public_dir.resolve())
                           or (target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != digest)):
                raise ValueError(f'Unsafe or conflicting destination: {target}')
            payloads.append((target, data))
            verified.append(digest)
        for target, data in payloads:
            if target:
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_bytes(data)
    return {'verifiedAssets': len(verified), 'written': public_dir is not None,
            'registrySha256': hashlib.sha256(REGISTRY.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT / 'seed/validation/runtime-assets.zip')
    parser.add_argument('--public-dir', type=Path)
    args = parser.parse_args()
    print(json.dumps(stage(args.archive, args.public_dir), indent=2))
