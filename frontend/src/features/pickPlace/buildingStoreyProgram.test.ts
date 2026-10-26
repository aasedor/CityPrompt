import { describe, expect, it } from 'vitest';
import { placeAsset, placementProperties, assetForZone } from './catalogue';
import { storeyProgramHeight, storeyProgramSupports } from './buildingStoreyProgram';
import { withStoreyMetadata } from './assetRegistry';

const tower = placeAsset('clay_vancouver_balcony_podium_tower');
const program = tower.storeyProgram!;

describe('authored building storey programs', () => {
  it('offers the finite Brick Podium pilot while preserving native 13-storey saved scenes', () => {
    const brick = placeAsset('claude_trial_brick_podium_condo_tower');
    expect(brick.storeyProgram?.mode).toBe('repeat_authored_floor');
    expect(brick.storeyProgram).toMatchObject({ nativeStoreys: 13, minStoreys: 13, maxStoreys: 40,
      recommendedMinStoreys: 15, recommendedMaxStoreys: 40 });
    for (const [floors, height] of [[13, 50.1], [15, 56.1], [25, 86.1], [40, 131.1]]) {
      expect(storeyProgramHeight(brick.storeyProgram!, floors)).toBe(height);
      expect(assetForZone({ properties: { ...placementProperties(brick), floor_count: floors, floors,
        height, height_m: height, development_height_override_m: height } })?.id).toBe(brick.id);
    }
    expect(storeyProgramSupports(brick.storeyProgram!, 12, 47.1)).toBe(false);
    expect(storeyProgramSupports(brick.storeyProgram!, 41, 134.1)).toBe(false);
  });
  it('does not expose the Brick Podium pilot in a production registry', () => {
    const brick = placeAsset('claude_trial_brick_podium_condo_tower');
    const { storeyProgram: _pilot, ...source } = brick;
    const production = withStoreyMetadata(source, false);
    expect(production.kind === 'object' && production.storeyProgram?.mode).toBe('fixed_authored_assembly');
  });
  it('keeps fixed podium and roof heights while repeating full storeys', () => {
    expect(storeyProgramHeight(program, 16)).toBe(58.8);
    expect(storeyProgramHeight(program, 25)).toBe(87.6);
    expect(storeyProgramHeight(program, 40)).toBe(135.6);
  });

  it.each([
    ['trial_postwar_bungalow', 6.36, 9.29],
    ['trial_edwardian_foursquare', 7.66, 10.81],
    ['validation_clapboard_north_end', 7.34, 10.48],
  ] as const)('selects complete one- and two-storey assemblies for %s', (assetId, oneStorey, twoStoreys) => {
    const houseProgram = placeAsset(assetId).storeyProgram!;
    expect(houseProgram.mode).toBe('select_authored_assembly');
    expect(storeyProgramHeight(houseProgram, 1)).toBe(oneStorey);
    expect(storeyProgramHeight(houseProgram, 2)).toBe(twoStoreys);
    expect(storeyProgramSupports(houseProgram, 0, oneStorey)).toBe(false);
    expect(storeyProgramSupports(houseProgram, 3, twoStoreys)).toBe(false);
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
