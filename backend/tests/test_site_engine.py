from __future__ import annotations

import pytest
from shapely.geometry import MultiPolygon, Polygon, box

from app.services.site_engine import (
    RealWorldSiteEngine,
    cleanup_developable_blocks,
    derive_right_of_way_polygons,
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
    WGS84_CRS,
)


class FakeContextFetcher:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls: list[tuple[Polygon, float]] = []

    async def fetch(self, polygon: Polygon, buffer_m: float = 50) -> dict:
        self.calls.append((polygon, buffer_m))
        return self.payload


def _site_polygon() -> Polygon:
    return Polygon(
        [
            (-114.0718, 51.0442),
            (-114.0704, 51.0442),
            (-114.0704, 51.0452),
            (-114.0718, 51.0452),
            (-114.0718, 51.0442),
        ]
    )


def test_cleanup_developable_blocks_discards_small_slivers() -> None:
    geometry = MultiPolygon(
        [
            box(0, 0, 20, 20),
            box(21, 0, 21.2, 100),
        ]
    )

    blocks = cleanup_developable_blocks(geometry, sliver_area_threshold=50.0)

    assert len(blocks) == 1
    assert round(blocks[0].area, 2) == 400.0


def test_derive_right_of_way_polygons_projects_and_clips_to_site() -> None:
    site = _site_polygon()
    metric_crs = local_metric_crs_for_polygon(site)
    to_metric = build_transformer(WGS84_CRS, metric_crs)
    site_metric = project_geometry(site, to_metric)

    roads = [
        {
            "osm_id": 101,
            "coordinates": [
                [-114.0711, 51.0440],
                [-114.0711, 51.0454],
            ],
            "width_m": 10.0,
            "road_type": "primary",
            "name": "Main Street",
        }
    ]

    row_features = derive_right_of_way_polygons(
        roads,
        to_metric=to_metric,
        site_metric=site_metric,
    )

    assert len(row_features) == 1
    assert row_features[0]["width_m"] == 10.0
    assert row_features[0]["geometry"].area > 1000.0
    assert row_features[0]["geometry"].intersects(site_metric)


@pytest.mark.asyncio
async def test_extract_developable_blocks_fetches_context_and_splits_site() -> None:
    site = _site_polygon()
    fetcher = FakeContextFetcher(
        {
            "roads": [
                {
                    "osm_id": 9001,
                    "coordinates": [
                        [-114.0711, 51.0440],
                        [-114.0711, 51.0454],
                    ],
                    "width_m": 12.0,
                    "road_type": "primary",
                    "name": "Center Street",
                }
            ]
        }
    )
    engine = RealWorldSiteEngine(context_fetcher=fetcher)

    result = await engine.extract_developable_blocks(site, buffer_m=80)

    assert len(fetcher.calls) == 1
    assert fetcher.calls[0][1] == 80
    assert result["fetched_context"] is True
    assert result["metric_crs"].startswith("EPSG:")
    assert result["roads_considered"] == 1
    assert len(result["right_of_way_polygons"]) == 1
    assert len(result["developable_blocks"]) == 2
    assert result["developable_area_sqm"] < result["site_area_sqm"]
    assert all(block["area_sqm"] >= 50.0 for block in result["developable_blocks"])
