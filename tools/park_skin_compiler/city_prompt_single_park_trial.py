"""Replace one City Prompt park zone with one exact batch-2 trial identity."""
from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.request
import urllib.error
from pathlib import Path

from shapely import affinity
from shapely.geometry import Polygon, box

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from app.core.security import create_access_token
from app.services.public_realm_lego import plan_public_realm_zone_recipe
from app.services.site_engine import (
    WGS84_CRS,
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
)


SPECS = {
    "tennis": {
        "name": "Trial 6 - Tennis Court Cluster", "width": 84.0, "depth": 48.0,
        "color": "#315A85", "archetype": "tennis_court_cluster", "variant": "tennis_court_cluster_v0",
        "category": "sports_recreation", "paving": "acrylic", "benches": True,
        "description": "Preserve four regulation blue acrylic courts, green surrounds, precise white markings, nets, tall green fencing, bleachers and floodlights.",
    },
    "tennis-single": {
        "name": "Regulation Trial - Single Tennis Court", "width": 46.0, "depth": 26.0,
        "color": "#315A85", "archetype": "tennis_court_cluster", "variant": "tennis_court_cluster_v0",
        "category": "sports_recreation", "paving": "acrylic", "benches": True,
        "description": "Fit one complete regulation tennis envelope; preserve blue acrylic, green surrounds, precise white markings, net, fencing, bleacher and floodlights without shrinking the court.",
    },
    "caged-single": {
        "name": "Regulation Trial - Single 5-a-side Cage", "width": 38.0, "depth": 24.0,
        "color": "#286B38", "archetype": "soccer_pitch_caged", "variant": "soccer_pitch_caged_v0",
        "category": "sports_recreation", "paving": "artificial_turf", "benches": True,
        "description": "Fit one complete 30 by 18 metre five-a-side pitch with exact 3 by 2 metre goals, dark mesh, white rebound boards, a gate apron, bench and four floodlights.",
    },
    "caged-double": {
        "name": "Regulation Trial - Double 5-a-side Cage", "width": 75.0, "depth": 24.0,
        "color": "#286B38", "archetype": "soccer_pitch_caged", "variant": "soccer_pitch_caged_v0",
        "category": "sports_recreation", "paving": "artificial_turf", "benches": True,
        "description": "Use the oversized site for two separate complete 30 by 18 metre five-a-side pitches, never one stretched pitch. Preserve exact goals, dark mesh, white rebound boards, gates, benches and floodlights.",
    },
    "soccer-single": {
        "name": "Regulation Trial - Single Full-size Soccer Field", "width": 102.0, "depth": 66.0,
        "color": "#5F8C54", "archetype": "athletics_precinct_sports_fields", "variant": "athletics_precinct_sports_fields_variant_0",
        "category": "sports_recreation", "paving": "sports_turf", "benches": True,
        "description": "Fit one complete 100 by 64 metre regulation community soccer field with archetype-matched striped turf, exact linework, goals, restrained bleachers and floodlights. The clubhouse is rendered separately.",
    },
    "soccer-double": {
        "name": "Regulation Trial - Double Full-size Soccer Fields", "width": 212.0, "depth": 66.0,
        "color": "#5F8C54", "archetype": "athletics_precinct_sports_fields", "variant": "athletics_precinct_sports_fields_variant_0",
        "category": "sports_recreation", "paving": "sports_turf", "benches": True,
        "description": "Use the oversized site for two separate complete 100 by 64 metre regulation community soccer fields, never one stretched field. Preserve archetype-matched turf, exact linework, goals, restrained bleachers and floodlights; no clubhouse or other large building.",
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
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"City Prompt API {error.code}: {detail}") from error


def fit_trial_rectangle(
    boundary_coordinates: list[list[float]],
    width_m: float,
    depth_m: float,
) -> list[list[float]]:
    """Place one unscaled trial rectangle inside the actual site polygon."""
    boundary_wgs84 = Polygon(boundary_coordinates)
    local_crs = local_metric_crs_for_polygon(boundary_wgs84)
    to_metric = build_transformer(WGS84_CRS, local_crs)
    to_wgs84 = build_transformer(local_crs, WGS84_CRS)
    receiving = project_geometry(boundary_wgs84, to_metric).buffer(-0.25)
    min_x, min_y, max_x, max_y = receiving.bounds
    angles: set[float] = {0.0, 90.0}
    exterior = list(receiving.exterior.coords)
    for start, end in zip(exterior, exterior[1:]):
        if math.dist(start, end) < 2.0:
            continue
        angle = math.degrees(math.atan2(end[1] - start[1], end[0] - start[0])) % 180.0
        angles.add(round(angle, 6))
        angles.add(round((angle + 90.0) % 180.0, 6))
    centroid = receiving.centroid
    x_values = [centroid.x] + [min_x + (max_x - min_x) * index / 16 for index in range(17)]
    y_values = [centroid.y] + [min_y + (max_y - min_y) * index / 16 for index in range(17)]
    base = box(-width_m / 2, -depth_m / 2, width_m / 2, depth_m / 2)
    for angle in sorted(angles):
        rotated = affinity.rotate(base, angle, origin=(0, 0), use_radians=False)
        for center_x in x_values:
            for center_y in y_values:
                candidate = affinity.translate(rotated, xoff=center_x, yoff=center_y)
                if receiving.covers(candidate):
                    projected = project_geometry(candidate, to_wgs84)
                    return [[float(x), float(y)] for x, y in list(projected.exterior.coords)[:-1]]
    raise SystemExit(
        f"the active site cannot contain a complete {width_m:g} x {depth_m:g} m {width_m / depth_m:.2f}:1 trial rectangle"
    )


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
    boundary = next((zone for zone in zones if zone["zone_type"] == "site_boundary"), None)
    if boundary is None:
        boundary = next(zone for zone in zones if zone["id"] == args.zone_id)
    coordinates = fit_trial_rectangle(boundary["coordinates"], spec["width"], spec["depth"])
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
    recipe = plan_public_realm_zone_recipe(
        "green_space",
        Polygon(coordinates),
        properties,
        strict=True,
    )
    if recipe is None:
        raise SystemExit(f"no executable Public Realm LEGO family for {spec['archetype']}")
    properties["public_realm_lego"] = recipe.model_dump(mode="json")
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
