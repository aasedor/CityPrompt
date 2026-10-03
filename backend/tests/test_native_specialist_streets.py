import pytest
from app.services.native_specialist_streets import CONTRACTS,validate_specialist_properties,validate_specialist_ground

def props(variant,length):
    parent,width,_,_=CONTRACTS[variant]
    return dict(road_selected_variant_id=variant,road_archetype_id=parent,width=width,plan_centerline=[[0,0],[0,length/111320]])

@pytest.mark.parametrize('variant',CONTRACTS)
def test_specialist_limits_identity_legacy_and_straightness(variant):
    _,_,minimum,maximum=CONTRACTS[variant]
    for length in (minimum,maximum):validate_specialist_properties(props(variant,length))
    for length in (minimum-1,maximum+1):
        with pytest.raises(ValueError,match='long'):validate_specialist_properties(props(variant,length))
    changed=props(variant,minimum);changed['width']=20
    with pytest.raises(ValueError,match='section'):validate_specialist_properties(changed)
    changed['validation_fixed_fixture']=True;validate_specialist_properties(changed)
    bent=props(variant,minimum);bent['plan_centerline'].insert(1,[1/111320,minimum/2/111320])
    with pytest.raises(ValueError,match='straight'):validate_specialist_properties(bent)

@pytest.mark.parametrize('variant',CONTRACTS)
def test_specialist_prepared_ground(variant):
    p=props(variant,300)
    with pytest.raises(ValueError,match='prepared'):validate_specialist_ground(p,{})
    validate_specialist_ground(p,dict(community_3d_mask_existing_tiles=True))
