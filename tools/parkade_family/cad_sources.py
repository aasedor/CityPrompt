"""Original dimensioned design drawings, independent of any candidate mesh.

The AI mood sheets are archived as aesthetic exploration. They do not control
dimensions, bay counts, rear ramp topology, or reviewed geometry.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image,ImageDraw,ImageFont


def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--ramp-source',type=Path,required=True)
    p.add_argument('--aesthetic-sheet',type=Path,action='append',required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
    title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',30)
    def page(role,subtitle):
        im=Image.new('RGB',(1600,1100),'#fffdf5');d=ImageDraw.Draw(im)
        d.text((45,24),'CLASSIC CONCRETE / ORIGINAL METRIC DESIGN',font=title,fill='#14282f')
        d.text((45,76),subtitle,font=font,fill='#14282f')
        d.text((45,1038),'Design authority v003 / 60 x 36 x 12.8 m / four levels / native fixed size / concept only',font=font,fill='#14282f')
        return im,d
    im,d=page('front','FRONT ELEVATION / floor datums 0.15, 3.45, 6.75, 10.05 m; tower caps 12.80 m')
    s=23;ox=800;oy=780
    def rect(x0,z0,x1,z1,fill,outline='#46575c'):
        d.rectangle((ox+x0*s,oy-z1*s,ox+x1*s,oy-z0*s),fill=fill,outline=outline,width=2)
    rect(-30,0,30,.15,'#b7b9af')
    for z in (3.45,6.75,10.05):rect(-25.2,z-.57,25.2,z-.07,'#b7b9af')
    for x in range(-24,25,6):rect(x-.25,.15,x+.25,11.15,'#b7b9af')
    for z in (3.45,6.75,10.05):
        for h in (.32,.68,1.1):d.line((ox-25*s,oy-(z+h)*s,ox+25*s,oy-(z+h)*s),fill='#354b54',width=2)
    for cx in (-27.5,27.5):
        rect(cx-2.3,.15,cx+2.3,12.62,'#b8d2d8')
        for x in (cx-2.3,cx-.8,cx+.8,cx+2.3):d.line((ox+x*s,oy-.15*s,ox+x*s,oy-12.62*s),fill='#354b54',width=2)
        for z in (.15,3.45,6.75,10.05):
            d.line((ox+(cx-2.3)*s,oy-z*s,ox+(cx+2.3)*s,oy-z*s),fill='#354b54',width=2)
            if z<10:
                d.line([(ox+(cx-1.8)*s,oy-z*s),(ox+(cx+1.8)*s,oy-(z+1.65)*s),(ox+(cx-1.8)*s,oy-(z+3.3)*s)],fill='#657f88',width=3)
        rect(cx-2.4,12.62,cx+2.4,12.8,'#354b54')
    rect(-23.725,2.625,-18.275,3.275,'#24393e')
    d.text((ox-22.8*s,oy-3.13*s),'ENTRANCE',font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',16),fill='#fffdf5')
    d.line((ox-30*s,850,ox+30*s,850),fill='#14282f',width=2)
    d.text((740,860),'60.00 m',font=font,fill='#14282f')
    d.text((180,920),'Eight principal 6 m bays between x=-24 and +24; narrow core transition at each end.',font=font,fill='#14282f')
    im.save(a.output/'front.png')
    im,d=page('top','TOP PLAN / dimensioned envelope, stair cores, fixed bays and continuous rear ramp well')
    s=20;ox=800;oy=560
    def plan(rect,fill,outline='#46575c'):
        x0,x1,y0,y1=rect;d.rectangle((ox+x0*s,oy-y1*s,ox+x1*s,oy-y0*s),fill=fill,outline=outline,width=2)
    plan((-30,30,-18,18),'#d7d7ca')
    plan((-23,23,11.5,18),'#b1cdd2')
    for x in (-30,23):plan((x,x+7,11.5,18),'#c6c8bd')
    for cx in (-27.5,27.5):plan((cx-2.3,cx+2.3,-17.9,-11.4),'#9ab9c2')
    for ya,yb,lo in [(-17,-11.5,-16.2),(-5.5,0,-21.6),(0,5.5,-21.6)]:
        n=round((21.6-lo)/2.7)
        for i in range(n+1):
            x=lo+i*2.7;d.line((ox+x*s,oy-ya*s,ox+x*s,oy-yb*s),fill='#fffdf5',width=2)
    for x in (-24,-18,-12,-6,0,6,12,18,24):
        for y in (-17.75,-5.75,5.75):plan((x-.25,x+.25,y-.25,y+.25),'#7f8e8c')
    d.text((420,230),'CONTINUOUS REAR RAMP WELL / 6 m CLEAR',font=font,fill='#14282f')
    d.line((430,265,1150,265),fill='#244c5c',width=5);d.polygon([(1150,265),(1130,253),(1130,277)],fill='#244c5c')
    d.text((460,960),'60.00 m width x 36.00 m depth; both stair cores included',font=font,fill='#14282f')
    im.save(a.output/'top.png')
    im,d=page('oblique','DESIGN AXONOMETRIC / metric frame and slender continuous glazed cores; not a model render')
    def point(x,y,z):return (800+(x*.8+y*.6)*18,760+(x*.25-y*.3-z)*18)
    def box(x0,x1,y0,y1,z0,z1,colour):
        faces=[[(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],
               [(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],
               [(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]]
        for face in faces:d.polygon([point(*v) for v in face],fill=colour,outline='#516167',width=2)
    for z in (.15,3.45,6.75,10.05):
        box(-30,30,-18,11.5,max(0,z-.25),z,'#c3c4b8')
        for xa,xb in [(-30,-23),(23,30)]:box(xa,xb,11.5,18,max(0,z-.25),z,'#c3c4b8')
    for x in range(-24,25,6):
        for y in (-17.75,-5.75,5.75):box(x-.25,x+.25,y-.25,y+.25,.15,11.15,'#b7b9af')
    for z in (3.45,6.75,10.05):
        for h in (.32,.68,1.1):
            d.line([point(-25,-17.8,z+h),point(25,-17.8,z+h)],fill='#354b54',width=2)
    for cx in (-27.5,27.5):
        box(cx-2.3,cx+2.3,-17.85,-11.45,.15,12.62,'#a7c6cc')
        for x in (cx-2.3,cx-.8,cx+.8,cx+2.3):d.line([point(x,-17.85,.15),point(x,-17.85,12.62)],fill='#354b54',width=2)
        for z in (.15,3.45,6.75,10.05):d.line([point(cx-2.3,-17.85,z),point(cx+2.3,-17.85,z)],fill='#354b54',width=2)
        box(cx-2.4,cx+2.4,-17.95,-11.35,12.62,12.8,'#354b54')
    d.text((100,945),'Exact internal openings and rear supports: dimensioned top plan + circulation section.',font=font,fill='#14282f')
    im.save(a.output/'oblique.png')
    shutil.copy2(a.ramp_source,a.output/'ramp_section.png')
    records=[]
    for role in ('front','oblique','top','ramp_section'):
        raw=(a.output/(role+'.png')).read_bytes();records.append(dict(role=role,file=role+'.png',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    aesthetics=[]
    for i,sheet in enumerate(a.aesthetic_sheet,1):
        file=f'aesthetic-study-{i}.png';shutil.copy2(sheet,a.output/file)
        aesthetics.append(dict(file=file,sha256=hashlib.sha256(sheet.read_bytes()).hexdigest(),authority='aesthetic exploration only; NOT dimensional or model-review authority'))
    provenance=dict(origin='original_authored_design',author='CityPrompt parkade initiative',date='2026-10-17',
        source_type='independently authored metric CAD-style design drawings, not candidate screenshots',records=records,
        aesthetic_references=aesthetics,supersedes='classic-sources-v002 exact-model source authority; preserve its failed v003 review',
        authority='These metric drawings govern envelope, bay cadence, continuous core glazing and rear circulation. AI sheets retain palette/grammar inspiration only.',
        limitations=['Original concept design, no engineering/accessibility/swept-path certification.','Oblique is schematic drawing; top and front govern coordinates.'])
    (a.output/'generation-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    shutil.copy2(__file__,a.output/'cad_sources.py')


if __name__=='__main__':main()
