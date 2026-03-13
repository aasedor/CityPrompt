from __future__ import annotations

from typing import Any, Sequence

MASTER_PLAN_KNOWLEDGE_BASE_VERSION = '2026-03-11'

MASTER_PLAN_KNOWLEDGE_SOURCES = [
    'Gensler - City Centre Deira Master Plan (official project page)',
    'Sasaki - Brookline High School Master Plan (official project page)',
    'SOM - Stavanger University Hospital and Campus (official project page)',
    'AECOM - Yonge North Subway Extension: Landscape and Public Realm (official project page)',
    'Stantec - Landscape Architecture (official practice page)',
    'User-supplied 2D master plan references showing landscape-led orthographic plans with muted context',
    'User-supplied prompt heuristics for rendered illustrative plans, digital watercolor, gradient layering, formal allees, annotated typography, and integrated context',
]

REFERENCE_PLAN_SIGNALS = [
    'landscape reads as the connective structure of the plan rather than a residual fill between buildings',
    'streets, promenades, and multimodal corridors form a clear hierarchy with civic nodes at key junctions',
    'buildings reinforce the public realm through disciplined frontage, courtyard definition, and calibrated spacing',
    'context is quieter and less saturated so the site plan reads as the primary figure on the board',
    'graphics feel presentation-grade: restrained materials, orthographic clarity, and elegant annotation rather than heavy outlines',
]

TWO_D_RENDER_DIRECTIVES = [
    'Preserve figure-ground clarity so the site reads immediately against muted surrounding context.',
    'Show circulation as a hierarchy: primary boulevards first, secondary streets next, then paths, promenades, and plazas.',
    'Let landscape organize the composition with canopy bands, groves, lawn rooms, buffers, and courtyard planting.',
    'Keep buildings mostly light in tone with restrained roof shadows so orthographic massing remains legible.',
    'Use overlays like legend, north arrow, and callouts as presentation-board elements that sit beside the plan rather than drawing new geometry lines.',
]

THREE_D_SCENE_DIRECTIVES = [
    'Use parks, water, and public streets as the structural framework of the district rather than decorative afterthoughts.',
    'Favor coherent massing families and repeated planting rhythms over object-by-object novelty.',
    'Match references at the level of material tone, canopy rhythm, edge treatment, and public-realm mood.',
    'Treat water edges, promenades, civic greens, and active main streets as high-value frontage with stronger detailing and activation.',
]

PRESENTATION_PROMPT_HINTS = {
    'schematic_render_terms': ['Illustrative Rendered', 'Digital Watercolor', 'watercolor and ink', 'textured paper background'],
    'massing_terms': ['Gradient Layering', 'Soft Shadows'],
    'vegetation_terms': ['Detailed Vegetation Texture', 'Formal Allee'],
    'annotation_terms': ['Annotated Typography', 'Integrated Context'],
    'typology_examples': ['Whistler-Style Alpine', 'Classic Haussmannian Parisian', 'Adaptive Reuse Warehouse Lofts', 'Kyoto Philosopher Walk'],
}

TYPOLOGY_TOKENS = {
    'Whistler-Style Alpine': ['whistler', 'alpine'],
    'Classic Haussmannian Parisian': ['haussmann', 'haussmannian', 'parisian', 'paris jardin', 'parisian garden'],
    'Adaptive Reuse Warehouse Lofts': ['adaptive reuse', 'warehouse loft', 'warehouse', 'brick loft'],
    'Kyoto Philosopher Walk': ['kyoto', 'philosopher', 'reflecting path', 'path of reflection'],
}

LBCS_COLOR_LOGIC = {
    'residential': 'yellow/warm neutral family',
    'commercial': 'red/warm accent family',
    'industrial': 'purple family',
    'civic_institutional': 'blue family',
    'mobility': 'gray/neutral family',
    'assembly_open_space': 'light green family',
    'leisure': 'dark cyan family',
    'natural_systems': 'forest green family',
}


def _has_any(text: str, tokens: Sequence[str]) -> bool:
    return any(token in text for token in tokens)


def _palette_summary(palette: dict[str, Any]) -> list[str]:
    ordered_keys = ['paper', 'site', 'park', 'water', 'road', 'path', 'roof', 'accent']
    return [
        str(palette[key])
        for key in ordered_keys
        if isinstance(palette.get(key), str) and str(palette[key]).startswith('#')
    ]


def _detected_typologies(text: str) -> list[str]:
    return [
        label
        for label, tokens in TYPOLOGY_TOKENS.items()
        if _has_any(text, tokens)
    ]


def build_master_plan_style_guide(
    style_key: str,
    style_name: str,
    palette: dict[str, Any],
    prompt: str | None,
    reference_images: Sequence[str] | None = None,
) -> dict[str, Any]:
    text = (prompt or '').lower()
    references = list(reference_images or [])

    softer = _has_any(text, ['soft', 'illustrative', 'watercolor', 'wash', 'digital watercolor', 'illustrative rendered'])
    green_structure = _has_any(text, ['green', 'lush', 'park', 'landscape', 'garden', 'courtyard', 'greenway', 'campus'])
    waterfront = _has_any(text, ['waterfront', 'river', 'canal', 'lake', 'pond', 'shore', 'wetland', 'marina', 'reflecting pool'])
    civic_space = _has_any(text, ['community', 'civic', 'plaza', 'promenade', 'boulevard', 'main street', 'public realm'])
    orthographic = _has_any(text, ['orthographic', 'plan', 'diagram', 'master plan', 'top-down', 'top down'])
    gradient_layering = _has_any(text, ['gradient layering', 'soft shadows', 'sunlight', 'massing'])
    vegetation_detail = _has_any(text, ['detailed vegetation texture', 'formal allee', 'allee', 'canopy rhythm', 'tree-lined'])
    formal_allee = _has_any(text, ['formal allee', 'allee', 'haussmann', 'haussmannian', 'parterres', 'symmetrical geometry'])
    annotated_typography = _has_any(text, ['annotated typography', 'annotated', 'callout', 'legend', 'typography', 'label'])
    integrated_context = _has_any(text, ['integrated context', 'blend', 'desaturated aerial', 'aerial perspective', 'real world beneath'])
    typologies = _detected_typologies(text)

    reference_bonus = min(len(references), 3) * 0.04
    emphasis = {
        'green_structure': 1.0 + (0.14 if green_structure else 0.0) + reference_bonus,
        'waterfront': 1.0 + (0.16 if waterfront else 0.0),
        'civic_space': 1.0 + (0.10 if civic_space else 0.0),
        'context_softness': 1.0 + (0.08 if softer else 0.0) + reference_bonus,
        'roof_clarity': 1.0 + (0.10 if orthographic else 0.0) + (0.03 if softer else 0.0),
        'illustrative_render': 1.0 + (0.16 if softer else 0.0) + reference_bonus * 0.5,
        'gradient_layering': 1.0 + (0.16 if gradient_layering else 0.0),
        'vegetation_detail': 1.0 + (0.16 if vegetation_detail else 0.0) + reference_bonus * 0.5,
        'formal_allee': 1.0 + (0.18 if formal_allee else 0.0),
        'annotated_typography': 1.0 + (0.12 if annotated_typography else 0.0),
        'integrated_context': 1.0 + (0.16 if integrated_context else 0.0),
        'typology_specificity': 1.0 + (0.08 if typologies else 0.0),
    }

    presentation_keywords: list[str] = []
    if softer or style_key == 'illustrative_landscape_plan':
        presentation_keywords.extend(['Illustrative Rendered', 'Digital Watercolor'])
    if gradient_layering:
        presentation_keywords.extend(['Gradient Layering', 'Soft Shadows'])
    if vegetation_detail:
        presentation_keywords.append('Detailed Vegetation Texture')
    if formal_allee:
        presentation_keywords.append('Formal Allee')
    if annotated_typography:
        presentation_keywords.append('Annotated Typography')
    if integrated_context:
        presentation_keywords.append('Integrated Context')

    return {
        'knowledge_base_version': MASTER_PLAN_KNOWLEDGE_BASE_VERSION,
        'style_key': style_key,
        'style_name': style_name,
        'source_documents': MASTER_PLAN_KNOWLEDGE_SOURCES,
        'reference_signals': REFERENCE_PLAN_SIGNALS,
        'prompt_schema_hints': PRESENTATION_PROMPT_HINTS,
        'presentation_keywords': presentation_keywords,
        'typology_hints': typologies,
        'palette': _palette_summary(palette),
        'composition': {
            'site_vs_context': 'Muted, desaturated context should recede behind the site composition.',
            'street_hierarchy': 'Primary boulevards, secondary streets, promenades, and pedestrian paths should be distinguishable at a glance.',
            'landscape_structure': 'Green space should connect blocks, edges, courtyards, and water rather than appear as leftover filler.',
            'building_readability': 'Roofs should stay light with restrained shadows so orthographic massing remains legible.',
            'presentation_schema': 'Rendered illustrative boards should use digital watercolor texture, gradient layering, and elegant annotations rather than flat fills and generic symbols.',
        },
        'land_use_color_logic': LBCS_COLOR_LOGIC,
        'two_d_render_directives': TWO_D_RENDER_DIRECTIVES,
        'three_d_scene_directives': THREE_D_SCENE_DIRECTIVES,
        'emphasis': emphasis,
        'reference_image_count': len(references),
    }


def build_site_preview_design_brief(
    *,
    has_water: bool,
    has_parks: bool,
    has_reference_images: bool,
) -> list[str]:
    directives = [
        'Keep the overall plan legible from above: major streets first, secondary lanes second, open-space connectors third.',
        'Let the site read as the figure against a quieter surrounding context with a restrained material palette.',
        'Favor tree-lined edges, planted buffers, and readable courtyards over leftover hardscape.',
        'Push the output toward a rendered-illustrative board with soft shadows, digital watercolor texture, and integrated annotations rather than a flat schematic.',
    ]
    if has_parks:
        directives.append('Use parks and courtyards as connective green structure that links blocks and civic destinations.')
    if has_water:
        directives.append('Treat water edges as premium public realm with promenades, planting buffers, and clearly defined embankments.')
    if has_reference_images:
        directives.append('Translate any selected archetype or precedent references into plan-view cues like massing softness, canopy rhythm, and material tone instead of copying or pasting imagery literally.')
    return directives


