"""Register the visually inspected park batch 3 pilots, preserving prior parks.

Usage: python scripts/register_park_batch3.py --package <built package directory>
Build each with tools/native_park_batch/build.py and check it with verify.py first.
Registration only records local pilots: runtime acceptance and publication stay separate.
"""
import argparse
from pathlib import Path
from register_classroom_park import register

SPECS = {
    'student_calgary_prairie_plaza_v1': dict(
        key='prairie-wind-plaza-v006', archetype='calgary_prairie_plaza',
        sha256='0af3427d166369a11dd1584cb7543992ebc0123b8d1f0699c6b88999d09a4f87',
        description='A civic plaza with a sandstone wind-rose circle, prairie grass crescents, shade sails, a reflecting pool, '
                    'market stalls and a wind screen framing the mountain view. Prepared level ground.',
        entrance=dict(x=0.0, y=-26.0, widthM=4.0, arrivalY=-23.0), group='plazas',
        walk_surface_materials=['paving', 'grass']),
    'student_clover_neighbourhood_park_v1': dict(
        key='clover-neighbourhood-v005', archetype='neighborhood_park',
        sha256='a320a1aa781522dc4264cce884920eda79c263c6c8a52848fabfab4d5ecc63ad',
        description='A neighbourhood park with an open play lawn, a ring walk, a timber playground, a picnic shelter, a nature-play '
                    'corner and shade trees. Prepared level ground.',
        entrance=dict(x=4.0, y=-34.0, widthM=2.4, arrivalY=-31.0), group='neighbourhood',
        walk_surface_materials=['grass', 'gravel', 'paving']),
    'student_prairie_sports_complex_v1': dict(
        key='prairie-sports-complex-v003', archetype='sports_field_complex',
        sha256='b61324564012769e401dcf5a38b591202790591703f8f0b92c7fb123ee8f04f3',
        description='Two soccer pitches and two ball diamonds round a central plaza and fieldhouse, with bleachers, field lights '
                    'and a promenade. Prepared level ground.',
        entrance=dict(x=0.0, y=-84.0, widthM=4.0, arrivalY=-81.0), group='play_sport',
        walk_surface_materials=['paving', 'grass', 'gravel']),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    register(parser.parse_args().package, specs=SPECS)
