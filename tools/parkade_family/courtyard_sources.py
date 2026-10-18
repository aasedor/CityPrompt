"""Original metric Mobility Courtyard authority; never imports a candidate mesh.

Author drawings before geometry and retain each version in a new external folder.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont

INK = '#243c46'
CONCRETE = '#bebfb2'
STEEL = '#354e58'
GLASS = '#b6d1d3'
SCREENS = ('#247e82', '#ca744f', '#d1a345')
DATUMS = (.15, 3.45, 6.75, 10.05)


def create_sources(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 23)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 19)
    title = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 31)

    def page(subtitle):
        im = Image.new('RGB', (1800, 1280), '#fffdf5')
        d = ImageDraw.Draw(im)
        d.text((48, 25), 'MOBILITY COURTYARD / ORIGINAL METRIC DESIGN v001', font=title, fill=INK)
        d.text((48, 78), subtitle, font=font, fill=INK)
        d.text((48, 1220), '64 x 48 m / 4 parking levels / caps 12.80 m / native fixed size / original concept, no engineering claim', font=font, fill=INK)
        return im, d

    im, d = page('FRONT ELEVATION / street at y=-24; floor tops 0.15, 3.45, 6.75, 10.05 m')
    s, ox, oy = 25, 900, 810
    def rect(x0,z0,x1,z1,fill):
        d.rectangle((ox+x0*s,oy-z1*s,ox+x1*s,oy-z0*s), fill=fill, outline=INK, width=2)
    rect(-32, 0, 32, .15, CONCRETE)
    for z in DATUMS[1:]: rect(-27.1,z-.5,27.1,z,CONCRETE)
    for x in range(-24,25,6):rect(x-.25,.15,x+.25,11.15,CONCRETE)
    for cx in (-29.5,29.5):
        rect(cx-2.3,.15,cx+2.3,12.62,GLASS)
        for z in DATUMS:
            d.line((ox+(cx-2.3)*s,oy-z*s,ox+(cx+2.3)*s,oy-z*s),fill=STEEL,width=3)
            if z<10:d.line([ (ox+(cx-1.7)*s,oy-z*s),(ox+(cx+1.7)*s,oy-(z+1.65)*s),(ox+(cx-1.7)*s,oy-(z+3.3)*s)],fill=STEEL,width=2)
        for x in (cx-2.3,cx-.8,cx+.8,cx+2.3):d.line((ox+x*s,oy-.15*s,ox+x*s,oy-12.62*s),fill=STEEL,width=2)
        rect(cx-2.4,12.62,cx+2.4,12.8,STEEL)
    for z in DATUMS[1:]:
        h = 1.6 if z>10 else 2.45
        for index,(a,b) in enumerate(((-19,-13),(-11,-5),(-3,3),(5,11),(13,19),(21,26))):
            for i in range(int((b-a)/.7)+1):
                x=a+i*.7;rect(x-.075,z+.18,x+.075,z+h,SCREENS[index%3])
    rect(-11.75,.15,-6.25,2.8,GLASS)
    rect(-5.75,.15,-.25,2.8,GLASS)
    rect(-2.2,.15,-.6,2.6,'#fffdf5')
    rect(-12,2.8,0,3.03,STEEL)
    d.text((ox-10.7*s,oy-2.8*s),'COURTYARD CAFE',font=small,fill='#fffdf5')
    rect(3,2.85,18,3.12,STEEL)
    for x in (3.15,17.85):rect(x-.08,.15,x+.08,2.85,STEEL)
    for x in (5,7,9,11,13,15,17):
        d.arc((ox+(x-.45)*s,oy-1.05*s,ox+(x+.45)*s,oy-.15*s),180,360,fill=STEEL,width=3)
        d.line((ox+(x-.45)*s,oy-.6*s,ox+(x-.45)*s,oy-.15*s),fill=STEEL,width=3)
        d.line((ox+(x+.45)*s,oy-.6*s,ox+(x+.45)*s,oy-.15*s),fill=STEEL,width=3)
    rect(-23.65,2.625,-18.35,3.275,STEEL)
    d.text((ox-23.0*s,oy-3.12*s),'ENTRANCE',font=small,fill='#fffdf5')
    d.line((100,860,1700,860),fill=INK,width=2);d.text((840,875),'64.00 m',font=font,fill=INK)
    d.text((100,940),'Permeable vertical fins: teal / terracotta / ochre. All three upper decks; lower roof band 1.60 m.',font=font,fill=INK)
    d.text((100,985),'Cafe 12 x 6.5 m with open 1.6 m street door. Open bicycle hub 15 x 6.5 m at right.',font=font,fill=INK)
    d.text((100,1030),'Glazed cores include visible paired return stair flights and full-level landings.',font=font,fill=INK)
    im.save(output/'front.png')

    im,d=page('TOP PLAN / courtyard is cut through every deck; ground plaza is open upward')
    s,ox,oy=18,900,660
    def plan(rectangle,fill):
        a,b,c,e=rectangle;d.rectangle((ox+a*s,oy-e*s,ox+b*s,oy-c*s),fill=fill,outline=INK,width=2)
    plan((-32,32,-24,24),CONCRETE)
    plan((-25,25,17.55,23.95),GLASS)
    plan((-8,8,-7,7),'#fffdf5')
    for cx in (-29.5,29.5):plan((cx-2.3,cx+2.3,-23.85,-17.45),GLASS)
    plan((-12,0,-24,-17.5),'#d9b895');plan((3,18,-24,-17.5),'#a7c8c7')
    # Four real soil wells are separated by a clear three metre walking cross.
    for a,b in ((-6.9,-2.0),(2.0,6.9)):
        for c,e in ((-5.9,-2.0),(2.0,5.9)):
            plan((a,b,c,e),'#789865')
            d.ellipse((ox+(a+.8)*s,oy-(e-.3)*s,ox+(b-.8)*s,oy-(c+.3)*s),outline='#355947',width=3)
    for x in (5,7,9,11,13,15,17):plan((x-.45,x+.45,-22.55,-22.45),STEEL)
    d.text((540,170),'REAR: 6 m CLEAR PARALLEL VEHICLE RAMPS',font=font,fill=INK)
    d.text((740,630),'16 x 14 m',font=font,fill=INK)
    d.text((735,660),'OPEN COURT',font=font,fill=INK)
    d.text((625,1095),'CAFE',font=small,fill=INK);d.text((985,1095),'BICYCLE HUB',font=small,fill=INK)
    d.text((100,1140),'Ring routes: 10.5 m front, 10.55 m rear to ramp edge, 24 m each side. No occupied court bridge.',font=font,fill=INK)
    d.text((100,1178),'Ground cross: 4 m clear, soil wells at corner quadrants; no continuous paving below roots.',font=small,fill=INK)
    im.save(output/'top.png')

    im,d=page('DESIGN AXONOMETRIC / independently drawn ring decks and central void; not a candidate render')
    def pt(x,y,z):return (900+(x*.8+y*.6)*16,830+(x*.22-y*.28-z)*16)
    def box(a,b,c,e,z0,z1,colour):
        for face in [[(a,c,z0),(b,c,z0),(b,c,z1),(a,c,z1)],[(b,c,z0),(b,e,z0),(b,e,z1),(b,c,z1)],[(a,c,z1),(b,c,z1),(b,e,z1),(a,e,z1)]]:
            d.polygon([pt(*v) for v in face],fill=colour,outline=INK,width=2)
    for z in DATUMS:
        # Four ring strips; rear ramp wells remain actual open voids.
        for a,b,c,e in [(-32,32,-24,-7),(-32,-8,-7,7),(8,32,-7,7),(-32,32,7,17.5),(-32,-25,17.5,24),(25,32,17.5,24)]:
            box(a,b,c,e,max(0,z-.25),z,CONCRETE)
    for a,b,c,e in [(-6.9,-2,-5.9,-2),(2,6.9,-5.9,-2),(-6.9,-2,2,5.9),(2,6.9,2,5.9)]:box(a,b,c,e,.06,.15,'#789865')
    for cx in (-29.5,29.5):box(cx-2.3,cx+2.3,-23.85,-17.45,.15,12.62,GLASS);box(cx-2.4,cx+2.4,-23.95,-17.35,12.62,12.8,STEEL)
    for z in DATUMS[1:]:
        h=1.6 if z>10 else 2.45
        for index,(a,b) in enumerate(((-19,-13),(-11,-5),(-3,3),(5,11),(13,19),(21,26))):
            for i in range(int((b-a)/.7)+1):
                x=a+i*.7;box(x-.075,x+.075,-23.92,-23.56,z+.18,z+h,SCREENS[index%3])
        for side in (-1,1):
            for i in range(37):
                y=-10+i*.7;box(side*31.8-.18,side*31.8+.18,y-.075,y+.075,z+.18,z+h,SCREENS[(i//9)%3])
        for yy in (-7,7):d.line([pt(-8,yy,z+1.1),pt(8,yy,z+1.1)],fill=STEEL,width=2)
        for xx in (-8,8):d.line([pt(xx,-7,z+1.1),pt(xx,7,z+1.1)],fill=STEEL,width=2)
    box(-12,0,-24,-17.5,.15,2.8,GLASS)
    d.text((110,1090),'Court stays unroofed; 4 small trees rooted in exposed soil wells at ground level.',font=font,fill=INK)
    d.text((110,1130),'Front coloured screen rhythm continues on both sides; rear exposes ramp structure and railings.',font=font,fill=INK)
    im.save(output/'oblique.png')

    im,d=page('REAR CIRCULATION SECTION / 3 parallel 6 m clear ramps; longitudinal section at rear strip')
    s,ox,oy=26,900,800
    def p(x,z):return (ox+x*s,oy-z*s)
    for i,z in enumerate(DATUMS):
        for a,b in ((-32,-25),(25,32)):d.rectangle((*p(a,z),*p(b,z-.25)),fill=CONCRETE,outline=INK,width=2)
        d.text((75,oy-z*s-25),f'{z:.2f} m',font=font,fill=INK)
        if i<3:
            z1=DATUMS[i+1]
            d.polygon([p(-25,z),p(25,z1),p(25,z1-.15),p(-25,z-.15)],fill=CONCRETE,outline=INK,width=2)
            for hh in (.32,.68,1.1):d.line([p(-25,z+hh),p(25,z1+hh)],fill=STEEL,width=2)
    d.text((250,925),'50 m ramp run / 3.30 m rise / 3.15 m deck-to-deck clear above ramp body',font=font,fill=INK)
    d.text((250,970),'Ramps y=17.55..23.95; rails and edge girders outside the central 6 m lane.',font=font,fill=INK)
    d.text((250,1015),'End landings are x=-32..-25 and +25..+32; no transverse walls or piers in lane.',font=font,fill=INK)
    d.text((250,1060),'Stair cores front: paired 1.35 m flights / 10 risers per half-storey / 1.55 m mid-landings.',font=font,fill=INK)
    im.save(output/'ramp_section.png')
    records=[]
    for role in ('front','oblique','top','ramp_section'):
        raw=(output/(role+'.png')).read_bytes()
        records.append(dict(role=role,file=role+'.png',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    provenance=dict(origin='original_authored_design',source_type='independent metric CAD-style drawings authored before candidate geometry',
        date='2026-10-17',archetype_id='parkade-mobility-courtyard',variant_id='mobility-courtyard-v1',records=records,
        dimensions_m=[64,48,12.8],floor_datums_m=DATUMS,courtyard_m=[-8,8,-7,7],
        authority='Original design drawings govern geometry; orthographic front/top and rear section govern metric coordinates over schematic axonometric.',
        limitations=['Original concept, no structural, accessibility, fire-egress, capacity or swept-path certification.',
                    'Architectural-clay source palette only; not a textured keeper.','Native fixed assembly; no mesh stretching.'])
    (output/'generation-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    board=Image.new('RGB',(1800,1280),'white')
    for index,role in enumerate(('front','oblique','top','ramp_section')):
        board.paste(Image.open(output/(role+'.png')).resize((900,640)),((index%2)*900,(index//2)*640))
    board.save(output/'source-board.png')
    shutil.copy2(__file__,output/'courtyard_sources.py')
    return provenance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
    create_sources(parser.parse_args().output)
