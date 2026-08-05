"""Replace one City Prompt park zone with one exact batch-2 trial identity."""
from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.core.security import create_access_token


SPECS = {
    "tennis": {
        "name": "Trial 6 - Tennis Court Cluster", "width": 84.0, "depth": 48.0,
        "color": "#315A85", "archetype": "tennis_court_cluster", "variant": "tennis_court_cluster_v0",
        "category": "sports_recreation", "paving": "acrylic", "benches": True,
        "description": "Preserve four regulation blue acrylic courts, green surrounds, precise white markings, nets, tall green fencing, bleachers and floodlights.",
    },
    "nature": {
        "name": "Trial 7 - Nature Play Area", "width": 42.0, "depth": 32.0,
        "color": "#6D4C41", "archetype": "nature_play_area", "variant": "nature_play_area_v0",
        "category": "neighborhood_public_realm", "paving": "woodchip", "benches": False,
        "description": "Preserve the shallow stone-edged water rill, balance logs, stepping stumps, log fort, willow tunnel, sand, boulders and fixed boundary trees.",
    },
    "pump": {
        "name": "Trial 8 - Pump Track", "width": 52.0, "depth": 32.0,
        "color": "#37474F", "archetype": "pump_track", "variant": "pump_track_v0",
        "category": "sports_recreation", "paving": "asphalt", "benches": True,
        "description": "Preserve the continuous dark asphalt outer rhythm loop, smooth figure-eight inner loop, low rollers, start mound and one spectator bench.",
    },
    "fitness": {
        "name": "Trial 9 - Outdoor Fitness Circuit", "width": 32.0, "depth": 27.0,
        "color": "#37474F", "archetype": "outdoor_fitness_circuit", "variant": "outdoor_fitness_circuit_v0",
        "category": "sports_recreation", "paving": "rubber", "benches": True,
        "description": "Preserve four separate rubber station pads with the main monkey-bar rig, parallel bars, sit-up bench, rings frame and one entry bench.",
    },
    "memorial": {
        "name": "Trial 10 - Memorial Garden", "width": 52.0, "depth": 42.0,
        "color": "#5D4037", "archetype": "memorial_garden", "variant": "memorial_garden_v0",
        "category": "specialty_gardens", "paving": "stone", "benches": False,
        "description": "Preserve the bilateral classical parterre, axial reflecting pool, foreground tiered fountain, terminal memorial wall, four topiary urns and formal evergreen rows.",
    },
}


def request_json(url: str, *, headers: dict[str, str], body: dict | None = None) -> object:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={**headers, **({"Content-Type": "application/json"} if data else {})},
        method="PUT" if data else "GET",
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trial", choices=sorted(SPECS))
    parser.add_argument("--api", default="http://127.0.0.1:8000/api/v1")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--zone-id", required=True)
    parser.add_argument("--user-id", required=True)
    args = parser.parse_args()
    spec = SPECS[args.trial]
    headers = {"Authorization": f"Bearer {create_access_token(args.user_id)}"}
    zones = request_json(f"{args.api}/site-zones/projects/{args.project_id}/zones", headers=headers)
    boundary = next(zone for zone in zones if zone["zone_type"] == "site_boundary")
    longitude = sum(point[0] for point in boundary["coordinates"]) / len(boundary["coordinates"])
    latitude = sum(point[1] for point in boundary["coordinates"]) / len(boundary["coordinates"])
    dx = (spec["width"] / 2) / (111_320 * math.cos(math.radians(latitude)))
    dy = (spec["depth"] / 2) / 111_320
    coordinates = [
        [longitude - dx, latitude - dy], [longitude + dx, latitude - dy],
        [longitude + dx, latitude + dy], [longitude - dx, latitude + dy],
    ]
    properties = {
        "green_space_archetype_id": spec["archetype"],
        "green_space_selected_variant_id": spec["variant"],
        "green_space_aesthetic_category": spec["category"],
        "tree_density": 0,
        "tree_density_level": "none",
        "has_paths": True,
        "has_benches": spec["benches"],
        "paving_material": spec["paving"],
        "shade_strategy": "authored_only",
        "custom_style_enabled": False,
        "description_text": (
            f"Use the exact {spec['name']} archetype render as the visual target. {spec['description']} "
            "Use the archetype-owned skin and metric GLBs. No people, generic park dressing, roads or buildings."
        ),
    }
    updated = request_json(
        f"{args.api}/site-zones/{args.zone_id}",
        headers=headers,
        body={"name": spec["name"], "coordinates": coordinates, "color": spec["color"], "properties": properties},
    )
    print(json.dumps({
        "id": updated["id"],
        "name": updated["name"],
        "archetype": updated["properties"]["green_space_archetype_id"],
        "variant": updated["properties"]["green_space_selected_variant_id"],
        "park_zone_count": 1,
    }))


if __name__ == "__main__":
    main()
