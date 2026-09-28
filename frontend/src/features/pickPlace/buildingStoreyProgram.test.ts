import { describe, expect, it } from 'vitest';
import { placeAsset, placementProperties, assetForZone } from './catalogue';
import { storeyProgramHeight, storeyProgramSupports } from './buildingStoreyProgram';

const tower = placeAsset('clay_vancouver_balcony_podium_tower');
const program = tower.storeyProgram!;

describe('authored building storey programs', () => {
  it('keeps fixed podium and roof heights while repeating full storeys', () => {
    expect(storeyProgramHeight(program, 16)).toBe(58.8);
    expect(storeyProgramHeight(program, 25)).toBe(87.6);
    expect(storeyProgramHeight(program, 40)).toBe(135.6);
  });

  it('accepts only the finite storey range and its authored height', () => {
    expect(storeyProgramSupports(program, 25, 87.6)).toBe(true);
    expect(storeyProgramSupports(program, 40, 135.6)).toBe(true);
    expect(storeyProgramSupports(program, 41, 138.8)).toBe(false);
    expect(storeyProgramSupports(program, 25, 100)).toBe(false);
  });

  it('keeps the exact catalogue binding for supported saved edits', () => {
    const supported = { ...placementProperties(tower), floors: 25, floor_count: 25,
      height: 87.6, height_m: 87.6, development_height_override_m: 87.6 };
    expect(assetForZone({ properties: supported })?.id).toBe(tower.id);
    expect(assetForZone({ properties: { ...supported, height_m: 100, development_height_override_m: 100 } })?.id)
      .toBe('canonical-building:vancouverism_tower_podium:vancouverism_classic');
  });
});
