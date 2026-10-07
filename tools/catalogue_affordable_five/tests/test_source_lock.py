import importlib.util
import json
from pathlib import Path
import pytest
from PIL import Image

SPEC=importlib.util.spec_from_file_location('affordable_plan',Path(__file__).parents[1]/'plan.py')
plan=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plan)

@pytest.fixture
def locked(tmp_path):
    root=tmp_path/'frontend/public/archetypes/buildings/affordable-porchlight'
    root.mkdir(parents=True)
    records=[]
    for i,role in enumerate(('front','oblique','top')):
        p=root/('variant_0'+('', '_angle_60','_angle_90')[i]+'.png')
        Image.new('RGB',(512,512),(i*50,40,80)).save(p)
        records.append(dict(role=role,file=p.name,bytes=p.stat().st_size,sha256=plan.digest(p),dimensions_px=[512,512]))
    provenance=root/'generation-provenance.json'
    provenance.write_text(json.dumps(dict(origin='original_generated_design',records=records)))
    return tmp_path,root,provenance

def test_complete_lock_preserves_exact_bytes(locked):
    base,root,_=locked
    entry=plan.source_entry('porchlight',base)
    assert len(entry['sources'])==3
    assert all(plan.digest(s['original_path'])==s['sha256'] for s in entry['sources'])

def test_tampering_is_rejected(locked):
    base,root,_=locked
    with (root/'variant_0.png').open('ab') as f:f.write(b'changed')
    with pytest.raises(ValueError,match='changed'):plan.source_entry('porchlight',base)

@pytest.mark.parametrize('change',['missing','duplicate','escape'])
def test_bad_role_inventory_is_rejected(locked,change):
    base,_,p=locked;data=json.loads(p.read_text())
    if change=='missing':data['records'].pop()
    elif change=='duplicate':data['records'].append(data['records'][0])
    else:data['records'][0]['file']='../variant_0.png'
    p.write_text(json.dumps(data))
    with pytest.raises(ValueError):plan.source_entry('porchlight',base)

def test_new_view_cannot_bypass_review(locked):
    base,root,_=locked
    Image.new('RGB',(512,512)).save(root/'variant_0_extra.png')
    with pytest.raises(ValueError,match='Additional reference'):plan.source_entry('porchlight',base)
