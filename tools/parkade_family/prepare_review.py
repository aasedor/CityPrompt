"""Diagnostic comparison layouts from immutable sources and actual GLB renders."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps


def main():
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);a=p.parse_args()
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
    for role in ('front','oblique','top'):
        if (a.candidate/'boards'/(role+'-phone.png')).exists():
            raise FileExistsError('Reviewed evidence is immutable; use a new candidate or evidence directory')
    for role,render in [('front','front'),('oblique','front_corner'),('top','top')]:
        board=Image.new('RGB',(1080,1920),'#f6f3ea');draw=ImageDraw.Draw(board)
        draw.text((30,25),f'{a.candidate.name.upper()} / {role.upper()}',font=font,fill='black')
        draw.text((30,80),'Original design reference',font=font,fill='black')
        with Image.open(a.candidate/'sources'/(role+'.png')) as src:
            tile=ImageOps.contain(src,(1020,800));board.paste(tile,((1080-tile.width)//2,140+(800-tile.height)//2))
        draw.text((30,990),'Delivered GLB reimport / architectural clay',font=font,fill='black')
        with Image.open(a.candidate/'renders'/(render+'.png')) as src:
            tile=ImageOps.contain(src,(1020,800));board.paste(tile,((1080-tile.width)//2,1060+(800-tile.height)//2))
        with (a.candidate/'boards'/(role+'-phone.png')).open('xb') as output:
            board.save(output,format='PNG')


if __name__=='__main__':main()
