"""Preserve one RLASM clay candidate from its artefact directory into the repository.

Mirrors the pilot brownstone preservation: the GLB goes to tools/<family>/candidates/ as an
ordinary blob (must stay under 1 MiB; Git LFS uploads are refused from the cloud build host),
the build report, source entry, prework manifest, aperture audit, reviewer brief and the
independent review record go to tools/<family>/evidence/<version>/, and every render and
phone board is stored there as a JPEG under 950 KB. Full-resolution PNGs plus the GLB are
zipped beside the artefact directory for delivery to the user.

Usage: python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/<family> [--version vNNN]
"""
import argparse
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image

MAX_JPEG = 950_000
MAX_GLB = 1_048_576
DOCS = ['build-report.json', 'source-entry.json', 'prework-manifest.json']


def jpeg_under(src, dest, limit=MAX_JPEG):
    img = Image.open(src).convert('RGB')
    for q in (92, 88, 84, 80, 76, 72, 68, 64, 60, 55, 50):
        img.save(dest, 'JPEG', quality=q, optimize=True, progressive=True)
        if dest.stat().st_size <= limit:
            return q
    raise RuntimeError('cannot fit ' + str(src))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', required=True)
    p.add_argument('--family', required=True)
    p.add_argument('--version', default=None)
    a = p.parse_args()
    cand = Path(a.candidate).resolve()
    fam = Path(a.family).resolve()
    report = json.loads((cand / 'build-report.json').read_text())
    name = report['candidate']
    version = a.version or name.rsplit('-', 1)[-1]
    ev = fam / 'evidence' / version
    (ev / 'renders').mkdir(parents=True, exist_ok=True)
    (ev / 'boards').mkdir(parents=True, exist_ok=True)
    (fam / 'candidates').mkdir(exist_ok=True)
    for d in DOCS:
        shutil.copy2(cand / d, ev / d)
    shutil.copy2(cand / 'evidence' / 'carrier-aperture-audit.json', ev / 'carrier-aperture-audit.json')
    for d in ('review/brief.md', 'review/independent-review.md'):
        if (cand / d).is_file():
            shutil.copy2(cand / d, ev / Path(d).name)
    qualities = {}
    for png in sorted((cand / 'renders').glob('*.png')):
        qualities[png.name] = jpeg_under(png, ev / 'renders' / (png.stem + '.jpg'))
    for png in sorted((cand / 'boards').glob('*.png')):
        qualities[png.name] = jpeg_under(png, ev / 'boards' / (png.stem + '.jpg'))
    glb = cand / report['runtime']['path']
    assert glb.stat().st_size < MAX_GLB, glb.stat().st_size
    shutil.copy2(glb, fam / 'candidates' / glb.name)
    zip_path = cand.parent / (name + '-renders-and-glb.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for png in sorted((cand / 'renders').glob('*.png')):
            z.write(png, 'renders/' + png.name)
        for png in sorted((cand / 'boards').glob('*.png')):
            z.write(png, 'boards/' + png.name)
        for s in sorted((cand / 'sources').iterdir()):
            z.write(s, 'sources/' + s.name)
        z.write(glb, glb.name)
        for d in DOCS + ['evidence/carrier-aperture-audit.json']:
            z.write(cand / d, Path(d).name)
        if (cand / 'review' / 'independent-review.md').is_file():
            z.write(cand / 'review' / 'independent-review.md', 'independent-review.md')
    (ev / 'preservation.json').write_text(json.dumps(dict(candidate=name, glb=glb.name, glb_bytes=glb.stat().st_size,
        glb_sha256=report['runtime']['sha256'], jpeg_qualities=qualities, zip=zip_path.name, zip_bytes=zip_path.stat().st_size), indent=2) + '\n')
    print(json.dumps(dict(evidence=str(ev), glb=str(fam / 'candidates' / glb.name), zip=str(zip_path), zip_bytes=zip_path.stat().st_size)))


if __name__ == '__main__':
    main()
