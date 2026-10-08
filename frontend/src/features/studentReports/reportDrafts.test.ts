import { afterEach, describe, expect, it, vi } from 'vitest';
import { clearSavedReportDraft, readReportDraft, reportDraftKey, writeReportDraft } from './reportDrafts';
afterEach(() => { vi.restoreAllMocks(); sessionStorage.clear(); });
describe('report draft storage', () => {
  const draft = { choice: 'adapt' as const, rationale: 'Keep trees', followThrough: '' };
  it('isolates accounts, projects and findings and clears only the saved version', () => {
    const key = reportDraftKey('a', 'p', 'r', 'f');
    writeReportDraft(key, draft);
    expect(readReportDraft(reportDraftKey('b', 'p', 'r', 'f'))).toBeNull();
    expect(readReportDraft(reportDraftKey('a', 'other', 'r', 'f'))).toBeNull();
    expect(readReportDraft(reportDraftKey('a', 'p', 'r', 'other'))).toBeNull();
    const newer = { ...draft, rationale: 'Keep trees and paths' };
    writeReportDraft(key, newer);
    clearSavedReportDraft(key, draft);
    expect(readReportDraft(key)).toEqual(newer);
    clearSavedReportDraft(key, newer);
    expect(readReportDraft(key)).toBeNull();
  });
  it('keeps newer text when storage fills but remains readable', () => {
    const key = reportDraftKey('quota', 'p', 'r', 'f');
    writeReportDraft(key, draft);
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('Quota exceeded'); });
    const newer = { ...draft, rationale: 'New text after quota failure' };
    writeReportDraft(key, newer);
    expect(readReportDraft(key)).toEqual(newer);
    clearSavedReportDraft(key, newer);
    expect(readReportDraft(key)).toBeNull();
  });
});
