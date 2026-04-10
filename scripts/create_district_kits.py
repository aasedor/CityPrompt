#!/usr/bin/env python3
"""
Create District Kit archetypes for City Prompt.

Generates building, street, and park archetype entries for 5 district kits:
Paris, Amsterdam, Barcelona, London, New York.

Usage:
    python scripts/create_district_kits.py --dry-run    # Preview counts
    python scripts/create_district_kits.py              # Write to JSON files
"""

import json
import sys
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILDING_FILE = PROJECT_ROOT / "frontend/src/data/buildingArchetypes.json"
STREET_FILE = PROJECT_ROOT / "frontend/src/data/streetPathArchetypes.json"
PARK_FILE = PROJECT_ROOT / "frontend/src/data/openSpaceArchetypes.json"

BASE_NEGATIVE = "cartoon, illustration, sketch, low quality, blurry, text, watermark, neon, unrealistic colors"


# ═══════════════════════════════════════════════════
# HELPER: Build a complete building archetype
# ═══════════════════════════════════════════════════

def make_building(
    id: str, title: str, category: str, description: str,
    shade: str, min_floors: int, max_floors: int, area_sqm: int,
    dev_type: str, tags: list[str],
    primary_mat: str, secondary_mat: str, accent_mat: str,
    ground_floor: str, upper_floors: str, cornice: str, color_scheme: str,
    roof_form: str, roof_material: str, roof_features: str, roof_aerial: str,
    materials: list[str],
    map_overlay: str, roof_view: str, negative: str,
    variants: list[dict],
    palette: dict | None = None,
) -> dict:
    return {
        "id": id,
        "shadeId": shade,
        "title": title,
        "aestheticCategory": category,
        "description": description[:120],
        "buildingSubcategory": dev_type,
        "generationTags": tags,
        "palette": palette or {
            "skyTop": "#8fa2b8", "skyBottom": "#ecf2f8",
            "facadePrimary": shade, "facadeSecondary": "#b9b0a3",
            "accent": "#34393f", "window": "#dff0ff",
            "ground": "#d6c7b6", "street": "#55504b", "landscape": "#7a9a68",
        },
        "styleProfile": {
            "materials": materials,
            "facadeRhythm": f"{title} facade rhythm",
            "roofForm": roof_form,
            "frontageType": dev_type,
            "windowStyle": f"{title} window proportioning",
            "massing": f"{title} massing profile",
            "heightTendency": "Low-mid to mid rise" if max_floors <= 5 else "Mid to high rise",
            "streetRelationship": "Clear streetwall and pedestrian interface",
            "renderingMood": "Photoreal architectural benchmark mood",
            "articulation": "Legible depth, frame, and entry hierarchy",
            "publicRealm": "Walkable active edge with planting and seating",
        },
        "prompt": {
            "subject": f"Front-facing canonical architectural archetype of {title}",
            "details": [
                "Centered subject with restrained perspective",
                "Facade language, massing, and frontage must be clearly legible",
                "Premium photoreal architectural rendering style",
            ],
            "negative": ["No side-angle hero perspective", "No text inside image", "No fantasy distortions"],
        },
        "renderPrompt": {
            "mapOverlay": map_overlay,
            "roofView": roof_view,
            "negative": negative,
        },
        "facadeDetail": {
            "primaryMaterial": primary_mat,
            "secondaryMaterial": secondary_mat,
            "accentMaterial": accent_mat,
            "groundFloor": ground_floor,
            "upperFloors": upper_floors,
            "cornice": cornice,
            "colorScheme": color_scheme,
        },
        "roofDetail": {
            "form": roof_form,
            "material": roof_material,
            "features": roof_features,
            "aerialAppearance": roof_aerial,
        },
        "thumbnailUrl": f"/archetypes/buildings/{id}/hero.png",
        "variants": variants,
        "minFloors": min_floors,
        "maxFloors": max_floors,
        "suggestedAreaSqm": area_sqm,
        "developmentType": dev_type,
    }


def make_variants(base_id: str, variant_data: list[tuple[str, str, str]]) -> list[dict]:
    """Create 4 variants from (suffix, label, description) tuples."""
    result = []
    for i, (suffix, label, desc) in enumerate(variant_data):
        result.append({
            "id": f"{base_id}_{suffix}",
            "label": label,
            "thumbnailUrl": f"/archetypes/buildings/{base_id}/variant_{i}.png",
            "description": desc,
            "shadeId": None,
            "palette": {"primary": None},
        })
    return result


def make_street(
    id: str, title: str, category: str, description: str,
    corridor: str, surface: str, planting: str, edge: str, public_realm: str,
    tags: list[str], map_overlay: str, negative: str,
    presets: dict | None = None,
    variants: list[dict] | None = None,
) -> dict:
    return {
        "id": id,
        "title": title,
        "aestheticCategory": category,
        "description": description[:120],
        "transportModes": ["walking", "cycling"],
        "volume": "low",
        "generationTags": tags,
        "styleProfile": {
            "corridorCharacter": corridor,
            "movementHierarchy": "Pedestrian priority",
            "surfaceType": surface,
            "plantingCharacter": planting,
            "edgeConditions": edge,
            "publicRealm": public_realm,
        },
        "prompt": {
            "subject": f"Street-level view of {title}",
            "details": ["Photoreal rendering", "Warm golden hour light"],
            "negative": ["No text", "No fantasy"],
        },
        "renderPrompt": {
            "mapOverlay": map_overlay,
            "negative": negative,
        },
        "propertyPresets": presets or {"width": 15},
        "thumbnailUrl": f"/archetypes/streets/{id}/hero.png",
        "variants": variants or [
            {"id": f"{id}_v{i}", "label": f"Variant {i+1}", "color": c,
             "description": f"{title} variant {i+1}",
             "thumbnailUrl": f"/archetypes/streets/{id}/variant_{i}.png"}
            for i, c in enumerate(["#8D6E63", "#795548", "#6D4C41", "#5D4037"])
        ],
    }


def make_park(
    id: str, title: str, category: str, space_type: str, description: str,
    landscape: str, paving: str, planting: str, seating: str, water: str,
    tags: list[str], map_overlay: str, negative: str,
    variants: list[dict] | None = None,
) -> dict:
    return {
        "id": id,
        "title": title,
        "aestheticCategory": category,
        "spaceType": space_type,
        "description": description[:120],
        "generationTags": tags,
        "styleProfile": {
            "landscapeCharacter": landscape,
            "pavingType": paving,
            "plantingType": planting,
            "seatingRealm": seating,
            "waterFeatures": water,
            "opennessEnclosure": "Semi-enclosed",
        },
        "prompt": {
            "subject": f"Aerial view of {title}",
            "details": ["Photoreal rendering", "Warm light"],
            "negative": ["No text", "No fantasy"],
        },
        "renderPrompt": {
            "mapOverlay": map_overlay,
            "negative": negative,
        },
        "propertyPresets": {},
        "thumbnailUrl": f"/archetypes/openspaces/{id}/hero.png",
        "variants": variants or [
            {"id": f"{id}_v{i}", "label": f"Variant {i+1}", "color": c,
             "description": f"{title} variant {i+1}",
             "thumbnailUrl": f"/archetypes/openspaces/{id}/variant_{i}.png"}
            for i, c in enumerate(["#4CAF50", "#388E3C", "#2E7D32", "#1B5E20"])
        ],
    }


# ═══════════════════════════════════════════════════
# PARIS KIT (8 buildings + 3 streets + 3 parks)
# ═══════════════════════════════════════════════════

PARIS_BUILDINGS = [
    make_building(
        "parisian_corner_dome", "Parisian Corner with Dome", "parisian", "Haussmann corner building with 45-degree pan coupe, zinc dome or tourelle, and ground-floor cafe terrasse",
        "#C4A35A", 6, 7, 400, "mixed_use", ["parisian", "haussmann", "corner", "dome", "pan_coupe"],
        "cut Lutetian limestone, smooth ashlar, cream-beige tone", "carved stone window surrounds with scroll brackets", "zinc dome or tourelle at corner, wrought-iron balconies",
        "ground-floor cafe with canvas awning, rattan bistro chairs on terrasse, large plate-glass windows", "continuous iron balconies at 2nd and 5th floors, tall French windows, progressive floor height reduction", "heavy modillioned stone cornice, 250mm projection", "cream limestone body, zinc grey dome, dark green awning, black ironwork",
        "zinc mansard with dome or tourelle at corner", "zinc cladding on dome, slate on mansard", "ornamental zinc finial, dormer windows, oeil-de-boeuf", "zinc dome prominent at intersection, mansard roofline radiating from corner",
        ["cut Lutetian limestone ashlar", "zinc dome cladding", "wrought-iron balcony railings", "carved stone brackets"],
        "Replace the colored building block with a photorealistic Parisian Haussmann corner building. Keep the exact same building footprint and height. 45-degree chamfered corner (pan coupe) crowned with a zinc dome or tourelle. Cut limestone facades with continuous iron balconies at 2nd and 5th floors. Ground-floor corner cafe with canvas awning and rattan chairs on the terrasse. 6-7 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a zinc mansard roof with prominent dome or tourelle at the corner. Dormer windows along the mansard. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, brutalist",
        make_variants("parisian_corner_dome", [
            ("cafe_terrace", "Cafe Terrace Corner", "Corner with prominent red awning cafe terrasse, rattan chairs, zinc dome above"),
            ("turret_ornate", "Ornate Tourelle", "Elaborate stone tourelle with carved decoration, gilded finial"),
            ("pharmacy_corner", "Pharmacy Corner", "Green cross pharmacy sign, Art Nouveau shopfront, simpler zinc cap"),
            ("rounded_corner", "Rounded Corner", "Smooth curved corner instead of chamfer, continuous balconies wrapping around"),
        ]),
    ),
    make_building(
        "parisian_hotel_particulier", "Hotel Particulier", "parisian", "Grand Parisian private mansion with courtyard entrance, set back behind ornamental gate and wall",
        "#D4C5A0", 2, 3, 600, "residential_luxury", ["parisian", "mansion", "hotel_particulier", "courtyard", "marais"],
        "cut limestone, fine-dressed smooth ashlar", "carved stone pilasters, entablatures, and pediments", "wrought-iron gates with gilded finials, carved stone cartouches",
        "grand porte-cochere entrance with carved stone arch, heavy timber doors, cobblestone courtyard visible beyond", "tall French windows with stone balustrades, piano nobile with tallest proportions, carved stone window surrounds", "stone balustrade parapet with urns", "pale cream limestone, dark timber doors, gilded iron gates, slate grey roof",
        "slate mansard with tall chimneys", "natural slate shingles", "tall brick chimneys, stone dormer windows with carved surrounds", "dark slate mansard with prominent chimneys and stone dormers, interior courtyard visible",
        ["cut limestone ashlar", "natural slate roofing", "wrought-iron gates", "carved stone ornament"],
        "Replace the colored building block with a photorealistic Parisian hotel particulier (private mansion). Keep the exact same building footprint and height. Set back behind an ornamental iron gate and stone wall, with a cobblestone courtyard visible. Fine limestone facades with carved pilasters and pediments. Tall French windows with stone balustrades on the piano nobile. 2-3 storey with slate mansard roof. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a slate mansard roof with chimneys and stone dormers. Interior courtyard garden visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, industrial",
        make_variants("parisian_hotel_particulier", [
            ("marais_brick", "Marais Brick & Stone", "Red brick with white stone quoins, Place des Vosges style"),
            ("classical_grand", "Classical Grand", "Full neoclassical facade with Corinthian pilasters, pediment"),
            ("garden_mansion", "Garden Mansion", "Emphasis on rear garden, lower walls, more visible greenery"),
            ("embassy_formal", "Embassy Formal", "Flags, security booth at gate, impeccably maintained"),
        ]),
    ),
    make_building(
        "parisian_passage_couvert", "Passage Couvert", "parisian", "Glass-and-iron covered arcade cutting through a city block, lined with boutiques and mosaic floors",
        "#B8860B", 2, 3, 350, "commercial_retail", ["parisian", "passage", "arcade", "covered", "glass_iron"],
        "cast iron columns with ornamental capitals", "timber and glass shopfronts, painted and gilded vitrines", "mosaic tile or marble floor, etched glass transoms",
        "continuous boutique shopfronts on both sides, original 19th-century wooden display cases, ornate entry arches from street", "upper floors with offices or apartments above the shops, iron-railed galleries overlooking the passage", "glass-and-iron barrel-vault roof structure", "dark green and gold ironwork, warm timber shopfronts, cream stone entry arches",
        "glass-and-iron barrel vault roof", "iron framework with glass panels", "ornamental iron ridge cresting, glass panels letting in natural light", "linear glass barrel vault visible from above, running through the block",
        ["cast iron columns", "glass barrel-vault roof", "mosaic tile floors", "gilded timber shopfronts"],
        "Replace the colored building block with a photorealistic Parisian passage couvert (covered shopping arcade). Keep the exact same building footprint. Glass-and-iron barrel-vault roof over a narrow arcade lined with ornate boutique shopfronts on both sides. Mosaic tile floors, cast iron columns, gilded timber vitrines. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a linear glass-and-iron barrel vault roof running through the building block. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, brutalist, minimalist",
        make_variants("parisian_passage_couvert", [
            ("galerie_vivienne", "Galerie Vivienne Style", "Ornate neoclassical decoration, mosaic floors, painted ceiling panels"),
            ("panoramas", "Passage des Panoramas Style", "Simpler iron structure, variety of small shops, vintage character"),
            ("grand_cerf", "Grand Cerf Style", "Tall glass roof, wider passage, wrought iron galleries"),
            ("modern_restored", "Modern Restored", "Restored with contemporary boutiques, preserved iron and glass"),
        ]),
    ),
    make_building(
        "parisian_marche_couvert", "Marche Couvert", "parisian", "Iron-and-glass covered market hall with arched bays and a central clock gable",
        "#8B4513", 1, 2, 800, "commercial_market", ["parisian", "market", "marche", "iron", "glass", "hall"],
        "cast iron structural columns and trusses", "brick perimeter walls with sandstone dressings and arched openings", "decorative terracotta panels, ornamental ironwork at entrance gable",
        "arched perimeter openings with iron gates, market stalls visible within, clock and decorative gable at main entrance", "open interior with iron columns supporting glass roof, mezzanine offices at ends", "iron-and-glass roof with clerestory ventilation", "red-brown brick walls, black iron structure, glass roof panels, sandstone trim",
        "iron-and-glass roof with clerestory", "glass panels in iron framework", "clock tower at entrance gable, ventilation lanterns, decorative ridge cresting", "large glass-and-iron roof visible from above, rectangular footprint",
        ["cast iron structure", "glass roof panels", "red-brown brick walls", "sandstone dressings"],
        "Replace the colored building block with a photorealistic Parisian marche couvert (covered market hall). Keep the exact same building footprint. Large open-span interior with cast iron columns and glass roof. Brick perimeter walls with arched openings. Clock and decorative gable at entrance. Single-storey hall. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a large iron-and-glass roof structure, rectangular. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, residential",
        make_variants("parisian_marche_couvert", [
            ("baltard_style", "Baltard Style", "Elegant iron pavilion inspired by Les Halles, ornamental columns"),
            ("neighborhood", "Neighborhood Market", "Simpler brick structure, community scale, fewer decorative elements"),
            ("restored_modern", "Restored Modern", "Original structure preserved, modern stalls and lighting within"),
            ("gourmet_hall", "Gourmet Food Hall", "Upscale conversion with artisan food vendors, preserved iron structure"),
        ]),
    ),
    make_building(
        "parisian_grand_magasin", "Grand Magasin", "parisian", "Parisian department store with ornate Art Nouveau or Beaux-Arts facade and interior glass dome atrium",
        "#9B7042", 5, 7, 1200, "commercial_retail", ["parisian", "department_store", "grand_magasin", "art_nouveau", "dome"],
        "cut limestone with heavily carved ornamental facade", "large plate-glass display windows with bronze or iron frames", "Art Nouveau ironwork balconies, ornamental copper dome",
        "monumental entrance with carved stone surround, large plate-glass display windows with seasonal arrangements", "continuous windows with ornate stone and iron balconies, carved garlands and mascarons between floors", "ornamental stone and iron cornice with copper or zinc dome above", "cream limestone, bronze metalwork, copper-green dome patina",
        "ornamental copper or zinc dome over central atrium", "copper cladding with green patina", "glass skylight dome over interior atrium, decorative ironwork, flagpoles", "prominent dome visible from surrounding streets, large rectangular footprint",
        ["cut limestone", "copper dome cladding", "Art Nouveau ironwork", "large plate-glass windows"],
        "Replace the colored building block with a photorealistic Parisian grand magasin (department store). Keep the exact same building footprint and height. Ornate Beaux-Arts limestone facade with carved decoration. Large plate-glass display windows. Copper or zinc dome over central atrium. Art Nouveau ironwork balconies. 5-7 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a large rooftop with prominent copper dome over central atrium. Glass skylight visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, minimalist, industrial",
        make_variants("parisian_grand_magasin", [
            ("lafayette", "Galeries Lafayette Style", "Ornate Art Nouveau facade, stained glass dome, gilded balconies"),
            ("bon_marche", "Le Bon Marche Style", "Eiffel-designed iron and glass, more restrained exterior"),
            ("printemps", "Printemps Style", "Green copper dome, elaborate mosaic interior, Beaux-Arts facade"),
            ("samaritaine", "La Samaritaine Style", "Art Deco renovation, mixed Art Nouveau and Deco elements"),
        ]),
    ),
    make_building(
        "parisian_cafe_brasserie", "Parisian Cafe Brasserie", "parisian", "Corner cafe with canvas awning, rattan chairs, and terrasse occupying the ground floor of a Haussmann building",
        "#C4A35A", 6, 7, 350, "mixed_use", ["parisian", "cafe", "brasserie", "terrasse", "corner"],
        "cut Lutetian limestone on upper floors", "painted timber or cast-iron cafe shopfront with etched glass", "canvas awning (store banne) in dark red or green, rattan bistro furniture",
        "tall ground-floor cafe with large plate-glass windows, etched and gilded lettering, sidewalk terrasse with rattan chairs and marble-topped tables, canvas awning", "standard Haussmann apartment floors above with iron balconies at 2nd and 5th, tall French windows", "projecting stone cornice with dentil molding", "cream limestone upper floors, dark green or red awning, warm timber cafe front, gilt lettering",
        "zinc mansard with dormers", "zinc cladding", "dormer windows, chimneys", "standard zinc mansard, building reads as a Haussmann apartment with prominent ground-floor cafe",
        ["cut limestone ashlar", "zinc mansard roofing", "painted timber cafe front", "rattan bistro chairs"],
        "Replace the colored building block with a photorealistic Parisian cafe brasserie building. Keep the exact same building footprint and height. Ground floor is a classic Parisian cafe with canvas awning, rattan bistro chairs on the sidewalk terrasse, etched glass windows, and gilt lettering. Upper floors are standard Haussmann limestone with iron balconies. 6-7 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a zinc mansard roof with dormers. Canvas awning visible extending over sidewalk at ground level. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, brutalist",
        make_variants("parisian_cafe_brasserie", [
            ("classic_red", "Classic Red Awning", "Deep red canvas awning, gold lettering, Art Nouveau interior visible"),
            ("green_tabac", "Green Tabac Corner", "Dark green awning, red diamond tabac sign, zinc bar visible"),
            ("belle_epoque", "Belle Epoque Grand", "Ornate mirrors, brass rails, globe lighting visible through windows"),
            ("modern_bistro", "Modern Bistro", "Contemporary interpretation, natural wood, simpler awning"),
        ]),
    ),
    make_building(
        "parisian_ecole", "Ecole Republicaine", "parisian", "Third Republic school building with brick-and-stone polychrome facade and Republican inscriptions",
        "#8B6914", 3, 4, 500, "institutional_education", ["parisian", "school", "ecole", "republican", "brick_stone"],
        "red-brown brick in running bond with stone dressings", "carved stone lintels, string courses, and quoins", "Republic motto carved in stone above entrance, RF monogram, Marianne bust",
        "symmetrical entrance with carved stone surround, inscription ECOLE above, iron gates to courtyard", "large classroom windows for maximum light, brick pilasters between bays, stone string courses", "stone cornice with brick corbelling, Republic symbols", "red-brown brick, cream stone dressings, slate grey roof, dark green iron gates",
        "slate roof with ridge tiles", "natural slate", "clock tower or bell, ventilation lanterns, chimney stacks", "slate roof with central clock, courtyard visible within the building complex",
        ["red-brown brick", "cream limestone dressings", "carved stone Republican inscriptions", "slate roofing"],
        "Replace the colored building block with a photorealistic French Third Republic school (ecole). Keep the exact same building footprint and height. Red-brown brick facades with cream stone dressings. Symmetrical composition with carved inscriptions LIBERTE EGALITE FRATERNITE. Large classroom windows. Interior courtyard. 3-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a slate roof with clock tower. Interior courtyard (cour de recreation) visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, residential",
        make_variants("parisian_ecole", [
            ("jules_ferry", "Jules Ferry Era", "Classic 1880s school, prominent Republican inscriptions, symmetrical facade"),
            ("art_deco_school", "Art Deco School", "1930s geometric brick patterns, streamlined entrance"),
            ("lycee_grand", "Grand Lycee", "Larger institutional scale, central courtyard, clock tower"),
            ("maternelle", "Maternelle/Primary", "Smaller scale, colorful details, courtyard play area visible"),
        ]),
    ),
    make_building(
        "parisian_marais_building", "Pre-Haussmann Marais Building", "parisian", "Older Parisian rental building with plaster-rendered facade, irregular plan following medieval parcels",
        "#B8A88A", 4, 5, 250, "residential_apartment", ["parisian", "marais", "pre_haussmann", "medieval", "plaster"],
        "plaster-rendered rubble stone (enduit), sometimes exposed stone at ground floor", "simple stone window surrounds, timber shutters", "wrought-iron balconettes on one or two floors, carved stone doorway",
        "arched stone doorway to staircase, sometimes a shop with old timber front", "simple plastered facade with stone-framed windows, occasional iron balconettes, no strict hierarchy", "simple stone or plaster cornice, modest projection", "cream or ochre plaster walls, grey stone surrounds, timber shutters in dark green or grey",
        "tile or slate roof, often irregular pitch", "clay tiles or slate", "visible chimney stacks, no dormers or simple ones", "irregular roofline following medieval parcel shapes, clay tile or slate",
        ["plaster render (enduit)", "rubble stone", "wrought-iron balconettes", "timber shutters"],
        "Replace the colored building block with a photorealistic pre-Haussmann Parisian Marais building. Keep the exact same building footprint and height. Plaster-rendered facade in cream or ochre, simple stone window surrounds, iron balconettes on one floor, arched stone doorway. Irregular medieval parcel shape. 4-5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with an irregular tile or slate roof following medieval parcel outlines. Chimneys visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, Haussmann uniformity",
        make_variants("parisian_marais_building", [
            ("exposed_stone", "Exposed Stone", "Visible rubble stone wall, partially rendered, medieval character"),
            ("ochre_plaster", "Ochre Plaster", "Warm yellow-ochre plaster, sun-faded, wooden shutters"),
            ("colombage", "Half-Timber Visible", "Exposed colombage timber frame, oldest surviving type"),
            ("boutique_ground", "Boutique Ground Floor", "Artisan or vintage shop at ground level, original timber shopfront"),
        ]),
    ),
]

# ═══════════════════════════════════════════════════
# PARIS STREETS
# ═══════════════════════════════════════════════════

PARIS_STREETS = [
    make_street(
        "parisian_boulevard", "Haussmann Boulevard", "parisian_boulevard",
        "Grand Parisian boulevard with double rows of plane trees, wide sidewalks, Morris columns, and continuous Haussmann facades",
        "Grand Haussmann boulevard, straight or gently curving, lined with 6-7 storey limestone buildings creating a continuous canyon. Double row of mature plane trees on each side, wide sidewalks with cafe terrasses, Morris advertising columns, Wallace drinking fountains, kiosques a journaux.",
        "Asphalt carriageway with stone curbs, granite crosswalks",
        "Double row of mature plane trees (platanes) on each side, horse chestnuts as alternate",
        "Continuous Haussmann limestone facades, ground-floor commerce, cafe terrasses on wide sidewalks",
        "Cafe terrasses with rattan chairs, Morris columns, Wallace fountains, green cast-iron benches, blue enamel street signs",
        ["parisian", "boulevard", "haussmann", "plane_trees", "wide"],
        "Replace the colored zone with a photorealistic Parisian Haussmann boulevard. Wide road with double rows of plane trees, continuous 6-7 storey limestone facades, sidewalk cafe terrasses, Morris columns, and Wallace fountains. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 40},
    ),
    make_street(
        "parisian_rue", "Parisian Rue", "parisian_rue",
        "Intimate Parisian residential street with continuous Haussmann facades, small shops, and narrow sidewalks",
        "Narrow residential street with continuous Haussmann facades at slightly less grand scale. One-way traffic. Narrow sidewalks. Small shops at ground level (boulangerie, fromagerie, caviste) with traditional painted shopfronts.",
        "Asphalt with stone curbs, cobblestone sections at crossings",
        "Single row of trees where width allows, otherwise none",
        "Continuous Haussmann facades, smaller-scale ground-floor shops with painted fronts",
        "Traditional shop signs, blue enamel street signs with green border, cast-iron bollards (potelets)",
        ["parisian", "rue", "residential", "intimate"],
        "Replace the colored zone with a photorealistic Parisian residential rue. Narrower than a boulevard, continuous limestone facades, traditional shopfronts (boulangerie, fromagerie), narrow sidewalks. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 15},
    ),
    make_street(
        "parisian_passage", "Parisian Passage", "parisian_passage",
        "Narrow cobblestone pedestrian passage or impasse cutting through a block, vine-covered walls, gated entrance",
        "Quiet pedestrian passage cutting through a block or dead-ending in an impasse. Cobblestone paving (paves). Lower-scale buildings (3-4 floors), vine-covered walls. Almost village-like tranquility. Sometimes gated at entrance.",
        "Cobblestone (paves) or stone setts, uneven historic surface",
        "Climbing vines on walls, potted plants, occasional small tree",
        "Lower-scale pre-Haussmann buildings, sometimes workshops or artist studios",
        "Cobblestone paving, iron gate at entrance, small cafe tables, potted plants",
        ["parisian", "passage", "impasse", "cobblestone", "pedestrian"],
        "Replace the colored zone with a photorealistic Parisian passage or impasse. Narrow cobblestone pedestrian alley between 3-4 storey buildings, vine-covered walls, potted plants, iron gate at entrance. Quiet village-like character. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 4},
    ),
]

# ═══════════════════════════════════════════════════
# PARIS PARKS
# ═══════════════════════════════════════════════════

PARIS_PARKS = [
    make_park(
        "parisian_place", "Place Royale", "parisian_civic", "plaza",
        "Formal Parisian plaza with uniform facades, central monument or fountain, and paved surface",
        "Formal paved square enclosed by uniform Haussmann or classical facades. Central monument, obelisk, or fountain. Radiating streets. No grass. Cafe terrasses at edges.",
        "Stone paving in geometric pattern, granite borders",
        "Formal clipped trees at perimeter, no lawn",
        "Cast-iron benches, period lampposts with globe lanterns",
        "Central fountain or monument with sculptural program",
        ["parisian", "place", "plaza", "formal", "monument"],
        "Replace the colored zone with a photorealistic Parisian place (formal square). Stone-paved with central monument or fountain, surrounded by uniform classical facades. No grass. Cafe terrasses at edges. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "parisian_square", "Square Parisien", "parisian_garden", "park",
        "Small fenced Parisian garden square with gravel paths, green benches, iron fence, and mature trees",
        "Small fenced green space within a residential block. Wrought iron fence (grille) painted dark green or black around perimeter. Gravel paths (allees en gravier). Green-painted cast-iron benches with wooden slats. Mature plane trees and chestnuts. Flower beds. Sometimes a small fountain or bandstand.",
        "Gravel paths (the characteristic crunching Parisian sound)",
        "Mature plane trees, chestnuts, lindens, seasonal flower beds, clipped box hedges",
        "Green-painted cast-iron benches with wooden slats, children's play area",
        "Small fountain or bandstand (kiosque a musique), sometimes a pond",
        ["parisian", "square", "garden", "fenced", "gravel"],
        "Replace the colored zone with a photorealistic Parisian square garden. Iron fence with gates, gravel paths, green cast-iron benches, mature plane trees, flower beds. Intimate neighbourhood scale. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "parisian_jardin", "Jardin a la Francaise", "parisian_formal_garden", "park",
        "Formal French garden with axial symmetry, geometric parterres, bassin, and moveable green metal chairs",
        "Formal French garden with axial symmetry and geometric parterres. Clipped hedges and topiary. Gravel allees. Circular or octagonal bassin where children sail model boats. Moveable green metal chairs (the iconic Luxembourg chairs). Statues throughout. Orangerie or pavilion.",
        "Gravel allees in formal geometric pattern",
        "Clipped box hedges, formal parterres, mature trees in allees, seasonal bedding plants",
        "Moveable green metal chairs (Luxembourg style, free to move), stone benches along allees",
        "Octagonal bassin with model sailing boats, monumental fountain",
        ["parisian", "jardin", "french_garden", "formal", "luxembourg"],
        "Replace the colored zone with a photorealistic Jardin a la Francaise. Formal axial garden with geometric parterres, clipped hedges, gravel paths, circular bassin, moveable green metal chairs, statues. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# AMSTERDAM KIT (10 buildings + 3 streets + 3 parks)
# ═══════════════════════════════════════════════════

AMSTERDAM_BUILDINGS = [
    make_building(
        "amsterdam_neck_gable", "Amsterdam Neck Gable House", "amsterdam_canal", "Golden Age canal house with ornamental sandstone neck gable, hoisting beam, and forward lean",
        "#8B4513", 4, 5, 200, "residential_apartment", ["amsterdam", "canal_house", "neck_gable", "golden_age", "halsgevel"],
        "dark red-brown Dutch brick (IJsselsteen), small format", "carved sandstone scrollwork (voluten) flanking the gable neck", "carved sandstone pediment with coat of arms or date stone, hoisting beam (hijsbalk)",
        "raised entrance (stoep) with stone steps, merchant's office or shop with large windows, basement entrance below", "tall narrow multi-pane sash windows (6-over-6), white-painted wooden frames, progressive size reduction on upper floors", "ornamental sandstone neck rising to carved pediment", "dark red-brown brick, white window frames, cream sandstone gable ornament, dark green shutters",
        "steeply pitched gable behind ornamental neck facade", "clay tiles", "hoisting beam at apex with pulley, chimney", "gabled roofline with decorative neck visible, part of varied gable silhouette along canal",
        ["dark red-brown Dutch brick", "carved sandstone scrollwork", "white-painted timber sash windows", "hoisting beam hardware"],
        "Replace the colored building block with a photorealistic Amsterdam neck gable canal house (halsgevel). Keep the exact same building footprint and height. Dark red-brown brick with ornamental sandstone neck gable topped by carved pediment. Hoisting beam at apex. White-painted multi-pane sash windows. Slight forward lean. Raised entrance stoep. 4-5 floors. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a clay tile gabled roof with hoisting beam projecting from apex. Part of a varied gable silhouette row along a canal. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, Mediterranean",
        make_variants("amsterdam_neck_gable", [
            ("golden_bend", "Golden Bend Grand", "Extra-wide double house, richest sandstone ornament, Herengracht style"),
            ("merchant", "Merchant House", "Standard two-bay, moderate ornament, typical Keizersgracht"),
            ("painted_stone", "Painted Stone Gable", "Gable ornament painted in white and gold highlights"),
            ("converted_office", "Converted to Office", "Modern interior visible through original windows, brass nameplate"),
        ]),
    ),
    make_building(
        "amsterdam_step_gable", "Amsterdam Step Gable House", "amsterdam_canal", "Medieval-era canal house with distinctive stepped zigzag gable profile and sandstone step caps",
        "#7B3F00", 3, 4, 150, "residential_apartment", ["amsterdam", "canal_house", "step_gable", "medieval", "trapgevel"],
        "dark red-brown Dutch brick, oldest Amsterdam brick type", "sandstone caps (dekstenen) on each step", "small pointed finials (pinakels) at step points, carved date stone (gevelsteen)",
        "raised stoep entrance, narrow doorway, ground-floor shop or office", "small multi-pane windows, white-painted frames, getting smaller at top", "stepped zigzag profile rising symmetrically, 3-5 steps per side", "dark brick, white window frames, cream sandstone step caps",
        "steeply pitched gable behind stepped facade", "clay tiles", "hoisting beam, chimney, simple dormers", "stepped gable silhouette, the oldest Amsterdam profile",
        ["dark red-brown Dutch brick", "sandstone step caps", "pointed finials", "white timber windows"],
        "Replace the colored building block with a photorealistic Amsterdam step gable canal house (trapgevel). Keep the exact same building footprint and height. Dark brick with distinctive staircase-stepped gable profile, sandstone caps on each step, pointed finials. Hoisting beam at apex. White-painted windows. 3-4 floors. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a clay tile gabled roof behind stepped facade. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, limestone",
        make_variants("amsterdam_step_gable", [
            ("jordaan_simple", "Jordaan Simple", "Narrowest, one bay, minimal ornament, Jordaan neighbourhood"),
            ("decorated", "Decorated Steps", "Carved sandstone on each step, richer detail"),
            ("date_stone", "With Date Stone", "Prominent carved gevelsteen identifying the house"),
            ("workshop", "Workshop Ground Floor", "Wider ground-floor opening for artisan workshop use"),
        ]),
    ),
    make_building(
        "amsterdam_bell_gable", "Amsterdam Bell Gable House", "amsterdam_canal", "18th-century canal house with smooth bell-shaped S-curve gable profile",
        "#6B4423", 3, 5, 180, "residential_apartment", ["amsterdam", "canal_house", "bell_gable", "18th_century", "klokgevel"],
        "dark red-brown Dutch brick", "sandstone or stucco scroll decorations at bell curves", "carved finial or small pediment at apex, hoisting beam",
        "raised stoep, shop or office at ground floor, white-painted timber door", "tall multi-pane sash windows, white frames, symmetrical arrangement", "smooth concave-convex S-curve on each side (bell profile)", "dark brick, white frames, cream sandstone trim at gable curves",
        "pitched gable behind bell-shaped facade", "clay tiles or slate", "hoisting beam, chimney", "bell-shaped gable silhouette, softer than step or neck gables",
        ["dark Dutch brick", "sandstone scroll ornament", "white timber sash windows", "clay tile roofing"],
        "Replace the colored building block with a photorealistic Amsterdam bell gable canal house (klokgevel). Keep the exact same building footprint and height. Dark brick with smooth bell-shaped S-curve gable profile. White-painted sash windows. Hoisting beam at apex. 3-5 floors. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a clay tile gabled roof. Bell-shaped gable profile visible from above. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, limestone, Mediterranean",
        make_variants("amsterdam_bell_gable", [
            ("simple_brick", "Simple Brick", "Minimal ornament, the bell curve itself is the decoration"),
            ("festoon_ornament", "Festoon Ornament", "Carved fruit and flower festoons at the bell curves"),
            ("painted_facade", "Painted Facade", "Facade painted in light color (cream, pale blue) over brick"),
            ("double_wide", "Double Wide", "Two-bay wide with paired windows, grander proportions"),
        ]),
    ),
    make_building(
        "amsterdam_cornice_house", "Amsterdam Cornice House", "amsterdam_canal", "Grand 18th-century canal house with flat top, classical horizontal cornice, and French-influenced ornament",
        "#5C4033", 3, 5, 250, "residential_apartment", ["amsterdam", "canal_house", "cornice", "classical", "lijstgevel"],
        "dark brick, sometimes fully plastered or sandstone on grandest examples", "classical stone pilasters, entablatures, and window surrounds", "elaborate carved cornice with dentils and modillions, sometimes balustrade with urns",
        "grand entrance with classical door surround, raised stoep, large ground-floor windows", "tall sash windows with classical stone surrounds, pilasters framing bays", "flat horizontal cornice, elevated above roofline, sometimes with balustrade and urns", "dark brick or pale plaster, white window frames, cream stone ornament",
        "flat or shallow-pitched behind elevated cornice parapet", "slate or zinc", "concealed behind parapet, chimneys visible", "flat top with prominent cornice parapet, the grandest Amsterdam house type",
        ["dark Dutch brick or pale stucco", "classical stone ornament", "elaborate carved cornice", "white timber sash windows"],
        "Replace the colored building block with a photorealistic Amsterdam cornice house (lijstgevel). Keep the exact same building footprint and height. Grand canal house with flat top and elaborate classical horizontal cornice. Classical pilasters and window surrounds. White-painted sash windows. 3-5 floors. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof behind prominent classical cornice parapet. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, Gothic, medieval",
        make_variants("amsterdam_cornice_house", [
            ("golden_bend", "Golden Bend Mansion", "Widest, fully sandstone facade, Herengracht double house"),
            ("louis_xiv", "Louis XIV Style", "French classical ornament, pilasters, carved garlands"),
            ("balustrade", "With Balustrade", "Stone balustrade with urns crowning the cornice"),
            ("stuccoed", "Stuccoed Facade", "Fully plastered and painted pale cream, hiding the brick"),
        ]),
    ),
    make_building(
        "amsterdam_pakhuis", "Amsterdam Canal Warehouse", "amsterdam_canal", "Golden Age warehouse with shuttered loading doors on every floor, heavy hoisting beam, converted to lofts",
        "#5D4037", 4, 6, 350, "residential_loft", ["amsterdam", "warehouse", "pakhuis", "loading_doors", "loft"],
        "dark red-brown brick, heavy masonry construction", "wooden shuttered loading doors (laaddeuren) on every floor", "heavy hoisting beam (hijsbalk) with large pulley wheel (katrol) at gable apex",
        "large double loading doors at ground level for goods reception, stone threshold", "shuttered loading doors on every floor instead of windows, larger and more utilitarian than residential houses", "simple spout gable (tuitgevel), functional rather than decorative", "dark brick, dark timber shutters, iron hoisting hardware",
        "simple spout gable, steep pitch", "clay tiles", "heavy hoisting beam with large pulley, simple chimney", "simple triangular gable, loading doors visible as grid pattern on facade",
        ["dark red-brown Dutch brick", "timber loading door shutters", "iron hoisting mechanism", "clay tile roofing"],
        "Replace the colored building block with a photorealistic Amsterdam canal warehouse (pakhuis). Keep the exact same building footprint and height. Dark brick with shuttered loading doors on every floor. Heavy hoisting beam with pulley at gable apex. Simple spout gable. Now converted to loft apartments with some loading doors replaced by large windows. 4-6 floors. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a simple clay tile gabled roof. Hoisting beam projecting from gable. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, ornamental, limestone",
        make_variants("amsterdam_pakhuis", [
            ("original_shutters", "Original Shutters", "All loading doors with original timber shutters, pre-conversion"),
            ("loft_conversion", "Loft Conversion", "Loading doors replaced with floor-to-ceiling glass, modern interior visible"),
            ("brouwersgracht", "Brouwersgracht Row", "Row of warehouses side by side along the canal, varied gable heights"),
            ("spice_warehouse", "VOC Spice Warehouse", "Larger scale, gable stone depicting ships or spices, double-width"),
        ]),
    ),
    make_building(
        "amsterdam_hofje", "Amsterdam Hofje", "amsterdam_hofje", "Enclosed courtyard almshouse complex with tiny dwellings around a shared garden, hidden behind a street gate",
        "#8B7355", 1, 2, 100, "residential_social", ["amsterdam", "hofje", "courtyard", "almshouse", "garden"],
        "simple brick, often whitewashed or light-colored facing the courtyard", "painted or stone doorway surrounds, white window frames", "decorative portal/gate (poort) from street, carved inscription naming the charity",
        "single unassuming gate from the street with carved arch and inscription, narrow passage leading to courtyard", "tiny individual dwellings each with own front door onto courtyard, simple sash windows", "simple brick parapet or tile ridge", "light-colored courtyard facades (contrast with dark brick exterior), white window frames, dark green or red doors",
        "clay tile pitched roofs on small individual dwellings", "clay tiles, orange-red", "small chimneys, simple ridge tiles", "ring of small roofs around central courtyard garden, hidden from street",
        ["simple Dutch brick", "whitewashed courtyard facades", "clay tile roofing", "carved stone gate portal"],
        "Replace the colored building block with a photorealistic Amsterdam hofje (courtyard almshouse complex). Keep the exact same footprint. Tiny 1-2 storey dwellings arranged around an enclosed courtyard garden. Entry through a single carved stone gate from the street. Whitewashed courtyard facades, clay tile roofs. Formal garden in center with gravel paths and low hedges. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with small clay tile roofs arranged around a central courtyard garden. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, high-rise, commercial",
        make_variants("amsterdam_hofje", [
            ("karthuizer", "Karthuizerhof Style", "Larger courtyard, formal garden with central pump, 17th century"),
            ("begijnhof", "Begijnhof Style", "Medieval origin, mix of building periods, chapel in courtyard"),
            ("modern_social", "Modern Social Housing", "Contemporary interpretation with shared courtyard garden"),
            ("restored", "Beautifully Restored", "Immaculate garden, fresh whitewash, flowering window boxes"),
        ]),
    ),
    make_building(
        "amsterdam_school_housing", "Amsterdam School Housing", "amsterdam_school", "Expressionist social housing block with sculptural dark brickwork, undulating facades, and integrated street furniture",
        "#5D3A1A", 4, 5, 500, "residential_social", ["amsterdam", "amsterdam_school", "expressionist", "brick", "de_klerk"],
        "specially produced dark brown/red brick in unusual formats and bonds, hand-crafted", "sculptural brickwork projecting and receding to create 3D texture", "integrated custom-designed letterboxes, street numbers, lampposts, balcony railings, stairwell windows",
        "dramatic entrance portal with sculptural brickwork, rounded corners, parabolic arched doorway", "undulating facade with projecting and receding brickwork patterns, windows integrated into sculptural composition, custom balcony railings", "varied roofline with towers, turrets, protruding stairwells", "dark brown-red brick throughout, teak window frames, wrought iron details",
        "varied roofline with towers and vertical accents", "clay tiles on varied roof planes", "corner towers, stairwell turrets, dramatic silhouette variations", "dynamic roofline with towers and turrets punctuating the housing block",
        ["dark expressionist brick", "teak window frames", "sculptural brickwork patterns", "custom wrought iron details"],
        "Replace the colored building block with a photorealistic Amsterdam School housing block. Keep the exact same building footprint and height. Dark expressive brick with sculptural undulating facades. Rounded corners, parabolic arches, integrated custom letterboxes and lampposts. Corner towers punctuating the block. 4-5 storey social housing. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with clay tile roofs with varied roofline, corner towers, and stairwell turrets. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, limestone, classical",
        make_variants("amsterdam_school_housing", [
            ("het_schip", "Het Schip Style", "De Klerk's masterwork, dramatic tower, ship-like prow form"),
            ("de_dageraad", "De Dageraad Style", "Piet Kramer, undulating brick walls, integrated sculpture"),
            ("plan_zuid", "Plan Zuid Block", "Berlage's plan, more restrained but still expressive brick"),
            ("scheepvaarthuis", "Scheepvaarthuis Style", "First Amsterdam School building, maritime ornament, most decorated"),
        ]),
    ),
    make_building(
        "amsterdam_brown_cafe", "Amsterdam Brown Cafe", "amsterdam_canal", "Traditional Dutch brown cafe (bruine kroeg) with dark wood interior, corner location, and lace half-curtains",
        "#3E2723", 2, 3, 120, "commercial_hospitality", ["amsterdam", "brown_cafe", "bruine_kroeg", "pub", "corner"],
        "dark brick exterior, often with tiled dado (betegeling) on lower facade", "dark-stained wood interior paneling, brass fittings", "stained glass transoms, hand-painted or gilded signage, hanging sign (uithangbord)",
        "corner entrance with chamfered doorway, cafe curtains (vitrage) on lower half of windows, beer taps visible, warm interior glow", "low ceiling upper floors with residential or storage use, simple windows", "simple brick parapet or small gable", "dark brick, dark timber, stained glass, warm amber interior lighting",
        "simple pitched roof or flat", "clay tiles or slate", "small chimney, simple dormer", "low profile, reads as a small building at a corner intersection",
        ["dark brick", "dark-stained timber", "stained glass transoms", "brass beer tap fittings"],
        "Replace the colored building block with a photorealistic Amsterdam brown cafe (bruine kroeg). Keep the exact same building footprint and height. Dark brick corner building with chamfered entrance, lace half-curtains (vitrage) in windows, dark wood interior visible, stained glass transoms, hand-painted signage, warm amber glow. 2-3 floors. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a simple clay tile or slate roof. Small building at corner. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, bright colors, minimalist",
        make_variants("amsterdam_brown_cafe", [
            ("canal_side", "Canal-Side Cafe", "Terrasse along the canal, view of houseboats, canopy over outdoor seating"),
            ("jordaan_corner", "Jordaan Corner", "Intimate Jordaan neighbourhood location, painted facade"),
            ("historic_1600s", "Historic 1600s", "Oldest surviving type, very low ceiling, sand on floor"),
            ("proeflokaal", "Proeflokaal (Tasting Room)", "Genever/jenever tasting house, standing room only, traditional tiles"),
        ]),
    ),
    make_building(
        "amsterdam_jordaan_house", "Amsterdam Jordaan House", "amsterdam_jordaan", "Narrow working-class canal house with simple gable, painted facade, and artisan workshop at ground floor",
        "#A0785A", 2, 3, 100, "residential_apartment", ["amsterdam", "jordaan", "working_class", "narrow", "painted"],
        "simple brick, often painted in light colors (white, cream, grey, ochre)", "simple timber window frames, white-painted", "simple spout gable or cornice, minimal decoration",
        "narrow doorway, ground-floor artisan workshop or small shop, simple timber front", "simple painted facade, small sash windows, no decorative gable ornament", "simple brick parapet or plain triangular gable", "painted facade in light color (cream, pale blue, ochre), white window frames, dark door",
        "simple pitched gable roof", "clay tiles", "small chimney", "simple narrow gabled roof, painted facade visible from above",
        ["painted brick or plaster", "simple timber windows", "clay tile roofing"],
        "Replace the colored building block with a photorealistic Amsterdam Jordaan neighbourhood house. Keep the exact same building footprint and height. Narrow 2-3 storey house with painted facade in cream or ochre. Simple spout gable, white-painted windows, ground-floor artisan workshop or small shop. Modest and charming. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a simple clay tile gabled roof. Narrow, modest. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, grand, ornamental, limestone, classical",
        make_variants("amsterdam_jordaan_house", [
            ("cream_painted", "Cream Painted", "Classic cream-painted facade, flower boxes at windows"),
            ("blue_painted", "Pale Blue", "Distinctive pale blue paint, characteristic of some Jordaan streets"),
            ("workshop_front", "Workshop Front", "Wider ground-floor opening for a small workshop"),
            ("gentrified", "Gentrified", "Beautifully maintained, designer curtains, upscale but preserving character"),
        ]),
    ),
    make_building(
        "amsterdam_spout_gable", "Amsterdam Spout Gable House", "amsterdam_canal", "Simple pointed triangular gable canal house, the most austere and oldest surviving Amsterdam type",
        "#6D4C41", 3, 4, 130, "residential_apartment", ["amsterdam", "canal_house", "spout_gable", "medieval", "tuitgevel", "simple"],
        "dark red-brown Dutch brick, plain construction", "minimal stone decoration, simple brick corbelling", "hoisting beam at apex, date stone or gevelsteen",
        "narrow entrance, ground-floor shop or workspace", "simple multi-pane windows, white frames, minimal ornament", "plain triangular gable rising to a point, gable walls project slightly above roof slope", "dark brick, white frames, austere beauty in simplicity",
        "steeply pitched behind pointed gable", "clay tiles", "hoisting beam, small chimney", "simple pointed triangular gable, the most basic Amsterdam silhouette",
        ["dark Dutch brick", "minimal sandstone", "white timber windows", "clay tiles"],
        "Replace the colored building block with a photorealistic Amsterdam spout gable house (tuitgevel). Keep the exact same building footprint and height. Dark brick with plain pointed triangular gable, no decorative scrollwork. The simplest and most austere gable type. White-painted windows. Hoisting beam at apex. 3-4 floors. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a steep clay tile gabled roof behind simple pointed gable. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, ornamental, classical",
        make_variants("amsterdam_spout_gable", [
            ("one_bay", "Single Bay (Narrowest)", "One window wide, the narrowest possible canal house"),
            ("date_stone", "With Gevelsteen", "Carved pictorial date stone identifying the house"),
            ("brick_detail", "Decorative Brick", "Subtle decorative brickwork patterns in the gable"),
            ("corner_position", "Corner Position", "Gable facing the canal at a bridge corner"),
        ]),
    ),
]

# ═══════════════════════════════════════════════════
# AMSTERDAM STREETS
# ═══════════════════════════════════════════════════

AMSTERDAM_STREETS = [
    make_street(
        "amsterdam_gracht", "Amsterdam Gracht", "amsterdam_canal_street",
        "Amsterdam canal street with water, quay walls, elm trees, houseboats, flat brick bridges, and varied gable silhouettes",
        "Canal street with dark water flanked by tree-lined quays. Continuous wall of narrow brick canal houses with varied gable silhouettes (step, neck, bell, cornice). Houseboats moored along canal edges. Flat brick arch bridges crossing at intervals. Elm trees creating green canopy. Cobblestone quay roads. Bicycles everywhere.",
        "Cobblestone (klinkers) in herringbone pattern, stone curbs at canal edge",
        "Elm trees (iepen) along both sides of canal, creating arched canopy over water",
        "Continuous varied gable facades reflecting in still canal water, houseboats moored along quay",
        "Iron mooring posts (meerpalen), Amsterdammertjes bollards (XXX coat of arms), flat brick arch bridges with iron railings, parked bicycles along railings",
        ["amsterdam", "gracht", "canal", "houseboats", "bridges", "elm_trees"],
        "Replace the colored zone with a photorealistic Amsterdam gracht (canal street). Canal water flanked by quay walls, elm trees, houseboats, varied gable houses reflecting in water. Flat brick bridges crossing at intervals. Cobblestone roads, bicycles. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 55},
    ),
    make_street(
        "amsterdam_straat", "Amsterdam Straat", "amsterdam_street",
        "Amsterdam street without canal, brick paving, separated bike lanes, Amsterdammertjes bollards, narrow sidewalks",
        "Regular Amsterdam street without a canal. Brick-paved (klinkers) in herringbone or stretcher bond. Dedicated bicycle lanes in red-brown asphalt. Narrow sidewalks with Amsterdammertjes bollards (cast-iron posts with three Saint Andrew's crosses). Building facades directly at sidewalk with no setbacks. Stoep steps projecting.",
        "Brick paving (klinkers) in herringbone pattern, red-brown asphalt bike lanes",
        "Street trees where width allows, typically linden or plane",
        "Building facades form continuous wall at sidewalk, stoep steps projecting into sidewalk",
        "Amsterdammertjes bollards (cast-iron posts with XXX), bicycle racks, bike parking along buildings",
        ["amsterdam", "straat", "street", "brick_paving", "bike_lanes"],
        "Replace the colored zone with a photorealistic Amsterdam straat. Brick-paved street with dedicated red-brown bike lanes, narrow sidewalks, Amsterdammertjes bollards, continuous building facades with stoep steps. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 12},
    ),
    make_street(
        "amsterdam_steeg", "Amsterdam Steeg", "amsterdam_alley",
        "Extremely narrow medieval Amsterdam alley between tall buildings, brick-paved, connecting two streets",
        "Extremely narrow pedestrian passage (barely shoulder-width) connecting two parallel streets. Original small-format brick paving (klinkers), often uneven. Dark, enclosed by tall buildings on both sides. Found in the medieval city center (Oude Zijde and Nieuwe Zijde). Sometimes projecting upper floors create overhead cover.",
        "Original small-format brick (klinkers), uneven, historic",
        "None (too narrow)",
        "Tall brick buildings rising on both sides, creating canyon effect, sometimes projecting upper floors",
        "Historic brick paving, occasional wall-mounted lantern",
        ["amsterdam", "steeg", "alley", "medieval", "narrow"],
        "Replace the colored zone with a photorealistic Amsterdam steeg (narrow alley). Extremely narrow passage between tall brick buildings, original brick paving, dark and enclosed. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 2.5},
    ),
]

# ═══════════════════════════════════════════════════
# AMSTERDAM PARKS
# ═══════════════════════════════════════════════════

AMSTERDAM_PARKS = [
    make_park(
        "amsterdam_vondelpark", "Vondelpark Garden", "amsterdam_landscape", "park",
        "English landscape park with winding paths, ponds, mature tree canopy, and open lawns",
        "Naturalistic English landscape style park with winding paths, irregular ponds bridged by small footbridges, rolling lawns, and dense mature tree groups (planes, elms, beeches, chestnuts). Open grassy areas for sitting and picnicking. Bandstand pavilion. Cafe terrasses.",
        "Winding gravel and asphalt paths through naturalistic landscape",
        "Dense mature deciduous trees (plane, elm, beech, chestnut), meadow grass, wildflower areas",
        "Wooden and iron benches along paths, open lawns for informal sitting, cafe pavilion",
        "Irregular ponds and streams, small footbridges",
        ["amsterdam", "vondelpark", "landscape_park", "english_garden", "ponds"],
        "Replace the colored zone with a photorealistic Vondelpark-style English landscape park. Winding paths, irregular ponds with footbridges, mature tree canopy, open lawns, naturalistic planting. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "amsterdam_hofje_garden", "Hofje Courtyard Garden", "amsterdam_courtyard", "park",
        "Enclosed courtyard garden within a hofje complex, with gravel paths, low hedges, and central well",
        "Secluded formal or semi-formal garden completely enclosed by small brick dwellings. Low box hedges, gravel paths, flower beds. Central feature: well, pump, sundial, or small statue. Roses, lavender, herbs. Completely hidden from the street, accessed through a single gate.",
        "Gravel paths in simple geometric layout",
        "Low box hedges, rose bushes, lavender, herbs, one or two small trees",
        "Simple wooden or iron bench, maintained by residents",
        "Central pump or well, sometimes a small sundial",
        ["amsterdam", "hofje", "courtyard_garden", "enclosed", "hidden"],
        "Replace the colored zone with a photorealistic Amsterdam hofje courtyard garden. Enclosed by small brick dwellings, gravel paths, low box hedges, central pump or well, roses and lavender. Hidden from street. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "amsterdam_plein", "Amsterdam Plein", "amsterdam_civic", "plaza",
        "Irregular hard-paved Amsterdam civic square with market use, cafe terrasses, and church or weigh house focal building",
        "Irregular-shaped civic square, predominantly hard-paved with brick or stone. Church, weigh house (Waag), or historic building as focal point. Outdoor cafe terrasses. Market stalls on market days. Mature trees at edges. Bicycle parking. Multi-use: markets, events, gathering.",
        "Brick or stone paving, irregular pattern following organic square shape",
        "Mature trees at square edges, minimal planting within the paved area",
        "Cafe terrasses, market stall positions, benches facing focal building",
        "None typically, sometimes a small fountain",
        ["amsterdam", "plein", "square", "market", "civic"],
        "Replace the colored zone with a photorealistic Amsterdam plein (civic square). Irregular shape, brick-paved, church or historic building as focus, cafe terrasses, market stalls, bicycles. Mature trees at edges. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# BARCELONA KIT (6 buildings + 3 streets + 3 parks)
# ═══════════════════════════════════════════════════

BARCELONA_BUILDINGS = [
    make_building(
        "barcelona_eixample_block", "Eixample Apartment Block", "barcelona_eixample", "Standard Cerda block apartment with chamfered corner, continuous balconies, and tribuna gallery",
        "#D4A574", 5, 7, 400, "mixed_use", ["barcelona", "eixample", "cerda", "chamfered", "balconies"],
        "stone base, rendered/stuccoed upper floors in warm cream or ochre", "wrought iron balcony railings in ornamental patterns", "ceramic tile accents, hydraulic patterned tile floors visible at entrance",
        "ground-floor commercial arcade with large display windows, sometimes with mezzanine", "continuous balconies with ornate iron railings, principal floor (planta noble) with tallest ceilings and glassed-in gallery (tribuna)", "stone or stucco parapet hiding flat roof", "warm cream or ochre stucco, black wrought iron balconies, green wooden shutters",
        "flat roof hidden behind parapet", "flat membrane roof, terra cotta tiles on older examples", "laundry drying, rooftop terraces, water tanks, TV antennas", "flat roof, interior courtyard (pati) visible as open rectangle within the block",
        ["rendered stucco", "wrought iron balconies", "hydraulic tile", "ceramic accents"],
        "Replace the colored building block with a photorealistic Barcelona Eixample apartment block. Keep the exact same building footprint and height. Warm stuccoed facade with continuous wrought iron balconies. Chamfered corner at 45 degrees. Ground-floor commercial arcade. Glassed-in gallery (tribuna) on principal floor. 5-7 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof. Interior courtyard (pati) visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass tower, northern European",
        make_variants("barcelona_eixample_block", [
            ("classic_cream", "Classic Cream", "Warm cream stucco, standard iron balconies, green shutters"),
            ("ochre_ornate", "Ochre Ornate", "Rich ochre facade, more elaborate balcony ironwork, ceramic details"),
            ("corner_turret", "Corner with Turret", "Prominent turret or dome at the chamfered corner"),
            ("tribuna_prominent", "Prominent Tribuna", "Large glassed-in gallery dominating the principal floor"),
        ]),
    ),
    make_building(
        "barcelona_modernisme_casa", "Modernisme Casa", "barcelona_modernisme", "Gaudi-era Modernisme building with organic undulating facade, trencadis mosaic, and sculptural rooftop",
        "#C4956A", 5, 6, 400, "residential_luxury", ["barcelona", "modernisme", "gaudi", "organic", "trencadis"],
        "carved limestone in organic flowing forms", "trencadis ceramic mosaic in polychrome colors", "sculptural rooftop chimneys, parabolic arched windows, nature-inspired balcony ironwork",
        "undulating stone ground floor with organic column supports, large windows in flowing forms", "flowing organic facade with bone-like window frames, polychrome trencadis mosaic, iron balconies shaped like sea creatures or plants", "sculptural rooftop with mosaic-clad chimneys and ventilation towers", "cream/honey limestone, polychrome mosaic (blue, green, gold), black iron organic forms",
        "sculptural rooftop with decorated chimneys", "ceramic tiles in mosaic patterns", "chimney sculptures clad in trencadis mosaic, ventilation towers as sculptures, no straight lines", "dramatic sculptural rooftop, mosaic-clad towers and chimneys visible from above",
        ["carved limestone", "trencadis ceramic mosaic", "wrought iron organic forms", "polychrome ceramic"],
        "Replace the colored building block with a photorealistic Barcelona Modernisme building in the style of Gaudi. Keep the exact same building footprint and height. Undulating organic limestone facade with no straight lines. Polychrome trencadis ceramic mosaic. Sculptural iron balconies shaped like natural forms. Parabolic arches. Sculptural mosaic chimneys on roof. 5-6 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a sculptural rooftop with mosaic-clad chimneys and ventilation towers. Colorful trencadis visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, minimalist, brutalist, straight lines",
        make_variants("barcelona_modernisme_casa", [
            ("casa_batllo", "Casa Batllo Style", "Skeleton-like facade, dragon-scale roof tiles, bone-shaped columns"),
            ("casa_mila", "La Pedrera Style", "Undulating stone facade like ocean waves, warrior chimneys"),
            ("domenech", "Domenech i Montaner Style", "More structured Modernisme, floral ceramics, brick and iron"),
            ("puig", "Puig i Cadafalch Style", "Northern European influence, stepped gables, sgraffito"),
        ]),
    ),
    make_building(
        "barcelona_xamfra", "Barcelona Corner Chamfer", "barcelona_eixample", "Prominent corner building wrapping the 45-degree chamfer with turret or dome, the visual anchor of the Eixample grid",
        "#B8860B", 6, 8, 500, "mixed_use", ["barcelona", "eixample", "xamfra", "chamfer", "corner", "turret"],
        "stone or ornate stucco, more decorated than mid-block", "wrought iron and glass, curved balconies following the corner", "turret, dome, or sculptural crown at the chamfer apex, ground-floor cafe",
        "curved or angled ground-floor cafe or pharmacy with ornate signage, continuous display windows", "curved balconies wrapping the chamfer, most ornate decoration concentrated at corner, tribuna on principal floor", "turret, dome, or tower crowning the chamfer, the visual punctuation of the Eixample", "warm stone or cream stucco, black iron, sometimes polychrome ceramic at turret",
        "flat behind parapet, turret or dome at corner", "dome in copper or ceramic tile", "turret or dome prominently visible at corner, flagpole", "corner turret or dome prominent, flat roof on wings",
        ["carved stone or ornate stucco", "curved wrought iron balconies", "copper or ceramic dome", "glazed ceramic tile"],
        "Replace the colored building block with a photorealistic Barcelona Eixample corner building wrapping the chamfered intersection. Keep the exact same building footprint and height. Ornate facade with curved balconies following the 45-degree corner. Turret or dome crowning the chamfer. Ground-floor cafe with ornate signage. 6-8 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with flat roof and prominent turret or dome at the chamfered corner. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, minimalist, northern European",
        make_variants("barcelona_xamfra", [
            ("dome_ornate", "Ornate Dome", "Full copper dome with lantern, the grandest chamfer treatment"),
            ("turret_gothic", "Gothic Turret", "Pointed turret with medieval inspiration, ceramic cladding"),
            ("cafe_corner", "Cafe Corner", "Emphasis on the ground-floor cafe, canvas awning, outdoor tables"),
            ("modernisme_corner", "Modernisme Corner", "Art Nouveau organic decoration on the chamfer face"),
        ]),
    ),
    make_building(
        "barcelona_mercat", "Barcelona Mercat", "barcelona_market", "Cast iron and glass market hall with polychrome ceramic decoration and clerestory windows",
        "#8B4513", 1, 2, 1000, "commercial_market", ["barcelona", "mercat", "market", "iron", "glass", "ceramic"],
        "cast iron columns and steel trusses", "polychrome ceramic tile decoration on exterior and interior", "glass clerestory panels, decorative ironwork at entrances",
        "multiple street entrances through arched iron frames, ceramic-tiled exterior walls", "open interior with iron columns supporting glass and steel roof, clerestory windows, market stalls arranged in aisles", "decorative iron parapet with ceramic tile panels", "iron structure painted green or dark red, polychrome ceramic in warm colors",
        "glass and steel truss roof with clerestory", "glass panels, steel trusses", "clerestory windows, decorative iron ridge, ceramic finials", "large glass and steel roof structure, rectangular",
        ["cast iron structure", "polychrome ceramic tile", "glass clerestory", "steel trusses"],
        "Replace the colored building block with a photorealistic Barcelona mercat (market hall). Keep the exact same building footprint. Cast iron columns and steel trusses supporting glass roof. Polychrome ceramic tile decoration on exterior. Multiple arched entrances. Clerestory windows. Single-storey hall. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a large glass and steel truss roof. Polychrome ceramic visible at edges. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, residential, northern European, minimalist",
        make_variants("barcelona_mercat", [
            ("boqueria", "La Boqueria Style", "Open to La Rambla, colorful awnings, fruit and seafood stalls"),
            ("sant_antoni", "Sant Antoni Style", "Restored with modern additions, large-scale iron structure"),
            ("neighborhood", "Neighborhood Mercat", "Smaller community scale, simpler iron structure"),
            ("gourmet", "Gourmet Market", "Upscale food hall conversion, preserved iron, artisan vendors"),
        ]),
    ),
    make_building(
        "barcelona_townhouse", "Barcelona Townhouse", "barcelona_eixample", "Narrow Eixample townhouse with sgraffito decoration and French balconies",
        "#C9A882", 3, 4, 180, "residential_apartment", ["barcelona", "townhouse", "sgraffito", "narrow"],
        "rendered stucco with sgraffito decoration (scratched patterns)", "timber window frames, wooden shutters (persianes)", "wrought iron French balconies on upper floors",
        "narrow entrance with carved stone surround, small shop or workshop at ground", "sgraffito decoration on stuccoed facade, French balconies (no projection, just iron railing at window), wooden shutters", "simple stucco cornice or parapet", "warm cream stucco with grey sgraffito patterns, timber brown shutters, black iron",
        "flat or shallow pitched behind parapet", "clay tiles on pitched sections", "small chimney, simple parapet", "narrow building, flat or shallow roof behind parapet",
        ["rendered stucco", "sgraffito decoration", "timber shutters", "wrought iron French balconies"],
        "Replace the colored building block with a photorealistic Barcelona townhouse. Keep the exact same building footprint and height. Narrow stuccoed facade with sgraffito decoration, French balconies with iron railings, wooden shutters. Small shop at ground floor. 3-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat or shallow-pitched roof. Narrow building. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, northern European",
        make_variants("barcelona_townhouse", [
            ("floral_sgraffito", "Floral Sgraffito", "Elaborate floral sgraffito patterns covering the facade"),
            ("geometric", "Geometric Patterns", "Geometric sgraffito, more restrained and classical"),
            ("painted", "Painted Facade", "No sgraffito, warm painted stucco in terracotta or ochre"),
            ("shop_front", "With Shop Front", "Prominent ground-floor shop with ornate timber display windows"),
        ]),
    ),
    make_building(
        "barcelona_taller", "Barcelona Modernist Workshop", "barcelona_industrial", "Interior courtyard workshop with sawtooth roof, decorative brickwork, and arched windows",
        "#8B6914", 2, 3, 300, "commercial_workshop", ["barcelona", "taller", "workshop", "industrial", "sawtooth"],
        "exposed brick with decorative patterns", "iron window frames, large arched openings", "sawtooth roof or large skylights for natural light",
        "large arched opening for goods and materials, brick with stone voussoirs", "tall arched windows for maximum workshop light, exposed brick with decorative patterns", "sawtooth roof profile visible, brick corbelling", "warm red brick, black iron, glass skylights",
        "sawtooth roof with north-facing glass", "glass panels in iron frames on sawtooth", "sawtooth profile, skylights, ventilation", "distinctive sawtooth roof profile, located in interior of blocks",
        ["exposed decorative brick", "iron window frames", "glass sawtooth roof", "stone voussoirs"],
        "Replace the colored building block with a photorealistic Barcelona modernist workshop (taller). Keep the exact same building footprint and height. Decorative exposed brick with arched windows and sawtooth roof. Located within the interior of an Eixample block. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a sawtooth roof with north-facing glass panels. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, residential, classical, ornate",
        make_variants("barcelona_taller", [
            ("art_studio", "Art Studio Conversion", "Converted to artist studios, large windows, creative signage"),
            ("craft_workshop", "Craft Workshop", "Active workshop, materials visible, open bay doors"),
            ("restaurant", "Restaurant Conversion", "Industrial-chic restaurant, exposed brick and iron preserved"),
            ("coworking", "Coworking Space", "Modern office conversion with original sawtooth skylights preserved"),
        ]),
    ),
]

BARCELONA_STREETS = [
    make_street(
        "barcelona_carrer", "Barcelona Eixample Carrer", "barcelona_grid",
        "Straight tree-lined Eixample grid street with wide sidewalks, continuous shopfronts, and cafe terraces",
        "Straight Cerda grid street lined with plane trees. Wide sidewalks (5m each side) with cafe terraces and outdoor seating. Continuous ground-floor shopfronts. Bike lanes. Chamfered corners at every intersection creating small diamond-shaped open spaces.",
        "Asphalt with distinctive hexagonal Gaudi-designed pavement tiles on sidewalks",
        "London plane trees in regular rows along both sidewalks",
        "Continuous 5-7 storey Eixample facades, ground-floor commerce, chamfered corners at intersections",
        "Hexagonal Gaudi pavement tiles, cafe terraces, modernisme lampposts, bench seating, bike parking",
        ["barcelona", "eixample", "carrer", "grid", "plane_trees"],
        "Replace the colored zone with a photorealistic Barcelona Eixample carrer (grid street). Straight, tree-lined with plane trees, wide sidewalks with hexagonal Gaudi tiles, cafe terraces, continuous shopfronts, chamfered corners. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 20},
    ),
    make_street(
        "barcelona_passeig", "Barcelona Passeig", "barcelona_boulevard",
        "Grand Barcelona promenade with central pedestrian rambla, luxury retail, and Modernisme lampposts",
        "Grand promenade boulevard (like Passeig de Gracia). Central tree-lined pedestrian rambla with benches and Modernisme lampposts. Flanked by roadways and generous sidewalks. Luxury retail at ground floor. Some of the finest Modernisme buildings visible. Hexagonal Gaudi-designed pavement tiles.",
        "Stone and granite paving on central rambla, asphalt roadways, hexagonal Gaudi tiles on sidewalks",
        "Mature plane trees along central promenade and both sidewalks, dense canopy",
        "Grand Eixample and Modernisme facades, luxury retail, galleries, cafes",
        "Modernisme lampposts by Pere Falques, stone benches, hexagonal Gaudi pavement tiles, cafe terraces under awnings",
        ["barcelona", "passeig", "rambla", "promenade", "luxury"],
        "Replace the colored zone with a photorealistic Barcelona passeig (grand promenade boulevard). Central pedestrian rambla with Modernisme lampposts and benches, flanked by roadways. Luxury retail. Plane tree canopy. Gaudi pavement tiles. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 50},
    ),
    make_street(
        "barcelona_passatge", "Barcelona Passatge", "barcelona_passage",
        "Narrow pedestrian passage cutting through an Eixample block, sometimes with iron-and-glass canopy",
        "Narrow pedestrian passage cutting through an Eixample block, connecting two parallel streets. Sometimes covered with iron-and-glass canopy. Small independent shops and cafes. Intimate scale contrasting with the formal grid streets. Stone or tile paving.",
        "Stone or decorative tile paving",
        "Climbing plants on walls, potted plants, small trees in planters",
        "Small-scale shops and cafes, intimate facades, 2-3 storey buildings within the passage",
        "Small cafe tables, potted plants, string lights, artisan shop displays",
        ["barcelona", "passatge", "passage", "pedestrian", "intimate"],
        "Replace the colored zone with a photorealistic Barcelona passatge (narrow passage). Pedestrian passage through an Eixample block, small shops and cafes, stone paving, climbing plants. Perhaps iron-and-glass canopy overhead. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 7},
    ),
]

BARCELONA_PARKS = [
    make_park(
        "barcelona_pati_interior", "Eixample Interior Courtyard", "barcelona_courtyard", "park",
        "Green oasis hidden inside an Eixample block, with gravel paths, fountain, and Mediterranean planting",
        "Reclaimed interior courtyard within a Cerda block. Green oasis hidden from the streets. Gravel paths, central fountain, Mediterranean planting (palms, citrus, bougainvillea, oleander). Benches, children's play area. Accessed through a passage from the street.",
        "Gravel paths, stone paving around fountain",
        "Mediterranean: palms, citrus trees, bougainvillea, oleander, jasmine, cypress",
        "Stone benches, children's play area, shaded seating under palms",
        "Central fountain or small pool, sometimes a water channel",
        ["barcelona", "eixample", "courtyard", "interior", "mediterranean"],
        "Replace the colored zone with a photorealistic Barcelona Eixample interior courtyard garden. Green oasis with Mediterranean planting (palms, bougainvillea, citrus), gravel paths, central fountain, benches. Hidden inside a city block. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "barcelona_placa_xamfra", "Chamfer Plaza", "barcelona_civic", "plaza",
        "Small diamond-shaped open space where four chamfered Eixample corners meet at an intersection",
        "Small diamond-shaped open space formed where four chamfered corners meet at an intersection. Cafe terraces radiating from corner buildings. A single mature tree or small fountain at center. Hexagonal Gaudi pavement tiles. Intimate urban room created by the geometry of the chamfered blocks.",
        "Hexagonal Gaudi pavement tiles, stone paving",
        "Single mature plane tree providing shade, sometimes small planted area",
        "Cafe terraces extending from corner buildings, moveable chairs and tables",
        "Small fountain or decorative element at center, sometimes a bench",
        ["barcelona", "eixample", "chamfer", "plaza", "diamond"],
        "Replace the colored zone with a photorealistic Barcelona chamfer plaza (placa de xamfra). Diamond-shaped open space at intersection of four chamfered corners, cafe terraces, single tree, hexagonal Gaudi tiles. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "barcelona_superilla", "Barcelona Superblock", "barcelona_urban", "plaza",
        "Modern pedestrianized superblock interior with colored pavement, planters, play equipment, and pop-up market",
        "Pedestrianized interior of a superblock (superilla) cluster. Temporary and permanent street furniture: planters, benches, play equipment. Colored pavement markings and painted surfaces in bold patterns. Trees, pop-up markets, community events. Reclaimed road space for people.",
        "Colored asphalt and painted pavement in bold geometric patterns (yellow, green, blue)",
        "Trees in planters, raised planting beds, climbing plants on temporary structures",
        "Moveable benches, ping-pong tables, community bulletin boards, pop-up market stalls",
        "Sometimes spray play or rain garden features",
        ["barcelona", "superblock", "superilla", "pedestrian", "tactical_urbanism"],
        "Replace the colored zone with a photorealistic Barcelona superblock (superilla). Pedestrianized street with bold colored pavement patterns, planters, benches, play equipment, trees. Pop-up market stalls. People-friendly reclaimed road space. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# LONDON KIT (6 buildings + 3 streets + 2 parks)
# ═══════════════════════════════════════════════════

LONDON_BUILDINGS = [
    make_building(
        "london_georgian_terrace", "Georgian Terrace House", "london_georgian", "Strict symmetrical Georgian terrace with sash windows, fanlight door, area railings, and stock brick",
        "#C4A35A", 3, 4, 200, "residential_townhouse", ["london", "georgian", "terrace", "sash_windows", "fanlight"],
        "London stock brick (yellow-brown) or Bath stone", "stone lintels, sills, and string courses", "cast iron area railings at basement, wrought iron door knocker, fanlight above front door",
        "raised ground floor with steps up, basement area with iron railings below, door with fanlight transom, boot scraper", "strictly symmetrical sash windows with decreasing pane sizes on upper floors, stone flat arches or gauged brick", "brick parapet hiding roof, stone cornice", "warm yellow-brown stock brick, white-painted sash windows, black iron railings, dark painted front door",
        "shallow pitched slate, hidden behind parapet", "Welsh slate", "chimney stacks in groups, roof not visible from street", "regular chimneys in groups along party walls, roof hidden behind parapet",
        ["London stock brick", "stone sills and lintels", "Welsh slate", "cast iron railings"],
        "Replace the colored building block with a photorealistic London Georgian terrace house. Keep the exact same building footprint and height. Warm yellow-brown London stock brick, strictly symmetrical sash windows with fanlight above front door, raised ground floor with iron area railings at basement. Parapet hiding roof. 3-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a shallow slate roof hidden behind brick parapet. Chimney pots in groups. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, continental European",
        make_variants("london_georgian_terrace", [
            ("bloomsbury", "Bloomsbury Style", "Refined proportions, plainer facade, understated elegance"),
            ("bath_stone", "Bath Stone", "Full stone facade (cream Bath stone), grander proportions"),
            ("painted", "Painted Stucco", "Facade painted or stuccoed white, Pimlico/Belgravia style"),
            ("coloured_door", "Coloured Door", "Distinctive bright-painted front door (red, blue, yellow)"),
        ]),
    ),
    make_building(
        "london_regency_terrace", "Regency Stucco Terrace", "london_regency", "Grand cream stucco terrace designed as unified palace facade with Ionic columns and porticos",
        "#F5F0E1", 4, 5, 300, "residential_luxury", ["london", "regency", "stucco", "nash", "columns", "portico"],
        "brick clad in painted stucco (cream/white), designed to look like stone", "Ionic or Corinthian pilasters and columns, portico entrances", "first-floor wrought iron balconies, black iron railings",
        "portico entrance with Ionic columns, raised steps, stucco surround", "stuccoed facade with classical pilasters, tall first-floor windows with iron balconies, decreasing window sizes above", "heavy classical cornice, sometimes with balustrade above", "cream or white stucco, black iron balconies and railings, dark painted doors",
        "shallow pitched behind parapet and balustrade", "Welsh slate", "chimneys, sometimes urns on balustrade", "cream stucco terrace with uniform roofline, designed as single palatial composition",
        ["cream/white stucco", "Ionic stone columns", "wrought iron balconies", "Welsh slate"],
        "Replace the colored building block with a photorealistic London Regency stucco terrace. Keep the exact same building footprint and height. Grand cream stucco facade designed as unified palace composition. Ionic columns, portico entrances, first-floor iron balconies. 4-5 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a continuous cream stucco terrace roofline. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, red brick, modern glass, industrial",
        make_variants("london_regency_terrace", [
            ("nash_terrace", "Nash Terrace (Regent's Park)", "Grand Nash terrace, longest continuous facade, Corinthian columns"),
            ("belgravia", "Belgravia Style", "Grander individual houses, larger porticos, residential squares"),
            ("kemp_town", "Kemp Town (Brighton)", "Seaside version, bow windows, painted pastel"),
            ("crescent", "Curved Crescent", "Following a gentle curve or crescent arc"),
        ]),
    ),
    make_building(
        "london_victorian_terrace", "Victorian Bay-Window Terrace", "london_victorian", "Red or yellow brick Victorian terrace with projecting bay windows, decorative brickwork, and stained glass",
        "#B03A2E", 2, 3, 150, "residential_apartment", ["london", "victorian", "bay_window", "brick", "terrace"],
        "red or yellow stock brick, exposed (not stuccoed)", "decorative terracotta panels, carved stone lintels, polychrome brick patterns", "stained glass panels in doors and fanlights, ornate timber porches, ridge tiles",
        "small front garden behind low brick wall with iron railings, tiled path, ornate timber porch with stained glass", "projecting bay windows (canted or curved), decorative brickwork with polychrome patterns, sash windows", "steeply pitched slate or tile roof with decorative ridge tiles, prominent chimney stacks", "red brick, cream stone lintels, stained glass colors, dark painted timber porches",
        "steeply pitched with decorative ridge tiles", "Welsh slate or clay tiles", "prominent chimney pots in groups, ridge tiles with finials", "regular pitched roofs with prominent chimneys, bay window projections visible",
        ["red or yellow London brick", "decorative terracotta", "stained glass panels", "Welsh slate"],
        "Replace the colored building block with a photorealistic London Victorian terrace with bay windows. Keep the exact same building footprint and height. Red brick with projecting bay windows, decorative brickwork, stained glass panels in doors, ornate timber porch, tiled front path. Steeply pitched slate roof with chimney pots. 2-3 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with steeply pitched slate roof with prominent chimney pots. Bay window projections visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, stucco, continental",
        make_variants("london_victorian_terrace", [
            ("red_brick", "Red Brick Classic", "Standard London red brick, canted bay windows, tiled path"),
            ("yellow_stock", "Yellow Stock Brick", "Softer yellow brick, south London style"),
            ("painted_brick", "Painted Brick", "Entire facade painted white or pale colour, gentrified"),
            ("double_fronted", "Double-Fronted", "Wider house with bay windows on both sides of front door"),
        ]),
    ),
    make_building(
        "london_mews", "London Mews House", "london_mews", "Former stable/carriage house behind grand terraces, arched coach door, on a narrow cobbled lane",
        "#9E8C7A", 2, 2, 80, "residential_townhouse", ["london", "mews", "stable", "coach_house", "cobbled"],
        "brick, often painted white, cream, or pastel colours", "timber garage doors (former coach entrance), sometimes sliding or folding", "flower boxes at windows, climbing plants on facade",
        "wide arched ground-floor opening (former coach entrance), now garage or living space", "small windows above, often with window boxes and trailing plants", "simple parapet or low-pitched roof", "painted brick (white, cream, pale blue, pastel), bright painted garage doors, flower boxes",
        "low pitched or flat", "slate or felt", "no chimneys typically, simple roof", "low profile, row of small houses on narrow cobbled lane",
        ["painted brick", "timber coach doors", "slate roofing", "climbing plants"],
        "Replace the colored building block with a photorealistic London mews house. Keep the exact same building footprint and height. Small 2-storey house on a cobbled lane, painted brick, arched former coach door at ground level, window boxes above, climbing plants. Intimate scale. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with low-profile roofs on a narrow cobbled lane. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, tall buildings, modern glass, grand scale",
        make_variants("london_mews", [
            ("white_painted", "White Painted", "Classic white-painted brick, bright blue or red garage door"),
            ("pastel", "Pastel Facade", "Painted in pale pastel (powder blue, mint, blush pink)"),
            ("original", "Original Character", "Unpainted brick, more utilitarian look, coach lamp above door"),
            ("luxury", "Luxury Conversion", "High-end renovation, glass insertion above garage, designer details"),
        ]),
    ),
    make_building(
        "london_crescent", "London Crescent Terrace", "london_crescent", "Sweeping curved terrace forming a grand arc with giant-order columns and unified palatial facade",
        "#E8DCC8", 3, 4, 300, "residential_luxury", ["london", "crescent", "bath", "curved", "columns", "grand"],
        "Bath stone or cream stucco", "giant-order Ionic or Corinthian columns spanning upper floors", "rusticated ground floor, stone balustrade at roofline with urns",
        "rusticated stone ground floor, entrance through unified colonnade", "giant-order columns spanning 2-3 upper floors, unified as single composition across entire sweeping curve", "heavy cornice and stone balustrade with urns", "cream Bath stone or stucco, uniform across entire crescent",
        "concealed behind stone balustrade", "slate or lead", "chimneys, hidden behind balustrade", "sweeping arc of uniform cream facade, gardens visible in the crescent bowl",
        ["Bath stone or cream stucco", "giant-order Ionic columns", "stone balustrade", "lead or slate roofing"],
        "Replace the colored building block with a photorealistic London/Bath crescent terrace. Keep the exact same building footprint and height. Sweeping curved unified facade with giant-order Ionic columns spanning upper floors. Rusticated ground floor. Bath stone. Stone balustrade with urns at roofline. 3-4 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a sweeping curved roofline behind stone balustrade. Crescent-shaped, uniform. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, red brick, industrial",
        make_variants("london_crescent", [
            ("royal_crescent", "Royal Crescent (Bath)", "114 Ionic columns across 150m sweep, the definitive crescent"),
            ("regent_park", "Regent's Park Crescent", "Nash-designed, stuccoed, part of the Regent's Park ensemble"),
            ("edinburgh", "Edinburgh Crescent", "Scottish stone, slightly more austere, dramatic hillside setting"),
            ("brighton", "Brighton Crescent", "Seaside crescent, bow windows, balconies, sea views"),
        ]),
    ),
    make_building(
        "london_townhouse", "London Townhouse", "london_georgian", "Grand Georgian townhouse wider than terrace, with columned portico and servants' basement",
        "#C4A35A", 4, 5, 350, "residential_luxury", ["london", "townhouse", "grand", "portico", "georgian"],
        "London stock brick or Bath stone", "columned portico entrance (Doric or Ionic), stone dressings", "ornamental iron balcony on first floor, fanlight above door",
        "grand columned portico entrance with pediment, wide steps, basement servants' entrance below", "wider than standard terrace house, classical proportions, formal reception rooms on first floor", "classical cornice, sometimes with pediment above central bays", "stock brick or stone, white portico, black railings, dark painted door",
        "concealed behind parapet", "Welsh slate", "groups of chimney pots, party wall stacks", "wider building in the terrace row, portico visible below",
        ["London stock brick or Bath stone", "stone columned portico", "Welsh slate", "cast iron railings"],
        "Replace the colored building block with a photorealistic grand London townhouse. Keep the exact same building footprint and height. Wider than standard terrace, columned portico entrance with pediment, formal classical proportions, iron balcony on first floor. 4-5 storey with servants' basement. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with slate roof behind parapet, wider than neighbouring terraces. Chimney pots in groups. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, continental European",
        make_variants("london_townhouse", [
            ("mayfair", "Mayfair Grand", "Largest scale, stone facade, embassy or ambassador's residence"),
            ("stock_brick", "Stock Brick Formal", "Yellow stock brick, restrained classical, Marylebone style"),
            ("semi_detached", "Semi-Detached Villa", "Paired with mirror image, suburban grand, Hampstead style"),
            ("corner_house", "Corner House", "End of terrace, returns on side elevation, extra windows"),
        ]),
    ),
]

LONDON_STREETS = [
    make_street(
        "london_terrace_street", "London Terrace Street", "london_residential",
        "London residential street lined with continuous brick terraces, iron railings, plane trees, and chimney pot roofline",
        "Straight residential street with continuous brick terrace frontage on both sides. Iron railings along basement areas. London plane trees at intervals. Parked cars. Uniform roofline with chimney pots. Tiled front paths. Low brick front walls.",
        "Asphalt with stone kerbs, brick pavement sections",
        "London plane trees at regular intervals, the signature London street tree",
        "Continuous terrace frontage, low brick front walls with iron railings, tiled paths to front doors",
        "Black cast iron railings, traditional lampposts, red pillar box at corner, residents' parking signs",
        ["london", "terrace", "residential", "plane_trees", "railings"],
        "Replace the colored zone with a photorealistic London terrace street. Continuous brick terraces on both sides, iron railings, plane trees, chimney pot roofline, tiled front paths. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 12},
    ),
    make_street(
        "london_mews_lane", "London Mews Lane", "london_mews",
        "Narrow cobblestone mews lane accessed through an arch, intimate two-storey scale, painted doors",
        "Narrow cobblestone lane accessed through an arch from the main street. Intimate two-storey scale. Former stable doors now painted in bright colors. Window boxes with trailing flowers. Quiet enclave hidden behind grand terraces. Occasional coach lamp.",
        "Cobblestone (granite setts), original uneven surface",
        "Window boxes, climbing wisteria or roses on facades",
        "Small two-storey mews houses, painted in various colors, arched former coach doors",
        "Cobblestones, coach lamps, hanging baskets, occasional small bollard",
        ["london", "mews", "cobblestone", "intimate", "hidden"],
        "Replace the colored zone with a photorealistic London mews lane. Narrow cobblestone passage, small painted houses with arched coach doors, window boxes, climbing plants. Intimate and hidden. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 5},
    ),
    make_street(
        "london_crescent_road", "London Crescent Road", "london_crescent",
        "Sweeping curved road following the arc of a grand crescent terrace, wide pavement, garden views",
        "Sweeping curved road following the arc of a crescent terrace. Wide pavement. Iron railings separating crescent garden from road. Period lampposts. Views outward across parkland or garden from the crescent's open side.",
        "Asphalt with stone kerbs, wide stone-flagged pavement",
        "Mature trees in the crescent garden visible beyond iron railings",
        "Grand unified crescent facade on inner side, open views on outer side",
        "Period lampposts, iron railings, stone bollards, wide flagstone pavement",
        ["london", "crescent", "curved", "grand", "garden_views"],
        "Replace the colored zone with a photorealistic London crescent road. Sweeping curve following grand crescent facade, wide pavement, iron railings, garden views. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 18},
    ),
]

LONDON_PARKS = [
    make_park(
        "london_garden_square", "London Garden Square", "london_georgian", "park",
        "Rectangular fenced garden enclosed by Georgian/Victorian terraces, with plane trees, gravel paths, and locked gate",
        "Rectangular fenced garden enclosed by Georgian or Victorian terraces on all four sides. Mature London plane trees. Gravel paths. Central lawn. Wrought iron railings and locked gate (residents' key only). Benches. Rose beds. The quintessential London green space.",
        "Gravel paths, stone edging",
        "Mature London plane trees, privet hedges, rose beds, central lawn",
        "Wrought iron benches, residents-only access with key-locked gate",
        "None typically, sometimes a small memorial or statue",
        ["london", "garden_square", "fenced", "plane_trees", "residents"],
        "Replace the colored zone with a photorealistic London garden square. Rectangular fenced garden enclosed by terraces, mature plane trees, gravel paths, central lawn, iron railings with locked gate, benches. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "london_circus", "London Circus", "london_georgian", "park",
        "Circular arrangement of grand terrace houses facing inward to a round garden with large trees",
        "Circular arrangement of unified classical terrace houses facing inward toward a round garden. Large mature trees (planes, limes) in the circular garden. Iron railings. Gravel paths. Benches. A miniature classical world enclosed by continuous facade.",
        "Gravel paths in circular and radial pattern",
        "Large mature trees (London plane, lime), central lawn, rose beds",
        "Iron benches, gravel seating areas, circular path for walking",
        "Sometimes a central statue or small fountain",
        ["london", "circus", "circular", "classical", "terrace_garden"],
        "Replace the colored zone with a photorealistic London circus garden. Round garden enclosed by circular classical terrace, mature trees, gravel paths, iron railings. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# NEW YORK KIT (5 buildings + 2 streets + 2 parks)
# ═══════════════════════════════════════════════════

NEWYORK_BUILDINGS = [
    make_building(
        "newyork_cast_iron", "SoHo Cast-Iron Loft Building", "newyork_cast_iron", "Ornate prefabricated cast-iron facade mimicking Renaissance palazzo, huge windows, and fire escapes",
        "#808080", 5, 7, 400, "commercial_loft", ["newyork", "soho", "cast_iron", "loft", "fire_escape"],
        "prefabricated cast iron facade sections (painted)", "large plate-glass windows in iron frames", "zigzag fire escape on facade, hoisting mechanism at roof, ornamental iron cornice",
        "cast-iron storefront with large display windows, Corinthian columns, loading dock", "repeating bay structure with ornate cast-iron columns (Corinthian, Composite), arched or rectangular windows, enormous glass area", "pressed-metal cornice, elaborate, projecting 2-3 feet", "painted cast iron (cream, grey, or olive), enormous windows, dark fire escapes",
        "flat roof with mechanical equipment", "tar or membrane", "water towers, rooftop additions, fire escape access, mechanical equipment", "flat roof, fire escape zigzag pattern visible on facade from above",
        ["prefabricated cast iron", "large plate glass", "pressed-metal cornice", "iron fire escapes"],
        "Replace the colored building block with a photorealistic SoHo cast-iron loft building. Keep the exact same building footprint and height. Ornate cast-iron facade with Corinthian columns, huge plate-glass windows, repeating bay structure. Fire escape zigzagging down front facade. Elaborate pressed-metal cornice. 5-7 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof with water tower and mechanical equipment. Fire escapes visible on facade. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass curtain wall, European",
        make_variants("newyork_cast_iron", [
            ("haughwout", "Haughwout Style", "Venetian palazzo inspiration, most ornate, cream painted"),
            ("gunther", "Gunther Building Style", "Curved corner, French Second Empire, mansard roof"),
            ("warehouse", "Industrial Warehouse", "Simpler iron facade, wider bays, more utilitarian"),
            ("gallery", "Gallery Conversion", "Art gallery at ground floor, contemporary interior visible"),
        ]),
    ),
    make_building(
        "newyork_art_deco", "New York Art Deco Tower", "newyork_art_deco", "Stepped-setback Art Deco tower with geometric ornament, ornate lobby, and illuminated crown",
        "#B8860B", 10, 20, 600, "mixed_use", ["newyork", "art_deco", "tower", "setback", "geometric"],
        "buff or cream brick, limestone, terracotta ornament", "chrome or nickel metalwork at entrance and lobby", "geometric terracotta ornament (chevrons, zigzags, sunbursts), illuminated crown at night",
        "dramatic entrance with ornamental metalwork canopy, marble lobby with terrazzo floors, geometric plaster ceiling", "wedding cake setbacks required by 1916 Zoning Resolution, geometric terracotta panels concentrated at base and crown", "stepped crown with geometric ornament, sometimes pinnacle or flagpole", "buff brick, cream limestone, polychrome terracotta (gold, green, blue), chrome metalwork",
        "stepped setbacks culminating in decorated crown", "copper or slate on crown, membrane on terraces", "decorative crown elements, flagpole, water towers on lower setbacks", "distinctive stepped silhouette with decorated crown, setback terraces",
        ["buff brick", "limestone", "polychrome terracotta", "chrome metalwork"],
        "Replace the colored building block with a photorealistic New York Art Deco tower. Keep the exact same building footprint and height. Wedding cake stepped setbacks, geometric terracotta ornament (chevrons, zigzags, sunbursts), ornate entrance with metalwork canopy. Illuminated crown. 10-20 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with stepped setback profile with decorated crown. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass curtain wall, minimalist, European",
        make_variants("newyork_art_deco", [
            ("chrysler", "Chrysler Style", "Stainless steel eagle gargoyles, sunburst crown, highest ornament"),
            ("residential", "Residential Tower", "Emery Roth style, twin towers, buff brick, restrained Deco"),
            ("polychrome", "Polychrome Tower", "Rich terracotta in multiple colors, Mayan or Egyptian motifs"),
            ("streamlined", "Streamlined Moderne", "Later 1930s, smoother forms, horizontal banding, rounded corners"),
        ]),
    ),
    make_building(
        "newyork_prewar", "New York Pre-War Apartment", "newyork_prewar", "Classic pre-war apartment building with symmetrical brick facade, limestone trim, and doorman entrance",
        "#8B6914", 6, 12, 500, "residential_apartment", ["newyork", "prewar", "apartment", "brick", "doorman"],
        "red, brown, or buff brick, limestone base and trim", "limestone quoins, window surrounds, and cornice", "copper or bronze entrance canopy, ornate lobby with terrazzo and plaster",
        "doorman entrance with bronze and glass canopy, limestone surround, terrazzo lobby visible", "symmetrical brick facade with limestone quoins and window surrounds, regular window pattern, sometimes courtyard plan (H or U shape)", "limestone or terracotta cornice, sometimes with parapet", "red or buff brick, cream limestone trim, bronze entrance metalwork",
        "flat with parapet", "tar or membrane", "water towers, roof deck, mechanical equipment", "flat roof with water towers, courtyard visible if H or U plan",
        ["red or buff brick", "limestone trim and quoins", "bronze entrance metalwork", "terrazzo lobby floors"],
        "Replace the colored building block with a photorealistic New York pre-war apartment building. Keep the exact same building footprint and height. Symmetrical brick facade with limestone quoins and window surrounds. Doorman entrance with bronze canopy. Regular window pattern. 6-12 storey. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof with water towers. If courtyard plan, H or U shape visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass curtain wall, European",
        make_variants("newyork_prewar", [
            ("upper_west", "Upper West Side", "Red brick, limestone, classic doorman building, Broadway style"),
            ("upper_east", "Upper East Side", "Buff brick, more refined limestone, Park Avenue elegance"),
            ("courtyard", "Courtyard Building", "H-plan or U-plan with garden courtyard, more light and air"),
            ("art_deco_detail", "Art Deco Detail", "Geometric terracotta panels, Deco lobby, stylized ornament"),
        ]),
    ),
    make_building(
        "newyork_bodega", "New York Corner Bodega", "newyork_commercial", "Corner deli/bodega with angled entrance, hand-lettered signage, awning, and produce on sidewalk",
        "#2E7D32", 1, 1, 80, "commercial_retail", ["newyork", "bodega", "deli", "corner", "signage"],
        "brick building (ground floor of tenement or apartment)", "painted metal storefront surround", "illuminated signage, hand-lettered price signs, metal roll-down security gate",
        "angled corner entrance with glass door, awning extending over sidewalk, produce displayed in wooden crates on sidewalk, ATM sign, newspaper rack, neon OPEN sign", "N/A (single storey commercial space, part of larger building)", "N/A", "painted metal in green or red, hand-lettered signs in multiple colors, neon accents",
        "flat (part of larger building roof)", "N/A", "N/A", "N/A (reads as ground-floor commercial at a corner)",
        ["painted metal storefront", "hand-lettered signage", "canvas awning", "neon signs"],
        "Replace the colored building block with a photorealistic New York corner bodega/deli. Keep the exact same footprint. Angled corner entrance with awning, hand-lettered signage, produce in wooden crates on sidewalk, ATM sign, newspaper rack, illuminated at night. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof. Awning extending over sidewalk visible. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, European, luxury",
        make_variants("newyork_bodega", [
            ("classic_green", "Classic Green Awning", "Standard green awning, hand-lettered prices, full produce display"),
            ("korean_deli", "Korean Deli", "Flower display outside, salad bar visible through window"),
            ("dominican", "Dominican Bodega", "Spanish signage, tropical fruit display, lottery signs"),
            ("night_glow", "Night Scene", "Illuminated at night, neon glow, warm interior light, city atmosphere"),
        ]),
    ),
    make_building(
        "newyork_tenement", "New York Walk-Up Tenement", "newyork_tenement", "Classic 5-6 storey walk-up tenement with fire escapes, pressed-metal cornice, and ground-floor retail",
        "#A0522D", 5, 6, 200, "residential_apartment", ["newyork", "tenement", "walk_up", "fire_escape", "cornice"],
        "red or brown brick", "stone lintels and sills", "pressed-metal cornice at roofline, iron fire escapes zigzagging down facade",
        "ground-floor retail shop with painted signage, separate residential entrance with tile vestibule", "regular window pattern on narrow lot (25ft), iron fire escape as dominant facade element, brick lintels", "elaborate pressed-metal cornice, projecting brackets, sometimes with date", "red or brown brick, dark iron fire escapes, painted ground-floor shop, ornate cornice",
        "flat with parapet", "tar or membrane", "pressed-metal cornice, fire escape roof access, chimney", "flat roof with fire escape access, narrow rectangular footprint",
        ["red or brown brick", "pressed-metal cornice", "iron fire escapes", "stone lintels"],
        "Replace the colored building block with a photorealistic New York walk-up tenement. Keep the exact same building footprint and height. Red or brown brick on narrow lot, iron fire escape zigzagging down front facade, elaborate pressed-metal cornice at roofline, ground-floor retail shop. 5-6 storey walk-up. Maintain the surrounding satellite map context exactly as-is. Oblique aerial view, sunny day, sharp shadows, photorealistic, 8k",
        "Replace the colored block viewed from above with a flat roof. Narrow building, fire escape access at roof. Keep surrounding context exactly as-is.",
        f"{BASE_NEGATIVE}, modern glass, European, luxury",
        make_variants("newyork_tenement", [
            ("lower_east", "Lower East Side", "Red brick, narrow, immigrant history, ground-floor shop"),
            ("east_village", "East Village", "More ornate cornice, painted murals, bohemian character"),
            ("hell_kitchen", "Hell's Kitchen", "Brown brick, utilitarian, wider building, 1900s era"),
            ("renovated", "Renovated", "Restored brickwork, modern ground-floor cafe, maintained fire escapes"),
        ]),
    ),
]

NEWYORK_STREETS = [
    make_street(
        "newyork_soho_street", "SoHo Cobblestone Street", "newyork_soho",
        "Cobblestone SoHo street lined with cast-iron facades, fire escapes, and art gallery ground floors",
        "Wide cobblestone street (Belgian block paving) lined with cast-iron facades on both sides. Fire escapes casting shadows. Art galleries and boutiques at ground floor. Loading docks. Wide sidewalks. Yellow taxi occasionally. Quiet on weekdays, bustling on weekends.",
        "Belgian block cobblestone (granite setts), heavy and durable",
        "Street trees in iron grates, relatively sparse",
        "Cast-iron facades on both sides, fire escapes, ground-floor galleries and boutiques",
        "Cobblestone paving, cast-iron bollards, loading dock platforms, fire hydrants",
        ["newyork", "soho", "cobblestone", "cast_iron", "galleries"],
        "Replace the colored zone with a photorealistic SoHo cobblestone street. Belgian block paving, cast-iron facades on both sides, fire escapes, art galleries at ground floor, wide sidewalks. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 20},
    ),
    make_street(
        "newyork_side_street", "New York Brownstone Side Street", "newyork_residential",
        "Tree-canopied Brooklyn or Manhattan side street lined with brownstones, stoops as social spaces, iron railings",
        "Tree-lined residential side street with brownstone and brick rowhouses. Stoops (elevated stone staircases) serving as social gathering spaces. Iron railings. Street trees creating a tunnel-like canopy. Garbage cans at curb. Fire hydrants. Double-parked delivery trucks.",
        "Asphalt with concrete sidewalks, sometimes bluestone flagstone",
        "Street trees (London plane, honeylocust, linden) creating continuous canopy",
        "Continuous brownstone and brick rowhouse facades, stoops projecting into sidewalk, iron railings",
        "Iron railings, fire hydrants, street trees in iron grates, garbage cans, blue parking signs",
        ["newyork", "brownstone", "side_street", "stoops", "tree_canopy"],
        "Replace the colored zone with a photorealistic New York brownstone side street. Tree-canopied, brownstone facades with stoops, iron railings, fire hydrants. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
        {"width": 18},
    ),
]

NEWYORK_PARKS = [
    make_park(
        "newyork_pocket_park", "New York Pocket Park", "newyork_urban", "park",
        "Tiny urban oasis between buildings with waterfall wall, moveable chairs, and honey locust shade",
        "Tiny reclaimed space between buildings (under 1000 sqm). Waterfall wall at back creating white noise and masking city sounds. Moveable wire-frame chairs and small tables. Honey locust trees providing dappled shade. Ivy on side walls. Elevated a few steps from sidewalk. An urban oasis.",
        "Stone or concrete paving, elevated from sidewalk by 3-4 steps",
        "Honey locust trees (dappled shade), ivy on side walls, small planted areas",
        "Moveable wire-frame chairs and small tables, no fixed benches",
        "Waterfall wall at back of park, creating white noise",
        ["newyork", "pocket_park", "waterfall", "paley", "oasis"],
        "Replace the colored zone with a photorealistic New York pocket park (Paley Park style). Tiny urban oasis between tall buildings, waterfall wall at back, moveable wire chairs, honey locust trees, ivy on walls. Elevated from sidewalk. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
    make_park(
        "newyork_community_garden", "New York Community Garden", "newyork_urban", "park",
        "Fenced community garden on a former vacant lot with raised beds, murals, casita shed, and volunteer-run plots",
        "Fenced lot on former vacant land. Raised planting beds with vegetables and flowers. Hand-painted murals on surrounding walls. Casita (small wooden shed) for tools and gatherings. Benches made from reclaimed materials. Sunflowers, tomato plants. Gate with combination lock. Volunteer-maintained.",
        "Gravel paths between raised beds, some stepping stones",
        "Raised bed vegetables (tomatoes, squash, herbs), sunflowers, fruit trees, wildflowers",
        "Reclaimed-material benches, casita shed, picnic table, community bulletin board",
        "Rain barrel, sometimes small pond or birdbath",
        ["newyork", "community_garden", "raised_beds", "murals", "casita"],
        "Replace the colored zone with a photorealistic New York community garden. Fenced former vacant lot, raised planting beds, hand-painted murals on walls, small casita shed, sunflowers, tomato plants. Volunteer-run community space. Maintain satellite context. Oblique aerial view, photorealistic, 8k",
        BASE_NEGATIVE,
    ),
]


# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

ALL_BUILDINGS = PARIS_BUILDINGS + AMSTERDAM_BUILDINGS + BARCELONA_BUILDINGS + LONDON_BUILDINGS + NEWYORK_BUILDINGS
ALL_STREETS = PARIS_STREETS + AMSTERDAM_STREETS + BARCELONA_STREETS + LONDON_STREETS + NEWYORK_STREETS
ALL_PARKS = PARIS_PARKS + AMSTERDAM_PARKS + BARCELONA_PARKS + LONDON_PARKS + NEWYORK_PARKS


def main():
    print(f"{'DRY RUN' if DRY_RUN else 'LIVE RUN'} — create_district_kits.py")
    print(f"{'=' * 50}")
    print(f"Buildings to add: {len(ALL_BUILDINGS)}")
    print(f"Streets to add:   {len(ALL_STREETS)}")
    print(f"Parks to add:     {len(ALL_PARKS)}")
    print(f"Total:            {len(ALL_BUILDINGS) + len(ALL_STREETS) + len(ALL_PARKS)}")
    print()

    # Buildings
    with open(BUILDING_FILE, encoding="utf-8") as f:
        bdata = json.load(f)
    existing_ids = {a["id"] for a in bdata["archetypes"]}
    new_buildings = [b for b in ALL_BUILDINGS if b["id"] not in existing_ids]
    skipped = len(ALL_BUILDINGS) - len(new_buildings)
    print(f"Buildings: {len(new_buildings)} new, {skipped} skipped (already exist)")
    if DRY_RUN:
        for b in new_buildings:
            print(f"  + {b['id']} — {b['title']}")
    else:
        bdata["archetypes"].extend(new_buildings)
        with open(BUILDING_FILE, "w", encoding="utf-8") as f:
            json.dump(bdata, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Written to {BUILDING_FILE}")

    # Streets
    with open(STREET_FILE, encoding="utf-8") as f:
        sdata = json.load(f)
    street_list = sdata.get("archetypes", sdata.get("streetTypes", []))
    existing_ids = {a["id"] for a in street_list}
    new_streets = [s for s in ALL_STREETS if s["id"] not in existing_ids]
    skipped = len(ALL_STREETS) - len(new_streets)
    print(f"Streets:   {len(new_streets)} new, {skipped} skipped")
    if DRY_RUN:
        for s in new_streets:
            print(f"  + {s['id']} — {s['title']}")
    else:
        street_list.extend(new_streets)
        if "archetypes" in sdata:
            sdata["archetypes"] = street_list
        else:
            sdata["streetTypes"] = street_list
        with open(STREET_FILE, "w", encoding="utf-8") as f:
            json.dump(sdata, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Written to {STREET_FILE}")

    # Parks
    with open(PARK_FILE, encoding="utf-8") as f:
        pdata = json.load(f)
    park_list = pdata.get("archetypes", pdata.get("openSpaceTypes", []))
    existing_ids = {a["id"] for a in park_list}
    new_parks = [p for p in ALL_PARKS if p["id"] not in existing_ids]
    skipped = len(ALL_PARKS) - len(new_parks)
    print(f"Parks:     {len(new_parks)} new, {skipped} skipped")
    if DRY_RUN:
        for p in new_parks:
            print(f"  + {p['id']} — {p['title']}")
    else:
        park_list.extend(new_parks)
        if "archetypes" in pdata:
            pdata["archetypes"] = park_list
        else:
            pdata["openSpaceTypes"] = park_list
        with open(PARK_FILE, "w", encoding="utf-8") as f:
            json.dump(pdata, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Written to {PARK_FILE}")

    print(f"\n{'=' * 50}")
    print("Done!")


if __name__ == "__main__":
    main()
