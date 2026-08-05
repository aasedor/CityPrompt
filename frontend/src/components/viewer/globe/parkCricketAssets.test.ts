import { describe, expect, it } from 'vitest';

import {
  buildCricketGroundLayout,
  resolveCricketGroundAssetProfile,
} from './parkCricketAssets';
import type { ParkGroundGuide } from './parkGroundProfiles';

const frame = {
  minX: -68.5,
  maxX: 68.5,
  minY: -35.5,
  maxY: 35.5,
  width: 137,
  height: 71,
};

const compactSemanticOval: ParkGroundGuide = {
  kind: 'track',
  x: 0.5,
  y: 0.5,
  width: 0.86,
  height: 0.76,
  color: '#6c925c',
  fitPolicy: 'clip',
};

describe('cricket archetype 3D assets', () => {
  it.each([
    [0, 'Village Green', 'thatched_tudor', 'white_picket'],
    [1, 'Municipal Oval', 'municipal_clubhouse', 'chainlink'],
    [2, 'South Asian Ground', 'maidan_pavilion', 'low_concrete_wall'],
    [3, 'Caribbean Beach Pitch', 'caribbean_grandstand', 'painted_timber'],
  ] as const)('binds variant %s to its own structures', (index, label, pavilion, perimeter) => {
    expect(resolveCricketGroundAssetProfile({ properties: {
      green_space_archetype_id: 'cricket_pitch_oval',
      green_space_selected_variant_id: `cricket_pitch_oval_v${index}`,
    } })).toMatchObject({
      variantIndex: index,
      label,
      pavilionStyle: pavilion,
      perimeterStyle: perimeter,
      suppressGenericMicrodetails: true,
    });
  });

  it('keeps the metric wicket while fitting the oval and pavilion to the pilot parcel', () => {
    const layout = buildCricketGroundLayout(compactSemanticOval, frame);
    expect(layout.pitchLengthM).toBe(22.56);
    expect(layout.pitchWidthM).toBe(3.05);
    expect(layout.wicketOffsetM).toBe(10.06);
    expect(layout.radiusX).toBeCloseTo(58.91, 2);
    expect(layout.radiusY).toBeCloseTo(26.98, 2);
    expect(Math.abs(layout.pavilion.y)).toBeGreaterThan(layout.radiusY);
    expect(layout.pavilion.y + layout.pavilion.depthM / 2).toBeLessThanOrEqual(frame.maxY);
    expect(layout.pavilion.y - layout.pavilion.depthM / 2).toBeGreaterThanOrEqual(frame.minY);
    expect(layout.sightScreenOffsetM).toBeGreaterThan(layout.wicketOffsetM + 7);
    expect(layout.sightScreenOffsetM).toBeLessThan(layout.radiusX);
  });

  it('is deterministic and ignores non-cricket parks', () => {
    expect(buildCricketGroundLayout(compactSemanticOval, frame))
      .toEqual(buildCricketGroundLayout(compactSemanticOval, frame));
    expect(resolveCricketGroundAssetProfile({ properties: {
      green_space_archetype_id: 'neighborhood_park',
    } })).toBeNull();
  });
});
