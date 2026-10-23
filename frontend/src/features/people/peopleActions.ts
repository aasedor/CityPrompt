import { detailAsset, type DetailAsset } from '@/features/parks/detailCatalogue';

export const PEOPLE_ACTIONS = [
  { id: 'standing', label: 'Standing' }, { id: 'walking', label: 'Walking' },
  { id: 'running', label: 'Running' }, { id: 'sitting', label: 'Sitting' },
  { id: 'talking', label: 'Talking' }, { id: 'lying_down', label: 'Lying down' },
  { id: 'waving', label: 'Waving' }, { id: 'using_phone', label: 'Using a phone' },
  { id: 'reading', label: 'Reading' }, { id: 'waiting', label: 'Waiting' },
  { id: 'looking_around', label: 'Looking around' }, { id: 'pointing', label: 'Pointing' },
  { id: 'stretching', label: 'Stretching' }, { id: 'dancing', label: 'Dancing' },
  { id: 'cheering', label: 'Cheering' },
] as const;
export type PeopleActionId = typeof PEOPLE_ACTIONS[number]['id'];

export function peopleAction(value: unknown) {
  const action = PEOPLE_ACTIONS.find(item => item.id === (value ?? 'standing'));
  if (!action) throw new Error('Unknown person action. Choose an action from the People menu.');
  return action;
}

export const FIXED_PEOPLE_LIMITATION = 'Fixed pose. Move, rotate, duplicate or delete; motion is not animated in the 3D preview.';

export function isPeopleAsset(asset: DetailAsset | undefined): boolean {
  return !!(asset?.people || asset?.peopleRepresentation);
}

export function peopleActionsForAsset(asset: DetailAsset | undefined) {
  if (!isPeopleAsset(asset)) return [];
  const supported = asset?.peopleRepresentation?.supportedActions;
  return PEOPLE_ACTIONS.filter(action => !supported || supported.includes(action.id));
}

/** Defaults are asset-specific; unsupported fixed poses must never be persisted. */
export function peopleActionForAsset(asset: DetailAsset | undefined, value?: unknown) {
  if (!isPeopleAsset(asset)) throw new Error('This detail does not support person actions.');
  const action = peopleAction(value ?? asset?.peopleRepresentation?.defaultAction);
  if (!peopleActionsForAsset(asset).some(supported => supported.id === action.id)) {
    throw new Error('This action is not supported by this fixed pose. Choose its supported action.');
  }
  return action;
}

/** Bounded, conditional direction: saved actors never create offscreen extras. */
const PEOPLE_DIRECTION_PREFIX = 'Saved people direction (apply only to these actors when visible in the captured scene):';

/** Recovery replaces the generated suffix rather than accumulating inventories. */
export function withPeopleDirection(brief: string, direction: string): string {
  const suffix = brief.indexOf(`\n${PEOPLE_DIRECTION_PREFIX}`);
  const base = brief.startsWith(PEOPLE_DIRECTION_PREFIX) ? '' : suffix >= 0 ? brief.slice(0, suffix) : brief;
  return [base, direction].filter(Boolean).join('\n');
}

export function buildPeopleDirection(props: readonly { id?:string; variant: string; people_action?: PeopleActionId }[] = []): string {
  const counts = new Map<PeopleActionId, number>();
  const representations = new Map<string, { count: number; description: string; personCount: number }>();
  props.forEach(prop => {
    const asset = detailAsset(prop.variant);
    if (!isPeopleAsset(asset)) return;
    const action = peopleActionForAsset(asset, prop.people_action).id;
    const representation = asset.peopleRepresentation;
    // A group action identifies the authored pose, not every member's activity:
    // the standing stroller parent's infant must never be described as standing.
    if (!representation || representation.personCount === 1) counts.set(action, (counts.get(action) ?? 0) + 1);
    if (representation) representations.set(asset.id, {
      count: (representations.get(asset.id)?.count ?? 0) + 1,
      description: representation.description, personCount: representation.personCount,
    });
  });
  if (!counts.size && !representations.size) return '';
  const actionSummary = PEOPLE_ACTIONS.filter(action => counts.has(action.id)).map(action => `${counts.get(action.id)} ${action.label.toLowerCase()}`).join('; ');
  const representationSummary = [...representations].map(([id, row]) => `${row.count} × ${id}: ${row.description} (${row.personCount} ${row.personCount === 1 ? 'person' : 'people'} per representation; fixed pose)`).join('; ');
  return `${PEOPLE_DIRECTION_PREFIX}${actionSummary ? ` ${actionSummary}.` : ''}${representationSummary ? ` Authored representations: ${representationSummary}. Preserve the mobility aids, guide dog and family group arrangements present in each representation.` : ''} Preserve each person's saved position, appearance and scene support. Do not invent offscreen people or seats. These actions also apply when no additional people are requested.`;
}
