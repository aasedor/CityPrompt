"""Compose 5 new Social / Event Space archetype entries as JSON-valid text.

Run:  python scripts/_compose_new_social_event.py
Output: scripts/_social_event_snippet.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def variant(vid, label, color, description, min_area, max_area, suggested_area, slug):
    return {
        "id": vid,
        "label": label,
        "color": color,
        "description": description,
        "thumbnailUrl": f"/archetypes/openspaces/{slug}/variant_{vid.split('_v')[-1]}.png",
        "minAreaSqm": min_area,
        "maxAreaSqm": max_area,
        "suggestedAreaSqm": suggested_area,
    }


def archetype(*, id, slug, title, description, tags, landscape_character,
              paving, planting, seating, water, openness, prompt_subject,
              prompt_details, prompt_negative, property_presets,
              variants_data, render_overlay, render_roof, render_negative,
              suggested_w, suggested_d, min_w, max_w, min_d, max_d,
              min_area, max_area, suggested_area, aspect_ratio, shape,
              space_type="plaza"):
    return {
        "id": id,
        "suggestedWidth_m": suggested_w,
        "suggestedDepth_m": suggested_d,
        "minWidth_m": min_w,
        "maxWidth_m": max_w,
        "minDepth_m": min_d,
        "maxDepth_m": max_d,
        "minAreaSqm": min_area,
        "maxAreaSqm": max_area,
        "aspectRatio": aspect_ratio,
        "shape": shape,
        "title": title,
        "aestheticCategory": "social_event_spaces",
        "spaceType": space_type,
        "description": description,
        "generationTags": tags,
        "styleProfile": {
            "landscapeCharacter": landscape_character,
            "pavingType": paving,
            "plantingType": planting,
            "seatingRealm": seating,
            "waterFeatures": water,
            "opennessEnclosure": openness,
        },
        "prompt": {
            "subject": prompt_subject,
            "details": prompt_details,
            "negative": prompt_negative,
        },
        "propertyPresets": property_presets,
        "suggestedAreaSqm": suggested_area,
        "thumbnailUrl": f"/archetypes/openspaces/{slug}/variant_0.png",
        "variants": variants_data,
        "renderPrompt": {
            "mapOverlay": render_overlay,
            "roofView": render_roof,
            "negative": render_negative,
        },
        "districtKit": None,
    }


# ---------------------------------------------------------------------------
# 1) Concert Pavilion Lawn
# ---------------------------------------------------------------------------
concert_pavilion_lawn = archetype(
    id="concert_pavilion_lawn",
    slug="concert-pavilion-lawn",
    title="Concert Pavilion Lawn",
    description="A purpose-built outdoor concert venue with a permanent stage shell or pavilion at one end and a sloped grass lawn for audience seating, used for symphony concerts, festivals, and outdoor performances",
    tags=["park", "concert-venue", "pavilion", "lawn", "amphitheatre", "performance"],
    space_type="park",
    landscape_character=(
        "A concert pavilion lawn venue seen from drone altitude. The site is anchored at one "
        "narrow end by a permanent acoustic stage shell — a curved or arched architectural "
        "structure with a covered orchestra platform — facing outward across a fan-shaped "
        "expanse of mowed grass that slopes gently upward away from the stage as natural "
        "audience seating. Closer to the stage, a covered seating section under a canopy "
        "structure may provide premium ticketed seats. The lawn is bisected by a few "
        "low-key paved aisles for circulation. A perimeter belt of mature shade trees "
        "frames the lawn but is kept pruned not to block sightlines from the back. Service "
        "buildings (concession kiosks, washroom blocks, sound-and-lighting tents) cluster "
        "behind or to the side of the seating area. From above the venue reads as a fan-"
        "shaped grass slope with a distinctive shell or canopy at the focal apex and "
        "perimeter tree-belt enclosure."
    ),
    paving="Mowed grass lawn slope; paved aisles for circulation; concrete or stone stage platform",
    planting="Perimeter belt of mature shade trees pruned for sightlines; grass slope as the seating field",
    seating="Grass-lawn audience seating; optional covered premium seating section near the stage; benches along aisles",
    water="None inside the venue; possible decorative reflecting pool flanking the stage",
    openness="Strongly directional — open fan toward the stage with perimeter tree enclosure",
    prompt_subject="Aerial view of a concert pavilion lawn venue with permanent stage shell and fan-shaped sloped grass audience field",
    prompt_details=[
        "Permanent acoustic stage shell or pavilion at one narrow end of the venue",
        "Fan-shaped sloped mowed-grass audience lawn radiating from the stage",
        "Optional covered premium seating section closer to the stage",
        "Low-key paved aisles bisecting the lawn for circulation",
        "Perimeter belt of mature shade trees framing the lawn",
        "Service kiosks, washrooms, and sound-and-lighting infrastructure clustered behind the seating",
    ],
    prompt_negative=[
        "No flat amphitheatre — must clearly show fan-shaped sloped lawn",
        "No urban plaza hardscape filling the audience area",
        "No buildings on the audience field",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "medium",
        "tree_density": 0.35,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "perimeter_grove",
    },
    variants_data=[
        variant(
            "concert_pavilion_lawn_v0", "Forest Hills Tennis-Stadium Concert", "#A0826D",
            "Forest-Hills-style adapted-stadium concert venue, roughly 80 by 100 meters of historic horseshoe-shaped stadium converted into an outdoor concert venue. The original tiered concrete bleachers form the audience seating with a permanent stage at one end fitted into the open horseshoe end. The pitch infield serves as a standing/dancing pit for major shows. A small concession concourse rings the upper rim. Surrounding context shows a leafy historic outer-borough neighbourhood.",
            5000, 12000, 8000, "concert-pavilion-lawn"),
        variant(
            "concert_pavilion_lawn_v1", "Modern Stainless Wave Canopy", "#708090",
            "Modern stainless-steel wave-canopy concert venue, roughly 100 by 130 meters of sloped lawn fronted by a sweeping curved silver-grey stainless-steel wave-canopy stage shell over a covered premium-seat section. Lawn slopes upward in a clean geometric form to a low concrete service-and-concession backline. Two paved aisles divide the lawn into thirds. Surrounding context shows a contemporary suburban entertainment district with parking lots beyond.",
            12000, 25000, 18000, "concert-pavilion-lawn"),
        variant(
            "concert_pavilion_lawn_v2", "Tanglewood Timber Shed Pavilion", "#6B4423",
            "Tanglewood-style timber-shed concert pavilion, roughly 130 by 170 meters of broad fan-shaped grass lawn rising gently from a heritage timber-truss open-sided concert pavilion (the Shed) covering thousands of seats. The grass extends well beyond the Shed for general-admission lawn tickets. Mature beech and maple form the perimeter belt. A picnic-blanket overflow area at the far edge. Surrounding context shows a Berkshires-style cultural-music-festival rural setting.",
            25000, 40000, 32000, "concert-pavilion-lawn"),
        variant(
            "concert_pavilion_lawn_v3", "Hollywood-Bowl Shell Amphitheatre", "#8B7355",
            "Hollywood-Bowl-style massive concrete-shell amphitheatre, roughly 200 by 220 meters of sweeping fan-shaped seating descending toward a large iconic concentric-arch-shell stage. Concrete-and-wood bench seating fills the bowl with a designated picnic-lawn upper terrace beyond. Two large paved staircases funnel audience traffic. Service backstage area with white tents and trailers. Surrounding context shows a Los Angeles-style chaparral-canyon rural-amphitheatre setting with parking switchbacks below.",
            45000, 80000, 60000, "concert-pavilion-lawn"),
    ],
    render_overlay="Replace the colored zone with a photorealistic concert pavilion lawn venue. Permanent acoustic stage shell or pavilion at one narrow end. Fan-shaped sloped mowed-grass audience lawn radiating from the stage. Optional covered premium seating closer to the stage. Low-key paved aisles bisecting the lawn. Perimeter belt of mature shade trees. Service kiosks behind the seating. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon golden hour, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a concert pavilion lawn venue. Fan-shaped grass slope visible as a wedge-shaped pale-green field. Distinctive stage shell or canopy at the focal apex with a strong shadow shape. Perimeter tree-canopy belt. Service-building roof shapes behind the seating. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, flat amphitheatre, urban plaza filling audience area, buildings on the audience field",
    suggested_w=130, suggested_d=170, min_w=50, max_w=300, min_d=70, max_d=350,
    min_area=5000, max_area=80000, suggested_area=20000,
    aspect_ratio="1:1.3", shape="fan",
)


# ---------------------------------------------------------------------------
# 2) Food-Truck Plaza
# ---------------------------------------------------------------------------
food_truck_plaza = archetype(
    id="food_truck_plaza",
    slug="food-truck-plaza",
    title="Food-Truck Plaza",
    description="A semi-permanent or permanent paved plaza dedicated to food-truck dining — multiple truck bays, communal picnic seating, string-light overhead, and a shared service zone",
    tags=["plaza", "food-truck", "dining", "communal", "string-lights", "casual"],
    landscape_character=(
        "A food-truck dining plaza seen from drone altitude. The site is a paved rectangular "
        "plaza with a clearly demarcated row of food-truck bays along one or two edges — "
        "rectangular paint-marked stalls 8 by 4 meters with electrical and water service "
        "drops accessible at the back of each. The center of the plaza holds a dense field "
        "of communal picnic-table seating arranged in regular rows, mixed with bar-height "
        "counter tables along the edges. String-light catenary or festoon lighting hangs "
        "overhead supported by tall steel posts. Black-steel or galvanized planters with "
        "ornamental grasses and small accent trees punctuate the perimeter. A shared dish-"
        "return-and-service kiosk stands at one corner. From above the plaza reads as a "
        "regular striped pattern of picnic-table rows on a paved field, with the food-truck "
        "row reading as parked rectangles along the perimeter and string-light lines "
        "crossing overhead."
    ),
    paving="Concrete pavers, asphalt, or stamped-concrete plaza floor with paint-marked truck bays",
    planting="Black-steel planters with ornamental grasses and small accent trees at the perimeter",
    seating="Communal picnic-table rows, bar-height counter tables along the edges, string-light overhead",
    water="None — service-water drops to truck bays only",
    openness="Open plaza with edge enclosure by parked food trucks and perimeter planters",
    prompt_subject="Aerial view of a food-truck dining plaza with truck bays along the edges and dense communal picnic-table seating",
    prompt_details=[
        "Paved rectangular plaza floor with paint-marked food-truck bays along one or two edges",
        "5-10 food trucks parked in their bays along the perimeter",
        "Dense field of communal picnic tables in regular rows in the center",
        "Bar-height counter tables along selected edges",
        "String-light catenary or festoon lighting supported by tall steel posts",
        "Black-steel planters at the perimeter with ornamental grasses and accent trees",
    ],
    prompt_negative=[
        "No restaurant building inside the plaza (only trucks)",
        "No grass lawn dominating the floor",
        "No formal civic monument",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "low",
        "tree_density": 0.15,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "string_lights_overhead",
    },
    variants_data=[
        variant(
            "food_truck_plaza_v0", "Industrial-Lot Pop-Up", "#5C5C5C",
            "Industrial-lot pop-up food-truck plaza, roughly 30 by 40 meters of asphalt former-industrial-lot with six food trucks parked in a single line along one edge, exposed brick warehouse walls behind. A loose grid of cedar picnic tables fills the dining area with a few standing-height drum tables. Catenary string lights crisscross overhead supported by salvaged industrial poles. Two corten-steel planters anchor the corners. Surrounding context shows a converted-warehouse arts district.",
            500, 1500, 1000, "food-truck-plaza"),
        variant(
            "food_truck_plaza_v1", "Permanent Food-Truck Park", "#B8860B",
            "Permanent purpose-built food-truck park, roughly 50 by 40 meters of decorative-stamped-concrete plaza with eight dedicated truck bays along two edges (L-shaped), each with utility-drop service. Permanent restroom-and-service kiosk pavilion at one corner. Dense communal picnic seating fills the center. Black-steel planters with ornamental grasses and small honey-locust trees along the perimeter. String lights overhead. Surrounding context shows a contemporary mixed-use neighbourhood with mid-rise residential.",
            1500, 3000, 2200, "food-truck-plaza"),
        variant(
            "food_truck_plaza_v2", "Adaptive Parking-Lot Conversion", "#708090",
            "Adaptive parking-lot conversion food-truck plaza, roughly 60 by 50 meters of repainted-asphalt former-parking-lot with ten trucks distributed around the perimeter in former parking bays. Picnic tables fill former driving aisles in regular rows. A shared shaded-pergola dining area in the center. Single mature plane tree retained from the original lot. Surrounding context shows a downtown commercial district with mid-rise office buildings.",
            2500, 4000, 3200, "food-truck-plaza"),
        variant(
            "food_truck_plaza_v3", "Night-Market Truck Plaza", "#5B7065",
            "Night-market festival-style truck plaza, roughly 70 by 80 meters of paved festival ground hosting twelve to fifteen food trucks arranged in two parallel rows down the long axis with a wide central pedestrian aisle between. Long parallel runs of communal picnic tables on the sides. A small live-music stage at one short end. Strings of paper lanterns and festoon bulbs overhead. Surrounding context shows an urban festival-district setting near a transit station.",
            5000, 7500, 6500, "food-truck-plaza"),
    ],
    render_overlay="Replace the colored zone with a photorealistic food-truck dining plaza. Paved plaza floor with paint-marked truck bays along the edges. 5-15 food trucks parked in the bays. Dense field of communal picnic tables in the center. Bar-height counter tables along edges. String-light catenary overhead. Black-steel planters at perimeter. Surrounding mixed-use neighbourhood. Keep surrounding satellite map context exactly as-is. Oblique aerial view, evening golden-hour light, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a food-truck plaza. Striped pattern of picnic-table rows on a paved floor. Food-truck rectangles parked along the perimeter. String-light lines crossing overhead as faint diagonal shadows. Planter shapes at the corners. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, restaurant building inside plaza, grass lawn floor, formal civic monument",
    suggested_w=50, suggested_d=50, min_w=15, max_w=120, min_d=15, max_d=120,
    min_area=500, max_area=8000, suggested_area=2500,
    aspect_ratio="1:1", shape="rectangular",
)


# ---------------------------------------------------------------------------
# 3) Outdoor Cinema Lawn
# ---------------------------------------------------------------------------
outdoor_cinema_lawn = archetype(
    id="outdoor_cinema_lawn",
    slug="outdoor-cinema-lawn",
    title="Outdoor Cinema Lawn",
    description="A summer-evening outdoor movie venue — a single large projection screen at one end of a sloped grass lawn, audience on blankets and low chairs, sometimes a concession kiosk and projection booth",
    tags=["park", "outdoor-cinema", "movies", "summer", "lawn", "projection"],
    space_type="park",
    landscape_character=(
        "An outdoor cinema lawn venue seen from drone altitude. The site is anchored at one "
        "narrow end by a single oversized projection screen — a free-standing white "
        "rectangular surface roughly 12 meters wide and 7 meters tall — facing outward over "
        "a fan-shaped expanse of mowed lawn. The lawn slopes gently upward away from the "
        "screen. A small projection booth or projection cart sits about two-thirds back. "
        "A small concession kiosk pavilion (hot snacks, popcorn) is tucked at the side. The "
        "audience sits on blankets, picnic mats, low folding chairs, or scattered timber "
        "benches. A perimeter belt of mature trees encloses the lawn but stays well clear of "
        "the projection sightline. From above the venue reads as a clean rectangular grass "
        "field with the screen as a stark white slab at one narrow end and the projection-"
        "booth structure as a small rectangular shape at the back."
    ),
    paving="Mowed grass lawn; small paved pad for the screen support and projection booth",
    planting="Perimeter belt of mature trees framing the lawn but pruned for sightlines",
    seating="Audience sits on blankets, mats, and low folding chairs; scattered timber benches near the perimeter",
    water="None inside the venue",
    openness="Open directional fan toward the projection screen with perimeter tree enclosure",
    prompt_subject="Aerial view of an outdoor cinema lawn venue with a large projection screen at one end and a sloped grass audience field",
    prompt_details=[
        "Single oversized white-rectangular projection screen at one narrow end",
        "Fan-shaped sloped mowed-grass audience lawn facing the screen",
        "Audience on picnic blankets, low folding chairs, and scattered benches",
        "Small projection booth or cart about two-thirds back from the screen",
        "Small concession kiosk pavilion at the side",
        "Perimeter belt of mature trees framing the lawn",
    ],
    prompt_negative=[
        "No flat audience field — must clearly show fan-shape gentle slope",
        "No fixed bleacher seating",
        "No urban plaza hardscape inside the lawn",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "medium",
        "tree_density": 0.3,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "perimeter_grove",
    },
    variants_data=[
        variant(
            "outdoor_cinema_lawn_v0", "Pop-Up Festival Cinema", "#5B7065",
            "Pop-up festival-style outdoor cinema, roughly 30 by 50 meters of mowed-grass lawn with a temporary inflatable-frame screen at one end. A small folding-canopy projection booth sits midway back. A few rows of folding chairs at the front, blanket seating beyond. Strings of festoon bulbs overhead supported by temporary poles. Service tents and a small ticket kiosk at the entry. Surrounding context shows a city park hosting a summer festival with other festival tents nearby.",
            1000, 2500, 1800, "outdoor-cinema-lawn"),
        variant(
            "outdoor_cinema_lawn_v1", "Park-Lawn Projection", "#6B8A4A",
            "Park-lawn outdoor cinema venue, roughly 50 by 80 meters of permanent dedicated cinema lawn with a fixed steel-frame projection screen mounted on a stone-and-concrete plinth at the focal end. A small permanent timber-clad projection-and-storage booth sits at the back. Audience on a mix of picnic blankets, permanent timber benches at the front, and folding chairs. A picnic-lawn perimeter and concession kiosk to one side. Surrounding context shows a Picturesque-style urban park with mature trees.",
            3000, 6500, 4500, "outdoor-cinema-lawn"),
        variant(
            "outdoor_cinema_lawn_v2", "Drive-In Heritage Lot", "#708090",
            "Heritage-drive-in-lot outdoor cinema, roughly 70 by 100 meters of paved former-drive-in lot with a vintage white painted billboard-frame projection screen at the end and rows of car parking bays. A few classic-car-friendly low fences and pole-mounted speakers. A small mid-century concession booth in the center. Audience watches both from inside cars and on lawn chairs in the front lawn area. Surrounding context shows a rural-American open landscape edge.",
            6000, 9000, 7500, "outdoor-cinema-lawn"),
        variant(
            "outdoor_cinema_lawn_v3", "Rooftop Cinema Terrace", "#8B7355",
            "Rooftop outdoor cinema terrace, roughly 50 by 70 meters of timber-decked rooftop with a free-standing high-resolution LED-wall screen at one end. A bar counter with stools along the back edge, lounge-style daybed seating in the center, and bar-height counter tables along the rim. String lights and small palm planters around the perimeter. Surrounding context shows a contemporary urban downtown with neighbouring high-rise rooftops and skyline beyond.",
            3500, 7000, 5000, "outdoor-cinema-lawn"),
    ],
    render_overlay="Replace the colored zone with a photorealistic outdoor cinema lawn venue. Single oversized projection screen at one narrow end. Fan-shaped sloped mowed-grass audience lawn. Audience on blankets, low chairs, and scattered benches. Small projection booth or cart back from the screen. Small concession kiosk to the side. Perimeter belt of mature trees. Surrounding park or urban context. Keep surrounding satellite map context exactly as-is. Oblique aerial view, late-afternoon to dusk light, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with an outdoor cinema lawn. Clean rectangular grass field with the screen as a stark white slab at one narrow end. Projection-booth small rectangle at the back. Perimeter tree-canopy circles. Surrounding context. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, fixed bleachers, urban plaza inside lawn",
    suggested_w=50, suggested_d=80, min_w=20, max_w=120, min_d=30, max_d=150,
    min_area=1000, max_area=10000, suggested_area=4000,
    aspect_ratio="1:1.6", shape="rectangular",
)


# ---------------------------------------------------------------------------
# 4) Night Market
# ---------------------------------------------------------------------------
night_market = archetype(
    id="night_market",
    slug="night-market",
    title="Night Market",
    description="A semi-permanent or permanent night-time market plaza — covered or partially-covered stall rows, hawker food kiosks, festoon lighting, lanterns, and dense communal seating",
    tags=["plaza", "night-market", "hawker", "food", "lanterns", "covered-stalls"],
    landscape_character=(
        "A night-market plaza seen from drone altitude. The plaza is paved as a rectangular "
        "or L-shaped market hall, with two or three parallel rows of permanent or semi-"
        "permanent timber-and-corrugated-roof market stalls running along the long axis. "
        "Each stall is roughly 3 meters wide by 4 meters deep with a sloping shed-roof and "
        "an open frontage facing the central pedestrian aisle. The aisle between stall rows "
        "is filled with communal long-table dining seating, low stools, and standing-height "
        "counter tables. Festoon string lights, paper lanterns, or hanging lantern columns "
        "punctuate the overhead and add density to the canopy. Hawker food kiosks "
        "(ramen, dumpling, satay, taco, churro, mulled-wine) cluster at intervals along the "
        "stall rows. Service-and-cooking smoke-stack chimneys rise above the roofs. From "
        "above the market reads as a regular striped pattern of pitched-roof stall rows "
        "with crowded seating in the central aisles and a glowing field of lantern points."
    ),
    paving="Asphalt, concrete pavers, or stamped concrete market floor",
    planting="Minimal planting — small potted shrubs or palms at corners; cooking-herb planters at some food stalls",
    seating="Long communal dining tables, low stools, standing-height counter tables in the central aisles",
    water="None — service-water drops to food kiosks only",
    openness="Strongly enclosed by stall-row roofs along the long axis; open at the short ends",
    prompt_subject="Aerial view of a covered night-market plaza with parallel rows of pitched-roof market stalls and dense communal aisle seating",
    prompt_details=[
        "Two or three parallel rows of timber-and-corrugated-roof stalls along the long axis",
        "Communal long-table dining and standing-counter seating in the central aisles between stall rows",
        "Hawker food kiosks at intervals along the stall rows with cooking smoke",
        "Festoon string lights, paper lanterns, or hanging lantern columns dense overhead",
        "Service smoke-stack chimneys rising above the roof line",
        "Surrounding dense urban or street-vendor neighbourhood context",
    ],
    prompt_negative=[
        "No empty plaza without stall structure",
        "No formal civic monument",
        "No grass lawn floor",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "very_low",
        "tree_density": 0.05,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "stall_canopy",
    },
    variants_data=[
        variant(
            "night_market_v0", "Asian Hawker Stall Lane", "#6B4423",
            "Asian hawker-stall night market, roughly 25 by 60 meters of long narrow alley-style market with two parallel rows of small timber-and-tin-roof food stalls running its length. Each stall is brightly painted in red-and-yellow with hand-painted signage. Plastic stools and folding tables fill the central aisle for communal eating. Red paper lanterns hang in continuous strings overhead. Cooking woks, charcoal grills, and steamers visible at each stall. Surrounding context shows a dense Southeast Asian street-market neighbourhood with covered alley extensions.",
            500, 2000, 1200, "night-market"),
        variant(
            "night_market_v1", "European Christmas-Market Kiosks", "#5B7065",
            "European Christmas-market style night plaza, roughly 50 by 60 meters of cobblestone civic square hosting two rings of A-frame timber Christmas-market kiosks (~25 stalls) around the perimeter. Stalls sell mulled wine, sausages, gingerbread, and crafts. A tall lit Christmas tree at the centre. Snow-dusted evergreen garlands. Festoon lights overhead. Communal standing tables in the central plaza for eating. Surrounding context shows a historic European old town with limestone civic buildings.",
            2000, 4500, 3500, "night-market"),
        variant(
            "night_market_v2", "Latin-American Night Plaza", "#A0826D",
            "Latin-American night-market plaza, roughly 60 by 70 meters of patterned cobblestone plaza with three parallel rows of brightly-coloured awning-roofed food stalls under a partial canvas-tarp central canopy. Hawker stalls selling tacos, arepas, churros, fresh fruit, and aguas frescas. Long picnic tables in the wide central aisles. Mariachi or live-music stage at one end. Hanging metal-and-paper lanterns. Surrounding context shows a colonial Latin-American old-town centre.",
            4000, 7000, 5500, "night-market"),
        variant(
            "night_market_v3", "Modern Food-Hall Plaza", "#708090",
            "Modern food-hall plaza, roughly 80 by 90 meters of contemporary multi-cuisine night-market with a permanent steel-and-glass shed-roof structure spanning three parallel rows of designer kitchen counters and bar-height seating runs. Communal long tables fill the wide aisles. Strings of cluster pendant lighting overhead. A central full-service bar island. Beer-garden-style picnic patio extends out one short end. Surrounding context shows a contemporary urban food-and-arts district with mid-rise residential.",
            7500, 10000, 8500, "night-market"),
    ],
    render_overlay="Replace the colored zone with a photorealistic night market plaza. Two or three parallel rows of pitched-roof market stalls. Communal long-table dining and standing-counter seating in the central aisles. Hawker food kiosks at intervals with cooking smoke. Festoon string lights, paper lanterns, or hanging lantern columns dense overhead. Service smoke-stack chimneys rising above. Surrounding dense urban or street-vendor context. Keep surrounding satellite map context exactly as-is. Oblique aerial view, dusk to early-evening light, lantern glow, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a night market. Striped pattern of pitched-roof stall rows. Crowded seating shapes in the central aisles. Field of lantern-point glows. Smoke-stack chimney shadows. Surrounding context. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, empty plaza without stalls, formal civic monument, grass lawn floor",
    suggested_w=60, suggested_d=70, min_w=15, max_w=140, min_d=20, max_d=160,
    min_area=500, max_area=12000, suggested_area=4000,
    aspect_ratio="1:1.15", shape="rectangular",
)


# ---------------------------------------------------------------------------
# 5) Parade Ground
# ---------------------------------------------------------------------------
parade_ground = archetype(
    id="parade_ground",
    slug="parade-ground",
    title="Parade / Procession Ground",
    description="A long axial open ground designed for ceremonial processions, parades, military reviews, and large-scale civic gatherings — wide gravel allée or formal lawn esplanade with monumental terminations",
    tags=["plaza", "parade", "procession", "ceremonial", "axial", "esplanade"],
    landscape_character=(
        "A ceremonial parade ground seen from drone altitude. The site is a strongly axial "
        "open ground — a long wide rectangular allée of gravel, lawn, or stone paving "
        "running between two monumental terminations (a triumphal arch, palace facade, "
        "monument, or grand institutional building at each end). The ground is bordered on "
        "both long sides by paired allées of mature symmetrical sentinel trees (lime, plane, "
        "cypress, oak, or palm) and continuous low edge-curbs or balustrades. Stepped "
        "tribunes or reviewing-stand structures may flank one or both sides at the "
        "ceremonial midpoint. A few cross-axes appear at strategic points, intersected by "
        "small fountains, statues, or geometric paving features. The character is "
        "monumental, formal, and decisively symmetric. From above the parade ground reads "
        "as a long pale-coloured rectangular axis bordered by dark-green tree allées, with "
        "monumental terminations at each end."
    ),
    paving="Compacted gravel, mowed lawn, or formal stone paving running the full axial length",
    planting="Paired allées of mature symmetrical sentinel trees flanking both long sides",
    seating="Stone perimeter benches, stepped tribunes or reviewing stands at the ceremonial midpoint",
    water="Optional axial fountains or reflecting basins at cross-axis intersections",
    openness="Strongly axial linear ground with strong tree-allée enclosure on both long sides",
    prompt_subject="Aerial view of a long axial ceremonial parade ground bordered by paired tree allées and terminated by monumental architecture at each end",
    prompt_details=[
        "Long wide rectangular allée running the full ceremonial axis",
        "Monumental terminations at each end — arch, palace facade, monument, or institutional building",
        "Paired allées of mature symmetrical sentinel trees flanking both long sides",
        "Stepped tribunes or reviewing-stand structures at the ceremonial midpoint",
        "Optional axial fountains or reflecting basins at cross-axis intersections",
        "Surrounding monumental civic district context",
    ],
    prompt_negative=[
        "No casual park lawn with picnic furniture",
        "No urban plaza with retail",
        "No asymmetric planting or curving paths",
        "No text overlays",
    ],
    property_presets={
        "tree_density_level": "medium",
        "tree_density": 0.4,
        "has_paths": True,
        "has_benches": True,
        "shade_strategy": "paired_tree_allees",
    },
    variants_data=[
        variant(
            "parade_ground_v0", "Stadium-Fronted Civic Forecourt", "#708090",
            "Modern stadium-fronted civic forecourt parade ground, roughly 80 by 200 meters of broad stone-paver concourse running between a contemporary stadium entrance at one end and a transit-station entry plaza at the other. Two paired rows of plane trees in stone tree-pits run along the long edges. Cluster-pole stadium lighting masts mark the perimeter. A small flag-bearing plinth marks the midpoint. Surrounding context shows a contemporary sports-and-events district with mixed-use mid-rise framing the boulevard.",
            8000, 18000, 12000, "parade-ground"),
        variant(
            "parade_ground_v1", "The Mall London Gravel Allée", "#A0826D",
            "London-Mall-style ceremonial gravel allée, roughly 50 by 350 meters of pale buff compacted-gravel processional way running between a triumphal stone arch at one end and a royal palace forecourt with iron gates at the other. Paired rows of mature plane trees with continuous stone curb edges flank both sides. A bronze equestrian monument punctuates the gravel midway. Royal Parks fencing along the boundary. Surrounding context shows a London-style royal-civic district with neoclassical institutional buildings.",
            15000, 35000, 25000, "parade-ground"),
        variant(
            "parade_ground_v2", "Champ-de-Mars Lawn Esplanade", "#6B8A4A",
            "Champ-de-Mars-style formal lawn esplanade, roughly 100 by 500 meters of broad rectangular mowed-lawn esplanade running between a beaux-arts colonnade at one end and a great iron-tower monument at the other. Symmetric gravel paths flank the central lawn rectangles. Paired rows of clipped chestnut trees on each side. Several cross-axis stone benches and small classical fountains. Surrounding context shows a formal Parisian Haussmannian institutional district.",
            40000, 80000, 60000, "parade-ground"),
        variant(
            "parade_ground_v3", "National Mall Ceremonial Axis", "#7E9F5A",
            "Massive National-Mall-style ceremonial axis, roughly 150 by 1500 meters of vast formal lawn-and-gravel esplanade running between a domed neoclassical capitol at one end and a tall obelisk monument at the other. Symmetric long-and-wide lawn panels alternate with gravel cross-axis paths. Paired rows of mature American elms flank the central panels. Reflecting pool at the obelisk end. Multiple monumental institutional buildings flank both long sides. Surrounding context shows a national-capital ceremonial district.",
            120000, 250000, 180000, "parade-ground"),
    ],
    render_overlay="Replace the colored zone with a photorealistic ceremonial parade ground. Long wide rectangular allée running an axis. Monumental terminations at each end (arch, palace, monument, or institutional building). Paired allées of mature symmetrical trees flanking both long sides. Stepped tribunes or reviewing stands at the midpoint. Optional axial fountains. Surrounding monumental civic district context. Keep surrounding satellite map context exactly as-is. Oblique aerial view, midday or golden hour, sharp shadows, photorealistic, 8k.",
    render_roof="Replace the colored zone viewed from directly above with a ceremonial parade ground. Long pale rectangular axis bordered by dark-green tree-allée bands. Monumental termination footprints at each end. Cross-axis path intersections. Surrounding civic district. Keep surrounding context exactly as-is.",
    render_negative="cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors, casual park lawn with picnics, urban plaza with retail, asymmetric planting",
    suggested_w=100, suggested_d=400, min_w=30, max_w=200, min_d=80, max_d=1500,
    min_area=8000, max_area=250000, suggested_area=40000,
    aspect_ratio="1:4", shape="linear",
)


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------
all_archetypes = [concert_pavilion_lawn, food_truck_plaza, outdoor_cinema_lawn,
                  night_market, parade_ground]


def emit_snippet(archetypes: list[dict]) -> str:
    out_lines: list[str] = []
    for arch in archetypes:
        text = json.dumps(arch, indent=2, ensure_ascii=False)
        prefixed = "\n".join("    " + line for line in text.splitlines())
        out_lines.append(prefixed + ",")
    return "\n".join(out_lines)


def main() -> int:
    snippet = emit_snippet(all_archetypes)
    try:
        json.loads("[" + snippet.rstrip(",") + "]")
    except json.JSONDecodeError as e:
        print(f"ERROR: emitted snippet is not valid JSON: {e}")
        return 1

    out_path = Path(__file__).parent / "_social_event_snippet.json"
    out_path.write_text(snippet, encoding="utf-8")
    print(f"OK: wrote {len(snippet)} chars to {out_path}")
    print(f"Validates as JSON array of {len(all_archetypes)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
