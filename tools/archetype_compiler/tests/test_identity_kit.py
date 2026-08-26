"""Contract tests for the parametric signature assemblies.

The suite deliberately covers the two properties that the previous approaches
each failed:

* ``compiler.py`` derives dimensions but drops the catalogue's identity words —
  ``derive_signatures`` must recover them with citable evidence;
* the v98 ``locked_mesh_bundle`` graphs reproduce a reference exactly but only
  within 1 cm of their authored size — the bay graph must keep fixed assemblies
  at authored proportions while ordinary bays absorb width.

``identity_kit`` imports ``bpy``, so the geometry builders are only exercised
where the Blender module is installed. The bay graph, clearance ledger and
prose derivation are pure logic and carry the important guarantees.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

TOOL_DIR = Path(__file__).resolve().parents[1]
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

identity_kit = pytest.importorskip(
    "identity_kit", reason="requires the bpy module (pip install bpy) or Blender's Python"
)

BayGraph = identity_kit.BayGraph
FacadeReservations = identity_kit.FacadeReservations
Reservation = identity_kit.Reservation
ClearanceError = identity_kit.ClearanceError
derive_signatures = identity_kit.derive_signatures


def make_graph(width: float = 20.0, floors: int = 3) -> "identity_kit.BayGraph":
    return BayGraph.from_dimensions(width=width, depth=30.0, floor_height=5.0, floors=floors)


class TestBayGraph:
    def test_ends_and_entrance_are_semantic(self) -> None:
        graph = make_graph()
        assert graph.bays[0].role == "end"
        assert graph.bays[-1].role == "end"
        assert len(graph.of_role("entrance")) == 3

    def test_entrance_stays_centred(self) -> None:
        for width in (14.0, 17.5, 20.0, 25.0):
            graph = make_graph(width)
            x0, x1 = graph.span("entrance")
            assert (x0 + x1) / 2 == pytest.approx(0.0, abs=width / len(graph.bays) / 2)

    def test_ordinary_bays_absorb_width(self) -> None:
        """The failure this prevents: identity bays stretching with the parcel.

        Extra width becomes extra ordinary bays. The entrance never grows past
        its authored count, so the marquee keeps its proportion instead of
        spreading across the frontage.
        """
        narrow, wide = make_graph(14.0), make_graph(25.0)
        assert len(wide.bays) > len(narrow.bays)
        assert len(wide.of_role("ordinary")) > len(narrow.of_role("ordinary"))
        assert len(wide.of_role("entrance")) <= 3

    def test_narrow_frontage_clamps_the_entrance_rather_than_the_ends(self) -> None:
        """On a small parcel the entrance yields; the end conditions never do."""
        narrow = make_graph(14.0)
        assert len(narrow.of_role("end")) == 2
        assert len(narrow.of_role("entrance")) < 3

    def test_bay_width_stays_in_a_believable_band(self) -> None:
        for width in (14.0, 20.0, 25.0):
            graph = make_graph(width)
            assert all(2.4 <= bay.width <= 4.6 for bay in graph.bays)


class TestClearance:
    def test_same_plane_collision_is_an_error(self) -> None:
        ledger = FacadeReservations()
        ledger.claim(Reservation(-2, 2, 4, 8, "relief", y_near=0.0, y_far=0.2))
        with pytest.raises(ClearanceError):
            ledger.claim(Reservation(-1, 1, 5, 7, "cornice", y_near=0.0, y_far=0.2))

    def test_different_depth_planes_may_overlap_in_elevation(self) -> None:
        """A bracketed blade sign legitimately passes in front of a relief band."""
        ledger = FacadeReservations()
        ledger.claim(Reservation(-2, 2, 4, 8, "relief", y_near=0.0, y_far=0.2))
        assert ledger.claim(Reservation(-1, 1, 5, 7, "blade_sign", y_near=0.55, y_far=1.65))

    def test_non_strict_claim_reports_instead_of_raising(self) -> None:
        ledger = FacadeReservations()
        ledger.claim(Reservation(-2, 2, 4, 8, "relief", y_near=0.0, y_far=0.2))
        assert ledger.claim(Reservation(-1, 1, 5, 7, "band", y_near=0.0, y_far=0.2), strict=False) is False


class TestProseDerivation:
    PAYLOAD = {
        "description": "Grand movie palace with ornate marquee, terra cotta facade with "
                       "Mayan-inspired geometric relief, vertical blade sign, and atmospheric lobby.",
        "facadeDetail": {"secondaryMaterial": "illuminated marquee with chaser lights"},
        "roofDetail": {"form": "decorative parapet with vertical blade sign"},
    }

    def test_recovers_the_identity_words_the_dimension_compiler_drops(self) -> None:
        found = {item["type"] for item in derive_signatures(self.PAYLOAD)}
        assert {"marquee", "blade_sign", "relief_band", "ornamental_parapet"} <= found

    def test_every_signature_cites_its_catalogue_evidence(self) -> None:
        for item in derive_signatures(self.PAYLOAD):
            assert item["evidence"], f"{item['type']} has no citable source text"
            assert ":" in item["evidence"]

    def test_order_is_stable_and_back_to_front(self) -> None:
        types = [item["type"] for item in derive_signatures(self.PAYLOAD)]
        assert types.index("ornamental_parapet") < types.index("marquee")
        assert types.index("marquee") < types.index("blade_sign")

    def test_a_plain_archetype_declares_nothing(self) -> None:
        """No identity words must mean no invented features."""
        assert derive_signatures({"description": "Simple three-storey brick walk-up."}) == []

    def test_variant_overrides_the_parent_entry(self) -> None:
        payload = {
            "description": "Plain block.",
            "selectedVariant": {"description": "Corner shop with a decorative parapet."},
        }
        assert [item["type"] for item in derive_signatures(payload)] == ["ornamental_parapet"]


class TestStoreyParsing:
    def test_reads_numeric_ordinals(self) -> None:
        assert identity_kit.parse_storeys("wrought iron balconies at 2nd and 5th floors") == [2, 5]

    def test_reads_written_ordinals_near_a_floor_word(self) -> None:
        assert 3 in identity_kit.parse_storeys("a loggia on the third floor")

    def test_ignores_numbers_that_are_not_storeys(self) -> None:
        assert identity_kit.parse_storeys("cut limestone facade with aligned window rhythm") == []

    def test_balcony_course_carries_the_parsed_storeys(self) -> None:
        payload = {
            "description": "Haussmann block with wrought iron balconies at 2nd and 5th floors.",
        }
        balcony = next(s for s in derive_signatures(payload) if s["type"] == "balcony_course")
        assert balcony["params"]["storeys"] == [2, 5]


class TestVocabularyBreadth:
    def test_a_ground_floor_arch_springs_from_the_ground_floor(self) -> None:
        """Evidence and geometry must agree: the citing field sets the storey."""
        payload = {"facadeDetail": {"groundFloor": "rusticated stone base with tall arched entry"}}
        arch = next(s for s in derive_signatures(payload) if s["type"] == "arched_opening")
        assert arch["params"]["storey"] == 0

    def test_haussmann_derives_its_defining_assemblies(self) -> None:
        payload = {
            "description": "Classic Haussmann apartment block with cut limestone facade, "
                           "wrought iron balconies at 2nd and 5th floors, zinc mansard roof.",
            "facadeDetail": {"groundFloor": "rusticated stone base with tall arched entry"},
        }
        found = {s["type"] for s in derive_signatures(payload)}
        assert {"rusticated_base", "balcony_course", "mansard_roof"} <= found

    def test_gothic_battlements_reuse_the_parapet_assembly(self) -> None:
        payload = {"description": "Limestone ashlar building with crenellated battlements."}
        assert [s["type"] for s in derive_signatures(payload)] == ["ornamental_parapet"]

    def test_theatre_assemblies_do_not_leak_into_other_families(self) -> None:
        payload = {"description": "Classic Haussmann apartment block with zinc mansard roof."}
        found = {s["type"] for s in derive_signatures(payload)}
        assert not ({"marquee", "blade_sign", "relief_band"} & found)
