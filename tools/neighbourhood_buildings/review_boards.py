"""Assemble unaltered source/render evidence in 1080 x 1920 comparisons."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

def main():
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);a=p.parse_args();root=a.package
    building=(root/'prework-manifest.json').exists()
    m=json.loads((root/('prework-manifest.json' if building else 'recipe.json')).read_text())
    sources=m['source_contract']['sources'] if building else m['source_references']
    refs={s['role']:root/s['path'] if building else root/Path(s['path']).name for s in sources}
    boarddir=root/'boards';boarddir.mkdir(exist_ok=True)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30)
    boards=[]
    for role,view in [('front','front_corner' if building else 'aerial'),('oblique','aerial'),('top','top')]:
        canvas=Image.new('RGB',(1080,1920),'#eeefea');draw=ImageDraw.Draw(canvas)
        for y,path,title in [(45,refs[role],'Locked catalogue reference: '+role),(990,root/'renders'/f'{view}.png','Exact exported GLB: '+view)]:
            draw.text((32,y),title,font=font,fill='#19261e')
            im=Image.open(path).convert('RGB');im=ImageOps.contain(im,(1020,850));canvas.paste(im,((1080-im.width)//2,y+60+(850-im.height)//2))
        out=boarddir/f'phone-{role}.png'
        if out.exists():raise ValueError('Do not overwrite evidence')
        canvas.save(out);boards.append(str(out.relative_to(root)))
    files={str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ['sources','renders','boards'] for f in (root/folder).glob('*') if f.is_file()}
    (root/'review-input-checksums.json').write_text(json.dumps(dict(files=files,phone_boards=boards),indent=2)+'\n')
    print(json.dumps(dict(phone_boards=boards,files=len(files))))
if __name__=='__main__':main()
