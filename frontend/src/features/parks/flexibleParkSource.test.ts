import { expect, it } from 'vitest';
import availability from '@/data/archetypeReferenceAvailability.json';
import sources from '@/data/openSpaceArchetypes.json';
import { OPENSPACE_AESTHETIC_OPTIONS_V2 } from '@/components/viewer/aestheticCatalog';

it('has the authored references for the two flexible park programmes', () => {
  expect(availability.openSpaceIds).toContain('urban_pocket_park');
  expect(sources.archetypes.some(source => source.id === 'urban_pocket_park')).toBe(true);
  expect(OPENSPACE_AESTHETIC_OPTIONS_V2.some(option => option.id === 'urban_pocket_park')).toBe(true);
  expect(OPENSPACE_AESTHETIC_OPTIONS_V2.some(option => option.id === 'linear_park_greenway')).toBe(true);
});
