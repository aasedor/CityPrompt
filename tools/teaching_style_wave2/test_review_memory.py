"""Keep exact teaching review evidence and activation boundaries in sync."""
import json
from pathlib import Path

import pytest

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


@pytest.mark.parametrize('family,model_sha,review_sha',[
    ('destijl','770f5eb08631a3fd3de71d43385d20049d18fe6f664f5b55dd13074ce8f70e15',
     'd13c6afb12156b3b5ce77bba2444f9f4e51fea8ebe9ef7a21db5b9d3e9090040'),
    ('pavilion','21ca71237504d6804a2eba435c25c0f4379793b68ad6ab9e6ff6450a7e3596c5',
     '76af7881090b0b6160e5c6a941291e046d9c850b79fc147ab89531e975f88540'),
])
def test_remaining_exact_review_records_are_bound_to_the_handoff(family,model_sha,review_sha):
    records=[json.loads((ROOT/path).read_text(encoding='utf-8'))['teaching_style_wave2']
             for path in ('tools/archetype_compiler/rlasm_method.json',
                          'tools/archetype_compiler/high_quality_building_memory.json')]
    assert records[0] == records[1]
    entry=records[0]['candidates'][family]
    assert entry['model_sha256'] == model_sha
    assert entry['review_sha256'] == review_sha
    assert entry['unresolved_p0'] == entry['unresolved_p1'] == 0
    assert model_sha in (ROOT/records[0]['evidence']).read_text(encoding='utf-8')
