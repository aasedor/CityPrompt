import { describe, expect, it } from 'vitest';
import { estimateCurrentViewRenderCalls } from './renderCost';

describe('current-view render cost', () => {
  it('counts one image request per A/B preview', () => {
    expect(estimateCurrentViewRenderCalls(2, false)).toBe(2);
  });

  it('adds one shared restyle request for high-fidelity artistic output', () => {
    expect(estimateCurrentViewRenderCalls(2, true)).toBe(3);
  });

  it('normalizes invalid and fractional preview counts safely', () => {
    expect(estimateCurrentViewRenderCalls(Number.POSITIVE_INFINITY, true)).toBe(0);
    expect(estimateCurrentViewRenderCalls(-3, true)).toBe(0);
    expect(estimateCurrentViewRenderCalls(2.9, false)).toBe(2);
  });
});
