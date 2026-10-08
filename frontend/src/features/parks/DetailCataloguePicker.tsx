import { useState } from "react";
import {
  searchDetails,
  DETAIL_CATALOGUE,
  DETAIL_CATEGORIES,
  type DetailAssetId,
} from "./detailCatalogue";

const control =
  "min-h-11 w-full rounded-lg border border-slate-400 bg-white px-3 py-2 text-sm text-slate-900 disabled:opacity-40";
export function DetailCataloguePicker({
  disabled,
  canAdd,
  onAdd,
}: {
  disabled: boolean;
  canAdd: (kind: string) => boolean;
  onAdd: (id: DetailAssetId) => void;
}) {
  const [query, setQuery] = useState(""),
    [category, setCategory] = useState("All"),
    [selected, setSelected] = useState<DetailAssetId>("timber-bench");
  const options = searchDetails(query, category);
  const choice = options.find((option) => option.id === selected) ?? options[0];
  return (
    <fieldset disabled={disabled} className="space-y-2">
      <legend className="mb-2 font-semibold">
        Detail catalogue · {DETAIL_CATALOGUE.length} choices
      </legend>
      <input
        aria-label="Search detail catalogue"
        placeholder="Search details…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className={control}
      />
      <select
        aria-label="Detail category"
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className={control}
      >
        {["All", ...DETAIL_CATEGORIES].map((group) => (
          <option key={group}>{group}</option>
        ))}
      </select>
      {choice ? (
        <>
          <select
            aria-label="Detail model"
            value={choice.id}
            onChange={(e) => setSelected(e.target.value as DetailAssetId)}
            className={control}
          >
            {options.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
          <p className="text-xs">{choice.description}</p>
          <p className="text-xs text-slate-600">
            {choice.dimensions.map((n) => n.toFixed(1)).join(" × ")} m · width ×
            depth × height
          </p>
          <button
            className={`${control} !bg-[#c9ff3d] font-semibold`}
            disabled={disabled || !canAdd(choice.kind)}
            onClick={() => onAdd(choice.id)}
          >
            Add {choice.kind}
          </button>
        </>
      ) : (
        <p role="status" className="text-sm">
          No matching details. Try another search or category.
        </p>
      )}
    </fieldset>
  );
}
