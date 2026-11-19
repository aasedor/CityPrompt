"""Register the visually inspected stormwater pond pilot, preserving prior parks.

Usage: python scripts/register_stormwater_pond.py --package <built stormwater pond directory>
Build it with tools/stormwater_pond_park/build.py and check it with verify.py first.
"""
import argparse
from pathlib import Path
from register_classroom_park import register

SPECS = {
    'student_stormwater_pond_v1': dict(
        key='stormwater-pond-v002', archetype='stormwater_retention_pond',
        sha256='9f883c823d0677b74a516a0758857e17551f27eb45b64ac4a0959bb7377ac593',
        description='A wet stormwater pond with cattail shallows, a 3 m pathway loop, a timber viewing dock, inlet and outlet structures, benches, willows and aspen. Decorative water; prepared level ground.',
        entrance=dict(x=0, y=-34, widthM=3, arrivalY=-31), group='water',
        walk_surface_materials=['paving', 'grass', 'deck']),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    register(parser.parse_args().package, specs=SPECS)
