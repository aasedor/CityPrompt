"""Independent scene furniture, stored in project metadata (not fake site zones)."""
import uuid
import json
import math
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shapely.geometry import Point, Polygon

from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import Project, User
from app.services.people_actions import PeopleAction, is_people_model, resolve_people_action

router = APIRouter()


class Bench(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    id: str = Field(pattern=r'^[\w-]{1,80}$')
    lng: float = Field(ge=-180, le=180)
    lat: float = Field(ge=-85, le=85)
    angle: float = Field(ge=-360, le=360)


# Shipped registry, never a client-provided model URL. Mirrored catalogue coverage
# is checked against frontend metadata by test_project_details.py.
_DETAIL_MODELS = json.loads((Path(__file__).resolve().parents[2] / 'data/project_detail_models.json').read_text())

class Tree(Bench):
    variant: str

    @field_validator('variant')
    @classmethod
    def known_tree(cls, value):
        if value not in _DETAIL_MODELS['trees']:
            raise ValueError('Unknown tree model')
        return value

class Prop(Bench):
    variant: str
    support_zone_id: str | None = Field(default=None, pattern=r'^[\w-]{1,80}$')
    people_action: PeopleAction | None = None

    @model_validator(mode='after')
    def action_requires_person(self):
        if self.people_action is not None and not is_people_model(self.variant):
            raise ValueError('People actions require a people model')
        if is_people_model(self.variant):
            resolved = resolve_people_action(self.variant, self.people_action)
            # Legacy people omit synthetic defaults; fixed seated assets must not
            # round-trip as standing through older clients that omit the field.
            if self.people_action is not None or self.variant.startswith('people-inclusive-'):
                self.people_action = resolved
        return self

    @field_validator('variant')
    @classmethod
    def known_prop(cls, value):
        if value not in _DETAIL_MODELS['props']:
            raise ValueError('Unknown detail model')
        return value


class ParkingDriveway(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    version: Literal[1]
    source: Literal['manual', 'mapped', 'authored']
    roadPoint: tuple[float, float]
    streetId: str | None = Field(default=None, pattern=r'^[\w:./-]{1,160}$')

    @model_validator(mode='after')
    def valid_target(self):
        x, y = self.roadPoint
        if not (-180 <= x <= 180 and -85 <= y <= 85):
            raise ValueError('Use a valid road edge')
        if self.source != 'manual' and not self.streetId:
            raise ValueError('Choose a road identity for a linked driveway')
        return self


class ParkingRecipe(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    version: Literal[1]
    rowAngle: Literal[0, 90]
    driveway: ParkingDriveway | None = None


class PavingSurface(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    id: str = Field(pattern=r'^[\w-]{1,80}$')
    material: Literal['concrete', 'brick', 'asphalt']
    coordinates: list[tuple[float, float]] = Field(min_length=3, max_length=64)
    parking: ParkingRecipe | None = None

    @model_validator(mode='after')
    def bounded_parking(self):
        if self.parking is not None:
            x0, y0 = self.coordinates[0]
            sx = 111320 * math.cos(math.radians(y0))
            points = [((x-x0)*sx,(y-y0)*111320) for x,y in self.coordinates]
            if Polygon(points).area > 15000:
                raise ValueError('Split parking lots larger than 15,000 square metres')
            if self.parking.driveway:
                x,y = self.parking.driveway.roadPoint
                road_point = ((x-x0)*sx,(y-y0)*111320)
                if Polygon(points).distance(Point(road_point)) > 60:
                    raise ValueError('Choose a road edge within 60 metres of the lot')
        return self

    @field_validator('coordinates')
    @classmethod
    def valid_polygon(cls, points):
        if any(not (-180 <= x <= 180 and -85 <= y <= 85) for x, y in points):
            raise ValueError('Use valid map coordinates')
        x0, y0 = points[0]
        sx = 111320 * math.cos(math.radians(y0))
        local = [((x-x0)*sx, (y-y0)*111320) for x, y in points]
        polygon = Polygon(local)
        if not polygon.is_valid or not 1 <= polygon.area <= 250000:
            raise ValueError('Draw a non-crossing paved area between 1 and 250,000 square metres')
        if any(math.dist(p, local[(i+1) % len(local)]) < .25 for i, p in enumerate(local)):
            raise ValueError('Leave space between neighbouring corners')
        if max(p[0] for p in local)-min(p[0] for p in local) > 2000 or max(p[1] for p in local)-min(p[1] for p in local) > 2000:
            raise ValueError('Keep each paved area within 2 km')
        return points


class DetailUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    benches: list[Bench] = Field(max_length=256)
    trees: list[Tree] | None = Field(default=None, max_length=256)
    props: list[Prop] | None = Field(default=None, max_length=256)
    surfaces: list[PavingSurface] | None = Field(default=None, max_length=64)

    @model_validator(mode='after')
    def unique_ids(self):
        items = [*self.benches, *(self.trees or []), *(self.props or []), *(self.surfaces or [])]
        if len({item.id for item in items}) != len(items):
            raise ValueError('Detail IDs must be unique')
        return self


class DetailResponse(BaseModel):
    version: Literal[1] = 1
    revision: int
    benches: list[Bench]
    trees: list[Tree] = Field(default_factory=list)
    props: list[Prop] = Field(default_factory=list)
    surfaces: list[PavingSurface] = Field(default_factory=list)
    can_edit: bool


def detail_data(project):
    return (project.metadata_ or {}).get('scene_details') or {'version':1,'revision':0,'benches':[]}


@router.get('/{project_id}/details', response_model=DetailResponse,response_model_exclude_none=True)
async def get_details(project_id: uuid.UUID, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    permission = await check_project_permission(project_id, user, db, required='viewer')
    project = (await db.execute(select(Project).where(Project.id == project_id))).scalar_one_or_none()
    if project is None:
        raise HTTPException(404, 'Project not found')
    return {**detail_data(project), 'can_edit':permission in {'owner','editor'}}


@router.put('/{project_id}/details', response_model=DetailResponse,response_model_exclude_none=True)
async def save_details(project_id: uuid.UUID, request: DetailUpdate, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    await check_project_permission(project_id, user, db, required='editor')
    project = (await db.execute(select(Project).where(Project.id == project_id).with_for_update().execution_options(populate_existing=True))).scalar_one_or_none()
    if project is None:
        raise HTTPException(404, 'Project not found')
    current = detail_data(project)
    if request.expected_revision != current['revision']:
        raise HTTPException(409, 'Details were updated elsewhere. Your draft is still open. Close and reopen the editor to load the latest version before editing again.')
    saved = {'version':1,'revision':current['revision']+1,'benches':[bench.model_dump() for bench in request.benches]}
    saved['trees'] = ([tree.model_dump() for tree in request.trees]
                      if request.trees is not None else current.get('trees', []))
    saved['props'] = ([prop.model_dump(exclude_none=True) for prop in request.props]
                      if request.props is not None else current.get('props', []))
    saved['surfaces'] = ([surface.model_dump(mode='json', exclude_none=True) for surface in request.surfaces]
                         if request.surfaces is not None else current.get('surfaces', []))
    items = [*saved['benches'], *saved['trees'], *saved['props'], *saved['surfaces']]
    if len({item['id'] for item in items}) != len(items):
        raise HTTPException(422, 'Detail IDs must be unique')
    project.metadata_ = {**(project.metadata_ or {}), 'scene_details':saved}
    await db.flush()
    return {**saved,'can_edit':True}
