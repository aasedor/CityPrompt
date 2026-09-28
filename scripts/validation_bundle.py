"""Verify/unpack the exact validation asset packet, or create private test env files."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import secrets
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'seed/validation'
DEST = ROOT / '.validation'
PICKER_HERO_DOMAINS = ('buildings', 'openspaces', 'streets')
PICKER_HERO_COUNT = 12

def digest(data): return hashlib.sha256(data).hexdigest()

def unpack(destination=DEST):
    manifest=json.loads((PACKET/'manifest.json').read_text())
    archive=PACKET/'runtime-assets.zip'
    if digest(archive.read_bytes()) != manifest['archive_sha256']:
        raise ValueError('Missing/wrong asset packet. Run git lfs pull --include="seed/validation/runtime-assets.zip"')
    with zipfile.ZipFile(archive) as z:
        expected={row['path']:row for row in manifest['files']}
        if set(z.namelist())!=set(expected) or len(z.namelist())!=len(expected):raise ValueError('Packet file inventory mismatch')
        for name,row in expected.items():
            path=PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:raise ValueError('Unsafe packet path')
            data=z.read(name)
            if len(data)!=row['bytes'] or digest(data)!=row['sha256']:raise ValueError(f'Bad packet bytes: {name}')
            target=destination/path
            if target.exists() and digest(target.read_bytes())!=row['sha256']:raise ValueError(f'Preserved changed file; extract into a new directory: {target}')
        for name in expected:
            target=destination/name;target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.write_bytes(z.read(name))
    sync_picker_heroes(destination)
    print(f'Verified {len(expected)} exact files; extracted to {destination}')

def sync_picker_heroes(destination=DEST, source_root=ROOT / 'frontend/public'):
    """Stage the small, curated picker views beside the locked runtime packet.

    Never overwrite a locally changed staged image; the source and destination
    must agree byte-for-byte on repeated runs.
    """
    source_root=Path(source_root)
    files=sorted(path for domain in PICKER_HERO_DOMAINS
                 for path in (source_root/'archetypes'/domain/'classroom-heroes').glob('*.webp'))
    if len(files)!=PICKER_HERO_COUNT:
        raise ValueError(f'Expected {PICKER_HERO_COUNT} picker heroes; found {len(files)}')
    for source in files:
        data=source.read_bytes()
        if data[:4]!=b'RIFF' or data[8:12]!=b'WEBP':
            raise ValueError(f'Unhydrated picker hero: {source}; pull its Git LFS object')
        target=destination/'public'/source.relative_to(source_root)
        if target.exists() and digest(target.read_bytes())!=digest(data):
            raise ValueError(f'Preserved changed picker hero: {target}')
    for source in files:
        target=destination/'public'/source.relative_to(source_root)
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():target.write_bytes(source.read_bytes())
    print(f'Staged {len(files)} picker heroes in {destination / "public"}')

def init_env():
    env_dir=DEST/'env';env_dir.mkdir(parents=True,exist_ok=True)
    backend=env_dir/'backend.env';frontend=env_dir/'frontend/.env'
    if backend.exists() or frontend.exists():raise ValueError('Private configuration already exists; edit it rather than overwriting it.')
    password=secrets.token_urlsafe(18);dbpass=secrets.token_urlsafe(24);storepass=secrets.token_urlsafe(24)
    values={
      'POSTGRES_PASSWORD':dbpass,'DATABASE_URL':f'postgresql+asyncpg://validation:{dbpass}@db:5432/cityprompt_validation_20260924',
      'DATABASE_URL_SYNC':f'postgresql://validation:{dbpass}@db:5432/cityprompt_validation_20260924',
      'REDIS_URL':'redis://redis:6379/0','S3_ENDPOINT_URL':'http://media:9000',
      'S3_BUCKET_NAME':'cityprompt-validation-20260924','S3_ACCESS_KEY':'validation-local',
      'S3_SECRET_KEY':storepass,'JWT_SECRET_KEY':secrets.token_urlsafe(48),
      'VALIDATION_STUDENT_EMAIL':'student-validation@example.com','VALIDATION_STUDENT_PASSWORD':password,
      'GOOGLE_MAPS_API_KEY':os.environ.get('GOOGLE_MAPS_API_KEY',''),
      'ALLOWED_ORIGINS':'http://127.0.0.1:5180,http://localhost:5180',
    }
    backend.write_text(''.join(f'{k}={v}\n' for k,v in values.items()))
    frontend.parent.mkdir(parents=True,exist_ok=True)
    frontend.write_text('VITE_API_URL=\nVITE_GOOGLE_MAPS_API_KEY='+os.environ.get('VITE_GOOGLE_MAPS_API_KEY','')+'\nVITE_MAPBOX_TOKEN='+os.environ.get('VITE_MAPBOX_TOKEN','')+'\n')
    try:backend.chmod(0o600);frontend.chmod(0o600)
    except OSError:pass
    print('Private environment created under .validation/env. Supply map keys there if absent.')
    print('Local-only login: student-validation@example.com')
    print('Local-only password: '+password)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['unpack','init-env','sync-picker-heroes']);p.add_argument('--destination',type=Path,default=DEST)
    args=p.parse_args()
    if args.command=='unpack':unpack(args.destination)
    elif args.command=='sync-picker-heroes':sync_picker_heroes(args.destination)
    else:init_env()
