import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { CanonicalCatalogueCard } from '@/features/pickPlace/CanonicalCatalogueCard';
import { CANONICAL_CHOICES } from '@/features/pickPlace/canonicalCatalogue';

it('explains a style and cites its source without selecting the building',()=>{
  const choice=CANONICAL_CHOICES.find(c=>c.placements[0]?.id==='clay_neoclassical_brick_headquarters')!;
  const onPlacement=vi.fn();
  render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={onPlacement} onDraw={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button',{name:/Expand details for/}));
  expect(screen.getByRole('region',{name:'Architecture and planning'})).toHaveTextContent(/symmetry/i);
  fireEvent.click(screen.getByText('Learn more / sources'));
  expect(screen.getByRole('link',{name:'RIBA: Neoclassicism'})).toHaveAttribute('href','https://www.riba.org/explore/riba-collections/architectural-styles/neoclassical-movement/');
  expect(onPlacement).not.toHaveBeenCalled();
});

it('holds a contradictory reference without displaying its proposed style as settled',()=>{
  const choice=CANONICAL_CHOICES.find(c=>c.placements[0]?.id==='community_inglewood_corner_merchants')!;
  render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={vi.fn()} onDraw={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button',{name:/Expand details for/}));
  expect(screen.getByRole('region',{name:'Architecture and planning'})).toHaveTextContent(/Style to be confirmed/);
  expect(screen.queryByRole('heading',{name:'Italianate'})).not.toBeInTheDocument();
});

it('does not show the old lesson when a model revision has changed',()=>{
  const original=CANONICAL_CHOICES.find(c=>c.placements[0]?.id==='clay_neoclassical_brick_headquarters')!;
  const choice={...original,placements:original.placements.map(a=>({...a,model:{...a.model,revision:'changed-after-review'}}))};
  render(<CanonicalCatalogueCard choice={choice} selected={null} onPlacement={vi.fn()} onDraw={vi.fn()}/>);
  fireEvent.click(screen.getByRole('button',{name:/Expand details for/}));
  expect(screen.getByRole('region',{name:'Architecture and planning'})).toHaveTextContent(/fresh review/i);
  expect(screen.queryByRole('link',{name:'RIBA: Neoclassicism'})).not.toBeInTheDocument();
});
