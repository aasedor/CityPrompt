"""Ten finite, reference-informed street concepts; no production catalogue writes.

Widths are original ideation sections, not measured designs or engineering standards.
Every band is in metres; its name is unique within the cross-section.
"""
import copy


def spec(title, reference, bands, observed, adapted, pattern='stone', length=48):
    return dict(title=title, reference=reference, bands=bands, length_m=length,
                pattern=pattern, observed_features=observed, adapted_features=adapted)


STREETS = {
    'main_street': spec('Neighbourhood Main Street', 'neighborhood-main-street/hero.png',
        [('west_walk',3,'paving'),('west_furniture',3,'paving'),('west_parking',2.5,'asphalt'),
         ('road',6,'asphalt'),('east_parking',2.5,'asphalt'),('east_furniture',3,'paving'),('east_walk',3,'paving')],
        ['Traditional lamps, paired tree rows, parking bays and contrasting crossing paving'],
        ['Parallel parking replaces angled parking; a small planted parklet replaces one bay']),
    'cycle_avenue': spec('Protected Cycle Avenue', 'protected-bike-lane-bi-directional/variant_0.png',
        [('west_walk',3,'paving'),('west_furniture',2.5,'paving'),('cycle',4,'cycle'),
         ('separator',2,'soil'),('road',6,'asphalt'),('east_furniture',3.5,'paving'),('east_walk',3,'paving')],
        ['Two-way protected cycle track, planted divider and separate sidewalk'],
        ['Warm red cycle surfacing and kit furniture; right-hand cycle arrows']),
    'planted_lane': spec('Planted Service Lane', 'green-alley/hero.png',
        [('west_garden',2.5,'soil'),('shared_lane',7,'paving'),('east_garden',2.5,'soil')],
        ['Timber boundary fences, narrow planted edges and a continuous paved lane'],
        ['Generous concept lane, separate seating pockets, openings in fence at midblock'], 'brick',40),
    'transit_street': spec('Transit Stop Street', 'floating-bus-stop-transit-street/variant_0.png',
        [('west_walk',3,'paving'),('west_furniture',3.5,'paving'),('road',6,'asphalt'),
         ('island',3,'paving'),('cycle',3.5,'cycle'),('east_furniture',5,'paving'),('east_walk',3,'paving')],
        ['Glazed transit shelter, stop pole, waiting island and cycle crossing'],
        ['Flush concept island; shelter shifted behind clear boarding strip; no live routes or operational traffic design']),
    'market_street': spec('Pedestrian Market Street', 'pedestrian-only-street/hero.png',
        [('west_walk',2.5,'paving'),('west_furniture',4,'paving'),('promenade',5,'paving'),
         ('east_furniture',4,'paving'),('east_walk',2.5,'paving')],
        ['Cobbled pedestrian space, fountain, cafe seating, planters and traditional lamps'],
        ['Side-bay fountain keeps the centre clear; striped market stalls extend the cafe programme'], 'cobble'),
    'green_alley': spec('Ruelle Verte Community Alley', 'montreal-ruelle-verte-green-alley/hero.png',
        [('west_garden',3,'paving'),('shared_lane',5,'paving'),('east_garden',3,'paving')],
        ['Raised timber planters, vines, small trees and community seating'],
        ['Freestanding planted trellises instead of invented neighbouring walls; firm paver route instead of grass-grid surface'], 'brick',40),
    'heritage_mews': spec('Heritage Mews Lane', 'london-mews-lane/hero.png',
        [('west_furniture',2,'paving'),('shared_lane',6,'paving'),('east_furniture',2,'paving')],
        ['Small-scale cobbled lane, lanterns and individual frontage planters'],
        ['Freestanding lanterns stand in for facade-mounted lights; building facades are omitted'], 'cobble',40),
    'boardwalk': spec('Waterfront Timber Boardwalk', 'halifax-waterfront-boardwalk/hero.png',
        [('water_edge',1,'paving'),('lounge',3.5,'paving'),('promenade',4,'paving'),
         ('east_furniture',3.5,'paving')],
        ['Timber decking, waterside guard, suspended hammocks and cafe furniture'],
        ['Level deck fixture with explicit open ends; no invented water or surrounding buildings'], 'deck'),
    'school_street': spec('Playful School Street', 'school-street/variant_0.png',
        [('west_walk',2.5,'paving'),('west_furniture',3.5,'paving'),('play_lane',6,'asphalt'),
         ('east_furniture',3.5,'paving'),('east_walk',2.5,'paving')],
        ['Painted play graphics, timber planters, bicycle parking, seats and bollards'],
        ['Side bollards leave centre open for later network-controlled access; no school building or claimed traffic restriction']),
    'grand_promenade': spec('Grand Promenade Boulevard', 'barcelona-passeig-grand-promenade/hero.png',
        [('west_walk',2.5,'paving'),('west_road',3.25,'asphalt'),('west_furniture',3.5,'paving'),
         ('promenade',6,'paving'),('east_furniture',3.5,'paving'),('east_road',3.25,'asphalt'),('east_walk',2.5,'paving')],
        ['Broad central walk, paired tree rows, benches, kiosks and outer traffic lanes'],
        ['Small news kiosk and flower stall occupy side bays; original metric section']),
}


def recipe(kind):
    r=copy.deepcopy(STREETS[kind]);w=sum(b[1] for b in r['bands']);x=-w/2
    sections=[]
    for name,width,material in r.pop('bands'):
        sections.append(dict(name=name,x=x+width/2,width=width,material=material));x+=width
    r.update(id=f'student_{kind}_v1',kind=kind,dimensions_m=[w,r['length_m']],sections=sections,
             fixed_width_m=w,fixture_length_m=r['length_m'])
    return r


def validate(r):
    assert len({s['name'] for s in r['sections']})==len(r['sections'])
    assert abs(sum(s['width'] for s in r['sections'])-r['dimensions_m'][0])<1e-8
    assert all(s['width']>0 for s in r['sections'])
    assert r['reference'].split('/')[0] and '..' not in r['reference']
    assert r['observed_features'] and r['adapted_features']
    return r
