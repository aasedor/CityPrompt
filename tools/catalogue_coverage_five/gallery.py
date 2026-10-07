"""Package five independently reviewed original designs without altering images."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil

try:
    from .plan import SPECS
except ImportError:
    from plan import SPECS


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_candidate(path, review_path):
    report = read(path / 'build-report.json')
    manifest = read(path / 'prework-manifest.json')
    review = read(review_path)
    # Preserved passes can later be withdrawn without rewriting historical evidence.
    review_sha = digest(review_path)
    for other_path in review_path.parent.glob('*review*.json'):
        if other_path == review_path:
            continue
        other = read(other_path)
        if isinstance(other, dict) and other.get('candidate') == review['candidate'] and other.get('supersedes_review_sha256') == review_sha:
            raise ValueError('Independent review has been superseded: ' + other_path.name)
    model = report['runtime']
    reviewed_hash = review.get('integrity', {}).get('glb_sha256') or review.get('checks', {}).get('glb', {}).get('sha256')
    if digest(path / model['path']) != model['sha256'] or reviewed_hash != model['sha256']:
        raise ValueError('Model does not match its independent review')
    if review['candidate'] != report['candidate']:
        raise ValueError('Review candidate mismatch')
    if review.get('decision', review.get('status')) not in ('PASS_ARCHITECTURAL_CLAY_REVIEW', 'PASS_ARCHITECTURAL_CLAY_ONLY'):
        raise ValueError('Candidate has not passed independent clay review')
    if not review.get('holistic') or review.get('unresolved_blocker_counts') != {'P0': 0, 'P1': 0}:
        raise ValueError('Unresolved or incomplete holistic review')
    required = {f'renders/{n}.png' for n in manifest['mandatory_review_views']}
    required.update(s['path'] for s in manifest['source_contract']['sources'])
    required.update('boards/' + name for name in ('locked-source-board.png', 'phone-source-comparison.png', 'phone-construction.png', 'all-views-contact.png'))
    inspected = review.get('inspected_files', [])
    if not required.issubset({s['path'] for s in inspected}):
        raise ValueError('Mandatory images are missing from the independent review')
    for record in inspected:
        if digest(path / record['path']) != record['sha256']:
            raise ValueError('Reviewed evidence changed: ' + record['path'])
    return report, manifest, review


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--batch-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--selection', type=Path, required=True)
    a = p.parse_args()
    root = a.batch_root.resolve()
    records = []
    selection = read(a.selection)
    for kind, spec in SPECS.items():
        path = root / selection[kind]['folder']
        candidate = read(path / 'build-report.json')['candidate']
        review_path = root / selection[kind]['review']
        report, manifest, review = verified_candidate(path, review_path)
        records.append((kind, spec, path, report, manifest, review, review_path))
    out = a.output.resolve()
    if not out.is_relative_to(Path('C:/dev-artifacts/CityPrompt').resolve()):
        raise ValueError('Gallery must remain in external artifact storage')
    out.mkdir(parents=True, exist_ok=False)
    cards = []
    inventory = []
    esc = html.escape
    for number, (kind, spec, path, report, manifest, review, review_path) in enumerate(records, 1):
        prefix = f'{number:02d}'
        dest = out / prefix
        dest.mkdir()
        copies = []
        paths = [(path / 'renders/front_corner.png', 'model.png'),
                 (path / 'renders/aerial.png', 'roof.png'), (path / 'renders/rear_side.png', 'rear.png'),
                 (path / 'renders/interior.png', 'interior.png'),
                 (path / 'boards/phone-source-comparison.png', 'comparison.png'),
                 (path / 'boards/phone-construction.png', 'construction.png'),
                 (path / report['runtime']['path'], 'model.glb'), (review_path, 'review.json'),
                 (path / 'sources/generation-provenance.json', 'reference-provenance.json')]
        for source in manifest['source_contract']['sources']:
            paths.append((path / source['path'], 'reference-' + source['role'] + Path(source['path']).suffix))
        for source, name in paths:
            shutil.copy2(source, dest / name)
            if digest(source) != digest(dest / name):
                raise ValueError('Evidence copy changed')
            copies.append(dict(path=f'{prefix}/{name}', original=str(source), sha256=digest(dest / name)))
        metadata = dict(spec, model=dict(candidate=report['candidate'], **report['runtime']),
                        review=dict(decision=review['decision'], scope='architectural clay', runtime='NOT TESTED'),
                        publication='LOCAL ONLY')
        (dest / 'metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        routes = ''.join(f'<li><a href="{esc(r["url"], quote=True)}">{esc(r["district"])}</a> — {esc(r["category"])} · s.{esc(r["section"])}'
                         + (f'<p>{esc(r["remaining_conditions"])}</p>' if r.get('remaining_conditions') else '')
                         + '</li>' for r in spec['zoning_research']['district_candidates'])
        conditions = ''.join(f'<li>{esc(t)}</li>' for t in spec['zoning_research']['program_conditions'])
        dims = spec['dimensions_m']
        dimension_label = 'authored compound' if kind == 'mews' else 'authored main building'
        inventory.append(dict(kind=kind, title=spec['title'], candidate=report['candidate'], candidate_path=str(path),
                              model_sha256=report['runtime']['sha256'], model_bytes=report['runtime']['bytes'],
                              review_path=str(review_path), review_sha256=digest(review_path), status=review['decision'],
                              reference_count=3, runtime='NOT TESTED', copies=copies))
        cards.append(f'''<article id="{kind}">
<div class="eyebrow">{prefix} / {esc(' · '.join(spec['uses']))}</div>
<h2>{esc(spec['title'])}</h2><p class="style">{esc(' · '.join(spec['styles']))}</p>
<div class="pair"><figure><a href="{prefix}/reference-front.png"><img src="{prefix}/reference-front.png" alt="Original generated design reference for {esc(spec['title'])}" loading="lazy"></a><figcaption>Original generated reference</figcaption></figure>
<figure><a href="{prefix}/model.png"><img src="{prefix}/model.png" alt="Actual exported architectural clay model of {esc(spec['title'])}" loading="lazy"></a><figcaption>Exported 3D clay model · {report['runtime']['bytes']/1000000:.2f} MB</figcaption></figure></div>
<p>{esc(spec['program'])}</p><div class="facts"><span>{dims['width']:g} × {dims['depth']:g} m {dimension_label}</span><span>{dims['height']:g} m nominal height</span><span>{spec['storeys']} occupied storey(s)</span><span>Independent clay review passed</span></div>
<nav aria-label="{esc(spec['title'])} views"><a href="{prefix}/reference-oblique.png">Oblique reference</a><a href="{prefix}/reference-top.png">Overhead reference</a><a href="{prefix}/roof.png">Model roof</a><a href="{prefix}/rear.png">Model rear</a><a href="{prefix}/interior.png">Model interior</a><a href="{prefix}/comparison.png">Comparison board</a><a href="{prefix}/construction.png">Construction board</a></nav>
<details><summary>Calgary use routes &amp; design metadata</summary><p>Candidate use routes, subject to the programme and site conditions below. These do not establish parcel approval.</p><ul>{routes}</ul><ul>{conditions}</ul><p>{esc(spec.get('reference_reconciliation','Metric dimensions are authored; original pixels govern visible topology.'))}</p><nav><a href="{prefix}/metadata.json">Complete metadata</a><a href="{prefix}/reference-provenance.json">Reference prompts &amp; provenance</a><a href="{prefix}/review.json">Independent review</a><a href="{prefix}/model.glb" download>Download 3D model</a></nav></details></article>''')
    links = ''.join(f'<a href="#{kind}">{esc(spec["title"])}</a>' for kind, spec in SPECS.items())
    document = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>City Prompt — five original designs</title><style>
:root{font-family:system-ui,sans-serif;color:#263b35;background:#f0eee7;color-scheme:light}*{box-sizing:border-box}body{margin:0}main{max-width:1240px;margin:auto;padding:46px 28px}header{max-width:980px;margin-bottom:38px}.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:12px;font-weight:650;color:#657565}h1{font-family:Georgia,serif;font-weight:400;letter-spacing:-.035em;font-size:clamp(36px,5vw,62px);line-height:1.08;margin:15px 0 22px}header p{font-size:18px;line-height:1.7;color:#53645d}a{color:#265e54;text-underline-offset:4px}nav{display:flex;gap:12px 23px;flex-wrap:wrap;margin:20px 0 4px}nav a{font-size:14px}article{padding:28px;background:#fffefa;border:1px solid #d6d9cc;border-radius:10px;margin-bottom:32px;scroll-margin-top:18px}h2{font-size:27px;font-weight:550;letter-spacing:-.025em;margin:10px 0 6px}.style{margin:0 0 24px;color:#6b776a;font-size:14px}p{line-height:1.65}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}img{display:block;width:100%;aspect-ratio:4/3;object-fit:contain;background:#e7e9e3}figcaption{font-size:13px;color:#627165;padding:9px 0}.facts{display:flex;flex-wrap:wrap;gap:8px}.facts span{font-size:12px;padding:7px 10px;background:#e9eee4;border-radius:4px}details{border-top:1px solid #e0e3d9;padding-top:18px;margin-top:24px}summary{cursor:pointer;font-weight:600}li{line-height:1.6;margin:8px 0}footer{font-size:14px;line-height:1.7;color:#617064;margin:32px 0}@media(max-width:680px){main{padding:28px 12px}article{padding:18px}.pair{grid-template-columns:1fr}h2{font-size:23px}}
</style></head><body><main><header><div class="eyebrow">City Prompt / Original catalogue studies / RLASM v6.1</div><h1>Homes, a garden court, and a place to work.</h1><p>Five new designs: two manufactured homes, a Craftsman cottage, six courtyard homes and a compact office. Fifteen original reference images guide their source-locked 3D models.</p><p>The photographic images are original generated designs. The model views show the actual exported architectural clay geometry, before final surface textures. Each has passed independent review at this stage.</p><nav aria-label="Designs">'''+links+'''</nav></header>'''+''.join(cards)+'''<footer>Local review collection · 6 October 2026. These are fictional designs with authored dimensions and inferred unseen details. Garden Mews dimensions describe its compound, not a complete zoning parcel. Overhead references are design evidence, not survey orthophotos. Models use fixed native scale. Student placement, terrain and classroom performance remain untested. No live catalogue or hosted-site changes were made. Affordable housing inspired by Attainable Homes Calgary is reserved for the following batch.</footer></main></body></html>'''
    (out / 'index.html').write_text(document, encoding='utf-8')
    (out / 'manifest.json').write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(gallery=str(out / 'index.html'), candidates=5, references=15, status='PASS_ARCHITECTURAL_CLAY_REVIEW'), indent=2))


if __name__ == '__main__':
    main()
