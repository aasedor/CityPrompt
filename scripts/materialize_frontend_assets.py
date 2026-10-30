"""Materialize only missing, manifest-required archive outputs for clean CI checkouts.

Loose historical LFS files remain pointers. The separate release asset workflow
performs full hydration; this prepares pinned archive members and Vite imports.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.hosted_assets import ROOT, RepositoryAssets, checked_payload, hydrate_source_media, safe_target, write_asset


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
    media = hydrate_source_media(sources)
    return {'archive_outputs': count, 'archive_bytes': total, 'source_media': len(media)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-lfs', action='store_true')
    args = parser.parse_args()
    print(json.dumps(materialize(fetch_lfs=args.fetch_lfs)))


if __name__ == '__main__':
    main()
