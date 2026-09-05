import { describe, expect, it } from 'vitest';
import { savedRenderIsSource, savedRenderNeedsReview, savedRenderNotice } from './renderPresentation';

describe('saved presentation labels', () => {
  it('keeps the review warning for legacy compound outcomes', () => {
    const render = { outcome: 'review_required · provider_full_scene_local_repairs' };
    expect(savedRenderNeedsReview(render)).toBe(true);
    expect(savedRenderNotice(render)).toContain('Review building locations');
  });
  it('identifies source fallback from stable fields or legacy metadata', () => {
    for (const render of [
      { outcome: 'review_required', presentation_strategy: 'authoritative_source' },
      { outcome: 'review_required · authoritative_source' },
    ]) {
      expect(savedRenderIsSource(render)).toBe(true);
      expect(savedRenderNotice(render)).toContain('3D source returned');
    }
  });
  it('never labels an original AI attempt as the returned source', () => {
    expect(savedRenderNotice({ variant: 'provider_original', outcome: 'review_required', presentation_strategy: 'authoritative_source' }))
      .toBe('Original AI attempt. It may differ from the design.');
    expect(savedRenderNeedsReview({ outcome: 'accepted' })).toBe(false);
    expect(savedRenderNotice({})).toBe('');
  });
});
