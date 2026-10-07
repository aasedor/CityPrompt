"""Install this finite batch using the running backend's loopback DB/storage settings."""
import argparse
import json
import os
from pathlib import Path
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',action='append');mode=p.add_mutually_exclusive_group()
    mode.add_argument('--apply',action='store_true');mode.add_argument('--verify',action='store_true')
    a=p.parse_args();root=Path(__file__).resolve().parents[2]
    sys.path[:0]=[str(root),str(root/'backend')]
    from app.core.config import get_settings
    s=get_settings()
    roster=json.loads((root/'frontend/src/data/communityBuildingBatch.json').read_text(encoding='utf-8'))['entries']
    allowed={row['candidate'] for row in roster};selected=a.candidate or sorted(allowed)
    if not selected or not set(selected)<=allowed:raise ValueError('Select only this reviewed finite batch')
    os.environ.update(S3_ENDPOINT_URL=s.s3_endpoint_url,S3_BUCKET_NAME=s.s3_bucket_name,
        S3_ACCESS_KEY=s.s3_access_key,S3_SECRET_KEY=s.s3_secret_key,DATABASE_URL_SYNC=s.database_url_sync)
    from tools.seed_model_library import main as seed
    args=['seed','--rlasm-clay-only','--local-trial']
    # Existing canonical seed ownership must already exist; explicit environment
    # override can target another existing local account without creating users.
    for candidate in selected:args+=['--candidate',candidate]
    if a.verify:args+=['--verify']
    elif not a.apply:args+=['--dry-run']
    sys.argv=args;return seed()

if __name__=='__main__':raise SystemExit(main())
