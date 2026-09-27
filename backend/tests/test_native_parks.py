import copy
import json
import math
from pathlib import Path

import pytest
from shapely.geometry import Polygon

from app.services.native_parks import registry, plan_native_park, native_park_identity
from app.services.public_realm_lego import plan_public_realm_zone_recipe, public_realm_recipe_identity, public_realm_fallback_marker
from app.services.residual_landscape import community_3d_source_hash, residual_landscape_source_hash, ResidualSourceZone, residual_occupied_geometry


def fixture(long=False):
    layout = next(p for p in registry()['layouts'] if p['id'] == ('basketball_court_v1--long-v1' if long else 'basketball_court_v1--native-v1'))
    lon, lat = -114.05, 51.04
    east = 111320 * math.cos(math.radians(lat))
    polygon = Polygon([(lon+x/east,lat+y/111320) for x,y in [(-46,-19.5),(46,-19.5),(46,19.5),(-46,19.5)]])
    props = {'green_space_archetype_id':layout['archetypeId'],'green_space_selected_variant_id':layout['variantId'],
             'green_space_native_layout':{'layout_id':layout['id'],'content_revision':layout['contentRevision'],
                                         'frame':{'longitude':lon,'latitude':lat,'yaw':0}}}
    return polygon,props


def test_shared_registry_is_byte_identical():
    root=Path(__file__).resolve().parents[2]
    assert (root/'backend/app/data/nativeParks.json').read_bytes()==(root/'frontend/src/data/nativeParks.json').read_bytes()


def test_native_recipe_round_trip_and_compiler_dispatch():
    polygon,props=fixture()
    recipe=plan_public_realm_zone_recipe('green_space',polygon,props,strict=True)
    assert recipe.schema_version==2
    assert public_realm_recipe_identity(json.loads(recipe.model_dump_json()))['recipe']==recipe.model_dump(mode='json')


@pytest.mark.parametrize('field,value',[('content_revision','0'*64),('mode','module_assembly'),('archetype_id','botanical_garden')])
def test_caller_cannot_replace_server_identity(field,value):
    polygon,props=fixture()
    recipe=plan_native_park(polygon,props).model_dump(mode='json')
    recipe[field]=value
    assert native_park_identity(recipe) is None


def test_layout_change_invalidates_source_and_requires_complete_fit():
    polygon,props=fixture()
    _,long_props=fixture(True)
    assert community_3d_source_hash('green_space',polygon,props)!=community_3d_source_hash('green_space',polygon,long_props)
    assert plan_native_park(polygon,long_props).layout_id.endswith('long-v1')
    small=Polygon([(x,y) for x,y in polygon.exterior.coords])
    from shapely.affinity import scale
    small=scale(small,xfact=52/92,yfact=1,origin='centroid')
    assert plan_native_park(small,props)
    with pytest.raises(ValueError,match='complete'):
        plan_native_park(small,long_props)


def test_holes_and_notches_are_not_bounding_box_fit():
    polygon,props=fixture(True)
    c=polygon.centroid
    hole=[(c.x-1e-5,c.y-1e-5),(c.x+1e-5,c.y-1e-5),(c.x+1e-5,c.y+1e-5),(c.x-1e-5,c.y+1e-5)]
    with pytest.raises(ValueError,match='complete'):
        plan_native_park(Polygon(polygon.exterior.coords,[hole]),props)
    altered=copy.deepcopy(props);altered['park_exclusion_rings']=[hole]
    with pytest.raises(ValueError,match='complete'):
        plan_native_park(polygon,altered)


def test_unknown_layout_never_falls_back_to_generic_park():
    polygon,props=fixture()
    props['green_space_native_layout']['layout_id']='unknown'
    with pytest.raises(ValueError,match='unavailable'):
        plan_public_realm_zone_recipe('green_space',polygon,props,strict=False)
    assert public_realm_fallback_marker('green_space',props) is None


def test_larger_native_parcel_keeps_surroundings_in_shared_landscape():
    polygon,props=fixture()
    selection=props['green_space_native_layout']
    source=ResidualSourceZone('park','park',polygon,native_selection=selection)
    occupied=residual_occupied_geometry(source)
    assert occupied.area / polygon.area == pytest.approx(52/92)
    before=residual_landscape_source_hash(polygon,[source])
    moved=copy.deepcopy(selection)
    moved['frame']['longitude']+=.00001
    assert residual_landscape_source_hash(polygon,[ResidualSourceZone('park','park',polygon,native_selection=moved)]) != before
    assert residual_occupied_geometry(ResidualSourceZone('legacy','park',polygon)).equals(polygon)
