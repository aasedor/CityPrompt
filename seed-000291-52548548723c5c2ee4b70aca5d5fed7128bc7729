# SiteForge Building Archetype Image Card Gap Analysis

Generated: 2026-03-30

---

## 1. Overview

The codebase defines **164 archetype IDs** in `buildingArchetypes.json`. Image card directories live under `frontend/public/archetypes/buildings/`. Many archetypes have **two** directory variants (underscore and hyphenated naming), representing old and new generation image cards.

**Total JSON archetype IDs:** 164
**IDs with matching underscore directories:** 96 (the "core" set with old-format cards)
**IDs missing directories entirely:** 68 (all city-kit archetypes -- see Section 3)

The 68 missing IDs are exclusively the **city-kit archetypes** (Parisian, Amsterdam, Barcelona, London, New York, Montreal, Vancouver, Toronto, Calgary, Halifax). These have hyphenated-name directories with image cards, but the directory names do not exactly match the JSON IDs (e.g., JSON uses `parisian_corner_dome` but the directory is `parisian-corner-with-dome`).

---

## 2. City-Kit Directory/ID Mismatches

These archetypes have image card directories (hyphenated names) but the directory name does not match the JSON ID. They need either directory renaming or ID mapping.

### Parisian Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `parisian_corner_dome` | `parisian-corner-with-dome` | NAME MISMATCH |
| `parisian_hotel_particulier` | `hotel-particulier` | NAME MISMATCH |
| `parisian_passage_couvert` | `passage-couvert` | NAME MISMATCH |
| `parisian_marche_couvert` | `marche-couvert` | NAME MISMATCH |
| `parisian_grand_magasin` | `grand-magasin` | NAME MISMATCH |
| `parisian_cafe_brasserie` | `parisian-cafe-brasserie` | NAME MISMATCH |
| `parisian_ecole` | `ecole-republicaine` | NAME MISMATCH |
| `parisian_marais_building` | `pre-haussmann-marais-building` | NAME MISMATCH |

### Amsterdam Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `amsterdam_neck_gable` | `amsterdam-neck-gable-house` | NAME MISMATCH |
| `amsterdam_step_gable` | `amsterdam-step-gable-house` | NAME MISMATCH |
| `amsterdam_bell_gable` | `amsterdam-bell-gable-house` | NAME MISMATCH |
| `amsterdam_cornice_house` | `amsterdam-cornice-house` | NAME MISMATCH |
| `amsterdam_pakhuis` | `amsterdam-canal-warehouse` | NAME MISMATCH |
| `amsterdam_hofje` | `amsterdam-hofje` | NAME MISMATCH |
| `amsterdam_school_housing` | `amsterdam-school-housing` | NAME MISMATCH |
| `amsterdam_brown_cafe` | `amsterdam-brown-cafe` | NAME MISMATCH |
| `amsterdam_jordaan_house` | `amsterdam-jordaan-house` | NAME MISMATCH |
| `amsterdam_spout_gable` | `amsterdam-spout-gable-house` | NAME MISMATCH |

### Barcelona Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `barcelona_eixample_block` | `eixample-apartment-block` | NAME MISMATCH |
| `barcelona_modernisme_casa` | `modernisme-casa` | NAME MISMATCH |
| `barcelona_xamfra` | `barcelona-corner-chamfer` | NAME MISMATCH |
| `barcelona_mercat` | `barcelona-mercat` | NAME MISMATCH |
| `barcelona_townhouse` | `barcelona-townhouse` | NAME MISMATCH |
| `barcelona_taller` | `barcelona-modernist-workshop` | NAME MISMATCH |

### London Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `london_georgian_terrace` | `georgian-terrace-house` | NAME MISMATCH |
| `london_regency_terrace` | `regency-stucco-terrace` | NAME MISMATCH |
| `london_victorian_terrace` | `victorian-bay-window-terrace` | NAME MISMATCH |
| `london_mews` | `london-mews-house` | NAME MISMATCH |
| `london_crescent` | `london-crescent-terrace` | NAME MISMATCH |
| `london_townhouse` | `london-townhouse` | NAME MISMATCH |

### New York Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `newyork_cast_iron` | `soho-cast-iron-loft-building` | NAME MISMATCH |
| `newyork_art_deco` | `new-york-art-deco-tower` | NAME MISMATCH |
| `newyork_prewar` | `new-york-pre-war-apartment` | NAME MISMATCH |
| `newyork_bodega` | `new-york-corner-bodega` | NAME MISMATCH |
| `newyork_tenement` | `new-york-walk-up-tenement` | NAME MISMATCH |

### Montreal Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `montreal_triplex` | `montreal-plateau-triplex` | NAME MISMATCH |
| `montreal_duplex` | `montreal-duplex` | NAME MISMATCH |
| `montreal_limestone_commercial` | `old-montreal-limestone-commercial` | NAME MISMATCH |
| `montreal_depanneur` | `montreal-depanneur` | NAME MISMATCH |
| `montreal_warehouse_loft` | `old-montreal-warehouse-loft` | NAME MISMATCH |
| `montreal_mile_end_triplex` | `mile-end-cultural-triplex` | NAME MISMATCH |
| `montreal_second_empire` | `montreal-second-empire-civic` | NAME MISMATCH |

### Vancouver Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `vancouver_special` | `vancouver-special` | NAME MISMATCH |
| `vancouver_laneway` | `vancouver-laneway-house` | NAME MISMATCH |
| `vancouver_gastown` | `gastown-heritage-commercial` | NAME MISMATCH |
| `vancouver_craftsman` | `vancouver-craftsman-bungalow` | NAME MISMATCH |
| `vancouver_tower_podium` | `vancouverism-tower-podium` | NAME MISMATCH |
| `vancouver_skytrain_station` | `skytrain-elevated-station` | NAME MISMATCH |
| `vancouver_west_end_tower` | `west-end-mid-century-tower` | NAME MISMATCH |

### Toronto Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `toronto_bay_and_gable` | `toronto-bay-and-gable-house` | NAME MISMATCH |
| `toronto_annex_mansion` | `toronto-annex-mansion` | NAME MISMATCH |
| `toronto_rowhouse` | `toronto-brick-rowhouse` | NAME MISMATCH |
| `toronto_junction_industrial` | `toronto-junction-converted-industrial` | NAME MISMATCH |
| `toronto_edwardian` | `toronto-edwardian-foursquare` | NAME MISMATCH |
| `toronto_streetcar_stop` | `toronto-streetcar-platform-stop` | NAME MISMATCH |
| `toronto_condo_tower` | `toronto-condo-podium-tower` | NAME MISMATCH |

### Calgary Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `calgary_sandstone` | `calgary-sandstone-heritage` | NAME MISMATCH |
| `calgary_inglewood` | `inglewood-heritage-brick-commercial` | NAME MISMATCH |
| `calgary_plus15_tower` | `calgary-plus-15-connected-tower` | NAME MISMATCH |
| `calgary_beltline_midrise` | `calgary-beltline-mid-rise` | NAME MISMATCH |
| `calgary_bungalow` | `calgary-inner-city-bungalow` | NAME MISMATCH |
| `calgary_modern_infill` | `calgary-modern-infill-house` | NAME MISMATCH |
| `calgary_ctrain_station` | `calgary-ctrain-station` | NAME MISMATCH |
| `calgary_central_library` | `calgary-new-central-library` | NAME MISMATCH |

### Halifax Kit
| JSON ID | Directory Name | Status |
|---|---|---|
| `halifax_hydrostone` | `hydrostone-neighbourhood-house` | NAME MISMATCH |
| `halifax_waterfront_warehouse` | `halifax-waterfront-warehouse` | NAME MISMATCH |
| `halifax_clapboard_row` | `halifax-painted-clapboard-row` | NAME MISMATCH |
| `halifax_georgian` | `halifax-georgian-colonial` | NAME MISMATCH |
| `halifax_commercial` | `halifax-maritime-commercial` | NAME MISMATCH |
| `halifax_ferry_terminal` | `halifax-ferry-terminal` | NAME MISMATCH |

---

## 3. Category-by-Category Gap Analysis

### Transportation

**EXISTS in codebase:**
- `historic_grand_station` -- Historic Grand Station (rail)
- `contemporary_transit_hub` -- Contemporary Transit Hub
- `urban_light_rail_stop` -- Urban Light Rail Stop
- `transit_oriented_station_block` -- Transit-Oriented Station Block
- `transit_podium_residential` -- Transit Podium Residential
- `vertiport_evtol` -- Vertiport / eVTOL Facility
- `ev_charging_hub` -- EV Charging Hub / Mobility Station
- `vancouver_skytrain_station` -- SkyTrain Elevated Station
- `toronto_streetcar_stop` -- Toronto Streetcar Platform Stop
- `calgary_ctrain_station` -- Calgary CTrain Station
- `halifax_ferry_terminal` -- Halifax Ferry Terminal

**MISSING:**
- Bus Rapid Transit (BRT) station/stop
- Metro/subway station (underground)
- Commuter rail station (suburban)
- Bike-share / micromobility station
- Airport terminal (small regional)
- Cargo / freight terminal
- Park-and-ride facility
- Cable car / gondola station
- Water taxi / river ferry dock
- Intercity bus terminal
- Taxi/rideshare stand

---

### Energy

**EXISTS in codebase:**
- `solar_farm_agrivoltaics` -- Solar Farm / Agrivoltaics
- `waste_to_energy_plant` -- Waste-to-Energy Plant
- `hyperscale_data_center` -- Hyperscale Data Center (energy-adjacent)

**MISSING:**
- Wind turbine / wind farm facility
- Battery energy storage facility (BESS)
- Hydrogen production / fueling facility
- District heating / cooling plant
- Electrical substation (urban)
- Geothermal energy plant
- Biogas / biomass plant
- Small modular nuclear reactor facility
- Combined heat and power (CHP) plant
- Pumped hydro storage facility
- Solar canopy / parking structure

---

### Civic

**EXISTS in codebase:**
- `modern_fire_station` -- Modern Fire Station
- `civic_classical_building` -- Civic Classical Building (general civic)
- `civic_monumental_institution` -- Civic Monumental Institution
- `modernist_civic_block` -- Modernist Civic Block
- `contemporary_civic` -- Contemporary Civic
- `monumental_courthouse_axis` -- Monumental Courthouse
- `neoclassical_institutional` -- Neoclassical Institutional
- `brutalist_institutional` -- Brutalist Institutional
- `calgary_central_library` -- Calgary New Central Library
- `montreal_second_empire` -- Montreal Second Empire Civic
- `parisian_ecole` -- Ecole Republicaine (school)

**MISSING:**
- Public library (modern, neighbourhood-scale)
- Police station / precinct
- Post office / mail sorting facility
- City hall / municipal building (contemporary)
- Courthouse (contemporary)
- Community center / neighbourhood house
- Government office building
- Embassy / consulate
- Public restroom / comfort station
- Animal shelter
- Public works / maintenance depot

---

### Agriculture

**EXISTS in codebase:**
- `vertical_farm` -- Vertical Farm / Indoor Agriculture
- `solar_farm_agrivoltaics` -- Solar Farm / Agrivoltaics (dual agriculture/energy)

**MISSING:**
- Greenhouse / horticultural center
- Urban farm / market garden (ground-level)
- Community garden building / toolshed (note: community garden exists in open spaces)
- Grain elevator / agricultural storage
- Farmers' market pavilion (permanent structure)
- Aquaponics / hydroponics facility
- Food processing / cold storage warehouse
- Agricultural research station
- Winery / vineyard estate building
- Livestock barn / dairy

---

### Bridges / Infrastructure

**EXISTS in codebase:**
- NONE -- Zero bridge archetypes exist in the building archetype system

**MISSING:**
- Pedestrian bridge / footbridge
- Covered pedestrian bridge / skywalk (Calgary Plus-15 style is a tower, not a bridge)
- Highway overpass / interchange
- Rail bridge / viaduct
- Historic stone bridge
- Modern cable-stayed bridge
- Suspension bridge
- Lift / drawbridge / bascule bridge
- Aqueduct
- Tunnel portal / entrance
- Retaining wall / embankment
- Dam / weir
- Utility corridor / pipe bridge

Note: Bridges may be better suited as a separate archetype category (not "buildings") or as street/infrastructure elements.

---

### Healthcare

**EXISTS in codebase:**
- `art_deco_healthcare` -- Art Deco Healthcare
- `functionalist_healthcare` -- Functionalist Healthcare
- `biophilic_healthcare` -- Biophilic Modern Healthcare
- `senior_living_complex` -- Senior Living Complex (care-adjacent)

**MISSING:**
- Contemporary hospital (large, multi-wing)
- Urgent care / walk-in clinic
- Mental health / behavioral health facility
- Pharmacy / drugstore (standalone)
- Dental clinic
- Medical office building (multi-tenant)
- Rehabilitation center
- Veterinary clinic / animal hospital
- Blood bank / donation center
- Long-term care / nursing home
- Children's hospital
- Research hospital / medical campus

---

### Entertainment

**EXISTS in codebase:**
- `deco_theater_mainstreet` -- Deco Theater (cinema/performing arts)
- `concert_hall_modern` -- Concert Hall (Modern)
- `immersive_experience_venue` -- Immersive Experience Venue
- `climbing_wall_building` -- Climbing Wall Building
- `modern_sports_arena` -- Modern Sports Arena
- `monumental_antiquity_arena` -- Monumental Antiquity Arena
- `high_tech_arena` -- High-Tech Structural Arena
- `concrete_megastructure_arena` -- Concrete Megastructure Arena
- `community_recreation_centre` -- Community Recreation Centre
- `civic_modernism_rec_centre` -- Civic Modernism Rec Centre
- `postmodern_rec_centre` -- Postmodern Community Rec Centre
- `contemporary_sustainable_rec_centre` -- Contemporary Sustainable Rec Centre
- `parkitecture_recreational` -- Parkitecture
- `brewery_distillery` -- Brewery / Distillery
- `food_hall_market_hall` -- Food Hall / Market Hall

**MISSING:**
- Multiplex cinema (modern)
- Bowling alley / entertainment center
- Water park / aquatic center (indoor)
- Amusement / theme park gate building
- Nightclub / live music venue
- Casino / gaming facility
- Museum (contemporary -- separate from monumental)
- Art gallery (neighbourhood-scale)
- Skating rink / ice arena
- Trampoline park / indoor play center
- Escape room / VR arcade
- Zoo / aquarium building
- Amphitheater (outdoor performance)
- Drive-in theater
- Convention / exhibition center
- Arcade / game hall

---

### Education

**EXISTS in codebase:**
- `collegiate_gothic_education` -- Collegiate Gothic (university)
- `parisian_ecole` -- Ecole Republicaine (school)

**MISSING:**
- Elementary / primary school (contemporary)
- Middle school / junior high
- High school / secondary school
- University campus building (modern)
- Trade school / vocational institute
- Daycare / early childhood center
- Montessori / alternative school
- Special education facility
- School gymnasium / athletic building
- University library
- Student residence / dormitory
- Research laboratory building
- Continuing education / adult learning center
- Driving school
- Language school

---

## 4. Summary Statistics

| Category | Exists | Missing | Coverage |
|---|---|---|---|
| Transportation | 11 | 11 | Moderate -- good rail/LRT, no bus/metro/bike |
| Energy | 3 | 11 | Very Low -- solar and waste-to-energy only |
| Civic | 11 | 11 | Moderate -- strong institutional, weak services |
| Agriculture | 2 | 10 | Very Low -- vertical farm and agrivoltaics only |
| Bridges/Infrastructure | 0 | 13 | None -- entire category absent |
| Healthcare | 4 | 12 | Low -- stylistic healthcare only, no hospitals |
| Entertainment | 15 | 16 | Moderate -- strong arenas/rec, weak casual |
| Education | 2 | 15 | Very Low -- only collegiate gothic and ecole |

---

## 5. Priority Recommendations

### Immediate High-Priority Gaps (essential for realistic city modeling)
1. **Elementary/High School** -- every neighbourhood needs schools
2. **Public Library** -- fundamental civic building
3. **Police Station** -- core emergency services
4. **Hospital / Medical Center** -- critical healthcare
5. **Metro/Subway Station** -- underground transit
6. **Bus Rapid Transit Stop** -- most common transit type
7. **Pedestrian Bridge** -- common urban infrastructure
8. **Greenhouse / Urban Farm** -- growing urban agriculture trend

### Medium Priority (important for complete districts)
9. Pharmacy / Clinic (neighbourhood health)
10. Daycare / Early Childhood Center
11. Multiplex Cinema
12. Post Office
13. Bowling / Entertainment Center
14. Wind Turbine Facility
15. Battery Storage Facility
16. Community Garden Building

### Lower Priority (specialty/niche)
17. Convention Center
18. Casino
19. Airport Terminal
20. Dam / Aqueduct
21. Veterinary Clinic
22. Driving School

### Structural Fix Needed
- **68 city-kit archetypes** have directory name mismatches between JSON IDs and image card folder names. A renaming pass or ID mapping layer is needed to connect them.

---

## 6. Appendix: All 96 Archetypes with Matching Directories

These JSON IDs have exact-match underscore directories containing image cards:

1. `collegiate_gothic_education`
2. `brownstone_rowhouse_frontage`
3. `classic_brownstone_streetwall`
4. `historical_brick_main_street`
5. `victorian_heritage_avenue`
6. `contemporary_midrise_residential`
7. `contemporary_townhouse_courtyard`
8. `detached_contemporary_infill`
9. `courtyard_family_housing`
10. `modern_glass_office_institutional`
11. `modernist_civic_block`
12. `mid_century_modern_pavilion_block`
13. `civic_classical_building`
14. `monumental_courthouse_axis`
15. `industrial_brick_mixed_use`
16. `adaptive_reuse_warehouse_lofts`
17. `scandinavian_urban_residential`
18. `nordic_timber_midrise`
19. `mediterranean_villa_estate`
20. `mediterranean_arcade_mixed_use`
21. `parametric_future_hub`
22. `autonomous_tech_campus`
23. `art_deco_setback_tower`
24. `deco_theater_mainstreet`
25. `traditional_vernacular_market_street`
26. `vernacular_courtyard_housing`
27. `minimalist_courtyard_block`
28. `minimalist_infill_townhouse`
29. `parisian_midrise_block`
30. `parisian_boulevard_corner`
31. `mountain_alpine_chalet`
32. `alpine_mixed_use_lodge`
33. `transit_oriented_station_block`
34. `transit_podium_residential`
35. `glass_tower_podium_modern`
36. `skyline_glass_office_cluster`
37. `civic_monumental_institution`
38. `monumental_museum_axis`
39. `japanese_contemporary_lanehouse`
40. `japanese_machiya_mixed_use`
41. `eco_urban_bioclimatic_block`
42. `vertical_forest_residential`
43. `coastal_resort_terrace_block`
44. `coastal_breezeway_mixed_use`
45. `custom_prompt_ready_archetype`
46. `custom_contextual_experiment`
47. `community_recreation_centre`
48. `modern_sports_arena`
49. `boutique_hotel_tower`
50. `neoclassical_institutional`
51. `brutalist_institutional`
52. `contemporary_civic`
53. `art_deco_healthcare`
54. `functionalist_healthcare`
55. `biophilic_healthcare`
56. `daylight_factory`
57. `industrial_park_modernism`
58. `art_deco_industrial`
59. `functionalist_brick_industrial`
60. `structural_expressionism_industrial`
61. `corrugated_vernacular_industrial`
62. `machine_aesthetic_heavy_industrial`
63. `brutalist_utility_heavy_industrial`
64. `early_20c_megastructure_industrial`
65. `romanesque_revival_warehouse`
66. `midcentury_distribution_warehouse`
67. `modern_bigbox_warehouse`
68. `parkitecture_recreational`
69. `civic_modernism_rec_centre`
70. `postmodern_rec_centre`
71. `contemporary_sustainable_rec_centre`
72. `monumental_antiquity_arena`
73. `high_tech_arena`
74. `concrete_megastructure_arena`
75. `chateauesque_hotel`
76. `resort_modernism_hotel`
77. `corporate_tower_hotel`
78. `historic_grand_station`
79. `contemporary_transit_hub`
80. `urban_light_rail_stop`
81. `climbing_wall_building`
82. `waste_to_energy_plant`
83. `senior_living_complex`
84. `brewery_distillery`
85. `solar_farm_agrivoltaics`
86. `immersive_experience_venue`
87. `modern_fire_station`
88. `concert_hall_modern`
89. `vertiport_evtol`
90. `shophouse_southeast_asian`
91. `food_hall_market_hall`
92. `ev_charging_hub`
93. `hyperscale_data_center`
94. `vertical_farm`
95. `mall_redevelopment`
96. `terraced_stepped_building`
