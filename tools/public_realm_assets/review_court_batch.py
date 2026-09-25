"""Index the exact ten verified packages and lay out their native review images."""
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path
from court_specs import COURTS

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    p.add_argument('--source-manifest',type=Path);a=p.parse_args()
    folders=[a.root/kind for kind in COURTS]
    for folder in folders:
        verification=json.loads((folder/'geometry-verification.json').read_text(encoding='utf-8'))
        assert verification['status']=='PASS_OFFLINE_GEOMETRY',folder
        assert any('court-entry width rays' in check for check in verification['checks']),folder
        assert (folder/'renders/court.png').is_file(),folder
        for name in ('verify.py','verify_courts.py'):
            shutil.copy2(Path(__file__).with_name(name),folder/name)
    subprocess.run([sys.executable,str(Path(__file__).with_name('package_review.py')),
                    '--report',str(a.root/'manifest.json'),*[str(folder) for folder in folders]],check=True)
    # This is a contact-sheet layout of native renders; no AI or image enhancement.
    from PIL import Image, ImageDraw, ImageFont
    font_path=Path('C:/Windows/Fonts/segoeui.ttf')
    font=ImageFont.truetype(str(font_path),24) if font_path.exists() else ImageFont.load_default()
    title_font=ImageFont.truetype(str(font_path),36) if font_path.exists() else font
    def board(view,name,columns):
        cell_w,cell_h=560,470;rows=(len(folders)+columns-1)//columns
        canvas=Image.new('RGB',(columns*cell_w,rows*cell_h+100),'#efeee8');draw=ImageDraw.Draw(canvas)
        draw.text((24,18),f'City Prompt | Ten sports gardens | {view}',font=title_font,fill='#283d35')
        draw.text((24,63),'Native 3D models - browser integration deferred',font=font,fill='#59695f')
        for i,folder in enumerate(folders):
            r=json.loads((folder/'recipe.json').read_text(encoding='utf-8'));image=Image.open(folder/'renders'/f'{view}.png').convert('RGB')
            image.thumbnail((cell_w-16,cell_h-62))
            x=(i%columns)*cell_w;y=100+(i//columns)*cell_h
            canvas.paste(image,(x+(cell_w-image.width)//2,y))
            draw.text((x+12,y+cell_h-56),r['title'],font=font,fill='#283d35')
            draw.text((x+12,y+cell_h-28),f"Park: {r['dimensions_m'][0]:g} x {r['dimensions_m'][1]:g} m",font=font,fill='#59695f')
        canvas.save(a.root/name)
    board('aerial','ten-sports-gardens.png',5)
    board('top','ten-court-layouts.png',5)
    board('court','ten-court-details.png',2)
    records=[]
    for kind,folder in zip(COURTS,folders):
        r=json.loads((folder/'recipe.json').read_text(encoding='utf-8'))
        verification=json.loads((folder/'geometry-verification.json').read_text(encoding='utf-8'))
        files=[folder/'assembly-preview.glb',folder/'sport-module.glb',folder/'recipe.json',folder/'geometry-verification.json',*sorted((folder/'renders').glob('*.png'))]
        records.append(dict(kind=kind,id=r['id'],title=r['title'],dimensions_m=r['dimensions_m'],playing_m=r['playing_m'],module_m=r['module_m'],
            assembly=r['assembly'],sport_asset=r['sport_asset'],triangles=r['triangles'],mesh_instances=r['mesh_instances'],
            source=r['source'],package=str(folder),geometry_status=verification['status'],browser_status='DEFERRED_BY_USER',
            image_references=r.get('image_references',[]),reference_profile=r.get('reference_profile'),
            files={str(f.relative_to(a.root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}))
    (a.root/'delivery.json').write_text(json.dumps(dict(candidates=records,paid_calls=0,local_only=True,catalogue_activated=False),indent=2)+'\n',encoding='utf-8')
    if a.source_manifest:
        concise=[{k:v for k,v in record.items() if k!='files'} for record in records]
        a.source_manifest.write_text(json.dumps(dict(version=1,candidates=concise,paid_calls=0,
            runtime_activated=False,browser_status='DEFERRED_BY_USER',
            evidence_root=str(a.root)),indent=2)+'\n',encoding='utf-8')
    print('Indexed ten candidates, exact files and three native contact sheets.')
if __name__=='__main__':main()
