import hashlib,json
from pathlib import Path
import pytest
from .stage_trial import preflight


def package(root):
    (root/'sources').mkdir();(root/'review').mkdir();records=[]
    for role in ('front','oblique','top','ramp_section'):
        raw=role.encode();(root/'sources'/(role+'.png')).write_bytes(raw)
        records.append(dict(role=role,path='sources/'+role+'.png',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
    raw=b'locked-reviewed-model';(root/'model.glb').write_bytes(raw);sha=hashlib.sha256(raw).hexdigest()
    identity=dict(candidate='parkade-urban-brick-clay-v001',archetype_id='parkade-urban-brick',variant_id='brick-v1')
    docs={'build-report.json':dict(candidate=identity['candidate'],runtime=dict(path='model.glb',sha256=sha)),
        'prework-manifest.json':dict(**identity,source_contract=dict(sources=records)),
        'source-entry.json':dict(archetype_id=identity['archetype_id'],variant_id=identity['variant_id'],sources=records),
        'review/independent.json':dict(candidate=identity['candidate'],model_sha256=sha,reviewer='independent',architectural_clay_pass=True,holistic_review_performed=True,unresolved_p0=0,unresolved_p1=0,inspected_files=[dict(sha256=r['sha256']) for r in records])}
    for name,doc in docs.items():(root/name).write_text(json.dumps(doc))
    return root


def test_preflight_accepts_exact_four_role_reviewed_bytes(tmp_path):
    preflight(package(tmp_path),'brick')


@pytest.mark.parametrize('file', ['front.png','ramp_section.png'])
def test_preflight_refuses_modified_sources_including_supplemental_section(tmp_path,file):
    root=package(tmp_path);(root/'sources'/file).write_bytes(b'unreviewed')
    with pytest.raises(ValueError,match='modified source'):preflight(root,'brick')


def test_preflight_refuses_review_for_another_candidate(tmp_path):
    root=package(tmp_path);p=root/'review/independent.json';r=json.loads(p.read_text());r['candidate']='other';p.write_text(json.dumps(r))
    with pytest.raises(ValueError,match='identity'):preflight(root,'brick')


def test_preflight_refuses_changed_model(tmp_path):
    root=package(tmp_path);(root/'model.glb').write_bytes(b'changed')
    with pytest.raises(ValueError,match='Model changed'):preflight(root,'brick')


def test_preflight_refuses_source_path_alias_that_would_copy_other_bytes(tmp_path):
    root=package(tmp_path);p=root/'source-entry.json';entry=json.loads(p.read_text())
    role=entry['sources'][-1];(root/'sources/reviewed-section.png').write_bytes((root/role['path']).read_bytes())
    role['path']='sources/reviewed-section.png';p.write_text(json.dumps(entry))
    with pytest.raises(ValueError,match='exact copied path'):preflight(root,'brick')
