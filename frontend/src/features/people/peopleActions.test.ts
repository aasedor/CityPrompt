import { describe, expect, it } from 'vitest';
import { PEOPLE_ACTIONS, peopleAction, buildPeopleDirection } from './peopleActions';

describe('saved people actions', () => {
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
