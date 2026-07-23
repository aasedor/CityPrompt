import { describe, expect, it } from 'vitest';

import {
  DIRECT_3D_CALL_DESCRIPTION,
  DIRECT_3D_PIPELINE_DESCRIPTION,
  DIRECT_3D_SCOPE_DESCRIPTION,
  isRenderStyleDisabled,
  shouldAutoSaveDirect3D,
  STYLES,
  STYLE_GROUPS,
} from './GlobeAIRenderPanel';
import { GLOBE_STYLE_PROMPTS } from './useGlobeAIRender';

describe('Globe AI render panel Direct 3D styles', () => {
  it('exposes every Classic aesthetic as a selectable Direct style', () => {
    expect(STYLES).toHaveLength(22);
    expect(new Set(STYLES.map((style) => style.id)))
      .toEqual(new Set(Object.keys(GLOBE_STYLE_PROMPTS)));

    for (const style of STYLES) {
      expect(isRenderStyleDisabled('direct3d', style.id, false), style.id).toBe(false);
    }
  });

  it('preserves the existing Classic Development gate', () => {
    for (const style of STYLES) {
      expect(isRenderStyleDisabled('classic', style.id, false), style.id)
        .toBe(style.id === 'development');
      expect(isRenderStyleDisabled('classic', style.id, true), style.id).toBe(false);
    }
  });

  it('groups all style buttons exactly once', () => {
    const groupedIds = STYLE_GROUPS.flatMap((group) => [...group.ids]);
    expect(groupedIds).toHaveLength(22);
    expect(new Set(groupedIds).size).toBe(22);
    expect(new Set(groupedIds)).toEqual(new Set(STYLES.map((style) => style.id)));
  });

  it('explains inventory locking, fidelity and review before spend', () => {
    expect(DIRECT_3D_PIPELINE_DESCRIPTION).toContain('inventory-locked');
    expect(DIRECT_3D_PIPELINE_DESCRIPTION).toContain('fidelity');
    expect(DIRECT_3D_SCOPE_DESCRIPTION).toContain('preserve authored structure');
    expect(DIRECT_3D_SCOPE_DESCRIPTION).toContain('review before saving');
    expect(DIRECT_3D_CALL_DESCRIPTION).toContain('1 image call');
    expect(DIRECT_3D_CALL_DESCRIPTION).toContain('never auto-saved');
  });

  it('auto-saves only server-accepted Direct results', () => {
    expect(shouldAutoSaveDirect3D('accepted')).toBe(true);
    expect(shouldAutoSaveDirect3D('review_required')).toBe(false);
  });
});
