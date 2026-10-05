import { describe, expect, it } from 'vitest';
import { loadRileyPolicy } from './rileyPolicy';
import { RILEY_DESIGNATIONS, rileyDesignation } from './rileyDesignations';

describe('Riley designation explanations', () => {
  it('provides a colour-matched explanation and source for every polygon', async () => {
    const data = await loadRileyPolicy();
    expect(RILEY_DESIGNATIONS).toHaveLength(9);
    const references: Record<string, [string, number]> = {
      'Neighbourhood Commercial': ['2.2.1.2',25], 'Neighbourhood Flex': ['2.2.1.3',26],
      'Neighbourhood Connector': ['2.2.1.5',28], 'Neighbourhood Local': ['2.2.1.6',29],
      'Commercial Centre': ['2.2.2.1',32], 'Natural Areas': ['2.2.3.1',35],
      'Parks and Open Space': ['2.2.3.2',36], 'City Civic and Recreation': ['2.2.3.3',37],
      'Private Institutional and Recreation': ['2.2.3.4',38],
    };
    for (const feature of data.features) {
      const designation = rileyDesignation(feature.properties.category)!;
      expect(designation).toBeDefined();
      expect(designation.color).toBe(feature.properties.color);
      expect([designation.section,designation.page]).toEqual(references[designation.name]);
      expect(designation.pdfPage).toBe(designation.page+5);
      expect(designation.summary.length).toBeGreaterThan(100);
      expect(designation.considerations).toHaveLength(3);
    }
    expect(rileyDesignation('R-CG')).toBeUndefined();
  });
  it('keeps conditional Local / Limited Scale and Connector business guidance explicit', () => {
    expect(rileyDesignation('Neighbourhood Local')!.considerations.join(' ')).toMatch(/If the site also has the Limited Scale modifier/);
    expect(rileyDesignation('Neighbourhood Connector')!.considerations.join(' ')).toMatch(/beyond work-live units and home businesses/);
    expect(rileyDesignation('Neighbourhood Connector')!.considerations.join(' ')).toMatch(/corner parcels on collector/);
  });
});
