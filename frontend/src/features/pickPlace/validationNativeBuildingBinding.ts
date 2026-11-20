import validation from '@/data/validationCatalogue.json';
import type { SiteZone } from '@/types';

type NativeBuildingBinding = (typeof validation.entries)[number] & {
  standalone_native?: boolean;
  model_revision?: string;
};

const bindings = new Map(
  (validation.entries as NativeBuildingBinding[])
    .filter(row => row.domain === 'building' && row.binding === 'native-runtime' && row.local_url)
    .map(row => [row.placement_id, row]),
);

/** Resolve only the static model bound to this saved picker revision. */
export function validationNativeBuildingBinding(assetId: unknown, revision: unknown) {
  if (typeof assetId !== 'string' || typeof revision !== 'string' || !revision) return undefined;
  const binding = bindings.get(assetId);
  return (binding?.model_revision ?? binding?.sha256) === revision ? binding : undefined;
}

export function standaloneNativeBuildingBinding(zone: Pick<SiteZone, 'properties'>) {
  const properties = zone.properties;
  const binding = validationNativeBuildingBinding(properties?.pick_place_asset, properties?.pick_place_model_revision);
  if (!binding?.standalone_native || binding.variant_id !== properties?.development_selected_variant_id) return undefined;
  if (properties.validation_fixed_fixture === true) {
    return binding.local_url === properties.validation_native_url ? binding : undefined;
  }
  // A published named revision may have been saved before it had a static URL.
  return binding.model_revision && properties.validation_native_url == null ? binding : undefined;
}

export function isStandaloneNativeBuilding(zone: Pick<SiteZone, 'properties'>): boolean {
  return Boolean(standaloneNativeBuildingBinding(zone));
}
