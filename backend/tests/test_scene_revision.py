import pytest

from app.services.scene_revision import compiled_scene_revision_sha256


CLAIMS = [
    {
        "zone_id": "park-1",
        "source_hash": "a" * 64,
        "representation_hash": "b" * 64,
    },
    {
        "zone_id": "street-1",
        "source_hash": "c" * 64,
        "representation_hash": "d" * 64,
    },
]


def test_boundaryless_scene_revision_is_stable_and_order_independent():
    first = compiled_scene_revision_sha256(CLAIMS, None)
    second = compiled_scene_revision_sha256(reversed(CLAIMS), None)

    assert first == second
    assert len(first) == 64


def test_scene_revision_still_requires_physical_zone_claims():
    with pytest.raises(ValueError, match="zone claims"):
        compiled_scene_revision_sha256([], None)


def test_authored_surface_source_changes_scene_revision_without_compiling_an_archetype():
    surfaces = [{"zone_id": "surface-1", "source_hash": "a" * 64},
                {"zone_id": "surface-2", "source_hash": "b" * 64}]
    first = compiled_scene_revision_sha256(CLAIMS, None, authored_surface_claims=surfaces)
    assert first == compiled_scene_revision_sha256(CLAIMS, None, authored_surface_claims=reversed(surfaces))
    assert first != compiled_scene_revision_sha256(CLAIMS, None)
    surfaces[0]["source_hash"] = "c" * 64
    assert first != compiled_scene_revision_sha256(CLAIMS, None, authored_surface_claims=surfaces)
