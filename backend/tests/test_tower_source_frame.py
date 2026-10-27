"""An asymmetric bridge belongs to one shared source frame across all floors."""
from dataclasses import replace

import pytest

from app.services.lego_assembly import AssemblyRequest, ModuleDescriptor, plan_vertical_assembly


def modules(origin=(0,15.5)):
    base=ModuleDescriptor(id='podium',name='podium',model_url='/podium.glb',family='plus15-frame',role='podium',
        width_m=52,depth_m=83,height_m=14,archetype_ids=('plus15',),reuse_keys=(),min_floors=10,max_floors=35,
        occupied_storeys=1,source_variant_id='plus15',generation_archetype_id='plus15',
        allow_inset_footprint=True,delivery_format='architectural_clay_module_v1',
        placement_contract={'mode':'authored_storey_program','source_frame_origin_xy_m':list(origin)})
    return [base,replace(base,id='floor',role='floor',width_m=37.7,depth_m=37.7,height_m=3.65,repeatable_z=True),
        replace(base,id='roof',role='roof',width_m=40,depth_m=40,height_m=10.26,occupied_storeys=0)]


@pytest.mark.parametrize('width,depth,expected',[(52,83,[0,-15.5]),(83,52,[15.5,0])])
def test_one_source_origin_centres_bridge_and_tower_together(width,depth,expected):
    plan=plan_vertical_assembly(modules(),AssemblyRequest(width,depth,10,archetype_id='plus15'),allow_forced_fit=False)
    assert all(item['position'][:2]==pytest.approx(expected) for item in plan['instances'])
    assert all(item['scale']==[1,1,1] for item in plan['instances'])
    assert plan['assembled_height_m']==pytest.approx(57.11)


def test_ordinary_modules_keep_existing_placement_when_no_source_origin_is_declared():
    plain=[replace(module,placement_contract=None) for module in modules()]
    plan=plan_vertical_assembly(plain,AssemblyRequest(52,83,10,archetype_id='plus15'),allow_forced_fit=False)
    assert all(item['position'][:2]==[0,0] for item in plan['instances'])


@pytest.mark.parametrize('origin',[(0,float('nan')),(0,15.5,2),('invalid',0)])
def test_invalid_authored_origins_cannot_create_nonfinite_saved_instances(origin):
    with pytest.raises(ValueError):
        plan_vertical_assembly(modules(origin),AssemblyRequest(52,83,10,archetype_id='plus15'),allow_forced_fit=False)
