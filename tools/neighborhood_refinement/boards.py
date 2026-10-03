import sys,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
root=Path(sys.argv[1]);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
def board(path,items,size,cols):
    out=Image.new('RGB',size,'#f4f1e9');d=ImageDraw.Draw(out);rows=(len(items)+cols-1)//cols;w=size[0]//cols;h=size[1]//rows
    for i,(label,p) in enumerate(items):
        x=i%cols*w;y=i//cols*h;d.text((x+16,y+12),label,fill='#252b28',font=font)
        im=ImageOps.contain(Image.open(p).convert('RGB'),(w-24,h-55));out.paste(im,(x+(w-im.width)//2,y+48+(h-55-im.height)//2))
    out.save(path)
sources=[(p.stem,p) for p in sorted((root/'sources').glob('*.png'))]
board(root/'boards/source-board.png',sources,(1440,1800),1)
board(root/'boards/phone-comparison.png',[('Original generated design',root/'sources/variant_0.png'),('Exact exported GLB',root/'renders/front.png'),('Exported GLB interior',root/'renders/program_interior.png')],(1080,1920),1)
renders=[(p.stem,p) for p in sorted((root/'renders').glob('*.png'))]
board(root/'boards/all-views.jpg',renders,(2560,640*((len(renders)+2)//3)),3)
