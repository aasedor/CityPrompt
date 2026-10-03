"""Portable private validation DB/bootstrap; never targets the local production app."""
from __future__ import annotations
import hashlib,json,os,sys,uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT/'backend');sys.path.insert(0,str(ROOT/'backend'))
from dotenv import load_dotenv
load_dotenv(ROOT/'.validation/env/backend.env',override=False)
os.environ.update(APP_ENV='development',APP_DEBUG='false',CLASSROOM_RELEASE='false',DIRECT_3D_JOBS_ENABLED='false',DIRECT_3D_IMAGES_ENABLED='false',MASTER_PLANNER_ENABLED='false',DESIGN_DIRECTOR_ENABLED='false',FRONTEND_URL='http://127.0.0.1:5180')
for key in ('OPENAI','OPENAI_API_KEY','GEMINI_API_KEY','ANTHROPIC_API_KEY','VERTEX_AI_PROJECT','GOOGLE_APPLICATION_CREDENTIALS','FAL_KEY','MESHY_API_KEY','TRIPO_API_KEY','STABILITY_API_KEY','SENTRY_DSN','SMTP_USER','SMTP_PASSWORD','GOOGLE_CLIENT_ID','GOOGLE_CLIENT_SECRET','MICROSOFT_CLIENT_ID','MICROSOFT_CLIENT_SECRET'):
    os.environ[key]=''
from app.core import config
config._dotenv.clear();config.Settings.model_config['env_file']=None;config.get_settings.cache_clear()
settings=config.get_settings()
if not settings.database_url.endswith('/cityprompt_validation_20260924') or settings.s3_bucket_name!='cityprompt-validation-20260924':
    raise ValueError('Use only the named dedicated validation database and bucket.')

def seed():
    from sqlalchemy import create_engine,select
    from sqlalchemy.orm import Session
    from app.models.models import User,ModelLibraryEntry
    from app.core.security import hash_password
    from app.services.render_attempt_storage import _client
    from app.services.lego_assembly import descriptor_from_library_entry
    password=os.environ['VALIDATION_STUDENT_PASSWORD'];email=os.environ['VALIDATION_STUDENT_EMAIL']
    client,bucket=_client()
    if not any(b['Name']==bucket for b in client.list_buckets()['Buckets']):client.create_bucket(Bucket=bucket)
    rows=json.loads((ROOT/'seed/validation/model-bindings.json').read_text())
    # Preflight the complete batch before any model writes.
    for row in rows:
        data=(ROOT/'.validation'/row['path']).read_bytes()
        if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Model packet hash mismatch')
    with Session(create_engine(settings.database_url_sync)) as db:
        account=db.scalar(select(User).where(User.email==email))
        if account is None:
            account=User(id=uuid.uuid4(),email=email,full_name='Catalogue Student',hashed_password=hash_password(password),role='editor',is_active=True,render_credits=0)
            db.add(account);db.flush()
        for row in rows:
            key=row['url'].removeprefix('/api/v1/files/');data=(ROOT/'.validation'/row['path']).read_bytes()
            from botocore.exceptions import ClientError
            try:
                remote=client.get_object(Bucket=bucket,Key=key)['Body'].read()
                if hashlib.sha256(remote).hexdigest()!=row['sha256']:raise ValueError('Existing stored object differs; refusing overwrite')
            except ClientError as exc:
                if exc.response['Error']['Code'] not in ('NoSuchKey','404','NotFound'):raise
                client.put_object(Bucket=bucket,Key=key,Body=data,ContentType='model/gltf-binary')
            assert hashlib.sha256(client.get_object(Bucket=bucket,Key=key)['Body'].read()).hexdigest()==row['sha256']
            mid=uuid.uuid5(uuid.NAMESPACE_URL,'validation/'+row['sha256']);existing=db.get(ModelLibraryEntry,mid)
            if existing:
                if existing.model_url!=row['url'] or existing.metadata_!=row['metadata']:raise ValueError('Existing binding differs; refusing overwrite')
                continue
            model=ModelLibraryEntry(id=mid,owner_id=account.id,name=row['title'],category='building',model_url=row['url'],lod_urls={'0':row['url']},generation_engine='rlasm',is_public=True,tags=['validation-only',row['variant']],metadata_=row['metadata'])
            assert descriptor_from_library_entry(model) is not None,row['variant']
            db.add(model)
        db.commit()
    print('12 exact model bindings verified; no design scenes or geometry seeded.')

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='bootstrap':
        from alembic.config import Config
        from alembic import command
        command.upgrade(Config('alembic.ini'),'head');seed()
    elif mode=='seed':seed()
    elif mode=='serve':
        import uvicorn
        from app.main import app
        uvicorn.run(app,host=os.environ.get('VALIDATION_BIND_HOST','127.0.0.1'),port=int(os.environ.get('VALIDATION_API_PORT','8006')),access_log=False)
