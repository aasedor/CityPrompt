import '@testing-library/jest-dom/vitest';
import {render, screen, waitFor} from '@testing-library/react';
import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import {expect, it, vi} from 'vitest';
import {ExistingLandUse} from './ExistingLandUse';
import type {Position} from './zoningLabels';

it('shows official site districts without authoring controls and previews their actual outlines', async () => {
  const boundary: Position[] = [[-114.07,51.04],[-114.069,51.04],[-114.069,51.041],[-114.07,51.041]];
  const mapDrawing = {begin:vi.fn(), cancel:vi.fn(), preview:vi.fn()};
  const data = {loadedAt:'2026-10-26',bounds:[-114.07,51.04,-114.069,51.041] as [number,number,number,number],
    districts:[{id:'city',label:'C-COR1',code:'C-COR1',description:'Commercial - Corridor 1',anchor:boundary[0],polygon:[[...boundary,boundary[0]]]}]};
  render(<QueryClientProvider client={new QueryClient()}><ExistingLandUse projectId="test" boundary={boundary} data={data} mapDrawing={mapDrawing}/></QueryClientProvider>);
  expect(await screen.findByText('C-COR1')).toBeInTheDocument();
  expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
  expect(screen.queryByRole('button',{name:/save|draw|remove/i})).not.toBeInTheDocument();
  await waitFor(() => expect(mapDrawing.preview).toHaveBeenCalledWith(expect.objectContaining({feature_count:1})));
  expect(mapDrawing.begin).not.toHaveBeenCalled();
});
