"""Private discovery and explicit reuse of completed student-generated models."""
import uuid
from urllib.parse import unquote, urlsplit

import boto3
from botocore.config import Config
from fastapi import HTTPException
from sqlalchemy import select
from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.models.models import Building, Project


def is_user_generated(building: Building) -> bool:
    specs = building.specifications or {}
    reused = specs.get('user_generated_model') or {}
    if reused:
        return reused.get('catalogue_entry') is True
    return bool(specs.get('photo_generation') or building.generation_engine in ('meshy', 'tripo'))


def generated_entry(building: Building) -> dict:
    specs = building.specifications or {}
    references = (specs.get('photo_generation') or {}).get('reference_keys') or []
    preview = (specs.get('user_generated_model') or {}).get('preview_url')
    return {'id': str(building.id), 'project_id': str(building.project_id),
            'name': building.name or 'My generated building',
            'preview_url': preview or (f'/api/v1/files/{references[0]}' if references else building.preview_url),
            'floor_count': building.floor_count, 'height_meters': float(building.height_meters or 6)}


def copy_generated_file(source: str, destination: str) -> str:
    settings = get_settings()
    url = urlsplit(source)
    endpoint = urlsplit(settings.s3_endpoint_url)
    if not url.netloc and url.path.startswith('/api/v1/files/'):
        key = unquote(url.path[len('/api/v1/files/'):])
    elif url.netloc == endpoint.netloc and url.path.startswith(f'/{settings.s3_bucket_name}/'):
        key = unquote(url.path[len(settings.s3_bucket_name) + 2:])
    else:
        raise HTTPException(status_code=422, detail='This model needs to be saved to City Prompt storage before it can be reused.')
    client = boto3.client('s3', endpoint_url=settings.s3_endpoint_url,
                         aws_access_key_id=settings.s3_access_key, aws_secret_access_key=settings.s3_secret_key,
                         region_name=settings.s3_region, config=Config(signature_version='s3v4'))
    client.copy_object(Bucket=settings.s3_bucket_name, CopySource={'Bucket': settings.s3_bucket_name, 'Key': key}, Key=destination)
    return f'/api/v1/files/{destination}'


async def attach_generated_model(db, zone, user, source_id):
    """Called within normal zone creation, including its fit checks and transaction."""
    if zone.zone_type != 'building':
        raise HTTPException(status_code=422, detail='User generated models need a building footprint.')
    try:
        source_id = uuid.UUID(str(source_id))
    except ValueError:
        raise HTTPException(status_code=422, detail='Choose a valid user generated model.') from None
    result = await db.execute(select(Building).join(Project, Building.project_id == Project.id).where(
        Building.id == source_id, Project.owner_id == user.id))
    source = result.scalar_one_or_none()
    if not source or not is_user_generated(source):
        raise HTTPException(status_code=404, detail='This user generated model is not in your account.')
    if source.generation_status != 'completed' or not source.model_url:
        raise HTTPException(status_code=409, detail='This model is still being prepared. Try again when it is complete.')
    building_id = uuid.uuid4()
    key = f'projects/{zone.project_id}/models/{building_id}_user.glb'
    try:
        model_url = await run_in_threadpool(copy_generated_file, source.model_url, key)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail='The saved model could not be copied. Your new placement was not saved; please retry.') from exc
    building = Building(id=building_id, project_id=zone.project_id, name=source.name,
        footprint=zone.geometry, model_url=model_url, generation_status='completed',
        generation_engine=source.generation_engine, height_meters=source.height_meters,
        floor_count=source.floor_count, floor_height_meters=source.floor_height_meters,
        specifications={'user_generated_model': {'version': 1, 'source_building_id': str(source.id),
            'catalogue_entry': False, 'model_url': model_url}})
    db.add(building)
    await db.flush()
    zone.building_id = building.id
    zone.building_ids = [str(building.id)]
    zone.name = source.name
    zone.properties = {**(zone.properties or {}), 'user_generated_source_id': str(source.id),
        'native_plot_axes': True,
        'height': float(source.height_meters or 6), 'floor_count': source.floor_count or 2,
        'floors': source.floor_count or 2}
    return building


def has_user_generated_binding(zone, building) -> bool:
    marker = (building.specifications or {}).get('user_generated_model') if building else None
    return bool(marker and building.generation_status == 'completed' and building.model_url
        and marker.get('source_building_id') == (zone.properties or {}).get('user_generated_source_id')
        and marker.get('model_url') == building.model_url)
