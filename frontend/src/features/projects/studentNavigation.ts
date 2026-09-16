import type { CityPromptWorkflowState } from '@/features/workflow/cityPromptWorkflow';

/** A saved design can predate site boundaries; opening it must not imply a reset. */
export function defaultStudentStep(workflow: Pick<CityPromptWorkflowState, 'activeBoundary' | 'physicalZones'>): 'site' | 'design' {
  return workflow.activeBoundary || workflow.physicalZones.length > 0 ? 'design' : 'site';
}
