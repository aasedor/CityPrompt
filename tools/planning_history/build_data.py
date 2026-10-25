"""Reproduce finite reviewed history metadata and research exports, never models."""
from pathlib import Path
import argparse
import csv
from datetime import date
import hashlib
import io
import json
import re
from urllib.parse import urlparse

from tools.catalogue_teaching.build_data import REVIEWED_INPUTS as BASE_INPUTS, reviewed_inputs
from tools.planning_history.contracts import validate_assignments

ROOT=Path(__file__).resolve().parents[2]
REVIEWED_INPUTS=Path(__file__).resolve().parent/'reviewed-inputs'
INPUT_NAMES=('framework.json','assignments.json','candidates.json')


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_framework(framework):
    if framework.get('schema')!='cityprompt.planning-history-framework@1':
        raise ValueError('Unknown history framework schema')
    as_of=date.fromisoformat(framework['asOf'])
    for order_key,key in (('eraOrder','eras'),('planningOrder','planning')):
        order=framework[order_key]
        if len(order)!=len(set(order)) or set(order)!=set(framework[key]):
            raise ValueError(f'Invalid {order_key}')
    for key in ('eras','planning','styles'):
        for ident,definition in framework[key].items():
            if not definition.get('label') or not definition.get('sourceIds'):
                raise ValueError(f'Missing definition/source: {key}/{ident}')
            if not set(definition['sourceIds'])<=framework['sources'].keys():
                raise ValueError(f'Unknown definition source: {key}/{ident}')
    for ident,source in framework['sources'].items():
        url=urlparse(source['url'])
        if url.scheme not in ('http','https') or not url.netloc or not source.get('label'):
            raise ValueError(f'Invalid research source: {ident}')
        if source.get('accessed') and date.fromisoformat(source['accessed'])>as_of:
            raise ValueError(f'Future source access date: {ident}')


def _validate_candidates(candidates,framework):
    # These are existing exact-byte approval records, independent of the new
    # history author's editable inputs. A new model needs a fresh context review.
    method=json.loads((ROOT/'tools/archetype_compiler/rlasm_method.json').read_text(encoding='utf-8'))
    pilot=method['teaching_style_local_pilot'];wave=method['teaching_style_wave2']['candidates']
    approved={'prairie_school_house':pilot['model_sha256'],
        'postmodern_neighbourhood_library':pilot['second_model_sha256'],
        'bauhaus_design_workshop':wave['workshop']['model_sha256'],
        'destijl_artist_studio':wave['destijl']['model_sha256'],
        'mughal_reading_pavilion':wave['pavilion']['model_sha256']}
    variants={'prairie_school_house':'roman_brick_hip_roof',
        'postmodern_neighbourhood_library':'broken_pediment_reading_room',
        'bauhaus_design_workshop':'glazed_studio_low_wing',
        'destijl_artist_studio':'primary_planes_glazed_studio',
        'mughal_reading_pavilion':'cusped_arcade_central_dome'}
    for record in method.get('housing_teaching_batch',{}).get('candidates',{}).values():
        approved[record['archetype_id']]=record['model_sha256']
        variants[record['archetype_id']]=record['variant_id']
    ids=[r['archetypeId'] for r in candidates]
    if len(ids)!=len(set(ids)) or set(ids)!=set(approved):
        raise ValueError('Candidate coverage differs from the exact independently reviewed originals')
    for row in candidates:
        if row.get('runtimeActivation') is not False or row.get('status')!='offline_review_candidate':
            raise ValueError('Research candidates must remain outside runtime')
        if not re.fullmatch('[0-9a-f]{64}',row.get('modelSha256','')) or row['modelSha256']!=approved[row['archetypeId']]:
            raise ValueError('Candidate history is not bound to the independently reviewed model')
        if row.get('variantId')!=variants[row['archetypeId']]:
            raise ValueError('Candidate history cannot be rebound to an unreviewed sibling variant')
        if row.get('constructionYear') is not None or row.get('dateBasis')!='approximate_design_association':
            raise ValueError('A candidate cannot acquire an invented construction year')
        for field,key in (('eraIds','eras'),('planningIds','planning'),('sourceIds','sources')):
            if not set(row[field])<=framework[key].keys():
                raise ValueError(f'Unknown candidate {field}')


def load_reviewed_inputs(review_dir=REVIEWED_INPUTS):
    review_dir=Path(review_dir)
    lock=json.loads((review_dir/'evidence-lock.json').read_text(encoding='utf-8'))
    if lock.get('schema')!='cityprompt.planning-history-evidence@1' or set(lock['inputs'])!=set(INPUT_NAMES):
        raise ValueError('Invalid history evidence lock')
    audit,inventory,_=reviewed_inputs(BASE_INPUTS/'audit.json',BASE_INPUTS/'inventory.json')
    if _sha(BASE_INPUTS/'audit.json')!=lock['baseAuditSha256'] or _sha(BASE_INPUTS/'inventory.json')!=lock['baseInventorySha256']:
        raise ValueError('History evidence must remain bound to the reviewed base pair')
    data={}
    for name in INPUT_NAMES:
        if _sha(review_dir/name)!=lock['inputs'][name]:
            raise ValueError(f'{name} changed; historical interpretations need a fresh review')
        data[name]=json.loads((review_dir/name).read_text(encoding='utf-8'))
    framework=data['framework.json'];records=data['assignments.json']['records'];candidates=data['candidates.json']['records']
    _validate_framework(framework)
    validate_assignments(framework,records,audit,inventory)
    _validate_candidates(candidates,framework)
    return framework,records,candidates,audit,lock


def build(review_dir=REVIEWED_INPUTS):
    """Return current-only UI data and separate exact-choice/family matrices."""
    framework,records,candidates,audit,lock=load_reviewed_inputs(review_dir)
    choices={c['placement_id']:c for c in audit['choices']}
    style_labels={**{k:v['label'] for k,v in audit['styles'].items()},
                  **{k:v['label'] for k,v in framework['styles'].items()}}
    def labels(ids,key):return '; '.join(framework[key][i]['label'] for i in ids)
    def sources(ids):return '; '.join(framework['sources'][i]['url'] for i in ids)
    archetypes=[]
    for row in records:
        original=choices[row['placementId']]
        archetypes.append(dict(record_id=row['placementId'],scope='current_exact_choice',status=row['status'],
            domain=row['domain'],name=original['name'],archetype_id=row['archetypeId'],variant_id=row['variantId'],
            model_revision_or_sha256=row['modelRevision'] or '',use=original['current_use_group'],form=row['formId'],
            aesthetic='; '.join(style_labels[i] for i in row['styleIds']),era=labels(row['eraIds'],'eras'),
            design_period=row['designPeriod'],construction_year='',date_basis=row['dateBasis'],
            planning_connections=labels(row['planningIds'],'planning'),canadian_context=row['canadianContext'],
            international_context=row['internationalContext'],interpretation_basis=row['eraRationale'],
            design_evidence=row['designEvidence'],source_urls=sources(row['sourceIds'])))
    for row in candidates:
        archetypes.append(dict(record_id=row['id'],scope=row['status'],status=row['status'],domain='building',
            name=row['title'],archetype_id=row['archetypeId'],variant_id=row['variantId'],
            model_revision_or_sha256=row['modelSha256'],use=row['typeLabel'],form=row['formId'],
            aesthetic=row['styleLabel'],era=labels(row['eraIds'],'eras'),design_period=row['designPeriod'],
            construction_year='',date_basis=row['dateBasis'],planning_connections=labels(row['planningIds'],'planning'),
            canadian_context=row['canadianContext'],international_context=row['internationalContext'],
            interpretation_basis=row['eraRationale'],design_evidence='Original generated reference; exact GLB independently reviewed; uninstalled.',
            source_urls=sources(row['sourceIds'])))
    coverage=[]
    families=[dict(family,source_library_family=True) for family in audit['source_families']]
    source_keys={(f['domain'],f['archetype_id']) for f in families}
    for row in records:
        key=(row['domain'],row['archetypeId'])
        if key not in source_keys:
            families.append(dict(domain=key[0],archetype_id=key[1],title=choices[row['placementId']]['name'],
                variant_count=None,source_library_family=False))
            source_keys.add(key)
    for family in families:
        linked=[r for r in records if (r['domain'],r['archetypeId'])==(family['domain'],family['archetype_id'])]
        held=sum(r['status']=='held' for r in linked)
        scope=('source_only_unreviewed' if not linked else 'held_current_variants' if held==len(linked)
               else 'has_classified_exact_variants' if family['source_library_family'] else 'current_only_exact_family')
        coverage.append(dict(domain=family['domain'],archetype_id=family['archetype_id'],title=family['title'],
            scope=scope,source_library_family=family['source_library_family'],
            source_variant_count=family['variant_count'],current_exact_choices=len(linked),
            classified_exact_choices=len(linked)-held,held_exact_choices=held,
            reviewed_placement_ids='; '.join(r['placementId'] for r in linked),
            eras_for_listed_exact_variants_only=labels(dict.fromkeys(e for r in linked for e in r['eraIds']),'eras'),
            planning_for_listed_exact_variants_only=labels(dict.fromkeys(e for r in linked for e in r['planningIds']),'planning'),
            boundary='Tags apply only to listed exact variants. Other source variants await review.'))
    summary=dict(currentChoices=len(records),classifiedChoices=sum(r['status']=='classified' for r in records),
        heldChoices=sum(r['status']=='held' for r in records),offlineCandidates=len(candidates),
        sourceFamilies=len(audit['source_families']),coverageFamilies=len(coverage),
        currentOnlyFamilies=sum(not c['source_library_family'] for c in coverage),
        sourceOnlyFamilies=sum(c['scope']=='source_only_unreviewed' for c in coverage),
        eras=len(framework['eras']),planningDefinitions=len(framework['planning']),sources=len(framework['sources']))
    actual={key:summary[key] for key in lock['scope']}
    expected_rows=lock['scope']['currentChoices']+lock['scope']['offlineCandidates']
    if actual!=lock['scope'] or len(archetypes)!=expected_rows or sum(c['current_exact_choices'] for c in coverage)!=len(records):
        raise ValueError('Reviewed scope/coverage mismatch')
    history=dict(schema='cityprompt.planning-history@1',asOf=framework['asOf'],scope=framework['scope'],
        evidence=dict(sourceCommit=lock['sourceCommit'],baseAuditSha256=lock['baseAuditSha256'],
            baseInventorySha256=lock['baseInventorySha256'],inputSha256=lock['inputs']),
        eraOrder=framework['eraOrder'],eras=framework['eras'],planningOrder=framework['planningOrder'],
        planning=framework['planning'],styles=framework['styles'],sources=framework['sources'],
        lessons={r['placementId']:r for r in records})
    bibliography=[dict(id=k,**s) for k,s in framework['sources'].items()]
    return dict(history=history,archetypes=archetypes,sourceCoverage=coverage,bibliography=bibliography,summary=summary)


def _csv_bytes(rows):
    out=io.StringIO(newline='');columns=list(dict.fromkeys(k for row in rows for k in row))
    writer=csv.DictWriter(out,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf-8-sig')


def write_outputs(output_dir,review_dir=REVIEWED_INPUTS):
    result=build(review_dir);output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=False)
    blobs={'cataloguePlanningHistory.json':(json.dumps(result['history'],ensure_ascii=False,indent=2)+'\n').encode('utf-8'),
        'planning-history-archetypes-2026-10-25.csv':_csv_bytes(result['archetypes']),
        'planning-history-source-coverage-2026-10-25.csv':_csv_bytes(result['sourceCoverage']),
        'planning-history-bibliography-2026-10-25.csv':_csv_bytes(result['bibliography']),
        'verification.json':(json.dumps(result['summary'],indent=2)+'\n').encode('utf-8')}
    for name,content in blobs.items():
        with (output_dir/name).open('xb') as out:out.write(content)
    return result['summary']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(write_outputs(args.output_dir)))


if __name__=='__main__':main()
