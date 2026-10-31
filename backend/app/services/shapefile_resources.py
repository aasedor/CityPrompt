"""Preflight ZIP and shapefile allocation declarations before native parsing."""

import struct

MAX_ARCHIVE_ENTRIES = 100
MAX_EXPANDED_BYTES = 100 * 1024 * 1024
MAX_RECORDS = 2000
MAX_POSITIONS = 100_000
MAX_POLYGON_RING_WORK = 1_000_000


def validate_archive(archive, *, max_expanded_bytes=MAX_EXPANDED_BYTES):
    entries = archive.infolist()
    if len(entries) > MAX_ARCHIVE_ENTRIES or sum(entry.file_size for entry in entries) > max_expanded_bytes:
        raise ValueError(
            f"The ZIP is too large when expanded (maximum {max_expanded_bytes // (1024 * 1024)} MB and 100 entries)."
        )
    if any(entry.flag_bits & 1 for entry in entries):
        raise ValueError("Encrypted ZIP archives are not supported.")
    if any(
        (entry.filename.lower().endswith(".prj") and entry.file_size > 64 * 1024)
        or (entry.filename.lower().endswith(".cpg") and entry.file_size > 128)
        for entry in entries
    ):
        raise ValueError("The shapefile sidecar text is too large (.prj maximum 64 KB; .cpg maximum 128 bytes).")
    names = [entry.filename for entry in entries if not entry.is_dir()]
    if len({name.lower() for name in names}) != len(names):
        raise ValueError("The ZIP contains ambiguous duplicate filenames.")
    return names


def validate_shapefile_components(shp: bytes, dbf: bytes, shx: bytes | None):
    """Check record counts and point/part lengths before PyShp allocates arrays."""

    def invalid():
        raise ValueError("The shapefile geometry exceeds the coordinate budget or has invalid record lengths.")

    if len(shp) < 100 or struct.unpack_from(">I", shp)[0] != 9994:
        invalid()
    if struct.unpack_from(">I", shp, 24)[0] * 2 != len(shp):
        invalid()
    offset, records, positions, polygon_ring_work = 100, 0, 0, 0
    while offset < len(shp):
        if offset + 12 > len(shp):
            invalid()
        length = struct.unpack_from(">I", shp, offset + 4)[0] * 2
        start, end = offset + 8, offset + 8 + length
        if length < 4 or end > len(shp):
            invalid()
        kind = struct.unpack_from("<I", shp, start)[0]
        records += 1
        if records > MAX_RECORDS:
            invalid()
        if kind in (1, 11, 21):
            count = 1
            if length < 20:
                invalid()
        elif kind in (8, 18, 28):
            if length < 40:
                invalid()
            count = struct.unpack_from("<I", shp, start + 36)[0]
            if 40 + count * 16 > length:
                invalid()
        elif kind in (3, 5, 13, 15, 23, 25, 31):
            if length < 44:
                invalid()
            parts, count = struct.unpack_from("<II", shp, start + 36)
            # MultiPatch includes a second per-part array (part types).
            if not 1 <= parts <= count or 44 + parts * (8 if kind == 31 else 4) + count * 16 > length:
                invalid()
            if count > MAX_POSITIONS - positions:
                invalid()
            if kind in (5, 15, 25):
                # PyShp associates holes with exteriors before output caps can
                # run. Bound candidates and repeated containment/area work,
                # including many individually small records in one dataset.
                polygon_ring_work += parts * count
                if polygon_ring_work > MAX_POLYGON_RING_WORK:
                    raise ValueError(
                        "The polygon ring association work exceeds the import budget. "
                        "Split complex multipart polygons into separate features or import a smaller area."
                    )
            # PyShp slices the points array using these starts. Overlapping or
            # backwards ranges can multiply bounded source points into billions
            # of GeoJSON coordinates before the later output budget runs.
            previous, previous_minimum = -1, 0
            for part in range(parts):
                part_start = struct.unpack_from("<i", shp, start + 44 + part * 4)[0]
                if (
                    not 0 <= part_start < count
                    or (part == 0 and part_start != 0)
                    or (part > 0 and part_start - previous < previous_minimum)
                ):
                    invalid()
                if kind == 31:
                    part_type = struct.unpack_from("<i", shp, start + 44 + parts * 4 + part * 4)[0]
                    if not 0 <= part_type <= 5:
                        invalid()
                    minimum = 3 if part_type in (0, 1) else 4
                else:
                    minimum = 2 if kind in (3, 13, 23) else 4
                previous, previous_minimum = part_start, minimum
            if count - previous < previous_minimum:
                invalid()
        elif kind == 0:
            count = 0
        else:
            invalid()
        positions += count
        if positions > MAX_POSITIONS:
            invalid()
        offset = end
    if shx is not None and (len(shx) < 100 or (len(shx) - 100) % 8 or (len(shx) - 100) // 8 != records):
        invalid()
    if len(dbf) < 33:
        invalid()
    rows, header, row_size = struct.unpack_from("<IHH", dbf, 4)
    if (
        rows > MAX_RECORDS
        or header < 33
        or header > len(dbf)
        or (header - 33) // 32 > 256
        or not 0 < row_size <= 32 * 1024
        or header + rows * row_size > len(dbf)
        or len(dbf) > 4 * 1024 * 1024
    ):
        invalid()
