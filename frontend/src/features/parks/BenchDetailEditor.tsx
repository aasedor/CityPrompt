import { useEffect, useMemo, useRef, useState, type PointerEvent } from "react";
import { createPortal } from "react-dom";
import type { SiteZone, SiteZoneProperties } from "@/types";
import {
  isNeighborhoodParkPilot,
  type ParkPoint,
} from "@/components/viewer/globe/neighborhoodParkLayout";
import {
  benchContext,
  resolveBenches,
  saveBenchDetails,
  benchPlacementProblem,
  plantingClearOfBenches,
  MAX_DETAIL_BENCHES,
  type DetailBench,
  type BenchContext,
  DETAIL_TREE_MODELS,
  type DetailTreeVariant,
} from "./benchDetails";
import { getApiErrorMessage } from "@/services/api";
import { isAxiosError } from "axios";
import { assetForZone } from "@/features/pickPlace/catalogue";
import { DetailCataloguePicker } from "./DetailCataloguePicker";
import { usePavingEditor } from "./PavingEditor";
import type { PavingSurface } from "./pavingSurfaces";
import { readNativePark, nativeParkFootprint } from "./nativeParkRegistry";
import {
  detailAsset,
  type DetailAssetId,
  type DetailPropVariant,
} from "./detailCatalogue";

const button =
  "min-h-11 rounded-lg border border-slate-400 bg-white px-3 py-2 text-sm font-semibold text-slate-900 disabled:opacity-40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-700";
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
  return (
    <BenchLayoutEditor
      context={context}
      initialBenches={resolveBenches(zone, context)}
      title={zone.name || "Neighbourhood park"}
      disabled={disabled}
      onSave={(benches) => onSave(saveBenchDetails(zone, benches, context))}
      onClose={onClose}
    />
  );
}

export function BenchLayoutEditor({
  context,
  initialBenches,
  title,
  disabled,
  onSave,
  onClose,
  contextZones = [],
  initialSurfaces = [],
}: {
  context: BenchContext;
  initialBenches: DetailBench[];
  title: string;
  disabled: boolean;
  onSave: (
    benches: DetailBench[],
    surfaces: PavingSurface[],
  ) => Promise<unknown>;
  onClose: () => void;
  contextZones?: SiteZone[];
  initialSurfaces?: PavingSurface[];
}) {
  const [benches, setBenches] = useState(initialBenches);
  const [surfaces, setSurfaces] = useState(initialSurfaces);
  const independent = context.scope === "project";
  const [viewScale, setViewScale] = useState(1);
  const [past, setPast] = useState<
      { benches: DetailBench[]; surfaces: PavingSurface[] }[]
    >([]),
    [selected, setSelected] = useState<string | null>(null);
  const [placing, setPlacing] = useState(false),
    [message, setMessage] = useState(""),
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
  const suppressPlanClick = useRef(false);
  const locked = disabled || saving,
    active = benches.find((b) => b.id === selected),
    dirty = past.length > 0;
  const activeKind = active?.treeVariant
    ? "tree"
    : active?.propVariant
      ? "object"
      : "bench";
  const benchCount = benches.filter(
    (b) => !b.treeVariant && !b.propVariant,
  ).length;
  const treeCount = benches.filter((b) => b.treeVariant).length;
  const propCount = benches.length - benchCount - treeCount;
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null,
      root = document.getElementById("root");
    const wasInert = root?.hasAttribute("inert");
    root?.setAttribute("inert", "");
    dialog.current?.focus();
    return () => {
      if (!wasInert) root?.removeAttribute("inert");
      previous?.focus();
    };
  }, []);
  useEffect(() => {
    if (!selected) dialog.current?.focus();
  }, [selected]);
  const box = useMemo(() => {
    const p = context.layout.boundary;
    const minX = Math.min(...p.map((v) => v.x)) - 2,
      maxX = Math.max(...p.map((v) => v.x)) + 2;
    const minY = Math.min(...p.map((v) => v.y)) - 2,
      maxY = Math.max(...p.map((v) => v.y)) + 2;
    const x = (minX + maxX) / 2,
      y = (minY + maxY) / 2;
    return {
      minX: x - ((maxX - minX) * viewScale) / 2,
      maxX: x + ((maxX - minX) * viewScale) / 2,
      minY: y - ((maxY - minY) * viewScale) / 2,
      maxY: y + ((maxY - minY) * viewScale) / 2,
    };
  }, [context, viewScale]);
  const change = (next: DetailBench[], nextSurfaces = surfaces) => {
    setPast((p) => [...p.slice(-49), { benches, surfaces }]);
    setBenches(next);
    setSurfaces(nextSurfaces);
    setMessage("");
  };
  const paving = usePavingEditor({
    surfaces,
    context,
    locked,
    change: (next) => change(benches, next),
    onActivate: () => {
      setSelected(null);
      setPlacing(false);
      setPreview(null);
      drag.current = null;
    },
  });
  const undo = () => {
    const previous = past[past.length - 1];
    if (!previous) return;
    setBenches(previous.benches);
    setSurfaces(previous.surfaces);
    setPast((p) => p.slice(0, -1));
    setPreview(null);
    setPlacing(false);
    paving.reset();
    setMessage("");
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
  const add = (assetId: DetailAssetId = "timber-bench") => {
    paving.reset();
    setPlacing(false);
    setPreview(null);
    const model = detailAsset(assetId);
    const candidate: DetailBench = {
      id: `${model.kind}-${crypto.randomUUID()}`,
      point: context.fromFrame(0.5, 0.5),
      yaw: context.angle,
      ...(model.kind === "tree"
        ? { treeVariant: assetId as DetailTreeVariant }
        : model.kind === "object"
          ? { propVariant: assetId as DetailPropVariant }
          : {}),
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
        "There is no clear starting space for another object in this layout. Move or remove an object first.",
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
  const points = (p: ParkPoint[]) => p.map((v) => `${v.x},${-v.y}`).join(" ");
  const shown = benches.map((b) => (preview?.id === b.id ? preview : b));
  const markerSize = independent ? Math.max(3, (box.maxX - box.minX) / 90) : 3;
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
          if (e.key === "Tab") {
            const controls = Array.from(
              dialog.current?.querySelectorAll<HTMLElement>(
                'button:not(:disabled),select:not(:disabled),[tabindex="0"]',
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
          if (e.key === "Escape" && !saving) {
            e.preventDefault();
            if (paving.armed) {
              paving.reset();
              return;
            }
            if (placing) {
              setPlacing(false);
              setPreview(null);
              return;
            }
            onClose();
          }
          if (locked) return;
          if ((e.target as HTMLElement).closest("select,input,textarea"))
            return;
          if (e.key === "Enter" && paving.drawing) {
            e.preventDefault();
            paving.finish();
            return;
          }
          if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
            e.preventDefault();
            if (past.length) {
              undo();
            }
            return;
          }
          if (!active) return;
          if (["Delete", "Backspace"].includes(e.key)) {
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
              {independent
                ? "Edit community details"
                : "Edit park details · benches"}
            </h2>
            <p className="text-xs">
              {title} ·{" "}
              {independent
                ? "standalone detail catalogue"
                : "detailed timber bench trial"}
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
          Select {independent ? "an object" : "a bench"} on this plan, then drag
          it or use the move buttons. Small objects can only be edited here.
          Save to update the 3D scene.
        </p>
        <div className="grid min-h-0 gap-4 md:grid-cols-[minmax(0,1fr)_240px]">
          <div className="min-w-0">
            <svg
              ref={svg}
              role="group"
              aria-label={
                independent ? "Detail layout plan" : "Bench layout plan"
              }
              viewBox={`${box.minX} ${-box.maxY} ${box.maxX - box.minX} ${box.maxY - box.minY}`}
              className="max-h-[58dvh] min-h-64 w-full touch-none rounded-xl border border-slate-400 bg-[#e8edd9]"
              onPointerMove={(e) => {
                if (placing && active && !locked) {
                  setPreview({ ...active, point: point(e) });
                  return;
                }
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
              onClickCapture={(e) => {
                if (suppressPlanClick.current || placing || paving.armed) {
                  e.preventDefault();
                  e.stopPropagation();
                  suppressPlanClick.current = false;
                }
              }}
              onPointerDownCapture={(e) => {
                suppressPlanClick.current = false;
                if (paving.armed && !locked) {
                  e.preventDefault();
                  e.stopPropagation();
                  suppressPlanClick.current = true;
                  paving.click(point(e));
                  return;
                }
                if (placing && active && !locked) {
                  e.preventDefault();
                  e.stopPropagation();
                  suppressPlanClick.current = true;
                  setPreview(null);
                  move({ ...active, point: point(e) });
                }
              }}
            >
              {!independent && (
                <polygon
                  points={points(context.layout.boundary)}
                  fill="#c2d09b"
                  stroke="#445737"
                  strokeWidth=".25"
                />
              )}
              {independent && paving.plan}
              {independent &&
                contextZones.map((zone) => (
                  <g key={zone.id} pointerEvents="none">
                    <polygon
                      points={points(zone.coordinates.map(context.fromWorld))}
                      fill={
                        zone.zone_type === "site_boundary"
                          ? "none"
                          : zone.zone_type === "road"
                            ? "#bec3c8"
                            : zone.zone_type === "green_space"
                              ? readNativePark(zone)
                                ? "none"
                                : "#aac593"
                              : "#d1b69c"
                      }
                      stroke="#6d7469"
                      strokeWidth={
                        zone.zone_type === "site_boundary" ? 0.4 : 0.2
                      }
                      strokeDasharray={
                        zone.zone_type === "site_boundary" ||
                        readNativePark(zone)
                          ? "2 1"
                          : undefined
                      }
                    />
                    {readNativePark(zone) && (
                      <polygon
                        points={points(
                          nativeParkFootprint(
                            readNativePark(zone)!.selection,
                            readNativePark(zone)!.layout,
                          ).map(context.fromWorld),
                        )}
                        fill="#aac593"
                        fillOpacity={0.5}
                        stroke="#315d4b"
                        strokeWidth={0.5}
                      />
                    )}
                    {zone.zone_type !== "site_boundary" && (
                      <text
                        x={context.fromWorld(zone.coordinates[0]).x}
                        y={-context.fromWorld(zone.coordinates[0]).y}
                        fontSize={Math.max(1.5, context.frame.width / 65)}
                      >
                        {zone.name ||
                          assetForZone(zone)?.label ||
                          zone.zone_type}
                      </text>
                    )}
                  </g>
                ))}
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
                    {m.kind === "tower" ? "Play" : m.kind}
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
                  aria-label={`Select ${bench.treeVariant ? "tree" : bench.propVariant ? "object" : "bench"} ${i + 1}`}
                  aria-pressed={selected === bench.id}
                  transform={`translate(${bench.point.x} ${-bench.point.y}) rotate(${(-bench.yaw * 180) / Math.PI})`}
                  onFocus={() => {
                    if (!placing && !paving.armed) setSelected(bench.id);
                  }}
                  onClick={() => {
                    if (!locked && !placing && !paving.armed) {
                      paving.reset();
                      setSelected(bench.id);
                    }
                  }}
                  onKeyDown={(e) => {
                    if (["Enter", " "].includes(e.key) && !locked) {
                      e.preventDefault();
                      setSelected(bench.id);
                    }
                  }}
                  onPointerDown={(e) => {
                    if (locked) return;
                    e.stopPropagation();
                    e.preventDefault();
                    setSelected(bench.id);
                    paving.reset();
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
                    x={-markerSize}
                    y={-markerSize}
                    width={markerSize * 2}
                    height={markerSize * 2}
                    rx=".6"
                    fill={
                      selected === bench.id
                        ? "#c9ff3d"
                        : independent
                          ? "#fff9ec"
                          : "transparent"
                    }
                    stroke={selected === bench.id ? "#263728" : "none"}
                    strokeWidth=".15"
                  />
                  {bench.treeVariant && (
                    <circle
                      r={
                        Math.max(
                          ...detailAsset(bench.treeVariant).dimensions.slice(
                            0,
                            2,
                          ),
                        ) / 2
                      }
                      fill="#76a65c"
                      fillOpacity={0.65}
                      stroke="#315935"
                      strokeWidth=".2"
                    />
                  )}
                  {!bench.treeVariant && !bench.propVariant && (
                    <>
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
                      <path
                        d="M-.9 -.45H.9"
                        stroke="#31271c"
                        strokeWidth=".18"
                      />
                    </>
                  )}
                  {bench.treeVariant && <circle r={0.4} fill="#725638" />}
                  {bench.propVariant && (
                    <rect
                      x={-detailAsset(bench.propVariant).dimensions[0] / 2}
                      y={-detailAsset(bench.propVariant).dimensions[1] / 2}
                      width={detailAsset(bench.propVariant).dimensions[0]}
                      height={Math.max(
                        0.3,
                        detailAsset(bench.propVariant).dimensions[1],
                      )}
                      fill={detailAsset(bench.propVariant).color}
                      stroke="#313b33"
                      strokeWidth=".2"
                    />
                  )}
                  <text
                    x="0"
                    y={markerSize * 0.8}
                    textAnchor="middle"
                    fontSize={markerSize * 0.6}
                    fill="#18251b"
                  >
                    {i + 1}
                  </text>
                </g>
              ))}
            </svg>
            <p className="mt-2 text-xs">
              Top view · north ↑ · objects keep their real dimensions.{" "}
              {independent
                ? "Dashed park outline = reserved parcel; solid green outline = fixed park layout. Details can be placed beyond these guides."
                : "Paths and larger park objects are shown for context."}
            </p>
          </div>
          <div className="space-y-3 md:max-h-[74dvh] md:overflow-y-auto md:pr-1">
            {independent && paving.controls}
            <p className="font-semibold">
              {benchCount} {benchCount === 1 ? "bench" : "benches"}
              {independent &&
                ` · ${treeCount} ${treeCount === 1 ? "tree" : "trees"} · ${propCount} objects`}
            </p>
            {independent ? (
              <DetailCataloguePicker
                disabled={locked}
                canAdd={(kind) =>
                  (kind === "bench"
                    ? benchCount
                    : kind === "tree"
                      ? treeCount
                      : propCount) < 256
                }
                onAdd={add}
              />
            ) : (
              <button
                className={`${button} w-full !bg-[#c9ff3d]`}
                disabled={locked || benchCount >= MAX_DETAIL_BENCHES}
                onClick={() => add()}
              >
                Add bench
              </button>
            )}
            {independent && (
              <>
                <p className="text-xs">
                  Add an object, then choose Move on plan and click anywhere.
                  Building and street outlines are guides.
                </p>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    className={button}
                    disabled={viewScale >= 8}
                    onClick={() => setViewScale((v) => v * 2)}
                  >
                    Expand view
                  </button>
                  <button
                    className={button}
                    disabled={viewScale <= 0.125}
                    onClick={() => setViewScale((v) => v / 2)}
                  >
                    Zoom in
                  </button>
                </div>
              </>
            )}
            {active ? (
              <>
                <p className="text-sm font-semibold">
                  {active.treeVariant
                    ? DETAIL_TREE_MODELS.find(
                        (m) => m.id === active.treeVariant,
                      )?.label
                    : active.propVariant
                      ? detailAsset(active.propVariant).label
                      : "Bench"}{" "}
                  {benches.findIndex((b) => b.id === active.id) + 1} selected
                </p>
                <button
                  className={`${button} w-full`}
                  disabled={locked}
                  aria-pressed={placing}
                  onClick={() => {
                    paving.reset();
                    setPreview(null);
                    setPlacing((v) => !v);
                    setMessage(
                      "Click a clear place on the plan to move this object.",
                    );
                  }}
                >
                  Move on plan
                </button>
                <div className="grid grid-cols-2 gap-2">
                  {(
                    [
                      ["north", 0, 0.5],
                      ["east", 0.5, 0],
                      ["south", 0, -0.5],
                      ["west", -0.5, 0],
                    ] as const
                  ).map(([name, x, y]) => (
                    <button
                      key={name}
                      className={button}
                      aria-label={`Move ${activeKind} ${name}`}
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
                  Remove {activeKind}
                </button>
              </>
            ) : (
              <p className="text-sm">
                Click a numbered {independent ? "object" : "bench"} to select
                it.
              </p>
            )}
            <button
              className={`${button} w-full`}
              aria-label="Undo detail edit"
              disabled={locked || !past.length}
              onClick={() => {
                undo();
              }}
            >
              Undo
            </button>
            <p role="status" className="text-sm text-amber-900">
              {message ||
                (invalid
                  ? "An object needs a clearer position. Select and move it before saving."
                  : "")}
            </p>
            <button
              className={`${button} w-full !bg-[#c9ff3d]`}
              disabled={locked || !dirty || !!invalid || paving.drawing}
              onClick={async () => {
                setSaving(true);
                setMessage("");
                try {
                  await onSave(benches, surfaces);
                  onClose();
                } catch (error) {
                  const fallback =
                    "Could not save the details. Your edits are still here; try Save details again.";
                  setMessage(
                    isAxiosError(error) && error.response?.status === 409
                      ? getApiErrorMessage(error, fallback)
                      : fallback,
                  );
                } finally {
                  setSaving(false);
                }
              }}
            >
              {saving ? "Saving…" : "Save details"}
            </button>
            <p className="text-xs text-slate-600">
              {dirty
                ? "Unsaved edits. Closing discards them."
                : "Your saved arrangement."}{" "}
              {independent
                ? "Details keep their own positions when buildings, streets or parks move."
                : "Moving or rotating the whole park carries the benches with it."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
