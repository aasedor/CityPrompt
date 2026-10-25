"""Validate authored historical interpretations without inventing asset history."""


MISSING_MIDDLE_FORMS=frozenset({'duplex','triplex','fourplex','townhouse','stacked_townhouse',
    'cottage_court','courtyard_cluster','small_walkup','live_work'})


def validate_assignments(framework,records,audit,inventory):
    """Require complete reviewed identities and explicit, supported interpretations."""
    expected={c['placement_id']:c for c in audit['choices']}
    assets={a['id']:(c,a) for c in inventory['choices'] for a in c['placements']}
    ids=[r['placementId'] for r in records]
    if len(ids)!=len(set(ids)) or set(ids)!=set(expected):
        raise ValueError('History coverage must match every reviewed placement exactly once')
    for row in records:
        ident=row['placementId'];choice,asset=assets[ident];prior=expected[ident]
        contract=dict(domain=choice['domain'],archetypeId=choice['option']['id'],
            variantId=asset['model']['variantId'],modelMethod=asset['model']['method'],
            modelRevision=asset['model'].get('revision'))
        if any(row.get(k)!=v for k,v in contract.items()):
            raise ValueError(f'Exact history contract mismatch: {ident}')
        held=prior['confidence']=='Review'
        if row.get('status')!=('held' if held else 'classified'):
            raise ValueError(f'Existing review status must be preserved: {ident}')
        if held and any(row.get(k) for k in ('eraIds','planningIds','styleIds')):
            raise ValueError(f'Held identity cannot advertise historical claims: {ident}')
        if not held and not row.get('eraIds'):
            raise ValueError(f'Explicit era or context-dependent outcome required: {ident}')
        for key,allowed in (
            ('eraIds',framework['eras']),('planningIds',framework['planning']),
            ('styleIds',set(framework['styles'])|set(audit['styles'])),('sourceIds',framework['sources'])):
            values=row.get(key,[])
            if len(values)!=len(set(values)) or not set(values)<=set(allowed):
                raise ValueError(f'Invalid {key} reference: {ident}')
        if not row.get('sourceIds') or not row.get('eraRationale') or not row.get('designPeriod'):
            raise ValueError(f'Historical reasoning and sources required: {ident}')
        if row.get('constructionYear') is not None or row.get('dateBasis')!='approximate_design_association':
            raise ValueError(f'Design association cannot invent a construction date: {ident}')
        if 'missing_middle' in row['planningIds'] and row.get('formId') not in MISSING_MIDDLE_FORMS:
            raise ValueError(f'Missing middle requires a reviewed house-scale housing form: {ident}')
        if 'vancouverism' in row['planningIds'] and row.get('formId')!='residential_tower_podium':
            raise ValueError(f'Vancouverism requires a residential tower/podium component: {ident}')
