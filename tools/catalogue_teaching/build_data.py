"""Build the finite teaching overlay from the preserved, individually authored audit.

Does not classify by keyword or modify any runtime asset/reference catalogue.
"""
from pathlib import Path
import argparse
import hashlib
import json


REVIEWED_INPUTS = Path(__file__).resolve().parent / 'reviewed-inputs'


def reviewed_inputs(audit_path, inventory_path):
    """Accept only the immutable pair that was actually reviewed together."""
    lock = json.loads((REVIEWED_INPUTS / 'evidence-lock.json').read_text(encoding='utf-8'))
    audit_bytes = audit_path.read_bytes()
    inventory_bytes = inventory_path.read_bytes()
    for label, data, key in [('audit', audit_bytes, 'auditSha256'),
                             ('inventory', inventory_bytes, 'inventorySha256')]:
        if hashlib.sha256(data).hexdigest() != lock[key]:
            raise ValueError(f'{label} does not match the reviewed evidence lock. '
                             'Changed inputs need a fresh teaching review before rebuilding.')
    return json.loads(audit_bytes), json.loads(inventory_bytes), lock


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', type=Path, default=REVIEWED_INPUTS / 'audit.json')
    parser.add_argument('--inventory', type=Path, default=REVIEWED_INPUTS / 'inventory.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    audit, inventory, evidence_lock = reviewed_inputs(args.audit, args.inventory)
    if audit['source_commit'] != evidence_lock['sourceCommit'] or inventory['sourceCommit'] != evidence_lock['sourceCommit']:
        raise ValueError('Source commit does not match the reviewed evidence lock.')
    assets = {a['id']: a for c in inventory['choices'] for a in c['placements']}
    contracts = {a['id']: (c['domain'], c['option']['id']) for c in inventory['choices'] for a in c['placements']}
    intro = ['new_urbanism', 'tod', 'garden_city', 'ecology', 'complete', 'auto']
    assert set(intro) <= audit['planning'].keys()
    labels = {s: c['student_style'] for c in audit['choices'] if c['confidence'] != 'Review' and c['domain'] == 'building'
              for s in c['proposed_style_ids'][:1]}
    styles = {key: dict(label=labels.get(key, value['label']), kind=value['kind'],
                       description=value['features'], designIdea=value['values'],
                       sourceIds=value['sources']) for key, value in audit['styles'].items()}
    planning_labels = dict(new_urbanism='New Urbanism', tod='Transit-oriented development',
                           garden_city='Garden City', ecology='Green infrastructure',
                           complete='Complete Streets', auto='Car-oriented layouts')
    planning = {key: dict(label=planning_labels[key], description=audit['planning'][key]['meaning'],
                         designIdea=audit['planning'][key]['values'],
                         componentLimit=audit['planning'][key]['limit'],
                         sourceIds=audit['planning'][key]['sources']) for key in intro}
    # Rechecked primary source for the process, not a single prescribed section.
    sources = {key: dict(label=value[0], url=value[1]) for key, value in audit['sources'].items()}
    sources['complete']['url'] = 'https://smartgrowthamerica.org/what-are-complete-streets/'
    lessons = {}
    for choice in audit['choices']:
        ident = choice['placement_id']; asset = assets[ident]
        if (asset['model']['variantId'] != choice['variant_id'] or
                contracts[ident] != (choice['domain'], choice['archetype_id']) or ident in lessons):
            raise ValueError(f'Identity does not match the reviewed evidence: {ident}')
        lessons[ident] = dict(domain=choice['domain'], archetypeId=choice['archetype_id'],
            variantId=choice['variant_id'], modelRevision=asset['model'].get('revision'),
            modelMethod=asset['model']['method'], typeLabel=choice['current_use_group'],
            styleIds=choice['proposed_style_ids'],
            planningIds=[p for p in choice['planning_ids'] if p in intro],
            confidence=choice['confidence'], referenceReviewed=bool(choice['reference_image']),
            rationale=choice['rationale'])
    result = dict(schema='cityprompt.catalogue-teaching@1', reviewedDate=audit['date'],
        scope='Introductory research classifications; does not grant model approval or planning certification',
        audit=dict(sourceCommit=audit['source_commit'],
                   sha256=evidence_lock['auditSha256'],
                   inventorySha256=evidence_lock['inventorySha256'],
                   sourceInventorySha256=evidence_lock['sourceInventorySha256']),
        introductoryPlanningIds=intro, styles=styles, planning=planning, sources=sources, lessons=lessons)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as out:
        json.dump(result, out, ensure_ascii=False, indent=2); out.write('\n')
    print(json.dumps(dict(lessons=len(lessons), styles=len(styles), planning=len(planning),
                         held=sum(v['confidence']=='Review' for v in lessons.values()))))


if __name__ == '__main__':
    main()
