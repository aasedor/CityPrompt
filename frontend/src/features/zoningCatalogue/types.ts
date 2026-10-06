import type { CalgaryDistrict } from '@/features/referenceLayers/calgaryDistricts';
import type { PlaceAsset } from '@/features/pickPlace/assetRegistry';

export interface ZoneInspection {
  id: string;
  layerId?: string;
  label: string;
  source: string;
  district?: CalgaryDistrict;
  custom?: boolean;
  color?: string;
}
export interface CatalogueProgram {
  revision: string | null;
  /** Each component is required; names within one component are alternative legal forms. */
  components: string[][];
  assumption: string;
  /** Exact-model evidence, or an explicit classroom occupancy chosen for this revision. */
  classification?: { basis: 'model' | 'teaching'; evidence: string };
  /** Conditions of the stated program; candidates still require normal site assessment. */
  conditions?: string[];
  /** Researched uses for this exact arrangement; absent districts remain unreviewed. */
  districtUseGroups?: Record<string, string[][]>;
  /** A known district-specific configuration conflict needs explicit assessment. */
  districtReview?: Record<string, string>;
  /** Known program whose approval depends on information outside this model. Blocks confirmation. */
  siteReview?: string;
  /** Unresolved catalogue classification, distinct from a known site dependency. */
  review?: string;
}
export interface ParkProgram extends CatalogueProgram {
  /** Flexible and native layouts can share a variant ID, so bind placement + variant + revision. */
  variantId: string;
}
export interface UseRule {
  use: string;
  category: 'permitted' | 'discretionary';
  section: string;
  definition: string;
  review?: string;
}
export interface DistrictRule {
  source: string;
  note?: string;
  rules: UseRule[];
  height: {
    mode: 'fixed' | 'mapped' | 'contextual' | 'parcel' | 'unlimited' | 'review';
    metres?: number;
    upperMetres?: number;
    section: string;
    note: string;
  };
}
export interface CatalogueMatch {
  asset: PlaceAsset;
  program?: CatalogueProgram;
  status: 'permitted' | 'discretionary' | 'review' | 'outside';
  uses: UseRule[];
  height?: number;
  limit?: number;
  reasons: string[];
}
