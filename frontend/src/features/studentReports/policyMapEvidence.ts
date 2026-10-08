import type { ReportSource } from './studentReportsApi';
import { matchLocalAreaPlans, loadLocalAreaPlan } from '@/features/policyPlans/localAreaPlans';
import { selectPolicySite } from '@/features/policyPlans/rileyPolicy';
export interface PolicyMapEvidence {
  boundary_coordinates: number[][];
  sources: ReportSource[];
}

export async function collectPolicyMapEvidence(coordinates: number[][]): Promise<PolicyMapEvidence> {
  if (coordinates.length < 3) return { boundary_coordinates: coordinates, sources: [] };
  // Use the report's site, not the last map clicked elsewhere in the city.
  const batches = await Promise.all(matchLocalAreaPlans(coordinates).matches.map(async plan => {
    try {
      const selection = selectPolicySite(await loadLocalAreaPlan(plan.id), coordinates);
      const categories = new Set(selection.features.map(feature => feature.properties.category));
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
  return { boundary_coordinates: coordinates, sources };
}
