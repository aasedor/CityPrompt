import validation from '@/data/validationCatalogue.json';
import type { SiteZone } from '@/types';

type NativeBuildingBinding = (typeof validation.entries)[number] & { standalone_native?: boolean };

const bindings = new Map(
  (validation.entries as NativeBuildingBinding[])
    .filter(row => row.domain === 'building' && row.binding === 'native-runtime' && row.local_url)
    .map(row => [row.placement_id, row]),
);

/** Resolve only the static model bound to this saved picker revision. */
export function validationNativeBuildingBinding(assetId: unknown, revision: unknown) {
  if (typeof assetId !== 'string' || typeof revision !== 'string' || !revision) return undefined;
  const binding = bindings.get(assetId);
  return binding?.sha256 === revision ? binding : undefined;
}

export function isStandaloneNativeBuilding(zone: Pick<SiteZone, 'properties'>): boolean {
  const properties = zone.properties;
  if (properties?.validation_fixed_fixture !== true) return false;
  const binding = validationNativeBuildingBinding(properties.pick_place_asset, properties.pick_place_model_revision);
  return binding?.standalone_native === true
    && binding.variant_id === properties.development_selected_variant_id
    && binding.local_url === properties.validation_native_url;
}
