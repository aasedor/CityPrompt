import { useCallback, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { StudioDialog } from '@/features/projects/StudioControls';
import { WORKING_VIEW_QUALITIES, type WorkingViewQuality } from './useWorkingViewQuality';

export interface WorkingViewStats { fps: number; frameMs: number; drawCalls: number; triangles: number; width: number; height: number }

/** Mounted only while the student has opened diagnostics; no telemetry leaves the browser. */
export function WorkingViewStatsSampler({onSample}: {onSample: (stats: WorkingViewStats) => void}) {
  const sample = useRef({ seconds: 0, frames: 0 });
  useFrame(({gl}, delta) => {
    if (document.hidden) { sample.current = {seconds: 0, frames: 0}; return; }
    sample.current.seconds += delta; sample.current.frames += 1;
    if (sample.current.seconds < 2) return;
    onSample({fps: Math.round(sample.current.frames / sample.current.seconds), frameMs: Math.round(1000 * sample.current.seconds / sample.current.frames),
      drawCalls: gl.info.render.calls, triangles: gl.info.render.triangles, width: gl.domElement.width, height: gl.domElement.height});
    sample.current = {seconds: 0, frames: 0};
  });
  return null;
}

export function WorkingViewPerformance({quality, onQuality, onOpen, stats}: {
  quality: WorkingViewQuality; onQuality: (quality: WorkingViewQuality) => void;
  onOpen: (open: boolean) => void; stats: WorkingViewStats | null;
}) {
  const [open, setOpen] = useState(false);
  const close = useCallback(() => {setOpen(false); onOpen(false);}, [onOpen]);
  return <>
    <button type="button" aria-haspopup="dialog" aria-expanded={open} onClick={() => {setOpen(true); onOpen(true);}}
      className="rounded-full border-2 border-slate-900 bg-[#fff9ec] px-3 py-1.5 text-xs font-semibold text-slate-950 shadow-[3px_3px_0_0_#151515]">3D detail · {WORKING_VIEW_QUALITIES[quality].label}</button>
    {open && <StudioDialog title="3D performance" onClose={close}>
      <div className="space-y-5 text-slate-900">
        <p className="text-sm leading-6">Choose a comfortable working view for this device. Lower detail reduces the number of screen pixels drawn; your buildings, park layouts and map coordinates stay the same.</p>
        <label className="block text-sm font-semibold">Working view detail
          <select value={quality} onChange={event => onQuality(event.target.value as WorkingViewQuality)} className="mt-2 min-h-11 w-full rounded-lg border border-slate-400 bg-white px-3">
            {Object.entries(WORKING_VIEW_QUALITIES).map(([id, option]) => <option key={id} value={id}>{option.label}</option>)}
          </select>
        </label>
        <p className="text-sm">{WORKING_VIEW_QUALITIES[quality].description}</p>
        <p className="text-sm leading-6 text-slate-600">Current-view still images use the view's resolution. Choose High before capturing a sharper still. Video uses its own Draft or High Quality capture setting.</p>
        <div aria-label="Live 3D performance" className="rounded-lg bg-slate-100 p-4 text-sm">
          {stats ? <><p>{stats.fps} frames/s · {stats.frameMs} ms per frame</p><p className="mt-2">{stats.width} × {stats.height} screen buffer · {stats.drawCalls.toLocaleString()} draw calls · {stats.triangles.toLocaleString()} triangles</p></>
            : <p role="status">Measuring the current view…</p>}
          <p className="mt-3 text-xs leading-5 text-slate-600">A short local sample of this view. Test while moving around a representative community; this does not measure server capacity or certify another device.</p>
        </div>
      </div>
    </StudioDialog>}
  </>;
}
