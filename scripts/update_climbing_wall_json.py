"""Add climbing_wall_building archetype to buildingArchetypes.json."""

import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_JSON_PATH = _PROJECT_ROOT / "frontend" / "src" / "data" / "buildingArchetypes.json"

new_archetype = {
    "id": "climbing_wall_building",
    "shadeId": "#3D3D3D",
    "title": "Climbing Wall Building",
    "aestheticCategory": "climbing_wall",
    "description": "A building that integrates exterior climbing walls as a primary architectural feature, transforming facades into vertical recreation landscapes",
    "buildingSubcategory": "Vertical Recreation",
    "generationTags": ["climbing_wall"],
    "palette": {
        "skyTop": "#8fa2b8",
        "skyBottom": "#c4b896",
        "ground": "#8a8a7a",
        "accent": "#D4870F",
    },
    "styleProfile": {"era": "", "influences": [], "keywords": []},
    "facadeDetail": {
        "primaryMaterial": "climbing wall panels and fiberglass shell",
        "secondaryMaterial": "glass curtain wall, timber, concrete",
        "accentMaterial": "LED route lines, climbing holds",
        "groundFloor": "public plaza with boulder garden and crash pads",
        "upperFloors": "climbing surfaces with rest terraces",
        "cornice": "rooftop garden or terrace",
        "colorScheme": "varies by variant — charcoal/amber, honey timber, bronze/grey, teal gradient",
    },
    "roofDetail": {
        "form": "varies — sloped wedge, flat with pool, tower cap, undulating shell",
        "material": "green roof, concrete, fiberglass",
    },
    "variants": [
        {
            "id": "climbing_crucible",
            "label": "The Crucible",
            "thumbnailUrl": "/archetypes/buildings/climbing_wall_building/variant_0.png",
            "description": "CopenHill-inspired industrial wedge with 75-degree sloped climbing facade in dark hexagonal panels with amber LED route lines",
            "facadeDetail": {
                "primaryMaterial": "dark charcoal hexagonal fiberglass panels",
                "secondaryMaterial": "floor-to-ceiling industrial glass, Corten steel",
                "groundFloor": "landscaped park with boulders and rubber fall zone",
                "colorScheme": "charcoal panels with amber LED route lines, rust-orange Corten ends",
            },
            "roofDetail": {
                "form": "sloped wedge with rooftop running track",
                "material": "native grasses on rooftop terrace",
            },
            "shadeId": None,
            "palette": {
                "primary": "#3D3D3D",
                "accent": "#D4870F",
                "ground": "#8B4513",
            },
        },
        {
            "id": "climbing_overhang",
            "label": "The Overhang",
            "thumbnailUrl": "/archetypes/buildings/climbing_wall_building/variant_1.png",
            "description": "Recreation center with dramatic 25m timber climbing wall cantilevered 12m over the street in faceted origami CLT geometry",
            "facadeDetail": {
                "primaryMaterial": "honey-toned Douglas fir cross-laminated timber",
                "secondaryMaterial": "white concrete and glass base",
                "groundFloor": "public plaza with grey granite pavers and ornamental grasses",
                "colorScheme": "warm honey timber with earth-toned climbing holds, white concrete base",
            },
            "roofDetail": {
                "form": "flat roof with infinity pool",
                "material": "concrete with pool deck",
            },
            "shadeId": None,
            "palette": {
                "primary": "#C8A876",
                "accent": "#8B6914",
                "ground": "#E8E0D0",
            },
        },
        {
            "id": "climbing_spine",
            "label": "The Spine",
            "thumbnailUrl": "/archetypes/buildings/climbing_wall_building/variant_2.png",
            "description": "30-story mixed-use tower with full-height sculptural concrete climbing strip and terraced rest stations every 5 floors",
            "facadeDetail": {
                "primaryMaterial": "light warm grey sculpted precast concrete",
                "secondaryMaterial": "dark bronze glass curtain wall",
                "groundFloor": "double-height retail arcade with boulder garden",
                "colorScheme": "warm grey concrete spine against dark bronze glass",
            },
            "roofDetail": {
                "form": "rooftop garden with sculptural boulders",
                "material": "concrete and landscape",
            },
            "shadeId": None,
            "palette": {
                "primary": "#A0A0B0",
                "accent": "#6B6B7B",
                "ground": "#D0D0D8",
            },
        },
        {
            "id": "climbing_reef",
            "label": "The Reef",
            "thumbnailUrl": "/archetypes/buildings/climbing_wall_building/variant_3.png",
            "description": "Organic bouldering community centre shaped like a coral reef — the entire building is a continuous climbable surface in teal-to-seafoam gradient",
            "facadeDetail": {
                "primaryMaterial": "fiberglass shell with teal-to-seafoam gradient",
                "secondaryMaterial": "circular skylight domes",
                "groundFloor": "sand-colored rubber crash pad zones surrounding building",
                "colorScheme": "deep teal through aquamarine to pale seafoam gradient",
            },
            "roofDetail": {
                "form": "undulating organic shell with skylight domes",
                "material": "fiberglass with organic rock-like texture",
            },
            "shadeId": None,
            "palette": {
                "primary": "#2E8B8B",
                "accent": "#7BC8C8",
                "ground": "#D4C4A0",
            },
        },
    ],
    "minFloors": 1,
    "maxFloors": 30,
    "suggestedAreaSqm": 5000,
    "developmentType": "recreational",
}

data = json.loads(_JSON_PATH.read_text(encoding="utf-8"))
data["archetypes"].append(new_archetype)
_JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"OK — added climbing_wall_building archetype")
print(f"Total archetypes: {len(data['archetypes'])}")
