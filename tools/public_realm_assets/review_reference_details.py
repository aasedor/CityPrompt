"""Package reviewed native amenities and a reference / before / after board."""
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from court_specs import COURTS

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    p.add_argument('--previous',type=Path,required=True);a=p.parse_args()
    kit=a.root/'amenity-kit';kit.mkdir(exist_ok=True);records={}
    for kind in COURTS:
        folder=a.root/'final'/kind;r=json.loads((folder/'recipe.json').read_text())
        v=json.loads((folder/'geometry-verification.json').read_text())
        assert v['status']=='PASS_OFFLINE_GEOMETRY'
        assert any('reimported amenity module envelopes' in check for check in v['checks'])
        for placement in r['reference_assets']:
            name=placement['kind']
            if name in records:continue
            module=r['modules'][name];source=folder/'modules'/module['path'];target=kit/f'{name}.glb'
            assert hashlib.sha256(source.read_bytes()).hexdigest()==module['sha256']
            if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==module['sha256'],'Use a fresh kit folder'
            else:shutil.copy2(source,target)
            records[name]=dict(path=target.name,sha256=module['sha256'],bytes=module['bytes'],
                native_bounds_m=placement['native_bounds_m'],source_package=r['id'],runtime_approved=False)
    assert len(records)==10
    (kit/'index.json').write_text(json.dumps(dict(units='metres',axes='GLB Y-up; source bounds Z-up',modules=records),indent=2)+'\n')
    # Simple layout of unretouched native renders and original catalogue images.
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
    title=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',34)
    width,height=560,440;canvas=Image.new('RGB',(width*3,height*3+122),'#efeee8');draw=ImageDraw.Draw(canvas)
    draw.text((16,15),'City Prompt | Details from the archetype images',font=title,fill='#293e36')
    for i,label in enumerate(('Catalogue reference','Original native model','Revised native model')):
        draw.text((i*width+16,73),label,font=font,fill='#52655b')
    rows=[('tennis','tennis-court-cluster/variant_0.png','Tennis: covered benches + spectator stand'),
          ('beach_volleyball','beach-volleyball-courts/variant_1.png','Beach volleyball: parasols + seat walls'),
          ('bocce','bocce-pétanque-court/hero.png','Bocce: planted arbour + cafe seating')]
    for j,(kind,reference,label) in enumerate(rows):
        folder=a.root/'final'/kind
        view='court' if kind=='tennis' else 'detail'
        paths=[folder/'references'/reference,a.previous/kind/'renders'/f'{view}.png',folder/'renders'/f'{view}.png']
        for i,path in enumerate(paths):
            im=Image.open(path).convert('RGB');im.thumbnail((width-16,height-38))
            canvas.paste(im,(i*width+(width-im.width)//2,122+j*height))
        draw.text((16,122+j*height+height-34),label,font=font,fill='#293e36')
    canvas.save(a.root/'reference-before-after.png')
    print(f'Packaged {len(records)} native amenity GLBs and reference-before-after.png')

if __name__=='__main__':main()
