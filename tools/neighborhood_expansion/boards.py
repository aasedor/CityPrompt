"""Exact source and render comparisons for a completed expansion candidate."""
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

root=Path(sys.argv[1])
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)

def board(name,items,size,cols):
    out=Image.new('RGB',size,'#f4f1e9');draw=ImageDraw.Draw(out)
    rows=(len(items)+cols-1)//cols;w=size[0]//cols;h=size[1]//rows
    for i,(label,p) in enumerate(items):
        x=i%cols*w;y=i//cols*h;draw.text((x+16,y+12),label,fill='#252b28',font=font)
        im=ImageOps.contain(Image.open(p).convert('RGB'),(w-24,h-55))
        out.paste(im,(x+(w-im.width)//2,y+48+(h-55-im.height)//2))
    out.save(root/'boards'/name)

spec=json.loads((root/'prework-manifest.json').read_text(encoding='utf-8'))
sources=[(p.stem,p) for p in sorted((root/'sources').glob('*.png'))]
renders=[(n,root/'renders'/(n+'.png')) for n in spec['mandatory_review_views']]
assert all(p.is_file() for _,p in renders),'Required render missing'
board('source-board.png',sources,(1440,1800),1)
front=next(s for s in spec['source_contract']['sources'] if s.get('role')=='front')
interior=next(n for n in ('classroom_left','left_living_0','reading_hall','program_interior') if (root/'renders'/(n+'.png')).is_file())
board('phone-comparison.png',[
    ('Original generated design',root/front['path']),
    ('Exact exported GLB',root/'renders/front.png'),
    ('Exported GLB occupied interior',root/'renders'/(interior+'.png'))],(1080,1920),1)
board('all-views.jpg',renders,(2560,640*((len(renders)+2)//3)),3)
