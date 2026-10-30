"""Part ranges must not multiply a bounded source coordinate array."""

import io
import math
import zipfile
from unittest.mock import MagicMock

import pytest
import shapefile

from app.services.reference_import import parse_shapefile_reference
from app.services.shapefile_import import parse_shapefile_zip
from app.services.shapefile_resources import validate_shapefile_components


PARTED_TYPES = [3, 5, 13, 15, 23, 25, 31]
PARSERS = [parse_shapefile_zip, parse_shapefile_reference]


def components(kind, starts, points=None, part_types=None, records=1):
    shp, shx, dbf = io.BytesIO(), io.BytesIO(), io.BytesIO()
    with shapefile.Writer(shp=shp, shx=shx, dbf=dbf, shapeType=kind) as writer:
        writer.field("name", "C")
        shape = shapefile.Shape(kind)
        shape.points = points if points is not None else [(i / 1000, i / 1000) for i in range(400)]
        shape.parts = starts
        if kind == 31:
            shape.partTypes = part_types if part_types is not None else [0] * len(starts)
        for _ in range(records):
            writer.shape(shape)
            writer.record("small isolated fixture")
    return shp.getvalue(), dbf.getvalue(), shx.getvalue()


def archive_for(parts):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in zip(("shp", "dbf", "shx"), parts):
            archive.writestr(f"small.{name}", data)
    return output.getvalue()


@pytest.mark.parametrize("parser", PARSERS)
@pytest.mark.parametrize("kind", PARTED_TYPES)
def test_overlapping_part_ranges_rejected_before_pyshp(monkeypatch, parser, kind):
    # Reviewer reproduction: 400 source points plus 200 overlapping ranges
    # become 39,901 line coordinates in PyShp. Never run that conversion here.
    data = archive_for(components(kind, [0, 399] * 100))
    reader = MagicMock(side_effect=AssertionError("Unvalidated parts reached PyShp"))
    monkeypatch.setattr(shapefile, "Reader", reader)
    with pytest.raises(ValueError):
        parser(data)
    reader.assert_not_called()


@pytest.mark.parametrize("parser", PARSERS)
@pytest.mark.parametrize(
    "starts",
    [[1, 4], [0, 0], [0, -1], [0, 8], [0, 4, 2], [0, 7]],
    ids=["first-nonzero", "duplicate", "negative", "past-end", "backwards", "short-line"],
)
def test_invalid_part_starts_rejected_before_pyshp(monkeypatch, parser, starts):
    data = archive_for(components(3, starts, points=[(i / 1000, 0) for i in range(8)]))
    reader = MagicMock(side_effect=AssertionError("Invalid part starts reached PyShp"))
    monkeypatch.setattr(shapefile, "Reader", reader)
    with pytest.raises(ValueError):
        parser(data)
    reader.assert_not_called()


@pytest.mark.parametrize("parser", PARSERS)
@pytest.mark.parametrize("kind", [3, 5, 13, 15, 23, 25])
def test_supported_disjoint_multipart_imports_remain_usable(parser, kind):
    if kind in (3, 13, 23):
        points, starts = [(0, 0), (0.01, 0.01), (0.02, 0), (0.03, 0.01)], [0, 2]
    else:
        points = [(0, 0), (0, 0.01), (0.01, 0.01), (0.01, 0), (0, 0)]
        points += [(x + 0.02, y) for x, y in points]
        starts = [0, 5]
    parsed = parser(archive_for(components(kind, starts, points)))
    assert parsed.feature_count == (2 if parser is parse_shapefile_zip else 1)


@pytest.mark.parametrize("kind", [5, 15, 25])
def test_polygon_parts_need_four_positions(kind):
    with pytest.raises(ValueError):
        validate_shapefile_components(*components(kind, [0, 5], points=[(i / 1000, 0) for i in range(8)]))


def test_bounded_multipatch_strips_fans_and_rings_pass_preflight():
    starts = [0, 3, 6, 10, 14, 18]
    parts = components(31, starts, points=[(i / 1000, 0) for i in range(22)], part_types=list(range(6)))
    validate_shapefile_components(*parts)


@pytest.mark.parametrize("part_type,count", [(0, 2), (1, 2), (2, 3), (3, 3), (4, 3), (5, 3), (6, 4)])
def test_multipatch_part_type_and_minimum_length_are_validated(part_type, count):
    with pytest.raises(ValueError):
        validate_shapefile_components(
            *components(31, [0], points=[(i / 1000, 0) for i in range(count)], part_types=[part_type])
        )


def polygon_parts(rings, points_per_ring, *, repeated_holes=False):
    points, starts = [], []
    for ring in range(rings):
        starts.append(len(points))
        if repeated_holes:
            # The reviewer's overlapping bounding-box configuration. Keep
            # actual conversion behind a Reader sentinel in rejection tests.
            coordinates = (
                [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
                if ring < rings // 2
                else [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8), (0.2, 0.2)]
            )
        else:
            center_x, center_y = (ring % 10) * 0.02, (ring // 10) * 0.02
            coordinates = [
                (
                    round(center_x + 0.005 * math.cos(-2 * math.pi * point / (points_per_ring - 1)), 6),
                    round(center_y + 0.005 * math.sin(-2 * math.pi * point / (points_per_ring - 1)), 6),
                )
                for point in range(points_per_ring - 1)
            ]
            coordinates.append(coordinates[0])
        points.extend(coordinates)
    return starts, points


@pytest.mark.parametrize("parser", PARSERS)
@pytest.mark.parametrize("kind", [5, 15, 25])
def test_polygon_ring_association_work_rejected_before_pyshp(monkeypatch, parser, kind):
    starts, points = polygon_parts(500, 5, repeated_holes=True)
    data = archive_for(components(kind, starts, points))
    reader = MagicMock(side_effect=AssertionError("Unbounded ring association reached PyShp"))
    monkeypatch.setattr(shapefile, "Reader", reader)
    with pytest.raises(ValueError):
        parser(data)
    reader.assert_not_called()


@pytest.mark.parametrize("parser", PARSERS)
def test_polygon_ring_association_budget_is_aggregate_across_records(monkeypatch, parser):
    starts, points = polygon_parts(20, 5, repeated_holes=True)
    # Each source alone is small, but 501 records exceed the combined work
    # budget while remaining below 2000 records and 100000 source points.
    data = archive_for(components(5, starts, points, records=501))
    reader = MagicMock(side_effect=AssertionError("Aggregate ring work reached PyShp"))
    monkeypatch.setattr(shapefile, "Reader", reader)
    with pytest.raises(ValueError):
        parser(data)
    reader.assert_not_called()


@pytest.mark.parametrize("parser", PARSERS)
@pytest.mark.parametrize("rings,points_per_ring", [(40, 250), (1, 100000)], ids=["complex-multipart", "100k-outline"])
def test_bounded_complex_polygons_keep_supported_import(parser, rings, points_per_ring):
    starts, points = polygon_parts(rings, points_per_ring)
    parsed = parser(archive_for(components(5, starts, points)))
    assert parsed.feature_count == (rings if parser is parse_shapefile_zip else 1)
