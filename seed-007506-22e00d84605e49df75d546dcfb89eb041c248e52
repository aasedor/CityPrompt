"""Texture pipeline units: keyword -> texture_key mapping, prose coverage,
and the deterministic tileability post-processing in generate_textures.py.

Image-processing tests are skipped when Pillow/numpy are absent so the grammar
unit suite still runs on minimal boxes.
"""
from __future__ import annotations

import pytest

from compiler import _MATERIAL_KEYWORDS, compile_archetype, texture_anchor_table
from schema import BuildingGrammar, Materials

from test_compiler import payload_mixed_use_midrise


def test_every_keyword_maps_to_an_anchored_texture_key():
    anchors = texture_anchor_table()
    for keyword, _pbr, texture_key in _MATERIAL_KEYWORDS:
        assert texture_key in anchors, f"keyword {keyword!r} names unanchored texture {texture_key!r}"


def test_every_texture_key_has_generation_prose():
    pytest.importorskip("PIL")
    pytest.importorskip("numpy")
    from generate_textures import TEXTURE_PROSE

    anchors = texture_anchor_table()
    missing = sorted(set(anchors) - set(TEXTURE_PROSE))
    assert not missing, f"texture keys without prose: {missing}"
    orphans = sorted(set(TEXTURE_PROSE) - set(anchors))
    assert not orphans, f"prose for unknown texture keys: {orphans}"


def test_compile_assigns_texture_keys_from_prose():
    grammar = compile_archetype(payload_mixed_use_midrise())
    # "charcoal-black metal panel and textural corrugated steel" -> black metal first
    assert grammar.materials.primary.texture_key == "black_metal"
    # "warm natural wood soffits and accent bays"
    assert grammar.materials.secondary.texture_key == "natural_timber"
    # "membrane flat roofs and timber decking" must read as membrane, not timber
    assert grammar.materials.roof.texture_key == "roof_membrane"
    # glass palette never goes through the keyword table
    assert grammar.materials.glass.texture_key is None
    # slots that skip the keyword match still carry the schema-default textures
    assert grammar.materials.concrete.texture_key == "concrete"
    assert grammar.materials.green_roof.texture_key == "sedum_roof"


def test_texture_key_round_trips_through_grammar_dict():
    grammar = compile_archetype(payload_mixed_use_midrise())
    clone = BuildingGrammar.from_dict(grammar.to_dict())
    assert clone.materials.primary.texture_key == grammar.materials.primary.texture_key
    assert clone.materials.glass.texture_key is None


def test_no_keyword_match_means_flat_colour():
    payload = payload_mixed_use_midrise(
        facadeDetail={"primaryMaterial": "iridescent unobtainium scales"}
    )
    grammar = compile_archetype(payload)
    assert grammar.materials.primary.texture_key is None


def test_materials_defaults_validate():
    materials = Materials()
    materials.validate()  # texture_key slugs must pass validation


def test_cross_blend_makes_noise_tileable():
    pytest.importorskip("PIL")
    np = pytest.importorskip("numpy")
    from PIL import Image
    from generate_textures import cross_blend_tile, mirror_tile, seam_ratio

    rng = np.random.default_rng(7)
    # smooth blobs + a hard brightness ramp: rich interior, terrible wrap seam
    base = rng.integers(0, 255, (32, 32, 3), dtype=np.uint8)
    img = Image.fromarray(base).resize((256, 256), Image.BILINEAR)
    ramp = np.linspace(0, 80, 256)[None, :, None]
    img = Image.fromarray(np.clip(np.asarray(img) + ramp, 0, 255).astype(np.uint8))

    raw_ratio = seam_ratio(img)
    blended_ratio = seam_ratio(cross_blend_tile(img, feather=0.09))
    mirrored_ratio = seam_ratio(mirror_tile(img))
    assert blended_ratio < raw_ratio
    assert blended_ratio < 1.5, "cross-blend output must wrap about as smoothly as its interior"
    assert mirrored_ratio < 0.2, "mirror tiling is seamless by construction"


def test_derived_maps_have_expected_shape_and_range():
    pytest.importorskip("PIL")
    np = pytest.importorskip("numpy")
    from PIL import Image
    from generate_textures import DERIVED_SIZE, derive_normal, derive_roughness

    rng = np.random.default_rng(11)
    albedo = Image.fromarray(rng.integers(0, 255, (1024, 1024, 3), dtype=np.uint8))

    normal = np.asarray(derive_normal(albedo))
    assert normal.shape == (DERIVED_SIZE, DERIVED_SIZE, 3)
    assert normal[..., 2].mean() > 170, "normal map Z must dominate (mostly-flat surface)"

    rough = np.asarray(derive_roughness(albedo, base_roughness=0.7))
    assert rough.shape == (DERIVED_SIZE, DERIVED_SIZE)
    assert 0.3 < rough.mean() / 255 < 0.95
