"""Read-only fixed public-realm release preflight; never copies or publishes assets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.services.fixed_public_realm import release_gate_errors  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-dir', type=Path, help='Also verify selected exact binary and thumbnail payloads.')
    parser.add_argument('--local-rehearsal', action='store_true', help='Include the finite runtime_trial pilot; does not grant publication.')
    parser.add_argument('--all-prepared', action='store_true', help='Inspect all prepared packages; does not activate them.')
    args = parser.parse_args()
    frontend = json.loads((ROOT / 'frontend/src/data/publicRealmRelease20261023.json').read_text(encoding='utf-8'))
    backend = json.loads((ROOT / 'backend/app/data/public_realm_release_20261023.json').read_text(encoding='utf-8'))
    if frontend != backend or frontend.get('schema') != 'cityprompt.fixed-public-realm-release@1':
        raise ValueError('Frontend/backend fixed public-realm manifests differ or have an unsupported schema.')
    ids = set()
    selected = []
    for row in frontend['models']:
        identity = row['asset']['id']
        errors = release_gate_errors(row)
        if identity in ids or 'identity_mismatch' in errors:
            raise ValueError(f'Invalid or duplicate exact fixed-model identity: {identity}')
        ids.add(identity)
        if row['status'] in ('ready', 'retired') and errors:
            raise ValueError(f'Invalid release approval for {identity}: {errors}')
        if args.all_prepared or row['status'] in ('ready', 'retired') or (args.local_rehearsal and row['status'] == 'runtime_trial'):
            selected.append(row)
    files = []
    if args.public_dir:
        public = args.public_dir.resolve()
        for row in selected:
            for url, digest in ((row['fixture']['url'], row['runtime_sha256']), (row['asset']['thumbnail'], row['thumbnail_sha256'])):
                target = (public / url.lstrip('/')).resolve()
                if not target.is_relative_to(public):
                    raise ValueError(f'Asset path escaped the public directory: {url}')
                payload = target.read_bytes()
                if hashlib.sha256(payload).hexdigest() != digest:
                    raise ValueError(f'Exact fixed-model payload hash differs: {url}')
                if url.endswith('.glb') and (payload[:4] != b'glTF' or struct.unpack_from('<I', payload, 8)[0] != len(payload)):
                    raise ValueError(f'Invalid GLB payload: {url}')
                files.append({'url': url, 'sha256': digest, 'bytes': len(payload)})
    print(json.dumps({'schema': frontend['schema'], 'prepared_count': len(ids),
                      'production_ready_count': sum(row['status'] == 'ready' for row in frontend['models']),
                      'selected_count': len(selected), 'files': files,
                      'publication_performed': False}, indent=2))


if __name__ == '__main__':
    main()
