"""Green Terraces: original metric CAD authority, authored before any mesh.

The four PNGs are design drawings rather than candidate-derived proof. Every
package is new and immutable. Vegetation symbols establish planted massing;
fine leaf placement is intentionally schematic architectural-clay detail.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil


DESIGN = dict(width=60, depth=40, frame_depth=36, levels=4,
    datums=[.15, 3.45, 6.75, 10.05], height=12.8,
    garden=(-10.8, 10.8, -5.5, 5.5), garden_max_height=12.55,
    garden_level=3, terrace_spans=[(-16, -6.4), (-5.6, 5.6), (6.4, 16)],
    projections=[2., 1.4, .8], screen_centres=[-12., 0., 12.],
    ground_rear_planters=[(-29, -24, 18, 20), (24, 29, 18, 20)])


def terrace_segments():
    return [dict(level=level, x0=a, x1=b, y0=-18-projection, y1=-18.,
        projection=projection, z=DESIGN['datums'][level])
        for level, projection in enumerate(DESIGN['projections'], 1)
        for a, b in DESIGN['terrace_spans']]


def garden_beds():
    # Three-metre central north/south path and 2.4 m crosswalk stay open.
    return [(-10.5, -6., -5.2, 5.2), (6., 10.5, -5.2, 5.2),
        *[(a, b, c, d) for a, b in [(-4.5, -1.5), (1.5, 4.5)]
            for c, d in [(-4.9, -2.4), (2.4, 4.9)]]]


def write_sources(output: Path):
    from PIL import Image, ImageDraw, ImageFont
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    title = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 30)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 23)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 19)
    colours = dict(line='#34473c', concrete='#b9bdad', steel='#3b5146',
        glass='#b2ccd0', planter='#748567', soil='#70654b', foliage='#4e7650', deck='#d7d9ca')
    def page(subtitle):
        im = Image.new('RGB', (1600, 1100), '#fffdf5'); d = ImageDraw.Draw(im)
        d.text((40, 25), 'GREEN TERRACES PARKADE / ORIGINAL METRIC DESIGN v001', font=title, fill=colours['line'])
        d.text((40, 80), subtitle, font=font, fill=colours['line'])
        d.text((40, 1025), 'Fixed 60 x 40 m occupied envelope / 4 parking levels / 12.8 m / original concept; no engineering claim', font=small, fill=colours['line'])
        return im, d

    im, d = page('FRONT / 60 m structural frontage; planted ledges step inward 2.0, 1.4, 0.8 m at upper levels')
    scale, ox, oy = 23, 800, 780
    def elevation_rect(x0, z0, x1, z1, colour):
        d.rectangle((ox+x0*scale, oy-z1*scale, ox+x1*scale, oy-z0*scale), fill=colour, outline=colours['line'], width=2)
    elevation_rect(-30, 0, 30, .15, colours['concrete'])
    for x in range(-24, 25, 6): elevation_rect(x-.25, .15, x+.25, 11.15, colours['concrete'])
    for z in DESIGN['datums'][1:]:
        elevation_rect(-25.2, z-.57, 25.2, z-.07, colours['concrete'])
        for h in (.32, .68, 1.1):
            d.line((ox-25*scale, oy-(z+h)*scale, ox+25*scale, oy-(z+h)*scale), fill=colours['steel'], width=2)
    for cx in (-27.5, 27.5):
        elevation_rect(cx-2.3, .15, cx+2.3, 12.62, colours['glass'])
        for x in (cx-2.3, cx-.8, cx+.8, cx+2.3):
            d.line((ox+x*scale, oy-.15*scale, ox+x*scale, oy-12.62*scale), fill=colours['steel'], width=2)
        for z in DESIGN['datums']:
            d.line((ox+(cx-2.3)*scale, oy-z*scale, ox+(cx+2.3)*scale, oy-z*scale), fill=colours['steel'], width=2)
        elevation_rect(cx-2.4, 12.62, cx+2.4, 12.8, colours['steel'])
    for centre in DESIGN['screen_centres']:
        elevation_rect(centre-1.1, .15, centre+1.1, .7, colours['planter'])
        for x in [centre-1., centre-.5, centre, centre+.5, centre+1.]:
            d.line((ox+x*scale, oy-.7*scale, ox+x*scale, oy-10.9*scale), fill=colours['steel'], width=2)
        for i in range(11):
            z=.9+i*.87
            d.line((ox+(centre-.9)*scale, oy-z*scale, ox+(centre+.9)*scale, oy-(z+.3)*scale), fill=colours['foliage'], width=4)
    for p in terrace_segments():
        elevation_rect(p['x0'], p['z']-.12, p['x1'], p['z']+.52, colours['planter'])
        for i in range(int((p['x1']-p['x0'])/.8)):
            x=p['x0']+.4+i*.8
            d.ellipse((ox+(x-.32)*scale, oy-(p['z']+1.05)*scale, ox+(x+.32)*scale, oy-(p['z']+.45)*scale), fill=colours['foliage'])
    for x in (-5,5):elevation_rect(x-.06,10.05,x+.06,12.4,'#7b7159')
    elevation_rect(-5.1,12.4,5.1,12.55,'#7b7159')
    elevation_rect(-23.725, 2.625, -18.275, 3.275, colours['steel'])
    d.text((ox-22.7*scale, oy-3.15*scale), 'ENTRANCE', font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 16), fill='#fffdf5')
    d.text((160, 875), 'Continuous glazed stair cores and vehicle portal remain unobstructed by planting.', font=font, fill=colours['line'])
    d.text((160, 920), 'Climbing steel mesh: x=-12, 0, +12 m. Ledges seat on steel cantilever brackets at concrete frame.', font=small, fill=colours['line'])
    im.save(output/'front.png')

    im, d = page('TOP / rooftop garden is a separate reserved pedestrian area; two 6 m motor aisles remain open')
    scale, ox, oy = 20, 800, 570
    def plan(rect, colour, outline=None):
        a,b,c,e=rect;d.rectangle((ox+a*scale, oy-e*scale, ox+b*scale, oy-c*scale), fill=colour, outline=outline or colours['line'], width=2)
    plan((-30, 30, -18, 18), colours['deck'])
    plan((-23, 23, 11.5, 18), '#a9c8cd')
    for cx in (-27.5, 27.5): plan((cx-2.3, cx+2.3, -17.85, -11.45), colours['glass'])
    for p in terrace_segments():
        if p['level']==1: plan((p['x0'],p['x1'],p['y0'],p['y1']), '#9ba48c')
    for p in terrace_segments():
        if p['level']==3: plan((p['x0'],p['x1'],p['y0'],p['y1']), colours['foliage'])
    for rect in DESIGN['ground_rear_planters']:plan(rect, colours['foliage'])
    for ya,yb,lo in [(-17,-11.5,-16.2),(-5.5,0,-21.6),(0,5.5,-21.6)]:
        for i in range(round((21.6-lo)/2.7)+1):
            x=lo+i*2.7
            if ya>=-5.5 and -10.8<x<10.8:continue
            d.line((ox+x*scale,oy-ya*scale,ox+x*scale,oy-yb*scale),fill='#fffdf5',width=2)
    plan(DESIGN['garden'], '#e3d8bd')
    for bed in garden_beds():
        plan(bed, colours['planter'])
        a,b,c,e=bed
        for i in range(max(1,int((b-a)/1.2))):
            for j in range(max(1,int((e-c)/1.2))):
                x=a+.6+i*1.2;y=c+.6+j*1.2
                d.ellipse((ox+(x-.4)*scale,oy-(y+.4)*scale,ox+(x+.4)*scale,oy-(y-.4)*scale),fill=colours['foliage'])
    for x in (-5,5):
        for y in (-1.7,1.7):plan((x-.06,x+.06,y-.06,y+.06), '#6c634b')
    for y in (-8.5,8.5):
        d.line((ox-19*scale,oy-y*scale,ox+19*scale,oy-y*scale),fill='#b09b3c',width=4)
        d.text((ox-8*scale,oy-y*scale-25),'6 m DRIVE AISLE',font=small,fill=colours['line'])
    d.text((ox-10.4*scale,oy-15.4*scale),'46 m RAMP WELL / 6 m clear',font=small,fill=colours['line'])
    d.text((160, 985),'Garden: x +/-10.8, y +/-5.5 m at z10.05 only; north/south gates and crosswalks; no roof bays inside.',font=small,fill=colours['line'])
    im.save(output/'top.png')

    im,d=page('OBLIQUE / low wide open parkade; stepped front gardens, climbing mesh and separate roof garden')
    def point(x,y,z):return (800+(x*.8+y*.6)*18,760+(x*.25-y*.3-z)*18)
    def box(a,b,c,e,z0,z1,colour):
        for face in [[(a,c,z0),(b,c,z0),(b,c,z1),(a,c,z1)],[(b,c,z0),(b,e,z0),(b,e,z1),(b,c,z1)],[(a,c,z1),(b,c,z1),(b,e,z1),(a,e,z1)]]:
            d.polygon([point(*v) for v in face], fill=colour, outline=colours['line'], width=2)
    for z in DESIGN['datums']:
        box(-30,30,-18,11.5,max(0,z-.25),z,colours['concrete'])
        for a,b in [(-30,-23),(23,30)]:box(a,b,11.5,18,max(0,z-.25),z,colours['concrete'])
    for x in range(-24,25,6):
        for y in (-17.75,-5.75,5.75):box(x-.25,x+.25,y-.25,y+.25,.15,11.15,colours['concrete'])
    for centre in DESIGN['screen_centres']:
        for x in (centre-1,centre-.5,centre,centre+.5,centre+1):
            d.line([point(x,-18.15,.6),point(x,-18.15,10.9)],fill=colours['steel'],width=2)
        for i in range(11):
            z=.9+i*.87
            d.line([point(centre-.8,-18.18,z),point(centre+.8,-18.18,z+.3)],fill=colours['foliage'],width=4)
    for p in terrace_segments():
        box(p['x0'],p['x1'],p['y0'],p['y1'],p['z']-.12,p['z']+.52,colours['planter'])
        box(p['x0']+.15,p['x1']-.15,p['y0']+.1,p['y1']-.1,p['z']+.52,p['z']+.95,colours['foliage'])
    for cx in (-27.5,27.5):
        box(cx-2.3,cx+2.3,-17.85,-11.45,.15,12.62,colours['glass'])
        box(cx-2.4,cx+2.4,-17.95,-11.35,12.62,12.8,colours['steel'])
    for bed in garden_beds():box(*bed,10.05,10.65,colours['foliage'])
    for x in (-5,5):
        for y in (-1.7,1.7):box(x-.06,x+.06,y-.06,y+.06,10.05,12.4,'#7b7159')
    for i in range(11):
        x=-5+i
        box(x-.04,x+.04,-1.8,1.8,12.4,12.55,'#7b7159')
    d.text((100,945),'Schematic foliage and axonometric overlap; front/top govern coordinates; section governs ramps/terraces.',font=small,fill=colours['line'])
    im.save(output/'oblique.png')

    im,d=page('SECTIONS / rear ramp circulation and metric planted-edge assembly; concept detail')
    sx,sz,ox,oy=20,27,800,545
    for level,z in enumerate(DESIGN['datums']):
        for a,b in [(-30,-23),(23,30)]:d.rectangle((ox+a*sx,oy-z*sz,ox+b*sx,oy-z*sz+7),fill=colours['concrete'])
        d.text((70,oy-z*sz-10),f'L{level+1}',font=small,fill=colours['line'])
    for i,z in enumerate(DESIGN['datums'][:-1]):
        d.line((ox-23*sx,oy-z*sz,ox+23*sx,oy-(z+3.3)*sz),fill='#457782',width=8)
    d.text((185,580),'Three same-direction ramps / 46 m run / 3.3 m rise / 6 m clear / >=2.4 m sparse-ray headroom target',font=small,fill=colours['line'])
    d.text((70,650),'FRONT LEDGE SECTION / y=-18 is parking frame face',font=font,fill=colours['line'])
    for i,p in enumerate((2.,1.4,.8)):
        xx=185+i*460;yy=820
        d.rectangle((xx,yy,xx+300,yy+12),fill=colours['concrete'])
        d.rectangle((xx,yy-60,xx+p*100,yy+8),fill=colours['planter'])
        d.rectangle((xx+12,yy-44,xx+p*100-12,yy-7),fill=colours['soil'])
        d.line((xx,yy+75,xx+p*100,yy+12),fill=colours['steel'],width=6)
        d.line((xx+p*100,yy+12,xx+p*100+70,yy+12),fill=colours['steel'],width=6)
        d.text((xx,yy+100),f'L{i+2}: {p:.1f} m projection',font=small,fill=colours['line'])
    d.text((70,985),'Planter walls/base + soil + rooted shrubs; real seated brackets; rooftop garden paths remain level with deck.',font=small,fill=colours['line'])
    im.save(output/'ramp_section.png')

    records=[]
    for role in ('front','top','oblique','ramp_section'):
        raw=(output/(role+'.png')).read_bytes()
        records.append(dict(role=role,file=role+'.png',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    contract=dict(archetype_id='parkade-green-terraces',variant_id='green-terraces-v1',design=DESIGN,
        roof_garden_beds=garden_beds(),terraces=terrace_segments(),
        authority='Metric front/top/section govern geometry. Oblique and planting symbols govern architectural hierarchy, not individual leaf positions.',
        route_clearances=dict(motor_aisles_m=6,garden_north_south_m=3,garden_crosswalk_m=2.4),
        limits=['Fixed native assembly only; no engineering, fire, accessibility or swept-path certification.',
            'Architectural clay foliage is physical stylized leaf geometry; no photoreal texture claim.'])
    (output/'design-contract.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    provenance=dict(origin='original_authored_design',author='CityPrompt Green Terraces builder',
        date='2026-10-17',source_type='Original metric CAD-style primitives authored before the Green candidate mesh',
        archetype_id=contract['archetype_id'],variant_id=contract['variant_id'],records=records,
        authority=contract['authority'],limitations=contract['limits'])
    (output/'generation-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    shutil.copy2(__file__,output/'green_sources.py')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
    write_sources(parser.parse_args().output)
