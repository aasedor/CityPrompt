"""Finite local parkade seeding wrapper; refuses non-pilot databases/storage."""
import argparse,json,os,runpy,sys
from pathlib import Path
from urllib.parse import urlsplit
from dotenv import load_dotenv
import sqlalchemy as sa
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))


def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--apply',action='store_true');g.add_argument('--verify',action='store_true');a=p.parse_args()
    load_dotenv(ROOT/'backend/.env',override=True)
    db=urlsplit(os.environ['DATABASE_URL_SYNC']);storage=urlsplit(os.environ['S3_ENDPOINT_URL'])
    if db.hostname not in ('127.0.0.1','localhost') or db.path!='/cityprompt_repairs_20261004' or db.port!=55432:raise ValueError('Refuse database outside isolated local pilot')
    if storage.hostname not in ('127.0.0.1','localhost') or storage.port!=19003:raise ValueError('Refuse storage outside local pilot')
    if not a.verify:
        with sa.create_engine(os.environ['DATABASE_URL_SYNC']).connect() as conn:
            owners=conn.execute(sa.text('select id from users where full_name=:name'),dict(name='Animation browser QA')).scalars().all()
        if len(owners)!=1:raise ValueError('Exactly one existing local QA owner required')
        os.environ['MODEL_LIBRARY_SEED_OWNER_ID']=str(owners[0])
    manifest=ROOT/'seed/parkade-family-trial/library.json';payload=json.loads(manifest.read_text())
    sys.argv=['seed_model_library','--rlasm-clay-only','--clay-library',str(manifest),'--local-trial']
    for entry in payload['entries']:sys.argv+=['--candidate',entry['candidate']]
    if a.verify:sys.argv+=['--verify']
    elif not a.apply:sys.argv+=['--dry-run']
    runpy.run_module('tools.seed_model_library',run_name='__main__')


if __name__=='__main__':main()
