import json
from pathlib import Path
import shutil
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.classroom_streets import inspect, SEED


def test_all_three_deliveries_are_closed_and_hash_verified():
    rows=inspect()
    assert len(rows)==3
    assert [len(files)-1 for _,files in rows]==[9,7,7]


@pytest.mark.parametrize('target',['module','program','source'])
def test_changed_deliveries_are_rejected(tmp_path,target):
    shutil.copytree(ROOT/SEED,tmp_path/SEED)
    path=tmp_path/SEED/'manifest.json'
    rows=json.loads(path.read_text())
    row=rows[0]
    if target=='program':
        row['program']['meshDetails'][0]['positions'][0]+=1
        path.write_text(json.dumps(rows))
    else:
        name=next(iter(row['modules']))+'.glb' if target=='module' else 'source-recipe.json'
        p=tmp_path/SEED/row['id']/name
        p.write_bytes(p.read_bytes()+b'corrupt')
    with pytest.raises(ValueError,match='Changed'):inspect(tmp_path)
