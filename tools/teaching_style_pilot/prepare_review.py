"""Labelled source/GLB evidence, with original source board kept unchanged."""
from pathlib import Path
import argparse
import json
import math
import shutil

from PIL import Image
from tools.catalogue_services_batch import proof
from tools.teaching_style_pilot.contracts import verify_evidence


def main():
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);a=p.parse_args()
    root=a.candidate.resolve();m=proof.read(root/'prework-manifest.json');r=proof.read(root/'build-report.json')
    verify_evidence(m['source_contract']['sources'],root,require_renders=True)
    if (root/'boards/phone-source-comparison.png').exists():raise FileExistsError('Evidence already exists')
    by_role={s['role']:root/s['path'] for s in m['source_contract']['sources']}
    source=by_role['front']
    # Panel extraction for matched evidence only; no retouching, repainting or
    # generation. Unmodified original board remains the source authority.
    with Image.open(source) as board:
        w,h=board.size
        regions={'front':(0,0,w//2,round(h*.45)),
                 'oblique':(w//2,0,w,round(h*.45)),
                 'top':(0,round(h*.49),w//2,round(h*.96)),
                 'rear_side':(w//2,round(h*.49),w,round(h*.96))}
        if len(set(by_role.values()))==1:
            for role,rect in regions.items():board.crop(rect).save(root/'boards'/f'source-panel-{role}.png')
        else:
            regions={r:'unchanged separate source view' for r in by_role}
            for role,path in by_role.items():shutil.copy2(path,root/'boards'/f'source-panel-{role}.png')
    locked=Image.new('RGB',(1800,620),'#f3f0e8')
    proof.label(locked,22,18,'LOCKED COMPATIBLE SOURCE VIEWS / original generated design',29)
    for i,role in enumerate(('front','oblique','top')):
        proof.label(locked,22+i*600,75,role.upper(),25)
        proof.panel(locked,root/'boards'/f'source-panel-{role}.png',12+i*600,120,576,465)
    locked.save(root/'boards/locked-source-board.png')
    phone=Image.new('RGB',(1080,1920),'#f3f0e8')
    proof.label(phone,28,25,'GENERATED SOURCE / EXPORTED ARCHITECTURAL CLAY',27)
    proof.label(phone,28,77,m['candidate'],23)
    for i,(s,v) in enumerate([('front','front'),('oblique','front_corner'),('top','top')]):
        y=145+i*540
        proof.label(phone,28,y,'SOURCE / '+s,24);proof.label(phone,554,y,'EXACT GLB / '+v,24)
        proof.panel(phone,root/'boards'/f'source-panel-{s}.png',28,y+45,498,435)
        proof.panel(phone,root/'renders'/f'{v}.png',554,y+45,498,435)
    proof.label(phone,28,1810,'Original design. Metric scale and unseen elevations are inferred.',21)
    proof.label(phone,28,1857,'Architectural clay; runtime and textured keeper not approved.',22)
    phone.save(root/'boards/phone-source-comparison.png')
    views=[s['name'] for s in m['camera_roster']]
    details=[v for v in views if v not in ('front','front_corner','aerial','top','left_side','right_side','rear','rear_side')]
    phone=Image.new('RGB',(1080,1920),'#f3f0e8');proof.label(phone,28,25,'CONSTRUCTION / EXACT GLB REIMPORT',29)
    for i,v in enumerate(details[:6]):
        x=28+i%2*526;y=125+i//2*540
        proof.label(phone,x,y,v.replace('_',' '),23);proof.panel(phone,root/'renders'/f'{v}.png',x,y+45,498,430)
    proof.label(phone,28,1857,'Full-resolution originals retained in renders/.',24)
    phone.save(root/'boards/phone-construction.png')
    sheet=Image.new('RGB',(1920,math.ceil(len(views)/4)*405+70),'#f3f0e8')
    proof.label(sheet,24,16,m['candidate']+' / complete view inventory',27)
    for i,v in enumerate(views):
        x=i%4*480;y=75+i//4*405
        proof.label(sheet,x+12,y,v,22);proof.panel(sheet,root/'renders'/f'{v}.png',x+8,y+34,464,360)
    sheet.save(root/'boards/all-views-contact.png')
    m['mandatory_review_views']=views
    m['provenance']['scripts']=[dict(path='scripts/'+p.name,sha256=proof.sha(p)) for p in (root/'scripts').glob('*.py')]
    proof.save_json(root/'evidence/layout-provenance.json',dict(operation='Label and letterbox enrolled source views; extract panels only when a shared board is supplied. No semantic image alteration.',
        source_sha256={role:proof.sha(path) for role,path in by_role.items()},source_panel_rectangles=regions))
    # Pass metadata as an in-memory supplement; never rewrite immutable prework.
    result=proof.verify(root,m)
    proof.save_json(root/'evidence/review-input-manifest.json',dict(candidate=m['candidate'],mandatory_review_views=views,
        files=[dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=proof.sha(p)) for p in
               [source,*sorted((root/'renders').glob('*.png')),*sorted((root/'boards').glob('*.png'))]],
        model_sha256=r['runtime']['sha256'],deterministic_status=result['status']))
    shutil.copy2(__file__,root/'scripts/prepare_review.py')
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='PASS_DELIVERY_CHECKS' else 1


if __name__=='__main__':raise SystemExit(main())
