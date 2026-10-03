"""Contact sheets of unretouched native GLB renders and deduplicated street kit."""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('packages',type=Path,nargs='+');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True);records=[];modules={}
    kit=a.output/'street-amenity-kit';kit.mkdir(exist_ok=True)
    for folder in a.packages:
        r=json.loads((folder/'recipe.json').read_text());v=json.loads((folder/'geometry-verification.json').read_text())
        assert v['status']=='PASS_OFFLINE_GEOMETRY'
        records.append((folder,r))
        for placement in r['reference_assets']:
            kind=placement['kind']
            if kind in modules:continue
            module=r['modules'][kind];source=folder/'modules'/module['path'];target=kit/f'{kind}.glb'
            assert hashlib.sha256(source.read_bytes()).hexdigest()==module['sha256']
            if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==module['sha256'],'Use a fresh delivery folder'
            else:shutil.copy2(source,target)
            modules[kind]=dict(**module,native_bounds_m=placement['native_bounds_m'],source_package=r['id'])
    (kit/'index.json').write_text(json.dumps(dict(units='metres',axes='standard GLB Y-up; recorded bounds Z-up',runtime_approved=False,modules=modules),indent=2)+'\n')
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21);heading=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',30)
    reviews=a.output/'reviews';reviews.mkdir(exist_ok=True)
    for folder,r in records:
        canvas=Image.new('RGB',(1600,1280),'#f0eee7');draw=ImageDraw.Draw(canvas)
        draw.text((16,8),r['title'],font=heading,fill='#293e36')
        for i,mode in enumerate(('aerial','top','detail','street')):
            im=Image.open(folder/'renders'/f'{mode}.png').convert('RGB');im.thumbnail((800,580))
            x=(i%2)*800;y=(i//2)*610+45;canvas.paste(im,(x+(800-im.width)//2,y))
            draw.text((x+14,y+580),mode,font=font,fill='#293e36')
        canvas.save(reviews/f"{r['kind']}.jpg",quality=93)
    for mode in ('aerial','detail','top','street'):
        cw,ch=700,560;rows=(len(records)+1)//2
        canvas=Image.new('RGB',(cw*2,ch*rows+85),'#f0eee7');draw=ImageDraw.Draw(canvas)
        draw.text((20,16),f'City Prompt | Ten new streets | {mode}',font=heading,fill='#293e36')
        draw.text((20,53),'Native GLB previews. Browser integration and Currie testing pending.',font=font,fill='#536159')
        for i,(folder,r) in enumerate(records):
            x=(i%2)*cw;y=(i//2)*ch+85
            im=Image.open(folder/'renders'/f'{mode}.png').convert('RGB');im.thumbnail((cw-16,ch-45))
            canvas.paste(im,(x+(cw-im.width)//2,y))
            draw.text((x+14,y+ch-38),f"{i+1:02d}  {r['title']}",font=font,fill='#293e36')
        canvas.save(a.output/f'{mode}-overview.jpg',quality=93)
    (a.output/'packages.json').write_text(json.dumps([dict(id=r['id'],kind=r['kind'],path=str(folder),assembly=r['assembly']) for folder,r in records],indent=2)+'\n')
    print(json.dumps(dict(packages=len(records),native_amenity_modules=len(modules),module_bytes=sum(m['bytes'] for m in modules.values()))))


if __name__=='__main__':main()
