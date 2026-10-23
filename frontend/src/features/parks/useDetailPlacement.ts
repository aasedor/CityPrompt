import { useEffect, useRef, useState } from 'react';
import { detailAsset, type DetailAssetId } from './detailCatalogue';
import type { ProjectDetails, ProjectBench } from './projectBenches';
import { useUndoRedoStore } from '@/store/undoRedo';
import type { DetailPose, DetailSupport } from './safetyPlacement';
import { isPeopleAsset, peopleActionForAsset, type PeopleActionId } from '@/features/people/peopleActions';

type ItemCollection = 'benches' | 'trees' | 'props';
/** Compare all persisted fields, independent of JSON property insertion order. */
function itemSnapshot(item: ProjectBench | undefined): string {
  return JSON.stringify(item, (_key, value: unknown) => value && typeof value === 'object' && !Array.isArray(value)
    ? Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b))) : value);
}

/** A selected item stays armed after a successful placement. Saves are serialized. */
export function useDetailPlacement(data: ProjectDetails | undefined, save: (next: ProjectDetails) => Promise<ProjectDetails>, projectId?: string,
  validate?: (id:string,pose:DetailPose)=>DetailSupport) {
  const current = useRef(data), busy = useRef(false);
  const validation=useRef(validate); validation.current=validate;
  const scope = useRef(projectId);
  const generation = useRef(0);
  const [selected, setSelected] = useState<DetailAssetId | null>(null);
  const [angle, setAngle] = useState(0);
  const [selectedAction, setSelectedAction] = useState<PeopleActionId>('standing');
  const [editing, setEditing] = useState<(ProjectBench & { variant: DetailAssetId; people_action?: PeopleActionId }) | null>(null);
  const [moving, setMoving] = useState(false);
  const [saving, setSaving] = useState(false), [error, setError] = useState(''), [status, setStatus] = useState('');
  const unavailable = () => busy.current || useUndoRedoStore.getState()._isSystemAction;
  const record = (key: ItemCollection, before: ProjectBench | undefined, after: ProjectBench | undefined, label: string) => {
    if (!projectId || itemSnapshot(before) === itemSnapshot(after)) return;
    const requestScope = projectId;
    const historyScope = useUndoRedoStore.getState().scopeVersion;
    const itemId = (after ?? before)!.id;
    const replay = async (expected: ProjectBench | undefined, replacement: ProjectBench | undefined) => {
      const source = current.current;
      if (scope.current !== requestScope || useUndoRedoStore.getState().scopeVersion !== historyScope || !source?.can_edit || busy.current)
        throw new Error('Detail history is unavailable in this project or during a save.');
      const items = source[key] ?? [];
      if (itemSnapshot(items.find(i => i.id === itemId)) !== itemSnapshot(expected))
        throw Object.assign(new Error('The item changed in another session.'), { response: { status: 409 } });
      if(replacement && 'variant' in replacement){
        const support=validation.current?.(String(replacement.variant),replacement);
        if(support&&!support.ok)throw new Error(support.message);
      }
      const next = items.filter(i => i.id !== itemId);
      // Preserve the item's position in its collection when possible.
      const index = items.findIndex(i => i.id === itemId);
      if (replacement) next.splice(index < 0 ? next.length : index, 0, replacement as typeof next[number]);
      busy.current = true; setSaving(true); setError('');
      try {
        const saved = await save({ ...source, [key]: next });
        if (scope.current !== requestScope || useUndoRedoStore.getState().scopeVersion !== historyScope) return;
        current.current = saved;
        setEditing(old => old?.id === itemId ? null : old);
        setMoving(false);
        setStatus('Detail change saved.');
      } finally { busy.current = false; setSaving(false); }
    };
    useUndoRedoStore.getState().pushAction({ projectId, label,
      undo: () => replay(after, before), redo: () => replay(before, after) });
  };
  useEffect(() => {
    if (scope.current !== projectId) {
      generation.current++;
      scope.current = projectId; current.current = data; setSelected(null); setEditing(null); setMoving(false); setStatus(''); setError('');
    } else if (!busy.current && data && (!current.current || data.revision >= current.current.revision)) {
      current.current = data;
    }
  }, [data, projectId]);
  const choose = (id: DetailAssetId | null, action?: PeopleActionId) => {
    if (unavailable()) return;
    const asset = id ? detailAsset(id) : undefined;
    let selectedAction: PeopleActionId = 'standing';
    try { if (isPeopleAsset(asset)) selectedAction = peopleActionForAsset(asset, action).id; }
    catch (error) { setError((error as Error).message); return; }
    setSelected(id); setSelectedAction(selectedAction); setEditing(null); setMoving(false); setError(''); setStatus('');
  };
  const selectItem = (id: string) => {
    if (unavailable() || !current.current?.can_edit) return;
    const source = current.current;
    const item = [...source.benches.map(b => ({ ...b, variant: 'timber-bench' as const })), ...(source.trees ?? []), ...(source.props ?? [])].find(b => b.id === id);
    if (!item) return;
    const asset = detailAsset(item.variant);
    try {
      const selected = isPeopleAsset(asset) ? {...item, people_action:peopleActionForAsset(asset, 'people_action' in item ? item.people_action : undefined).id} : item;
      setSelected(null); setEditing(selected); setAngle(item.angle); setMoving(false); setError(''); setStatus('');
    } catch (error) { setError((error as Error).message); }
  };
  const updateItem = async (position?: [number, number], remove = false, nextAngle = angle, nextAction?: PeopleActionId) => {
    const source = current.current;
    if (!source?.can_edit || !editing || unavailable() || !Number.isFinite(nextAngle)) return;
    const asset = detailAsset(editing.variant);
    let action: PeopleActionId | undefined;
    if (!remove) {
      try {
        if (nextAction !== undefined || isPeopleAsset(asset)) action = peopleActionForAsset(asset, nextAction ?? editing.people_action).id;
      } catch (error) { setError((error as Error).message); return; }
    }
    const key = (['benches', 'trees', 'props'] as const).find(k => source[k]?.some(i => i.id === editing.id));
    if (!key) return;
    const before = source[key]?.find(i => i.id === editing.id);
    const support = remove ? {ok:true as const} : validate?.(editing.variant,{lng:position?.[0]??editing.lng,lat:position?.[1]??editing.lat,angle:nextAngle}) ?? {ok:true as const};
    if(!support.ok){setError(support.message);return;}
    const requestScope = scope.current;
    const requestGeneration = generation.current;
    const update = <T extends ProjectBench>(items: T[]) => items.filter(i => !remove || i.id !== editing.id).map(i => i.id === editing.id
      ? { ...i, angle: ((nextAngle % 360) + 360) % 360, lng: position?.[0] ?? editing.lng, lat: position?.[1] ?? editing.lat,
        ...(action ? {people_action:action} : {}),
        ...('hostId' in support && support.hostId ? {support_zone_id:support.hostId}: {}) } : i);
    busy.current = true; setSaving(true); setError('');
    try {
      const saved = await save({ ...source, benches: update(source.benches), trees: update(source.trees ?? []), props: update(source.props ?? []) });
      if (scope.current === requestScope && generation.current === requestGeneration) {
        record(key, before, saved[key]?.find(i => i.id === editing.id), remove ? 'Delete detail' : nextAction ? 'Change person action' : 'Move or rotate detail');
        current.current = saved; setMoving(false);
        if (remove) setEditing(null);
        else setEditing({ ...editing, ...(action ? {people_action:action} : {}), lng: position?.[0] ?? editing.lng, lat: position?.[1] ?? editing.lat, angle: ((nextAngle % 360) + 360) % 360 });
        setAngle(((nextAngle % 360) + 360) % 360);
        setStatus(remove ? 'Item removed and saved.' : 'Item changes saved.');
      }
    } catch { if (scope.current === requestScope && generation.current === requestGeneration) setError('Changes were not saved. Your saved items are safe; retry or cancel this edit.'); }
    finally { busy.current = false; setSaving(false); }
  };
  const place = async (position: [number, number]) => {
    if (!position.every(Number.isFinite)) return;
    if (editing) { if (moving) await updateItem(position); return; }
    const source = current.current;
    if (!source?.can_edit || !selected || unavailable() || !position.every(Number.isFinite) || !Number.isFinite(angle)) return;
    const asset = detailAsset(selected);
    const support=validate?.(selected,{lng:position[0],lat:position[1],angle})??{ok:true as const};
    if(!support.ok){setError(support.message);return;}
    const key = asset.kind === 'tree' ? 'trees' : asset.kind === 'bench' ? 'benches' : 'props';
    const items = source[key] ?? [];
    if (items.length >= 256) { setError('This category is full. Remove an item in Arrange details to make room.'); return; }
    const item = { id: `${asset.kind}-${crypto.randomUUID()}`, lng: position[0], lat: position[1], angle,
      ...(asset.kind === 'bench' ? {} : { variant: selected }),
      ...(isPeopleAsset(asset) ? {people_action:peopleActionForAsset(asset, selectedAction).id} : {}),
      ...('hostId' in support && support.hostId ? {support_zone_id:support.hostId}: {}) };
    const requestScope = scope.current;
    const requestGeneration = generation.current;
    busy.current = true; setSaving(true); setError(''); setStatus('');
    try {
      const saved = await save({ ...source, [key]: [...items, item] });
      if (scope.current === requestScope && generation.current === requestGeneration) {
        record(key, undefined, saved[key]?.find(i => i.id === item.id), `Place ${asset.label}`);
        current.current = saved;
        setStatus(`${asset.label} placed and saved. Choose another item or place another copy.`);
      }
    } catch {
      if (scope.current === requestScope && generation.current === requestGeneration) setError('That item was not saved. Your existing details are safe. Try placing it again; if details changed elsewhere, reopen this panel to refresh.');
    } finally { busy.current = false; setSaving(false); }
  };
  const source=current.current;
  const items=source ? [...source.benches.map(item=>({...item,variant:'timber-bench' as const})),...(source.trees??[]),...(source.props??[])] : [];
  return { items, rotateBy:(delta:number)=>updateItem(undefined,false,angle+delta), selected, selectedAction, choose, angle, setAngle, saving, error, status, place, editing, selectItem, moving, setMoving,
    setPeopleAction:(action:PeopleActionId)=>updateItem(undefined,false,angle,action),
    saveEdit: () => updateItem(), removeItem: () => updateItem(undefined, true) };
}
