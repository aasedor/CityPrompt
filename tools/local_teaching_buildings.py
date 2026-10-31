"""Finite, development-only hydration of the seven reviewed teaching buildings.

No database, production seed, generation, approval or publication side effects.
Example: python -m tools.local_teaching_buildings --candidate wartime-victory-house-clay-v004
Add --apply after the dry run. --public-dir overrides the active local profile.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
from typing import Any

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / 'frontend/src/data/localTeachingBuildings.json'


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _contained(root: Path, value: str, *, url: bool = False) -> Path:
    relative = value[1:] if url and value.startswith('/') else value
    if not relative or '\\' in relative or ':' in relative or '?' in relative or '#' in relative:
        raise ValueError(f'Invalid asset path: {value}')
    parts = PurePosixPath(relative).parts
    if '..' in parts or PurePosixPath(relative).is_absolute() or (url and len(parts) < 2):
        raise ValueError(f'Invalid asset path: {value}')
    # The configured local public tree reuses hydrated top-level namespaces
    # through Windows junctions. Resolve that explicit namespace once, while
    # still refusing escapes through any nested link or parent segment.
    base = (root / parts[0]).resolve() if url else root.resolve()
    result = (base.joinpath(*parts[1:]) if url else base / relative).resolve()
    if result == base or not result.is_relative_to(base):
        raise ValueError(f'Asset path escapes root: {value}')
    return result


def install(manifest: dict[str, Any], source_root: Path, public_dir: Path,
            candidates: list[str], *, apply: bool = False) -> dict[str, Any]:
    if manifest.get('schema') != 'cityprompt.local-teaching-buildings@1' or manifest.get('local_trial_only') is not True:
        raise ValueError('Expected a local teaching trial manifest')
    roster = {row['candidate']: row for row in manifest['models']}
    if len(roster) != len(manifest['models']) or not candidates or len(set(candidates)) != len(candidates):
        raise ValueError('Expected unique, explicit candidates')
    if set(candidates) - roster.keys():
        raise ValueError('Unknown candidate: ' + ', '.join(sorted(set(candidates) - roster.keys())))
    plan: list[tuple[Path, Path, dict[str, Any]]] = []
    destinations: set[Path] = set()
    for candidate in candidates:
        entry = roster[candidate]
        roles: dict[str, list[Path]] = {}
        for item in entry['files']:
            source = _contained(source_root, item['source'])
            destination = _contained(public_dir, item['url'], url=True)
            expected = item['sha256']
            if not source.is_file() or _hash(source) != expected:
                raise ValueError(f'Source hash mismatch: {candidate} / {item["role"]}')
            if destination in destinations:
                raise ValueError(f'Duplicate destination path: {item["url"]}')
            destinations.add(destination)
            if destination.exists() and (not destination.is_file() or _hash(destination) != expected):
                raise ValueError(f'Conflicting destination: {item["url"]}; existing bytes preserved')
            roles.setdefault(item['role'], []).append(source)
            plan.append((source, destination, {'candidate': candidate, **item, 'bytes': source.stat().st_size}))
        if len(roles.get('model', [])) != 1 or len(roles.get('review', [])) != 1 or not roles.get('reference'):
            raise ValueError(f'Missing exact model, review or reference: {candidate}')
        model = roles['model'][0]
        review = json.loads(roles['review'][0].read_text(encoding='utf-8'))
        # Preserve the original independent review bytes. Wave 2 records its
        # pass as a decision and unresolved issues as lists, unlike the other
        # two cohorts' boolean/count schema.
        wave2_pass = (review.get('schema') == 'cityprompt.rlasm.independent_architectural_clay_review@1'
                      and review.get('decision') == 'approved_offline_architectural_clay')
        if (_hash(model) != entry['model_sha256'] or review.get('candidate') != candidate
                or review.get('model_sha256') != entry['model_sha256'] or not review.get('reviewer')
                or not (review.get('architectural_clay_pass') is True or wave2_pass)
                or not (review.get('holistic') is True or review.get('holistic_review_performed') is True)
                or review.get('unresolved_p0') not in (0, []) or review.get('unresolved_p1') not in (0, [])):
            raise ValueError(f'Independent review does not bind this model: {candidate}')
        import trimesh
        scene = trimesh.load(model, force='scene', process=False)
        declared = entry['asset']['nativeDimensions']
        # glTF Y up. Frontend dimensions are width, depth, height.
        measured = scene.extents[[0, 2, 1]] if scene.bounds is not None else []
        if len(declared) != 3 or len(measured) != 3 or any(
                not math.isfinite(float(a)) or float(a) <= 0 or
                not math.isclose(float(a), float(b), abs_tol=1e-4, rel_tol=1e-6)
                for a, b in zip(declared, measured)):
            raise ValueError(f'Native envelope differs from reviewed model: {candidate}')
    # All sources, reviews, bounds and destination conflicts validate before writes.
    for source, destination, item in plan:
        if apply:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                with destination.open('xb') as output:
                    output.write(source.read_bytes())
            if _hash(destination) != item['sha256']:
                raise ValueError(f'Installed readback hash mismatch: {item["url"]}')
    return {'schema': 'cityprompt.local-teaching-install@1',
            'status': 'installed_verified' if apply else 'dry_run',
            'public_dir': str(public_dir.resolve()), 'candidates': candidates,
            'files': [item for _, _, item in plan]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=Path('C:/dev-artifacts/CityPrompt'))
    parser.add_argument('--public-dir', type=Path)
    parser.add_argument('--candidate', action='append', required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    public = args.public_dir
    if public is None:
        profile = REPO / 'artifacts/local-runtime.json'
        if not profile.is_file():
            parser.error('Provide --public-dir or configure artifacts/local-runtime.json')
        public = Path(json.loads(profile.read_text(encoding='utf-8-sig'))['publicDir'])
    report = install(json.loads(MANIFEST.read_text(encoding='utf-8')), args.source_root, public, args.candidate, apply=args.apply)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'candidates': report['candidates'],
                      'files': len(report['files']), 'public_dir': report['public_dir']}))


if __name__ == '__main__':
    main()
