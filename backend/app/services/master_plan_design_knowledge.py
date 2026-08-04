from __future__ import annotations

import re
from typing import Any, Sequence

MASTER_PLAN_KNOWLEDGE_BASE_VERSION = "2026-03-13"

MASTER_PLAN_KNOWLEDGE_SOURCES = [
    "Official master-plan and district-visualization precedent pages from Gensler, Sasaki, SOM, AECOM, and Stantec",
    "User-supplied 2D orthographic district references with photoreal roofs, paved ground planes, and subdued suburban context",
    "User-supplied 3D aerial-oblique and street-level references showing mixed-use districts, civic parks, and real-world neighborhood continuity",
    "Current SiteForge rendering architecture: deterministic geometry, hidden prompt matrix, aerial underlay registration, and board overlays kept outside image generation",
]

REFERENCE_PLAN_SIGNALS = [
    "the project reads as a complete district rather than isolated building objects",
    "the ground plane carries real information through curbs, asphalt, sidewalks, parking courts, promenades, planting beds, and water edges",
    "buildings define streets, courtyards, and open space through perimeter alignment and coherent frontage",
    "existing neighborhood context stays visible and geographically believable but subdued relative to the proposal",
    "large sites contain at least one primary civic or landscape anchor that organizes the district composition",
]

TWO_D_RENDER_DIRECTIVES = [
    "Construct a photoreal orthographic district visualization rather than an annotated board or abstract land-use diagram.",
    "Fill the site intentionally so every residual area becomes hardscape, softscape, water, or programmed open space instead of undefined blank ground.",
    "Keep the proposal registered to real roads, neighboring houses, and surrounding block structure while maintaining the proposal as the visual priority.",
    "Use realistic roof planes, paving variation, lane geometry, curb definition, parking logic, tree cadence, and landscape texture.",
    "Keep text, legends, scale bars, north arrows, and other editorial graphics out of the generated image entirely.",
]

THREE_D_SCENE_DIRECTIVES = [
    "Render the district as one coherent neighborhood with realistic edges, circulation, and public realm instead of isolated hero buildings.",
    "Preserve the approved 2D site composition, especially block hierarchy, water or civic anchors, podium edges, and street alignment.",
    "For aerial-oblique views, keep surrounding suburban or urban fabric visible so the district feels registered to a real place.",
    "For main-street views, prioritize podium frontage, retail animation, street trees, furnishing, sidewalks, and believable pedestrian scale.",
    "Use clear daylight realism first: balanced contrast, crisp materials, readable planting, and no collage or board overlays.",
]

PRESENTATION_PROMPT_HINTS = {
    "orthographic_terms": ["Photoreal Orthographic Aerial", "district visualization", "true top-down", "roof clarity"],
    "district_terms": ["street wall", "civic anchor", "perimeter block", "public realm hierarchy"],
    "ground_plane_terms": [
        "curb definition",
        "parking geometry",
        "sidewalk network",
        "paved apron",
        "landscape framework",
    ],
    "context_terms": ["subdued existing neighborhood", "registered roads", "real-world context alignment"],
    "three_d_terms": ["district aerial oblique", "main street eye level", "clear daylight mixed-use district"],
}

TYPOLOGY_TOKENS = {
    "Perimeter Mid-Rise Block": ["perimeter block", "courtyard block", "mid-rise block"],
    "Townhouse Edge": ["townhouse", "rowhouse", "row house"],
    "Mixed-Use Podium Tower": ["mixed-use", "mixed use", "podium", "tower"],
    "Civic Park District": ["civic park", "central park", "pond", "water feature", "public realm"],
}

LBCS_COLOR_LOGIC = {
    "residential": "warm neutral / stone / roof gray family",
    "commercial": "deeper neutral / active mixed-use frontage family",
    "industrial": "dark neutral utility family",
    "civic_institutional": "light civic stone family",
    "mobility": "asphalt / curb / concrete family",
    "assembly_open_space": "green open-space family",
    "leisure": "amenity landscape family",
    "natural_systems": "deep green / water-edge family",
}


def _has_any(text: str, tokens: Sequence[str]) -> bool:
    return any(token in text for token in tokens)


def _palette_summary(palette: dict[str, Any]) -> list[str]:
    ordered_keys = ["paper", "site", "park", "water", "road", "path", "roof", "accent"]
    return [
        str(palette[key])
        for key in ordered_keys
        if isinstance(palette.get(key), str) and str(palette[key]).startswith("#")
    ]


def _detected_typologies(text: str) -> list[str]:
    return [label for label, tokens in TYPOLOGY_TOKENS.items() if _has_any(text, tokens)]


def _extract_specific_typologies(prompt_text: str) -> list[str]:
    matches = re.findall(r"specific\s+typology\s*:\s*([^\n,;]+)", prompt_text, flags=re.IGNORECASE)
    output: list[str] = []
    seen: set[str] = set()
    for raw in matches:
        value = str(raw).strip()
        if not value:
            continue
        token = value.lower()
        if token in seen:
            continue
        seen.add(token)
        output.append(value)
    return output


def build_master_plan_style_guide(
    style_key: str,
    style_name: str,
    palette: dict[str, Any],
    prompt: str | None,
    reference_images: Sequence[str] | None = None,
) -> dict[str, Any]:
    prompt_text = prompt or ""
    text = prompt_text.lower()
    references = list(reference_images or [])

    softer = _has_any(text, ["soft", "illustrative", "wash", "watercolor"])
    gradient_layering = _has_any(text, ["gradient layering"])
    formal_allee = _has_any(text, ["formal allee"])
    annotated_typography = _has_any(text, ["annotated typography"])
    orthographic = _has_any(text, ["orthographic", "plan", "master plan", "top-down", "top down"])
    aerial_realism = _has_any(text, ["photoreal", "aerial", "district visualization", "realistic roofs", "drone"])
    green_structure = _has_any(text, ["green", "park", "landscape", "garden", "courtyard", "greenway", "civic"])
    waterfront = _has_any(text, ["waterfront", "river", "canal", "lake", "pond", "shore", "wetland", "basin"])
    civic_space = _has_any(
        text, ["community", "civic", "plaza", "promenade", "boulevard", "main street", "public realm"]
    )
    typologies = _detected_typologies(text)
    typologies.extend(label for label in _extract_specific_typologies(prompt_text) if label not in typologies)

    reference_bonus = min(len(references), 3) * 0.04
    emphasis = {
        "green_structure": 1.0 + (0.14 if green_structure else 0.0) + reference_bonus,
        "waterfront": 1.0 + (0.16 if waterfront else 0.0),
        "civic_space": 1.0 + (0.14 if civic_space else 0.0),
        "context_softness": 1.0 + (0.08 if softer else 0.0) + reference_bonus,
        "roof_clarity": 1.0 + (0.16 if orthographic else 0.0) + (0.08 if aerial_realism else 0.0),
        "ground_plane_clarity": 1.0 + (0.18 if aerial_realism or orthographic else 0.0),
        "district_fill": 1.0 + (0.16 if civic_space or green_structure else 0.0),
        "context_alignment": 1.0 + (0.14 if aerial_realism else 0.0),
        "typology_specificity": 1.0 + (0.08 if typologies else 0.0),
        "illustrative_render": 1.0 + (0.08 if softer else 0.0),
        "gradient_layering": 1.0 + (0.08 if gradient_layering else 0.0),
        "formal_allee": 1.0 + (0.08 if formal_allee else 0.0),
        "annotated_typography": 1.0 + (0.08 if annotated_typography else 0.0),
    }

    presentation_keywords: list[str] = []
    if orthographic or aerial_realism:
        presentation_keywords.extend(["Photoreal Orthographic Aerial", "District Visualization"])
    if _has_any(text, ["digital watercolor"]):
        presentation_keywords.append("Digital Watercolor")
    if civic_space:
        presentation_keywords.append("Civic Anchor")
    if green_structure:
        presentation_keywords.append("Landscape Framework")
    if waterfront:
        presentation_keywords.append("Water Edge")

    return {
        "knowledge_base_version": MASTER_PLAN_KNOWLEDGE_BASE_VERSION,
        "style_key": style_key,
        "style_name": style_name,
        "source_documents": MASTER_PLAN_KNOWLEDGE_SOURCES,
        "reference_signals": REFERENCE_PLAN_SIGNALS,
        "prompt_schema_hints": PRESENTATION_PROMPT_HINTS,
        "presentation_keywords": presentation_keywords,
        "typology_hints": typologies,
        "palette": _palette_summary(palette),
        "composition": {
            "site_vs_context": "Keep existing neighborhood context visible but quieter so the proposal reads as the primary figure.",
            "street_hierarchy": "Primary streets, secondary drives, sidewalks, promenades, and civic paths should be distinguishable at a glance.",
            "landscape_structure": "Landscape should organize blocks, edges, courtyards, and water anchors rather than filling leftover space.",
            "building_readability": "Roofs should remain crisp and light enough to read clearly in orthographic view without turning diagrammatic.",
            "presentation_schema": "Generated imagery should stay image-only; board layout, annotations, legends, and scales belong in deterministic overlays.",
        },
        "land_use_color_logic": LBCS_COLOR_LOGIC,
        "two_d_render_directives": TWO_D_RENDER_DIRECTIVES,
        "three_d_scene_directives": THREE_D_SCENE_DIRECTIVES,
        "emphasis": emphasis,
        "reference_image_count": len(references),
    }


def build_site_preview_design_brief(
    *,
    has_water: bool,
    has_parks: bool,
    has_reference_images: bool,
) -> list[str]:
    directives = [
        "Keep the overall plan strictly top-down and orthographic, with one coherent light direction and one continuous material world.",
        "Construct a district, not isolated footprints: if an area is not a building, it must read clearly as street, hardscape, landscape, or water.",
        "Make the ground plane legible through roads, sidewalks, parking courts, curbs, plazas, promenades, and planted edges so buildings do not float in blank space.",
        "Keep real-world surrounding houses, roads, and context visible but subdued so the proposal stays aligned to place without losing focus.",
        "Preserve hard site geometry and major zone placement while enriching the district with coherent frontage, block structure, and public realm continuity.",
    ]
    if has_parks:
        directives.append(
            "Use parks and courtyards as connective landscape structure, and give larger sites at least one strong civic green anchor."
        )
    if has_water:
        directives.append(
            "Treat water edges as premium public realm with promenades, embankments, and layered planting rather than leftover voids."
        )
    if has_reference_images:
        directives.append(
            "Translate selected references into district-level cues such as typology mix, planting rhythm, material tone, digital watercolor plan-view cues, and public-realm character without copying or pasting imagery literally."
        )
    return directives
