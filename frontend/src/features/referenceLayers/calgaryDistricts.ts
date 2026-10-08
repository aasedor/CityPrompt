/** Published district identity is separate from a student's editable caption. */
export interface CalgaryDistrict {
  bylaw?: 'draft-2025';
  code?: string;
  designation: string;
  description?: string;
}

export const CALGARY_BYLAW = 'https://www.calgary.ca/planning/land-use/online-land-use-bylaw.html';

export function readCalgaryDistrict(value: unknown): CalgaryDistrict | undefined {
  if (!value || typeof value !== 'object') return undefined;
  const district = value as Record<string, unknown>;
  if (typeof district.designation !== 'string' || !district.designation.trim() || district.designation.length > 120) return undefined;
  if (district.code !== undefined && (typeof district.code !== 'string' || !district.code.trim() || district.code.length > 40)) return undefined;
  if (district.description !== undefined && (typeof district.description !== 'string' || district.description.length > 300)) return undefined;
  if (district.bylaw !== undefined && district.bylaw !== 'draft-2025') return undefined;
  return { ...(district.bylaw === 'draft-2025' ? { bylaw: 'draft-2025' as const } : {}), designation: district.designation.trim(),
    ...(typeof district.code === 'string' ? { code: district.code.trim() } : {}),
    ...(typeof district.description === 'string' && district.description.trim() ? { description: district.description.trim() } : {}),
  };
}

/** A small current list from the same City dataset as the site overlay.
 * DC is intentionally available only through a full designation copied from
 * the site: a generic DC choice would discard its individual bylaw reference.
 * These are published district references, not a development compliance test.
 */
export async function fetchCalgaryDistricts(signal: AbortSignal): Promise<CalgaryDistrict[]> {
  const query = new URLSearchParams({ '$select': 'lu_code,description', '$group': 'lu_code,description',
    '$where': "lu_code is not null AND lu_code != 'DC'", '$order': 'lu_code', '$limit': '257' });
  const response = await fetch(`https://data.calgary.ca/resource/qe6k-p9nh.json?${query}`, { signal });
  if (!response.ok) throw new Error('Calgary district choices could not load. Try again.');
  const rows: unknown = await response.json();
  if (!Array.isArray(rows) || !rows.length || rows.length > 256) throw new Error('Calgary returned an incomplete district list. Try again.');
  const districts = new Map<string, CalgaryDistrict>();
  for (const row of rows) {
    if (!row || typeof row !== 'object') throw new Error('Calgary returned an incomplete district list.');
    const district = readCalgaryDistrict({ code: row.lu_code, designation: row.lu_code, description: row.description });
    if (!district) throw new Error('Calgary returned a district without a valid code.');
    if (district.code === 'DC') continue;
    if (!districts.has(district.designation) || district.description) districts.set(district.designation, district);
  }
  return [...districts.values()];
}
