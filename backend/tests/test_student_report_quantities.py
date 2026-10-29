"""Classroom totals must distinguish saved objects, estimates and missing data."""
from types import SimpleNamespace
import uuid

import pytest

from tests.test_student_report import zone, rectangle, snapshot, values
from app.services.student_report import analyze_snapshot, report_html


def building(**specifications):
    return SimpleNamespace(id=uuid.uuid4(), name="Model", footprint=rectangle(),
                           floor_count=2, height_meters=6, specifications=specifications)


def test_quantities_count_linked_buildings_once_and_keep_ground_out_of_development():
    model = building()
    a, b = zone('building', floor_count=2), zone('building', floor_count=2)
    a.building_id = b.building_id = model.id
    ground = zone('development_area', ground_surface_material='grass')
    report = analyze_snapshot(snapshot([zone('site_boundary'), a, b, ground, zone('green_space'), zone('road')], [model]))
    result = values(report)
    assert result['building_count'] == 1
    assert result['park_count'] == result['street_count'] == result['ground_surface_count'] == 1
    assert result['development_land_m2'] == 0
    assert result['ground_surface_area_m2'] > 7000
    assert result['gfa_ft2'] == pytest.approx(result['gfa_m2'] * 10.7639104167, abs=.06)


def test_retail_is_recorded_units_never_an_area_yield_and_incomplete_values_remain_visible():
    plan = snapshot([zone('building', development_type='commercial', floor_count=3, retail_unit_count=4),
                     zone('building', development_type='mixed_use', floor_count=5)])
    report = analyze_snapshot(plan)
    row = next(m for m in report['metrics'] if m['key'] == 'retail_units')
    assert row['value'] == 4
    assert 'incomplete' in row['label'].lower()
    assert '1' in row['derivation'] and 'unknown' in row['derivation'].lower()
    next(z['properties'] for z in plan['zones'] if 'retail_unit_count' in z['properties']).pop('retail_unit_count')
    assert values(analyze_snapshot(plan))['retail_units'] is None


@pytest.mark.parametrize('invalid', [True, -1, 2.5, 'NaN', float('inf')])
def test_invalid_retail_counts_do_not_become_quantities(invalid):
    assert values(analyze_snapshot(snapshot([zone('building', development_type='commercial', retail_unit_count=invalid)])))['retail_units'] is None


def test_zero_is_valid_and_linked_unit_specs_are_used_once_instead_of_parent_zone_estimates():
    model = building(residential_units=12, retail_units=0)
    a, b = zone('building', development_type='mixed_use', unit_count=99), zone('development_area', development_type='mixed_use')
    a.building_id = b.building_id = model.id
    result = values(analyze_snapshot(snapshot([a, b], [model])))
    assert result['residential_units'] == 12
    assert result['retail_units'] == 0


def test_no_geometry_retains_unknown_site_area_and_does_not_claim_zero_floor_area():
    invalid = zone('building', development_type='residential')
    invalid.geometry = None
    result = values(analyze_snapshot(snapshot([invalid])))
    assert result['building_count'] == 1
    assert result['gfa_m2'] is None
    assert result['gfa_ft2'] is None
    assert result['site_area_m2'] is None
    assert result['residential_units'] is None


def test_commercial_legacy_unit_count_does_not_become_housing_and_shared_zone_yield_is_not_repeated():
    a, b = building(), building()
    development = zone('development_area', development_type='residential', unit_count=30)
    development.building_ids = [a.id, b.id]
    plan = snapshot([development, zone('building', development_type='commercial', unit_count=999)], [a, b])
    result = values(analyze_snapshot(plan))
    assert result['building_count'] == 3
    assert result['residential_units'] == 30


def test_invalid_park_geometry_is_unknown_and_whole_project_details_survive_snapshot():
    park = zone('green_space')
    park.geometry = None
    result = values(analyze_snapshot(snapshot([zone('site_boundary'), park])))
    assert result['park_count'] == 1
    assert result['park_area_m2'] is None
    plan = snapshot([])
    plan['scene_details'] = {'benches': [{'id': 'bench'}], 'trees': [], 'props': [{'id': 'person'}, {'id': 'bin'}], 'surfaces': []}
    result = values(analyze_snapshot(plan))
    assert result['detail_benches'] == 1 and result['detail_props'] == 2


def test_quantitative_export_has_no_unanswered_student_questions():
    plan = snapshot([zone('residential', floor_count=3)])
    report = dict(id='r', project_name='Site', plan_version='v', created_at='today', requested_by_name='Student',
                  is_stale=False, analysis=analyze_snapshot(plan), decisions={}, response_revision=0)
    output = report_html(report, plan, [])
    assert 'Student response: not yet recorded' not in output
    assert 'Suggested next step:' not in output
    assert 'Buildings' in output and 'ft²' in output


def test_native_bungalow_programme_resolves_units_and_pending_warning_without_inventing_floor_area():
    props = dict(pick_place_asset='trial_postwar_bungalow', development_selected_variant_id='bungalow_postwar_ranch',
                 development_archetype_id='calgary_inner_city_bungalow', pick_place_model_revision='calgary-inner-city-bungalow-clay-v005',
                 floor_count=1, building_geometry_basis='placement_plot', pick_place_automatic_3d=True)
    report = analyze_snapshot(snapshot([zone('building', **props)]))
    result = values(report)
    assert result['residential_units'] == 1
    assert result['retail_units'] == 0
    assert result['gfa_m2'] is None and result['gfa_ft2'] is None
    assert result['detached_plots_pending'] == 0
    assert any('single-home' in source['title'].lower() for finding in report['findings'] for source in finding['sources'])


