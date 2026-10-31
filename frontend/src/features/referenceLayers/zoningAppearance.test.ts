import { describe, expect, it } from 'vitest';
import { DEFAULT_ZONING_PREFERENCES, readZoningPreferences, zoningColor } from './zoningAppearance';

describe('land-use presentation preferences', () => {
  it.each([
    ['R-CG', '#fff7da'], ['M-CG d72', '#ffefa9'], ['M-H2 f4.0 h30', '#ffe672'],
    ['C-COR1', '#f9bca9'], ['CR20-C20/R20', '#f58c7d'], ['CC-X', '#f9bca9'],
    ['CC-MH', '#ffe672'], ['CC-MHX', '#ffe672'], ['CC-EIR', '#e99aad'],
    ['MU-2 f4.0 h24', '#e99aad'], ['I-G', '#8d8d8d'], ['S-TUC', '#cecece'],
    ['S-SPR', '#d3e6bd'], ['S-R', '#d3e6bd'], ['S-CI', '#acbcd0'],
    ['S-CRI', '#cbedff'], ['S-FUD', '#f1f7ed'], ['DC121Z86', '#ceb2cd'],
  ])('uses the published Calgary class colour for %s', (label, color) => {
    expect(zoningColor({ label })).toBe(color);
  });
  it('uses the published code even when the label has a caption and keeps unknown codes neutral', () => {
    expect(zoningColor({ code: 'CR20-C20/R20', label: 'Downtown core' })).toBe('#f58c7d');
    expect(zoningColor({ label: 'R-CG-invented' })).toBe('#c9c9c9');
  });
  it('starts hidden and ignores retired lot lines, including an old disabled setting', () => {
    for (const value of [null, 'invalid', 'null', '{"lines":true}', '{"labels":false,"districtLines":false}']) {
      expect(readZoningPreferences(value)).toEqual(DEFAULT_ZONING_PREFERENCES);
    }
    expect(readZoningPreferences('{"labels":true,"lines":true}')).toMatchObject({ enabled: true, labels: true, lines: false, fill: false });
    expect(readZoningPreferences('{"districtLines":true}')).toMatchObject({ enabled: true, lines: true, fill: false });
  });
  it('keeps hidden styles and clamps saved opacity', () => {
    expect(readZoningPreferences('{"enabled":false,"labels":false,"districtLines":true,"fill":true,"fillOpacity":0.37}'))
      .toEqual({ enabled: false, clipToSite: false, labels: false, lines: true, fill: true, fillOpacity: 0.37 });
    expect(readZoningPreferences('{"enabled":true,"fillOpacity":5}').fillOpacity).toBe(1);
    expect(readZoningPreferences('{"enabled":true,"fillOpacity":-1}').fillOpacity).toBe(0);
  });
  it('defaults site clipping off for existing settings and restores explicit choices', () => {
    expect(readZoningPreferences('{"enabled":true}').clipToSite).toBe(false);
    expect(readZoningPreferences('{"enabled":true,"clipToSite":true}').clipToSite).toBe(true);
  });
  it('uses one DC family colour without guessing its land use or confusing park/infrastructure districts', () => {
    expect(zoningColor({ code: 'DC', label: 'DC48Z84' })).toBe(zoningColor({ label: 'DC126D2016' }));
    expect(zoningColor({ label: 'S-SPR' })).not.toBe(zoningColor({ label: 'S-CRI' }));
    expect(zoningColor({ code: 'M-C1', label: 'M-C1 d75' })).toBe(zoningColor({ label: 'M-C1 d100' }));
    expect(zoningColor({ label: 'MU-1' })).not.toBe(zoningColor({ label: 'M-1' }));
  });
});
