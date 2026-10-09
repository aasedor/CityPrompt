import { readFileSync } from 'node:fs';
import { deflateSync } from 'node:zlib';

const CATALOGUES = /\/src\/data\/(?:buildingArchetypes|openSpaceArchetypes|streetPathArchetypes|nativeParks|nativeStreetPilots|archetypeReferenceAvailability|legoFamilySignatures|validationCatalogue)\.json$/;

/** Retain all legacy IDs, reference paths and prompts without compiling several
 * megabytes of JSON into JavaScript object literals. Three already ships this
 * small inflater; no additional browser dependency or network request is needed. */
export function packCatalogue(source) {
  const canonical = JSON.stringify(JSON.parse(source));
  const packed = deflateSync(Buffer.from(canonical, 'utf8'), { level: 9 }).toString('base64');
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
      if (!CATALOGUES.test(filename)) return null;
      return { code: packCatalogue(readFileSync(id, 'utf8')), map: null };
    },
  };
}
