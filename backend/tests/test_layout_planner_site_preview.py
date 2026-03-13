import asyncio
import base64
import sys
from types import ModuleType, SimpleNamespace

import app.services.layout_planner as layout_planner
from shapely.geometry import Polygon


def _site_preview_fixture():
    boundary = Polygon([
        (-114.0710, 51.0440),
        (-114.0690, 51.0440),
        (-114.0690, 51.0454),
        (-114.0710, 51.0454),
        (-114.0710, 51.0440),
    ])
    buildable_shape = Polygon([
        (-114.0708, 51.0442),
        (-114.0701, 51.0442),
        (-114.0701, 51.0449),
        (-114.0708, 51.0449),
        (-114.0708, 51.0442),
    ])
    road_shape = Polygon([
        (-114.0710, 51.04495),
        (-114.0690, 51.04495),
        (-114.0690, 51.04508),
        (-114.0710, 51.04508),
        (-114.0710, 51.04495),
    ])
    zone = SimpleNamespace(id='zone-1', zone_type='building', name='Housing Precinct')
    option = SimpleNamespace(
        layout_strategy='Front-facing composition with street-level eye-height camera',
        buildings=[SimpleNamespace(building_type='residential', width_m=22, depth_m=14, floors=6, height_m=21)],
        roads=[SimpleNamespace(road_type='shared street', width_m=8)],
        green_spaces=[SimpleNamespace(space_type='courtyard garden')],
    )
    zone_layouts = [
        {
            'zone': zone,
            'shape': buildable_shape,
            'option': option,
            'properties': {
                'development_type': 'residential',
                'development_aesthetic': 'Mediterranean residential front elevation',
                'facade_material': 'brick facade',
                'roof_style': 'terracotta roof',
                'ground_texture': 'stone promenade paving',
                'description_text': 'Front-facing residential front elevation with strong park frontage',
                'reference_images': ['https://example.com/archetype.png'],
                'development_archetype_label': 'Mediterranean Residential Front Elevation',
            },
        }
    ]
    non_buildable_zones = [
        {
            'zone_type': 'road',
            'shape': road_shape,
            'properties': {
                'width': 12,
                'lane_count': 2,
                'road_surface': 'asphalt',
                'sidewalks': 'both',
                'mobility_profile': 'walking_only',
                'reference_images': ['https://example.com/street-board.png'],
                'description_text': 'Street-level frontage should read clearly',
            },
            'name': 'Main Street',
            'zone_id': 'road-1',
        }
    ]
    return boundary, zone_layouts, non_buildable_zones


def test_site_preview_sanitizer_neutralizes_elevation_language():
    text = layout_planner._site_preview_sanitize_text(
        'Front-facing composition with street-level eye-height camera, facade sheet, and restrained perspective distortion.'
    )

    lowered = text.lower()
    assert 'front-facing' not in lowered
    assert 'street-level' not in lowered
    assert 'facade sheet' not in lowered
    assert 'plan-view' in lowered or 'orthographic' in lowered


def test_site_preview_generation_uses_planimetric_prompt_and_skips_reference_images(monkeypatch):
    boundary, zone_layouts, non_buildable_zones = _site_preview_fixture()
    monkeypatch.setattr(layout_planner.settings, 'gemini_api_key', 'test-key')

    captured: dict[str, object] = {}

    class FakePart(SimpleNamespace):
        @staticmethod
        def from_bytes(data, mime_type):
            return FakePart(inline_data=SimpleNamespace(data=data), mime_type=mime_type, text=None)

    class FakeClient:
        def __init__(self, api_key):
            captured['api_key'] = api_key
            self.models = self

        def generate_content(self, model, contents, config):
            captured['model'] = model
            captured['contents'] = contents
            captured['config'] = config
            return SimpleNamespace(
                candidates=[
                    SimpleNamespace(
                        content=SimpleNamespace(
                            parts=[SimpleNamespace(inline_data=SimpleNamespace(data=b'fake-image'), text=None)]
                        )
                    )
                ],
                usage_metadata=SimpleNamespace(prompt_token_count=0, candidates_token_count=0),
            )

    google_module = ModuleType('google')
    google_module.genai = SimpleNamespace(
        Client=FakeClient,
        types=SimpleNamespace(
            Part=FakePart,
            GenerateContentConfig=lambda **kwargs: kwargs,
        ),
    )
    monkeypatch.setitem(sys.modules, 'google', google_module)

    screenshot = 'data:image/png;base64,' + base64.b64encode(b'geometry-guide').decode('ascii')
    planner = layout_planner.LayoutPlanner()
    image_bytes = asyncio.run(
        planner.generate_site_preview_image(
            boundary_polygon=boundary,
            zone_layouts=zone_layouts,
            non_buildable_zones=non_buildable_zones,
            reference_context={'roads': [{'road_type': 'arterial', 'name': 'Main Street'}]},
            map_screenshots={'with_zones': screenshot},
            zone_meta={'zone-1': {'name': 'Housing Precinct', 'color': '#9b59b6'}},
            buildable_without_layouts=[],
        )
    )

    assert image_bytes == b'fake-image'
    contents = captured['contents']
    prompt = contents[-1]
    lowered = prompt.lower()
    inline_data_parts = [item for item in contents if getattr(item, 'inline_data', None) is not None]

    assert len(inline_data_parts) == 1
    assert prompt.startswith('90-degree direct overhead planimetric master plan. True top-down view only. No side views. No elevations.')
    assert 'Render a professional illustrative master plan, not a drone photo' in prompt
    assert 'ARCHETYPE METADATA RULE:' in prompt
    assert 'Do not paste, reproduce, or collage any source imagery into the master plan.' in prompt
    assert 'front elevation' not in lowered
    assert 'street-level' not in lowered
    assert 'facade sheet' not in lowered
    assert 'roof plans and footprints only' in lowered
    assert 'reference image(s) attached' not in lowered