"""Independent scene furniture, stored in project metadata (not fake site zones)."""
import uuid
import json
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import check_project_permission, require_auth
from app.models.models import Project, User

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

    @field_validator('variant')
    @classmethod
    def known_prop(cls, value):
        if value not in _DETAIL_MODELS['props']:
            raise ValueError('Unknown detail model')
        return value


class DetailUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_revision: int = Field(ge=0)
    benches: list[Bench] = Field(max_length=256)
    trees: list[Tree] | None = Field(default=None, max_length=256)
    props: list[Prop] | None = Field(default=None, max_length=256)

    @model_validator(mode='after')
    def unique_ids(self):
        items = [*self.benches, *(self.trees or []), *(self.props or [])]
        if len({item.id for item in items}) != len(items):
            raise ValueError('Detail IDs must be unique')
        return self


class DetailResponse(BaseModel):
    version: Literal[1] = 1
    revision: int
    benches: list[Bench]
    trees: list[Tree] = Field(default_factory=list)
    props: list[Prop] = Field(default_factory=list)
    can_edit: bool


def detail_data(project):
    return (project.metadata_ or {}).get('scene_details') or {'version':1,'revision':0,'benches':[]}


@router.get('/{project_id}/details', response_model=DetailResponse)
async def get_details(project_id: uuid.UUID, user: User = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    permission = await check_project_permission(project_id, user, db, required='viewer')
    project = (await db.execute(select(Project).where(Project.id == project_id))).scalar_one_or_none()
    if project is None:
        raise HTTPException(404, 'Project not found')
    return {**detail_data(project), 'can_edit':permission in {'owner','editor'}}


@router.put('/{project_id}/details', response_model=DetailResponse)
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
    saved['props'] = ([prop.model_dump() for prop in request.props]
                      if request.props is not None else current.get('props', []))
    items = [*saved['benches'], *saved['trees'], *saved['props']]
    if len({item['id'] for item in items}) != len(items):
        raise HTTPException(422, 'Detail IDs must be unique')
    project.metadata_ = {**(project.metadata_ or {}), 'scene_details':saved}
    await db.flush()
    return {**saved,'can_edit':True}
