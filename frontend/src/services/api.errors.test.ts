import { describe, expect, it } from 'vitest';
import { getApiErrorMessage } from './api';

describe('student drawing API errors', () => {
  it('does not expose geometry diagnostics in the save-error toast', () => {
    const error = { response: { data: { detail: 'Polygon boundary self-intersects or overlaps; undo the last point and redraw (Self-intersection[-114.05 51.04])' } } };
    expect(getApiErrorMessage(error)).toBe('This outline has crossing or overlapping edges. Move its corners so the edges do not cross.');
  });
  it('preserves unrelated server errors and their useful details', () => {
    expect(getApiErrorMessage({ response: { data: { detail: 'The site boundary must contain every authored zone.' } } }))
      .toBe('The site boundary must contain every authored zone.');
  });
});
