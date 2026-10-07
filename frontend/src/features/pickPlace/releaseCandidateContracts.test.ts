import { createElement, useState } from 'react';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { SiteZone } from '@/types';
import { assetForZone, placeAsset, placementPlanRequest, placementProperties } from './catalogue';
import type { PlacementDraft } from './GlobePlacementPreview';
import { PlacementControls } from './PlacementControls';
import { ReshapePanel } from './ReshapePanel';
import { rectangleAt, rectangleDimensions } from './geometry';
import { nativeBuildingContract } from './nativeBuildingContract';
import library from '../../../../seed/model-library/rlasm-architectural-clay/library.json';

interface Candidate {
  candidate: string;
  variant_id: string;
  local_trial_only?: boolean;
  native_floors: number;
  picker: { id: string; width: number; depth: number; max_size: number };
  model: { native_dimensions_m: { width: number; depth: number; height: number } };
}

// Independent seed identities keep omitted or incorrectly wired trial models
// from disappearing silently when the discovery registry changes.
const candidates = (library.entries as Candidate[]).filter(entry => entry.local_trial_only);
const center = [-114.04677, 51.04542];

function DraftHarness({ assetId }: { assetId: string }) {
  const asset = placeAsset(assetId);
  const [draft, setDraft] = useState<PlacementDraft>({ assetId, width: asset.width, depth: asset.depth, degrees: 0, faceStreet: true });
  return createElement('div', null,
    createElement(PlacementControls, { draft, onChange: setDraft }),
    createElement('pre', { 'data-testid': 'candidate-draft' }, JSON.stringify(draft)));
}

const draftValue = () => JSON.parse(screen.getByTestId('candidate-draft').textContent!) as PlacementDraft;
const change = (label: string, value: number) => fireEvent.change(screen.getByLabelText(label), { target: { value: String(value) } });
afterEach(cleanup);

describe('release candidate native placement contracts (not browser acceptance)', () => {
  it('covers all 19 selected local trials independently of discovery gates', () => {
    expect(candidates).toHaveLength(19);
    expect(new Set(candidates.map(entry => entry.candidate)).size).toBe(19);
  });

  describe.each(candidates)('$candidate', entry => {
    it('accepts default, minimum and maximum plots without changing native identity or dimensions', () => {
      const asset = placeAsset(entry.picker.id);
      const native = entry.model.native_dimensions_m;
      const expectedDimensions = [native.width, native.depth, native.height];
      expect(asset.model).toMatchObject({ variantId: entry.variant_id, revision: entry.candidate });
      expect(asset.reshapeMode).toBe('fixed_native');
      render(createElement(DraftHarness, { assetId: asset.id }));
      for (const [width, depth] of [[asset.width, asset.depth], [asset.minWidth, asset.minDepth], [asset.maxWidth ?? asset.maxSize, asset.maxDepth ?? asset.maxSize]]) {
        change('Placement width', width);
        change('Placement depth', depth);
        const draft = draftValue();
        expect(draft.inputError).toBeUndefined();
        expect([draft.width, draft.depth]).toEqual([width, depth]);
        expect(width).toBeGreaterThanOrEqual(native.width + 3 - 1e-6);
        expect(depth).toBeGreaterThanOrEqual(native.depth + 3 - 1e-6);
        expect(placementPlanRequest(asset, draft.width, draft.depth)).toMatchObject({
          target_width_m: width, target_depth_m: depth, target_floors: entry.native_floors,
          archetype_id: entry.variant_id, native_home_plot: false, allow_forced_fit: false,
        });
        const properties = placementProperties(asset, 1097, rectangleAt(center, width, depth));
        expect(properties.model_native_dimensions_m).toEqual(expectedDimensions);
        expect(properties.pick_place_model_revision).toBe(entry.candidate);
        const contract = nativeBuildingContract({ properties });
        expect(contract).toMatchObject({ revision: entry.candidate, rigid: true, heightM: native.height, storeys: entry.native_floors });
        expect(contract?.asset.nativeDimensions).toEqual(expectedDimensions);
      }
      // These are compiler request/metadata contracts. Actual GLB instance
      // scales are verified separately by backend compilation tests.
    });

    it('blocks undersized width and depth independently and recovers at the exact limits', () => {
      const asset = placeAsset(entry.picker.id);
      render(createElement(DraftHarness, { assetId: asset.id }));
      change('Placement width', asset.minWidth - 0.1);
      expect(draftValue().inputError).toBeTruthy();
      change('Placement depth', asset.minDepth);
      expect(draftValue().inputError).toBeTruthy();
      change('Placement width', asset.minWidth);
      expect(draftValue().inputError).toBeUndefined();
      change('Placement depth', asset.minDepth - 0.1);
      expect(draftValue().inputError).toBeTruthy();
      change('Placement width', asset.maxWidth ?? asset.maxSize);
      expect(draftValue().inputError).toBeTruthy();
      change('Placement depth', asset.minDepth);
      expect(draftValue().inputError).toBeUndefined();
      expect(draftValue().assetId).toBe(asset.id);
    });

    it('rotates the minimum plot without rounding it below its limit or changing saved properties', () => {
      const asset = placeAsset(entry.picker.id);
      const zone = { id: entry.candidate, zone_type: 'building', coordinates: rectangleAt(center, asset.minWidth, asset.minDepth),
        properties: placementProperties(asset, 1097) } as SiteZone;
      const original = JSON.stringify(zone.properties);
      const onReshape = vi.fn();
      render(createElement(ReshapePanel, { zone, disabled: false, onReshape, onClose: vi.fn(), onDelete: vi.fn(), onDuplicate: vi.fn(), onMore: vi.fn() }));
      change('Rotation (degrees)', 37);
      fireEvent.click(screen.getByRole('button', { name: 'Apply shape' }));
      expect(onReshape).toHaveBeenCalledOnce();
      const dimensions = rectangleDimensions(onReshape.mock.calls[0][0]);
      expect(dimensions.width).toBeCloseTo(asset.minWidth, 4);
      expect(dimensions.depth).toBeCloseTo(asset.minDepth, 4);
      expect(dimensions.degrees).toBeCloseTo(37, 4);
      expect(JSON.stringify(zone.properties)).toBe(original);
      const saved = JSON.parse(JSON.stringify({ ...zone, coordinates: onReshape.mock.calls[0][0] })) as SiteZone;
      expect(assetForZone(saved)?.model).toMatchObject({ variantId: entry.variant_id, revision: entry.candidate });
      expect(nativeBuildingContract(saved)?.asset.nativeDimensions).toEqual(asset.nativeDimensions);
    });

    it('restores the exact saved revision and refuses an unavailable revision instead of substituting today\'s model', () => {
      const asset = placeAsset(entry.picker.id);
      const saved = JSON.parse(JSON.stringify({ properties: placementProperties(asset) })) as Pick<SiteZone, 'properties'>;
      expect(assetForZone(saved)?.model).toEqual(asset.model);
      const unavailable = { properties: { ...saved.properties, pick_place_model_revision: `${entry.candidate}-unavailable` } };
      expect(assetForZone(unavailable)).toBeUndefined();
      expect(nativeBuildingContract(unavailable)).toBeUndefined();
      expect(saved.properties?.pick_place_model_revision).toBe(entry.candidate);
    });
  });
});
