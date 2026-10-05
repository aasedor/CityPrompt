"""Render pinned City plan maps into geographic, transparent, multiresolution tiles.

Inputs stay outside Git. No online work, OCR or generated cartography at runtime.
Usage: python tools/policy_maps/tile_citywide.py --sources C:/source --output C:/review
Promote only the reviewed output. See citywide_calibration.json for source locks.
"""
import argparse,hashlib,json
from pathlib import Path
import fitz
import numpy as np
from PIL import Image
from pyproj import Transformer

HERE=Path(__file__).resolve().parent
SPECS=[
 ('mdp-1','mdp',188,[43,144,750,1030],[47,1034,751,1185],[[678,203,733,270],[43,970,285,1000],[590,1016,735,1030]]),
 ('mdp-2','mdp',189,[44,145,750,1057],[49,1057,751,1185],[[680,204,735,267],[594,1025,736,1057]]),
 ('mdp-3','mdp',190,[35,146,742,1057],[41,1047,505,1182],[[677,204,732,267],[35,1047,333,1058],[585,1024,730,1057]]),
 ('mdp-4','mdp',191,[43,145,748,1028],[46,1018,143,1114],[[680,204,735,267],[586,1011,735,1028],[43,1018,143,1028]]),
 ('mdp-5','mdp',192,[45,130,755,1065],[44,1075,700,1170],[[680,204,735,266],[580,1032,740,1065],[175,120,260,136]]),
 ('mdp-6','mdp',193,[40,142,722,1078],[39,1078,613,1185],[[679,206,726,266],[574,1040,710,1071],[41,976,123,997]]),
 ('ctp-1','ctp',100,[20,217,744,1108],[27,816,307,1102],[[680,197,738,255],[22,815,282,910],[22,910,190,1038],[22,1038,250,1061],[22,1061,310,1108],[25,766,110,783]]),
 ('ctp-2','ctp',101,[40,149,745,1060],[46,1061,747,1188],[[680,200,738,266],[590,1027,735,1060]]),
 ('ctp-3','ctp',102,[36,151,645,1182],[642,816,764,1184],[[122,196,173,251]]),
 ('ctp-5','ctp',104,[44,148,746,1078],[44,1079,680,1188],[[680,200,738,266],[590,1022,736,1053]]),
 ('ctp-6','ctp',105,[40,147,743,1060],[41,1063,368,1188],[[680,200,738,266],[590,1028,736,1060]]),
 ('ctp-7','ctp',106,[32,149,740,1059],[40,1050,504,1188],[[680,200,738,266],[580,1028,732,1059],[32,1049,100,1059]]),
]

def transparent_paper(rgb):
    """Retain original RGB cartography; only near-white paper becomes transparent."""
    alpha=np.clip((250-rgb.min(axis=2).astype(float))*51,0,255).astype('uint8')
    return np.dstack([rgb,alpha])

def geographic_grid(rect,crop,matrix,translation,subdivisions=4):
    inverse=Transformer.from_crs(26911,4326,always_xy=True)
    points=[]
    for row in range(subdivisions+1):
        for col in range(subdivisions+1):
            u=rect[0]+col/subdivisions*(rect[2]-rect[0]);v=rect[1]+row/subdivisions*(rect[3]-rect[1])
            xy=np.array([crop[0]+u*(crop[2]-crop[0]),crop[1]+v*(crop[3]-crop[1])])
            east,north=np.array(matrix)@xy+translation
            points.append([round(x,8) for x in inverse.transform(east,north)])
    return points

def build(sources,output,only=None):
    calibration=json.loads((HERE/'citywide_calibration.json').read_text())
    for name,expected in calibration['sources'].items():
        if hashlib.sha256((sources/f'{name}.pdf').read_bytes()).hexdigest()!=expected['sha256']:
            raise ValueError(f'{name} PDF changed: review the edition, map pages and geographic alignment before extraction.')
    report=[]
    for map_id,name,page_num,crop,legend,exclusions in SPECS:
        if only and map_id!=only:continue
        with fitz.open(sources/f'{name}.pdf') as document:
            page=document[page_num-1];factor=4096/max(crop[2]-crop[0],crop[3]-crop[1])
            pix=page.get_pixmap(matrix=fitz.Matrix(factor,factor),clip=fitz.Rect(crop),alpha=False)
            rgb=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
            rgba=transparent_paper(rgb)
            annotations=exclusions+([[25,crop[1],190,175]] if map_id!='ctp-3' and crop[1]<175 else [])
            # Amendment notices are page furniture, not geographically located labels.
            # They all occupy the empty lower-left margin in these pinned sources.
            annotations += [[crop[0], 968, 285, crop[3]]] if map_id not in ('ctp-1','ctp-3','mdp-5','mdp-6') else []
            for x0,y0,x1,y1 in annotations:
                xa=max(0,round((x0-crop[0])*factor));xb=min(pix.width,round((x1-crop[0])*factor))
                ya=max(0,round((y0-crop[1])*factor));yb=min(pix.height,round((y1-crop[1])*factor))
                if xb>xa and yb>ya:rgba[ya:yb,xa:xb,3]=0
            raster=Image.fromarray(rgba).resize((4096,4096),Image.Resampling.LANCZOS)
            dest=output/map_id;dest.mkdir(parents=True,exist_ok=True)
            raster.resize((1024,1024),Image.Resampling.LANCZOS).save(dest/'overview.webp',lossless=True)
            lp=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(legend),alpha=False)
            legend_image=Image.frombytes('RGB',(lp.width,lp.height),lp.samples)
            # Remove adjacent artwork without touching the legend's symbols/text.
            from PIL import ImageDraw
            ink=ImageDraw.Draw(legend_image)
            if map_id=='mdp-1':ink.rectangle([int((530-legend[0])*3),0,lp.width,int((1056-legend[1])*3)],fill='white')
            if map_id=='ctp-1':
                ink.rectangle([int((282-legend[0])*3),0,lp.width,int((910-legend[1])*3)],fill='white')
                ink.rectangle([int((190-legend[0])*3),int((909-legend[1])*3),lp.width,int((989-legend[1])*3)],fill='white')
            if map_id=='ctp-3':legend_image=legend_image.transpose(Image.Transpose.ROTATE_270)
            legend_image.save(dest/'legend.webp',lossless=True)
        alignment=calibration['maps'][f'{name}-{page_num}'];tiles=[]
        for row in range(8):
            for col in range(8):
                image=raster.crop((col*512,row*512,(col+1)*512,(row+1)*512))
                if not image.getchannel('A').getbbox():continue
                tile_id=f'r{row}-c{col}';image.save(dest/f'{tile_id}.webp',lossless=True)
                rect=[col/8,row/8,(col+1)/8,(row+1)/8]
                tiles.append({'id':tile_id,'rect':rect,'grid':geographic_grid(rect,crop,alignment['matrix'],alignment['translation'])})
        all_points=np.array([point for tile in tiles for point in tile['grid']])
        metadata={'id':map_id,'overview':'overview.webp','gridSize':4,'tiles':tiles,'bounds':[*all_points.min(axis=0),*all_points.max(axis=0)],
                  'sourcePage':page_num,'sourceSha256':calibration['sources'][name]['sha256'],
                  'accuracy':'Aligned published policy artwork; conceptual map scale, not parcel or engineering accuracy.'}
        (dest/'map.json').write_text(json.dumps(metadata,separators=(',',':'))+'\n')
        report.append({'id':map_id,'tiles':len(tiles),'bytes':sum(p.stat().st_size for p in dest.iterdir() if p.is_file())})
        print(report[-1],flush=True)
    (output/'build-report.json').write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sources',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--only')
    args=parser.parse_args();build(args.sources,args.output,args.only)
