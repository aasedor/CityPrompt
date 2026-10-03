"""Prepare the two bounded road-edge rehearsals; generated data stays outside Git."""
import argparse
import json
import math
from pathlib import Path

from pyproj import Transformer

from tools.elevation_trial.calgary_alignment import CalgaryAlignment, EPOCH_DATE
from tools.elevation_trial.calgary_dem import AsciiDem, geoid


class LocalFrame:
    """Match the viewer's WGS84 east/north/up frame through geocentric coordinates."""
    def __init__(self, lng, lat, height, heading):
        self.to_ecef = Transformer.from_crs(4979, 4978, always_xy=True)
        self.to_geo = Transformer.from_crs(4978, 4979, always_xy=True)
        self.origin = self.to_ecef.transform(lng, lat, height)
        lo, la = math.radians(lng), math.radians(lat)
        self.east = (-math.sin(lo), math.cos(lo), 0)
        self.north = (-math.sin(la)*math.cos(lo), -math.sin(la)*math.sin(lo), math.cos(la))
        self.up = (math.cos(la)*math.cos(lo), math.cos(la)*math.sin(lo), math.sin(la))
        self.angle = math.radians(90-heading)

    def geographic(self, x, y):
        east = x*math.cos(self.angle)-y*math.sin(self.angle)
        north = x*math.sin(self.angle)+y*math.cos(self.angle)
        return self.to_geo.transform(*(p+east*e+north*n for p,e,n in zip(self.origin,self.east,self.north)))

    def local_height(self, lng, lat, height):
        point = self.to_ecef.transform(lng,lat,height)
        return sum((p-o)*u for p,o,u in zip(point,self.origin,self.up))


def prepare(data: Path, grid: Path, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    alignment = CalgaryAlignment(grid)
    projected = Transformer.from_crs(4269, 3776, always_xy=True)
    geographic = Transformer.from_crs(3776, 4269, always_xy=True)
    # Finite batch: clear outfield and a constrained public-road connection.
    # Positions are locked to the original trial's NAD83 source coordinates.
    cases = [('field', -114.1265, 51.0245, 'S0724015', -2, -65, 0, 36, 10, 4),
             ('connection', -114.12, 51.016, 'S0624015', 27, -18, 90, 32, 6, 4)]
    reports = []
    for name,lng,lat,section,dx,dy,heading,length,blend,end in cases:
        source = data/f'DEM_LIDAR_2022-2024_2m_{section}.asc'
        dem = AsciiDem(source)
        cx,cy = projected.transform(lng,lat)
        sx,sy = cx+dx,cy+dy
        original_lng,original_lat = geographic.transform(sx,sy)
        orthometric = dem.sample(sx,sy)
        lo,la = alignment.display_lonlat(original_lng,original_lat,orthometric-16)
        n = geoid(la,lo,out,f'road-{name}-centre',EPOCH_DATE)
        h0 = orthometric+n
        lo,la = alignment.display_lonlat(original_lng,original_lat,h0)
        frame = LocalFrame(lo,la,h0,heading)
        def sample(x,y):
            lon,latitude,h = frame.geographic(x,y)
            old_lon,old_lat = alignment.source_lonlat(lon,latitude,h)
            px,py = projected.transform(old_lon,old_lat)
            # Centre geoid over this small footprint, explicitly recorded.
            return frame.local_height(lon,latitude,dem.sample(px,py)+n)
        width = math.ceil(3+.6+blend)
        ground = [dict(x=x,y=y,z=sample(x,y))
                  for x in range(-end,length+end+1) for y in range(-width,width+1)]
        output = dict(origin=[lo,la,h0],headingDegrees=heading,length=length,
                      halfWidth=3,blendWidth=blend,endBlend=end,
                      profile=[dict(x=x,z=sample(x,0)) for x in range(0,length+1,2)],
                      ground=ground,label=name,provenance=dict(
                          sourceFile=source.name,sourceSha256=dem.sha256,
                          alignment=alignment.provenance(),geoidCentreM=n,
                          geoidApproximation='Centre GSD95 value over the bounded corridor',
                          localFrame='WGS84 ECEF/ENU, matching the viewer',
                          sourceUncertainty='No construction accuracy or Google datum agreement claimed'))
        (out/f'{name}.json').write_text(json.dumps(output,indent=2))
        reports.append(dict(name=name,origin=output['origin'],points=len(ground)))
    return reports


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--grid',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.data,args.grid,args.out),indent=2))
