import { useState } from 'react';
import { checkPromptSpelling } from '@/features/spelling/checkPromptSpelling';
import type { SpellingIssue } from '@/features/spelling/spellingTypes';

interface Props {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  maxLength?: number;
}

/** Explicit suggestions also work in browsers that replace the native spelling menu. */
export function PromptSpellingSuggestions({ value, onChange, disabled, maxLength }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  const [result, setResult] = useState<{ text: string; issues: SpellingIssue[] } | null>(null);
  const current = result?.text === value && !disabled ? result : null;

  async function check() {
    setBusy(true);
    setError(false);
    setResult(null);
    try { setResult({ text: value, issues: await checkPromptSpelling(value) }); }
    catch { setError(true); }
    finally { setBusy(false); }
  }

  function replace(issue: SpellingIssue, suggestion: string) {
    if (!current || disabled || value.slice(issue.start, issue.end) !== issue.word) return;
    const next = value.slice(0, issue.start) + suggestion + value.slice(issue.end);
    if (maxLength !== undefined && next.length > maxLength) return;
    const delta = suggestion.length - issue.word.length;
    setResult({ text: next, issues: current.issues.filter(i => i !== issue).map(i => i.start > issue.start
      ? { ...i, start: i.start + delta, end: i.end + delta } : i) });
    onChange(next);
  }

  return <div className="mt-1 text-xs font-normal">
    <button type="button" disabled={disabled || busy || !value.trim()} onClick={() => void check()}
      className="rounded px-1 py-1 underline underline-offset-2 disabled:opacity-50">
      {busy ? 'Checking spelling…' : 'Check spelling'}
    </button>
    {error && <p role="status">Spelling suggestions could not load. Try Check spelling again.</p>}
    {current && <div className="mt-1 max-h-44 overflow-y-auto rounded-lg border border-black/20 bg-[#fff9ec] p-2 text-[#151515]">
      <p role="status" className="mb-1">{current.issues.length ? 'Choose a correction, or keep the word.' : 'No more spelling suggestions.'}</p>
      {value.length > 5000 && <p>Checking the first 5,000 characters.</p>}
      {current.issues.length === 20 && <p>Showing the first 20 words. Check again after correcting them.</p>}
      {current.issues.map(issue => <div key={issue.start} className="flex flex-wrap items-center gap-1 border-t border-black/10 py-1.5">
        <span className="mr-1 font-semibold">{issue.word} →</span>
        {issue.suggestions.length === 0 && <span>No suggested replacement.</span>}
        {issue.suggestions.map(suggestion => <button type="button" key={suggestion}
          aria-label={`Replace ${issue.word} with ${suggestion}`}
          disabled={maxLength !== undefined && value.length - issue.word.length + suggestion.length > maxLength}
          onClick={() => replace(issue, suggestion)}
          className="rounded border border-black/30 bg-[#c9ff3d] px-2 py-1 font-semibold hover:bg-white disabled:opacity-50">{suggestion}</button>)}
        <button type="button" aria-label={`Keep ${issue.word}`} className="ml-1 rounded px-1 py-1 underline"
          onClick={() => setResult({ ...current, issues: current.issues.filter(i => i !== issue) })}>Keep word</button>
      </div>)}
    </div>}
  </div>;
}
