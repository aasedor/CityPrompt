import { useEffect, useRef, useState } from 'react';
import { detailAsset, type DetailAssetId } from './detailCatalogue';
import type { ProjectDetails } from './projectBenches';

/** A selected item stays armed after a successful placement. Saves are serialized. */
export function useDetailPlacement(data: ProjectDetails | undefined, save: (next: ProjectDetails) => Promise<ProjectDetails>, projectId?: string) {
  const current = useRef(data), busy = useRef(false);
  const scope = useRef(projectId);
  const [selected, setSelected] = useState<DetailAssetId | null>(null);
  const [angle, setAngle] = useState(0);
  const [saving, setSaving] = useState(false), [error, setError] = useState(''), [status, setStatus] = useState('');
  useEffect(() => {
    if (scope.current !== projectId) {
      scope.current = projectId; current.current = data; setSelected(null); setStatus(''); setError('');
    } else if (!busy.current && data && (!current.current || data.revision >= current.current.revision)) {
      current.current = data;
    }
  }, [data, projectId]);
  const choose = (id: DetailAssetId | null) => { setSelected(id); setError(''); setStatus(''); };
  const place = async (position: [number, number]) => {
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
  return { selected, choose, angle, setAngle, saving, error, status, place };
}
