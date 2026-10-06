import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { CatalogueMatches, ZoningCatalogueCard } from './ZoningCatalogueCard';
import type { ZoneInspection } from './types';

const zone = (designation: string): ZoneInspection => ({ id: 'zone', label: 'Homes', source: 'Proposed land-use study', district: { designation } });

describe('zoning catalogue panel', () => {
  it('updates both lists when a student rezones, preserving the correct bylaw links', () => {
    const { rerender } = render(<CatalogueMatches zone={zone('R-CG')} />);
    expect(screen.getByRole('heading', { name: 'Discretionary use candidates (6)' })).toBeInTheDocument();
    const list = screen.getByRole('region', { name: 'Discretionary use candidates' });
    expect(within(list).getByRole('heading', { name: 'Juniper Courtyard Cottages' })).toBeInTheDocument();
    expect(within(list).getByRole('link', { name: 'Semi-detached Dwelling · s.527(2)' })).toHaveAttribute('href', expect.stringContaining('#section527'));
    rerender(<CatalogueMatches zone={zone('R-G')} />);
    expect(screen.getByRole('heading', { name: 'Permitted use candidates (10)' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Discretionary use candidates (0)' })).toBeInTheDocument();
  });
  it('shows the declared program, conditions and evidence alongside the actual use definition', () => {
    render(<CatalogueMatches zone={zone('R-G')} />);
    const list = screen.getByRole('region', { name: 'Permitted use candidates' });
    const row = within(list).getByRole('heading', { name: 'Charcoal Gable Fourplex' }).closest('li')!;
    expect(within(row).getByText(/Classroom program: four side-by-side/)).toBeInTheDocument();
    expect(within(row).getByText(/every home must face a public street/)).toBeInTheDocument();
    fireEvent.click(within(row).getByText('Classroom program · basis'));
    expect(row.querySelector('details')).toHaveAttribute('open');
    expect(within(row).getByRole('link', { name: 'What “Rowhouse Building” means · s.287' })).toHaveAttribute('href', expect.stringContaining('#section287'));
  });
  it('focuses on selection and supports Escape and the close button', () => {
    const close = vi.fn();
    const { rerender } = render(<ZoningCatalogueCard zone={zone('M-C1')} onClose={close} />);
    const panel = screen.getByRole('region', { name: 'M-C1' });
    expect(panel).toHaveFocus();
    fireEvent.keyDown(panel, { key: 'Escape' });
    expect(close).toHaveBeenCalledOnce();
    fireEvent.click(screen.getByRole('button', { name: 'Close zoning catalogue' }));
    expect(close).toHaveBeenCalledTimes(2);
    rerender(<ZoningCatalogueCard zone={null} onClose={close} />);
    expect(screen.queryByRole('region', { name: 'M-C1' })).not.toBeInTheDocument();
  });
  it('explains custom and Direct Control designations without fabricated matches', () => {
    const { rerender } = render(<CatalogueMatches zone={zone('DC106Z82')} />);
    expect(screen.getByText(/Direct Control districts have their own rules/)).toBeInTheDocument();
    expect(screen.queryByRole('region', { name: 'Permitted use candidates' })).not.toBeInTheDocument();
    rerender(<CatalogueMatches zone={{ ...zone('R-G'), custom: true }} />);
    expect(screen.getByText(/This is a custom zone/)).toBeInTheDocument();
  });
  it('keeps missing thumbnails from becoming broken-image cards', () => {
    const { container } = render(<CatalogueMatches zone={zone('R-G')} />);
    const img = container.querySelector('img')!;
    const label = img.closest('li')!.querySelector('h4')!.textContent!;
    fireEvent.error(img);
    expect(screen.getByLabelText('Preview unavailable')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: label })).toBeInTheDocument();
  });
  it('opens park districts on the park list with cited use definitions and an explicit height scope', () => {
    render(<CatalogueMatches zone={zone('S-SPR')} />);
    expect(screen.getByRole('button', { name: 'Parks (32)' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('heading', { name: 'Permitted use candidates (30)' })).toBeInTheDocument();
    expect(screen.getByText(/Land use only\. Buildings, shelters/)).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: 'What “Park” means · s.249' })[0]).toHaveAttribute('href', expect.stringContaining('&alpha=P#section249'));
    expect(screen.getAllByRole('link', { name: 'What “Outdoor Recreation Area” means · s.248' })[0]).toHaveAttribute('href', expect.stringContaining('&alpha=O#section248'));
    expect(screen.queryByText('Height unverified')).not.toBeInTheDocument();
  });
  it('updates park permission lists on rezoning and keeps buildings separately selectable', () => {
    const { rerender } = render(<CatalogueMatches zone={zone('R-CG')} />);
    fireEvent.click(screen.getByRole('button', { name: 'Parks (32)' }));
    expect(screen.getByRole('heading', { name: 'Permitted use candidates (26)' })).toBeInTheDocument();
    rerender(<CatalogueMatches zone={zone('S-R')} />);
    expect(screen.getByRole('heading', { name: 'Discretionary use candidates (5)' })).toBeInTheDocument();
    const discretionary = screen.getByRole('region', { name: 'Discretionary use candidates' });
    expect(within(discretionary).getByRole('heading', { name: 'Basketball park' })).toBeInTheDocument();
    expect(within(discretionary).getByRole('heading', { name: 'Terraced performance lawn' })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^Buildings \(\d+\)$/ }));
    expect(screen.queryByRole('heading', { name: 'Basketball park' })).not.toBeInTheDocument();
  });
});
