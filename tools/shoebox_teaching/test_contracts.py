"""Protect physical roof/entry relationships and complete replay inputs."""
import importlib.util
import json
from pathlib import Path

import pytest
from tools.housing_teaching.contracts import validate_card

HERE=Path(__file__).resolve().parent


def test_basic_card_separates_form_style_era_and_tenure():
    assert (HERE/'card.json').is_file(), 'Missing authored shoebox teaching card'
    card=json.loads((HERE/'card.json').read_text(encoding='utf-8'))
    validate_card(card)
    assert card['archetypeId']=='montreal_shoebox_house'
    assert card['form']!=card['aesthetic']
    assert '1900' in card['designPeriod'] and '1940' in card['designPeriod']
    assert 'montreal.ca' in card['sourceUrls'][0]


def contracts():
    assert (HERE/'contracts.py').is_file(), 'Missing source/replay/roof contracts'
    spec=importlib.util.spec_from_file_location('shoebox_contracts',HERE/'contracts.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_flat_roof_has_positive_rearward_fall_and_occupied_clearance():
    d=contracts().datums()
    assert 0 < (d['roof_front_top']-d['roof_rear_top'])/d['depth'] < .03
    assert d['roof_rear_top']-d['roof_thickness']-d['floor'] > 2.4
    assert d['parapet_top']>d['roof_front_top']
    assert d['entry_levels'][-1]==pytest.approx(d['floor'])
    assert max(d['entry_levels'][0],*(b-a for a,b in zip(d['entry_levels'],d['entry_levels'][1:])))<=.18


def test_replay_overlay_includes_consumed_json_and_sources(tmp_path):
    c=contracts();repo=tmp_path/'repo';repo.mkdir()
    inputs={'tools/shoebox_teaching/card.json':'{"title":"original card"}',
            'tools/shoebox_teaching/source-lock.json':'{"source":"exact"}',
            'tools/shoebox_teaching/build.py':'# exact builder\n',
            'frontend/public/archetypes/buildings/shoebox-teaching/front.png':'exact original pixels'}
    for name,content in inputs.items():
        p=repo/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
    out=tmp_path/'replay'
    manifest=c.archive_replay(repo,out,inputs)
    for name,content in inputs.items():assert (out/name).read_text()==content
    assert len(manifest['files'])==4
    with pytest.raises(FileExistsError):c.archive_replay(repo,out,inputs)
    # Reproduction must fail closed when a consumed input disappears.
    (repo/'tools/shoebox_teaching/source-lock.json').unlink()
    with pytest.raises(FileNotFoundError):c.archive_replay(repo,tmp_path/'missing',inputs)


def test_replay_rejects_paths_outside_the_repository(tmp_path):
    repo=tmp_path/'repo';repo.mkdir();(tmp_path/'private.txt').write_text('not a build input')
    with pytest.raises(ValueError):contracts().archive_replay(repo,tmp_path/'overlay',['../private.txt'])


def test_source_identity_and_all_four_compatible_roles_are_locked():
    assert (HERE/'source-lock.json').is_file(), 'Missing exact source lock'
    rows=json.loads((HERE/'source-lock.json').read_text(encoding='utf-8'))
    assert {r['role'] for r in rows}=={'front','oblique','top','rear_oblique'}
    assert all(r['archetype_id']=='montreal_shoebox_house' and
               r['variant_id']=='red_brick_flat_roof_cornice' and
               len(r['sha256'])==64 and r['bytes']>0 for r in rows)
