"""Exercise source binding, complete exports and preservation of reviewed output."""
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil

import pytest

from tools.planning_history.build_data import REVIEWED_INPUTS, build, write_outputs


def test_exports_all_current_and_candidate_records_without_activating_candidates():
    result=build()
    assert len(result['history']['lessons'])==196
    assert len(result['archetypes'])==201
    assert len(result['sourceCoverage'])==521
    assert sum(r['source_library_family'] for r in result['sourceCoverage'])==497
    assert sum(not r['source_library_family'] for r in result['sourceCoverage'])==24
    assert sum(r['status']=='held' for r in result['archetypes'])==8
    assert sum(r['scope']=='offline_review_candidate' for r in result['archetypes'])==5
    assert sum(r['current_exact_choices'] for r in result['sourceCoverage'])==196
    assert sum(r['scope']=='source_only_unreviewed' for r in result['sourceCoverage'])==343
    assert 'bauhaus_design_workshop' not in result['history']['lessons']
    assert all(not r['construction_year'] for r in result['archetypes'])


@pytest.mark.parametrize('mutation',['unlocked_bytes','relocked_revision','duplicate','unknown_era',
    'unknown_source','held_claim','candidate_activation','candidate_duplicate','candidate_rebound','wrong_base'])
def test_changed_inputs_need_fresh_review_and_cannot_rebind_contracts(tmp_path,mutation):
    review=tmp_path/'inputs';shutil.copytree(REVIEWED_INPUTS,review)
    assignments=json.loads((review/'assignments.json').read_text(encoding='utf-8'))
    candidates=json.loads((review/'candidates.json').read_text(encoding='utf-8'))
    lock=json.loads((review/'evidence-lock.json').read_text(encoding='utf-8'))
    if mutation=='unlocked_bytes':
        with (review/'framework.json').open('a',encoding='utf-8') as f:f.write(' ')
    else:
        row=assignments['records'][0]
        if mutation=='relocked_revision':row['modelRevision']='unreviewed'
        elif mutation=='duplicate':assignments['records'].append(dict(row))
        elif mutation=='unknown_era':row['eraIds']=['invented']
        elif mutation=='unknown_source':row['sourceIds']=['invented']
        elif mutation=='held_claim':next(r for r in assignments['records'] if r['status']=='held')['eraIds']=['postwar']
        elif mutation=='candidate_activation':candidates['records'][0]['runtimeActivation']=True
        elif mutation=='candidate_duplicate':candidates['records'].append(dict(candidates['records'][0]))
        elif mutation=='candidate_rebound':candidates['records'][0]['modelSha256']='f'*64
        elif mutation=='wrong_base':lock['baseAuditSha256']='0'*64
        for name,data in [('assignments.json',assignments),('candidates.json',candidates)]:
            (review/name).write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            lock['inputs'][name]=hashlib.sha256((review/name).read_bytes()).hexdigest()
        (review/'evidence-lock.json').write_text(json.dumps(lock),encoding='utf-8')
    with pytest.raises(ValueError):build(review)


def test_output_is_deterministic_unicode_csv_and_refuses_existing_directory(tmp_path):
    target=tmp_path/'new';summary=write_outputs(target)
    data=json.loads((target/'cataloguePlanningHistory.json').read_text(encoding='utf-8'))
    assert data==build()['history']
    content=(target/'planning-history-archetypes-2026-10-25.csv').read_bytes()
    assert content.startswith(b'\xef\xbb\xbf')
    rows=list(csv.DictReader(io.StringIO(content.decode('utf-8-sig'))))
    assert len(rows)==201 and any('Montréal' in r['canadian_context'] for r in rows)
    assert summary['currentChoices']==196
    before={p.name:p.read_bytes() for p in target.iterdir()}
    with pytest.raises(FileExistsError):write_outputs(target)
    assert before=={p.name:p.read_bytes() for p in target.iterdir()}
