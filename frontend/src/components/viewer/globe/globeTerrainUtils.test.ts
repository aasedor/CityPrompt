import { describe, expect, it } from 'vitest';
import { isPlausibleTerrainAnchor, MAX_ANCHOR_DEVIATION_METERS } from './globeTerrainUtils';

describe('isPlausibleTerrainAnchor', () => {
  it('rejects the unrefined-root-tile trap (~29km below the surface)', () => {
    // Values measured live 2026-07-11: first-frame raycasts against Google's
    // root tiles returned ≈ -28,090m at Calgary (true surface ≈ +1,145m).
    expect(isPlausibleTerrainAnchor(-28090, 1045)).toBe(false);
  });

  it('accepts a sample near the reference', () => {
    expect(isPlausibleTerrainAnchor(1145, 1045)).toBe(true);
    expect(isPlausibleTerrainAnchor(1045 - MAX_ANCHOR_DEVIATION_METERS, 1045)).toBe(true);
  });

  it('rejects just outside the band', () => {
    expect(isPlausibleTerrainAnchor(1045 + MAX_ANCHOR_DEVIATION_METERS + 1, 1045)).toBe(false);
  });

  it('accepts any finite sample when no reference exists', () => {
    expect(isPlausibleTerrainAnchor(-28090, null)).toBe(true);
    expect(isPlausibleTerrainAnchor(-28090, Number.NaN)).toBe(true);
  });

  it('rejects non-finite samples', () => {
    expect(isPlausibleTerrainAnchor(null, 1045)).toBe(false);
    expect(isPlausibleTerrainAnchor(Number.NaN, 1045)).toBe(false);
    expect(isPlausibleTerrainAnchor(undefined, 1045)).toBe(false);
  });
});
