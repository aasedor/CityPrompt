"""Register the visually inspected park batch 4 pilots, preserving prior parks.

Usage: python scripts/register_park_batch4.py --package <built package directory>
Build each with tools/native_park_batch/build.py and check it with verify.py first.
Registration only records local pilots: runtime acceptance and publication stay separate.
"""
import argparse
from pathlib import Path
from register_classroom_park import register

SPECS = {
    'student_creekside_mini_golf_v1': dict(
        key='creekside-mini-golf-v007', archetype='mini_golf_course',
        sha256='c989175c73f3cb0d1c554ba672694ee4e9785e7fedf1ae418e1c695a04fb6179',
        description='A nine-hole mini golf course along a rock-lined creek, with carpet greens, timber footbridges and a sod-roof '
                    'starter hut. Prepared level ground.',
        entrance=dict(x=0.0, y=-20.0, widthM=1.8, arrivalY=-17.0), group='play_sport',
        walk_surface_materials=['grass', 'gravel', 'deck']),
    'student_boulder_block_park_v1': dict(
        key='boulder-block-park-v004', archetype='climbing_bouldering_wall',
        sha256='d9434bae810de52030aba1ffee5039a5e126ffd395d57bb4563cd7775ee333b5',
        description='Angular concrete bouldering blocks with coloured holds in a black rubber fall zone, with a timber seat edge and '
                    'prairie planting. Prepared level ground.',
        entrance=dict(x=0.0, y=-16.0, widthM=3.0, arrivalY=-13.0), group='play_sport',
        walk_surface_materials=['paving', 'rubber', 'grass']),
    'student_prairie_pollinator_meadow_v1': dict(
        key='prairie-pollinator-meadow-v004', archetype='pollinator_meadow',
        sha256='d157f0792eb8499deb484d55d5fbe7e415301bed875fe7915c5b036f0d8f6f65',
        description='A native wildflower meadow with a winding walk, a mown loop, bee hotels and interpretive lecterns. Prepared '
                    'level ground.',
        entrance=dict(x=0.0, y=-18.0, widthM=1.8, arrivalY=-15.0), group='nature',
        walk_surface_materials=['gravel', 'grass']),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    register(parser.parse_args().package, specs=SPECS)
