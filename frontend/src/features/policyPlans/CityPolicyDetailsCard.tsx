import { useEffect, useId, useRef } from "react";
import { ExternalLink, X } from "lucide-react";
import {
  CITY_PLAN_ASSETS,
  CITY_PLAN_EDITION,
  type CityPlanMap,
} from "./citywidePlans";
import { transportStyle, type TransportFeature, type TransportSnapshot } from './transportVectors';

export function CityPolicyDetailsCard({
  map,
  onClose,
  feature,
  snapshot,
}: {
  map: CityPlanMap | null;
  onClose: () => void;
  feature?: TransportFeature;
  snapshot?: TransportSnapshot;
}) {
  const heading = useId();
  const panel = useRef<HTMLElement>(null);
  useEffect(() => {
    if (map) panel.current?.focus({ preventScroll: true });
  }, [map]);
  if (!map) return null;
  return (
    <section
      ref={panel}
      tabIndex={-1}
      role="region"
      aria-labelledby={heading}
      onKeyDown={(event) => {
        if (event.key === "Escape") {
          event.stopPropagation();
          onClose();
        }
      }}
      className="absolute bottom-16 right-3 z-40 max-h-[72vh] w-[min(30rem,calc(100vw-1.5rem))] overflow-y-auto rounded-2xl border border-[#151515]/25 bg-[#fffdf6] text-[#151515] shadow-2xl focus:outline-none sm:bottom-20 sm:right-4"
    >
      <header className="sticky top-0 z-10 flex items-start gap-2 border-b border-[#151515]/10 bg-[#fffdf6] p-4">
        <div className="flex-1">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-[#5c554d]">
            {map.group} · Map {map.number}
          </p>
          <h2 id={heading} className="mt-1 text-base font-bold">
            {map.title}
          </h2>
        </div>
        <button
          type="button"
          aria-label="Close city policy details"
          onClick={onClose}
          className="-mr-2 -mt-2 flex h-11 w-11 items-center justify-center rounded-xl hover:bg-stone-100"
        >
          <X size={18} />
        </button>
      </header>
      <div className="space-y-4 p-4 text-sm leading-relaxed">
        {feature && <div className="space-y-2 rounded-xl border border-stone-200 bg-white p-3">
          <h3 className="font-bold">{transportStyle(feature.properties.category).label}</h3>
          <p>{transportStyle(feature.properties.category).description}</p>
          {feature.properties.priority && <p className="text-xs">Network priority: {feature.properties.priority.toLowerCase()}</p>}
          {snapshot?.sources[feature.properties.source] && <a className="text-xs underline" target="_blank" rel="noreferrer"
            href={snapshot.sources[feature.properties.source].url}>View official City feature service</a>}
          <p className="text-[11px]">City vector snapshot: {snapshot?.retrieved.slice(0, 10)} UTC. Conceptual policy alignment; not a surveyed route.</p>
        </div>}
        <p>{map.summary}</p>
        <h3 className="text-xs font-bold uppercase tracking-wide">
          Reading this map
        </h3>
        <ul className="list-disc space-y-2 pl-4">
          {map.guidance.map((text) => (
            <li key={text}>{text}</li>
          ))}
        </ul>
        <figure className="rounded-xl border border-stone-200 bg-white p-2">
          <figcaption className="mb-2 text-xs font-bold">
            {snapshot ? 'Published PDF reference legend' : 'Original City legend'}
          </figcaption>
          <a
            href={`${CITY_PLAN_ASSETS}/${map.id}/legend.webp`}
            target="_blank"
            rel="noreferrer"
            aria-label={`Enlarge ${map.group} Map ${map.number} legend`}
          >
            <img
              src={`${CITY_PLAN_ASSETS}/${map.id}/legend.webp`}
              alt={map.legendText}
              className="w-full"
            />
          </a>
          <p className="mt-2 text-[10px] text-[#5c554d]">
            Click the legend to enlarge it.
          </p>
        </figure>
        <p className="text-[11px] text-[#5c554d]">{map.legendText}</p>
        <a
          href={map.source}
          target="_blank"
          rel="noreferrer"
          className="flex min-h-11 items-center gap-2 text-xs font-semibold text-[#37594b] underline underline-offset-2"
        >
          Read the plan · page {map.printedPage}
          <ExternalLink size={14} />
        </a>
        <p className="text-[10px] text-[#5c554d]">
          © The City of Calgary · {CITY_PLAN_EDITION}. Student guidance
          accompanies the original map artwork. Read the plan’s written policies
          and check subsequent amendments for site-specific decisions.
        </p>
      </div>
    </section>
  );
}
