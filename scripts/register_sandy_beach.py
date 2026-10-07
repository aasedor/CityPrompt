"""Register the single visually inspected sandy beach pilot, preserving prior parks."""
import argparse
from pathlib import Path
from register_classroom_park import register

SPECS = {
    'student_sandy_beach_v1': dict(
        key='sandy-beach-v004', archetype='urban_beach',
        sha256='1c74b53d35dbd80286bd1caff819643f1c84fbf5e752b4ea8be9e955f90eced2',
        description='A sandy freshwater crescent with a lagoon, cedar boardwalk, loungers, striped parasols and two picnic shelters. Includes decorative water; prepared level ground.',
        entrance=dict(x=0, y=-24, widthM=3, arrivalY=-21), group='water',
        walk_surface_materials=['paving.001', 'grass', 'sand']),
}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    register(parser.parse_args().package, specs=SPECS)
