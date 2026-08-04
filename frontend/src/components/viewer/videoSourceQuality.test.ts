import { describe, expect, it } from 'vitest';

import { assessVideoSourceFramePixels } from './videoSourceQuality';

function pixels(width: number, height: number, colorAt: (x: number, y: number) => number[]) {
  const result = new Uint8ClampedArray(width * height * 4);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      const [red, green, blue] = colorAt(x, y);
      result.set([red, green, blue, 255], offset);
    }
  }
  return result;
}

describe('video source quality', () => {
  it('rejects a blank or clipped foreground frame', () => {
    const frame = pixels(24, 16, () => [220, 220, 220]);
    expect(assessVideoSourceFramePixels(frame, 24, 16)).toMatchObject({
      edgeRatio: 0,
      dominantColorRatio: 1,
      usable: false,
    });
  });

  it('accepts a structured architectural frame with varied edges and colours', () => {
    const frame = pixels(24, 16, (x, y) => [
      (x * 47 + y * 13) % 256,
      (x * 17 + y * 61) % 256,
      (x * 83 + y * 29) % 256,
    ]);
    const quality = assessVideoSourceFramePixels(frame, 24, 16);
    expect(quality.edgeRatio).toBeGreaterThan(0.2);
    expect(quality.dominantColorRatio).toBeLessThan(0.47);
    expect(quality.usable).toBe(true);
  });
});
