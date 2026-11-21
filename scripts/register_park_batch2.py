"""Register the visually inspected park batch 2 pilots, preserving prior parks.

Usage: python scripts/register_park_batch2.py --package <built package directory>
Build each with tools/native_park_batch/build.py and check it with verify.py first.
Registration only records local pilots: runtime acceptance and publication stay separate.
"""
import argparse
from pathlib import Path
from register_classroom_park import register

SPECS = {
    'student_community_ball_diamond_v1': dict(
        key='community-diamond-v005', archetype='baseball_softball_diamond',
        sha256='08fab3e99c6b68540868ea7a17050348b1167d78600c114ab01c491aed271a9a',
        description='A Little League ball diamond with a dirt infield, backstop, dugouts, bleachers, field lights and a scoreboard, '
                    'ringed by a path loop and trees. Prepared level ground.',
        entrance=dict(x=-14.0, y=-44.0, widthM=3.0, arrivalY=-41.0), group='play_sport',
        walk_surface_materials=['paving', 'grass', 'gravel']),
    'student_community_track_field_v1': dict(
        key='community-track-v005', archetype='running_track_oval',
        sha256='983a00d5aa8a812714df19aaa0cdb36cf6688ec9ab4b91b4a0b57da9e286c6f5',
        description='A six-lane 400 m running track round a soccer pitch, with long jump and shot put, bleachers, a shelter and a '
                    'walking loop through trees. Prepared level ground.',
        entrance=dict(x=0.0, y=-56.0, widthM=3.0, arrivalY=-53.0), group='play_sport',
        walk_surface_materials=['paving', 'grass', 'rubber', 'gravel']),
    'student_village_green_cricket_v1': dict(
        key='village-cricket-v003', archetype='cricket_pitch_oval',
        sha256='3819fe8dada57fcfabc096a5b24badeac38bd42895ddcb119c28fe439f56de65',
        description='A village cricket ground with a picket fence, boundary rope, square and pitch, sight screens, a timber pavilion '
                    'and shade trees. Prepared level ground.',
        entrance=dict(x=16.0, y=-60.0, widthM=2.4, arrivalY=-57.0), group='play_sport',
        walk_surface_materials=['paving', 'grass', 'gravel']),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    register(parser.parse_args().package, specs=SPECS)
