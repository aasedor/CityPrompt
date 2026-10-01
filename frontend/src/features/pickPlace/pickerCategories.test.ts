import { describe, expect, it } from 'vitest';
import { CLASSROOM_CHOICES } from './canonicalCatalogue';
import { PICKER_CATEGORIES, availablePickerCategories, pickerCategory } from './pickerCategories';

describe('student picker categories', () => {
  it('assigns each exact model to one visible category in its own section', () => {
    for (const choice of CLASSROOM_CHOICES) {
      const id=pickerCategory(choice);
      expect(PICKER_CATEGORIES.filter(c=>c.id===id && c.domain===choice.domain)).toHaveLength(1);
      expect(availablePickerCategories(choice.domain,CLASSROOM_CHOICES).some(c=>c.id===id)).toBe(true);
    }
    expect(availablePickerCategories('building',[])).toEqual([]);
  });
  it.each([
    ['infill_duplex','low-density'], ['clapboard_north_end','low-density'],
    ['med_villa_tuscan','low-density'], ['nordic_timber_mass_timber','apartments'],
    ['glass_tower_blue_reflective','towers'], ['vancouverism_classic','towers'],
    ['deco_theater_movie_palace','civic'], ['student_pickleball_garden_v1','play-sport'],
    ['student_stone_labyrinth_garden_v1','gardens'], ['wetland_rain_garden_v0','nature-trails'],
    ['student_grass_tram_avenue_v1','transit'], ['student_london_cobbled_mews_v1','alleys'],
    ['student_barcelona_shaded_promenade_v1','walking-cycling'],
    ['student_elevated_garden_rail_v1','transit'],
  ])('places %s in %s without changing its binding', (variant,category) => {
    const choice=CLASSROOM_CHOICES.find(c=>c.placements[0]?.model.variantId===variant)!;
    const original=JSON.stringify(choice);
    expect(pickerCategory(choice)).toBe(category);
    expect(JSON.stringify(choice)).toBe(original);
  });
});
