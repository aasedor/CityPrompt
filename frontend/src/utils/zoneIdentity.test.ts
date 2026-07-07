import { describe, it, expect } from 'vitest';
import { isPersistedZoneId } from './zoneIdentity';

describe('isPersistedZoneId', () => {
  it('accepts a real UUID', () => {
    expect(isPersistedZoneId('a3bb189e-8bf9-3888-9912-ace4e6543002')).toBe(true);
    expect(isPersistedZoneId('A3BB189E-8BF9-3888-9912-ACE4E6543002')).toBe(true);
  });

  it('rejects optimistic temp ids', () => {
    expect(isPersistedZoneId(`temp-${Date.now()}`)).toBe(false);
    expect(isPersistedZoneId('temp-1751900000000')).toBe(false);
  });

  it('rejects empty / missing ids', () => {
    expect(isPersistedZoneId('')).toBe(false);
    expect(isPersistedZoneId(undefined)).toBe(false);
    expect(isPersistedZoneId(null)).toBe(false);
  });

  it('rejects UUID-ish strings with wrong shape', () => {
    expect(isPersistedZoneId('a3bb189e-8bf9-3888-9912')).toBe(false);
    expect(isPersistedZoneId('not-a-uuid-at-all')).toBe(false);
  });
});
