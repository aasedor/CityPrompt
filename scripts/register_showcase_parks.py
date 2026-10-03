"""Register only the exact three offline-reviewed showcase park deliveries."""
import argparse
import hashlib
import json
from pathlib import Path
from register_classroom_park import register

SPECS={
 'student_woodland_stream_garden_v1':dict(key='showcase-woodland-v004',archetype='japanese_garden',sha256='b4280c800244f05b035aea3a01ed954ec87740001b91130792f01a0bb19316b3',description='A winding stream, arched timber bridge, raked gravel room and layered woodland planting.',entrance=dict(x=0,y=-29,widthM=2.7,arrivalY=-27.5)),
 'student_reflecting_fountain_garden_v1':dict(key='showcase-reflecting-v002',archetype='fountain_water_feature',sha256='2eb802caefceb5e591a12ea7393ac84f79dfbf82cb471d152acae6d04b691179',description='A formal two-lobed pool with four jets, clipped hedges and shaded promenade seating.',entrance=dict(x=0,y=-24,widthM=2.7,arrivalY=-22)),
 'student_terraced_cafe_court_v1':dict(key='showcase-court-v002',archetype='sunken_plaza',sha256='d4c6735bf653130f28ce81c87fcf228e31410e992b28a6ae8bf0b9263afbd477',description='A limestone gathering court with seven seat steps, café umbrellas and a bronze fountain.',entrance=dict(x=0,y=-24,widthM=2.7,arrivalY=-22)),
}

def main(package):
    recipe=json.loads((package/'recipe.json').read_text());review=json.loads((package/'visual-review.json').read_text())
    if review.get('status')!='PASS_OFFLINE_NATIVE_REVIEW' or review.get('model_sha256')!=recipe['assembly']['sha256']:
        raise ValueError('Require the actual exported-model visual review')
    reference=next(r for r in recipe['source_references'] if r['role']=='front')
    hero=Path(reference['path']).name
    if hashlib.sha256((package/hero).read_bytes()).hexdigest()!=reference['sha256']:raise ValueError('Hero must be the exact photographic reference')
    register(package,specs=SPECS,thumbnail_name=hero)
    # Preserve the readable exact-variant visual ledger with the model seed.
    seed=Path(__file__).resolve().parents[1]/'seed/classroom-parks'/SPECS[recipe['id']]['key']
    (seed/'visual-review.json').write_bytes((package/'visual-review.json').read_bytes())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);main(p.parse_args().package)
