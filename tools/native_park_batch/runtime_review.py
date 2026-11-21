"""Write the exact-variant runtime review for one registered park from the repository template.

    python3 tools/native_park_batch/runtime_review.py <park> <seed package directory>

Every applicable gate stays NOT TESTED: nothing here runs the app. Building, street and
bridge rows are N/A with a reason. Offline evidence is listed separately.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build as batch  # noqa: E402

NA = {
    'B1 ': 'N/A: park, not a building', 'B2 ': 'N/A: park, not a building', 'B3 ': 'N/A: park, not a building',
    'B4 ': 'N/A: park, not a building', 'B5 ': 'N/A: park, not a building',
    'S1 ': 'N/A: park, not a street', 'S2 ': 'N/A: park, not a street', 'S3 ': 'N/A: park, not a street', 'S4 ': 'N/A: park, not a street',
    'Revision-locked fixed-native step pick': 'N/A: building step pick', 'Multiple low steps': 'N/A: building entrances',
    'Interrupted building asset download': 'N/A: building asset', 'Supported storey edit': 'N/A: no storeys',
    'Storey source frame': 'N/A: no storeys', 'Oversized fixed-native candidate': 'N/A: fixed-native building',
    'Repeat placement on both sides of a bent street': 'N/A: building placement', 'Assisted placement and automatic entrance': 'N/A: building entrance',
    'Fixed-native entrance after plot resize': 'N/A: building entrance', 'Prepared level: actual native step pick': 'N/A: building step pick',
    'Proposed off-site public-road endpoint': 'N/A: street endpoint', 'Fixed street bend through ordinary controls': 'N/A: street route',
    'Long repeatable route and exact edit datum': 'N/A: street route', 'Repeated street travel-surface ownership': 'N/A: street surface',
    'X-to-T and T-to-X recovery': 'N/A: street junctions', 'Narrow pedestrian section and bend control retention': 'N/A: street section',
    'Native street production recipe and unchanged Apply': 'N/A: street recipe', 'Finite street draft and connected section replacement': 'N/A: street draft',
    'Angled join and short-arm recovery': 'N/A: street joins',
}
NOTES = {
    'C1 ': 'Exact layout, content revision and model hash registered offline; not checked in the app',
    'C2 ': 'Fixed native assembly at true size; the parcel must be at least the occupied footprint',
    'C3 ': 'Prepared level ground only; record the result on natural ground (expected: guidance to prepare the site)',
    'P1 ': 'Exact native program; offline checks list every module and route',
    'P2 ': 'The assembly owns its ground; check tile and prepared-ground cut-outs around it',
    'P3 ': 'Not run',
    'P4 ': 'Walk the routes from the entrance in the app; offline route rays pass',
}


def write(park, package):
    module = batch.load(park)
    recipe = json.loads((package / 'recipe.json').read_text(encoding='utf-8'))
    registry = json.loads((ROOT / 'frontend/src/data/nativeParks.json').read_text(encoding='utf-8'))
    layout = next(p for p in registry['layouts'] if p['variantId'] == recipe['id'])
    report = json.loads((package / 'geometry-verification.json').read_text(encoding='utf-8'))
    template = (ROOT / 'docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md').read_text(encoding='utf-8')
    values = {
        'Kind': 'park or open space: fixed native assembly (native_park_v2)',
        'Archetype ID and exact variant ID': f"`{module.ARCHETYPE}` / `{recipe['id']}` ({recipe['title']}); layout `{layout['id']}`",
        'Model SHA-256 or procedural recipe ID/revision/hash': f"assembly `{recipe['assembly']['sha256']}`; content revision `{layout['contentRevision']}`",
        'Runtime source commit and integration-checklist version': 'registered on `claude/tender-albattani-fsnp50`; checklist 2026-09-24',
        'Reviewer, date, project URL, viewport/device/input': 'none; not run',
        'Vacant test site, protected reference, disposable test project': 'not set up',
        'Supported plot dimensions, axes/base datum, reshape/repetition behavior': f"native {recipe['dimensions_m'][0]:g} x {recipe['dimensions_m'][1]:g} m; occupied {layout['occupiedWidthM']:g} x {layout['occupiedDepthM']:g} m; `authored_footprint`, never stretched",
        'Supported terrain modes and connection capabilities': 'prepared level ground only; the assembly owns its ground; one entrance at the south edge',
        'Public-realm detail: metric plant height/footprint, paving scale, instance/texture budgets, and native close/aerial evidence': f"no textures; {recipe['triangles']:,} rendered triangles, {recipe['mesh_instances']} mesh instances; renders under `artifacts/park-batch/{park}/` (ignored, reproducible) and `docs/park-batch-1/review.jpg`",
        'Reference-image fidelity: exact image hashes, observed amenity cues, borrowed/inferred details, native before/after views and separately exported reusable amenity modules': f"original concept after `{recipe['reference_views']}.png` and its oblique and plan views; not traced",
        'Asset review status and separate publication/activation status': 'builder visual review only; no independent review; status `pilot`, runtime `not_tested`; publication not authorized',
        'Fresh installation: exact binding/recipe/module seed, byte readback, conflict preservation and disposable DB/bucket evidence': 'offline only: `scripts/register_park_batch1.py` refuses changed content; the generator rebuilds the registered bytes',
        'Evidence manifest location and hashes; durable shared location for delivery': f"`{package.relative_to(ROOT)}` (recipe, assembly, preview, geometry verification)",
        'Mixed-scene project and separate oversized-candidate project, if applicable': 'not set up',
        'Authored storey programme': 'N/A: park',
        'Replacement furniture': 'N/A: no replacement furniture',
        'Vegetation': 'plants from the shared foliage generator, placed as instances; canopies stay inside the site and plant origins stay clear of every route (offline check)',
        'Hardscape trees': 'N/A: no tree wells or grates',
        'Native park seams and raised/cycle access': 'one fixed assembly, no seams; level routes only; offline route rays from the entrance pass',
    }
    out, section = [], None
    for line in template.split('\n'):
        if line.startswith('# Runtime integration review'):
            out.append(f"# Runtime integration review — {module.ARCHETYPE} / {recipe['id']}")
            continue
        if line.startswith('Copy this template into'):
            out += [f"**Nothing in this review was run in the app.** {recipe['title']} was built and checked offline only, so every",
                    'applicable gate and matrix row is NOT TESTED. Building, street and bridge rows are N/A with a reason. Offline',
                    'evidence is listed at the end and is not a runtime pass. It follows `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` and',
                    '`docs/ARCHETYPE_RUNTIME_INTEGRATION.md` (version 2026-09-24).', '']
            section = 'skip'
            continue
        if section == 'skip':
            if not line.startswith('## '):
                continue
            section = None
        if line.startswith('## '):
            section = line[3:].strip()
        if section == 'Candidate and scope' and line.startswith('- '):
            label = line[2:].rstrip()
            label = label[:-1] if label.endswith(':') else label
            key = label if label in values else label.split(':')[0]
            out.append(f'- {key}: {values.get(key, "N/A" if "building" in label.lower() or "street" in label.lower() or "Sports" in label else "not recorded")}')
            continue
        m = re.match(r'^\| ([^|]+?) \| (NOT TESTED) \| (.*)\|$', line)
        if m:
            name = m.group(1)
            reason = next((v for k, v in NA.items() if name.startswith(k)), None)
            line = f'| {name} | N/A | {reason} |' if reason else f"| {name} | NOT TESTED | {next((v for k, v in NOTES.items() if name.startswith(k)), m.group(3).strip())} |"
        out.append(line)
    text = '\n'.join(out).rstrip('\n')
    text += '\n\n## Offline evidence (not runtime passes)\n\n'
    text += '\n'.join(f'- {c}' for c in report['checks'])
    text += f"\n\nGeometry verification: `{report['status']}` for model `{report['model_sha256']}`.\n"
    (package / 'runtime-review.md').write_text(text, encoding='utf-8')
    return text.count('| NOT TESTED |'), text.count('| N/A |'), text.count('| PASS |')


if __name__ == '__main__':
    print(write(sys.argv[1], Path(sys.argv[2]).resolve()))
