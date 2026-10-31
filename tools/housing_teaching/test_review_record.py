"""Keep an offline visual pass from silently becoming catalogue activation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_housing_evidence_is_synchronized_exact_and_separate_from_activation():
    method = json.loads((ROOT/'tools/archetype_compiler/rlasm_method.json').read_text())
    memory = json.loads((ROOT/'tools/archetype_compiler/high_quality_building_memory.json').read_text())
    batch = method['housing_teaching_batch']
    assert batch == memory['housing_teaching_batch']
    assert batch['method'] == 'RLASM v6.1'
    assert batch['runtime_integration'] == 'NOT TESTED'
    assert batch['seed_activation'] is False
    assert set(batch['candidates']) == {'victory', 'split'}
    cards = json.loads((ROOT/'docs/housing-teaching-cards.json').read_text())
    for name, record in batch['candidates'].items():
        card = cards[name]
        assert card['archetypeId'] == record['archetype_id']
        assert card['variantId'] == record['variant_id']
        assert card['modelSha256'] == record['model_sha256']
        assert card['independentReviewSha256'] == record['review_sha256']
        assert record['unresolved_p0'] == record['unresolved_p1'] == 0
        assert len(record['model_sha256']) == len(record['review_sha256']) == 64
        assert card['runtimeActivation'] is False
        assert card['tenure'] == card['affordability'] == 'not_inferred'
    assert (ROOT/batch['evidence']).is_file()
