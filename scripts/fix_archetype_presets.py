"""Add minFloors, maxFloors, suggestedAreaSqm to new archetypes."""
import json

path = "frontend/src/data/buildingArchetypes.json"
data = json.loads(open(path, encoding="utf-8").read())

presets = {
    "concert_hall_modern": {"minFloors": 2, "maxFloors": 8, "suggestedAreaSqm": 15000},
    "vertiport_evtol": {"minFloors": 1, "maxFloors": 3, "suggestedAreaSqm": 5000},
    "shophouse_southeast_asian": {"minFloors": 2, "maxFloors": 4, "suggestedAreaSqm": 400},
    "food_hall_market_hall": {"minFloors": 1, "maxFloors": 3, "suggestedAreaSqm": 5000},
    "ev_charging_hub": {"minFloors": 1, "maxFloors": 2, "suggestedAreaSqm": 3000},
    "hyperscale_data_center": {"minFloors": 1, "maxFloors": 4, "suggestedAreaSqm": 50000},
    "vertical_farm": {"minFloors": 5, "maxFloors": 50, "suggestedAreaSqm": 5000},
    "waste_to_energy_plant": {"minFloors": 3, "maxFloors": 12, "suggestedAreaSqm": 40000},
    "senior_living_complex": {"minFloors": 2, "maxFloors": 12, "suggestedAreaSqm": 10000},
    "brewery_distillery": {"minFloors": 1, "maxFloors": 4, "suggestedAreaSqm": 5000},
    "solar_farm_agrivoltaics": {"minFloors": 1, "maxFloors": 1, "suggestedAreaSqm": 100000},
    "immersive_experience_venue": {"minFloors": 1, "maxFloors": 5, "suggestedAreaSqm": 8000},
    "modern_fire_station": {"minFloors": 1, "maxFloors": 3, "suggestedAreaSqm": 2500},
    "climbing_wall_building": {"minFloors": 1, "maxFloors": 6, "suggestedAreaSqm": 5000},
}

updated = 0
for a in data["archetypes"]:
    if a["id"] in presets:
        p = presets[a["id"]]
        a["minFloors"] = p["minFloors"]
        a["maxFloors"] = p["maxFloors"]
        a["suggestedAreaSqm"] = p["suggestedAreaSqm"]
        updated += 1
        print(f"  Updated: {a['id']} (floors {p['minFloors']}-{p['maxFloors']}, area ~{p['suggestedAreaSqm']} sqm)")

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nUpdated {updated} archetypes with floor/area presets")
