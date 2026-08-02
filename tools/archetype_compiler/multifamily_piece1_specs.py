"""Reference-locked contracts for Piece 1 of multifamily completion.

The first piece closes the Contemporary Mid-Rise Residential catalogue parent.
Only the Timber & Glass pilot is enabled until its comparison sheet receives
visual approval; the two remaining sibling variants are intentionally deferred.
"""
from __future__ import annotations


GOALPOST_CELLS = {
    "front-elevation-source-v1.png": (0.002, 0.002, 0.498, 0.498),
    "street-hero-source-v1.png": (0.502, 0.002, 0.998, 0.498),
    "rear-corner-source-v1.png": (0.002, 0.502, 0.498, 0.998),
    "aerial-roof-source-v1.png": (0.502, 0.502, 0.998, 0.998),
}


# This board was authored with the occupied glass sample in the top-centre
# cell.  The names deliberately register semantic purpose rather than relying
# on the generic Wave 14 cell order.
MATERIAL_CELLS = {
    "material-a-source-v1.png": (0.002, 0.002, 0.331, 0.498),
    "occupied-depth-source-v1.png": (0.335, 0.002, 0.665, 0.498),
    "material-c-source-v1.png": (0.669, 0.002, 0.998, 0.498),
    "material-d-source-v1.png": (0.002, 0.502, 0.331, 0.998),
    "material-b-source-v1.png": (0.335, 0.502, 0.665, 0.998),
    "material-f-source-v1.png": (0.669, 0.502, 0.998, 0.998),
}


FAMILIES: dict[str, dict] = {
    "contemporary-timber-glass-midrise": {
        "archetype_id": "contemporary_midrise_residential",
        "variant_id": "contemporary_midrise_variant_timber_glass",
        "label": "Contemporary Mid-Rise Residential - Timber & Glass",
        "shape": "contemporary_timber_glass_midrise",
        "cohort": "multifamily_parent_completion_pilot",
        "native": (32.0, 22.0, 21.4),
        "native_floors": 6,
        "min_floors": 4,
        "max_floors": 8,
        "floor_height": 3.15,
        "podium_height": 3.85,
        "crown_height": 3.20,
        "roof_height": 1.25,
        "catalogue_slug": "contemporary_mid_rise_residential",
        "catalogue_variant_index": 0,
        "identity": (
            "A six-storey honey-amber mass-timber apartment building exposes a "
            "continuous glulam post-and-beam grid around deep neutral low-iron "
            "glazing, alternating planted balcony bays, and a carved double-height "
            "central lobby; the set-back sixth floor opens to timber terraces beneath "
            "a roof divided between sedum, framed photovoltaic arrays and communal deck."
        ),
        "material_zones": (
            "honey-amber larch and glulam structure; pale board-formed concrete plinth "
            "and lobby threshold; deep timber-framed balconies with dark soil and mixed "
            "green planting; slim graphite aluminum window, guard and photovoltaic frames; "
            "neutral high-transmission low-iron glass revealing warm occupied rooms; "
            "sedum roof beds, timber terrace decking, gravel fire breaks and dark blue-black photovoltaic cells"
        ),
        "glass_profile": (
            "neutral_high_transmission_low_iron_residential_glass_with_warm_occupied_room_depth"
        ),
        "aliases": [
            "contemporary_midrise_residential",
            "contemporary_midrise_variant_timber_glass",
            "contemporary_timber_glass_midrise",
            "timber_glass_biophilic_midrise",
            "mass_timber_balcony_apartments",
        ],
        "reuse_keys": [
            "Contemporary Mid-Rise Residential Timber and Glass",
            "Mass Timber Balcony Apartments",
            "Biophilic Glulam Mid-Rise",
            "Timber Frame Low-Iron Glass Housing",
        ],
        "design_lock": (
            "32 m by 22 m and exactly six occupied levels: one pale-concrete ground floor, "
            "four full upper residential floors, and one set-back sixth floor; a real "
            "double-height glazed lobby is carved through the centre of the front rather "
            "than printed onto it; exposed glulam columns and beams form six broad coherent "
            "front bays; alternating outer bays project as supported timber balconies with "
            "open guards and integral planters; every glazed bay has occupied depth, pane, "
            "frame and wall return; the roof visibly separates sedum, PV, gravel drainage "
            "and a communal timber terrace"
        ),
        "palette": {
            "primary": (
                "honey amber larch and exposed glulam with legible end grain and joints",
                (181, 124, 67),
                "wood",
            ),
            "secondary": (
                "pale board formed concrete plinth and entrance threshold",
                (181, 178, 168),
                "stone",
            ),
            "ornament": (
                "timber balcony planter with dark soil and mixed green planting",
                (105, 126, 70),
                "plant",
            ),
            "frame": (
                "slim graphite aluminum window guard and photovoltaic framing",
                (44, 48, 47),
                "metal",
            ),
            "glass": (
                "neutral low iron residential glazing with warm occupied depth",
                (119, 143, 140),
                "glass",
            ),
            "roof": (
                "dark blue black photovoltaic cells with silver rails and sedum roof edge",
                (48, 67, 68),
                "metal",
            ),
        },
        "avoid": (
            "generic timber-clad box, pasted window texture, flat curtain wall, blue mirror "
            "glass, unsupported bolt-on balconies, repeated balcony on every bay, token "
            "green roof, oversized solar panels, opaque lobby, missing secondary elevations, "
            "seven occupied storeys"
        ),
        "development_type": "residential_multifamily",
        "aesthetic": "mass_timber_biophilic_contemporary",
    },
}


def goalpost_prompt(family: str) -> str:
    spec = FAMILIES[family]
    return f"""Use case: photorealistic-natural
Asset type: render-locked four-view architectural construction board for a CityPrompt LEGO multifamily variant
Primary request: Design one coherent, physically buildable {spec['label']} from the catalogue contract below and show that exact same building in four equal panels in a precise 2 by 2 grid.
Panel 1: dead-front orthographic elevation, complete building visible. Panel 2: pedestrian-height front-right architectural survey oblique. Panel 3: rear-left oblique proving every material and structural system wraps the secondary elevations. Panel 4: high aerial roof-plan oblique proving roof zoning, setback, terraces, photovoltaics, sedum, drainage and equipment.
Catalogue contract: {spec['identity']}
Building lock: {spec['design_lock']}.
Scene/backdrop: clean warm-light-grey architectural studio ground and backdrop, no neighbors, trees, cars or people.
Style/medium: premium photoreal architectural survey photography and physically plausible construction reference, not concept art.
Lighting/mood: neutral bright overcast survey illumination with soft contact shadows and controlled glass reflections, consistent in every panel.
Materials/textures: {spec['material_zones']}.
Constraints: exact same coherent building topology and exactly six occupied levels in every panel; credible timber load paths; real recessed openings; deep integral balconies; slim physical frames; thin neutral gutters; whole building in every frame; no labels, text, signs, logos or watermark.
Avoid: {spec['avoid']}; perspective distortion, blank sides, changed geometry between panels, entourage, dramatic sunset."""


def material_prompt(family: str) -> str:
    spec = FAMILIES[family]
    return f"""Use case: photorealistic-natural
Asset type: shadow-neutral 3 by 2 construction and occupied-depth material board for the exact {spec['label']} shown in Image 1
Input images: Image 1 is the approved four-view geometry, palette, construction-scale and optical authority.
Primary request: Create six equal square straight-on orthographic samples in a precise 3-column by 2-row grid separated only by thin neutral-grey gutters, with no labels.
Top-left: honey-amber glulam and larch post-and-beam joint with legible timber grain and steel knife-plate connection at authentic construction scale, no complete facade.
Top-center: neutral high-transmission low-iron residential pane seen dead-on, revealing a clean warm occupied room with floor edge, ceiling, curtain, timber furniture and restrained depth; no exterior mullion or facade.
Top-right: integral timber balcony edge and planter with dark soil, mixed grasses and trailing plants at authentic construction scale, no complete balcony elevation.
Bottom-left: pale board-formed concrete threshold meeting a deep glulam entrance canopy with credible flashing and shadow-neutral soffit, no complete entrance.
Bottom-center: sedum roof build-up, gravel fire break, metal drainage edge and dark membrane at authentic construction scale, no complete roof.
Bottom-right: dark blue-black photovoltaic module with fine cell pattern, silver edge frame and raised rail connection at authentic construction scale, no complete array.
Scene/backdrop: flat evenly lit material-capture setup. Style/medium: premium physically based photoreal architectural construction texture reference.
Lighting: diffuse neutral overcast capture; no directional sunlight, baked shadow, vignette or perspective.
Constraints: exact 3 by 2 grid; every sample fills its cell edge-to-edge; no labels, text, logos or watermark; no complete facade or repeated window grid; match Image 1 exactly.
Avoid: cartoon materials, generic substitutions, blue mirror glass, oversized solar cells, decorative border, dramatic lighting, building perspective."""


def with_family(family: str) -> dict:
    config = dict(FAMILIES[family])
    config["family"] = family
    return config
