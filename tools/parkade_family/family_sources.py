"""Original metric drawings for the two remaining parking designs, not model captures."""
import argparse,hashlib,importlib,json,math,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from layout import frame_plan


def create(key,output):
    family=importlib.import_module('family_'+key);s=family.SPEC
    f=frame_plan(s['width'],s['depth'],s['levels']);w=s['width'];depth=s['depth'];top=f['top'];height=f['towerHeight']
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',30)
    ink='#253a40';colour='#a76442' if key=='brick' else '#9daeb6';records=[]
    def page(role,subtitle):
        im=Image.new('RGB',(1600,1100),'#fffdf5');d=ImageDraw.Draw(im)
        d.text((45,24),s['label'].upper()+' / ORIGINAL METRIC DESIGN',font=title,fill=ink)
        d.text((45,76),subtitle,font=font,fill=ink)
        d.text((45,1025),f'{w} x {depth} x {height:.2f} m; {s["levels"]} parking levels. Fixed native concept. No engineering certification.',font=font,fill=ink)
        return im,d
    im,d=page('front','FRONT / actual 6 m structural bays, open screens and two continuous glazed stair cores')
    scale=20;ox=800;oy=800
    def rect(a,b,c,e,fill):d.rectangle((ox+a*scale,oy-e*scale,ox+b*scale,oy-c*scale),fill=fill,outline=ink,width=2)
    rect(-w/2,w/2,0,.15,'#b8b8a9')
    for z in f['datums'][1:]:
        rect(-w/2+4.8,w/2-4.8,z-.57,z-.07,colour)
        for h in (.32,.68,1.1):d.line((ox+(-w/2+5)*scale,oy-(z+h)*scale,ox+(w/2-5)*scale,oy-(z+h)*scale),fill=ink,width=2)
    for x in f['frontColumns']:rect(x-.425,x+.425,.15,top+1.1,colour)
    for cx in (-w/2+2.5,w/2-2.5):
        rect(cx-2.3,cx+2.3,.15,height-.18,'#afcdd1');rect(cx-2.4,cx+2.4,height-.18,height,ink)
        for z in f['datums']:d.line((ox+(cx-2.3)*scale,oy-z*scale,ox+(cx+2.3)*scale,oy-z*scale),fill=ink,width=2)
        for dx in (-2.3,-.8,.8,2.3):d.line((ox+(cx+dx)*scale,oy-.15*scale,ox+(cx+dx)*scale,oy-(height-.18)*scale),fill=ink,width=2)
    for z in f['datums'][1:]:
        if key=='brick':
            for a,b in zip(f['frontColumns'],f['frontColumns'][1:]):
                for i in range(12):
                    x=a+.55+i*(b-a-1.1)/11;d.line((ox+x*scale,oy-(z+.43)*scale,ox+x*scale,oy-(z+2.08)*scale),fill=ink,width=1)
        else:
            for x in range(-27,28,2):d.line((ox+x*scale,oy-(z+.15)*scale,ox+(x+.6)*scale,oy-(z+2.55)*scale),fill=colour,width=3)
    entry=f['entryX'];rect(entry-2.725,entry+2.725,2.625,3.275,ink)
    d.text((100,910),'Portal between full structural bays; continuous ramps and actual stair openings.',font=font,fill=ink)
    if key=='brick':
        rect(22.15,26.85,2.71,2.89,ink)
        d.text((100,950),'Warm brick-faced piers; screens recessed 0.48 m; pedestrian canopy at right core.',font=font,fill=ink)
    else:
        rect(-27,27,top+2.3,top+2.57,'#244452')
        d.text((100,950),'Roof: 18 x 8 photovoltaic modules, seated canopy frame; no energy-production claim.',font=font,fill=ink)
    im.save(output/'front.png')
    im,d=page('top','TOP / native footprint; rear 6.5 m ramp well, 7 m end landings, fixed 2.7 x 5.5 m stalls')
    scale=18;ox=800;oy=570
    def plan(a,b,c,e,fill):d.rectangle((ox+a*scale,oy-e*scale,ox+b*scale,oy-c*scale),fill=fill,outline=ink,width=2)
    plan(-w/2,w/2,-depth/2,depth/2,'#d2d4c5')
    ax,bx=f['rampX'];plan(ax,bx,depth/2-6.5,depth/2,'#afcdd1')
    for cx in (-w/2+2.5,w/2-2.5):plan(cx-2.3,cx+2.3,-depth/2+.15,-depth/2+6.55,'#99bbc2')
    for ya in (-depth/2+1,-5.5,0):
        count=math.floor((w-14)/2.7);left=-count*2.7/2
        for i in range(count+1):x=left+i*2.7;d.line((ox+x*scale,oy-ya*scale,ox+x*scale,oy-(ya+5.5)*scale),fill='white',width=2)
    if key=='solar':
        plan(-27,27,-12,12,'#294b58')
        for x in range(-27,28,3):d.line((ox+x*scale,oy+12*scale,ox+x*scale,oy-12*scale),fill='#78929e',width=1)
        d.text((100,950),'Roof canopy shown; charging pedestals at ground x=7,12.4,17.8; rows stay native.',font=font,fill=ink)
    else:d.text((100,950),'Two front cores and rear ramp kept clear; 6 m circulation aisles; roof light masts.',font=font,fill=ink)
    im.save(output/'top.png')
    im,d=page('oblique','SCHEMATIC AXONOMETRIC / dimensional authority is front + top + ramp section')
    def pt(x,y,z):return (800+(x*.8+y*.6)*17,740+(x*.23-y*.3-z)*17)
    for z in f['datums']:
        for face in [[(-w/2,-depth/2,z),(w/2,-depth/2,z),(w/2,depth/2-6.5,z),(-w/2,depth/2-6.5,z)]]:d.polygon([pt(*v) for v in face],fill='#bfc3b4',outline=ink,width=2)
        for x in f['frontColumns']:d.line([pt(x,-depth/2+.25,.15),pt(x,-depth/2+.25,top+1.1)],fill=colour,width=5)
        if z>.2:
            for h in (.32,.68,1.1):d.line([pt(-w/2+5,-depth/2+.2,z+h),pt(w/2-5,-depth/2+.2,z+h)],fill=ink,width=2)
    for cx in (-w/2+2.5,w/2-2.5):
        d.polygon([pt(cx-2.3,-depth/2+.15,.15),pt(cx+2.3,-depth/2+.15,.15),pt(cx+2.3,-depth/2+.15,height),pt(cx-2.3,-depth/2+.15,height)],fill='#afcdd1',outline=ink,width=2)
    if key=='solar':d.polygon([pt(-27,-12,top+2.53),pt(27,-12,top+2.53),pt(27,12,top+2.53),pt(-27,12,top+2.53)],fill='#294b58',outline=ink,width=3)
    d.text((100,950),s['description'],font=font,fill=ink)
    im.save(output/'oblique.png')
    im,d=page('ramp_section','REAR CIRCULATION SECTION / same-direction stacked ramps; no barriers across vehicle lane')
    ox=160;oy=850;sx=1280/(bx-ax);sz=30
    for za,zb in zip(f['datums'],f['datums'][1:]):
        d.polygon([(ox,oy-za*sz),(ox+1280,oy-zb*sz),(ox+1280,oy-(zb-.15)*sz),(ox,oy-(za-.15)*sz)],fill='#929d90',outline=ink)
    for x in (ax,ax/2,0,bx/2,bx):
        z=f['datums'][-2]+3.3*(x-ax)/(bx-ax)-.15
        d.line((ox+(x-ax)*sx,oy,ox+(x-ax)*sx,oy-z*sz),fill=ink,width=4)
    d.text((100,180),f'Run {bx-ax:.1f} m; rise 3.3 m; 6.0 m clear lane inside 6.4 m ramp.',font=font,fill=ink)
    d.text((100,220),'Ramp slab 0.15 m, 3.15 m clear vertical headroom; edge girders outside vehicle lane.',font=font,fill=ink)
    d.text((100,270),'Stairs: 2 x 10 risers / storey; 1.35 m wide; full landings and side doorway bridges.',font=font,fill=ink)
    d.text((100,950),'Concept only; no structural, fire-egress, accessibility or swept-path certification.',font=font,fill=ink)
    im.save(output/'ramp_section.png')
    for role in ('front','top','oblique','ramp_section'):
        raw=(output/(role+'.png')).read_bytes();records.append(dict(role=role,file=role+'.png',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    (output/'generation-provenance.json').write_text(json.dumps(dict(origin='original_authored_design',source_type='Independent metric design drawings, not mesh renders',author='CityPrompt parkade initiative',date='2026-10-17',records=records,limitations=['Original concept, not engineered or certified.','Oblique is schematic; metric front/top/section govern.']),indent=2)+'\n')
    (output/'design-contract.json').write_text(json.dumps(dict(spec=s,frame=f),indent=2)+'\n')
    shutil.copy2(__file__,output/'family_sources.py')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('key',choices=['brick','solar']);p.add_argument('output');a=p.parse_args();create(a.key,a.output)
