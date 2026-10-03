"""Bounded, offline Calgary DEM pilot preparation; never changes application ground.

Requires the existing local NumPy, pyproj and requests preparation environment.
Source ASC files and all generated output belong outside the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import requests
from pyproj import Transformer


class AsciiDem:
    def __init__(self, path: Path):
        with path.open() as stream:
            self.header = {parts[0].lower(): float(parts[1]) for parts in
                           (stream.readline().split() for _ in range(6))}
            self.values = np.loadtxt(stream)
        h = self.header
        if self.values.shape != (int(h['nrows']), int(h['ncols'])) or h['cellsize'] <= 0:
            raise ValueError('Invalid raster dimensions')
        self.sha256 = hashlib.sha256(path.read_bytes()).hexdigest()

    def sample(self, x: float, y: float) -> float:
        """Bilinear sample at cell centres; north-first rows, no no-data bridging."""
        h = self.header
        col = (x - h['xllcorner']) / h['cellsize'] - .5
        row = h['nrows'] - .5 - (y - h['yllcorner']) / h['cellsize']
        c, r = int(np.floor(col)), int(np.floor(row))
        if c < 0 or r < 0 or c + 1 >= h['ncols'] or r + 1 >= h['nrows']:
            raise ValueError('Point outside raster interpolation support')
        cells = self.values[r:r+2, c:c+2]
        if not np.isfinite(cells).all() or (cells == h['nodata_value']).any():
            raise ValueError('Missing ground data; interpolation refused')
        u, v = col-c, row-r
        return float((1-v)*((1-u)*cells[0, 0]+u*cells[0, 1]) + v*((1-u)*cells[1, 0]+u*cells[1, 1]))


def geoid(lat: float, lng: float, out: Path, tag: str, epoch: str = '2024-01-01') -> float:
    """Use the source-stated GSD95 model, explicitly recording frame/epoch assumptions."""
    params = dict(lang='en', proj='geo', x=lat, y=lng, z=0, frame='ITRF2014', epoch=epoch, model='GSD95')
    url = 'https://webapp.csrs-scrs.nrcan-rncan.gc.ca/CSRS/tools/GPSH/GSD95'
    cache = out / f'geoid-{tag}.json'
    if cache.exists():
        saved = json.loads(cache.read_text())
        if saved['params'] != params:
            raise ValueError('Geoid cache does not match query')
        return saved['N']
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    match = re.search(r'(?:^|, )N: (-?\d+(?:\.\d+)?)', response.text)
    if not match or 'Errors: ok' not in response.text:
        raise ValueError('Geoid service did not provide a valid result')
    n = float(match[1])
    if not -25 < n < -5:
        raise ValueError('Geoid value outside the Calgary trial range')
    cache.write_text(json.dumps(dict(url=url, params=params, raw=response.text, N=n), indent=2))
    return n


def prepare(data: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    forward = Transformer.from_crs(4326, 3776, always_xy=True)
    inverse = Transformer.from_crs(3776, 4326, always_xy=True)
    # Finite trial: two 60 m squares. Street position is visually checked before
    # selecting a connection profile; an arbitrary grid line is not called a road.
    sites = [('slope', -114.1265, 51.0245, 'S0724015'),
             ('street', -114.1200, 51.0160, 'S0624015')]
    result = {'source': 'City of Calgary 2022–2024 bare-earth DEM, 2 m',
              'sourceVertical': 'CGVD28; GSD95 (ITRF version), as declared by Calgary',
              'displayVertical': 'Approximate ITRF2014/WGS84 ellipsoid',
              'limitations': ['NAD83 original to WGS84 ensemble operation has 4 m stated accuracy.',
                             'GSD95 service uses ITRF2014, epoch 2024; source reference epoch is not specified.',
                             'CGVD28 and the GSD95-derived surface are not assumed interchangeable with newer geoids.',
                             'No visual height fitting or Google-derived correction is applied.',
                             '2 m raster interpolation does not certify survey or accessibility accuracy.'],
              'sites': []}
    for name, lng, lat, section in sites:
        source = data / f'DEM_LIDAR_2022-2024_2m_{section}.asc'
        dem = AsciiDem(source)
        cx, cy = forward.transform(lng, lat)
        corners = [inverse.transform(cx+x, cy+y) for x, y in [(-30, -30), (30, -30), (30, 30), (-30, 30)]]
        geoids = [geoid(la, lo, out, f'{name}-{i}') for i, (lo, la) in enumerate(corners)]
        n0 = geoid(lat, lng, out, f'{name}-centre')
        points = []
        for j in range(31):
            for i in range(31):
                x, y = cx-30+i*2, cy-30+j*2
                lo, la = inverse.transform(x, y)
                u, v = i/30, j/30
                n = (1-v)*((1-u)*geoids[0]+u*geoids[1]) + v*((1-u)*geoids[3]+u*geoids[2])
                h = dem.sample(x, y)
                points.append([lo, la, h, h+n])
        heights = np.array([p[2] for p in points]).reshape(31, 31)
        profile = heights[:, 15]
        result['sites'].append(dict(name=name, center=[lng, lat], boundary=corners, columns=31, rows=31,
            spacingM=2, sourceFile=source.name, sourceSha256=dem.sha256, points=points,
            geoidCentreM=n0, geoidCornerRangeM=[min(geoids), max(geoids)],
            terrainRangeM=[float(heights.min()), float(heights.max())], reliefM=float(np.ptp(heights)),
            northSouthProfile=dict(lengthM=60, riseM=float(profile[-1]-profile[0]),
                                  maxSegmentGrade=float(np.max(np.abs(np.diff(profile)/2))))))
    result['horizontalOperation'] = inverse.description
    result['horizontalAccuracyM'] = inverse.accuracy
    # Visually reviewed street site: eastward profile reaches the paved approach
    # to the roundabout. This is a diagnostic corridor, not a saved design street.
    street = result['sites'][1]
    dem = AsciiDem(data/street['sourceFile'])
    cx, cy = forward.transform(*street['center'])
    end_lng, end_lat = inverse.transform(cx+60, cy)
    end_geoid = geoid(end_lat, end_lng, out, 'street-connection-end')
    profile, edges = [], []
    for i in range(31):
        x = cx + i*2
        n = street['geoidCentreM'] + (end_geoid-street['geoidCentreM'])*i/30
        lo, la = inverse.transform(x, cy)
        h = dem.sample(x, cy)
        profile.append([lo, la, h, h+n])
        pair = []
        for dy in [-3, 3]:
            lo, la = inverse.transform(x, cy+dy)
            h = dem.sample(x, cy+dy)
            pair.append([lo, la, h, h+n])
        edges.append(pair)
    street['connection'] = dict(lengthM=60, widthM=6, spacingM=2, profile=profile, edges=edges)
    (out/'trial-data.json').write_text(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = prepare(args.data, args.out)
    print(json.dumps({**report, 'sites': [{k:v for k,v in site.items() if k!='points'} for site in report['sites']]}, indent=2))
