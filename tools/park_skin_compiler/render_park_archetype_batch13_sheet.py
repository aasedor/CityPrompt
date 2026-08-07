"""Render the mobile-friendly Batch 13 reference/skin comparison sheet."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from compile_neighborhood_park_skins import REPO_ROOT
SCHEDULE=Path(__file__).with_name("park_archetype_batch13_skin_sources.json");DEFAULT_OUT=REPO_ROOT/"docs/park_lego_batch13/park_lego_batch13_reference_skin_sheet.jpg";ROLE_COLORS={"paver":"#d9cfbc","lawn":"#78935f","asphalt":"#555754","planting":"#57704c","safety":"#b78355","timber":"#8a6646"}
def cover(image:Image.Image,size:tuple[int,int])->Image.Image:
 scale=max(size[0]/image.width,size[1]/image.height);resized=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS);left=(resized.width-size[0])//2;top=(resized.height-size[1])//2;return resized.crop((left,top,left+size[0],top+size[1]))
def main()->None:
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--out",type=Path,default=DEFAULT_OUT);parser.add_argument("--skin-root",type=Path,default=REPO_ROOT/"frontend/public/park-skins");args=parser.parse_args();items=list(json.loads(SCHEDULE.read_text(encoding="utf-8"))["archetypes"].items());width,row_height=1500,245;canvas=Image.new("RGB",(width,110+row_height*len(items)),"#eee9df");draw=ImageDraw.Draw(canvas);font=ImageFont.load_default();draw.rectangle((0,0,width,90),fill="#252b29");draw.text((34,24),"PARK LEGO BATCH 13 - EXACT REFERENCE + ADAPTIVE 3D FAMILY",fill="white",font=font);draw.text((34,50),"10 landscape and waterfront parents - no people/large buildings - zero API calls",fill="#c8d7c6",font=font);roles=["paver","lawn","asphalt","planting","safety","timber"]
 for index,(slug,item) in enumerate(items):
  top=100+index*row_height;draw.rounded_rectangle((20,top,width-20,top+row_height-10),radius=16,fill="#f8f5ee",outline="#c7bfae",width=2);canvas.paste(cover(Image.open(REPO_ROOT/item["source"]).convert("RGB"),(420,190)),(40,top+28));draw.text((40,top+8),f"{index+1:02d}  {slug.replace('-',' ').upper()}",fill="#27312d",font=font)
  for ri,role in enumerate(roles):
   left=495+ri*158;path=args.skin_root/slug/"adaptive-v1"/role/"albedo.jpg";swatch=cover(Image.open(path).convert("RGB"),(142,142))if path.exists()else Image.new("RGB",(142,142),ROLE_COLORS[role]);canvas.paste(swatch,(left,top+40));draw.text((left,top+190),role.upper(),fill="#4a514d",font=font)
 args.out.parent.mkdir(parents=True,exist_ok=True);canvas.save(args.out,quality=91,optimize=True);print(args.out)
if __name__=="__main__":main()
