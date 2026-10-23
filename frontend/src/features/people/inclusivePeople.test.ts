import { describe, expect, it, vi } from 'vitest';
vi.mock('./inclusivePeopleCatalogue.json', async () => ({ default: (await import('./testFixtures/inclusivePeople')).inclusivePeople }));
import { detailAsset, searchDetails } from '@/features/parks/detailCatalogue';
import { buildPeopleDirection, peopleActionForAsset, peopleActionsForAsset, isPeopleAsset } from './peopleActions';

describe('fixed people representation', () => {
  it('finds a static wheelchair user in People without opting into the rig loader', () => {
    const asset = detailAsset('people-inclusive-manual-wheelchair');
    expect(searchDetails('wheelchair', 'People').map(item => item.id)).toContain(asset?.id);
    expect(asset?.people).toBeUndefined();
    expect(isPeopleAsset(asset)).toBe(true);
    expect(peopleActionForAsset(asset).id).toBe('sitting');
    expect(peopleActionsForAsset(asset).map(action => action.id)).toEqual(['sitting']);
    expect(() => peopleActionForAsset(asset, 'walking')).toThrow(/supported|fixed/i);
  });
  it('counts the people in a family and preserves the aid/group identity in render directions', () => {
    const direction = buildPeopleDirection([
      {variant: 'people-inclusive-family-parent-child'},
      {variant: 'people-inclusive-manual-wheelchair'},
      {variant: 'people-pilot-commuter', people_action: 'reading'},
      {variant: 'timber-bench'},
    ]);
    expect(direction).toContain('2 people');
    expect(direction).toContain('1 sitting');
    expect(direction).toContain('1 reading');
    expect(direction).toMatch(/parent and child/i);
    expect(direction).toMatch(/manual wheelchair/i);
    expect(direction).toMatch(/preserve.*aid|aid.*preserve/i);
    expect(() => buildPeopleDirection([{variant: 'people-inclusive-manual-wheelchair', people_action: 'running'}])).toThrow();
  });
  it('counts the infant without describing the infant as standing', () => {
    const direction = buildPeopleDirection([{variant: 'people-inclusive-family-stroller'}]);
    expect(direction).toContain('2 people');
    expect(direction).toContain('with the adult standing');
    expect(direction).not.toContain('2 standing');
  });
});
