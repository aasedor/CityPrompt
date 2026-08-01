"""Canonical variant-specific design contracts for Wave 14.

Wave 14 deliberately models catalogue siblings as independent families.  A
variant id is therefore a geometry, material, glazing, and silhouette lock —
never a parent-family recolour.  The data in this module is Blender-free so it
can be consumed by the skin builder, model generator, assessors, and tests.
"""
from __future__ import annotations


GOALPOST_CELLS = {
    "front-elevation-source-v1.png": (0.002, 0.002, 0.498, 0.498),
    "street-hero-source-v1.png": (0.502, 0.002, 0.998, 0.498),
    "rear-corner-source-v1.png": (0.002, 0.502, 0.498, 0.998),
    "aerial-roof-source-v1.png": (0.502, 0.502, 0.998, 0.998),
}

MATERIAL_CELLS = {
    "material-a-source-v1.png": (0.002, 0.002, 0.331, 0.498),
    "material-b-source-v1.png": (0.335, 0.002, 0.665, 0.498),
    "material-c-source-v1.png": (0.669, 0.002, 0.998, 0.498),
    "material-d-source-v1.png": (0.002, 0.502, 0.331, 0.998),
    "occupied-depth-source-v1.png": (0.335, 0.502, 0.665, 0.998),
    "material-f-source-v1.png": (0.669, 0.502, 0.998, 0.998),
}


def _spec(
    *,
    archetype_id: str,
    variant_id: str,
    label: str,
    shape: str,
    native: tuple[float, float, float],
    floors: int,
    min_floors: int,
    max_floors: int,
    floor_height: float,
    podium_height: float,
    crown_height: float,
    roof_height: float,
    catalogue_slug: str,
    catalogue_variant_index: int,
    identity: str,
    materials: str,
    glass_profile: str,
    aliases: list[str],
    reuse_keys: list[str],
    design_lock: str,
    palette: dict[str, tuple[str, tuple[int, int, int], str]],
    avoid: str,
    development_type: str,
    aesthetic: str,
) -> dict:
    return {
        "archetype_id": archetype_id,
        "variant_id": variant_id,
        "label": label,
        "shape": shape,
        "native": native,
        "native_floors": floors,
        "min_floors": min_floors,
        "max_floors": max_floors,
        "floor_height": floor_height,
        "podium_height": podium_height,
        "crown_height": crown_height,
        "roof_height": roof_height,
        "catalogue_slug": catalogue_slug,
        "catalogue_variant_index": catalogue_variant_index,
        "identity": identity,
        "material_zones": materials,
        "glass_profile": glass_profile,
        "aliases": aliases,
        "reuse_keys": reuse_keys,
        "design_lock": design_lock,
        "palette": palette,
        "avoid": avoid,
        "development_type": development_type,
        "aesthetic": aesthetic,
    }


FAMILIES: dict[str, dict] = {
    "art-deco-black-chrome-tower": _spec(
        archetype_id="art_deco_setback_tower",
        variant_id="art_deco_black_chrome",
        label="Art Deco Setback Tower - Black Granite and Chrome",
        shape="black_chrome_deco",
        native=(35.0, 30.0, 74.0),
        floors=24,
        min_floors=20,
        max_floors=35,
        floor_height=3.65,
        podium_height=7.3,
        crown_height=2.0,
        roof_height=8.2,
        catalogue_slug="art_deco_setback_tower",
        catalogue_variant_index=1,
        identity="A polished black-granite twenty-four-storey setback tower is drawn upward by continuous chrome fins, narrow smoky geometric windows, three streamlined shoulders, and a fluted chrome crown and needle finial.",
        materials="polished black granite; fine silver chrome fins and speed bands; charcoal relief stone; neutral smoky low-e glass; warm occupied depth; brushed stainless crown metal and dark terrace membrane",
        glass_profile="neutral_smoky_geometric_glass_block_and_occupied_depth",
        aliases=["art_deco_setback_tower", "art_deco_black_chrome", "black_chrome_art_deco_tower", "streamlined_black_granite_tower"],
        reuse_keys=["Black Chrome Art Deco Tower", "Streamlined Black Granite Tower", "Chrome Fin Setback High Rise"],
        design_lock="35 m by 30 m, 24 occupied storeys grouped behind 15 expressed facade tiers; seven-to-five-to-three-bay black granite setbacks, full-height paired chrome fins, narrow recessed glazing, fluted chrome crown and needle finial",
        palette={
            "primary": ("polished black granite panels", (28, 30, 33), "stone"),
            "secondary": ("mirror-bright architectural chrome", (175, 184, 190), "metal"),
            "ornament": ("charcoal geometric relief stone", (60, 63, 66), "stone"),
            "frame": ("brushed stainless window metal", (123, 132, 138), "metal"),
            "glass": ("neutral smoky low-e vision glass", (62, 73, 78), "glass"),
            "roof": ("dark terrace membrane and chrome crown", (42, 44, 47), "metal"),
        },
        avoid="plain black box, blue mirror curtain wall, gold ornament, cream terra cotta, missing fins, flat crown",
        development_type="mixed_use_highrise",
        aesthetic="art_deco_black_chrome",
    ),
    "art-deco-polychrome-zigzag-tower": _spec(
        archetype_id="art_deco_setback_tower",
        variant_id="art_deco_polychrome",
        label="Art Deco Setback Tower - Polychrome Zigzag Moderne",
        shape="polychrome_deco",
        native=(45.0, 38.0, 91.0),
        floors=32,
        min_floors=30,
        max_floors=45,
        floor_height=2.55,
        podium_height=5.1,
        crown_height=2.1,
        roof_height=10.5,
        catalogue_slug="art_deco_setback_tower",
        catalogue_variant_index=2,
        identity="A thirty-two-storey turquoise-and-cream Zigzag Moderne tower steps from seven to five to three bays above a carved two-storey arched portal, with orange-gold-blue mosaic bands and a compact green pyramidal crown.",
        materials="turquoise glazed terra cotta; warm cream molded terra cotta; orange, gold, deep-blue and turquoise ceramic mosaic; aged bronze frames; neutral smoky low-e glass; warm occupied depth; patinated copper crown and charcoal terrace membrane",
        glass_profile="neutral_smoky_bronze_framed_occupied",
        aliases=["art_deco_setback_tower", "art_deco_polychrome", "polychrome_zigzag_moderne_tower", "turquoise_mosaic_setback_tower"],
        reuse_keys=["Polychrome Zigzag Moderne Tower", "Turquoise Mosaic Setback Tower", "Colorful Terra Cotta High Rise"],
        design_lock="45 m by 38 m, 32 occupied storeys grouped behind 16 large expressed facade tiers; three seven-to-five-to-three-bay setback stages, monumental arched public portal, turquoise/cream solid piers, continuous ceramic chevron belts and green pyramidal crown",
        palette={
            "primary": ("turquoise glazed terra-cotta ashlar", (47, 134, 137), "stone"),
            "secondary": ("warm cream glazed terra-cotta trim", (224, 208, 170), "stone"),
            "ornament": ("orange gold blue turquoise ceramic mosaic", (179, 113, 35), "stone"),
            "frame": ("aged dark bronze architectural metal", (73, 54, 38), "metal"),
            "glass": ("neutral smoky low-e vision glass", (65, 73, 70), "glass"),
            "roof": ("oxidized green copper and charcoal membrane", (60, 115, 105), "metal"),
        },
        avoid="generic box, plain beige facade, omitted arched portal, oversized fantasy mosaic, blue mirror glass, altered crown",
        development_type="mixed_use_highrise",
        aesthetic="zigzag_moderne_polychrome",
    ),
    "mid-century-wood-stone-pavilion": _spec(
        archetype_id="mid_century_modern_pavilion_block",
        variant_id="mid_century_pavilion_wood_stone",
        label="Mid-Century Pavilion - Organic Wood and Stone",
        shape="wood_stone_pavilion",
        native=(38.0, 25.0, 10.8),
        floors=2,
        min_floors=1,
        max_floors=3,
        floor_height=3.45,
        podium_height=3.45,
        crown_height=0.55,
        roof_height=3.35,
        catalogue_slug="mid_century_modern_pavilion_block",
        catalogue_variant_index=1,
        identity="A low two-level organic modern pavilion grows from layered native-stone terraces, warm horizontal timber walls and clear occupied glazing beneath one broad, shallow-hipped sheltering roof.",
        materials="warm horizontal cedar boards; rugged native ledgestone; dark bronze steel; neutral low-iron glass; warm occupied depth; pale concrete terrace; charcoal roof membrane and copper fascia",
        glass_profile="neutral_low_iron_deep_eave_occupied",
        aliases=["mid_century_modern_pavilion_block", "mid_century_pavilion_wood_stone", "organic_wood_stone_pavilion", "wright_inspired_terrace_pavilion"],
        reuse_keys=["Organic Wood Stone Pavilion", "Wright Inspired Terrace Pavilion", "Cantilevered Landscape Pavilion"],
        design_lock="38 m by 25 m, exactly two occupied levels; interlocking stone hearth/core, long timber-and-glass bars, layered cantilevered terraces, and one shallow hip roof with a long ridge and very deep eaves",
        palette={
            "primary": ("warm horizontal cedar siding", (112, 70, 39), "wood"),
            "secondary": ("rugged grey-brown native ledgestone", (98, 92, 78), "stone"),
            "ornament": ("dark bronze structural steel", (53, 48, 43), "metal"),
            "frame": ("dark bronze window frame", (57, 50, 43), "metal"),
            "glass": ("neutral low-iron glass", (111, 127, 124), "glass"),
            "roof": ("charcoal membrane and aged copper fascia", (51, 52, 49), "metal"),
        },
        avoid="generic glass cube, flat box, white concrete, suburban pitched house, shallow eaves, fake stone wallpaper",
        development_type="commercial_cultural_lowrise",
        aesthetic="organic_mid_century_modern",
    ),
    "mid-century-white-brise-soleil-pavilion": _spec(
        archetype_id="mid_century_modern_pavilion_block",
        variant_id="mid_century_pavilion_white_concrete",
        label="Mid-Century Pavilion - White Concrete Brise-Soleil",
        shape="white_concrete_pavilion",
        native=(31.0, 23.0, 11.8),
        floors=2,
        min_floors=1,
        max_floors=4,
        floor_height=3.55,
        podium_height=3.55,
        crown_height=0.45,
        roof_height=3.75,
        catalogue_slug="mid_century_modern_pavilion_block",
        catalogue_variant_index=2,
        identity="A white concrete two-storey pavilion is lifted on slender pilotis, wrapped by dense open-cell brise-soleil screens, and crowned by a recessed glazed garden room beneath one wafer-thin flat canopy.",
        materials="warm white board-formed concrete; perforated breeze-block ceramic; charcoal steel frames; neutral clear low-e glass; occupied gallery depth; pale terrazzo; white aluminum flat canopy and planted terrace",
        glass_profile="neutral_clear_screened_gallery_occupied",
        aliases=["mid_century_modern_pavilion_block", "mid_century_pavilion_white_concrete", "white_brise_soleil_pavilion", "pilotis_butterfly_roof_pavilion"],
        reuse_keys=["White Brise Soleil Pavilion", "Pilotis Butterfly Roof Pavilion", "Breeze Block Modernist Gallery"],
        design_lock="31 m by 23 m, two principal occupied levels; recessed ground plane on pilotis, dense physical breeze-block screens with open cells, planted upper terrace, recessed glazed garden room and a wafer-thin flat white canopy",
        palette={
            "primary": ("warm white board-formed concrete", (224, 222, 211), "stone"),
            "secondary": ("white perforated breeze block", (214, 211, 196), "stone"),
            "ornament": ("pale terrazzo and planter stone", (180, 178, 166), "stone"),
            "frame": ("charcoal painted steel", (48, 51, 51), "metal"),
            "glass": ("neutral clear low-e gallery glass", (125, 143, 140), "glass"),
            "roof": ("warm white aluminum roof and green planting", (206, 207, 198), "metal"),
        },
        avoid="solid screen texture, generic white box, thick canopy, missing pilotis, blue glass, closed breeze-block cells",
        development_type="commercial_cultural_lowrise",
        aesthetic="mid_century_brazilian_modern",
    ),
    "modern-black-screen-machiya": _spec(
        archetype_id="japanese_machiya_mixed_use",
        variant_id="machiya_modern_reinterpretation",
        label="Japanese Machiya - Modern Black Screen",
        shape="modern_machiya",
        native=(13.0, 18.0, 17.8),
        floors=4,
        min_floors=3,
        max_floors=6,
        floor_height=3.25,
        podium_height=3.45,
        crown_height=0.55,
        roof_height=4.25,
        catalogue_slug="japanese_machiya_mixed_use",
        catalogue_variant_index=1,
        identity="A narrow four-level contemporary machiya hides clear occupied rooms behind a full-height black metal koshi screen, a deeply cut ground passage and tsuboniwa, beneath a compact dark hip and screened rooftop garden.",
        materials="matte blackened steel lattice; charred cedar; graphite metal panels; neutral clear glass; warm occupied depth; dark basalt plinth; charcoal zinc roof and planted courtyard",
        glass_profile="neutral_clear_full_height_screened_occupied",
        aliases=["japanese_machiya_mixed_use", "machiya_modern_reinterpretation", "modern_black_screen_machiya", "contemporary_koshi_townhouse"],
        reuse_keys=["Modern Black Screen Machiya", "Contemporary Koshi Townhouse", "Urban Tsuboniwa Mixed Use"],
        design_lock="13 m by 18 m, four occupied levels; one continuous black vertical screen with real gaps, recessed glass rooms, carved ground passage and visible courtyard, shallow dark hip and screened rooftop garden",
        palette={
            "primary": ("matte blackened steel koshi slats", (31, 34, 34), "metal"),
            "secondary": ("charred cedar shou sugi ban", (43, 39, 35), "wood"),
            "ornament": ("dark basalt plinth", (58, 58, 54), "stone"),
            "frame": ("graphite aluminum frame", (46, 49, 50), "metal"),
            "glass": ("neutral clear low-e glass", (91, 107, 105), "glass"),
            "roof": ("charcoal zinc standing seam", (54, 58, 59), "metal"),
        },
        avoid="traditional red timber shop, generic black box, pasted stripe texture, sealed entrance, missing courtyard, pagoda roof",
        development_type="mixed_use_lowrise",
        aesthetic="contemporary_japanese_machiya",
    ),
    "red-machiya-cafe-gallery": _spec(
        archetype_id="japanese_machiya_mixed_use",
        variant_id="machiya_cafe_gallery",
        label="Japanese Machiya - Red Cafe Gallery",
        shape="cafe_machiya",
        native=(18.0, 15.0, 10.9),
        floors=2,
        min_floors=1,
        max_floors=4,
        floor_height=3.25,
        podium_height=3.25,
        crown_height=0.65,
        roof_height=4.4,
        catalogue_slug="japanese_machiya_mixed_use",
        catalogue_variant_index=2,
        identity="A converted two-storey machiya cafe-gallery keeps its vermilion timber frame, fine red koshi, pale earthen walls and deep kawara roof while opening one large ground room and side passage toward a planted inner court.",
        materials="weathered vermilion cedar; pale ochre earthen plaster; charcoal kawara tile; dark bronze frames; clear neutral glass; warm cafe/gallery depth; woven bamboo blinds and grey stone",
        glass_profile="neutral_clear_koshi_and_bamboo_screened_occupied",
        aliases=["japanese_machiya_mixed_use", "machiya_cafe_gallery", "red_machiya_cafe_gallery", "vermilion_koshi_gallery_house"],
        reuse_keys=["Red Machiya Cafe Gallery", "Vermilion Koshi Gallery House", "Converted Kyoto Cafe"],
        design_lock="18 m by 15 m, two occupied levels; vermilion post-and-beam frame, fine red lattice, open ground cafe room and side passage, bamboo blinds, earthen infill and a deep individually tiled gable roof",
        palette={
            "primary": ("weathered vermilion cedar", (133, 50, 35), "wood"),
            "secondary": ("pale ochre earthen plaster", (191, 167, 126), "stone"),
            "ornament": ("woven bamboo blind", (153, 126, 79), "wood"),
            "frame": ("dark bronze glazing frame", (65, 52, 41), "metal"),
            "glass": ("neutral clear shopfront glass", (112, 124, 116), "glass"),
            "roof": ("charcoal glazed kawara tile", (54, 56, 54), "stone"),
        },
        avoid="black contemporary facade, generic Asian restaurant, sealed shopfront, cartoon red, oversized lattice, flat roof",
        development_type="mixed_use_lowrise",
        aesthetic="adaptive_reuse_japanese_machiya",
    ),
    "dark-frame-clear-glass-office": _spec(
        archetype_id="modern_glass_office_institutional",
        variant_id="glass_office_dark_frame",
        label="Modern Glass Office - Dark Expressed Frame",
        shape="dark_frame_office",
        native=(35.0, 25.0, 24.5),
        floors=5,
        min_floors=4,
        max_floors=10,
        floor_height=4.15,
        podium_height=4.35,
        crown_height=0.7,
        roof_height=3.0,
        catalogue_slug="modern_glass_office_institutional",
        catalogue_variant_index=2,
        identity="A compact five-level office exposes a heavy charcoal steel exoskeleton around exceptionally clear occupied glass, with bright slab datums, a recessed double-height corner lobby, and a transparent rooftop greenhouse room.",
        materials="matte charcoal structural steel; neutral low-iron glass; bright concrete slab edges; warm occupied office depth; black aluminum pressure caps; pale lobby terrazzo; clear rooftop greenhouse and zinc roof",
        glass_profile="high_transmission_low_iron_revealing_occupied_floorplates",
        aliases=["modern_glass_office_institutional", "glass_office_dark_frame", "dark_frame_clear_glass_office", "expressed_steel_grid_office"],
        reuse_keys=["Dark Frame Clear Glass Office", "Expressed Steel Grid Office", "Transparent Rooftop Greenhouse Office"],
        design_lock="35 m by 25 m, five occupied levels; external four-by-five charcoal steel grid, clear recessed glass, visible white floor plates and warm rooms, cut-away corner lobby and transparent rooftop pavilion",
        palette={
            "primary": ("matte charcoal structural steel", (38, 42, 44), "metal"),
            "secondary": ("bright smooth concrete slab edge", (177, 180, 176), "stone"),
            "ornament": ("pale lobby terrazzo", (166, 165, 154), "stone"),
            "frame": ("black aluminum pressure cap", (42, 46, 48), "metal"),
            "glass": ("neutral high-transmission low-iron glass", (111, 132, 133), "glass"),
            "roof": ("clear greenhouse glass and zinc", (100, 119, 118), "glass"),
        },
        avoid="blue mirror office box, hidden structure, opaque spandrel bands, blank rooms, generic tower, solid rooftop box",
        development_type="office_institutional_midrise",
        aesthetic="expressed_structure_high_tech",
    ),
    "mass-timber-glass-office": _spec(
        archetype_id="modern_glass_office_institutional",
        variant_id="glass_office_timber_hybrid",
        label="Modern Glass Office - Mass Timber Hybrid",
        shape="timber_hybrid_office",
        native=(45.0, 28.0, 23.0),
        floors=5,
        min_floors=5,
        max_floors=12,
        floor_height=3.75,
        podium_height=4.0,
        crown_height=0.55,
        roof_height=3.7,
        catalogue_slug="modern_glass_office_institutional",
        catalogue_variant_index=3,
        identity="A broad five-level mass-timber office displays honey glulam columns, CLT floor plates and tree-filled occupied rooms through clear glass, stepping into two sawtooth volumes beneath metal clerestory roofs.",
        materials="honey glulam; pale CLT end grain and slab edges; graphite steel connectors; neutral low-iron glass; biophilic occupied depth; pale concrete plinth; silver standing-seam clerestory roof",
        glass_profile="neutral_low_iron_revealing_mass_timber_and_biophilic_depth",
        aliases=["modern_glass_office_institutional", "glass_office_timber_hybrid", "mass_timber_glass_office", "glulam_biophilic_office"],
        reuse_keys=["Mass Timber Glass Office", "Glulam Biophilic Office", "CLT Clerestory Workplace"],
        design_lock="45 m by 28 m, five occupied levels in two stepped bars; complete external glulam bay frame, visible CLT slabs, clear glass and planted interior depth, sawtooth clerestory roof and recessed entry court",
        palette={
            "primary": ("honey-toned exposed glulam", (159, 110, 61), "wood"),
            "secondary": ("pale CLT slab edge", (190, 151, 102), "wood"),
            "ornament": ("graphite steel connector", (55, 59, 59), "metal"),
            "frame": ("dark bronze curtain-wall cap", (57, 56, 50), "metal"),
            "glass": ("neutral low-iron glass", (116, 139, 135), "glass"),
            "roof": ("silver standing-seam clerestory metal", (136, 140, 137), "metal"),
        },
        avoid="generic glass cube, orange plastic wood, concealed columns, blue mirror glass, flat anonymous roof, unoccupied interior",
        development_type="office_institutional_midrise",
        aesthetic="mass_timber_biophilic_modern",
    ),
    "streamline-moderne-theater": _spec(
        archetype_id="deco_theater_mainstreet",
        variant_id="deco_theater_streamline",
        label="Deco Theater - Streamline Moderne",
        shape="streamline_theater",
        native=(27.0, 32.0, 19.0),
        floors=3,
        min_floors=2,
        max_floors=5,
        floor_height=4.0,
        podium_height=5.0,
        crown_height=2.0,
        roof_height=5.0,
        catalogue_slug="deco_theater_mainstreet",
        catalogue_variant_index=1,
        identity="A three-level Streamline Moderne theater rounds both street corners around a broad white lobby, curved glass-block ribbons, sweeping pink-and-blue neon speed bands, a cantilevered marquee and an integrated fin-shaped blade tower.",
        materials="smooth warm-white render; pale cream terrazzo; clear and translucent glass block; neutral curved lobby glass; warm occupied lobby depth; brushed stainless trim; restrained pink and blue neon; charcoal auditorium roof",
        glass_profile="curved_clear_lobby_plus_translucent_glass_block_occupied",
        aliases=["deco_theater_mainstreet", "deco_theater_streamline", "streamline_moderne_theater", "curved_neon_corner_cinema"],
        reuse_keys=["Streamline Moderne Theater", "Curved Neon Corner Cinema", "Glass Block Deco Theater"],
        design_lock="27 m by 32 m, three occupied public levels; two rounded front corners and a broad central lobby form one facade with real curved glazing and glass-block ribbons, sweeping neon speed lines, projecting marquee, integral vertical fin and deep auditorium volume",
        palette={
            "primary": ("smooth warm-white mineral render", (225, 220, 207), "stone"),
            "secondary": ("translucent glass block", (160, 177, 174), "glass"),
            "ornament": ("pink and blue neon enamel", (183, 75, 126), "metal"),
            "frame": ("brushed stainless architectural trim", (145, 151, 151), "metal"),
            "glass": ("neutral curved lobby glass", (104, 126, 125), "glass"),
            "roof": ("charcoal auditorium membrane", (53, 55, 55), "stone"),
        },
        avoid="generic rectangular cinema, pasted corner window, detached blade sign, ornate movie palace, square lobby, missing neon bands",
        development_type="cultural_entertainment_lowrise",
        aesthetic="streamline_moderne",
    ),
    "egyptian-revival-theater": _spec(
        archetype_id="deco_theater_mainstreet",
        variant_id="deco_theater_egyptian_revival",
        label="Deco Theater - Egyptian Revival",
        shape="egyptian_theater",
        native=(30.0, 34.0, 18.5),
        floors=3,
        min_floors=2,
        max_floors=5,
        floor_height=4.0,
        podium_height=5.2,
        crown_height=2.3,
        roof_height=4.0,
        catalogue_slug="deco_theater_mainstreet",
        catalogue_variant_index=2,
        identity="An ochre Egyptian Revival theater forms a deep ceremonial entrance between battered pylons and four lotus columns, crowned by a winged sun disk, small scarab reliefs, turquoise-copper bands and a projecting bronze marquee.",
        materials="warm ochre limestone; sand-colored stucco; turquoise and oxidized copper inlay; dark bronze doors and marquee; neutral smoky lobby glass; warm occupied lobby depth; charcoal auditorium roof",
        glass_profile="neutral_smoky_bronze_framed_ceremonial_lobby",
        aliases=["deco_theater_mainstreet", "deco_theater_egyptian_revival", "egyptian_revival_theater", "lotus_pylon_cinema"],
        reuse_keys=["Egyptian Revival Theater", "Lotus Pylon Cinema", "Winged Sun Mainstreet Theater"],
        design_lock="30 m by 34 m, three public levels; two battered entrance pylons, four separate lotus columns, deep shadowed entry court, winged sun and scarab relief, turquoise-copper friezes, integrated bronze marquee and rear auditorium",
        palette={
            "primary": ("warm ochre limestone ashlar", (191, 146, 82), "stone"),
            "secondary": ("sand-colored mineral stucco", (205, 178, 129), "stone"),
            "ornament": ("turquoise enamel and oxidized copper", (45, 133, 132), "metal"),
            "frame": ("dark bronze ceremonial metalwork", (78, 56, 36), "metal"),
            "glass": ("neutral smoky lobby glass", (78, 91, 88), "glass"),
            "roof": ("charcoal auditorium membrane", (54, 55, 52), "stone"),
        },
        avoid="Greek temple, generic beige box, painted columns, shallow entry, detached ornament, blue mirror glass, missing pylon batter",
        development_type="cultural_entertainment_lowrise",
        aesthetic="egyptian_revival_art_deco",
    ),
}

# These towers contain paired internal office floors behind each large Art Deco
# exterior window tier.  The planner still works in true internal floor units;
# only the fixed landmark's expressed facade rhythm uses the taller tier.
FAMILIES["art-deco-polychrome-zigzag-tower"]["visual_floor_height"] = 4.55
FAMILIES["art-deco-black-chrome-tower"]["visual_floor_height"] = 4.05


def goalpost_prompt(family: str) -> str:
    spec = FAMILIES[family]
    return f"""Use case: photorealistic-natural
Asset type: render-locked four-view architectural reconstruction board for a CityPrompt LEGO building variant
Input image: Image 1 is the sole authority for topology, proportions, facade rhythm, ornament, palette, and silhouette.
Primary request: Reconstruct the exact same {spec['label']} from Image 1 as one coherent true-metric building in four equal panels in a precise 2 by 2 grid.
Panel 1: dead-front orthographic elevation, complete building visible. Panel 2: pedestrian-height front-right architectural survey oblique. Panel 3: rear-left oblique proving all construction and materials wrap the secondary elevations. Panel 4: high aerial roof-plan oblique proving roof, setbacks, courts, and mechanical volumes.
Building lock: {spec['design_lock']}.
Scene/backdrop: clean warm-light-grey architectural studio ground and backdrop, no neighbors, trees, cars or people.
Style/medium: premium photoreal architectural survey photography and physically plausible construction reference, not concept art.
Lighting/mood: neutral bright overcast survey illumination with soft contact shadows and controlled glass reflections, consistent in every panel.
Materials/textures: {spec['material_zones']}.
Constraints: exact same coherent building topology, storey datums, structural bays, openings, entrances, material zones and roof in all four panels; real recessed openings and physical screens; thin neutral gutters; whole building in every frame; no labels, text, signs, logos or watermark.
Avoid: {spec['avoid']}; perspective distortion, blank sides, changed geometry between panels, entourage, dramatic sunset."""


def material_prompt(family: str) -> str:
    spec = FAMILIES[family]
    cells = list(spec["palette"].values())
    descriptions = [item[0] for item in cells]
    return f"""Use case: photorealistic-natural
Asset type: shadow-neutral 3 by 2 construction and occupied-depth material board for the exact {spec['label']} in Image 1; Image 2 is the original palette authority.
Primary request: Create six equal square straight-on orthographic samples in a precise 3-column by 2-row grid separated only by thin neutral-grey gutters, with no labels.
Top-left: {descriptions[0]}, authentic construction scale and fine micro-detail, no facade or opening.
Top-center: {descriptions[1]}, authentic construction scale and fine micro-detail, no complete building element.
Top-right: {descriptions[2]}, authentic construction scale and fine micro-detail, no complete ornament assembly.
Bottom-left: {descriptions[3]}, authentic construction scale and fine micro-detail, no complete frame, door or screen.
Bottom-center: {descriptions[4]} plus clean occupied room depth seen dead-on, with clear ceiling/floor separation and restrained warm occupation, no exterior frame, mullion, screen, facade or skewed perspective.
Bottom-right: {descriptions[5]}, authentic construction scale and evenly lit, no complete roof scene.
Scene/backdrop: flat evenly lit material-capture setup. Style: premium physically based photoreal architectural construction texture reference.
Lighting: diffuse neutral overcast capture; no directional sunlight, baked shadow, vignette or perspective.
Constraints: exact 3 by 2 grid; every sample fills its cell edge-to-edge; no labels, text, logos or watermark; no complete facade or repeated window grid; match Images 1 and 2.
Avoid: cartoon materials, generic substitutions, oversized motifs, blue mirror glass, dramatic lighting, building perspective, decorative border."""


def with_family(family: str) -> dict:
    config = dict(FAMILIES[family])
    config["family"] = family
    return config
