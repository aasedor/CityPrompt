import type { AestheticCategory } from '@/components/viewer/aestheticCatalog';
import type { CatalogueAsset } from './assetRegistry';
import type { CanonicalChoice } from './canonicalCatalogue';
import type { CatalogueDomain } from '@/features/calgaryCatalogue/guide';
import { cataloguePresentationFor } from './cataloguePresentation';

export interface CatalogueFacets { styleId: string; sizeId: string }
interface SizeBand { id: string; label: string; min: number; max: number }
const AREA_BANDS: SizeBand[] = [
  { id: 'small', label: 'Under 500 m²', min: 0, max: 500 },
  { id: 'medium', label: '500 to under 2,000 m²', min: 500, max: 2000 },
  { id: 'large', label: '2,000 to under 10,000 m²', min: 2000, max: 10000 },
  { id: 'district', label: '10,000 m² and up', min: 10000, max: Infinity },
];
const WIDTH_BANDS: SizeBand[] = [
  { id: 'narrow', label: 'Under 12 m wide', min: 0, max: 12 },
  { id: 'local', label: '12 to under 20 m wide', min: 12, max: 20 },
  { id: 'wide', label: '20 m wide and up', min: 20, max: Infinity },
];
const UNKNOWN = { id: 'unknown', label: 'Size not catalogued' };
const STYLE_ALIASES: Record<string, string> = {
  brutalism: 'brutalism', brutalist: 'brutalism', brutalist_utility: 'brutalism',
  scandinavian_nordic: 'scandinavian_nordic', scandinavian: 'scandinavian_nordic', nordic: 'scandinavian_nordic',
};
// Source IDs remain stable evidence keys; card/filter labels use plain names.
const STYLE_LABELS: Record<string, string> = {
  brutalism: 'Brutalist',
  scandinavian_nordic: 'Scandinavian / Nordic',
  civic_modernism_rec: 'Civic Modernism',
  civic_monumental: 'Monumental Civic',
  daylight_factory: 'Industrial',
  glass_tower_modern: 'Modern Glass',
  modern_bigbox: 'Modern Commercial',
  roadside_commercial: 'Roadside Commercial',
  corrugated_vernacular: 'Corrugated-Metal Vernacular',
  japanese_contemporary: 'Contemporary Japanese',
  parkitecture: 'Rustic Park Architecture',
};
// These legacy categories describe a use or programme, not an appearance.
// Keep their existing land-use grouping; do not advertise it as a style.
const PURPOSE_CATEGORIES = new Set(['other','transportation','energy_infrastructure','transit_infrastructure',
  'civic_infrastructure','civic_institutional','brewery_distillery','climbing_wall','immersive_experience',
  'industrial_logistics','industrial_park','institutional_civic','institutional_civic_sports',
  'institutional_education','institutional_healthcare','institutional_research','senior_living']);
const STYLE_TAGS = new Set(['historical','contemporary_urban','modernist','classical','industrial_brick',
  'mediterranean','futuristic','art_deco','traditional_vernacular','minimalist','parisian','brownstone_rowhouse',
  'mountain_alpine','japanese_contemporary','eco_urban_green_architecture','gothic','collegiate_gothic',
  'neoclassical','postmodern','structural_expressionism']);
const number = new Intl.NumberFormat('en-CA', { maximumFractionDigits: 1 });
const positive = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value) && value > 0;
const normalizeStyle = (value: string) => value.trim().toLowerCase().replace(/[\s/-]+/g, '_');

/** Browsing evidence only. Positive catalogue tags may supplement the authored
 * category; material, location, and render-prompt text never invent a style. */
export function catalogueStyleIds(choice: CanonicalChoice): string[] {
  if (choice.domain !== 'building') return [];
  const presentation = cataloguePresentationFor(choice.placements[0]?.id);
  if (presentation) return [...presentation.styleIds];
  const ids = new Set<string>();
  const category = normalizeStyle(choice.option.categoryId ?? '');
  if (category && !PURPOSE_CATEGORIES.has(category)) ids.add(STYLE_ALIASES[category] ?? category);
  for (const tag of choice.option.generationTags ?? []) {
    const normalized = normalizeStyle(tag);
    const alias = STYLE_ALIASES[normalized] ?? (STYLE_TAGS.has(normalized) ? normalized : undefined);
    if (alias) ids.add(alias);
  }
  return [...ids];
}

export function catalogueStyleLabel(id: string, categories: AestheticCategory[] = []): string {
  if (id === 'unknown') return 'Style not catalogued';
  if (STYLE_LABELS[id]) return STYLE_LABELS[id];
  return categories.find(category => category.id === id)?.label
    ?? id.replace(/_/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase());
}

export function availableCatalogueStyles(choices: CanonicalChoice[], categories: AestheticCategory[]) {
  const ids = new Set(choices.flatMap(catalogueStyleIds));
  if (choices.some(choice => choice.domain === 'building' && !catalogueStyleIds(choice).length)) ids.add('unknown');
  return [...ids].map(id => ({ id, label: catalogueStyleLabel(id, categories) }))
    .sort((a,b) => a.label.localeCompare(b.label));
}

/** The default reserved plot is intentionally distinct from the model envelope
 * and gross floor area. Route length is student-authored, so streets use width. */
export function catalogueAssetSize(asset: CatalogueAsset | undefined): number | undefined {
  if (!asset) return undefined;
  if (asset.kind === 'street') return positive(asset.sectionWidth) ? asset.sectionWidth : undefined;
  return positive(asset.width) && positive(asset.depth) && positive(asset.width * asset.depth) ? asset.width * asset.depth : undefined;
}

export function catalogueSizeId(choice: CanonicalChoice): string {
  const value = catalogueAssetSize(choice.placements[0]);
  if (value === undefined) return 'unknown';
  const bands = choice.domain === 'street_pathway' ? WIDTH_BANDS : AREA_BANDS;
  return bands.find(band => value >= band.min && value < band.max)?.id ?? 'unknown';
}

export function availableCatalogueSizes(domain: CatalogueDomain, choices: CanonicalChoice[]) {
  const ids = new Set(choices.filter(choice => choice.domain === domain).map(catalogueSizeId));
  const bands = domain === 'street_pathway' ? WIDTH_BANDS : AREA_BANDS;
  return [...bands, UNKNOWN].filter(band => ids.has(band.id));
}

export function catalogueSizeLabel(asset: CatalogueAsset | undefined): string {
  const value = catalogueAssetSize(asset);
  if (value === undefined || !asset) return 'Size not catalogued';
  if (asset.kind === 'street') return `${number.format(value)} m corridor width`;
  return `Default plot ${number.format(asset.width)} × ${number.format(asset.depth)} m · ${number.format(value)} m²`;
}

export function choiceMatchesFacets(choice: CanonicalChoice, { styleId, sizeId }: CatalogueFacets): boolean {
  const styles = catalogueStyleIds(choice);
  return (!styleId || (styleId === 'unknown' ? !styles.length : styles.includes(styleId)))
    && (!sizeId || catalogueSizeId(choice) === sizeId);
}
