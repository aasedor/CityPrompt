import { describe, expect, it } from 'vitest';
import { deriveCityPromptWorkflow } from '@/features/workflow/cityPromptWorkflow';
import type { SiteZone } from '@/types';
import { defaultStudentStep } from './studentNavigation';

function zone(zone_type: SiteZone['zone_type']): SiteZone {
  return { id: 'older-zone', project_id: 'older-project', zone_type, coordinates: [[0, 0], [1, 0], [1, 1]], properties: {} } as SiteZone;
}

describe('opening saved designs', () => {
  it('starts an empty project at site selection', () => {
    expect(defaultStudentStep(deriveCityPromptWorkflow([]))).toBe('site');
  });
  it.each(['building', 'road', 'green_space', 'site_boundary'] as const)('opens an older %s project in Design without requiring a new boundary', (kind) => {
    expect(defaultStudentStep(deriveCityPromptWorkflow([zone(kind)]))).toBe('design');
  });
});
