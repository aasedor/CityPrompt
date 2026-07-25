# Building Taxonomy Research

Research into how professional tools, building codes, and architecture firms categorize building types. The goal is to propose a **function-based building taxonomy** for SiteForge that complements the existing **style-based** archetype categories.

---

## 1. IBC (International Building Code) Occupancy Classifications

The 2024 IBC defines **10 major occupancy groups** (Chapter 3). These classifications drive fire safety, egress, and construction type requirements.

| Group | Name | Sub-groups | Examples |
|-------|------|------------|----------|
| A | Assembly | A-1 through A-5 | Theaters (A-1), restaurants/bars (A-2), churches/libraries/museums (A-3), indoor arenas (A-4), outdoor stadiums (A-5) |
| B | Business | -- | Offices, banks, courthouses, higher education, outpatient clinics |
| E | Educational | -- | K-12 schools, daycare (>5 children over 2.5 yrs) |
| F | Factory/Industrial | F-1, F-2 | Manufacturing, assembly plants, workshops (F-1 moderate hazard, F-2 low hazard) |
| H | High Hazard | H-1 through H-5 | Explosives, flammable materials, health hazards, labs |
| I | Institutional | I-1 through I-4 | Assisted living (I-1), hospitals/jails (I-2), prisons (I-3), daycare (I-4) |
| M | Mercantile | -- | Retail stores, markets, department stores, drug stores |
| R | Residential | R-1 through R-4 | Hotels/motels (R-1), apartments (R-2), single/two-family homes (R-3), care/assisted living (R-4) |
| S | Storage | S-1, S-2 | Warehouses, parking garages (S-1 combustible, S-2 non-combustible) |
| U | Utility/Misc | -- | Agricultural buildings, carports, sheds, fences, tanks |

**Key takeaway:** IBC is organized purely by *occupancy risk and safety*, not by architectural function or urban role. It collapses many distinct building types into broad groups (e.g., libraries and churches both fall under A-3). Useful as a safety cross-reference, but too coarse for a design taxonomy.

Sources: [ICC Digital Codes - IBC Chapter 3](https://codes.iccsafe.org/content/IBC2024P1/chapter-3-occupancy-classification-and-use), [NFSA Occupancy Classifications](https://nfsa.org/2024/01/08/occupancy-classifications-in-the-ibc/), [UpCodes IBC 2024](https://up.codes/viewer/general-services-administration/ibc-2024/chapter/3/occupancy-classification-and-use)

---

## 2. Urban Planning / Zoning Land-Use Categories

### US Standard: APA Land Based Classification Standards (LBCS)

The American Planning Association's LBCS classifies land across **5 dimensions**:
- **Activity** (what observably happens: farming, shopping, manufacturing)
- **Function** (economic type of establishment)
- **Structure Type** (physical building form: single-family house, warehouse, hospital)
- **Site Development Character** (overall site: park, undeveloped, built-up)
- **Ownership** (public, private, non-profit)

### Typical US/Canadian Municipal Zoning Categories

| Zone | Description | Sub-types |
|------|-------------|-----------|
| R (Residential) | Housing | R-1 single-family, R-2 duplex, R-3 triplex/fourplex, R-4 medium multi-family, R-5 high-density, R-A rural |
| C (Commercial) | Business, retail, services | C-1 neighborhood, C-2 community, C-3 regional/highway, C-4 central business |
| I (Industrial) | Manufacturing, warehousing | I-1 light industrial, I-2 heavy industrial |
| A (Agricultural) | Farming, rural | A-1 general, A-2 reserve |
| MU (Mixed-Use) | Combined residential/commercial | MU-R residential-dominant, MU-C commercial-dominant |
| OS (Open Space) | Parks, recreation, natural areas | -- |
| IN (Institutional) | Public facilities | Schools, hospitals, government |

### Canadian Variations

- Toronto has 30+ residential zoning sub-classifications (RD, RS, RT zones)
- Alberta uses Agricultural (AG), Country Residential (CR), Hamlet Residential (HR) zones
- All provinces follow the same basic R/C/I/A framework but with municipal variation

**Key takeaway:** Zoning is fundamentally about *permitted land use and density*, not building design. It maps well to a top-level functional taxonomy but lacks the granularity needed for architectural subtypes. The "mixed-use" and "overlay" concepts are relevant to SiteForge.

Sources: [APA LBCS Standards](https://www.planning.org/lbcs/standards/), [Canadian Encyclopedia - Zoning](https://www.thecanadianencyclopedia.ca/en/article/zoning), [Ontario Zoning Guide](https://www.ontario.ca/document/citizens-guide-land-use-planning/zoning-bylaws), [Toronto Zoning By-law](https://www.toronto.ca/zoning/bylaw_amendments/ZBL_NewProvision_Chapter1_40.htm)

---

## 3. Architecture Firm Project Categorization

### Gensler (world's largest firm, 33 practice areas)

Organizes into 4 macro-sectors:
- **Work**: Offices, Professional Services, Workplace
- **Lifestyle**: Hospitality, Retail, Sports, Entertainment, Mixed-Use Districts
- **Community**: Education, Planning/Urban Design, Airports/Aviation, Government, Residential/Multifamily, Industrial/Logistics, Mission-Critical Facilities/Data Centers
- **Health**: Healthcare, Senior Living, Sciences/Life Sciences

Source: [Gensler Projects](https://www.gensler.com/projects), [Gensler Services](https://www.gensler.com/services)

### BIG (Bjarke Ingels Group)

Organized under the "BIG LEAP" framework (Landscape, Engineering, Architecture, Planning, Products):
- **Architecture sub-categories**: Culture, Education, Work, Hospitality, Residential, Infrastructure, Space, Sports, Health
- **Landscape sub-categories**: Civic Spaces, Parks, Gardens, Balconies/Terraces
- **Also**: Mobility, Interiors, Products

Source: [big.dk](https://big.dk/)

### Foster + Partners

Major project sectors:
- Airports and transport hubs
- Office towers and headquarters
- Cultural buildings and museums
- Residential developments
- Bridges and infrastructure
- Retail and hospitality
- Industrial design
- Stadiums and sports venues

Source: [Foster + Partners Projects](https://www.fosterandpartners.com/projects/)

### MVRDV

Three core pillars: Architecture, Urbanism, Research. Project types span:
- Housing, Cultural buildings, Libraries, Government buildings
- Stores, Shopping centres, Mixed-use "hybrid" buildings
- Masterplans and urban strategies

Source: [MVRDV Portfolio](https://www.mvrdv.com/projects/portfolio)

### ArchDaily Categories (industry standard)

Extensive taxonomy including: Residential, Commercial, Cultural, Educational, Healthcare, Industrial, Religious, Civic, Sports, Transportation, Hotels, Offices, Retail, Mixed-Use, and many more.

Source: [ArchDaily Projects](https://www.archdaily.com/search/projects)

**Key takeaway:** Firms consistently use function-based categories (Residential, Commercial, Cultural, etc.) rather than style-based. BIG and Gensler add "Infrastructure" and "Mobility" as distinct categories. Mixed-use is always present. The firm categories align well with what architecture students already know.

---

## 4. GIS / Mapping Tools

### OpenStreetMap `building=*` Tags

OSM classifies buildings by both physical type and use. The Overture Maps schema groups OSM tags into:

| Category | Tag Values |
|----------|------------|
| Residential | apartments, house, residential, detached, semidetached_house, terrace, bungalow, cabin, dormitory, farm, houseboat, static_caravan |
| Commercial | commercial, hotel, kiosk, marketplace, office, restaurant, retail, shop, supermarket, warehouse |
| Civic | civic, fire_station, government, government_office, public |
| Education | college, kindergarten, school, university |
| Religious | cathedral, chapel, church, mosque, religious, shrine, synagogue, temple |
| Entertainment | grandstand, pavilion, sports_centre, sports_hall, stadium |
| Industrial | factory, industrial, manufacture |
| Agricultural | agricultural, barn, cowshed, farm, farm_auxiliary, glasshouse, greenhouse, silo, stable, sty |
| Healthcare | hospital |
| Transportation | train_station, transportation |
| Military | bunker, military |

Source: [OSM Key:building](https://wiki.openstreetmap.org/wiki/Key:building), [Overture Maps Building Schema](https://docs.overturemaps.org/schema/concepts/by-theme/buildings/)

### Google Maps Places API

Google organizes place types into these top-level categories:
- **Automotive**: car_dealer, car_rental, car_repair, gas_station, ev_charging_station, parking
- **Business**: (generic)
- **Culture**: (museums, galleries)
- **Education**: library, preschool, primary_school, secondary_school, university
- **Entertainment & Recreation**: amusement_park, aquarium, bowling_alley, casino, movie_theater, zoo, etc.
- **Financial**: bank, ATM
- **Food & Drink**: restaurant types, cafe, bar, bakery
- **Government**: city_hall, courthouse, embassy, post_office
- **Health & Wellness**: hospital, pharmacy, dentist, doctor
- **Lodging**: hotel, motel, campground
- **Shopping**: department_store, shopping_mall, grocery_store
- **Sports**: gym, swimming_pool, stadium
- **Transportation**: airport, bus_station, train_station, subway_station, transit_station

Source: [Google Places API Types](https://developers.google.com/maps/documentation/places/web-service/place-types)

**Key takeaway:** GIS/mapping tools use a flat, function-based taxonomy. Google's is the most granular. OSM distinguishes physical building form from function (which aligns with having separate "style" and "use" axes). Transportation and Agricultural appear as dedicated categories in both systems.

---

## 5. Game / Simulation Tools

### Cities: Skylines (I and II)

The core zoning model uses **4 zone types**:
- **Residential** (Low Density, Medium Density, High Density)
- **Commercial** (Low Density, High Density)
- **Industrial** (Generic, plus specializations: Agriculture, Forestry, Oil, Ore)
- **Office** (separate from Commercial)

Non-zoned "ploppable" buildings include:
- **Services**: Fire, Police, Healthcare, Education, Parks, Unique Buildings
- **Transportation**: Roads, Highways, Rail, Metro, Bus, Airports, Harbors
- **Utilities**: Power, Water, Sewage, Waste
- **Parks & Recreation**: Plazas, Parks, Nature Reserves
- **Monuments / Unique Buildings**: Landmarks, tourist attractions

Cities: Skylines II added **Mixed-Use** zoning and **Signature Buildings** (unique ploppable buildings with city-wide effects).

Source: [Cities: Skylines Wiki - Zoning](https://skylines.paradoxwikis.com/Zoning), [CS2 Feature Highlight](https://www.paradoxinteractive.com/games/cities-skylines-ii/features/zones-signature-buildings)

**Key takeaway:** The game's simplification is instructive. The 4-zone model (R/C/I/O) works for mass-generation but lacks the nuance SiteForge needs. The "ploppable" services/transport/utility distinction is useful: these are buildings users explicitly place rather than auto-generate. SiteForge is essentially a "ploppable-only" tool.

---

## 6. Synthesis: Cross-Reference Matrix

| Category | IBC | Zoning | Arch Firms | OSM | Google | Games |
|----------|-----|--------|------------|-----|--------|-------|
| Residential | R | R | Yes | Yes | (Lodging) | Yes |
| Commercial/Retail | M | C | Yes | Yes | Shopping | Yes |
| Office/Workplace | B | C | Yes | Yes | Business | Yes |
| Industrial | F | I | Yes | Yes | -- | Yes |
| Civic/Government | B/A | IN | Yes | Yes | Government | Services |
| Educational | E | IN | Yes | Yes | Education | Services |
| Healthcare | I | IN | Yes | Yes | Health | Services |
| Cultural/Arts | A | C/IN | Yes | -- | Culture | Unique |
| Hospitality/Lodging | R-1 | C | Yes | Yes | Lodging | -- |
| Religious | A-3 | IN | -- | Yes | -- | -- |
| Sports/Recreation | A-4,A-5 | OS/C | Yes | Yes | Sports | Parks |
| Transportation | -- | -- | Yes(BIG) | Yes | Transportation | Yes |
| Agriculture | U | A | -- | Yes | -- | Industry |
| Energy/Utilities | -- | -- | -- | -- | -- | Utilities |

---

## 7. Proposed Building Taxonomy for SiteForge

### Design Principles

1. **Function-first, style-second**: The current SiteForge categories (Parisian, Art Deco, etc.) describe *style*. This taxonomy describes *function/use*. Both axes coexist: a user picks a function (e.g., "School") and then a style (e.g., "Modernist").
2. **10-15 top-level categories**: Enough to cover all urban building types without overwhelming the UI.
3. **5-15 sub-types per category**: Specific enough to generate meaningful archetype cards.
4. **Intuitive for the audience**: Architecture students and urban planners already think in these categories.
5. **Includes user-requested types**: Transportation, Energy, Civic, Agriculture, Bridges.

### The Taxonomy (13 Top-Level Categories)

---

#### 1. RESIDENTIAL
Housing for people to live in.

| Sub-type | Description |
|----------|-------------|
| Single-Family Detached | Standalone house on its own lot |
| Semi-Detached / Duplex | Two attached units sharing a party wall |
| Rowhouse / Townhouse | Attached units in a continuous streetwall |
| Triplex / Fourplex | Small-scale stacked multi-family (walk-up) |
| Low-Rise Apartment | 3-5 storey multi-unit residential |
| Mid-Rise Apartment | 6-12 storey residential building |
| High-Rise Residential Tower | 13+ storey apartment or condo tower |
| Mixed-Use Residential | Residential above ground-floor retail or office |
| Courtyard Housing | Units arranged around a shared courtyard |
| Live-Work Unit | Combined residential and workspace |
| Laneway / Accessory Dwelling | Secondary suite or coach house |
| Student / Co-Living Housing | Dormitory or shared-living residence |
| Senior Living / Assisted Living | Age-restricted or care-supported housing |
| Social / Affordable Housing | Publicly subsidized or non-profit housing |

---

#### 2. COMMERCIAL & RETAIL
Buildings for selling goods and services.

| Sub-type | Description |
|----------|-------------|
| Corner Shop / Bodega | Small neighborhood retail (single storefront) |
| Main Street Shopfront | Traditional street-level retail in a mixed-use building |
| Department Store | Large multi-floor retail building |
| Shopping Mall / Centre | Enclosed multi-tenant retail complex |
| Big-Box Retail | Large single-storey retail warehouse (e.g., Costco) |
| Market Hall / Food Hall | Open-plan vendor hall for food or goods |
| Strip Mall / Power Centre | Auto-oriented grouped retail |
| Boutique Hotel / Shop | Small specialty retail or hospitality |
| Restaurant / Cafe | Standalone food-service building |
| Gas Station / Service Station | Fuel retail and convenience |
| Drive-Through Commercial | Auto-oriented fast-food or banking |

---

#### 3. OFFICE & WORKPLACE
Buildings for professional and administrative work.

| Sub-type | Description |
|----------|-------------|
| Low-Rise Office | 1-5 storey office building |
| Mid-Rise Office | 6-12 storey office building |
| Office Tower / High-Rise | 13+ storey commercial office tower |
| Corporate Campus / Headquarters | Multi-building corporate complex |
| Co-Working / Flex Space | Shared or serviced office building |
| Tech Campus | R&D-focused workplace with campus layout |
| Medical Office Building | Outpatient clinics and professional health offices |
| Creative / Studio Office | Converted or purpose-built creative workspace |
| Data Centre / Mission-Critical | Secure computing and server facilities |

---

#### 4. CIVIC & GOVERNMENT
Buildings serving public administration and democratic functions.

| Sub-type | Description |
|----------|-------------|
| City Hall / Town Hall | Municipal government seat |
| Courthouse | Judicial facility |
| Post Office | Mail and postal services |
| Embassy / Consulate | Diplomatic facility |
| Fire Station | Fire and emergency response |
| Police Station | Law enforcement facility |
| Community Centre | Multi-purpose public gathering space |
| Library | Public lending library |
| Government Office Building | Federal, provincial, or state administrative offices |
| Military / Defense Facility | Barracks, armory, or base buildings |
| Prison / Correctional Facility | Detention and incarceration |

---

#### 5. CULTURAL & INSTITUTIONAL
Buildings for arts, culture, heritage, and public life.

| Sub-type | Description |
|----------|-------------|
| Museum / Gallery | Art, history, or science exhibition space |
| Concert Hall / Performing Arts Centre | Live music and theater venue |
| Theater / Cinema | Movie theater or playhouse |
| Convention Centre | Large event and exhibition facility |
| Opera House | Dedicated opera and ballet venue |
| Cultural Centre | Multi-use arts and community programming |
| Archive / Special Library | Research and archival collections |
| Monument / Memorial | Commemorative public structure |
| Aquarium / Planetarium | Specialized public science exhibit |
| Religious Building | Church, mosque, synagogue, temple, shrine |

---

#### 6. EDUCATION & RESEARCH
Buildings for learning and knowledge production.

| Sub-type | Description |
|----------|-------------|
| Elementary / Primary School | K-6 education facility |
| Secondary / High School | Grades 7-12 education facility |
| University / College Building | Higher education lecture halls and departments |
| Daycare / Preschool | Early childhood care and education |
| Vocational / Technical School | Trade and skills training |
| Research Laboratory | Scientific research facility |
| University Library | Academic library building |
| Student Union / Campus Centre | Student services and social hub |
| Sports / Athletics Facility | Campus gymnasium, pool, or field house |

---

#### 7. HEALTHCARE
Buildings for medical treatment and wellness.

| Sub-type | Description |
|----------|-------------|
| Hospital | Full-service inpatient medical facility |
| Urgent Care / Walk-In Clinic | Minor emergency and after-hours care |
| Medical Centre / Polyclinic | Multi-specialty outpatient facility |
| Rehabilitation Centre | Physical therapy and recovery |
| Mental Health Facility | Psychiatric and counseling services |
| Dental Clinic | Oral health care |
| Veterinary Clinic | Animal healthcare |
| Pharmacy (Standalone) | Drug dispensary building |
| Long-Term Care / Nursing Home | Extended residential medical care |

---

#### 8. HOSPITALITY & LODGING
Buildings for temporary accommodation and tourism.

| Sub-type | Description |
|----------|-------------|
| Boutique Hotel | Small-scale distinctive hotel |
| Full-Service Hotel | Large hotel with amenities and conference |
| Resort Hotel | Destination hospitality with leisure facilities |
| Motel / Motor Lodge | Auto-oriented roadside accommodation |
| Hostel | Budget shared accommodation |
| Bed & Breakfast / Inn | Small owner-operated lodging |
| Conference / Convention Hotel | Hotel integrated with event facilities |
| Serviced Apartments | Extended-stay furnished units |
| Campground / Glamping Facility | Outdoor/semi-permanent lodging |

---

#### 9. INDUSTRIAL & PRODUCTION
Buildings for manufacturing, processing, and logistics.

| Sub-type | Description |
|----------|-------------|
| Light Industrial / Workshop | Small-scale fabrication and assembly |
| Heavy Industrial / Factory | Large-scale manufacturing plant |
| Warehouse / Distribution Centre | Storage and logistics hub |
| Brewery / Distillery / Winery | Beverage production facility |
| Food Processing Plant | Agricultural product processing |
| Lumber Mill / Sawmill | Timber processing |
| Printing / Publishing Facility | Media production |
| Self-Storage Facility | Consumer rental storage units |
| Waste Processing / Recycling Plant | Waste sorting and recovery |
| Water Treatment Plant | Municipal water processing |

---

#### 10. TRANSPORTATION & MOBILITY
Buildings and structures supporting movement of people and goods.

| Sub-type | Description |
|----------|-------------|
| Train Station / Rail Terminal | Intercity and commuter rail hub |
| Subway / Metro Station | Underground transit stop |
| Light Rail / Streetcar Stop | Surface transit platform and shelter |
| Bus Station / Transit Hub | Bus terminal or transfer point |
| Airport Terminal | Passenger air travel building |
| Ferry Terminal | Water transit passenger building |
| Parking Structure / Garage | Multi-level vehicle storage |
| Mobility Hub / Bike Station | Multimodal transfer with bike share/EV charging |
| Freight / Intermodal Terminal | Cargo transfer between rail, truck, ship |
| Toll Booth / Border Crossing | Vehicle checkpoint structure |
| Bridge (Pedestrian) | Footbridge or skyway |
| Bridge (Vehicular) | Road or rail bridge structure |
| Vertiport / eVTOL Facility | Urban air mobility landing pad |

---

#### 11. ENERGY & UTILITIES
Buildings and structures for power generation, distribution, and utility services.

| Sub-type | Description |
|----------|-------------|
| Solar Farm / Agrivoltaics | Photovoltaic array (ground-mounted or dual-use) |
| Wind Farm (on-site element) | Wind turbine cluster |
| Waste-to-Energy Plant | Incineration with energy recovery |
| Power Substation | Electrical distribution node |
| Hydroelectric Station | Water-powered generation facility |
| District Heating / Cooling Plant | Centralized thermal energy plant |
| EV Charging Hub | Dedicated electric vehicle charging facility |
| Telecommunications Tower | Cell tower or broadcast facility |
| Battery Storage Facility | Grid-scale energy storage |
| Hydrogen / Fuel Cell Station | Alternative fuel production/distribution |
| Pumping Station | Water or sewage pumping infrastructure |

---

#### 12. SPORTS & RECREATION
Buildings for organized sports, fitness, and leisure.

| Sub-type | Description |
|----------|-------------|
| Stadium (Outdoor) | Large open-air spectator venue |
| Arena (Indoor) | Enclosed spectator venue for sports and events |
| Recreation Centre / YMCA | Community fitness and pool facility |
| Gymnasium / Fitness Centre | Standalone gym or health club |
| Swimming Pool / Aquatic Centre | Public or competitive pool facility |
| Ice Rink / Hockey Arena | Ice sport facility |
| Tennis / Racquet Centre | Court sport complex |
| Climbing Gym / Adventure Centre | Indoor climbing and adventure sports |
| Golf Clubhouse | Course amenity building |
| Ski Lodge / Mountain Base | Alpine sports facility |
| Skate Park Pavilion | Shelter and amenity for skate parks |
| Fieldhouse / Indoor Track | Large indoor multi-sport building |

---

#### 13. AGRICULTURE & FOOD PRODUCTION
Buildings supporting farming, food growing, and related rural/urban agriculture.

| Sub-type | Description |
|----------|-------------|
| Barn / Farm Building | General agricultural storage and operations |
| Greenhouse / Nursery | Controlled-environment plant growing |
| Vertical Farm / Indoor Agriculture | Multi-storey or enclosed crop production |
| Grain Elevator / Silo | Bulk agricultural storage |
| Dairy / Livestock Facility | Animal husbandry building |
| Farmstand / Farm Market | Direct-to-consumer agricultural retail |
| Agricultural Processing Shed | Washing, packing, and sorting facility |
| Equestrian Centre / Stable | Horse boarding and riding facility |
| Aquaculture / Fish Farm | Fish and shellfish growing facility |
| Winery / Cidery Estate | Estate-based beverage production with tasting |
| Community Garden Pavilion | Shared urban garden amenity building |

---

### How This Taxonomy Integrates with SiteForge

The existing SiteForge archetype system uses **style categories** (Parisian, Art Deco, Modernist, etc.) to describe the visual language of buildings. This proposed taxonomy adds a **function axis**:

```
Building Archetype = Function (this taxonomy) x Style (existing categories)

Example:
  Function: "Elementary School" (Education & Research)
  Style:    "Modernist"
  Result:   A modernist elementary school archetype card
```

Each archetype card in the system would carry **both** tags:
- `category` (style): "modernist", "parisian", "art_deco", etc.
- `buildingType` (function): "elementary_school"
- `buildingCategory` (function group): "education_research"

This two-axis system lets users browse by either dimension:
- "Show me all schools" (filter by function)
- "Show me all Parisian buildings" (filter by style)
- "Show me Parisian schools" (filter by both)

### Coverage Verification

| User-Requested Category | Covered? | Location in Taxonomy |
|--------------------------|----------|----------------------|
| Transportation | Yes | Category 10 (13 sub-types) |
| Energy | Yes | Category 11 (11 sub-types) |
| Civic | Yes | Category 4 (11 sub-types) |
| Agriculture | Yes | Category 13 (11 sub-types) |
| Bridges | Yes | Category 10 sub-types (pedestrian + vehicular) |

### Summary Statistics

- **13 top-level categories**
- **139 total sub-types**
- Average of **10.7 sub-types per category**
- Range: 9 (Office, Healthcare, Hospitality) to 14 (Residential)

---

## Sources

### Building Codes
- [ICC Digital Codes - IBC 2024 Chapter 3](https://codes.iccsafe.org/content/IBC2024P1/chapter-3-occupancy-classification-and-use)
- [NFSA Occupancy Classifications](https://nfsa.org/2024/01/08/occupancy-classifications-in-the-ibc/)
- [UpCodes IBC 2024](https://up.codes/viewer/general-services-administration/ibc-2024/chapter/3/occupancy-classification-and-use)

### Zoning & Land Use
- [APA LBCS Standards](https://www.planning.org/lbcs/standards/)
- [Canadian Encyclopedia - Zoning](https://www.thecanadianencyclopedia.ca/en/article/zoning)
- [Ontario Zoning Guide](https://www.ontario.ca/document/citizens-guide-land-use-planning/zoning-bylaws)
- [Toronto Zoning By-law 569-2013](https://www.toronto.ca/zoning/bylaw_amendments/ZBL_NewProvision_Chapter1_40.htm)
- [Alberta Zoning System](https://albertatownandcountry.com/blog.html/alberta-land-zoning-system-explained-8801532)

### Architecture Firms
- [Gensler Projects](https://www.gensler.com/projects)
- [BIG Projects](https://big.dk/)
- [Foster + Partners Projects](https://www.fosterandpartners.com/projects/)
- [MVRDV Portfolio](https://www.mvrdv.com/projects/portfolio)
- [ArchDaily Projects](https://www.archdaily.com/search/projects)
- [Architectural Record Building Type Studies](https://www.architecturalrecord.com/topics/306-buildings-by-type)

### GIS & Mapping
- [OSM Key:building](https://wiki.openstreetmap.org/wiki/Key:building)
- [OSM Buildings Wiki](https://wiki.openstreetmap.org/wiki/Buildings)
- [Overture Maps Building Schema](https://docs.overturemaps.org/schema/concepts/by-theme/buildings/)
- [Google Places API Types](https://developers.google.com/maps/documentation/places/web-service/place-types)

### Games & Simulation
- [Cities: Skylines Wiki - Zoning](https://skylines.paradoxwikis.com/Zoning)
- [Cities: Skylines II - Zones & Signature Buildings](https://www.paradoxinteractive.com/games/cities-skylines-ii/features/zones-signature-buildings)
