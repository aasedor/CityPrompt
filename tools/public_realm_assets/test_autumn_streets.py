from scripts.autumn_streets import inspect_seed, ROOT
import json


def test_autumn_seed_is_closed_and_matches_active_exact_bindings():
    inspected = inspect_seed()
    rows = {r['id']: r for r in json.loads((ROOT/'frontend/src/data/nativeStreetPilots.json').read_text())}
    assert len(inspected) == 3
    for row, files in inspected:
        assert rows[row['id']] == row
        assert all(p['kind']+'.glb' in files for p in row['placements'])
        assert row['program']['preparedLevelOnly'] is True
        assert row['program']['minLengthM'] == row['fixtureLengthM']
