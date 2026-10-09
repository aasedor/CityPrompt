import '@testing-library/jest-dom/vitest';
import { useState } from 'react';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { PromptSpellingSuggestions } from './PromptSpellingSuggestions';
import { checkPromptSpelling } from '@/features/spelling/checkPromptSpelling';
vi.mock('@/features/spelling/checkPromptSpelling', () => ({ checkPromptSpelling: vi.fn() }));
const check = vi.mocked(checkPromptSpelling);
afterEach(cleanup);
beforeEach(() => { check.mockReset(); });
function Field() {
  const [value, setValue] = useState('Have a party goingg on in the park.');
  return <><textarea aria-label="Prompt" value={value} onChange={e => setValue(e.target.value)} />
    <PromptSpellingSuggestions value={value} onChange={setValue} /></>;
}
it('offers a correction and replaces only the selected occurrence', async () => {
  check.mockResolvedValue([{ word: 'goingg', start: 13, end: 19, suggestions: ['going'] }]);
  render(<Field />);
  expect(check).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Check spelling' }));
  fireEvent.click(await screen.findByRole('button', { name: 'Replace goingg with going' }));
  expect(screen.getByRole('textbox')).toHaveValue('Have a party going on in the park.');
  expect(screen.queryByRole('button', { name: 'Replace goingg with going' })).not.toBeInTheDocument();
});
it('never applies results to text edited while checking', async () => {
  let resolve!: (value: Awaited<ReturnType<typeof check>>) => void;
  check.mockImplementation(() => new Promise(r => { resolve = r; }));
  render(<Field />);
  fireEvent.click(screen.getByRole('button', { name: 'Check spelling' }));
  fireEvent.change(screen.getByRole('textbox'), { target: { value: 'A different scene.' } });
  resolve([{ word: 'goingg', start: 13, end: 19, suggestions: ['going'] }]);
  await waitFor(() => expect(screen.getByRole('button', { name: 'Check spelling' })).toBeEnabled());
  expect(screen.queryByRole('button', { name: 'Replace goingg with going' })).not.toBeInTheDocument();
  expect(screen.getByRole('textbox')).toHaveValue('A different scene.');
});
it('lets users keep names and gives a retry after dictionary failure', async () => {
  check.mockRejectedValueOnce(new Error('unavailable'));
  check.mockResolvedValueOnce([{ word: 'goingg', start: 13, end: 19, suggestions: ['going'] }]);
  render(<Field />);
  fireEvent.click(screen.getByRole('button', { name: 'Check spelling' }));
  expect(await screen.findByText(/Spelling suggestions could not load/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Check spelling' }));
  fireEvent.click(await screen.findByRole('button', { name: 'Keep goingg' }));
  expect(screen.getByRole('textbox')).toHaveValue('Have a party goingg on in the park.');
});
it('does not allow checking or applying corrections to a disabled prompt', async () => {
  const onChange = vi.fn();
  const { rerender } = render(<PromptSpellingSuggestions value="goingg" onChange={onChange} />);
  check.mockResolvedValue([{ word: 'goingg', start: 0, end: 6, suggestions: ['going'] }]);
  fireEvent.click(screen.getByRole('button', { name: 'Check spelling' }));
  await screen.findByRole('button', { name: 'Replace goingg with going' });
  rerender(<PromptSpellingSuggestions value="goingg" onChange={onChange} disabled />);
  expect(screen.getByRole('button', { name: 'Check spelling' })).toBeDisabled();
  expect(screen.queryByRole('button', { name: 'Replace goingg with going' })).not.toBeInTheDocument();
  expect(onChange).not.toHaveBeenCalled();
});

it('adjusts later word offsets after the first correction', async () => {
  function Repeated() {
    const [value, setValue] = useState('goingg goingg');
    return <><textarea aria-label="Prompt" value={value} readOnly /><PromptSpellingSuggestions value={value} onChange={setValue} /></>;
  }
  check.mockResolvedValue([
    { word: 'goingg', start: 0, end: 6, suggestions: ['going'] },
    { word: 'goingg', start: 7, end: 13, suggestions: ['going'] },
  ]);
  render(<Repeated />);
  fireEvent.click(screen.getByRole('button', { name: 'Check spelling' }));
  fireEvent.click((await screen.findAllByRole('button', { name: 'Replace goingg with going' }))[0]);
  fireEvent.click(screen.getByRole('button', { name: 'Replace goingg with going' }));
  expect(screen.getByRole('textbox')).toHaveValue('going going');
});
it('respects the animation prompt length limit', async () => {
  check.mockResolvedValue([{ word: 'goin', start: 0, end: 4, suggestions: ['going'] }]);
  const onChange = vi.fn();
  render(<PromptSpellingSuggestions value="goin" onChange={onChange} maxLength={4} />);
  fireEvent.click(screen.getByRole('button', { name: 'Check spelling' }));
  expect(await screen.findByRole('button', { name: 'Replace goin with going' })).toBeDisabled();
  expect(onChange).not.toHaveBeenCalled();
});
