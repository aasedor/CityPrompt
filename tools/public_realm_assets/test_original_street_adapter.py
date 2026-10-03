import hashlib
import json
import pytest
from tools.public_realm_assets import original_street_adapter as adapter


def test_original_adapter_preserves_input_and_rejects_changed_source(tmp_path, monkeypatch):
    source=dict(id='student_test_v1',kind='residential',dimensions_m=[18,48],
                sections=[dict(name='west_garden',x=-4.5,width=3)],
                metric_paving_module_m=[1.2,.8],surface_regions=[dict(x=-4.5,y=7,width=2.76,depth=4.6,material='soil')])
    raw=json.dumps(source).encode()
    (tmp_path/'renders').mkdir()
    (tmp_path/'renders/aerial.png').write_bytes(b'image')
    (tmp_path/'build.py').write_text('original builder')
    lock=dict(recipeSha256=hashlib.sha256(raw).hexdigest(),sourceArchetypeId=source['id'],
              files={name:hashlib.sha256((tmp_path/name).read_bytes()).hexdigest() for name in ['build.py','renders/aerial.png']})
    lockfile=tmp_path/'locks.json';lockfile.write_text(json.dumps({source['id']:lock}))
    monkeypatch.setattr(adapter,'LOCKS',lockfile)
    normalized,program=adapter.adapt_original(tmp_path,source,raw)
    assert 'fixed_width_m' not in source
    assert normalized['fixed_width_m']==18
    assert normalized['fixture_length_m']==48
    assert program['surfaceRegions']==source['surface_regions']
    assert len([d for d in program['details'] if d['height']==.05])==4
    assert program['minLengthM']==48
    (tmp_path/'build.py').write_text('changed')
    with pytest.raises(ValueError,match='source changed'):
        adapter.adapt_original(tmp_path,source,raw)
    with pytest.raises(ValueError,match='recipe differs'):
        adapter.adapt_original(tmp_path,source,raw+b' ')
