"""Matched-view evidence layouts; label/letterbox originals without retouching."""
import argparse
import math
from pathlib import Path
import shutil

from PIL import Image
from tools.catalogue_services_batch import proof
from tools.catalogue_zoning_five.prepare_review import require_complete


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('candidate',type=Path)
    args=parser.parse_args()
    root=args.candidate.resolve()
    manifest=proof.read(root/'prework-manifest.json')
    require_complete(root,manifest)
    if (root/'evidence/delivery-verification.json').exists():
        raise FileExistsError('Candidate review evidence is immutable')
    dest=root/'boards'
    source={s['role']:root/s['path'] for s in manifest['source_contract']['sources']}
    board=Image.new('RGB',(1800,570),'#f3f0e8')
    proof.label(board,22,15,'ORIGINAL GENERATED REFERENCES / exact design',28)
    for i,role in enumerate(('front','oblique','top')):
        proof.label(board,20+i*600,60,role.upper(),22)
        proof.panel(board,source[role],10+i*600,92,580,445)
    board.save(dest/'locked-source-board.png')
    phone=Image.new('RGB',(1080,1920),'#f3f0e8')
    proof.label(phone,28,25,'SOURCE / EXPORTED ARCHITECTURAL CLAY',28)
    proof.label(phone,28,73,manifest['candidate'],21)
    for i,(s,v) in enumerate([('front','front'),('oblique','front_corner'),('top','aerial')]):
        y=145+i*550
        proof.label(phone,28,y,'SOURCE / '+s,23)
        proof.label(phone,554,y,'DELIVERED / '+v,23)
        proof.panel(phone,source[s],28,y+50,498,415)
        proof.panel(phone,root/'renders'/f'{v}.png',554,y+50,498,415)
    proof.label(phone,28,1815,'Generated originals; metric scale and hidden rooms inferred.',21)
    proof.label(phone,28,1860,'Architectural clay. Runtime and textured keeper not approved.',21)
    phone.save(dest/'phone-source-comparison.png')
    phone=Image.new('RGB',(1080,1920),'#f3f0e8')
    proof.label(phone,28,25,'CONSTRUCTION / ACTUAL GLB REIMPORT',30)
    for i,role in enumerate(('architecture_close','glass_close','facade_close','roof_contact','stairs','bathroom')):
        x=28+i%2*526;y=125+i//2*540
        proof.label(phone,x,y,role.replace('_',' '),24)
        proof.panel(phone,root/'renders'/f'{role}.png',x,y+48,500,420)
    proof.label(phone,28,1820,'Full-resolution evidence is retained in renders/.',23)
    proof.label(phone,28,1860,'Geometry counts never substitute for visual review.',23)
    phone.save(dest/'phone-construction.png')
    views=manifest['mandatory_review_views']
    sheet=Image.new('RGB',(1920,math.ceil(len(views)/4)*405+70),'#f3f0e8')
    proof.label(sheet,24,15,manifest['candidate']+' / view inventory',26)
    for i,view in enumerate(views):
        x=i%4*480;y=75+i//4*405
        proof.label(sheet,x+12,y,view,22)
        proof.panel(sheet,root/'renders'/f'{view}.png',x+8,y+34,464,360)
    sheet.save(dest/'all-views-contact.png')
    proof.save_json(dest/'layout-provenance.json',dict(
        operation='Letterboxing and labels only; no image generation, retouching, cropping or relighting.',
        inputs=[dict(path=str(p.relative_to(root)),sha256=proof.sha(p))
                for p in list(source.values())+sorted((root/'renders').glob('*.png'))]))
    shutil.copy2(__file__,root/'scripts/prepare_review.py')
    result=proof.verify(root,manifest)
    proof.save_json(root/'evidence/runtime-status.json',dict(status='NOT_TESTED',
        limitations=['No catalogue activation','No CityPrompt placement, walking or persistence trial yet',
                     'Fixed native scale only','Architectural clay, not a textured keeper']))
    print(result['status'])
    return 0 if result['status']=='PASS_DELIVERY_CHECKS' else 1


if __name__=='__main__':
    raise SystemExit(main())
