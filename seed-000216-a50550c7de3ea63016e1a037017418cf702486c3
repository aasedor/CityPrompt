import io
import json
import re
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
import app.services.master_plan_2d as master_plan_2d
from geoalchemy2.shape import from_shape
from PIL import Image
from shapely.geometry import LineString, Polygon

from app.schemas.schemas import MasterPlan3DGenerateRequest
from app.services.master_plan_2d import _boundary_from_snapshot_zones, _build_ai_style_pass_prompt, _build_master_plan_3d_response, _compose_ai_style_pass, _generate_precinct_footprints, _park_program_geometries, _prepare_scene, _render_variant_assets, _sanitize_reference_metadata_bundle, _tree_points, _zone_snapshots_from_request


def _sample_payload():
    boundary = Polygon([
        (-114.0710, 51.0440),
        (-114.0690, 51.0440),
        (-114.0690, 51.0454),
        (-114.0710, 51.0454),
        (-114.0710, 51.0440),
    ])
    return {
        'boundary': boundary,
        'building_footprints': [
            {'geometry': Polygon([(-114.0707, 51.0442), (-114.0702, 51.0442), (-114.0702, 51.0446), (-114.0707, 51.0446), (-114.0707, 51.0442)]), 'name': 'Building A', 'properties': {'floors': 6}},
        ],
        'building_masses': [
            {'geometry': Polygon([(-114.0698, 51.0447), (-114.0693, 51.0447), (-114.0693, 51.0451), (-114.0698, 51.0451), (-114.0698, 51.0447)]), 'name': 'Building B', 'properties': {'floors': 3}},
        ],
        'roads': [
            {'geometry': LineString([(-114.0709, 51.04495), (-114.0691, 51.04495)]), 'kind': 'line', 'width_m': 8.0, 'properties': {'road_type': 'collector'}},
        ],
        'paths': [
            {'geometry': LineString([(-114.07055, 51.0441), (-114.07055, 51.0453)]), 'kind': 'path', 'width_m': 4.0, 'properties': {'road_type': 'pedestrian path'}},
        ],
        'parks': [
            {'geometry': Polygon([(-114.07095, 51.04405), (-114.0706, 51.04405), (-114.0706, 51.04445), (-114.07095, 51.04445), (-114.07095, 51.04405)]), 'name': 'Central Park', 'properties': {'tree_density_level': 'dense', 'tree_density': 0.3, 'has_paths': True}},
        ],
        'plazas': [
            {'geometry': Polygon([(-114.06945, 51.0441), (-114.06915, 51.0441), (-114.06915, 51.04435), (-114.06945, 51.04435), (-114.06945, 51.0441)]), 'name': 'Plaza', 'properties': {}},
        ],
        'water': [],
        'callouts': [
            {'geometry': Polygon([(-114.07095, 51.04405), (-114.0706, 51.04405), (-114.0706, 51.04445), (-114.07095, 51.04445), (-114.07095, 51.04405)]), 'name': 'Central Park', 'properties': {}},
        ],
        'context_buildings': [],
        'context_parks': [],
        'context_water': [],
        'context_roads': [],
        'buildable_zones': [],
        'prompt_zones': [
            {
                'zone_id': 'zone-1',
                'zone_type': 'building',
                'name': 'Housing Precinct',
                'color': '#9b59b6',
                'properties': {
                    'height': 30,
                    'floors': 10,
                    'description_text': 'Courtyard housing with strong park frontage',
                    'generation_style_input': {
                        'subtype': 'contemporary mid-rise residential',
                        'archetypeLabel': 'Contemporary Mid-Rise Residential',
                        'aestheticCategoryLabel': 'Urban Residential',
                        'styleProfile': {
                            'massing': 'perimeter courtyard massing',
                            'roofForm': 'contemporary urban roof expression',
                            'materials': ['brick', 'stone', 'glass'],
                            'facadeRhythm': 'regular punched-bay facade rhythm',
                            'windowStyle': 'deep-set vertically proportioned windows',
                            'publicRealm': 'walkable active edge with planting and seating',
                            'pavingType': 'unit paver forecourt paving',
                            'plantingType': 'allee trees and layered courtyard planting',
                        },
                    },
                },
            },
            {
                'zone_id': 'zone-2',
                'zone_type': 'green_space',
                'name': 'Garden Square',
                'color': '#27ae60',
                'properties': {
                    'description_text': 'Formal basin garden with promenade walks',
                    'generation_style_inputs': {
                        'parks': {
                            'subtype': 'formal garden square',
                            'aestheticCategoryLabel': 'Parisian Garden',
                            'styleProfile': {
                                'landscapeCharacter': 'formal civic garden composition',
                                'massing': 'formal garden composition with strong central symmetry',
                                'roofForm': 'light pavilion roof expression where structures occur',
                                'materials': ['stone', 'gravel', 'cast iron'],
                                'publicRealm': 'a designed civic landscape with promenades and seating',
                                'pavingType': 'stone and gravel promenade paving',
                                'plantingType': 'formal allee planting and clipped garden structure',
                            },
                        },
                    },
                },
            },
            {
                'zone_id': 'zone-3',
                'zone_type': 'road',
                'name': 'Main Promenade',
                'color': '#444444',
                'properties': {
                    'description_text': 'Primary pedestrian spine with premium paving',
                    'generation_style_inputs': {
                        'streets_paths': {
                            'subtype': 'pedestrian promenade',
                            'styleProfile': {
                                'corridorCharacter': 'ceremonial paseo public realm',
                                'surfaceType': 'stone banding and scored paving',
                            },
                        },
                    },
                },
            },
        ],
    }


def _toggles():
    return {
        'show_legend': True,
        'show_north_arrow': True,
        'show_scale_bar': True,
        'show_callout_markers': True,
        'show_surrounding_context': True,
    }


def test_variants_keep_geometry_locked_and_change_style_only():
    scene = _prepare_scene(_sample_payload(), 4200, _toggles())
    reference_metadata = [
        {
            'zone_id': 'zone-1',
            'zone_type': 'building',
            'source': 'archetype',
            'source_label': 'Building archetype',
            'category': 'urban_residential',
            'subcategory': 'contemporary_mid_rise_residential',
            'archetype_name': 'Contemporary Mid-Rise Residential',
            'image_url': 'https://example.com/archetype.png',
            'tags': ['brick', 'main street', 'landscape-led'],
        }
    ]

    version_a = _render_variant_assets('Renderer Test', scene, 'rendered_sales_plan', _toggles(), 'greener park', ['https://example.com/archetype.png'], reference_metadata, 'board_ready', 0, False, compose_board=False)
    version_b = _render_variant_assets('Renderer Test', scene, 'rendered_sales_plan', _toggles(), 'greener park', ['https://example.com/archetype.png'], reference_metadata, 'board_ready', 1, False, compose_board=False)

    boundary_a = re.search(r'<clipPath id="siteClip"><path d="([^"]+)"', version_a['svg']).group(1)
    boundary_b = re.search(r'<clipPath id="siteClip"><path d="([^"]+)"', version_b['svg']).group(1)
    geometry_group = re.search(r'<g id="geometry-layer"[^>]*>(.*?)</g>', version_a['svg']).group(1)

    assert scene['geometry_hash']
    assert boundary_a == boundary_b
    assert version_a['full_png'] != version_b['full_png']
    assert 'stroke=' not in geometry_group
    assert 'stroke-width=' not in geometry_group


def test_two_pass_board_compositor_returns_board_and_plan_layers():
    scene = _prepare_scene(_sample_payload(), 4200, _toggles())
    rendered = _render_variant_assets(
        'Renderer Test',
        scene,
        'hybrid_annotated_master_plan',
        _toggles(),
        'Board-ready deterministic composition',
        [],
        [],
        'board_ready',
        0,
        False,
        compose_board=True,
        board_template='master_plan_board_v1',
        include_photo_strip=True,
    )

    assert rendered['board']['template'] == 'master_plan_board_v1'
    assert rendered['plan_full_png']
    assert rendered['full_png']
    assert rendered['plan_full_png'] != rendered['full_png']
    assert rendered['plan_svg'].startswith('<svg')
    assert 'data:image/png;base64' in rendered['svg']


def test_precinct_generator_creates_multiple_footprints_inside_zone():
    zone_geometry = Polygon([
        (-114.0712, 51.0440),
        (-114.0690, 51.0440),
        (-114.0690, 51.0456),
        (-114.0712, 51.0456),
        (-114.0712, 51.0440),
    ])
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        name='North Housing Precinct',
        properties={
            'development_type': 'residential',
            'development_subcategory': 'contemporary_mid_rise_residential',
            'development_archetype_label': 'Contemporary Mid-Rise Residential',
            'description_text': 'Park-adjacent mid-rise community with strong street edge and permeability to the park',
            'floors': 6,
        },
    )
    context = {
        'roads': [
            {'geometry': LineString([(-114.0713, 51.04545), (-114.0689, 51.04545)]), 'kind': 'line', 'width_m': 10.0, 'properties': {'road_type': 'collector'}},
        ],
        'paths': [
            {'geometry': LineString([(-114.0708, 51.0441), (-114.0708, 51.0455)]), 'kind': 'path', 'width_m': 4.0, 'properties': {'road_type': 'pedestrian path'}},
        ],
        'parks': [
            {'geometry': Polygon([(-114.0712, 51.0440), (-114.0703, 51.0440), (-114.0703, 51.0446), (-114.0712, 51.0446), (-114.0712, 51.0440)]), 'name': 'Park', 'properties': {'has_paths': True}},
        ],
        'plazas': [],
        'water': [],
        'buildable_zones': [],
    }

    footprints = _generate_precinct_footprints(zone, zone_geometry, context)

    assert len(footprints) >= 2
    for item in footprints:
        assert zone_geometry.buffer(1e-9).contains(item['geometry']) or zone_geometry.buffer(1e-9).covers(item['geometry'])
        assert item['properties']['generated_precinct_grammar'] in {
            'parallel_bars',
            'perimeter_courtyard',
            'townhouse_courtyard',
            'mixed_use_edge',
            'clustered_bars',
        }

def test_variant_assets_embed_user_research_style_guide():
    scene = _prepare_scene(_sample_payload(), 4200, _toggles())
    reference_metadata = [
        {
            'zone_id': 'zone-1',
            'zone_type': 'green_space',
            'source': 'reference_board',
            'source_label': 'Landscape precedent',
            'caption': 'Soft waterfront promenade with lush planting and orthographic roofs',
            'tags': ['waterfront', 'courtyard', 'lush'],
        }
    ]

    rendered = _render_variant_assets(
        'Renderer Test',
        scene,
        'illustrative_landscape_plan',
        _toggles(),
        'Waterfront community master plan with lush courtyards',
        ['https://example.com/reference-board.png'],
        reference_metadata,
        'board_ready',
        0,
        False,
    )

    assert rendered['style_guide']['knowledge_base_version']
    assert rendered['style_guide']['emphasis']['green_structure'] > 1.0
    assert rendered['style_guide']['emphasis']['waterfront'] > 1.0
    assert rendered['style_guide']['presentation_keywords']


def test_park_program_geometries_stay_stable_when_variant_seed_changes():
    geometry = Polygon([
        (0.0, 0.0),
        (120.0, 0.0),
        (120.0, 80.0),
        (0.0, 80.0),
        (0.0, 0.0),
    ])
    props = {
        'has_paths': True,
        'park_typology': 'formal garden square with fountain and promenade',
        'description_text': 'Formal parterre landscape with central basin',
    }

    variant_a = {'seed': 0, 'layout_seed': 123456, 'tree_pattern': 'formal_allee', 'tree_size': 1.0}
    variant_b = {'seed': 2, 'layout_seed': 123456, 'tree_pattern': 'formal_allee', 'tree_size': 1.2}

    programs_a = _park_program_geometries(geometry, props, variant_a)
    programs_b = _park_program_geometries(geometry, props, variant_b)

    assert [kind for kind, _ in programs_a] == [kind for kind, _ in programs_b]
    assert [geom.wkt for _, geom in programs_a] == [geom.wkt for _, geom in programs_b]


def test_tree_layout_stays_stable_when_style_variants_change():
    geometry = Polygon([
        (0.0, 0.0),
        (90.0, 0.0),
        (90.0, 60.0),
        (0.0, 60.0),
        (0.0, 0.0),
    ])
    props = {
        'tree_density_level': 'dense',
        'tree_density': 0.28,
    }

    variant_a = {'seed': 0, 'layout_seed': 987654, 'tree_pattern': 'formal_allee', 'tree_size': 1.0}
    variant_b = {'seed': 1, 'layout_seed': 987654, 'tree_pattern': 'formal_allee', 'tree_size': 1.3}

    points_a = _tree_points(geometry, props, variant_a)
    points_b = _tree_points(geometry, props, variant_b)

    assert [(round(x, 3), round(y, 3)) for x, y, *_ in points_a] == [(round(x, 3), round(y, 3)) for x, y, *_ in points_b]


def test_style_pass_prompt_uses_professional_planimetric_language():
    scene = {'prompt_zones': _sample_payload()['prompt_zones']}
    prompt = _build_ai_style_pass_prompt(
        'Renderer Test',
        scene,
        'illustrative_landscape_plan',
        'Digital Watercolor, Formal Allee, Annotated Typography',
        [
            {
                'zone_id': 'zone-2',
                'zone_type': 'green_space',
                'source_label': 'Landscape precedent',
                'category': 'Parisian Garden',
                'caption': 'Formal garden promenade with layered planting',
                'tags': ['allee', 'watercolor'],
            }
        ],
        {'seed': 1},
    )

    lowered = prompt.lower()

    assert prompt.startswith('90-degree direct overhead planimetric master plan. True top-down view only. No side views. No elevations. No collage elements.')
    assert 'Treat the entire site as one continuous sheet with one palette family, one light direction, and one shared paper texture.' in prompt
    assert 'Preserve every existing site boundary, zone clip, building footprint, roof edge, street alignment, planting bed, and water edge exactly as already drawn.' in prompt
    assert 'Do not turn archetype labels, precedent captions, or reference metadata into separate picture tiles, facade inserts, or floating boards.' in prompt
    assert '[Within #9b59b6 Zone]: Render the roof plan and building footprint for Contemporary Mid-Rise Residential.' in prompt
    assert '[Within #27ae60 Zone]: Render a top-down landscape plan with formal civic garden composition.' in prompt
    assert '[Within #444444 Zone]: Render a flat plan-view corridor with ceremonial paseo public realm.' in prompt
    assert 'CRITICAL DESIGN DIRECTIVE: Courtyard housing with strong park frontage.' in prompt
    assert 'CRITICAL DESIGN DIRECTIVE: Formal basin garden with promenade walks.' in prompt
    assert 'CRITICAL DESIGN DIRECTIVE: Primary pedestrian spine with premium paving.' in prompt
    assert 'front elevation' not in lowered
    assert 'street-level' not in lowered
    assert 'front-facing' not in lowered
    assert 'perspective thumbnail' not in lowered


def test_reference_metadata_sanitizer_neutralizes_elevation_language():
    sanitized = _sanitize_reference_metadata_bundle([
        {
            'zone_id': 'zone-1',
            'zone_type': 'building',
            'prompt_text': 'Front-facing composition with street-level eye-height camera and restrained perspective distortion.',
            'caption': 'Mediterranean residential front elevation',
            'subcategory': 'front_day',
            'tags': ['front elevation', 'perspective'],
            'image_url': 'https://example.com/front_day.png',
        }
    ])[0]

    joined = ' '.join([
        str(sanitized.get('caption') or ''),
        str(sanitized.get('subcategory') or ''),
        ' '.join(str(tag) for tag in (sanitized.get('tags') or [])),
    ]).lower()

    assert sanitized.get('prompt_text') is None
    assert 'front elevation' not in joined
    assert 'perspective' not in joined
    assert 'roof plan' in joined or 'plan reference' in joined
    assert sanitized.get('image_url') == 'https://example.com/front_day.png'

def test_ai_style_pass_falls_back_to_base_render_when_no_provider_keys(monkeypatch):
    monkeypatch.setattr(master_plan_2d.settings, 'gemini_api_key', '')
    monkeypatch.setattr(master_plan_2d.settings, 'stability_api_key', '')
    scene = _prepare_scene(_sample_payload(), 4200, _toggles())
    rendered = _render_variant_assets(
        'Renderer Test',
        scene,
        'illustrative_landscape_plan',
        _toggles(),
        'Digital Watercolor master plan',
        [],
        [],
        'board_ready',
        0,
        False,
        ai_style_pass_enabled=True,
        ai_style_pass_provider='auto',
    )

    assert rendered['ai_style_pass']['requested'] is True
    assert rendered['ai_style_pass']['applied'] is False
    assert rendered['ai_style_pass']['requested_provider'] == 'auto'
    assert rendered['ai_style_pass']['attempted_providers'] == ['gemini']
    assert 'GEMINI_API_KEY not configured' in rendered['ai_style_pass']['reason']
    assert rendered['full_png']


def test_ai_style_pass_uses_stability_provider_when_selected(monkeypatch):
    monkeypatch.setattr(master_plan_2d.settings, 'gemini_api_key', '')
    monkeypatch.setattr(master_plan_2d.settings, 'stability_api_key', 'stability-test-key')

    class _FakeResponse:
        def __init__(self, content: bytes):
            self.content = content

        def raise_for_status(self):
            return None

    def _fake_post(*_args, **_kwargs):
        image = Image.new('RGB', (640, 426), (192, 184, 168))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return _FakeResponse(buffer.getvalue())

    fake_httpx = type('FakeHttpx', (), {'post': staticmethod(_fake_post)})
    monkeypatch.setitem(sys.modules, 'httpx', fake_httpx)

    scene = _prepare_scene(_sample_payload(), 4200, _toggles())
    rendered = _render_variant_assets(
        'Renderer Test',
        scene,
        'illustrative_landscape_plan',
        _toggles(),
        'Digital Watercolor master plan',
        [],
        [],
        'board_ready',
        0,
        False,
        ai_style_pass_enabled=True,
        ai_style_pass_provider='stability',
    )

    assert rendered['ai_style_pass']['requested'] is True
    assert rendered['ai_style_pass']['applied'] is True
    assert rendered['ai_style_pass']['requested_provider'] == 'stability'
    assert rendered['ai_style_pass']['provider'] == 'stability'
    assert rendered['ai_style_pass']['model'] == master_plan_2d.STABILITY_STYLE_PASS_MODEL


def test_ai_style_composite_preserves_canvas_size_and_changes_finish():
    scene = {
        'pixel': {
            'boundary': Polygon([(120, 120), (1080, 120), (1080, 720), (120, 720), (120, 120)]),
        },
        'pixels_per_meter': 1.0,
    }
    base = Image.new('RGBA', (1400, 900), (240, 236, 228, 255))
    styled = Image.new('RGBA', (1200, 800), (196, 182, 160, 255))

    composited = _compose_ai_style_pass(base, styled, scene, {'seed': 1, 'quality_level': 'board_ready'})

    assert composited.size == base.size
    assert composited.tobytes() != base.tobytes()










def test_zone_snapshot_payload_supports_unsaved_canvas_geometry_for_3d_packaging():
    request = MasterPlan3DGenerateRequest(
        selected_perspective='corner_perspective',
        lighting_variant='overcast_soft_light',
        scope='full_site',
        zones=[
            {
                'zone_id': 'z-r1',
                'zone_label': 'Affordable Graduate Student Housing',
                'zone_type': 'residential_area',
                'color': '#4ADE80',
                'polygon': [
                    [-114.131, 51.081],
                    [-114.130, 51.081],
                    [-114.130, 51.082],
                    [-114.131, 51.082],
                    [-114.131, 51.081],
                ],
                'height_m': 18,
                'floor_count': 5,
                'archetype_title': 'Mixed-Use Residential',
                'archetype_metadata': {'styleProfile': {'roofForm': 'flat with green roof elements'}},
                'user_notes': 'Open park-like courtyards.',
            },
            {
                'zone_id': 'z-w1',
                'zone_label': 'Sound, Visual & Safety Art Wall',
                'zone_type': 'infrastructure',
                'color': '#8B5CF6',
                'polygon': [
                    [-114.128, 51.078],
                    [-114.127, 51.078],
                    [-114.127, 51.080],
                    [-114.128, 51.080],
                    [-114.128, 51.078],
                ],
                'height_m': 6,
                'floor_count': 1,
                'archetype_title': 'Infrastructure Barrier',
                'archetype_metadata': {'styleProfile': {'materials': 'concrete mural wall'}},
                'user_notes': 'Barrier to improve safety and acoustics.',
            },
        ],
    )

    snapshot_zones = _zone_snapshots_from_request(request)
    assert len(snapshot_zones) == 2
    assert snapshot_zones[0].zone_type == 'residential'
    assert snapshot_zones[1].zone_type == 'development_area'

    boundary = _boundary_from_snapshot_zones(snapshot_zones)
    assert boundary is not None
    assert not boundary.is_empty

    project = SimpleNamespace(id=uuid.uuid4())
    option = SimpleNamespace(id=uuid.uuid4(), label='Version A', metadata_={})
    response = _build_master_plan_3d_response(project, option, boundary, snapshot_zones, [], request)

    assert len(response['render_packages']) == 2
    assert all(pkg['footprint_geometry']['type'] == 'Polygon' for pkg in response['render_packages'])


def test_gold_standard_fixture_builds_zone_snapshots_without_loss():
    fixture_path = Path(__file__).parent / 'fixtures' / 'university_station_gold_board_v1.json'
    fixture = json.loads(fixture_path.read_text(encoding='utf-8'))
    zones_payload = [
        {
            'zone_id': item['zone_id'],
            'zone_label': item.get('zone_label'),
            'zone_type': item.get('zone_kind'),
            'color': item.get('color'),
            'polygon': item.get('polygon'),
            'height_m': item.get('height_m'),
            'floor_count': item.get('floor_count'),
            'archetype_title': item.get('archetype_title'),
            'archetype_metadata': item.get('archetype_metadata'),
            'user_notes': item.get('user_notes'),
        }
        for item in fixture.get('zones', [])
    ]

    request = MasterPlan3DGenerateRequest(scope='full_site', zones=zones_payload)
    snapshot_zones = _zone_snapshots_from_request(request)

    assert len(snapshot_zones) == 3
    assert [zone.zone_type for zone in snapshot_zones] == ['development_area', 'residential', 'development_area']
    assert all(zone.geometry is not None for zone in snapshot_zones)


def test_build_master_plan_3d_response_preserves_geometry_and_metadata():
    boundary = Polygon([
        (-114.0710, 51.0440),
        (-114.0690, 51.0440),
        (-114.0690, 51.0454),
        (-114.0710, 51.0454),
        (-114.0710, 51.0440),
    ])
    zone_id = uuid.uuid4()
    zone = SimpleNamespace(
        id=zone_id,
        zone_type='building',
        name='Main Street Block',
        color='#9b59b6',
        sort_order=0,
        created_at=0,
        geometry=from_shape(Polygon([
            (-114.0708, 51.0442),
            (-114.0701, 51.0442),
            (-114.0701, 51.0448),
            (-114.0708, 51.0448),
            (-114.0708, 51.0442),
        ]), srid=4326),
        properties={
            'height': 22,
            'floors': 6,
            'description_text': 'Emphasize elegant retail frontages and a stronger corner condition',
            'development_archetype_label': 'Mid-Rise Mixed Use Main Street',
            'generation_style_input': {
                'aestheticCategoryLabel': 'Contemporary Urban Main Street',
                'styleProfile': {
                    'massing': 'perimeter-block composition',
                    'roofForm': 'articulated flat roof',
                    'materials': ['warm brick', 'charcoal metal', 'clear glazing'],
                    'windowStyle': 'vertically proportioned windows and large storefront openings',
                    'articulation': 'fine-grain mixed-use frontage',
                    'publicRealm': 'walkable main street',
                    'pavingType': 'unit pavers',
                    'plantingType': 'street trees',
                    'corridorCharacter': 'pedestrian-priority corridor',
                },
            },
        },
        building_id=None,
        building_ids=None,
    )
    project = SimpleNamespace(id=uuid.uuid4())
    option = SimpleNamespace(id=uuid.uuid4(), label='Version A', metadata_={'prompt': 'Focus on warm, premium mixed-use realism'})
    request = MasterPlan3DGenerateRequest(
        selected_perspective='street_level_eye_height',
        lighting_variant='golden_hour',
        scope='selected_zones',
        selected_zone_ids=[str(zone_id)],
    )

    response = _build_master_plan_3d_response(project, option, boundary, [zone], [], request)

    assert response['selected_zone_ids'] == [str(zone_id)]
    assert len(response['render_packages']) == 1
    package = response['render_packages'][0]
    assert package['zone_id'] == str(zone_id)
    assert package['height_m'] == 22.0
    assert package['floor_count'] == 6
    assert package['footprint_geometry']['type'] == 'Polygon'
    assert package['renderer_notes']['keep_footprint_alignment'] is True
    assert package['render_prompt'].startswith('A premium photorealistic architectural 3D rendering from a street-level eye-height perspective.')
    assert 'Critical Directive: Emphasize elegant retail frontages and a stronger corner condition.' in package['render_prompt']
    assert package['archetype_metadata']['generation_style_input']['aestheticCategoryLabel'] == 'Contemporary Urban Main Street'


def test_build_master_plan_3d_response_defaults_missing_height_floor_gracefully():
    boundary = Polygon([
        (-114.0710, 51.0440),
        (-114.0690, 51.0440),
        (-114.0690, 51.0454),
        (-114.0710, 51.0454),
        (-114.0710, 51.0440),
    ])
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        zone_type='building',
        name='Fallback Block',
        color='#d4a574',
        sort_order=0,
        created_at=0,
        geometry=from_shape(Polygon([
            (-114.0706, 51.0443),
            (-114.0699, 51.0443),
            (-114.0699, 51.0449),
            (-114.0706, 51.0449),
            (-114.0706, 51.0443),
        ]), srid=4326),
        properties={
            'development_archetype_label': 'Adaptive Reuse Loft Block',
        },
        building_id=None,
        building_ids=None,
    )
    project = SimpleNamespace(id=uuid.uuid4())
    option = SimpleNamespace(id=uuid.uuid4(), label='Version B', metadata_={})
    request = MasterPlan3DGenerateRequest()

    response = _build_master_plan_3d_response(project, option, boundary, [zone], [], request)

    package = response['render_packages'][0]
    assert package['height_m'] == 24.0
    assert package['floor_count'] == 6
    assert any('defaulted this zone to 24m over 6 levels' in warning['reason'] for warning in response['skipped_zones'])


def test_build_master_plan_3d_response_carries_project_style_direction_without_duplication():
    boundary = Polygon([
        (-114.0710, 51.0440),
        (-114.0690, 51.0440),
        (-114.0690, 51.0454),
        (-114.0710, 51.0454),
        (-114.0710, 51.0440),
    ])
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        zone_type='building',
        name='Market Hall Block',
        color='#9b59b6',
        sort_order=0,
        created_at=0,
        geometry=from_shape(Polygon([
            (-114.0707, 51.0442),
            (-114.0701, 51.0442),
            (-114.0701, 51.0448),
            (-114.0707, 51.0448),
            (-114.0707, 51.0442),
        ]), srid=4326),
        properties={
            'height': 20,
            'floors': 5,
            'development_archetype_label': 'Urban Market Hall',
        },
        building_id=None,
        building_ids=None,
    )
    project = SimpleNamespace(
        id=uuid.uuid4(),
        default_style='warm premium mixed-use realism',
    )
    option = SimpleNamespace(
        id=uuid.uuid4(),
        label='Version C',
        metadata_={'prompt': 'Warm premium mixed-use realism'},
    )
    request = MasterPlan3DGenerateRequest(
        global_style_notes='Emphasize crafted public-realm materials',
    )

    response = _build_master_plan_3d_response(project, option, boundary, [zone], [], request)

    assert response['global_style_notes'] == 'Emphasize crafted public-realm materials. Warm premium mixed-use realism'
    assert response['render_packages'][0]['archetype_metadata']['resolved_archetype_title'] == 'Urban Market Hall'



def test_build_master_plan_3d_response_handles_malformed_zone_properties_without_crashing():
    boundary = Polygon([
        (-114.0710, 51.0440),
        (-114.0690, 51.0440),
        (-114.0690, 51.0454),
        (-114.0710, 51.0454),
        (-114.0710, 51.0440),
    ])
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        zone_type='building',
        name='Malformed Metadata Block',
        color='#9b59b6',
        sort_order=0,
        created_at=0,
        geometry=from_shape(Polygon([
            (-114.0708, 51.0442),
            (-114.0702, 51.0442),
            (-114.0702, 51.0448),
            (-114.0708, 51.0448),
            (-114.0708, 51.0442),
        ]), srid=4326),
        properties='corrupted-json-string',
        building_id=None,
        building_ids=None,
    )
    project = SimpleNamespace(id=uuid.uuid4())
    option = SimpleNamespace(id=uuid.uuid4(), label='Version D', metadata_={})

    response = _build_master_plan_3d_response(project, option, boundary, [zone], [], MasterPlan3DGenerateRequest())

    assert len(response['render_packages']) == 1
    assert response['render_packages'][0]['height_m'] == 24.0
    assert any('malformed' in warning['reason'].lower() for warning in response['skipped_zones'])


def test_build_master_plan_3d_response_surfaces_clip_failures_as_validation_errors(monkeypatch):
    boundary = Polygon([
        (-114.0710, 51.0440),
        (-114.0690, 51.0440),
        (-114.0690, 51.0454),
        (-114.0710, 51.0454),
        (-114.0710, 51.0440),
    ])
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        zone_type='building',
        name='Clip Failure Block',
        color='#9b59b6',
        sort_order=0,
        created_at=0,
        geometry=from_shape(Polygon([
            (-114.0708, 51.0442),
            (-114.0701, 51.0442),
            (-114.0701, 51.0448),
            (-114.0708, 51.0448),
            (-114.0708, 51.0442),
        ]), srid=4326),
        properties={'height': 18, 'floors': 5},
        building_id=None,
        building_ids=None,
    )
    project = SimpleNamespace(id=uuid.uuid4())
    option = SimpleNamespace(id=uuid.uuid4(), label='Version E', metadata_={})

    monkeypatch.setattr(
        master_plan_2d,
        '_clip_zone_polygon_to_boundary',
        lambda _geometry, _boundary: (None, 'Zone geometry could not be clipped to the site boundary.'),
    )

    with pytest.raises(ValueError) as exc_info:
        _build_master_plan_3d_response(project, option, boundary, [zone], [], MasterPlan3DGenerateRequest())

    assert 'could not be clipped to the site boundary' in str(exc_info.value)






def test_render_variant_assets_exposes_control_maps_for_orthographic_pipeline():
    scene = _prepare_scene(_sample_payload(), 4200, _toggles())

    rendered = _render_variant_assets(
        'Renderer Test',
        scene,
        'rendered_sales_plan',
        _toggles(),
        'Photoreal orthographic aerial master plan',
        [],
        [],
        'board_ready',
        0,
        False,
        compose_board=False,
        render_style_preset='photoreal_orthographic_aerial',
    )

    control_maps = rendered['control_maps']
    assert control_maps['available'] is True
    assert control_maps['conditioning_mode'] == 'stability_structure_ready'
    assert set(control_maps['images'].keys()) == {'massing', 'depth', 'segmentation', 'structure'}
    assert control_maps['images']['structure'].size == (scene['width'], scene['height'])
    assert control_maps['images']['depth'].mode == 'L'


def test_ai_style_pass_uses_structure_control_for_orthographic_stability(monkeypatch):
    monkeypatch.setattr(master_plan_2d.settings, 'gemini_api_key', '')
    monkeypatch.setattr(master_plan_2d.settings, 'stability_api_key', 'stability-test-key')

    called = {'structure': False}

    def _fake_structure_pass(*, control_image, prompt, negative_prompt, control_strength):
        called['structure'] = True
        assert control_image.size[0] > 0 and control_image.size[1] > 0
        assert control_strength > 0.0
        return Image.new('RGBA', control_image.size, (188, 182, 176, 255)), None

    monkeypatch.setattr(master_plan_2d, '_run_stability_structure_pass', _fake_structure_pass)

    scene = _prepare_scene(_sample_payload(), 4200, _toggles())
    rendered = _render_variant_assets(
        'Renderer Test',
        scene,
        'rendered_sales_plan',
        _toggles(),
        'Photoreal orthographic aerial master plan',
        [],
        [],
        'board_ready',
        0,
        False,
        compose_board=False,
        ai_style_pass_enabled=True,
        ai_style_pass_provider='stability',
        render_style_preset='photoreal_orthographic_aerial',
    )

    assert called['structure'] is True
    assert rendered['ai_style_pass']['provider'] == 'stability'
    assert rendered['ai_style_pass']['model'] == master_plan_2d.STABILITY_STRUCTURE_MODEL
    assert rendered['ai_style_pass']['control_mode'] == 'structure'


def test_build_master_plan_3d_response_carries_conditioning_assets_from_selected_option():
    boundary = Polygon([
        (-114.0710, 51.0440),
        (-114.0690, 51.0440),
        (-114.0690, 51.0454),
        (-114.0710, 51.0454),
        (-114.0710, 51.0440),
    ])
    zone_id = uuid.uuid4()
    zone = SimpleNamespace(
        id=zone_id,
        zone_type='building',
        name='Conditioned Block',
        color='#9b59b6',
        sort_order=0,
        created_at=0,
        geometry=from_shape(Polygon([
            (-114.0707, 51.0442),
            (-114.0701, 51.0442),
            (-114.0701, 51.0449),
            (-114.0707, 51.0449),
            (-114.0707, 51.0442),
        ]), srid=4326),
        properties={'height': 22, 'floors': 6},
        building_id=None,
        building_ids=None,
    )
    project = SimpleNamespace(id=uuid.uuid4())
    option = SimpleNamespace(
        id=uuid.uuid4(),
        label='Version Control',
        metadata_={
            'assets': {
                'control_structure_png_url': 'data:image/png;base64,structure',
                'control_depth_png_url': 'data:image/png;base64,depth',
                'control_segmentation_png_url': 'data:image/png;base64,segmentation',
                'control_massing_png_url': 'data:image/png;base64,massing',
            },
            'control_maps': {
                'conditioning_mode': 'stability_structure_ready',
                'control_strength': 0.88,
            },
        },
    )

    response = _build_master_plan_3d_response(project, option, boundary, [zone], [], MasterPlan3DGenerateRequest())

    package = response['render_packages'][0]
    assert package['conditioning_assets']['structure_image_url'] == 'data:image/png;base64,structure'
    assert package['conditioning_assets']['depth_map_url'] == 'data:image/png;base64,depth'
    assert package['conditioning_assets']['perspective_structure_image_url'].startswith('data:image/png;base64,')
    assert package['conditioning_assets']['perspective_depth_map_url'].startswith('data:image/png;base64,')
    assert package['conditioning_assets']['camera_perspective'] == 'aerial_oblique'
    assert package['conditioning_assets']['control_mode'] == 'orthographic_source_plus_camera_controls'
    assert package['conditioning_assets']['control_strength'] == 0.88
    assert response['renderer_adapter']['integration_status'] == 'camera_conditioned_packages_ready'



def test_render_plan_image_preserves_underlay_through_site_center():
    scene = _prepare_scene(_sample_payload(), 2400, _toggles())
    underlay = Image.new('RGBA', (2400, 1600), (62, 118, 84, 255))

    rendered = master_plan_2d._render_plan_image(
        scene,
        style_preset='rendered_sales_plan',
        variant=master_plan_2d._make_variant_profile('rendered_sales_plan', 'board_ready', 0, scene['geometry_hash'], render_style_preset='photoreal_orthographic_aerial'),
        toggles=_toggles(),
        context_underlay=underlay,
    )

    center = rendered.getpixel((rendered.width // 2, rendered.height // 2))
    assert center[1] > center[0]
    assert sum(center[:3]) < 690


def test_collect_scene_payload_generates_internal_precinct_site_features():
    boundary = Polygon([
        (-114.0710, 51.0440),
        (-114.0685, 51.0440),
        (-114.0685, 51.0458),
        (-114.0710, 51.0458),
        (-114.0710, 51.0440),
    ])
    zone = SimpleNamespace(
        id=uuid.uuid4(),
        zone_type='development_area',
        name='Mixed Use Precinct',
        color='#9b59b6',
        sort_order=0,
        created_at=0,
        geometry=from_shape(boundary, srid=4326),
        properties={
            'height': 26,
            'floors': 8,
            'description_text': 'Mixed-use district with retail frontage, parking access, promenades, and a central courtyard',
            'development_type': 'mixed_use',
            'generation_style_input': {'subtype': 'mixed-use precinct'},
        },
        building_id=None,
        building_ids=None,
    )
    project = SimpleNamespace(id=uuid.uuid4())

    payload = master_plan_2d._collect_scene_payload(project, [zone], [])

    assert len(payload['building_footprints']) >= 2
    assert len(payload['paths']) >= 1
    assert len(payload['parks']) >= 1
    assert len(payload['plazas']) >= 1
