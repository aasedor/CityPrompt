"""Extract Beltline ARP concept-map vectors from pinned official PDFs.

The City GIS plan boundary is authoritative for coverage. Map fills and road gaps
come from the PDF; no polygons are inferred from zoning or category names.
"""
import argparse
import hashlib
import json
from pathlib import Path
import fitz
import numpy as np
from pyproj import Transformer
from shapely import set_precision
from shapely.geometry import Polygon, LineString, mapping, shape
from shapely.ops import transform, unary_union
from extract_riley import path_geometry, path_parts, polygons


def hex_color(value):
    return '#' + ''.join(f'{round(v*255):02x}' for v in value) if value else None


def reviewed_paths(drawing):
    # PyMuPDF collapses four straight edges to a quadrilateral in Part 2.
    items=[]
    for item in drawing['items']:
        if item[0]=='qu':
            q=item[1]
            vertices=[q.ul,q.ur,q.lr,q.ll,q.ul]
            items.extend(('l',a,b) for a,b in zip(vertices,vertices[1:]))
        else:
            items.append(item)
    return {**drawing,'items':items}


def extract(pdf, config):
    if hashlib.sha256(Path(pdf).read_bytes()).hexdigest()!=config['source_sha256']:
        raise ValueError('PDF changed. Review its vector paths, legend and calibration before extraction.')
    with fitz.open(pdf) as document:
        drawings=document[config['pdf_page']-1].get_drawings()
    categories=config['categories']
    areas={color:Polygon() for color in categories}
    for index in config['fill_indices']:
        drawing=reviewed_paths(drawings[index])
        color=hex_color(drawing['fill'])
        if color not in categories and color not in config['mask_colors']:
            raise ValueError(f'Unexpected reviewed fill {index}: {color}')
        geometry=set_precision(path_geometry(drawing),1e-5)
        for key in areas:
            areas[key]=areas[key].difference(geometry)
        if color in areas:
            areas[color]=unary_union([areas[color],geometry])
    roads=[]
    for drawing in drawings:
        if drawing['fill'] is None and hex_color(drawing['color'])=='#ffffff' and abs(drawing['width']-config['road_width'])<.001:
            for part in path_parts(reviewed_paths(drawing)):
                if len(part)>1:
                    roads.append(LineString(part).buffer(drawing['width']/2,quad_segs=4))
    road_mask=unary_union(roads)
    matrix=np.array(config['matrix']);offset=np.array(config['translation'])
    inverse=Transformer.from_crs(config['crs'],4326,always_xy=True)
    def world(x,y,z=None):
        return inverse.transform(matrix[0,0]*np.array(x)+matrix[0,1]*np.array(y)+offset[0],matrix[1,0]*np.array(x)+matrix[1,1]*np.array(y)+offset[1])
    boundary=shape(config['boundary']);occupied=Polygon();features=[]
    for color,area in areas.items():
        geographic=unary_union([set_precision(set_precision(transform(world,piece),1e-7),0) for piece in polygons(area.difference(road_mask)) if piece.area>=.01])
        geographic=geographic.intersection(boundary).difference(occupied)
        occupied=unary_union([occupied,geographic])
        for piece in polygons(geographic):
            if not piece.is_empty:
                features.append({'type':'Feature','id':f"{config['id']}-land-use-{len(features)+1}",'properties':{'category':categories[color],'color':color},'geometry':mapping(piece)})
    return {'type':'FeatureCollection','snapshot':f"{config['id']}-land-use-{config['source_sha256'][:12]}",'source':config['source_url'],'sourcePage':config['pdf_page'],'boundary':config['boundary'],'bounds':list(boundary.bounds),'features':features}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan');parser.add_argument('pdf',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    config=json.loads((Path(__file__).parent/'beltline_calibrations.json').read_text())[args.plan]
    data=extract(args.pdf,config)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,separators=(',',':'))+'\n',encoding='utf8')
    print(f"Extracted {len(data['features'])} source polygons to {args.output}")
