import '@testing-library/jest-dom/vitest';
import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { GenerationProgressBar } from './GenerationProgressBar';

vi.mock('@/store/generationStore', () => ({ useGenerationStore: () => ({
  isActive: () => true, activeCount: () => 1, completedCount: () => 0,
  totalCount: () => 1, overallProgress: () => 10, projectId: 'project-a',
  buildings: new Map([['b', { buildingId:'b', buildingName:'House', status:'generating', step:'polling' }]]),
  cancelAll: vi.fn(), cancelOne: vi.fn(),
}) }));
afterEach(cleanup);
function Location() { return <output>{useLocation().pathname}</output>; }
it('opens the real project route and gives dismissal its own action', () => {
  render(<MemoryRouter initialEntries={['/projects']}><GenerationProgressBar /><Location /></MemoryRouter>);
  fireEvent.click(screen.getByRole('button', {name:'Open generation project'}));
  expect(screen.getByRole('status')).toHaveTextContent('/projects/project-a');
  fireEvent.click(screen.getByRole('button', {name:'Dismiss generation progress'}));
  expect(screen.queryByRole('button', {name:'Open generation project'})).not.toBeInTheDocument();
});
