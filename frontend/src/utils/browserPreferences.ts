/** Optional UI preferences must not interrupt startup or project editing when
 * storage is blocked or full. Keep the active choice in component/store state. */
export function readBrowserPreference(key: string): string | null {
  try { return window.localStorage.getItem(key); } catch { return null; }
}

export function writeBrowserPreference(key: string, value: string | null): void {
  try {
    if (value === null) window.localStorage.removeItem(key);
    else window.localStorage.setItem(key, value);
  } catch { /* Persistence is optional; the current UI state remains usable. */ }
}
