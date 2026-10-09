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
PICKER_HERO_MANIFEST = ROOT / 'frontend/src/data/catalogueHeroImages.json'

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

def _picker_hero_path(url):
    if not isinstance(url, str):
        raise ValueError(f'Unsafe picker hero path: {url!r}')
    path=PurePosixPath(url)
    if (not url.startswith('/') or '\\' in url or ':' in url or '%' in url
            or '?' in url or '#' in url or '..' in path.parts
            or str(path)!=url or len(path.parts)!=5 or path.parts[1]!='archetypes'
            or path.parts[2] not in PICKER_HERO_DOMAINS
            or path.parts[3]!='classroom-heroes' or path.suffix!='.webp'):
        raise ValueError(f'Unsafe picker hero path: {url!r}')
    return Path(*path.parts[1:])


def _verify_picker_webp(data, source):
    if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
        raise ValueError(f'Unhydrated picker hero: {source}; pull its Git LFS object')
    if (len(data)<20 or data[:4]!=b'RIFF' or data[8:12]!=b'WEBP'
            or int.from_bytes(data[4:8], 'little')!=len(data)-8):
        raise ValueError(f'Invalid WebP picker hero: {source}')
    offset=12
    image_found=False
    while offset<len(data):
        if offset+8>len(data):
            raise ValueError(f'Invalid WebP picker hero: {source}')
        kind=data[offset:offset+4]
        size=int.from_bytes(data[offset+4:offset+8], 'little')
        payload=data[offset+8:offset+8+size]
        offset+=8+size+(size%2)
        if offset>len(data):
            raise ValueError(f'Invalid WebP picker hero: {source}')
        if kind==b'VP8 ':
            image_found=len(payload)>=10 and payload[3:6]==b'\x9d\x01\x2a'
        elif kind==b'VP8L':
            image_found=len(payload)>=5 and payload[0]==0x2f
    if not image_found:
        raise ValueError(f'Invalid WebP picker hero: {source}')


def sync_picker_heroes(destination=DEST, source_root=ROOT / 'frontend/public', manifest_path=None):
    """Stage the small, curated picker views beside the locked runtime packet.

    Never overwrite a locally changed staged image; the source and destination
    must agree byte-for-byte on repeated runs.
    """
    source_root=Path(source_root).resolve()
    destination=Path(destination)
    manifest_path=Path(manifest_path) if manifest_path is not None else PICKER_HERO_MANIFEST
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    if not isinstance(manifest,dict) or not manifest:
        raise ValueError('Picker hero manifest must be a non-empty placement-to-URL mapping')
    # Other reference photos are delivered by the existing public/runtime asset
    # pipeline; this supplement owns only the classroom hero directories.
    if any(not isinstance(url,str) for url in manifest.values()):
        raise ValueError('Unsafe picker hero path: manifest URLs must be strings')
    required={_picker_hero_path(url) for url in manifest.values() if '/classroom-heroes/' in url}
    for path in required:
        source=source_root/path
        if not source.resolve().is_relative_to(source_root):
            raise ValueError(f'Unsafe picker hero source: {source}')
        if not source.is_file():
            raise ValueError(f'Missing required picker hero: {source}')
    # Retain inactive/legacy views too: saved or older clients can still use them.
    files=sorted(path for domain in PICKER_HERO_DOMAINS
                 for path in (source_root/'archetypes'/domain/'classroom-heroes').glob('*.webp'))
    for source in files:
        if not source.resolve().is_relative_to(source_root):
            raise ValueError(f'Unsafe picker hero source: {source}')
        data=source.read_bytes()
        _verify_picker_webp(data, source)
        target=destination/'public'/source.relative_to(source_root)
        if not target.resolve().is_relative_to((destination/'public').resolve()):
            raise ValueError(f'Unsafe picker hero destination: {target}')
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
