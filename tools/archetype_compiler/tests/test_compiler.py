"""Unit tests for the archetype -> Building Grammar compiler.

Fixtures mirror real export_catalog.ts payload shapes (not hand-invented
schemas): field names match frontend/src/data/buildingArchetypes.json and the
derived generationStyleInput from aestheticCatalog.ts.
"""
from __future__ import annotations

import pytest

from compiler import compile_archetype
from schema import SCHEMA_VERSION, BuildingGrammar, GrammarError


def payload_mixed_use_midrise(**overrides):
    base = {
        "exportSchema": "archetype-source@1",
        "archetypeId": "rndsqr_terraced_mixed_use_midrise",
        "archetypeLabel": "RNDSQR Terraced Mixed-Use Mid-Rise",
        "developmentType": "mixed_use",
        "buildingSubcategory": "Mixed-Use – Residential over Retail (Mid-Rise Infill)",
        "aestheticCategoryId": "contemporary_urban",
        "generationTags": ["mixed_use", "mid_rise", "ground_floor_retail", "terraced"],
        "styleProfile": {
            "materials": ["charcoal-black metal panel", "warm natural wood soffits"],
            "massing": "Steps down to 2-3 storeys at the corner, stepped terraces toward the rear",
        },
        "generationStyleInput": {
            "archetypeId": "rndsqr_terraced_mixed_use_midrise_variant_0",
            "downstreamHints": {
                "reuseKeys": [
                    "rndsqr_terraced_mixed_use_midrise",
                    "contemporary_urban",
                    "Mixed-Use – Residential over Retail (Mid-Rise Infill)",
                ]
            },
        },
        "facadeDetail": {
            "primaryMaterial": "charcoal-black metal panel and textural corrugated steel",
            "secondaryMaterial": "warm natural wood soffits and accent bays",
            "accentMaterial": "matte-black metal balcony railings",
            "groundFloor": "fully glazed active retail and restaurant frontage",
            "upperFloors": "stepped residential floors with recessed balconies",
        },
        "roofDetail": {
            "form": "articulated roofscape of pitched and flat planes with rooftop terraces",
            "material": "membrane flat roofs and timber decking",
            "features": "rooftop terraces, screened mechanical",
        },
        "palette": {"window": "#28323C"},
        "dimensions": {
            "suggestedWidth_m": 38, "suggestedDepth_m": 30,
            "minWidth_m": 24, "maxWidth_m": 60, "minDepth_m": 20, "maxDepth_m": 45,
            "minFloors": 3, "maxFloors": 12, "suggestedFloorHeight": 3.6,
        },
        "variants": [],
        "selectedVariant": None,
    }
    base.update(overrides)
    return base


def payload_low_rise_residential():
    return {
        "archetypeId": "scandinavian_urban_residential",
        "archetypeLabel": "Scandinavian Urban Residential",
        "developmentType": "residential_multifamily",
        "aestheticCategoryId": "scandinavian_nordic",
        "generationTags": ["nordic", "residential"],
        "styleProfile": {"massing": "Low-mid rise residential"},
        "facadeDetail": {
            "primaryMaterial": "white plaster over insulated masonry",
            "secondaryMaterial": "painted timber accents",
            "upperFloors": "recessed balconies with slim railings",
        },
        "roofDetail": {"form": "shallow mono-pitch with clean edge", "material": "standing seam metal"},
        "dimensions": {
            "suggestedWidth_m": 20, "suggestedDepth_m": 16,
            "minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 3.0,
        },
    }


def test_mixed_use_midrise_gets_retail_podium_and_setback():
    grammar = compile_archetype(payload_mixed_use_midrise())
    assert grammar.schema_version == SCHEMA_VERSION
    assert grammar.massing.has_podium_retail is True
    assert grammar.dimensions.podium_height_m == pytest.approx(4.5)
    assert grammar.massing.has_setback is True  # default floors round((3+12)/2)=8 >= 6
    assert grammar.dimensions.default_floors == 8
    assert grammar.dimensions.width_m == 38
    # provenance preserved
    assert grammar.source.archetype_id == "rndsqr_terraced_mixed_use_midrise"
    assert "rndsqr_terraced_mixed_use_midrise" in grammar.source.reuse_keys
    assert "contemporary_urban" in grammar.source.reuse_keys
    assert grammar.source.generation_archetype_id == "rndsqr_terraced_mixed_use_midrise_variant_0"


def test_low_rise_residential_no_retail_recessed_balconies():
    grammar = compile_archetype(payload_low_rise_residential())
    assert grammar.massing.has_podium_retail is False
    assert grammar.dimensions.podium_height_m < 4.5
    assert grammar.facade.balcony_mode == "recessed"
    assert grammar.dimensions.default_floors == 3
    assert grammar.massing.has_setback is False
    # white plaster -> light primary material
    assert grammar.materials.primary.base_color == "#e8e6e0"


def test_townhouse_gets_wide_bays():
    payload = payload_mixed_use_midrise(
        archetypeId="victorian_townhouse_row",
        developmentType="residential_townhouse",
        generationTags=["townhouse", "rowhouse"],
        buildingSubcategory="Residential – Townhouse / Rowhouse",
    )
    payload["dimensions"] = {"suggestedWidth_m": 30, "suggestedDepth_m": 12, "minFloors": 2, "maxFloors": 3}
    grammar = compile_archetype(payload)
    assert grammar.facade.bay_width_m == pytest.approx(5.4)


def test_tower_podium_gets_narrow_bays_and_setback():
    payload = payload_mixed_use_midrise(
        archetypeId="plus15_mixed_use_tower",
        generationTags=["tower", "podium", "curtain_wall"],
    )
    payload["styleProfile"] = {"windowStyle": "curtain wall", "massing": "tower on podium with setback crown"}
    payload["dimensions"] = {"suggestedWidth_m": 36, "suggestedDepth_m": 32, "minFloors": 8, "maxFloors": 30}
    grammar = compile_archetype(payload, floors=12)
    assert grammar.facade.bay_width_m == pytest.approx(2.4)
    assert grammar.dimensions.default_floors == 12
    assert grammar.massing.has_setback is True


def test_missing_optional_metadata_uses_deterministic_defaults():
    grammar = compile_archetype({"archetypeId": "bare_bones"})
    assert grammar.family_id == "bare-bones"
    assert grammar.dimensions.width_m == 24.0
    assert grammar.dimensions.depth_m == 18.0
    assert grammar.materials.primary.base_color == "#c9c2b4"  # neutral default
    assert grammar.roof.type == "flat"
    # runs validate() without raising
    grammar.validate()


def test_no_archetype_id_is_an_error():
    with pytest.raises(GrammarError, match="archetypeId"):
        compile_archetype({})


def test_malformed_dimensions_raise_actionable_error():
    payload = payload_mixed_use_midrise()
    payload["dimensions"] = {"suggestedWidth_m": 1.0, "suggestedDepth_m": 30}  # below 3 m floor
    with pytest.raises(GrammarError, match="width_m"):
        compile_archetype(payload)


def test_gabled_roof_inference():
    payload = payload_low_rise_residential()
    payload["roofDetail"] = {"form": "asymmetric pitched with deep eaves", "material": "black metal standing seam"}
    grammar = compile_archetype(payload)
    assert grammar.roof.type == "gabled"
    assert grammar.roof.parapet is False


def test_flat_roof_with_green_roof_inference():
    payload = payload_low_rise_residential()
    payload["roofDetail"] = {
        "form": "flat with communal roof garden",
        "material": "extensive green roof with sedum",
        "features": "timber-clad mechanical housing",
    }
    grammar = compile_archetype(payload)
    assert grammar.roof.type == "flat"
    assert grammar.roof.green_roof is True
    assert grammar.roof.mechanical_screen is True


def test_variant_override_changes_family_and_materials():
    payload = payload_mixed_use_midrise()
    payload["selectedVariant"] = {
        "id": "rndsqr_midrise_charred",
        "label": "Charred Variant",
        "facadeDetail": {"primaryMaterial": "charred timber cladding (shou sugi ban)"},
        "roofDetail": {"form": "asymmetric pitched with deep eaves"},
        "minFloors": 4,
        "maxFloors": 6,
        "suggestedFloorHeight": 3.1,
    }
    grammar = compile_archetype(payload)
    assert grammar.family_id == "rndsqr-midrise-charred"
    assert grammar.source.variant_id == "rndsqr_midrise_charred"
    assert grammar.materials.primary.base_color == "#2e2a26"  # shou sugi ban
    assert grammar.roof.type == "gabled"
    assert grammar.dimensions.min_floors == 4
    assert grammar.dimensions.max_floors == 6
    assert grammar.dimensions.floor_height_m == pytest.approx(3.1)


def test_floor_override_clamped_to_catalogue_range():
    grammar = compile_archetype(payload_mixed_use_midrise(), floors=40)
    assert grammar.dimensions.default_floors == 12  # clamped to maxFloors
    assert any("clamped" in note for note in grammar.notes)


def test_grammar_round_trips_through_dict():
    grammar = compile_archetype(payload_mixed_use_midrise())
    data = grammar.to_dict()
    rebuilt = BuildingGrammar.from_dict(data)
    assert rebuilt.to_dict() == data


@pytest.mark.parametrize(
    ("primary", "secondary", "ground", "expected"),
    [
        ("cross-laminated timber panels", "floor-to-ceiling curtain wall glazing", "timber portal", "timber_grid"),
        ("smooth white mineral render", "dark metal panels", "recessed lobby", "punched_render"),
        ("dark red-brown running bond brick", "bronze anodized frames", "arched masonry portal", "brick_bays"),
        ("textured limestone panels", "corten upper band", "formal colonnade", "stone_frame"),
    ],
)
def test_facade_system_is_derived_from_catalogue_prose(primary, secondary, ground, expected):
    payload = payload_mixed_use_midrise()
    payload["facadeDetail"] = {
        "primaryMaterial": primary,
        "secondaryMaterial": secondary,
        "accentMaterial": secondary,
        "groundFloor": ground,
        "upperFloors": "residential balconies",
    }
    grammar = compile_archetype(payload)
    assert grammar.facade.system == expected
    assert grammar.facade.window_recess_m > 0


def test_schema_v1_grammar_is_upgraded_with_v3_facade_graph_defaults():
    data = compile_archetype(payload_mixed_use_midrise()).to_dict()
    data["schema_version"] = 1
    data.pop("facade_graph", None)
    for key in (
        "system", "window_recess_m", "panel_projection_m", "material_bay_frequency",
        "feature_bay_frequency", "planter_frequency", "balcony_guard", "entrance_type", "top_band",
    ):
        data["facade"].pop(key, None)
    rebuilt = BuildingGrammar.from_dict(data)
    assert rebuilt.schema_version == SCHEMA_VERSION
    assert rebuilt.facade.system == "regular"
    assert {variant.key for variant in rebuilt.facade_graph.floor_variants} == {"typical_a"}


def test_v3_facade_graph_has_alternating_floors_and_resolved_references():
    payload = payload_mixed_use_midrise()
    payload["facadeDetail"] = {
        "primaryMaterial": "cross-laminated timber panels",
        "secondaryMaterial": "floor-to-ceiling curtain wall glazing",
        "groundFloor": "timber portal and retail glazing",
        "upperFloors": "residential balconies",
    }
    grammar = compile_archetype(payload)
    variants = {variant.key: variant for variant in grammar.facade_graph.floor_variants}
    assert set(variants) == {"typical_a", "typical_b", "upper", "crown"}
    assert variants["typical_a"].bay_sequence != variants["typical_b"].bay_sequence
    assert {zone.kind for zone in grammar.facade_graph.zones} == {"base", "middle", "upper", "crown"}
    grammar.facade_graph.validate()


def test_brick_graph_compiles_true_oriel_and_arch_attachments():
    payload = payload_mixed_use_midrise()
    payload["facadeDetail"] = {
        "primaryMaterial": "dark red-brown running bond brick",
        "secondaryMaterial": "bronze anodized frames",
        "groundFloor": "arched masonry portal",
        "upperFloors": "stacked projecting bays",
    }
    grammar = compile_archetype(payload)
    attachments = {attachment.kind for attachment in grammar.facade_graph.attachments}
    assert {"oriel", "arch", "cornice"} <= attachments
