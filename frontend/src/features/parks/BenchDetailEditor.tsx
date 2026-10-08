import { useEffect, useMemo, useRef, useState, type PointerEvent } from 'react';
import { createPortal } from 'react-dom';
import type { SiteZone, SiteZoneProperties } from '@/types';
import {
  isNeighborhoodParkPilot,
  type ParkPoint,
} from '@/components/viewer/globe/neighborhoodParkLayout';
import {
  benchContext,
  resolveBenches,
  saveBenchDetails,
  benchPlacementProblem,
  plantingClearOfBenches,
  MAX_DETAIL_BENCHES,
  type DetailBench,
} from './benchDetails';

const button =
  'min-h-11 rounded-lg border border-slate-400 bg-white px-3 py-2 text-sm font-semibold text-slate-900 disabled:opacity-40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-700';
export function BenchDetailControls({
  zone,
  disabled,
  onSave,
  onEditingChange,
}: {
  zone: SiteZone;
  disabled: boolean;
  onSave: (properties: SiteZoneProperties) => Promise<unknown>;
  onEditingChange?: (editing: boolean) => void;
}) {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    onEditingChange?.(open);
    return () => onEditingChange?.(false);
  }, [open, onEditingChange]);
  if (!isNeighborhoodParkPilot(zone)) return null;
  return (
    <>
      <button
        className={`${button} mb-3 w-full`}
        disabled={disabled}
        onClick={() => setOpen(true)}
      >
        Edit details · benches
      </button>
      {open &&
        createPortal(
          <BenchDetailEditor
            zone={zone}
            disabled={disabled}
            onSave={onSave}
            onClose={() => setOpen(false)}
          />,
          document.body,
        )}
    </>
  );
}

function BenchDetailEditor({
  zone,
  disabled,
  onSave,
  onClose,
}: {
  zone: SiteZone;
  disabled: boolean;
  onSave: (properties: SiteZoneProperties) => Promise<unknown>;
  onClose: () => void;
}) {
  const context = useMemo(() => benchContext(zone), [zone]);
  const [benches, setBenches] = useState(() => resolveBenches(zone, context));
  const [past, setPast] = useState<DetailBench[][]>([]),
    [selected, setSelected] = useState<string | null>(null);
  const [placing, setPlacing] = useState(false),
    [message, setMessage] = useState(''),
    [saving, setSaving] = useState(false);
  const [preview, setPreview] = useState<DetailBench | null>(null);
  const drag = useRef<{
    id: string;
    start: ParkPoint;
    screenStart: ParkPoint;
    bench: DetailBench;
  } | null>(null);
  const svg = useRef<SVGSVGElement>(null),
    dialog = useRef<HTMLDivElement>(null);
  const locked = disabled || saving,
    active = benches.find((b) => b.id === selected),
    dirty = past.length > 0;
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null,
      root = document.getElementById('root');
    const wasInert = root?.hasAttribute('inert');
    root?.setAttribute('inert', '');
    dialog.current?.focus();
    return () => {
      if (!wasInert) root?.removeAttribute('inert');
      previous?.focus();
    };
  }, []);
  useEffect(() => {
    if (!selected) dialog.current?.focus();
  }, [selected]);
  const box = useMemo(() => {
    const p = context.layout.boundary;
    return {
      minX: Math.min(...p.map((v) => v.x)) - 2,
      minY: Math.min(...p.map((v) => v.y)) - 2,
      maxX: Math.max(...p.map((v) => v.x)) + 2,
      maxY: Math.max(...p.map((v) => v.y)) + 2,
    };
  }, [context]);
  const change = (next: DetailBench[]) => {
    setPast((p) => [...p.slice(-49), benches]);
    setBenches(next);
    setMessage('');
  };
  const move = (candidate: DetailBench) => {
    const problem = benchPlacementProblem(candidate, benches, context);
    if (problem) {
      setMessage(problem);
      return;
    }
    change(benches.map((p) => (p.id === candidate.id ? candidate : p)));
    setPlacing(false);
  };
  const add = () => {
    const candidate: DetailBench = {
      id: `bench-${crypto.randomUUID()}`,
      point: context.fromFrame(0.5, 0.5),
      yaw: context.angle,
    };
    // A bounded search offers a usable starting point; students can then drag it.
    const positions = [];
    for (let u = 0.1; u < 0.95; u += 0.08)
      for (let v = 0.1; v < 0.95; v += 0.08) positions.push({ u, v });
    positions.sort(
      (a, b) =>
        Math.hypot(a.u - 0.5, a.v - 0.5) - Math.hypot(b.u - 0.5, b.v - 0.5),
    );
    const free = positions.find(
      (p) =>
        !benchPlacementProblem(
          { ...candidate, point: context.fromFrame(p.u, p.v) },
          benches,
          context,
        ),
    );
    if (!free) {
      setMessage(
        'There is no clear starting space for another bench in this layout. Move or remove a bench first.',
      );
      return;
    }
    candidate.point = context.fromFrame(free.u, free.v);
    change([...benches, candidate]);
    setSelected(candidate.id);
  };
  const point = (event: PointerEvent<SVGElement>): ParkPoint => {
    const matrix = svg.current?.getScreenCTM();
    if (!matrix) return { x: 0, y: 0 };
    const p = new DOMPoint(event.clientX, event.clientY).matrixTransform(
      matrix.inverse(),
    );
    return { x: p.x, y: -p.y };
  };
  const points = (p: ParkPoint[]) => p.map((v) => `${v.x},${-v.y}`).join(' ');
  const shown = benches.map((b) => (preview?.id === b.id ? preview : b));
  const invalid = benches.find((b) =>
    benchPlacementProblem(b, benches, context),
  );
  return (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-slate-950/40 p-3"
      onPointerDown={(e) => e.stopPropagation()}
      onWheel={(e) => e.stopPropagation()}
    >
      <div
        ref={dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="bench-editor-title"
        tabIndex={-1}
        className="flex h-[min(94dvh,680px)] w-full max-w-5xl flex-col overflow-y-auto rounded-2xl border-2 border-slate-900 bg-[#fff9ec] p-4 text-slate-900 shadow-xl"
        onKeyDown={(e) => {
          e.stopPropagation();
          if (e.key === 'Tab') {
            const controls = Array.from(
              dialog.current?.querySelectorAll<HTMLElement>(
                'button:not(:disabled),[tabindex="0"]',
              ) ?? [],
            );
            const first = controls[0],
              last = controls[controls.length - 1];
            if (
              e.shiftKey &&
              (document.activeElement === first ||
                document.activeElement === dialog.current)
            ) {
              e.preventDefault();
              last?.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
              e.preventDefault();
              first?.focus();
            }
          }
          if (e.key === 'Escape' && !saving) {
            e.preventDefault();
            onClose();
          }
          if (locked) return;
          if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
            e.preventDefault();
            if (past.length) {
              setBenches(past[past.length - 1]);
              setPast((p) => p.slice(0, -1));
              setPreview(null);
              setMessage('');
            }
            return;
          }
          if (!active) return;
          if (['Delete', 'Backspace'].includes(e.key)) {
            e.preventDefault();
            change(benches.filter((b) => b.id !== active.id));
            setSelected(null);
          }
          const directions: Record<string, number[]> = {
            ArrowLeft: [-0.5, 0],
            ArrowRight: [0.5, 0],
            ArrowUp: [0, 0.5],
            ArrowDown: [0, -0.5],
          };
          const direction = directions[e.key];
          if (direction) {
            e.preventDefault();
            move({
              ...active,
              point: {
                x: active.point.x + direction[0],
                y: active.point.y + direction[1],
              },
            });
          }
        }}
      >
        <header className="mb-3 flex items-center justify-between gap-3">
          <div>
            <h2 id="bench-editor-title" className="text-lg font-bold">
              Edit park details · benches
            </h2>
            <p className="text-xs">
              {zone.name || 'Neighbourhood park'} · detailed timber bench trial
            </p>
          </div>
          <button
            aria-label="Close detail editor"
            disabled={saving}
            className={button}
            onClick={onClose}
          >
            Close
          </button>
        </header>
        <p className="mb-3 text-sm">
          Select a bench on this plan, then drag it or use the move buttons.
          Small objects can only be edited here. Save to update the 3D scene.
        </p>
        <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_240px]">
          <div className="min-w-0">
            <svg
              ref={svg}
              role="group"
              aria-label="Bench layout plan"
              viewBox={`${box.minX} ${-box.maxY} ${box.maxX - box.minX} ${box.maxY - box.minY}`}
              className="max-h-[58dvh] min-h-64 w-full touch-none rounded-xl border border-slate-400 bg-[#e8edd9]"
              onPointerMove={(e) => {
                if (!drag.current || locked) return;
                if (
                  Math.hypot(
                    e.clientX - drag.current.screenStart.x,
                    e.clientY - drag.current.screenStart.y,
                  ) < 3
                )
                  return;
                const p = point(e),
                  d = drag.current;
                setPreview({
                  ...d.bench,
                  point: {
                    x: d.bench.point.x + p.x - d.start.x,
                    y: d.bench.point.y + p.y - d.start.y,
                  },
                });
              }}
              onPointerCancel={() => {
                drag.current = null;
                setPreview(null);
              }}
              onPointerUp={(e) => {
                if (!drag.current || locked) return;
                const p = point(e),
                  d = drag.current;
                drag.current = null;
                setPreview(null);
                if (
                  Math.hypot(
                    e.clientX - d.screenStart.x,
                    e.clientY - d.screenStart.y,
                  ) >= 3
                )
                  move({
                    ...d.bench,
                    point: {
                      x: d.bench.point.x + p.x - d.start.x,
                      y: d.bench.point.y + p.y - d.start.y,
                    },
                  });
              }}
              onPointerDown={(e) => {
                if (placing && active && !locked) {
                  e.preventDefault();
                  move({ ...active, point: point(e) });
                }
              }}
            >
              <polygon
                points={points(context.layout.boundary)}
                fill="#c2d09b"
                stroke="#445737"
                strokeWidth=".25"
              />
              <polyline
                points={points(
                  [...context.layout.loop, context.layout.loop[0]].filter(
                    Boolean,
                  ),
                )}
                fill="none"
                stroke="#d0bc96"
                strokeWidth={context.layout.pathWidth}
              />
              {[
                ...context.layout.paths,
                ...context.accessPaths.map((p) => p.points),
              ].map((path, i) => (
                <polyline
                  key={`path-${i}`}
                  points={points(path)}
                  fill="none"
                  stroke="#d0bc96"
                  strokeWidth={context.layout.pathWidth}
                />
              ))}
              {context.layout.modules.map((m) => (
                <g key={m.id}>
                  <polygon
                    points={points(m.envelope)}
                    fill="#b7aaa0"
                    stroke="#706256"
                    strokeWidth=".1"
                  />
                  <text
                    x={m.center.x}
                    y={-m.center.y}
                    textAnchor="middle"
                    fontSize="1.4"
                    fill="#342e28"
                  >
                    {m.kind === 'tower' ? 'Play' : m.kind}
                  </text>
                </g>
              ))}
              {plantingClearOfBenches(context.layout.trees, benches)
                .filter((p) => context.clearOfEntrances(p, 3))
                .map((p, i) => (
                  <circle
                    key={`tree-${i}`}
                    cx={p.x}
                    cy={-p.y}
                    r="1.4"
                    fill="#527649"
                    fillOpacity=".6"
                  />
                ))}
              {shown.map((bench, i) => (
                <g
                  key={bench.id}
                  role="button"
                  tabIndex={locked ? -1 : 0}
                  aria-label={`Select bench ${i + 1}`}
                  aria-pressed={selected === bench.id}
                  transform={`translate(${bench.point.x} ${-bench.point.y}) rotate(${(-bench.yaw * 180) / Math.PI})`}
                  onFocus={() => setSelected(bench.id)}
                  onClick={() => {
                    if (!locked) setSelected(bench.id);
                  }}
                  onKeyDown={(e) => {
                    if (['Enter', ' '].includes(e.key) && !locked) {
                      e.preventDefault();
                      setSelected(bench.id);
                    }
                  }}
                  onPointerDown={(e) => {
                    if (locked) return;
                    e.stopPropagation();
                    e.preventDefault();
                    setSelected(bench.id);
                    setPlacing(false);
                    drag.current = {
                      id: bench.id,
                      start: point(e),
                      screenStart: { x: e.clientX, y: e.clientY },
                      bench,
                    };
                    e.currentTarget.setPointerCapture(e.pointerId);
                  }}
                >
                  <rect
                    x="-3"
                    y="-2.5"
                    width="6"
                    height="5"
                    rx=".6"
                    fill={selected === bench.id ? '#c9ff3d' : 'transparent'}
                    stroke={selected === bench.id ? '#263728' : 'none'}
                    strokeWidth=".15"
                  />
                  <rect
                    x="-.95"
                    y="-.293"
                    width="1.9"
                    height=".586"
                    rx=".1"
                    fill="#855633"
                    stroke="#31271c"
                    strokeWidth=".15"
                  />
                  <path d="M-.9 -.45H.9" stroke="#31271c" strokeWidth=".18" />
                  <text
                    x="0"
                    y="1.9"
                    textAnchor="middle"
                    fontSize="1.5"
                    fill="#18251b"
                  >
                    {i + 1}
                  </text>
                </g>
              ))}
            </svg>
            <p className="mt-2 text-xs">
              Top view · north ↑ · benches keep their actual 1.9 m size. Paths
              and larger park objects are shown for context.
            </p>
          </div>
          <div className="space-y-3">
            <p className="font-semibold">{benches.length} benches</p>
            <button
              className={`${button} w-full !bg-[#c9ff3d]`}
              disabled={locked || benches.length >= MAX_DETAIL_BENCHES}
              onClick={add}
            >
              Add bench
            </button>
            {active ? (
              <>
                <p className="text-sm font-semibold">
                  Bench {benches.findIndex((b) => b.id === active.id) + 1}{' '}
                  selected
                </p>
                <button
                  className={`${button} w-full`}
                  disabled={locked}
                  aria-pressed={placing}
                  onClick={() => {
                    setPlacing((v) => !v);
                    setMessage(
                      'Click a clear place on the plan to move this bench.',
                    );
                  }}
                >
                  Move on plan
                </button>
                <div className="grid grid-cols-2 gap-2">
                  {(
                    [
                      ['north', 0, 0.5],
                      ['east', 0.5, 0],
                      ['south', 0, -0.5],
                      ['west', -0.5, 0],
                    ] as const
                  ).map(([name, x, y]) => (
                    <button
                      key={name}
                      className={button}
                      aria-label={`Move bench ${name}`}
                      disabled={locked}
                      onClick={() =>
                        move({
                          ...active,
                          point: {
                            x: active.point.x + x,
                            y: active.point.y + y,
                          },
                        })
                      }
                    >
                      {name} 0.5 m
                    </button>
                  ))}
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {[-15, 15].map((deg) => (
                    <button
                      key={deg}
                      className={button}
                      disabled={locked}
                      onClick={() =>
                        move({
                          ...active,
                          yaw: active.yaw + (deg * Math.PI) / 180,
                        })
                      }
                    >
                      Rotate {deg}°
                    </button>
                  ))}
                </div>
                <button
                  className={`${button} w-full`}
                  disabled={locked}
                  onClick={() => {
                    change(benches.filter((b) => b.id !== active.id));
                    setSelected(null);
                  }}
                >
                  Remove bench
                </button>
              </>
            ) : (
              <p className="text-sm">Click a numbered bench to select it.</p>
            )}
            <button
              className={`${button} w-full`}
              aria-label="Undo detail edit"
              disabled={locked || !past.length}
              onClick={() => {
                setBenches(past[past.length - 1]);
                setPast((p) => p.slice(0, -1));
                setMessage('');
              }}
            >
              Undo
            </button>
            <p role="status" className="text-sm text-amber-900">
              {message ||
                (invalid
                  ? 'A bench needs a clearer position. Select and move it before saving.'
                  : '')}
            </p>
            <button
              className={`${button} w-full !bg-[#c9ff3d]`}
              disabled={locked || !dirty || !!invalid}
              onClick={async () => {
                setSaving(true);
                setMessage('');
                try {
                  await onSave(saveBenchDetails(zone, benches, context));
                  onClose();
                } catch {
                  setMessage(
                    'Could not save the benches. Your edits are still here; try Save details again.',
                  );
                } finally {
                  setSaving(false);
                }
              }}
            >
              {saving ? 'Saving…' : 'Save details'}
            </button>
            <p className="text-xs text-slate-600">
              {dirty
                ? 'Unsaved edits. Closing discards them.'
                : 'Your saved arrangement.'}{' '}
              Moving or rotating the whole park carries the benches with it.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
