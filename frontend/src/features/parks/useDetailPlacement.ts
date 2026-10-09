import { useEffect, useRef, useState } from 'react';
import { detailAsset, type DetailAssetId } from './detailCatalogue';
import type { ProjectDetails, ProjectBench } from './projectBenches';

/** A selected item stays armed after a successful placement. Saves are serialized. */
export function useDetailPlacement(data: ProjectDetails | undefined, save: (next: ProjectDetails) => Promise<ProjectDetails>, projectId?: string) {
  const current = useRef(data), busy = useRef(false);
  const scope = useRef(projectId);
  const [selected, setSelected] = useState<DetailAssetId | null>(null);
  const [angle, setAngle] = useState(0);
  const [editing, setEditing] = useState<(ProjectBench & { variant: DetailAssetId }) | null>(null);
  const [moving, setMoving] = useState(false);
  const [saving, setSaving] = useState(false), [error, setError] = useState(''), [status, setStatus] = useState('');
  useEffect(() => {
    if (scope.current !== projectId) {
      scope.current = projectId; current.current = data; setSelected(null); setEditing(null); setMoving(false); setStatus(''); setError('');
    } else if (!busy.current && data && (!current.current || data.revision >= current.current.revision)) {
      current.current = data;
    }
  }, [data, projectId]);
  const choose = (id: DetailAssetId | null) => { if (busy.current) return; setSelected(id); setEditing(null); setMoving(false); setError(''); setStatus(''); };
  const selectItem = (id: string) => {
    if (busy.current || !current.current?.can_edit) return;
    const source = current.current;
    const item = [...source.benches.map(b => ({ ...b, variant: 'timber-bench' as const })), ...(source.trees ?? []), ...(source.props ?? [])].find(b => b.id === id);
    if (!item) return;
    setSelected(null); setEditing(item); setAngle(item.angle); setMoving(false); setError(''); setStatus('');
  };
  const updateItem = async (position?: [number, number], remove = false) => {
    const source = current.current;
    if (!source?.can_edit || !editing || busy.current || !Number.isFinite(angle)) return;
    const requestScope = scope.current;
    const update = <T extends ProjectBench>(items: T[]) => items.filter(i => !remove || i.id !== editing.id).map(i => i.id === editing.id
      ? { ...i, angle: ((angle % 360) + 360) % 360, lng: position?.[0] ?? editing.lng, lat: position?.[1] ?? editing.lat } : i);
    busy.current = true; setSaving(true); setError('');
    try {
      const saved = await save({ ...source, benches: update(source.benches), trees: update(source.trees ?? []), props: update(source.props ?? []) });
      if (scope.current === requestScope) {
        current.current = saved; setMoving(false);
        if (remove) setEditing(null);
        else setEditing({ ...editing, lng: position?.[0] ?? editing.lng, lat: position?.[1] ?? editing.lat, angle });
        setStatus(remove ? 'Item removed and saved.' : 'Item changes saved.');
      }
    } catch { if (scope.current === requestScope) setError('Changes were not saved. Your saved items are safe; retry or cancel this edit.'); }
    finally { busy.current = false; setSaving(false); }
  };
  const place = async (position: [number, number]) => {
    if (!position.every(Number.isFinite)) return;
    if (editing) { if (moving) await updateItem(position); return; }
    const source = current.current;
    if (!source?.can_edit || !selected || busy.current || !position.every(Number.isFinite)) return;
    const asset = detailAsset(selected);
    const key = asset.kind === 'tree' ? 'trees' : asset.kind === 'bench' ? 'benches' : 'props';
    const items = source[key] ?? [];
    if (items.length >= 256) { setError('This category is full. Remove an item in Arrange details to make room.'); return; }
    const item = { id: `${asset.kind}-${crypto.randomUUID()}`, lng: position[0], lat: position[1], angle,
      ...(asset.kind === 'bench' ? {} : { variant: selected }) };
    const requestScope = scope.current;
    busy.current = true; setSaving(true); setError(''); setStatus('');
    try {
      const saved = await save({ ...source, [key]: [...items, item] });
      if (scope.current === requestScope) {
        current.current = saved;
        setStatus(`${asset.label} placed and saved. Choose another item or place another copy.`);
      }
    } catch {
      if (scope.current === requestScope) setError('That item was not saved. Your existing details are safe. Try placing it again; if details changed elsewhere, reopen this panel to refresh.');
    } finally { busy.current = false; setSaving(false); }
  };
  return { selected, choose, angle, setAngle, saving, error, status, place, editing, selectItem, moving, setMoving,
    saveEdit: () => updateItem(), removeItem: () => updateItem(undefined, true) };
}
