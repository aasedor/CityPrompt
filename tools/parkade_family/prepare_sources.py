"""Split the original design sheet and enroll an explicit circulation drawing.

No repainting or generated replacement content: rectangular panel extraction only.
The ramp drawing is a separate original metric design, not model-derived proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('sheet',type=Path);parser.add_argument('output',type=Path)
    a=parser.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    shutil.copy2(a.sheet,a.output/'original-sheet.png')
    records=[]
    def enroll(role,file,**other):
        raw=(a.output/file).read_bytes()
        records.append(dict(role=role,file=file,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),**other))
    with Image.open(a.sheet) as image:
        if image.size!=(1774,887):raise ValueError('Unexpected sheet dimensions; review crop coordinates')
        for role,crop in [('oblique',(1,1,993,886)),('front',(996,1,1773,391)),('top',(996,394,1773,886))]:
            image.crop(crop).save(a.output/(role+'.png'))
            enroll(role,role+'.png',operation='lossless rectangular PNG extraction',source_crop_px=crop)
    im=Image.new('RGB',(1600,1050),'#fffdf5');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
    title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',32)
    def text(x,y,value,large=False):d.text((x,y),value,fill='#202e34',font=title if large else font)
    text(50,25,'CLASSIC CONCRETE / CIRCULATION DESIGN v1',True)
    text(50,80,'Authority for rear-strip topology, openings, partitions and ramps. Not an engineered layout.')
    text(50,135,'REAR LONGITUDINAL SECTION: three parallel ramps, same rising direction',True)
    x0,x1=140,1440; ybase=555; sx=(x1-x0)/60; sz=28
    for i in range(4):
        z=.15+i*3.3; yy=ybase-z*sz
        for lo,hi in [(-30,-23),(23,30)]:
            d.rectangle((x0+(lo+30)*sx,yy,x0+(hi+30)*sx,yy+7),fill='#798083')
        text(50,yy-15,f'L{i+1}')
    for i in range(3):
        ya=ybase-(.15+i*3.3)*sz;yb=ybase-(.15+(i+1)*3.3)*sz
        d.line((x0+7*sx,ya,x0+53*sx,yb),fill='#2c7789',width=9)
    text(240,575,'Ramp run 46 m / rise 3.3 m / clear width 6 m / slope 7.17%')
    text(240,610,'Aligned ramp-to-ramp clear height: 3.10 m before any future services')
    text(50,675,'PLAN: rear ramp well + end landings; return through main-deck aisles',True)
    d.rectangle((140,740,1440,930),outline='#202e34',width=3)
    d.rectangle((140+7*sx,741,140+53*sx,790),fill='#d7e8ed',outline='#2c7789',width=3)
    d.line((350,765,1230,765),fill='#2c7789',width=5)
    d.polygon([(1230,765),(1212,755),(1212,775)],fill='#2c7789')
    text(490,746,'Ramp lane: 6 m clear')
    text(460,838,'Main parking deck and circulation aisles')
    text(50,975,'Decks exclude ramp well. End landings join each main deck. No alternating stacked slopes.')
    im.save(a.output/'ramp_section.png');enroll('ramp_section','ramp_section.png',operation='original metric design drawing')
    provenance=dict(origin='original_generated_design',provider='OpenAI image generation tool',
        source_sheet=str(a.sheet.resolve()),source_sheet_sha256=hashlib.sha256(a.sheet.read_bytes()).hexdigest(),
        sheet_generation='2026-10-17, CityPrompt conversation: Classic Concrete Parkade original reference triptych',
        records=records,limitations=['Concept visualization; no engineering or accessibility certification.',
        'Rear section supersedes the original rear-strip internal topology, arrows and transverse divisions; no full-width barriers remain across the ramp lane. External envelope remains reference-locked.'])
    (a.output/'generation-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
