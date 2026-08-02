"""Compare annual AlphaEarth embeddings for one site and its context ring.

The annual embeddings are unit-vector-like, but the Cloud Storage COGs encode
them as int8 values. This pilot re-normalizes every valid 64-axis pixel before
computing cosine similarity, making the calculation robust to that encoding.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


DATASET_ID = "GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL"
DATASET_VERSION = "v1"
INDEX_URL = (
    "https://storage.googleapis.com/alphaearth_foundations/"
    "satellite_embedding/v1/annual/aef_index.parquet"
)
GCS_PREFIX = "gs://alphaearth_foundations/"
HTTPS_PREFIX = "https://storage.googleapis.com/alphaearth_foundations/"
ATTRIBUTION = (
    "The AlphaEarth Foundations Satellite Embedding dataset is produced by "
    "Google and Google DeepMind."
)


@dataclass(frozen=True)
class Bounds:
    west: float
    south: float
    east: float
    north: float

    def validate(self) -> "Bounds":
        if not (-180 <= self.west < self.east <= 180):
            raise ValueError(f"Invalid longitude bounds: {self}")
        if not (-90 <= self.south < self.north <= 90):
            raise ValueError(f"Invalid latitude bounds: {self}")
        return self


@dataclass(frozen=True)
class TileRecord:
    path: str
    year: int
    crs: str
    utm_zone: str
    wgs84_west: float
    wgs84_south: float
    wgs84_east: float
    wgs84_north: float
    utm_west: float
    utm_south: float
    utm_east: float
    utm_north: float

    @property
    def https_url(self) -> str:
        if not self.path.startswith(GCS_PREFIX):
            raise ValueError(f"Unexpected AlphaEarth path: {self.path}")
        return HTTPS_PREFIX + self.path.removeprefix(GCS_PREFIX)


def _iter_coordinate_pairs(value: Any) -> Iterable[tuple[float, float]]:
    if (
        isinstance(value, Sequence)
        and len(value) >= 2
        and isinstance(value[0], (int, float))
        and isinstance(value[1], (int, float))
    ):
        yield float(value[0]), float(value[1])
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            yield from _iter_coordinate_pairs(child)


def load_site(path: Path) -> tuple[dict[str, Any], dict[str, Any], Bounds]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("type") == "Feature":
        geometry = payload.get("geometry")
        properties = payload.get("properties") or {}
    else:
        geometry = payload
        properties = {}
    if not isinstance(geometry, dict) or "coordinates" not in geometry:
        raise ValueError("Site must be a GeoJSON geometry or Feature")
    pairs = list(_iter_coordinate_pairs(geometry["coordinates"]))
    if not pairs:
        raise ValueError("Site GeoJSON contains no coordinate pairs")
    xs, ys = zip(*pairs)
    bounds = Bounds(min(xs), min(ys), max(xs), max(ys)).validate()
    return geometry, properties, bounds


def ensure_index(index_path: Path, *, allow_download: bool) -> Path:
    if index_path.exists():
        return index_path
    if not allow_download:
        raise FileNotFoundError(
            f"AlphaEarth index not found at {index_path}. Re-run without "
            "--no-download-index or provide --index."
        )
    index_path.parent.mkdir(parents=True, exist_ok=True)
    partial = index_path.with_suffix(index_path.suffix + ".partial")
    try:
        urllib.request.urlretrieve(INDEX_URL, partial)
        partial.replace(index_path)
    finally:
        partial.unlink(missing_ok=True)
    return index_path


def _intersects(row: dict[str, Any], bounds: Bounds) -> bool:
    return bool(
        row["wgs84_west"] <= bounds.east
        and row["wgs84_east"] >= bounds.west
        and row["wgs84_south"] <= bounds.north
        and row["wgs84_north"] >= bounds.south
    )


def find_tile(
    index_path: Path,
    *,
    year: int,
    site_bounds: Bounds,
) -> TileRecord:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover - operator setup path
        raise RuntimeError("Install tools/alphaearth_pilot/requirements.txt") from exc

    columns = [field.name for field in TileRecord.__dataclass_fields__.values()]
    table = pq.read_table(index_path, columns=columns, filters=[[('year', '=', year)]])
    candidates = [row for row in table.to_pylist() if _intersects(row, site_bounds)]
    if not candidates:
        raise LookupError(f"No AlphaEarth tile covers the site for {year}")
    containing = [
        row
        for row in candidates
        if row["wgs84_west"] <= site_bounds.west
        and row["wgs84_east"] >= site_bounds.east
        and row["wgs84_south"] <= site_bounds.south
        and row["wgs84_north"] >= site_bounds.north
    ]
    if len(containing) != 1:
        raise LookupError(
            f"Pilot expects one tile containing the site for {year}; "
            f"found {len(containing)} containing and {len(candidates)} intersecting"
        )
    return TileRecord(**containing[0])


def normalize_vectors(data: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Return HxWxB unit vectors, leaving invalid pixels as zero vectors."""
    if data.ndim != 3:
        raise ValueError("Embedding data must have shape (bands, height, width)")
    vectors = np.moveaxis(data.astype(np.float32), 0, -1)
    magnitudes = np.linalg.norm(vectors, axis=-1, keepdims=True)
    safe = valid[..., None] & (magnitudes > 0)
    return np.divide(vectors, magnitudes, out=np.zeros_like(vectors), where=safe)


def cosine_change(
    first: np.ndarray,
    second: np.ndarray,
    first_valid: np.ndarray,
    second_valid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if first.shape != second.shape:
        raise ValueError(f"Embedding shapes do not match: {first.shape} vs {second.shape}")
    if first_valid.shape != second_valid.shape or first_valid.shape != first.shape[1:]:
        raise ValueError("Validity masks do not match embedding dimensions")
    valid = first_valid & second_valid
    first_norm = normalize_vectors(first, valid)
    second_norm = normalize_vectors(second, valid)
    similarity = np.sum(first_norm * second_norm, axis=-1)
    change = 1.0 - np.clip(similarity, -1.0, 1.0)
    change[~valid] = np.nan
    return change.astype(np.float32), valid


def summarize_change(
    change: np.ndarray,
    mask: np.ndarray,
    *,
    threshold: float,
) -> dict[str, float | int | None]:
    values = change[mask & np.isfinite(change)]
    if values.size == 0:
        return {
            "valid_pixel_count": 0,
            "mean_change": None,
            "median_change": None,
            "p90_change": None,
            "p95_change": None,
            "changed_area_pct": None,
        }
    return {
        "valid_pixel_count": int(values.size),
        "mean_change": round(float(np.mean(values)), 4),
        "median_change": round(float(np.median(values)), 4),
        "p90_change": round(float(np.quantile(values, 0.90)), 4),
        "p95_change": round(float(np.quantile(values, 0.95)), 4),
        "changed_area_pct": round(float(np.mean(values >= threshold) * 100.0), 2),
    }


def _window_for_projected_bounds(dataset: Any, bounds: tuple[float, float, float, float]) -> Any:
    from rasterio.windows import Window

    west, south, east, north = bounds
    indexes = [
        dataset.index(x, y)
        for x, y in ((west, south), (west, north), (east, south), (east, north))
    ]
    rows = [row for row, _ in indexes]
    cols = [col for _, col in indexes]
    row_start = max(0, min(rows))
    row_stop = min(dataset.height, max(rows) + 1)
    col_start = max(0, min(cols))
    col_stop = min(dataset.width, max(cols) + 1)
    if row_start >= row_stop or col_start >= col_stop:
        raise ValueError("Analysis bounds do not overlap the selected tile")
    return Window(col_start, row_start, col_stop - col_start, row_stop - row_start)


def download_byte_range(url: str, start: int, end: int, destination: Path) -> Path:
    """Download one inclusive HTTP byte range atomically and validate its size."""
    expected = end - start + 1
    if destination.exists() and destination.stat().st_size == expected:
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".partial")
    request = urllib.request.Request(
        url,
        headers={"Range": f"bytes={start}-{end}", "Accept-Encoding": "identity"},
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response, partial.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        actual = partial.stat().st_size
        if actual != expected:
            raise RuntimeError(
                f"Range download size mismatch for {url}: expected {expected}, got {actual}"
            )
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)
    return destination


def _overview_page_number(analysis_resolution_m: int) -> int:
    if analysis_resolution_m < 80 or analysis_resolution_m % 10:
        raise ValueError(
            "The bounded COG pilot supports 80 metres or coarser; use Earth Engine "
            "or a production block cache for native 10-metre analysis"
        )
    ratio = analysis_resolution_m // 10
    page = int(math.log2(ratio))
    if 2**page != ratio:
        raise ValueError("Analysis resolution must be 10 metres times a power of two")
    return page


def ensure_cog_cache(
    tile: TileRecord,
    *,
    cache_dir: Path,
    analysis_resolution_m: int,
    allow_download: bool,
) -> tuple[Path, Path, int]:
    """Cache a TIFF header and the contiguous payload for one overview page."""
    try:
        import tifffile
    except ImportError as exc:  # pragma: no cover - operator setup path
        raise RuntimeError("Install tools/alphaearth_pilot/requirements.txt") from exc

    page_number = _overview_page_number(analysis_resolution_m)
    header_path = cache_dir / f"{tile.year}-header.bin"
    if not header_path.exists():
        if not allow_download:
            raise FileNotFoundError(f"Missing cached TIFF header: {header_path}")
        download_byte_range(tile.https_url, 0, 4 * 1024 * 1024 - 1, header_path)
    with tifffile.TiffFile(header_path) as tif:
        if page_number >= len(tif.pages):
            raise ValueError(
                f"Resolution {analysis_resolution_m}m is unavailable in {tile.year} COG"
            )
        page = tif.pages[page_number]
        start = min(page.dataoffsets)
        end = max(
            offset + count
            for offset, count in zip(page.dataoffsets, page.databytecounts, strict=True)
        ) - 1
    payload_path = cache_dir / f"{tile.year}-overview-{analysis_resolution_m}m.bin"
    if not payload_path.exists():
        if not allow_download:
            raise FileNotFoundError(f"Missing cached overview payload: {payload_path}")
        download_byte_range(tile.https_url, start, end, payload_path)
    return header_path, payload_path, page_number


def decode_overview(header_path: Path, payload_path: Path, page_number: int) -> np.ndarray:
    """Decode a band-separate overview payload into a bands/rows/columns array."""
    try:
        import tifffile
    except ImportError as exc:  # pragma: no cover - operator setup path
        raise RuntimeError("Install tools/alphaearth_pilot/requirements.txt") from exc

    payload = payload_path.read_bytes()
    with tifffile.TiffFile(header_path) as tif:
        page = tif.pages[page_number]
        start = min(page.dataoffsets)
        result = np.empty(page.shape, dtype=page.dtype)
        for block_index, (offset, byte_count) in enumerate(
            zip(page.dataoffsets, page.databytecounts, strict=True)
        ):
            local_start = offset - start
            compressed = payload[local_start : local_start + byte_count]
            if len(compressed) != byte_count:
                raise RuntimeError(f"Cached payload is incomplete at block {block_index}")
            decoded, location, _ = page.decode(compressed, block_index)
            if decoded is None:
                raise RuntimeError(f"Could not decode block {block_index}")
            sample = int(location[0])
            result[sample] = decoded[0, : page.imagelength, : page.imagewidth, 0]
    return result


def read_cached_embedding_pair(
    first_tile: TileRecord,
    second_tile: TileRecord,
    *,
    site_geometry: dict[str, Any],
    site_bounds: Bounds,
    context_buffer_m: float,
    analysis_resolution_m: int,
    cache_dir: Path,
    allow_download: bool,
) -> tuple[np.ndarray, np.ndarray, Any, Any, np.ndarray, np.ndarray]:
    try:
        from affine import Affine
        from rasterio.features import geometry_mask
        from rasterio.warp import transform_bounds, transform_geom
    except ImportError as exc:  # pragma: no cover - operator setup path
        raise RuntimeError("Install tools/alphaearth_pilot/requirements.txt") from exc

    if first_tile.crs != second_tile.crs:
        raise ValueError("Selected annual tiles use different coordinate systems")
    first_header, first_payload, first_page = ensure_cog_cache(
        first_tile,
        cache_dir=cache_dir,
        analysis_resolution_m=analysis_resolution_m,
        allow_download=allow_download,
    )
    second_header, second_payload, second_page = ensure_cog_cache(
        second_tile,
        cache_dir=cache_dir,
        analysis_resolution_m=analysis_resolution_m,
        allow_download=allow_download,
    )
    if first_page != second_page:
        raise ValueError("Selected annual COGs resolved to different overview levels")
    first_full = decode_overview(first_header, first_payload, first_page)
    second_full = decode_overview(second_header, second_payload, second_page)
    if first_full.shape != second_full.shape:
        raise ValueError("Selected annual overview grids do not match")

    crs = first_tile.crs
    full_transform = Affine(
        analysis_resolution_m,
        0,
        first_tile.utm_west,
        0,
        analysis_resolution_m,
        first_tile.utm_south,
    )
    projected = transform_bounds(
        "EPSG:4326",
        crs,
        site_bounds.west,
        site_bounds.south,
        site_bounds.east,
        site_bounds.north,
        densify_pts=21,
    )
    analysis_bounds = (
        projected[0] - context_buffer_m,
        projected[1] - context_buffer_m,
        projected[2] + context_buffer_m,
        projected[3] + context_buffer_m,
    )

    class _Grid:
        transform = full_transform
        height = first_full.shape[1]
        width = first_full.shape[2]

        @staticmethod
        def index(x: float, y: float) -> tuple[int, int]:
            col, row = (~full_transform) * (x, y)
            return math.floor(row), math.floor(col)

    window = _window_for_projected_bounds(_Grid(), analysis_bounds)
    row_start = int(window.row_off)
    row_stop = row_start + int(window.height)
    col_start = int(window.col_off)
    col_stop = col_start + int(window.width)
    first = first_full[:, row_start:row_stop, col_start:col_stop]
    second = second_full[:, row_start:row_stop, col_start:col_stop]
    south_up_transform = full_transform * Affine.translation(col_start, row_start)
    # Google's COG is stored south-up. Normalize outputs to conventional
    # north-up orientation before masking, visualization, and GeoTIFF export.
    first = first[:, ::-1, :]
    second = second[:, ::-1, :]
    transform = Affine(
        analysis_resolution_m,
        0,
        south_up_transform.c,
        0,
        -analysis_resolution_m,
        south_up_transform.f + first.shape[1] * analysis_resolution_m,
    )
    first_valid = np.all(first != -128, axis=0)
    second_valid = np.all(second != -128, axis=0)
    projected_site = transform_geom("EPSG:4326", crs, site_geometry)
    site_mask = geometry_mask(
        [projected_site],
        out_shape=first.shape[1:],
        transform=transform,
        invert=True,
    )
    context_mask = ~site_mask
    return first, second, transform, crs, site_mask, context_mask & first_valid & second_valid


def _heat_color(values: np.ndarray, upper: float) -> np.ndarray:
    scaled = np.clip(values / max(upper, 1e-6), 0.0, 1.0)
    stops = np.array(
        [
            [15, 23, 42],
            [14, 116, 144],
            [34, 211, 238],
            [250, 204, 21],
            [239, 68, 68],
        ],
        dtype=np.float32,
    )
    position = scaled * (len(stops) - 1)
    lower = np.floor(position).astype(np.int16)
    upper_index = np.minimum(lower + 1, len(stops) - 1)
    fraction = (position - lower)[..., None]
    return (stops[lower] * (1 - fraction) + stops[upper_index] * fraction).astype(np.uint8)


def write_heatmap(
    path: Path,
    change: np.ndarray,
    valid: np.ndarray,
    site_mask: np.ndarray,
    *,
    first_year: int,
    second_year: int,
    site_name: str,
) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:  # pragma: no cover - operator setup path
        raise RuntimeError("Install tools/alphaearth_pilot/requirements.txt") from exc

    finite = change[valid & np.isfinite(change)]
    upper = float(np.quantile(finite, 0.98)) if finite.size else 1.0
    rgb = _heat_color(np.nan_to_num(change, nan=0.0), upper)
    rgb[~valid] = [30, 30, 30]
    scale = max(3, math.ceil(640 / max(rgb.shape[1], 1)))
    image = Image.fromarray(rgb).resize(
        (rgb.shape[1] * scale, rgb.shape[0] * scale), Image.Resampling.NEAREST
    )
    site_edge = site_mask ^ (
        np.roll(site_mask, 1, axis=0)
        & np.roll(site_mask, -1, axis=0)
        & np.roll(site_mask, 1, axis=1)
        & np.roll(site_mask, -1, axis=1)
    )
    edge = Image.fromarray((site_edge * 255).astype(np.uint8)).resize(
        image.size, Image.Resampling.NEAREST
    )
    white = Image.new("RGB", image.size, (255, 255, 255))
    image.paste(white, mask=edge)

    header_height = 112
    footer_height = 52
    canvas = Image.new("RGB", (image.width, image.height + header_height + footer_height), (15, 23, 42))
    canvas.paste(image, (0, header_height))
    draw = ImageDraw.Draw(canvas)
    try:
        title_font = ImageFont.truetype("arial.ttf", 22)
        font = ImageFont.truetype("arial.ttf", 16)
    except OSError:  # pragma: no cover - depends on operator fonts
        title_font = ImageFont.load_default()
        font = title_font
    draw.text((18, 14), f"AlphaEarth annual embedding change: {first_year} -> {second_year}", fill="white", font=title_font)
    draw.text((18, 48), site_name, fill=(203, 213, 225), font=font)
    draw.text((18, 76), "White outline: pilot site | color: 1 - cosine similarity | 80 m analysis", fill=(148, 163, 184), font=font)
    draw.text((image.width - 54, header_height + 12), "N ↑", fill="white", font=font)
    gradient_width = max(80, image.width - 190)
    gradient = _heat_color(np.linspace(0, upper, gradient_width)[None, :], upper)[0]
    gradient_img = Image.fromarray(gradient[None, :, :]).resize((gradient_width, 18))
    y = header_height + image.height + 12
    canvas.paste(gradient_img, (86, y))
    draw.text((14, y), "low change", fill="white", font=font)
    draw.text((92 + gradient_width, y), "high", fill="white", font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def write_change_geotiff(path: Path, change: np.ndarray, transform: Any, crs: Any) -> None:
    import rasterio

    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=change.shape[0],
        width=change.shape[1],
        count=1,
        dtype="float32",
        crs=crs,
        transform=transform,
        nodata=-9999.0,
        compress="deflate",
        tiled=True,
    ) as destination:
        destination.write(np.nan_to_num(change, nan=-9999.0), 1)
        destination.update_tags(
            dataset=DATASET_ID,
            attribution=ATTRIBUTION,
            measurement="1 - cosine_similarity",
        )


def build_result(
    *,
    site_name: str,
    first_tile: TileRecord,
    second_tile: TileRecord,
    threshold: float,
    context_buffer_m: float,
    analysis_resolution_m: int,
    site_summary: dict[str, Any],
    context_summary: dict[str, Any],
) -> dict[str, Any]:
    field_name = f"surface_change_{first_tile.year}_{second_tile.year}"
    value = {
        "period": f"{first_tile.year}-{second_tile.year}",
        "native_resolution_m": 10,
        "analysis_resolution_m": analysis_resolution_m,
        "measurement": "1 - cosine_similarity",
        "change_threshold": threshold,
        "threshold_status": "pilot heuristic; validate before production",
        "site": site_summary,
        "context_buffer_m": context_buffer_m,
        "context_ring": context_summary,
    }
    return {
        "pilot": "alphaearth_annual_change_v1",
        "site_name": site_name,
        "dataset": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "attribution": ATTRIBUTION,
        "tiles": {str(first_tile.year): asdict(first_tile), str(second_tile.year): asdict(second_tile)},
        "urban_dna_fields": {
            f"environment.{field_name}": {
                "value": value,
                "confidence": 0.6,
                "source_datasets": ["google_alphaearth_annual_embeddings"],
                "source_phase": "city_connector",
                "notes": [
                    "Change magnitude is not a semantic land-cover classification.",
                    "Pilot boundary is approximate and must not be used as parcel geometry.",
                ],
            }
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=root / "sites" / "calgary_university_district.geojson")
    parser.add_argument("--index", type=Path, default=Path.home() / ".cache" / "siteforge" / "alphaearth" / "aef_index.parquet")
    parser.add_argument("--first-year", type=int, default=2017)
    parser.add_argument("--second-year", type=int, default=2025)
    parser.add_argument("--context-buffer-m", type=float, default=500.0)
    parser.add_argument(
        "--analysis-resolution-m",
        type=int,
        default=80,
        help="COG overview resolution; use 80m for the bounded neighborhood pilot",
    )
    parser.add_argument("--change-threshold", type=float, default=0.15)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts") / "alphaearth-pilot")
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("artifacts") / "alphaearth-pilot" / "cache",
    )
    parser.add_argument("--no-download-index", action="store_true")
    parser.add_argument("--no-download-cogs", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Resolve inputs and tiles without opening embedding COGs")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.first_year >= args.second_year:
        raise ValueError("--first-year must be earlier than --second-year")
    if not (0.0 < args.change_threshold < 2.0):
        raise ValueError("--change-threshold must be between 0 and 2")
    geometry, properties, bounds = load_site(args.site)
    site_name = str(properties.get("name") or args.site.stem)
    index_path = ensure_index(args.index, allow_download=not args.no_download_index)
    first_tile = find_tile(index_path, year=args.first_year, site_bounds=bounds)
    second_tile = find_tile(index_path, year=args.second_year, site_bounds=bounds)
    plan = {
        "site": site_name,
        "bounds": asdict(bounds),
        "first_tile": asdict(first_tile),
        "second_tile": asdict(second_tile),
        "context_buffer_m": args.context_buffer_m,
        "analysis_resolution_m": args.analysis_resolution_m,
        "change_threshold": args.change_threshold,
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0

    first, second, transform, crs, site_mask, context_mask = read_cached_embedding_pair(
        first_tile,
        second_tile,
        site_geometry=geometry,
        site_bounds=bounds,
        context_buffer_m=args.context_buffer_m,
        analysis_resolution_m=args.analysis_resolution_m,
        cache_dir=args.cache_dir,
        allow_download=not args.no_download_cogs,
    )
    first_valid = np.all(first != -128, axis=0)
    second_valid = np.all(second != -128, axis=0)
    change, valid = cosine_change(first, second, first_valid, second_valid)
    result = build_result(
        site_name=site_name,
        first_tile=first_tile,
        second_tile=second_tile,
        threshold=args.change_threshold,
        context_buffer_m=args.context_buffer_m,
        analysis_resolution_m=args.analysis_resolution_m,
        site_summary=summarize_change(change, site_mask & valid, threshold=args.change_threshold),
        context_summary=summarize_change(change, context_mask & valid, threshold=args.change_threshold),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_change_geotiff(args.output_dir / "change_score.tif", change, transform, crs)
    write_heatmap(
        args.output_dir / "change_map.png",
        change,
        valid,
        site_mask,
        first_year=args.first_year,
        second_year=args.second_year,
        site_name=site_name,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, LookupError, RuntimeError, ValueError) as exc:
        print(f"alphaearth pilot failed: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
