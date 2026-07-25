import {
  PUBLIC_REALM_STREET_FAMILIES,
  PUBLIC_REALM_STREET_FAMILY_VERSION,
  PUBLIC_REALM_STREET_SELECTIONS,
  isPublicRealmStreetFamilyId,
  type PublicRealmStreetFamilyId,
  type PublicRealmStreetSelectionDefinition,
  type StreetAppearanceKitId,
} from './streetFamilyCatalog';

export type StreetRecipeValidationCode =
  | 'missing_contract'
  | 'schema_version_unsupported'
  | 'family_not_found'
  | 'family_version_unsupported'
  | 'kind_incompatible'
  | 'generator_incompatible'
  | 'source_incompatible'
  | 'variant_incompatible'
  | 'appearance_incompatible'
  | 'profile_incompatible'
  | 'integrity_incompatible'
  | 'target_incompatible'
  | 'source_identity_mismatch';

export interface ValidatedPublicRealmStreetRecipe {
  schemaVersion: 1;
  familyId: PublicRealmStreetFamilyId;
  familyVersion: typeof PUBLIC_REALM_STREET_FAMILY_VERSION;
  archetypeId: string;
  variantId: string;
  profileId: string;
  profileVersion: number;
  appearanceKitId: StreetAppearanceKitId;
  targetType: 'street_segment' | 'street_node';
  targetRowM?: number;
  armCount?: number;
  catalogFingerprint: string;
  capabilityFingerprint: string;
  recipeHash: string;
  selection: PublicRealmStreetSelectionDefinition;
  raw: Record<string, unknown>;
}

export type PublicRealmStreetRecipeValidation =
  | { valid: true; recipe: ValidatedPublicRealmStreetRecipe }
  | { valid: false; code: StreetRecipeValidationCode; message: string };

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown>
    : null;
}

function canonicalId(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

function invalid(code: StreetRecipeValidationCode, message: string): PublicRealmStreetRecipeValidation {
  return { valid: false, code, message };
}

const SHA256_HEX = /^[a-f0-9]{64}$/;

/** Strict structural validation for a compiled Public Realm LEGO V1 street
 * recipe. It intentionally has no legacy fallback and is safe to reuse for
 * Direct-3D readiness decisions. */
export function validatePublicRealmStreetRecipe(
  value: unknown,
): PublicRealmStreetRecipeValidation {
  const raw = asRecord(value);
  if (!raw) return invalid('missing_contract', 'A nested public_realm_lego recipe is required.');
  if (raw.schema_version !== 1) {
    return invalid('schema_version_unsupported', 'Only Public Realm LEGO schema version 1 is executable.');
  }
  const familyId = canonicalId(raw.family_id);
  if (!isPublicRealmStreetFamilyId(familyId)) {
    return invalid('family_not_found', `Unknown executable street family '${familyId || 'missing'}'.`);
  }
  const family = PUBLIC_REALM_STREET_FAMILIES[familyId];
  if (raw.family_version !== PUBLIC_REALM_STREET_FAMILY_VERSION) {
    return invalid('family_version_unsupported', `Street family '${familyId}' must use version 1.`);
  }
  if (canonicalId(raw.kind) !== 'street') {
    return invalid('kind_incompatible', 'The compiled recipe kind must be street.');
  }
  if (canonicalId(raw.generator) !== 'street_section') {
    return invalid('generator_incompatible', 'The compiled street generator must be street_section.');
  }
  const archetypeId = canonicalId(raw.archetype_id);
  if (!family.sourceArchetypeIds.includes(archetypeId)) {
    return invalid('source_incompatible', `'${archetypeId || 'missing'}' is not executable by '${familyId}'.`);
  }
  const variantId = canonicalId(raw.variant_id);
  const selection = PUBLIC_REALM_STREET_SELECTIONS.find((candidate) => (
    candidate.familyId === familyId
    && candidate.archetypeId === archetypeId
    && candidate.variantId === variantId
  ));
  if (!selection) {
    return invalid('variant_incompatible', `'${variantId || 'missing'}' is not executable for '${archetypeId}'.`);
  }
  const appearanceKitId = canonicalId(raw.appearance_kit_id);
  if (appearanceKitId !== selection.appearanceKitId) {
    return invalid(
      'appearance_incompatible',
      `Variant '${variantId}' requires appearance kit '${selection.appearanceKitId}'.`,
    );
  }
  const profileId = typeof raw.profile_id === 'string' ? raw.profile_id.trim() : '';
  const profileVersion = raw.profile_version;
  if (
    !profileId
    || typeof profileVersion !== 'number'
    || !Number.isInteger(profileVersion)
    || profileVersion < 1
  ) {
    return invalid('profile_incompatible', 'The compiled recipe requires a non-empty profile id and positive integer profile version.');
  }
  const catalogFingerprint = typeof raw.catalog_fingerprint === 'string'
    ? raw.catalog_fingerprint
    : '';
  const capabilityFingerprint = typeof raw.capability_fingerprint === 'string'
    ? raw.capability_fingerprint
    : '';
  const recipeHash = typeof raw.recipe_hash === 'string' ? raw.recipe_hash : '';
  if (
    !SHA256_HEX.test(catalogFingerprint)
    || !SHA256_HEX.test(capabilityFingerprint)
    || !SHA256_HEX.test(recipeHash)
  ) {
    return invalid(
      'integrity_incompatible',
      'The compiled recipe requires canonical 64-character catalog, capability and recipe SHA-256 fields.',
    );
  }
  const target = asRecord(raw.target);
  if (canonicalId(target?.target_type) !== selection.targetType) {
    return invalid('target_incompatible', `Family '${familyId}' requires target type '${selection.targetType}'.`);
  }
  const targetRowValue = target?.row_width_m ?? target?.approach_row_width_m;
  const targetRowM = typeof targetRowValue === 'number' ? targetRowValue : Number.NaN;
  if (!(targetRowM > 0) || !Number.isFinite(targetRowM)) {
    return invalid('target_incompatible', 'The compiled street target requires a positive metric row width.');
  }
  const armCount = selection.targetType === 'street_node' && typeof target?.arm_count === 'number'
    ? target.arm_count
    : undefined;
  if (
    selection.targetType === 'street_node'
    && (!Number.isInteger(armCount) || !family.supportedNodeArmCounts?.includes(armCount as number))
  ) {
    return invalid(
      'target_incompatible',
      `Frontend V1 family '${familyId}' supports exactly four graph arms.`,
    );
  }
  return {
    valid: true,
    recipe: {
      schemaVersion: 1,
      familyId,
      familyVersion: PUBLIC_REALM_STREET_FAMILY_VERSION,
      archetypeId,
      variantId,
      profileId,
      profileVersion,
      appearanceKitId: appearanceKitId as StreetAppearanceKitId,
      targetType: selection.targetType,
      targetRowM,
      ...(armCount !== undefined ? { armCount } : {}),
      catalogFingerprint,
      capabilityFingerprint,
      recipeHash,
      selection,
      raw,
    },
  };
}

/** Validate the nested recipe and its persisted source identity together. */
export function validateStreetRecipeProperties(
  properties: unknown,
): PublicRealmStreetRecipeValidation {
  const props = asRecord(properties);
  if (!props) return invalid('missing_contract', 'Street properties are required.');
  const validation = validatePublicRealmStreetRecipe(props.public_realm_lego);
  if (!validation.valid) return validation;
  const legacyArchetype = canonicalId(props.road_archetype_id);
  const legacyVariant = canonicalId(props.road_selected_variant_id);
  if (legacyArchetype && legacyArchetype !== validation.recipe.archetypeId) {
    return invalid('source_identity_mismatch', 'road_archetype_id disagrees with the compiled street recipe.');
  }
  if (legacyVariant && legacyVariant !== validation.recipe.variantId) {
    return invalid('source_identity_mismatch', 'road_selected_variant_id disagrees with the compiled street recipe.');
  }
  return validation;
}
