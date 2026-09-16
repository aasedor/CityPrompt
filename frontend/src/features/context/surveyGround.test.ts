import { expect, it } from 'vitest';
import { surveyFixture, surveySite } from './surveyGround.testFixtures';
import { readSurveyGround, surveyGroundState } from './surveyGround';
import { captureSharedGround } from '@/components/viewer/globe/sharedGroundCapture';

it('reuses the common triangle sampler at negative ellipsoid heights without pretending to measure Google twice', () => {
  const state = surveyGroundState(surveySite())!;
  expect(state.status).toBe('ready'); expect(state.snapshot?.source).toBe('classified_lidar');
  expect(state.snapshot?.quality.stablePasses).toBe(0);
  expect(state.heightAt(-122.42695, 37.75905)).toBeCloseTo(-3, 6);
  expect(state.heightAt(-122.425, 37.75905)).toBeNull();
  expect(() => captureSharedGround(state)).toThrow(/survey pilot/);
});

it('preserves ground across unrelated revisions and binds changed source measurements', () => {
  const site = surveySite(), original = surveyGroundState(site)!;
  expect(surveyGroundState({ ...site, updated_at: 'later' })!.revision).toBe(original.revision);
  expect(surveyGroundState(surveySite({ ...surveyFixture, heights: surveyFixture.heights.map(h => h + .1) }))!.revision).not.toBe(original.revision);
});

it('fails closed for malformed, unsupported, incomplete or out-of-domain survey data', () => {
  for (const data of [null, {}, { ...surveyFixture, verticalReference: 'NAVD88' },
    { ...surveyFixture, heights: [1] }, { ...surveyFixture, heights: Array(1300).fill(1) },
    { ...surveyFixture, grid: { ...surveyFixture.grid, stepLat: 0 } },
    { ...surveyFixture, grid: { ...surveyFixture.grid, west: undefined } },
    { ...surveyFixture, provenance: { ...surveyFixture.provenance, classification: 1 } },
    { ...surveyFixture, provenance: { ...surveyFixture.provenance, maximumSupportDistanceM: 4 } }]) {
    expect(readSurveyGround(data)).toBeNull();
    expect(surveyGroundState(surveySite(data))?.status).toBe('unavailable');
  }
  expect(surveyGroundState({ ...surveySite(), coordinates: [[0, 0], [1, 0], [1, 1]] })?.status).toBe('unavailable');
  expect(surveyGroundState(surveySite({ ...surveyFixture, heights: [50, -3, -2, -3, -2, -1, -2, -1, 0] }))?.status).toBe('unavailable');
  expect(surveyGroundState({ ...surveySite(), properties: {} })).toBeNull();
});
