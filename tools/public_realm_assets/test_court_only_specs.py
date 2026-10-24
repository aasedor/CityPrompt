"""Student building blocks must remain independent of complete sports gardens."""
import copy
import pytest
from court_specs import COURTS
from court_only_specs import COURT_ONLY_KINDS, court_only_recipe


def test_bounded_batch_and_independent_recipes():
    before = copy.deepcopy(COURTS)
    assert set(COURT_ONLY_KINDS) == {'basketball', 'tennis', 'pickleball', 'beach_volleyball'}
    for kind in COURT_ONLY_KINDS:
        recipe = court_only_recipe(kind)
        assert recipe['dimensions_m'] == recipe['module_m']
        assert all(p < m for p, m in zip(recipe['playing_m'], recipe['module_m']))
        assert recipe['include_enclosure'] is False
        recipe['playing_m'][0] = -1
        assert court_only_recipe(kind)['playing_m'][0] > 0
    assert COURTS == before
    assert COURTS['basketball']['dimensions_m'] == [41, 56]


def test_native_dimensions_include_equipment_and_playing_reserve():
    basketball = court_only_recipe('basketball')
    assert basketball['playing_m'] == [15, 28]
    assert basketball['module_m'] == [21, 36]
    assert basketball['hoop_height_m'] == 3.05
    tennis = court_only_recipe('tennis')
    assert tennis['module_m'] == [18.3, 36.6]
    pickleball = court_only_recipe('pickleball')
    assert pickleball['playing_m'] == pytest.approx([20 * .3048, 44 * .3048])
    assert pickleball['module_m'][0] >= 34 * .3048
    assert pickleball['module_m'][1] >= 64 * .3048
    assert pickleball['kitchen_m'] == pytest.approx(7 * .3048)
    assert court_only_recipe('beach_volleyball')['module_m'] == [14, 22]


def test_unknown_sport_is_not_silently_substituted():
    with pytest.raises(ValueError, match='Unsupported court-only sport'):
        court_only_recipe('padel')
