import { describe, expect, it } from 'vitest';
import { selectRenderLabelIds, type RenderLabelCandidate } from './renderLabelBudget';

const candidate = (
  id: string,
  groupKey: string,
  priority = 0,
  area = 100,
): RenderLabelCandidate => ({ id, groupKey, priority, area });

describe('render label budget', () => {
  it('keeps every label in a small scene', () => {
    expect([...selectRenderLabelIds([
      candidate('a', 'housing'),
      candidate('b', 'park'),
      candidate('c', 'street'),
    ], 8)].sort()).toEqual(['a', 'b', 'c']);
  });

  it('represents each program group before repeating a group', () => {
    const selected = selectRenderLabelIds([
      candidate('housing-large', 'housing', 0, 500),
      candidate('housing-small', 'housing', 0, 300),
      candidate('park', 'park', 0, 100),
    ], 2);

    expect(selected).toEqual(new Set(['housing-large', 'park']));
  });

  it('prioritizes important groups when representatives exceed the cap', () => {
    const selected = selectRenderLabelIds([
      candidate('housing', 'housing', 1, 900),
      candidate('park', 'park', 100, 100),
      candidate('connector', 'connector', 1_000, 20),
    ], 2);

    expect(selected).toEqual(new Set(['connector', 'park']));
  });

  it('is deterministic, hard-capped, and handles invalid limits', () => {
    const input = [
      candidate('c', 'housing', 0, 100),
      candidate('a', 'housing', 0, 100),
      candidate('b', 'housing', 0, 100),
    ];

    expect(selectRenderLabelIds(input, 2)).toEqual(new Set(['a', 'b']));
    expect(selectRenderLabelIds(input, 0).size).toBe(0);
    expect(selectRenderLabelIds(input, Number.NaN).size).toBe(0);
  });
});
