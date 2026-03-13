from app.services.master_plan_design_knowledge import (
    MASTER_PLAN_KNOWLEDGE_BASE_VERSION,
    build_master_plan_style_guide,
    build_site_preview_design_brief,
)


def test_master_plan_style_guide_extracts_shared_emphasis():
    guide = build_master_plan_style_guide(
        'illustrative_landscape_plan',
        'Illustrative Landscape Plan',
        {
            'paper': '#f2eee3',
            'site': '#eef1e3',
            'park': '#9ebd87',
            'water': '#89acc8',
            'road': '#96968f',
            'path': '#d4c3a4',
            'roof': '#ebe4d7',
            'accent': '#88672b',
        },
        'Illustrative Rendered, Digital Watercolor, Gradient Layering, Formal Allee, Specific Typology: Classic Haussmannian Parisian, Annotated Typography, Integrated Context',
        ['https://example.com/reference-a.png'],
    )

    assert guide['knowledge_base_version'] == MASTER_PLAN_KNOWLEDGE_BASE_VERSION
    assert guide['emphasis']['illustrative_render'] > 1.0
    assert guide['emphasis']['gradient_layering'] > 1.0
    assert guide['emphasis']['formal_allee'] > 1.0
    assert guide['emphasis']['annotated_typography'] > 1.0
    assert 'Classic Haussmannian Parisian' in guide['typology_hints']
    assert 'Digital Watercolor' in guide['presentation_keywords']


def test_site_preview_brief_adds_water_and_reference_guidance():
    brief = build_site_preview_design_brief(
        has_water=True,
        has_parks=True,
        has_reference_images=True,
    )
    text = ' '.join(brief).lower()

    assert 'water edges' in text
    assert 'parks and courtyards' in text
    assert 'digital watercolor' in text
    assert 'plan-view cues' in text
    assert 'copying or pasting imagery literally' in text
