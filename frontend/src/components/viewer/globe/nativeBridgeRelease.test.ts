import { expect, it } from 'vitest';
import release from '@/data/nativeBridgeRelease.json';
import { releasedNativeBridgeProfiles } from './nativeBridgeSources';

type Entry = typeof release.entries[number];
it.each([
  ['changed programme', (entry: Entry) => { entry.profile.program.maxLengthM = 241; }],
  ['changed source', (entry: Entry) => { entry.profile.sourceAssemblySha256 = 'f'.repeat(64); }],
  ['changed module', (entry: Entry) => {
    const module = entry.profile.modules.bridge_bay;
    if (!module) throw new Error('Timber fixture must include its bay');
    module.sha256 = 'f'.repeat(64);
  }],
  ['missing module', (entry: Entry) => { Reflect.deleteProperty(entry.profile.modules,'bridge_bay'); }],
  ['pending runtime review', (entry: Entry) => { entry.runtimeReview.status = 'pending'; }],
  ['wrong runtime identity', (entry: Entry) => { entry.runtimeReview.profileSha256 = 'f'.repeat(64); }],
  ['missing source review', (entry: Entry) => { entry.sourceVisualReview.sha256 = ''; }],
  ['unpublished receipt', (entry: Entry) => { entry.status = 'local-pilot-runtime-pending'; }],
] as const)('does not execute a release with %s', (_name, mutate) => {
  const candidate = structuredClone(release.entries[0]);
  mutate(candidate);
  expect(releasedNativeBridgeProfiles([candidate])).toEqual([]);
});
