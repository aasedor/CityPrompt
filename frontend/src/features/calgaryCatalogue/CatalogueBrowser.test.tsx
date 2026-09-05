import { afterEach, describe, expect, it, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { CatalogueBrowserControls, useCatalogueBrowser } from './CatalogueBrowser';
import type { CalgaryBrowsable } from './guide';

afterEach(cleanup);
const options = Array.from({ length: 30 }, (_, index) => ({
  id: String(index), label: `Home ${index}`, categoryId: index < 20 ? 'modern' : 'heritage',
  calgaryGuide: { groupId: index < 20 ? 'detached' : 'ground_housing', basis: 'form_reference' as const },
}));
function BrowserTrial({ onSelect }: { onSelect: (option: CalgaryBrowsable) => void }) {
  const browser = useCatalogueBrowser(options);
  return <><CatalogueBrowserControls domain="building" categories={[{ id: 'modern', label: 'Modern' }, { id: 'heritage', label: 'Heritage' }]} {...browser.props} />
    <div data-testid="cards">{browser.options.slice(0, browser.limit).map(option => <button key={option.id} onClick={() => onSelect(option)}>{option.label}</button>)}</div>
    {browser.more}</>;
}
describe('Calgary browsing controls', () => {
  it('paginates, resets pagination on filters and leaves selection untouched while browsing', () => {
    const onSelect = vi.fn(); render(<BrowserTrial onSelect={onSelect} />);
    expect(screen.getByTestId('cards').children).toHaveLength(12);
    fireEvent.click(screen.getByRole('button', { name: /Show more choices/ }));
    expect(screen.getByTestId('cards').children).toHaveLength(24);
    fireEvent.change(screen.getByRole('combobox', { name: /Browse by purpose/ }), { target: { value: 'detached' } });
    expect(screen.getByTestId('cards').children).toHaveLength(12);
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'not a home' } });
    expect(screen.getByTestId('cards').children).toHaveLength(0);
    fireEvent.click(screen.getByRole('button', { name: 'Reset filters' }));
    expect(screen.getByTestId('cards').children).toHaveLength(12);
    expect(onSelect).not.toHaveBeenCalled();
  });
  it('combines a district search with appearance filters without silently widening the result', () => {
    render(<BrowserTrial onSelect={vi.fn()} />);
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'RC1' } });
    expect(screen.getByRole('status')).toHaveTextContent('20 choices');
    fireEvent.change(screen.getByLabelText('Appearance category'), { target: { value: 'heritage' } });
    expect(screen.getByRole('status')).toHaveTextContent('0 choices');
    fireEvent.click(screen.getByRole('button', { name: 'Reset filters' }));
    expect(screen.getByRole('status')).toHaveTextContent('30 choices');
  });
});
