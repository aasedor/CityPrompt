"""Observed catalogue-image cues, separate from regulation court dimensions."""
from copy import deepcopy
from pathlib import Path
import hashlib

REFERENCE_PROFILES={
 'basketball':dict(terrace='urban',sideline='players',lights='court',
    images=['basketball-court/hero.png','basketball-court/variant_0.png'],
    observed='Simple player benches, open chain-link enclosure, charcoal playing finish and twin-head floodlights.',
    adaptation='Single neighbourhood court; omit background buildings and image people.'),
 'three_x_three':dict(terrace='urban',sideline='walls',lights='court',
    images=['basketball-court/hero.png','pickleball-courts/hero.png'],
    observed='Urban player seating and timber-capped masonry seats.',
    adaptation='Half-court adaptation; seat walls borrowed from the related pickleball reference, not an exact 3x3 image.'),
 'tennis':dict(terrace='covered',sideline='bleachers',lights='court',
    images=['tennis-court-cluster/variant_0.png','pickleball-courts/hero.png'],
    observed='Aluminium spectator stands, sport floodlights and covered timber player seating.',
    adaptation='Retain one full native court, not the reference multi-court cluster. Shelter cue borrowed from pickleball.'),
 'padel':dict(terrace='club',sideline='players',lights='court',
    images=['pickleball-courts/hero.png','beach-volleyball-courts/variant_1.png'],
    observed='Covered player seating and small parasol cafe terraces.',
    adaptation='No exact padel catalogue image; related racquet-club treatment around the existing padel glass enclosure.'),
 'volleyball':dict(terrace='team',sideline='bleachers',lights='court',referee=True,
    images=['beach-volleyball-courts/hero.png','tennis-court-cluster/variant_0.png','pickleball-courts/hero.png'],
    observed='Referee chair, spectator stands and covered player benches.',
    adaptation='Hardcourt adaptation of beach officiating and related court seating; referee stand outside the full reserve.'),
 'beach_volleyball':dict(terrace='parasols',sideline='walls',lights='park',referee=True,
    images=['beach-volleyball-courts/hero.png','beach-volleyball-courts/variant_1.png'],
    observed='Low spectator seat walls, elevated referee chair, cafe tables and parasols.',
    adaptation='Use the temperate meadow planting kit for Currie; do not import tropical palms or a clubhouse.'),
 'badminton':dict(terrace='garden',sideline='players',lights='park',
    images=['pickleball-courts/variant_2.png','bocce-pétanque-court/hero.png'],
    observed='Small timber shelters, player benches and informal cafe seating.',
    adaptation='No exact badminton catalogue image; calm-weather garden adaptation of the related outdoor court kit.'),
 'netball':dict(terrace='urban',sideline='bleachers',lights='court',
    images=['basketball-court/variant_0.png','tennis-court-cluster/variant_0.png'],
    observed='Player seating, low aluminium stands and tall court lighting.',
    adaptation='No exact netball catalogue image; related community sports setting, retaining netball ring-only posts.'),
 'bocce':dict(terrace='arbour',sideline='walls',lights='park',
    images=['bocce-pétanque-court/hero.png','bocce-pétanque-court/variant_1.png'],
    observed='Braced timber arbour, cafe tables/chairs, informal seat walls and overhead string lights.',
    adaptation='Open neighbourhood garden with timber lane boards; light climbing foliage is an original refinement.'),
 'petanque':dict(terrace='cafe',sideline='walls',lights='park',
    images=['bocce-pétanque-court/variant_1.png','bocce-pétanque-court/hero.png'],
    observed='Cafe seating, low edge seats and strings of lights beneath trees.',
    adaptation='Two marked lanes remain; use tree shade and cafe furniture without repeating the large pergola.'),
}

def apply_profile(recipe,reference_root):
    profile=deepcopy(REFERENCE_PROFILES[recipe['sport']]);root=Path(reference_root)
    references=[]
    for name in profile.pop('images'):
        p=root/name
        assert p.is_file(),p
        references.append(dict(path=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
    recipe['previous_id']=recipe['id'];recipe['id']=recipe['id'].removesuffix('_v1')+'_v2'
    recipe['reference_profile']=profile;recipe['image_references']=references
    if recipe['sport'] in ('basketball','three_x_three'):recipe['court_colour']=[.13,.15,.14]
    return recipe
