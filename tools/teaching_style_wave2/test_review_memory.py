"""Keep exact teaching review evidence and activation boundaries in sync."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_wave2_review_memory_agrees_without_implying_activation():
    records = [json.loads((ROOT / path).read_text(encoding='utf-8'))['teaching_style_wave2']
               for path in ('tools/archetype_compiler/rlasm_method.json',
                            'tools/archetype_compiler/high_quality_building_memory.json')]
    assert records[0] == records[1]
    record = records[0]
    assert record['method'] == 'RLASM v6.1'
    assert record['review_scope'] == 'holistic_architectural_clay'
    assert record['seed_activation'] is False
    assert record['runtime_integration'] == 'NOT TESTED'
    workshop = record['candidates']['workshop']
    assert workshop['model_sha256'] == '9bb30f08a744b62325e012ba52ccc57ce7cd65b5b753774af5e8c145733ab648'
    assert workshop['review_sha256'] == '87d090f2a1037a579ff43558cbbead3d7cc31080dabcc76bf22bb9415a50433f'
    assert workshop['unresolved_p0'] == workshop['unresolved_p1'] == 0
    document = (ROOT / record['evidence']).read_text(encoding='utf-8')
    assert workshop['model_sha256'] in document
    assert 'NOT TESTED' in document
