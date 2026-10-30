"""
Document extraction service.
Routes uploaded files to the appropriate extractor based on file type.
"""

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)

MAX_PDF_TEXT_PAGES = 200
MAX_PDF_RASTER_PAGES = 20
PDF_RASTER_DPI = 300
MAX_RASTER_DIMENSION = 8192
MAX_PAGE_PIXELS = 25_000_000
MAX_DOCUMENT_PIXELS = 48_000_000
MAX_TEXT_CHARS = 4 * 1024 * 1024
MAX_PDF_PAGE_POINTS = 72 * 72  # up to a six-foot drawing sheet


class ExtractionResult:
    """Standardized result from any extractor."""

    def __init__(self):
        self.text_content: str = ""
        self.dimensions: list[dict] = []
        self.coordinates: list[list[float]] = []
        self.metadata: dict[str, Any] = {}
        self.images: list[bytes] = []
        self.page_classifications: list[dict] = []  # Per-page type info
        self.confidence: float = 0.0
        self.errors: list[str] = []

    def to_dict(self) -> dict:
        return {
            "text_content": self.text_content,
            "dimensions": self.dimensions,
            "coordinates": self.coordinates,
            "metadata": self.metadata,
            "image_count": len(self.images),
            "page_classifications": self.page_classifications,
            "confidence": self.confidence,
            "errors": self.errors,
        }


def extract_from_file(file_path: str, file_type: str, *, text_only: bool = False) -> ExtractionResult:
    """Route file to appropriate extractor."""
    if file_type == "pdf":
        return extract_pdf(file_path, text_only=text_only)
    extractors = {
        "pdf": extract_pdf,
        "jpg": extract_image,
        "jpeg": extract_image,
        "png": extract_image,
        "tiff": extract_image,
        "dwg": extract_cad,
        "dxf": extract_cad,
        "xlsx": extract_spreadsheet,
        "csv": extract_spreadsheet,
        "geojson": extract_geojson,
    }

    extractor = extractors.get(file_type)
    if not extractor:
        result = ExtractionResult()
        result.errors.append(f"No extractor available for file type: {file_type}")
        return result

    return extractor(file_path)


def _classify_pdf_page(page_image_bytes: bytes, page_text: str, page_num: int) -> dict:
    """
    Classify a PDF page as floor_plan, elevation, schedule, or text.

    Uses heuristics:
    - Line density: floor plans and elevations have many straight lines
    - Text ratio: text-heavy pages are schedules/specifications
    - Edge density: architectural drawings have high edge density
    - Dimension keywords: floor plans often reference rooms, dimensions, scales
    """
    import cv2
    import numpy as np

    classification = {
        "page": page_num,
        "type": "text",
        "confidence": 0.5,
        "line_count": 0,
        "text_density": 0.0,
        "edge_density": 0.0,
    }

    try:
        # Decode image
        nparr = np.frombuffer(page_image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return classification

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        total_pixels = h * w

        # Edge density
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        edge_pixels = np.count_nonzero(edges)
        edge_density = edge_pixels / total_pixels
        classification["edge_density"] = round(edge_density, 4)

        # Line detection
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=40, maxLineGap=10)
        line_count = len(lines) if lines is not None else 0
        classification["line_count"] = line_count

        # Text density — ratio of text characters to page area
        text_len = len(page_text.strip())
        text_density = text_len / max(total_pixels / 1000, 1)
        classification["text_density"] = round(text_density, 4)

        # Keyword detection for floor plans
        text_lower = page_text.lower()
        floor_plan_keywords = [
            "floor plan",
            "ground floor",
            "first floor",
            "level",
            "scale",
            "bedroom",
            "bathroom",
            "kitchen",
            "living",
            "corridor",
            "1:",
            "m²",
            "sq ft",
            "sqm",
            "sq.m",
        ]
        elevation_keywords = [
            "elevation",
            "section",
            "facade",
            "front view",
            "side view",
            "rear view",
            "north elevation",
            "south elevation",
        ]
        schedule_keywords = [
            "schedule",
            "specification",
            "table",
            "qty",
            "quantity",
            "item",
            "description",
            "total",
            "summary",
            "legend",
        ]

        fp_keyword_hits = sum(1 for kw in floor_plan_keywords if kw in text_lower)
        elev_keyword_hits = sum(1 for kw in elevation_keywords if kw in text_lower)
        sched_keyword_hits = sum(1 for kw in schedule_keywords if kw in text_lower)

        # Scoring: combine heuristics
        # Floor plans: many lines, moderate text, floor plan keywords
        # Elevations: many lines, elevation keywords
        # Schedules: lots of text, schedule keywords, few lines
        # Text pages: lots of text, few lines, no architectural keywords

        scores = {
            "floor_plan": (
                (min(line_count / 100, 1.0) * 0.35)
                + (min(edge_density / 0.05, 1.0) * 0.25)
                + (min(fp_keyword_hits / 3, 1.0) * 0.25)
                + ((1.0 - min(text_density / 5, 1.0)) * 0.15)
            ),
            "elevation": (
                (min(line_count / 80, 1.0) * 0.30)
                + (min(edge_density / 0.04, 1.0) * 0.25)
                + (min(elev_keyword_hits / 2, 1.0) * 0.30)
                + ((1.0 - min(text_density / 5, 1.0)) * 0.15)
            ),
            "schedule": (
                (min(text_density / 3, 1.0) * 0.35)
                + (min(sched_keyword_hits / 3, 1.0) * 0.35)
                + ((1.0 - min(line_count / 200, 1.0)) * 0.15)
                + ((1.0 - min(edge_density / 0.06, 1.0)) * 0.15)
            ),
            "text": (
                (min(text_density / 2, 1.0) * 0.40)
                + ((1.0 - min(line_count / 50, 1.0)) * 0.30)
                + ((1.0 - min(edge_density / 0.03, 1.0)) * 0.30)
            ),
        }

        best_type = max(scores, key=scores.get)
        classification["type"] = best_type
        classification["confidence"] = round(scores[best_type], 3)
        classification["scores"] = {k: round(v, 3) for k, v in scores.items()}

    except Exception as e:
        logger.warning(f"Page classification failed for page {page_num}: {e}")

    return classification


def extract_pdf(file_path: str, *, text_only: bool = False) -> ExtractionResult:
    """Extract reference text, or preflight the complete raster workload first."""
    import fitz  # PyMuPDF

    result = ExtractionResult()
    try:
        with fitz.open(file_path) as doc:
            page_count = len(doc)
            result.metadata = dict(doc.metadata) if doc.metadata else {}
            result.metadata.update(page_count=page_count, text_only=text_only)
            page_limit = MAX_PDF_TEXT_PAGES if text_only else MAX_PDF_RASTER_PAGES
            if page_count > page_limit:
                raise ValueError(f"PDF page budget exceeded (maximum {page_limit} pages).")
            page_dpis = []
            if not text_only:
                pixels = 0
                for page in doc:
                    width_pt, height_pt = page.rect.width, page.rect.height
                    if not 0 < width_pt <= MAX_PDF_PAGE_POINTS or not 0 < height_pt <= MAX_PDF_PAGE_POINTS:
                        raise ValueError(
                            "PDF page dimensions exceed the raster budget. Use a standard drawing sheet size."
                        )
                    # Preserve ordinary pages at 300 DPI; downsample large
                    # architectural sheets instead of rejecting usable plans.
                    dpi = max(
                        1,
                        math.floor(
                            min(
                                PDF_RASTER_DPI,
                                MAX_RASTER_DIMENSION * 72 / width_pt,
                                MAX_RASTER_DIMENSION * 72 / height_pt,
                                math.sqrt(MAX_PAGE_PIXELS * 72 * 72 / (width_pt * height_pt)),
                            )
                        ),
                    )
                    page_dpis.append(dpi)
                    # IntegerRect matches MuPDF's outward rounding, including
                    # rotated pages. Inspect every page before any allocation.
                    rect = (page.rect * fitz.Matrix(dpi / 72, dpi / 72)).irect
                    width, height = rect.width, rect.height
                    pixels += width * height
                    if (
                        not 0 < width <= MAX_RASTER_DIMENSION
                        or not 0 < height <= MAX_RASTER_DIMENSION
                        or width * height > MAX_PAGE_PIXELS
                        or pixels > MAX_DOCUMENT_PIXELS
                    ):
                        raise ValueError("PDF raster pixel budget exceeded. Use smaller pages or split the document.")
                result.metadata["raster_dpi"] = page_dpis
            texts, chars = [], 0
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                chars += len(page_text) + 1
                if chars > MAX_TEXT_CHARS:
                    raise ValueError("PDF text budget exceeded (maximum 4 million characters).")
                texts.append(page_text)
                if not text_only:
                    pix = page.get_pixmap(dpi=page_dpis[page_num], colorspace=fitz.csRGB, alpha=False)
                    image_bytes = pix.tobytes("png")
                    result.images.append(image_bytes)
                    result.page_classifications.append(_classify_pdf_page(image_bytes, page_text, page_num))
            result.text_content = "\n".join(texts)

        # Sort images so floor plans come first, then elevations, then others
        type_priority = {"floor_plan": 0, "elevation": 1, "schedule": 2, "text": 3}
        sorted_pages = sorted(
            enumerate(result.page_classifications),
            key=lambda x: (type_priority.get(x[1]["type"], 3), -x[1]["confidence"]),
        )
        sorted_images = [result.images[i] for i, _ in sorted_pages]
        sorted_classifications = [cls for _, cls in sorted_pages]

        result.images = sorted_images
        result.page_classifications = sorted_classifications

        # Summary
        type_counts = {}
        for cls in result.page_classifications:
            t = cls["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        result.metadata["page_types"] = type_counts

        result.confidence = 0.7
        logger.info(f"PDF extracted: {page_count} pages, types: {type_counts}")

    except Exception as e:
        result.images.clear()
        result.page_classifications.clear()
        result.text_content = ""
        result.errors.append(f"PDF extraction error: {str(e)}")
        logger.error(f"PDF extraction failed: {e}")

    return result


def extract_image(file_path: str) -> ExtractionResult:
    """Extract data from architectural images."""
    import cv2
    import numpy as np

    result = ExtractionResult()
    try:
        import os
        from PIL import Image

        if os.path.getsize(file_path) > 50 * 1024 * 1024:
            raise ValueError("Image file budget exceeded (maximum 50 MB).")
        with Image.open(file_path) as image:
            width, height = image.size
            if (
                not 0 < width <= MAX_RASTER_DIMENSION
                or not 0 < height <= MAX_RASTER_DIMENSION
                or width * height > MAX_PAGE_PIXELS
            ):
                raise ValueError("Image pixel budget exceeded. Resize the reference image before uploading.")
            image.verify()
        img = cv2.imread(file_path)
        if img is None:
            result.errors.append("Failed to read image file")
            return result

        # Preprocessing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Deskew
        # Edge detection for wall lines
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Line detection
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

        if lines is not None:
            result.metadata["detected_lines"] = len(lines)

        # OCR for dimension text
        try:
            import pytesseract

            text = pytesseract.image_to_string(gray)
            result.text_content = text
        except Exception:
            logger.warning("Tesseract OCR not available, skipping text extraction")

        # Store original image for AI interpretation
        with open(file_path, "rb") as f:
            result.images.append(f.read())

        result.confidence = 0.5
        logger.info(f"Image extracted: {img.shape}, {result.metadata.get('detected_lines', 0)} lines")

    except Exception as e:
        result.errors.append(f"Image extraction error: {str(e)}")
        logger.error(f"Image extraction failed: {e}")

    return result


def extract_cad(file_path: str) -> ExtractionResult:
    """Extract data from CAD files (DWG/DXF)."""
    import ezdxf

    result = ExtractionResult()
    try:
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()

        result.metadata["layers"] = [layer.dxf.name for layer in doc.layers]
        result.metadata["units"] = doc.header.get("$INSUNITS", 0)

        # Extract entities by type
        lines = []
        polylines = []
        dimensions = []

        for entity in msp:
            if entity.dxftype() == "LINE":
                lines.append(
                    {
                        "start": [entity.dxf.start.x, entity.dxf.start.y],
                        "end": [entity.dxf.end.x, entity.dxf.end.y],
                        "layer": entity.dxf.layer,
                    }
                )
            elif entity.dxftype() in ("LWPOLYLINE", "POLYLINE"):
                points = [[p[0], p[1]] for p in entity.get_points()]
                polylines.append({"points": points, "layer": entity.dxf.layer})
            elif entity.dxftype() == "DIMENSION":
                dimensions.append(
                    {
                        "value": getattr(entity.dxf, "actual_measurement", None),
                        "text": getattr(entity.dxf, "text", ""),
                    }
                )

        result.metadata["entity_counts"] = {
            "lines": len(lines),
            "polylines": len(polylines),
            "dimensions": len(dimensions),
        }

        # Convert polylines to potential building footprints
        for poly in polylines:
            if len(poly["points"]) >= 3:
                result.coordinates.append(poly["points"])

        result.dimensions = dimensions
        result.confidence = 0.85
        logger.info(f"CAD extracted: {len(lines)} lines, {len(polylines)} polylines")

    except Exception as e:
        result.errors.append(f"CAD extraction error: {str(e)}")
        logger.error(f"CAD extraction failed: {e}")

    return result


def extract_spreadsheet(file_path: str) -> ExtractionResult:
    """Extract data from spreadsheets (CSV/XLSX)."""
    result = ExtractionResult()
    try:
        from app.processing.extractors.table_resources import MAX_TABLE_ROWS, preflight_table

        preflight_table(file_path)
        import pandas as pd

        if file_path.lower().endswith(".csv"):
            df = pd.read_csv(file_path, nrows=MAX_TABLE_ROWS, encoding="utf-8-sig")
        else:
            df = pd.read_excel(file_path, nrows=MAX_TABLE_ROWS)

        result.metadata["columns"] = list(df.columns)
        result.metadata["row_count"] = len(df)

        # Look for coordinate columns
        coord_cols = [
            c for c in df.columns if str(c).lower() in ("lat", "latitude", "lng", "longitude", "lon", "x", "y")
        ]
        if len(coord_cols) >= 2:
            result.metadata["has_coordinates"] = True

        # Look for dimension columns
        dim_cols = [
            c for c in df.columns if any(kw in str(c).lower() for kw in ("height", "width", "length", "area", "floor"))
        ]
        if dim_cols:
            for _, row in df.iterrows():
                dim = {}
                for col in dim_cols:
                    dim[col] = row[col]
                result.dimensions.append(dim)

        # Fixed-width formatting multiplies each column's widest cell by every
        # row. CSV stays proportional to the already bounded table contents.
        result.text_content = df.to_csv(index=False)
        if len(result.text_content.encode("utf-8")) > 8 * 1024 * 1024:
            result.text_content = ""
            raise ValueError("The spreadsheet text exceeds the 8 MB extraction limit.")
        result.confidence = 0.9
        logger.info(f"Spreadsheet extracted: {len(df)} rows, {len(df.columns)} columns")

    except Exception as e:
        result.errors.append(f"Spreadsheet extraction error: {str(e)}")
        logger.error(f"Spreadsheet extraction failed: {e}")

    return result


def extract_geojson(file_path: str) -> ExtractionResult:
    """Extract data from GeoJSON files."""
    import json

    result = ExtractionResult()
    try:
        with open(file_path) as f:
            data = json.load(f)

        features = data.get("features", [])
        result.metadata["feature_count"] = len(features)

        for feature in features:
            geom = feature.get("geometry", {})
            if geom.get("type") == "Polygon":
                result.coordinates.append(geom["coordinates"][0])
            props = feature.get("properties", {})
            if props:
                result.dimensions.append(props)

        result.confidence = 0.95
        logger.info(f"GeoJSON extracted: {len(features)} features")

    except Exception as e:
        result.errors.append(f"GeoJSON extraction error: {str(e)}")
        logger.error(f"GeoJSON extraction failed: {e}")

    return result
