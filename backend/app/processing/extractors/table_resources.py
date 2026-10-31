"""Bound table expansion before pandas/openpyxl build their in-memory models."""

import csv
import os
import re
import zipfile
from xml.etree.ElementTree import iterparse

from app.services.shapefile_resources import validate_archive

MAX_TABLE_ROWS = 10_000
MAX_TABLE_COLUMNS = 256
MAX_TABLE_CELLS = 250_000
MAX_TABLE_CHARS = 4 * 1024 * 1024
MAX_CELL_CHARS = 32 * 1024


def _over_budget():
    raise ValueError("Table budget exceeded: use at most 10,000 rows, 256 columns, 250,000 cells and 4 MB of text.")


def _check_reference(reference):
    for coordinate in reference.split(":"):
        match = re.fullmatch(r"\$?([A-Za-z]+)\$?([1-9][0-9]*)", coordinate)
        if not match:
            _over_budget()
        column = 0
        for letter in match[1].upper():
            column = column * 26 + ord(letter) - ord("A") + 1
            if column > MAX_TABLE_COLUMNS:
                _over_budget()
        if int(match[2]) > MAX_TABLE_ROWS + 1:
            _over_budget()


class _XmlWithoutDtd:
    """Reject DTDs before ElementTree consumes them; XLSX uses UTF-8 XML."""

    def __init__(self, stream):
        self.stream = stream
        self.tail = b""

    def read(self, size=-1):
        chunk = self.stream.read(size)
        check = (self.tail + chunk).upper()
        if b"\0" in chunk or b"<!DOCTYPE" in check or b"<!ENTITY" in check:
            raise ValueError("Table XML with DTDs or unsupported encodings is not supported.")
        self.tail = check[-16:]
        return chunk


def preflight_table(file_path):
    if os.path.getsize(file_path) > 25 * 1024 * 1024:
        _over_budget()
    if file_path.lower().endswith(".csv"):
        cells, chars = 0, 0
        with open(file_path, encoding="utf-8-sig", newline="") as source:
            for row_number, row in enumerate(csv.reader(source), 1):
                cells += len(row)
                chars += sum(len(cell) for cell in row)
                if (
                    row_number > MAX_TABLE_ROWS + 1
                    or len(row) > MAX_TABLE_COLUMNS
                    or cells > MAX_TABLE_CELLS
                    or chars > MAX_TABLE_CHARS
                    or any(len(cell) > MAX_CELL_CHARS for cell in row)
                ):
                    _over_budget()
        return

    with zipfile.ZipFile(file_path) as archive:
        validate_archive(archive, max_expanded_bytes=32 * 1024 * 1024)
        nodes, cells, chars = 0, 0, 0
        for entry in archive.infolist():
            if not entry.filename.lower().endswith(".xml"):
                continue
            with archive.open(entry) as stream:
                for event, element in iterparse(_XmlWithoutDtd(stream), events=("start", "end")):
                    tag = element.tag.rsplit("}", 1)[-1]
                    if event == "start":
                        nodes += 1
                        if nodes > 1_000_000:
                            _over_budget()
                        if tag == "dimension" and element.get("ref"):
                            _check_reference(element.get("ref"))
                        if tag == "c":
                            cells += 1
                            if element.get("r"):
                                _check_reference(element.get("r"))
                            if cells > MAX_TABLE_CELLS:
                                _over_budget()
                        if tag == "row" and int(element.get("r", "1")) > MAX_TABLE_ROWS + 1:
                            _over_budget()
                    else:
                        text = element.text or ""
                        chars += len(text)
                        if len(text) > MAX_CELL_CHARS or chars > MAX_TABLE_CHARS:
                            _over_budget()
                        element.clear()
