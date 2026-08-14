import { describe, expect, it } from 'vitest';

import {
  hasScenarioPlanCompleted,
  snapshotScenarioPlanStatuses,
} from './siteIntelligencePlanStatus';

function scenario(id: string, status?: string) {
  return {
    id,
    payload: status ? { plan: { status } } : {},
  };
}

describe('site intelligence plan status transitions', () => {
  it('detects queued-to-complete for the same scenario ID', () => {
    const previous = snapshotScenarioPlanStatuses([
      scenario('economic', 'queued'),
      scenario('balanced', 'complete'),
    ]);
    const current = snapshotScenarioPlanStatuses([
      scenario('economic', 'complete'),
      scenario('balanced', 'complete'),
    ]);

    expect(hasScenarioPlanCompleted(previous, current)).toBe(true);
  });

  it('does not mistake reordering for a completion transition', () => {
    const previous = snapshotScenarioPlanStatuses([
      scenario('economic', 'complete'),
      scenario('balanced', 'drawing'),
    ]);
    const current = snapshotScenarioPlanStatuses([
      scenario('balanced', 'drawing'),
      scenario('economic', 'complete'),
    ]);

    expect(hasScenarioPlanCompleted(previous, current)).toBe(false);
  });

  it('does not mistake insertion or deletion for a completion transition', () => {
    const previous = snapshotScenarioPlanStatuses([
      scenario('economic', 'complete'),
      scenario('deleted', 'drawing'),
    ]);
    const current = snapshotScenarioPlanStatuses([
      scenario('inserted', 'complete'),
      scenario('economic', 'complete'),
    ]);

    expect(hasScenarioPlanCompleted(previous, current)).toBe(false);
  });

  it('uses the first observation as a baseline', () => {
    const current = snapshotScenarioPlanStatuses([scenario('economic', 'complete')]);

    expect(hasScenarioPlanCompleted(null, current)).toBe(false);
  });
});
