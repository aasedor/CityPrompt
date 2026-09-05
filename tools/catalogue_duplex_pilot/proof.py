"""Letterboxed evidence layouts and deterministic checks; no image retouching."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import struct
from PIL import Image, ImageDraw, ImageFont, ImageOps


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2); f.write('\n')


def label(canvas, x, y, text, size=24):
    ImageDraw.Draw(canvas).text((x,y), text, fill='#263238', font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size))


def panel(canvas, path, x, y, w, h):
    with Image.open(path) as source:
        picture=ImageOps.contain(source.convert('RGB'),(w,h),Image.Resampling.LANCZOS)
    canvas.paste(picture,(x+(w-picture.width)//2,y+(h-picture.height)//2))


def boards(root, manifest):
    dest=root/'boards'
    source={s['role']:root/s['path'] for s in manifest['source_contract']['sources']}
    board=Image.new('RGB',(1800,570),'#f3f0e8')
    label(board,22,15,'LOCKED CATALOGUE SOURCES / infill_duplex',28)
    for i,role in enumerate(('front','oblique','top')):
        label(board,20+i*600,60,role.upper(),22)
        panel(board,source[role],10+i*600,92,580,445)
    board.save(dest/'locked-source-board.png')
    phone=Image.new('RGB',(1080,1920),'#f3f0e8')
    label(phone,28,25,'CALGARY DUPLEX / SOURCE AND CLAY',32)
    label(phone,28,73,manifest['candidate'],21)
    for i,(s,v) in enumerate([('front','front_corner'),('oblique','aerial'),('top','top')]):
        y=145+i*550
        label(phone,28,y,'SOURCE / '+s,23); label(phone,554,y,'DELIVERED GLB / '+v,23)
        panel(phone,source[s],28,y+50,498,415)
        panel(phone,root/'renders'/f'{v}.png',554,y+50,498,415)
    label(phone,28,1815,'Native clay only. Rear and room layouts are inferred.',23)
    label(phone,28,1860,'No runtime, survey or textured-keeper approval.',23)
    phone.save(dest/'phone-source-comparison.png')
    phone=Image.new('RGB',(1080,1920),'#f3f0e8')
    label(phone,28,25,'CONSTRUCTION / ACTUAL GLB REIMPORT',30)
    for i,role in enumerate(('architecture_close','glass_close','facade_close','roof_contact','side_projection','rear_side')):
        x=28+i%2*526;y=125+i//2*540
        label(phone,x,y,role.replace('_',' '),24)
        panel(phone,root/'renders'/f'{role}.png',x,y+48,500,420)
    label(phone,28,1820,'Full-resolution evidence is retained in renders/.',23)
    label(phone,28,1860,'Geometry counts never substitute for visual review.',23)
    phone.save(dest/'phone-construction.png')
    views=manifest['mandatory_review_views']
    sheet=Image.new('RGB',(1920,math.ceil(len(views)/4)*405+70),'#f3f0e8')
    label(sheet,24,15,manifest['candidate']+' / view inventory',26)
    for i,v in enumerate(views):
        x=i%4*480;y=75+i//4*405
        label(sheet,x+12,y,v,22);panel(sheet,root/'renders'/f'{v}.png',x+8,y+34,464,360)
    sheet.save(dest/'all-views-contact.png')
    save_json(dest/'layout-provenance.json',dict(operation='Letterboxing and labels only. No generation, cropping, retouching or relighting.',
        inputs=[dict(path=str(p.relative_to(root)),sha256=sha(p)) for p in list(source.values())+sorted((root/'renders').glob('*.png'))]))


def verify(root, manifest):
    import trimesh
    report=read(root/'build-report.json');checks={}
    for item in manifest['source_contract']['sources']:
        path=root/item['path'];checks['source '+item['role']]=path.stat().st_size==item['bytes'] and sha(path)==item['sha256']
    for item in manifest['provenance']['scripts']:
        checks['script '+item['path']]=sha(root/item['path'])==item['sha256']
    path=root/report['runtime']['path'];raw=path.read_bytes();n,typ=struct.unpack_from('<II',raw,12);payload=json.loads(raw[20:20+n])
    checks['glb header']=struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw)) and typ==0x4E4F534A
    checks['model hash']=sha(path)==report['runtime']['sha256']
    checks['texture-free']=not payload.get('images') and not payload.get('textures')
    checks['self-contained']=all('uri' not in b for b in payload.get('buffers',[]))
    checks['no QA camera or light']=not payload.get('cameras') and not payload.get('extensions',{}).get('KHR_lights_punctual')
    checks['native grade zero']=abs(report['delivered_bounds_m'][0][2])<1e-5
    checks['bounds roundtrip']=report['max_roundtrip_delta_m']<1e-4
    checks['carrier apertures']=report['carrier_aperture_audit']=='PASS_CARRIER_APERTURES'
    scene=trimesh.load(path,force='scene',process=False)
    checks['finite geometry']=all(math.isfinite(float(x)) for mesh in scene.geometry.values() for row in mesh.vertices for x in row)
    checks['nonzero triangles']=all(bool((mesh.area_faces>1e-12).all()) for mesh in scene.geometry.values())
    for view in manifest['mandatory_review_views']:
        with Image.open(root/'renders'/f'{view}.png') as im:
            checks['render '+view]=list(im.size)==report['render_resolution'];im.verify()
    for spec in manifest['camera_roster']:
        if spec.get('whole',True):
            q=report['camera_safety_margin'][spec['name']]
            checks['camera margin '+spec['name']]=min(q['xmin'],q['ymin'],1-q['xmax'],1-q['ymax'])>=.074
    for name in ('phone-source-comparison.png','phone-construction.png'):
        with Image.open(root/'boards'/name) as im:checks[name]=im.size==(1080,1920);im.verify()
    result=dict(status='PASS_DELIVERY_CHECKS' if all(checks.values()) else 'FAIL_DELIVERY_CHECKS',checks=checks,
        model_sha256=sha(path),runtime_approved=False,independent_visual_review='pending')
    save_json(root/'evidence/delivery-verification.json',result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('candidate',type=Path);a=parser.parse_args()
    root=a.candidate.resolve();manifest=read(root/'prework-manifest.json')
    for name in ('locked-source-board.png','phone-source-comparison.png','phone-construction.png','all-views-contact.png','layout-provenance.json'):
        if (root/'boards'/name).exists():raise FileExistsError(root/'boards'/name)
    if (root/'evidence/delivery-verification.json').exists():raise FileExistsError('Immutable verification already exists')
    boards(root,manifest)
    shutil.copy2(__file__,root/'scripts'/Path(__file__).name)
    result=verify(root,manifest)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['status'].startswith('PASS') else 1)


if __name__=='__main__':main()
