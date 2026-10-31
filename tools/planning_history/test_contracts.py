"""Historical claims must remain bound to reviewed, exact asset identities."""
from copy import deepcopy

import pytest

from tools.planning_history.contracts import validate_assignments


@pytest.fixture
def evidence():
    framework={'eras':{'postwar':{}},'planning':{'missing_middle':{},'vancouverism':{}},
               'styles':{},'sources':{'history':{'url':'https://example.org/history'}}}
    audit={'styles':{},'choices':[
        {'placement_id':'fourplex','domain':'building','archetype_id':'four','variant_id':'v1','confidence':'High'},
        {'placement_id':'held','domain':'building','archetype_id':'conflict','variant_id':'v2','confidence':'Review'}]}
    inventory={'choices':[{'domain':'building','option':{'id':'four'},'placements':[
        {'id':'fourplex','model':{'variantId':'v1','method':'RLASM 6.1','revision':'exact'}}]},
        {'domain':'building','option':{'id':'conflict'},'placements':[
        {'id':'held','model':{'variantId':'v2','method':'RLASM 6.1','revision':'other'}}]}]}
    records=[dict(placementId='fourplex',domain='building',archetypeId='four',variantId='v1',modelMethod='RLASM 6.1',
                  modelRevision='exact',status='classified',eraIds=['postwar'],planningIds=['missing_middle'],
                  styleIds=[],sourceIds=['history'],formId='fourplex',constructionYear=None,
                  dateBasis='approximate_design_association',designPeriod='A postwar design reference',
                  eraRationale='The authored design is interpreted in this period.'),
             dict(placementId='held',domain='building',archetypeId='conflict',variantId='v2',modelMethod='RLASM 6.1',
                  modelRevision='other',status='held',eraIds=[],planningIds=[],styleIds=[],sourceIds=['history'],
                  formId='unconfirmed',constructionYear=None,dateBasis='approximate_design_association',
                  designPeriod='Reference identity needs checking',eraRationale='Existing conflict remains held.')]
    return framework,records,audit,inventory


def test_accepts_complete_exact_records_with_explicitly_held_identity(evidence):
    validate_assignments(*evidence)


@pytest.mark.parametrize('field,value',[('variantId','new'),('modelRevision','changed'),
    ('modelMethod','different'),('archetypeId','sibling'),('domain','park_plaza')])
def test_rejects_unreviewed_contract_change(evidence,field,value):
    framework,records,audit,inventory=deepcopy(evidence);records[0][field]=value
    with pytest.raises(ValueError,match='contract'):validate_assignments(framework,records,audit,inventory)


@pytest.mark.parametrize('mutation',['missing','duplicate','held_claim','invented_date','unknown_era','unknown_source','wrong_form'])
def test_rejects_misleading_or_incomplete_classification(evidence,mutation):
    framework,records,audit,inventory=deepcopy(evidence)
    if mutation=='missing':records.pop()
    elif mutation=='duplicate':records.append(deepcopy(records[0]))
    elif mutation=='held_claim':records[1]['eraIds']=['postwar']
    elif mutation=='invented_date':records[0]['constructionYear']=1955
    elif mutation=='unknown_era':records[0]['eraIds']=['unknown']
    elif mutation=='unknown_source':records[0]['sourceIds']=['unread']
    elif mutation=='wrong_form':records[0]['formId']='single_family'
    with pytest.raises(ValueError):validate_assignments(framework,records,audit,inventory)


def test_vancouverism_requires_residential_tower_and_podium_component(evidence):
    framework,records,audit,inventory=deepcopy(evidence)
    records[0].update(planningIds=['vancouverism'],formId='office_tower')
    with pytest.raises(ValueError,match='Vancouverism'):validate_assignments(framework,records,audit,inventory)
