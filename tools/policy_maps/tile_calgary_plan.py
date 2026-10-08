"""Extract the eight proposed maps from the pinned May 2026 annotated plan.

Render only each embedded map Form: page annotations, deleted text and the
watermark are separate PDF objects. Preserve map artwork and original legends.
UI and export metadata identify the proposed edition. Inputs/output stay outside
Git until visual review; never substitute another PDF without recalibration.
"""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np
from PIL import Image

from tile_citywide import geographic_grid, transparent_paper

HERE = Path(__file__).resolve().parent
SPECS = [(1,25,'Fm2'), (2,26,'Fm1'), (3,51,'Fm2'), (4,59,'Fm2'),
         (5,61,'Fm2'), (6,63,'Fm2'), (7,65,'Fm2'), (8,83,'Fm1')]


def artwork(document, page_number, form):
    clean = fitz.open()
    clean.insert_pdf(document, from_page=page_number-1, to_page=page_number-1)
    page = clean[0]
    if not any(name == form and parent == 0 for _,name,parent,_ in page.get_xobjects()):
        raise ValueError('Expected map Form is missing; review the source edition.')
    content = page.get_contents()[0]
    page.set_contents(content)
    clean.update_stream(content, f'q /{form} Do Q'.encode('ascii'))
    return clean


def build(source, output, only=None):
    calibration = json.loads((HERE/'calgary_plan_calibration.json').read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest() != calibration['sha256']:
        raise ValueError('Calgary Plan PDF changed: review the edition and alignment before extraction.')
    output.mkdir(parents=True, exist_ok=True)
    report = []
    with fitz.open(source) as document:
        for number,page_number,form in SPECS:
            if only and number != only:
                continue
            map_id = f'calgary-plan-{number}'
            crop = [28,397,575,737] if number == 2 else [36,46,549,622]
            legend = [30,640,276,735] if number == 2 else [36,605,549,721]
            # Only page furniture: source map number/title, legend heading and north arrow.
            exclusions = [[28,597,201,638], [28,639,277,737], [393,701,575,737], [548,397,575,424]] if number == 2 else [
                [36,533,60,546], [36,547,272 if number == 8 else 203,601], [36,605,72,622], [520,46,549,74]]
            with artwork(document, page_number, form) as clean:
                page = clean[0]
                factor = 4096/max(crop[2]-crop[0],crop[3]-crop[1])
                pix = page.get_pixmap(matrix=fitz.Matrix(factor,factor), clip=fitz.Rect(crop), alpha=False)
                rgb = np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
                rgba = transparent_paper(rgb)
                for x0,y0,x1,y1 in exclusions:
                    xa=max(0,round((x0-crop[0])*factor)); xb=min(pix.width,round((x1-crop[0])*factor))
                    ya=max(0,round((y0-crop[1])*factor)); yb=min(pix.height,round((y1-crop[1])*factor))
                    rgba[ya:yb,xa:xb,3]=0
                raster = Image.fromarray(rgba).resize((4096,4096),Image.Resampling.LANCZOS)
                dest = output/map_id
                dest.mkdir(parents=True,exist_ok=True)
                raster.resize((1024,1024),Image.Resampling.LANCZOS).save(dest/'overview.webp',lossless=True)
                lp=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(legend),alpha=False)
                Image.frombytes('RGB',(lp.width,lp.height),lp.samples).save(dest/'legend.webp',lossless=True)
            alignment = calibration['maps'][str(page_number)]
            tiles=[]
            for row in range(8):
                for col in range(8):
                    tile=raster.crop((col*512,row*512,(col+1)*512,(row+1)*512))
                    if not tile.getchannel('A').getbbox():
                        continue
                    tile_id=f'r{row}-c{col}'
                    tile.save(dest/f'{tile_id}.webp',lossless=True)
                    rect=[col/8,row/8,(col+1)/8,(row+1)/8]
                    tiles.append({'id':tile_id,'rect':rect,'grid':geographic_grid(rect,crop,alignment['matrix'],alignment['translation'])})
            points=np.array([p for tile in tiles for p in tile['grid']])
            metadata={'id':map_id,'overview':'overview.webp','gridSize':4,'tiles':tiles,
                      'bounds':[*points.min(axis=0),*points.max(axis=0)],'sourcePage':page_number,
                      'sourceSha256':calibration['sha256'],'edition':calibration['edition'],
                      'accuracy':'Aligned proposed policy artwork; conceptual map scale, not parcel or engineering accuracy.'}
            (dest/'map.json').write_text(json.dumps(metadata,separators=(',',':'))+'\n')
            report.append({'id':map_id,'tiles':len(tiles),'bytes':sum(p.stat().st_size for p in dest.iterdir())})
            print(report[-1],flush=True)
    (output/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--only',type=int,choices=range(1,9))
    args=parser.parse_args()
    build(args.source,args.output,args.only)
