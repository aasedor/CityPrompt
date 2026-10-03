"""Compose labelled evidence sheets without changing source/render pixels."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);a=p.parse_args()
root=a.candidate;source=json.loads((root/'source-entry.json').read_text())
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27)
board=Image.new('RGB',(1080,1920),'#f4f1e9');draw=ImageDraw.Draw(board)
rows=[('Original design reference (AI-generated)',root/source['sources'][0]['path']),
      ('Exact delivered GLB: exterior',root/'renders/front_corner.png'),
      ('Exact delivered GLB: interior',root/'renders/program_interior.png')]
for i,(label,path) in enumerate(rows):
    y=i*640;draw.text((25,y+14),label,fill='#202428',font=font)
    img=Image.open(path).convert('RGB')
    if i==0 and source['archetype_id']=='gothic_community_church':
        # Evidence layout: show the enrolled front/oblique and governing roof;
        # never display the rejected lower-left alternative as design authority.
        top=img.crop((0,0,img.width,img.height//2))
        roof=Image.open(root/'sources/roof-reference-v1.png').convert('RGB')
        panel=Image.new('RGB',(1030,570),'#f4f1e9')
        for item,slot in ((top,(0,0,1030,285)),(roof,(0,285,1030,285))):
            fitted=ImageOps.contain(item,(slot[2],slot[3]));panel.paste(fitted,(slot[0]+(slot[2]-fitted.width)//2,slot[1]))
        img=panel
    img=ImageOps.contain(img,(1030,570))
    board.paste(img,((1080-img.width)//2,y+59+(570-img.height)//2))
board.save(root/'boards/phone-comparison.png')
