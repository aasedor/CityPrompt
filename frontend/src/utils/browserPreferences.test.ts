import { afterEach, expect, it, vi } from 'vitest';
import { readBrowserPreference, writeBrowserPreference } from './browserPreferences';

afterEach(() => { vi.restoreAllMocks(); localStorage.clear(); });

it('reads, updates and clears a project preference when storage is available', () => {
  writeBrowserPreference('plan-layer:project', 'Plan A');
  expect(readBrowserPreference('plan-layer:project')).toBe('Plan A');
  writeBrowserPreference('plan-layer:project', null);
  expect(readBrowserPreference('plan-layer:project')).toBeNull();
});

it('survives browsers that throw when the storage property itself is accessed', () => {
  vi.spyOn(window, 'localStorage', 'get').mockImplementation(() => { throw new DOMException('Blocked', 'SecurityError'); });
  expect(readBrowserPreference('plan-layer:project')).toBeNull();
  expect(() => writeBrowserPreference('plan-layer:project', 'Plan B')).not.toThrow();
  expect(() => writeBrowserPreference('plan-layer:project', null)).not.toThrow();
});

it('preserves the prior stored preference if a quota failure prevents saving', () => {
  writeBrowserPreference('plan-layer:project', 'Plan A');
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new DOMException('Full', 'QuotaExceededError'); });
  expect(() => writeBrowserPreference('plan-layer:project', 'Plan B')).not.toThrow();
  expect(readBrowserPreference('plan-layer:project')).toBe('Plan A');
});
