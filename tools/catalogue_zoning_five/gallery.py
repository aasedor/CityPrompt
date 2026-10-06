"""Package a local, read-only comparison gallery from reviewed model evidence.

Copies original images unchanged. This is an offline review gallery, not a
City Prompt installation or a runtime/performance acceptance test.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--batch-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--office',default='office-v004')
    p.add_argument('--row',default='row-v004')
    p.add_argument('--school',default='school-v004')
    a=p.parse_args();root=a.batch_root.resolve()
    historic=Path('C:/dev-artifacts/CityPrompt/2026-09-02_clay-eight-10h')
    roster=[
        ('Industrial shed',historic/'08-corrugated-vernacular-industrial/v002','Existing exact-variant model, independently rechecked.'),
        ('Classic retail strip',historic/'07-commercial-strip-mall/v002','Existing exact-variant model, independently rechecked.'),
        ('Neoclassical office',root/a.office,'New two-storey office with a portico and rooftop cupola.'),
        ('RNDSQR contextual townhouses',root/a.row,'New four-home row with three floors and rooftop access rooms.'),
        ('Provincial Brick school',root/a.school,'New courtyard school. Front and aerial references conflict; the chosen roof/dormer interpretation is recorded.'),
    ]
    # Validate every input before creating an output folder.
    records=[]
    for title,path,note in roster:
        report=read(path/'build-report.json');manifest=read(path/'prework-manifest.json')
        reviewpath=root/'independent-review'/f'{report["candidate"]}-independent-review-2026-10-05.json'
        review=read(reviewpath)
        glb=path/report['runtime']['path']
        if digest(glb)!=report['runtime']['sha256']:raise ValueError(f'Model changed: {glb}')
        reviewed_hash=review.get('integrity',{}).get('glb_sha256') or review.get('checks',{}).get('glb',{}).get('sha256')
        if review['candidate']!=report['candidate'] or reviewed_hash!=report['runtime']['sha256']:
            raise ValueError(f'Review does not identify this exact model: {reviewpath}')
        decision=review.get('decision') or review.get('status')
        if not decision:raise ValueError(f'Review has no decision: {reviewpath}')
        inspected=review.get('inspected_files',review.get('inspected_images',[]))
        for item in inspected:
            if digest(path/item['path'])!=item['sha256']:
                raise ValueError(f'Reviewed image changed: {item["path"]}')
        records.append(dict(title=title,path=path,note=note,report=report,manifest=manifest,review=review,reviewpath=reviewpath,decision=decision))
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    cards=[];inventory=[]
    for i,r in enumerate(records,1):
        target=out/f'{i:02d}';target.mkdir()
        candidates=[(r['path']/'renders/front_corner.png','model.png'),
            (r['path']/'renders/aerial.png','aerial.png'),
            (r['path']/'renders/rear_side.png','rear.png'),
            (r['path']/'boards/phone-source-comparison.png','comparison.png'),
            (r['path']/'boards/phone-construction.png','construction.png'),
            (r['reviewpath'],'review.json')]
        source=next(s for s in r['manifest']['source_contract']['sources'] if s['role']=='front')
        candidates.append((r['path']/source['path'],'reference'+Path(source['path']).suffix))
        copies=[]
        for original,name in candidates:
            dest=target/name;shutil.copy2(original,dest)
            assert digest(dest)==digest(original)
            copies.append(dict(path=str(dest.relative_to(out)).replace('\\','/'),source=str(original),sha256=digest(dest)))
        refname=candidates[-1][1]
        passed=r['decision']=='PASS_ARCHITECTURAL_CLAY_ONLY'
        status='Independent clay review passed' if passed else 'Visual rework required'
        model=r['report']['runtime']
        inventory.append(dict(title=r['title'],candidate=r['report']['candidate'],candidate_path=str(r['path']),
            status=r['decision'],model_sha256=model['sha256'],model_bytes=model['bytes'],copies=copies,
            runtime='NOT TESTED',publication='LOCAL ONLY'))
        esc=html.escape
        cards.append(f'''<article>
          <div class="heading"><h2>{i:02d} / {esc(r['title'])}</h2><span class="badge {'pass' if passed else 'hold'}">{status}</span></div>
          <p>{esc(r['note'])}</p><div class="pair">
          <figure><a href="{i:02d}/{refname}"><img src="{i:02d}/{refname}" alt="Locked design reference for {esc(r['title'])}" loading="lazy"></a><figcaption>Design reference</figcaption></figure>
          <figure><a href="{i:02d}/model.png"><img src="{i:02d}/model.png" alt="Actual exported clay model of {esc(r['title'])}" loading="lazy"></a><figcaption>Exported 3D model · {model['bytes']/1_000_000:.2f} MB</figcaption></figure></div>
          <nav aria-label="{esc(r['title'])} evidence"><a href="{i:02d}/aerial.png">Roof view</a><a href="{i:02d}/rear.png">Rear view</a><a href="{i:02d}/comparison.png">Source comparison</a><a href="{i:02d}/construction.png">Construction details</a><a href="{i:02d}/review.json">Independent review</a></nav>
        </article>''')
    document='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>City Prompt — five RLASM model studies</title><style>
:root{color-scheme:light;font-family:system-ui,sans-serif;background:#f3f0e9;color:#263238}*{box-sizing:border-box}body{margin:0}main{max-width:1180px;margin:auto;padding:42px 24px}header{max-width:900px;margin-bottom:36px}.eyebrow{font-size:13px;letter-spacing:.15em;text-transform:uppercase}h1{font-size:clamp(30px,5vw,52px);letter-spacing:-.035em;margin:12px 0}header p{font-size:18px;line-height:1.65}article{background:#fffdf8;border:1px solid #d8d5cb;border-radius:12px;padding:24px;margin-bottom:26px}.heading{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}h2{font-size:22px;margin:0}.badge{padding:7px 10px;font-size:12px;border-radius:4px}.pass{background:#dfece3;color:#225c37}.hold{background:#f6e6bf;color:#765318}article p{color:#58636a;line-height:1.5}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img{width:100%;aspect-ratio:4/3;object-fit:contain;background:#e6e5e1;display:block}figcaption{font-size:13px;padding:10px 0;color:#59646a}nav{display:flex;gap:12px 20px;flex-wrap:wrap;margin-top:14px}a{color:#255975;text-underline-offset:3px}nav a{font-size:14px}footer{font-size:14px;line-height:1.65;color:#58636a}@media(max-width:650px){main{padding:24px 12px}.pair{grid-template-columns:1fr}article{padding:16px}}
</style><main><header><div class="eyebrow">City Prompt / RLASM v6.1 / 5 October 2026</div><h1>Five building studies</h1><p>Reference images beside renders of the actual exported 3D models. These architectural clay models establish the form, openings and building details before final surface textures.</p><p>Local review batch. Student placement, terrain, editing and classroom performance have not been tested for this batch.</p></header>'''+''.join(cards)+'''<footer>Source dimensions and unseen interiors are inferred from the reference images. These are design studies, not surveys or confirmation of zoning permission. Fixed native scale only. Nothing in this batch has been published or added to the live catalogue.</footer></main></html>'''
    (out/'index.html').write_text(document,encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
    print(json.dumps(dict(gallery=str(out/'index.html'),candidates=len(inventory),passed=sum(r['status']=='PASS_ARCHITECTURAL_CLAY_ONLY' for r in inventory)),indent=2))


if __name__=='__main__':main()
