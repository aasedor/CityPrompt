import { describe, expect, it } from 'vitest';
import { PEOPLE_ACTIONS, peopleAction, buildPeopleDirection, withPeopleDirection } from './peopleActions';

describe('saved people actions', () => {
  it('keeps a legal 256-person inclusive crowd below the video brief limit', () => {
    const direction = buildPeopleDirection(Array.from({ length: 256 }, (_, i) => ({
      id: `actor-${i}`, variant: 'people-inclusive-white-cane',
    })));
    expect(direction.length).toBeLessThan(4000);
    expect(direction).toContain('256 standing');
    expect(direction).toContain('256 × people-inclusive-white-cane');
    expect(direction).not.toContain('actor-255');
  });
  it('replaces only the generated People suffix when recovering a guide', () => {
    const before = buildPeopleDirection([{ variant: 'people-inclusive-white-cane' }]);
    const after = buildPeopleDirection([{ variant: 'people-inclusive-manual-wheelchair' }]);
    const brief = withPeopleDirection('Preserve the buildings and the source camera.', before);
    expect(withPeopleDirection(brief, before)).toBe(brief);
    expect(withPeopleDirection(brief, after)).toBe(`Preserve the buildings and the source camera.\n${after}`);
    expect(withPeopleDirection(brief, '')).toBe('Preserve the buildings and the source camera.');
  });
  it('offers fifteen stable actions and defaults legacy people to standing', () => {
    expect(PEOPLE_ACTIONS).toHaveLength(15);
    expect(new Set(PEOPLE_ACTIONS.map(action => action.id)).size).toBe(15);
    expect(peopleAction(undefined).id).toBe('standing');
    expect(() => peopleAction('flying')).toThrow();
  });
  it('describes only authored actors without turning ordinary props into people', () => {
    const direction = buildPeopleDirection([
      { id: 'one', variant: 'people-pilot-commuter', people_action: 'reading' },
      { id: 'two', variant: 'people-pilot-neighbour', people_action: 'sitting' },
      { id: 'bench', variant: 'timber-bench' },
    ]);
    expect(direction).toContain('reading');
    expect(direction).toContain('sitting');
    expect(direction).toContain('visible');
    expect(direction).not.toContain('bench');
    expect(buildPeopleDirection([])).toBe('');
  });
});
