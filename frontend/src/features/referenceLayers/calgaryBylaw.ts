import catalogue from './calgaryBylawCatalogue.json';
import type { CalgaryDistrict } from './calgaryDistricts';

/** Reviewed snapshot of City bylaw districts and the City's Land Use Class
 * renderer. Keep this small local catalogue available during classroom outages. */
export const CALGARY_DISTRICTS: CalgaryDistrict[] = catalogue.districts;
export const CALGARY_COLOUR_SOURCE = catalogue.colourItem;
export const CALGARY_DISTRICT_SOURCE = catalogue.bylawSource;
export const CALGARY_CATALOGUE_DATE = catalogue.retrievedAt.slice(0, 10);
export const CUSTOM_ZONE = '__custom__';
const colours: Record<string, string> = catalogue.colours;
const byCode = new Map(catalogue.districts.map(district => [district.code, district]));
const codes = [...byCode.keys()].sort((a, b) => b.length - a.length);

export function calgaryDistrictColour(designation: string): string {
  designation = designation.replace(/\s+/g, '');
  if (/^DC(?:\b|\d)/i.test(designation)) return colours['Direct Control'];
  // Keep density/height modifiers and full DC bylaws intact in the label.
  const code = codes.find(value => designation === value || designation.startsWith(value) && /^[dfh]\d/.test(designation.slice(value.length)));
  return code ? colours[byCode.get(code)!.major] : '#c9c9c9';
}

export function districtChoices(extras: CalgaryDistrict[] = []): CalgaryDistrict[] {
  const choices = new Map(CALGARY_DISTRICTS.map(district => [district.designation, district]));
  for (const district of extras) if (!choices.has(district.designation)) choices.set(district.designation, district);
  return [...choices.values()].sort((a, b) => a.designation.localeCompare(b.designation));
}
