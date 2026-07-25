import type { SiteZone } from '@/types';

export type StreetControlHierarchy = 'local' | 'major';
export type FourWayIntersectionControl = 'unsignalized' | 'traffic_signal';

const MAJOR_STREET_ROLES = new Set([
  'arterial',
  'collector',
  'main',
  'main_street',
  'major',
  'primary',
  'spine',
  'trunk',
]);

function normalizedId(value: unknown): string {
  return String(value ?? '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown>
    : undefined;
}

function isMajorArchetype(value: unknown): boolean {
  const archetype = normalizedId(value);
  if (!archetype) return false;
  return archetype === 'main_street_complete'
    || archetype.includes('arterial')
    || archetype.includes('collector')
    || archetype.startsWith('main_street_')
    || archetype.endsWith('_main_street');
}

function isMajorRole(value: unknown): boolean {
  const role = normalizedId(value);
  if (MAJOR_STREET_ROLES.has(role)) return true;
  const tokens = role.split('_');
  return tokens.includes('arterial')
    || tokens.includes('collector')
    || tokens.includes('major')
    || role.includes('main_street');
}

/** Deterministic hierarchy used only for intersection control. Width alone is
 * intentionally not a warrant: a broad local residential street remains
 * unsignalized unless its explicit family, role, archetype or functional
 * class identifies a major/collector/main/arterial corridor. */
export function resolveStreetControlHierarchy(
  zone: Pick<SiteZone, 'properties'>,
): StreetControlHierarchy {
  const props = asRecord(zone.properties);
  const recipe = asRecord(props?.public_realm_lego);
  if (normalizedId(recipe?.family_id) === 'street_complete_main_22m') return 'major';

  const roleValues = [
    props?.street_role,
    props?.road_class,
    props?.functional_class,
    props?.classification,
  ];
  if (roleValues.some(isMajorRole)) return 'major';
  if ([props?.road_archetype_id, recipe?.archetype_id].some(isMajorArchetype)) return 'major';
  return 'local';
}

/** Signal control is warranted when at least one connected approach has an
 * explicit major hierarchy. The order of the connected zones has no effect. */
export function resolveFourWayIntersectionControl(
  connectedZones: readonly Pick<SiteZone, 'properties'>[],
): FourWayIntersectionControl {
  return connectedZones.some((zone) => resolveStreetControlHierarchy(zone) === 'major')
    ? 'traffic_signal'
    : 'unsignalized';
}
