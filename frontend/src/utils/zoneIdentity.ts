/**
 * Zone identity helpers.
 *
 * Newly drawn zones live client-side with an optimistic `temp-<timestamp>` id
 * (see useSiteZones.ts) until the backend persists them and returns a real
 * UUID. Every backend endpoint validates `zone_id: uuid.UUID`, so calling any
 * of them with a temp id is a guaranteed 422 — gate on this first.
 */

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isPersistedZoneId(id: string | undefined | null): boolean {
  return typeof id === 'string' && UUID_RE.test(id);
}
