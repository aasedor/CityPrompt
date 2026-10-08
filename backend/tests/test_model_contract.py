from types import SimpleNamespace

from app.api.v1.lego_assembly import _planned_massing_dimensions
from app.services.model_contract import native_model_facts, uses_placement_plot
from app.services.model_contract import catalogue_dwellings

CURRENT = {'pick_place_asset': 'validation_minimalist_infill_brick_monolith',
           'development_selected_variant_id': 'minimalist_infill_brick_monolith',
           'pick_place_model_revision': '97f91c15feddd9c2bf0595f61266aa08fa85cb140f70cd2271ff75d3a33f1de7'}


def test_catalogue_programme_requires_unchanged_height_storeys_and_revision():
    from app.services.model_contract import _records
    row = next(row for row in _records() if row['variant_id'] == 'affordable_aspen_original' and row['current'])
    properties = {'pick_place_asset': row['asset_id'], 'development_selected_variant_id': row['variant_id'],
                  'pick_place_model_revision': row['revision'], 'floor_count': row['storeys']}
    assert catalogue_dwellings(properties) == 12
    assert catalogue_dwellings({**properties, 'floor_count': row['storeys'] + 1}) is None
    assert catalogue_dwellings({**properties, 'development_height_override_m': 100}) is None
    assert catalogue_dwellings({**properties, 'pick_place_model_revision': 'unreviewed'}) is None


def test_exact_model_overrules_generic_height_without_rewriting_zone():
    properties = {**CURRENT, 'height': 30, 'floors': 2}
    floors, height = _planned_massing_dimensions(SimpleNamespace(properties=properties))
    assert floors == 2 and height == 10.68
    assert properties['height'] == 30
    assert uses_placement_plot(properties)


def test_saved_revision_and_unknown_revision_are_distinct():
    old = {**CURRENT, 'pick_place_model_revision': '3c7ab81c4db3c2a67ec280788ff84008da0cbd20a16129feba75dffcfcd0d4a6'}
    assert native_model_facts(old)['dimensions_m'][2] == 10.479999542236328
    assert native_model_facts({**CURRENT, 'pick_place_model_revision': 'missing'}) is None
    assert native_model_facts({k: v for k, v in CURRENT.items() if k != 'pick_place_model_revision'})['revision'] == CURRENT['pick_place_model_revision']


def test_explicit_procedural_height_is_preserved():
    zone = SimpleNamespace(properties={**CURRENT, 'development_height_override_m': 20, 'height_m': 20, 'floors': 4})
    assert native_model_facts(zone.properties) is None
    assert _planned_massing_dimensions(zone) == (4, 20)


def test_invalid_measurement_binding_is_unavailable_instead_of_crashing(monkeypatch):
    from app.services import model_contract
    monkeypatch.setattr(model_contract, '_records', lambda: ({'asset_id': CURRENT['pick_place_asset'],
        'variant_id': CURRENT['development_selected_variant_id'], 'revision': CURRENT['pick_place_model_revision'],
        'dimensions_m': None, 'current': True},))
    assert native_model_facts({**CURRENT, 'development_height_override_m': 30}) is None
