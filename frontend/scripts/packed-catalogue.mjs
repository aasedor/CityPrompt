import { readFileSync } from 'node:fs';
import { deflateSync } from 'node:zlib';

const DATA_CATALOGUES = /\/src\/data\/(?:buildingArchetypes|openSpaceArchetypes|streetPathArchetypes|nativeParks|nativeStreetPilots|archetypeReferenceAvailability|legoFamilySignatures|validationCatalogue|buildingWalkDoors|cataloguePresentation|classroomExpansion|streetManual|nativeStreetModuleBounds)\.json$/;

const FEATURE_CATALOGUES = /\/src\/features\/(?:parks\/(?:detailCatalogueExtras|recoveredDetails|trafficSafetyCatalogue)|zoningCatalogue\/(?:buildingPrograms|parkPrograms|districtRules))\.json$/;

/** Retain all legacy IDs, reference paths and prompts without compiling several
 * megabytes of JSON into JavaScript object literals. Three already ships this
 * small inflater; no additional browser dependency or network request is needed. */
export function packCatalogue(source) {
  JSON.parse(source); // Reject invalid JSON before emitting a browser module.
  // Strip whitespace only outside strings. Re-stringifying parsed objects loses
  // signed zero, which occurs in authored model offsets and must round-trip.
  const canonical = source.replace(/("(?:\\.|[^"\\])*")|\s+/g, (_match, quoted) => quoted ?? '');
  const bytes = Buffer.from(canonical, 'utf8');
  // Two deterministic build-time profiles: smaller hash tables compress the
  // repeated geometry recipes better, while prose catalogues favour the default.
  // Keep the smaller stream; browser decoding and every authored value are unchanged.
  const packed = [8, 6].map(memLevel => deflateSync(bytes, { level: 9, memLevel }))
    .reduce((a, b) => b.length < a.length ? b : a).toString('base64');
  return `import { unzlibSync, strFromU8 } from 'three/examples/jsm/libs/fflate.module.js';
const bytes = Uint8Array.from(atob(${JSON.stringify(packed)}), character => character.charCodeAt(0));
export default JSON.parse(strFromU8(unzlibSync(bytes)));`;
}

export function packedCatalogue() {
  return {
    name: 'cityprompt-packed-catalogue',
    apply: 'build',
    enforce: 'post',
    transform(_code, id) {
      const filename = id.replaceAll('\\', '/');
      if (!DATA_CATALOGUES.test(filename) && !FEATURE_CATALOGUES.test(filename)) return null;
      return { code: packCatalogue(readFileSync(id, 'utf8')), map: null };
    },
  };
}
