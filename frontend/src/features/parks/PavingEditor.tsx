import { useMemo, useState } from "react";
import type { BenchContext } from "./benchDetails";
import type { ParkPoint } from "@/components/viewer/globe/neighborhoodParkLayout";
import {
  PAVING_MATERIALS,
  pavingProblem,
  type PavingSurface,
  pavingLocalPoints,
} from "./pavingSurfaces";
import { parkingLayout, parkingMarkingSegments } from './parkingLot';
import { metersPerDegLon, METERS_PER_DEG_LAT } from '@/components/viewer/mapEngine/geoUtils';
import { parkOutlineDimensions, reshapeParkOutline } from '@/features/pickPlace/parkOutline';

const button =
  "min-h-11 rounded-lg border border-slate-400 bg-white px-3 py-2 text-sm font-semibold disabled:opacity-40";
const points = (p: ParkPoint[]) => p.map((v) => `${v.x},${-v.y}`).join(" ");

/** Paving shares the detail draft, save and undo history, but never object collisions. */
export function usePavingEditor({
  surfaces,
  context,
  locked,
  change,
  onActivate,
}: {
  surfaces: PavingSurface[];
  context: BenchContext;
  locked: boolean;
  change: (next: PavingSurface[]) => void;
  onActivate: () => void;
}) {
  const [selected, setSelected] = useState<string | null>(null);
  const [draft, setDraft] = useState<ParkPoint[] | null>(null);
  const [target, setTarget] = useState<"surface" | number | null>(null);
  const [material, setMaterial] =
    useState<PavingSurface["material"]>("concrete");
  const [corner, setCorner] = useState(0);
  const [message, setMessage] = useState("");
  const [drawingParking, setDrawingParking] = useState(false);
  const active = surfaces.find((s) => s.id === selected);
  const layouts = useMemo(() => new Map(surfaces.filter(s=>s.parking).map(s=>
    [s.id,parkingLayout(pavingLocalPoints(s.coordinates),s.parking!)])),[surfaces]);
  const parking = active ? layouts.get(active.id) : undefined;
  const armed = draft !== null || target !== null;
  const select = (id: string) => {
    onActivate();
    setSelected(id);
    setCorner(0);
    setTarget(null);
    setDraft(null);
    setMessage("");
  };
  const reset = () => {
    setSelected(null);
    setTarget(null);
    setDraft(null);
    setMessage("");
  };
  const apply = (next: PavingSurface) => {
    const problem = pavingProblem(next.coordinates) || (next.parking
      ? parkingLayout(pavingLocalPoints(next.coordinates),next.parking).problem : null);
    if (problem) {
      setMessage(problem);
      return;
    }
    change(surfaces.map((s) => (s.id === next.id ? next : s)));
    setTarget(null);
    setMessage("");
  };
  const click = (p: ParkPoint) => {
    if (locked) return;
    if (draft !== null) {
      if (draft.length < 64) setDraft([...draft, p]);
      return;
    }
    if (active && target !== null) {
      const local = active.coordinates.map(context.fromWorld);
      const center = {
        x: local.reduce((n, v) => n + v.x, 0) / local.length,
        y: local.reduce((n, v) => n + v.y, 0) / local.length,
      };
      apply({
        ...active,
        coordinates: local.map((v, i) =>
          context.toWorld(
            target === "surface"
              ? { x: v.x + p.x - center.x, y: v.y + p.y - center.y }
              : i === target
                ? p
                : v,
          ),
        ),
      });
    }
  };
  const finish = () => {
    if (!draft || locked) return;
    const coordinates = draft.map(context.toWorld),
      problem = pavingProblem(coordinates);
    if (problem) {
      setMessage(problem);
      return;
    }
    const next:PavingSurface = { id: `paving-${crypto.randomUUID()}`, material:drawingParking?'asphalt':material, coordinates,
      ...(drawingParking?{parking:{version:1 as const,rowAngle:0}}:{}) };
    if(next.parking){
      const issue=parkingLayout(pavingLocalPoints(coordinates),next.parking).problem;
      if(issue){setMessage(issue);return;}
    }
    change([...surfaces, next]);
    setSelected(next.id);
    setDraft(null);
    setMessage("");
  };
  const plan = (
    <>
      {surfaces.map((s, i) => <g key={s.id}>
        <polygon
          role="button"
          tabIndex={locked ? -1 : 0}
          aria-label={`Select ${s.parking?'parking lot':'paving'} ${i + 1}`}
          aria-pressed={s.id === selected}
          points={points(s.coordinates.map(context.fromWorld))}
          fill={PAVING_MATERIALS[s.material].color}
          fillOpacity={0.8}
          stroke={s.id === selected ? (s.parking?'#b6ed18':"#075985") : "#7a7468"}
          strokeWidth={s.id === selected ? 0.7 : 0.2}
          onClick={() => {
            if (!locked && !armed) select(s.id);
          }}
          onKeyDown={(e) => {
            if (!locked && ["Enter", " "].includes(e.key)) {
              e.preventDefault();
              select(s.id);
            }
          }}
        />
        {s.parking && <g pointerEvents="none" aria-hidden="true">
          {parkingMarkingSegments(layouts.get(s.id)!).map(([a,b],j)=>{
            const local=[a,b].map(([x,y])=>context.fromWorld([
              s.coordinates[0][0]+x/metersPerDegLon(s.coordinates[0][1]),
              s.coordinates[0][1]+y/METERS_PER_DEG_LAT,
            ]));
            return <polyline key={j} points={points(local)} stroke="white" strokeWidth={.10} fill="none"/>;
          })}
        </g>}
      </g>)}
      {active &&
        active.coordinates.map((p, i) => (
          <g key={i} pointerEvents="none">
            <circle
              cx={context.fromWorld(p).x}
              cy={-context.fromWorld(p).y}
              r={1}
              fill={i === corner ? "#38bdf8" : "white"}
              stroke="#075985"
              strokeWidth={0.3}
            />
            <text
              x={context.fromWorld(p).x + 1.5}
              y={-context.fromWorld(p).y}
              fontSize={2}
            >
              {i + 1}
            </text>
          </g>
        ))}
      {draft && (
        <polyline
          pointerEvents="none"
          points={points(draft)}
          fill={PAVING_MATERIALS[material].color}
          fillOpacity={0.35}
          stroke="#075985"
          strokeWidth={0.6}
        />
      )}
    </>
  );
  const controls = (
    <section
      aria-label="Custom paving"
      className="space-y-2 rounded-lg border border-slate-300 p-2"
    >
      <h3 className="text-sm font-bold">Parking lots & custom paving</h3>
      <p className="text-xs">
        Draw a plaza or paved area beneath your details. Follows prepared site
        ground; does not clear buildings or reshape terrain.
      </p>
      <label className="block text-xs">
        Paving material
        <select
          aria-label="Paving material"
          disabled={locked}
          className={`${button} mt-1 w-full`}
          value={active?.material ?? material}
          onChange={(e) => {
            const value = e.target.value as PavingSurface["material"];
            setMaterial(value);
            if (active) apply({ ...active, material: value });
          }}
        >
          {Object.entries(PAVING_MATERIALS).map(([id, m]) => (
            <option key={id} value={id}>
              {m.label}
            </option>
          ))}
        </select>
      </label>
      <button className={`${button} w-full !border-2 !border-[#232323] !bg-[#c9ff3d]`}
        disabled={locked || surfaces.length >=64 || draft!==null}
        onClick={()=>{
          onActivate();setSelected(null);setTarget(null);setDraft([]);setDrawingParking(true);
          setMessage('Draw the lot outline on the plan. Use the first edge to aim the rows, then Finish parking lot.');
        }}>Draw parking lot</button>
      <button
        className={`${button} w-full`}
        disabled={locked || surfaces.length >= 64 || draft !== null}
        onClick={() => {
          onActivate();
          setSelected(null);
          setTarget(null);
          setDraft([]);
          setDrawingParking(false);
          setMessage(
            "Click at least three corners on the plan, then Finish paving.",
          );
        }}
      >
        Draw paved area
      </button>
      {draft !== null && (
        <>
          <p className="text-xs">
            {draft.length} corners · click to add a corner
          </p>
          <button
            className={button}
            disabled={locked || draft.length < 3}
            onClick={finish}
          >
            {drawingParking?'Finish parking lot':'Finish paving'}
          </button>
          <button
            className={button}
            disabled={locked || !draft.length}
            onClick={() => setDraft(draft.slice(0, -1))}
          >
            Undo corner
          </button>
          <button className={button} disabled={locked} onClick={reset}>
            Cancel paving
          </button>
        </>
      )}
      {active && (
        <>
          <p className="text-sm font-semibold">
            {active.parking?'Parking lot':'Paved area'} {surfaces.indexOf(active) + 1} selected
          </p>
          {active.parking && <div className="space-y-2 rounded-xl border-2 border-[#232323] bg-lime-50 p-3">
            <p className="text-lg font-bold">{parking?.spaces.length ?? 0} parking spaces</p>
            <p className="text-xs">2.7 × 5.5 m spaces · 6 m drive aisles. Capacity changes with the outline; spaces keep their size.</p>
            <label className="block text-xs font-semibold">Row direction
              <select aria-label="Parking row direction"
                value={active.parking.rowAngle} disabled={locked} className={`${button} mt-1 w-full`}
                onChange={e=>apply({...active,parking:{...active.parking!,rowAngle:Number(e.target.value)}})}>
                <option value={0}>Along first edge</option>
                <option value={90}>Across first edge</option>
              </select>
            </label>
            <button className={`${button} w-full`} disabled={locked} onClick={()=>{
              const frame=parkOutlineDimensions(active.coordinates);
              apply({...active,coordinates:reshapeParkOutline(active.coordinates,frame.width,frame.depth,frame.degrees+15)});
            }}>Rotate parking lot 15°</button>
            <p className="text-xs text-slate-600">Local pilot: perpendicular bays on level ground. Outlines need a clear straight side aisle; split incompatible outlines into smaller lots. The clear side aisle needs a road entrance; this tool does not cut curbs or connect roads. Cars, accessible bays and islands are not included yet.</p>
          </div>}
          <button
            className={`${button} w-full`}
            disabled={locked}
            aria-pressed={target === "surface"}
            onClick={() => {
              setTarget("surface");
              setMessage("Click the new centre of the paved area.");
            }}
          >
            Move paved area
          </button>
          <label className="block text-xs">
            Corner
            <select
              aria-label="Paving corner"
              className={`${button} w-full`}
              value={corner}
              onChange={(e) => setCorner(Number(e.target.value))}
              disabled={locked}
            >
              {active.coordinates.map((_, i) => (
                <option key={i} value={i}>
                  Corner {i + 1}
                </option>
              ))}
            </select>
          </label>
          <button
            className={`${button} w-full`}
            disabled={locked}
            aria-pressed={typeof target === "number"}
            onClick={() => {
              setTarget(corner);
              setMessage("Click the new position for this corner.");
            }}
          >
            Move paving corner
          </button>
          <button
            className={`${button} w-full`}
            disabled={locked}
            onClick={() => {
              change(surfaces.filter((s) => s.id !== active.id));
              reset();
            }}
          >
            {active.parking?'Remove parking lot':'Remove paved area'}
          </button>
        </>
      )}
      <p role="status" className="text-xs text-sky-900">
        {message}
      </p>
    </section>
  );
  return {
    plan,
    controls,
    armed,
    drawing: draft !== null,
    click,
    reset,
    finish,
  };
}
