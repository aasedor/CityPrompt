import { describe, expect, it } from 'vitest';

import type { SiteZone } from '@/types';

import { collectMasterPlan2DReferences } from './masterPlan2DReferences';

describe('collectMasterPlan2DReferences', () => {
  it('sanitizes elevation-oriented archetype metadata into plan-view guidance', () => {
    const zone: SiteZone = {
      id: 'zone-1',
      project_id: 'project-1',
      name: 'Housing Precinct',
      zone_type: 'building',
      coordinates: [[0, 0], [1, 0], [1, 1], [0, 1]],
      color: '#9b59b6',
      sort_order: 0,
      created_at: '2026-03-10T00:00:00Z',
      updated_at: '2026-03-10T00:00:00Z',
      properties: {
        development_archetype_label: 'Mediterranean Residential',
        development_archetype_id: 'front_day',
        development_archetype_image: {
          id: 'front_day',
          label: 'Mediterranean Residential Front Elevation',
          description: 'Front-facing composition with street-level eye-height camera and restrained perspective distortion.',
          imagePath: '/archetypes/buildings/mediterranean/front_day.png',
          prompt: {
            positive: 'Front-facing or strongly centered composition. Street-level eye-height camera. Restrained perspective distortion.',
          },
          generationTags: ['front elevation', 'facade detail'],
          tags: ['street-level', 'perspective'],
          category: 'Mediterranean Front Elevation',
          subcategory: 'front_day',
          caption: 'Residential front elevation board',
        },
      },
    };

    const [reference] = collectMasterPlan2DReferences([zone]);
    const joined = [
      reference.label,
      reference.metadata.archetype_name,
      reference.metadata.category,
      reference.metadata.subcategory,
      reference.metadata.prompt_text,
      reference.metadata.caption,
      ...(reference.metadata.tags || []),
    ].join(' ').toLowerCase();

    expect(reference.url).toContain('/archetypes/buildings/mediterranean/front_day.png');
    expect(joined).not.toContain('front elevation');
    expect(joined).not.toContain('street-level');
    expect(joined).not.toContain('perspective');
    expect(joined).toContain('roof plan');
    expect(joined).toContain('plan reference');
  });
});