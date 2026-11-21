import { describe, expect, it } from 'vitest';
import { buildStreetViewPrompt } from './useStreetViewRender';

describe('buildStreetViewPrompt', () => {
  it('asks for readable distant buildings without adding haze to the default style', () => {
    const prompt = buildStreetViewPrompt([0, 0], 0, []);

    expect(prompt).toMatch(/distant building outlines and facade details readable/i);
    expect(prompt).not.toMatch(/\bhaz(?:e|y)\b/i);
  });
});
