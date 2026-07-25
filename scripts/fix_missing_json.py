"""Add the 7 missing batch-1 archetypes to buildingArchetypes.json"""
import json

path = "frontend/src/data/buildingArchetypes.json"
data = json.loads(open(path, encoding="utf-8").read())

new_archetypes = [
    {
        "id": "concert_hall_modern",
        "title": "Concert Hall (Modern)",
        "developmentType": "recreational",
        "buildingSubcategory": "Concert Hall / Music Venue",
        "description": "A sculptural modern concert hall with dramatic forms driven by acoustic engineering, serving as a civic cultural landmark",
        "variants": [
            {"id": "concert_sculptural_organic", "label": "Sculptural Organic", "description": "Flowing white aluminum shell forms undulating like snow dunes with glass curtain wall and ash timber interior", "palette": {"primary": "#E8E8F0", "accent": "#C0C0D0"}},
            {"id": "concert_crystalline_glass", "label": "Crystalline Glass", "description": "Undulating glass crown atop historic brick base with curved panels and chrome frit", "palette": {"primary": "#A8C8E0", "accent": "#6090B8"}},
            {"id": "concert_timber_acoustic", "label": "Timber Acoustic", "description": "Two opposing curved planes in weathered bronze-tone metal with landscaped rooftop terrace", "palette": {"primary": "#B89878", "accent": "#8B7355"}},
            {"id": "concert_civic_landmark", "label": "Civic Landmark", "description": "Billowing stainless steel sail forms catching golden light with Douglas fir interior", "palette": {"primary": "#C8C8D0", "accent": "#A0A0B0"}},
        ],
    },
    {
        "id": "vertiport_evtol",
        "title": "Vertiport / eVTOL Facility",
        "developmentType": "institutional",
        "buildingSubcategory": "Transit / Aviation",
        "description": "Purpose-built infrastructure for electric vertical takeoff and landing aircraft",
        "variants": [
            {"id": "vertiport_rooftop", "label": "Rooftop Vertiport", "description": "Sleek landing pad atop a glass tower with ETFE canopy and passenger lounge", "palette": {"primary": "#D0E0F0", "accent": "#80B0D8"}},
            {"id": "vertiport_ground_terminal", "label": "Ground-Level Terminal", "description": "Crescent-shaped terminal with overhanging aluminum canopy and metro integration", "palette": {"primary": "#E0E8F0", "accent": "#90B8D0"}},
            {"id": "vertiport_futuristic_canopy", "label": "Futuristic Canopy", "description": "Tree-like steel columns with ETFE cushion canopy, solar cells, living green walls", "palette": {"primary": "#C8E0C8", "accent": "#78B878"}},
            {"id": "vertiport_transit_hub", "label": "Integrated Transit Hub", "description": "Multi-modal hub with Corten steel roof, rail station and bus terminal below", "palette": {"primary": "#D8C0A0", "accent": "#B89868"}},
        ],
    },
    {
        "id": "shophouse_southeast_asian",
        "title": "Shophouse (Southeast Asian)",
        "developmentType": "commercial_retail",
        "buildingSubcategory": "Shophouse / Mixed-Use",
        "description": "Traditional narrow-and-deep mixed-use terraced buildings with five-foot-way covered arcades",
        "variants": [
            {"id": "shophouse_peranakan", "label": "Traditional Peranakan", "description": "Vibrant pastel facades with elaborate plasterwork, Peranakan ceramic tiles, carved doors", "palette": {"primary": "#40B0B0", "accent": "#E87070"}},
            {"id": "shophouse_chinese", "label": "Chinese Shophouse", "description": "Restrained cream and ochre facades with timber windows and Chinese fretwork", "palette": {"primary": "#C8B080", "accent": "#987848"}},
            {"id": "shophouse_adaptive_reuse", "label": "Modern Adaptive Reuse", "description": "Heritage facades preserved with contemporary steel and glass rear additions", "palette": {"primary": "#B8A090", "accent": "#786858"}},
            {"id": "shophouse_contemporary", "label": "Contemporary Interpretation", "description": "Modern with terracotta louvers, perforated brass screens, glazed terracotta cladding", "palette": {"primary": "#304878", "accent": "#688848"}},
        ],
    },
    {
        "id": "food_hall_market_hall",
        "title": "Food Hall / Market Hall",
        "developmentType": "commercial_retail",
        "buildingSubcategory": "Food Hall / Market",
        "description": "Multi-vendor culinary destination with diverse food stalls and communal dining",
        "variants": [
            {"id": "market_historic_iron_glass", "label": "Historic Iron & Glass", "description": "Restored 19th-century market with wrought-iron framework and barrel-vaulted glass roof", "palette": {"primary": "#2D5D3D", "accent": "#B89060"}},
            {"id": "market_contemporary", "label": "Contemporary Purpose-Built", "description": "Monumental limestone arch with cable-net glass facades and digital ceiling artwork", "palette": {"primary": "#A0A0A8", "accent": "#D0D0D8"}},
            {"id": "market_industrial_reuse", "label": "Industrial Adaptive Reuse", "description": "Former rail warehouse with sawtooth roof, shipping container stalls, festoon lights", "palette": {"primary": "#4A4A50", "accent": "#C89050"}},
            {"id": "market_open_air_pavilion", "label": "Open-Air Pavilion", "description": "Undulating timber canopy with living green roof, open sides, radial vendor stalls", "palette": {"primary": "#5D8D50", "accent": "#A0C890"}},
        ],
    },
    {
        "id": "ev_charging_hub",
        "title": "EV Charging Hub / Mobility Station",
        "developmentType": "industrial",
        "buildingSubcategory": "EV Infrastructure",
        "description": "Purpose-built EV charging facility with solar canopies and community amenities",
        "variants": [
            {"id": "ev_solar_canopy", "label": "Solar Canopy Station", "description": "Sweeping bifacial solar panel canopy on angled white columns with LED guidance", "palette": {"primary": "#2848A0", "accent": "#E0E8F0"}},
            {"id": "ev_green_mobility_hub", "label": "Green Mobility Hub", "description": "Butterfly zinc roof with cafe, e-bike docking, and living green wall", "palette": {"primary": "#608868", "accent": "#A0B8A0"}},
            {"id": "ev_highway_reststop", "label": "Highway Rest-Stop Reimagined", "description": "CLT timber tree-structures with ETFE canopies, native wildflowers, lounge pavilion", "palette": {"primary": "#A08850", "accent": "#C8B078"}},
            {"id": "ev_urban_garden", "label": "Urban Charging Garden", "description": "Former gas station as green oasis with raised planters and canvas shade sails", "palette": {"primary": "#78A068", "accent": "#B8C8A8"}},
        ],
    },
    {
        "id": "hyperscale_data_center",
        "title": "Hyperscale Data Center",
        "developmentType": "industrial",
        "buildingSubcategory": "Data Center",
        "description": "Massive computing facility with advanced cooling, designed with architectural ambition",
        "variants": [
            {"id": "datacenter_campus", "label": "Campus-Style", "description": "Four buildings around prairie courtyard with grey precast and sedum green roofs", "palette": {"primary": "#787880", "accent": "#A8A8B0"}},
            {"id": "datacenter_urban_stealth", "label": "Urban-Integrated Stealth", "description": "Eight-story urban building with terracotta fins evoking microchip patterns", "palette": {"primary": "#484850", "accent": "#987850"}},
            {"id": "datacenter_nordic", "label": "Nordic Sustainable", "description": "Former paper mill on fjord shore with CLT additions and seawater cooling", "palette": {"primary": "#506878", "accent": "#A08860"}},
            {"id": "datacenter_futuristic_modular", "label": "Futuristic Modular", "description": "Circular ring of stacked prefab pods with reflective pool courtyard", "palette": {"primary": "#606068", "accent": "#909098"}},
        ],
    },
    {
        "id": "vertical_farm",
        "title": "Vertical Farm / Indoor Agriculture",
        "developmentType": "industrial",
        "buildingSubcategory": "Indoor Agriculture",
        "description": "Multi-story controlled-environment agriculture using hydroponics and LED grow lights",
        "variants": [
            {"id": "farm_glass_greenhouse_tower", "label": "Glass Greenhouse Tower", "description": "30-story glazed tower with each floor a lush hydroponic layer and robotic arms", "palette": {"primary": "#48A848", "accent": "#E8F0E0"}},
            {"id": "farm_led_indoor", "label": "LED-Lit Indoor Farm", "description": "Opaque charcoal exterior with pink-purple LED glow from narrow windows", "palette": {"primary": "#9830B0", "accent": "#383040"}},
            {"id": "farm_timber_farmscraper", "label": "Timber Farmscraper", "description": "50-story CLT tower with rotating glass louvers and greenhouse floors", "palette": {"primary": "#90B860", "accent": "#C8A868"}},
            {"id": "farm_rooftop_greenhouse", "label": "Rooftop Greenhouse Complex", "description": "Three peaked glass greenhouses atop a red brick warehouse", "palette": {"primary": "#68A050", "accent": "#C04830"}},
        ],
    },
]

existing_ids = {a["id"] for a in data["archetypes"]}
added = 0
for arch in new_archetypes:
    if arch["id"] not in existing_ids:
        data["archetypes"].append(arch)
        added += 1
        print(f"  Added: {arch['id']}")
    else:
        print(f"  Already exists: {arch['id']}")

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nTotal archetypes now: {len(data['archetypes'])} (added {added})")
