from __future__ import annotations

from catalog_coverage import Candidate, _best_candidates, _normalise_catalogue, _summary, _target_rows


def test_live_frontend_catalogue_wrapper_and_field_names_are_supported():
    rows = _normalise_catalogue({"archetypes": [{
        "id": "brick_hall",
        "title": "Brick Hall",
        "variants": [{"id": "brick_hall_red", "label": "Red"}],
    }]})

    assert rows[0]["archetypeId"] == "brick_hall"
    assert rows[0]["archetypeLabel"] == "Brick Hall"


def test_parent_fallback_does_not_count_as_named_variant_coverage():
    catalogue = [{
        "archetypeId": "brick_hall",
        "archetypeLabel": "Brick Hall",
        "developmentType": "mixed_use",
        "variants": [
            {"id": "brick_hall_red", "label": "Red"},
            {"id": "brick_hall_dark", "label": "Dark"},
        ],
    }]
    parent = Candidate(
        archetype_id="brick_hall",
        variant_id=None,
        family="brick-hall",
        manifest_path="parent.json",
        validation="pass",
        render_locked=True,
        modified_at=1.0,
    )

    rows = _target_rows(catalogue, _best_candidates([parent]), {}, {"brick-hall"})

    assert [row["state"] for row in rows] == ["imported", "missing", "missing"]
    assert rows[1]["family"] is None
    assert rows[2]["family"] is None


def test_exact_variant_tracks_validation_import_and_live_review_independently():
    catalogue = [{
        "archetypeId": "brick_hall",
        "archetypeLabel": "Brick Hall",
        "variants": [{"id": "brick_hall_red", "label": "Red"}],
    }]
    variant = Candidate(
        archetype_id="brick_hall",
        variant_id="brick_hall_red",
        family="brick-hall-red-v1",
        manifest_path="variant.json",
        validation="pass",
        render_locked=True,
        modified_at=2.0,
    )

    rows = _target_rows(
        catalogue,
        _best_candidates([variant]),
        {"brick-hall-red-v1": "keeper_live_cityprompt"},
        {"brick-hall-red-v1"},
    )
    summary = _summary(rows, candidate_count=1, imported_count=1)

    assert rows[0]["state"] == "missing"
    assert rows[1]["state"] == "live_qa"
    assert summary["coverage"]["variant"]["total"] == 1
    assert summary["coverage"]["variant"]["validated_or_better"] == 1
    assert summary["coverage"]["variant"]["live_qa"] == 1


def test_best_candidate_prefers_validation_then_render_lock_then_recency():
    rows = [
        Candidate("a", "v", "new-invalid", "a.json", "fail", True, 30.0),
        Candidate("a", "v", "valid-flat", "b.json", "pass", False, 20.0),
        Candidate("a", "v", "valid-renderlocked-old", "c.json", "pass", True, 10.0),
        Candidate("a", "v", "valid-renderlocked-new", "d.json", "pass", True, 15.0),
    ]

    selected = _best_candidates(rows)[("a", "v")]

    assert selected.family == "valid-renderlocked-new"
