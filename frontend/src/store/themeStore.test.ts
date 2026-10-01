import { afterEach, expect, it, vi } from 'vitest';

afterEach(() => {
  vi.restoreAllMocks();
  vi.resetModules();
  localStorage.clear();
  document.documentElement.classList.remove('dark');
});

it('starts with a usable theme when browser storage access is denied', async () => {
  vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => { throw new DOMException('Blocked', 'SecurityError'); });
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new DOMException('Blocked', 'SecurityError'); });
  const { useThemeStore } = await import('./themeStore');
  expect(useThemeStore.getState().theme).toBe('light');
  useThemeStore.getState().setTheme('dark');
  expect(useThemeStore.getState().effective).toBe('dark');
  expect(document.documentElement.classList.contains('dark')).toBe(true);
});

it('still applies a chosen theme when browser storage is full', async () => {
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new DOMException('Full', 'QuotaExceededError'); });
  const { useThemeStore } = await import('./themeStore');
  useThemeStore.getState().setTheme('dark');
  expect(useThemeStore.getState().theme).toBe('dark');
});

it('ignores invalid saved theme values', async () => {
  localStorage.setItem('siteforge-theme', 'broken-value');
  const { useThemeStore } = await import('./themeStore');
  expect(useThemeStore.getState().theme).toBe('light');
});
