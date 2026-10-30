"""Shapefile import — parse a zipped ESRI shapefile into WGS84 zone polygons.

Stateless: this endpoint does not persist anything. The frontend takes the
returned features and creates site zones through the normal zone-create path,
so imported geometry flows through the same rendering / persistence pipeline as
hand-drawn zones.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.core.security import require_auth
from app.models.models import User
from app.services.shapefile_import import ShapefileImportError, parse_shapefile_zip

router = APIRouter()

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


@router.post("/parse")
async def parse_shapefile(
    file: UploadFile = File(...),
    user: User = Depends(require_auth),
):
    """Parse a zipped shapefile and return features reprojected to lon/lat (EPSG:4326)."""
    filename = (file.filename or "").lower()
    if not filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Please upload the shapefile as a .zip containing the " ".shp, .dbf, .shx and .prj files.",
        )

    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(data) // (1024 * 1024)} MB). Limit is 25 MB.",
        )

    try:
        parsed = await run_in_threadpool(parse_shapefile_zip, data)
    except ShapefileImportError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "feature_count": parsed.feature_count,
        "skipped_count": parsed.skipped_count,
        "detected_crs": parsed.detected_crs,
        "warnings": parsed.warnings,
        "features": [
            {
                "coordinates": f.coordinates,
                "zone_type": f.zone_type,
                "properties": f.properties,
            }
            for f in parsed.features
        ],
    }
