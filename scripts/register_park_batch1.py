"""Register the visually inspected park batch 1 pilots, preserving prior parks.

Usage: python scripts/register_park_batch1.py --package <built package directory>
Build each with tools/native_park_batch/build.py and check it with verify.py first.
Registration only records local pilots: runtime acceptance and publication stay separate.
"""
import argparse
from pathlib import Path

from register_classroom_park import register

SPECS = {
    'student_prairie_bowl_skate_park_v1': dict(
        key='prairie-bowl-skate-v006', archetype='skate_park',
        sha256='63f17b45b72cfd215efaac152232ee60dba2c2a7b282e05133edb8e1bfda5b0f',
        description='Concrete bowls and a snake run set into prairie meadow, with timber terrace seating, a street plaza and a path loop. '
                    'Prepared level ground.',
        entrance=dict(x=0, y=-26, widthM=2.2, arrivalY=-23), group='play_sport',
        walk_surface_materials=['paving', 'grass', 'gravel']),
    'student_parkour_calisthenics_yard_v1': dict(
        key='parkour-yard-v004', archetype='outdoor_fitness_circuit',
        sha256='de904793cef32f06eca7e786563864d192bdf011a537553d794b15c9506cd20e',
        description='A red rubber movement floor with vault walls, a climbing wall, a pull-up rig and a hex frame, in lawn and planting '
                    'with a path loop. Prepared level ground.',
        entrance=dict(x=6, y=-18, widthM=2.0, arrivalY=-15), group='play_sport',
        walk_surface_materials=['paving', 'grass', 'rubber']),
    'student_walled_memorial_garden_v1': dict(
        key='walled-memorial-v004', archetype='memorial_garden',
        sha256='fbfc279068e6bdfb0b8f35064dcda46d7851a7f8cf514599637e0611464325f2',
        description='A brick-walled garden with a long reflecting pool, hedged flower beds, columnar trees, a rose arbour and a wall of '
                    'blank plaques. Prepared level ground.',
        entrance=dict(x=0, y=-25, widthM=3.0, arrivalY=-22), group='gardens',
        walk_surface_materials=['paving', 'gravel', 'grass']),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    register(parser.parse_args().package, specs=SPECS)
