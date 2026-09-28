import json
from scripts.showcase_streets import inspect_seed,IDS

def test_showcase_seed_is_closed_and_hash_verified():
    rows=inspect_seed()
    assert {r['id'] for r,_ in rows}==IDS
    for row,files in rows:
        assert set(files)=={k+'.glb' for k in row['modules']}|{'reference.png'}
        assert row['program']['surfaceRegions']
        assert row['program']['preparedLevelOnly']
        assert len(row['programSha256'])==64
