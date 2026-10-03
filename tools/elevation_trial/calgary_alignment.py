"""Explicit, offline coordinate alignment for the bounded Calgary DEM trial.

The baseline deliberately used NAD83 longitude/latitude as WGS84. Recover those
same source positions, then apply Alberta's original -> CSRSv7 grid and EPSG
8265 in reverse at the grid's epoch (2010). Heights use GPSH's GSD95 in that same
ITRF2014 frame/epoch. No mesh fitting or production ground changes are made.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

from pyproj import Geod, Transformer, __proj_version__, __version__
from pyproj.enums import TransformDirection

from tools.elevation_trial.calgary_dem import geoid


GRID_URL = ('https://open.alberta.ca/dataset/2f2c8a98-ed4d-435b-ae03-63c21db84364/'
            'resource/8e17411b-3f59-4842-8abc-b84552a59452/download/abcsrsv7.dac')
GRID_SHA256 = 'f5cf8cfa53e6922ebfa02d4b76400d02c84b840cf5a298b79b00bb82606cf2aa'
EPOCH = 2010.0
EPOCH_DATE = '2010-01-01'


class CalgaryAlignment:
    def __init__(self, grid: Path):
        if hashlib.sha256(grid.read_bytes()).hexdigest() != GRID_SHA256:
            raise ValueError('Unrecognized Alberta grid; alignment refused')
        # A required grid, with no @optional flag or identity fallback.
        self.grid = Transformer.from_pipeline(
            '+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad '
            f'+step +proj=hgridshift +grids="{grid.resolve().as_posix()}" '
            '+step +proj=unitconvert +xy_in=rad +xy_out=deg')
        self.frame = Transformer.from_crs(8254, 7912, always_xy=True,
                                          allow_ballpark=False, only_best=True)
        operation = self.frame.to_json_dict()
        if not any(step.get('id') == {'authority': 'INVERSE(EPSG)', 'code': 8265}
                   for step in operation.get('steps', [])):
            raise ValueError('Expected inverse EPSG:8265 frame operation')

    @staticmethod
    def _validate(lng: float, lat: float, height: float):
        if not all(math.isfinite(v) for v in (lng, lat, height)):
            raise ValueError('Non-finite coordinate')
        if not (-114.5 < lng < -113.7 and 50.75 < lat < 51.3 and 500 < height < 2000):
            raise ValueError('Coordinate outside the bounded Calgary trial')

    def display_lonlat(self, lng: float, lat: float, itrf_height: float) -> tuple:
        """Align horizontal coordinates at an independently converted ITRF height.

        Solve the CSRS ellipsoid height needed by the 3D Helmert operation. Its
        output height must NOT be added to H+N again: GPSH already supplies N in
        the target frame. Two refinements avoid using an orthometric height as
        though it were a CSRS ellipsoid height.
        """
        self._validate(lng, lat, itrf_height)
        csrs_lng, csrs_lat = self.grid.transform(lng, lat, errcheck=True)
        csrs_height = itrf_height
        for _ in range(3):
            lo, la, h, _ = self.frame.transform(csrs_lng, csrs_lat, csrs_height,
                                               EPOCH, errcheck=True)
            csrs_height += itrf_height - h
        if abs(h - itrf_height) > 1e-6:
            raise ValueError('Frame height solution did not converge')
        return lo, la

    def source_lonlat(self, lng: float, lat: float, itrf_height: float) -> tuple:
        self._validate(lng, lat, itrf_height)
        lo, la, _, _ = self.frame.transform(lng, lat, itrf_height, EPOCH,
                                            direction=TransformDirection.INVERSE,
                                            errcheck=True)
        return self.grid.transform(lo, la, direction=TransformDirection.INVERSE,
                                   errcheck=True)

    def provenance(self) -> dict:
        return dict(gridUrl=GRID_URL, gridSha256=GRID_SHA256,
                    gridTarget='NAD83(CSRS)v7, epoch 2010.0',
                    frameOperation='Inverse EPSG:8265', coordinateEpoch=EPOCH,
                    framePipeline=self.frame.definition, pyprojVersion=__version__,
                    projVersion=__proj_version__, displayFrame='ITRF2014',
                    horizontalAccuracyM=None, visualOffsetM=0,
                    note='Operation accuracy 0 denotes the frame definition, not survey accuracy.')


def align_trial(baseline: dict, alignment: CalgaryAlignment, out: Path) -> dict:
    # This reader is intentionally tied to the recorded identity-datum baseline.
    # A different baseline requires its own inverse operation, never this shortcut.
    if (baseline.get('horizontalAccuracyM') != 4 or
            'NAD83 to WGS 84 (1)' not in baseline.get('horizontalOperation', '')):
        raise ValueError('Expected the original 4 m identity-datum baseline')
    if not baseline.get('sites') or any(
            s.get('columns') != 31 or s.get('rows') != 31 or
            len(s.get('points', [])) != 961 or len(s.get('boundary', [])) != 4 or
            ('connection' in s and (len(s['connection'].get('profile', [])) != 31 or
                                   len(s['connection'].get('edges', [])) != 31))
            for s in baseline['sites']):
        raise ValueError('Expected 31 by 31 trial grids and 31 point connection')
    out.mkdir(parents=True, exist_ok=True)
    result = deepcopy(baseline)
    geodesic = Geod(ellps='WGS84')
    for original, site in zip(baseline['sites'], result['sites']):
        source_centre = original['center']
        centre_h = original['points'][480][2]
        centre = alignment.display_lonlat(*source_centre, centre_h - 16)
        n0 = geoid(centre[1], centre[0], out, f"{site['name']}-centre", EPOCH_DATE)
        site['center'] = alignment.display_lonlat(*source_centre, centre_h + n0)
        site['sourceCenterLonLatNAD83'] = source_centre
        geoids, boundary = [], []
        for i, point in enumerate(original['boundary']):
            lo, la = alignment.display_lonlat(*point, centre_h + n0)
            boundary.append([lo, la])
            geoids.append(geoid(la, lo, out, f"{site['name']}-{i}", EPOCH_DATE))
        site['boundary'] = boundary
        def converted(point, n):
            h = point[2] + n
            return [*alignment.display_lonlat(*point[:2], h), point[2], h]
        shifts = []
        for i, point in enumerate(original['points']):
            u, v = (i % 31) / 30, (i // 31) / 30
            n = ((1-v)*((1-u)*geoids[0]+u*geoids[1]) +
                 v*((1-u)*geoids[3]+u*geoids[2]))
            site['points'][i] = converted(point, n)
            shifts.append(geodesic.inv(*point[:2], *site['points'][i][:2])[2])
        site['horizontalShiftRangeM'] = [min(shifts), max(shifts)]
        site['geoidCentreM'] = n0
        site['geoidCornerRangeM'] = [min(geoids), max(geoids)]
        if 'connection' in original:
            end = original['connection']['profile'][-1]
            lo, la = alignment.display_lonlat(*end[:2], end[2] + n0)
            n_end = geoid(la, lo, out, 'street-connection-end', EPOCH_DATE)
            for i, point in enumerate(original['connection']['profile']):
                n = n0 + (n_end-n0)*i/30
                site['connection']['profile'][i] = converted(point, n)
                site['connection']['edges'][i] = [
                    converted(p, n) for p in original['connection']['edges'][i]]
    result.update(horizontalOperation='ABCSRSV7 + inverse EPSG:8265 at 2010.0',
                  horizontalAccuracyM=None, alignment=alignment.provenance(),
                  displayVertical='GSD95-derived ITRF2014 ellipsoid at epoch 2010.0',
                  limitations=[
                      'ITRF2014 at 2010 is used as approximate WGS84 display coordinates; Google realization/epoch is unspecified.',
                      'No propagation from Alberta grid epoch 2010 to imagery epoch is claimed.',
                      'Source CGVD28/GSD95 relationship is taken from Calgary metadata, not independently surveyed control.',
                      'Combined absolute accuracy is unquantified; 2 m raster is not construction control.',
                      'No fitted visual offset. Buildings, trees and tile reconstruction can disagree with bare earth.'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--grid', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.baseline.resolve() == (args.out/'trial-data.json').resolve():
        parser.error('Use a new output directory; preserve the baseline')
    report = align_trial(json.loads(args.baseline.read_text()), CalgaryAlignment(args.grid), args.out)
    report['baselineSha256'] = hashlib.sha256(args.baseline.read_bytes()).hexdigest()
    (args.out/'trial-data.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(dict(alignment=report['alignment'], sites=[
        dict(name=s['name'], shiftM=s['horizontalShiftRangeM'], geoidM=s['geoidCentreM'])
        for s in report['sites']]), indent=2))
