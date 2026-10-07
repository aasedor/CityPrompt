import { describe, expect, it } from 'vitest';
import { DEFAULT_ZONING_PREFERENCES, readZoningPreferences, zoningColor } from './zoningAppearance';

describe('land-use presentation preferences', () => {
  it('starts hidden and ignores retired lot lines, including an old disabled setting', () => {
    for (const value of [null, 'invalid', 'null', '{"lines":true}', '{"labels":false,"districtLines":false}']) {
      expect(readZoningPreferences(value)).toEqual(DEFAULT_ZONING_PREFERENCES);
    }
    expect(readZoningPreferences('{"labels":true,"lines":true}')).toMatchObject({ enabled: true, labels: true, lines: false, fill: false });
    expect(readZoningPreferences('{"districtLines":true}')).toMatchObject({ enabled: true, lines: true, fill: false });
  });
  it('keeps hidden styles and clamps saved opacity', () => {
    expect(readZoningPreferences('{"enabled":false,"labels":false,"districtLines":true,"fill":true,"fillOpacity":0.37}'))
      .toEqual({ enabled: false, labels: false, lines: true, fill: true, fillOpacity: 0.37 });
    expect(readZoningPreferences('{"enabled":true,"fillOpacity":5}').fillOpacity).toBe(1);
    expect(readZoningPreferences('{"enabled":true,"fillOpacity":-1}').fillOpacity).toBe(0);
  });
  it('uses one DC family colour without guessing its land use or confusing park/infrastructure districts', () => {
    expect(zoningColor({ code: 'DC', label: 'DC48Z84' })).toBe(zoningColor({ label: 'DC126D2016' }));
    expect(zoningColor({ label: 'S-SPR' })).not.toBe(zoningColor({ label: 'S-CRI' }));
    expect(zoningColor({ code: 'M-C1', label: 'M-C1 d75' })).toBe(zoningColor({ label: 'M-C1 d100' }));
    expect(zoningColor({ label: 'MU-1' })).not.toBe(zoningColor({ label: 'M-1' }));
  });
});
