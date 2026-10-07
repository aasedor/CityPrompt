export function readStoredRenderDraft(key: string): Record<string, unknown> {
  try {
    const saved = key ? JSON.parse(sessionStorage.getItem(key) ?? 'null') : null;
    return saved && typeof saved === 'object' && !Array.isArray(saved) ? saved : {};
  } catch { return {}; }
}
