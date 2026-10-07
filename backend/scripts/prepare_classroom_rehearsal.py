"""Provision forty disposable API-read fixtures in an explicitly isolated local DB.

Run after the dedicated local environment is loaded. No normal application DB,
existing project, credential, paid credit balance or geometry is modified.
The private session file is external evidence and must never be committed.
"""
import argparse
import asyncio
import json
from pathlib import Path
import uuid

from sqlalchemy.engine import make_url
from geoalchemy2 import WKTElement
from app.core.config import get_settings
from app.core.database import async_session_factory, engine
from app.core.security import create_access_token
from app.models.models import Project, SiteZone, User


async def prepare(database_name, output, base_url):
    url = make_url(get_settings().database_url)
    if url.host not in ('127.0.0.1', 'localhost') or url.database != database_name or not database_name.startswith(('cityprompt_load_', 'cityprompt_repairs_')):
        raise ValueError('Fixtures require an explicitly named isolated local load/repair database')
    if base_url not in ('http://127.0.0.1:8009', 'http://localhost:8009'):
        raise ValueError('Local fixture tokens are limited to the dedicated local API on 8009')
    namespace = uuid.UUID('a1ed6812-1281-4cde-b339-3d51458c43db')
    sessions = []
    async with async_session_factory() as db:
        for index in range(40):
            user_id = uuid.uuid5(namespace, f'user-{index}')
            project_id = uuid.uuid5(namespace, f'project-{index}')
            user = await db.get(User, user_id)
            if user is None:
                user = User(id=user_id, email=f'cityprompt-load-{index+1:02}@example.invalid', full_name=f'Local simulated student {index+1:02}', role='editor', render_credits=0)
                db.add(user); await db.flush()
                db.add(Project(id=project_id, owner_id=user_id, name=f'Disposable classroom load fixture {index+1:02}', status='draft'))
                await db.flush()
                for zone_index in range(16):
                    lng = -114.129 + (zone_index % 4) * .0003; lat = 51.014 + (zone_index // 4) * .0003
                    polygon = f'POLYGON(({lng} {lat},{lng+.0002} {lat},{lng+.0002} {lat+.0002},{lng} {lat+.0002},{lng} {lat}))'
                    db.add(SiteZone(project_id=project_id, zone_type='building', name=f'Load fixture zone {zone_index+1}', geometry=WKTElement(polygon, srid=4326), color='#aacc88', sort_order=zone_index,
                                    properties={'height_m': 12, 'floors': 3, 'load_test_fixture': True}))
            else:
                project = await db.get(Project, project_id)
                if user.email != f'cityprompt-load-{index+1:02}@example.invalid' or user.role != 'editor' or not project or project.owner_id != user_id:
                    raise ValueError('Existing fixture identity differs; preserve it and use a new isolated DB')
            sessions.append({'user_id': str(user_id), 'project_id': str(project_id), 'token': create_access_token(str(user_id), 'editor')})
        await db.commit()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'base_url': base_url, 'minimum_zones': 16, 'sessions': sessions}) + '\n', encoding='utf-8')
    print(f'Prepared 40 isolated accounts/projects with 16 read-only load zones each; private sessions saved outside Git.')
    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--base-url', default='http://127.0.0.1:8009')
    args = parser.parse_args()
    # Refuse a private token file inside the checkout.
    if Path(__file__).resolve().parents[2] in args.output.resolve().parents:
        parser.error('Keep the private session file outside the source checkout')
    asyncio.run(prepare(args.database, args.output, args.base_url))


if __name__ == '__main__': main()
