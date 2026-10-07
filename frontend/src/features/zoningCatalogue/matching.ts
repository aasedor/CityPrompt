import snapshot from './districtRules.json';
import programs from './buildingPrograms.json';
import parkPrograms from './parkPrograms.json';
import parkUseRules from './parkUseRules.json';
import type { CatalogueMatch, CatalogueProgram, DistrictRule, ParkProgram, UseRule, ZoneInspection } from './types';
import type { PlaceAsset } from '@/features/pickPlace/assetRegistry';

export const RULES_REVIEWED_AT = snapshot.reviewedAt;
export const DISTRICT_RULES: Record<string, DistrictRule> = Object.fromEntries(
  Object.entries(snapshot.districts as Record<string, DistrictRule>).map(([code, rule]) => [code, { ...rule,
    rules: [...rule.rules, ...((parkUseRules as Record<string, UseRule[]>)[code] ?? [])] }]),
);
export const BUILDING_PROGRAMS = programs as Record<string, CatalogueProgram>;
export const PARK_PROGRAMS = parkPrograms as Record<string, ParkProgram>;
const districtCodes = Object.keys(DISTRICT_RULES).sort((a, b) => b.length - a.length);
const useKey = (use: string) => use.toLowerCase().replace(/[^a-z0-9]/g, '');

/** Parse the complete designation, rejecting unrecognised suffixes and duplicate modifiers.
 * Never infer a bylaw from a student's caption or a DC district number. */
export function parseDesignation(designation: string) {
  const text = designation.trim().toUpperCase().replace(/\s+/g, '');
  if (!text || /^DC|^\d+DC/.test(text)) return null;
  const code = districtCodes.find(candidate => text.startsWith(candidate.toUpperCase()));
  if (!code) return null;
  const suffix = text.slice(code.length);
  const modifiers = [...suffix.matchAll(/([FHD])(\d+(?:\.\d+)?)/g)];
  if (modifiers.map(m => m[0]).join('') !== suffix || new Set(modifiers.map(m => m[1])).size !== modifiers.length) return null;
  const height = modifiers.find(m => m[1] === 'H');
  if (height && (Number(height[2]) <= 0 || DISTRICT_RULES[code].height.mode !== 'mapped')) return null;
  return { code, height: height ? Number(height[2]) : undefined };
}

export function rulesForZone(zone: ZoneInspection) {
  const parsed = !zone.custom && zone.district ? parseDesignation(zone.district.designation) : null;
  return parsed ? { ...parsed, rule: DISTRICT_RULES[parsed.code] } : null;
}

function matchUses(result: CatalogueMatch, program: CatalogueProgram, rule: DistrictRule, kind: 'building' | 'park') {
  for (const alternatives of program.components) {
    const options = rule.rules.filter(r => alternatives.some(use => useKey(use) === useKey(r.use)))
      .sort((a, b) => Number(Boolean(a.review)) - Number(Boolean(b.review)) || Number(a.category === 'discretionary') - Number(b.category === 'discretionary'));
    if (!options.length) {
      result.status = 'outside'; result.reasons.push(`No listed new-${kind} route found for ${alternatives.join(' / ')}.`);
    } else {
      result.uses.push(options[0]);
      if (options[0].review) result.reasons.push(options[0].review);
    }
  }
}

function finishMatch(result: CatalogueMatch) {
  if (result.status !== 'outside' && !result.reasons.length) {
    result.status = result.uses.some(r => r.category === 'discretionary') ? 'discretionary' : 'permitted';
  }
  return result;
}

export function matchBuilding(asset: PlaceAsset, zone: ZoneInspection,
  program: CatalogueProgram | undefined = BUILDING_PROGRAMS[asset.model.variantId]): CatalogueMatch {
  const height = asset.nativeDimensions?.[2];
  const result: CatalogueMatch = { asset, program: program?.revision === asset.model.revision ? program : undefined, status: 'review', uses: [], reasons: [],
    ...(height != null && Number.isFinite(height) && height > 0 ? { height } : {}) };
  const district = rulesForZone(zone);
  if (!district) {
    result.reasons.push(zone.custom ? 'Custom zones have no Calgary bylaw rules.' : 'This designation needs its own bylaw review, including any Direct Control bylaw.');
    return result;
  }
  if (!program || program.revision !== asset.model.revision) {
    result.reasons.push('This exact model revision needs a use classification.'); return result;
  }
  if (program.review || !program.components.length) {
    result.reasons.push(program.review ?? program.siteReview ?? 'The building program needs review.'); return result;
  }
  const { rule } = district;
  const districtComponents = program.districtUseGroups?.[district.code];
  if (program.districtUseGroups && !districtComponents) {
    result.reasons.push('This exact building arrangement has not been screened for this district.');
    return result;
  }
  matchUses(result, districtComponents ? { ...program, components: districtComponents } : program, rule, 'building');
  if (program.districtReview?.[district.code]) result.reasons.push(program.districtReview[district.code]);
  if (program.siteReview) result.reasons.push(program.siteReview);
  const h = rule.height;
  const limit = h.mode === 'mapped' ? district.height ?? h.metres : h.metres;
  result.limit = limit;
  if (result.height === undefined) result.reasons.push('The model has no verified height in metres.');
  else if (h.mode === 'review' || h.mode === 'mapped' && limit === undefined) result.reasons.push(h.note);
  else if (h.mode === 'mapped' && district.height !== undefined && h.metres !== undefined && ['M-H1', 'M-H2'].includes(district.code) && district.height >= h.metres) {
    result.reasons.push('The h modifier conflicts with this district’s height rules; verify the full designation.');
  } else if (limit !== undefined && result.height > limit + 0.01) {
    if (h.upperMetres && result.height <= h.upperMetres + 0.01) result.reasons.push(h.note);
    else { result.status = 'outside'; result.reasons.push(`Model envelope ${result.height.toFixed(1)} m exceeds the ${limit} m screening limit. Grade measurement and exempt roof features can change bylaw height.`); }
  }
  // Grade access is not encoded in an apartment's architectural browsing label.
  if (['M-CG', 'M-G', 'H-GO'].includes(district.code) && result.uses.some(r => /Multi-Residential|Dwelling Unit/.test(r.use))) {
    result.reasons.push('Individual access to grade and the unit arrangement need confirmation for this district.');
  }
  return finishMatch(result);
}

/** Park use screening intentionally excludes the model envelope: its tallest
 * object may be a tree. Buildings, shelters and elevated structures need their
 * own measurements and site checks, as stated on every park result. */
export function matchPark(asset: PlaceAsset, zone: ZoneInspection): CatalogueMatch {
  const candidate = PARK_PROGRAMS[asset.id];
  const program = candidate?.variantId === asset.model.variantId && candidate.revision === asset.model.revision ? candidate : undefined;
  const result: CatalogueMatch = { asset, program, status: 'review', uses: [], reasons: [] };
  const district = rulesForZone(zone);
  if (!district) {
    result.reasons.push(zone.custom ? 'Custom zones have no Calgary bylaw rules.' : 'This designation needs its own bylaw review, including any Direct Control bylaw.');
    return result;
  }
  if (asset.zoneType !== 'green_space' || !program || !program.components.length) {
    result.reasons.push('This exact park layout needs a use classification.'); return result;
  }
  matchUses(result, program, district.rule, 'park');
  if (program.review) result.reasons.push(program.review);
  if (program.siteReview) result.reasons.push(program.siteReview);
  return finishMatch(result);
}

export function matchCatalogue(assets: PlaceAsset[], zone: ZoneInspection) {
  return assets.filter(asset => ['building', 'green_space'].includes(asset.zoneType) && ['ready', 'pilot'].includes(asset.readiness))
    .map(asset => asset.zoneType === 'green_space' ? matchPark(asset, zone) : matchBuilding(asset, zone))
    .sort((a, b) => a.asset.label.localeCompare(b.asset.label));
}
