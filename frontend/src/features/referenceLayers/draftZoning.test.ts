import { describe, expect, it } from 'vitest';
import { readCalgaryDistrict } from './calgaryDistricts';
import { DRAFT_DISTRICTS, DRAFT_ZONING_SOURCE, draftDistrictInfo } from './draftZoning';
import { studyMetadata, studyPreviewLayer, studySvg, studyZones } from './zoningStudy';
import { rulesForZone } from '../zoningCatalogue/matching';

describe('May 2025 draft zoning namespace', () => {
  it('keeps reused codes distinct from current bylaw rules', () => {
    const district = readCalgaryDistrict({ designation: 'MU-1', bylaw: 'draft-2025' });
    expect(district?.bylaw).toBe('draft-2025');
    expect(rulesForZone({ id: 'draft', label: 'MU-1', source: 'Draft', district })).toBeNull();
    expect(rulesForZone({ id: 'current', label: 'MU-1', source: 'City', district: { designation: 'MU-1' } })).not.toBeNull();
    expect(readCalgaryDistrict({ designation: 'MU-1', bylaw: 'unknown' })).toBeUndefined();
  });
  it('provides sourced choices and a separate round-trippable layer', () => {
    expect(DRAFT_DISTRICTS).toHaveLength(27);
    expect(new Set(DRAFT_DISTRICTS.map(d => d.designation)).size).toBe(27);
    expect(draftDistrictInfo('MU-1')?.source).toBe(`${DRAFT_ZONING_SOURCE}#page=64`);
    const boundary: [number, number][] = [[-114.12,51.01],[-114.119,51.01],[-114.119,51.011],[-114.12,51.011]];
    const zones = [{ id: 'one', label: 'MU-1', color: '#eca88d', origin: 'student' as const,
      district: DRAFT_DISTRICTS.find(d => d.designation === 'MU-1')!, rings: [[...boundary,boundary[0]]] }];
    const layer = studyPreviewLayer(zones, boundary, 'draft-2025', .4);
    expect(studyMetadata(layer)?.condition).toBe('draft-2025');
    expect(studyZones(layer)[0].district?.bylaw).toBe('draft-2025');
    const svg = studySvg(zones,boundary,'Student proposal','draft-2025');
    expect(svg).toContain(DRAFT_ZONING_SOURCE);
    expect(svg).toContain('May 2025');
    expect(svg).toContain('illustrative');
  });
});
