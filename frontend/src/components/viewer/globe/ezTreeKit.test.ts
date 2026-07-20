import { describe, expect, it } from 'vitest';
import { resolveEzTreeStyle } from './ezTreeKit';

describe('resolveEzTreeStyle', () => {
  it('uses a compact ornamental stand for Japanese gardens', () => {
    expect(resolveEzTreeStyle('japanese_garden', 'japanese_stroll_garden')).toBe('ornamental');
  });

  it('uses a varied collection for botanical gardens', () => {
    expect(resolveEzTreeStyle('botanical_garden', 'garden_courtyard')).toBe('botanical');
  });

  it('uses mature stands for regional parks, forests, and naturalistic groves', () => {
    expect(resolveEzTreeStyle('regional_park', undefined)).toBe('woodland');
    expect(resolveEzTreeStyle('urban_forest', undefined)).toBe('woodland');
    expect(resolveEzTreeStyle('neighborhood_park', 'naturalistic_grove')).toBe('woodland');
  });

  it('uses a uniform formal palette for allees and civic planting', () => {
    expect(resolveEzTreeStyle('neighborhood_park', 'formal_allee')).toBe('formal');
    expect(resolveEzTreeStyle('formal_civic_plaza', 'paved_plaza')).toBe('formal');
  });

  it('keeps the Calgary-plausible mixed stand as the default', () => {
    expect(resolveEzTreeStyle('neighborhood_park', 'active_recreation')).toBe('temperate');
  });

  it('uses a deciduous riparian family for reservoir and wetland edges', () => {
    expect(resolveEzTreeStyle('reservoir_watershed_park', 'reservoir_perimeter')).toBe('riparian');
    expect(resolveEzTreeStyle('wetland_rain_garden', undefined)).toBe('riparian');
  });
});
