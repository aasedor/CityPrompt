"""Small, isolated regressions for untrusted decoded-work boundaries."""

import io
import json
import struct
import threading
import sys
import uuid
import zipfile
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import fitz
import pytest
from fastapi import HTTPException, UploadFile

from app.processing.extractors import document_extractor as extractor
from app.services import reference_import, shapefile_import
from tests.test_glb_import import glb
from tests.test_lego_assembly import _manifest
from tests.test_reference_import import shapefile_zip


def polygon_zip():
    def write(writer):
        writer.poly([[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]])
        writer.record("Parcel")

    return shapefile_zip(write)


@pytest.mark.parametrize("parser", [shapefile_import.parse_shapefile_zip, reference_import.parse_shapefile_reference])
def test_zip_expansion_rejected_before_any_member_read(monkeypatch, parser):
    raw = polygon_zip()
    real = zipfile.ZipFile
    reads = []

    class AdvertisedArchive(real):
        def infolist(self):
            entries = super().infolist()
            entries[0].file_size = 101 * 1024 * 1024
            return entries

        def read(self, *args, **kwargs):
            reads.append(args)
            raise AssertionError("Expanded members must not be read")

    monkeypatch.setattr(zipfile, "ZipFile", AdvertisedArchive)
    with pytest.raises(ValueError, match="expanded"):
        parser(raw)
    assert reads == []


@pytest.mark.parametrize("parser", [shapefile_import.parse_shapefile_zip, reference_import.parse_shapefile_reference])
def test_zip_sidecar_text_rejected_before_read(monkeypatch, parser):
    raw = polygon_zip()
    real = zipfile.ZipFile

    class AdvertisedSidecar(real):
        def infolist(self):
            entry = zipfile.ZipInfo("nested/district.prj")
            entry.file_size = 65537
            return super().infolist() + [entry]

        def read(self, *args, **kwargs):
            raise AssertionError("Sidecar budget must precede reads")

    monkeypatch.setattr(zipfile, "ZipFile", AdvertisedSidecar)
    with pytest.raises(ValueError, match="sidecar"):
        parser(raw)


def test_design_shapefile_exploded_parts_obey_output_feature_cap(monkeypatch):
    def write(writer):
        writer.multipoint([[0, 0], [1, 1], [2, 2]])
        writer.record("Markers")

    monkeypatch.setattr(shapefile_import, "MAX_FEATURES", 2)
    result = shapefile_import.parse_shapefile_zip(shapefile_zip(write))
    assert result.feature_count == 2
    assert result.warnings


@pytest.mark.parametrize("parser", [shapefile_import.parse_shapefile_zip, reference_import.parse_shapefile_reference])
def test_shapefile_declared_points_rejected_before_pyshp(monkeypatch, parser):
    raw = polygon_zip()
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive, zipfile.ZipFile(output, "w") as target:
        for entry in archive.infolist():
            data = bytearray(archive.read(entry))
            if entry.filename.endswith(".shp"):
                # Polygon record: shape type, bbox, part count, point count.
                struct.pack_into("<I", data, 148, 1_000_000_000)
            target.writestr(entry.filename, data)
    import shapefile

    reader = MagicMock(side_effect=AssertionError("Preflight must run before PyShp"))
    monkeypatch.setattr(shapefile, "Reader", reader)
    with pytest.raises(ValueError, match="(coordinate|point|geometry)"):
        parser(output.getvalue())
    reader.assert_not_called()


@pytest.mark.asyncio
async def test_shapefile_route_requires_auth_before_upload_read(client, monkeypatch):
    response = await client.post("/api/v1/shapefiles/parse", files={"file": ("parcel.zip", b"invalid")})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_shapefile_route_limits_read_and_runs_parser_off_event_loop(monkeypatch):
    from app.api.v1 import shapefiles

    main_thread = threading.get_ident()
    thread_ids = []
    real = shapefiles.parse_shapefile_zip

    def parse(data):
        thread_ids.append(threading.get_ident())
        return real(data)

    monkeypatch.setattr(shapefiles, "parse_shapefile_zip", parse)
    result = await shapefiles.parse_shapefile(
        UploadFile(filename="parcel.zip", file=io.BytesIO(polygon_zip())), object()
    )
    assert result["feature_count"] == 1
    assert thread_ids and thread_ids[0] != main_thread
    upload = SimpleNamespace(filename="parcel.zip", read=AsyncMock(return_value=b"a" * 9))
    monkeypatch.setattr(shapefiles, "MAX_UPLOAD_BYTES", 8)
    with pytest.raises(HTTPException) as exc:
        await shapefiles.parse_shapefile(upload, object())
    assert exc.value.status_code == 413
    upload.read.assert_awaited_once_with(9)


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [b"not a GLB", glb(external=True)])
async def test_manifest_upload_validates_all_bytes_before_any_storage(monkeypatch, payload):
    from app.api.v1 import lego_assembly as api
    from app.tasks import processing

    stored = MagicMock()
    monkeypatch.setattr(processing, "_upload_to_storage", stored)
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    db = SimpleNamespace(execute=AsyncMock(return_value=result), add=MagicMock(), commit=AsyncMock(), flush=AsyncMock())
    files = [
        UploadFile(filename="fam_podium.glb", file=io.BytesIO(glb())),
        UploadFile(filename="fam_floor.glb", file=io.BytesIO(payload)),
    ]
    with pytest.raises(HTTPException) as exc:
        await api.import_compiler_manifest(
            UploadFile(filename="manifest.json", file=io.BytesIO(json.dumps(_manifest()).encode())),
            files,
            None,
            UploadFile(filename="report.json", file=io.BytesIO(b'{"status":"pass"}')),
            True,
            SimpleNamespace(id=uuid.uuid4()),
            db,
        )
    assert exc.value.status_code == 422
    stored.assert_not_called()
    db.add.assert_not_called()


def pdf_file(tmp_path, sizes, text="Reference zoning guidance"):
    path = tmp_path / "reference.pdf"
    with fitz.open() as document:
        for width, height in sizes:
            page = document.new_page(width=width, height=height)
            page.insert_text((20, 20), text)
        document.save(path)
    return str(path)


def test_reference_pdf_is_text_only_even_with_oversized_page(tmp_path, monkeypatch):
    path = pdf_file(tmp_path, [(14400, 14400)])
    raster = MagicMock(side_effect=AssertionError("Reference PDFs must not rasterize"))
    monkeypatch.setattr(fitz.Page, "get_pixmap", raster)
    result = extractor.extract_from_file(path, "pdf", text_only=True)
    assert not result.errors
    assert "Reference zoning guidance" in result.text_content
    assert result.images == []
    raster.assert_not_called()


@pytest.mark.parametrize("sizes", [[(14400, 14400)], [(612, 792)] * 6])
def test_pdf_raster_budget_rejected_before_any_rasterization(tmp_path, monkeypatch, sizes):
    path = pdf_file(tmp_path, sizes)
    calls = []

    def raster(*args, **kwargs):
        calls.append(True)
        raise AssertionError("Budget preflight must reject before rasterization")

    monkeypatch.setattr(fitz.Page, "get_pixmap", raster)
    result = extractor.extract_pdf(path)
    assert result.errors
    assert calls == []
    assert result.images == []


def test_normal_pdf_raster_keeps_text_and_image(tmp_path, monkeypatch):
    monkeypatch.setattr(
        extractor, "_classify_pdf_page", lambda image, text, page: {"page": page, "type": "text", "confidence": 0.5}
    )
    result = extractor.extract_pdf(pdf_file(tmp_path, [(144, 144)]))
    assert not result.errors
    assert "Reference zoning" in result.text_content
    assert len(result.images) == 1


def test_large_architectural_sheet_is_downsampled_within_raster_budget(tmp_path, monkeypatch):
    # ANSI E (34 x 44 inches) is a normal architectural drawing size. Keep it
    # usable without actually allocating the 25-million-pixel test image.
    from PIL import Image

    output = io.BytesIO()
    Image.new("RGB", (2, 2)).save(output, format="PNG")
    dpis = []

    def raster(page, *, dpi, **kwargs):
        dpis.append(dpi)
        return SimpleNamespace(tobytes=lambda kind: output.getvalue())

    monkeypatch.setattr(fitz.Page, "get_pixmap", raster)
    monkeypatch.setattr(
        extractor, "_classify_pdf_page", lambda image, text, page: {"page": page, "type": "text", "confidence": 0.5}
    )
    result = extractor.extract_pdf(pdf_file(tmp_path, [(2448, 3168)]))
    assert not result.errors
    assert len(result.images) == 1
    assert dpis == [129]


@pytest.mark.parametrize(
    "text",
    ["height\n" + "1\n" * 10001, ",".join(["column"] * 257) + "\n1\n", "height\n" + "x" * 32769],
    ids=["rows", "columns", "cell"],
)
def test_csv_limits_precede_dataframe_loading(tmp_path, monkeypatch, text):
    path = tmp_path / "table.csv"
    path.write_text(text, encoding="utf-8")
    load = MagicMock(side_effect=AssertionError("Table parser must not run before preflight"))
    monkeypatch.setitem(sys.modules, "pandas", SimpleNamespace(read_csv=load))
    result = extractor.extract_spreadsheet(str(path))
    assert result.errors and "budget" in result.errors[0].lower()
    load.assert_not_called()


def test_xlsx_dimensions_rejected_before_workbook_loader(tmp_path, monkeypatch):
    path = tmp_path / "table.xlsx"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "xl/worksheets/sheet1.xml", '<worksheet><dimension ref="A1:XFD1048576"/><sheetData/></worksheet>'
        )
    load = MagicMock(side_effect=AssertionError("Workbook loader must not run before preflight"))
    monkeypatch.setitem(sys.modules, "pandas", SimpleNamespace(read_excel=load))
    result = extractor.extract_spreadsheet(str(path))
    assert result.errors and "budget" in result.errors[0].lower()
    load.assert_not_called()


def test_image_dimensions_rejected_before_opencv_decode(tmp_path, monkeypatch):
    from PIL import Image
    import cv2

    path = tmp_path / "reference.png"
    Image.new("RGB", (2, 2)).save(path)
    decode = MagicMock(side_effect=AssertionError("Pixel allocation must follow header validation"))
    monkeypatch.setattr(cv2, "imread", decode)
    monkeypatch.setattr(extractor, "MAX_PAGE_PIXELS", 3)
    result = extractor.extract_image(str(path))
    assert result.errors and "budget" in result.errors[0].lower()
    decode.assert_not_called()


def test_reference_worker_uses_text_only_pdf_path(tmp_path, monkeypatch):
    from app.tasks import processing

    path = pdf_file(tmp_path, [(14400, 14400)])
    payload = open(path, "rb").read()
    document = SimpleNamespace(file_type="pdf", storage_url="controlled-key", project_id=uuid.uuid4())
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = document
    monkeypatch.setattr(processing, "_get_sync_session", lambda: session)
    monkeypatch.setattr(processing, "_download_from_storage", lambda url: payload)
    monkeypatch.setattr(processing, "_queue_procedural_generation_jobs", lambda *args: [])
    monkeypatch.setattr(processing.process_document, "update_state", lambda **kwargs: None)
    raster = MagicMock(side_effect=AssertionError("Reference processing must not rasterize"))
    monkeypatch.setattr(fitz.Page, "get_pixmap", raster)
    result = processing.process_document.run(str(uuid.uuid4()), extract_only=True)
    assert result["status"] == "completed"
    assert "Reference zoning guidance" in document.extracted_data["extraction"]["text_content"]
    assert document.extracted_data["extraction"]["image_count"] == 0
    raster.assert_not_called()


def test_worker_marks_budget_rejection_failed_without_retry_or_generation(monkeypatch):
    from app.tasks import processing

    document = SimpleNamespace(file_type="csv", storage_url="controlled-key", project_id=uuid.uuid4())
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = document
    monkeypatch.setattr(processing, "_get_sync_session", lambda: session)
    monkeypatch.setattr(processing, "_download_from_storage", lambda url: b"height\n" + b"1\n" * 10001)
    monkeypatch.setattr(processing.process_document, "update_state", lambda **kwargs: None)
    queue = MagicMock(side_effect=AssertionError("Rejected input must not reach generation"))
    monkeypatch.setattr(processing, "_queue_procedural_generation_jobs", queue)
    result = processing.process_document.run(str(uuid.uuid4()), extract_only=True)
    assert result["status"] == "failed"
    assert document.processing_status == "failed"
    assert "budget" in document.extracted_data["error"].lower()
    queue.assert_not_called()


@pytest.mark.parametrize("extension", ["csv", "xlsx"])
def test_supported_tables_preserve_dimensions_and_coordinates(tmp_path, extension):
    path = tmp_path / f"table.{extension}"
    if extension == "csv":
        path.write_text("height,latitude,longitude\n12,51,-114\n15,52,-115\n", encoding="utf-8")
    else:
        from openpyxl import Workbook

        workbook = Workbook()
        workbook.active.append(["height", "latitude", "longitude"])
        workbook.active.append([12, 51, -114])
        workbook.active.append([15, 52, -115])
        workbook.save(path)
        workbook.close()
    result = extractor.extract_spreadsheet(str(path))
    assert not result.errors
    assert result.metadata["row_count"] == 2
    assert result.metadata["has_coordinates"] is True
    assert result.dimensions == [{"height": 12}, {"height": 15}]


def test_spreadsheet_serialization_does_not_expand_by_column_padding(tmp_path):
    from app.processing.extractors.document_extractor import extract_spreadsheet

    path = tmp_path / "wide-text.csv"
    path.write_text(
        ",".join(f"C{i}" for i in range(20))
        + "\n"
        + ",".join(["x" * 1500] * 20)
        + "\n"
        + (",".join(["x"] * 20) + "\n") * 199,
        encoding="utf-8",
    )
    result = extract_spreadsheet(str(path))
    assert not result.errors
    assert len(result.text_content) < 100000
