import { GROUND_SURFACES } from '@/features/groundSurfaces/groundSurfaces';

export const DEFAULT_SITE_BOUNDARY_COLOUR = '#668545';

export const SITE_BOUNDARY_SURFACE_OPTIONS = [
  { id: 'default', label: 'Default' },
  { id: 'earth', label: 'Bare earth' },
  ...GROUND_SURFACES,
  { id: 'custom', label: 'Custom colour' },
];

const DEFAULT_SURFACE = { kind: 'default', id: 'default' } as const;

export function resolveSiteBoundarySurface(value: unknown) {
  if (typeof value !== 'string' || value === 'default') return DEFAULT_SURFACE;
  if (/^#[0-9a-f]{6}$/i.test(value)) return { kind: 'colour', id: value.toLowerCase() } as const;
  if (value === 'earth') return { kind: 'earth', id: value } as const;
  const material = GROUND_SURFACES.find((surface) => surface.id === value);
  return material ? { kind: 'material', id: material.id, material } as const : DEFAULT_SURFACE;
}
