"""Exact legacy review provenance can coexist with a new canonical record."""
import copy
import hashlib
import json

import pytest

from tools.seed_model_library import verify_existing_row


def sealed_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                                     allow_nan=False).encode('utf-8')).hexdigest()


@pytest.fixture
def binding():
    raw_text = 'Preserved original independent review.'
    raw_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
    url = '/api/v1/files/library/rlasm-architectural-clay/test-exact-v009.glb'
    expected = {
        'id': 'exact-existing-row', 'model_url': url, 'lod_urls': {'0': url},
        'metadata': {
            'rlasm': {'candidate': 'test-exact-v009', 'archetype_id': 'test_parent', 'variant_id': 'test_variant',
                      'model_sha256': 'a' * 64, 'review_sha256': 'b' * 64,
                      'review_status': 'PASS_INDEPENDENT_ARCHITECTURAL_CLAY',
                      'native_dimensions_m': {'width': 4, 'depth': 6, 'height': 8},
                      'design_dimensions_m': {'width': 3, 'depth': 5, 'height': 7},
                      'method': 'RLASM', 'method_version': '6.1', 'delivery_format': 'architectural_clay',
                      'runtime_enabled': True, 'source_locked': True, 'continuous_resize_allowed': False},
            'lego': {'family': 'canonical-family', 'role': 'assembled', 'variant_key': 'test_variant',
                     'native_floors': 2, 'min_floors': 2, 'max_floors': 2, 'allowed_levels': [2],
                     'width_m': 4, 'depth_m': 6, 'height_m': 8, 'repeatable_z': False},
        },
    }
    metadata = copy.deepcopy(expected['metadata'])
    metadata['rlasm'].update(review_sha256=raw_hash, review_status='PASS_ZERO_P0_P1',
                             design_dimensions_m={'width': 4, 'depth': 6, 'height': 8},
                             source_delivery={'units': 'metres'}, import_scope='local_trial_only')
    metadata['lego']['family'] = 'original-source-family'
    stored = {'model_url': url, 'lod_urls': {'0': url}, 'is_public': True, 'metadata': metadata}
    review = {
        'candidate': 'test-exact-v009', 'model_sha256': 'a' * 64, 'reviewer': 'original independent reviewer',
        'architectural_clay_pass': True, 'holistic_review_performed': True, 'unresolved_p0': 0, 'unresolved_p1': 0,
        'source_review': {'sha256': raw_hash, 'text': raw_text},
        'legacy_seed_metadata_attestation': {
            'schema': 'cityprompt.clay-legacy-seed-attestation@1',
            'candidate': 'test-exact-v009', 'row_id': 'exact-existing-row',
            'model_sha256': 'a' * 64, 'source_review_sha256': raw_hash,
            'storage_key': 'library/rlasm-architectural-clay/test-exact-v009.glb',
            'native_floors': 2, 'native_dimensions_m': {'width': 4, 'depth': 6, 'height': 8},
            'legacy_metadata_sha256': sealed_digest(metadata),
        },
    }
    return expected, stored, review


def test_attested_original_review_binding_is_verified_without_changing_it(binding):
    expected, stored, review = binding
    before = copy.deepcopy(stored)
    verify_existing_row(expected, stored, review=review, verified_model_sha256='a' * 64)
    assert stored == before


def test_clean_canonical_install_still_uses_strict_metadata_without_attestation(binding):
    expected, stored, _ = binding
    stored['metadata'] = copy.deepcopy(expected['metadata'])
    verify_existing_row(expected, stored)


def test_legacy_difference_without_attestation_remains_a_conflict(binding):
    expected, stored, _ = binding
    with pytest.raises(ValueError, match='conflicting'):
        verify_existing_row(expected, stored)


def test_compatibility_review_must_be_the_exact_hashed_canonical_file(tmp_path):
    from tools.seed_model_library import verified_seed_review
    path = tmp_path / 'evidence/review.json'
    path.parent.mkdir()
    path.write_text('{"candidate":"test-exact-v009"}', encoding='utf-8')
    entry = {'review': {'repo_path': 'evidence/review.json', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}}
    assert verified_seed_review(entry, repo_root=tmp_path) == {'candidate': 'test-exact-v009'}
    path.write_text('{"candidate":"another-v009"}', encoding='utf-8')
    with pytest.raises(ValueError, match='review bytes'):
        verified_seed_review(entry, repo_root=tmp_path)


def test_attestation_requires_an_independent_read_of_exact_stored_model_bytes(binding):
    expected, stored, review = binding
    with pytest.raises(ValueError, match='conflicting'):
        verify_existing_row(expected, stored, review=review)


@pytest.mark.parametrize('change', ['model_bytes', 'source_review', 'raw_review_text', 'new_review_model', 'new_review_candidate',
                                  'nonholistic', 'metadata_digest', 'row_id', 'storage_key', 'floor',
                                  'native_dimensions', 'variant', 'unknown_metadata', 'private', 'lod_url'])
def test_attestation_cannot_hide_changed_identity_geometry_review_or_metadata(binding, change):
    expected, stored, review = binding
    verified = 'a' * 64
    attestation = review['legacy_seed_metadata_attestation']
    if change == 'model_bytes':
        verified = 'd' * 64
    elif change == 'source_review':
        review['source_review']['sha256'] = 'd' * 64
    elif change == 'raw_review_text':
        review['source_review']['text'] = 'Changed historical review.'
    elif change == 'new_review_model':
        review['model_sha256'] = 'd' * 64
    elif change == 'new_review_candidate':
        review['candidate'] = 'another-v009'
    elif change == 'nonholistic':
        review['holistic_review_performed'] = False
    elif change == 'metadata_digest':
        attestation['legacy_metadata_sha256'] = 'd' * 64
    elif change == 'row_id':
        attestation['row_id'] = 'another-row'
    elif change == 'storage_key':
        attestation['storage_key'] = 'library/rlasm-architectural-clay/another-v009.glb'
    elif change == 'floor':
        stored['metadata']['lego']['native_floors'] = 3
        attestation['legacy_metadata_sha256'] = sealed_digest(stored['metadata'])
    elif change == 'native_dimensions':
        stored['metadata']['rlasm']['native_dimensions_m']['height'] = 9
        attestation['legacy_metadata_sha256'] = sealed_digest(stored['metadata'])
    elif change == 'variant':
        stored['metadata']['rlasm']['variant_id'] = 'another_variant'
        attestation['legacy_metadata_sha256'] = sealed_digest(stored['metadata'])
    elif change == 'unknown_metadata':
        stored['metadata']['lego']['unreviewed_capability'] = True
        attestation['legacy_metadata_sha256'] = sealed_digest(stored['metadata'])
    elif change == 'private':
        stored['is_public'] = False
    elif change == 'lod_url':
        stored['lod_urls']['0'] += '?different-version'
    with pytest.raises(ValueError, match='conflicting'):
        verify_existing_row(expected, stored, review=review, verified_model_sha256=verified)
