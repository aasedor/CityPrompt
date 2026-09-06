"""Durable promotion contract for the exact three human-activated clay models."""
import hashlib
import json
from pathlib import Path

from tools.rlasm_clay_library import load_library, clay_seed_rows, clay_seed_objects


def test_published_trio_has_reviewed_native_models_and_public_exact_variant_rows():
    root = Path(__file__).resolve().parents[3]
    library = load_library(repo_root=root)
    assert {e['variant_id'] for e in library['entries']} >= {
        'bungalow_postwar_ranch', 'toronto_foursquare_red_brick', 'sandstone_romanesque_revival',
    }
    rows = list(clay_seed_rows(library))
    assert len(rows) == len(list(clay_seed_objects(library))) == len(library['entries'])
    for entry, row in zip(library['entries'], rows):
        review_file = root / entry['review']['repo_path']
        assert hashlib.sha256(review_file.read_bytes()).hexdigest() == entry['review']['sha256']
        review = json.loads(review_file.read_text())
        assert review['architectural_clay_pass'] and review['holistic_review_performed']
        assert review['model_sha256'] == entry['model']['sha256']
        assert review['unresolved_p0'] == review['unresolved_p1'] == 0
        assert row['is_public'] and row['metadata']['rlasm']['keeper_approved'] is False
        assert row['metadata']['lego']['variant_key'] == entry['variant_id']
        assert row['metadata']['lego']['repeatable_z'] is False
        assert row['metadata']['lego']['width_m'] == entry['model']['native_dimensions_m']['width']
