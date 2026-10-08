import type { ReportSource } from './studentReportsApi';
import { matchLocalAreaPlans, loadLocalAreaPlan } from '@/features/policyPlans/localAreaPlans';
import { selectPolicySite } from '@/features/policyPlans/rileyPolicy';
import type { SiteZone } from '@/types';
import type { ReferenceLayer } from '@/features/referenceLayers/api';
import type { StudentFinding } from './studentReportsApi';
export interface PolicyMapEvidence {
  boundary_coordinates: number[][];
  sources: ReportSource[];
  comparisons?: StudentFinding[];
  design_inputs?: {
    zones: { id: string; coordinates: number[][]; properties: SiteZone['properties'] }[];
    references: { id: string; content_hash?: string; feature_collection?: ReferenceLayer['feature_collection'] }[];
  };
}

export async function collectPolicyMapEvidence(coordinates: number[][], zones?: SiteZone[], layers: ReferenceLayer[] = []): Promise<PolicyMapEvidence> {
  if (coordinates.length < 3) return { boundary_coordinates: coordinates, sources: [] };
  const comparison = zones ? await import('./planComparisons') : undefined;
  const comparisons: StudentFinding[] = comparison ? comparison.compareProposedZoning(zones!, layers) : [];
  const compared = new Set<string>();
  // Use the report's site, not the last map clicked elsewhere in the city.
  const batches = await Promise.all(matchLocalAreaPlans(coordinates).matches.map(async plan => {
    try {
      const selection = selectPolicySite(await loadLocalAreaPlan(plan.id), coordinates);
      const categories = new Set(selection.features.map(feature => feature.properties.category));
      if (comparison) for (const zone of comparison.comparisonObjects(zones!)) {
        for (const designation of plan.designations) {
          const polygons = selection.features.filter(feature => feature.properties.category === designation.name).map(feature => feature.geometry.coordinates);
          const coverage = comparison.overlap(comparison.plot(zone), polygons);
          if (coverage <= 0.001) continue;
          compared.add(zone.id);
          const result = comparison.comparePolicyIntent(zone, designation.name);
          comparisons.push(comparison.comparisonFinding(zone, `policy-${zone.id}-${plan.id}-${designation.name}`, {
            group:'local_plan',status:result.status,
            expected:`${plan.title} · ${designation.name}. ${designation.summary}`,
            proposed:`${comparison.describeProposal(zone).description} Approximately ${(coverage*100).toFixed(0)}% of its placement plot intersects this designation.`,
          }, result.reason, [{title:`${plan.title}: ${designation.name}`,url:plan.source,page:designation.page,section:designation.section,
            excerpt:`${plan.edition}. ${designation.summary} ${designation.considerations.join(' ')}`} ]));
        }
      }
      return plan.designations.filter(item => categories.has(item.name)).map(designation => ({
        title: `${plan.title}: ${designation.name}`, url: plan.source,
        page: designation.page, section: designation.section,
        excerpt: `${plan.edition} · map snapshot ${plan.snapshot}. ${designation.summary} ${designation.considerations.join(' ')} Urban Form is policy context, not statutory zoning or a compliance verdict.`,
      }));
    } catch {
      return [{ title: `${plan.title}: map evidence unavailable`, url: plan.source,
        excerpt: `${plan.edition}. The map could not be loaded for this report; consult the linked plan. No designation has been inferred.` }];
    }
  }));
  const sources: ReportSource[] = batches.flat().slice(0, 64);
  if (comparison) for (const zone of comparison.comparisonObjects(zones!)) {
    if (!compared.has(zone.id)) comparisons.push(comparison.comparisonFinding(zone, `policy-unavailable-${zone.id}`, {
      group:'local_plan',status:'review',expected:'A local-plan designation at this location.',proposed:zone.name || zone.zone_type,
    }, 'No usable local-plan polygon covers this object in the loaded collection. Consult the plan directly; absence of coverage is not policy approval.'));
  }
  return { boundary_coordinates: coordinates, sources, ...(zones ? {
    comparisons: comparisons.sort((a,b) => a.id.localeCompare(b.id)),
    design_inputs: {
      zones: zones.map(zone => ({id:zone.id,coordinates:zone.coordinates,properties:zone.properties ?? {}})),
      references: layers.map(layer => ({id:layer.id,...(layer.content_hash ? {content_hash:layer.content_hash} : {feature_collection:layer.feature_collection})})),
    },
  } : {}) };
}
