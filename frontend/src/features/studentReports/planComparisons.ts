import clipping, { type Polygon, type MultiPolygon } from 'polygon-clipping';
import type { SiteZone } from '@/types';
import type { ReferenceLayer } from '@/features/referenceLayers/api';
import { studyMetadata, studyZones } from '@/features/referenceLayers/zoningStudy';
import { assetForZone } from '@/features/pickPlace/catalogue';
import { BUILDING_PROGRAMS, PARK_PROGRAMS, matchBuilding, matchPark, rulesForZone, RULES_REVIEWED_AT } from '@/features/zoningCatalogue/matching';
import type { ZoneInspection } from '@/features/zoningCatalogue/types';
import type { StudentFinding, ReportSource } from './studentReportsApi';

export type Comparison = { group: 'local_plan' | 'proposed_zoning'; status: 'permitted' | 'discretionary' | 'review' | 'potential_conflict'; expected: string; proposed: string };
export const comparisonObjects = (zones: SiteZone[]) => zones.filter(zone =>
  ['building', 'residential', 'development_area', 'green_space'].includes(zone.zone_type)
  && !zone.properties?.is_reference && zone.properties?._layer_role !== 'reference');
export const plot = (zone: SiteZone): Polygon => [zone.coordinates.map(([x,y]) => [x,y])];

function area(polygons: MultiPolygon): number {
  const ringArea = (ring: number[][]) => {
    const [x,y] = ring[0];
    return Math.abs(ring.reduce((sum, p, i) => {
      const next = ring[(i+1)%ring.length];
      return sum+(p[0]-x)*(next[1]-y)-(next[0]-x)*(p[1]-y);
    },0)/2);
  };
  return polygons.reduce((sum, polygon) => sum + ringArea(polygon[0]) - polygon.slice(1).reduce((holes, ring) => holes + ringArea(ring), 0),0);
}
export function overlap(plotShape: Polygon, polygons: Polygon[]): number {
  if (!polygons.length) return 0;
  const total = area([plotShape]);
  return total > 0 ? area(clipping.intersection(plotShape, clipping.union(polygons[0], ...polygons.slice(1)))) / total : 0;
}

function programme(zone: SiteZone) {
  const asset = assetForZone(zone);
  const candidate = asset && (asset.zoneType === 'green_space' ? PARK_PROGRAMS[asset.id] : BUILDING_PROGRAMS[asset.model.variantId]);
  const program = candidate?.revision === asset?.model.revision ? candidate : undefined;
  return { asset, program, description: program?.assumption || 'No reviewed use programme for this saved model.' };
}

export function describeProposal(zone: SiteZone) {
  const { asset, description } = programme(zone);
  const label = zone.name && !['building','green space','green_space','residential','development area'].includes(zone.name.toLowerCase())
    ? zone.name : asset?.label || zone.zone_type;
  return { label, description };
}

export function comparisonFinding(zone: SiteZone, id: string, comparison: Comparison, reason: string, sources: ReportSource[] = []): StudentFinding {
  return {
    id, comparison, kind: comparison.status === 'potential_conflict' ? 'unresolved_question' : 'source_context',
    title: `${comparison.group === 'local_plan' ? 'Local area plan' : 'Proposed zoning'} · ${describeProposal(zone).label}`,
    observation: reason,
    recommendation: comparison.group === 'local_plan'
      ? 'Explain how the design supports this policy intent, or justify the departure and identify any plan amendment or further policy review needed.'
      : 'Keep or adjust the design and district, or explain the proposed relaxation/amendment. Discretionary uses and relaxations require assessment; they are not automatic approvals.',
    basis: 'Client-derived spatial comparison of saved placement plots, exact catalogue programmes and sourced map/rule snapshots.',
    uncertainty: 'Placement plots include yards. This is preliminary use/height screening, not a permit assessment. Setbacks, density, parking, parcel rules and exceptions need separate review. Urban Form does not establish a building-scale limit.',
    location: { label: describeProposal(zone).label, zone_ids: [zone.id] }, sources,
  };
}

export function comparePolicyIntent(zone: SiteZone, category: string) {
  const { program } = programme(zone);
  const uses = program?.components.flat().join(' ') ?? '';
  const housing = /Dwelling|Residential|Housing/i.test(uses);
  const recreationLand = ['City Civic and Recreation','Private Institutional and Recreation','Parks and Open Space','Natural Areas'].includes(category);
  const conflict = (housing && recreationLand) || (category === 'Natural Areas' && zone.zone_type === 'building')
    || (housing && category === 'Industrial Heavy');
  return { status: conflict ? 'potential_conflict' as const : 'review' as const,
    reason: conflict ? `Potential departure: this proposal introduces ${housing ? 'housing' : 'a building'} on ${category} land. Check whether supporting uses or site-specific exceptions apply; otherwise explain the policy change needed.`
      : `Compare the proposed programme with ${category} policy intent. Confirm the mix of uses, frontage, public access and site-specific policies; no automatic alignment verdict is inferred from the colour.` };
}

export function compareProposedZoning(zones: SiteZone[], layers: ReferenceLayer[]): StudentFinding[] {
  const districts = layers.filter(layer => studyMetadata(layer)?.condition === 'proposed')
    .flatMap(layer => studyZones(layer).map(zone => ({ zone, layer })));
  return comparisonObjects(zones).flatMap(object => {
    const shape = plot(object);
    const hits = districts.filter(({ zone }) => overlap(shape, [zone.rings]) > 0.001);
    const { asset, description } = programme(object);
    if (!hits.length) return [comparisonFinding(object, `zoning-unassigned-${object.id}`, {
      group:'proposed_zoning', status:'review', expected:'No saved proposed district covers this plot.', proposed:description,
    }, 'Assign a proposed district before comparing this object. Unsaved zoning drafts are not included.')];
    const results = hits.map(({ zone, layer }) => {
      const inspection: ZoneInspection = {id:zone.id,label:zone.label,source:layer.name,custom:zone.custom,district:zone.district};
      const matched = asset && (asset.zoneType === 'green_space' ? matchPark(asset, inspection) : matchBuilding(asset, inspection));
      const rule = rulesForZone(inspection);
      const override = Number(object.properties?.development_height_override_m);
      const nativeHeight = asset?.nativeDimensions?.[2];
      const changedHeight = Number.isFinite(override) && override > 0 && override !== nativeHeight;
      const status = matched?.status === 'outside' ? 'potential_conflict' : changedHeight ? 'review' : matched?.status ?? 'review';
      const height = matched?.height;
      return comparisonFinding(object, `zoning-${object.id}-${layer.id}-${zone.id}`, {
        group:'proposed_zoning', status,
        expected: `${zone.custom ? 'Custom zone' : zone.district?.designation ?? 'Unassigned district'} · ${layer.name}${matched?.limit != null ? ` · height screen ${matched.limit} m` : ''}`,
        proposed: `${description}${height != null ? ` Catalogue envelope ${height.toFixed(1)} m.` : ''}${changedHeight ? ` Saved height override ${override} m requires a fresh check.` : ''}`,
      }, [matched?.uses.map(use => `${use.use}: ${use.category} (§${use.section})`).join('; '), ...(matched?.reasons ?? ['No reviewed classification for this saved model.']),
        changedHeight ? 'Changed building height has not been certified by the catalogue match.' : '',
        `Overlaps approximately ${(overlap(shape,[zone.rings])*100).toFixed(0)}% of the placement plot.`].filter(Boolean).join(' '),
      rule ? [{title:`Calgary ${rule.code} use and height screening`,url:rule.rule.source,section:rule.rule.height.section,
        excerpt:`Rules reviewed ${RULES_REVIEWED_AT}. ${rule.rule.height.note}`} ] : []);
    });
    if (hits.length > 1 || overlap(shape, hits.map(hit => hit.zone.rings)) < 0.999) {
      const finding = comparisonFinding(object, `zoning-boundary-${object.id}`, {
        group:'proposed_zoning',status:'review',expected:'A clearly assigned proposed district across the placement plot.',proposed:description,
      }, 'The plot crosses a district boundary, overlaps multiple study zones, or is partly unzoned. Review each intersected district; the centroid is not used to select one winning zone.');
      finding.title = `Proposed zoning boundary · ${object.name || asset?.label || object.zone_type}`;
      results.unshift(finding);
    }
    return results;
  });
}
