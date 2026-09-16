from unittest.mock import patch

import pytest

from app.api.v1.lego_assembly import _strict_locked_building_plan
from app.services.lego_assembly import AssemblyPlanningError, assert_authored_height


def test_legacy_height_and_rounded_native_height_remain_compatible():
    assert_authored_height({"assembled_height_m": 6.98001}, None)
    assert_authored_height({"assembled_height_m": 6.98001}, 6.98)


@pytest.mark.parametrize("requested", [10, 3, float("nan"), -1])
def test_incompatible_height_requires_massing_without_scaling(requested):
    plan = {"assembled_height_m": 6.98001, "instances": [{"scale": [1, 1, 1]}]}
    with pytest.raises(AssemblyPlanningError, match="requested height") as error:
        assert_authored_height(plan, requested)
    assert error.value.code == "family_incompatible"
    assert plan["instances"][0]["scale"] == [1, 1, 1]


def test_locked_recipe_recheck_enforces_the_saved_height_override():
    with patch("app.api.v1.lego_assembly.plan_vertical_assembly", return_value={"assembled_height_m": 7}):
        assert _strict_locked_building_plan([], "infill", (12, 16, 2, "rectangle", None), {})["assembled_height_m"] == 7
        with pytest.raises(AssemblyPlanningError):
            _strict_locked_building_plan(
                [], "infill", (12, 16, 2, "rectangle", None), {"development_height_override_m": 12}
            )
