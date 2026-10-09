import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { DetailPlacementPanel } from './DetailPlacementPanel';
import { useDetailPlacement } from './useDetailPlacement';
import type { ProjectDetails } from './projectBenches';
// jsdom has no WebGL or intersection observer; placement, search and saving stay real.
vi.mock('./detailThumbnail', () => ({ detailThumbnail: async () => 'data:image/png;base64,preview' }));
afterEach(() => vi.unstubAllGlobals());
describe('detail catalogue workflow', () => {
  it('places and rotates traffic items without closing the category', async () => {
    vi.stubGlobal('IntersectionObserver', class { observe() {} disconnect() {} });
    const saved: ProjectDetails[] = [];
    function Trial() {
      const placement = useDetailPlacement({ version: 1, revision: 0, can_edit: true, benches: [] }, async next => {
        const result = { ...next, revision: next.revision + 1 }; saved.push(result); return result;
      });
      return <><DetailPlacementPanel placement={placement} canEdit onClose={() => {}} onArrange={() => {}} />
        <button onClick={() => void placement.place([-114, 51])}>Traffic placement ground</button></>;
    }
    render(<Trial />);
    fireEvent.change(screen.getByLabelText('Item category'), { target: { value: 'Traffic & safety' } });
    fireEvent.click(screen.getByRole('button', { name: 'Choose Traffic signal' }));
    fireEvent.change(screen.getByLabelText('Detail rotation'), { target: { value: '90' } });
    fireEvent.click(screen.getByText('Traffic placement ground'));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Traffic signal placed and saved'));
    expect(saved[0].props?.[0]).toMatchObject({ variant: 'detail-traffic-signal', angle: 90 });
    fireEvent.click(screen.getByRole('button', { name: 'Choose Speed hump' }));
    fireEvent.click(screen.getByText('Traffic placement ground'));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Speed hump placed and saved'));
    expect(saved[1].props).toHaveLength(2);
    expect(screen.getByLabelText('Item category')).toHaveValue('Traffic & safety');
  });
  it('keeps the picker and filter open after placing different items', async () => {
    vi.stubGlobal('IntersectionObserver', class { observe() {} disconnect() {} });
    const saved: ProjectDetails[] = [];
    function Trial() {
      const placement = useDetailPlacement({ version: 1, revision: 0, can_edit: true, benches: [] }, async next => {
        const result = { ...next, revision: next.revision + 1 }; saved.push(result); return result;
      });
      return <><DetailPlacementPanel placement={placement} canEdit onClose={() => {}} onArrange={() => {}} />
        <button onClick={() => void placement.place([-114, 51])}>Map ground</button></>;
    }
    render(<Trial />);
    fireEvent.change(screen.getByLabelText('Item category'), { target: { value: 'Seating' } });
    fireEvent.click(screen.getByRole('button', { name: 'Choose Timber bench' }));
    fireEvent.click(screen.getByText('Map ground'));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Timber bench placed and saved'));
    expect(screen.getByRole('complementary', { name: 'Detail catalogue' })).toBeVisible();
    expect(screen.getByLabelText('Item category')).toHaveValue('Seating');
    fireEvent.click(screen.getByRole('button', { name: 'Choose Accessible picnic table' }));
    fireEvent.click(screen.getByText('Map ground'));
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Accessible picnic table placed and saved'));
    expect(saved[1].benches).toHaveLength(1);
    expect(saved[1].props?.[0].variant).toBe('picnic-table-accessible');
  });
});
