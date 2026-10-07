"""Gallery publication must preserve the exact independently inspected candidate."""
import hashlib
import json
import pytest
from tools.catalogue_coverage_five.gallery import verified_candidate


@pytest.fixture
def evidence(tmp_path):
    def write(name,value):
        path=tmp_path/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value),encoding='utf-8')
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    model=tmp_path/'model.glb';model.write_bytes(b'fixture model identity')
    inspected=[]
    for name in ['renders/front.png','sources/front.png','boards/locked-source-board.png','boards/phone-source-comparison.png','boards/phone-construction.png','boards/all-views-contact.png']:
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(name.encode())
        inspected.append(dict(path=name,sha256=digest(path)))
    write('build-report.json',dict(candidate='fixture-v001',runtime=dict(path='model.glb',sha256=digest(model))))
    write('prework-manifest.json',dict(mandatory_review_views=['front'],source_contract=dict(sources=[dict(path='sources/front.png')])))
    review=dict(candidate='fixture-v001',decision='PASS_ARCHITECTURAL_CLAY_REVIEW',holistic=True,unresolved_blocker_counts=dict(P0=0,P1=0),integrity=dict(glb_sha256=digest(model)),inspected_files=inspected)
    write('review.json',review)
    return tmp_path,review,write


def test_exact_reviewed_evidence_is_accepted(evidence):
    root,_,_=evidence
    assert verified_candidate(root,root/'review.json')[0]['candidate']=='fixture-v001'


def test_model_cannot_be_substituted_after_review(evidence):
    root,_,_=evidence;(root/'model.glb').write_bytes(b'replacement model')
    with pytest.raises(ValueError,match='does not match'):verified_candidate(root,root/'review.json')


def test_uninspected_view_cannot_be_added_to_delivery(evidence):
    root,_,write=evidence
    write('prework-manifest.json',dict(mandatory_review_views=['front','rear'],source_contract=dict(sources=[dict(path='sources/front.png')])))
    with pytest.raises(ValueError,match='Mandatory images'):verified_candidate(root,root/'review.json')


def test_failed_candidate_cannot_enter_gallery(evidence):
    root,review,write=evidence;review['decision']='FAIL';write('review.json',review)
    with pytest.raises(ValueError,match='has not passed'):verified_candidate(root,root/'review.json')


def test_reviewed_pixels_cannot_be_changed(evidence):
    root,_,_=evidence;(root/'renders/front.png').write_bytes(b'changed pixels')
    with pytest.raises(ValueError,match='Reviewed evidence changed'):verified_candidate(root,root/'review.json')


def test_withdrawn_pass_cannot_be_reused(evidence):
    root,_,write=evidence
    previous_hash=hashlib.sha256((root/'review.json').read_bytes()).hexdigest()
    write('withdrawal-review.json',dict(candidate='fixture-v001',decision='FAIL',supersedes_review_sha256=previous_hash))
    with pytest.raises(ValueError,match='has been superseded'):verified_candidate(root,root/'review.json')
