# Building Archetype Category Audit Report

Generated: 2026-03-30

---

## 1. Current State Summary

### 1.1 Archetype Count

**166 building archetypes** in `frontend/src/data/buildingArchetypes.json`.

### 1.2 Current Aesthetic Categories (JSON `categories` array)

These are the `aestheticCategory` groupings defined in the JSON. They describe **visual/architectural style**, not functional use:

| Category ID | Label |
|---|---|
| `historical` | Historical |
| `contemporary_urban` | Contemporary Urban |
| `modernist` | Modernist |
| `classical` | Classical |
| `industrial_brick` | Industrial Brick |
| `scandinavian_nordic` | Scandinavian / Nordic |
| `mediterranean` | Mediterranean |
| `futuristic` | Futuristic |
| `art_deco` | Art Deco |
| `traditional_vernacular` | Traditional / Vernacular |
| `minimalist` | Minimalist |
| `parisian` | Parisian |
| `brownstone_rowhouse` | Brownstone / Rowhouse |
| `mountain_alpine` | Mountain / Alpine |
| `transit_oriented_contemporary` | Transit-Oriented Contemporary |
| `glass_tower_modern` | Glass Tower Modern |
| `civic_monumental` | Civic Monumental |
| `japanese_contemporary` | Japanese Contemporary |
| `eco_urban_green_architecture` | Eco-Urban / Green Architecture |
| `coastal_resort_contemporary` | Coastal / Resort Contemporary |
| `other` | Custom / Other |

Additionally, many district-kit archetypes use per-archetype aesthetic categories not in the master list (e.g., `amsterdam_canal`, `barcelona_eixample`, `london_georgian`, `newyork_cast_iron`, `montreal_plateau`, `toronto_victorian`, `calgary_sandstone`, `halifax_hydrostone`, etc.). These are valid but the `categories[]` array in the JSON is incomplete -- it only lists 21 categories while archetypes reference 80+ distinct `aestheticCategory` values.

### 1.3 Current `developmentType` Values in UI Dropdown

From `ZonePropertiesPanel.tsx` (building and development_area zone types):

| Group | Value | Label |
|---|---|---|
| -- | `city_kit` | City Kit |
| Residential | `residential_single_family` | Single Family |
| Residential | `residential_duplex` | Duplex |
| Residential | `residential_multifamily` | Multi-Family |
| Residential | `residential_highrise` | High-Rise |
| Commercial | `commercial_light` | Light Commercial |
| Commercial | `commercial_retail` | Retail |
| Commercial | `commercial_office` | Office |
| Commercial | `commercial` | General Commercial |
| -- | `mixed_use` | Mixed Use |
| Institutional | `institutional` | General Institutional |
| Institutional | `institutional_education` | Education |
| Institutional | `institutional_health` | Health Care |
| Industrial | `industrial_light` | Light Industrial |
| Industrial | `industrial` | General Industrial |
| Industrial | `industrial_heavy` | Heavy Industrial |
| Industrial | `industrial_warehouse` | Warehouse |
| -- | `recreational` | Recreational |
| -- | `recreational_centre` | Rec Centre |
| -- | `sports_arena` | Sports Arena |
| -- | `hotel` | Hotels |
| -- | `other` | Other |

**Note:** The "building" zone dropdown has all of the above. The "development_area" dropdown is missing `city_kit`, `recreational`, `recreational_centre`, `sports_arena`, `hotel`, and `other`.

### 1.4 developmentType Mismatch Analysis

**20 developmentType values exist in archetype JSON but are NOT in the UI dropdown:**

| Value | Used By | Issue |
|---|---|---|
| `commercial_creative` | toronto_junction_industrial | Not selectable in UI |
| `commercial_heritage` | 5 archetypes (montreal, vancouver, calgary, halifax) | Not selectable |
| `commercial_hospitality` | amsterdam_brown_cafe | Not selectable |
| `commercial_loft` | newyork_cast_iron | Not selectable |
| `commercial_market` | parisian_marche_couvert, barcelona_mercat | Not selectable |
| `commercial_workshop` | barcelona_taller | Not selectable |
| `institutional_civic` | montreal_second_empire | Not selectable |
| `institutional_cultural` | calgary_central_library | Not selectable |
| `institutional_heritage` | halifax_georgian | Not selectable |
| `residential_apartment` | 9 archetypes (amsterdam, barcelona, london, NY, vancouver) | Not selectable |
| `residential_condo` | vancouver_tower_podium, toronto_condo_tower | Not selectable |
| `residential_house` | 6 archetypes (vancouver, toronto, calgary, halifax) | Not selectable |
| `residential_laneway` | vancouver_laneway | Not selectable |
| `residential_loft` | amsterdam_pakhuis, montreal_warehouse_loft | Not selectable |
| `residential_luxury` | 5 archetypes (paris, barcelona, london, toronto) | Not selectable |
| `residential_social` | amsterdam_hofje, amsterdam_school_housing | Not selectable |
| `residential_townhouse` | 5 archetypes (london, toronto, halifax) | Not selectable |
| `residential_triplex` | montreal_triplex, montreal_mile_end_triplex | Not selectable |
| `transit_station` | 4 archetypes (vancouver, calgary, halifax SkyTrain/CTrain/Ferry) | Not selectable |
| `transit_stop` | toronto_streetcar_stop | Not selectable |

**3 dropdown values exist in UI but are NOT used by any archetype:**

| Value | Issue |
|---|---|
| `city_kit` | Meta-option, not a real dev type -- expected |
| `commercial` | No archetype uses bare "commercial" |
| `other` | No archetype uses "other" |

**Impact:** District-kit archetypes (Amsterdam, Barcelona, London, New York, Montreal, Vancouver, Toronto, Calgary, Halifax) use fine-grained developmentType values that the dropdown does not expose. Users cannot filter to these types unless using City Kit mode. The `getAllowedDevelopmentTypes()` function in `aestheticCatalog.ts` only maps broad zone types to broad dev types, so these fine-grained values are invisible to the filtering system.

---

## 2. Proposed Functional Category Mapping

Below is every archetype mapped to one of the proposed functional categories. The current system groups by **aesthetic style**; the proposed system groups by **functional use**.

### Transportation (7 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `historic_grand_station` | Historic Grand Station | institutional |
| `contemporary_transit_hub` | Contemporary Transit Hub | institutional |
| `urban_light_rail_stop` | Urban Light Rail Stop | institutional |
| `vancouver_skytrain_station` | SkyTrain Elevated Station | transit_station |
| `toronto_streetcar_stop` | Toronto Streetcar Platform Stop | transit_stop |
| `calgary_ctrain_station` | Calgary CTrain Station | transit_station |
| `halifax_ferry_terminal` | Halifax Ferry Terminal | transit_station |

**Flag:** `vertiport_evtol` (Vertiport / eVTOL Facility) also belongs here. Currently `developmentType: institutional`.

| `vertiport_evtol` | Vertiport / eVTOL Facility | institutional |

**Total: 8 archetypes**

### Energy / Infrastructure (4 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `waste_to_energy_plant` | Waste-to-Energy Plant | industrial |
| `solar_farm_agrivoltaics` | Solar Farm / Agrivoltaics | industrial |
| `ev_charging_hub` | EV Charging Hub / Mobility Station | industrial |
| `hyperscale_data_center` | Hyperscale Data Center | industrial |

**Gap:** No wind energy, battery storage, or district heating archetypes exist.

### Civic / Institutional (12 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `civic_classical_building` | Civic Classical Building | institutional |
| `monumental_courthouse_axis` | Monumental Courthouse Axis | institutional |
| `modernist_civic_block` | Modernist Civic Block | institutional |
| `civic_monumental_institution` | Civic Monumental Institution | institutional_education |
| `monumental_museum_axis` | Monumental Museum Axis | institutional |
| `neoclassical_institutional` | Neoclassical Institutional | institutional |
| `brutalist_institutional` | Brutalist Institutional | institutional |
| `contemporary_civic` | Contemporary Civic | institutional |
| `modern_fire_station` | Modern Fire Station | institutional |
| `montreal_second_empire` | Montreal Second Empire Civic | institutional_civic |
| `halifax_georgian` | Halifax Georgian Colonial | institutional_heritage |
| `calgary_central_library` | Calgary New Central Library | institutional_cultural |

### Agriculture (1 archetype)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `vertical_farm` | Vertical Farm / Indoor Agriculture | industrial |

**Gap:** Only 1 archetype. No community gardens (those are open spaces), no greenhouse complexes, no agricultural processing facilities.

### Healthcare (4 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `art_deco_healthcare` | Art Deco Healthcare | institutional_health |
| `functionalist_healthcare` | Functionalist Healthcare | institutional_health |
| `biophilic_healthcare` | Biophilic Modern Healthcare | institutional_health |
| `senior_living_complex` | Senior Living Complex | residential_multifamily |

**Flag:** `senior_living_complex` is categorized as `residential_multifamily` but functionally is healthcare-adjacent. Could reasonably live in Residential or Healthcare.

### Entertainment / Culture (7 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `deco_theater_mainstreet` | Deco Theater Mainstreet | commercial_light |
| `modern_sports_arena` | Modern Sports Arena | sports_arena |
| `monumental_antiquity_arena` | Monumental Antiquity Arena | sports_arena |
| `high_tech_arena` | High-Tech Structural Arena | sports_arena |
| `concrete_megastructure_arena` | Concrete Megastructure Arena | sports_arena |
| `immersive_experience_venue` | Immersive Experience Venue | recreational |
| `concert_hall_modern` | Concert Hall (Modern) | recreational |

### Hospitality (5 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `boutique_hotel_tower` | Boutique Hotel | hotel |
| `chateauesque_hotel` | Chateauesque / Grand Railway Hotel | hotel |
| `resort_modernism_hotel` | Resort Modernism Hotel | hotel |
| `corporate_tower_hotel` | Corporate Tower Hotel | hotel |
| `amsterdam_brown_cafe` | Amsterdam Brown Cafe | commercial_hospitality |

**Flag:** `amsterdam_brown_cafe` is a pub/cafe, not really a hotel. Could also be Commercial.

### Education (3 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `collegiate_gothic_education` | Collegiate Gothic | institutional_education |
| `autonomous_tech_campus` | Autonomous Tech Campus | institutional_education |
| `parisian_ecole` | Ecole Republicaine | institutional_education |

**Flag:** `civic_monumental_institution` has `developmentType: institutional_education` but is more of a general civic building. Listed under Civic above.

### Recreation (6 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `community_recreation_centre` | Community Recreation Centre | recreational_centre |
| `civic_modernism_rec_centre` | Civic Modernism Rec Centre | recreational_centre |
| `postmodern_rec_centre` | Postmodern Community Rec Centre | recreational_centre |
| `contemporary_sustainable_rec_centre` | Contemporary Sustainable Rec Centre | recreational_centre |
| `parkitecture_recreational` | Parkitecture | recreational |
| `climbing_wall_building` | Climbing Wall Building | recreational |

### Industrial (12 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `daylight_factory` | Daylight Factory | industrial_light |
| `industrial_park_modernism` | Industrial Park Modernism | industrial_light |
| `art_deco_industrial` | Art Deco Industrial | industrial_light |
| `functionalist_brick_industrial` | Functionalist Brick Industrial | industrial |
| `structural_expressionism_industrial` | Structural Expressionism Industrial | industrial |
| `corrugated_vernacular_industrial` | Corrugated Vernacular Industrial | industrial |
| `machine_aesthetic_heavy_industrial` | Machine Aesthetic Heavy Industrial | industrial_heavy |
| `brutalist_utility_heavy_industrial` | Brutalist Utility Heavy Industrial | industrial_heavy |
| `early_20c_megastructure_industrial` | Early 20th Century Megastructure | industrial_heavy |
| `romanesque_revival_warehouse` | Romanesque Revival Warehouse | industrial_warehouse |
| `midcentury_distribution_warehouse` | Mid-Century Distribution Warehouse | industrial_warehouse |
| `modern_bigbox_warehouse` | Modern Big-Box Logistics | industrial_warehouse |

### Residential (55 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `brownstone_rowhouse_frontage` | Brownstone Rowhouse Frontage | residential_duplex |
| `classic_brownstone_streetwall` | Classic Brownstone Streetwall | residential_duplex |
| `victorian_heritage_avenue` | Victorian Heritage Avenue | residential_duplex |
| `contemporary_midrise_residential` | Contemporary Mid-Rise Residential | residential_multifamily |
| `contemporary_townhouse_courtyard` | Contemporary Townhouse Courtyard | residential_duplex |
| `detached_contemporary_infill` | Detached Contemporary Infill | residential_single_family |
| `courtyard_family_housing` | Courtyard Family Housing | residential_multifamily |
| `scandinavian_urban_residential` | Scandinavian Urban Residential | residential_multifamily |
| `nordic_timber_midrise` | Nordic Timber Mid-Rise | residential_multifamily |
| `mediterranean_villa_estate` | Mediterranean Villa / Estate | residential_single_family |
| `art_deco_setback_tower` | Art Deco Setback Tower | residential_highrise |
| `vernacular_courtyard_housing` | Vernacular Courtyard Housing | residential_duplex |
| `minimalist_courtyard_block` | Minimalist Courtyard Block | residential_multifamily |
| `minimalist_infill_townhouse` | Minimalist Infill Townhouse | residential_duplex |
| `mountain_alpine_chalet` | Mountain / Alpine Chalet | residential_single_family |
| `transit_podium_residential` | Transit Podium Residential | residential_multifamily |
| `japanese_contemporary_lanehouse` | Japanese Contemporary Lanehouse | residential_single_family |
| `eco_urban_bioclimatic_block` | Eco-Urban Bioclimatic Block | residential_multifamily |
| `vertical_forest_residential` | Vertical Forest Residential | residential_highrise |
| `terraced_stepped_building` | Terraced / Stepped Building | residential_multifamily |
| `senior_living_complex` | Senior Living Complex | residential_multifamily |
| `parisian_hotel_particulier` | Hotel Particulier | residential_luxury |
| `parisian_marais_building` | Pre-Haussmann Marais Building | residential_apartment |
| `amsterdam_neck_gable` | Amsterdam Neck Gable House | residential_apartment |
| `amsterdam_step_gable` | Amsterdam Step Gable House | residential_apartment |
| `amsterdam_bell_gable` | Amsterdam Bell Gable House | residential_apartment |
| `amsterdam_cornice_house` | Amsterdam Cornice House | residential_apartment |
| `amsterdam_pakhuis` | Amsterdam Canal Warehouse | residential_loft |
| `amsterdam_hofje` | Amsterdam Hofje | residential_social |
| `amsterdam_school_housing` | Amsterdam School Housing | residential_social |
| `amsterdam_jordaan_house` | Amsterdam Jordaan House | residential_apartment |
| `amsterdam_spout_gable` | Amsterdam Spout Gable House | residential_apartment |
| `barcelona_modernisme_casa` | Modernisme Casa | residential_luxury |
| `barcelona_townhouse` | Barcelona Townhouse | residential_apartment |
| `london_georgian_terrace` | Georgian Terrace House | residential_townhouse |
| `london_regency_terrace` | Regency Stucco Terrace | residential_luxury |
| `london_victorian_terrace` | Victorian Bay-Window Terrace | residential_apartment |
| `london_mews` | London Mews House | residential_townhouse |
| `london_crescent` | London Crescent Terrace | residential_luxury |
| `london_townhouse` | London Townhouse | residential_luxury |
| `newyork_prewar` | New York Pre-War Apartment | residential_apartment |
| `newyork_tenement` | New York Walk-Up Tenement | residential_apartment |
| `montreal_triplex` | Montreal Plateau Triplex | residential_triplex |
| `montreal_duplex` | Montreal Duplex | residential_duplex |
| `montreal_warehouse_loft` | Old Montreal Warehouse Loft | residential_loft |
| `montreal_mile_end_triplex` | Mile End Cultural Triplex | residential_triplex |
| `vancouver_special` | Vancouver Special | residential_house |
| `vancouver_laneway` | Vancouver Laneway House | residential_laneway |
| `vancouver_craftsman` | Vancouver Craftsman Bungalow | residential_house |
| `vancouver_tower_podium` | Vancouverism Tower-Podium | residential_condo |
| `vancouver_west_end_tower` | West End Mid-Century Tower | residential_apartment |
| `toronto_bay_and_gable` | Toronto Bay-and-Gable House | residential_townhouse |
| `toronto_annex_mansion` | Toronto Annex Mansion | residential_luxury |
| `toronto_rowhouse` | Toronto Brick Rowhouse | residential_townhouse |
| `toronto_edwardian` | Toronto Edwardian Foursquare | residential_house |
| `toronto_condo_tower` | Toronto Condo Podium Tower | residential_condo |
| `calgary_bungalow` | Calgary Inner-City Bungalow | residential_house |
| `calgary_modern_infill` | Calgary Modern Infill House | residential_house |
| `halifax_hydrostone` | Hydrostone Neighbourhood House | residential_house |
| `halifax_clapboard_row` | Halifax Painted Clapboard Row | residential_townhouse |
| `adaptive_reuse_warehouse_lofts` | Adaptive Reuse Warehouse Lofts | residential_multifamily |

**Note:** 55 residential archetypes but only 4 residential options in the dropdown. The fine-grained types (`residential_apartment`, `residential_townhouse`, `residential_house`, `residential_condo`, `residential_luxury`, `residential_loft`, `residential_laneway`, `residential_social`, `residential_triplex`) are all invisible to users.

### Commercial / Mixed-Use (33 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `historical_brick_main_street` | Historical Brick Main Street | commercial_light |
| `modern_glass_office_institutional` | Modern Glass Office / Institutional | commercial_office |
| `industrial_brick_mixed_use` | Industrial Brick Mixed Use | mixed_use |
| `mediterranean_arcade_mixed_use` | Mediterranean Arcade Mixed Use | commercial_retail |
| `parametric_future_hub` | Parametric Future Hub | commercial_office |
| `traditional_vernacular_market_street` | Traditional Vernacular Market Street | commercial_light |
| `mid_century_modern_pavilion_block` | Mid-Century Modern Pavilion Block | mixed_use |
| `parisian_midrise_block` | Parisian Mid-Rise | mixed_use |
| `parisian_boulevard_corner` | Parisian Boulevard Corner | mixed_use |
| `alpine_mixed_use_lodge` | Alpine Mixed-Use Lodge | mixed_use |
| `transit_oriented_station_block` | Transit-Oriented Station Block | mixed_use |
| `glass_tower_podium_modern` | Glass Tower Modern | commercial_office |
| `skyline_glass_office_cluster` | Skyline Glass Office Cluster | commercial_office |
| `japanese_machiya_mixed_use` | Japanese Machiya Mixed Use | commercial_retail |
| `coastal_resort_terrace_block` | Coastal / Resort Terrace Block | mixed_use |
| `coastal_breezeway_mixed_use` | Coastal Breezeway Mixed Use | commercial_retail |
| `brewery_distillery` | Brewery / Distillery | commercial_retail |
| `shophouse_southeast_asian` | Shophouse (Southeast Asian) | commercial_retail |
| `food_hall_market_hall` | Food Hall / Market Hall | commercial_retail |
| `mall_redevelopment` | Mall Redevelopment | mixed_use |
| `parisian_corner_dome` | Parisian Corner with Dome | mixed_use |
| `parisian_passage_couvert` | Passage Couvert | commercial_retail |
| `parisian_marche_couvert` | Marche Couvert | commercial_market |
| `parisian_grand_magasin` | Grand Magasin | commercial_retail |
| `parisian_cafe_brasserie` | Parisian Cafe Brasserie | mixed_use |
| `barcelona_eixample_block` | Eixample Apartment Block | mixed_use |
| `barcelona_xamfra` | Barcelona Corner Chamfer | mixed_use |
| `barcelona_mercat` | Barcelona Mercat | commercial_market |
| `barcelona_taller` | Barcelona Modernist Workshop | commercial_workshop |
| `newyork_cast_iron` | SoHo Cast-Iron Loft Building | commercial_loft |
| `newyork_art_deco` | New York Art Deco Tower | mixed_use |
| `newyork_bodega` | New York Corner Bodega | commercial_retail |
| `montreal_limestone_commercial` | Old Montreal Limestone Commercial | commercial_heritage |
| `montreal_depanneur` | Montreal Depanneur | commercial_retail |
| `vancouver_gastown` | Gastown Heritage Commercial | commercial_heritage |
| `toronto_junction_industrial` | Toronto Junction Converted Industrial | commercial_creative |
| `calgary_sandstone` | Calgary Sandstone Heritage | commercial_heritage |
| `calgary_inglewood` | Inglewood Heritage Brick Commercial | commercial_heritage |
| `calgary_plus15_tower` | Calgary Plus-15 Connected Tower | commercial_office |
| `calgary_beltline_midrise` | Calgary Beltline Mid-Rise | mixed_use |
| `halifax_waterfront_warehouse` | Halifax Waterfront Warehouse | commercial_heritage |
| `halifax_commercial` | Halifax Maritime Commercial | commercial_heritage |

### Custom / Other (2 archetypes)

| Archetype ID | Title | Current developmentType |
|---|---|---|
| `custom_prompt_ready_archetype` | Custom Prompt-Ready Archetype | *(none)* |
| `custom_contextual_experiment` | Custom Contextual Experiment | *(none)* |

---

## 3. Ambiguous / Multi-Category Archetypes

These archetypes could reasonably belong to more than one proposed category:

| Archetype ID | Title | Primary Category | Alternative Category | Notes |
|---|---|---|---|---|
| `senior_living_complex` | Senior Living Complex | Residential | Healthcare | Functionally residential but healthcare-adjacent |
| `amsterdam_brown_cafe` | Amsterdam Brown Cafe | Hospitality | Commercial | A pub/cafe, not a hotel |
| `autonomous_tech_campus` | Autonomous Tech Campus | Education | Commercial/Mixed-Use | Innovation campus straddles education and commercial |
| `civic_monumental_institution` | Civic Monumental Institution | Civic/Institutional | Education | Has `institutional_education` dev type but is a general civic building |
| `transit_oriented_station_block` | Transit-Oriented Station Block | Commercial/Mixed-Use | Transportation | Mixed-use building near transit, not a station itself |
| `transit_podium_residential` | Transit Podium Residential | Residential | Transportation | Residential tower near transit |
| `adaptive_reuse_warehouse_lofts` | Adaptive Reuse Warehouse Lofts | Residential | Industrial | Former industrial, now residential |
| `industrial_brick_mixed_use` | Industrial Brick Mixed Use | Commercial/Mixed-Use | Industrial | Industrial aesthetic but mixed-use function |
| `brewery_distillery` | Brewery / Distillery | Commercial | Industrial | Production facility but commercially oriented |
| `solar_farm_agrivoltaics` | Solar Farm / Agrivoltaics | Energy | Agriculture | Dual-use energy + agriculture |
| `deco_theater_mainstreet` | Deco Theater Mainstreet | Entertainment/Culture | Commercial | Sits on a commercial main street |
| `toronto_junction_industrial` | Toronto Junction Converted Industrial | Commercial | Industrial | Former industrial, now commercial/creative |
| `parkitecture_recreational` | Parkitecture | Recreation | Parks/Open Space | Park buildings blur the line |
| `vertiport_evtol` | Vertiport / eVTOL Facility | Transportation | Energy/Infrastructure | Aviation facility |
| `parisian_cafe_brasserie` | Parisian Cafe Brasserie | Commercial | Hospitality | Cafe/restaurant |
| `ev_charging_hub` | EV Charging Hub | Energy | Transportation | Mobility infrastructure |

---

## 4. Category Gap Analysis

| Proposed Category | Archetype Count | Assessment |
|---|---|---|
| **Residential** | 55 | Well covered; rich variety across cities |
| **Commercial/Mixed-Use** | 33+ | Well covered |
| **Industrial** | 12 | Good coverage (light, general, heavy, warehouse) |
| **Civic/Institutional** | 12 | Good coverage |
| **Transportation** | 8 | Adequate; could add bus terminal, airport terminal |
| **Entertainment/Culture** | 7 | Adequate; could add museum building, gallery |
| **Recreation** | 6 | Adequate |
| **Hospitality** | 5 | Adequate |
| **Energy/Infrastructure** | 4 | Sparse -- no wind, battery, district heating |
| **Healthcare** | 4 | Sparse -- only 3 hospital styles + senior living |
| **Education** | 3 | Sparse -- only 3 archetypes |
| **Custom/Other** | 2 | As expected |
| **Agriculture** | 1 | Very sparse -- only vertical farm |
| **Bridges/Infrastructure** | 0 | **EMPTY** -- no bridge or overpass archetypes |

### Categories with Significant Gaps

1. **Bridges/Infrastructure**: Zero archetypes. No pedestrian bridges, overpasses, or infrastructure structures.
2. **Agriculture**: Only 1 archetype (vertical_farm). Missing: greenhouse, agricultural processing, community garden structures.
3. **Education**: Only 3 archetypes. Missing: primary school, high school, modern university building, daycare/early childhood center.
4. **Healthcare**: Only 3+1 archetypes. Missing: modern hospital, walk-in clinic, urgent care, mental health facility.
5. **Energy**: Only 4 archetypes. Missing: wind farm, battery storage, district energy plant, hydrogen facility.

---

## 5. developmentType Taxonomy Issues

### 5.1 Fine-Grained Types Not Exposed in Dropdown

The district-kit archetypes introduced 20 new developmentType values that the dropdown does not offer. This means:

- A user cannot directly filter to see "residential_townhouse" or "residential_apartment" archetypes
- The `getAllowedDevelopmentTypes()` function maps `residential` zone to `['residential', 'residential_single_family', 'residential_duplex', 'residential_multifamily', 'residential_highrise']` -- which **excludes** `residential_apartment`, `residential_townhouse`, `residential_house`, `residential_condo`, `residential_luxury`, `residential_loft`, `residential_laneway`, `residential_social`, `residential_triplex`
- Similarly for commercial: `commercial_heritage`, `commercial_market`, `commercial_loft`, `commercial_creative`, `commercial_workshop`, `commercial_hospitality` are all excluded from filtering

**Result:** When a user selects zone_type "residential", district-kit archetypes with these fine-grained types are **invisible** in the aesthetic picker.

### 5.2 Missing Functional Categories in Dropdown

The dropdown has no top-level categories for:
- **Transportation** -- transit stations are tagged as `institutional` or `transit_station`, neither of which maps well
- **Energy/Infrastructure** -- tagged as `industrial`, which lumps them with factories
- **Entertainment/Culture** -- sports arenas have `sports_arena` but theaters and concert halls are `commercial_light` or `recreational`
- **Agriculture** -- tagged as `industrial`
- **Hospitality** -- has `hotel` in dropdown but `commercial_hospitality` is not included

### 5.3 Inconsistent Naming

- Some use underscores (`mixed_use`), some use hyphens in labels but not values
- `residential_luxury` is a lifestyle tier, not a density type like the rest of the residential taxonomy
- `commercial_heritage` describes age/preservation status, not commercial function
- `institutional_civic` vs `institutional` vs `institutional_heritage` -- overlapping concepts

---

## 6. Recommendations

### 6.1 Immediate Fixes (No Category Restructuring)

1. **Update `getAllowedDevelopmentTypes()`** to include all fine-grained residential and commercial subtypes so district-kit archetypes appear when filtering by zone type.
2. **Add missing developmentType values to the dropdown** -- at minimum add `transit_station` and `transit_stop` as a Transportation group.
3. **Fix `vertiport_evtol` and transit stations** -- they should not be `institutional`. Use `transit_station` consistently.

### 6.2 Proposed Dropdown Restructuring

```
-- Select --
City Kit

Residential
  Single Family / House
  Duplex
  Townhouse / Rowhouse
  Triplex
  Apartment / Multi-Family
  High-Rise / Condo
  Laneway / ADU
  Senior Living

Commercial
  Retail
  Office
  Light Commercial
  Market / Food Hall
  Heritage Commercial
  Hospitality / Cafe

Mixed Use

Institutional
  General Institutional
  Education
  Health Care
  Civic / Government

Industrial
  Light Industrial
  General Industrial
  Heavy Industrial
  Warehouse / Logistics

Transportation
  Transit Station
  Transit Stop

Entertainment / Culture
  Sports Arena
  Concert / Performance Venue
  Theater / Cultural

Recreation
  Rec Centre
  Recreational

Hospitality
  Hotel / Resort

Energy / Infrastructure
  Renewable Energy
  Data Center
  EV / Mobility

Other
```

### 6.3 Long-Term: Introduce `functionalCategory` Field

Add a new `functionalCategory` field to each archetype (separate from `aestheticCategory` which describes visual style). This would enable:
- Filtering by **what the building does** (Transportation, Healthcare, etc.)
- Keeping the existing aesthetic category system intact for style-based browsing
- Cleaner dropdown organization

---

## 7. Complete Archetype-to-Category Mapping Table

| # | Archetype ID | Title | District Kit | Current developmentType | Proposed Functional Category |
|---|---|---|---|---|---|
| 1 | `collegiate_gothic_education` | Collegiate Gothic | -- | institutional_education | Education |
| 2 | `brownstone_rowhouse_frontage` | Brownstone Rowhouse Frontage | new_york | residential_duplex | Residential |
| 3 | `classic_brownstone_streetwall` | Classic Brownstone Streetwall | -- | residential_duplex | Residential |
| 4 | `historical_brick_main_street` | Historical Brick Main Street | -- | commercial_light | Commercial/Mixed-Use |
| 5 | `victorian_heritage_avenue` | Victorian Heritage Avenue | -- | residential_duplex | Residential |
| 6 | `contemporary_midrise_residential` | Contemporary Mid-Rise Residential | classic | residential_multifamily | Residential |
| 7 | `contemporary_townhouse_courtyard` | Contemporary Townhouse Courtyard | classic | residential_duplex | Residential |
| 8 | `detached_contemporary_infill` | Detached Contemporary Infill | -- | residential_single_family | Residential |
| 9 | `courtyard_family_housing` | Courtyard Family Housing | -- | residential_multifamily | Residential |
| 10 | `modern_glass_office_institutional` | Modern Glass Office / Institutional | classic | commercial_office | Commercial/Mixed-Use |
| 11 | `modernist_civic_block` | Modernist Civic Block | -- | institutional | Civic/Institutional |
| 12 | `mid_century_modern_pavilion_block` | Mid-Century Modern Pavilion Block | -- | mixed_use | Commercial/Mixed-Use |
| 13 | `civic_classical_building` | Civic Classical Building | classic | institutional | Civic/Institutional |
| 14 | `monumental_courthouse_axis` | Monumental Courthouse Axis | -- | institutional | Civic/Institutional |
| 15 | `industrial_brick_mixed_use` | Industrial Brick Mixed Use | classic | mixed_use | Commercial/Mixed-Use |
| 16 | `adaptive_reuse_warehouse_lofts` | Adaptive Reuse Warehouse Lofts | classic | residential_multifamily | Residential |
| 17 | `scandinavian_urban_residential` | Scandinavian Urban Residential | copenhagen | residential_multifamily | Residential |
| 18 | `nordic_timber_midrise` | Nordic Timber Mid-Rise | copenhagen | residential_multifamily | Residential |
| 19 | `mediterranean_villa_estate` | Mediterranean Villa / Estate | mediterranean | residential_single_family | Residential |
| 20 | `mediterranean_arcade_mixed_use` | Mediterranean Arcade Mixed Use | mediterranean | commercial_retail | Commercial/Mixed-Use |
| 21 | `parametric_future_hub` | Parametric Future Hub | -- | commercial_office | Commercial/Mixed-Use |
| 22 | `autonomous_tech_campus` | Autonomous Tech Campus | -- | institutional_education | Education |
| 23 | `art_deco_setback_tower` | Art Deco Setback Tower | -- | residential_highrise | Residential |
| 24 | `deco_theater_mainstreet` | Deco Theater Mainstreet | -- | commercial_light | Entertainment/Culture |
| 25 | `traditional_vernacular_market_street` | Traditional Vernacular Market Street | -- | commercial_light | Commercial/Mixed-Use |
| 26 | `vernacular_courtyard_housing` | Vernacular Courtyard Housing | -- | residential_duplex | Residential |
| 27 | `minimalist_courtyard_block` | Minimalist Courtyard Block | -- | residential_multifamily | Residential |
| 28 | `minimalist_infill_townhouse` | Minimalist Infill Townhouse | -- | residential_duplex | Residential |
| 29 | `parisian_midrise_block` | Parisian Mid-Rise | paris | mixed_use | Commercial/Mixed-Use |
| 30 | `parisian_boulevard_corner` | Parisian Boulevard Corner | paris | mixed_use | Commercial/Mixed-Use |
| 31 | `mountain_alpine_chalet` | Mountain / Alpine Chalet | -- | residential_single_family | Residential |
| 32 | `alpine_mixed_use_lodge` | Alpine Mixed-Use Lodge | -- | mixed_use | Commercial/Mixed-Use |
| 33 | `transit_oriented_station_block` | Transit-Oriented Station Block | -- | mixed_use | Commercial/Mixed-Use |
| 34 | `transit_podium_residential` | Transit Podium Residential | -- | residential_multifamily | Residential |
| 35 | `glass_tower_podium_modern` | Glass Tower Modern | -- | commercial_office | Commercial/Mixed-Use |
| 36 | `skyline_glass_office_cluster` | Skyline Glass Office Cluster | -- | commercial_office | Commercial/Mixed-Use |
| 37 | `civic_monumental_institution` | Civic Monumental Institution | -- | institutional_education | Civic/Institutional |
| 38 | `monumental_museum_axis` | Monumental Museum Axis | -- | institutional | Civic/Institutional |
| 39 | `japanese_contemporary_lanehouse` | Japanese Contemporary Lanehouse | -- | residential_single_family | Residential |
| 40 | `japanese_machiya_mixed_use` | Japanese Machiya Mixed Use | -- | commercial_retail | Commercial/Mixed-Use |
| 41 | `eco_urban_bioclimatic_block` | Eco-Urban Bioclimatic Block | -- | residential_multifamily | Residential |
| 42 | `vertical_forest_residential` | Vertical Forest Residential | -- | residential_highrise | Residential |
| 43 | `coastal_resort_terrace_block` | Coastal / Resort Terrace Block | -- | mixed_use | Commercial/Mixed-Use |
| 44 | `coastal_breezeway_mixed_use` | Coastal Breezeway Mixed Use | -- | commercial_retail | Commercial/Mixed-Use |
| 45 | `custom_prompt_ready_archetype` | Custom Prompt-Ready Archetype | -- | *(none)* | Custom/Other |
| 46 | `custom_contextual_experiment` | Custom Contextual Experiment | -- | *(none)* | Custom/Other |
| 47 | `community_recreation_centre` | Community Recreation Centre | -- | recreational_centre | Recreation |
| 48 | `modern_sports_arena` | Modern Sports Arena | -- | sports_arena | Entertainment/Culture |
| 49 | `boutique_hotel_tower` | Boutique Hotel | -- | hotel | Hospitality |
| 50 | `neoclassical_institutional` | Neoclassical Institutional | -- | institutional | Civic/Institutional |
| 51 | `brutalist_institutional` | Brutalist Institutional | -- | institutional | Civic/Institutional |
| 52 | `contemporary_civic` | Contemporary Civic | classic | institutional | Civic/Institutional |
| 53 | `art_deco_healthcare` | Art Deco Healthcare | -- | institutional_health | Healthcare |
| 54 | `functionalist_healthcare` | Functionalist Healthcare | -- | institutional_health | Healthcare |
| 55 | `biophilic_healthcare` | Biophilic Modern Healthcare | -- | institutional_health | Healthcare |
| 56 | `daylight_factory` | Daylight Factory | -- | industrial_light | Industrial |
| 57 | `industrial_park_modernism` | Industrial Park Modernism | -- | industrial_light | Industrial |
| 58 | `art_deco_industrial` | Art Deco Industrial | -- | industrial_light | Industrial |
| 59 | `functionalist_brick_industrial` | Functionalist Brick Industrial | -- | industrial | Industrial |
| 60 | `structural_expressionism_industrial` | Structural Expressionism Industrial | -- | industrial | Industrial |
| 61 | `corrugated_vernacular_industrial` | Corrugated Vernacular Industrial | -- | industrial | Industrial |
| 62 | `machine_aesthetic_heavy_industrial` | Machine Aesthetic Heavy Industrial | -- | industrial_heavy | Industrial |
| 63 | `brutalist_utility_heavy_industrial` | Brutalist Utility Heavy Industrial | -- | industrial_heavy | Industrial |
| 64 | `early_20c_megastructure_industrial` | Early 20th Century Megastructure | -- | industrial_heavy | Industrial |
| 65 | `romanesque_revival_warehouse` | Romanesque Revival Warehouse | -- | industrial_warehouse | Industrial |
| 66 | `midcentury_distribution_warehouse` | Mid-Century Distribution Warehouse | -- | industrial_warehouse | Industrial |
| 67 | `modern_bigbox_warehouse` | Modern Big-Box Logistics | -- | industrial_warehouse | Industrial |
| 68 | `parkitecture_recreational` | Parkitecture | -- | recreational | Recreation |
| 69 | `civic_modernism_rec_centre` | Civic Modernism Rec Centre | -- | recreational_centre | Recreation |
| 70 | `postmodern_rec_centre` | Postmodern Community Rec Centre | -- | recreational_centre | Recreation |
| 71 | `contemporary_sustainable_rec_centre` | Contemporary Sustainable Rec Centre | classic | recreational_centre | Recreation |
| 72 | `monumental_antiquity_arena` | Monumental Antiquity Arena | -- | sports_arena | Entertainment/Culture |
| 73 | `high_tech_arena` | High-Tech Structural Arena | -- | sports_arena | Entertainment/Culture |
| 74 | `concrete_megastructure_arena` | Concrete Megastructure Arena | -- | sports_arena | Entertainment/Culture |
| 75 | `chateauesque_hotel` | Chateauesque / Grand Railway Hotel | -- | hotel | Hospitality |
| 76 | `resort_modernism_hotel` | Resort Modernism Hotel | -- | hotel | Hospitality |
| 77 | `corporate_tower_hotel` | Corporate Tower Hotel | -- | hotel | Hospitality |
| 78 | `historic_grand_station` | Historic Grand Station | -- | institutional | Transportation |
| 79 | `contemporary_transit_hub` | Contemporary Transit Hub | classic | institutional | Transportation |
| 80 | `urban_light_rail_stop` | Urban Light Rail Stop | -- | institutional | Transportation |
| 81 | `climbing_wall_building` | Climbing Wall Building | -- | recreational | Recreation |
| 82 | `waste_to_energy_plant` | Waste-to-Energy Plant | -- | industrial | Energy/Infrastructure |
| 83 | `senior_living_complex` | Senior Living Complex | -- | residential_multifamily | Residential (or Healthcare) |
| 84 | `brewery_distillery` | Brewery / Distillery | -- | commercial_retail | Commercial/Mixed-Use |
| 85 | `solar_farm_agrivoltaics` | Solar Farm / Agrivoltaics | -- | industrial | Energy/Infrastructure |
| 86 | `immersive_experience_venue` | Immersive Experience Venue | -- | recreational | Entertainment/Culture |
| 87 | `modern_fire_station` | Modern Fire Station | -- | institutional | Civic/Institutional |
| 88 | `concert_hall_modern` | Concert Hall (Modern) | -- | recreational | Entertainment/Culture |
| 89 | `vertiport_evtol` | Vertiport / eVTOL Facility | -- | institutional | Transportation |
| 90 | `shophouse_southeast_asian` | Shophouse (Southeast Asian) | singapore | commercial_retail | Commercial/Mixed-Use |
| 91 | `food_hall_market_hall` | Food Hall / Market Hall | -- | commercial_retail | Commercial/Mixed-Use |
| 92 | `ev_charging_hub` | EV Charging Hub / Mobility Station | -- | industrial | Energy/Infrastructure |
| 93 | `hyperscale_data_center` | Hyperscale Data Center | -- | industrial | Energy/Infrastructure |
| 94 | `vertical_farm` | Vertical Farm / Indoor Agriculture | -- | industrial | Agriculture |
| 95 | `mall_redevelopment` | Mall Redevelopment | -- | mixed_use | Commercial/Mixed-Use |
| 96 | `terraced_stepped_building` | Terraced / Stepped Building | -- | residential_multifamily | Residential |
| 97 | `parisian_corner_dome` | Parisian Corner with Dome | paris | mixed_use | Commercial/Mixed-Use |
| 98 | `parisian_hotel_particulier` | Hotel Particulier | paris | residential_luxury | Residential |
| 99 | `parisian_passage_couvert` | Passage Couvert | paris | commercial_retail | Commercial/Mixed-Use |
| 100 | `parisian_marche_couvert` | Marche Couvert | paris | commercial_market | Commercial/Mixed-Use |
| 101 | `parisian_grand_magasin` | Grand Magasin | paris | commercial_retail | Commercial/Mixed-Use |
| 102 | `parisian_cafe_brasserie` | Parisian Cafe Brasserie | paris | mixed_use | Commercial/Mixed-Use |
| 103 | `parisian_ecole` | Ecole Republicaine | paris | institutional_education | Education |
| 104 | `parisian_marais_building` | Pre-Haussmann Marais Building | paris | residential_apartment | Residential |
| 105 | `amsterdam_neck_gable` | Amsterdam Neck Gable House | amsterdam | residential_apartment | Residential |
| 106 | `amsterdam_step_gable` | Amsterdam Step Gable House | amsterdam | residential_apartment | Residential |
| 107 | `amsterdam_bell_gable` | Amsterdam Bell Gable House | amsterdam | residential_apartment | Residential |
| 108 | `amsterdam_cornice_house` | Amsterdam Cornice House | amsterdam | residential_apartment | Residential |
| 109 | `amsterdam_pakhuis` | Amsterdam Canal Warehouse | amsterdam | residential_loft | Residential |
| 110 | `amsterdam_hofje` | Amsterdam Hofje | amsterdam | residential_social | Residential |
| 111 | `amsterdam_school_housing` | Amsterdam School Housing | amsterdam | residential_social | Residential |
| 112 | `amsterdam_brown_cafe` | Amsterdam Brown Cafe | amsterdam | commercial_hospitality | Hospitality |
| 113 | `amsterdam_jordaan_house` | Amsterdam Jordaan House | amsterdam | residential_apartment | Residential |
| 114 | `amsterdam_spout_gable` | Amsterdam Spout Gable House | amsterdam | residential_apartment | Residential |
| 115 | `barcelona_eixample_block` | Eixample Apartment Block | barcelona | mixed_use | Commercial/Mixed-Use |
| 116 | `barcelona_modernisme_casa` | Modernisme Casa | barcelona | residential_luxury | Residential |
| 117 | `barcelona_xamfra` | Barcelona Corner Chamfer | barcelona | mixed_use | Commercial/Mixed-Use |
| 118 | `barcelona_mercat` | Barcelona Mercat | barcelona | commercial_market | Commercial/Mixed-Use |
| 119 | `barcelona_townhouse` | Barcelona Townhouse | barcelona | residential_apartment | Residential |
| 120 | `barcelona_taller` | Barcelona Modernist Workshop | barcelona | commercial_workshop | Commercial/Mixed-Use |
| 121 | `london_georgian_terrace` | Georgian Terrace House | london | residential_townhouse | Residential |
| 122 | `london_regency_terrace` | Regency Stucco Terrace | london | residential_luxury | Residential |
| 123 | `london_victorian_terrace` | Victorian Bay-Window Terrace | london | residential_apartment | Residential |
| 124 | `london_mews` | London Mews House | london | residential_townhouse | Residential |
| 125 | `london_crescent` | London Crescent Terrace | london | residential_luxury | Residential |
| 126 | `london_townhouse` | London Townhouse | london | residential_luxury | Residential |
| 127 | `newyork_cast_iron` | SoHo Cast-Iron Loft Building | new_york | commercial_loft | Commercial/Mixed-Use |
| 128 | `newyork_art_deco` | New York Art Deco Tower | new_york | mixed_use | Commercial/Mixed-Use |
| 129 | `newyork_prewar` | New York Pre-War Apartment | new_york | residential_apartment | Residential |
| 130 | `newyork_tenement` | New York Walk-Up Tenement | new_york | residential_apartment | Residential |
| 131 | `montreal_triplex` | Montreal Plateau Triplex | montreal | residential_triplex | Residential |
| 132 | `montreal_duplex` | Montreal Duplex | montreal | residential_duplex | Residential |
| 133 | `montreal_limestone_commercial` | Old Montreal Limestone Commercial | montreal | commercial_heritage | Commercial/Mixed-Use |
| 134 | `montreal_depanneur` | Montreal Depanneur | montreal | commercial_retail | Commercial/Mixed-Use |
| 135 | `montreal_warehouse_loft` | Old Montreal Warehouse Loft | montreal | residential_loft | Residential |
| 136 | `montreal_mile_end_triplex` | Mile End Cultural Triplex | montreal | residential_triplex | Residential |
| 137 | `montreal_second_empire` | Montreal Second Empire Civic | montreal | institutional_civic | Civic/Institutional |
| 138 | `vancouver_special` | Vancouver Special | vancouver | residential_house | Residential |
| 139 | `vancouver_laneway` | Vancouver Laneway House | vancouver | residential_laneway | Residential |
| 140 | `vancouver_gastown` | Gastown Heritage Commercial | vancouver | commercial_heritage | Commercial/Mixed-Use |
| 141 | `vancouver_craftsman` | Vancouver Craftsman Bungalow | vancouver | residential_house | Residential |
| 142 | `vancouver_tower_podium` | Vancouverism Tower-Podium | vancouver | residential_condo | Residential |
| 143 | `vancouver_skytrain_station` | SkyTrain Elevated Station | vancouver | transit_station | Transportation |
| 144 | `toronto_bay_and_gable` | Toronto Bay-and-Gable House | toronto | residential_townhouse | Residential |
| 145 | `toronto_annex_mansion` | Toronto Annex Mansion | toronto | residential_luxury | Residential |
| 146 | `toronto_rowhouse` | Toronto Brick Rowhouse | toronto | residential_townhouse | Residential |
| 147 | `toronto_junction_industrial` | Toronto Junction Converted Industrial | toronto | commercial_creative | Commercial/Mixed-Use |
| 148 | `toronto_edwardian` | Toronto Edwardian Foursquare | toronto | residential_house | Residential |
| 149 | `toronto_streetcar_stop` | Toronto Streetcar Platform Stop | toronto | transit_stop | Transportation |
| 150 | `toronto_condo_tower` | Toronto Condo Podium Tower | toronto | residential_condo | Residential |
| 151 | `calgary_sandstone` | Calgary Sandstone Heritage | calgary | commercial_heritage | Commercial/Mixed-Use |
| 152 | `calgary_inglewood` | Inglewood Heritage Brick Commercial | calgary | commercial_heritage | Commercial/Mixed-Use |
| 153 | `calgary_plus15_tower` | Calgary Plus-15 Connected Tower | calgary | commercial_office | Commercial/Mixed-Use |
| 154 | `calgary_beltline_midrise` | Calgary Beltline Mid-Rise | calgary | mixed_use | Commercial/Mixed-Use |
| 155 | `calgary_bungalow` | Calgary Inner-City Bungalow | calgary | residential_house | Residential |
| 156 | `calgary_modern_infill` | Calgary Modern Infill House | calgary | residential_house | Residential |
| 157 | `calgary_ctrain_station` | Calgary CTrain Station | calgary | transit_station | Transportation |
| 158 | `calgary_central_library` | Calgary New Central Library | calgary | institutional_cultural | Civic/Institutional |
| 159 | `halifax_hydrostone` | Hydrostone Neighbourhood House | halifax | residential_house | Residential |
| 160 | `halifax_waterfront_warehouse` | Halifax Waterfront Warehouse | halifax | commercial_heritage | Commercial/Mixed-Use |
| 161 | `halifax_clapboard_row` | Halifax Painted Clapboard Row | halifax | residential_townhouse | Residential |
| 162 | `halifax_georgian` | Halifax Georgian Colonial | halifax | institutional_heritage | Civic/Institutional |
| 163 | `halifax_commercial` | Halifax Maritime Commercial | halifax | commercial_heritage | Commercial/Mixed-Use |
| 164 | `halifax_ferry_terminal` | Halifax Ferry Terminal | halifax | transit_station | Transportation |
| 165 | `newyork_bodega` | New York Corner Bodega | new_york | commercial_retail | Commercial/Mixed-Use |
| 166 | `vancouver_west_end_tower` | West End Mid-Century Tower | vancouver | residential_apartment | Residential |

---

## 8. Summary of Proposed Category Distribution

| Proposed Category | Count | % of Total |
|---|---|---|
| Residential | 55 | 33.1% |
| Commercial/Mixed-Use | 42 | 25.3% |
| Industrial | 12 | 7.2% |
| Civic/Institutional | 12 | 7.2% |
| Transportation | 8 | 4.8% |
| Entertainment/Culture | 7 | 4.2% |
| Recreation | 6 | 3.6% |
| Hospitality | 5 | 3.0% |
| Energy/Infrastructure | 4 | 2.4% |
| Healthcare | 4 | 2.4% |
| Education | 3 | 1.8% |
| Custom/Other | 2 | 1.2% |
| Agriculture | 1 | 0.6% |
| Bridges/Infrastructure | 0 | 0.0% |
| **Total** | **166** | **100%** |
