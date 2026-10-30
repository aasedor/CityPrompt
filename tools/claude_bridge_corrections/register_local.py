"""Register one exact, independently reviewed bridge for local rehearsal only.

No catalogue splice, production activation, upload, or source-GLB mutation.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--archetype', required=True)
    parser.add_argument('--variant', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--hero', required=True)
    args = parser.parse_args()
    report = read(args.candidate / 'build-report.json')
    review_path = args.candidate / 'review/independent-review.json'
    review = read(review_path)
    candidate = report['candidate']
    model = args.candidate / report['runtime']['path']
    sha = digest(model)
    if not (sha == report['runtime']['sha256'] == review['model_sha256']
            and review.get('candidate') == candidate
            and review.get('holistic_review_performed') is True
            and review.get('category_closure_only') is False
            and review['architectural_clay_pass'] is True
            and review['unresolved_p0'] == review['unresolved_p1'] == 0):
        raise ValueError('Exact holistic independent architectural-clay review is required')
    public = ROOT / 'frontend/public'
    hero = (public / args.hero.lstrip('/')).resolve()
    if not hero.is_relative_to(public.resolve()) or not hero.is_file():
        raise ValueError('Hero must be an existing exact local source image')
    thumbnail_sha = digest(hero)
    sources = read(args.candidate / 'source-entry.json')
    nominated = sources['source_archetype'].split('/')
    if (len(nominated) != 2 or nominated[0] != args.archetype
            or args.variant != args.archetype + '_v' + nominated[1].removeprefix('variant_')
            or not any(source['sha256'] == thumbnail_sha
                       and Path(source['original_path']).as_posix().endswith(args.hero)
                       for source in sources['sources'])):
        raise ValueError('Hero and variant must match the exact locked source')
    prefix = '/street-kits/claude-20261023/'
    slug = candidate.removeprefix('clay-').split('-clay-v')[0]
    asset_id = f'claude_public_realm:{slug}:{sha[:12]}'
    path = ROOT / 'frontend/src/data/publicRealmRelease20261023.json'
    manifest = read(path)
    asset = copy.deepcopy(next(row['asset'] for row in manifest['models']
                               if row['candidate'] == 'clay-weathering-steel-footbridge-clay-v003'))
    native = [report['native_dimensions_m'][key] for key in ('width', 'depth', 'height')]
    dimensions = [math.ceil((size + .3) * 10) / 10 for size in native[:2]]
    description = ('Fixed bridge with bounded structural supports and approaches. Move and rotate; '
                   'prepared level site required. Native dimensions; no stretching or automatic intersections.')
    asset.update(id=asset_id, label=args.title, description=description,
                 thumbnail=prefix + thumbnail_sha + hero.suffix, readiness='pilot',
                 width=dimensions[0], depth=dimensions[1], minWidth=dimensions[0], minDepth=dimensions[1],
                 maxWidth=dimensions[0], maxDepth=dimensions[1], nativeDimensions=native,
                 reshapeDescription='Move and rotate the complete bridge. Its authored geometry stays fixed.')
    asset['model'].update(variantId=args.variant, revision=sha)
    asset['properties'].update(road_archetype_id=args.archetype, road_selected_variant_id=args.variant,
                               public_realm_release_asset=asset_id, native_public_realm_url=prefix + sha + '.glb')
    fixture = dict(id=asset_id, title=args.title, kind='street', dimensions=dimensions, sha256=sha,
                   url=prefix + sha + '.glb', surfaceRegions=[], preserveNativeGround=True, centerNativeClay=True)
    row = dict(candidate=candidate, category='street', source_sha256=sha,
               review_sha256=digest(review_path), runtime_sha256=sha, thumbnail_sha256=thumbnail_sha,
               status='runtime_trial', visual_review=dict(status='passed', scope='complete_runtime_derivative',
                   runtime_sha256=sha, evidence_sha256=digest(review_path), unresolved_p0=0, unresolved_p1=0),
               runtime_review=dict(status='pending', runtime_sha256=sha, evidence_sha256=None), asset=asset, fixture=fixture)
    existing = [value for value in manifest['models'] if value['candidate'] == candidate or value['asset']['id'] == asset_id]
    if existing and existing != [row]:
        raise ValueError('Existing binding differs; preserve it and advance a new candidate')
    if not existing:
        manifest['models'].append(row)
    destination = public / prefix.lstrip('/')
    destination.mkdir(parents=True, exist_ok=True)
    for source, name in ((model, sha + '.glb'), (hero, thumbnail_sha + hero.suffix)):
        target = destination / name
        if target.exists() and digest(target) != digest(source):
            raise ValueError('Hash-addressed payload differs: ' + str(target))
        if not target.exists():
            target.write_bytes(source.read_bytes())
    write(path, manifest)
    write(ROOT / 'backend/app/data/public_realm_release_20261023.json', manifest)
    heroes_path = ROOT / 'frontend/src/data/catalogueHeroImages.json'
    heroes = read(heroes_path)
    heroes[asset_id] = args.hero
    write(heroes_path, heroes)
    print(json.dumps(dict(candidate=candidate, asset_id=asset_id, sha256=sha,
                          dimensions=dimensions, native_dimensions=native, local_trial_only=True)))


if __name__ == '__main__':
    main()
