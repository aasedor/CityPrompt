import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { CatalogueMatches, ZoningCatalogueCard } from './ZoningCatalogueCard';
import type { ZoneInspection } from './types';

const zone = (designation: string): ZoneInspection => ({ id: 'zone', label: 'Homes', source: 'Proposed land-use study', district: { designation } });

describe('zoning catalogue panel', () => {
  it('updates both lists when a student rezones, preserving the correct bylaw links', () => {
    const { rerender } = render(<CatalogueMatches zone={zone('R-CG')} />);
    expect(screen.getByRole('heading', { name: 'Discretionary use candidates (4)' })).toBeInTheDocument();
    const list = screen.getByRole('region', { name: 'Discretionary use candidates' });
    expect(within(list).getByRole('link', { name: 'Semi-detached Dwelling · s.527(2)' })).toHaveAttribute('href', expect.stringContaining('#section527'));
    rerender(<CatalogueMatches zone={zone('R-G')} />);
    expect(screen.getByRole('heading', { name: 'Permitted use candidates (8)' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Discretionary use candidates (0)' })).toBeInTheDocument();
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
});
