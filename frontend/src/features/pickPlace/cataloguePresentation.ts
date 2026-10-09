import metadata from '@/data/cataloguePresentation.json';

/** Browsing copy only. These fields never replace registry identities, saved
 * properties, generation tags, model contracts or land-use classifications. */
export interface CataloguePresentation {
  label: string;
  description: string;
  styleIds: string[];
  searchTags: string[];
}
const presentations: Readonly<Record<string, CataloguePresentation>> = metadata;

/** Exact placement keys prevent a parent's appearance leaking into variants.
 * Missing future entries retain the existing authored catalogue fallback. */
export function cataloguePresentationFor(placementId: string | undefined): CataloguePresentation | undefined {
  return placementId ? presentations[placementId] : undefined;
}
