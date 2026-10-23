import { detailAsset } from '@/features/parks/detailCatalogue';

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

/** Bounded, conditional direction: saved actors never create offscreen extras. */
export function buildPeopleDirection(props: readonly { id?:string; variant: string; people_action?: PeopleActionId }[] = []): string {
  const counts = new Map<PeopleActionId, number>();
  props.forEach(prop => {
    if (!detailAsset(prop.variant)?.people) return;
    const action = peopleAction(prop.people_action).id;
    counts.set(action, (counts.get(action) ?? 0) + 1);
  });
  if (!counts.size) return '';
  return `Saved people direction (apply only to these actors when visible in the captured scene): ${PEOPLE_ACTIONS.filter(action => counts.has(action.id)).map(action => `${counts.get(action.id)} ${action.label.toLowerCase()}`).join('; ')}. Preserve each person's saved position, appearance and scene support. Do not invent offscreen people or seats. These actions also apply when no additional people are requested.`;
}
