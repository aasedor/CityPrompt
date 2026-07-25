import { describe, expect, it } from 'vitest';
import {
  getObjectFilteredTerrainHeight,
  hasUsableElevationRelief,
  isPlausibleTerrainAnchor,
  MAX_ANCHOR_DEVIATION_METERS,
  preferLowerGroundAnchor,
  rejectRaisedObjectTop,
  resolveReplacementGroundAnchor,
  shouldFilterObjectTerrainHeight,
} from './globeTerrainUtils';

describe('getObjectFilteredTerrainHeight', () => {
  it('does not preserve a stale low fallback when loaded tiles are materially higher', () => {
    expect(getObjectFilteredTerrainHeight([1121, 1122, 1123, 1134], 1045)).toBe(1121);
  });

  it('keeps a nearby stable fallback to avoid small photogrammetry jitter', () => {
    expect(getObjectFilteredTerrainHeight([1121, 1122, 1123, 1134], 1122)).toBe(1122);
  });
});

describe('hasUsableElevationRelief', () => {
  it('rejects the constant geoid fallback returned when Elevation is unavailable', () => {
    expect(hasUsableElevationRelief([-25, -25, -25])).toBe(false);
  });

  it('accepts a real terrain profile', () => {
    expect(hasUsableElevationRelief([1121.1, 1121.2, 1121.35])).toBe(true);
  });
});

describe('preferLowerGroundAnchor', () => {
  it('uses a lower current probe when a stored click was on a roof', () => {
    expect(preferLowerGroundAnchor(1120, 1131)).toBe(1120);
  });

  it('keeps stored ground when the current probe hits a roof', () => {
    expect(preferLowerGroundAnchor(1131, 1120)).toBe(1120);
  });

  it('keeps stable stored ground within the photogrammetry jitter band', () => {
    expect(preferLowerGroundAnchor(1121.2, 1120)).toBe(1120);
  });
});

describe('rejectRaisedObjectTop', () => {
  it('replaces an interior roof or canopy hit with nearby trusted ground', () => {
    expect(rejectRaisedObjectTop(1138, 1121)).toBe(1121);
  });

  it('keeps a nearby terrain sample and does not erase lower landscape relief', () => {
    expect(rejectRaisedObjectTop(1122.5, 1121)).toBe(1122.5);
    expect(rejectRaisedObjectTop(1114, 1121)).toBe(1114);
  });

  it('falls back cleanly when one of the two samples is unavailable', () => {
    expect(rejectRaisedObjectTop(null, 1121)).toBe(1121);
    expect(rejectRaisedObjectTop(1121, null)).toBe(1121);
  });
});

describe('resolveReplacementGroundAnchor', () => {
  it('does not frame a replacement park on a roof stored by an earlier click', () => {
    expect(resolveReplacementGroundAnchor(1132, 1131, 1120)).toBe(1120);
  });

  it('keeps a stable local ground reading when all references agree', () => {
    expect(resolveReplacementGroundAnchor(1120.6, 1120, 1120.4)).toBe(1120.4);
  });

  it('preserves a lower current sample on a descending site', () => {
    expect(resolveReplacementGroundAnchor(1112, 1120, 1121)).toBe(1112);
  });
});

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

describe('shouldFilterObjectTerrainHeight', () => {
  it('uses bare-ground sampling for every replaceable development surface', () => {
    for (const zoneType of [
      'building',
      'residential',
      'road',
      'street',
      'green_space',
      'park',
      'plaza',
      'parking',
    ]) {
      expect(shouldFilterObjectTerrainHeight(zoneType)).toBe(true);
    }
    expect(shouldFilterObjectTerrainHeight('site_boundary')).toBe(false);
  });
});
