/**
 * Authored archetype artwork for Direct 3D renders.
 *
 * Collects per-building style references — the compiler's facade elevation
 * sheets first (binding design sources), catalogue hero cards otherwise — and
 * labels each with the building it styles plus the authored family identity.
 * The backend attaches them to the provider call after the metadata passes
 * and instructs the model to apply them to the named buildings.
 */
import type { SiteZone } from '@/types';
import buildingCatalog from '@/data/buildingArchetypes.json';
import legoFamilySignatures from '@/data/legoFamilySignatures.json';

export interface Direct3DArchetypeReference {
  image_base64: string;
  label: string;
}

interface FamilySignature {
  archetypeId?: string;
  identity?: string;
  materialZones?: string;
  elevationUrl?: string;
}

interface CatalogEntry {
  id?: string;
  title?: string;
  thumbnailUrl?: string;
}

const FAMILIES: Record<string, FamilySignature> =
  (legoFamilySignatures as { families?: Record<string, FamilySignature> }).families ?? {};

const CATALOG: CatalogEntry[] =
  (buildingCatalog as { archetypes?: CatalogEntry[] }).archetypes ?? [];

/** Server-side schema cap is 8; leave headroom for future street/park refs. */
const MAX_REFERENCES = 6;
const MAX_LABEL_LENGTH = 600;

/** Planner cards store `<archetype>_variant_<n>`; the suffix picks artwork,
 *  not a different family. Mirrors the backend/LEGO matching rule. */
function stripCardVariantSuffix(id: string): string {
  return id.replace(/_(?:variant_|v)\d+$/, '');
}

async function fetchImageBase64(url: string): Promise<string | null> {
  try {
    const response = await fetch(url);
    if (!response.ok) return null;
    const blob = await response.blob();
    // Dev servers answer missing files with 200 + an HTML fallback page;
    // forwarding those bytes as an image poisons the provider request.
    if (!blob.type.startsWith('image/')) {
      console.warn(`[Direct3D refs] Skipping non-image response (${blob.type || 'unknown'}):`, url);
      return null;
    }
    return await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.includes(',') ? dataUrl.split(',')[1] : null);
      };
      reader.onerror = () => resolve(null);
      reader.readAsDataURL(blob);
    });
  } catch (err) {
    console.warn('[Direct3D refs] Failed to fetch reference image:', url, err);
    return null;
  }
}

function clampLabel(label: string): string {
  return label.length <= MAX_LABEL_LENGTH ? label : `${label.slice(0, MAX_LABEL_LENGTH - 1)}…`;
}

/** Collect authored style references for the building zones in a capture. */
export async function collectDirect3DArchetypeReferences(
  zones: SiteZone[],
  limit: number = MAX_REFERENCES,
): Promise<Direct3DArchetypeReference[]> {
  // Group building zones by resolved archetype so a repeated family attaches
  // one reference naming every building it styles.
  const byArchetype = new Map<string, { rawId: string; zoneNames: string[] }>();
  for (const zone of zones) {
    if (zone.zone_type !== 'building') continue;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const props: any = zone.properties || {};
    const rawId = props.development_archetype_id || props.archetype_id;
    if (!rawId) continue;
    const baseId = stripCardVariantSuffix(String(rawId));
    const entry = byArchetype.get(baseId) ?? { rawId: String(rawId), zoneNames: [] };
    if (zone.name && entry.zoneNames.length < 3) entry.zoneNames.push(zone.name);
    byArchetype.set(baseId, entry);
  }

  const references: Direct3DArchetypeReference[] = [];
  for (const [baseId, { rawId, zoneNames }] of byArchetype) {
    if (references.length >= limit) break;
    const signature = FAMILIES[baseId] ?? FAMILIES[rawId] ?? null;
    const catalogEntry = CATALOG.find((c) => c.id === baseId)
      ?? CATALOG.find((c) => c.id === rawId)
      ?? null;
    const title = catalogEntry?.title || baseId.replace(/_/g, ' ');
    const buildingClause = zoneNames.length
      ? ` for the building(s) named ${zoneNames.map((n) => `"${n}"`).join(', ')}`
      : '';
    const identityClause = signature?.identity
      ? ` AUTHORED IDENTITY (binding): ${signature.identity}${signature.materialZones ? ` Materials: ${signature.materialZones}.` : ''}`
      : '';

    if (signature?.elevationUrl) {
      const facade = await fetchImageBase64(signature.elevationUrl);
      if (facade) {
        references.push({
          image_base64: facade,
          label: clampLabel(
            `FACADE SOURCE — ${title}${buildingClause}: authored facade elevation. `
            + 'Reproduce this exact facade system — bay rhythm, opening proportions, '
            + `coursing, cornice and materials — on the matching building.${identityClause}`,
          ),
        });
        continue;
      }
    }
    if (catalogEntry?.thumbnailUrl) {
      const card = await fetchImageBase64(catalogEntry.thumbnailUrl);
      if (card) {
        references.push({
          image_base64: card,
          label: clampLabel(
            `STYLE REFERENCE — ${title}${buildingClause}: apply this archetype's `
            + `materials, facade character and detailing to the matching building.${identityClause}`,
          ),
        });
      }
    }
  }
  return references;
}
