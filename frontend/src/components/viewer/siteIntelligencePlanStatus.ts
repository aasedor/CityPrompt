export type ScenarioPlanStatusSnapshot = ReadonlyMap<string, string | undefined>;

interface ScenarioWithPlanPayload {
  id: string;
  payload?: unknown;
}

function planStatusOf(payload: unknown): string | undefined {
  if (!payload || typeof payload !== 'object') return undefined;
  const plan = (payload as { plan?: unknown }).plan;
  if (!plan || typeof plan !== 'object') return undefined;
  const status = (plan as { status?: unknown }).status;
  return typeof status === 'string' ? status : undefined;
}

export function snapshotScenarioPlanStatuses(
  scenarios: readonly ScenarioWithPlanPayload[],
): ScenarioPlanStatusSnapshot {
  return new Map(scenarios.map((scenario) => [scenario.id, planStatusOf(scenario.payload)]));
}

/**
 * Detect a real transition into `complete` for a scenario that existed in the
 * previous poll. Stable IDs keep list insertion, deletion, and reordering from
 * being mistaken for plan completion.
 */
export function hasScenarioPlanCompleted(
  previous: ScenarioPlanStatusSnapshot | null,
  current: ScenarioPlanStatusSnapshot,
): boolean {
  if (!previous) return false;
  for (const [scenarioId, status] of current) {
    if (
      status === 'complete'
      && previous.has(scenarioId)
      && previous.get(scenarioId) !== 'complete'
    ) {
      return true;
    }
  }
  return false;
}
