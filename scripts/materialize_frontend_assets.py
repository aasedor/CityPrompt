"""Materialize only missing, manifest-required archive outputs for clean CI checkouts.

Loose historical LFS files remain pointers. The separate release asset workflow
performs full hydration; this prepares pinned archive members and Vite imports.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.hosted_assets import LFS, ROOT, RepositoryAssets, checked_payload, hydrate_source_media, safe_target, write_asset


def hydrate_startup_assets(root: Path, sources) -> int:
    """Hydrate the exact rustic park assets preloaded on workspace entry."""
    kit = root / 'frontend/src/data/neighborhoodParkV0StickerKit.json'
    if not kit.exists():
        return 0
    payloads = []
    for row in json.loads(kit.read_text(encoding='utf-8'))['assets'].values():
        url, digest, size = row['url'], row['sha256'], row['bytes']
        if (not url.startswith('/park-kits/neighborhood-park-rustic-v0/')
                or not url.endswith('.glb') or not re.fullmatch(r'[a-f0-9]{64}', digest)):
            raise ValueError('Unpinned asset outside the startup kit')
        target = safe_target(root / 'frontend/public', url)
        current = target.read_bytes() if target.exists() else None
        if current is not None and current.startswith(LFS):
            pointer = re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\r?\noid sha256:([a-f0-9]{64})\r?\nsize (\d+)\r?\n?', current)
            if not pointer or pointer[1].decode() != digest or int(pointer[2]) != size:
                raise ValueError('Startup LFS pointer differs from its catalogue lock')
        elif current is not None:
            data = checked_payload(current, digest)
            if len(data) != size:
                raise ValueError('Startup asset size differs from its catalogue lock')
            continue
        data = checked_payload(sources.public(url, digest), digest)
        if len(data) != size:
            raise ValueError('Startup asset size differs from its catalogue lock')
        payloads.append((target, current, data))
    # Validate the finite batch before replacing any pointer; preserve local edits.
    for target, current, data in payloads:
        if (target.read_bytes() if target.exists() else None) != current:
            raise ValueError('Startup asset changed during preparation')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return len(payloads)


def materialize(root: Path = ROOT, fetch_lfs: bool = False, *, sources=None) -> dict:
    root = root.resolve()
    manifest = json.loads((root / 'frontend/src/data/runtimeAssetManifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != 'cityprompt.runtime-assets@1':
        raise ValueError('Unsupported runtime asset manifest')
    sources = sources if sources is not None else RepositoryAssets(root, fetch_lfs)
    public = root / 'frontend/public'
    count = total = 0
    for row in manifest['explicitReferences']:
        url = row['url']
        target = safe_target(public, url)
        if target.exists():
            continue  # Preserve local files; ordinary asset checks verify their contents.
        data = checked_payload(sources.public(url, row.get('lfsOid')), row.get('lfsOid'))
        if len(data) != row['logicalBytes']:
            raise ValueError(f'Archive output size differs from runtime manifest: {url}')
        write_asset(public, url, data)
        count += 1
        total += len(data)
    startup = hydrate_startup_assets(root, sources)
    media = hydrate_source_media(sources)
    return {'archive_outputs': count, 'archive_bytes': total, 'startup_outputs': startup, 'source_media': len(media)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-lfs', action='store_true')
    args = parser.parse_args()
    print(json.dumps(materialize(fetch_lfs=args.fetch_lfs)))


if __name__ == '__main__':
    main()
