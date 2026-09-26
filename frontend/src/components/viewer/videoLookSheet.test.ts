import { describe, expect, it } from 'vitest';

import { DIRECT_3D_STYLE_IDS } from './globe/useDirect3DRender';
import {
  DEFAULT_VIDEO_LOOK,
  VIDEO_LOOK_GROUPS,
  VIDEO_LOOK_STYLES,
  VIDEO_STUDENT_NOTE_MAX,
  isVideoLookStyle,
  sanitizeStudentNote,
  videoLookLabel,
} from './videoLookSheet';

describe('video look sheet', () => {
  it('offers ten unique looks with the photorealistic default', () => {
    const ids = VIDEO_LOOK_STYLES.map((option) => option.id);
    expect(ids).toHaveLength(10);
    expect(new Set(ids).size).toBe(10);
    expect(ids[0]).toBe(DEFAULT_VIDEO_LOOK);
    expect(isVideoLookStyle('night')).toBe(true);
    expect(isVideoLookStyle('neon')).toBe(false);
    for (const option of VIDEO_LOOK_STYLES) {
      expect(VIDEO_LOOK_GROUPS).toContain(option.group);
    }
  });

  it('maps every look to an existing Direct 3D image style for the anchor frame', () => {
    for (const option of VIDEO_LOOK_STYLES) {
      expect(option.imageStyle === null || DIRECT_3D_STYLE_IDS.includes(option.imageStyle)).toBe(true);
    }
  });

  it('labels looks for history rows', () => {
    expect(videoLookLabel('after_rain')).toBe('After rain');
    expect(videoLookLabel('unknown_look')).toBe('unknown look');
    expect(videoLookLabel(null)).toBe('');
  });

  it('sanitizes the student note exactly like the server', () => {
    expect(sanitizeStudentNote('  keep the\n\n  plaza   busy ')).toBe('keep the plaza busy.');
    expect(sanitizeStudentNote('Already ends?')).toBe('Already ends?');
    expect(sanitizeStudentNote('')).toBe('');
    expect(sanitizeStudentNote(undefined)).toBe('');
    const long = sanitizeStudentNote('word '.repeat(100));
    expect(long.length).toBeLessThanOrEqual(VIDEO_STUDENT_NOTE_MAX + 1);
    expect(long.endsWith('.')).toBe(true);
  });
});
