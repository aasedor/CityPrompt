"""Bind October teaching programmes to installed, exact model revisions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def sync():
    library = read(ROOT/'seed/model-library/rlasm-architectural-clay/library.json')
    installed = {e['variant_id']: e for e in library['entries']}
    path = ROOT/'frontend/src/features/zoningCatalogue/buildingPrograms.json'
    programs = read(path)
    basics = {
        'neoclassical_brick_headquarters': (['Office'], 'Professional and administrative office, with no medical, retail or production use assumed.'),
        'admin_faculty_brick_bronze_fins': (['Office'], 'Faculty administrative offices and meeting rooms; no classroom or laboratory use assumed.'),
        'strip_single_storey_classic': (['Retail and Consumer Service'], 'Small retail and personal-service tenancies; restaurants and vehicle uses require separate classification.'),
        'factory_sawtooth_roof': (['General Industrial – Light'], 'Teaching programme: enclosed light fabrication. No external processing, hazardous materials or off-site nuisance assumed.'),
        'industrial_gabled_metal_shed': (['General Industrial – Light'], 'Teaching programme: enclosed workshop with ancillary storage and office. The operator and process must satisfy the Light definition.'),
        'industrial_tilt_up_concrete': (['General Industrial – Light'], 'Teaching programme: enclosed light production with ancillary offices. No separate retail or public-service occupancy assumed.'),
        'warehouse_tilt_wall_mega': (['General Industrial – Light'], 'Teaching programme: enclosed warehousing and distribution with ancillary administration. External storage or transport-terminal operations need separate review.'),
        'ecole-republicaine-provincial-brick': (['School Authority – School'], 'Teaching programme: school operated by a school authority; a private school is a different defined use.'),
        'rndsqr_townhome_brick_contextual': (['Rowhouse Building', 'Townhouse', 'Multi-Residential Development'], 'Unstacked homes with individual entrances and internal stairs; parcel arrangement determines the applicable defined use.'),
        'rndsqr_townhome_scandinavian_peaks': (['Rowhouse Building', 'Townhouse', 'Multi-Residential Development'], 'Unstacked gabled homes with individual entrances and internal stairs; parcel arrangement determines the applicable defined use.'),
    }
    for variant, (uses, assumption) in basics.items():
        if variant not in installed: continue
        entry = installed[variant]
        programs[variant] = dict(revision=entry['candidate'], components=[uses], assumption=assumption,
            classification=dict(basis='teaching', evidence='Exact reviewed October model with the explicitly stated classroom occupancy.'),
            conditions=['Changing the occupancy requires a new use check. Setbacks, density, servicing, parking, access and measured bylaw height remain site requirements.'])
    for module in ('catalogue_original_five', 'catalogue_coverage_five', 'catalogue_affordable_five'):
        source = ROOT/f'tools/{module}/designs.json'
        if not source.exists(): continue
        for design in read(source)['candidates']:
            variant = design['variant']
            if variant not in installed: continue
            research = design['zoning_research']; groups = {}; district_review = {}
            for route in research['district_candidates']:
                district = route['district']
                uses = groups.setdefault(district, [[]])[0]
                use = route.get('defined_use') or route.get('use') or research.get('use_label')
                if use and use not in uses: uses.append(use)
                alternative = route.get('alternative_discretionary_route')
                if alternative and alternative['use'] not in uses: uses.append(alternative['use'])
                if route.get('fit_status') not in (None, 'candidate_site_review_required'):
                    district_review[district] = ' '.join(route['conditions'])
            conditions = research.get('program_conditions', research.get('general_conditions', []))
            programs[variant] = dict(revision=installed[variant]['candidate'], components=[design['uses']],
                assumption=design['program'], classification=dict(basis='teaching', evidence=f'{source.relative_to(ROOT).as_posix()}: {design["id"]}; original authored programme and researched use routes.'),
                conditions=conditions, districtUseGroups=groups)
            if district_review: programs[variant]['districtReview'] = district_review
    save(path, programs)

if __name__ == '__main__': sync()
