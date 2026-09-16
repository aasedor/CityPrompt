import { expect, it } from 'vitest';
import { contextPilotCaptureProblem, readContextPilot, visibleContext } from './contextProvider';

const fixture = { id: 'drone-building-scans-flat-roof', kind: '3d-tiles', projectId: 'pilot',
  tilesetPath: '/context-pilot/tileset.json', registration: 'local-engineering-test', groundAuthority: 'saved-project',
  attribution: 'Drone Building Scans — Matthew Guertin, 2026', licenseUrl: 'https://creativecommons.org/licenses/by/4.0/' };

it('accepts only the attributed fixture belonging to this project', () => {
  expect(readContextPilot(fixture, 'pilot')).toEqual(fixture);
  expect(readContextPilot(fixture, 'other')).toBeNull();
  for (const bad of [null, {}, { ...fixture, attribution: '' }, { ...fixture, registration: 'survey' },
    { ...fixture, groundAuthority: 'photogrammetry' }, { ...fixture, tilesetPath: 'https://example.com/tileset.json' },
    { ...fixture, tilesetPath: '/context-pilot/../private/tileset.json' }]) expect(readContextPilot(bad, 'pilot')).toBeNull();
});

it('retains Google while loading or after failure, without changing the chosen design ground', () => {
  expect(visibleContext('capture', false, false)).toBe('google');
  expect(visibleContext('capture', true, false)).toBe('capture');
  expect(visibleContext('capture', true, true)).toBe('google');
  expect(visibleContext('terrain', false, false)).toBe('terrain');
  expect(visibleContext('google', true, false)).toBe('google');
});

it('keeps Gaussian samples separate from tile and survey contracts', () => {
  const { tilesetPath: _unused, ...base } = fixture;
  const splat = { ...base, id: 'knock-community-hall', kind: 'gaussian-splat', assetPath: '/gaussian-splat/knock-community-hall.sog' };
  expect(readContextPilot(splat, 'pilot')).toEqual(splat);
  for (const bad of [{ ...splat, assetPath: 'https://example.com/test.sog' },
    { ...splat, registration: 'geographic-pilot' }, { ...splat, groundAuthority: 'classified-lidar' },
    { ...splat, kind: '3d-tiles' }]) expect(readContextPilot(bad, 'pilot')).toBeNull();
});

it('accepts the fixed geographic LiDAR fixture without mixing its registration and ground contract with the mesh', () => {
  const lidar = { ...fixture, id: 'usgs-san-francisco-2023', tilesetPath: '/sf-lidar/tileset.json',
    registration: 'geographic-pilot', groundAuthority: 'classified-lidar',
    licenseUrl: 'https://www.fisheries.noaa.gov/inport/item/73386/full-list' };
  expect(readContextPilot(lidar, 'pilot')).toEqual(lidar);
  expect(readContextPilot({ ...lidar, groundAuthority: 'saved-project' }, 'pilot')).toBeNull();
  expect(readContextPilot({ ...lidar, tilesetPath: '/context-pilot/tileset.json' }, 'pilot')).toBeNull();
});

it('keeps the unregistered sample out of professional render provenance', () => {
  const provider = readContextPilot(fixture, 'pilot');
  expect(contextPilotCaptureProblem(provider, 'capture')).toMatch(/Switch to Google 3D/);
  expect(contextPilotCaptureProblem(provider, 'terrain')).toBeTruthy();
  expect(contextPilotCaptureProblem(provider, 'google')).toBeNull();
  expect(contextPilotCaptureProblem(null, 'capture')).toBeNull();
});
